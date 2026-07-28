import { API } from "../constants/api";

export async function browserSearch(query) {
  const response = await fetch(API.BROWSER, {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      query,
    }),
  });

  if (!response.ok) {
    throw new Error("Search failed.");
  }

  return response.json();
}