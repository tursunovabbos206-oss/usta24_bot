import os
import sqlite3
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.request import HTTPXRequest


# =========================================================
# SOZLAMALAR
# =========================================================

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 5930225049

DB_NAME = "usta24.db"

PORT = int(os.environ.get("PORT", 10000))


# =========================================================
# TOKEN TEKSHIRISH
# =========================================================

if not TOKEN:
    print("XATO: BOT_TOKEN topilmadi!")
    print("Termuxda BOT_TOKEN ni export qiling.")
    raise SystemExit(1)


# =========================================================
# XIZMATLAR
# =========================================================

SERVICES = [
    "🔧 Santexnik",
    "⚡ Elektrik",
    "❄️ Konditsioner",
    "💻 Kompyuter",
    "🏗 Qurilish",
    "🚗 Avto xizmat",
    "🛠 Boshqa",
]


# =========================================================
# O‘ZBEKISTON HUDUDLARI
# =========================================================

REGIONS = {
    "Toshkent shahri": [
        "Bektemir tumani",
        "Chilonzor tumani",
        "Mirobod tumani",
        "Mirzo Ulug‘bek tumani",
        "Olmazor tumani",
        "Sergeli tumani",
        "Shayxontohur tumani",
        "Uchtepa tumani",
        "Yashnobod tumani",
        "Yunusobod tumani",
        "Yakkasaroy tumani",
        "Yangihayot tumani",
    ],

    "Toshkent viloyati": [
        "Angren shahri",
        "Bekobod shahri",
        "Chirchiq shahri",
        "Olmaliq shahri",
        "Ohangaron shahri",
        "Nurafshon shahri",
        "Yangiyo‘l shahri",
        "Bekobod tumani",
        "Bo‘stonliq tumani",
        "Bo‘ka tumani",
        "Chinoz tumani",
        "Ohangaron tumani",
        "Oqqo‘rg‘on tumani",
        "Parkent tumani",
        "Piskent tumani",
        "Quyi Chirchiq tumani",
        "Toshkent tumani",
        "Yuqori Chirchiq tumani",
        "Zangiota tumani",
        "Yangiyo‘l tumani",
    ],

    "Samarqand viloyati": [
        "Samarqand shahri",
        "Kattaqo‘rg‘on shahri",
        "Bulung‘ur tumani",
        "Ishtixon tumani",
        "Jomboy tumani",
        "Kattaqo‘rg‘on tumani",
        "Narpay tumani",
        "Nurobod tumani",
        "Oqdaryo tumani",
        "Paxtachi tumani",
        "Payariq tumani",
        "Pastdarg‘om tumani",
        "Qo‘shrabot tumani",
        "Samarqand tumani",
        "Toyloq tumani",
        "Urgut tumani",
    ],

    "Buxoro viloyati": [
        "Buxoro shahri",
        "Kogon shahri",
        "Buxoro tumani",
        "G‘ijduvon tumani",
        "Jondor tumani",
        "Kogon tumani",
        "Olot tumani",
        "Peshku tumani",
        "Qorako‘l tumani",
        "Qorovulbozor tumani",
        "Romitan tumani",
        "Shofirkon tumani",
        "Vobkent tumani",
    ],

    "Andijon viloyati": [
        "Andijon shahri",
        "Asaka tumani",
        "Andijon tumani",
        "Baliqchi tumani",
        "Bo‘z tumani",
        "Buloqboshi tumani",
        "Izboskan tumani",
        "Jalaquduq tumani",
        "Marhamat tumani",
        "Oltinko‘l tumani",
        "Paxtaobod tumani",
        "Qo‘rg‘ontepa tumani",
        "Shahrixon tumani",
        "Ulug‘nor tumani",
        "Xo‘jaobod tumani",
    ],

    "Farg‘ona viloyati": [
        "Farg‘ona shahri",
        "Qo‘qon shahri",
        "Marg‘ilon shahri",
        "Quvasoy shahri",
        "Bag‘dod tumani",
        "Beshariq tumani",
        "Buvayda tumani",
        "Dang‘ara tumani",
        "Farg‘ona tumani",
        "Furqat tumani",
        "Oltiariq tumani",
        "O‘zbekiston tumani",
        "Qo‘shtepa tumani",
        "Rishton tumani",
        "So‘x tumani",
        "Toshloq tumani",
        "Uchko‘prik tumani",
        "Yozyovon tumani",
    ],

    "Namangan viloyati": [
        "Namangan shahri",
        "Chortoq tumani",
        "Chust tumani",
        "Kosonsoy tumani",
        "Mingbuloq tumani",
        "Namangan tumani",
        "Norin tumani",
        "Pop tumani",
        "To‘raqo‘rg‘on tumani",
        "Uchqo‘rg‘on tumani",
        "Uychi tumani",
        "Yangiqo‘rg‘on tumani",
    ],

    "Qashqadaryo viloyati": [
        "Qarshi shahri",
        "Shahrisabz shahri",
        "Chiroqchi tumani",
        "Dehqonobod tumani",
        "G‘uzor tumani",
        "Kasbi tumani",
        "Kitob tumani",
        "Koson tumani",
        "Mirishkor tumani",
        "Muborak tumani",
        "Nishon tumani",
        "Qamashi tumani",
        "Qarshi tumani",
        "Shahrisabz tumani",
        "Yakkabog‘ tumani",
    ],

    "Surxondaryo viloyati": [
        "Termiz shahri",
        "Angor tumani",
        "Bandixon tumani",
        "Boysun tumani",
        "Denov tumani",
        "Jarqo‘rg‘on tumani",
        "Muzrabot tumani",
        "Oltinsoy tumani",
        "Qiziriq tumani",
        "Qumqo‘rg‘on tumani",
        "Sariosiyo tumani",
        "Sherobod tumani",
        "Sho‘rchi tumani",
        "Termiz tumani",
        "Uzun tumani",
    ],

    "Jizzax viloyati": [
        "Jizzax shahri",
        "Arnasoy tumani",
        "Baxmal tumani",
        "Do‘stlik tumani",
        "Forish tumani",
        "G‘allaorol tumani",
        "Mirzacho‘l tumani",
        "Paxtakor tumani",
        "Sharof Rashidov tumani",
        "Yangiobod tumani",
        "Zarbdor tumani",
        "Zafarobod tumani",
    ],

    "Sirdaryo viloyati": [
        "Guliston shahri",
        "Shirin shahri",
        "Yangiyer shahri",
        "Boyovut tumani",
        "Guliston tumani",
        "Mirzaobod tumani",
        "Oqoltin tumani",
        "Sayxunobod tumani",
        "Sardoba tumani",
        "Sirdaryo tumani",
        "Xovos tumani",
    ],

    "Navoiy viloyati": [
        "Navoiy shahri",
        "Zarafshon shahri",
        "Karmana tumani",
        "Konimex tumani",
        "Navbahor tumani",
        "Nurota tumani",
        "Qiziltepa tumani",
        "Tomdi tumani",
        "Uchquduq tumani",
        "Xatirchi tumani",
    ],

    "Xorazm viloyati": [
        "Urganch shahri",
        "Xiva shahri",
        "Bog‘ot tumani",
        "Gurlan tumani",
        "Hazorasp tumani",
        "Qo‘shko‘pir tumani",
        "Shovot tumani",
        "Tuproqqal’a tumani",
        "Urganch tumani",
        "Xonqa tumani",
        "Xiva tumani",
        "Yangiariq tumani",
        "Yangibozor tumani",
    ],

    "Qoraqalpog‘iston Respublikasi": [
        "Nukus shahri",
        "Amudaryo tumani",
        "Beruniy tumani",
        "Chimboy tumani",
        "Ellikqal’a tumani",
        "Kegeyli tumani",
        "Mo‘ynoq tumani",
        "Nukus tumani",
        "Qanliko‘l tumani",
        "Qo‘ng‘irot tumani",
        "Qorao‘zak tumani",
        "Shumanay tumani",
        "Taxtako‘pir tumani",
        "To‘rtko‘l tumani",
        "Xo‘jayli tumani",
    ],
}


# =========================================================
# DATABASE
# =========================================================

def db():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = db()
    cur = conn.cursor()

    # Ustalar
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

    # Eski database bo'lsa completed_orders ustuni bo'lmasligi mumkin
    try:
        cur.execute(
            "ALTER TABLE masters ADD COLUMN completed_orders INTEGER DEFAULT 0"
        )
    except sqlite3.OperationalError:
        pass

    # Buyurtmalar
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            master_id INTEGER,
            description TEXT,
            budget TEXT,
            latitude REAL,
            longitude REAL,
            status TEXT DEFAULT 'new'
        )
    """)

    # Baholar
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            master_id INTEGER,
            customer_id INTEGER,
            rating INTEGER,
            comment TEXT DEFAULT ''
        )
    """)

    conn.commit()
    conn.close()


init_db()


# =========================================================
# HTTP HEALTH SERVER
# RENDER PORT UCHUN
# =========================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()

        self.wfile.write(
            b"USTA24 BOT OK"
        )

    def log_message(self, format, *args):
        return


def run_health_server():
    server = HTTPServer(
        ("0.0.0.0", PORT),
        HealthHandler
    )

    print(f"HTTP SERVER PORT: {PORT}")

    server.serve_forever()


# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    keyboard = [
        [
            InlineKeyboardButton(
                "🔎 USTA TOPISH",
                callback_data="find_master"
            ),
            InlineKeyboardButton(
                "📋 BUYURTMA BERISH",
                callback_data="find_master"
            ),
        ],
        [
            InlineKeyboardButton(
                "🛠 USTA BO‘LISH",
                callback_data="become_master"
            ),
        ],
        [
            InlineKeyboardButton(
                "📂 XIZMATLAR",
                callback_data="services"
            ),
            InlineKeyboardButton(
                "👤 PROFIL",
                callback_data="profile"
            ),
        ],
        [
            InlineKeyboardButton(
                "📦 BUYURTMALARIM",
                callback_data="my_orders"
            ),
        ],
        [
            InlineKeyboardButton(
                "ℹ️ USTA24 HAQIDA",
                callback_data="about"
            ),
        ],
    ]

    if update.effective_user.id == ADMIN_ID:
        keyboard.append([
            InlineKeyboardButton(
                "🛠 ADMIN PANEL",
                callback_data="admin_panel"
            )
        ])

    text = (
        "🔧 <b>USTA24</b>\n\n"
        "Assalomu alaykum! 👋\n\n"
        "Uyingiz yoki biznesingiz uchun kerakli ustani "
        "tez va qulay toping.\n\n"
        "🔎 Usta toping\n"
        "📋 Buyurtma bering\n"
        "⭐ Baholang\n\n"
        "<b>USTA24 — xizmat kerak bo‘lsa, usta shu yerda!</b>"
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# XIZMATLAR
# =========================================================

async def show_services(update, context):

    keyboard = []

    for i in range(0, len(SERVICES), 2):

        row = []

        row.append(
            InlineKeyboardButton(
                SERVICES[i],
                callback_data=f"service:{SERVICES[i]}"
            )
        )

        if i + 1 < len(SERVICES):
            row.append(
                InlineKeyboardButton(
                    SERVICES[i + 1],
                    callback_data=f"service:{SERVICES[i + 1]}"
                )
            )

        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ BOSH MENYU",
            callback_data="home"
        )
    ])

    await update.callback_query.message.edit_text(
        "📂 <b>XIZMATLAR</b>\n\n"
        "Kerakli xizmat turini tanlang:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_regions(update, context):

    keyboard = []

    region_names = list(REGIONS.keys())

    for i in range(0, len(region_names), 2):

        row = []

        for j in range(i, min(i + 2, len(region_names))):

            region_name = region_names[j]

            row.append(
                InlineKeyboardButton(
                    region_name,
                    callback_data=f"province:{j}"
                )
            )

        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(
            "🌍 BARCHA HUDUDLAR",
            callback_data="all_regions"
        )
    ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ BOSH MENYU",
            callback_data="home"
        )
    ])

    await update.callback_query.message.edit_text(
        "📍 <b>HUDUDNI TANLANG</b>\n\n"
        "Usta qaysi viloyat yoki shaharda kerak?",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_districts(update, context, province_index):

    region_names = list(REGIONS.keys())

    try:
        province_index = int(province_index)
        province = region_names[province_index]
    except (ValueError, IndexError):
        await update.callback_query.message.edit_text(
            "❌ Hudud tanlashda xatolik yuz berdi."
        )
        return

    context.user_data["selected_province"] = province

    districts = REGIONS[province]

    keyboard = []

    for i in range(0, len(districts), 2):

        row = []

        for j in range(i, min(i + 2, len(districts))):

            district = districts[j]

            row.append(
                InlineKeyboardButton(
                    district,
                    callback_data=f"district:{province_index}:{j}"
                )
            )

        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ VILOYATLAR",
            callback_data="back_regions"
        )
    ])

    keyboard.append([
        InlineKeyboardButton(
            "🏠 BOSH MENYU",
            callback_data="home"
        )
    ])

    await update.callback_query.message.edit_text(
        f"📍 <b>{province}</b>\n\n"
        "🏙 Tuman yoki shaharni tanlang:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# USTALAR RO‘YXATI
# =========================================================

async def show_masters(update, context, service=None, region=None):

    conn = db()
    cur = conn.cursor()

    query = """
        SELECT id, name, service, region, price,
               completed_orders
        FROM masters
        WHERE status='approved'
    """
    params = []

    if service:
        query += " AND service=?"
        params.append(service)

    if region:
        # Eski ro‘yxatdan o‘tgan ustalar ham ishlashi uchun
        # hudud nomining ichidan qidiramiz.
        query += " AND region LIKE ?"
        params.append(f"%{region}%")

    query += " ORDER BY id DESC"

    cur.execute(query, params)

    masters = cur.fetchall()
    conn.close()

    keyboard = []

    if not masters:

        text = (
            "😔 <b>Usta topilmadi</b>\n\n"
            f"📍 Hudud: {region or 'Barcha hududlar'}\n"
            f"🔧 Xizmat: {service or 'Barcha xizmatlar'}\n\n"
            "Boshqa hudud yoki xizmatni tanlab ko‘ring."
        )

    else:

        text = "🔎 <b>USTALAR</b>\n\n"

        if service:
            text += f"🔧 Xizmat: <b>{service}</b>\n"

        if region:
            text += f"📍 Hudud: <b>{region}</b>\n"

        text += f"\n👥 Topilgan ustalar: <b>{len(masters)}</b>\n\n"

        for master in masters:

            mid, name, service_name, master_region, price, completed = master

            text += (
                f"🛠 <b>{name}</b>\n"
                f"🔧 {service_name}\n"
                f"📍 {master_region}\n"
                f"💰 {price}\n"
                f"🏆 Tugallangan ishlar: {completed}\n\n"
            )

            keyboard.append([
                InlineKeyboardButton(
                    f"👤 {name}",
                    callback_data=f"master:{mid}"
                )
            ])

    keyboard.append([
        InlineKeyboardButton(
            "📍 BOSHQA HUDUD",
            callback_data="back_regions"
        )
    ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ BOSH MENYU",
            callback_data="home"
        )
    ])

    await update.callback_query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# USTA PROFILI
# =========================================================


# =========================================================

async def show_master_profile(update, context, master_id):

    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, service, region, phone,
               price, completed_orders, about
        FROM masters
        WHERE id=? AND status='approved'
    """, (master_id,))

    master = cur.fetchone()

    cur.execute("""
        SELECT AVG(rating), COUNT(rating)
        FROM reviews
        WHERE master_id=?
    """, (master_id,))

    rating_data = cur.fetchone()

    conn.close()

    if not master:
        await update.callback_query.message.edit_text(
            "❌ Usta topilmadi."
        )
        return

    mid, name, service, region, phone, price, completed, about = master

    rating = rating_data[0] if rating_data else None
    review_count = rating_data[1] if rating_data else 0

    if rating:
        rating_text = f"{rating:.1f}/5 ⭐"
    else:
        rating_text = "Hali baholanmagan ⭐"

    about_text = about.strip() if about else (
        "Usta hali o‘zi haqida ma’lumot kiritmagan."
    )

    text = (
        "👤 <b>USTA PROFILI 2.0</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🛠 <b>{name}</b> ✅\n\n"
        f"🔧 <b>Xizmat:</b> {service}\n"
        f"📍 <b>Hudud:</b> {region}\n"
        f"💰 <b>Taxminiy narx:</b> {price}\n"
        f"🏆 <b>Tugallangan ishlar:</b> {completed}\n"
        f"⭐ <b>Reyting:</b> {rating_text}\n"
        f"💬 <b>Baholar soni:</b> {review_count} ta\n\n"
        "📝 <b>USTA HAQIDA</b>\n"
        f"{about_text}\n\n"
        "🛡 <b>USTA24 tasdiqlangan ustasi</b>"
    )

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
            ),
            InlineKeyboardButton(
                "📍 LOKATSIYA",
                callback_data=f"master_location:{mid}"
            ),
        ],
        [
            InlineKeyboardButton(
                "⭐ BAHOLAR",
                callback_data=f"reviews:{mid}"
            ),
        ],
        [
            InlineKeyboardButton(
                "⬅️ ORQAGA",
                callback_data="find_master"
            ),
        ],
    ]

    await update.callback_query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# BUYURTMA BOSHLASH
# =========================================================

async def start_order(update, context, master_id):

    context.user_data.clear()

    context.user_data["order_master_id"] = master_id
    context.user_data["order_step"] = "description"

    await update.callback_query.message.edit_text(
        "📋 <b>BUYURTMA BERISH</b>\n\n"
        "1️⃣ Muammoingizni batafsil yozing.\n\n"
        "Masalan:\n"
        "«Oshxonadagi kran suv chiqaryapti.»\n\n"
        "✍️ Muammoni yozing:",
        parse_mode="HTML"
    )


# =========================================================
# BUYURTMA YARATISH
# =========================================================

async def create_order(update, context):

    user_id = update.effective_user.id

    master_id = context.user_data.get("order_master_id")
    description = context.user_data.get("order_description")
    budget = context.user_data.get("order_budget")

    if not master_id:
        return

    location = update.message.location

    latitude = location.latitude
    longitude = location.longitude

    conn = db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO orders
        (
            customer_id,
            master_id,
            description,
            budget,
            latitude,
            longitude,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, 'new')
    """, (
        user_id,
        master_id,
        description,
        budget,
        latitude,
        longitude
    ))

    order_id = cur.lastrowid

    cur.execute(
        "SELECT telegram_id, name FROM masters WHERE id=?",
        (master_id,)
    )

    master = cur.fetchone()

    conn.commit()
    conn.close()

    context.user_data.clear()

    await update.message.reply_text(
        f"✅ <b>BUYURTMA QABUL QILINDI!</b>\n\n"
        f"📋 Buyurtma №{order_id}\n"
        f"📝 Muammo: {description}\n"
        f"💰 Budjet: {budget}\n\n"
        "Ustaga yuborildi. Usta javobini kuting.",
        parse_mode="HTML"
    )

    if master:

        master_telegram_id, master_name = master

        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ QABUL QILAMAN",
                    callback_data=f"accept_order:{order_id}"
                ),
                InlineKeyboardButton(
                    "❌ RAD ETISH",
                    callback_data=f"reject_order:{order_id}"
                ),
            ]
        ]

        await context.bot.send_message(
            chat_id=master_telegram_id,
            text=(
                "🔔 <b>YANGI BUYURTMA!</b>\n\n"
                f"📋 Buyurtma №{order_id}\n\n"
                f"📝 Muammo:\n{description}\n\n"
                f"💰 Budjet: {budget}\n\n"
                "Mijoz lokatsiyasi quyida yuborildi."
            ),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        await context.bot.send_location(
            chat_id=master_telegram_id,
            latitude=latitude,
            longitude=longitude
        )


# =========================================================
# BUYURTMALAR
# =========================================================

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
            m.name
        FROM orders o
        LEFT JOIN masters m
            ON o.master_id = m.id
        WHERE o.customer_id=?
        ORDER BY o.id DESC
        LIMIT 20
    """, (user_id,))

    customer_orders = cur.fetchall()

    cur.execute("""
        SELECT id
        FROM masters
        WHERE telegram_id=?
    """, (user_id,))

    master = cur.fetchone()

    master_orders = []

    if master:

        master_id = master[0]

        cur.execute("""
            SELECT
                o.id,
                o.description,
                o.budget,
                o.status
            FROM orders o
            WHERE o.master_id=?
            ORDER BY o.id DESC
            LIMIT 20
        """, (master_id,))

        master_orders = cur.fetchall()

    conn.close()

    text = "📦 <b>BUYURTMALARIM</b>\n\n"

    if customer_orders:

        text += "👤 <b>MENING BUYURTMALARIM:</b>\n\n"

        for order in customer_orders:

            oid, desc, budget, status, master_name = order

            if status == "new":
                status_text = "🟡 Yangi"
            elif status == "accepted":
                status_text = "🟢 Qabul qilindi"
            elif status == "completed":
                status_text = "✅ Tugallangan"
            elif status == "rejected":
                status_text = "🔴 Rad etildi"
            else:
                status_text = status

            text += (
                f"📋 №{oid}\n"
                f"📝 {desc}\n"
                f"💰 {budget}\n"
                f"🛠 Usta: {master_name or '-'}\n"
                f"📊 Holat: {status_text}\n\n"
            )

    else:
        text += "Siz hali buyurtma bermagansiz.\n\n"

    if master_orders:

        text += "🛠 <b>USTA SIFATIDA:</b>\n\n"

        for order in master_orders:

            oid, desc, budget, status = order

            if status == "new":
                status_text = "🟡 Yangi"
            elif status == "accepted":
                status_text = "🟢 Qabul qilingan"
            elif status == "completed":
                status_text = "✅ Tugallangan"
            elif status == "rejected":
                status_text = "🔴 Rad etilgan"
            else:
                status_text = status

            text += (
                f"📋 №{oid}\n"
                f"📝 {desc}\n"
                f"💰 {budget}\n"
                f"📊 {status_text}\n\n"
            )

    keyboard = [
        [
            InlineKeyboardButton(
                "⬅️ BOSH MENYU",
                callback_data="home"
            )
        ]
    ]

    await update.callback_query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# PROFIL
# =========================================================

async def show_profile(update, context):

    user_id = update.effective_user.id

    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            name,
            service,
            region,
            phone,
            price,
            status,
            completed_orders
        FROM masters
        WHERE telegram_id=?
    """, (user_id,))

    master = cur.fetchone()

    cur.execute("""
        SELECT COUNT(*)
        FROM orders
        WHERE customer_id=?
    """, (user_id,))

    customer_orders = cur.fetchone()[0]

    conn.close()

    text = "👤 <b>PROFIL</b>\n\n"

    text += (
        f"📋 Mijoz buyurtmalari: {customer_orders}\n\n"
    )

    if master:

        name, service, region, phone, price, status, completed = master

        if status == "approved":
            status_text = "✅ Tasdiqlangan"
        elif status == "pending":
            status_text = "🟡 Tekshirilmoqda"
        else:
            status_text = "🔴 Rad etilgan"

        text += (
            "🛠 <b>USTA PROFILI:</b>\n\n"
            f"👤 Ism: {name}\n"
            f"🔧 Xizmat: {service}\n"
            f"📍 Hudud: {region}\n"
            f"📞 Telefon: {phone}\n"
            f"💰 Narx: {price}\n"
            f"🏆 Tugallangan ishlar: {completed}\n"
            f"📊 Holat: {status_text}\n"
        )

    else:

        text += (
            "🛠 Siz hali USTA24 tizimida usta sifatida "
            "ro‘yxatdan o‘tmagansiz."
        )

    keyboard = [
        [
            InlineKeyboardButton(
                "🛠 USTA BO‘LISH",
                callback_data="become_master"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ BOSH MENYU",
                callback_data="home"
            )
        ]
    ]

    await update.callback_query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# BAHOLAR
# =========================================================

async def show_reviews(update, context, master_id):

    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT rating, comment
        FROM reviews
        WHERE master_id=?
        ORDER BY id DESC
        LIMIT 20
    """, (master_id,))

    reviews = cur.fetchall()
    conn.close()

    text = "⭐ <b>USTA BAHOLARI</b>\n\n"

    if not reviews:

        text += "Hali baholar mavjud emas."

    else:

        for rating, comment in reviews:

            text += (
                f"{'⭐' * rating}\n"
            )

            if comment:
                text += f"💬 {comment}\n"

            text += "\n"

    keyboard = [
        [
            InlineKeyboardButton(
                "⬅️ ORQAGA",
                callback_data=f"master:{master_id}"
            )
        ]
    ]

    await update.callback_query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )



# =========================================================
# ADMIN PANEL
# =========================================================

async def admin_panel(update, context):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.message.edit_text(
            "⛔ Sizda admin huquqi yo‘q.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Bosh menyu", callback_data="home")]
            ])
        )
        return

    keyboard = [
        [
            InlineKeyboardButton("📊 STATISTIKA", callback_data="admin_stats"),
            InlineKeyboardButton("⏳ KUTILAYOTGAN", callback_data="admin_pending"),
        ],
        [
            InlineKeyboardButton("👨‍🔧 USTALAR", callback_data="admin_masters"),
            InlineKeyboardButton("👥 FOYDALANUVCHILAR", callback_data="admin_users"),
        ],
        [
            InlineKeyboardButton("📦 BUYURTMALAR", callback_data="admin_orders"),
            InlineKeyboardButton("⭐ BAHOLAR", callback_data="admin_reviews"),
        ],
        [
            InlineKeyboardButton("⬅️ BOSH MENYU", callback_data="home")
        ],
    ]

    await query.message.edit_text(
        "🛠 <b>USTA24 ADMIN PANEL</b>\n\n"
        "Kerakli bo‘limni tanlang:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def admin_stats(update, context):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        return

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM masters")
    masters = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM masters WHERE status='approved'")
    approved = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM masters WHERE status='pending'")
    pending = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM masters WHERE status='blocked'")
    blocked = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders")
    orders = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders WHERE status='completed'")
    completed = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM reviews")
    reviews = cur.fetchone()[0]

    conn.close()

    text = (
        "📊 <b>USTA24 STATISTIKA</b>\n\n"
        f"👨‍🔧 Jami ustalar: <b>{masters}</b>\n"
        f"✅ Tasdiqlangan: <b>{approved}</b>\n"
        f"⏳ Kutilayotgan: <b>{pending}</b>\n"
        f"🚫 Bloklangan: <b>{blocked}</b>\n\n"
        f"📦 Jami buyurtmalar: <b>{orders}</b>\n"
        f"✅ Yakunlangan: <b>{completed}</b>\n"
        f"⭐ Baholar: <b>{reviews}</b>"
    )

    await query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Admin panel", callback_data="admin_panel")]
        ])
    )


async def admin_pending(update, context):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        return

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, service, region, phone
        FROM masters
        WHERE status='pending'
        ORDER BY id DESC
    """)

    rows = cur.fetchall()
    conn.close()

    if not rows:
        text = "⏳ <b>KUTILAYOTGAN USTALAR</b>\n\nHozircha yangi ariza yo‘q."
        keyboard = [
            [InlineKeyboardButton("⬅️ Admin panel", callback_data="admin_panel")]
        ]
    else:
        text = "⏳ <b>KUTILAYOTGAN USTALAR</b>\n\n"
        keyboard = []

        for master_id, name, service, region, phone in rows:
            text += (
                f"🆔 {master_id} | <b>{name}</b>\n"
                f"🛠 {service}\n"
                f"📍 {region}\n"
                f"📞 {phone}\n\n"
            )

            keyboard.append([
                InlineKeyboardButton(
                    f"👨‍🔧 {name}",
                    callback_data=f"admin_master:{master_id}"
                )
            ])

        keyboard.append([
            InlineKeyboardButton("⬅️ Admin panel", callback_data="admin_panel")
        ])

    await query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def admin_master(update, context, master_id):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        return

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, telegram_id, name, service, region, phone, price,
               status, completed_orders
        FROM masters
        WHERE id=?
    """, (master_id,))

    row = cur.fetchone()
    conn.close()

    if not row:
        await query.message.edit_text("❌ Usta topilmadi.")
        return

    (
        mid, telegram_id, name, service, region,
        phone, price, status, completed_orders
    ) = row

    status_text = {
        "pending": "⏳ Kutilmoqda",
        "approved": "✅ Tasdiqlangan",
        "blocked": "🚫 Bloklangan",
        "rejected": "❌ Rad etilgan"
    }.get(status, status)

    text = (
        "👨‍🔧 <b>USTA MA'LUMOTLARI</b>\n\n"
        f"🆔 ID: <b>{mid}</b>\n"
        f"👤 Ism: <b>{name}</b>\n"
        f"🛠 Xizmat: {service}\n"
        f"📍 Hudud: {region}\n"
        f"📞 Telefon: {phone}\n"
        f"💰 Narx: {price}\n"
        f"📦 Tugallangan ishlar: {completed_orders}\n"
        f"📌 Holat: <b>{status_text}</b>"
    )

    keyboard = []

    if status == "pending":
        keyboard.append([
            InlineKeyboardButton("✅ TASDIQLASH", callback_data=f"approve:{mid}"),
            InlineKeyboardButton("❌ RAD ETISH", callback_data=f"reject:{mid}")
        ])

    if status == "approved":
        keyboard.append([
            InlineKeyboardButton("🚫 BLOKLASH", callback_data=f"block:{mid}")
        ])

    if status == "blocked":
        keyboard.append([
            InlineKeyboardButton("🔓 BLOKDAN CHIQARISH", callback_data=f"unblock:{mid}")
        ])

    keyboard.append([
        InlineKeyboardButton("⬅️ Kutilayotganlar", callback_data="admin_pending")
    ])

    await query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def admin_masters(update, context):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        return

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, service, region, status
        FROM masters
        ORDER BY id DESC
        LIMIT 30
    """)

    rows = cur.fetchall()
    conn.close()

    if not rows:
        text = "👨‍🔧 Ustalar ro‘yxati hozircha bo‘sh."
        keyboard = []
    else:
        text = "👨‍🔧 <b>USTALAR</b>\n\n"
        keyboard = []

        for mid, name, service, region, status in rows:
            text += f"🆔 {mid} | {name} | {service} | {region} | {status}\n"

            keyboard.append([
                InlineKeyboardButton(
                    f"👤 {name}",
                    callback_data=f"admin_master:{mid}"
                )
            ])

    keyboard.append([
        InlineKeyboardButton("⬅️ Admin panel", callback_data="admin_panel")
    ])

    await query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def admin_users(update, context):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        return

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(DISTINCT telegram_id) FROM masters")
    masters_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT customer_id) FROM orders")
    customers = cur.fetchone()[0]

    conn.close()

    text = (
        "👥 <b>FOYDALANUVCHILAR</b>\n\n"
        f"👨‍🔧 Usta sifatida ro‘yxatdan o‘tganlar: <b>{masters_users}</b>\n"
        f"👤 Buyurtma bergan mijozlar: <b>{customers}</b>"
    )

    await query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Admin panel", callback_data="admin_panel")]
        ])
    )


async def admin_orders(update, context):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        return

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT o.id, o.status, m.name, o.description
        FROM orders o
        LEFT JOIN masters m ON o.master_id=m.id
        ORDER BY o.id DESC
        LIMIT 20
    """)

    rows = cur.fetchall()
    conn.close()

    if not rows:
        text = "📦 Hozircha buyurtmalar yo‘q."
    else:
        text = "📦 <b>SO‘NGGI BUYURTMALAR</b>\n\n"

        for oid, status, master, description in rows:
            master = master or "Usta tanlanmagan"
            description = description[:60] if description else "-"

            text += (
                f"🆔 #{oid}\n"
                f"👨‍🔧 {master}\n"
                f"📌 {status}\n"
                f"📝 {description}\n\n"
            )

    await query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Admin panel", callback_data="admin_panel")]
        ])
    )


async def admin_reviews(update, context):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        return

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT r.rating, r.comment, m.name
        FROM reviews r
        LEFT JOIN masters m ON r.master_id=m.id
        ORDER BY r.id DESC
        LIMIT 20
    """)

    rows = cur.fetchall()
    conn.close()

    if not rows:
        text = "⭐ Hozircha baholar yo‘q."
    else:
        text = "⭐ <b>SO‘NGGI BAHOLAR</b>\n\n"

        for rating, comment, master in rows:
            master = master or "Noma'lum usta"
            comment = comment or "Izoh yo‘q"

            text += (
                f"👨‍🔧 {master}\n"
                f"⭐ {rating}/5\n"
                f"💬 {comment}\n\n"
            )

    await query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Admin panel", callback_data="admin_panel")]
        ])
    )


# =========================================================
# CALLBACK HANDLER
# =========================================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    data = query.data

    # =====================================================
    # ADMIN ROUTING
    # =====================================================

    if data == "admin_panel":
        await admin_panel(update, context)
        return

    if data == "admin_stats":
        await admin_stats(update, context)
        return

    if data == "admin_pending":
        await admin_pending(update, context)
        return

    if data == "admin_masters":
        await admin_masters(update, context)
        return

    if data == "admin_users":
        await admin_users(update, context)
        return

    if data == "admin_orders":
        await admin_orders(update, context)
        return

    if data == "admin_reviews":
        await admin_reviews(update, context)
        return

    if data.startswith("admin_master:"):
        master_id = int(data.split(":")[1])
        await admin_master(update, context, master_id)
        return

    if data.startswith("approve:"):
        master_id = int(data.split(":")[1])

        if query.from_user.id != ADMIN_ID:
            return

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            "UPDATE masters SET status='approved' WHERE id=?",
            (master_id,)
        )
        cur.execute(
            "SELECT telegram_id, name FROM masters WHERE id=?",
            (master_id,)
        )
        row = cur.fetchone()
        conn.commit()
        conn.close()

        if row:
            try:
                await context.bot.send_message(
                    chat_id=row[0],
                    text=(
                        "🎉 <b>Tabriklaymiz!</b>\n\n"
                        "Sizning USTA24 ustasi sifatidagi arizangiz "
                        "tasdiqlandi.\n\n"
                        "Endi mijozlar sizni topishi mumkin. 🔧"
                    ),
                    parse_mode="HTML"
                )
            except Exception as e:
                print("Ustaga xabar yuborilmadi:", e)

        await admin_pending(update, context)
        return

    if data.startswith("reject:"):
        master_id = int(data.split(":")[1])

        if query.from_user.id != ADMIN_ID:
            return

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            "UPDATE masters SET status='rejected' WHERE id=?",
            (master_id,)
        )
        conn.commit()
        conn.close()

        await admin_pending(update, context)
        return

    if data.startswith("block:"):
        master_id = int(data.split(":")[1])

        if query.from_user.id != ADMIN_ID:
            return

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            "UPDATE masters SET status='blocked' WHERE id=?",
            (master_id,)
        )
        conn.commit()
        conn.close()

        await admin_masters(update, context)
        return

    if data.startswith("unblock:"):
        master_id = int(data.split(":")[1])

        if query.from_user.id != ADMIN_ID:
            return

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            "UPDATE masters SET status='approved' WHERE id=?",
            (master_id,)
        )
        conn.commit()
        conn.close()

        await admin_masters(update, context)
        return

    # query.answer() ataylab ishlatilmayapti.
    # Oldingi versiyada Telegram callback timeout muammosi bo'lgan.

    # -----------------------------------------------------
    # HOME
    # -----------------------------------------------------

    if data == "home":

        keyboard = [
            [
                InlineKeyboardButton(
                    "🔎 USTA TOPISH",
                    callback_data="find_master"
                ),
                InlineKeyboardButton(
                    "📋 BUYURTMA BERISH",
                    callback_data="find_master"
                ),
            ],
            [
                InlineKeyboardButton(
                    "🛠 USTA BO‘LISH",
                    callback_data="become_master"
                ),
            ],
            [
                InlineKeyboardButton(
                    "📂 XIZMATLAR",
                    callback_data="services"
                ),
                InlineKeyboardButton(
                    "👤 PROFIL",
                    callback_data="profile"
                ),
            ],
            [
                InlineKeyboardButton(
                    "📦 BUYURTMALARIM",
                    callback_data="my_orders"
                ),
            ],
            [
                InlineKeyboardButton(
                    "ℹ️ USTA24 HAQIDA",
                    callback_data="about"
                ),
            ],
        ]

        if query.from_user.id == ADMIN_ID:
            keyboard.append([
                InlineKeyboardButton(
                    "🛠 ADMIN PANEL",
                    callback_data="admin_panel"
                )
            ])

        await query.message.edit_text(
            "🔧 <b>USTA24</b>\n\n"
            "Kerakli xizmatni tanlang:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return

    # -----------------------------------------------------
    # FIND MASTER
    # -----------------------------------------------------

    if data == "find_master":

        await show_services(update, context)

        return

    # -----------------------------------------------------
    # SERVICES
    # -----------------------------------------------------

    if data == "services":

        await show_services(update, context)

        return

    # -----------------------------------------------------
    # SERVICE SELECT
    # -----------------------------------------------------

    if data.startswith("service:"):

        service = data.split(":", 1)[1]

        # Tanlangan xizmatni vaqtincha saqlaymiz
        context.user_data["selected_service"] = service

        # "Boshqa" bo‘lsa ham hudud tanlashni davom ettiramiz
        await show_regions(update, context)

        return

    # -----------------------------------------------------
    # REGION SELECT
    # -----------------------------------------------------

    if data == "back_regions":

        await show_regions(update, context)

        return


    if data.startswith("province:"):

        province_index = data.split(":", 1)[1]

        await show_districts(
            update,
            context,
            province_index
        )

        return


    if data == "all_regions":

        service = context.user_data.get("selected_service")

        if service == "🛠 Boshqa":
            service = None

        await show_masters(
            update,
            context,
            service=service,
            region=None
        )

        return


    if data.startswith("district:"):

        parts = data.split(":")

        if len(parts) != 3:
            return

        province_index = int(parts[1])
        district_index = int(parts[2])

        region_names = list(REGIONS.keys())

        if province_index < 0 or province_index >= len(region_names):
            return

        province = region_names[province_index]
        districts = REGIONS[province]

        if district_index < 0 or district_index >= len(districts):
            return

        district = districts[district_index]

        service = context.user_data.get("selected_service")

        if service == "🛠 Boshqa":
            service = None

        # Masterning eski va yangi hudud yozuvlarini
        # moslashtirish uchun viloyat + tuman bo‘yicha qidiramiz.
        region = district

        await show_masters(
            update,
            context,
            service=service,
            region=region
        )

        return


    # -----------------------------------------------------
    # MASTER PROFILE
    # -----------------------------------------------------

    if data.startswith("master:"):

        master_id = int(
            data.split(":", 1)[1]
        )

        await show_master_profile(
            update,
            context,
            master_id
        )

        return

    # -----------------------------------------------------
    # ORDER MASTER
    # -----------------------------------------------------

    if data.startswith("order_master:"):

        master_id = int(
            data.split(":", 1)[1]
        )

        await start_order(
            update,
            context,
            master_id
        )

        return

    # -----------------------------------------------------
    # PHONE
    # -----------------------------------------------------

    if data.startswith("phone:"):

        master_id = int(
            data.split(":", 1)[1]
        )

        conn = db()
        cur = conn.cursor()

        cur.execute(
            "SELECT name, phone FROM masters WHERE id=?",
            (master_id,)
        )

        master = cur.fetchone()

        conn.close()

        if master:

            await query.message.reply_text(
                f"📞 <b>{master[0]}</b>\n\n"
                f"Telefon: <code>{master[1]}</code>",
                parse_mode="HTML"
            )

        return

    # -----------------------------------------------------
    # MASTER LOCATION
    # -----------------------------------------------------

    if data.startswith("master_location:"):

        await query.message.reply_text(
            "📍 Ustaning aniq lokatsiyasi buyurtma jarayonida "
            "mijoz va usta o‘rtasida yuboriladi."
        )

        return

    # -----------------------------------------------------
    # REVIEWS
    # -----------------------------------------------------

    if data.startswith("reviews:"):

        master_id = int(
            data.split(":", 1)[1]
        )

        await show_reviews(
            update,
            context,
            master_id
        )

        return

    # -----------------------------------------------------
    # MY ORDERS
    # -----------------------------------------------------

    if data == "my_orders":

        await show_orders(
            update,
            context
        )

        return

    # -----------------------------------------------------
    # PROFILE
    # -----------------------------------------------------

    if data == "profile":

        await show_profile(
            update,
            context
        )

        return

    # -----------------------------------------------------
    # ABOUT
    # -----------------------------------------------------

    if data == "about":

        await query.message.edit_text(
            "🔧 <b>USTA24</b>\n\n"
            "USTA24 — mijozlar va xizmat ko‘rsatuvchi "
            "ustalarni bog‘lovchi marketplace.\n\n"
            "🔎 Usta topish\n"
            "📋 Buyurtma berish\n"
            "📍 Lokatsiya yuborish\n"
            "⭐ Baholash\n"
            "🛠 Usta bo‘lish\n\n"
            "Maqsadimiz — kerakli ustani tez va qulay "
            "topishga yordam berish.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "⬅️ BOSH MENYU",
                        callback_data="home"
                    )
                ]
            ])
        )

        return

    # =====================================================
    # MASTER REGISTRATION
    # =====================================================

    if data == "become_master":

        context.user_data.clear()
        context.user_data["register_step"] = "name"

        await query.message.edit_text(
            "🛠 <b>USTA BO‘LISH</b>\n\n"
            "1️⃣ Ism va familiyangizni yozing:",
            parse_mode="HTML"
        )

        return

    # =====================================================
    # MASTER SERVICE
    # =====================================================

    if data.startswith("reg_service:"):

        service = data.split(":", 1)[1]

        if service == "🛠 Boshqa":

            context.user_data["register_step"] = "custom_service"

            await query.message.edit_text(
                "🛠 Qaysi xizmatni ko‘rsatasiz?\n\n"
                "Xizmat nomini yozing:"
            )

        else:

            context.user_data["service"] = service
            context.user_data["register_step"] = "region"

            await query.message.edit_text(
                "📍 Qaysi hududda xizmat ko‘rsatasiz?\n\n"
                "Masalan: Samarqand shahri"
            )

        return

    # =====================================================
    # ADMIN APPROVE
    # =====================================================

    if data.startswith("approve:"):

        if update.effective_user.id != ADMIN_ID:
            return

        master_id = int(
            data.split(":", 1)[1]
        )

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            UPDATE masters
            SET status='approved'
            WHERE id=?
        """, (master_id,))

        cur.execute("""
            SELECT telegram_id, name
            FROM masters
            WHERE id=?
        """, (master_id,))

        master = cur.fetchone()

        conn.commit()
        conn.close()

        await query.message.edit_text(
            "✅ USTA TASDIQLANDI!"
        )

        if master:

            await context.bot.send_message(
                chat_id=master[0],
                text=(
                    "🎉 <b>TABRIKLAYMIZ!</b>\n\n"
                    "Sizning USTA24 arizangiz tasdiqlandi.\n"
                    "Endi mijozlar sizni topishi mumkin."
                ),
                parse_mode="HTML"
            )

        return

    # =====================================================
    # ADMIN REJECT
    # =====================================================

    if data.startswith("reject_master:"):

        if update.effective_user.id != ADMIN_ID:
            return

        master_id = int(
            data.split(":", 1)[1]
        )

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            UPDATE masters
            SET status='rejected'
            WHERE id=?
        """, (master_id,))

        cur.execute("""
            SELECT telegram_id
            FROM masters
            WHERE id=?
        """, (master_id,))

        master = cur.fetchone()

        conn.commit()
        conn.close()

        await query.message.edit_text(
            "❌ USTA ARIZASI RAD ETILDI."
        )

        if master:

            await context.bot.send_message(
                chat_id=master[0],
                text=(
                    "❌ USTA24 arizangiz rad etildi.\n\n"
                    "Ma'lumotlaringizni tekshirib qayta "
                    "ro‘yxatdan o‘tishingiz mumkin."
                )
            )

        return

    # =====================================================
    # ACCEPT ORDER
    # =====================================================

    if data.startswith("accept_order:"):

        order_id = int(
            data.split(":", 1)[1]
        )

        user_id = update.effective_user.id

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                o.customer_id,
                o.master_id
            FROM orders o
            JOIN masters m
                ON o.master_id=m.id
            WHERE o.id=?
            AND m.telegram_id=?
        """, (order_id, user_id))

        order = cur.fetchone()

        if not order:
            conn.close()
            return

        customer_id, master_id = order

        cur.execute("""
            UPDATE orders
            SET status='accepted'
            WHERE id=?
        """, (order_id,))

        conn.commit()
        conn.close()

        await query.message.edit_text(
            f"✅ <b>BUYURTMA №{order_id} QABUL QILINDI!</b>\n\n"
            "Mijozga xabar yuborildi.\n\n"
            "Ish tugagach quyidagi tugmani bosing:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🏁 ISHNI TUGATISH",
                        callback_data=f"finish_order:{order_id}"
                    )
                ]
            ])
        )

        await context.bot.send_message(
            chat_id=customer_id,
            text=(
                f"🟢 <b>BUYURTMA №{order_id}</b>\n\n"
                "Usta buyurtmangizni qabul qildi. ✅\n"
                "Ish jarayonini usta bilan kelishib oling."
            ),
            parse_mode="HTML"
        )

        return

    # =====================================================
    # REJECT ORDER
    # =====================================================

    if data.startswith("reject_order:"):

        order_id = int(
            data.split(":", 1)[1]
        )

        user_id = update.effective_user.id

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            SELECT o.customer_id
            FROM orders o
            JOIN masters m
                ON o.master_id=m.id
            WHERE o.id=?
            AND m.telegram_id=?
        """, (order_id, user_id))

        order = cur.fetchone()

        if not order:
            conn.close()
            return

        customer_id = order[0]

        cur.execute("""
            UPDATE orders
            SET status='rejected'
            WHERE id=?
        """, (order_id,))

        conn.commit()
        conn.close()

        await query.message.edit_text(
            f"❌ Buyurtma №{order_id} rad etildi."
        )

        await context.bot.send_message(
            chat_id=customer_id,
            text=(
                f"🔴 <b>BUYURTMA №{order_id}</b>\n\n"
                "Afsuski, tanlangan usta buyurtmani "
                "qabul qilmadi.\n\n"
                "Boshqa ustani tanlashingiz mumkin."
            ),
            parse_mode="HTML"
        )

        return

    # =====================================================
    # FINISH ORDER
    # =====================================================

    if data.startswith("finish_order:"):

        order_id = int(
            data.split(":", 1)[1]
        )

        user_id = update.effective_user.id

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                o.customer_id,
                o.master_id
            FROM orders o
            JOIN masters m
                ON o.master_id=m.id
            WHERE o.id=?
            AND m.telegram_id=?
            AND o.status='accepted'
        """, (order_id, user_id))

        order = cur.fetchone()

        if not order:
            conn.close()
            return

        customer_id, master_id = order

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

        await query.message.edit_text(
            f"🏁 <b>BUYURTMA №{order_id}</b>\n\n"
            "Ish tugallangan deb belgilandi. ✅",
            parse_mode="HTML"
        )

        rating_keyboard = [
            [
                InlineKeyboardButton(
                    "⭐ 1",
                    callback_data=f"rate:{order_id}:1"
                ),
                InlineKeyboardButton(
                    "⭐ 2",
                    callback_data=f"rate:{order_id}:2"
                ),
                InlineKeyboardButton(
                    "⭐ 3",
                    callback_data=f"rate:{order_id}:3"
                ),
                InlineKeyboardButton(
                    "⭐ 4",
                    callback_data=f"rate:{order_id}:4"
                ),
                InlineKeyboardButton(
                    "⭐ 5",
                    callback_data=f"rate:{order_id}:5"
                ),
            ]
        ]

        await context.bot.send_message(
            chat_id=customer_id,
            text=(
                f"🏁 <b>BUYURTMA №{order_id}</b>\n\n"
                "Ish tugallandi.\n\n"
                "⭐ Ustaga baho bering:"
            ),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(rating_keyboard)
        )

        return

    # =====================================================
    # RATING
    # =====================================================

    if data.startswith("rate:"):

        parts = data.split(":")

        order_id = int(parts[1])
        rating = int(parts[2])

        customer_id = update.effective_user.id

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            SELECT master_id
            FROM orders
            WHERE id=?
            AND customer_id=?
            AND status='completed'
        """, (order_id, customer_id))

        order = cur.fetchone()

        if not order:
            conn.close()
            return

        master_id = order[0]

        cur.execute("""
            SELECT id
            FROM reviews
            WHERE order_id=?
        """, (order_id,))

        existing = cur.fetchone()

        if not existing:

            cur.execute("""
                INSERT INTO reviews
                (
                    order_id,
                    master_id,
                    customer_id,
                    rating,
                    comment
                )
                VALUES (?, ?, ?, ?, '')
            """, (
                order_id,
                master_id,
                customer_id,
                rating
            ))

            conn.commit()

        conn.close()

        await query.message.edit_text(
            f"⭐ <b>Rahmat!</b>\n\n"
            f"Siz ustaga {rating}/5 baho berdingiz. 👍",
            parse_mode="HTML"
        )

        return


# =========================================================
# MATN HANDLER
# =========================================================

async def text_handler(update, context):

    text = update.message.text

    # =====================================================
    # BUYURTMA
    # =====================================================

    order_step = context.user_data.get("order_step")

    if order_step == "description":

        context.user_data["order_description"] = text
        context.user_data["order_step"] = "budget"

        keyboard = [
            [
                InlineKeyboardButton(
                    "🤝 Kelishiladi",
                    callback_data="budget:Kelishiladi"
                )
            ]
        ]

        await update.message.reply_text(
            "💰 <b>Budjetni kiriting</b>\n\n"
            "Masalan: 100 000 so‘m\n\n"
            "Yoki:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return

    if order_step == "budget":

        context.user_data["order_budget"] = text
        context.user_data["order_step"] = "location"

        await update.message.reply_text(
            "📍 Endi buyurtma joylashgan manzilingizni "
            "Telegram orqali yuboring.\n\n"
            "Pastdagi 📎 tugma orqali <b>Location</b> yuboring.",
            parse_mode="HTML"
        )

        return

    # =====================================================
    # USTA RO‘YXATDAN O‘TISH
    # =====================================================

    register_step = context.user_data.get("register_step")

    if register_step == "name":

        context.user_data["name"] = text
        context.user_data["register_step"] = "service"

        keyboard = []

        for i in range(0, len(SERVICES), 2):

            row = []

            row.append(
                InlineKeyboardButton(
                    SERVICES[i],
                    callback_data=f"reg_service:{SERVICES[i]}"
                )
            )

            if i + 1 < len(SERVICES):

                row.append(
                    InlineKeyboardButton(
                        SERVICES[i + 1],
                        callback_data=f"reg_service:{SERVICES[i + 1]}"
                    )
                )

            keyboard.append(row)

        await update.message.reply_text(
            "🔧 Qaysi xizmatni ko‘rsatasiz?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return

    if register_step == "custom_service":

        context.user_data["service"] = text
        context.user_data["register_step"] = "region"

        await update.message.reply_text(
            "📍 Qaysi hududda xizmat ko‘rsatasiz?\n\n"
            "Masalan: Samarqand shahri"
        )

        return

    if register_step == "region":

        context.user_data["region"] = text
        context.user_data["register_step"] = "phone"

        await update.message.reply_text(
            "📞 Telefon raqamingizni yuboring.\n\n"
            "Masalan: +998901234567"
        )

        return

    if register_step == "phone":

        context.user_data["phone"] = text
        context.user_data["register_step"] = "price"

        await update.message.reply_text(
            "💰 Xizmat narxingizni yozing.\n\n"
            "Masalan:\n"
            "100 000 so‘mdan\n"
            "yoki\n"
            "Kelishiladi"
        )

        return

    if register_step == "price":

        context.user_data["price"] = text
        context.user_data["register_step"] = "about"

        await update.message.reply_text(
            "📝 <b>O‘zingiz haqingizda yozing:</b>\n\n"
            "Masalan:\n"
            "10 yildan beri santexnik bo‘lib ishlayman. "
            "Suv quvurlari, kran va kanalizatsiya ta’mirlash "
            "xizmatlarini ko‘rsataman.\n\n"
            "Qancha ko‘p ma’lumot bersangiz, mijozlar sizni "
            "shuncha yaxshi tanishadi.",
            parse_mode="HTML"
        )

        return

    if register_step == "about":

        context.user_data["about"] = text

        await save_master(update, context)

        return


# =========================================================
# BUDJET CALLBACK
# =========================================================

async def budget_handler(update, context):

    query = update.callback_query

    data = query.data

    if not data.startswith("budget:"):
        return

    budget = data.split(":", 1)[1]

    context.user_data["order_budget"] = budget
    context.user_data["order_step"] = "location"

    await query.message.edit_text(
        "📍 Endi buyurtma joylashgan manzilingizni "
        "Telegram orqali yuboring.\n\n"
        "📎 Tugma orqali <b>Location</b> yuboring.",
        parse_mode="HTML"
    )


# =========================================================
# CONTACT HANDLER
# =========================================================

async def contact_handler(update, context):

    contact = update.message.contact

    register_step = context.user_data.get("register_step")

    if register_step != "phone":
        return

    context.user_data["phone"] = contact.phone_number
    context.user_data["register_step"] = "price"

    await update.message.reply_text(
        "💰 Xizmat narxingizni yozing.\n\n"
        "Masalan:\n"
        "100 000 so‘mdan\n"
        "yoki\n"
        "Kelishiladi"
    )


# =========================================================
# LOCATION HANDLER
# =========================================================

async def location_handler(update, context):

    order_step = context.user_data.get("order_step")

    if order_step != "location":
        return

    await create_order(
        update,
        context
    )


# =========================================================
# USTA SAQLASH
# =========================================================

async def save_master(update, context):

    user_id = update.effective_user.id

    name = context.user_data.get("name")
    service = context.user_data.get("service")
    region = context.user_data.get("region")
    phone = context.user_data.get("phone")
    price = context.user_data.get("price")

    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM masters
        WHERE telegram_id=?
    """, (user_id,))

    existing = cur.fetchone()

    if existing:

        cur.execute("""
            UPDATE masters
            SET name=?,
                service=?,
                region=?,
                phone=?,
                price=?,
                status='pending'
            WHERE telegram_id=?
        """, (
            name,
            service,
            region,
            phone,
            price,
            user_id
        ))

        master_id = existing[0]

    else:

        cur.execute("""
            INSERT INTO masters
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
            user_id,
            name,
            service,
            region,
            phone,
            price
        ))

        master_id = cur.lastrowid

    conn.commit()
    conn.close()

    context.user_data.clear()

    await update.message.reply_text(
        "✅ <b>ARIZANGIZ QABUL QILINDI!</b>\n\n"
        "Administrator ma’lumotlaringizni tekshiradi.\n"
        "Tasdiqlangandan keyin profilingiz USTA24 "
        "ro‘yxatida ko‘rinadi.",
        parse_mode="HTML"
    )

    # ADMIN GA XABAR
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ TASDIQLASH",
                callback_data=f"approve:{master_id}"
            ),
            InlineKeyboardButton(
                "❌ RAD ETISH",
                callback_data=f"reject_master:{master_id}"
            ),
        ]
    ]

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "🔔 <b>YANGI USTA ARIZASI</b>\n\n"
            f"👤 Ism: {name}\n"
            f"🔧 Xizmat: {service}\n"
            f"📍 Hudud: {region}\n"
            f"📞 Telefon: {phone}\n"
            f"💰 Narx: {price}\n"
            f"🆔 Telegram ID: {user_id}"
        ),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# ERROR HANDLER
# =========================================================

async def error_handler(update, context):

    print(
        "XATO:",
        repr(context.error)
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print("===================================")
    print("🚀 USTA24 MODERN BOT ISHLAYAPTI")
    print(f"🌐 PORT: {PORT}")
    print("===================================")

    # Render port
    health_thread = threading.Thread(
        target=run_health_server,
        daemon=True
    )

    health_thread.start()

    # Telegram timeout sozlamalari
    request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0,
    )

    get_updates_request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0,
    )

    application = (
        Application.builder()
        .token(TOKEN)
        .request(request)
        .get_updates_request(get_updates_request)
        .build()
    )

    # Handlers
    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            budget_handler,
            pattern=r"^budget:"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )

    application.add_handler(
        MessageHandler(
            filters.CONTACT,
            contact_handler
        )
    )

    application.add_handler(
        MessageHandler(
            filters.LOCATION,
            location_handler
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_handler
        )
    )

    application.add_error_handler(
        error_handler
    )

    print("🤖 Telegram bot ishga tushmoqda...")

    application.run_polling(
        drop_pending_updates=True
    )


# =========================================================
# START PROGRAM
# =========================================================

if __name__ == "__main__":
    main()
