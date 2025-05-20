from datetime import datetime
from sqlalchemy.orm import Session
from models.attendance import Attendance, AttendanceStatus
from models.session import Session, SessionStatus
from models.student import Student
from core.logger import logger

def get_attendance(db: Session, attendance_id: int):
    return db.query(Attendance).filter(Attendance.attendance_id == attendance_id).first()

def get_attendances(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Attendance).offset(skip).limit(limit).all()

def get_attendances_by_session(db: Session, session_id: int):
    return db.query(Attendance).filter(Attendance.session_id == session_id).all()

def get_attendances_by_student(db: Session, student_id: int):
    return db.query(Attendance).filter(Attendance.student_id == student_id).all()

def create_attendance(db: Session, session_id: int, student_id: int, status: AttendanceStatus, time=None):
    if time is None:
        time = datetime.utcnow()

    db_attendance = Attendance(
        session_id=session_id,
        student_id=student_id,
        time=time,
        status=status
    )
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

def update_attendance(db: Session, attendance_id: int, status: AttendanceStatus = None, time=None):
    db_attendance = db.query(Attendance).filter(Attendance.attendance_id == attendance_id).first()
    if db_attendance:
        if status:
            db_attendance.status = status
        if time:
            db_attendance.time = time
        db_attendance.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_attendance)
    return db_attendance


def check_attendance(db: Session, rfid_card_id: str, room: str):
    try:
        now = datetime.utcnow()
        today = datetime.utcnow().date()

        logger.info(f"Current time: {now}")
        logger.info(f"Current date: {today}")
        logger.info(f"Looking for sessions in room: {room}")

        # Get student
        student = db.query(Student).filter(Student.rfid_card_id == rfid_card_id).first()
        if not student:
            logger.warning(f"Unknown RFID card: {rfid_card_id}")
            return "Unknown card"

        # Get all sessions for this room (without date filter)
        sessions = (
            db.query(Session)
            .filter(
                Session.room == room,
                )
            .all()
        )

        logger.info(f"Found {len(sessions)} sessions in room {room}")

        # Flag to track if we found and processed an active session
        active_session_processed = False

        # Debug each session
        for session in sessions:
            # Extract the date from session.date for clarity
            session_date = session.date.date() if hasattr(session.date, 'date') else session.date
            logger.info(f"Session {session.session_id}: date={session_date}, start={session.start_time}, end={session.end_time}")

            # Check if the session date matches today
            if session_date != today:
                logger.info(f"Session {session.session_id} is for a different date: {session_date}, skipping")
                continue

            # Create proper datetime objects for comparison
            try:
                start_time = session.start_time.time() if hasattr(session.start_time, 'time') else session.start_time
                end_time = session.end_time.time() if hasattr(session.end_time, 'time') else session.end_time

                start_datetime = datetime.combine(today, start_time)
                end_datetime = datetime.combine(today, end_time)

                # Log the individual comparisons
                is_after_start = now >= start_datetime
                is_before_end = now <= end_datetime

                logger.info(f"Time checks for session {session.session_id}:")
                logger.info(f"  After start? {is_after_start} ({now} >= {start_datetime})")
                logger.info(f"  Before end? {is_before_end} ({now} <= {end_datetime})")

                if is_after_start and is_before_end:
                    logger.info(f"SUCCESS! Found ACTIVE session: {session.session_id}")
                    session.status = SessionStatus.active

                    # Process attendance for this active session
                    existing_attendance = (
                        db.query(Attendance)
                        .filter(
                            Attendance.session_id == session.session_id,
                            Attendance.student_id == student.student_id,
                            )
                        .first()
                    )

                    if existing_attendance:
                        logger.info(f"Student {student.name} already marked for session {session.session_id}")
                        db.commit()  # Still commit status changes
                        return f"Already marked: {existing_attendance.status.value}"

                    status = AttendanceStatus.present
                    minutes_late = (now - start_datetime).total_seconds() / 60

                    if minutes_late > 15:
                        status = AttendanceStatus.late
                        logger.info(f"Student {student.name} is late ({minutes_late:.1f} minutes)")

                    # Create the attendance record
                    try:
                        attendance = create_attendance(
                            db=db,
                            session_id=session.session_id,
                            student_id=student.student_id,
                            status=status,
                            time=now,
                        )

                        db.commit()
                        logger.info(f"Successfully marked {student.name} as {status.value}")
                        active_session_processed = True
                        return f"Marked: {status.value}"
                    except Exception as e:
                        logger.error(f"Error creating attendance record: {e}", exc_info=True)
                        return f"Error creating attendance: {str(e)}"
                else:
                    logger.info(f"Session {session.session_id} is not active at current time")
                    if now < start_datetime:
                        session.status = SessionStatus.not_started
                    else:
                        session.status = SessionStatus.ended
            except Exception as e:
                logger.error(f"Error processing session {session.session_id}: {e}", exc_info=True)
                continue

        db.commit()

        if not active_session_processed:
            logger.warning(f"No active session found in room {room} at current time")
            return "No active session"

        return "Attendance processed"

    except Exception as e:
        logger.error(f"Error processing attendance: {e}", exc_info=True)
        return f"Error processing attendance: {str(e)}"