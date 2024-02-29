The project is hosted at [multi-modal-starter-kit.fly.dev](https://multi-modal-starter-kit.fly.dev/)

## Development setup

First, fork the repo and change to `webapp dir` to install dependencies:

```bash
cd webapp
npm run install
```

The project uses [Next.js](https://nextjs.org/docs) to load and display files
from [Tigris object store](https://www.tigrisdata.com/docs/) on the webapp. For development,
the files are hosted in bucket mentioned in [`.env`](.env) environment file as `BUCKET_NAME`, free to
use your own. 

Before running the web server, let's set the credentials to access the Tigris bucket. You'd need
`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` for the bucket, these can be set in the `.env.development`
file in project root as follows:

```bash
AWS_ACCESS_KEY_ID=<your access key id>
AWS_SECRET_ACCESS_KEY=<your access secret>
```

This `.env.development` file is already included in *gitignore* and *dockerignore* to prevent accidental checkin, Next.js builder will automatically 
[load environment variables](https://nextjs.org/docs/app/building-your-application/configuring/environment-variables#environment-variable-load-order) 
from .env files and use them in the project. Another option is to set these environment variables using
[export](https://ioflood.com/blog/bash-environment-variables/) command from cli.

Next, run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

Take a look at [GET api/files](src/app/api/files/route.ts) API that is used by [/files router](src/app/files/page.tsx) to list the objects from Tigris bucket.  
