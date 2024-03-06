export default async function Page({searchParams}: {searchParams: {
  name: string;
}}) {
  const videoUrl: string = `https://${process.env.BUCKET_NAME}.fly.storage.tigris.dev/${searchParams.name}`
  return (
    <body>
      <h3>Playing video from Tigris:</h3>
      <video id="vid1" width="640" height="480" controls preload="auto" data-setup="{}">
        <source src={`${videoUrl}`} type="video/mp4" />
      </video>
    </body>
  )
}
