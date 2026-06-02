# SearXNG Self Hosting

This project can use a self-hosted SearXNG instance as the news and web-search provider. This is the preferred no-key path when you already have a server such as Contabo.

## Recommended Setup

Run SearXNG separately from the app, then point the app at the SearXNG URL:

```env
SEARXNG_BASE_URLS=https://search.example.com
SEARXNG_PUBLIC_INSTANCES_ENABLED=false
```

Use `SEARXNG_PUBLIC_INSTANCES_ENABLED=false` for production so analysis jobs do not depend on random public instances.

## Minimal Docker Compose Example

Create a separate directory on the server, for example `/opt/searxng`, and run SearXNG there:

```yaml
services:
  searxng:
    image: searxng/searxng:latest
    container_name: searxng
    restart: unless-stopped
    ports:
      - "127.0.0.1:8080:8080"
    volumes:
      - ./searxng:/etc/searxng
    environment:
      - BASE_URL=https://search.example.com/
      - INSTANCE_NAME=daily-stock-analysis-search
```

Put a reverse proxy such as Nginx or Caddy in front of it and expose HTTPS at `https://search.example.com`.

## Required SearXNG Setting

The app calls the SearXNG JSON endpoint, so SearXNG must allow JSON responses. In `/opt/searxng/searxng/settings.yml`, include:

```yaml
search:
  formats:
    - html
    - json
```

Restart SearXNG after changing the file.

## Local Verification

From the server, verify that JSON search works:

```bash
curl "https://search.example.com/search?q=AAPL%20stock%20news&format=json"
```

Then run the app search diagnostic from this project:

```bash
python scripts/check_env.py --search --search-query "Samsung Electronics stock news"
```

## Notes

- SearXNG has no API key cost, but your server still pays normal VPS traffic and CPU cost.
- Some upstream search engines may rate-limit an instance. If searches get unstable, reduce analysis frequency or add another self-hosted URL to `SEARXNG_BASE_URLS` separated by commas.
- Keep SearXNG behind HTTPS. Avoid publishing an unrestricted high-traffic public instance unless you intentionally want to operate one.
