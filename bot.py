from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import Config, validate
from game import Game

validate()

app = Client(
    "raja_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

games = {}

# 🔹 START (DM)
@app.on_message(filters.command("start") & filters.private)
async def start(client, message: Message):
    text = f"""
👋 Welcome to Raja Mantri Bot!

🎮 Add me in a group and start game using /startgame

📢 Channel: {Config.SUPPORT_CHANNEL}
💬 Support: {Config.SUPPORT_CHAT}
"""
    await message.reply(text)


# 🔹 HELP COMMAND
@app.on_message(filters.command("help"))
async def help_cmd(client, message: Message):
    text = f"""
📖 **Raja Mantri Bot Help**

🎮 Commands:
/startgame - Start game
/join - Join game

🧠 How to Play:
• 4 players join  
• Roles assigned secretly  
• 👑 Raja revealed  
• 🧠 Mantri guesses Chor  

🏆 Win:
• Correct → Mantri wins  
• Wrong → Chor wins  

📢 Channel: {Config.SUPPORT_CHANNEL}
💬 Support: {Config.SUPPORT_CHAT}
"""
    await message.reply(text)


# 🔹 START GAME
@app.on_message(filters.command("startgame") & filters.group)
async def startgame(client, message: Message):
    chat_id = message.chat.id
    games[chat_id] = Game()
    await message.reply("🎮 Game started! Use /join to join.")


# 🔹 JOIN (WITH DM)
@app.on_message(filters.command("join") & filters.group)
async def join(client, message: Message):
    chat_id = message.chat.id
    user = message.from_user

    if chat_id not in games:
        return await message.reply("Start game first using /startgame!")

    game = games[chat_id]

    if user.id in game.players:
        return await message.reply("You already joined!")

    if game.is_full(Config.MAX_PLAYERS):
        return await message.reply("Game is full!")

    game.add_player(user.id)

    # DM confirmation
    try:
        await client.send_message(
            user.id,
            f"✅ You successfully joined the game in {message.chat.title}"
        )
    except:
        await message.reply(f"{user.mention}, please start bot in DM first!")

    await message.reply(
        f"✅ {user.mention} joined! ({len(game.players)}/{Config.MAX_PLAYERS})"
    )

    if game.is_full(Config.MAX_PLAYERS):
        await start_round(client, message, game)


# 🔹 START ROUND + BUTTONS
async def start_round(client, message, game):
    game.assign_roles()

    # Send roles in DM
    for user_id, role in game.roles.items():
        try:
            await client.send_message(user_id, f"🎭 Your role: {role}")
        except:
            pass

    raja = [u for u, r in game.roles.items() if r == "Raja"][0]
    mantri = game.mantri

    await message.reply(f"👑 Raja is [player](tg://user?id={raja})")

    # Buttons
    buttons = []
    row = []

    for uid in game.players:
        if uid != mantri:
            user = await client.get_users(uid)
            row.append(
                InlineKeyboardButton(
                    user.first_name,
                    callback_data=f"guess_{uid}"
                )
            )

        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    await message.reply(
        "🧠 Mantri, choose who is Chor:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# 🔹 HANDLE GUESS
@app.on_callback_query(filters.regex("^guess_"))
async def guess(client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id

    if chat_id not in games:
        return

    game = games[chat_id]

    if user_id != game.mantri:
        return await callback_query.answer("Only Mantri can guess!", show_alert=True)

    guessed = int(callback_query.data.split("_")[1])

    if game.check_guess(guessed):
        result = "✅ Mantri wins!"
    else:
        result = "❌ Chor wins!"

    # Reveal roles
    text = f"{result}\n\n🎭 Roles:\n"
    for uid, role in game.roles.items():
        user = await client.get_users(uid)
        text += f"{user.first_name} → {role}\n"

    await callback_query.message.edit(text)

    del games[chat_id]


app.run()