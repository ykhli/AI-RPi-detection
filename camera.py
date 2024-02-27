
from picamera2 import Picamera2
import time, datetime, os, logging

picam2 = Picamera2()

def capture_photo():
    try:
        take_photo()  # Call your take_photo function
        logging.info("Image captured successfully")
    except Exception as e:
        return e
    

def take_photo():
    global picam2
    try:
        timestamp = int(datetime.timestamp(datetime.now()))
        image_name = f'{timestamp}.jpg'
        current_dir = os.path.dirname(__file__)
        static_dir = os.path.join(current_dir, 'static')
        filepath = os.path.join(static_dir, image_name)
        request = picam2.capture_request()
        request.save("main", filepath)
        request.release()
        logging.info(f"Image captured successfully. Path: {filepath}")
    except Exception as e:
        logging.error(f"Error capturing image: {e}")

def main():
    while True:
        capture_photo()
        time.sleep(3)

if __name__ == "__main__":
    main()