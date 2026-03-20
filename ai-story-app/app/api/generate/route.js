import { generateWithFallback } from "@/lib/llm";
import { redis } from "@/lib/cache/redis";
import { rateLimit } from "@/lib/rateLimit";

export async function POST(req) {
  try {
    const ip = req.headers.get("x-forwarded-for") || "unknown";
    await rateLimit(ip);

    const { name, age, interest } = await req.json();

    const key = `story:${name}:${age}:${interest}`;
    const cached = await redis.get(key);

    if (cached) {
      return Response.json({ story: cached, cached: true });
    }

    const prompt = `写一个温馨有趣的儿童故事，主角是${name}，${age}岁，喜欢${interest}`;

    const story = await generateWithFallback(prompt);

    await redis.set(key, story, "EX", 3600);

    return Response.json({ story });
  } catch (e) {
    return Response.json({ error: e.message }, { status: 500 });
  }
}
