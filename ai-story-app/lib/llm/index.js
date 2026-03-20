import { callGroq } from "./groq";

export async function generateWithFallback(prompt) {
  return await callGroq(prompt);
}
