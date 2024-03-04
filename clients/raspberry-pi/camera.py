
from picamera2 import Picamera2, Preview
import time, os, logging
from datetime import datetime
from openai import OpenAI
import base64
import cv2
import numpy as np
from elevenlabs import generate, play, set_api_key, voices
import boto3
from dotenv import load_dotenv

load_dotenv()

# Create S3 service client
svc = boto3.client('s3', endpoint_url='https://fly.storage.tigris.dev')


logging.basicConfig(level=logging.INFO) 
save_location='static'
save_dir = os.path.join(os.getcwd(), save_location)
os.makedirs(save_dir, exist_ok=True)
set_api_key(os.environ.get("ELEVENLABS_API_KEY"))
IMAGE_CAPTURE_INTERVAL = 2
COLLAGE_FRAMES = 5
BUCKET_NAME = os.environ.get("BUCKET_NAME")

openAI = OpenAI()

picam2 = Picamera2()
picam2.start()
time.sleep(2)

def play_audio(text):
    audio = generate(text, voice=os.environ.get("ELEVENLABS_VOICE_ID"))

    unique_id = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8").rstrip("=")
    dir_path = os.path.join("narration", unique_id)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, "audio.wav")

    with open(file_path, "wb") as f:
        f.write(audio)

    play(audio)


def describe_image(base64_images, context):
    # for testing
    logging.info(f"base64_images: {len(base64_images)}")
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
                    "These are frames a camera stream consist of one to many pictures. Generate a compelling description of the image or a sequence of images: ", *map(lambda x: {"image": x, "resize": 768}, base64_images),
                    # {"type": "text", "text": "Describe this image"},
                    # {
                    #     "type": "image_url",
                    #     "image_url": f"data:image/jpeg;base64,{base64_image}",
                    # },
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
        filepath = os.path.join(static_dir, image_name)
        request = picam2.capture_request()
        request.save("main", filepath)
        request.release()
        logging.info(f"Image captured successfully. Path: {filepath}")
        
        # save to Tigris bucket
        try: 
            svc.upload_file(filepath, BUCKET_NAME, "raw/" + image_name)
        except Exception as e:
            logging.error(f"Error uploading {image_name} to Tigris: {e}")
            
        return filepath
    except Exception as e:
        logging.error(f"Error capturing image: {e}")

def save_image_collage(base64_images):
    collage = None

    for base64_frame in base64_images:
        # Decode the base64 string
        jpg_original = base64.b64decode(base64_frame)
        
        # Convert binary data to numpy array
        jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
        
        # Decode numpy array to image
        frame = cv2.imdecode(jpg_as_np, flags=1)
        
        if collage is None:
            collage = frame
        else:
            collage = np.hstack((collage, frame))

    # Save the montage as an image
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"collage_{timestamp}.jpg"
    file_path = os.path.join(save_dir, file_name)
    cv2.imwrite(file_path, collage)
    # save to Tigris bucket
    try: 
        svc.upload_file(file_path, BUCKET_NAME, "collage/"+file_name)
    except Exception as e:
        logging.error(f"Error uploading {file_name} to Tigris: {e}")
    logging.info(f"Collage saved successfully. Path: {file_path}")

def main():
    context = []
    base64Frames = []

    while True:
        filePath = capture_photo()
        base64_image = encode_image(filePath)
        if len(base64Frames) < COLLAGE_FRAMES:
            base64Frames.append(base64_image)
        else:
            # ---- Uncomment to test AI response on device while developing ----
            # aiResponse = describe_image(base64Frames, context)
            # logging.info(f"AI Response: {aiResponse}")
            # play_audio(aiResponse)
            # context = context + [{"role": "assistant", "content": aiResponse}]
            save_image_collage(base64Frames)
            base64Frames = []

        time.sleep(IMAGE_CAPTURE_INTERVAL)

if __name__ == "__main__":
    main()