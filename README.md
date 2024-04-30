## AI Raspberry Pi Cat Detection 🐱

AI Raspberry Pi cat detection and notification: get a text/email when your cat does something it's not supposed to do, and have AI narrate what it sees 👁️

This RPi starter kit makes it easy to get started with AI (both running device model & calling an LLM), and it's generalizable across other vision-related use cases.

**Demo** (sound on 🔊):

[![AI cat detection demo](http://img.youtube.com/vi/8KSAiwyDoy8/0.jpg)](http://www.youtube.com/watch?v=8KSAiwyDoy8 "AI Cat Detection & Narration")

https://www.youtube.com/watch?v=8KSAiwyDoy8

Have questions? Join [AI Stack devs](https://discord.gg/TsWCNVvRP5)

This starter kit is super simple: it allows you to use your Raspberry Pi to monitor what your cat does at home, and email you when your cat does something it's not supposed to do. **My #1 use case is detecting if my cats are jumping on my dinning table or kitchen counter.** You could also opt to turn this into an AI narrator, where the voice narrates on everything it sees.

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
- 💻 Orchestration and function calling: [Langchain](https://python.langchain.com/docs/get_started/introduction/)
- 📖 Docs: [Mintlify](https://ai-cat-detection.yoko.dev/introduction)
- 🐱 Cats

## Overview

- 🚀 [Quickstart](#quickstart)
- 💻 [Dev Environment](#dev-environment)

## Quickstart

To try out this starter kit, you need a Raspberry Pi with a camera module, optionally a speaker module for narration!

I can send you one if you are one of the first few lucky people to try this kit :). Discord DM me.

For detailed setup instructions, visit our docs page [here](https://ai-cat-detection.yoko.dev/) (powered by [Mintlify](https://mintlify.com/))

## Dev Environment

You can find helpful tips on setting up dev environment [here](https://ai-cat-detection.yoko.dev/dev-environment)

## FAQ

For common questions and bugs, feel free to try out our AI Q&A bot [here](https://ai-cat-detection.yoko.dev/introduction). You could simply type on the search bar or use cmd+k shortcut.
