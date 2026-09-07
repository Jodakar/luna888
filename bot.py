#!/usr/bin/env python3
import os
import logging
import smtplib
import ssl
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Почта
SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = int(os.getenv('SMTP_PORT', 465))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
SMTP_FROM = os.getenv('SMTP_FROM')
SMTP_TO = os.getenv('SMTP_TO')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def send_email(subject, body, is_error=True):
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_FROM
        msg['To'] = SMTP_TO
        msg['Subject'] = f"[{'❌' if is_error else '✅'}] Luna888: {subject}"
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"📧 Письмо отправлено на {SMTP_TO}")
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки email: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Бот работает напрямую!\n\n"
        "📌 Доступные команды:\n"
        "/status — статус сервера\n"
        "/help — помощь"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import subprocess
    nginx_ok = subprocess.run(['systemctl', 'is-active', 'nginx'], capture_output=True, text=True).stdout.strip() == 'active'
    pg_ok = subprocess.run(['systemctl', 'is-active', 'postgresql'], capture_output=True, text=True).stdout.strip() == 'active'
    
    status_text = (
        f"📊 **СТАТУС СЕРВЕРА**\n\n"
        f"🖥️ Nginx: {'✅ Работает' if nginx_ok else '❌ Не работает'}\n"
        f"🗄️ PostgreSQL: {'✅ Работает' if pg_ok else '❌ Не работает'}\n"
        f"🤖 Бот: ✅ Активен"
    )
    await update.message.reply_text(status_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 **Помощь**\n\n"
        "/start — приветствие\n"
        "/status — статус сервера\n"
        "/help — эта справка"
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    error_msg = f"🚨 Ошибка в боте\n\nВремя: {datetime.now()}\n\n{str(context.error)[:500]}"
    logger.error(error_msg)
    send_email("Ошибка в боте", error_msg)

def main():
    print("=" * 60)
    print("🤖 ЗАПУСК TELEGRAM-БОТА")
    print("=" * 60)
    print(f"🤖 Токен: {TOKEN[:10]}...")
    print("📡 Прямое подключение (без прокси)")
    print("=" * 60)

    try:
        app = Application.builder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("status", status))
        app.add_handler(CommandHandler("help", help_command))
        app.add_error_handler(error_handler)

        send_email("Бот запущен", f"Бот успешно запущен на сервере Luna888\nВремя: {datetime.now()}")
        print("📧 Тестовое письмо отправлено на jodakar@vk.com")
        print("✅ Бот запущен! Напиши /start в Telegram")
        print("=" * 60)
        
        app.run_polling()
        
    except Exception as e:
        error_msg = f"Критическая ошибка: {str(e)}"
        print(f"❌ {error_msg}")
        send_email("Критическая ошибка", error_msg)

if __name__ == "__main__":
    main()
