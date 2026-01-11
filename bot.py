import os
import requests
import re
from bs4 import BeautifulSoup
from telegram import InputMediaPhoto, Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# Variables Railway
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

INVITE_LINK = "https://m.hipobuy.com/pages/register/index?inviteCode=E6EMQHWWA"

# Fonction pour arrondir le prix à l'euro
def round_price(price_text):
    match = re.search(r"(\d+[.,]?\d*)", price_text.replace(",", "."))
    if not match:
        return "Prix non disponible"
    price = float(match.group(1))
    return f"{round(price)}€"

# Récupération du prix et des images
def scrape_hipobuy(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, "lxml")

    # Prix
    price_tag = soup.find(class_="price")
    price = round_price(price_tag.text) if price_tag else "Prix non disponible"

    # Images
    images = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if src and src.startswith("http"):
            images.append(src)
    images = list(dict.fromkeys(images))[:5]  # max 5 images
    return price, images

# Handler des messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "|" not in text:
        await update.message.reply_text(
            "❌ Format invalide\nExemple :\nNom de l’article | lien Hipobuy"
        )
        return

    name, url = map(str.strip, text.split("|", 1))

    if "hipobuy.com" not in url:
        await update.message.reply_text("❌
