import discord
from discord.ext import commands
from discord.ui import View, Button
import json
from config import COR_FFZ, URL_THUMBNAIL_FFZ, IDS_CANAIS_MODALIDADES, NOME_CARGO_STAFF
from utils import carregar_json, salvar_json

class ViewFila(View):
    def __init__(self, modalidade):
        super().__init__(timeout=None)
        self.modalidade = modalidade

    @discord.ui.button(label="JOGAR", style=discord.ButtonStyle.success, emoji="🎮", custom_id="jogar_fila_ffz")
    async def jogar_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        filas = carregar_json("filas.json")
        if self.modalidade not in filas:
            filas[self.modalidade] = []

        user_id = interaction.user.id
        if user_id in filas[self.modalidade]:
            return await interaction.response.send_message("Tu já tá na fila!", ephemeral=True)

        filas[self.modalidade].append(user_id)
        salvar_json("filas.json", filas)
        await atualizar_embed_fila(interaction.guild, self.modalidade)
        await interaction.response.send_message(f"✅ Entrou na fila {self.modalidade}!", ephemeral=True)

        # Verifica se bateu o mínimo pra criar partida
        from cogs.partidas import criar_partida
        min_players = 2 if "1X1" in self.modalidade else 4 if "2X2" in self.modalidade else 6 if "3X3" in self.modalidade else 8
        if len(filas[self.modalidade]) >= min_players:
            await criar_partida(interaction.guild, self.modalidade, filas[self.modalidade][:min_players])

    @discord.ui.button(label="SAIR", style=discord.ButtonStyle.danger, emoji="🚪", custom_id="sair_fila_ffz")
    async def sair_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        filas = carregar_json("filas.json")
        user_id = interaction.user.id

        if self.modalidade not in filas or user_id not in filas[self.modalidade]:
            return await interaction.response.send_message("Tu nem tá na fila!", ephemeral=True)

        filas[self.modalidade].remove(user_id)
        salvar_json("filas.json", filas)
        await atualizar_embed_fila(interaction.guild, self.modalidade)
        await interaction.response.send_message(f"❌ Saiu da fila {self.modalidade}!", ephemeral=True)

async def atualizar_embed_fila(guild, modalidade):
    filas = carregar_json("filas.json")
    canal_id = IDS_CANAIS_MODALIDADES.get(modalidade)
    if not canal_id:
        return
    canal = guild.get_channel(canal_id)

    jogadores = filas.get(modalidade, [])
    min_players = 2 if "1X1" in modalidade else 4 if "2X2" in modalidade else 6 if "3X3" in modalidade else 8

    desc = f"**FILA {modalidade}**\n\n"
    desc += f"**Jogadores: {len(jogadores)}/{min_players}**\n\n"

    if not jogadores:
        desc += "Ninguém na fila 😢"
    else:
        for i, user_id in enumerate(jogadores, 1):
            membro = guild.get_member(user_id)
            nome = membro.display_name if membro else "Desconhecido"
            desc += f"**{i}.** {nome}\n"

    embed = discord.Embed(title=f"🎮 {modalidade} • FFZ E-SPORTS", description=desc, color=COR_FFZ)
    embed.set_thumbnail(url=URL_THUMBNAIL_FFZ)
    embed.set_footer(text="Clique em JOGAR para entrar • FFZ E-SPORTS")

    async for msg in canal.history(limit=10):
        if msg.author == guild.me and msg.embeds and modalidade in msg.embeds[0].title:
            await msg.edit(embed=embed, view=ViewFila(modalidade))
            return
    await canal.send(embed=embed, view=ViewFila(modalidade))

class Filas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role(NOME_CARGO_STAFF)
    async def fila(self, ctx, modalidade: str = None):
        if not modalidade:
            await ctx.send("Use: `!fila 1X1-MOB` ou `!fila todas`")
            return

        if modalidade.lower() == "todas":
            for mod in IDS_CANAIS_MODALIDADES.keys():
                await atualizar_embed_fila(ctx.guild, mod)
            await ctx.send("Todas as filas criadas!", delete_after=5)
        else:
            modalidade = modalidade.upper()
            if modalidade not in IDS_CANAIS_MODALIDADES:
                return await ctx.send("Modalidade inválida!")
            await atualizar_embed_fila(ctx.guild, modalidade)
            await ctx.send(f"Fila {modalidade} criada!", delete_after=5)

async def setup(bot):
    await bot.add_cog(Filas(bot))
