#!/usr/bin/env python3
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

# Third-party dependencies from requirements.txt
from dotenv import load_dotenv
import requests
import aiohttp
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import MessageEntityUrl, MessageEntityTextUrl
from flask import Flask, request, jsonify, send_file

# Load environment configuration
load_dotenv()

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
BOT_TOKEN = (
    read_file_safe("token.txt")
    or os.environ.get("BOT_TOKEN", "").strip()
)
BOT_USERNAME = os.environ.get("BOT_USERNAME", "TheLinkzoBot").strip().lstrip("@")
OWNER_ID = int(os.environ["OWNER_ID"].strip()) if os.environ.get("OWNER_ID", "").strip().isdigit() else None
DEVELOPER = os.environ.get("DEVELOPER", "@ProviderBotz").strip()
FSUB_CHANNEL = os.environ.get("FSUB_CHANNEL", "@ProviderBotz").strip()
START_IMAGE_URL = os.environ.get("START_IMAGE_URL", "").strip()

# Userbot credentials
TELEGRAM_API_ID = int(os.environ.get("TELEGRAM_API_ID", "0")) or 0
TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH", "").strip()
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
async def fast_direct_bypass(target_url: str) -> Optional[str]:
    """Recursively traces HTTP redirects and extracts unshortened destination."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
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

    # 2. HTTP Redirection follow
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            curr = target_url
            for _ in range(6):
                async with session.head(curr, headers=headers, allow_redirects=False) as resp:
                    if resp.status in (301, 302, 303, 307, 308) and "Location" in resp.headers:
                        loc = resp.headers["Location"]
                        if not loc.startswith("http"):
                            loc = requests.compat.urljoin(curr, loc)
                        curr = loc
                    else:
                        break
            if curr != target_url and is_valid_destination(curr, target_url):
                return curr
    except Exception:
        pass
    return None

# ══════════════════════════════════════════════════════════════
#  TELETHON USERBOT CORE (DUAL ENGINE DISPATCHER)
# ══════════════════════════════════════════════════════════════
class BypassJob:
    def __init__(self, job_id: str, url: str, user_id: Optional[int] = None, first_name: Optional[str] = None):
        self.id = job_id
        self.url = url
        self.user_id = user_id
        self.first_name = first_name or "Friend"
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

    def create_job(self, url: str, user_id: Optional[int] = None, first_name: Optional[str] = None) -> BypassJob:
        job_id = secrets.token_hex(6)
        job = BypassJob(job_id, url, user_id, first_name)
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
        except Exception:
            job.fast_failed = True

    async def _send_core():
        try:
            target = engine.core_entity or (ENGINE_CORE_GROUP if ENGINE_CORE_GROUP else ENGINE_CORE_BOT)
            cmd = f"/b {target_url}" if ENGINE_CORE_GROUP else target_url
            sent = await engine.client.send_message(target, cmd)
            job.core_msg_id = sent.id
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

async def restart_userbot(new_session: str) -> Tuple[bool, str]:
    global TELEGRAM_SESSION
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        return False, "TELEGRAM_API_ID and TELEGRAM_API_HASH are not configured in .env"
    try:
        new_client = TelegramClient(StringSession(new_session.strip()), TELEGRAM_API_ID, TELEGRAM_API_HASH)
        await new_client.connect()
        if not await new_client.is_user_authorized():
            await new_client.disconnect()
            return False, "Session string is invalid or unauthorized."
        me = await new_client.get_me()
        if engine.client:
            try:
                await engine.client.disconnect()
            except Exception:
                pass
        engine.client = new_client
        engine.connected = True
        TELEGRAM_SESSION = new_session.strip()
        write_file_safe("session.txt", new_session.strip())
        setup_userbot_handlers(engine.client)

        # Resolve external engines entities
        try:
            engine.fast_entity = await new_client.get_entity(ENGINE_FAST_BOT)
            engine.fast_bot_id = engine.fast_entity.id
        except Exception:
            pass
        if ENGINE_CORE_GROUP:
            try:
                engine.core_entity = await new_client.get_entity(ENGINE_CORE_GROUP)
            except Exception:
                pass

        account_name = f"{me.first_name} (@{me.username or me.id})"
        logger.info(f"✅ Userbot connected: {account_name}")
        return True, account_name
    except Exception as e:
        return False, str(e)

# ══════════════════════════════════════════════════════════════
#  TELEGRAM BOT API WORKER (COLORED BUTTONS & POLLING)
# ══════════════════════════════════════════════════════════════
class TelegramBotAPI:
    def __init__(self, token: str):
        self.token = token.strip()
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=45))
        return self.session

    async def request(self, method: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{method}"
        s = await self.get_session()
        try:
            async with s.post(url, json=data or {}) as resp:
                return await resp.json()
        except Exception as e:
            return {"ok": False, "description": str(e)}

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

async def process_telegram_link(chat_id: int, user_id: int, target_url: str, reply_msg_id: Optional[int] = None, first_name: Optional[str] = None):
    job = engine.create_job(target_url, user_id=user_id, first_name=first_name)
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
                        await bot_api.send_message(chat_id, start_msg, reply_markup=build_start_markup(user_id))
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
                            f"• <b>{to_small_caps('developer')}</b>: {DEVELOPER}\n"
                            f"• <b>{to_small_caps('engine')}</b>: Dual-Core ProviderBotz High-Speed Engines\n"
                            f"• <b>{to_small_caps('mode')}</b>: High-Speed Async Telethon Userbot"
                        )
                        await bot_api.send_message(chat_id, about_msg)
                    elif text in ("/stats", "/users"):
                        if is_owner:
                            st = (
                                f"📊 <b>{to_small_caps('bot statistics')}</b>\n\n"
                                f"• 🤖 <b>Userbot:</b> {'🟢 Online' if engine.connected else '🔴 Offline'}\n"
                                f"• 👥 <b>Registered Users:</b> <code>{len(_REGISTERED_USERS)}</code>\n"
                                f"• ⚡ <b>Total Bypasses:</b> <code>{engine.total_bypasses}</code>\n"
                                f"• ✅ <b>Successful:</b> <code>{engine.successful_bypasses}</code>\n"
                                f"• ❌ <b>Failed:</b> <code>{engine.failed_bypasses}</code>"
                            )
                            await bot_api.send_message(chat_id, st)
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
                            asyncio.create_task(process_telegram_link(chat_id, user_id, m_url.group(0), msg.get("message_id"), first_name))

                # 2. Callback Query Event
                elif "callback_query" in update:
                    cq = update["callback_query"]
                    cq_id = cq["id"]
                    data = cq.get("data", "")
                    msg = cq.get("message", {})
                    chat_id = msg.get("chat", {}).get("id")
                    mid = msg.get("message_id")
                    user_id = cq.get("from", {}).get("id")
                    await bot_api.answer_callback_query(cq_id)

                    if data == "cmd_paste_session":
                        OWNER_INPUT_STATE[user_id] = "WAITING_SESSION"
                        await bot_api.send_message(chat_id, "📋 <b>Paste StringSession:</b> Please send your Telethon StringSession:")
                    elif data == "cmd_set_miniapp":
                        OWNER_INPUT_STATE[user_id] = "WAITING_MINIAPP"
                        await bot_api.send_message(chat_id, "🌐 <b>Set Mini App Link:</b> Please send your HTTPS WebApp URL:")
                    elif data == "cmd_close":
                        await bot_api.delete_message(chat_id, mid)
                    elif data == "cmd_help":
                        await bot_api.send_message(chat_id, "📖 Send any shortener link to bypass instantly.")
                    elif data == "cmd_about":
                        await bot_api.send_message(chat_id, f"ShortnerBypass by {DEVELOPER}")
                    elif data.startswith("retry:"):
                        retry_url = data.split("retry:", 1)[1]
                        asyncio.create_task(process_telegram_link(chat_id, user_id, retry_url, mid))

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Telegram polling notice: {e}")
            await asyncio.sleep(3)

# ══════════════════════════════════════════════════════════════
#  FLASK HTTP WEB SERVER & REST API
# ══════════════════════════════════════════════════════════════
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
    job = engine.create_job(url, user_id=uid, first_name=fname)
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
        "uptime_sec": int(time.time() - engine.start_time),
        "total_bypasses": engine.total_bypasses,
        "successful_bypasses": engine.successful_bypasses,
        "failed_bypasses": engine.failed_bypasses,
        "userbot_connected": engine.connected
    }), 200

def run_flask():
    logger.info(f"Flask HTTP server starting on port {PORT}...")
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False, threaded=True)

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

    # 2. Launch Telegram Bot API Polling
    asyncio.create_task(run_bot_polling())

    # 3. Print Startup Banner
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ProviderBotz Auto Bypass Bot
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
    t = threading.Thread(target=run_flask, daemon=True, name="FlaskThread")
    t.start()
    try:
        asyncio.run(main_async())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 ShortnerBypass stopped.")
