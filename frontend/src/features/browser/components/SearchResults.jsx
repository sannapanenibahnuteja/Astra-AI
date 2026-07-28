import ReactMarkdown from "react-markdown";

import useBrowserStore from "../../../store/browserStore";

export default function SearchResults() {

  const summary = useBrowserStore((s) => s.summary);
  const loading = useBrowserStore((s) => s.loading);
  const error = useBrowserStore((s) => s.error);

  if (loading)
    return <h2>Searching...</h2>;

  if (error)
    return <h2>{error}</h2>;

  if (!summary)
    return (
      <p>
        Search results will appear here.
      </p>
    );

  return (

    <div
      style={{
        padding: 25,
        borderRadius: 18,
        background: "rgba(255,255,255,.05)",
      }}
    >

      <ReactMarkdown>

        {summary}

      </ReactMarkdown>

    </div>

  );

}