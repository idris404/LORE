import os
import httpx
from utils.retry import retry_async

GITHUB_API = "https://api.github.com"
_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def _auth_headers() -> dict:
    token = os.getenv("GITHUB_TOKEN", "")
    # Only use token if it looks like a real one (not a placeholder)
    if token and not token.startswith("ghp_...") and len(token) > 10:
        return {**_HEADERS, "Authorization": f"Bearer {token}"}
    return _HEADERS


@retry_async(max_attempts=3, delay=1.0)
async def search_repos(keywords: list[str], max_results: int = 10) -> list[dict]:
    query = " ".join(keywords) + " topic:ai"
    params = {"q": query, "sort": "stars", "order": "desc", "per_page": max_results}
    async with httpx.AsyncClient(headers=_auth_headers(), timeout=15) as client:
        r = await client.get(f"{GITHUB_API}/search/repositories", params=params)
        r.raise_for_status()
        items = r.json().get("items", [])
    return [
        {
            "title": repo["full_name"],
            "url": repo["html_url"],
            "abstract": repo.get("description") or "",
            "stars": repo.get("stargazers_count", 0),
            "language": repo.get("language"),
            "topics": repo.get("topics", []),
            "source": "github",
        }
        for repo in items
    ]


@retry_async(max_attempts=3, delay=1.0)
async def get_readme(owner: str, repo: str) -> str:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/readme"
    headers = {**_auth_headers(), "Accept": "application/vnd.github.raw+json"}
    async with httpx.AsyncClient(headers=headers, timeout=15) as client:
        r = await client.get(url)
        if r.status_code == 404:
            return ""
        r.raise_for_status()
        return r.text
