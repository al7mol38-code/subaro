name = f"<@{user_id}>"

        description += f"**{rank}.** {name} — ⭐ **{points}**\n"

        rank += 1

    embed = discord.Embed(
        title="🏆 Top Points",
        description=description
    )

    await ctx.send(embed=embed)


# =========================
# Flask لإبقاء Render شغال
# =========================

app = Flask(__name__)


@app.route("/")
def home():
    return "Points Bot is online!"


def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(
        host="0.0.0.0",
        port=port
    )


# =========================
# تشغيل Flask + Discord
# =========================

if name == "__main__":

    flask_thread = threading.Thread(
        target=run_flask,
        daemon=True
    )

    flask_thread.start()

    token = os.environ.get("DISCORD_TOKEN")

    if not token:
        raise ValueError("DISCORD_TOKEN is missing!")

    bot.run(token)
