import os
import threading
from flask import Flask
from pymongo import MongoClient
import discord
from discord.ext import commands

# =========================
# إعدادات الرتب
# =========================

POINT_ROLE_ID = 1536368394868363344
CO_OWNER_ROLE_ID = 1533463570564649121
OWNER_ROLE_ID = 1533463569683845160

ALLOWED_ROLE_IDS = {
    POINT_ROLE_ID,
    CO_OWNER_ROLE_ID,
    OWNER_ROLE_ID
}

# =========================
# MongoDB
# =========================

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["pointsbot"]
points_collection = db["points"]

# =========================
# إعداد البوت
# =========================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="=",
    intents=intents,
    help_command=None
)

# =========================
# الدوال المساعدة
# =========================

def has_points_permission(member):
    return any(role.id in ALLOWED_ROLE_IDS for role in member.roles)

def get_points(user_id):
    user = points_collection.find_one({"_id": str(user_id)})
    return user["points"] if user else 0

def set_points(user_id, points):
    points_collection.update_one(
        {"_id": str(user_id)},
        {"$set": {"points": points}},
        upsert=True
    )

# =========================
# أحداث البوت (Events)
# =========================

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Bot Ready!")

# =========================
# الأوامر (Commands)
# =========================

@bot.command(name="مساعدة")
async def help_command(ctx):
    embed = discord.Embed(
        title="📋 أوامر البوت",
        description=(
            "`=نقاط @العضو +5` ➜ إضافة نقاط\n"
            "`=نقاط @العضو -5` ➜ خصم نقاط\n"
            "`=نقاط @العضو` ➜ عرض نقاط العضو\n"
            "`=توب` ➜ أفضل 10 أعضاء"
        ),
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)


@bot.command(name="نقاط")
async def points(ctx, member: discord.Member = None, amount: str = None):
    # إذا لم يتم تحديد عضو، يعرض نقاط مرسل الأمر تلقائياً
    if member is None:
        member = ctx.author

    # في حال استعلام عن نقاط العضو فقط (=نقاط @العضو)
    if amount is None:
        user_points = get_points(member.id)
        await ctx.send(f"⭐ نقاط {member.mention}: **{user_points}**")
        return

    # التعديل على النقاط يحتاج صلاحية
    if not has_points_permission(ctx.author):
        await ctx.send("❌ ليس لديك صلاحية لإضافة أو خصم النقاط.")
        return

    # محاولة تحويل المبلغ إلى رقم
    try:
        val = int(amount)
    except ValueError:
        await ctx.send("❌ صيغة المبلغ غير صحيحة! استخدم مثلاً: `=نقاط @العضو +5` أو `=نقاط @العضو -5`")
        return

    current = get_points(member.id)
    current += val

    if current < 0:
        current = 0

    set_points(member.id, current)

    if val >= 0:
        await ctx.send(f"✅ تمت إضافة **{val}** نقطة إلى {member.mention}\n⭐ المجموع: **{current}**")
    else:
        await ctx.send(f"✅ تم خصم **{abs(val)}** نقطة من {member.mention}\n⭐ المجموع: **{current}**")


@bot.command(name="توب")
async def top(ctx):
    users = list(
        points_collection.find().sort("points", -1).limit(10)
    )

    if not users:
        await ctx.send("📭 لا توجد نقاط حتى الآن.")
        return

    description = ""
    for index, user in enumerate(users, start=1):
        member = ctx.guild.get_member(int(user["_id"]))
        name = member.display_name if member else f"<@{user['_id']}>"
        description += f"**{index}.** {name} — ⭐ **{user['points']}**\n"

    embed = discord.Embed(
        title="🏆 Top Points",
        description=description,
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)

# =========================
# Flask (Keep Alive)
# =========================

app = Flask(__name__)

@app.route("/")
def home():
    return "Points Bot Online"

def run_flask():
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# =========================
# تشغيل البوت
# =========================

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN غير موجود في متغيرات البيئة Environment Variables")

    bot.run(token)
