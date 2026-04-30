import discord
from discord.ext import commands
import os
import asyncio
from config import TOKEN, PREFIX

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'FFZ BOT ON • Logado como {bot.user}')
    print(f'ID: {bot.user.id}')
    print('------')
    
    # Carrega todos os cogs automaticamente
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'Cog carregado: {filename}')
            except Exception as e:
                print(f'Erro ao carregar {filename}: {e}')

@bot.command()
@commands.is_owner()
async def reload(ctx, cog: str):
    try:
        await bot.reload_extension(f'cogs.{cog}')
        await ctx.send(f'✅ Cog `{cog}` recarregado!')
    except Exception as e:
        await ctx.send(f'❌ Erro: {e}')

bot.run(TOKEN)
