import os
import re
import json
import threading

import discord
from discord.ext import commands
from flask import Flask

TOKEN = os.getenv("DISCORD_TOKEN")
POINTS_ROLE_NAME = "point"
DATA_FILE = "points.json"

app = Flask(__name__)


@app.route("/")
def home():
    return "Points Bot is online!"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="=",
    intents=intents,
    help_command=None
)


def load_points():
    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


def save_points():
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(
            points,
            file,
            ensure_ascii=False,
            indent=4
        )


points = load_points()


def has_points_role(member):
    return any(
        role.name == POINTS_ROLE_NAME
        for role in member.roles
    )


@bot.event
async def on_ready():
    print(f"✅ تم تشغيل البوت: {bot.user}")


@bot.command(name="نقاط")
async def points_command(
    ctx,
    member: discord.Member = None,
    amount: str = None
):

    if member is not None and amount is None:
        user_points = points.get(
            str(member.id),
            0
        )

        await ctx.send(
            f"⭐ نقاط {member.mention}: **{user_points}**"
        )
        return

    if not has_points_role(ctx.author):
        await ctx.send(
            "❌ ما عندك رتبة point لإدارة النقاط."
        )
        return

    if member is None:
        await ctx.send(
            "❌ الاستخدام الصحيح:\n"
            "`=نقاط @العضو +6`\n"
            "`=نقاط @العضو -6`"
        )
        return

    if amount is None:
        await ctx.send(
            "❌ اكتب عدد النقاط."
        )
        return

    match = re.fullmatch(
        r"([+-])(\d+)",
        amount
    )

    if not match:
        await ctx.send(
            "❌ الاستخدام الصحيح:\n"
            "`=نقاط @العضو +6`\n"
            "`=نقاط @العضو -6`"
        )
        return

    sign = match.group(1)
    number = int(match.group(2))

    user_id = str(member.id)
    old_points = points.get(user_id, 0)

    if sign == "+":
        new_points = old_points + number
        action = "إضافة"
    else:
        new_points = max(0, old_points - number)
        action = "خصم"

    points[user_id] = new_points
    save_points()

    await ctx.send(
        f"✅ تم {action} {number} نقطة "
        f"لـ {member.mention}\n"
        f"⭐ مجموع نقاطه الآن: **{new_points}**"
    )


@bot.command(name="توب")
async def leaderboard(ctx):

    if not points:
        await ctx.send("❌ لا توجد نقاط حتى الآن.")
        return

    sorted_points = sorted(
        points.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    message = "🏆 **توب النقاط**\n\n"

    for i, (user_id, score) in enumerate(
        sorted_points,
        start=1
    ):
        member = ctx.guild.get_member(int(user_id))

        if member:
            name = member.mention
        else:
            name = f"<@{user_id}>"

        message += (
            f"**{i}.** {name} — "
            f"⭐ **{score}**\n"
        )

    await ctx.send(message)


@bot.command(name="مساعدة")
async def help_command(ctx):
    await ctx.send(
        "**📌 أوامر النقاط**\n\n"
        "`=نقاط @العضو +6` — إضافة نقاط\n"
        "`=نقاط @العضو -6` — خصم نقاط\n"
        "`=نقاط @العضو` — عرض النقاط\n"
        "`=توب` — أفضل 10 أعضاء"
    )


if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN غير موجود")


web_thread = threading.Thread(
    target=run_web,
    daemon=True
)

web_thread.start()

bot.run(TOKEN)
