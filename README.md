## AI Raspberry Pi Cat Detection 🐱


A hardware AI starter kit for cat detection and narration .... on your Raspberry Pi! 🥧🍓


Demo (sound on 🔊):

https://github.com/ykhli/AI-RPi-detection/assets/3489963/865250d7-2f42-4f58-899b-36e34fb078b5


This starter kit is super simple: it allows you to use your Raspberry Pi to monitor what your cat does at home, and email you when your cat does something it's not supposed to do. My #1 use case is detecting if my cats are jumping on my dinning table or kitchen counter. You could also opt to turn this into an AI narrator, where the voice narrates on everything it sees.

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

## Overview

- 🚀 [Quickstart](#quickstart)
- 💻 [Dev Environment](#dev-environment)

## Quickstart
To try out this starter kit, you need a Raspberry Pi with a camera module, optional a speaker module depending on your use case.
I can send you one if you are one of the first few lucky people to try this kit :). Discord DM me.

**0. Set up your Raspberry Pi**

   This kit has been tested on Raspberry Pi 4 and 5. If you just got your RPi, follow their [documentations](https://www.raspberrypi.com/documentation/computers/getting-started.html) to set it up. 


   📷 You will also need a camera attached to the RPi to test this out. [This](https://www.adafruit.com/product/5657) is the most standard RPi camera, but any camera should work.
   📢 If you want to hear the narration, you will need to set up 11labs and attach a speaker to the RPi. 

**1. Create and activate your venv**
   ```
   python -m venv --system-site-packages rpi-venv
   source rpi-venv/bin/activate
   ```

**2. Install requirements**
   ```
   pip install -r requirements.txt
   ```

**3. Create an .env file**
   ```
   cp .env.example .env
   ```

**4. Get OpenAI API key**

   Visit https://platform.openai.com/account/api-keys to get your OpenAI API key and set the `OPENAI_API_KEY` in the .env file

**5. Get Resend key**

   Visit https://resend.com/api-keys to get your Resend API key and set `RESEND_API_KEY` in the .env file
   Note that before using Resend to send emails, you also need to verify your domain [here](https://resend.com/domains). Resend also has a helpful guide on [everything related to domains](https://resend.com/docs/dashboard/domains/introduction).

**6. (Optional) Get ElevenLabs key**

   a. Go to https://elevenlabs.io/, log in, and click on your profile picture on lower left. Select "Profile + API key". Copy the API key and save it as `ELEVEN_API_KEY` in the .env file
   
   b. Select a 11labs voice by clicking on "Voices" on the left side nav bar and navigate to "VoiceLab". Copy the voice ID and save it as `ELEVEN_VOICE_ID_VOICE_ID` in .env


**7. Run the program**
   ```
   python camera.py
   ```
   The program will save all the pictures taken under /static folder. 

**8. Update the prompt!**

   You probably noticed that we have a default prompt in .env called `REQUEST_PROMPT` -- you can update this prompt and tell the AI model to detect other things! One example that worked for me is the following prompt -- I got a summary of what my cat was doing every minute.

   `
   "You are an AI assistant who can send emails based on what you see in the picture.
   If you see a cat in the picture, send an email summarizing what it's doing. The email should include a description parameter, which is describing what the cat is doing.
   For example, the description could be 'The cat is playing with a ball.'"
   `

   
   
## Dev Environment 

### SSH
The easiest way to work with an RPi is to ssh into it and use it as if it's a server. For the latest RPi distribution, you could ssh into it by running 
```
ssh username@RPI_NAME
```
Both username and RPi name can be found when you first set up the RPi

### Testing out code
All you need to run this kit is `python camera.py` in a virtual environment. What I usually do is checking out the git repository on the RPi and test out functions from there. If I needed to change anything, I use vim to edit on cli.

You could also choose to mount RPi as a folder on your local file system using something like [sshfs](https://github.com/libfuse/sshfs). This way you could edit the file on RPi as if it's a file local to your system using any editor of your choice. 

