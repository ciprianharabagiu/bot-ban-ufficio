import discord
import os
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# INSERISCI QUI L'ID DEL TUO CANALE TRAPPOLA
TRAP_CHANNEL_ID = 1562519108954751196  

MESSAGE_ID = None
ban_count = 0

@bot.event
async def on_ready():
    print(f'Bot online! Connesso come: {bot.user}')

@bot.event
async def on_message(message):
    global ban_count, MESSAGE_ID

    if message.author.bot:
        return

    if message.channel.id == TRAP_CHANNEL_ID:
        try:
            await message.delete()
            await message.guild.ban(message.author, reason="Canale vietato - Ban automatico")
            ban_count += 1

            embed = discord.Embed(
                title="DO NOT WRITE IN THIS CHANNEL",
                description="YOU WILL BE BANNED AUTOMATICALLY",
                color=discord.Color.red()
            )
            embed.add_field(name="", value=f"**Ban counter:** {ban_count}", inline=False)

            if MESSAGE_ID:
                msg = await message.channel.fetch_message(MESSAGE_ID)
                await msg.edit(embed=embed)
            else:
                new_msg = await message.channel.send(embed=embed)
                MESSAGE_ID = new_msg.id

        except discord.Forbidden:
            print("Errore: Il bot non ha permessi sufficienti o la gerarchia dei ruoli è errata.")
        except Exception as e:
            print(f"Errore: {e}")

# INSERISCI QUI IL TOKEN DEL TUO BOT TRA LE VIRGOLETTE
bot.run(os.getenv("DISCORD_TOKEN"))