import os
import requests
import re
from bs4 import BeautifulSoup
from telegram import InputMediaPhoto, Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

INVITE_LINK = "https://m.hipobuy.com/pages/register/index?inviteCode=E6EMQHWWA"


def round_price(price_text):
    match = re.search(r"(\d+[.,]?\d*)", price_text.replace(",", "."))
    if not match:
        return "Prix non disponible"

    price = float(match.group(1))
    return f"{round(price)}€"


def scrape_hipobuy(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, "lxml")

    price_tag = soup.find(class_="price")
    price = round_price(price_tag.text) if price_tag else "Prix non disponible"

    images = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if src and src.startswith("http"):
            images.append(src)

    images = list(dict.fromkeys(images))[:5]
    return price, images


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "|" not in text:
        await update.message.reply_text(
            "❌ Format invalide\nExemple :\nNom de l’article | lien Hipobuy"
        )
        return

    name, url = map(str.strip, text.split("|", 1))

    if "hipobuy.com" not in url:
        await update.message.reply_text("❌ Lien Hipobuy invalide.")
        return

    price, images = scrape_hipobuy(url)

    caption = (
        f"📜 Article : {name}\n"
        f"💲 Prix : {price}\n"
        f"🧩 Lien : {url}\n\n"
        f"! S'INSCRIRE ICI :\n{INVITE_LINK}"
    )

    if images:
        media = [InputMediaPhoto(media=images[0], caption=caption)]
        for img in images[1:]:
            media.append(InputMediaPhoto(media=img))

        await context.bot.send_media_group(
            chat_id=CHANNEL_ID,
            media=media
        )
    else:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=caption
        )

    await update.message.reply_text("✅ Publié dans le canal.")


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
