import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
from config import COR_FFZ, URL_THUMBNAIL_FFZ, ID_CANAL_FILA_MED, ID_CANAL_PIX_MED, NOME_CARGO_MED, NOME_CARGO_STAFF
from utils import carregar_json, salvar_json

class ModalConfiPix(Modal, title="Configurar PIX"):
    nome = TextInput(label="Nome Completo", placeholder="Ex: João da Silva", max_length=50)
    pix = TextInput(label="Chave PIX", placeholder="CPF, Email, Telefone ou Aleatória", max_length=100)

    async def on_submit(self, interaction: discord.Interaction):
        pix_data = carregar_json("pix_mediadores.json")
        pix_data[str(interaction.user.id)] = {"nome": self.nome.value, "chave": self.pix.value}
        salvar_json("pix_mediadores.json", pix_data)
        await interaction.response.send_message(f"✅ PIX configurado!\n**Nome:** {self.nome.value}\n**Chave:** `{self.pix.value}`", ephemeral=True)

class ViewMediadores(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Entrar na Fila", style=discord.ButtonStyle.success, emoji="✅", custom_id="entrar_fila_med_ffz")
    async def entrar_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not discord.utils.get(interaction.guild.roles, name=NOME_CARGO_MED) in interaction.user.roles:
            return await interaction.response.send_message("Só MEDIADOR pode entrar na fila.", ephemeral=True)

        fila = carregar_json("fila_mediadores.json")
        user_id = interaction.user.id

        if user_id in fila:
            return await interaction.response.send_message("Tu já tá na fila!", ephemeral=True)

        fila.append(user_id)
        salvar_json("fila_mediadores.json", fila)
        await atualizar_embed_fila_med(interaction.guild)
        await interaction.response.send_message("✅ Tu entrou na fila de mediadores!", ephemeral=True)

    @discord.ui.button(label="Sair da Fila", style=discord.ButtonStyle.danger, emoji="❌", custom_id="sair_fila_med_ffz")
    async def sair_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        fila = carregar_json("fila_mediadores.json")
        user_id = interaction.user.id

        if user_id not in fila:
            return await interaction.response.send_message("Tu nem tá na fila!", ephemeral=True)

        fila.remove(user_id)
        salvar_json("fila_mediadores.json", fila)
        await atualizar_embed_fila_med(interaction.guild)
        await interaction.response.send_message("❌ Tu saiu da fila de mediadores!", ephemeral=True)

    @discord.ui.button(label="Cadastrar PIX", style=discord.ButtonStyle.primary, emoji="💰", custom_id="cad_pix_med_ffz")
    async def pix_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not discord.utils.get(interaction.guild.roles, name=NOME_CARGO_MED) in interaction.user.roles:
            return await interaction.response.send_message("Só MEDIADOR pode cadastrar PIX.", ephemeral=True)
        await interaction.response.send_modal(ModalConfiPix())

async def atualizar_embed_fila_med(guild):
    fila = carregar_json("fila_mediadores.json")
    canal = guild.get_channel(ID_CANAL_FILA_MED)

    desc = "**MEDIADORES DISPONÍVEIS:**\n\n"
    if not fila:
        desc += "Nenhum mediador na fila 😢"
    else:
        for i, user_id in enumerate(fila, 1):
            membro = guild.get_member(user_id)
            nome = membro.display_name if membro else "Desconhecido"
            desc += f"**{i}.** {nome}\n"

    embed = discord.Embed(title="🎯 FILA DE MEDIADORES FFZ", description=desc, color=COR_FFZ)
    embed.set_thumbnail(url=URL_THUMBNAIL_FFZ)
    embed.set_footer(text=f"Total: {len(fila)} mediadores • FFZ E-SPORTS")

    async for msg in canal.history(limit=10):
        if msg.author == guild.me and msg.embeds and "FILA DE MEDIADORES" in msg.embeds[0].title:
            await msg.edit(embed=embed, view=ViewMediadores())
            return
    await canal.send(embed=embed, view=ViewMediadores())

class FilaMed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(ViewMediadores()) # REGISTRA BOTÃO IMORTAL

    @commands.command()
    @commands.has_role(NOME_CARGO_STAFF)
    async def setup_med(self, ctx):
        await atualizar_embed_fila_med(ctx.guild)
        await ctx.send("Painel de mediadores postado!", delete_after=5)

    # APAGUEI O!confi_pix BUGADO

    @commands.command()
    @commands.has_role(NOME_CARGO_STAFF)
    async def pix(self, ctx, membro: discord.Member):
        pix_data = carregar_json("pix_mediadores.json")
        dados = pix_data.get(str(membro.id))

        if not dados:
            return await ctx.send(f"❌ {membro.display_name} não configurou o PIX ainda.")

        embed = discord.Embed(title="💰 PIX DO MEDIADOR", color=COR_FFZ)
        embed.add_field(name="Nome", value=dados["nome"], inline=False)
        embed.add_field(name="Chave PIX", value=f"`{dados['chave']}`", inline=False)
        embed.set_footer(text="FFZ E-SPORTS")
        try:
            await ctx.author.send(embed=embed)
            await ctx.send("✅ Te mandei o PIX na DM.", delete_after=5)
        except:
            await ctx.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(FilaMed(bot)) 
