import { inngest } from "@/inngest/client";
import {
  GetObjectCommand,
  ListObjectsV2Command,
  S3Client,
} from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
import OpenAI from "openai";
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";
import { Resend } from "resend";
import { EmailTemplate } from "@/components/emailTemplate";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY, // This is the default and can be omitted
});
const client = new S3Client();
const resend = new Resend(process.env.RESEND_API_KEY);

export async function fetchLatestFromTigris() {
  const listObjectsV2Command = new ListObjectsV2Command({
    Bucket: process.env.NEXT_PUBLIC_BUCKET_NAME,
    Prefix: process.env.COLLAGE_FOLER_NAME
      ? `${process.env.COLLAGE_FOLER_NAME!}/`
      : "",
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
    Bucket: process.env.BUCKET_NAME,
    Key: latestFile.Key,
  });

  const url = await getSignedUrl(client, getObjectCommand);
  inngest.send({
    name: "Tigris.complete",
    data: { url },
  });
  return url;
}

export async function describeImage(url: string) {
  const chatCompletion = await openai.chat.completions.create({
    messages: [
      {
        role: "system",
        content: `
              You are an AI assistant that can help me detect if there is a cat sitting on the cat bed. ONLY reply TRUE or FALSE.
           `,
      },
      {
        role: "user",
        content: [
          {
            type: "text",
            text: `These are frames a camera stream consist of one to many pictures. Generate a compelling description of the image or a sequence of images: "`,
          },
          {
            type: "image_url",
            image_url: { url: url },
          },
        ],
      },
    ],
    model: "gpt-4-vision-preview",
    max_tokens: 2048,
  });
  const content = chatCompletion.choices[0].message.content;
  console.log("AI Response", content);
  const result = {
    message: chatCompletion.choices[0].message,
    url,
    ts: Date.now(),
  };

  if (["TRUE", "FALSE"].includes(content || "")) {
    inngest.send({
      name: "aiResponse.complete",
      data: { ...result },
    });
  } else {
    // inngest will auto retry
    throw new Error("OpenAI response does not conform to the expected format.");
  }

  return result;
}

export async function notifyViaEmail(url: string) {
  const { data, error } = await resend.emails.send({
    from: process.env.FROM_EMAIL!,
    to: [process.env.TO_EMAIL!],
    subject: "AI detection",
    react: EmailTemplate({ url }),
    html: "",
  });
}

export const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(1, "10 m"),
  analytics: true,
  prefix: "@upstash/ratelimit",
});
