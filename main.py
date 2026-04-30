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
    
    # BOTÕES IMORTAIS - REGISTRA AS VIEWS
    from cogs.ranking import ViewPainelRank
    from cogs.tickets import ViewPainelTicket
    from cogs.fila_med import ViewFilaMed
    from cogs.filas import ViewFilaX1
    from cogs.partidas import ViewRegistrarResultado
    
    bot.add_view(ViewPainelRank())
    bot.add_view(ViewPainelTicket())
    bot.add_view(ViewFilaMed())
    bot.add_view(ViewRegistrarResultado())
    
    # Pra cada modalidade da fila
    from config import IDS_CANAIS_MODALIDADES
    for modalidade in IDS_CANAIS_MODALIDADES.keys():
        bot.add_view(ViewFilaX1(modalidade))
    
    print("✅ Botões imortais registrados!")

@bot.command()
@commands.is_owner()
async def reload(ctx, cog: str):
    try:
        await bot.reload_extension(f'cogs.{cog}')
        await ctx.send(f'✅ Cog `{cog}` recarregado!')
    except Exception as e:
        await ctx.send(f'❌ Erro: {e}')

bot.run(TOKEN)
