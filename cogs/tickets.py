import discord
from discord.ext import commands
from discord.ui import View, Button, Select
import asyncio
from config import COR_FFZ, URL_THUMBNAIL_FFZ, ID_CANAL_TICKET, CARGOS_SUPORTE, NOME_CARGO_STAFF, NOME_CARGO_MED
from utils import tem_cargo_suporte

class BotaoAssumir(Button):
    def __init__(self):
        super().__init__(label="Assumir Ticket", style=discord.ButtonStyle.success, emoji="🫡", custom_id="assumir_ticket_ffz")

    async def callback(self, interaction: discord.Interaction):
        if not tem_cargo_suporte(interaction.user, CARGOS_SUPORTE):
            return await interaction.response.send_message("Só STAFF, /SUPORTE ou GERENTE pode assumir.", ephemeral=True)
        thread = interaction.channel
        if "assumido-" in thread.name:
            return await interaction.response.send_message("Já foi assumido.", ephemeral=True)
        await thread.edit(name=f"assumido-{interaction.user.name}")
        embed = discord.Embed(title="🫡 Ticket Assumido", description=f"{interaction.user.mention} assumiu a bronca.", color=COR_FFZ)
        embed.set_thumbnail(url=URL_THUMBNAIL_FFZ)
        await interaction.response.send_message(embed=embed)

class BotaoFechar(Button):
    def __init__(self):
        super().__init__(label="Fechar Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="fechar_ticket_ffz")

    async def callback(self, interaction: discord.Interaction):
        if not any(discord.utils.get(interaction.guild.roles, name=cargo) in interaction.user.roles for cargo in ["STAFF", NOME_CARGO_MED, "GERENTE"]):
            return await interaction.response.send_message("Só cargo superior fecha.", ephemeral=True)
        await interaction.response.send_message("Fechando em 10s...", ephemeral=True)
        await asyncio.sleep(10)
        await interaction.channel.delete()

class ViewControleTicket(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(BotaoAssumir())
        self.add_item(BotaoFechar())

class MenuTicket(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Denúncia", description="Reportar player/partida", emoji="⚠️", value="denuncia"),
            discord.SelectOption(label="Suporte", description="Dúvidas gerais", emoji="🎫", value="suporte"),
            discord.SelectOption(label="Reembolso", description="Problema com pagamento", emoji="💰", value="reembolso"),
            discord.SelectOption(label="Vagas", description="Seja Staff/Mediador", emoji="📝", value="vagas")
        ]
        super().__init__(placeholder="Escolha o tipo de ticket", custom_id="menu_ticket_ffz", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        canal_ticket = interaction.guild.get_channel(ID_CANAL_TICKET)
        nome_thread = f"ticket-{self.values[0]}-{interaction.user.name}"
        thread = await canal_ticket.create_thread(name=nome_thread, type=discord.ChannelType.private_thread)
        await thread.add_user(interaction.user)
        mencoes = " ".join([c.mention for nome_cargo in CARGOS_SUPORTE if (c := discord.utils.get(interaction.guild.roles, name=nome_cargo))])
        embed = discord.Embed(title=f"🎫 Ticket de {self.values[0].capitalize()}", description=f"{interaction.user.mention} explica o problema.\n\n**Status:** Aguardando STAFF", color=COR_FFZ)
        embed.set_thumbnail(url=URL_THUMBNAIL_FFZ)
        await thread.send(content=f"{interaction.user.mention} {mencoes}", embed=embed, view=ViewControleTicket())
        await interaction.followup.send(f"Ticket criado: {thread.mention}", ephemeral=True)

class ViewTicket(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(MenuTicket())

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def painel_ffz(self, ctx):
        canal = self.bot.get_channel(ID_CANAL_TICKET)
        embed = discord.Embed(
            title="🎫 CENTRAL FFZ E-SPORTS",
            description="Abre teu ticket abaixo:\n\n**STAFF, /SUPORTE ou GERENTE: Primeiro assume, leva.**",
            color=COR_FFZ
        )
        embed.set_thumbnail(url=URL_THUMBNAIL_FFZ)
        embed.set_footer(text="FFZ E-SPORTS • 24h")
        await canal.send(content="@here", embed=embed, view=ViewTicket())
        await ctx.send("Painel FFZ no ar.", delete_after=5)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
