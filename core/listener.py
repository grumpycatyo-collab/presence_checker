import serial
import threading
from .logger import logger
from crud import attendance as attendance_crud
from core.db import get_db

# Tested in a linux environment
def serial_listener(port='/dev/ttyUSB0', baudrate=115200):
    ser = serial.Serial(port, baudrate)
    logger.info(f"Serial listener started on {port}")
    db = get_db()
    while True:
        try:
            if ser.in_waiting:
                data = ser.readline().decode().strip()
                logger.info(f"Received: {data}")
                parts = data.split(',')

                if len(parts) == 2:
                    id, room = parts
                    message = attendance_crud.check_attendance(db=db, rfid_card_id=id, room=room)
                    logger.info("Sending:", message)
                    ser.write((message + "\n").encode())
        except Exception as e:
            logger.error(f"Error in listener: {e}")
            time.sleep(1)

def start_listener_thread():
    thread = threading.Thread(target=serial_listener, daemon=True)
    thread.start()
    return thread

