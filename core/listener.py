import serial
import threading
from .logger import logger
from crud import attendance as attendance_crud

def serial_listener(port='/dev/tty.usbserial-0001', baudrate=115200):
    ser = serial.Serial(port, baudrate)
    logger.info(f"Serial listener started on {port}")

    while True:
        try:
            if ser.in_waiting:
                data = ser.readline().decode().strip()
                logger.info(f"Received: {data}")
                parts = data.split(',')

                if len(parts) == 4:
                    uid, room, time_now, day = parts
                    message = attendance_crud.mock_check_attendance(uid, room, time_now, day)
                    logger.info("Sending:", message)
                    ser.write((message + "\n").encode())
        except Exception as e:
            logger.error(f"Error in listener: {e}")
            time.sleep(1)

def start_listener_thread():
    thread = threading.Thread(target=serial_listener, daemon=True)
    thread.start()
    return thread

