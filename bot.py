import discord
from discord.ext import commands
from discord.ui import Modal, TextInput
import psycopg2
import asyncio
import math
import os
import random
from datetime import datetime, timezone, timedelta

# ============================================================
# CONFIGURAÇÃO DO DISCORD
# ============================================================

intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

# ============================================================
# RECOMPENSAS MYSTERY BOX
# ============================================================

RECOMPENSAS_MYSTERYBOX = [

    # ========================================================
    # XP
    # ========================================================

    {
        "nome": "+250 XP de Level",
        "tipo": "xp",
        "valor": 250,
        "raridade": "comum",
        "restricao": "todos"
    },

    {
        "nome": "+500 XP de Level",
        "tipo": "xp",
        "valor": 500,
        "raridade": "raro",
        "restricao": "todos"
    },

    {
        "nome": "+1000 XP de Level",
        "tipo": "xp",
        "valor": 1000,
        "raridade": "lendario",
        "restricao": "todos"
    },


    # ========================================================
    # PONTOS DE STATUS
    # ========================================================

    {
        "nome": "+5 Pontos de Status",
        "tipo": "status",
        "valor": 5,
        "raridade": "comum",
        "restricao": "todos"
    },

    {
        "nome": "+10 Pontos de Status",
        "tipo": "status",
        "valor": 10,
        "raridade": "comum",
        "restricao": "todos"
    },

    {
        "nome": "+20 Pontos de Status",
        "tipo": "status",
        "valor": 20,
        "raridade": "raro",
        "restricao": "todos"
    },

    {
        "nome": "+30 Pontos de Status",
        "tipo": "status",
        "valor": 30,
        "raridade": "raro",
        "restricao": "todos"
    },

    {
        "nome": "+50 Pontos de Status",
        "tipo": "status",
        "valor": 50,
        "raridade": "epico",
        "restricao": "todos"
    },

    {
        "nome": "+70 Pontos de Status",
        "tipo": "status",
        "valor": 70,
        "raridade": "lendario",
        "restricao": "todos"
    },

    {
        "nome": "+100 Pontos de Status",
        "tipo": "status",
        "valor": 100,
        "raridade": "mitico",
        "restricao": "todos"
    },


    # ========================================================
    # ITENS UNIVERSAIS
    # ========================================================

    {
        "nome": "Máscara de Sabito",
        "tipo": "item",
        "valor": "Máscara de Sabito",
        "raridade": "raro",
        "restricao": "todos"
    },

    {
        "nome": "Máscara de Makomo",
        "tipo": "item",
        "valor": "Máscara de Makomo",
        "raridade": "raro",
        "restricao": "todos"
    },

    {
        "nome": "Máscara de Urokodaki",
        "tipo": "item",
        "valor": "Máscara de Urokodaki",
        "raridade": "raro",
        "restricao": "todos"
    },

    {
        "nome": "Máscara de Javali",
        "tipo": "item",
        "valor": "Máscara de Javali",
        "raridade": "comum",
        "restricao": "todos"
    },

    {
        "nome": "Máscara Oni Simples",
        "tipo": "item",
        "valor": "Máscara Oni Simples",
        "raridade": "comum",
        "restricao": "todos"
    },

    {
        "nome": "Máscara Oni Demoníaca",
        "tipo": "item",
        "valor": "Máscara Oni Demoníaca",
        "raridade": "raro",
        "restricao": "todos"
    },

    {
        "nome": "Ratos musculosos do Uzui",
        "tipo": "item",
        "valor": "Ratos musculosos do Uzui",
        "raridade": "raro",
        "restricao": "todos"
    },

    {
        "nome": "Chuntaro",
        "tipo": "item",
        "valor": "Chuntaro",
        "raridade": "raro",
        "restricao": "todos"
    },


    # ========================================================
    # HUMANOS / CAÇADORES
    # ========================================================

    {
        "nome": "Tsuba do Giyu Tomioka",
        "tipo": "item",
        "valor": "Tsuba do Giyu Tomioka",
        "raridade": "raro",
        "restricao": "humano"
    },

    {
        "nome": "Tsuba do Kyojuro Rengoku",
        "tipo": "item",
        "valor": "Tsuba do Kyojuro Rengoku",
        "raridade": "epico",
        "restricao": "humano"
    },

    {
        "nome": "Tsuba do Tengen Uzui",
        "tipo": "item",
        "valor": "Tsuba do Tengen Uzui",
        "raridade": "raro",
        "restricao": "humano"
    },


    {
        "nome": "Haori do Kyojuro Rengoku",
        "tipo": "item",
        "valor": "Haori do Kyojuro Rengoku",
        "raridade": "epico",
        "restricao": "humano"
    },

    {
        "nome": "Haori do Giyu Tomioka",
        "tipo": "item",
        "valor": "Haori do Giyu Tomioka",
        "raridade": "epico",
        "restricao": "humano"
    },


    # ========================================================
    # ONIS
    # ========================================================

    {
        "nome": "Roupa do Akaza",
        "tipo": "item",
        "valor": "Roupa do Akaza",
        "raridade": "epico",
        "restricao": "oni"
    },

    {
        "nome": "Roupa do Douma",
        "tipo": "item",
        "valor": "Roupa do Douma",
        "raridade": "epico",
        "restricao": "oni"
    },

    {
        "nome": "Roupa do Kokushibo",
        "tipo": "item",
        "valor": "Roupa do Kokushibo",
        "raridade": "epico",
        "restricao": "oni"
    },

    {
        "nome": "Roupa do Muzan",
        "tipo": "item",
        "valor": "Roupa do Muzan",
        "raridade": "lendario",
        "restricao": "oni"
    }

]

# ============================================================
# PROBABILIDADES MYSTERY BOX
# ============================================================

RARIDADES_MYSTERYBOX = {
    "comum": 60,
    "raro": 25,
    "epico": 10,
    "lendario": 4,
    "mitico": 1
}

# ============================================================
# ADICIONAR PONTOS DE STATUS
# ============================================================

def adicionar_pontos_status(user_id, quantidade):

    cursor.execute(
        """
        UPDATE jogadores
        SET pontos = pontos + %s
        WHERE user_id = %s
        """,
        (
            quantidade,
            user_id
        )
    )

    db.commit()

# ============================================================
# SISTEMA DE DINHEIRO
# ============================================================

def criar_dinheiro(user_id):

    cursor.execute(
        """
        INSERT INTO dinheiro (user_id)
        VALUES (%s)
        ON CONFLICT (user_id) DO NOTHING
        """,
        (user_id,)
    )

    db.commit()



def obter_dinheiro(user_id):

    criar_dinheiro(user_id)

    cursor.execute(
        """
        SELECT quantidade
        FROM dinheiro
        WHERE user_id = %s
        """,
        (user_id,)
    )

    return cursor.fetchone()[0]



def adicionar_dinheiro(user_id, quantidade):

    criar_dinheiro(user_id)

    cursor.execute(
        """
        UPDATE dinheiro
        SET quantidade = quantidade + %s
        WHERE user_id = %s
        """,
        (
            quantidade,
            user_id
        )
    )

    db.commit()



def remover_dinheiro(user_id, quantidade):

    cursor.execute(
        """
        UPDATE dinheiro
        SET quantidade = quantidade - %s
        WHERE user_id = %s
        """,
        (
            quantidade,
            user_id
        )
    )

    db.commit()

# ============================================================
# SISTEMA DE LOJA
# ============================================================


def adicionar_produto(nome, preco, descricao):

    cursor.execute(
        """
        INSERT INTO loja (nome, preco, descricao)
        VALUES (%s, %s, %s)
        """,
        (
            nome,
            preco,
            descricao
        )
    )

    db.commit()



def remover_produto(nome):

    cursor.execute(
        """
        DELETE FROM loja
        WHERE nome = %s
        """,
        (nome,)
    )

    db.commit()



def obter_produtos():

    cursor.execute(
        """
        SELECT id, nome, preco, descricao
        FROM loja
        """
    )

    return cursor.fetchall()



def obter_produto(id):

    cursor.execute(
        """
        SELECT id, nome, preco, descricao
        FROM loja
        WHERE id = %s
        """,
        (id,)
    )

    return cursor.fetchone()

# ============================================================
# CARGOS DE PERSONAGEM
# ============================================================

CARGO_HUMANO = 1386546298068402236
CARGO_ONI = 1386546400950620190
CARGO_HIBRIDO = 1386546789829709824


# ============================================================
# CARGOS DE STAFF
# ============================================================

CARGO_MODERADOR = 1388566955069280287
CARGO_SUPERVISAO = 1388567043628077197
CARGO_ADM = 1388566858390573246
CARGO_FUNDADOR = 1386441239125295237
CARGO_NARRADOR = 1386441241742278716


# ============================================================
# VERIFICAÇÃO DE STAFF
# ============================================================

def is_staff(member):

    cargos_staff = [
        CARGO_MODERADOR,
        CARGO_SUPERVISAO,
        CARGO_ADM,
        CARGO_FUNDADOR
    ]

    return any(
        cargo.id in cargos_staff
        for cargo in member.roles
    )


# ============================================================
# VERIFICAÇÃO DE NARRADOR
# ============================================================

def is_narrador(member):

    return any(
        cargo.id == CARGO_NARRADOR
        for cargo in member.roles
    )

# ============================================================
# RECOMPENSAS DOS OPONENTES
# ============================================================

RECOMPENSAS_OPONENTES = {

    # ========================================================
    # RANK 1
    # ========================================================

    "Mizunoto": {
        "pontos": 10,
        "xp": 350,
        "dinheiro": 1000
    },

    "Oni Figurante": {
        "pontos": 10,
        "xp": 350,
        "dinheiro": 1000
    },

    "Mizunoe": {
        "pontos": 15,
        "xp": 500,
        "dinheiro": 1200
    },

    "Oni Desconhecido": {
        "pontos": 15,
        "xp": 500,
        "dinheiro": 1200
    },

    # ========================================================
    # RANK 2
    # ========================================================

    "Kanoto": {
        "pontos": 20,
        "xp": 650,
        "dinheiro": 1400
    },

    "Oni Popular": {
        "pontos": 20,
        "xp": 650,
        "dinheiro": 1400
    },

    "Kanoe": {
        "pontos": 25,
        "xp": 800,
        "dinheiro": 1600
    },

    "Oni Semi-Prodígio": {
        "pontos": 25,
        "xp": 800,
        "dinheiro": 1600
    },

    # ========================================================
    # RANK 3
    # ========================================================

    "Tsuchinoto": {
        "pontos": 30,
        "xp": 950,
        "dinheiro": 1800
    },

    "Oni Prodígio": {
        "pontos": 30,
        "xp": 950,
        "dinheiro": 1800
    },

    "Tsuchinoe": {
        "pontos": 35,
        "xp": 1100,
        "dinheiro": 2000
    },

    "Oni Talentoso": {
        "pontos": 35,
        "xp": 1100,
        "dinheiro": 2000
    },

    # ========================================================
    # RANK 4
    # ========================================================

    "Hinoto": {
        "pontos": 40,
        "xp": 1250,
        "dinheiro": 2200
    },

    "Oni Semi-Lunar": {
        "pontos": 40,
        "xp": 1250,
        "dinheiro": 2200
    },

    "Hinoe": {
        "pontos": 45,
        "xp": 1400,
        "dinheiro": 2400
    },

    "Oni Lunar": {
        "pontos": 45,
        "xp": 1400,
        "dinheiro": 2400
    },

    # ========================================================
    # RANK 5
    # ========================================================

    "Kinoto": {
        "pontos": 50,
        "xp": 1550,
        "dinheiro": 2600
    },

    "Kinoe": {
        "pontos": 60,
        "xp": 1700,
        "dinheiro": 2800
    },

    "Lua Inferior": {
        "pontos": 60,
        "xp": 1700,
        "dinheiro": 2800
    },

    # ========================================================
    # RANK 6
    # ========================================================

    "Hashira": {
        "pontos": 70,
        "xp": 2000,
        "dinheiro": 3000
    },

    "Lua Superior": {
        "pontos": 70,
        "xp": 2000,
        "dinheiro": 3000
    }
}

# ============================================================
# OPONENTES DISPONÍVEIS POR RANK DE MISSÃO
# ============================================================

OPONENTES_MISSAO = {

    1: {
        "Humano": [
            "Oni Figurante",
            "Oni Desconhecido"
        ],
        "Oni": [
            "Mizunoto",
            "Mizunoe"
        ]
    },

    2: {
        "Humano": [
            "Oni Popular",
            "Oni Semi-Prodígio"
        ],
        "Oni": [
            "Kanoto",
            "Kanoe"
        ]
    },

    3: {
        "Humano": [
            "Oni Prodígio"
        ],
        "Oni": [
            "Tsuchinoto",
            "Tsuchinoe"
        ]
    },

    4: {
        "Humano": [
            "Oni Talentoso",
            "Oni Semi-Lunar"
        ],
        "Oni": [
            "Hinoto",
            "Hinoe"
        ]
    },

    5: {
        "Humano": [
            "Oni Lunar",
            "Lua Inferior"
        ],
        "Oni": [
            "Kinoto",
            "Kinoe"
        ]
    },

    6: {
        "Humano": [
            "Lua Inferior",
            "Lua Superior"
        ],
        "Oni": [
            "Kinoe",
            "Hashira"
        ]
    }
}

# ============================================================
# VIEW — ESCOLHER OPONENTES DA MISSÃO
# ============================================================

class EscolherOponentesMissao(discord.ui.View):

    def __init__(self, jogador, rank_missao, raca):
        super().__init__(timeout=180)

        self.jogador = jogador
        self.rank_missao = rank_missao
        self.raca = raca

        self.oponentes = OPONENTES_MISSAO[
            rank_missao
        ][raca]

    @discord.ui.button(
        label="Registar derrotas",
        style=discord.ButtonStyle.danger,
        emoji="⚔️"
    )
    async def registar(
        self,
        interaction,
        button
    ):

        if not is_narrador(interaction.user):

            return await interaction.response.send_message(
                "❌ Apenas Narradores podem utilizar esta interface.",
                ephemeral=True
            )

        await interaction.response.send_modal(
            ModalOponentesMissao(
                self.jogador,
                self.rank_missao,
                self.raca,
                self.oponentes
            )
        )


# ============================================================
# MODAL — QUANTIDADE DE OPONENTES
# ============================================================

class ModalOponentesMissao(discord.ui.Modal):

    def __init__(
        self,
        jogador,
        rank_missao,
        raca,
        oponentes
    ):

        super().__init__(
            title=f"Missão Rank {rank_missao}"
        )

        self.jogador = jogador
        self.rank_missao = rank_missao
        self.raca = raca
        self.oponentes = oponentes

        self.campos = []

        for oponente in oponentes:

            campo = discord.ui.TextInput(
                label=oponente,
                placeholder="Número de inimigos derrotados",
                required=True,
                min_length=1,
                max_length=4
            )

            self.campos.append(campo)
            self.add_item(campo)

    async def on_submit(self, interaction):

        # ====================================================
        # VERIFICAR NARRADOR
        # ====================================================

        if not is_narrador(interaction.user):

            return await interaction.response.send_message(
                "❌ Apenas **Narradores** podem utilizar esta interface.",
                ephemeral=True
            )

        await interaction.response.defer(ephemeral=True)

        # ====================================================
        # LER QUANTIDADES
        # ====================================================

        quantidades = {}

        try:

            for oponente, campo in zip(
                self.oponentes,
                self.campos
            ):

                quantidade = int(campo.value)

                if quantidade < 0:
                    raise ValueError

                quantidades[oponente] = quantidade

        except ValueError:

            return await interaction.followup.send(
                "❌ As quantidades devem ser números inteiros "
                "iguais ou superiores a 0.",
                ephemeral=True
            )

        # ====================================================
        # CALCULAR RECOMPENSAS
        # ====================================================

        pontos_totais = 0
        xp_total = 0
        dinheiro_total = 0

        detalhes = []

        for oponente, quantidade in quantidades.items():

            if quantidade <= 0:
                continue

            recompensa = RECOMPENSAS_OPONENTES[oponente]

            pontos = recompensa["pontos"] * quantidade
            xp = recompensa["xp"] * quantidade
            dinheiro = recompensa["dinheiro"] * quantidade

            pontos_totais += pontos
            xp_total += xp
            dinheiro_total += dinheiro

            detalhes.append(
                f"⚔️ **{oponente}** × {quantidade}\n"
                f"└ ⭐ +{pontos} pontos | "
                f"✨ +{xp} XP | "
                f"💰 +{dinheiro} moedas"
            )

        # ====================================================
        # VERIFICAR SE HOUVE DERROTAS
        # ====================================================

        if not detalhes:

            return await interaction.followup.send(
                "❌ Tens de registar pelo menos um inimigo derrotado.",
                ephemeral=True
            )

        # ====================================================
        # GUARDAR RANK ANTERIOR
        # ====================================================

        rank_anterior = obter_rank(
            self.jogador.id,
            self.raca,
            self.jogador
        )

        # ====================================================
        # DAR PONTOS DE RANK
        # ====================================================

        cursor.execute(
            """
            INSERT INTO progresso_rank (user_id, pontos_rank)
            VALUES (%s, %s)
            ON CONFLICT (user_id)
            DO UPDATE SET pontos_rank =
                progresso_rank.pontos_rank + EXCLUDED.pontos_rank
            """,
            (
                self.jogador.id,
                pontos_totais
            )
        )

        db.commit()

        # ====================================================
        # DAR XP
        # ====================================================

        adicionar_xp(
            self.jogador.id,
            xp_total
        )

        # ====================================================
        # DAR DINHEIRO
        # ====================================================

        adicionar_dinheiro(
            self.jogador.id,
            dinheiro_total
        )

        # ====================================================
        # ATUALIZAR RANK AUTOMATICAMENTE
        # ====================================================

        novo_rank = await atualizar_rank_automaticamente(
            self.jogador
        )

        # ====================================================
        # CONFIRMAÇÃO
        # ====================================================

        descricao = (
            f"👤 **Jogador:** {self.jogador.mention}\n"
            f"🧬 **Raça:** {self.raca}\n"
            f"⚔️ **Rank da missão:** {self.rank_missao}\n\n"
            + "\n\n".join(detalhes)
        )

        # ====================================================
        # INFORMAR PROMOÇÃO
        # ====================================================

        if (
            rank_anterior is not None
            and novo_rank is not None
            and novo_rank[1] > rank_anterior["ordem"]
        ):

            descricao += (
                f"\n\n🎉 **PROMOÇÃO DE RANK!**\n"
                f"🏅 **{rank_anterior['nome']}** → "
                f"**{novo_rank[0]}**"
            )

        embed = discord.Embed(
            title="📜 Missão Concluída",
            description=descricao,
            color=discord.Color.green()
        )

        embed.add_field(
            name="🏆 Recompensas Recebidas",
            value=(
                f"⭐ **+{pontos_totais} Pontos de Rank**\n"
                f"✨ **+{xp_total} XP**\n"
                f"💰 **+{dinheiro_total} moedas**"
            ),
            inline=False
        )

        if novo_rank is not None:

            embed.add_field(
                name="🏅 Rank Atual",
                value=f"**{novo_rank[0]}**",
                inline=False
            )

        embed.set_footer(
            text="👻 . 𝗟ᥲ᥉t 𝗦᥆ᥙᥣ • Sistema de Missões"
        )

        await interaction.followup.send(
            embed=embed,
            ephemeral=True
        )


# ============================================================
# VIEW — ESCOLHER RANK DA MISSÃO
# ============================================================

class EscolherRankMissao(discord.ui.View):

    def __init__(self, jogador):
        super().__init__(timeout=120)
        self.jogador = jogador

    async def verificar_narrador(self, interaction):

        if not is_narrador(interaction.user):

            await interaction.response.send_message(
                "❌ Apenas Narradores podem utilizar esta interface.",
                ephemeral=True
            )

            return False

        return True

    async def escolher_rank(
        self,
        interaction,
        rank_missao
    ):

        if not await self.verificar_narrador(interaction):
            return

        raca = obter_raca(self.jogador)

        if raca is None:

            return await interaction.response.send_message(
                "❌ Este jogador não possui um cargo de "
                "Humano, Oni ou Híbrido.",
                ephemeral=True
            )

        oponentes = OPONENTES_MISSAO[
            rank_missao
        ][raca]

        lista_oponentes = "\n".join(
            f"⚔️ **{oponente}**"
            for oponente in oponentes
        )

        embed = discord.Embed(
            title=f"⚔️ Missão Rank {rank_missao}",
            description=(
                f"👤 **Jogador:** {self.jogador.mention}\n"
                f"🧬 **Raça:** {raca}\n\n"
                "### Oponentes disponíveis\n"
                f"{lista_oponentes}\n\n"
                "Clique abaixo para indicar quantos "
                "oponentes foram derrotados."
            ),
            color=discord.Color.dark_red()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=EscolherOponentesMissao(
                self.jogador,
                rank_missao,
                raca
            )
        )

    @discord.ui.button(
        label="Rank 1",
        style=discord.ButtonStyle.secondary
    )
    async def rank1(self, interaction, button):
        await self.escolher_rank(interaction, 1)

    @discord.ui.button(
        label="Rank 2",
        style=discord.ButtonStyle.secondary
    )
    async def rank2(self, interaction, button):
        await self.escolher_rank(interaction, 2)

    @discord.ui.button(
        label="Rank 3",
        style=discord.ButtonStyle.primary
    )
    async def rank3(self, interaction, button):
        await self.escolher_rank(interaction, 3)

    @discord.ui.button(
        label="Rank 4",
        style=discord.ButtonStyle.primary
    )
    async def rank4(self, interaction, button):
        await self.escolher_rank(interaction, 4)

    @discord.ui.button(
        label="Rank 5",
        style=discord.ButtonStyle.danger
    )
    async def rank5(self, interaction, button):
        await self.escolher_rank(interaction, 5)

    @discord.ui.button(
        label="Rank 6",
        style=discord.ButtonStyle.danger
    )
    async def rank6(self, interaction, button):
        await self.escolher_rank(interaction, 6)


# ============================================================
# !MISSAO
# ============================================================

@bot.command()
async def missao(ctx, membro: discord.Member = None):

    # --------------------------------------------------------
    # VERIFICAR NARRADOR
    # --------------------------------------------------------

    if not is_narrador(ctx.author):

        return await ctx.send(
            "❌ Apenas **Narradores** podem utilizar o comando `!missao`."
        )

    # --------------------------------------------------------
    # VERIFICAR JOGADOR
    # --------------------------------------------------------

    if membro is None:

        return await ctx.send(
            "❌ Tens de mencionar o jogador que realizou a missão.\n\n"
            "Exemplo:\n"
            "`!missao @Jogador`"
        )

    # --------------------------------------------------------
    # VERIFICAR RAÇA
    # --------------------------------------------------------

    raca = obter_raca(membro)

    if raca is None:

        return await ctx.send(
            "❌ Esse jogador não possui um cargo de "
            "**Humano, Oni ou Híbrido**."
        )

    # --------------------------------------------------------
    # EMBED
    # --------------------------------------------------------

    embed = discord.Embed(
        title="📜 Registo de Missão",
        description=(
            f"👤 **Jogador:** {membro.mention}\n"
            f"🧬 **Raça:** {raca}\n\n"
            "Selecione abaixo o **Rank da missão narrada**."
        ),
        color=discord.Color.dark_red()
    )

    embed.set_footer(
        text="👻 . 𝗟ᥲ᥉t 𝗦᥆ᥙᥣ • Sistema de Missões"
    )

    await ctx.send(
        embed=embed,
        view=EscolherRankMissao(membro)
    )

# ============================================================
# CARGOS DE TREINO
# ============================================================

CARGO_CIVIL = 1388751894750429296
CARGO_ONI_FIGURANTE = 1389241118952132710

CARGO_KANOTO = 1389233677099339806
CARGO_ONI_POPULAR = 1389241691063586856

CARGO_HINOTO = 1389238699124068444
CARGO_ONI_TALENTOSO = 1389245570350321704

CARGO_PRODIGIO = 1539055788352479264


# ============================================================
# BASE DE DADOS
# ============================================================

db = psycopg2.connect(
    os.environ["DATABASE_URL"]
)

cursor = db.cursor()

print("DATABASE POSTGRESQL LIGADA")

# ============================================================
# SISTEMA DE RANKS
# ============================================================

def obter_pontos_rank(user_id):

    cursor.execute("""
        SELECT pontos_rank
        FROM progresso_rank
        WHERE user_id = %s
    """, (user_id,))

    resultado = cursor.fetchone()

    if resultado is None:

        cursor.execute("""
            INSERT INTO progresso_rank (user_id, pontos_rank)
            VALUES (%s, 0)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id,))

        db.commit()

        return 0

    return resultado[0]


# ============================================================
# OBTER RANK PELO CARGO
# ============================================================

def obter_rank(user_id, tipo, membro=None):

    # --------------------------------------------------------
    # 1. Procurar o maior rank que o jogador possui
    # através dos cargos do Discord
    # --------------------------------------------------------

    if membro is not None:

        cargos_usuario = {
            cargo.id
            for cargo in membro.roles
        }

        cursor.execute("""
            SELECT nome, ordem, pontos_necessarios, cargo_id
            FROM ranks
            WHERE tipo = %s
            AND cargo_id = ANY(%s)
            ORDER BY ordem DESC
            LIMIT 1
        """, (tipo, list(cargos_usuario)))

        resultado = cursor.fetchone()

        if resultado is not None:

            pontos = obter_pontos_rank(user_id)

            return {
                "nome": resultado[0],
                "ordem": resultado[1],
                "pontos_necessarios": resultado[2],
                "cargo_id": resultado[3],
                "pontos": pontos
            }

    # --------------------------------------------------------
    # 2. Caso não tenha nenhum cargo de rank,
    # determinar o rank através dos pontos
    # --------------------------------------------------------

    pontos = obter_pontos_rank(user_id)

    cursor.execute("""
        SELECT nome, ordem, pontos_necessarios, cargo_id
        FROM ranks
        WHERE tipo = %s
        AND pontos_necessarios <= %s
        ORDER BY pontos_necessarios DESC
        LIMIT 1
    """, (tipo, pontos))

    resultado = cursor.fetchone()

    if resultado is None:
        return None

    return {
        "nome": resultado[0],
        "ordem": resultado[1],
        "pontos_necessarios": resultado[2],
        "cargo_id": resultado[3],
        "pontos": pontos
    }

# ============================================================
# ATUALIZAR RANK AUTOMATICAMENTE
# ============================================================

async def atualizar_rank_automaticamente(membro):

    # --------------------------------------------------------
    # Verificar a raça do jogador
    # --------------------------------------------------------

    tipo = obter_raca(membro)

    if tipo is None:
        return None

    # Híbridos não entram no sistema automático por enquanto
    if tipo == "Híbrido":
        return None

    # --------------------------------------------------------
    # Obter pontos atuais
    # --------------------------------------------------------

    pontos = obter_pontos_rank(membro.id)

    # --------------------------------------------------------
    # Procurar o maior rank que os pontos permitem
    # --------------------------------------------------------

    cursor.execute("""
        SELECT nome, ordem, pontos_necessarios, cargo_id
        FROM ranks
        WHERE tipo = %s
        AND pontos_necessarios <= %s
        ORDER BY ordem DESC
        LIMIT 1
    """, (tipo, pontos))

    novo_rank = cursor.fetchone()

    if novo_rank is None:
        return None

    nome_novo = novo_rank[0]
    ordem_nova = novo_rank[1]
    cargo_novo_id = novo_rank[3]

    # --------------------------------------------------------
    # Não promover automaticamente para Lua Inferior/Superior
    # --------------------------------------------------------

    if nome_novo in ["Lua Inferior", "Lua Superior"]:
        return None

    # --------------------------------------------------------
    # Obter o cargo novo
    # --------------------------------------------------------

    cargo_novo = membro.guild.get_role(cargo_novo_id)

    if cargo_novo is None:
        return None

    # --------------------------------------------------------
    # Procurar cargos de rank da mesma raça
    # --------------------------------------------------------

    cursor.execute("""
        SELECT cargo_id
        FROM ranks
        WHERE tipo = %s
    """, (tipo,))

    cargos_rank = {
        linha[0]
        for linha in cursor.fetchall()
    }

    # --------------------------------------------------------
    # Remover cargos de rank antigos
    # --------------------------------------------------------

    cargos_remover = [
        cargo
        for cargo in membro.roles
        if cargo.id in cargos_rank
        and cargo.id != cargo_novo_id
    ]

    if cargos_remover:

        await membro.remove_roles(
            *cargos_remover,
            reason="Atualização automática de Rank"
        )

    # --------------------------------------------------------
    # Adicionar o novo cargo
    # --------------------------------------------------------

    if cargo_novo not in membro.roles:

        await membro.add_roles(
            cargo_novo,
            reason="Promoção automática de Rank"
        )

    return novo_rank


# ============================================================
# DETETAR RAÇA DO PERSONAGEM
# ============================================================

def obter_raca(membro):

    cargos = {
        cargo.id
        for cargo in membro.roles
    }

    # Humano
    if CARGO_HUMANO in cargos:
        return "Humano"

    # Oni
    if CARGO_ONI in cargos:
        return "Oni"

    # Híbrido utiliza a progressão dos Onis
    if CARGO_HIBRIDO in cargos:
        return "Oni"

    return None

# ============================================================
# DETETAR RAÇA DO PERSONAGEM
# ============================================================

def obter_raca(membro):

    cargos = [cargo.id for cargo in membro.roles]

    if CARGO_HUMANO in cargos:
        return "Humano"

    if CARGO_ONI in cargos:
        return "Oni"

    if CARGO_HIBRIDO in cargos:
        return "Oni"

    return None


# ============================================================
# TABELA DE JOGADORES
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS jogadores (
    user_id BIGINT PRIMARY KEY,
    pontos INTEGER DEFAULT 0,
    velocidade INTEGER DEFAULT 0,
    forca INTEGER DEFAULT 0,
    resistencia INTEGER DEFAULT 0,
    manejo INTEGER DEFAULT 0,
    regeneracao INTEGER DEFAULT 0,
    folego INTEGER DEFAULT 0,
    sangue INTEGER DEFAULT 0
)
""")


# ============================================================
# ADICIONAR PONTOS DE RANK
# ============================================================

cursor.execute("""
ALTER TABLE jogadores
ADD COLUMN IF NOT EXISTS pontos_rank INTEGER DEFAULT 0
""")


# ============================================================
# TABELA DE TREINOS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS treinos (
    user_id BIGINT PRIMARY KEY,
    tipo TEXT NOT NULL,
    canal_id BIGINT NOT NULL,
    inicio TEXT NOT NULL,
    termino TEXT NOT NULL,
    pontos INTEGER NOT NULL,
    aguardando_acao INTEGER DEFAULT 1
)
""")


# ============================================================
# GUARDAR ALTERAÇÕES
# ============================================================

db.commit()


# ============================================================
# CARREGAR RANKS
# ============================================================

cursor.execute("""
SELECT tipo, nome, ordem, pontos_necessarios, cargo_id
FROM ranks
ORDER BY tipo, ordem
""")

ranks = cursor.fetchall()

print(f"RANKS CARREGADOS: {len(ranks)}")


# ============================================================
# DADOS DOS TREINOS
# ============================================================

TREINOS = {

    "iniciante": {
        "nome": "Treino Iniciante",
        "caracteres": 500,
        "tempo": 3600,
        "pontos": 60,
        "humano": CARGO_CIVIL,
        "oni": CARGO_ONI_FIGURANTE
    },

    "intermediario": {
        "nome": "Treino Intermediário",
        "caracteres": 750,
        "tempo": 5400,
        "pontos": 90,
        "humano": CARGO_KANOTO,
        "oni": CARGO_ONI_POPULAR
    },

    "extremo": {
        "nome": "Treino Extremo",
        "caracteres": 1000,
        "tempo": 7200,
        "pontos": 125,
        "humano": CARGO_HINOTO,
        "oni": CARGO_ONI_TALENTOSO
    }
}


# ============================================================
# ATRIBUTOS
# ============================================================

ATRIBUTOS = {
    "velocidade": {
        "nome": "Velocidade",
        "emoji": "⚡"
    },

    "forca": {
        "nome": "Força",
        "emoji": "💪"
    },

    "resistencia": {
        "nome": "Resistência",
        "emoji": "🛡️"
    },

    "manejo": {
        "nome": "Manejo",
        "emoji": "⚔️"
    },

    "regeneracao": {
        "nome": "Regeneração",
        "emoji": "🩸"
    },

    "folego": {
        "nome": "Fôlego",
        "emoji": "🌬️"
    },

    "sangue": {
        "nome": "Sangue",
        "emoji": "🩸"
    }
}


ATRIBUTOS_PERMITIDOS = {

    "humano": [
        "velocidade",
        "forca",
        "resistencia",
        "manejo",
        "folego"
    ],

    "oni": [
        "velocidade",
        "forca",
        "resistencia",
        "regeneracao",
        "sangue"
    ],

    "hibrido": [
        "velocidade",
        "forca",
        "resistencia",
        "manejo",
        "regeneracao",
        "folego",
        "sangue"
    ]
}


LIMITES = {
    "humano": 1000,
    "oni": 1150,
    "hibrido": 1150
}


# ============================================================
# BASE DOS ATRIBUTOS
# ============================================================

BASE_VELOCIDADE = 15
BASE_FORCA = 10
BASE_FOLEGO = 150_000
BASE_SANGUE = 100_000

# ============================================================
# CONVERSÃO DOS PONTOS PARA VALORES REAIS
# ============================================================

def calcular_velocidade(pontos):

    return BASE_VELOCIDADE + pontos


def calcular_forca(pontos):

    return BASE_FORCA + pontos


def calcular_folego(pontos):

    blocos = pontos // 150

    return BASE_FOLEGO + (blocos * 50_000)


def calcular_sangue(pontos):

    blocos = pontos // 150

    return BASE_SANGUE + (blocos * 150_000)

# ============================================================
# BÔNUS DE MANEJO
# ============================================================

def calcular_bonus_manejo(manejo):

    blocos = manejo // 100

    return blocos * 0.015

# ============================================================
# FUNÇÕES DA BASE DE DADOS
# ============================================================

def criar_jogador(user_id):

    cursor.execute(
        """
        INSERT INTO jogadores (user_id)
        VALUES (%s)
        ON CONFLICT (user_id) DO NOTHING
        """,
        (user_id,)
    )

    db.commit()


def obter_jogador(user_id):

    criar_jogador(user_id)

    cursor.execute(
        """
        SELECT
            user_id,
            pontos,
            velocidade,
            forca,
            resistencia,
            manejo,
            regeneracao,
            folego,
            sangue
        FROM jogadores
        WHERE user_id = %s
        """,
        (user_id,)
    )

    return cursor.fetchone()
# ============================================================
# SISTEMA DE EQUIPAMENTOS
# ============================================================

def criar_equipamento(user_id):

    cursor.execute(
        """
        INSERT INTO equipamentos (user_id)
        VALUES (%s)
        ON CONFLICT (user_id) DO NOTHING
        """,
        (user_id,)
    )

    db.commit()


def obter_equipamentos(user_id):

    criar_equipamento(user_id)

    cursor.execute(
        """
        SELECT tsuba, haori, nichirin, mascara
        FROM equipamentos
        WHERE user_id = %s
        """,
        (user_id,)
    )

    return cursor.fetchone()


def equipar_item(user_id, tipo, item):

    criar_equipamento(user_id)

    tipos_validos = [
        "tsuba",
        "haori",
        "nichirin",
        "mascara"
    ]

    if tipo not in tipos_validos:
        return False

    cursor.execute(
        f"""
        UPDATE equipamentos
        SET {tipo} = %s
        WHERE user_id = %s
        """,
        (item, user_id)
    )

    db.commit()

    return True


def desequipar_item(user_id, tipo):

    criar_equipamento(user_id)

    tipos_validos = [
        "tsuba",
        "haori",
        "nichirin",
        "mascara"
    ]

    if tipo not in tipos_validos:
        return False

    cursor.execute(
        f"""
        UPDATE equipamentos
        SET {tipo} = NULL
        WHERE user_id = %s
        """,
        (user_id,)
    )

    db.commit()

    return True

# ============================================================
# ADICIONAR PONTOS DE STATUS
# ============================================================

def adicionar_pontos_status(user_id, quantidade):

    cursor.execute(
        """
        UPDATE jogadores
        SET pontos = pontos + %s
        WHERE user_id = %s
        """,
        (
            quantidade,
            user_id
        )
    )

    db.commit()

# ============================================================
# SISTEMA DE INVENTÁRIO
# ============================================================

def adicionar_item(user_id, item, quantidade=1):

    cursor.execute(
        """
        INSERT INTO inventario (
            user_id,
            item,
            quantidade
        )
        VALUES (%s, %s, %s)

        ON CONFLICT (user_id, item)
        DO UPDATE SET quantidade = inventario.quantidade + %s
        """,
        (
            user_id,
            item,
            quantidade,
            quantidade
        )
    )

    db.commit()



def remover_item(user_id, item, quantidade=1):

    cursor.execute(
        """
        SELECT quantidade
        FROM inventario
        WHERE user_id = %s
        AND item = %s
        """,
        (
            user_id,
            item
        )
    )

    resultado = cursor.fetchone()


    if resultado is None:
        return False


    quantidade_atual = resultado[0]


    if quantidade_atual <= quantidade:

        cursor.execute(
            """
            DELETE FROM inventario
            WHERE user_id = %s
            AND item = %s
            """,
            (
                user_id,
                item
            )
        )

    else:

        cursor.execute(
            """
            UPDATE inventario
            SET quantidade = quantidade - %s
            WHERE user_id = %s
            AND item = %s
            """,
            (
                quantidade,
                user_id,
                item
            )
        )


    db.commit()

    return True



def obter_inventario(user_id):

    cursor.execute(
        """
        SELECT item, quantidade
        FROM inventario
        WHERE user_id = %s
        ORDER BY item ASC
        """,
        (user_id,)
    )

    return cursor.fetchall()



def tem_item(user_id, item):

    cursor.execute(
        """
        SELECT quantidade
        FROM inventario
        WHERE user_id = %s
        AND item = %s
        """,
        (
            user_id,
            item
        )
    )

    resultado = cursor.fetchone()


    if resultado:

        return resultado[0] > 0


    return False

# ============================================================
# BOTÃO MYSTERY BOX
# ============================================================

class MysteryBoxView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.button(
        label="🎁 Abrir Mystery Box",
        style=discord.ButtonStyle.blurple
    )
    async def abrir_box(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        recompensa = abrir_mysterybox(
            interaction.user.id
        )


        if recompensa is None:

            await interaction.response.send_message(
                "❌ Não tens Mystery Boxes disponíveis.",
                ephemeral=True
            )

            return


        dar_recompensa_mysterybox(
            interaction.user.id,
            recompensa
        )


        await interaction.response.send_message(
            f"🎁 Abriste uma Mystery Box!\n\n"
            f"🏆 Recompensa: **{recompensa['nome']}**\n"
            f"⭐ Raridade: **{recompensa['raridade'].capitalize()}**",
            ephemeral=True
        )

# ============================================================
# SISTEMA DE MYSTERY BOX
# ============================================================

def criar_mysterybox(user_id):

    cursor.execute(
        """
        INSERT INTO mysteryboxes (user_id)
        VALUES (%s)
        ON CONFLICT (user_id) DO NOTHING
        """,
        (user_id,)
    )

    db.commit()


def obter_mysterybox(user_id):

    criar_mysterybox(user_id)

    cursor.execute(
        """
        SELECT quantidade
        FROM mysteryboxes
        WHERE user_id = %s
        """,
        (user_id,)
    )

    return cursor.fetchone()[0]


def adicionar_mysterybox(user_id, quantidade=1):

    criar_mysterybox(user_id)

    cursor.execute(
        """
        UPDATE mysteryboxes
        SET quantidade = quantidade + %s
        WHERE user_id = %s
        """,
        (
            quantidade,
            user_id
        )
    )

    db.commit()


def remover_mysterybox(user_id, quantidade=1):

    cursor.execute(
        """
        UPDATE mysteryboxes
        SET quantidade = quantidade - %s
        WHERE user_id = %s
        """,
        (
            quantidade,
            user_id
        )
    )

    db.commit()

# ============================================================
# ABRIR MYSTERY BOX
# ============================================================

def abrir_mysterybox(user_id):

    quantidade = obter_mysterybox(user_id)

    if quantidade <= 0:
        return None


    remover_mysterybox(user_id, 1)


    recompensa = random.choice(RECOMPENSAS_MYSTERYBOX)


    return recompensa

# ============================================================
# DAR RECOMPENSA DA MYSTERY BOX
# ============================================================

def dar_recompensa_mysterybox(user_id, recompensa):

    tipo = recompensa["tipo"]

    if tipo == "xp":

        adicionar_xp(
            user_id,
            recompensa["valor"]
        )


    elif tipo == "status":

        adicionar_pontos_status(
            user_id,
            recompensa["valor"]
        )


    elif tipo == "item":

        adicionar_item(
            user_id,
            recompensa["valor"]
        )


    return recompensa

# ============================================================
# SISTEMA DE NÍVEIS
# ============================================================

def criar_nivel(user_id):

    cursor.execute(
        """
        INSERT INTO niveis (user_id)
        VALUES (%s)
        ON CONFLICT (user_id) DO NOTHING
        """,
        (user_id,)
    )

    db.commit()


def obter_nivel(user_id):

    criar_nivel(user_id)

    cursor.execute(
        """
        SELECT xp, level
        FROM niveis
        WHERE user_id = %s
        """,
        (user_id,)
    )

    return cursor.fetchone()

# ============================================================
# FUNÇÕES DO SISTEMA DE NÍVEIS
# ============================================================

def xp_para_proximo_level(level):

    return math.floor(
        100 * (level ** 1.5)
    )


def adicionar_xp(user_id, quantidade):

    xp_atual, level_atual = obter_nivel(user_id)

    novo_xp = xp_atual + quantidade
    novo_level = level_atual

    xp_necessario = xp_para_proximo_level(level_atual)

    while novo_xp >= xp_necessario:

        novo_xp -= xp_necessario
        novo_level += 1

        if novo_level % 10 == 0:

            adicionar_mysterybox(user_id, 1)

        xp_necessario = xp_para_proximo_level(novo_level)


    cursor.execute(
        """
        UPDATE niveis
        SET xp = %s,
            level = %s
        WHERE user_id = %s
        """,
        (
            novo_xp,
            novo_level,
            user_id
        )
    )

    db.commit()


    return novo_level > level_atual, novo_level


# ============================================================
# FUNÇÕES DE CARGOS
# ============================================================

def obter_tipo(member):

    cargos = {cargo.id for cargo in member.roles}

    if CARGO_HIBRIDO in cargos:
        return "hibrido"

    if CARGO_ONI in cargos:
        return "oni"

    if CARGO_HUMANO in cargos:
        return "humano"

    return None


def eh_staff(member):

    cargos = {cargo.id for cargo in member.roles}

    return any(cargo in cargos for cargo in [
        CARGO_MODERADOR,
        CARGO_ADM,
        CARGO_FUNDADOR
    ])


def eh_prodigio(member):

    return any(
        cargo.id == CARGO_PRODIGIO
        for cargo in member.roles
    )


# ============================================================
# VERIFICAR REQUISITO DO TREINO
# ============================================================

def pode_fazer_treino(member, tipo_treino):

    tipo_personagem = obter_tipo(member)

    if tipo_personagem is None:
        return False, "❌ Não tens um cargo de Humano, Oni ou Híbrido."

    treino = TREINOS[tipo_treino]

    # Humanos usam os cargos de progressão Humanos.
    if tipo_personagem == "humano":
        cargo_necessario = treino["humano"]

    # Onis E Híbridos usam os cargos de progressão dos Onis.
    elif tipo_personagem in ["oni", "hibrido"]:
        cargo_necessario = treino["oni"]

    else:
        return False, "❌ Não foi possível identificar a tua classe."

    possui_cargo = any(
        cargo.id == cargo_necessario
        for cargo in member.roles
    )

    if not possui_cargo:

        nomes = {
            CARGO_CIVIL: "Civil",
            CARGO_ONI_FIGURANTE: "Oni Figurante",
            CARGO_KANOTO: "Kanoto",
            CARGO_ONI_POPULAR: "Oni Popular",
            CARGO_HINOTO: "Hinoto",
            CARGO_ONI_TALENTOSO: "Oni Talentoso"
        }

        nome_cargo = nomes.get(
            cargo_necessario,
            "Cargo necessário"
        )

        return False, (
            f"❌ Não tens o cargo necessário para este treino.\n"
            f"🎖️ Cargo mínimo: **{nome_cargo}**"
        )

    return True, None


# ============================================================
# VERIFICAR TREINO ATIVO
# ============================================================

def obter_treino(user_id):

    cursor.execute(
        """
        SELECT user_id, tipo, canal_id, inicio,
               termino, pontos, aguardando_acao
        FROM treinos
        WHERE user_id = %s
        """,
        (user_id,)
    )

    return cursor.fetchone()

# ============================================================
# BOT ONLINE
# ============================================================

@bot.event
async def on_ready():

    print(f"{bot.user} está online!")
    print(f"ID: {bot.user.id}")

    bot.loop.create_task(verificar_treinos())


# ============================================================
# SISTEMA DE XP POR MENSAGEM
# ============================================================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    xp_ganho = 5

    subiu, novo_level = adicionar_xp(
        message.author.id,
        xp_ganho
    )

    if subiu:

        await message.channel.send(
            f"🎉 {message.author.mention} subiu para o **Level {novo_level}**!"
        )

    await bot.process_commands(message)


# ============================================================
# SISTEMA AUTOMÁTICO DE CONCLUSÃO
# ============================================================

async def verificar_treinos():

    await bot.wait_until_ready()

    while not bot.is_closed():

        agora = datetime.now(timezone.utc)

        cursor.execute("""
            SELECT user_id, tipo, canal_id,
                   termino, pontos, aguardando_acao
            FROM treinos
            WHERE aguardando_acao = 0
        """)

        treinos_ativos = cursor.fetchall()

        for treino in treinos_ativos:

            user_id = treino[0]
            tipo = treino[1]
            canal_id = treino[2]
            termino = treino[3]
            pontos = treino[4]

            try:

                termino_data = datetime.fromisoformat(termino)

                if agora >= termino_data:

                    cursor.execute(
                        """
                        UPDATE jogadores
                        SET pontos = pontos + %s
                        WHERE user_id = %s
                        """,
                        (
                            pontos,
                            user_id
                        )
                    )

                    cursor.execute(
                        """
                        DELETE FROM treinos
                        WHERE user_id = %s
                        """,
                        (user_id,)
                    )

                    db.commit()

                    canal = bot.get_channel(canal_id)

                    if canal:

                        membro = canal.guild.get_member(user_id)

                        if membro:

                            await canal.send(
                                f"🎉 {membro.mention} **terminou o teu treino!**\n\n"
                                f"🏋️ Treino: **{TREINOS[tipo]['nome']}**\n"
                                f"📦 Pontos recebidos: **+{pontos}**\n\n"
                                f"Os pontos foram adicionados ao teu inventário."
                            )

            except Exception as erro:

                print(
                    f"Erro ao verificar treino de {user_id}: {erro}"
                )

        await asyncio.sleep(30)

# ============================================================
# !ADDATRIBUTO (STAFF)
# ============================================================

@bot.command()
async def addatributo(ctx, membro: discord.Member = None, atributo: str = None, quantidade: int = None):


    if not is_staff(ctx.author):

        await ctx.send(
            "❌ Não tens permissão para usar este comando."
        )

        return



    if membro is None or atributo is None or quantidade is None:

        await ctx.send(
            "❌ Uso correto:\n"
            "`!addatributo @jogador atributo quantidade`\n\n"
            "Exemplo:\n"
            "`!addatributo @jogador forca 100`"
        )

        return



    atributos_validos = [
        "velocidade",
        "forca",
        "resistencia",
        "manejo",
        "regeneracao",
        "folego",
        "sangue"
    ]


    atributo = atributo.lower()


    if atributo not in atributos_validos:

        await ctx.send(
            "❌ Atributo inválido."
        )

        return



    cursor.execute(
        "SELECT * FROM jogadores WHERE user_id = %s",
        (membro.id,)
    )

    jogador = cursor.fetchone()


    if jogador is None:

        await ctx.send(
            "❌ Esse jogador ainda não tem atributos."
        )

        return



    limite = 1000


    # Oni e híbrido podem ir até 1150
    tipo = obter_tipo(membro)


    if tipo in ["oni", "hibrido"]:

        limite = 1150



    colunas = {
        "velocidade": 2,
        "forca": 3,
        "resistencia": 4,
        "manejo": 5,
        "regeneracao": 6,
        "folego": 7,
        "sangue": 8
    }



    valor_atual = jogador[colunas[atributo]]


    novo_valor = valor_atual + quantidade


    if novo_valor > limite:

        novo_valor = limite



    ganho = novo_valor - valor_atual



    cursor.execute(
        f"""
        UPDATE jogadores
        SET {atributo} = %s
        WHERE user_id = %s
        """,
        (
            novo_valor,
            membro.id
        )
    )


    db.commit()



    await ctx.send(
        f"✅ **Atributo atualizado!**\n\n"
        f"👤 Jogador: {membro.mention}\n"
        f"📊 Atributo: **{atributo.capitalize()}**\n"
        f"➕ Adicionado: **+{ganho} pontos**\n"
        f"📈 Atual: **{novo_valor}/{limite}**"
    )

# ============================================================
# !HELP
# ============================================================

class HelpView(discord.ui.View):

    def __init__(self, author):
        super().__init__(timeout=180)
        self.author = author

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "❌ Apenas quem abriu este menu pode utilizá-lo.",
                ephemeral=True
            )
            return False

        return True

    @discord.ui.select(
        placeholder="📚 Escolhe uma categoria...",
        options=[
            discord.SelectOption(
                label="Início",
                emoji="🏠",
                description="Voltar à página principal",
                value="inicio"
            ),
            discord.SelectOption(
                label="Jogador",
                emoji="👤",
                description="Perfil, atributos, nível e progressão",
                value="jogador"
            ),
            discord.SelectOption(
                label="Equipamentos",
                emoji="⚔️",
                description="Nichirin e equipamentos",
                value="equipamentos"
            ),
            discord.SelectOption(
                label="Treinamentos",
                emoji="🏋️",
                description="Sistema de treinamentos",
                value="treinos"
            ),
            discord.SelectOption(
                label="Economia",
                emoji="💰",
                description="Moedas, loja e compras",
                value="economia"
            ),
            discord.SelectOption(
                label="Staff",
                emoji="🛡️",
                description="Comandos exclusivos da Staff",
                value="staff"
            )
        ]
    )
    async def categoria(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select
    ):

        escolha = select.values[0]

        # ====================================================
        # 🏠 INÍCIO
        # ====================================================

        if escolha == "inicio":

            embed = discord.Embed(
                title="📚 Central de Comandos",
                description=(
                    "Bem-vindo à central de comandos do "
                    "👻 . 𝗟ᥲ᥉t 𝗦᥆ᥙᥣ!\n\n"
                    "Utiliza o menu abaixo para encontrar "
                    "todos os comandos disponíveis.\n\n"
                    "📌 **Categorias disponíveis:**\n"
                    "👤 Jogador\n"
                    "⚔️ Equipamentos\n"
                    "🏋️ Treinamentos\n"
                    "💰 Economia\n"
                    "🛡️ Staff"
                ),
                color=discord.Color.dark_red()
            )

            embed.add_field(
                name="💡 Como utilizar",
                value=(
                    "Seleciona uma categoria no menu acima "
                    "para veres os comandos e a forma correta "
                    "de os utilizar."
                ),
                inline=False
            )

            embed.set_footer(
                text="👻 Last Soul • Central de Comandos"
            )

        # ====================================================
        # 👤 JOGADOR
        # ====================================================

        elif escolha == "jogador":

            embed = discord.Embed(
                title="👤 Comandos de Jogador",
                description="Comandos relacionados com o teu personagem.",
                color=discord.Color.blue()
            )

            embed.add_field(
                name="📊 Atributos",
                value=(
                    "`!atributos`\n"
                    "Mostra os teus atributos atuais.\n\n"

                    "`!atributos @jogador`\n"
                    "Mostra os atributos de outro jogador.\n\n"

                    "`!add <quantidade> <atributo>`\n"
                    "Distribui os teus pontos disponíveis por um atributo."
                ),
                inline=False
            )

            embed.add_field(
                name="📈 Progressão",
                value=(
                    "`!level`\n"
                    "Mostra o teu nível, XP e progresso.\n\n"

                    "`!level @jogador`\n"
                    "Mostra o nível e progresso de outro jogador.\n\n"

                    "`!rank`\n"
                    "Mostra o teu rank e os teus pontos de rank.\n\n"

                    "`!perfil`\n"
                    "Mostra o teu perfil completo."
                ),
                inline=False
            )

            embed.add_field(
                name="📈 Bónus",
                value=(
                    "`!bonus`\n"
                    "Mostra todos os bónus de atributos "
                    "recebidos pelos equipamentos atualmente equipados.\n\n"

                    "`!bonus @jogador`\n"
                    "Mostra os bónus de equipamento de outro jogador."
                ),
                inline=False
            )

            embed.add_field(
                name="🎒 Inventário",
                value=(
                    "`!inventario`\n"
                    "Mostra todos os itens que possuis.\n\n"

                    "`!use <item>`\n"
                    "Utiliza um item consumível do inventário."
                ),
                inline=False
            )

        # ====================================================
        # ⚔️ EQUIPAMENTOS
        # ====================================================

        elif escolha == "equipamentos":

            embed = discord.Embed(
                title="⚔️ Nichirin & Equipamentos",
                description="Gerencia a tua Nichirin e os teus equipamentos.",
                color=discord.Color.red()
            )

            embed.add_field(
                name="🎨 Nichirin",
                value=(
                    "`!nichirin`\n"
                    "Mostra as cores de Nichirin disponíveis e os seus bónus.\n\n"

                    "`!escolhernichirin <cor>`\n"
                    "Escolhe e equipa uma cor de Nichirin.\n\n"

                    "Exemplo:\n"
                    "`!escolhernichirin preta`"
                ),
                inline=False
            )

            embed.add_field(
                name="⚔️ Equipar",
                value=(
                    "`!equipar <item>`\n"
                    "Equipa um item que possuas no inventário.\n\n"

                    "Exemplo:\n"
                    "`!equipar Tsuba do Giyu Tomioka`"
                ),
                inline=False
            )

            embed.add_field(
                name="❌ Desequipar",
                value=(
                    "`!desequipar <tipo>`\n"
                    "Desequipa um equipamento.\n\n"

                    "Tipos disponíveis:\n"
                    "`tsuba`\n"
                    "`haori`\n"
                    "`mascara`"
                ),
                inline=False
            )

        # ====================================================
        # 🏋️ TREINOS
        # ====================================================

        elif escolha == "treinos":

            embed = discord.Embed(
                title="🏋️ Comandos de Treinamento",
                description="Treina o teu personagem para obter pontos.",
                color=discord.Color.orange()
            )

            embed.add_field(
                name="🏋️ Iniciar Treino",
                value=(
                    "`!treinar <tipo>`\n"
                    "Inicia um treinamento.\n\n"

                    "**Tipos de treino:**\n"
                    "🥉 `iniciante`\n"
                    "🥈 `intermediario`\n"
                    "🥇 `extremo`\n\n"

                    "Exemplo:\n"
                    "`!treinar iniciante`"
                ),
                inline=False
            )

            embed.add_field(
                name="⏱️ Gerir Treino",
                value=(
                    "`!finalizar`\n"
                    "Finaliza o treino quando o tempo terminar.\n\n"

                    "`!cancelar`\n"
                    "Cancela o treino atual."
                ),
                inline=False
            )

        # ====================================================
        # 💰 ECONOMIA
        # ====================================================

        elif escolha == "economia":

            embed = discord.Embed(
                title="💰 Economia",
                description="Gerencia as tuas moedas e compras.",
                color=discord.Color.gold()
            )

            embed.add_field(
                name="💸 Carteira",
                value=(
                    "`!saldo`\n"
                    "Mostra a quantidade de moedas que possuis."
                ),
                inline=False
            )

            embed.add_field(
                name="🏪 Loja",
                value=(
                    "`!loja`\n"
                    "Mostra os produtos disponíveis na loja.\n\n"

                    "`!comprar <item>`\n"
                    "Compra um produto da loja.\n\n"

                    "Exemplo:\n"
                    "`!comprar Pequena Casa`"
                ),
                inline=False
            )

        # ====================================================
        # 🛡️ STAFF
        # ====================================================

        elif escolha == "staff":

            if not is_staff(interaction.user):
                return await interaction.response.send_message(
                    "❌ Esta categoria é exclusiva da Staff.",
                    ephemeral=True
                )

            embed = discord.Embed(
                title="🛡️ Comandos da Staff",
                description="Comandos exclusivos para membros da Staff.",
                color=discord.Color.dark_red()
            )

            # ------------------------------------------------
            # 📊 PONTOS & ATRIBUTOS
            # ------------------------------------------------

            embed.add_field(
                name="📊 Pontos & Atributos",
                value=(
                    "`!givepoints @jogador <quantidade>`\n"
                    "Adiciona pontos disponíveis a um jogador.\n\n"

                    "`!addatributo @jogador <atributo> <quantidade>`\n"
                    "Adiciona diretamente pontos a um atributo."
                ),
                inline=False
            )

            # ------------------------------------------------
            # ⭐ XP & LEVEL
            # ------------------------------------------------

            embed.add_field(
                name="⭐ XP & Level",
                value=(
                    "`!givexp @jogador <quantidade>`\n"
                    "Adiciona XP a um jogador.\n\n"

                    "`!setlevel @jogador <nível>`\n"
                    "Define o nível de um jogador."
                ),
                inline=False
            )

            # ------------------------------------------------
            # 🏅 RANKS & MISSÕES
            # ------------------------------------------------

            embed.add_field(
                name="🏅 Ranks & Missões",
                value=(
                    "`!addrank @jogador <quantidade>`\n"
                    "Adiciona ou retira pontos de rank de um jogador.\n\n"

                    "**Exemplos:**\n"
                    "`!addrank @jogador 100`\n"
                    "└ Adiciona 100 pontos de rank.\n\n"

                    "`!addrank @jogador -50`\n"
                    "└ Retira 50 pontos de rank.\n\n"

                    "`!missao`\n"
                    "Abre o sistema de missões para registar uma missão."
                ),
                inline=False
            )

            # ------------------------------------------------
            # 🎁 MYSTERY BOX
            # ------------------------------------------------

            embed.add_field(
                name="🎁 Mystery Box",
                value=(
                    "`!addbox @jogador <quantidade>`\n"
                    "Adiciona Mystery Boxes a um jogador."
                ),
                inline=False
            )

            # ------------------------------------------------
            # 💰 DINHEIRO
            # ------------------------------------------------

            embed.add_field(
                name="💰 Dinheiro",
                value=(
                    "`!addmoney @jogador <quantidade>`\n"
                    "Adiciona moedas à conta de um jogador."
                ),
                inline=False
            )

            # ------------------------------------------------
            # 🏪 GESTÃO DA LOJA
            # ------------------------------------------------

            embed.add_field(
                name="🏪 Gestão da Loja",
                value=(
                    "`!addproduto`\n"
                    "Abre o formulário para adicionar um produto.\n\n"

                    "`!removerproduto`\n"
                    "Abre o formulário para remover um produto."
                ),
                inline=False
            )

            # ------------------------------------------------
            # ⚔️ NICHIRIN
            # ------------------------------------------------

            embed.add_field(
                name="⚔️ Nichirin",
                value=(
                    "`!setnichirin @jogador <cor>`\n"
                    "Define a Nichirin de um jogador.\n\n"

                    "Exemplo:\n"
                    "`!setnichirin @jogador preta`"
                ),
                inline=False
            )

        # ====================================================
        # FOOTER
        # ====================================================

        embed.set_footer(
            text="👻 Last Soul • Usa o menu acima para navegar"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )


# ============================================================
# COMANDO !HELP
# ============================================================

@bot.command()
async def help(ctx):

    embed = discord.Embed(
        title="📚 Central de Comandos",
        description=(
            "Bem-vindo à central de comandos do "
            "👻 . 𝗟ᥲ᥉t 𝗦᥆ᥙᥣ!\n\n"
            "Aqui podes consultar todos os sistemas "
            "e comandos disponíveis no servidor.\n\n"
            "👇 **Seleciona uma categoria no menu abaixo.**"
        ),
        color=discord.Color.dark_red()
    )

    embed.add_field(
        name="👤 Jogador",
        value="Perfil, atributos, nível, rank, bónus e inventário.",
        inline=True
    )

    embed.add_field(
        name="⚔️ Equipamentos",
        value="Nichirin e equipamentos.",
        inline=True
    )

    embed.add_field(
        name="🏋️ Treinamentos",
        value="Sistema de treinos.",
        inline=True
    )

    embed.add_field(
        name="💰 Economia",
        value="Saldo, loja e compras.",
        inline=True
    )

    if is_staff(ctx.author):

        embed.add_field(
            name="🛡️ Staff",
            value="Comandos exclusivos da Staff, incluindo ranks e missões.",
            inline=True
        )

    embed.set_footer(
        text="👻 Last Soul • Central de Comandos"
    )

    await ctx.send(
        embed=embed,
        view=HelpView(ctx.author)
    )

# ============================================================
# OBTER EQUIPAMENTOS
# ============================================================

def obter_equipamentos(user_id):

    cursor.execute(
        """
        SELECT tsuba, haori, nichirin, mascara
        FROM equipamentos
        WHERE user_id = %s
        """,
        (user_id,)
    )

    resultado = cursor.fetchone()

    if resultado is None:

        cursor.execute(
            """
            INSERT INTO equipamentos
            (user_id, tsuba, haori, nichirin, mascara)
            VALUES (%s, NULL, NULL, NULL, NULL)
            ON CONFLICT (user_id) DO NOTHING
            """,
            (user_id,)
        )

        db.commit()

        return (None, None, None, None)

    return resultado


# ============================================================
# CALCULAR BÓNUS DOS EQUIPAMENTOS
# ============================================================

def calcular_bonus_equipamentos(user_id):

    equipamentos = obter_equipamentos(user_id)

    tsuba = equipamentos[0]
    haori = equipamentos[1]
    nichirin = equipamentos[2]
    mascara = equipamentos[3]

    bonus = {
        "velocidade": 0,
        "forca": 0,
        "resistencia": 0,
        "manejo": 0,
        "regeneracao": 0,
        "folego": 0,
        "sangue": 0
    }


    # ========================================================
    # TSUBA / HAORI / MÁSCARA
    # ========================================================

    for item in [tsuba, haori, mascara]:

        if item in BONUS_EQUIPAMENTOS:

            for atributo, valor in BONUS_EQUIPAMENTOS[item].items():

                bonus[atributo] += valor


    # ========================================================
    # NICHIRIN
    # ========================================================

    if nichirin in CORES_NICHIRIN:

        dados = CORES_NICHIRIN[nichirin]

        for atributo, valor in dados["bonus"].items():

            bonus[atributo] += valor


    return bonus
    
# ============================================================
# !ATRIBUTOS
# ============================================================

@bot.command()
async def atributos(ctx, membro: discord.Member = None):

    if not isinstance(ctx.author, discord.Member):
        return

    alvo = membro if membro is not None else ctx.author

    tipo = obter_tipo(alvo)

    if tipo is None:

        await ctx.send(
            f"❌ {alvo.mention} não tem um cargo válido de "
            f"**Humano, Oni ou Híbrido**."
        )

        return

    jogador = obter_jogador(alvo.id)

    if jogador is None:

        await ctx.send(
            f"❌ {alvo.mention} ainda não possui atributos."
        )

        return

    (
        user_id,
        pontos,
        velocidade,
        forca,
        resistencia,
        manejo,
        regeneracao,
        folego,
        sangue
    ) = jogador


    # ========================================================
    # VALORES REAIS
    # ========================================================

    velocidade_real = calcular_velocidade(velocidade)

    forca_real = calcular_forca(forca)

    folego_real = calcular_folego(folego)

    sangue_real = calcular_sangue(sangue)


    # ========================================================
    # BÓNUS DO MANEJO
    # ========================================================

    bonus_manejo = calcular_bonus_manejo(manejo)


    velocidade_final = velocidade_real * (1 + bonus_manejo)

    forca_final = forca_real * (1 + bonus_manejo)


    # ========================================================
    # BÓNUS DOS EQUIPAMENTOS
    # ========================================================

    bonus_equipamentos = calcular_bonus_equipamentos(alvo.id)


    velocidade_final *= (
        1 + bonus_equipamentos["velocidade"] / 100
    )

    forca_final *= (
        1 + bonus_equipamentos["forca"] / 100
    )

    resistencia_final = resistencia * (
        1 + bonus_equipamentos["resistencia"] / 100
    )

    regeneracao_final = regeneracao * (
        1 + bonus_equipamentos["regeneracao"] / 100
    )

    folego_final = folego_real * (
        1 + bonus_equipamentos["folego"] / 100
    )

    sangue_final = sangue_real * (
        1 + bonus_equipamentos["sangue"] / 100
    )


    permitidos = ATRIBUTOS_PERMITIDOS[tipo]

    limite = LIMITES[tipo]


    # ========================================================
    # EQUIPAMENTOS
    # ========================================================

    equipamentos = obter_equipamentos(alvo.id)

    tsuba = equipamentos[0]
    haori = equipamentos[1]
    nichirin = equipamentos[2]
    mascara = equipamentos[3]


    # ========================================================
    # EMBED
    # ========================================================

    embed = discord.Embed(
        title=f"📊 Atributos de {alvo.display_name}",
        color=discord.Color.dark_red()
    )


    # ========================================================
    # VELOCIDADE
    # ========================================================

    if "velocidade" in permitidos:

        texto = (
            f"⚡ **Velocidade**\n"
            f"📊 Pontos: `{velocidade}/{limite}`\n"
            f"🏃 Valor: **{velocidade_final:.2f} km/h**"
        )

    else:

        texto = (
            "⚡ **Velocidade**\n"
            "`🚫 Bloqueado`"
        )

    embed.add_field(
        name="\u200b",
        value=texto,
        inline=True
    )


    # ========================================================
    # FORÇA
    # ========================================================

    if "forca" in permitidos:

        texto = (
            f"💪 **Força**\n"
            f"📊 Pontos: `{forca}/{limite}`\n"
            f"⚖️ Valor: **{forca_final:.2f} kg**"
        )

    else:

        texto = (
            "💪 **Força**\n"
            "`🚫 Bloqueado`"
        )

    embed.add_field(
        name="\u200b",
        value=texto,
        inline=True
    )


    # ========================================================
    # RESISTÊNCIA
    # ========================================================

    if "resistencia" in permitidos:

        texto = (
            f"🛡️ **Resistência**\n"
            f"📊 Pontos: `{resistencia}/{limite}`\n"
            f"📈 Bónus Equipamento: "
            f"**+{bonus_equipamentos['resistencia']:.1f}%**"
        )

    else:

        texto = (
            "🛡️ **Resistência**\n"
            "`🚫 Bloqueado`"
        )

    embed.add_field(
        name="\u200b",
        value=texto,
        inline=True
    )


    # ========================================================
    # MANEJO
    # ========================================================

    if "manejo" in permitidos:

        texto = (
            f"⚔️ **Manejo**\n"
            f"📊 Pontos: `{manejo}/{limite}`\n"
            f"⚡ Bónus: **+{bonus_manejo * 100:.1f}% Velocidade**\n"
            f"💪 Bónus: **+{bonus_manejo * 100:.1f}% Força**"
        )

    else:

        texto = (
            "⚔️ **Manejo**\n"
            "`🚫 Bloqueado`"
        )

    embed.add_field(
        name="\u200b",
        value=texto,
        inline=True
    )


    # ========================================================
    # REGENERAÇÃO
    # ========================================================

    if "regeneracao" in permitidos:

        texto = (
            f"🩸 **Regeneração**\n"
            f"📊 Pontos: `{regeneracao}/{limite}`\n"
            f"📈 Bónus Equipamento: "
            f"**+{bonus_equipamentos['regeneracao']:.1f}%**"
        )

    else:

        texto = (
            "🩸 **Regeneração**\n"
            "`🚫 Bloqueado`"
        )

    embed.add_field(
        name="\u200b",
        value=texto,
        inline=True
    )


    # ========================================================
    # FÔLEGO
    # ========================================================

    if "folego" in permitidos:

        texto = (
            f"🌬️ **Fôlego**\n"
            f"📊 Pontos: `{folego}/{limite}`\n"
            f"💨 Valor: **{folego_final:,.0f}**"
        ).replace(",", ".")

    else:

        texto = (
            "🌬️ **Fôlego**\n"
            "`🚫 Bloqueado`"
        )

    embed.add_field(
        name="\u200b",
        value=texto,
        inline=True
    )


    # ========================================================
    # SANGUE
    # ========================================================

    if "sangue" in permitidos:

        texto = (
            f"🩸 **Sangue**\n"
            f"📊 Pontos: `{sangue}/{limite}`\n"
            f"🩸 Valor: **{sangue_final:,.0f}**"
        ).replace(",", ".")

    else:

        texto = (
            "🩸 **Sangue**\n"
            "`🚫 Bloqueado`"
        )

    embed.add_field(
        name="\u200b",
        value=texto,
        inline=True
    )


    # ========================================================
    # PONTOS DISPONÍVEIS
    # ========================================================

    embed.add_field(
        name="📦 Pontos disponíveis",
        value=f"**{pontos}**",
        inline=False
    )


    # ========================================================
    # CLASSE
    # ========================================================

    embed.add_field(
        name="👤 Classe",
        value=f"**{tipo.capitalize()}**",
        inline=False
    )


    # ========================================================
    # EQUIPAMENTO
    # ========================================================

    nichirin_texto = "Nenhuma"

    if nichirin in CORES_NICHIRIN:

        dados_nichirin = CORES_NICHIRIN[nichirin]

        nichirin_texto = (
            f"{dados_nichirin['emoji']} "
            f"**{dados_nichirin['nome']}**"
        )

    elif nichirin:

        nichirin_texto = f"**{nichirin}**"


    equipamento_texto = (
        f"⚔️ **Tsuba:** {tsuba or 'Nenhuma'}\n"
        f"👘 **Haori:** {haori or 'Nenhum'}\n"
        f"🎭 **Máscara:** {mascara or 'Nenhuma'}\n"
        f"🎨 **Nichirin:** {nichirin_texto}"
    )


    embed.add_field(
        name="⚔️ Equipamentos Equipados",
        value=equipamento_texto,
        inline=False
    )


    await ctx.send(embed=embed)
    
# ============================================================
# !ADD
# ============================================================

@bot.command()
async def add(ctx, quantidade: int, *, atributo: str):

    if not isinstance(ctx.author, discord.Member):
        return


    if quantidade <= 0:

        await ctx.send(
            "❌ A quantidade precisa ser maior que **0**."
        )

        return


    tipo = obter_tipo(ctx.author)


    if tipo is None:

        await ctx.send(
            "❌ Não tens um cargo válido de **Humano, Oni ou Híbrido**."
        )

        return


    jogador = obter_jogador(ctx.author.id)

    pontos = jogador[1]


    if quantidade > pontos:

        await ctx.send(
            f"❌ Não tens pontos suficientes.\n"
            f"📦 Pontos disponíveis: **{pontos}**"
        )

        return


    atributo = atributo.lower().strip()


    nomes = {
        "velocidade": "velocidade",
        "vel": "velocidade",

        "forca": "forca",
        "força": "forca",

        "resistencia": "resistencia",
        "resistência": "resistencia",

        "manejo": "manejo",

        "regeneracao": "regeneracao",
        "regeneração": "regeneracao",
        "regen": "regeneracao",

        "folego": "folego",
        "fôlego": "folego",

        "sangue": "sangue"
    }


    if atributo not in nomes:

        await ctx.send(
            "❌ Atributo inválido."
        )

        return


    atributo = nomes[atributo]


    if atributo not in ATRIBUTOS_PERMITIDOS[tipo]:

        await ctx.send(
            f"❌ **{tipo.capitalize()}** não pode distribuir pontos "
            f"em **{ATRIBUTOS[atributo]['nome']}**."
        )

        return


    limite = LIMITES[tipo]


    cursor.execute(
        f"SELECT {atributo} FROM jogadores WHERE user_id = %s",
        (ctx.author.id,)
    )


    atual = cursor.fetchone()[0]


    if atual + quantidade > limite:

        disponivel = limite - atual

        await ctx.send(
            f"❌ Não podes ultrapassar **{limite}**.\n"
            f"📊 Atual: **{atual}**\n"
            f"📈 Máximo que podes adicionar: **{disponivel}**"
        )

        return


    novo_valor = atual + quantidade
    novos_pontos = pontos - quantidade


    cursor.execute(
        f"""
        UPDATE jogadores
        SET {atributo} = %s,
            pontos = %s
        WHERE user_id = %s
        """,
        (
            novo_valor,
            novos_pontos,
            ctx.author.id
        )
    )


    db.commit()


    await ctx.send(
        f"✅ **{ATRIBUTOS[atributo]['nome']}** aumentou!\n\n"
        f"{ATRIBUTOS[atributo]['emoji']} "
        f"**{atual} → {novo_valor}**\n"
        f"📦 Pontos restantes: **{novos_pontos}**"
    )

# ============================================================
# !GIVEPOINTS (STAFF)
# ============================================================

@bot.command()
async def givepoints(ctx, membro: discord.Member, quantidade: int):

    if not is_staff(ctx.author):

        await ctx.send(
            "❌ Não tens permissão para utilizar este comando."
        )

        return


    if quantidade <= 0:

        await ctx.send(
            "❌ A quantidade precisa ser maior que **0**."
        )

        return


    criar_jogador(membro.id)


    cursor.execute(
        """
        UPDATE jogadores
        SET pontos = pontos + %s
        WHERE user_id = %s
        """,
        (
            quantidade,
            membro.id
        )
    )


    db.commit()


    jogador = obter_jogador(membro.id)

    total = jogador[1]


    await ctx.send(
        f"✅ {membro.mention} recebeu **{quantidade} pontos**.\n"
        f"📦 Inventário atual: **{total} pontos**"
    )


# ============================================================
# !TREINAR
# ============================================================

@bot.command()
async def treinar(ctx, tipo: str):

    if not isinstance(ctx.author, discord.Member):
        return

# ============================================================
# LIMITE DIÁRIO DE TREINOS (3 POR DIA)
# ============================================================

    hoje = datetime.now(timezone.utc).date().isoformat()

    cursor.execute(
    """
    SELECT COUNT(*)
    FROM treinos
    WHERE user_id = %s
    AND DATE(inicio) = %s
    AND aguardando_acao = 0
    """,
    (
        ctx.author.id,
        hoje
    )
)

    treinos_hoje = cursor.fetchone()[0]


    if treinos_hoje >= 3:

        await ctx.send(
            f"❌ {ctx.author.mention}, atingiste o limite diário de treinos.\n\n"
            f"🏋️ Limite máximo: **3 treinos por dia**.\n"
            f"Volta amanhã para treinar novamente."
        )

        return


    tipo = tipo.lower().strip()

    if tipo not in TREINOS:

        await ctx.send(
            "❌ Tipo de treino inválido.\n\n"
            "Usa:\n"
            "`!treinar iniciante`\n"
            "`!treinar intermediario`\n"
            "`!treinar extremo`"
        )

        return

    treino_existente = obter_treino(ctx.author.id)

    if treino_existente:

        await ctx.send(
            "❌ Já tens um treino em andamento.\n"
            "Termina ou aguarda o treino atual antes de começar outro."
        )

        return

    pode, motivo = pode_fazer_treino(
        ctx.author,
        tipo
    )

    if not pode:

        await ctx.send(motivo)

        return

    treino = TREINOS[tipo]

    prodigio = eh_prodigio(ctx.author)

    caracteres = treino["caracteres"]
    tempo = treino["tempo"]
    pontos = treino["pontos"]

    if prodigio:

        caracteres = caracteres // 2
        tempo = tempo // 2

        # +25%, arredondado para baixo
        pontos = math.floor(pontos * 1.25)

    minutos = tempo // 60

    if minutos >= 60:

        horas = minutos // 60
        minutos_restantes = minutos % 60

        if minutos_restantes:
            duracao_texto = (
                f"{horas}h {minutos_restantes}min"
            )
        else:
            duracao_texto = f"{horas}h"

    else:

        duracao_texto = f"{minutos}min"

    agora = datetime.now(timezone.utc)

    # Guardamos o treino como "aguardando ação".
    # O horário de início real só será criado depois da ação.
    cursor.execute(
        """
        INSERT INTO treinos
        (user_id, tipo, canal_id, inicio, termino, pontos, aguardando_acao)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            ctx.author.id,
            tipo,
            ctx.channel.id,
            agora.isoformat(),
            agora.isoformat(),
            pontos,
            1
        )
    )

    db.commit()

    embed = discord.Embed(
        title=f"🏋️ {treino['nome']}",
        description=(
            f"{ctx.author.mention}, prepara-te para o treino.\n\n"

            f"📝 **Ação necessária:**\n"
            f"Deves enviar uma ação com **pelo menos "
            f"{caracteres} caracteres**.\n\n"

            f"⏳ Tens **15 minutos** para enviar a ação.\n\n"

            f"⏱️ **Duração do treino:** {duracao_texto}\n"
            f"📦 **Recompensa:** +{pontos} pontos"
        ),
        color=discord.Color.orange()
    )

    if prodigio:

        embed.add_field(
            name="🧞 Benefício de Prodígio",
            value=(
                "Os requisitos deste treino foram reduzidos em **50%** "
                "e a recompensa recebeu **+25%**."
            ),
            inline=False
        )

    embed.set_footer(
        text="Envie a sua ação neste canal para iniciar o treino."
    )

    await ctx.send(embed=embed)

    def verificar_mensagem(message):

        return (
            message.author.id == ctx.author.id
            and message.channel.id == ctx.channel.id
            and not message.author.bot
        )

    try:

        mensagem = await bot.wait_for(
            "message",
            timeout=900,
            check=verificar_mensagem
        )

    except asyncio.TimeoutError:

        cursor.execute(
            "DELETE FROM treinos WHERE user_id = %s",
            (ctx.author.id,)
        )

        db.commit()

        await ctx.send(
            f"❌ {ctx.author.mention}, o tempo de **15 minutos** "
            f"para enviar a ação acabou.\n"
            f"O treino foi **cancelado**."
        )

        return

    quantidade_caracteres = len(mensagem.content)

    if quantidade_caracteres < caracteres:

        cursor.execute(
            "DELETE FROM treinos WHERE user_id = %s",
            (ctx.author.id,)
        )

        db.commit()

        await ctx.send(
            f"❌ {ctx.author.mention}, a tua ação possui "
            f"**{quantidade_caracteres} caracteres**.\n\n"
            f"Este treino exige pelo menos **{caracteres} caracteres**.\n"
            f"O treino foi **cancelado**."
        )

        return

    inicio = datetime.now(timezone.utc)
    termino = inicio + timedelta(seconds=tempo)

    cursor.execute(
        """
        UPDATE treinos
        SET inicio = %s,
            termino = %s,
            aguardando_acao = 0
        WHERE user_id = %s
        """,
        (
            inicio.isoformat(),
            termino.isoformat(),
            ctx.author.id
        )
    )

    db.commit()

    timestamp = int(termino.timestamp())

    await ctx.send(
        f"✅ **Treino iniciado!**\n\n"
        f"👤 Jogador: {ctx.author.mention}\n"
        f"🏋️ Treino: **{treino['nome']}**\n"
        f"📝 Caracteres: **{quantidade_caracteres}/{caracteres}**\n"
        f"⏱️ Duração: **{duracao_texto}**\n"
        f"🏁 Término: <t:{timestamp}:R>\n"
        f"📦 Recompensa: **+{pontos} pontos**\n\n"
        f"Quando o tempo terminar, usa `!finalizar`."
    )

# ============================================================
# !CANCELAR
# ============================================================

@bot.command()
async def cancelar(ctx):

    if not isinstance(ctx.author, discord.Member):
        return

    treino = obter_treino(ctx.author.id)

    if not treino:

        await ctx.send(
            "❌ Não tens nenhum treino em andamento."
        )

        return

    tipo = treino[1]
    aguardando_acao = treino[6]

    cursor.execute(
        "DELETE FROM treinos WHERE user_id = %s",
        (ctx.author.id,)
    )

    db.commit()

    if aguardando_acao == 1:

        mensagem = (
            f"🛑 {ctx.author.mention}, o teu pedido de "
            f"**{TREINOS[tipo]['nome']}** foi cancelado."
        )

    else:

        mensagem = (
            f"🛑 {ctx.author.mention}, o teu "
            f"**{TREINOS[tipo]['nome']}** foi cancelado.\n"
            f"📦 Nenhum ponto foi recebido."
        )

    await ctx.send(mensagem)

# ============================================================
# !FINALIZAR
# ============================================================

@bot.command()
async def finalizar(ctx):

    if not isinstance(ctx.author, discord.Member):
        return

    treino = obter_treino(ctx.author.id)

    if not treino:

        await ctx.send(
            "❌ Não tens nenhum treino em andamento."
        )

        return

    (
        user_id,
        tipo,
        canal_id,
        inicio,
        termino,
        pontos,
        aguardando_acao
    ) = treino

    if aguardando_acao == 1:

        await ctx.send(
            "❌ O teu treino ainda não foi iniciado."
        )

        return

    termino_data = datetime.fromisoformat(termino)
    agora = datetime.now(timezone.utc)

    if agora < termino_data:

        restante = termino_data - agora
        segundos = int(restante.total_seconds())

        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segundos_restantes = segundos % 60

        if horas > 0:

            tempo_texto = (
                f"{horas}h {minutos}min"
            )

        else:

            tempo_texto = (
                f"{minutos}min {segundos_restantes}s"
            )

        await ctx.send(
            f"⏳ **O teu treino ainda não terminou!**\n"
            f"Tempo restante: **{tempo_texto}**"
        )

        return

    cursor.execute(
        """
        UPDATE jogadores
        SET pontos = pontos + %s
        WHERE user_id = %s
        """,
        (
            pontos,
            ctx.author.id
        )
    )

    cursor.execute(
        "DELETE FROM treinos WHERE user_id = %s",
        (ctx.author.id,)
    )

    db.commit()

    jogador = obter_jogador(ctx.author.id)
    total = jogador[1]

    await ctx.send(
        f"🎉 {ctx.author.mention} **treino concluído!**\n\n"
        f"🏋️ Treino: **{TREINOS[tipo]['nome']}**\n"
        f"📦 Pontos recebidos: **+{pontos}**\n"
        f"💰 Inventário atual: **{total} pontos**"
    )

# ============================================================
# !LEVEL
# ============================================================

@bot.command()
async def level(ctx, membro: discord.Member = None):

    if membro is None:
        membro = ctx.author


    jogador = obter_nivel(membro.id)

    xp = jogador[0]
    nivel = jogador[1]


    xp_necessario = xp_para_proximo_level(nivel)


    progresso = int((xp / xp_necessario) * 10)


    barra = "█" * progresso + "░" * (10 - progresso)


    await ctx.send(
        f"⚔️ **{membro.display_name}**\n\n"
        f"⭐ Level: **{nivel}**\n"
        f"✨ XP: **{xp}/{xp_necessario}**\n\n"
        f"{barra}"
    )

# ============================================================
# !PERFIL
# ============================================================

@bot.command()
async def perfil(ctx):

    # ========================================================
    # PROGRESSÃO
    # ========================================================

    nivel = obter_nivel(ctx.author.id)

    xp = nivel[0]
    level = nivel[1]

    mysteryboxes = obter_mysterybox(ctx.author.id)


    # ========================================================
    # ATRIBUTOS
    # ========================================================

    jogador = obter_jogador(ctx.author.id)

    velocidade = jogador[2]
    forca = jogador[3]
    resistencia = jogador[4]
    manejo = jogador[5]
    regeneracao = jogador[6]
    folego = jogador[7]
    sangue = jogador[8]


    # ========================================================
    # EQUIPAMENTOS
    # ========================================================

    equipamentos = obter_equipamentos(ctx.author.id)

    tsuba = equipamentos[0]
    haori = equipamentos[1]
    nichirin = equipamentos[2]
    mascara = equipamentos[3]


    # ========================================================
    # NICHIRIN
    # ========================================================

    if nichirin in CORES_NICHIRIN:

        dados_nichirin = CORES_NICHIRIN[nichirin]

        nichirin_texto = (
            f"{dados_nichirin['emoji']} "
            f"**{dados_nichirin['nome']}**"
        )

    elif nichirin:

        nichirin_texto = f"🎨 **{nichirin}**"

    else:

        nichirin_texto = "❌ Nenhuma"


    # ========================================================
    # EQUIPAMENTOS
    # ========================================================

    equipamentos_texto = (
        f"⚔️ **Tsuba:** {tsuba or '❌ Nenhuma'}\n"
        f"👘 **Haori:** {haori or '❌ Nenhum'}\n"
        f"🎭 **Máscara:** {mascara or '❌ Nenhuma'}\n"
        f"🎨 **Nichirin:** {nichirin_texto}"
    )


    # ========================================================
    # EMBED
    # ========================================================

    embed = discord.Embed(
        title=f"⚔️ Perfil de {ctx.author.display_name}",
        color=discord.Color.blue()
    )


    # ========================================================
    # PROGRESSÃO
    # ========================================================

    embed.add_field(
        name="⭐ Progressão",
        value=(
            f"Level: **{level}**\n"
            f"XP: **{xp}**\n"
            f"🎁 Mystery Boxes: **{mysteryboxes}**"
        ),
        inline=False
    )


    # ========================================================
    # ATRIBUTOS
    # ========================================================

    embed.add_field(
        name="📊 Atributos",
        value=(
            f"⚡ Velocidade: **{velocidade} pontos**\n"
            f"💪 Força: **{forca} pontos**\n"
            f"🛡️ Resistência: **{resistencia} pontos**\n"
            f"⚔️ Manejo: **{manejo} pontos**\n"
            f"❤️ Regeneração: **{regeneracao} pontos**\n"
            f"🌊 Fôlego: **{folego} pontos**\n"
            f"🩸 Sangue: **{sangue} pontos**"
        ),
        inline=False
    )


    # ========================================================
    # EQUIPAMENTOS
    # ========================================================

    embed.add_field(
        name="⚔️ Equipamentos Equipados",
        value=equipamentos_texto,
        inline=False
    )


    # ========================================================
    # ENVIO
    # ========================================================

    await ctx.send(
        embed=embed,
        view=MysteryBoxView()
    )
    
# ============================================================
# !INVENTARIO
# ============================================================

@bot.command()
async def inventario(ctx):

    itens = obter_inventario(ctx.author.id)

    embed = discord.Embed(
        title=f"🎒 Inventário de {ctx.author.display_name}",
        color=discord.Color.green()
    )

    if not itens:

        embed.description = "O teu inventário está vazio."

    else:

        lista_itens = ""

        for item, quantidade in itens:
            lista_itens += f"• {item} x{quantidade}\n"

        embed.description = lista_itens


    await ctx.send(embed=embed)

# ============================================================
# !ADDBOX (STAFF)
# ============================================================

@bot.command()
async def addbox(ctx, membro: discord.Member, quantidade: int):

    if not is_staff(ctx.author):

        return await ctx.send(
            "❌ Não tens permissão para utilizar este comando."
        )


    if quantidade <= 0:

        return await ctx.send(
            "❌ A quantidade precisa ser maior que **0**."
        )


    adicionar_mysterybox(
        membro.id,
        quantidade
    )


    await ctx.send(
        f"🎁 {membro.mention} recebeu **{quantidade} Mystery Box(es)**!"
    )

# ============================================================
# !GIVEXP (STAFF)
# ============================================================

@bot.command()
async def givexp(ctx, membro: discord.Member, quantidade: int):

    if not is_staff(ctx.author):

        return await ctx.send(
            "❌ Não tens permissão para utilizar este comando."
        )


    if quantidade <= 0:

        return await ctx.send(
            "❌ A quantidade de XP precisa ser maior que **0**."
        )


    subiu, novo_level = adicionar_xp(
        membro.id,
        quantidade
    )


    mensagem = (
        f"⭐ {quantidade} XP adicionados a {membro.mention}!"
    )


    if subiu:

        mensagem += (
            f"\n🎉 {membro.mention} subiu para o Level "
            f"**{novo_level}**!"
        )


        if novo_level % 10 == 0:

            mensagem += (
                "\n🎁 Recebeu uma Mystery Box por atingir este nível!"
            )


    await ctx.send(mensagem)

# ============================================================
# !SALDO
# ============================================================

@bot.command()
async def saldo(ctx):

    dinheiro = obter_dinheiro(ctx.author.id)

    embed = discord.Embed(
        title="💸 Carteira",
        description=f"Possuis **{dinheiro} 💸**",
        color=discord.Color.gold()
    )

    await ctx.send(embed=embed)

# ============================================================
# !ADDMONEY (STAFF)
# ============================================================

@bot.command()
async def addmoney(ctx, membro: discord.Member, quantidade: int):

    if not is_staff(ctx.author):
        return await ctx.send("❌ Sem permissão.")


    adicionar_dinheiro(
        membro.id,
        quantidade
    )


    await ctx.send(
        f"💸 {membro.mention} recebeu **{quantidade} moedas**."
    )

# ============================================================
# FORMULÁRIO ADICIONAR PRODUTO
# ============================================================

class AdicionarProdutoModal(Modal):

    def __init__(self):
        super().__init__(
            title="🏪 Adicionar Produto"
        )

        self.nome = TextInput(
            label="📦 Nome do Item",
            placeholder="Ex: Pequena Casa",
            required=True,
            max_length=100
        )

        self.preco = TextInput(
            label="💸 Preço",
            placeholder="Ex: 5000",
            required=True,
            max_length=10
        )

        self.descricao = TextInput(
            label="📝 Descrição",
            placeholder="Ex: Uma pequena casa para o personagem.",
            required=True,
            style=discord.TextStyle.paragraph,
            max_length=300
        )


        self.add_item(self.nome)
        self.add_item(self.preco)
        self.add_item(self.descricao)



    async def on_submit(self, interaction: discord.Interaction):

        try:
            preco = int(self.preco.value)

        except:

            return await interaction.response.send_message(
                "❌ O preço precisa ser um número.",
                ephemeral=True
            )


        adicionar_produto(
            self.nome.value,
            preco,
            self.descricao.value
        )


        embed = discord.Embed(
            title="✅ Produto Adicionado à Loja",
            color=discord.Color.green()
        )


        embed.add_field(
            name="📦 Item",
            value=self.nome.value,
            inline=False
        )


        embed.add_field(
            name="💸 Preço",
            value=f"{preco} 💸",
            inline=False
        )


        embed.add_field(
            name="📝 Descrição",
            value=self.descricao.value,
            inline=False
        )


        await interaction.response.send_message(
            embed=embed
        )



# ============================================================
# BOTÃO PARA ABRIR FORMULÁRIO
# ============================================================

class AdicionarProdutoButton(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=60)


    @discord.ui.button(
        label="🏪 Adicionar Produto",
        style=discord.ButtonStyle.green
    )
    async def adicionar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not is_staff(interaction.user):

            return await interaction.response.send_message(
                "❌ Sem permissão.",
                ephemeral=True
            )


        await interaction.response.send_modal(
            AdicionarProdutoModal()
        )


# ============================================================
# !ADDPRODUTO (STAFF)
# ============================================================

@bot.command()
async def addproduto(ctx):

    if not is_staff(ctx.author):

        return await ctx.send(
            "❌ Não tens permissão."
        )


    embed = discord.Embed(
        title="🏪 Adicionar Produto",
        description=(
            "Clica no botão abaixo para abrir "
            "o formulário de criação de produto."
        ),
        color=discord.Color.green()
    )


    await ctx.send(
        embed=embed,
        view=AdicionarProdutoButton()
    )

# ============================================================
# FORMULÁRIO REMOVER PRODUTO
# ============================================================

class RemoverProdutoModal(Modal):

    def __init__(self):
        super().__init__(
            title="🗑️ Remover Produto"
        )


        self.nome = TextInput(
            label="📦 Nome do Item",
            placeholder="Ex: Pequena Casa",
            required=True,
            max_length=100
        )


        self.add_item(self.nome)



    async def on_submit(self, interaction: discord.Interaction):

        remover_produto(
            self.nome.value
        )


        embed = discord.Embed(
            title="🗑️ Produto Removido",
            description=f"O item **{self.nome.value}** foi removido da loja.",
            color=discord.Color.red()
        )


        await interaction.response.send_message(
            embed=embed
        )



# ============================================================
# BOTÃO PARA REMOVER PRODUTO
# ============================================================

class RemoverProdutoButton(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=60)


    @discord.ui.button(
        label="🗑️ Remover Produto",
        style=discord.ButtonStyle.red
    )
    async def remover(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not is_staff(interaction.user):

            return await interaction.response.send_message(
                "❌ Sem permissão.",
                ephemeral=True
            )


        await interaction.response.send_modal(
            RemoverProdutoModal()
        )



# ============================================================
# !REMOVERPRODUTO (STAFF)
# ============================================================

@bot.command()
async def removerproduto(ctx):

    if not is_staff(ctx.author):

        return await ctx.send(
            "❌ Não tens permissão."
        )


    embed = discord.Embed(
        title="🗑️ Remover Produto",
        description=(
            "Clica no botão abaixo para abrir "
            "o formulário de remoção."
        ),
        color=discord.Color.red()
    )


    await ctx.send(
        embed=embed,
        view=RemoverProdutoButton()
    )

# ============================================================
# !LOJA
# ============================================================

@bot.command()
async def loja(ctx):

    produtos = obter_produtos()

    if not produtos:

        return await ctx.send(
            "🏪 A loja está vazia neste momento."
        )


    dinheiro = obter_dinheiro(
        ctx.author.id
    )


    embed = discord.Embed(
        title="🏪 Loja — Last Soul",
        description=(
            f"💸 O teu saldo: **{dinheiro} moedas**\n\n"
            "Produtos disponíveis:"
        ),
        color=discord.Color.gold()
    )


    for produto in produtos:

        id_produto = produto[0]
        nome = produto[1]
        preco = produto[2]
        descricao = produto[3]


        embed.add_field(
            name=f"📦 {id_produto} | {nome}",
            value=(
                f"💸 Preço: **{preco} moedas**\n"
                f"📝 {descricao}"
            ),
            inline=False
        )


    embed.set_footer(
        text="Usa !comprar <ID> para comprar um produto."
    )


    await ctx.send(
        embed=embed
    )

# ============================================================
# !COMPRAR
# ============================================================

@bot.command()
async def comprar(ctx, *, nome):

    cursor.execute(
        """
        SELECT nome, preco, descricao
        FROM loja
        WHERE LOWER(nome) = LOWER(%s)
        """,
        (nome,)
    )

    produto = cursor.fetchone()


    if produto is None:

        return await ctx.send(
            "❌ Esse item não existe na loja."
        )


    nome_item = produto[0]
    preco = produto[1]
    descricao = produto[2]


    dinheiro = obter_dinheiro(
        ctx.author.id
    )


    if dinheiro < preco:

        return await ctx.send(
            f"❌ Não tens dinheiro suficiente.\n"
            f"💸 Precisas de **{preco} moedas**."
        )


    remover_dinheiro(
        ctx.author.id,
        preco
    )


    adicionar_item(
        ctx.author.id,
        nome_item
    )


    embed = discord.Embed(
        title="🛒 Compra realizada!",
        color=discord.Color.green()
    )


    embed.add_field(
        name="📦 Item",
        value=nome_item,
        inline=False
    )

    embed.add_field(
        name="💸 Valor pago",
        value=f"{preco} moedas",
        inline=False
    )

    embed.add_field(
        name="📝 Descrição",
        value=descricao,
        inline=False
    )


    await ctx.send(
        embed=embed
    )

# ============================================================
# !USE
# ============================================================

@bot.command()
async def use(ctx, *, item):

    inventario = obter_inventario(
        ctx.author.id
    )


    item_encontrado = None
    quantidade = 0


    for nome, qtd in inventario:

        if nome.lower() == item.lower():

            item_encontrado = nome
            quantidade = qtd
            break



    if item_encontrado is None:

        return await ctx.send(
            "❌ Não possuis esse item no inventário."
        )



    if quantidade <= 0:

        return await ctx.send(
            "❌ Não tens nenhuma unidade desse item."
        )



    # Remove 1 unidade do inventário

    remover_item(
        ctx.author.id,
        item_encontrado,
        1
    )


    embed = discord.Embed(
        title="✨ Item usado",
        description=(
            f"📦 Usaste **{item_encontrado}**.\n\n"
            "O efeito deste item será definido futuramente."
        ),
        color=discord.Color.green()
    )


    await ctx.send(
        embed=embed
    )

# ============================================================
# !SETLEVEL (STAFF)
# ============================================================

@bot.command()
async def setlevel(ctx, membro: discord.Member, nivel: int):

    if not is_staff(ctx.author):

        return await ctx.send(
            "❌ Não tens permissão para utilizar este comando."
        )


    if nivel < 1:

        return await ctx.send(
            "❌ O nível mínimo é **1**."
        )


    criar_nivel(membro.id)


    cursor.execute(
        """
        UPDATE niveis
        SET level = %s
        WHERE user_id = %s
        """,
        (
            nivel,
            membro.id
        )
    )


    db.commit()


    await ctx.send(
        f"⭐ O nível de {membro.mention} foi alterado para **Level {nivel}**."
    )

# ============================================================
# CORES DA NICHIRIN
# ============================================================

CORES_NICHIRIN = {

    # ========================================================
    # CORES COMUNS
    # ========================================================

    "preta": {
        "nome": "Preta",
        "emoji": "⚫",
        "raridade": "comum",
        "bonus": {
            "forca": 5
        }
    },

    "azul": {
        "nome": "Azul",
        "emoji": "🔵",
        "raridade": "comum",
        "bonus": {
            "resistencia": 5
        }
    },

    "vermelha": {
        "nome": "Vermelha",
        "emoji": "🔴",
        "raridade": "comum",
        "bonus": {
            "forca": 5
        }
    },

    "verde": {
        "nome": "Verde",
        "emoji": "🟢",
        "raridade": "comum",
        "bonus": {
            "velocidade": 5
        }
    },

    "branca": {
        "nome": "Branca",
        "emoji": "⚪",
        "raridade": "comum",
        "bonus": {
            "folego": 5
        }
    },


    # ========================================================
    # CORES ESPECIAIS
    # ========================================================

    "amarela": {
        "nome": "Amarela",
        "emoji": "🟡",
        "raridade": "rara",
        "bonus": {
            "velocidade": 10
        }
    },

    "rosa": {
        "nome": "Rosa",
        "emoji": "🩷",
        "raridade": "rara",
        "bonus": {
            "velocidade": 10,
            "forca": 5
        }
    },

    "roxa": {
        "nome": "Roxa",
        "emoji": "🟣",
        "raridade": "rara",
        "bonus": {
            "velocidade": 10,
            "folego": 5
        }
    },

    "verde-clara": {
        "nome": "Verde-clara",
        "emoji": "🟢",
        "raridade": "rara",
        "bonus": {
            "forca": 10,
            "velocidade": 5
        }
    },

    "branca-cinza": {
        "nome": "Branca-Cinza",
        "emoji": "🌫️",
        "raridade": "rara",
        "bonus": {
            "velocidade": 10,
            "folego": 10
        }
    },

    "vermelho-alaranjada": {
        "nome": "Vermelho-alaranjada",
        "emoji": "🔥",
        "raridade": "rara",
        "bonus": {
            "forca": 15,
            "resistencia": 5
        }
    },

    "azul-escura": {
        "nome": "Azul-escura",
        "emoji": "🔵",
        "raridade": "rara",
        "bonus": {
            "resistencia": 10,
            "folego": 10
        }
    },

    "cinza": {
        "nome": "Cinza",
        "emoji": "🩶",
        "raridade": "rara",
        "bonus": {
            "forca": 15,
            "resistencia": 10
        }
    },

    "ambar": {
        "nome": "Âmbar",
        "emoji": "🟠",
        "raridade": "rara",
        "bonus": {
            "velocidade": 10,
            "forca": 10
        }
    }
}

# ============================================================
# SISTEMA DE NICHIRIN
# ============================================================

def criar_nichirin(user_id):

    cursor.execute(
        """
        INSERT INTO nichirin_jogadores (user_id)
        VALUES (%s)
        ON CONFLICT (user_id) DO NOTHING
        """,
        (user_id,)
    )

    db.commit()


def obter_cores_nichirin(user_id):

    criar_nichirin(user_id)

    cursor.execute(
        """
        SELECT cores
        FROM nichirin_jogadores
        WHERE user_id = %s
        """,
        (user_id,)
    )

    resultado = cursor.fetchone()

    if resultado is None:
        return []

    return resultado[0] or []


def adicionar_cor_nichirin(user_id, cor):

    criar_nichirin(user_id)

    cores = obter_cores_nichirin(user_id)

    cor = cor.lower()

    if cor not in cores:

        cores.append(cor)

        cursor.execute(
            """
            UPDATE nichirin_jogadores
            SET cores = %s
            WHERE user_id = %s
            """,
            (cores, user_id)
        )

        db.commit()

        return True

    return False

# ============================================================
# BÓNUS DOS EQUIPAMENTOS
# ============================================================

BONUS_EQUIPAMENTOS = {

    # ========================================================
    # TSUBAS
    # ========================================================

    "Tsuba do Giyu Tomioka": {
        "resistencia": 5
    },

    "Tsuba do Kyojuro Rengoku": {
        "forca": 7
    },

    "Tsuba do Tengen Uzui": {
        "velocidade": 5,
        "forca": 3
    },


    # ========================================================
    # HAORIS / ROUPAS
    # ========================================================

    "Haori do Kyojuro Rengoku": {
        "forca": 8,
        "resistencia": 3
    },

    "Haori do Giyu Tomioka": {
        "resistencia": 5,
        "folego": 5
    },

    "Roupa do Akaza": {
        "forca": 8,
        "velocidade": 5
    },

    "Roupa do Douma": {
        "folego": 8,
        "velocidade": 5
    },

    "Roupa do Kokushibo": {
        "forca": 8,
        "velocidade": 8
    },

    "Roupa do Muzan": {
        "forca": 10,
        "velocidade": 10,
        "regeneracao": 5
    },


    # ========================================================
    # MÁSCARAS
    # ========================================================

    "Máscara de Sabito": {
        "velocidade": 5
    },

    "Máscara de Makomo": {
        "folego": 5
    },

    "Máscara de Urokodaki": {
        "resistencia": 5
    },

    "Máscara de Javali": {
        "forca": 5
    },

    "Máscara Oni Simples": {
        "forca": 3,
        "resistencia": 3
    },

    "Máscara Oni Demoníaca": {
        "forca": 7,
        "regeneracao": 3
    },

    "Ratos musculosos do Uzui": {
        "forca": 5,
        "velocidade": 5
    },

    "Chuntaro": {
        "velocidade": 5
    }
}


# ============================================================
# BÓNUS DAS NICHIRINS
# ============================================================

CORES_NICHIRIN = {

    # ========================================================
    # COMUNS
    # ========================================================

    "preta": {
        "nome": "Preta",
        "emoji": "⚫",
        "raridade": "comum",
        "bonus": {
            "forca": 5
        }
    },

    "azul": {
        "nome": "Azul",
        "emoji": "🔵",
        "raridade": "comum",
        "bonus": {
            "resistencia": 5
        }
    },

    "vermelha": {
        "nome": "Vermelha",
        "emoji": "🔴",
        "raridade": "comum",
        "bonus": {
            "forca": 5
        }
    },

    "verde": {
        "nome": "Verde",
        "emoji": "🟢",
        "raridade": "comum",
        "bonus": {
            "velocidade": 5
        }
    },

    "branca": {
        "nome": "Branca",
        "emoji": "⚪",
        "raridade": "comum",
        "bonus": {
            "folego": 5
        }
    },


    # ========================================================
    # ESPECIAIS
    # ========================================================

    "amarela": {
        "nome": "Amarela",
        "emoji": "🟡",
        "raridade": "rara",
        "bonus": {
            "velocidade": 10
        }
    },

    "rosa": {
        "nome": "Rosa",
        "emoji": "🩷",
        "raridade": "rara",
        "bonus": {
            "velocidade": 10,
            "forca": 5
        }
    },

    "roxa": {
        "nome": "Roxa",
        "emoji": "🟣",
        "raridade": "rara",
        "bonus": {
            "velocidade": 10,
            "folego": 5
        }
    },

    "verde-clara": {
        "nome": "Verde-clara",
        "emoji": "🟢",
        "raridade": "rara",
        "bonus": {
            "forca": 10,
            "velocidade": 5
        }
    },

    "branca-cinza": {
        "nome": "Branca-Cinza",
        "emoji": "🌫️",
        "raridade": "rara",
        "bonus": {
            "velocidade": 10,
            "folego": 10
        }
    },

    "vermelho-alaranjada": {
        "nome": "Vermelho-alaranjada",
        "emoji": "🔥",
        "raridade": "rara",
        "bonus": {
            "forca": 15,
            "resistencia": 5
        }
    },

    "azul-escura": {
        "nome": "Azul-escura",
        "emoji": "🔵",
        "raridade": "rara",
        "bonus": {
            "resistencia": 10,
            "folego": 10
        }
    },

    "cinza": {
        "nome": "Cinza",
        "emoji": "🩶",
        "raridade": "rara",
        "bonus": {
            "forca": 15,
            "resistencia": 10
        }
    },

    "ambar": {
        "nome": "Âmbar",
        "emoji": "🟠",
        "raridade": "rara",
        "bonus": {
            "velocidade": 10,
            "forca": 10
        }
    }
}

# ============================================================
# EQUIPAR ITEM
# ============================================================

@bot.command()
async def equipar(ctx, *, item: str = None):

    if item is None:

        return await ctx.send(
            "❌ Indica o item que queres equipar.\n"
            "Exemplo: `!equipar Tsuba do Giyu Tomioka`"
        )


    item = item.strip()


    # ========================================================
    # VERIFICAR INVENTÁRIO
    # ========================================================

    inventario = obter_inventario(ctx.author.id)

    possui_item = False

    for nome_item, quantidade in inventario:

        if nome_item.lower() == item.lower() and quantidade > 0:

            possui_item = True
            item = nome_item
            break


    if not possui_item:

        return await ctx.send(
            f"❌ Não tens **{item}** no teu inventário."
        )


    # ========================================================
    # IDENTIFICAR TIPO
    # ========================================================

    tipo_item = None

    if item.startswith("Tsuba"):

        tipo_item = "tsuba"

    elif item.startswith("Haori") or item.startswith("Roupa"):

        tipo_item = "haori"

    elif item.startswith("Máscara"):

        tipo_item = "mascara"


    if tipo_item is None:

        return await ctx.send(
            "❌ Esse item não pode ser equipado."
        )


    # ========================================================
    # VERIFICAR RESTRIÇÃO
    # ========================================================

    tipo_jogador = obter_tipo(ctx.author)


    restricoes = {

        "Tsuba do Giyu Tomioka": "humano",
        "Tsuba do Kyojuro Rengoku": "humano",
        "Tsuba do Tengen Uzui": "humano",

        "Haori do Kyojuro Rengoku": "humano",
        "Haori do Giyu Tomioka": "humano",

        "Roupa do Akaza": "oni",
        "Roupa do Douma": "oni",
        "Roupa do Kokushibo": "oni",
        "Roupa do Muzan": "oni"
    }


    restricao = restricoes.get(item)


    if restricao is not None:

        if tipo_jogador != restricao and tipo_jogador != "hibrido":

            return await ctx.send(
                f"❌ **{item}** só pode ser utilizado por "
                f"**{restricao.capitalize()}s**."
            )


    # ========================================================
    # EQUIPAR
    # ========================================================

    coluna = tipo_item


    cursor.execute(
        f"""
        INSERT INTO equipamentos
        (user_id, {coluna})
        VALUES (%s, %s)

        ON CONFLICT (user_id)
        DO UPDATE SET {coluna} = EXCLUDED.{coluna}
        """,
        (
            ctx.author.id,
            item
        )
    )


    db.commit()


    await ctx.send(
        f"✅ {ctx.author.mention} equipou "
        f"**{item}**!\n\n"
        f"⚔️ O equipamento já está a aplicar os seus bônus."
    )

# ============================================================
# DESEQUIPAR ITEM
# ============================================================

@bot.command()
async def desequipar(ctx, tipo: str = None):

    if tipo is None:

        return await ctx.send(
            "❌ Indica o tipo de equipamento.\n\n"
            "`!desequipar tsuba`\n"
            "`!desequipar haori`\n"
            "`!desequipar mascara`"
        )


    tipo = tipo.lower()


    colunas_validas = {
        "tsuba": "tsuba",
        "haori": "haori",
        "mascara": "mascara"
    }


    if tipo not in colunas_validas:

        return await ctx.send(
            "❌ Tipo inválido.\n"
            "Usa: `tsuba`, `haori` ou `mascara`."
        )


    coluna = colunas_validas[tipo]


    cursor.execute(
        f"""
        UPDATE equipamentos
        SET {coluna} = NULL
        WHERE user_id = %s
        """,
        (ctx.author.id,)
    )


    db.commit()


    await ctx.send(
        f"✅ {ctx.author.mention} desequipou o seu "
        f"**{tipo.capitalize()}**."
    )

# ============================================================
# !NICHIRIN
# ============================================================

@bot.command()
async def nichirin(ctx):

    embed = discord.Embed(
        title="🎨 Coloração da Nichirin",
        description=(
            "Escolhe a cor da tua Nichirin.\n"
            "A cor escolhida ficará equipada no teu perfil."
        ),
        color=discord.Color.dark_red()
    )

    for chave, dados in CORES_NICHIRIN.items():

        bonus_texto = " / ".join(
            f"+{valor}% {atributo.capitalize()}"
            for atributo, valor in dados["bonus"].items()
        )

        embed.add_field(
            name=f"{dados['emoji']} {dados['nome']}",
            value=(
                f"**Raridade:** {dados['raridade'].capitalize()}\n"
                f"**Bónus:** {bonus_texto}\n"
                f"`!nichirin {chave}`"
            ),
            inline=True
        )

    await ctx.send(embed=embed)

# ============================================================
# !NICHIRIN <COR>
# ============================================================

@bot.command()
async def escolhernichirin(ctx, cor: str = None):

    if cor is None:

        return await ctx.send(
            "❌ Indica uma cor.\n"
            "Exemplo: `!escolhernichirin preta`"
        )

    cor = cor.lower().strip()

    if cor not in CORES_NICHIRIN:

        return await ctx.send(
            "❌ Essa coloração de Nichirin não existe."
        )

    dados = CORES_NICHIRIN[cor]

    cursor.execute(
        """
        INSERT INTO equipamentos
        (user_id, nichirin)
        VALUES (%s, %s)

        ON CONFLICT (user_id)
        DO UPDATE SET nichirin = EXCLUDED.nichirin
        """,
        (
            ctx.author.id,
            cor
        )
    )

    db.commit()

    bonus_texto = "\n".join(
        f"{dados['emoji']} +{valor}% {atributo.capitalize()}"
        for atributo, valor in dados["bonus"].items()
    )

    await ctx.send(
        f"🎨 {ctx.author.mention} equipou a Nichirin "
        f"**{dados['nome']}**!\n\n"
        f"**Bónus:**\n"
        f"{bonus_texto}"
    )

# ============================================================
# !SETNICHIRIN (STAFF)
# ============================================================

@bot.command()
async def setnichirin(ctx, membro: discord.Member = None, cor: str = None):

    if not is_staff(ctx.author):

        return await ctx.send(
            "❌ Não tens permissão para usar este comando."
        )


    if membro is None or cor is None:

        return await ctx.send(
            "❌ Uso correto:\n"
            "`!setnichirin @jogador cor`\n\n"
            "Exemplo:\n"
            "`!setnichirin @jogador preta`"
        )


    cor = cor.lower().strip()


    if cor not in CORES_NICHIRIN:

        return await ctx.send(
            "❌ Essa cor de Nichirin não existe."
        )


    dados = CORES_NICHIRIN[cor]


    cursor.execute(
        """
        INSERT INTO equipamentos
        (user_id, nichirin)
        VALUES (%s, %s)

        ON CONFLICT (user_id)
        DO UPDATE SET nichirin = EXCLUDED.nichirin
        """,
        (
            membro.id,
            cor
        )
    )


    db.commit()


    bonus_texto = "\n".join(
        f"{dados['emoji']} +{valor}% {atributo.capitalize()}"
        for atributo, valor in dados["bonus"].items()
    )


    await ctx.send(
        f"🎨 **Nichirin definida!**\n\n"
        f"👤 Jogador: {membro.mention}\n"
        f"⚔️ Coloração: **{dados['nome']}**\n\n"
        f"**Bónus:**\n"
        f"{bonus_texto}"
    )

# ============================================================
# !BONUS
# ============================================================

@bot.command()
async def bonus(ctx, membro: discord.Member = None):

    if not isinstance(ctx.author, discord.Member):
        return

    alvo = membro if membro is not None else ctx.author

    tipo = obter_tipo(alvo)

    if tipo is None:
        return await ctx.send(
            f"❌ {alvo.mention} não tem um cargo válido de "
            f"**Humano, Oni ou Híbrido**."
        )

    # ========================================================
    # OBTER BÓNUS DOS EQUIPAMENTOS
    # ========================================================

    bonus_equipamentos = calcular_bonus_equipamentos(alvo.id)

    equipamentos = obter_equipamentos(alvo.id)

    tsuba = equipamentos[0]
    haori = equipamentos[1]
    nichirin = equipamentos[2]
    mascara = equipamentos[3]

    # ========================================================
    # EMBED
    # ========================================================

    embed = discord.Embed(
        title=f"📈 Bónus de {alvo.display_name}",
        description=(
            "Aqui estão os bónus de atributos recebidos "
            "pelos teus equipamentos atualmente equipados."
        ),
        color=discord.Color.dark_red()
    )

    # ========================================================
    # BÓNUS
    # ========================================================

    bonus_texto = ""

    if bonus_equipamentos["velocidade"] != 0:
        bonus_texto += (
            f"⚡ **Velocidade:** "
            f"+{bonus_equipamentos['velocidade']:.1f}%\n"
        )

    if bonus_equipamentos["forca"] != 0:
        bonus_texto += (
            f"💪 **Força:** "
            f"+{bonus_equipamentos['forca']:.1f}%\n"
        )

    if bonus_equipamentos["resistencia"] != 0:
        bonus_texto += (
            f"🛡️ **Resistência:** "
            f"+{bonus_equipamentos['resistencia']:.1f}%\n"
        )

    if bonus_equipamentos["manejo"] != 0:
        bonus_texto += (
            f"⚔️ **Manejo:** "
            f"+{bonus_equipamentos['manejo']:.1f}%\n"
        )

    if bonus_equipamentos["regeneracao"] != 0:
        bonus_texto += (
            f"🩸 **Regeneração:** "
            f"+{bonus_equipamentos['regeneracao']:.1f}%\n"
        )

    if bonus_equipamentos["folego"] != 0:
        bonus_texto += (
            f"🌬️ **Fôlego:** "
            f"+{bonus_equipamentos['folego']:.1f}%\n"
        )

    if bonus_equipamentos["sangue"] != 0:
        bonus_texto += (
            f"🩸 **Sangue:** "
            f"+{bonus_equipamentos['sangue']:.1f}%\n"
        )

    # ========================================================
    # SEM BÓNUS
    # ========================================================

    if not bonus_texto:
        bonus_texto = "❌ Não tens nenhum bónus de equipamento ativo."

    embed.add_field(
        name="📊 Bónus de Atributos",
        value=bonus_texto,
        inline=False
    )

    # ========================================================
    # EQUIPAMENTOS
    # ========================================================

    equipamentos_texto = (
        f"⚔️ **Tsuba:** {tsuba or 'Nenhuma'}\n"
        f"👘 **Haori:** {haori or 'Nenhum'}\n"
        f"🎭 **Máscara:** {mascara or 'Nenhuma'}"
    )

    embed.add_field(
        name="⚔️ Equipamentos",
        value=equipamentos_texto,
        inline=False
    )

    embed.set_footer(
        text="👻 Last Soul • Bónus provenientes dos equipamentos"
    )

    await ctx.send(embed=embed)

# ============================================================
# !RANK
# ============================================================

@bot.command()
async def rank(ctx):

    # --------------------------------------------------------
    # DETETAR RAÇA
    # --------------------------------------------------------

    raca = obter_raca(ctx.author)

    if raca is None:

        return await ctx.send(
            "❌ Não tens um cargo de personagem válido.\n\n"
            "Precisas de um dos seguintes cargos:\n"
            "👤 Humano\n"
            "👹 Oni\n"
            "🩸 Híbrido"
        )

    # --------------------------------------------------------
    # OBTER RANK ATRAVÉS DO CARGO
    # --------------------------------------------------------

    rank_atual = obter_rank(
        ctx.author.id,
        raca,
        ctx.author
    )

    if rank_atual is None:

        return await ctx.send(
            "❌ Não foi possível determinar o teu rank."
        )

    # --------------------------------------------------------
    # PONTOS
    #
    # O cargo define o mínimo de pontos do rank.
    # Se a BD tiver menos pontos que esse valor,
    # usamos o valor mínimo do próprio rank.
    # --------------------------------------------------------

    pontos_guardados = obter_pontos_rank(ctx.author.id)

    pontos_minimos_rank = rank_atual["pontos_necessarios"]

    pontos = max(
        pontos_guardados,
        pontos_minimos_rank
    )

    # --------------------------------------------------------
    # SE OS PONTOS DA BD ESTAVAM ABAIXO DO RANK,
    # ATUALIZAR AUTOMATICAMENTE
    # --------------------------------------------------------

    if pontos_guardados < pontos_minimos_rank:

        cursor.execute("""
            INSERT INTO progresso_rank (user_id, pontos_rank)
            VALUES (%s, %s)
            ON CONFLICT (user_id)
            DO UPDATE SET pontos_rank = %s
        """, (
            ctx.author.id,
            pontos_minimos_rank,
            pontos_minimos_rank
        ))

        db.commit()

    # --------------------------------------------------------
    # PROCURAR O PRÓXIMO RANK
    #
    # IMPORTANTE:
    # Procuramos pela ORDEM do rank atual,
    # e não simplesmente pelos pontos.
    # --------------------------------------------------------

    cursor.execute("""
        SELECT nome, ordem, pontos_necessarios, cargo_id
        FROM ranks
        WHERE tipo = %s
        AND ordem > %s
        ORDER BY ordem ASC
        LIMIT 1
    """, (
        raca,
        rank_atual["ordem"]
    ))

    proximo = cursor.fetchone()

    # --------------------------------------------------------
    # VERIFICAR PRÓXIMO RANK
    # --------------------------------------------------------

    if proximo is None:

        proximo_texto = (
            "🏆 **Último rank disponível**"
        )

    else:

        nome_proximo = proximo[0]
        pontos_proximo = proximo[2]

        falta = max(
            0,
            pontos_proximo - pontos
        )

        # ----------------------------------------------------
        # RANKS QUE NÃO PODEM SER ATRIBUÍDOS AUTOMATICAMENTE
        # ----------------------------------------------------

        if nome_proximo in (
            "Hashira",
            "Lua Inferior",
            "Lua Superior"
        ):

            proximo_texto = (
                f"⬆️ Próximo rank: **{nome_proximo}**\n"
                f"📊 Necessários: **{pontos_proximo} pontos**\n"
                f"🎯 Faltam: **{falta} pontos**\n\n"
                "⚠️ Este rank requer atribuição manual."
            )

        else:

            proximo_texto = (
                f"⬆️ Próximo rank: **{nome_proximo}**\n"
                f"📊 Necessários: **{pontos_proximo} pontos**\n"
                f"🎯 Faltam: **{falta} pontos**"
            )

    # --------------------------------------------------------
    # EMBED
    # --------------------------------------------------------

    embed = discord.Embed(
        title=f"⚔️ Rank de {ctx.author.display_name}",
        color=discord.Color.dark_red()
    )

    embed.set_thumbnail(
        url=ctx.author.display_avatar.url
    )

    embed.add_field(
        name="🧬 Raça",
        value=raca,
        inline=True
    )

    embed.add_field(
        name="🏅 Rank atual",
        value=rank_atual["nome"],
        inline=True
    )

    embed.add_field(
        name="⭐ Pontos de Rank",
        value=f"{pontos} pontos",
        inline=True
    )

    embed.add_field(
        name="📈 Progressão",
        value=proximo_texto,
        inline=False
    )

    embed.set_footer(
        text="👻 . 𝗟ᥲ᥉t 𝗦᥆ᥙᥣ • Sistema de Ranks"
    )

    await ctx.send(embed=embed)

# ============================================================
# !ADDRANK — ADICIONAR / RETIRAR PONTOS DE RANK
# ============================================================

@bot.command()
async def addrank(ctx, membro: discord.Member, quantidade: int):

    # --------------------------------------------------------
    # VERIFICAR STAFF
    # --------------------------------------------------------

    if not is_staff(ctx.author):
        return await ctx.send(
            "❌ Apenas membros da **Staff** podem utilizar este comando."
        )

    # --------------------------------------------------------
    # OBTER PONTOS ATUAIS
    # --------------------------------------------------------

    pontos_atuais = obter_pontos_rank(membro.id)

    # --------------------------------------------------------
    # CALCULAR NOVOS PONTOS
    # --------------------------------------------------------

    novos_pontos = pontos_atuais + quantidade

    # Impedir pontos negativos
    if novos_pontos < 0:
        novos_pontos = 0

    # --------------------------------------------------------
    # ATUALIZAR BASE DE DADOS
    # --------------------------------------------------------

    cursor.execute(
        """
        INSERT INTO progresso_rank (user_id, pontos_rank)
        VALUES (%s, %s)
        ON CONFLICT (user_id)
        DO UPDATE SET pontos_rank = EXCLUDED.pontos_rank
        """,
        (
            membro.id,
            novos_pontos
        )
    )

    db.commit()

    # --------------------------------------------------------
    # ATUALIZAR RANK AUTOMATICAMENTE
    # --------------------------------------------------------

    novo_rank = await atualizar_rank_automaticamente(membro)

    # --------------------------------------------------------
    # MENSAGEM
    # --------------------------------------------------------

    if quantidade > 0:

        mensagem = (
            f"⭐ Foram adicionados **{quantidade} pontos de rank** a "
            f"{membro.mention}."
        )

    elif quantidade < 0:

        mensagem = (
            f"⭐ Foram retirados **{abs(quantidade)} pontos de rank** de "
            f"{membro.mention}."
        )

    else:

        mensagem = (
            f"ℹ️ Nenhuma alteração foi feita nos pontos de rank de "
            f"{membro.mention}."
        )

    mensagem += (
        f"\n\n📊 **Pontos de Rank:** `{novos_pontos}`"
    )

    if novo_rank is not None:

        mensagem += (
            f"\n🏅 **Rank:** `{novo_rank[0]}`"
        )

    await ctx.send(mensagem)
    
# ============================================================
# TOKEN
# ============================================================

bot.run(os.getenv("DISCORD_TOKEN"))
