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

def delete_attendance(db: Session, attendance_id: int):
    db_attendance = db.query(Attendance).filter(Attendance.attendance_id == attendance_id).first()
    if db_attendance:
        db.delete(db_attendance)
        db.commit()
    return db_attendance

def check_attendance(db: Session, rfid_card_id: str, room: str, time_str: str, day_str: str): ## TODO: To be done when session gets implemented
    """
    Process attendance based on RFID scan
    Returns a message to send back to the device
    """
    try:
        # TODO: Needs absences as a separate thread implemented
        time_now = datetime.strptime(time_str, "%H:%M:%S")
        day = datetime.strptime(day_str, "%Y-%m-%d").date()

        student = db.query(Student).filter(Student.rfid_card_id == rfid_card_id).first()
        if not student:
            logger.warning(f"Unknown RFID card: {rfid_card_id}")
            return "Unknown card"

        # TODO: Session logic -> needs session implemented
        # active_session = db.query(Session).filter(
        #     Session.room == room,
        #     Session.date == day,
        #     Session.status == SessionStatus.active,
        #     Session.start_time <= time_now,
        #     Session.end_time >= time_now
        # ).first()
        #
        # if not active_session:
        #     logger.warning(f"No active session found in room {room} at {time_now} on {day}")
        #     return "No active session"
        #
        #
        # existing_attendance = db.query(Attendance).filter(
        #     Attendance.session_id == active_session.session_id,
        #     Attendance.student_id == student.student_id
        # ).first()
        #
        # if existing_attendance:
        #     logger.info(f"Student {student.name} already marked for session {active_session.session_id}")
        #     return f"Already marked: {existing_attendance.status.value}"

        status = AttendanceStatus.present

        session_start = datetime.combine(day, active_session.start_time.time())
        time_full = datetime.combine(day, time_now.time())
        minutes_late = (time_full - session_start).total_seconds() / 60

        if minutes_late > 15:
            status = AttendanceStatus.late


        attendance = create_attendance(
            db=db,
            session_id=active_session.session_id,
            student_id=student.student_id,
            status=status,
            time=time_now
        )

        logger.info(f"Marked {student.name} as {status.value}")
        logger.info(f"Attendance ID: {attendance.attendance_id}")
        return f"Marked: {status.value}"

    except Exception as e:
        logger.error(f"Error processing attendance: {e}")
        return "Error processing attendance"

## Mock attendance checker for testing purposes (will be deleted)
def mock_check_attendance(db: Session, rfid_card_id: str, room: str, time_str: str, day_str: str):
    """
    Process attendance based on RFID scan - mock simplified version without session requirements
    Returns a message to send back to the device
    """
    try:

        time_now = datetime.strptime(time_str, "%H:%M:%S")
        day = datetime.strptime(day_str, "%Y-%m-%d").date()


        mock_session_id = f"{room}_{day.strftime('%Y%m%d')}"
        logger.info(f"Using mock session ID: {mock_session_id}")

        today_midnight = datetime.combine(day, datetime.min.time())


        logger.info(f"Recording attendance for student Arthur in room {room}")

        class_start_time = datetime.strptime("09:00:00", "%H:%M:%S").time()
        class_start = datetime.combine(day, class_start_time)
        time_full = datetime.combine(day, time_now.time())

        if time_full > class_start:
            minutes_late = (time_full - class_start).total_seconds() / 60

            if minutes_late > 15:
                status = AttendanceStatus.late
                logger.info(f"Student Arthur is late ({minutes_late:.1f} minutes)")
            else:
                status = AttendanceStatus.present
                logger.info(f"Student Arthur is on time")
        else:
            status = AttendanceStatus.present
            logger.info(f"Student Arthur arrived early")

        attendance_record = {
            "student_id": 132,
            "student_name": "Arthur",
            "room": room,
            "time": time_now.strftime("%H:%M:%S"),
            "date": day.strftime("%Y-%m-%d"),
            "status": status.value
        }


        logger.info(f"Attendance record: {attendance_record}")

        return f"Marked: {status.value}"

    except Exception as e:
        logger.error(f"Error processing attendance: {e}")
        return f"Error: {str(e)}"