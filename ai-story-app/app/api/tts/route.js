import { ttsWithFallback } from "@/lib/tts";

export async function POST(req) {
  const { text } = await req.json();

  const audio = await ttsWithFallback(text);

  return new Response(audio, {
    headers: { "Content-Type": "audio/mpeg" }
  });
}
