## Multi Modal Starter Kit

### Web app

#### Video narration

TODO

#### Object detection

This part of the app assumes you have a set of video snapshots stored in Tigris in real time -- the app takes the snapshot and send it to GPT-4v for comments. If the object or scenario you are detecting shows up on the picture, the app will use Resend to send you an email.

1. `npm install`
2. `npm run dev`
3. open another terminal tab and run `npx inngest-cli@latest dev`

### Raspberry Pi setup

Details [here](https://github.com/tigrisdata-community/multi-modal-starter-kit/tree/main/clients/raspberry-pi)
