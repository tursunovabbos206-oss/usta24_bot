import os
import sqlite3
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 5930225049
DB_NAME = "usta24.db"

SERVICES = [
    "🔧 Santexnik",
    "⚡ Elektrik",
    "❄️ Konditsioner",
    "💻 Kompyuter",
    "🏗 Qurilish",
    "🚗 Avto xizmat",
    "🛠 Boshqa",
]


# =========================
# DATABASE
# =========================

def db():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS masters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        name TEXT,
        service TEXT,
        region TEXT,
        phone TEXT,
        price TEXT,
        status TEXT DEFAULT 'pending',
        completed_orders INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        master_id INTEGER,
        description TEXT,
        budget TEXT,
        location TEXT,
        status TEXT DEFAULT 'new'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        master_id INTEGER,
        customer_id INTEGER,
        rating INTEGER,
        UNIQUE(order_id)
    )
    """)

    conn.commit()
    conn.close()


# =========================
# MAIN MENU
# =========================

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("🔎 USTA TOPISH", callback_data="find_master"),
            InlineKeyboardButton("📋 BUYURTMA BERISH", callback_data="choose_service_order"),
        ],
        [
            InlineKeyboardButton("🛠 USTA BO‘LISH", callback_data="become_master"),
            InlineKeyboardButton("📂 XIZMATLAR", callback_data="services"),
        ],
        [
            InlineKeyboardButton("👤 PROFIL", callback_data="profile"),
            InlineKeyboardButton("📦 BUYURTMALARIM", callback_data="my_orders"),
        ],
        [
            InlineKeyboardButton("ℹ️ USTA24 HAQIDA", callback_data="about"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def services_menu(prefix="service"):
    keyboard = []

    for i, service in enumerate(SERVICES):
        keyboard.append([
            InlineKeyboardButton(
                service,
                callback_data=f"{prefix}:{i}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton("⬅️ Orqaga", callback_data="back")
    ])

    return InlineKeyboardMarkup(keyboard)


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    text = """
🔧 USTA24

Assalomu alaykum!

USTA24 — kerakli ustani tez topish va xizmat ko‘rsatish uchun qulay platforma.

🔎 Usta toping
📋 Buyurtma bering
🛠 Usta sifatida ro‘yxatdan o‘ting
⭐ Reytinglarni ko‘ring

Kerakli bo‘limni tanlang:
"""

    await update.message.reply_text(
        text,
        reply_markup=main_menu()
    )


# =========================
# SHOW MASTERS
# =========================

async def show_masters(update, context, service=None):

    conn = db()
    cur = conn.cursor()

    if service:
        cur.execute("""
        SELECT id, name, service, region, price, completed_orders
        FROM masters
        WHERE status='approved' AND service=?
        """, (service,))
    else:
        cur.execute("""
        SELECT id, name, service, region, price, completed_orders
        FROM masters
        WHERE status='approved'
        """)

    masters = cur.fetchall()
    conn.close()

    if not masters:
        text = "😔 Hozircha bu xizmat bo‘yicha tasdiqlangan usta mavjud emas."

        keyboard = [[
            InlineKeyboardButton("⬅️ Orqaga", callback_data="back")
        ]]

        await update.effective_message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    for master in masters:

        master_id, name, srv, region, price, completed = master

        conn = db()
        cur = conn.cursor()

        cur.execute("""
        SELECT AVG(rating)
        FROM reviews
        WHERE master_id=?
        """, (master_id,))

        rating = cur.fetchone()[0]
        conn.close()

        if rating:
            rating_text = f"{rating:.1f}/5 ⭐"
        else:
            rating_text = "Yangi ⭐"

        text = f"""
👨‍🔧 {name}
✅ Tasdiqlangan usta

🛠 Xizmat: {srv}
📍 Hudud: {region}
💰 Narx: {price}

⭐ Reyting: {rating_text}
📦 Tugallangan ishlar: {completed}
"""

        keyboard = [[
            InlineKeyboardButton(
                "👤 PROFIL",
                callback_data=f"master:{master_id}"
            )
        ]]

        await update.effective_message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


# =========================
# MASTER PROFILE
# =========================

async def show_master_profile(update, context, master_id):

    conn = db()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, name, service, region, phone, price, completed_orders
    FROM masters
    WHERE id=? AND status='approved'
    """, (master_id,))

    master = cur.fetchone()

    cur.execute("""
    SELECT AVG(rating)
    FROM reviews
    WHERE master_id=?
    """, (master_id,))

    rating = cur.fetchone()[0]

    conn.close()

    if not master:
        await update.effective_message.reply_text(
            "❌ Usta topilmadi."
        )
        return

    (
        mid,
        name,
        service,
        region,
        phone,
        price,
        completed
    ) = master

    rating_text = f"{rating:.1f}/5 ⭐" if rating else "Hali baholanmagan"

    text = f"""
👨‍🔧 USTA PROFILI

👤 Ism: {name}
✅ Tasdiqlangan usta

🛠 Xizmat: {service}
📍 Hudud: {region}
💰 Narx: {price}

⭐ Reyting: {rating_text}
📦 Tugallangan ishlar: {completed}
"""

    keyboard = [
        [
            InlineKeyboardButton(
                "📋 BUYURTMA BERISH",
                callback_data=f"order_master:{mid}"
            )
        ],
        [
            InlineKeyboardButton(
                "📞 TELEFON",
                callback_data=f"phone:{mid}"
            )
        ],
        [
            InlineKeyboardButton(
                "⭐ BAHOLAR",
                callback_data=f"reviews:{mid}"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Orqaga",
                callback_data="find_master"
            )
        ],
    ]

    await update.effective_message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# START ORDER
# =========================

async def start_order(update, context, master_id):

    context.user_data["order_master"] = master_id
    context.user_data["order_step"] = "description"

    await update.effective_message.reply_text(
        """
📋 YANGI BUYURTMA

Muammoingizni batafsil yozing.

Masalan:
"Uyda kran suv o'tkazmoqda."
"Kir yuvish mashinasi ishlamayapti."
"Konditsioner sovutmayapti."
"""
    )


# =========================
# CREATE ORDER
# =========================

async def create_order(update, context):

    master_id = context.user_data.get("order_master")
    description = context.user_data.get("order_description")
    budget = context.user_data.get("order_budget")

    if not master_id:
        return

    location = update.message.location

    if location:
        location_text = (
            f"{location.latitude},{location.longitude}"
        )
    else:
        location_text = "Lokatsiya yuborilmagan"

    conn = db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO orders
    (customer_id, master_id, description, budget, location, status)
    VALUES (?, ?, ?, ?, ?, 'new')
    """, (
        update.effective_user.id,
        master_id,
        description,
        budget,
        location_text
    ))

    order_id = cur.lastrowid

    cur.execute("""
    SELECT telegram_id, name
    FROM masters
    WHERE id=?
    """, (master_id,))

    master = cur.fetchone()

    conn.commit()
    conn.close()

    if master:

        master_telegram_id, master_name = master

        keyboard = [[
            InlineKeyboardButton(
                "✅ QABUL QILISH",
                callback_data=f"accept_order:{order_id}"
            ),
            InlineKeyboardButton(
                "❌ RAD ETISH",
                callback_data=f"reject_order:{order_id}"
            )
        ]]

        master_text = f"""
📥 YANGI BUYURTMA #{order_id}

👤 Mijoz: {update.effective_user.first_name}

📝 Muammo:
{description}

💰 Byudjet:
{budget}

📍 Mijoz lokatsiyasi yuborildi.

Buyurtmani qabul qilasizmi?
"""

        try:
            await context.bot.send_message(
                chat_id=master_telegram_id,
                text=master_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

            if location:
                await context.bot.send_location(
                    chat_id=master_telegram_id,
                    latitude=location.latitude,
                    longitude=location.longitude
                )

        except Exception as e:
            print("MASTER NOTIFICATION ERROR:", e)

    await update.message.reply_text(
        f"""
✅ BUYURTMA YUBORILDI!

📋 Buyurtma raqami: #{order_id}

Usta buyurtmangizni ko‘rib chiqadi.

Usta qabul qilganda sizga xabar beramiz.
""",
        reply_markup=main_menu()
    )

    context.user_data.clear()


# =========================
# ACCEPT ORDER
# =========================

async def accept_order(update, context, order_id):

    conn = db()
    cur = conn.cursor()

    cur.execute("""
    SELECT customer_id, master_id, status
    FROM orders
    WHERE id=?
    """, (order_id,))

    order = cur.fetchone()

    if not order:
        conn.close()
        await update.effective_message.reply_text(
            "❌ Buyurtma topilmadi."
        )
        return

    customer_id, master_id, status = order

    if status != "new":
        conn.close()

        await update.effective_message.reply_text(
            "⚠️ Bu buyurtma allaqachon ko‘rib chiqilgan."
        )
        return

    cur.execute("""
    SELECT telegram_id, name
    FROM masters
    WHERE id=?
    """, (master_id,))

    master = cur.fetchone()

    if not master:
        conn.close()
        return

    master_telegram_id, master_name = master

    if update.effective_user.id != master_telegram_id:
        conn.close()

        await update.effective_message.reply_text(
            "❌ Bu buyurtma sizga tegishli emas."
        )
        return

    cur.execute("""
    UPDATE orders
    SET status='accepted'
    WHERE id=?
    """, (order_id,))

    conn.commit()
    conn.close()

    # MUHIM:
    # Endi ustaga ISHNI TUGATISH tugmasi chiqadi.

    keyboard = [[
        InlineKeyboardButton(
            "🏁 ISHNI TUGATISH",
            callback_data=f"finish_order:{order_id}"
        )
    ]]

    await update.effective_message.reply_text(
        f"""
✅ BUYURTMA QABUL QILINDI!

📋 Buyurtma: #{order_id}

Mijoz bilan bog‘lanib ishni bajaring.

Ish tugagach quyidagi tugmani bosing:
""",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    try:
        await context.bot.send_message(
            chat_id=customer_id,
            text=f"""
✅ USTA BUYURTMANGIZNI QABUL QILDI!

📋 Buyurtma: #{order_id}

👨‍🔧 Usta: {master_name}

Usta tez orada siz bilan bog‘lanadi.
"""
        )
    except Exception as e:
        print("CUSTOMER NOTIFICATION ERROR:", e)


# =========================
# REJECT ORDER
# =========================

async def reject_order(update, context, order_id):

    conn = db()
    cur = conn.cursor()

    cur.execute("""
    SELECT customer_id, master_id, status
    FROM orders
    WHERE id=?
    """, (order_id,))

    order = cur.fetchone()

    if not order:
        conn.close()
        return

    customer_id, master_id, status = order

    cur.execute("""
    SELECT telegram_id
    FROM masters
    WHERE id=?
    """, (master_id,))

    master = cur.fetchone()

    if not master:
        conn.close()
        return

    if update.effective_user.id != master[0]:
        conn.close()

        await update.effective_message.reply_text(
            "❌ Bu buyurtma sizga tegishli emas."
        )
        return

    cur.execute("""
    UPDATE orders
    SET status='rejected'
    WHERE id=?
    """, (order_id,))

    conn.commit()
    conn.close()

    await update.effective_message.reply_text(
        f"❌ Buyurtma #{order_id} rad etildi."
    )

    try:
        await context.bot.send_message(
            chat_id=customer_id,
            text=f"""
❌ Afsuski, usta #{order_id} buyurtmani qabul qilmadi.

Boshqa ustani tanlab ko‘rishingiz mumkin.
""",
            reply_markup=main_menu()
        )
    except Exception as e:
        print("REJECT NOTIFICATION ERROR:", e)


# =========================
# FINISH ORDER
# =========================

async def finish_order(update, context, order_id):

    conn = db()
    cur = conn.cursor()

    cur.execute("""
    SELECT customer_id, master_id, status
    FROM orders
    WHERE id=?
    """, (order_id,))

    order = cur.fetchone()

    if not order:
        conn.close()
        await update.effective_message.reply_text(
            "❌ Buyurtma topilmadi."
        )
        return

    customer_id, master_id, status = order

    cur.execute("""
    SELECT telegram_id, name
    FROM masters
    WHERE id=?
    """, (master_id,))

    master = cur.fetchone()

    if not master:
        conn.close()
        return

    master_telegram_id, master_name = master

    if update.effective_user.id != master_telegram_id:
        conn.close()

        await update.effective_message.reply_text(
            "❌ Bu buyurtma sizga tegishli emas."
        )
        return

    if status != "accepted":
        conn.close()

        await update.effective_message.reply_text(
            "⚠️ Bu buyurtmani tugatish mumkin emas."
        )
        return

    cur.execute("""
    UPDATE orders
    SET status='completed'
    WHERE id=?
    """, (order_id,))

    cur.execute("""
    UPDATE masters
    SET completed_orders = completed_orders + 1
    WHERE id=?
    """, (master_id,))

    conn.commit()
    conn.close()

    await update.effective_message.reply_text(
        f"""
🏁 BUYURTMA TUGALLANDI!

📋 Buyurtma: #{order_id}

Mijozdan baho kutilmoqda ⭐
"""
    )

    # Mijozga baholash
    keyboard = [
        [
            InlineKeyboardButton("⭐", callback_data=f"rate:1:{order_id}"),
            InlineKeyboardButton("⭐⭐", callback_data=f"rate:2:{order_id}"),
            InlineKeyboardButton("⭐⭐⭐", callback_data=f"rate:3:{order_id}"),
        ],
        [
            InlineKeyboardButton("⭐⭐⭐⭐", callback_data=f"rate:4:{order_id}"),
            InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data=f"rate:5:{order_id}"),
        ],
    ]

    try:
        await context.bot.send_message(
            chat_id=customer_id,
            text=f"""
🏁 BUYURTMANGIZ TUGALLANDI!

📋 Buyurtma: #{order_id}
👨‍🔧 Usta: {master_name}

⭐ Ustaga baho bering:
""",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as e:
        print("RATING NOTIFICATION ERROR:", e)


# =========================
# SAVE RATING
# =========================

async def save_rating(update, context, rating, order_id):

    conn = db()
    cur = conn.cursor()

    cur.execute("""
    SELECT customer_id, master_id, status
    FROM orders
    WHERE id=?
    """, (order_id,))

    order = cur.fetchone()

    if not order:
        conn.close()
        return

    customer_id, master_id, status = order

    if update.effective_user.id != customer_id:
        conn.close()

        await update.effective_message.reply_text(
            "❌ Bu baholash sizga tegishli emas."
        )
        return

    if status != "completed":
        conn.close()

        await update.effective_message.reply_text(
            "⚠️ Buyurtma hali tugallanmagan."
        )
        return

    cur.execute("""
    SELECT id
    FROM reviews
    WHERE order_id=?
    """, (order_id,))

    existing = cur.fetchone()

    if existing:
        conn.close()

        await update.effective_message.reply_text(
            "⚠️ Siz bu buyurtmaga allaqachon baho bergansiz."
        )
        return

    cur.execute("""
    INSERT INTO reviews
    (order_id, master_id, customer_id, rating)
    VALUES (?, ?, ?, ?)
    """, (
        order_id,
        master_id,
        customer_id,
        rating
    ))

    conn.commit()
    conn.close()

    await update.effective_message.reply_text(
        f"""
⭐ RAHMAT!

Siz ustaga {rating}/5 baho berdingiz.

USTA24 xizmatidan foydalanganingiz uchun rahmat! 🔧
""",
        reply_markup=main_menu()
    )


# =========================
# SHOW ORDERS
# =========================

async def show_orders(update, context):

    user_id = update.effective_user.id

    conn = db()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        o.id,
        o.description,
        o.budget,
        o.status,
        m.name,
        m.service
    FROM orders o
    LEFT JOIN masters m ON o.master_id = m.id
    WHERE o.customer_id=?
    ORDER BY o.id DESC
    """, (user_id,))

    customer_orders = cur.fetchall()

    conn.close()

    if not customer_orders:
        await update.effective_message.reply_text(
            """
📦 BUYURTMALARIM

Sizda hozircha buyurtmalar yo‘q.
""",
            reply_markup=main_menu()
        )
        return

    text = "📦 SIZNING BUYURTMALARINGIZ\n\n"

    status_names = {
        "new": "🟡 Yangi",
        "accepted": "🟢 Qabul qilindi",
        "rejected": "🔴 Rad etildi",
        "completed": "🏁 Tugallandi",
    }

    for order in customer_orders:

        oid, description, budget, status, master_name, service = order

        status_text = status_names.get(
            status,
            status
        )

        text += f"""
📋 #{oid}
📝 {description}
💰 {budget}
👨‍🔧 {master_name or "Usta tanlanmagan"}
🛠 {service or "-"}
📌 Holat: {status_text}

"""

    await update.effective_message.reply_text(
        text,
        reply_markup=main_menu()
    )


# =========================
# CUSTOMER PROFILE
# =========================

async def show_profile(update, context):

    user_id = update.effective_user.id

    conn = db()
    cur = conn.cursor()

    cur.execute("""
    SELECT COUNT(*)
    FROM orders
    WHERE customer_id=?
    """, (user_id,))

    orders_count = cur.fetchone()[0]

    cur.execute("""
    SELECT COUNT(*)
    FROM orders
    WHERE customer_id=? AND status='completed'
    """, (user_id,))

    completed = cur.fetchone()[0]

    conn.close()

    text = f"""
👤 PROFIL

🆔 Telegram ID: {user_id}

📋 Buyurtmalar: {orders_count}
🏁 Tugallangan: {completed}
"""

    await update.effective_message.reply_text(
        text,
        reply_markup=main_menu()
    )


# =========================
# SHOW REVIEWS
# =========================

async def show_reviews(update, context, master_id):

    conn = db()
    cur = conn.cursor()

    cur.execute("""
    SELECT rating
    FROM reviews
    WHERE master_id=?
    ORDER BY id DESC
    LIMIT 10
    """, (master_id,))

    reviews = cur.fetchall()

    conn.close()

    if not reviews:
        text = "⭐ Bu usta hali baholanmagan."
    else:
        text = "⭐ SO‘NGGI BAHOLAR\n\n"

        for r in reviews:
            text += f"{'⭐' * r[0]} — {r[0]}/5\n"

    await update.effective_message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Orqaga",
                    callback_data=f"master:{master_id}"
                )
            ]
        ])
    )


# =========================
# MASTER REGISTRATION
# =========================

async def start_master_registration(update, context):

    context.user_data.clear()
    context.user_data["master_step"] = "name"

    await update.effective_message.reply_text(
        """
🛠 USTA BO‘LISH

Ro‘yxatdan o‘tish uchun ismingizni yozing.
"""
    )


# =========================
# ADMIN NOTIFICATION
# =========================

async def notify_admin(context, master_id):

    conn = db()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        id,
        telegram_id,
        name,
        service,
        region,
        phone,
        price
    FROM masters
    WHERE id=?
    """, (master_id,))

    master = cur.fetchone()

    conn.close()

    if not master:
        return

    (
        mid,
        telegram_id,
        name,
        service,
        region,
        phone,
        price
    ) = master

    text = f"""
🆕 YANGI USTA RO‘YXATDAN O‘TDI

🆔 ID: {mid}

👤 Ism: {name}
🛠 Xizmat: {service}
📍 Hudud: {region}
📞 Telefon: {phone}
💰 Narx: {price}

Tasdiqlaysizmi?
"""

    keyboard = [[
        InlineKeyboardButton(
            "✅ TASDIQLASH",
            callback_data=f"approve:{mid}"
        ),
        InlineKeyboardButton(
            "❌ RAD ETISH",
            callback_data=f"reject:{mid}"
        )
    ]]

    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        print("ADMIN NOTIFICATION ERROR:", e)


# =========================
# ADMIN APPROVE / REJECT
# =========================

async def admin_handler(update, context):

    query = update.callback_query
    data = query.data

    if update.effective_user.id != ADMIN_ID:
        await query.message.reply_text(
            "❌ Siz admin emassiz."
        )
        return

    action, master_id = data.split(":")
    master_id = int(master_id)

    conn = db()
    cur = conn.cursor()

    cur.execute("""
    SELECT telegram_id, name
    FROM masters
    WHERE id=?
    """, (master_id,))

    master = cur.fetchone()

    if not master:
        conn.close()
        await query.message.reply_text(
            "❌ Usta topilmadi."
        )
        return

    telegram_id, name = master

    if action == "approve":

        cur.execute("""
        UPDATE masters
        SET status='approved'
        WHERE id=?
        """, (master_id,))

        message = "✅ Usta tasdiqlandi."

        user_message = """
🎉 TABRIKLAYMIZ!

Sizning USTA24 usta sifatidagi profilingiz tasdiqlandi.

Endi mijozlar sizni topishi va buyurtma berishi mumkin. 🔧
"""

    else:

        cur.execute("""
        UPDATE masters
        SET status='rejected'
        WHERE id=?
        """, (master_id,))

        message = "❌ Usta rad etildi."

        user_message = """
❌ Afsuski, USTA24dagi usta profilingiz tasdiqlanmadi.
"""

    conn.commit()
    conn.close()

    await query.message.reply_text(message)

    try:
        await context.bot.send_message(
            chat_id=telegram_id,
            text=user_message,
            reply_markup=main_menu()
        )
    except Exception as e:
        print("MASTER STATUS ERROR:", e)


# =========================
# TEXT HANDLER
# =========================

async def text_handler(update, context):

    text = update.message.text

    # ORDER
    order_step = context.user_data.get("order_step")

    if order_step == "description":

        context.user_data["order_description"] = text
        context.user_data["order_step"] = "budget"

        keyboard = [[
            KeyboardButton("🤝 Kelishiladi")
        ]]

        await update.message.reply_text(
            """
💰 Taxminiy byudjetingizni yozing.

Masalan:
100 000 so‘m

Yoki:
🤝 Kelishiladi
""",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )

        return

    if order_step == "budget":

        context.user_data["order_budget"] = text
        context.user_data["order_step"] = "location"

        keyboard = [[
            KeyboardButton(
                "📍 Lokatsiyamni yuborish",
                request_location=True
            )
        ]]

        await update.message.reply_text(
            """
📍 Endi lokatsiyangizni yuboring.

Bu usta sizning manzilingizni aniqlashi uchun kerak.
""",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )

        return

    # MASTER REGISTRATION
    master_step = context.user_data.get("master_step")

    if master_step == "name":

        context.user_data["master_name"] = text
        context.user_data["master_step"] = "service"

        await update.message.reply_text(
            "🛠 Qaysi xizmat bo‘yicha usta ekansiz?",
            reply_markup=services_menu("master_service")
        )

        return

    if master_step == "custom_service":

        context.user_data["master_service"] = text
        context.user_data["master_step"] = "region"

        await update.message.reply_text(
            "📍 Qaysi hududda ishlaysiz?"
        )

        return

    if master_step == "region":

        context.user_data["master_region"] = text
        context.user_data["master_step"] = "phone"

        keyboard = [[
            KeyboardButton(
                "📞 Telefon raqamimni yuborish",
                request_contact=True
            )
        ]]

        await update.message.reply_text(
            "📞 Telefon raqamingizni yuboring:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )

        return

    if master_step == "price":

        context.user_data["master_price"] = text

        conn = db()
        cur = conn.cursor()

        try:

            cur.execute("""
            INSERT OR REPLACE INTO masters
            (
                telegram_id,
                name,
                service,
                region,
                phone,
                price,
                status,
                completed_orders
            )
            VALUES (?, ?, ?, ?, ?, ?, 'pending', 0)
            """, (
                update.effective_user.id,
                context.user_data["master_name"],
                context.user_data["master_service"],
                context.user_data["master_region"],
                context.user_data["master_phone"],
                context.user_data["master_price"]
            ))

            master_id = cur.lastrowid

            conn.commit()

        finally:
            conn.close()

        await update.message.reply_text(
            """
✅ RO‘YXATDAN O‘TISH YAKUNLANDI!

Profilingiz admin tasdig‘iga yuborildi.

⏳ Tasdiqlangandan keyin mijozlarga ko‘rinasiz.
"""
        )

        await notify_admin(context, master_id)

        context.user_data.clear()

        return

    await update.message.reply_text(
        "Kerakli bo‘limni tanlang:",
        reply_markup=main_menu()
    )


# =========================
# CONTACT HANDLER
# =========================

async def contact_handler(update, context):

    contact = update.message.contact

    # ORDER CONTACT NOT USED

    if context.user_data.get("master_step") == "phone":

        context.user_data["master_phone"] = contact.phone_number
        context.user_data["master_step"] = "price"

        await update.message.reply_text(
            """
💰 Xizmat narxingizni yozing.

Masalan:
100 000 so‘mdan

Yoki:
Kelishiladi
"""
        )

        return


# =========================
# LOCATION HANDLER
# =========================

async def location_handler(update, context):

    if context.user_data.get("order_step") != "location":
        return

    await create_order(update, context)


# =========================
# CALLBACK HANDLER
# =========================

async def button_handler(update, context):

    query = update.callback_query
    data = query.data

    # IMPORTANT:
    # query.answer() ataylab ishlatilmayapti.
    # Oldingi Telegram callback timeout muammosining oldini oladi.

    if data == "back":

        await query.message.reply_text(
            "🔧 USTA24 ASOSIY MENYU",
            reply_markup=main_menu()
        )
        return

    if data == "find_master":

        await query.message.reply_text(
            "🛠 Xizmat turini tanlang:",
            reply_markup=services_menu("find_service")
        )
        return

    if data == "choose_service_order":

        await query.message.reply_text(
            "📋 Buyurtma berish uchun xizmat turini tanlang:",
            reply_markup=services_menu("find_service")
        )
        return

    if data == "services":

        await query.message.reply_text(
            """
📂 USTA24 XIZMATLARI

Quyidagi xizmatlardan birini tanlang:
""",
            reply_markup=services_menu("find_service")
        )
        return

    if data == "become_master":

        await start_master_registration(update, context)
        return

    if data == "profile":

        await show_profile(update, context)
        return

    if data == "my_orders":

        await show_orders(update, context)
        return

    if data == "about":

        await query.message.reply_text(
            """
🔧 USTA24

Mahalliy xizmat ko‘rsatuvchi ustalarni mijozlar bilan bog‘lovchi platforma.

👨‍🔧 Ustalar
📋 Buyurtmalar
📍 Lokatsiya
⭐ Reyting
💬 Aloqa

USTA24 — xizmat kerak bo‘lsa, usta shu yerda.
""",
            reply_markup=main_menu()
        )
        return

    # FIND SERVICE
    if data.startswith("find_service:"):

        index = int(data.split(":")[1])
        service = SERVICES[index]

        await show_masters(
            update,
            context,
            service
        )

        return

    # MASTER SERVICE
    if data.startswith("master_service:"):

        index = int(data.split(":")[1])
        service = SERVICES[index]

        if service == "🛠 Boshqa":

            context.user_data["master_step"] = "custom_service"

            await query.message.reply_text(
                "🛠 Xizmatingiz nomini yozing:"
            )

        else:

            context.user_data["master_service"] = service
            context.user_data["master_step"] = "region"

            await query.message.reply_text(
                "📍 Qaysi hududda ishlaysiz?"
            )

        return

    # MASTER PROFILE
    if data.startswith("master:"):

        master_id = int(data.split(":")[1])

        await show_master_profile(
            update,
            context,
            master_id
        )

        return

    # ORDER MASTER
    if data.startswith("order_master:"):

        master_id = int(data.split(":")[1])

        await start_order(
            update,
            context,
            master_id
        )

        return

    # ACCEPT
    if data.startswith("accept_order:"):

        order_id = int(data.split(":")[1])

        await accept_order(
            update,
            context,
            order_id
        )

        return

    # REJECT
    if data.startswith("reject_order:"):

        order_id = int(data.split(":")[1])

        await reject_order(
            update,
            context,
            order_id
        )

        return

    # FINISH
    if data.startswith("finish_order:"):

        order_id = int(data.split(":")[1])

        await finish_order(
            update,
            context,
            order_id
        )

        return

    # RATING
    if data.startswith("rate:"):

        parts = data.split(":")

        rating = int(parts[1])
        order_id = int(parts[2])

        await save_rating(
            update,
            context,
            rating,
            order_id
        )

        return

    # PHONE
    if data.startswith("phone:"):

        master_id = int(data.split(":")[1])

        conn = db()
        cur = conn.cursor()

        cur.execute("""
        SELECT name, phone
        FROM masters
        WHERE id=? AND status='approved'
        """, (master_id,))

        master = cur.fetchone()
        conn.close()

        if master:

            name, phone = master

            await query.message.reply_text(
                f"""
📞 USTA ALOQASI

👨‍🔧 {name}
📱 {phone}
"""
            )

        return

    # REVIEWS
    if data.startswith("reviews:"):

        master_id = int(data.split(":")[1])

        await show_reviews(
            update,
            context,
            master_id
        )

        return

    # ADMIN
    if data.startswith("approve:") or data.startswith("reject:"):

        await admin_handler(
            update,
            context
        )

        return


# =========================
# ERROR
# =========================

async def error_handler(update, context):

    print("XATO:", context.error)


# =========================
# MAIN
# =========================

def main():

    if not TOKEN:
        print("❌ BOT_TOKEN topilmadi!")
        print("Termuxda BOT_TOKEN ni export qiling.")
        return

    init_db()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    app.add_handler(
        MessageHandler(
            filters.CONTACT,
            contact_handler
        )
    )

    app.add_handler(
        MessageHandler(
            filters.LOCATION,
            location_handler
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_handler
        )
    )

    app.add_error_handler(error_handler)

    print("🚀 USTA24 2.1 ISHLAYAPTI...")

    app.run_polling()


if __name__ == "__main__":
    main()
