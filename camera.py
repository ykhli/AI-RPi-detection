from picamera2 import Picamera2
import time, os, logging, getpass
from datetime import datetime
import base64
import cv2
import numpy as np
from elevenlabs import generate, play, set_api_key, save, voices
from dotenv import load_dotenv
import resend
import json
import interesting_list
from exif import Image as ExifImage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

USE_LOCAL_MODEL = os.environ.get("USE_LOCAL_MODEL", "False").lower() == "true"
print(f"USE_LOCAL_MODEL: {USE_LOCAL_MODEL}")
if USE_LOCAL_MODEL: 
    print(f"Loading local model to memory")
    # Start the timer
    start_time = time.time()
    # Load the model and libraries if we're using it
    import torch
    from torchvision import models
    torch.backends.quantized.engine = 'qnnpack'

    # Load model into memory and prep weights
    weights = models.Swin_V2_S_Weights.DEFAULT
    preprocess = weights.transforms()
    model = models.swin_v2_s(weights=weights)
    model.eval()
    model_input_size = 640, 480

    # End the timer
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Loaded local model to memory in {execution_time} seconds")

interesting_array = interesting_list.animals

logging.basicConfig(level=logging.INFO) 
llm = ChatOpenAI(model="gpt-4-vision-preview", max_tokens=500)
save_location = os.environ.get("TMP_FILE_PATH", 'static')
save_base_path = os.environ.get("TMP_FILE_BASE_PATH", "/tmp")
save_dir = os.path.join(save_base_path, save_location)
USE_ELEVEN = False
os.makedirs(save_dir, exist_ok=True)
if (os.environ.get("ELEVEN_API_KEY") != None):
    set_api_key(os.environ.get("ELEVEN_API_KEY"))
    USE_ELEVEN = True
resend.api_key = os.environ.get("RESEND_API_KEY")
print(f"USE_ELEVEN: {USE_ELEVEN}")

picam2 = Picamera2()
picam2.start()
time.sleep(2)
requestPrompt = os.environ.get("REQUEST_PROMPT")
lastEmailTs = None

@tool
def send_email(detected, description, filePath):
    """
    send an email based on if a cat was detected in the response. 
    There are three parameters: 
    - detected: Boolean. Is the object detected?
    - description: string. Description of the scene
    - filePath: string. You don't need to worry about this one. 
    """

    global lastEmailTs

    if (detected == False):
        return
    f = open(filePath, "rb").read()
    params = {
        "from": os.environ.get("FROM_EMAIL"),
        "to": [os.environ.get("TO_EMAIL")],
        "subject": "AI Detection!",
        "html": f"<strong>{description}</strong>",
        "attachments": [{"content": list(f), "filename": "image.jpg"}],
    }
    email = resend.Emails.send(params)
    if (email['id']!=None):
        lastEmailTs = datetime.now()
    logging.info(f"Email sending status: {email}, {lastEmailTs}")

tools = [send_email]
llm_with_tools = llm.bind_tools(tools)

def play_audio(text):
    try: 
        audio = generate(text, voice=os.environ.get("ELEVEN_VOICE_ID"))
        unique_id = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8").rstrip("=")
        dir_path = os.path.join("narration", unique_id)
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, "audio.wav")

        save(audio, file_path)
        play(audio)
    except Exception as e:
        print(f"Error generating and playing audio: {e}")


def describe_image(collageFilePath):
    base64 = encode_image(collageFilePath)
    result = llm_with_tools.invoke(
        [HumanMessage(
            content = [
                 {"type": "text", "text": requestPrompt},
                 {"type": "image_url", 
                  "image_url": 
                    {"url": f"data:image/jpeg;base64,{base64}"
                    }
                }
        ])]
    )
    print('langchain result: ', result)
    return result
    
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

# image from PIL
def is_interesting(image, filePath):
    # Everything is interesting if we're not using the model
    if not USE_LOCAL_MODEL:
        return True, "Everything is awesome"
    model_image = image.resize(model_input_size).convert('RGB')
    # preprocess
    input_tensor = preprocess(model_image)

    # create a mini-batch as expected by the model
    input_batch = input_tensor.unsqueeze(0)

    # output = net(input_batch)
    prediction = model(input_batch)

    top = list(enumerate(prediction[0].softmax(dim=0)))    
    top.sort(key=lambda x: x[1], reverse=True)

    result = ""
    top_categories = []
    for idx, val in top[:10]:
        result_str = f"{val.item()*100:.2f}% {weights.meta['categories'][idx]}"
        top_categories.append(weights.meta['categories'][idx])
        result = result + (result_str + "\n")
        print(result_str)

    with open(filePath, "rb") as saved_image:
        exif_image = ExifImage(saved_image)
    
    exif_image.user_comment = result

    # this cases multiple writes for 1 image, not ideal
    with open(filePath, 'wb') as new_image_file:
        new_image_file.write(exif_image.get_file())
    
    return any(x in interesting_array for x in top_categories), result

def take_photo():
    global picam2
    try:
        timestamp = int(datetime.timestamp(datetime.now()))
        image_name = f'{timestamp}.jpg'
        current_dir = os.path.dirname(__file__)
        static_dir = os.path.join(current_dir, save_dir)
        filepath = os.path.join(static_dir, image_name)
        request = picam2.capture_request()
        image = request.make_image("main")

        # request.save("main", filepath)
        image.save(filepath)

        request.release()
        logging.info(f"Image captured successfully. Path: {filepath}")

        return filepath, image
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


def main():
    base64Frames = []
    numOfFrames = 5
    availableFunctions = {"send_email": send_email}
    global lastEmailTs
    captureMode = False

    while True:
        filePath, image = take_photo()
        if not captureMode:
            interestingBool, objects_detected = is_interesting(image, filePath)
            if interestingBool:
                captureMode = True
                print(f"Interesting image detected:\n {objects_detected}")
            else:
                print("Not interesting")
                continue

        base64_image = encode_image(filePath)
        if len(base64Frames) < numOfFrames:
            base64Frames.append(base64_image)
        else:
            # We got enough frames, let's process them
            captureMode = False 
            collageFilePath = save_image_collage(base64Frames)
            aiResponse = describe_image(collageFilePath)
            descriptionText = None
            if (aiResponse.tool_calls):
                for tool_call in aiResponse.tool_calls:
                    try:
                        functionToCall = tool_call['name']
                        args = tool_call['args']
                        descriptionText = args['description']
                        print('lastEmailTs', lastEmailTs)
                        if (lastEmailTs == None or (datetime.now() - lastEmailTs).seconds > 60):
                            args["filePath"] = collageFilePath
                            selectedFunction = availableFunctions[functionToCall]
                            selectedFunction.invoke(args)
                            print(f'description text: {descriptionText}')
                    except Exception as e:
                        print(f"An error occurred while calling the function: {e}")

            if (USE_ELEVEN): 
                play_audio(aiResponse.content or descriptionText) 
            base64Frames = []

        time.sleep(2)

if __name__ == "__main__":
    main()