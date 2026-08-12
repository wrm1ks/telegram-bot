import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import random
import json
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN не найден! Добавьте его в переменные окружения.")

# ============ КОМАНДА /START ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    first_name = user.first_name or "Друг"
    
    # Клавиатура с кнопками
    keyboard = [
        [
            InlineKeyboardButton("📝 Помощь", callback_data="help"),
            InlineKeyboardButton("ℹ️ О боте", callback_data="about")
        ],
        [
            InlineKeyboardButton("🎮 Игра", callback_data="game"),
            InlineKeyboardButton("📊 Статистика", callback_data="stats")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 Привет, {first_name}!\n\n"
        f"Я — твой личный помощник! Вот что я умею:\n\n"
        f"✅ Отвечать на сообщения\n"
        f"✅ Играть в игры\n"
        f"✅ Помогать с задачами\n\n"
        f"Выбери действие ниже:",
        reply_markup=reply_markup
    )

# ============ КОМАНДА /HELP ============
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 **Доступные команды:**\n\n"
        "/start — Главное меню\n"
        "/help — Эта справка\n"
        "/game — Сыграть в игру\n"
        "/stats — Твоя статистика\n"
        "/info — Информация о боте\n\n"
        "Также я умею отвечать на твои сообщения! 😊"
    )

# ============ КОМАНДА /GAME ============
async def game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = random.randint(1, 10)
    context.user_data['secret_number'] = number
    context.user_data['attempts'] = 0
    
    keyboard = [
        [InlineKeyboardButton("🔢 Угадать число", callback_data="guess")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎮 **Игра 'Угадай число'**\n\n"
        f"Я загадал число от 1 до 10.\n"
        f"Попробуй угадать! Нажми кнопку ниже.",
        reply_markup=reply_markup
    )

# ============ КОМАНДА /STATS ============
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    # Загружаем статистику из файла
    try:
        with open('stats.json', 'r') as f:
            stats_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        stats_data = {}
    
    user_stats = stats_data.get(user_id, {"games": 0, "wins": 0, "messages": 0})
    
    win_rate = (user_stats["wins"] / user_stats["games"] * 100) if user_stats["games"] > 0 else 0
    
    await update.message.reply_text(
        f"📊 **Твоя статистика**\n\n"
        f"🎮 Игр сыграно: {user_stats['games']}\n"
        f"🏆 Побед: {user_stats['wins']}\n"
        f"📈 Процент побед: {win_rate:.1f}%\n"
        f"💬 Сообщений отправлено: {user_stats['messages']}"
    )

# ============ КОМАНДА /INFO ============
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **О боте**\n\n"
        "Версия: 1.0.0\n"
        "Создан: Август 2026\n"
        "Хостинг: Railway.app\n\n"
        "Этот бот работает 24/7 и создан для демонстрации возможностей!"
    )

# ============ ОБРАБОТЧИК КНОПОК (CallbackQuery) ============
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = str(update.effective_user.id)
    
    # Загружаем статистику
    try:
        with open('stats.json', 'r') as f:
            stats_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        stats_data = {}
    
    if user_id not in stats_data:
        stats_data[user_id] = {"games": 0, "wins": 0, "messages": 0}
    
    if data == "help":
        await query.edit_message_text(
            "📚 **Доступные команды:**\n\n"
            "/start — Главное меню\n"
            "/help — Эта справка\n"
            "/game — Сыграть в игру\n"
            "/stats — Твоя статистика\n"
            "/info — Информация о боте"
        )
    
    elif data == "about":
        await query.edit_message_text(
            "🤖 Я — бот-помощник, созданный на Python.\n\n"
            "Мои возможности:\n"
            "✅ Отвечать на сообщения\n"
            "✅ Играть в игры\n"
            "✅ Хранить статистику\n"
            "✅ Работать 24/7"
        )
    
    elif data == "game" or data == "guess":
        number = context.user_data.get('secret_number', random.randint(1, 10))
        context.user_data['secret_number'] = number
        attempts = context.user_data.get('attempts', 0)
        
        keyboard = []
        # Создаем кнопки с числами 1-10 (по 5 в ряду)
        row1 = []
        row2 = []
        for i in range(1, 6):
            row1.append(InlineKeyboardButton(str(i), callback_data=f"num_{i}"))
        for i in range(6, 11):
            row2.append(InlineKeyboardButton(str(i), callback_data=f"num_{i}"))
        
        keyboard.append(row1)
        keyboard.append(row2)
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🎮 **Угадай число!**\n\n"
            f"Я загадал число от 1 до 10.\n"
            f"Попыток: {attempts}\n\n"
            f"Выбери число:",
            reply_markup=reply_markup
        )
    
    elif data.startswith("num_"):
        number = int(data.split("_")[1])
        secret = context.user_data.get('secret_number', random.randint(1, 10))
        attempts = context.user_data.get('attempts', 0) + 1
        context.user_data['attempts'] = attempts
        
        stats_data[user_id]["games"] += 1
        
        if number == secret:
            stats_data[user_id]["wins"] += 1
            # Сохраняем статистику
            with open('stats.json', 'w') as f:
                json.dump(stats_data, f)
            
            await query.edit_message_text(
                f"🎉 **Поздравляю!**\n\n"
                f"Ты угадал число {secret}!\n"
                f"Количество попыток: {attempts}\n\n"
                f"Хочешь сыграть еще? Напиши /game"
            )
        else:
            hint = "больше" if number < secret else "меньше"
            # Сохраняем статистику
            with open('stats.json', 'w') as f:
                json.dump(stats_data, f)
            
            keyboard = [
                [InlineKeyboardButton("🔄 Попробовать еще", callback_data="game")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"❌ Не угадал! Число {hint} чем {number}.\n"
                f"Попыток: {attempts}\n\n"
                f"Попробуй еще раз!",
                reply_markup=reply_markup
            )
    
    elif data == "stats":
        user_stats = stats_data.get(user_id, {"games": 0, "wins": 0, "messages": 0})
        win_rate = (user_stats["wins"] / user_stats["games"] * 100) if user_stats["games"] > 0 else 0
        
        await query.edit_message_text(
            f"📊 **Твоя статистика**\n\n"
            f"🎮 Игр сыграно: {user_stats['games']}\n"
            f"🏆 Побед: {user_stats['wins']}\n"
            f"📈 Процент побед: {win_rate:.1f}%"
        )

# ============ ОБРАБОТЧИК ТЕКСТОВЫХ СООБЩЕНИЙ ============
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text
    
    # Загружаем статистику
    try:
        with open('stats.json', 'r') as f:
            stats_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        stats_data = {}
    
    if user_id not in stats_data:
        stats_data[user_id] = {"games": 0, "wins": 0, "messages": 0}
    
    stats_data[user_id]["messages"] += 1
    
    with open('stats.json', 'w') as f:
        json.dump(stats_data, f)
    
    # Ответные фразы в зависимости от сообщения
    responses = {
        "привет": "Привет! Как дела? 😊",
        "как дела": "Отлично! А у тебя? 🚀",
        "спасибо": "Пожалуйста! Всегда рад помочь! 🤝",
        "пока": "До встречи! Было приятно пообщаться! 👋",
    }
    
    response = responses.get(text.lower(), f"Ты написал: {text}")
    await update.message.reply_text(response)

# ============ ЗАПУСК БОТА ============
def main():
    app = Application.builder().token(TOKEN).build()
    
    # Добавляем команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("game", game))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("info", info))
    
    # Обработчики
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Запуск
    logger.info("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
