import jwt from "jsonwebtoken";

export function sign(userId) {
  return jwt.sign({ userId }, process.env.JWT_SECRET);
}

export function verify(token) {
  return jwt.verify(token, process.env.JWT_SECRET);
}
