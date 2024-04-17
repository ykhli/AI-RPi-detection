## AI Raspberry Pi Cat Detection 🐱

A multi-modal starter kit for cat motion detection.... on your Raspberry Pi! 🥧🍓

This starter kit is super simple: it allows you to use your Raspberry Pi to monitor what your cat does at home, and email you when your cat does something it's not supposed to do. My #1 use case is detecting if my cats are jumping on my dinning table or kitchen counter. 

Of course this doesn't just work for cats 😄. You are welcomed to simply change the prompts and do other kinds of detections: 

- 🐦 for bird watching: email a summary of what birds came by during the day, for the birdies
- 🐻 Racoon deterrent (I have not tried this, but you can?): play loud sound when AI sees Racoons going through your trash cans. You need an external speaker attached to your RPi if you want to do this. 
- 🪴 Plant monitor: email you when your plants are dying from not being watered
- 📦 Package alert: email when there's a new package delivered at the door, even better, AI can tell you if it's a big one
- (submit your fun use cases!)

## Stack
- 🧠 Multi-modal models: OpenAI
- 📫 Notification: [Resend](https://resend.com/)
- 📢 Narration (optional): [ElevenLabs](https://elevenlabs.io/)
- 🐱 Cats

## Quickstart
To try out this starter kit, you need a Raspberry Pi with a camera module, optional a speaker module depending on your use case.
I can send you one if you are one of the first few lucky people to try this kit :). Discord DM me.

1. Create and activate your own venv
   `python -m venv --system-site-packages rpi-venv`\
   `source rpi-venv/bin/activate`

2. Install requirements\
   `pip install -r requirements.txt`

3. Acquire OpenAI API key

   Visit https://platform.openai.com/account/api-keys to get your OpenAI API key and set the `OPENAI_API_KEY` environment variable.

4. Acquire Resend API key
   Visit https://resend.com/api-keys to get your Resend API key and set `RESEND_API_KEY` environment variable.

5. Run `python camera.py`
