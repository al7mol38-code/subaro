# =========================
# المساعدة
# =========================

@bot.command(name="مساعدة")
async def help_command(ctx):

    await ctx.send(
        "**📌 أوامر النقاط**\n\n"
        "`=نقاط @العضو +6` — إضافة نقاط\n"
        "`=نقاط @العضو -6` — خصم نقاط\n"
        "`=نقاط @العضو` — عرض النقاط\n"
        "`=توب` — أفضل 10 أعضاء\n"
        "`=مساعدة` — الأوامر"
    )


# =========================
# تشغيل Web + Discord
# =========================

if not TOKEN:
    raise ValueError(
        "❌ لم يتم وضع DISCORD_TOKEN"
    )


web_thread = threading.Thread(
    target=run_web,
    daemon=True
)

web_thread.start()

bot.run(TOKEN)
