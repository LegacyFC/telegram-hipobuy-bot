import os, requests, re
from bs4 import BeautifulSoup
from telegram import InputMediaPhoto, Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
INVITE_LINK = "https://m.hipobuy.com/pages/register/index?inviteCode=E6EMQHWWA"

def round_price(text):
    m = re.search(r"(\d+[.,]?\d*)", text.replace(",", "."))
    return f"{round(float(m.group(1)))}€" if m else "Prix non dispo"

def scrape(url):
    r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "lxml")
    p = soup.find(class_="price")
    price = round_price(p.text) if p else "Prix non dispo"
    imgs = [img.get("src") for img in soup.find_all("img") if img.get("src") and img.get("src").startswith("http")]
    return price, list(dict.fromkeys(imgs))[:5]

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "|" not in update.message.text:
        await update.message.reply_text("❌ Format invalide : Nom | lien")
        return
    name, url = map(str.strip, update.message.text.split("|",1))
    if "hipobuy.com" not in url:
        await update.message.reply_text("❌ Lien Hipobuy invalide.")
        return
    price, imgs = scrape(url)
    caption = f"📜 Article : {name}\n💲 Prix : {price}\n🧩 Lien : {url}\n\n! S'INSCRIRE ICI :\n{INVITE_LINK}"
    if imgs:
        media=[InputMediaPhoto(imgs[0], caption=caption)]
        for img in imgs[1:]: media.append(InputMediaPhoto(img))
        await context.bot.send_media_group(CHANNEL_ID, media)
    else:
        await context.bot.send_message(CHANNEL_ID, caption)
    await update.message.reply_text("✅ Publié dans le canal.")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
app.run_polling()
