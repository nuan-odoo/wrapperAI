# WrapperAI

A shadow/wrapper API that drives a chatbot GUI using browser automation.  
Built as a university assignment exploring wrapper APIs, their real-world applications, and ethics.

## How it works

WrapperAI spins up a headless Chromium browser inside Docker, logs into a chatbot, and exposes the conversation as a clean REST API — mimicking what a real LLM API looks like.

```
Your Request → FastAPI → Playwright (Headless Chrome) → Chatbot GUI → Response → You
```

## Running it

You only need Docker installed. No Python, no anything else.

```bash
docker run -p 8000:8000 \
  -e CHATBOT_EMAIL=your@email.com \
  -e CHATBOT_PASSWORD=yourpassword \
  ghcr.io/YOUR_GITHUB_USERNAME/wrapperai:latest
```

Or with docker-compose (edit the email/password in `docker-compose.yml` first):

```bash
docker-compose up
```

## Using the API

**Send a message:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is a wrapper API?"}'
```

**Check the API is alive:**
```bash
curl http://localhost:8000/health
```

**Interactive docs (open in browser):**
```
http://localhost:8000/docs
```

## Endpoints

| Method | Endpoint  | Description                        |
|--------|-----------|------------------------------------|
| POST   | `/chat`   | Send a message, get a response     |
| GET    | `/health` | Check browser session is alive     |
| GET    | `/docs`   | Interactive API documentation      |

## Tech Stack

- **FastAPI** — API framework
- **Playwright** — Browser automation
- **Docker** — Containerisation
- **GitHub Actions** — Auto-builds the image on every push
- **ghcr.io** — Hosts the Docker image

## Ethics & Real-World Context

This project explores the concept of shadow APIs — a technique used in RPA (Robotic Process Automation) tools like UiPath. Key considerations:

- Most chatbot Terms of Service prohibit automated access
- Shadow APIs are fragile — any UI update can break them
- They bypass rate limits designed for fairness
- Legitimate uses include legacy system integration where no API exists
