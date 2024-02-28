
from picamera2 import Picamera2, Preview
import time, os, logging
from datetime import datetime
from openai import OpenAI
import base64

logging.basicConfig(level=logging.INFO) 
save_location='static'
save_dir = os.path.join(os.getcwd(), save_location)
os.makedirs(save_dir, exist_ok=True)

openAI = OpenAI()

picam2 = Picamera2()
picam2.start()
time.sleep(2)


def describe_image(base64_image, context):
    # for testing
    response = openAI.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": """
                You are an AI assistant that can help me describe images. Your responses are short and to the point.
                Only return 1-2 sentences.
                """,
            },
        ]
        + context
        + [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image"},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            },
        ],
        max_tokens=500,
    )
    return response.choices[0].message.content


def capture_photo():
    try:
        filePath = take_photo()  # Call your take_photo function
        logging.info("Image captured sauccessfully")
        return filePath
    except Exception as e:
        return e
    
def encode_image(image_path):
    while True:
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except IOError as e:
            if e.errno != errno.EACCES:
                # Not a "file in use" error, re-raise
                raise
            # File is being written to, wait a bit and retry
            time.sleep(0.1)


def take_photo():
    global picam2
    try:
        timestamp = int(datetime.timestamp(datetime.now()))
        image_name = f'{timestamp}.jpg'
        current_dir = os.path.dirname(__file__)
        static_dir = os.path.join(current_dir, save_dir)
        logging.info(f"Capturing image. Path: {static_dir}")
        filepath = os.path.join(static_dir, image_name)
        request = picam2.capture_request()
        request.save("main", filepath)
        request.release()
        logging.info(f"Image captured successfully. Path: {filepath}")
        return filepath
    except Exception as e:
        logging.error(f"Error capturing image: {e}")

def main():
    context = []
    while True:
        filePath = capture_photo()
        base64_image = encode_image(filePath)
        aiResponse = describe_image(base64_image, context)
        logging.info(f"AI Response: {aiResponse}")
        context = context + [{"role": "assistant", "content": aiResponse}]

        time.sleep(3)

if __name__ == "__main__":
    main()