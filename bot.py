import asyncio
import json
import os
from urllib.request import Request, urlopen

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_USERNAME = "@MIMI618HunterBot"
TOKEN_NAME = "MIMI618"
NETWORK = "TON"
TOTAL_SUPPLY = "1,000,000,000 MIMI618"
TOTAL_SUPPLY_BASE_UNITS = 1_000_000_000_000_000_000
DECIMALS = 9
CONTRACT_ADDRESS = "EQBMSvB2k2gNqCcZNFZkGyoPO-GVQlu2pddFcCt9Al6yVOO6"
WEBSITE_URL = "https://ton618-hunter.github.io/MimiToken/"
LOGO_URL = "https://ton618-hunter.github.io/MimiToken/logo.png"
EXPLORER_URL = "https://tonviewer.com/EQBMSvB2k2gNqCcZNFZkGyoPO-GVQlu2pddFcCt9Al6yVOO6"
TONAPI_JETTON_URL = f"https://tonapi.io/v2/jettons/{CONTRACT_ADDRESS}"
TONAPI_HOLDERS_URL = f"https://tonapi.io/v2/jettons/{CONTRACT_ADDRESS}/holders?limit=10&sort_by=balance"
TONAPI_ACCOUNT_JETTONS_URL = "https://tonapi.io/v2/accounts/{address}/jettons"

COMMUNITY_URL = os.getenv("MIMI618_COMMUNITY_URL", "")
ROADMAP_URL = os.getenv("MIMI618_ROADMAP_URL", WEBSITE_URL)


def community_text() -> str:
    if COMMUNITY_URL:
        return f"👥 MIMI618 Community: {COMMUNITY_URL}"
    return "👥 MIMI618 Community: link will be added when the official group is created."


def format_supply(raw_supply: int) -> str:
    amount = raw_supply / (10 ** DECIMALS)
    return f"{amount:,.0f} {TOKEN_NAME}"


async def fetch_live_supply() -> str | None:
    def fetch() -> str | None:
        request = Request(
            TONAPI_JETTON_URL,
            headers={"User-Agent": "MIMI618-Bot/1.0"},
        )
        with urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
        raw_supply = payload.get("total_supply")
        if raw_supply is None:
            return None
        return format_supply(int(raw_supply))

    try:
        return await asyncio.to_thread(fetch)
    except Exception:
        return None


def is_valid_ton_address(address: str) -> bool:
    if address.startswith(("EQ", "UQ")) and len(address) == 48:
        return True
    if address.startswith(("0:", "-1:")) and len(address) == 66:
        return True
    return False


def short_address(address: str) -> str:
    if len(address) <= 14:
        return address
    return f"{address[:6]}...{address[-6:]}"


async def fetch_holders() -> tuple[int, list[tuple[str, int]]] | None:
    def fetch() -> tuple[int, list[tuple[str, int]]] | None:
        request = Request(
            TONAPI_HOLDERS_URL,
            headers={"User-Agent": "MIMI618-Bot/1.0"},
        )
        with urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))

        total = int(payload.get("total", 0))
        holders = []
        for item in payload.get("addresses", []):
            owner = item.get("owner") or {}
            address = owner.get("address") or item.get("address")
            balance = item.get("balance")
            if address and balance is not None:
                holders.append((address, int(balance)))
        return total, holders

    try:
        return await asyncio.to_thread(fetch)
    except Exception:
        return None


async def fetch_wallet_balance(address: str) -> int | None:
    def fetch() -> int | None:
        url = TONAPI_ACCOUNT_JETTONS_URL.format(address=address)
        request = Request(url, headers={"User-Agent": "MIMI618-Bot/1.0"})
        with urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
        for item in payload.get("balances", []):
            jetton = item.get("jetton") or {}
            if jetton.get("address") == CONTRACT_ADDRESS:
                return int(item.get("balance", 0))
        return 0
    try:
        return await asyncio.to_thread(fetch)
    except Exception:
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🐱 Welcome to MIMI618!\n\n"
        "MIMI618 is a community token on The Open Network (TON).\n"
        "Fixed initial supply: 1,000,000,000 MIMI618.\n"
        "No further minting is possible.\n\n"
        "Use /token to see token details.\n"
        "Use /supply to check the live on-chain supply.\n"
        "Use /holders to see the current holder count and top holders.\n"
        "Use /wallet <TON address> to check a wallet's MIMI618 balance.\n"
        "Use /roadmap to see the project roadmap.\n"
        "Use /links to see official links."
    )


async def token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🐱 MIMI618 Token\n\n"
        f"Name: {TOKEN_NAME}\n"
        "Symbol: MIMI618\n"
        f"Network: {NETWORK}\n"
        f"Declared supply: {TOTAL_SUPPLY}\n"
        "Supply: fixed, no further minting\n"
        f"Contract: {CONTRACT_ADDRESS}\n\n"
        f"Explorer: {EXPLORER_URL}"
    )


async def supply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    live_supply = await fetch_live_supply()

    if live_supply:
        message = (
            "📦 MIMI618 live supply\n\n"
            f"Current on-chain supply: {live_supply}\n"
            "Source: TON blockchain via TON API.\n\n"
            "Minting is permanently disabled."
        )
    else:
        message = (
            "📦 MIMI618 supply\n\n"
            f"Declared supply: {TOTAL_SUPPLY}\n"
            "Live on-chain data is temporarily unavailable.\n"
            "Please try /supply again in a moment."
        )

    await update.message.reply_text(message)


async def holders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = await fetch_holders()

    if not data:
        await update.message.reply_text(
            "👥 MIMI618 Holders\n\n"
            "Live holder data is temporarily unavailable.\n"
            "Please try /holders again in a moment."
        )
        return

    total, top_holders = data
    lines = [
        "👥 MIMI618 Holders",
        "",
        f"Total holders: {total:,}",
        "",
        "🏆 Top 10 holders:",
    ]

    for index, (address, raw_balance) in enumerate(top_holders, start=1):
        amount = raw_balance / (10 ** DECIMALS)
        percentage = (amount / (TOTAL_SUPPLY_BASE_UNITS / (10 ** DECIMALS)) * 100)
        lines.append(
            f"{index}. {short_address(address)} · "
            f"{amount:,.0f} MIMI618 ({percentage:.2f}%)"
        )

    lines.extend([
        "",
        "Source: TON blockchain via TON API.",
        f"Explorer: {EXPLORER_URL}",
    ])
    await update.message.reply_text("\n".join(lines))


async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 1:
        await update.message.reply_text(
            "👛 MIMI618 Wallet\n\n"
            "Usage:\n"
            "/wallet <TON address>\n\n"
            "Example:\n"
            "/wallet EQ..."
        )
        return

    address = context.args[0].strip()
    if not is_valid_ton_address(address):
        await update.message.reply_text(
            "❌ Invalid TON address format.\n\n"
            "Send a standard EQ/UQ address or a raw TON address (0:/-1:)."
        )
        return

    raw_balance = await fetch_wallet_balance(address)
    if raw_balance is None:
        await update.message.reply_text(
            "👛 MIMI618 Wallet\n\n"
            "Wallet data is temporarily unavailable.\n"
            "Please try /wallet again in a moment."
        )
        return

    amount = raw_balance / (10 ** DECIMALS)
    percentage = amount / (TOTAL_SUPPLY_BASE_UNITS / (10 ** DECIMALS)) * 100
    status = "✅ Wallet holds MIMI618." if amount > 0 else "ℹ️ Wallet has no MIMI618 balance."

    await update.message.reply_text(
        "👛 MIMI618 Wallet\n\n"
        f"Address: {short_address(address)}\n"
        f"Balance: {amount:,.9f} MIMI618\n"
        f"Share of initial supply: {percentage:.6f}%\n\n"
        f"{status}\n\n"
        "Source: TON blockchain via TON API.\n"
        f"Wallet: https://tonviewer.com/{address}"
    )


async def contract(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"📜 MIMI618 Jetton contract:\n{CONTRACT_ADDRESS}\n\n"
        f"Explorer: {EXPLORER_URL}"
    )


async def roadmap(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🗺 MIMI618 Roadmap\n\n"
        "1. Telegram community and official bot\n"
        "2. MIMI618 website and project information\n"
        "3. Liquidity and ecosystem development\n"
        "4. Integration with TON618Hunter\n"
        "5. Future wallet, holder and market-data features\n\n"
        f"Project: {ROADMAP_URL}"
    )


async def links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🔗 MIMI618 Official Links\n\n"
        f"Website: {WEBSITE_URL}\n"
        f"Contract explorer: {EXPLORER_URL}\n"
        f"Bot: https://t.me/{BOT_USERNAME.lstrip('@')}\n\n"
        + community_text()
    )


async def community(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(community_text())


def main() -> None:
    token_value = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token_value:
        raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is not set.")

    app = Application.builder().token(token_value).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("token", token))
    app.add_handler(CommandHandler("supply", supply))
    app.add_handler(CommandHandler("holders", holders))
    app.add_handler(CommandHandler("wallet", wallet))
    app.add_handler(CommandHandler("contract", contract))
    app.add_handler(CommandHandler("roadmap", roadmap))
    app.add_handler(CommandHandler("links", links))
    app.add_handler(CommandHandler("community", community))

    app.run_polling()


if __name__ == "__main__":
    main()
