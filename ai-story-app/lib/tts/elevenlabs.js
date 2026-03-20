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
