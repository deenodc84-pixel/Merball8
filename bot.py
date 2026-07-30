import os
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token from environment variable
TOKEN = os.environ.get('BOT_TOKEN')

# Sports data
SPORTS = ['⚽ Football', '🏀 Basketball', '🎾 Tennis', '🏏 Cricket', '🏈 American Football']

TRIVIA_QUESTIONS = [
    {'question': 'Which country has won the most FIFA World Cups?', 'answer': 'Brazil (5 times)'},
    {'question': 'Who holds the NBA record for most points in a single game?', 'answer': 'Wilt Chamberlain (100 points)'},
    {'question': 'Which tennis player has won the most Grand Slam titles?', 'answer': 'Novak Djokovic (24)'},
    {'question': 'In which sport do you use a shuttlecock?', 'answer': 'Badminton'},
    {'question': 'What is the fastest recorded tennis serve speed?', 'answer': '163.7 mph (Sam Groth)'},
]

FACTS = [
    'The oldest known sport is wrestling, dating back to 15,000 years ago.',
    'The first Olympic Games were held in 776 BC in Greece.',
    'A standard football match lasts 90 minutes with 15-minute halftime.',
    'The fastest red card in football history was 2 seconds.',
    'Basketball was invented by Dr. James Naismith in 1891.',
]

QUIZ_QUESTIONS = [
    {'q': 'How many players are on a football team?', 'ops': ['9', '10', '11', '12'], 'a': 2},
    {'q': 'What is the diameter of a basketball hoop?', 'ops': ['18 inches', '20 inches', '22 inches', '24 inches'], 'a': 0},
    {'q': 'How many Grand Slam tournaments are there in tennis?', 'ops': ['2', '3', '4', '5'], 'a': 2},
    {'q': 'What is the length of a cricket pitch?', 'ops': ['18m', '20m', '22m', '24m'], 'a': 2},
    {'q': 'How many points is a touchdown worth in American football?', 'ops': ['4', '6', '7', '8'], 'a': 1},
]

# User session storage
user_quizzes = {}

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when /start is issued."""
    keyboard = [
        [InlineKeyboardButton("📝 Trivia", callback_data='trivia'),
         InlineKeyboardButton("📊 Quiz", callback_data='quiz')],
        [InlineKeyboardButton("📖 Facts", callback_data='fact'),
         InlineKeyboardButton("🏆 Highlights", callback_data='highlight')],
        [InlineKeyboardButton("📈 Stats", callback_data='stats'),
         InlineKeyboardButton("📚 Sports List", callback_data='sports')],
        [InlineKeyboardButton("ℹ️ About", callback_data='about')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🏆 *Welcome to SportsZone!* ⚽🏀🎾\n\n"
        "Your ultimate sports companion for daily trivia, fun facts, and "
        "interactive quizzes! Test your sports knowledge across Football, "
        "Basketball, Tennis, Cricket, and more.\n\n"
        "👉 *Choose an option below:*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when /help is issued."""
    help_text = (
        "📋 *Available Commands:*\n\n"
        "/start - Welcome & main menu\n"
        "/trivia - Random sports trivia\n"
        "/fact - Fun sports fact\n"
        "/quiz - 5-question sports quiz\n"
        "/highlight - Match highlight summary\n"
        "/stats - Player statistics\n"
        "/sports - Sports categories\n"
        "/daily - Today's featured content\n"
        "/about - About this bot\n"
        "/help - Show this help"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """About the bot."""
    about_text = (
        "🤖 *About SportsZone Bot*\n\n"
        "SportsZone is a non-commercial bot created for sports enthusiasts to "
        "learn interesting facts, test their knowledge, and enjoy sports content "
        "in a fun, interactive way.\n\n"
        "📌 *Bot Info:*\n"
        "• Follows Telegram TOS\n"
        "• No data collection\n"
        "• No spam or ads\n"
        "• Educational & entertainment only\n\n"
        "Made with ❤️ for the Telegram community"
    )
    await update.message.reply_text(about_text, parse_mode='Markdown')

async def trivia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a random trivia question."""
    q = random.choice(TRIVIA_QUESTIONS)
    await update.message.reply_text(
        f"🧠 *Sports Trivia*\n\n"
        f"❓ {q['question']}\n\n"
        f"💡 *Answer:* `{q['answer']}`",
        parse_mode='Markdown'
    )

async def fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a random sports fact."""
    fact_text = random.choice(FACTS)
    await update.message.reply_text(
        f"📖 *Did You Know?*\n\n{fact_text}",
        parse_mode='Markdown'
    )

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start a quiz."""
    user_id = update.effective_user.id
    questions = random.sample(QUIZ_QUESTIONS, min(5, len(QUIZ_QUESTIONS)))
    user_quizzes[user_id] = {
        'questions': questions,
        'current': 0,
        'score': 0
    }
    await send_question(update, context, user_id)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Send the current quiz question."""
    quiz_data = user_quizzes.get(user_id)
    if not quiz_data:
        return
    
    current = quiz_data['current']
    questions = quiz_data['questions']
    
    if current >= len(questions):
        await update.message.reply_text(
            f"🎉 *Quiz Complete!*\n\n"
            f"Your Score: *{quiz_data['score']}/{len(questions)}*\n\n"
            f"Use /quiz to try again!",
            parse_mode='Markdown'
        )
        del user_quizzes[user_id]
        return
    
    q_data = questions[current]
    keyboard = []
    options = ['A', 'B', 'C', 'D']
    for i, option in enumerate(q_data['ops']):
        keyboard.append([InlineKeyboardButton(f"{options[i]}. {option}", callback_data=f'quiz_{i}')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"📊 *Question {current+1}/{len(questions)}*\n\n"
        f"{q_data['q']}\n\n"
        f"Choose your answer:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def highlight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a match highlight summary."""
    highlights = [
        "⚽ *Match Highlight:* Liverpool 3-1 Arsenal\n\n"
        "🔴 Liverpool dominated with 65% possession.\n"
        "⚽ Goals: Salah (23'), Núñez (45+2'), Díaz (67')\n"
        "🎯 Arsenal scored through Odegaard (34')",
        
        "🏀 *NBA Highlight:* Lakers 112-107 Warriors\n\n"
        "🌟 LeBron James: 32 points, 10 rebounds\n"
        "🎯 Curry scored 28 points with 6 threes\n"
        "📊 Lakers extend winning streak to 5 games",
        
        "🎾 *Tennis Highlight:* Djokovic vs Alcaraz\n\n"
        "🏆 Grand Slam Quarterfinal\n"
        "📊 Djokovic wins 6-4, 7-6, 4-6, 6-3\n"
        "⭐ Alcaraz shows promising form"
    ]
    await update.message.reply_text(random.choice(highlights), parse_mode='Markdown')

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show player stats."""
    stats_text = (
        "🏆 *Top Sports Stats*\n\n"
        "⚽ *Football:*\n"
        "• Most Goals: Cristiano Ronaldo (873)\n"
        "• Most Assists: Lionel Messi (397)\n\n"
        "🏀 *Basketball:*\n"
        "• Most Points: LeBron James (38,652)\n"
        "• Most Assists: John Stockton (15,806)\n\n"
        "🎾 *Tennis:*\n"
        "• Most Grand Slams: Novak Djokovic (24)\n"
        "• Most Weeks at #1: Novak Djokovic (407)\n\n"
        "🏏 *Cricket:*\n"
        "• Most Runs: Sachin Tendulkar (34,357)\n"
        "• Most Wickets: Muttiah Muralitharan (1,347)"
    )
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def sports_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List available sports."""
    sports_text = "📚 *Available Sports Categories*\n\n"
    for sport in SPORTS:
        sports_text += f"• {sport}\n"
    sports_text += "\nMore sports coming soon! 🚀"
    await update.message.reply_text(sports_text, parse_mode='Markdown')

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send daily featured content."""
    daily_content = (
        "📅 *Today's Featured Content*\n\n"
        "🏆 *Sport of the Day:* Football\n\n"
        "📖 *Fact:* The first official football match was played in 1863.\n\n"
        "❓ *Trivia:* Which country has the most World Cup wins?\n"
        "Answer: Brazil (5 wins)\n\n"
        "🔗 Use /trivia for more questions!"
    )
    await update.message.reply_text(daily_content, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    if callback_data == 'trivia':
        q = random.choice(TRIVIA_QUESTIONS)
        await query.edit_message_text(
            f"🧠 *Sports Trivia*\n\n"
            f"❓ {q['question']}\n\n"
            f"💡 *Answer:* `{q['answer']}`",
            parse_mode='Markdown'
        )
    elif callback_data == 'quiz':
        user_id = update.effective_user.id
        questions = random.sample(QUIZ_QUESTIONS, min(5, len(QUIZ_QUESTIONS)))
        user_quizzes[user_id] = {
            'questions': questions,
            'current': 0,
            'score': 0
        }
        current = user_quizzes[user_id]['current']
        q_data = questions[current]
        
        keyboard = []
        options = ['A', 'B', 'C', 'D']
        for i, option in enumerate(q_data['ops']):
            keyboard.append([InlineKeyboardButton(f"{options[i]}. {option}", callback_data=f'quiz_{i}')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"📊 *Question {current+1}/{len(questions)}*\n\n"
            f"{q_data['q']}\n\n"
            f"Choose your answer:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif callback_data == 'fact':
        fact_text = random.choice(FACTS)
        await query.edit_message_text(
            f"📖 *Did You Know?*\n\n{fact_text}",
            parse_mode='Markdown'
        )
    elif callback_data == 'highlight':
        highlight_text = random.choice([
            "⚽ *Match Highlight:* Liverpool 3-1 Arsenal\n\n"
            "🔴 Liverpool dominated with 65% possession.\n"
            "⚽ Goals: Salah (23'), Núñez (45+2'), Díaz (67')\n"
            "🎯 Arsenal scored through Odegaard (34')",
            
            "🏀 *NBA Highlight:* Lakers 112-107 Warriors\n\n"
            "🌟 LeBron James: 32 points, 10 rebounds\n"
            "🎯 Curry scored 28 points with 6 threes\n"
            "📊 Lakers extend winning streak to 5 games",
        ])
        await query.edit_message_text(highlight_text, parse_mode='Markdown')
    elif callback_data == 'stats':
        stats_text = (
            "🏆 *Top Sports Stats*\n\n"
            "⚽ *Football:*\n"
            "• Most Goals: Cristiano Ronaldo (873)\n"
            "• Most Assists: Lionel Messi (397)\n\n"
            "🏀 *Basketball:*\n"
            "• Most Points: LeBron James (38,652)\n"
            "• Most Assists: John Stockton (15,806)"
        )
        await query.edit_message_text(stats_text, parse_mode='Markdown')
    elif callback_data == 'sports':
        sports_text = "📚 *Available Sports Categories*\n\n"
        for sport in SPORTS:
            sports_text += f"• {sport}\n"
        sports_text += "\nMore sports coming soon! 🚀"
        await query.edit_message_text(sports_text, parse_mode='Markdown')
    elif callback_data == 'about':
        about_text = (
            "🤖 *About SportsZone Bot*\n\n"
            "SportsZone is a non-commercial bot created for sports enthusiasts.\n\n"
            "📌 *Bot Info:*\n"
            "• Follows Telegram TOS\n"
            "• No data collection\n"
            "• No spam or ads\n"
            "• Educational & entertainment only\n\n"
            "Made with ❤️ for the Telegram community"
        )
        await query.edit_message_text(about_text, parse_mode='Markdown')
    elif callback_data.startswith('quiz_'):
        # Handle quiz answer
        user_id = update.effective_user.id
        quiz_data = user_quizzes.get(user_id)
        if not quiz_data:
            await query.edit_message_text("Quiz expired! Use /quiz to start a new one.")
            return
        
        selected = int(callback_data.split('_')[1])
        current = quiz_data['current']
        q_data = quiz_data['questions'][current]
        
        if selected == q_data['a']:
            quiz_data['score'] += 1
            result = "✅ Correct! Well done! 🎉"
        else:
            correct_answer = q_data['ops'][q_data['a']]
            result = f"❌ Wrong! The correct answer was: {correct_answer}"
        
        quiz_data['current'] += 1
        
        if quiz_data['current'] >= len(quiz_data['questions']):
            total = len(quiz_data['questions'])
            await query.edit_message_text(
                f"🎉 *Quiz Complete!*\n\n"
                f"Your Score: *{quiz_data['score']}/{total}*\n\n"
                f"Use /quiz to try again!",
                parse_mode='Markdown'
            )
            del user_quizzes[user_id]
        else:
            next_q = quiz_data['current']
            next_data = quiz_data['questions'][next_q]
            keyboard = []
            options = ['A', 'B', 'C', 'D']
            for i, option in enumerate(next_data['ops']):
                keyboard.append([InlineKeyboardButton(f"{options[i]}. {option}", callback_data=f'quiz_{i}')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"{result}\n\n"
                f"📊 *Question {next_q+1}/{len(quiz_data['questions'])}*\n\n"
                f"{next_data['q']}\n\n"
                f"Choose your answer:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("trivia", trivia))
    application.add_handler(CommandHandler("fact", fact))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CommandHandler("highlight", highlight))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("sports", sports_list))
    application.add_handler(CommandHandler("daily", daily))
    
    # Register callback query handler for buttons
    application.add_handler(CallbackQueryHandler(button_callback))

    # Start the Bot
    print("🤖 SportsZone Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
