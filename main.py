guild.get_member(
            int(user_id)
        )

        if member:
            name = member.mention
        else:
            name = f"<@{user_id}>"

        message += (
            f"**{i}.** {name} — ⭐ **{score}**\n"
        )

    await ctx.send(message)


# =========================
# Help
# =========================

@bot.command(name="مساعدة")
async def help_command(ctx):

    await ctx.send(
        "**📌 أوامر النقاط**\n\n"
        "`=نقاط @العضو +6` — إضافة نقاط\n"
        "`=نقاط @العضو -6` — خصم نقاط\n"
        "`=نقاط @العضو` — عرض النقاط\n"
        "`=توب` — أفضل 10 أعضاء\n"
        "`=مساعدة` — المساعدة"
    )


# =========================
# Start
# =========================

if not TOKEN:
    raise ValueError(
        "❌ DISCORD_TOKEN غير موجود"
    )


web_thread = threading.Thread(
    target=run_web,
    daemon=True
)

web_thread.start()

bot.run(TOKEN)
