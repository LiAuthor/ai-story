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
