import { ListObjectsV2Command, S3Client } from '@aws-sdk/client-s3'

export const dynamic = 'force-dynamic'
const client = new S3Client()

export type TigrisObject = {
  displayName: string,
  key: string,
  urlSlug: string
}

export type FilesResponse = Array<TigrisObject>;

export async function GET () {
  const listObjectsV2Command = new ListObjectsV2Command(
    { Bucket: process.env.NEXT_PUBLIC_BUCKET_NAME })
  const resp = await client.send(listObjectsV2Command)
  const fileList: FilesResponse = []
  if (resp.Contents) {
    for (let i = 0; i < resp.Contents.length; i++) {
      // todo: filter files by extension
      const key = resp.Contents[i].Key
      if (key === undefined) {
        continue
      }
      fileList.push(
        {
          displayName: key,
          key: key,
          urlSlug: key.replace(".", "_")
        })
    }
  }
  return Response.json(fileList)
}
