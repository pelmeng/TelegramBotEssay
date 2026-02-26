# 🤖 Telegram Essay Bot with Ollama

AI-powered Telegram bot that generates school essays using a local LLM (Ollama).

## 🚀 Features
- Essay generation by topic
- Class-based difficulty
- Automatic length parsing (words / pages)
- Local AI model via Ollama
- Flask keep-alive server

## 🧠 Tech Stack
- Python
- pyTelegramBotAPI
- Ollama (LLM)
- Flask
- Requests

## ⚙️ Installation

1. Install Ollama
2. Pull model:
   ollama pull llama3

3. Install dependencies:
   pip install -r requirements.txt

4. Create .env file:
   BOT_TOKEN=your_token_here

5. Run:
   python bot.py

## 🏗 Architecture
Telegram → Bot → Ollama API → Response → User
