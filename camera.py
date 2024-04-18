
from picamera2 import Picamera2, Preview
import time, os, logging
from datetime import datetime
from openai import OpenAI
import base64
import cv2
import numpy as np
from elevenlabs import generate, play, set_api_key, voices
from dotenv import load_dotenv
import resend
import json

load_dotenv()

logging.basicConfig(level=logging.INFO) 
save_location='static'
save_dir = os.path.join(os.getcwd(), save_location)
USE_ELEVEN = False
os.makedirs(save_dir, exist_ok=True)
if (os.environ.get("ELEVEN_API_KEY") != None):
    set_api_key(os.environ.get("ELEVEN_API_KEY"))
    USE_ELEVEN = True
resend.api_key = os.environ.get("RESEND_API_KEY")
print(f"USE_ELEVEN: {USE_ELEVEN}")

openAI = OpenAI()

picam2 = Picamera2()
picam2.start()
time.sleep(2)
requestPrompt = os.environ.get("REQUEST_PROMPT")
lastEmailTs = None

def play_audio(text):
    try: 
        audio = generate(text, voice=os.environ.get("ELEVEN_VOICE_ID"))
        unique_id = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8").rstrip("=")
        dir_path = os.path.join("narration", unique_id)
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, "audio.wav")

        with open(file_path, "wb") as f:
            f.write(audio)

        play(audio)
    except Exception as e:
        print(f"Error generating and playing audio: {e}")


def describe_image(base64_images):
    # for testing
    logging.info(f"base64_images: {len(base64_images)}")
    response = openAI.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                   requestPrompt, *map(lambda x: {"image": x, "resize": 768}, base64_images),
                    # {"type": "text", "text": "Describe this image"},
                    # {
                    #     "type": "image_url",
                    #     "image_url": f"data:image/jpeg;base64,{base64_image}",
                    # },
                ],
            },
        ],
        max_tokens=500,
        tools=[{
            "type": "function", 
            "function": {
                "name": "send_email",
                "description": "send an email based on if a cat was detected in the response", 
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "detected": {
                            "type": "boolean",
                            "description": "if a cat was detected in the response"
                        },
                        "description": {
                            "type": "boolean",
                            "description": "if a cat was detected in the response, the description given by the model"
                        }
                    },
                    "required": ["detected", "description"]
                }
            }
        }]
    )
    print(response.choices[0].message)
    return response.choices[0].message


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
        return filepath
    except Exception as e:
        logging.error(f"Error capturing image: {e}")

def save_image_collage(base64_images):
    montage = None

    for base64_frame in base64_images:
        # Decode the base64 string
        jpg_original = base64.b64decode(base64_frame)
        
        # Convert binary data to numpy array
        jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
        
        # Decode numpy array to image
        frame = cv2.imdecode(jpg_as_np, flags=1)
        
        if montage is None:
            # Initialize the montage with the first frame
            montage = frame
        else:
            # Concatenate the current frame horizontally to the montage
            montage = np.hstack((montage, frame))

    # Save the montage as an image
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = os.path.join(save_dir, f"montage_{timestamp}.jpg")
    cv2.imwrite(file_path, montage)
    logging.info(f"Montage saved successfully. Path: {file_path}")
    return file_path

def send_email(detected, description, filePath):
    global lastEmailTs

    if (detected == False):
        return
    f = open(filePath, "rb").read()
    params = {
        "from": os.environ.get("FROM_EMAIL"),
        "to": [os.environ.get("TO_EMAIL")],
        "subject": "AI dection!",
        "html": f"<strong>{description}</strong>",
        "attachments": [{"content": list(f), "filename": "image.jpg"}],
    }
    email = resend.Emails.send(params)
    if (email['id']!=None):
        lastEmailTs = datetime.now()
    logging.info(f"Email sending status: {email}, {lastEmailTs}")

def main():
    base64Frames = []
    numOfFrames = 5
    availableFunctions = {"send_email": send_email}
    global lastEmailTs

    while True:
        filePath = capture_photo()
        base64_image = encode_image(filePath)
        if len(base64Frames) < numOfFrames:
            base64Frames.append(base64_image)
        else:
            collageFilePath = save_image_collage(base64Frames)
            aiResponse = describe_image(base64Frames)
            if (aiResponse.tool_calls):
                for tool_call in aiResponse.tool_calls:
                    try:
                        print(tool_call.function)
                        args = json.loads(tool_call.function.arguments)
                        print('lastEmailTs', lastEmailTs)
                        if (lastEmailTs == None or (datetime.now() - lastEmailTs).seconds > 60):
                            extra_param = {"filePath": collageFilePath}
                            availableFunctions[tool_call.function.name](**args, **extra_param)
                    except Exception as e:
                        print(f"An error occurred while calling the function: {e}")

            ## TODO - play audio later
            # if (USE_ELEVEN): 
            #     play_audio(aiResponse)
            base64Frames = []

        time.sleep(2)

if __name__ == "__main__":
    main()