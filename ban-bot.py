import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import discord
from discord.ext import commands

# --- SERVER WEB FITTIZIO (RISPOSTA VUOTA 204 PER EVITARE ERRORI) ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(204) # 204 No Content: risponde senza inviare dati pesanti
        self.end_headers()

    def log_message(self, format, *args):
        pass # Disattiva i log di accesso superflui nel terminale di Render

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# Avvia il server web in background prima del bot
threading.Thread(target=run_web_server, daemon=True).start()
# ----------------------------------------------------

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ID del tuo canale trappola
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

bot.run(os.getenv("DISCORD_TOKEN"))
