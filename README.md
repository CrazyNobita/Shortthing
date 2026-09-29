<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![Telegram][telegram-shield]][telegram-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/LazyProvider/ShortnerBypass">
    <img src="https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/bolt.svg" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">ShortnerBypass</h3>

  <p align="center">
    High-Performance Telegram Auto Link Bypass Bot & Obsidian Red Mini App
    <br />
    <a href="https://t.me/ProviderBotz"><strong>Explore the Bot »</strong></a>
    <br />
    <br />
    <a href="https://t.me/ProviderBotz">View Live Demo</a>
    &middot;
    <a href="https://github.com/LazyProvider/ShortnerBypass/issues">Report Bug</a>
    &middot;
    <a href="https://github.com/LazyProvider/ShortnerBypass/issues">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#key-features">Key Features</a></li>
        <li><a href="#architecture-flow">Architecture Flow</a></li>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#environment-variables">Environment Variables</a></li>
        <li><a href="#generating-telethon-string-session">Generating Telethon String Session</a></li>
      </ul>
    </li>
    <li>
      <a href="#usage">Usage</a>
      <ul>
        <li><a href="#telegram-bot-commands">Telegram Bot Commands</a></li>
        <li><a href="#rest-api-endpoints">REST API Endpoints</a></li>
        <li><a href="#deployment">Deployment (Docker, Render, Railway)</a></li>
      </ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

**ShortnerBypass** is a production-grade Telegram Auto Link Bypass system built on high-performance asynchronous Python and Telethon. It bridges public Telegram users, an HTTP REST API, and a mobile-first Obsidian Red Telegram Mini App directly with underlying bypass providers:

1. **DZHQ Bypass Engine (`@DZHQ_BypassBot`)** — High-speed Telegram group bypass flow (`-1003644908415`).
2. **Alex Bypass Engine (`@alexbypassbot`)** — Telegram private DM userbot flow.

All legacy Nick bypass integrations and Alex HTTP API dependencies have been **completely eliminated**. The system strictly relies on Telegram-native message and edited-message detection with zero external databases required.

### Key Features

* **⚡ Native Bot API 9.4+ Button Styling:** Real colored background buttons (`PRIMARY` dark blue, `SUCCESS` emerald green, `DANGER` crimson red) rendered seamlessly across modern Telegram clients.
* **🛡 Resilient Reply-Quoting & Blockquotes:** All messages are formatted in elegant Telegram blockquotes (`<blockquote>...</blockquote>`) from start to end with built-in zero-error fallbacks (`allow_sending_without_reply: true`).
* **🔄 Live Progress Animation:** Dynamic 5-stage progress indicator (`10% -> 35% -> 60% -> 80% -> 95%`) with animated status bar and haptic feedback.
* **📱 Obsidian Red Telegram Mini App:** Responsive glassmorphism dashboard (`index.html`) with 1-tap clipboard copying, instant auto-copy popup (`/?copy=url`), and WebApp haptics.
* **🌐 Dynamic Auto-Tunneling:** Automatic detection and provisioning of Cloudflare Quick Tunnels for instant, zero-config HTTPS public URLs.
* **🛑 Anti-Junk & Clean URL Engine:** Strips unwanted promo handles and spam links while safely preserving legitimate destination URLs.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Architecture Flow

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

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* [![Python][Python.org]][Python-url]
* [![Telethon][Telethon-badge]][Telethon-url]
* [![Flask][Flask.palletsprojects.com]][Flask-url]
* [![Telegram][Telegram-badge]][Telegram-url]
* [![Docker][Docker-badge]][Docker-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

Follow these steps to set up and run the ShortnerBypass project locally or on your server.

### Prerequisites

* Python 3.10 or higher
* Git installed on your system
* Telegram API ID & Hash from [my.telegram.org](https://my.telegram.org)
* Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/LazyProvider/ShortnerBypass.git
   cd ShortnerBypass
   ```
2. Create and activate a Python virtual environment:
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   # On Windows: .venv\Scripts\activate
   ```
3. Install required Python packages:
   ```sh
   pip install -r requirements.txt
   ```
4. Create and configure your environment file:
   ```sh
   cp .env.example .env
   ```
5. Run the application:
   ```sh
   python bot.py
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Environment Variables

Configure these settings inside your `.env` file or hosting provider's dashboard:

| Variable | Required | Default | Description |
|:---|:---:|:---:|:---|
| `BOT_TOKEN` | **Yes** | — | Telegram Bot token from [@BotFather](https://t.me/BotFather) |
| `BOT_USERNAME` | **Yes** | — | Bot username without `@` (e.g. `ShortnerBypassBot`) |
| `OWNER_ID` | Optional | — | Numeric Telegram ID of the admin for broadcasts and audits |
| `TELEGRAM_API_ID` | **Yes** | — | Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `TELEGRAM_API_HASH` | **Yes** | — | Telegram API Hash from [my.telegram.org](https://my.telegram.org) |
| `TELEGRAM_SESSION` | **Yes** | — | Telethon StringSession for the userbot account |
| `FSUB_CHANNEL` | No | `@ProviderBotz` | Force subscription channel handle (e.g. `@ProviderBotz`) |
| `DZHQ_BOT_USERNAME` | No | `@DZHQ_BypassBot` | Telegram handle for DZHQ Bot |
| `ALEX_BOT_USERNAME` | No | `@alexbypassbot` | Telegram handle for Alex DM Bot |
| `PUBLIC_URL` | No | Auto | Publicly accessible domain for Telegram Mini App |
| `PORT` | No | `5000` | Port for the local Flask web server |
| `RATE_LIMIT_SECONDS` | No | `3` | Cooldown period between bypass requests per user |
| `MAX_CONCURRENT_PER_USER` | No | `2` | Maximum concurrent tasks permitted per user |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Generating Telethon String Session

To generate a session string for `TELEGRAM_SESSION`:

1. Install Telethon locally:
   ```sh
   pip install telethon
   ```
2. Run this python snippet:
   ```python
   from telethon.sync import TelegramClient
   from telethon.sessions import StringSession

   api_id = int(input("Enter API ID: "))
   api_hash = input("Enter API Hash: ")

   with TelegramClient(StringSession(), api_id, api_hash) as client:
       print("\nYour TELEGRAM_SESSION string:\n")
       print(client.session.save())
   ```
3. Copy the output string and paste it into your `.env` as `TELEGRAM_SESSION`.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

### Telegram Bot Commands

* `/start` — Welcome message, launch button for Obsidian Red Mini App, and channel links.
* `/help` — Step-by-step user guide and bypass instructions.
* `/about` — Bot engine details, developer attribution, and version info.
* `/bypass <link>` — Direct bypass command (or simply paste any shortlink into the chat).
* `/stats` — *(Owner Only)* Live statistics on users, bypass counts, and engine status.
* `/broadcast <message>` — *(Owner Only)* High-speed broadcast message to all bot users.

### REST API Endpoints

#### 1. Web Mini App Dashboard
* **Endpoint:** `GET /`
* **Description:** Serves the Obsidian Red glassmorphism Telegram Mini App interface.

#### 2. Health Check
* **Endpoint:** `GET /health`
* **Response:**
  ```json
  {
    "developer": "@ProviderBotz",
    "public_bot_online": true,
    "service": "ShortnerBypass",
    "status": "ok",
    "userbot_online": true
  }
  ```

#### 3. Instant Link Bypass
* **Endpoint:** `GET /bypass?url=https://target-shortlink.com/xyz`
* **Response:**
  ```json
  {
    "developer": "@ProviderBotz",
    "links": {
      "bypassed": "https://final-destination.com/target-file",
      "original": "https://target-shortlink.com/xyz"
    },
    "response_ms": "1420ms",
    "source": "dzhq",
    "status": true,
    "url": "https://final-destination.com/target-file"
  }
  ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Deployment

#### Docker

Build and run using Docker:
```sh
docker build -t shortner-bypass .
docker run -d -p 5000:5000 --env-file .env --name shortner-bypass-app shortner-bypass
```

#### Render / Railway / VPS
* **Render:** Connect repository to Render. It auto-detects `render.yaml`. Set environment variables in the dashboard.
* **Railway:** Select **Deploy from GitHub repo**. Railway automatically reads `railway.yaml` and `Dockerfile`.
* **VPS (Systemd):** Run `python bot.py` via systemd or supervisor to ensure auto-restart on system reboots.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->
## Roadmap

- [x] Dual-engine bypass integration (DZHQ + Alex DM)
- [x] Native Telegram Bot API 9.4+ colored button styles
- [x] Obsidian Red responsive glassmorphism Telegram Mini App
- [x] Automatic Cloudflare tunnel generation for Mini App
- [x] Full Telegram blockquote (`<blockquote>`) message formatting
- [x] Resilient custom reply quoting with zero-error fallback
- [ ] Multi-account userbot rotation pool
- [ ] Webhook support for ultra-low latency Telegram event delivery

See the [open issues](https://github.com/LazyProvider/ShortnerBypass/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

**Developer:** [@LazyProvider](https://t.me/LazyProvider)  
**Official Channel:** [@ProviderBotz](https://t.me/ProviderBotz)  
**Project Link:** [https://github.com/LazyProvider/ShortnerBypass](https://github.com/LazyProvider/ShortnerBypass)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Telethon — Pure Python Telegram Client Library](https://github.com/LonamiWebs/Telethon)
* [Flask — The Python Micro Framework](https://palletsprojects.com/p/flask/)
* [Telegram Bot API](https://core.telegram.org/bots/api)
* [Cloudflare Quick Tunnels](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)
* [Othneil Drew's Best-README-Template](https://github.com/othneildrew/Best-README-Template)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/LazyProvider/ShortnerBypass.svg?style=for-the-badge
[contributors-url]: https://github.com/LazyProvider/ShortnerBypass/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/LazyProvider/ShortnerBypass.svg?style=for-the-badge
[forks-url]: https://github.com/LazyProvider/ShortnerBypass/network/members
[stars-shield]: https://img.shields.io/github/stars/LazyProvider/ShortnerBypass.svg?style=for-the-badge
[stars-url]: https://github.com/LazyProvider/ShortnerBypass/stargazers
[issues-shield]: https://img.shields.io/github/issues/LazyProvider/ShortnerBypass.svg?style=for-the-badge
[issues-url]: https://github.com/LazyProvider/ShortnerBypass/issues
[license-shield]: https://img.shields.io/github/license/LazyProvider/ShortnerBypass.svg?style=for-the-badge
[license-url]: https://github.com/LazyProvider/ShortnerBypass/blob/main/LICENSE
[telegram-shield]: https://img.shields.io/badge/Telegram-Channel-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white
[telegram-url]: https://t.me/ProviderBotz
[Python.org]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[Telethon-badge]: https://img.shields.io/badge/Telethon-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white
[Telethon-url]: https://github.com/LonamiWebs/Telethon
[Flask.palletsprojects.com]: https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white
[Flask-url]: https://flask.palletsprojects.com/
[Telegram-badge]: https://img.shields.io/badge/Telegram_Bot_API-9.4+-blue?style=for-the-badge&logo=telegram&logoColor=white
[Telegram-url]: https://core.telegram.org/bots/api
[Docker-badge]: https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/
