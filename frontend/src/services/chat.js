import { API } from "../constants/api";

export async function sendMessage(message) {
  const response = await fetch(API.CHAT, {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      message,
    }),
  });

  if (!response.ok) {
    throw new Error("Unable to reach Astra.");
  }

  const data = await response.json();

  return data.response;
}

export async function streamMessage(message, onChunk) {
  const response = await fetch(API.CHAT_STREAM, {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      message,
    }),
  });

  if (!response.ok) {
    throw new Error("Unable to reach Astra.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  let fullResponse = "";

  while (true) {
    const { value, done } = await reader.read();

    if (done) break;

    fullResponse += decoder.decode(value);

    onChunk(fullResponse);
  }

  return fullResponse;
}