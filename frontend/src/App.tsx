import { type FormEvent, useEffect, useState } from "react";

import { SHORT_LINK_BASE, createLink, getClicks } from "./api";

interface SavedLink {
  slug: string;
  url: string;
}

const STORAGE_KEY = "short-links";

function loadSavedLinks(): SavedLink[] {
  const saved = localStorage.getItem(STORAGE_KEY);
  return saved === null ? [] : (JSON.parse(saved) as SavedLink[]);
}

export default function App() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [links, setLinks] = useState(loadSavedLinks);
  const [clicks, setClicks] = useState<Record<string, number>>({});
  const [copiedSlug, setCopiedSlug] = useState("");

  async function refreshClicks(list: SavedLink[]) {
    const counts: Record<string, number> = {};
    for (const link of list) {
      const count = await getClicks(link.slug);
      if (count !== null) counts[link.slug] = count;
    }
    setClicks(counts);
  }

  useEffect(() => {
    void refreshClicks(links);
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setNotice("");
    setLoading(true);
    try {
      const created = await createLink(url.trim());
      const others = links.filter((link) => link.slug !== created.slug);
      const updated = [{ slug: created.slug, url: url.trim() }, ...others];
      setLinks(updated);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      setNotice(
        created.alreadyExisted
          ? "You already shortened this link."
          : "Your short link is ready.",
      );
      setUrl("");
      void refreshClicks(updated);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  async function handleCopy(slug: string) {
    await navigator.clipboard.writeText(`${SHORT_LINK_BASE}/${slug}`);
    setCopiedSlug(slug);
  }

  return (
    <main className="page">
      <h1>Short Links</h1>
      <p className="subtitle">Paste a long link and get a short one.</p>

      <form className="card" onSubmit={handleSubmit}>
        <div className="row">
          <input
            placeholder="https://example.com/a/very/long/page"
            value={url}
            onChange={(event) => setUrl(event.target.value)}
          />
          <button type="submit" disabled={loading || url.trim() === ""}>
            {loading ? "Shortening..." : "Shorten"}
          </button>
        </div>
        {error !== "" && <p className="error">{error}</p>}
        {notice !== "" && <p className="success">{notice}</p>}
      </form>

      <section className="card">
        <div className="row title-row">
          <h2>Your links</h2>
          {links.length > 0 && (
            <button className="ghost" onClick={() => void refreshClicks(links)}>
              Refresh clicks
            </button>
          )}
        </div>

        {links.length === 0 && <p className="subtitle">No links yet.</p>}

        <ul>
          {links.map((link) => (
            <li key={link.slug}>
              <div className="link-text">
                <a href={`${SHORT_LINK_BASE}/${link.slug}`} target="_blank">
                  {`${SHORT_LINK_BASE}/${link.slug}`}
                </a>
                <span>{link.url}</span>
              </div>
              <strong>{clicks[link.slug] ?? "-"} clicks</strong>
              <button className="ghost" onClick={() => void handleCopy(link.slug)}>
                {copiedSlug === link.slug ? "Copied" : "Copy"}
              </button>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
