import { useState } from "react";
import { Search } from "lucide-react";

import { browserSearch } from "../../../services/browser";
import useBrowserStore from "../../../store/browserStore";

export default function SearchBar() {

  const [text, setText] = useState("");

  const setSummary = useBrowserStore((s) => s.setSummary);
  const setLoading = useBrowserStore((s) => s.setLoading);
  const setError = useBrowserStore((s) => s.setError);

  async function handleSearch() {

    if (!text.trim()) return;

    setLoading(true);
    setError("");

    try {

      const result = await browserSearch(text);

      setSummary(result.summary);

    } catch {

      setError("Search failed.");

    }

    setLoading(false);

  }

  return (

    <div
      style={{
        display: "flex",
        gap: 15,
        marginBottom: 35,
      }}
    >

      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            handleSearch();
          }
        }}
        placeholder="Ask Astra to search..."
        style={{
          flex: 1,
          padding: 18,
          borderRadius: 16,
          background: "rgba(255,255,255,.05)",
          border: "1px solid rgba(255,255,255,.08)",
          color: "white",
        }}
      />

      <button
        onClick={handleSearch}
        style={{
          width: 70,
          borderRadius: 16,
          cursor: "pointer",
          border: "none",
        }}
      >
        <Search />
      </button>

    </div>

  );

}