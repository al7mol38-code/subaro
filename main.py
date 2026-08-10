import os
import re
import json
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

PREFIX = "="
DATA_FILE = "points.json"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)


def load_points():
    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_points(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


points = load_points()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command(name="نقاط")
async def points_command(ctx, member: discord.Member = None, amount: str = None):

    if member is None:
        await ctx.send("❌ منشن العضو أولاً.")
        return

    # إذا كان الأمر مجرد =نقاط @عضو
    if amount is None:
        user_points = points.get(str(member.id), 0)

        await ctx.send(
            f"⭐ نقاط {member.mention}: **{user_points}**"
        )
        return

    # التحقق من الرقم
    match = re.fullmatch(r"([+-])(\d+)", amount)

    if not match:
        await ctx.send(
            "❌ الاستخدام الصحيح:\n"
            "`=نقاط @العضو +6`\n"
            "`=نقاط @العضو -6`"
        )
        return

    # منع الأعضاء العاديين من تعديل النقاط
    if not ctx.author.guild_permissions.manage_guild:
        await ctx.send("❌ ما عندك صلاحية تعديل النقاط.")
        return

    sign = match.group(1)
    number = int(match.group(2))

    user_id = str(member.id)

    old_points = points.get(user_id, 0)

    if sign == "+":
        new_points = old_points + number
    else:
        new_points = max(0, old_points - number)

    points[user_id] = new_points
    save_points(points)

    if sign == "+":
        await ctx.send(
            f"✅ تمت إضافة {number} نقطة إلى {member.mention}\n"
            f"⭐ مجموع نقاطه: **{new_points}**"
        )
    else:
        await ctx.send(
            f"✅ تم خصم {number} نقطة من {member.mention}\n"
            f"⭐ مجموع نقاطه: **{new_points}**"
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

    text = "🏆 **توب النقاط**\n\n"

    for i, (user_id, score) in enumerate(sorted_points, start=1):
        member = ctx.guild.get_member(int(user_id))

        if member:
            name = member.mention
        else:
            name = f"<@{user_id}>"

        text += f"**{i}.** {name} — ⭐ **{score}**\n"

    await ctx.send(text)


@bot.command(name="مساعدة")
async def help_command(ctx):
    await ctx.send(
        "**📌 أوامر النقاط**\n\n"
        "`=نقاط @العضو +6` — إضافة نقاط\n"
        "`=نقاط @العضو -6` — خصم نقاط\n"
        "`=نقاط @العضو` — عرض نقاط العضو\n"
        "`=توب` — عرض أعلى 10 أعضاء"
    )


bot.run(TOKEN)
