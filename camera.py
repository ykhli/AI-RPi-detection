from picamera2 import Picamera2, Preview
import time, os, logging
from datetime import datetime
from openai import OpenAI
import base64
import cv2
import numpy as np
from elevenlabs import generate, play, set_api_key, save, voices
from dotenv import load_dotenv
import resend
import json
from exif import Image as ExifImage

load_dotenv()

USE_LOCAL_MODEL = True
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
    weights = models.ResNeXt101_32X8D_Weights.DEFAULT
    preprocess = weights.transforms()
    model = models.resnext101_32x8d(weights=weights)
    model.eval()
    model_input_size = 224, 224

    # End the timer
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Loaded local model to memory in {execution_time} seconds")

animals = [
    "kit fox", "English setter", "Australian terrier", "grey whale", "lesser panda", "Egyptian cat",
    "ibex", "Persian cat", "cougar", "gazelle", "porcupine", "sea lion", "badger", "Great Dane",
    "Scottish deerhound", "killer whale", "mink", "African elephant", "red wolf", "jaguar", "hyena",
    "titi monkey", "three-toed sloth", "sorrel", "black-footed ferret", "dalmatian", "Staffordshire bullterrier",
    "Bouvier des Flandres", "weasel", "miniature poodle", "bighorn sheep", "fox squirrel", "colobus monkey",
    "tiger cat", "impala", "coyote", "Yorkshire terrier", "Newfoundland dog", "red fox", "hartebeest", "grey fox",
    "Pekinese", "guenon monkey", "mongoose", "indri", "tiger", "wild boar", "zebra", "ram", "orangutan", "basenji",
    "leopard", "vizsla", "squirrel monkey", "Siamese cat", "chimpanzee", "komondor", "proboscis monkey",
    "guinea pig", "white wolf", "polar bear", "gorilla", "ox", "Tibetan mastiff", "spider monkey", "Doberman",
    "warthog", "Arabian camel", "siamang", "golden retriever", "Border collie", "hare", "boxer", "patas monkey",
    "baboon", "macaque", "capuchin", "flat-coated retriever", "hog", "Eskimo dog", "Brittany spaniel",
    "Gordon setter", "dingo", "hamster", "Arctic fox", "water buffalo", "American black bear", "Angora rabbit",
    "bison", "howler monkey", "hippopotamus", "giant panda", "tabby cat", "marmoset", "Saint Bernard", "armadillo",
    "redbone", "polecat", "marmot", "gibbon", "llama", "wood rabbit", "lion", "Irish setter", "dugong",
    "Indian elephant", "beaver", "Madagascar cat", "Rhodesian ridgeback", "lynx", "African hunting dog", "langur",
    "timber wolf", "cheetah", "sloth bear", "German shepherd", "otter", "koala", "tusker", "echidna",
    "wallaby", "platypus", "wombat", "Siberian husky", "English springer", "malamute", "Walker hound",
    "Welsh springer spaniel", "whippet", "Weimaraner", "soft-coated wheaten terrier", "Dandie Dinmont",
    "Old English sheepdog", "otterhound", "bloodhound", "Airedale", "giant schnauzer", "black-and-tan coonhound",
    "papillon", "Mexican hairless", "Cardigan Welsh corgi", "malinois", "Lhasa", "Norwegian elkhound", "Rottweiler",
    "Saluki", "schipperke", "Brabancon griffon", "West Highland white terrier", "Sealyham terrier", "Irish wolfhound",
    "EntleBucher", "French bulldog", "Bernese mountain dog", "Maltese dog", "Norfolk terrier", "toy terrier",
    "cairn terrier", "groenendael", "clumber spaniel", "Afghan hound", "Japanese spaniel", "borzoi", "toy poodle",
    "Kerry blue terrier", "Scotch terrier", "Boston bull", "Greater Swiss Mountain dog", "Appenzeller", "Shih-Tzu",
    "Irish water spaniel", "Pomeranian", "Bedlington terrier", "miniature schnauzer", "collie", "Irish terrier",
    "affenpinscher", "silky terrier", "beagle", "Leonberger", "German short-haired pointer", "dhole", "Chesapeake Bay retriever",
    "bull mastiff", "kuvasz", "pug", "curly-coated retriever", "Norwich terrier", "keeshond",  "Lakeland terrier", "standard schnauzer", "Tibetan terrier", "chrysanthemum dog", "wire-haired fox terrier",
    "basset", "basset hound", "chow", "chow chow", "American Staffordshire terrier", "Staffordshire terrier",
    "American pit bull terrier", "pit bull terrier", "Shetland sheepdog", "Shetland sheep dog", "Shetland",
    "Great Pyrenees", "Chihuahua", "Labrador retriever", "Samoyed", "Samoyede", "bluetick", "kelpie",
    "miniature pinscher", "Italian greyhound", "cocker spaniel", "English cocker spaniel", "cocker",
    "Sussex spaniel", "Pembroke", "Pembroke Welsh corgi", "Blenheim spaniel", "Ibizan hound", "Ibizan Podenco",
    "English foxhound", "briard", "Border terrier", "tabby"]

interesting_array = animals

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

        save(audio, file_path)
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
    print("response:", response.choices[0].message)
    return response.choices[0].message
    
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
    captureMode = False

    while True:
        filePath, image = take_photo()
        if not captureMode:
            interestingBool, objects_detected = is_interesting(image, filePath)
            if interestingBool:
                captureMode = True
                print(f"Interesting image detected: {objects_detected}")
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

            if (USE_ELEVEN): 
                play_audio(aiResponse.content)
            base64Frames = []

        time.sleep(2)

if __name__ == "__main__":
    main()