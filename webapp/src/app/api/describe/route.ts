import { describeImage } from "@/app/utils";
import { NextRequest } from "next/server";

export async function POST(req: NextRequest) {
  const videoUrl = (await req.json())["frame"];
  const aiResponse = await describeImage(videoUrl);
  console.log("querying openai for narration")
  return new Response(aiResponse.content);
}