import { describeImage } from "@/app/utils";
import {
  GetObjectCommand,
  ListObjectsV2Command,
  S3Client,
} from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
import OpenAI from "openai";

export const dynamic = "force-dynamic";
const client = new S3Client();

export type TigrisObject = {
  displayName: string;
  key: string;
  urlSlug: string;
};

export type FilesResponse = Array<TigrisObject>;

export async function POST() {
  const listObjectsV2Command = new ListObjectsV2Command({
    Bucket: process.env.NEXT_PUBLIC_BUCKET_NAME,
    Prefix: `${process.env.COLLAGE_FOLER_NAME!}/`,
  });
  const resp = await client.send(listObjectsV2Command);
  if (!resp.Contents || resp.Contents.length === 0) {
    console.log("No files found.");
    return;
  }

  const latestFile = resp.Contents.sort(
    (a: any, b: any) => b.LastModified - a.LastModified
  )[0];

  if (!latestFile) {
    console.log("No file found.");
    return;
  }

  const getObjectCommand = new GetObjectCommand({
    Bucket: process.env.NEXT_PUBLIC_BUCKET_NAME,
    Key: latestFile.Key,
  });

  const url = await getSignedUrl(client, getObjectCommand, {
    expiresIn: 3600,
  });

  const aiResponse = await describeImage(url);

  return Response.json(aiResponse);
}
