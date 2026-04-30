import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
import asyncio
from config import COR_FFZ, URL_THUMBNAIL_FFZ, ID_CANAL_PARTIDAS, ID_CANAL_LOG, NOME_CARGO_STAFF, NOME_CARGO_MED, TABELA_APOSTAS
from utils import carregar_json, salvar_json, add_pontos_ranking

class ViewWin(View):
    def __init__(self, time1, time2, valor):
        super().__init__(timeout=None)
        self.time1 = time1
        self.time2 = time2
        self.valor = valor

    @discord.ui.button(label="TIME 1 VENCEU", style=discord.ButtonStyle.success, custom_id="time1_win_ffz")
    async def time1_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await finalizar_partida(interaction, self.time1, self.time2, 1, self.valor)

    @discord.ui.button(label="TIME 2 VENCEU", style=discord.ButtonStyle.success, custom_id="time2_win_ffz")
    async def time2_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await finalizar_partida(interaction, self.time1, self.time2, 2, self.valor)

class ViewConfirmar(View):
    def __init__(self, time1, time2, valor):
        super().__init__(timeout=None)
        self.time1 = time1
        self.time2 = time2
        self.valor = valor
        self.confirmados = set()

    @discord.ui.button(label="CONFIRMAR PAGAMENTO", style=discord.ButtonStyle.primary, emoji="✅", custom_id="confirmar_pag_ffz")
    async def confirmar_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in self.time1 and interaction.user.id not in self.time2:
            return await interaction.response.send_message("Tu nem tá na partida!", ephemeral=True)

        self.confirmados.add(interaction.user.id)
        total = len(self.time1) + len(self.time2)

        if len(self.confirmados) >= total:
            embed = discord.Embed(title="✅ TODOS CONFIRMARAM", description="Partida liberada! Boa sorte.", color=COR_FFZ)
            await interaction.response.send_message(embed=embed)
            await interaction.channel.send("**AGUARDANDO RESULTADO:**", view=ViewWin(self.time1, self.time2, self.valor))
        else:
            await interaction.response.send_message(f"✅ Confirmado! {len(self.confirmados)}/{total}", ephemeral=True)

class ModalUIDSenha(Modal, title="UID E SENHA DA SALA"):
    uid = TextInput(label="UID da Sala", placeholder="123456789", max_length=20)
    senha = TextInput(label="Senha da Sala", placeholder="ffz2024", max_length=20)

    def __init__(self, time1, time2):
        super().__init__()
        self.time1 = time1
        self.time2 = time2

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🔐 DADOS DA PARTIDA", color=COR_FFZ)
        embed.add_field(name="UID", value=f"`{self.uid.value}`", inline=True)
        embed.add_field(name="SENHA", value=f"`{self.senha.value}`", inline=True)
        embed.set_footer(text="FFZ E-SPORTS • Bom jogo")
        await interaction.response.send_message(embed=embed)

class ViewPartida(View):
    def __init__(self, time1, time2, valor):
        super().__init__(timeout=None)
        self.time1 = time1
        self.time2 = time2
        self.valor = valor

    @discord.ui.button(label="ENVIAR UID/SENHA", style=discord.ButtonStyle.secondary, emoji="🔑", custom_id="uid_senha_ffz")
    async def uid_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not discord.utils.get(interaction.guild.roles, name=NOME_CARGO_MED) in interaction.user.roles:
            return await interaction.response.send_message("Só MEDIADOR envia UID/SENHA.", ephemeral=True)
        await interaction.response.send_modal(ModalUIDSenha(self.time1, self.time2))

async def finalizar_partida(interaction, time1, time2, vencedor, valor):
    if not discord.utils.get(interaction.guild.roles, name=NOME_CARGO_MED) in interaction.user.roles:
        return await interaction.response.send_message("Só MEDIADOR finaliza partida.", ephemeral=True)

    vencedores = time1 if vencedor == 1 else time2
    perdedores = time2 if vencedor == 1 else time1

    premio = TABELA_APOSTAS.get(valor, {}).get("premio", valor * 2)

    for uid in vencedores:
        add_pontos_ranking(uid, 3)
    for uid in perdedores:
        add_pontos_ranking(uid, -3)

    embed = discord.Embed(title=f"🏆 TIME {vencedor} VENCEU!", color=0x00FF00)
    embed.add_field(name="💰 Prêmio", value=f"R$ {premio:.2f}", inline=True)
    embed.add_field(name="Valor Apostado", value=f"R$ {valor:.2f}", inline=True)
    embed.set_footer(text="FFZ E-SPORTS • GG")

    await interaction.response.send_message(embed=embed)

    # Remove da fila
    filas = carregar_json("filas.json")
    for modalidade, lista in filas.items():
        filas[modalidade] = [u for u in lista if u not in time1 + time2]
    salvar_json("filas.json", filas)

    # Log
    log = interaction.guild.get_channel(ID_CANAL_LOG)
    if log:
        await log.send(embed=embed)

    await asyncio.sleep(30)
    await interaction.channel.delete()

async def criar_partida(guild, modalidade, jogadores):
    meio = len(jogadores) // 2
    time1 = jogadores[:meio]
    time2 = jogadores[meio:]

    canal_partidas = guild.get_channel(ID_CANAL_PARTIDAS)
    valor = 5.00 # Padrão, depois faz select de valor

    thread = await canal_partidas.create_thread(name=f"{modalidade}-{valor}", type=discord.ChannelType.private_thread)

    for uid in jogadores:
        membro = guild.get_member(uid)
        if membro:
            await thread.add_user(membro)

    embed = discord.Embed(title=f"🎮 PARTIDA {modalidade}", color=COR_FFZ)
    embed.add_field(name="TIME 1", value="\n".join([f"<@{uid}>" for uid in time1]), inline=True)
    embed.add_field(name="TIME 2", value="\n".join([f"<@{uid}>" for uid in time2]), inline=True)
    embed.add_field(name="💰 VALOR", value=f"R$ {valor:.2f}", inline=False)
    embed.set_footer(text="Confirme o pagamento para liberar UID/SENHA")

    await thread.send(embed=embed, view=ViewConfirmar(time1, time2, valor))
    await thread.send(view=ViewPartida(time1, time2, valor))

class Partidas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role(NOME_CARGO_STAFF)
    async def win(self, ctx, vencedor: int, valor: float):
        await ctx.send("Use os botões na partida para finalizar.", delete_after=5)

    @commands.command()
    @commands.has_role(NOME_CARGO_STAFF)
    async def resetfila(self, ctx, modalidade: str = None):
        filas = carregar_json("filas.json")
        if modalidade:
            filas[modalidade.upper()] = []
            await ctx.send(f"Fila {modalidade} resetada!")
        else:
            for mod in filas.keys():
                filas[mod] = []
            await ctx.send("Todas as filas resetadas!")
        salvar_json("filas.json", filas)

async def setup(bot):
    await bot.add_cog(Partidas(bot))
