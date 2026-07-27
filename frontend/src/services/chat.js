import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export async function sendMessage(message) {
  const { data } = await api.post("/chat", {
    message,
  });

  return data.reply;
}