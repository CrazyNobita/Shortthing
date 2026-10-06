#!/usr/bin/env python3
from __future__ import annotations
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ShortnerBypass — Production-Ready Auto Link Bypass Bot
  Unified Telethon Userbot Dual Engine + Telegram Bot API + Flask WebApp
  Powered by ProviderBotz
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import os
import sys
import re
import json
import time
import html
import secrets
import asyncio
import logging
import threading
from urllib.parse import urlparse, parse_qs, unquote
from typing import Optional, Dict, List, Any, Union, Tuple

# Third-party dependencies with zero-crash fallbacks
def load_dotenv_safe(env_filename: str = ".env"):
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), env_filename)
    if not os.path.exists(p):
        return
    try:
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k and k not in os.environ:
                    os.environ[k] = v
    except Exception:
        pass

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    load_dotenv_safe()

try:
    import requests
except ImportError:
    requests = None

try:
    import aiohttp
except ImportError:
    aiohttp = None

try:
    from telethon import TelegramClient, events
    from telethon.sessions import StringSession
    from telethon.tl.types import MessageEntityUrl, MessageEntityTextUrl
    from telethon.errors import (
        AuthKeyDuplicatedError,
        SessionRevokedError,
        SessionPasswordNeededError,
        SecurityError,
    )
    HAS_TELETHON = True
except ImportError:
    HAS_TELETHON = False
    TelegramClient = None
    events = None
    StringSession = None
    MessageEntityUrl = None
    MessageEntityTextUrl = None
    class AuthKeyDuplicatedError(Exception): pass
    class SessionRevokedError(Exception): pass
    class SessionPasswordNeededError(Exception): pass
    class SecurityError(Exception): pass

try:
    from flask import Flask, request, jsonify, send_file
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False
    Flask = None
    request = None
    jsonify = None
    send_file = None

# ══════════════════════════════════════════════════════════════
#  LOGGING CONFIGURATION
# ══════════════════════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("ShortnerBypass")

# ══════════════════════════════════════════════════════════════
#  PERSISTENCE STORAGE & HELPERS
# ══════════════════════════════════════════════════════════════
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def read_file_safe(filename: str, default: str = "") -> str:
    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass
    return default

def write_file_safe(filename: str, content: str):
    try:
        with open(os.path.join(BASE_DIR, filename), "w", encoding="utf-8") as f:
            f.write(content.strip())
    except Exception as e:
        logger.warning(f"Could not write {filename}: {e}")

# ══════════════════════════════════════════════════════════════
#  CONFIG & CREDENTIALS
# ══════════════════════════════════════════════════════════════
VERSION = "4.0.3"
BOT_TOKEN = (
    read_file_safe("token.txt")
    or os.environ.get("BOT_TOKEN", "8678804822:AAGTnMN8kCBoeIwhDhF3b4fASkO9cTzL0Lo").strip()
)
BOT_USERNAME = os.environ.get("BOT_USERNAME", "TheLinkzoBot").strip().lstrip("@")
OWNER_ID = int(os.environ.get("OWNER_ID", "7931847651").strip()) if os.environ.get("OWNER_ID", "7931847651").strip().isdigit() else None
DEVELOPER = os.environ.get("DEVELOPER", "@ProviderBotz").strip()
FSUB_CHANNEL = os.environ.get("FSUB_CHANNEL", "@ProviderBotz").strip()
START_IMAGE_URL = os.environ.get("START_IMAGE_URL", "https://i.ibb.co/2Yv768HY/uploaded-image.jpg").strip()

# Userbot credentials
raw_api_id = (os.environ.get("TELEGRAM_API_ID") or "36805393").strip()
TELEGRAM_API_ID = int(raw_api_id) if raw_api_id.isdigit() else 36805393
TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH", "cfd5ff24d915c1691d88b0f3b51b96f5").strip()
TELEGRAM_SESSION = (
    read_file_safe("session.txt")
    or os.environ.get("TELEGRAM_SESSION", "").strip()
)

# External Engines (Core Group Flow & Fast Private DM Flow)
ENGINE_CORE_BOT = (
    os.environ.get("ENGINE_CORE_BOT")
    or os.environ.get("DZHQ_BOT_USERNAME")
    or "@DZHQ_BypassBot"
).strip()
raw_group = os.environ.get("ENGINE_CORE_GROUP") or os.environ.get("DZHQ_GROUP", "-1003644908415")
try:
    ENGINE_CORE_GROUP: Optional[Union[int, str]] = int(raw_group.strip())
except Exception:
    ENGINE_CORE_GROUP = raw_group.strip() if raw_group else None

ENGINE_FAST_BOT = (
    os.environ.get("ENGINE_FAST_BOT")
    or os.environ.get("ALEX_BOT_USERNAME")
    or "@alexbypassbot"
).strip()

MINI_APP_URL = (
    read_file_safe("miniapp.txt")
    or os.environ.get("MINI_APP_URL", "").strip()
    or os.environ.get("PUBLIC_URL", "").strip()
)

FLASK_PORT = int(os.environ.get("FLASK_PORT", os.environ.get("PORT", "5000")))
if FLASK_PORT in (8080, 3000):
    FLASK_PORT = 5000
PORT = FLASK_PORT

MAX_BYPASS_TIMEOUT_SEC = int(os.environ.get("MAX_BYPASS_TIMEOUT_SEC", "120"))

# Small-caps typography dictionary for Telegram messages
SMALL_CAPS = {
    'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ', 'g': 'ɢ',
    'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ',
    'o': 'ᴏ', 'p': 'ᴩ', 'q': 'ǫ', 'r': 'ʀ', 's': 'ꜱ', 't': 'ᴛ', 'u': 'ᴜ',
    'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ'
}

def to_small_caps(text: str) -> str:
    return "".join(SMALL_CAPS.get(c.lower(), c) if c.isalpha() else c for c in text)

# Registered users persistence
_REGISTERED_USERS: set = set()
def load_registered_users():
    global _REGISTERED_USERS
    raw = read_file_safe("users.txt")
    if raw:
        for line in raw.splitlines():
            line = line.strip()
            if line.isdigit():
                _REGISTERED_USERS.add(int(line))

def register_user(user_id: int):
    if user_id and user_id not in _REGISTERED_USERS:
        _REGISTERED_USERS.add(user_id)
        try:
            with open(os.path.join(BASE_DIR, "users.txt"), "a", encoding="utf-8") as f:
                f.write(f"{user_id}\n")
        except Exception:
            pass

load_registered_users()

# ══════════════════════════════════════════════════════════════
#  URL VALIDATION & ENGINE NAME SANITIZATION
# ══════════════════════════════════════════════════════════════
PROMO_DOMAINS = {
    "t.me", "telegram.me", "telegram.dog", "youtube.com", "youtu.be",
    "facebook.com", "instagram.com", "twitter.com", "x.com", "tiktok.com"
}

def clean_url(url: Optional[str]) -> str:
    if not url:
        return ""
    u = url.strip().strip("<>\"'`()[]{}.,;")
    if u.endswith("/"):
        u = u[:-1]
    return u

def is_valid_destination(dest: str, original: str) -> bool:
    if not dest or not dest.startswith(("http://", "https://")):
        return False
    c_dest = clean_url(dest).lower()
    c_orig = clean_url(original).lower()
    if c_dest == c_orig:
        return False
    parsed = urlparse(dest)
    domain = (parsed.netloc or "").lower().split(":")[0]
    if any(domain == p or domain.endswith("." + p) for p in PROMO_DOMAINS):
        return False
    return len(dest) > 10

def sanitize_engine_names(text: Optional[str]) -> str:
    """Ensures external engine names are NEVER leaked to users."""
    if not text:
        return "ProviderBotz Engine could not resolve this link."
    patterns = [
        (r'@?alexbypassbot', "ProviderBotz Engine"),
        (r'@?dzhq_bypassbot', "ProviderBotz Engine"),
        (r'@?dzhqbot', "ProviderBotz Engine"),
        (r'@?BypassAlexBot', "ProviderBotz Engine"),
        (r'@?alex_bypass_bot', "ProviderBotz Engine"),
        (r'@?DZHQBypassBot', "ProviderBotz Engine"),
        (r'@?DZHQBypass', "ProviderBotz Engine"),
        (r'\balexbypass\b', "ProviderBotz Engine"),
        (r'\balexmodz\b', "ProviderBotz Engine"),
        (r'\bdzhqbypass\b', "ProviderBotz Engine"),
        (r'\bdzhq\b', "ProviderBotz Engine"),
        (r'\balex\b', "ProviderBotz Engine"),
        (r'\bAlex Bypass Bot\b', "ProviderBotz Engine"),
        (r'\bAlex Bot\b', "ProviderBotz Engine"),
        (r'\bDZHQ bot\b', "ProviderBotz Engine"),
        (r'\bDZHQ Group\b', "ProviderBotz Direct Engine"),
        (r'\bDZHQ\b', "ProviderBotz Engine"),
        (r'Telethon Userbot', "ProviderBotz Engine"),
    ]
    res = str(text)
    for pat, repl in patterns:
        res = re.sub(pat, repl, res, flags=re.IGNORECASE)
    return res

# ══════════════════════════════════════════════════════════════
#  FAST DIRECT RESOLVER (INSTANT REDIRECT / UNSHORTENER)
# ══════════════════════════════════════════════════════════════
def sync_direct_bypass(target_url: str) -> Optional[str]:
    import urllib.request
    import urllib.error
    import urllib.parse
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    opener = urllib.request.build_opener(NoRedirect)
    curr = target_url
    for _ in range(6):
        try:
            req = urllib.request.Request(curr, headers=headers, method="HEAD")
            with opener.open(req, timeout=5) as resp:
                pass
        except urllib.error.HTTPError as e:
            if e.code in (301, 302, 303, 307, 308) and "Location" in e.headers:
                loc = e.headers["Location"]
                if not loc.startswith("http"):
                    loc = urllib.parse.urljoin(curr, loc)
                curr = loc
            else:
                break
        except Exception:
            break
    if curr != target_url and is_valid_destination(curr, target_url):
        return curr
    return None

async def fast_direct_bypass(target_url: str) -> Optional[str]:
    """Recursively traces HTTP redirects and extracts unshortened destination."""
    # 1. Query parameter search
    try:
        parsed = urlparse(target_url)
        qs = parse_qs(parsed.query)
        for key in ("dest", "url", "target", "link", "destination", "r", "goto", "u"):
            if key in qs and qs[key]:
                candidate = unquote(qs[key][0])
                if is_valid_destination(candidate, target_url):
                    return candidate
    except Exception:
        pass

    # 2. HTTP Redirection follow with aiohttp if available
    if aiohttp:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        try:
            timeout = aiohttp.ClientTimeout(total=8)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                curr = target_url
                for _ in range(6):
                    async with session.head(curr, headers=headers, allow_redirects=False) as resp:
                        if resp.status in (301, 302, 303, 307, 308) and "Location" in resp.headers:
                            loc = resp.headers["Location"]
                            if not loc.startswith("http"):
                                loc = requests.compat.urljoin(curr, loc) if requests else loc
                            curr = loc
                        else:
                            break
                if curr != target_url and is_valid_destination(curr, target_url):
                    return curr
        except Exception:
            pass

    # Fallback to standard library redirect tracer
    try:
        return await asyncio.to_thread(sync_direct_bypass, target_url)
    except Exception:
        return None

# ══════════════════════════════════════════════════════════════
#  TELETHON USERBOT CORE (DUAL ENGINE DISPATCHER)
# ══════════════════════════════════════════════════════════════
class BypassJob:
    def __init__(self, job_id: str, url: str, user_id: Optional[int] = None, first_name: Optional[str] = None, username: Optional[str] = None):
        self.id = job_id
        self.url = url
        self.user_id = user_id
        self.first_name = first_name or "Friend"
        self.username = username
        self.event = asyncio.Event()
        self.final_url: Optional[str] = None
        self.error: Optional[str] = None
        self.state: str = "PENDING"
        self.start_time = time.time()
        self.core_msg_id: Optional[int] = None
        self.fast_msg_id: Optional[int] = None
        self.core_failed = False
        self.fast_failed = False

class UserbotEngine:
    def __init__(self):
        self.client: Optional[TelegramClient] = None
        self.connected = False
        self.active_jobs: Dict[str, BypassJob] = {}
        self.jobs_lock = threading.Lock()
        self.core_entity: Any = None
        self.fast_entity: Any = None
        self.core_bot_id: Optional[int] = None
        self.fast_bot_id: Optional[int] = None
        self.total_bypasses = 0
        self.successful_bypasses = 0
        self.failed_bypasses = 0
        self.start_time = time.time()

    def create_job(self, url: str, user_id: Optional[int] = None, first_name: Optional[str] = None, username: Optional[str] = None) -> BypassJob:
        job_id = secrets.token_hex(6)
        job = BypassJob(job_id, url, user_id, first_name, username)
        with self.jobs_lock:
            self.active_jobs[job_id] = job
        return job

    def cleanup_job(self, job_id: str):
        with self.jobs_lock:
            self.active_jobs.pop(job_id, None)

engine = UserbotEngine()
GLOBAL_ASYNC_LOOP: Optional[asyncio.AbstractEventLoop] = None

# Response parser for external engine replies
_RX_RESULT = re.compile(r'(?:Got\s*Result|Bypassed\s*Link|Result)[^:\n]*:?-?\s*[`*]*\s*(https?://[^\s*`\n]+)', re.I)
_RX_FAIL = re.compile(r'invalid|unsupported|not\s*found|error|failed|cannot|wrong', re.I)
_RX_RATE = re.compile(r'rate\s*limit|flood|try\s*again', re.I)

def parse_engine_message(text: str, entities: list, original_url: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    # 1. Check rate limit
    if _RX_RATE.search(text):
        return {"status": "rate_limit", "error": "Bypass engine rate limited"}
    # 2. Check failure
    if _RX_FAIL.search(text) and not _RX_RESULT.search(text):
        return {"status": "failed", "error": "Bypass engine could not resolve link"}
    # 3. Check explicit result regex
    m = _RX_RESULT.search(text)
    if m:
        dest = clean_url(m.group(1))
        if is_valid_destination(dest, original_url):
            return {"status": "ok", "url": dest}
    # 4. Check Telegram entity text URLs
    if entities:
        for ent in entities:
            url_val = getattr(ent, 'url', None)
            if not url_val and isinstance(ent, MessageEntityUrl):
                off = getattr(ent, 'offset', 0)
                lng = getattr(ent, 'length', 0)
                url_val = text[off:off + lng]
            if url_val:
                dest = clean_url(url_val)
                if is_valid_destination(dest, original_url):
                    return {"status": "ok", "url": dest}
    # 5. Fallback URL extraction
    urls = re.findall(r'https?://[^\s\n\)\]>"\']+', text)
    for u in urls:
        dest = clean_url(u)
        if is_valid_destination(dest, original_url):
            return {"status": "ok", "url": dest}
    return None

def setup_userbot_handlers(client: TelegramClient):
    @client.on(events.NewMessage())
    @client.on(events.MessageEdited())
    async def on_userbot_message(event):
        text = event.raw_text or ""
        msg = event.message
        sender_id = event.sender_id
        reply_to_id = getattr(msg, 'reply_to_msg_id', None)

        # Match with an active job
        matched_job: Optional[BypassJob] = None
        with engine.jobs_lock:
            for job in engine.active_jobs.values():
                if job.state != "PENDING":
                    continue
                if reply_to_id and (reply_to_id in (job.core_msg_id, job.fast_msg_id)):
                    matched_job = job
                    break
                if job.url in text:
                    matched_job = job
                    break

        if not matched_job:
            return

        parsed = parse_engine_message(text, msg.entities or [], matched_job.url)
        if not parsed:
            return

        if parsed.get("status") == "ok" and parsed.get("url"):
            matched_job.final_url = parsed["url"]
            matched_job.state = "SUCCESS"
            matched_job.event.set()
            # Auto-click Delete button if present in group
            if getattr(msg, 'buttons', None):
                try:
                    for row in msg.buttons:
                        for btn in row:
                            if any(k in btn.text.lower() for k in ("del", "delete", "close", "❌")):
                                await btn.click()
                                break
                except Exception:
                    pass
        elif parsed.get("status") in ("failed", "rate_limit"):
            if sender_id == engine.fast_bot_id:
                matched_job.fast_failed = True
            else:
                matched_job.core_failed = True
            if matched_job.fast_failed and matched_job.core_failed:
                matched_job.error = sanitize_engine_names(parsed.get("error"))
                matched_job.state = "FAILED"
                matched_job.event.set()

async def send_owner_log(job: BypassJob, final_url: str, duration_str: str):
    """Sends bypassed link notification to Owner with direct DM and bot buttons."""
    if not OWNER_ID or not globals().get("bot_api"):
        return
    try:
        user_id = job.user_id
        first_name = html.escape(job.first_name or "User")
        username = job.username

        if user_id:
            user_mention = f'<a href="tg://user?id={user_id}">{first_name}</a>'
            dm_url = f"https://t.me/{username}" if username else f"tg://user?id={user_id}"
        else:
            user_mention = f"<code>{first_name}</code> (Web Client)"
            dm_url = None

        log_text = (
            f"⚡ <b>New Link Bypassed! (v{VERSION})</b>\n\n"
            f"• 👤 <b>User:</b> {user_mention}" + (f" [<code>{user_id}</code>]" if user_id else "") + "\n"
            f"• ⏱ <b>Time Taken:</b> <code>{duration_str}</code>\n"
            f"• 🛡 <b>Engine:</b> <code>Dual-Core Bypass Engine (v{VERSION})</code>\n\n"
            f"🔗 <b>Original Link:</b>\n{html.escape(job.url)}\n\n"
            f"🎯 <b>Bypassed Destination:</b>\n{html.escape(final_url)}"
        )

        buttons: List[List[Dict[str, Any]]] = []
        row1: List[Dict[str, Any]] = []
        if dm_url:
            row1.append({"text": "👤 User Direct DM", "url": dm_url, "style": "primary"})
        row1.append({"text": "🤖 Bot", "url": f"https://t.me/{BOT_USERNAME}", "style": "secondary"})
        buttons.append(row1)

        row2: List[Dict[str, Any]] = [
            {"text": "🔑 String Session", "url": "https://t.me/StringFatherBot", "style": "secondary"},
            {"text": "🔗 Bypassed Link", "url": final_url, "style": "success"}
        ]
        buttons.append(row2)

        markup = {"inline_keyboard": buttons}
        await bot_api.send_message(OWNER_ID, log_text, reply_markup=markup)
    except Exception as e:
        logger.warning(f"Could not send log to owner: {e}")

async def execute_bypass_job(job_id: str) -> Dict[str, Any]:
    with engine.jobs_lock:
        job = engine.active_jobs.get(job_id)
    if not job:
        return {"status": False, "message": "Job not found"}

    t0 = time.time()
    target_url = job.url

    # Fast direct resolver first
    direct_res = await fast_direct_bypass(target_url)
    if direct_res and is_valid_destination(direct_res, target_url):
        duration_ms = int((time.time() - t0) * 1000)
        engine.total_bypasses += 1
        engine.successful_bypasses += 1
        job.state = "SUCCESS"
        job.final_url = direct_res
        asyncio.create_task(send_owner_log(job, direct_res, f"{duration_ms}ms"))
        return {
            "status": True,
            "url": direct_res,
            "response_ms": f"{duration_ms}ms",
            "source": "providerbotz_core"
        }

    # If userbot is not connected, return error
    if not engine.client or not engine.connected:
        return {
            "status": False,
            "message": "Bypass Engine is currently offline. Please configure TELEGRAM_SESSION.",
            "response_ms": "0ms"
        }

    # Send to engines concurrently
    async def _send_fast():
        try:
            target = engine.fast_entity or engine.fast_bot_id or ENGINE_FAST_BOT
            sent = await engine.client.send_message(target, target_url)
            job.fast_msg_id = sent.id
        except AuthKeyDuplicatedError:
            logger.error("❌ Telethon AuthKeyDuplicatedError in DM engine: session revoked (multiple active IPs).")
            engine.connected = False
            job.fast_failed = True
        except Exception:
            job.fast_failed = True

    async def _send_core():
        try:
            target = engine.core_entity or (ENGINE_CORE_GROUP if ENGINE_CORE_GROUP else ENGINE_CORE_BOT)
            cmd = f"/b {target_url}" if ENGINE_CORE_GROUP else target_url
            sent = await engine.client.send_message(target, cmd)
            job.core_msg_id = sent.id
        except AuthKeyDuplicatedError:
            logger.error("❌ Telethon AuthKeyDuplicatedError in Core Group engine: session revoked (multiple active IPs).")
            engine.connected = False
            job.core_failed = True
        except Exception:
            job.core_failed = True

    await asyncio.gather(_send_fast(), _send_core(), return_exceptions=True)

    # Wait for result
    try:
        await asyncio.wait_for(job.event.wait(), timeout=MAX_BYPASS_TIMEOUT_SEC)
    except asyncio.TimeoutError:
        pass

    duration_ms = int((time.time() - t0) * 1000)
    if job.state == "SUCCESS" and job.final_url:
        engine.total_bypasses += 1
        engine.successful_bypasses += 1
        asyncio.create_task(send_owner_log(job, job.final_url, f"{duration_ms}ms"))
        return {
            "status": True,
            "url": job.final_url,
            "response_ms": f"{duration_ms}ms",
            "source": "providerbotz_core"
        }

    engine.total_bypasses += 1
    engine.failed_bypasses += 1
    return {
        "status": False,
        "message": sanitize_engine_names(job.error or "The link could not be bypassed or expired."),
        "response_ms": f"{duration_ms}ms"
    }

async def watch_userbot_disconnect(client: Any):
    try:
        await client.disconnected
    except AuthKeyDuplicatedError:
        logger.error("❌ Telethon AuthKeyDuplicatedError: session revoked by Telegram (active under multiple IPs). Halting reconnect.")
        engine.connected = False
        try:
            await client.disconnect()
        except Exception:
            pass
        if OWNER_ID and globals().get("bot_api"):
            try:
                await bot_api.send_message(
                    OWNER_ID,
                    f"⚠️ <b>Userbot Session Alert (v{VERSION})</b>\n\n"
                    f"Telegram revoked this authorization key because it was detected under two different IP addresses simultaneously (<code>AuthKeyDuplicatedError</code>).\n\n"
                    f"👉 <i>Please generate a fresh session below and tap Paste StringSession to reconnect:</i>",
                    reply_markup={
                        "inline_keyboard": [
                            [{"text": "🔑 Generate StringSession", "url": "https://t.me/StringFatherBot", "style": "primary"}],
                            [{"text": "📋 Paste StringSession", "callback_data": "cmd_paste_session", "style": "success"}]
                        ]
                    }
                )
            except Exception:
                pass
    except Exception as e:
        logger.warning(f"Userbot disconnected: {e}")
        engine.connected = False

async def restart_userbot(new_session: str) -> Tuple[bool, str]:
    global TELEGRAM_SESSION
    if not HAS_TELETHON or not TelegramClient or not StringSession:
        return False, "Telethon is not installed (run 'pip install -r requirements.txt')."
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        return False, "TELEGRAM_API_ID and TELEGRAM_API_HASH are not configured in .env"
    clean_session = new_session.strip()
    if not clean_session:
        return False, "Session string is empty."

    # Disconnect previous client safely
    if engine.client:
        try:
            await engine.client.disconnect()
        except Exception:
            pass
        engine.client = None
        engine.connected = False

    try:
        new_client = TelegramClient(
            StringSession(clean_session),
            TELEGRAM_API_ID,
            TELEGRAM_API_HASH,
            auto_reconnect=False,
            connection_retries=2,
            retry_delay=3,
            device_model="ProviderBotz Engine",
            system_version="Linux 4.0",
            app_version=f"ShortnerBypass v{VERSION}"
        )
        await new_client.connect()
        if not await new_client.is_user_authorized():
            await new_client.disconnect()
            return False, "Session string is invalid or unauthorized."

        me = await new_client.get_me()
        engine.client = new_client
        engine.connected = True
        TELEGRAM_SESSION = clean_session
        write_file_safe("session.txt", clean_session)
        setup_userbot_handlers(engine.client)

        # Resolve external engines entities
        try:
            engine.fast_entity = await new_client.get_entity(ENGINE_FAST_BOT)
            engine.fast_bot_id = engine.fast_entity.id
        except Exception as e:
            logger.warning(f"Could not resolve fast engine {ENGINE_FAST_BOT}: {e}")
        if ENGINE_CORE_GROUP:
            try:
                engine.core_entity = await new_client.get_entity(ENGINE_CORE_GROUP)
            except Exception as e:
                logger.warning(f"Could not resolve core group {ENGINE_CORE_GROUP}: {e}")

        account_name = f"{me.first_name} (@{me.username or me.id})"
        logger.info(f"✅ Userbot connected: {account_name}")
        asyncio.create_task(watch_userbot_disconnect(new_client))
        return True, account_name
    except AuthKeyDuplicatedError:
        err_msg = (
            "AuthKeyDuplicatedError: Session was active on two different IP addresses simultaneously "
            "and was terminated by Telegram. Please generate a fresh StringSession via @StringFatherBot or /gensession."
        )
        logger.error(f"❌ {err_msg}")
        engine.connected = False
        engine.client = None
        return False, err_msg
    except (SessionRevokedError, SecurityError) as e:
        err_msg = f"Session revoked by Telegram ({type(e).__name__}). Please generate a fresh StringSession."
        logger.error(f"❌ {err_msg}")
        engine.connected = False
        engine.client = None
        return False, err_msg
    except SessionPasswordNeededError:
        err_msg = "Two-Step Verification password required for this Telegram account."
        logger.error(f"❌ {err_msg}")
        engine.connected = False
        engine.client = None
        return False, err_msg
    except Exception as e:
        err_msg = f"Userbot connection error: {e}"
        logger.error(f"❌ {err_msg}")
        engine.connected = False
        engine.client = None
        return False, err_msg

# ══════════════════════════════════════════════════════════════
#  TELEGRAM BOT API WORKER (COLORED BUTTONS & POLLING)
# ══════════════════════════════════════════════════════════════
class TelegramBotAPI:
    def __init__(self, token: str):
        self.token = token.strip()
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.session: Any = None

    async def get_session(self) -> Any:
        if aiohttp and (not self.session or self.session.closed):
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=45))
        return self.session

    async def request(self, method: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{method}"
        payload = data or {}
        if aiohttp:
            s = await self.get_session()
            if s:
                try:
                    async with s.post(url, json=payload) as resp:
                        return await resp.json()
                except Exception as e:
                    return {"ok": False, "description": str(e)}

        def _sync_post():
            import urllib.request
            import urllib.error
            body_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=body_bytes, headers={"Content-Type": "application/json"}, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=35) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                try:
                    return json.loads(e.read().decode("utf-8"))
                except Exception:
                    return {"ok": False, "description": str(e)}
            except Exception as e:
                return {"ok": False, "description": str(e)}

        return await asyncio.to_thread(_sync_post)

    async def send_message(self, chat_id: int, text: str, reply_markup: Optional[Dict] = None, reply_to_message_id: Optional[int] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id
        return await self.request("sendMessage", payload)

    async def send_photo(self, chat_id: int, photo: str, caption: Optional[str] = None, reply_markup: Optional[Dict] = None, reply_to_message_id: Optional[int] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "chat_id": chat_id,
            "photo": photo,
            "parse_mode": "HTML"
        }
        if caption:
            payload["caption"] = caption
        if reply_markup:
            payload["reply_markup"] = reply_markup
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id
        return await self.request("sendPhoto", payload)

    async def edit_message_text(self, chat_id: int, message_id: int, text: str, reply_markup: Optional[Dict] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return await self.request("editMessageText", payload)

    async def delete_message(self, chat_id: int, message_id: int):
        return await self.request("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

    async def answer_callback_query(self, callback_query_id: str, text: Optional[str] = None, show_alert: bool = False):
        payload: Dict[str, Any] = {"callback_query_id": callback_query_id, "show_alert": show_alert}
        if text:
            payload["text"] = text
        return await self.request("answerCallbackQuery", payload)

bot_api = TelegramBotAPI(BOT_TOKEN)

# Button Builders with Bot API 9.4 Colored Styles
def build_start_markup(user_id: Optional[int] = None) -> Dict[str, Any]:
    inline_keyboard: List[List[Dict[str, Any]]] = []
    is_owner = bool(user_id and (not OWNER_ID or user_id == OWNER_ID))
    if is_owner:
        inline_keyboard.append([{"text": "📋 Paste StringSession", "callback_data": "cmd_paste_session", "style": "primary"}])
        inline_keyboard.append([{"text": "🔑 Generate StringSession", "callback_data": "cmd_gen_session", "style": "secondary"}])
        inline_keyboard.append([{"text": "🌐 Set Mini App Link", "callback_data": "cmd_set_miniapp", "style": "secondary"}])
    if MINI_APP_URL:
        if MINI_APP_URL.startswith("https://"):
            inline_keyboard.append([{"text": "🚀 Open Mini App", "web_app": {"url": MINI_APP_URL}, "style": "success"}])
        else:
            inline_keyboard.append([{"text": "🚀 Open Web App", "url": MINI_APP_URL, "style": "success"}])
    inline_keyboard.append([
        {"text": "ℹ️ Help", "callback_data": "cmd_help", "style": "primary"},
        {"text": "📖 About", "callback_data": "cmd_about", "style": "success"}
    ])
    return {"inline_keyboard": inline_keyboard}

async def send_gen_session_menu(chat_id: int, message_id: Optional[int] = None):
    gen_text = (
        f"🔑 <b>{to_small_caps('generate telethon stringsession')} (v{VERSION})</b>\n\n"
        f"<i>Follow any of these 3 easy methods to generate a fresh StringSession:</i>\n\n"
        f"<b>1. Telegram Bot Method (Fastest):</b>\n"
        f"Use @StringFatherBot to generate directly inside Telegram with your phone number.\n\n"
        f"<b>2. Web Browser Method:</b>\n"
        f"Generate securely online without installing Python.\n\n"
        f"<b>3. Terminal / Python One-Liner:</b>\n"
        f"<code>python3 -c \"from telethon.sync import TelegramClient; from telethon.sessions import StringSession; api_id=int(input('API ID: ')); api_hash=input('API Hash: '); client=TelegramClient(StringSession(), api_id, api_hash); client.start(); print('\\nYOUR SESSION:\\n' + client.session.save())\"</code>\n\n"
        f"👉 <i>After generating, tap '📋 Paste StringSession' below to activate!</i>"
    )
    markup = {
        "inline_keyboard": [
            [
                {"text": "🤖 Open @StringFatherBot", "url": "https://t.me/StringFatherBot", "style": "primary"},
                {"text": "🌐 Web Generator", "url": "https://telegram.tools/session-string-generator", "style": "secondary"}
            ],
            [
                {"text": "📋 Paste StringSession", "callback_data": "cmd_paste_session", "style": "success"}
            ],
            [
                {"text": "🏠 Home", "callback_data": "cmd_home", "style": "primary"}
            ]
        ]
    }
    if message_id:
        await bot_api.edit_message_text(chat_id, message_id, gen_text, reply_markup=markup)
    else:
        await bot_api.send_message(chat_id, gen_text, reply_markup=markup)

def build_result_markup(final_url: str, job_url: str) -> Dict[str, Any]:
    return {"inline_keyboard": [
        [{"text": "🔗 Open Link", "url": final_url, "style": "success"}],
        [
            {"text": "🔄 Retry", "callback_data": f"retry:{job_url[:40]}", "style": "primary"},
            {"text": "❌ Close", "callback_data": "cmd_close", "style": "danger"}
        ]
    ]}

OWNER_INPUT_STATE: Dict[int, str] = {}

def schedule_auto_delete(chat_id: int, message_id: int, delay_sec: int = 120):
    async def _del():
        await asyncio.sleep(delay_sec)
        try:
            await bot_api.delete_message(chat_id, message_id)
        except Exception:
            pass
    if GLOBAL_ASYNC_LOOP:
        GLOBAL_ASYNC_LOOP.create_task(_del())

async def process_telegram_link(chat_id: int, user_id: int, target_url: str, reply_msg_id: Optional[int] = None, first_name: Optional[str] = None, username: Optional[str] = None):
    job = engine.create_job(target_url, user_id=user_id, first_name=first_name, username=username)
    initial_text = f"🔄 <b>{to_small_caps('bypassing link...')}</b> [▰▱▱▱▱▱▱▱▱▱] 10%\n🔍 <i>{to_small_caps('fetching link data...')}</i>"
    init_res = await bot_api.send_message(chat_id, initial_text, reply_to_message_id=reply_msg_id)
    status_msg_id = init_res.get("result", {}).get("message_id")

    stop_updater = asyncio.Event()
    async def _progress_ticker():
        frames = [
            f"🔄 <b>{to_small_caps('bypassing link...')}</b> [▰▰▰▱▱▱▱▱▱▱] 35%\n🔓 <i>{to_small_caps('bypassing security & captcha...')}</i>",
            f"🔄 <b>{to_small_caps('bypassing link...')}</b> [▰▰▰▰▰▱▱▱▱▱] 60%\n⚙️ <i>{to_small_caps('decoding shortlink tokens...')}</i>",
            f"🔄 <b>{to_small_caps('bypassing link...')}</b> [▰▰▰▰▰▰▰▰▰▱] 95%\n✨ <i>{to_small_caps('verifying clean destination...')}</i>"
        ]
        idx = 0
        while not stop_updater.is_set():
            await asyncio.sleep(1.2)
            if stop_updater.is_set():
                break
            if status_msg_id:
                try:
                    await bot_api.edit_message_text(chat_id, status_msg_id, frames[idx])
                except Exception:
                    pass
            idx = (idx + 1) % len(frames)

    ticker_task = asyncio.create_task(_progress_ticker())
    try:
        result = await execute_bypass_job(job.id)
    finally:
        stop_updater.set()
        ticker_task.cancel()
        engine.cleanup_job(job.id)

    if result.get("status") is True and result.get("url"):
        final_url = result["url"]
        dur = result.get("response_ms", "1000ms")
        res_text = (
            f"⚡ <b>{to_small_caps('Link Bypassed Successfully!')}</b>\n\n"
            f"🔗 <b>{to_small_caps('Original Link')}:</b>\n{html.escape(target_url)}\n\n"
            f"🎯 <b>{to_small_caps('Bypassed Link')}:</b>\n{html.escape(final_url)}\n\n"
            f"⏱ <b>{to_small_caps('Time Taken')}:</b> <code>{dur}</code>\n\n"
            f"👆 <i>{to_small_caps('Tap the bypassed link above to copy immediately!')}</i>"
        )
        markup = build_result_markup(final_url, target_url)
        if status_msg_id:
            await bot_api.edit_message_text(chat_id, status_msg_id, res_text, reply_markup=markup)
        else:
            await bot_api.send_message(chat_id, res_text, reply_markup=markup)
        if status_msg_id:
            schedule_auto_delete(chat_id, status_msg_id, 120)
        if reply_msg_id:
            schedule_auto_delete(chat_id, reply_msg_id, 120)
    else:
        err = sanitize_engine_names(result.get("message"))
        err_text = (
            f"❌ <b>{to_small_caps('Bypass Failed!')}</b>\n\n"
            f"⚠️ <i>{to_small_caps(err)}</i>\n\n"
            f"🔗 <b>{to_small_caps('Original Link')}:</b>\n{html.escape(target_url)}"
        )
        if status_msg_id:
            await bot_api.edit_message_text(chat_id, status_msg_id, err_text)
        else:
            await bot_api.send_message(chat_id, err_text)

async def run_bot_polling():
    global BOT_TOKEN, bot_api
    offset = 0
    while True:
        token = (read_file_safe("token.txt") or os.environ.get("BOT_TOKEN", "").strip())
        if not token:
            logger.info("ℹ️ Telegram BOT_TOKEN is waiting to be configured (in .env or token.txt). Retrying in 10s...")
            await asyncio.sleep(10)
            continue

        if bot_api.token != token:
            bot_api = TelegramBotAPI(token)
            BOT_TOKEN = token

        try:
            res = await bot_api.request("getUpdates", {"offset": offset, "timeout": 20})
            if not res.get("ok"):
                await asyncio.sleep(4)
                continue

            for update in res.get("result", []):
                offset = update["update_id"] + 1

                # 1. Message Event
                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    user = msg.get("from", {})
                    user_id = user.get("id")
                    first_name = html.escape(user.get("first_name", "Friend"))
                    text = (msg.get("text") or msg.get("caption") or "").strip()
                    if user_id:
                        register_user(user_id)

                    is_owner = bool(not OWNER_ID or user_id == OWNER_ID)

                    # Check Owner Inputs
                    if is_owner and OWNER_INPUT_STATE.get(user_id) == "WAITING_SESSION":
                        OWNER_INPUT_STATE.pop(user_id, None)
                        wait_m = await bot_api.send_message(chat_id, "🔄 <b>Connecting Userbot with pasted StringSession...</b>")
                        w_mid = wait_m.get("result", {}).get("message_id")
                        ok, info = await restart_userbot(text)
                        msg_txt = f"✅ <b>Userbot Connected:</b> {info}" if ok else f"❌ <b>Connection Failed:</b> {info}"
                        if w_mid:
                            await bot_api.edit_message_text(chat_id, w_mid, msg_txt)
                        else:
                            await bot_api.send_message(chat_id, msg_txt)
                        continue

                    if is_owner and OWNER_INPUT_STATE.get(user_id) == "WAITING_MINIAPP":
                        OWNER_INPUT_STATE.pop(user_id, None)
                        global MINI_APP_URL
                        MINI_APP_URL = text
                        write_file_safe("miniapp.txt", text)
                        await bot_api.send_message(chat_id, f"✅ <b>Mini App URL Updated:</b> <code>{text}</code>")
                        continue

                    # Direct Session String Paste for Owner
                    if is_owner and len(text) > 100 and text.startswith("1") and not text.startswith("http"):
                        wait_m = await bot_api.send_message(chat_id, "🔄 <b>Connecting Userbot with StringSession...</b>")
                        w_mid = wait_m.get("result", {}).get("message_id")
                        ok, info = await restart_userbot(text)
                        msg_txt = f"✅ <b>Userbot Connected:</b> {info}" if ok else f"❌ <b>Connection Failed:</b> {info}"
                        if w_mid:
                            await bot_api.edit_message_text(chat_id, w_mid, msg_txt)
                        continue

                    # Commands
                    if text == "/start":
                        start_msg = (
                            f"{to_small_caps('welcome')} {first_name} 🌹\n\n"
                            f"{to_small_caps('this is the fastest and powerful auto link bypass bot ∆')}\n\n"
                            f"⚡ <b>{to_small_caps('providerbotz engine')}</b>\n"
                            f"{to_small_caps('send any supported shortener link below to bypass instantly.')}\n\n"
                            f"📢 <b>{to_small_caps('official updates')}:</b> {FSUB_CHANNEL}"
                        )
                        start_markup = build_start_markup(user_id)
                        sent_start = False
                        if START_IMAGE_URL:
                            res_photo = await bot_api.send_photo(chat_id, START_IMAGE_URL, caption=start_msg, reply_markup=start_markup)
                            if res_photo.get("ok"):
                                sent_start = True
                        if not sent_start:
                            await bot_api.send_message(chat_id, start_msg, reply_markup=start_markup)
                    elif text == "/help":
                        help_msg = (
                            f"📖 <b>{to_small_caps('help guide')}</b>\n\n"
                            f"1. <b>{to_small_caps('send a link')}</b>: Simply paste any supported shortlink.\n"
                            f"2. <b>{to_small_caps('automatic processing')}</b>: The bot resolves destination URLs instantly.\n"
                            f"3. <b>{to_small_caps('clean result')}</b>: Tap the link above to copy immediately."
                        )
                        await bot_api.send_message(chat_id, help_msg)
                    elif text == "/about":
                        about_msg = (
                            f"ℹ️ <b>{to_small_caps('about')} ShortnerBypass</b>\n\n"
                            f"• <b>{to_small_caps('version')}</b>: <code>v{VERSION}</code>\n"
                            f"• <b>{to_small_caps('developer')}</b>: {DEVELOPER}\n"
                            f"• <b>{to_small_caps('engine')}</b>: Dual-Core ProviderBotz High-Speed Engines\n"
                            f"• <b>{to_small_caps('mode')}</b>: High-Speed Async Telethon Userbot"
                        )
                        await bot_api.send_message(chat_id, about_msg)
                    elif text in ("/stats", "/users"):
                        if is_owner:
                            st = (
                                f"📊 <b>{to_small_caps('bot statistics')} (v{VERSION})</b>\n\n"
                                f"• 🤖 <b>Userbot:</b> {'🟢 Online' if engine.connected else '🔴 Offline'}\n"
                                f"• 👥 <b>Registered Users:</b> <code>{len(_REGISTERED_USERS)}</code>\n"
                                f"• ⚡ <b>Total Bypasses:</b> <code>{engine.total_bypasses}</code>\n"
                                f"• ✅ <b>Successful:</b> <code>{engine.successful_bypasses}</code>\n"
                                f"• ❌ <b>Failed:</b> <code>{engine.failed_bypasses}</code>"
                            )
                            await bot_api.send_message(chat_id, st)
                        else:
                            await bot_api.send_message(chat_id, "⛔ Access denied.")
                    elif text in ("/gensession", "/generatesession", "/sessiongen"):
                        if is_owner:
                            await send_gen_session_menu(chat_id)
                        else:
                            await bot_api.send_message(chat_id, "⛔ Access denied.")
                    elif text.startswith(("/setsession", "/session")):
                        if is_owner:
                            parts = text.split(None, 1)
                            if len(parts) > 1:
                                ok, info = await restart_userbot(parts[1].strip())
                                await bot_api.send_message(chat_id, f"{'✅' if ok else '❌'} {info}")
                            else:
                                OWNER_INPUT_STATE[user_id] = "WAITING_SESSION"
                                await bot_api.send_message(chat_id, "📋 Please paste your StringSession below:")
                    elif text.startswith(("/setminiapp", "/miniapp")):
                        if is_owner:
                            parts = text.split(None, 1)
                            if len(parts) > 1:
                                MINI_APP_URL = parts[1].strip()
                                write_file_safe("miniapp.txt", MINI_APP_URL)
                                await bot_api.send_message(chat_id, f"✅ Mini App URL set: <code>{MINI_APP_URL}</code>")
                            else:
                                OWNER_INPUT_STATE[user_id] = "WAITING_MINIAPP"
                                await bot_api.send_message(chat_id, "🌐 Please send your Mini App URL:")
                    else:
                        m_url = re.search(r'https?://[^\s\n\)\]>"\']+', text)
                        if m_url:
                            username_val = user.get("username")
                            asyncio.create_task(process_telegram_link(chat_id, user_id, m_url.group(0), msg.get("message_id"), first_name, username_val))

                # 2. Callback Query Event
                elif "callback_query" in update:
                    cq = update["callback_query"]
                    cq_id = cq["id"]
                    data = cq.get("data", "")
                    msg = cq.get("message", {})
                    chat_id = msg.get("chat", {}).get("id")
                    mid = msg.get("message_id")
                    user = cq.get("from", {})
                    user_id = user.get("id")
                    first_name = html.escape(user.get("first_name", "Friend"))
                    username_val = user.get("username")
                    await bot_api.answer_callback_query(cq_id)

                    if data == "cmd_paste_session":
                        OWNER_INPUT_STATE[user_id] = "WAITING_SESSION"
                        await bot_api.send_message(chat_id, "📋 <b>Paste StringSession:</b> Please send your Telethon StringSession:")
                    elif data == "cmd_gen_session":
                        await send_gen_session_menu(chat_id, mid)
                    elif data == "cmd_home":
                        start_msg = (
                            f"{to_small_caps('welcome')} {first_name} 🌹\n\n"
                            f"{to_small_caps('this is the fastest and powerful auto link bypass bot ∆')}\n\n"
                            f"⚡ <b>{to_small_caps('providerbotz engine')} (v{VERSION})</b>\n"
                            f"{to_small_caps('send any supported shortener link below to bypass instantly.')}\n\n"
                            f"📢 <b>{to_small_caps('official updates')}:</b> {FSUB_CHANNEL}"
                        )
                        await bot_api.edit_message_text(chat_id, mid, start_msg, reply_markup=build_start_markup(user_id))
                    elif data == "cmd_set_miniapp":
                        OWNER_INPUT_STATE[user_id] = "WAITING_MINIAPP"
                        await bot_api.send_message(chat_id, "🌐 <b>Set Mini App Link:</b> Please send your HTTPS WebApp URL:")
                    elif data == "cmd_close":
                        await bot_api.delete_message(chat_id, mid)
                    elif data == "cmd_help":
                        await bot_api.send_message(chat_id, "📖 Send any shortener link to bypass instantly.")
                    elif data == "cmd_about":
                        await bot_api.send_message(chat_id, f"ShortnerBypass v{VERSION} by {DEVELOPER}")
                    elif data.startswith("retry:"):
                        retry_url = data.split("retry:", 1)[1]
                        asyncio.create_task(process_telegram_link(chat_id, user_id, retry_url, mid, first_name, username_val))

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Telegram polling notice: {e}")
            await asyncio.sleep(3)

# ══════════════════════════════════════════════════════════════
#  HTTP WEB SERVER & REST API (FLASK OR BUILT-IN FALLBACK)
# ══════════════════════════════════════════════════════════════
if HAS_FLASK:
    app = Flask(__name__)

    @app.route("/", methods=["GET"])
    def index():
        index_file = os.path.join(BASE_DIR, "index.html")
        if os.path.exists(index_file):
            return send_file(index_file)
        return jsonify({"status": "online", "developer": DEVELOPER}), 200

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "healthy",
            "service": "ShortnerBypass",
            "version": VERSION,
            "userbot": engine.connected,
            "uptime": int(time.time() - engine.start_time)
        }), 200

    @app.route("/bypass", methods=["GET"])
    def api_bypass():
        url = request.args.get("url") or request.args.get("link")
        if not url:
            return jsonify({"status": False, "message": "Missing 'url' query parameter"}), 400

        if not GLOBAL_ASYNC_LOOP:
            return jsonify({"status": False, "message": "Async loop not initialized"}), 503

        raw_uid = request.args.get("uid")
        uid = int(raw_uid) if raw_uid and raw_uid.isdigit() else None
        fname = request.args.get("fname") or "API User"
        uname = request.args.get("uname") or request.args.get("username")
        job = engine.create_job(url, user_id=uid, first_name=fname, username=uname)
        try:
            future = asyncio.run_coroutine_threadsafe(execute_bypass_job(job.id), GLOBAL_ASYNC_LOOP)
            result = future.result(timeout=MAX_BYPASS_TIMEOUT_SEC + 5)
            code = 200 if result.get("status") is True else 422
            return jsonify(result), code
        except Exception as e:
            return jsonify({"status": False, "message": f"Timeout or engine error: {e}"}), 504
        finally:
            engine.cleanup_job(job.id)

    @app.route("/api/config", methods=["GET", "POST", "OPTIONS"])
    def api_config():
        if request.method == "OPTIONS":
            return "", 204
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            if "bot_token" in data and data["bot_token"]:
                write_file_safe("token.txt", data["bot_token"].strip())
            if "miniapp_url" in data and data["miniapp_url"]:
                global MINI_APP_URL
                MINI_APP_URL = data["miniapp_url"].strip()
                write_file_safe("miniapp.txt", MINI_APP_URL)
            if "telegram_session" in data and data["telegram_session"] and GLOBAL_ASYNC_LOOP:
                asyncio.run_coroutine_threadsafe(restart_userbot(data["telegram_session"].strip()), GLOBAL_ASYNC_LOOP)
            return jsonify({"status": "updated"}), 200

        return jsonify({
            "bot_configured": bool(BOT_TOKEN),
            "bot_username": BOT_USERNAME,
            "userbot_connected": engine.connected,
            "miniapp_url": MINI_APP_URL,
            "owner_id": OWNER_ID
        }), 200

    @app.route("/admin/status", methods=["GET"])
    def admin_status():
        return jsonify({
            "developer": DEVELOPER,
            "version": VERSION,
            "uptime_sec": int(time.time() - engine.start_time),
            "total_bypasses": engine.total_bypasses,
            "successful_bypasses": engine.successful_bypasses,
            "failed_bypasses": engine.failed_bypasses,
            "userbot_connected": engine.connected
        }), 200
else:
    app = None

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class FallbackHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        if path == "/":
            index_path = os.path.join(BASE_DIR, "index.html")
            if os.path.exists(index_path):
                try:
                    with open(index_path, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                    return
                except Exception:
                    pass
            self._send_json({"status": "online", "developer": DEVELOPER})
            return

        if path == "/health":
            self._send_json({
                "status": "healthy",
                "service": "ShortnerBypass",
                "version": VERSION,
                "userbot": engine.connected,
                "uptime": int(time.time() - engine.start_time)
            })
            return

        if path == "/bypass":
            url = (qs.get("url") or qs.get("link") or [""])[0].strip()
            if not url:
                self._send_json({"status": False, "message": "Missing 'url' query parameter"}, code=400)
                return
            if not GLOBAL_ASYNC_LOOP:
                self._send_json({"status": False, "message": "Async loop not initialized"}, code=503)
                return
            uid = int(qs["uid"][0]) if "uid" in qs and qs["uid"][0].isdigit() else None
            fname = (qs.get("fname") or ["API User"])[0]
            uname = (qs.get("uname") or qs.get("username") or [None])[0]
            job = engine.create_job(url, user_id=uid, first_name=fname, username=uname)
            try:
                fut = asyncio.run_coroutine_threadsafe(execute_bypass_job(job.id), GLOBAL_ASYNC_LOOP)
                res = fut.result(timeout=MAX_BYPASS_TIMEOUT_SEC + 5)
                code = 200 if res.get("status") is True else 422
                self._send_json(res, code=code)
            except Exception as e:
                self._send_json({"status": False, "message": f"Timeout or engine error: {e}"}, code=504)
            finally:
                engine.cleanup_job(job.id)
            return

        if path == "/admin/status":
            self._send_json({
                "developer": DEVELOPER,
                "version": VERSION,
                "uptime_sec": int(time.time() - engine.start_time),
                "total_bypasses": engine.total_bypasses,
                "successful_bypasses": engine.successful_bypasses,
                "failed_bypasses": engine.failed_bypasses,
                "userbot_connected": engine.connected
            })
            return

        if path == "/api/config":
            self._send_json({
                "bot_configured": bool(BOT_TOKEN),
                "bot_username": BOT_USERNAME,
                "userbot_connected": engine.connected,
                "miniapp_url": MINI_APP_URL,
                "owner_id": OWNER_ID
            })
            return

        self._send_json({"status": "not_found"}, code=404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path == "/api/config":
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
            try:
                data = json.loads(post_body)
            except Exception:
                data = {}
            if "bot_token" in data and data["bot_token"]:
                write_file_safe("token.txt", data["bot_token"].strip())
            if "miniapp_url" in data and data["miniapp_url"]:
                global MINI_APP_URL
                MINI_APP_URL = data["miniapp_url"].strip()
                write_file_safe("miniapp.txt", MINI_APP_URL)
            if "telegram_session" in data and data["telegram_session"] and GLOBAL_ASYNC_LOOP:
                asyncio.run_coroutine_threadsafe(restart_userbot(data["telegram_session"].strip()), GLOBAL_ASYNC_LOOP)
            self._send_json({"status": "updated"})
            return
        self._send_json({"status": "not_found"}, code=404)

    def _send_json(self, data: Dict[str, Any], code: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def run_http_server():
    if HAS_FLASK and app:
        logger.info(f"Flask HTTP server starting on port {PORT}...")
        app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False, threaded=True)
    else:
        logger.info(f"Built-in HTTP server starting on port {PORT}...")
        try:
            server = HTTPServer(("0.0.0.0", PORT), FallbackHTTPHandler)
            server.serve_forever()
        except Exception as e:
            logger.warning(f"Built-in HTTP server notice: {e}")

# ══════════════════════════════════════════════════════════════
#  MAIN ASYNC RUNNER
# ══════════════════════════════════════════════════════════════
async def main_async():
    global GLOBAL_ASYNC_LOOP
    GLOBAL_ASYNC_LOOP = asyncio.get_running_loop()

    # 1. Initialize Telethon Userbot if credentials present
    if TELEGRAM_API_ID and TELEGRAM_API_HASH and TELEGRAM_SESSION:
        logger.info("Connecting Telethon Userbot...")
        ok, info = await restart_userbot(TELEGRAM_SESSION)
        if ok:
            logger.info(f"✅ Userbot online: {info}")
        else:
            logger.warning(f"⚠️ Userbot connection note: {info}")
            if "AuthKeyDuplicatedError" in info and OWNER_ID and BOT_TOKEN:
                try:
                    await bot_api.send_message(
                        OWNER_ID,
                        f"⚠️ <b>Userbot Session Alert (v{VERSION})</b>\n\n"
                        f"Telegram invalidated your StringSession because it was detected active on two different IP addresses simultaneously (<code>AuthKeyDuplicatedError</code>).\n\n"
                        f"👉 <i>Please generate a fresh session below and tap Paste StringSession to restore userbot:</i>",
                        reply_markup={
                            "inline_keyboard": [
                                [{"text": "🔑 Generate StringSession", "url": "https://t.me/StringFatherBot", "style": "primary"}],
                                [{"text": "📋 Paste StringSession", "callback_data": "cmd_paste_session", "style": "success"}]
                            ]
                        }
                    )
                except Exception:
                    pass

    # 2. Launch Telegram Bot API Polling
    asyncio.create_task(run_bot_polling())

    # 3. Print Startup Banner
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ProviderBotz Auto Bypass Bot (v{VERSION})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HTTP Health Server: running (Port {PORT})
Public Bot API: {'online (@' + BOT_USERNAME + ')' if BOT_TOKEN else 'waiting for token'}
Bypass Engine: {'connected' if engine.connected else 'offline'}
Mode: High-Performance Async Telethon + Flask
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""", flush=True)

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    t = threading.Thread(target=run_http_server, daemon=True, name="HTTPThread")
    t.start()
    try:
        asyncio.run(main_async())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 ShortnerBypass stopped.")
