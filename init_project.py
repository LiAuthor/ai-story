import os

base = "ai-story-app"

files = {
    "app/page.js": """\
"use client";
import { useState } from "react";

export default function Home() {
  const [story, setStory] = useState("");
  const [audio, setAudio] = useState("");

  const run = async () => {
    const res = await fetch("/api/generate", {
      method: "POST",
      body: JSON.stringify({
        name: "小明",
        age: 5,
        interest: "恐龙"
      })
    });

    const data = await res.json();
    setStory(data.story);

    const tts = await fetch("/api/tts", {
      method: "POST",
      body: JSON.stringify({ text: data.story })
    });

    const blob = await tts.blob();
    setAudio(URL.createObjectURL(blob));
  };

  return (
    <div style={{ padding: 40 }}>
      <button onClick={run}>生成故事</button>
      <p>{story}</p>
      {audio && <audio controls src={audio} />}
    </div>
  );
}
""",

    "app/api/generate/route.js": """\
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
""",

    "app/api/tts/route.js": """\
import { ttsWithFallback } from "@/lib/tts";

export async function POST(req) {
  const { text } = await req.json();

  const audio = await ttsWithFallback(text);

  return new Response(audio, {
    headers: { "Content-Type": "audio/mpeg" }
  });
}
""",

    "lib/llm/groq.js": """\
import axios from "axios";

export async function callGroq(prompt) {
  const res = await axios.post(
    "https://api.groq.com/openai/v1/chat/completions",
    {
      model: "llama3-70b-8192",
      messages: [{ role: "user", content: prompt }]
    },
    {
      headers: {
        Authorization: `Bearer ${process.env.GROQ_API_KEY}`
      }
    }
  );

  return res.data.choices[0].message.content;
}
""",

    "lib/llm/index.js": """\
import { callGroq } from "./groq";

export async function generateWithFallback(prompt) {
  return await callGroq(prompt);
}
""",

    "lib/tts/elevenlabs.js": """\
import axios from "axios";

export async function elevenTTS(text) {
  const res = await axios({
    method: "POST",
    url: "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL",
    headers: {
      "xi-api-key": process.env.ELEVENLABS_API_KEY,
      "Content-Type": "application/json"
    },
    data: {
      text,
      model_id: "eleven_multilingual_v2"
    },
    responseType: "arraybuffer"
  });

  return res.data;
}
""",

    "lib/tts/index.js": """\
import { elevenTTS } from "./elevenlabs";

export async function ttsWithFallback(text) {
  return await elevenTTS(text);
}
""",

    "lib/cache/redis.js": """\
import Redis from "ioredis";

export const redis = new Redis(process.env.REDIS_URL);
""",

    "lib/utils/retry.js": """\
export async function retry(fn, retries = 2) {
  try {
    return await fn();
  } catch (err) {
    if (retries <= 0) throw err;
    return retry(fn, retries - 1);
  }
}
""",

    "lib/rateLimit.js": """\
import { redis } from "./cache/redis";

export async function rateLimit(ip) {
  const key = `rate:${ip}`;
  const count = await redis.incr(key);

  if (count === 1) {
    await redis.expire(key, 60);
  }

  if (count > 10) {
    throw new Error("Too many requests");
  }
}
""",

    "lib/auth.js": """\
import jwt from "jsonwebtoken";

export function sign(userId) {
  return jwt.sign({ userId }, process.env.JWT_SECRET);
}

export function verify(token) {
  return jwt.verify(token, process.env.JWT_SECRET);
}
""",

    ".env.local": """\
GROQ_API_KEY=
ELEVENLABS_API_KEY=
REDIS_URL=
JWT_SECRET=your_secret
""",

    "package.json": """\
{
  "name": "ai-story-app",
  "version": "1.0.0",
  "scripts": {
    "dev": "next dev"
  },
  "dependencies": {
    "axios": "^1.6.0",
    "ioredis": "^5.3.2",
    "jsonwebtoken": "^9.0.0"
  }
}
""",

    "next.config.js": "module.exports = {};"
}

for path, content in files.items():
    full_path = os.path.join(base, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("✅ 项目创建完成（已切换 ElevenLabs，无 Google TTS）")