import "./BrowserPage.css";

import SearchBar from "./components/SearchBar";
import SearchResults from "./components/SearchResults";

export default function BrowserPage() {
  return (
    <div className="browser-page">

      <div className="browser-header">

        <h1>🌐 Astra Browser</h1>

        <p>
          AI-powered web search with summaries and sources.
        </p>

      </div>

      <SearchBar />

      <SearchResults />

    </div>
  );
}