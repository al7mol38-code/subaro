import os
import json
import threading
from flask import Flask
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
# قاعدة البيانات
# =========================

DATA_FILE = "points.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)

data_lock = threading.Lock()


def load_points():
    with data_lock:
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}


def save_points(data):
    with data_lock:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


# =========================
# التحقق من الصلاحية
# =========================

def has_points_permission(member):
    return any(role.id in ALLOWED_ROLE_IDS for role in member.roles)


# =========================
# عند تشغيل البوت
# =========================

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Points Bot is ready!")


# =========================
# أمر المساعدة
# =========================

@bot.command(name="مساعدة")
async def help_command(ctx):
    embed = discord.Embed(
        title="📋 أوامر Points",
        description=(
            "`=نقاط @العضو +6` — إضافة نقاط\n"
            "`=نقاط @العضو -6` — خصم نقاط\n"
            "`=نقاط @العضو` — عرض نقاط عضو\n"
            "`=توب` — عرض أعلى الأعضاء\n"
            "`=مساعدة` — عرض هذه القائمة"
        )
    )

    await ctx.send(embed=embed)


# =========================
# أمر النقاط
# =========================

@bot.command(name="نقاط")
async def points_command(ctx, member: discord.Member = None, amount: int = None):

    # إذا كان الأمر بدون عضو
    if member is None:
        await ctx.send("❌ استخدم الأمر بهذا الشكل:\n`=نقاط @العضو +6`")
        return

    # إذا كان إضافة أو خصم
    if amount is not None:

        if not has_points_permission(ctx.author):
            await ctx.send("❌ ما عندك صلاحية استخدام أوامر النقاط.")
            return

        data = load_points()

        user_id = str(member.id)

        if user_id not in data:
            data[user_id] = 0

        data[user_id] += amount

        # منع النقاط من النزول تحت الصفر
        if data[user_id] < 0:
            data[user_id] = 0

        save_points(data)

        if amount > 0:
            await ctx.send(
                f"✅ تمت إضافة {amount} نقطة إلى {member.mention}\n"
                f"⭐ نقاطه الآن: **{data[user_id]}**"
            )
        else:
            await ctx.send(
                f"✅ تم خصم {abs(amount)} نقطة من {member.mention}\n"
                f"⭐ نقاطه الآن: **{data[user_id]}**"
            )

        return

    # عرض نقاط العضو
    data = load_points()
    user_id = str(member.id)

    points = data.get(user_id, 0)

    await ctx.send(
        f"⭐ نقاط {member.mention}: **{points}**"
    )


# =========================
# أمر التوب
# =========================

@bot.command(name="توب")
async def top_command(ctx):

    data = load_points()

    if not data:
        await ctx.send("📭 لا توجد نقاط حتى الآن.")
        return

    sorted_points = sorted(
        data.items(),
        key=lambda x: x[1],
        reverse=True
    )

    description = ""

    rank = 1

    for user_id, points in sorted_points[:10]:

        try:
            member = ctx.guild.get_member(int(user_id))

            if member:
                name = member.display_name
            else:
                name = f"<@{user_id}>"

        except:
