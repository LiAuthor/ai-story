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
