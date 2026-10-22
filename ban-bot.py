import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import discord
from discord.ext import commands

# --- SERVER WEB FITTIZIO PER RENDER (204 No Content) ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(204)
        self.end_headers()
    def log_message(self, format, *args):
        pass

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

TRAP_CHANNEL_ID = 1562519108954751196  # ID del tuo canale trappola

async def get_or_create_trap_message(channel):
    bot_messages = []
    current_count = 0
    
    # Cerca i messaggi del bot nel canale
    async for msg in channel.history(limit=50):
        if msg.author == bot.user and msg.embeds:
            bot_messages.append(msg)
            
    if bot_messages:
        # Il primo della lista (il più recente) è quello principale da mantenere
        main_msg = bot_messages[0]
        try:
            field_value = main_msg.embeds[0].fields[0].value
            digits = "".join([c for c in field_value if c.isdigit()])
            current_count = int(digits) if digits else 0
        except Exception:
            current_count = 0
            
        # Cancella tutti gli altri duplicati più vecchi per fare pulizia
        for old_msg in bot_messages[1:]:
            try:
                await old_msg.delete()
            except:
                pass
        return main_msg, current_count
    else:
        # Se non esiste alcun messaggio, ne crea uno nuovo partendo da 0
        embed = discord.Embed(
            title="DO NOT WRITE IN THIS CHANNEL",
            description="YOU WILL BE BANNED AUTOMATICALLY",
            color=discord.Color.red()
        )
        embed.add_field(name="", value="**Ban counter:** 0", inline=False)
        new_msg = await channel.send(embed=embed)
        return new_msg, 0

@bot.event
async def on_ready():
    print(f'Bot online! Connesso come: {bot.user}')
    # All'avvio, assicura che ci sia un unico messaggio nel canale trappola
    channel = bot.get_channel(TRAP_CHANNEL_ID)
    if channel:
        await get_or_create_trap_message(channel)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id == TRAP_CHANNEL_ID:
        try:
            # 1. Cancella il messaggio dell'utente e banna
            await message.delete()
            await message.guild.ban(message.author, reason="Canale vietato - Ban automatico")

            # 2. Ottiene il messaggio unico del bot e legge il contatore attuale
            channel = message.channel
            main_msg, current_count = await get_or_create_trap_message(channel)

            # 3. Incrementa il contatore
            new_count = current_count + 1

            # 4. Crea l'embed aggiornato
            embed = discord.Embed(
                title="DO NOT WRITE IN THIS CHANNEL",
                description="YOU_WILL_BE_BANNED_AUTOMATICALLY", # se preferisci lo spaziato rimetti la stringa normale
                color=discord.Color.red()
            )
            embed.title = "DO NOT WRITE IN THIS CHANNEL"
            embed.description = "YOU WILL BE BANNED AUTOMATICALLY"
            embed.add_field(name="", value=f"**Ban counter:** {new_count}", inline=False)

            # 5. Modifica il messaggio esistente senza crearne altri
            await main_msg.edit(embed=embed)

        except discord.Forbidden:
            print("Errore: Il bot non ha permessi sufficienti o la gerarchia dei ruoli è errata.")
        except Exception as e:
            print(f"Errore: {e}")

bot.run(os.getenv("DISCORD_TOKEN"))
