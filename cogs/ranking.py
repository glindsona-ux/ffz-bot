import discord
from discord.ext import commands
from discord.ui import View, Button
from config import COR_FFZ, URL_THUMBNAIL_FFZ, ID_CANAL_RANKING, NOME_CARGO_STAFF
from utils import carregar_json

class ViewRanking(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="RANKING", style=discord.ButtonStyle.primary, emoji="🏆", custom_id="botao_ranking_ffz")
    async def ranking_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        ranking = carregar_json("ranking.json")
        sorted_geral = sorted(ranking.items(), key=lambda x: x[1].get("geral", 0), reverse=True)[:10]
        desc_geral = ""
        for i, (uid, dados) in enumerate(sorted_geral, 1):
            membro = interaction.guild.get_member(int(uid))
            nome = membro.display_name if membro else "Desconhecido"
            desc_geral += f"**{i}.** {nome} - {dados.get('geral', 0)} pts\n"

        embed = discord.Embed(title="🏆 RANKING FFZ E-SPORTS", color=COR_FFZ)
        embed.set_thumbnail(url=URL_THUMBNAIL_FFZ)
        embed.add_field(name="📊 GERAL", value=desc_geral or "Ninguém pontuou ainda", inline=False)

        sorted_semanal = sorted(ranking.items(), key=lambda x: x[1].get("semanal", 0), reverse=True)[:5]
        desc_semanal = ""
        for i, (uid, dados) in enumerate(sorted_semanal, 1):
            membro = interaction.guild.get_member(int(uid))
            nome = membro.display_name if membro else "Desconhecido"
            desc_semanal += f"**{i}.** {nome} - {dados.get('semanal', 0)} pts\n"
        embed.add_field(name="📅 SEMANAL", value=desc_semanal or "Ninguém pontuou ainda", inline=True)

        sorted_mensal = sorted(ranking.items(), key=lambda x: x[1].get("mensal", 0), reverse=True)[:5]
        desc_mensal = ""
        for i, (uid, dados) in enumerate(sorted_mensal, 1):
            membro = interaction.guild.get_member(int(uid))
            nome = membro.display_name if membro else "Desconhecido"
            desc_mensal += f"**{i}.** {nome} - {dados.get('mensal', 0)} pts\n"
        embed.add_field(name="🗓️ MENSAL", value=desc_mensal or "Ninguém pontuou ainda", inline=True)
        embed.set_footer(text="FFZ E-SPORTS • +3 pts por vitória")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="MEU PERFIL", style=discord.ButtonStyle.success, emoji="👤", custom_id="botao_perfil_ffz")
    async def perfil_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        ranking = carregar_json("ranking.json")
        user_id = str(interaction.user.id)
        dados = ranking.get(user_id, {"geral": 0, "semanal": 0, "mensal": 0, "vitorias": 0, "derrotas": 0})

        total = dados["vitorias"] + dados["derrotas"]
        winrate = (dados["vitorias"] / total * 100) if total > 0 else 0

        embed = discord.Embed(title=f"👤 PERFIL • {interaction.user.display_name}", color=COR_FFZ)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="🏆 Pontos Geral", value=f"{dados['geral']} pts", inline=True)
        embed.add_field(name="📅 Semanal", value=f"{dados['semanal']} pts", inline=True)
        embed.add_field(name="🗓️ Mensal", value=f"{dados['mensal']} pts", inline=True)
        embed.add_field(name="✅ Vitórias", value=str(dados["vitorias"]), inline=True)
        embed.add_field(name="❌ Derrotas", value=str(dados["derrotas"]), inline=True)
        embed.add_field(name="📊 Win Rate", value=f"{winrate:.1f}%", inline=True)
        embed.set_footer(text="FFZ E-SPORTS")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class Ranking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role(NOME_CARGO_STAFF)
    async def painel_rank(self, ctx):
        embed = discord.Embed(
            title="🏆 CENTRAL DE RANKING FFZ",
            description="**Veja o top players da FFZ E-SPORTS**\n\n🔵 **RANKING** - Top 10 Geral, Semanal e Mensal\n🟢 **MEU PERFIL** - Suas estatísticas pessoais\n\n**Sistema de pontos:** +3 por vitória",
            color=COR_FFZ
        )
        embed.set_thumbnail(url=URL_THUMBNAIL_FFZ)
        embed.set_footer(text="FFZ E-SPORTS • 24H")
        await self.bot.get_channel(ID_CANAL_RANKING).send(embed=embed, view=ViewRanking())
        await ctx.send("Painel de ranking postado!", delete_after=5)

async def setup(bot):
    await bot.add_cog(Ranking(bot))
