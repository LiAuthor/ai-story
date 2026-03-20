import { elevenTTS } from "./elevenlabs";

export async function ttsWithFallback(text) {
  return await elevenTTS(text);
}
