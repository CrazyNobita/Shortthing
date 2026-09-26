# ⚡ ShortnerBypass — Telegram Auto Link Bypass Bot & Mini App
> **Developer & Updates:** [@ProviderBotz](https://t.me/ProviderBotz)  
> **Architecture:** Public Telegram Bot + Telethon Userbot Engine (DZHQ + Alex DM) + Obsidian Red Telegram Mini App

---

## 📖 Overview

**ShortnerBypass** is a production-grade Telegram Auto Link Bypass system built on high-performance async Python and Telethon. It bridges public Telegram users and the web via a REST API and a mobile-first Telegram Mini App directly with two underlying bypass providers:
1. **DZHQ Bypass Bot (`@DZHQ_BypassBot`)** — Telegram group bypass flow (`-1003644908415`).
2. **Alex Bypass Bot (`@alexbypassbot`)** — Telegram private DM userbot flow.

All legacy Nick bypass integrations and Alex HTTP API dependencies have been **completely eliminated**. The system strictly relies on Telegram-native message and edited-message detection with zero external databases.

---

## 🏗 Architecture Flow

```text
               PUBLIC TELEGRAM BOT  /  TELEGRAM MINI APP  /  GET /bypass
                                       ↓
                            PROVIDER BYPASS ENGINE
                                       ↓
                             TELETHON USERBOT
                         ┌───────────────────────┐
                         │   Provider Selector   │
                         └───────────────────────┘
                                   ↙   ↘
             ┌─────────────────────────┐   ┌─────────────────────────┐
             │     DZHQ Bypass Bot     │   │     Alex Bypass Bot     │
             │   Telegram Group Flow   │   │     Telegram DM Flow    │
             └─────────────────────────┘   └─────────────────────────┘
                                   ↘   ↙
                        MESSAGE / EDITED MESSAGE PARSER
                                       ↓
                               FINAL BYPASSED URL
                                       ↓
                          USER / BOT / MINI APP RESULT
```

---

## ✨ Key Features

- **Native Bot API 9.4+ Colored Inline Buttons:** Implements real colored background buttons (`ButtonStyle.PRIMARY` for Dark Blue, `ButtonStyle.SUCCESS` for Green, `ButtonStyle.DANGER` for Red) supporting Pyrogram syntax and Telegram clients released after Feb 9, 2026.
- **Double-Engine Architecture:** DZHQ group chat bypass combined with Alex DM bypass.
- **Intermediate Message Filtering:** Tolerates multi-step status messages (`🔄 Bypassing...`, `⏳ Processing...`, `🔍 Checking link...`, `▰▱` progress bars) without premature aborts.
- **Message Edit Monitoring:** Tracks `MessageEdited` events so bots that replace their status message with the destination URL are handled seamlessly.
- **Original URL Protection:** Ensures the submitted shortlink is never erroneously returned as the bypassed result.
- **Mandatory Small-Caps Font:** Styled with the exact custom Unicode alphabet (`ᴧʙᴄᴅєꜰɢʜιᴊᴋʟᴍɴσᴩǫʀѕтυνω᥊ʏᴢ`) for headings and badges.
- **Obsidian Red Telegram Mini App:** Responsive, dark red glassmorphism web app with real-time progress steps, clipboard copy, and Telegram WebApp Haptic Feedback.
- **Unified Engine:** The `/bypass?url=...` endpoint executes the exact same underlying Telethon engine as the Telegram Bot.
- **Zero Database Dependency:** In-memory job state machine, queues, and concurrency managers. (Note: Runtime statistics reset upon server restart).
- **Per-User Rate Limiting & Concurrency:** Configurable rate limits and concurrent job barriers to safeguard accounts from Telegram flood limits.

---

## ⚙️ Environment Variables

Configure these inside your `.env` file or cloud provider environment settings:

| Variable | Required | Default | Description |
|---|---|---|---|
| `BOT_TOKEN` | **Yes** | — | Public Telegram Bot Token (from [@BotFather](https://t.me/BotFather)) |
| `BOT_USERNAME` | **Yes** | — | Bot username without `@` (e.g. `ShortnerBypassBot`) |
| `OWNER_ID` | Optional | — | Numeric Telegram ID of the administrator for audit alerts |
| `TELEGRAM_API_ID` | **Yes** | — | Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `TELEGRAM_API_HASH` | **Yes** | — | Telegram API Hash from [my.telegram.org](https://my.telegram.org) |
| `TELEGRAM_SESSION` | **Yes** | — | Telethon StringSession for the userbot account |
| `DZHQ_BOT_USERNAME` | No | `@DZHQ_BypassBot` | Telegram handle for DZHQ Bot |
| `ALEX_BOT_USERNAME` | No | `@alexbypassbot` | Telegram handle for Alex DM Bot |
| `PUBLIC_URL` | No | `http://localhost:5000` | Publicly reachable domain for the Mini App |
| `PORT` | No | `5000` | Port for the Flask web server |
| `SECRET_KEY` | No | auto-generated | Secret key for Flask session security |
| `ADMIN_PASSWORD` | No | `ProviderPro` | Administrative access credential |
| `BYPASS_IDLE_TIMEOUT_SEC` | No | `30` | Inactivity timeout (reset by progress messages) |
| `ALEX_DM_TIMEOUT_SEC` | No | `75` | Alex DM execution timeout limit |
| `MAX_BYPASS_TIMEOUT_SEC` | No | `120` | Hard ceiling timeout for any single bypass job |
| `RATE_LIMIT_SECONDS` | No | `3` | Minimum seconds between requests per user |
| `MAX_CONCURRENT_PER_USER` | No | `2` | Maximum concurrent jobs running per user |
| `TRACE_BOTS` | No | `false` | Enable verbose provider debugging in logs |

---

## 🔑 Generating a Telethon String Session

To generate a string session for `TELEGRAM_SESSION`:

1. Install Telethon locally:
   ```bash
   pip install telethon
   ```
2. Run this short interactive script:
   ```python
   from telethon.sync import TelegramClient
   from telethon.sessions import StringSession

   api_id = int(input("Enter API ID: "))
   api_hash = input("Enter API Hash: ")

   with TelegramClient(StringSession(), api_id, api_hash) as client:
       print("\nYour TELEGRAM_SESSION string:\n")
       print(client.session.save())
   ```
3. Copy the output string and paste it as `TELEGRAM_SESSION` in `.env`.

---

## 🚀 Local Installation & Run

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd ShortnerBypass
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup `.env`:**
   ```bash
   cp .env.example .env # or edit .env directly
   ```

5. **Start the application:**
   ```bash
   python bot.py
   ```

---

## 🌐 Endpoints

### 1. Web Mini App
- **Endpoint:** `GET /`
- **Output:** Serves the Obsidian Red Telegram Mini App (`index.html`).

### 2. Health Monitoring
- **Endpoint:** `GET /health`
- **Output:**
  ```json
  {
    "developer": "@ProviderBotz",
    "public_bot_online": true,
    "service": "ShortnerBypass",
    "status": "ok",
    "userbot_online": true
  }
  ```

### 3. API Bypass
- **Endpoint:** `GET /bypass?url=https://target-shortlink.com/xyz`
- **Output:**
  ```json
  {
    "developer": "@ProviderBotz",
    "links": {
      "bypassed": "https://final-destination.com/file",
      "original": "https://target-shortlink.com/xyz"
    },
    "response_ms": "1420ms",
    "source": "dzhq",
    "status": true,
    "url": "https://final-destination.com/file"
  }
  ```

---

## 🐳 Docker Deployment

Build and run using Docker:

```bash
docker build -t shortner-bypass .
docker run -d -p 5000:5000 --env-file .env --name shortner-bypass-app shortner-bypass
```

---

## ☁️ Cloud Deployments

### Render
1. Connect your GitHub repository to Render.
2. Render will automatically detect `render.yaml`.
3. Fill in the required environment variables (`BOT_TOKEN`, `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_SESSION`, `PUBLIC_URL`).
4. Deploy the Web Service.

### Railway
1. Click **New Project** > **Deploy from GitHub repo**.
2. Railway detects `railway.yaml` and `Dockerfile`.
3. In **Variables**, add all keys from `.env`.
4. Generate a public domain under **Networking** and set `PUBLIC_URL`.

### Koyeb / VPS
1. Set up a Python 3.10+ environment or deploy the Docker image.
2. Export all environment variables.
3. Use a process manager like `systemd` or `supervisord` to run `python bot.py`.

---

## 📡 Uptime Monitoring (UptimeRobot)

To prevent cold starts on free tiers (Render, Koyeb):
1. Create a free account at [UptimeRobot](https://uptimerobot.com/).
2. Add a new monitor with type **HTTP(s)**.
3. Set the URL to `https://your-domain.com/health`.
4. Set monitoring interval to every **5 minutes**.

---

## 🔒 Security Best Practices

- Never commit real credentials to GitHub or public repositories.
- Keep `TELEGRAM_SESSION` strictly confidential; it grants access to your Telegram userbot account.
- User input is escaped via HTML sanitizers before sending into Telegram messages.
- The system enforces `RATE_LIMIT_SECONDS` and `MAX_CONCURRENT_PER_USER` to prevent account bans.

---

## 📜 Credits & Support

Maintained and developed by **[@ProviderBotz](https://t.me/ProviderBotz)**.  
Join [@ProviderBotz](https://t.me/ProviderBotz) on Telegram for updates, bug reports, and new releases.
