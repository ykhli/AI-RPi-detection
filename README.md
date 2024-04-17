## AI Raspberry Pi Cat Detection 🐱

A multi-modal starter kit for cat detection and narration .... on your Raspberry Pi! 🥧🍓

Demo (sound on 🔊):

https://github.com/ykhli/AI-RPi-detection/assets/3489963/865250d7-2f42-4f58-899b-36e34fb078b5


This starter kit is super simple: it allows you to use your Raspberry Pi to monitor what your cat does at home, and email you when your cat does something it's not supposed to do. My #1 use case is detecting if my cats are jumping on my dinning table or kitchen counter. You could also opt to turn this into an AI narrator, where the voice narrates on everything it sees.

Of course this doesn't just work for cats 😄. You are welcomed to simply change the prompts and do other kinds of detections: 

- 🐦 for bird watching: email a summary of what birds came by during the day, for the birdies
- 🐻 Racoon deterrent (I have not tried this, but you can?): play loud sound when AI sees Racoons going through your trash cans. You need an external speaker attached to your RPi if you want to do this. 
- 🪴 Plant monitor: email you when your plants are dying from not being watered
- (submit your fun use cases!)

## Stack
- 🧠 Multi-modal models: OpenAI
- 📫 Notification: [Resend](https://resend.com/)
- 📢 Narration (optional): [ElevenLabs](https://elevenlabs.io/)
- 🐱 Cats

## Quickstart
Well you have to have a Raspberry Pi. I can send you some if you are one of the first lucky people to try this kit :). Discord DM me.

1. create and activate your own venv
   `python -m venv --system-site-packages rpi-venv`
   `source rpi-venv/bin/activate`

2. install requirements
   `pip install -r requirements.txt`

3. get an OpenAI key and store it in the env

4. get a Resend key and store it in the env

5. Run `python camera.py`
