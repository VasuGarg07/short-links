export const SHORT_LINK_BASE = "http://127.0.0.1:8000";

export async function createLink(
  url: string,
): Promise<{ slug: string; alreadyExisted: boolean }> {
  const response = await fetch("/links", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  if (response.status === 422) {
    throw new Error("That does not look like a valid http or https link.");
  }
  if (!response.ok) {
    throw new Error("Something went wrong. Please try again.");
  }
  const body = (await response.json()) as { slug: string };
  return { slug: body.slug, alreadyExisted: response.status === 200 };
}

export async function getClicks(slug: string): Promise<number | null> {
  const response = await fetch(`/links/${slug}/stats`);
  if (!response.ok) return null;
  const body = (await response.json()) as { clicks: number };
  return body.clicks;
}
