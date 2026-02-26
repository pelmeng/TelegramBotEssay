# =========================================
# Telegram Essay Bot + Ollama AI
# =========================================

import telebot
import requests
import re
from flask import Flask
from threading import Thread
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"
# ===============================================

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

# ---------- Keep Alive ----------
app = Flask('')

@app.route('/')
def home():
    return "Essay bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

# ---------- Парсер размера ----------
def parse_length(text):
    t = text.lower().strip()

    WORD_NUMBERS = {
        "ноль": 0,
        "один": 1, "одна": 1,
        "два": 2, "две": 2,
        "три": 3,
        "четыре": 4,
        "пять": 5,
        "шесть": 6,
        "семь": 7,
        "восемь": 8,
        "девять": 9,
        "десять": 10,
        "пол": 0.5,
        "полторы": 1.5,
        "полтора": 1.5
    }

    # 1️⃣ слова
    if "слов" in t:
        nums = re.findall(r"\d+", t)
        if nums:
            return int(nums[0])

    # 2️⃣ цифры + страницы
    if "страниц" in t or "страница" in t:
        nums = re.findall(r"\d+(?:\.\d+)?", t)
        if nums:
            return int(float(nums[0]) * 180)

        for word, value in WORD_NUMBERS.items():
            if word in t:
                return int(value * 180)

    # 3️⃣ только слова (без "страница")
    for word, value in WORD_NUMBERS.items():
        if word == "пол":
            continue
        if word in t:
            if value <= 10:
                return int(value * 180)

    # 4️⃣ просто число
    nums = re.findall(r"\d+(?:\.\d+)?", t)
    if nums:
        n = float(nums[0])
        if n <= 10:
            return int(n * 180)
        return int(n)

    # 5️⃣ если вообще не понял
    return 180


# ---------- Ollama ----------
def generate_essay(topic, class_num, words):
    prompt = f"""
Напиши школьное сочинение для {class_num} класса.
Тема: "{topic}"

Требования:
- объём {words}–{words + 40} слов
- школьный стиль
- простой и понятный язык
- структура: вступление, основная часть, заключение
- без сложных терминов
- на русском языке
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]

# ---------- /start ----------
@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"step": "topic"}
    bot.send_message(chat_id, "✍️ Привет! Напиши тему сочинения.")

# ---------- Основная логика ----------
@bot.message_handler(func=lambda m: True)
def handler(message):
    chat_id = message.chat.id
    text = message.text

    if chat_id not in user_data:
        bot.send_message(chat_id, "Напиши /start")
        return

    step = user_data[chat_id]["step"]

    if step == "topic":
        user_data[chat_id]["topic"] = text
        user_data[chat_id]["step"] = "class"
        bot.send_message(chat_id, "Для какого класса?")

    elif step == "class":
        user_data[chat_id]["class"] = text
        user_data[chat_id]["step"] = "length"
        bot.send_message(chat_id, "Какой размер сочинения?")

    elif step == "length":
        words = parse_length(text)
        user_data[chat_id]["words"] = words

        bot.send_message(chat_id, "🧠 Пишу сочинение...")

        essay = generate_essay(
            user_data[chat_id]["topic"],
            user_data[chat_id]["class"],
            user_data[chat_id]["words"]
        )

        bot.send_message(chat_id, essay)
        user_data.pop(chat_id)

# ---------- Запуск ----------
if __name__ == "__main__":
    keep_alive()
    print("🤖 Essay AI Bot запущен")
    bot.polling(none_stop=True)
