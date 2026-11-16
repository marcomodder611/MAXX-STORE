import os
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ==================================================
# RAGE ITEM PURCHASE - CONFIG
# ==================================================

BOT_TOKEN = "8766844452:AAGAsedJL3eJJ_GgORsQ2Fhd2ZoJpyB0cr0"

# Your Telegram username for payments/help
ADMIN_USERNAME = "@OwnerMaxxHackStore"
ADMIN_LINK = "t.me/OwnerMaxxHackStore"

# Menu image URL - replace this with your image direct URL
MENU_PHOTO_URL = "https://i.ibb.co/Y4m3zRW1/file-00000000cdd882118be895db8d9660ec.png"

# Your numeric Telegram Owner ID
OWNER_ID = 5517571292

DB_FILE = "rage_item_purchase.db"


# ==================================================
# DATABASE
# ==================================================

db = sqlite3.connect(DB_FILE, check_same_thread=False)

db.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    coins INTEGER DEFAULT 0
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    file_id TEXT NOT NULL,
    file_type TEXT NOT NULL
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    price INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

db.commit()


# ==================================================
# DATABASE FUNCTIONS
# ==================================================

def save_user(user):
    db.execute("""
        INSERT INTO users(user_id, username, first_name)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name
    """, (
        user.id,
        user.username or "",
        user.first_name or ""
    ))
    db.commit()


def get_balance(user_id):
    row = db.execute(
        "SELECT coins FROM users WHERE user_id=?",
        (user_id,)
    ).fetchone()

    return row[0] if row else 0


def owner(user_id):
    return user_id == OWNER_ID


# ==================================================
# START
# ==================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    save_user(user)

    caption = (
        "╔══════════════════════════╗\n"
        "      ⚡ MAXX HACK STORE ⚡\n"
        "╚══════════════════════════╝\n\n"
        f"👤 Welcome, {user.first_name}!\n\n"
        "▸ PREMIUM DIGITAL ITEM STORE\n"
        "▸ SECURE COIN SYSTEM\n"
        "▸ INSTANT ITEM DELIVERY\n"
        "▸ FAST & SIMPLE PURCHASES\n\n"
        "💻 SYSTEM STATUS: ONLINE\n"
        "🔐 ACCESS: AUTHORIZED\n\n"
        "👇 Select an option below:"
    )

    if MENU_PHOTO_URL != "PASTE_YOUR_MENU_PHOTO_URL_HERE":
        try:
            await update.message.reply_photo(
                photo=MENU_PHOTO_URL,
                caption=caption,
                reply_markup=main_menu(user.id)
            )
            return
        except Exception as e:
            print("MENU PHOTO ERROR:", e)

    await update.message.reply_text(
        caption,
        reply_markup=main_menu(user.id)
    )


# ==================================================
# MAIN MENU
# ==================================================

def main_menu(user_id):

    keyboard = [
        [
            InlineKeyboardButton(
                "🛒 ALL ITEMS",
                callback_data="items"
            )
        ],
        [
            InlineKeyboardButton(
                "🪙 MY BALANCE",
                callback_data="balance"
            )
        ],
        [
            InlineKeyboardButton(
                "💰 BUY COINS",
                url=ADMIN_LINK
            )
        ],
        [
            InlineKeyboardButton(
                "👨‍💻 ADMIN CONTACT",
                url=ADMIN_LINK
            )
        ]
    ]

    if owner(user_id):
        keyboard.append([
            InlineKeyboardButton(
                "👑 ADMIN PANEL",
                callback_data="admin"
            )
        ])

    return InlineKeyboardMarkup(keyboard)


# ==================================================
# SHOW ALL ITEMS
# ==================================================

async def show_items(message):

    rows = db.execute("""
        SELECT id, name, price
        FROM items
        ORDER BY id DESC
    """).fetchall()

    if not rows:

        await message.reply_text(
            "🛒 *ALL ITEMS*\n\n"
            "❌ No items are available right now.",
            parse_mode="Markdown"
        )

        return

    buttons = []

    for item_id, name, price in rows:

        buttons.append([
            InlineKeyboardButton(
                f"📦 {name} | 🪙 {price}",
                callback_data=f"item:{item_id}"
            )
        ])

    await message.reply_text(
        "🛒 *MAXX HACK STORE*\n\n"
        "👇 Select an item:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ==================================================
# CALLBACK HANDLER
# ==================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user
    user_id = user.id

    save_user(user)

    data = query.data

    # ----------------------------------------------
    # ALL ITEMS
    # ----------------------------------------------

    if data == "items":

        await show_items(query.message)
        return

    # ----------------------------------------------
    # BALANCE
    # ----------------------------------------------

    if data == "balance":

        balance = get_balance(user_id)

        await query.message.reply_text(
            "🪙 *YOUR BALANCE*\n\n"
            f"💰 Available Coins: `{balance}` 🪙\n\n"
            "💡 To purchase coins, "
            "click BUY COINS.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "💰 BUY COINS",
                        url=ADMIN_LINK
                    )
                ]
            ])
        )

        return

    # ----------------------------------------------
    # ADMIN PANEL
    # ----------------------------------------------

    if data == "admin":

        if not owner(user_id):

            await query.message.reply_text(
                "❌ ACCESS DENIED."
            )

            return

        await query.message.reply_text(
            "👑 *MAXX HACK STORE ADMIN PANEL*\n\n"
            "📦 `/addnewitem` — Add a new item\n"
            "📋 `/items` — List all items\n"
            "🗑 `/removeitem ID` — Remove an item\n"
            "✏️ `/edititem ID PRICE` — Edit item price\n\n"
            "🪙 `/addcoins USER_ID AMOUNT`\n"
            "➖ `/removecoins USER_ID AMOUNT`\n\n"
            "👥 `/users` — Total users\n"
            "📊 `/stats` — Statistics\n"
            "📦 `/orders` — Total orders",
            parse_mode="Markdown"
        )

        return

    # ----------------------------------------------
    # ITEM DETAILS
    # ----------------------------------------------

    if data.startswith("item:"):

        item_id = int(data.split(":")[1])

        row = db.execute("""
            SELECT id, name, price
            FROM items
            WHERE id=?
        """, (item_id,)).fetchone()

        if not row:

            await query.message.reply_text(
                "❌ Item not found."
            )

            return

        item_id, name, price = row

        balance = get_balance(user_id)

        keyboard = [
            [
                InlineKeyboardButton(
                    f"🛒 BUY NOW — {price} 🪙",
                    callback_data=f"buy:{item_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 SARA ITEMS",
                    callback_data="items"
                )
            ]
        ]

        await query.message.reply_text(
            f"📦 *{name}*\n\n"
            f"🪙 Price: `{price}` coins\n"
            f"💰 Your Balance: `{balance}` coins\n\n"
            "👇 Press BUY NOW to purchase.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return

    # ----------------------------------------------
    # PURCHASE
    # ----------------------------------------------

    if data.startswith("buy:"):

        item_id = int(data.split(":")[1])

        row = db.execute("""
            SELECT id, name, price, file_id, file_type
            FROM items
            WHERE id=?
        """, (item_id,)).fetchone()

        if not row:

            await query.message.reply_text(
                "❌ Item is no longer available."
            )

            return

        item_id, name, price, file_id, file_type = row

        balance = get_balance(user_id)

        if balance < price:

            await query.message.reply_text(
                "❌ *INSUFFICIENT COINS*\n\n"
                f"🪙 Required: `{price}`\n"
                f"💰 Your Balance: `{balance}`\n\n"
                "💰 Contact the Admin to purchase coins.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "👨‍💻 BUY COINS",
                            url=ADMIN_LINK
                        )
                    ]
                ])
            )

            return

        # Deduct coins
        db.execute("""
            UPDATE users
            SET coins = coins - ?
            WHERE user_id=?
        """, (price, user_id))

        # Save order
        db.execute("""
            INSERT INTO orders(user_id, item_id, price)
            VALUES (?, ?, ?)
        """, (user_id, item_id, price))

        db.commit()

        # Deliver item
        try:

            if file_type == "document":

                await query.message.reply_document(
                    document=file_id,
                    caption=(
                        "✅ *PURCHASE SUCCESSFUL!*\n\n"
                        f"📦 {name}\n"
                        f"🪙 Spent: {price}\n"
                        f"💰 Remaining: {get_balance(user_id)}"
                    ),
                    parse_mode="Markdown"
                )

            elif file_type == "photo":

                await query.message.reply_photo(
                    photo=file_id,
                    caption=(
                        "✅ *PURCHASE SUCCESSFUL!*\n\n"
                        f"📦 {name}\n"
                        f"🪙 Spent: {price}\n"
                        f"💰 Remaining: {get_balance(user_id)}"
                    ),
                    parse_mode="Markdown"
                )

            elif file_type == "video":

                await query.message.reply_video(
                    video=file_id,
                    caption=(
                        "✅ *PURCHASE SUCCESSFUL!*\n\n"
                        f"📦 {name}\n"
                        f"🪙 Spent: {price}\n"
                        f"💰 Remaining: {get_balance(user_id)}"
                    ),
                    parse_mode="Markdown"
                )

        except Exception as e:

            print("DELIVERY ERROR:", e)

            # Refund if delivery fails
            db.execute("""
                UPDATE users
                SET coins = coins + ?
                WHERE user_id=?
            """, (price, user_id))

            db.commit()

            await query.message.reply_text(
                "❌ Item delivery failed.\n"
                "Your coins have been refunded."
            )


# ==================================================
# MY COINS
# ==================================================

async def mycoins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user)
    balance = get_balance(user.id)

    await update.message.reply_text(
        "🪙 *YOUR BALANCE*\n\n"
        f"💰 Available Coins: `{balance}` 🪙",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "💰 BUY COINS",
                    url=ADMIN_LINK
                )
            ]
        ])
    )


# ==================================================
# ADD NEW ITEM
# ==================================================

async def addnewitem(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not owner(update.effective_user.id):

        await update.message.reply_text(
            "❌ ACCESS DENIED."
        )

        return

    context.user_data.clear()
    context.user_data["adding_item"] = True
    context.user_data["step"] = "file"
    context.user_data["item"] = {}

    await update.message.reply_text(
        "📦 *ADD NEW ITEM*\n\n"
        "Step 1/3\n\n"
        "📤 Send the product file, photo, video, or document.",
        parse_mode="Markdown"
    )


# ==================================================
# RECEIVE PRODUCT FILE
# ==================================================

async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not owner(update.effective_user.id):
        return

    if not context.user_data.get("adding_item"):
        return

    if context.user_data.get("step") != "file":
        return

    item = context.user_data["item"]

    if update.message.document:

        item["file_id"] = update.message.document.file_id
        item["file_type"] = "document"

    elif update.message.photo:

        item["file_id"] = update.message.photo[-1].file_id
        item["file_type"] = "photo"

    elif update.message.video:

        item["file_id"] = update.message.video.file_id
        item["file_type"] = "video"

    else:
        return

    context.user_data["step"] = "name"

    await update.message.reply_text(
        "✅ File received.\n\n"
        "Step 2/3\n"
        "📦 Now send the item *name*.",
        parse_mode="Markdown"
    )


# ==================================================
# RECEIVE NAME / PRICE
# ==================================================

async def receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not owner(update.effective_user.id):
        return

    if not context.user_data.get("adding_item"):
        return

    step = context.user_data.get("step")
    item = context.user_data["item"]

    # NAME
    if step == "name":

        item["name"] = update.message.text.strip()

        context.user_data["step"] = "price"

        await update.message.reply_text(
            "Step 3/3\n\n"
            "🪙 Send the item price in coins.\n\n"
            "Example:\n"
            "`500`",
            parse_mode="Markdown"
        )

        return

    # PRICE
    if step == "price":

        try:

            price = int(update.message.text.strip())

            if price <= 0:
                raise ValueError

            item["price"] = price

            db.execute("""
                INSERT INTO items(
                    name,
                    price,
                    file_id,
                    file_type
                )
                VALUES (?, ?, ?, ?)
            """, (
                item["name"],
                item["price"],
                item["file_id"],
                item["file_type"]
            ))

            db.commit()

            item_id = db.execute(
                "SELECT last_insert_rowid()"
            ).fetchone()[0]

            await update.message.reply_text(
                "✅ *ITEM ADDED SUCCESSFULLY!*\n\n"
                f"🆔 ID: `{item_id}`\n"
                f"📦 Name: {item['name']}\n"
                f"🪙 Price: `{price}` coins\n\n"
                "🛒 This item is now available in ALL ITEMS.",
                parse_mode="Markdown"
            )

            context.user_data.clear()

        except ValueError:

            await update.message.reply_text(
                "❌ Price must be a number.\n"
                "Example: `500`"
            )


# ==================================================
# ADD COINS
# ==================================================

async def addcoins(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not owner(update.effective_user.id):

        await update.message.reply_text(
            "❌ ACCESS DENIED."
        )

        return

    if len(context.args) != 2:

        await update.message.reply_text(
            "`/addcoins USER_ID AMOUNT`",
            parse_mode="Markdown"
        )

        return

    try:

        user_id = int(context.args[0])
        amount = int(context.args[1])

        if amount <= 0:
            raise ValueError

        db.execute("""
            INSERT OR IGNORE INTO users(user_id, coins)
            VALUES (?, 0)
        """, (user_id,))

        db.execute("""
            UPDATE users
            SET coins = coins + ?
            WHERE user_id=?
        """, (amount, user_id))

        db.commit()

        await update.message.reply_text(
            "✅ *COINS ADDED*\n\n"
            f"👤 User ID: `{user_id}`\n"
            f"🪙 Added: `{amount}`\n"
            f"💰 New Balance: `{get_balance(user_id)}`",
            parse_mode="Markdown"
        )

    except ValueError:

        await update.message.reply_text(
            "❌ Invalid User ID or amount."
        )


# ==================================================
# REMOVE COINS
# ==================================================

async def removecoins(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not owner(update.effective_user.id):

        await update.message.reply_text(
            "❌ ACCESS DENIED."
        )

        return

    if len(context.args) != 2:

        await update.message.reply_text(
            "`/removecoins USER_ID AMOUNT`",
            parse_mode="Markdown"
        )

        return

    try:

        user_id = int(context.args[0])
        amount = int(context.args[1])

        if amount <= 0:
            raise ValueError

        balance = get_balance(user_id)

        if balance < amount:

            await update.message.reply_text(
                "❌ The user does not have enough coins."
            )

            return

        db.execute("""
            UPDATE users
            SET coins = coins - ?
            WHERE user_id=?
        """, (amount, user_id))

        db.commit()

        await update.message.reply_text(
            "✅ *COINS REMOVED*\n\n"
            f"👤 User ID: `{user_id}`\n"
            f"🪙 Removed: `{amount}`\n"
            f"💰 New Balance: `{get_balance(user_id)}`",
            parse_mode="Markdown"
        )

    except ValueError:

        await update.message.reply_text(
            "❌ Invalid User ID or amount."
    )


# ==================================================
# REMOVE ITEM
# ==================================================

async def removeitem(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not owner(update.effective_user.id):

        await update.message.reply_text(
            "❌ ACCESS DENIED."
        )

        return

    if len(context.args) != 1:

        await update.message.reply_text(
            "`/removeitem ITEM_ID`",
            parse_mode="Markdown"
        )

        return

    try:

        item_id = int(context.args[0])

        row = db.execute(
            "SELECT name FROM items WHERE id=?",
            (item_id,)
        ).fetchone()

        if not row:

            await update.message.reply_text(
                "❌ Item not found."
            )

            return

        db.execute(
            "DELETE FROM items WHERE id=?",
            (item_id,)
        )

        db.commit()

        await update.message.reply_text(
            f"🗑️ Item `{item_id}` has been deleted.",
            parse_mode="Markdown"
        )

    except ValueError:

        await update.message.reply_text(
            "❌ Invalid Item ID."
        )


# ==================================================
# EDIT ITEM PRICE
# ==================================================

async def edititem(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not owner(update.effective_user.id):

        await update.message.reply_text(
            "❌ ACCESS DENIED."
        )

        return

    if len(context.args) != 2:

        await update.message.reply_text(
            "`/edititem ITEM_ID NEW_PRICE`",
            parse_mode="Markdown"
        )

        return

    try:

        item_id = int(context.args[0])
        new_price = int(context.args[1])

        if new_price <= 0:
            raise ValueError

        row = db.execute(
            "SELECT name FROM items WHERE id=?",
            (item_id,)
        ).fetchone()

        if not row:

            await update.message.reply_text(
                "❌ Item not found."
            )

            return

        db.execute("""
            UPDATE items
            SET price=?
            WHERE id=?
        """, (new_price, item_id))

        db.commit()

        await update.message.reply_text(
            "✅ *ITEM UPDATED*\n\n"
            f"📦 {row[0]}\n"
            f"🪙 New Price: `{new_price}`",
            parse_mode="Markdown"
        )

    except ValueError:

        await update.message.reply_text(
            "❌ Invalid ID or price."
        )


# ==================================================
# ITEMS ADMIN LIST
# ==================================================

async def admin_items(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not owner(update.effective_user.id):

        await update.message.reply_text(
            "❌ ACCESS DENIED."
        )

        return

    rows = db.execute("""
        SELECT id, name, price
        FROM items
        ORDER BY id DESC
    """).fetchall()

    if not rows:

        await update.message.reply_text(
            "📦 No items found."
        )

        return

    text = "📦 *ALL ITEMS*\n\n"

    for item_id, name, price in rows:

        text += (
            f"🆔 `{item_id}` | "
            f"{name} | 🪙 `{price}`\n"
        )

    await update.message.reply_text(
        text,
        parse_mode="Markdown"
    )


# ==================================================
# USERS
# ==================================================

async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not owner(update.effective_user.id):

        await update.message.reply_text(
            "❌ ACCESS DENIED."
        )

        return

    total = db.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    await update.message.reply_text(
        f"👥 *TOTAL USERS*\n\n`{total}`",
        parse_mode="Markdown"
    )


# ==================================================
# ORDERS
# ==================================================

async def orders(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not owner(update.effective_user.id):

        await update.message.reply_text(
            "❌ ACCESS DENIED."
        )

        return

    total = db.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()[0]

    await update.message.reply_text(
        f"📦 *TOTAL ORDERS*\n\n`{total}`",
        parse_mode="Markdown"
    )


# ==================================================
# STATS
# ==================================================

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not owner(update.effective_user.id):

        await update.message.reply_text(
            "❌ ACCESS DENIED."
        )

        return

    total_users = db.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    total_items = db.execute(
        "SELECT COUNT(*) FROM items"
    ).fetchone()[0]

    total_orders = db.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()[0]

    total_coins = db.execute(
        "SELECT COALESCE(SUM(coins), 0) FROM users"
    ).fetchone()[0]

    await update.message.reply_text(
        "📊 *MAXX HACK STORE STATS*\n\n"
        f"👥 Users: `{total_users}`\n"
        f"📦 Items: `{total_items}`\n"
        f"🛒 Orders: `{total_orders}`\n"
        f"🪙 Coins: `{total_coins}`",
        parse_mode="Markdown"
    )


# ==================================================
# MAIN
# ==================================================

def main():

    if BOT_TOKEN == "YOUR_BOT_TOKEN":

        print("❌ BOT_TOKEN set karo.")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mycoins", mycoins))

    # Owner commands
    app.add_handler(CommandHandler("addnewitem", addnewitem))
    app.add_handler(CommandHandler("addcoins", addcoins))
    app.add_handler(CommandHandler("removecoins", removecoins))
    app.add_handler(CommandHandler("removeitem", removeitem))
    app.add_handler(CommandHandler("edititem", edititem))
    app.add_handler(CommandHandler("items", admin_items))
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CommandHandler("orders", orders))
    app.add_handler(CommandHandler("stats", stats))

    # Buttons
    app.add_handler(
        CallbackQueryHandler(callback_handler)
    )

    # Product files
    app.add_handler(
        MessageHandler(
            filters.Document.ALL |
            filters.PHOTO |
            filters.VIDEO,
            receive_file
        )
    )

    # Product name / price
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            receive_text
        )
    )

    print("🔥 MAXX HACK STORE BOT RUNNING...")

    app.run_polling()


if __name__ == "__main__":
    main()
