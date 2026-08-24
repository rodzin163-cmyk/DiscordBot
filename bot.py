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
# BASE DE DADOS
# ============================================================

db = psycopg2.connect(
    os.environ["DATABASE_URL"]
)

cursor = db.cursor()

print("DATABASE POSTGRESQL LIGADA")

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

db.commit()


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
        "SELECT * FROM jogadores WHERE user_id = %s",
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

@bot.command()
async def help(ctx):

    embed = discord.Embed(
        title="📚 Central de Comandos",
        description=(
            "Bem-vindo à central de comandos do 👻 . 𝗟ᥲ᥉t 𝗦᥆ᥙᥣ!\n"
            "Aqui podes consultar todos os sistemas disponíveis no servidor."
        ),
        color=discord.Color.dark_red()
    )

    # ========================================================
    # 📊 ATRIBUTOS
    # ========================================================

    embed.add_field(
        name="📊 Atributos",
        value=(
            "📋 `!atributos`\n"
            "Mostra os teus atributos atuais.\n\n"

            "👤 `!atributos @jogador`\n"
            "Mostra os atributos de outro jogador.\n\n"

            "➕ `!add <quantidade> <atributo>`\n"
            "Distribui os teus pontos disponíveis por um atributo."
        ),
        inline=False
    )

    # ========================================================
    # 📈 PROGRESSÃO
    # ========================================================

    embed.add_field(
        name="📈 Progressão",
        value=(
            "⭐ `!level`\n"
            "Mostra o teu nível, XP e progresso.\n\n"

            "👤 `!perfil`\n"
            "Mostra o teu perfil completo, incluindo progressão, "
            "atributos e Mystery Boxes."
        ),
        inline=False
    )

    # ========================================================
    # ⚔️ NICHIRIN & EQUIPAMENTOS
    # ========================================================

    embed.add_field(
        name="⚔️ Nichirin & Equipamentos",
        value=(
            "🗡️ `!nichirin`\n"
            "Mostra as informações relacionadas com a tua Nichirin.\n\n"

            "⚔️ `!equipar <item>`\n"
            "Equipa um item que possuas no inventário.\n\n"

            "❌ `!desequipar <item>`\n"
            "Desequipa um item atualmente equipado.\n\n"

            "🎒 Os equipamentos podem ser consultados através do "
            "`!inventario`."
        ),
        inline=False
    )

    # ========================================================
    # 💰 ECONOMIA
    # ========================================================

    embed.add_field(
        name="💰 Economia",
        value=(
            "💸 `!saldo`\n"
            "Mostra a quantidade de moedas que possuis.\n\n"

            "🏪 `!loja`\n"
            "Mostra os produtos atualmente disponíveis na loja.\n\n"

            "🛒 `!comprar <item>`\n"
            "Compra um produto disponível na loja."
        ),
        inline=False
    )

    # ========================================================
    # 🎒 INVENTÁRIO
    # ========================================================

    embed.add_field(
        name="🎒 Inventário",
        value=(
            "🎒 `!inventario`\n"
            "Mostra todos os itens que possuis.\n\n"

            "✨ `!use <item>`\n"
            "Utiliza um item consumível do teu inventário.\n\n"

            "⚔️ `!equipar <item>`\n"
            "Equipa um equipamento que possuas.\n\n"

            "❌ `!desequipar <item>`\n"
            "Remove um equipamento atualmente equipado."
        ),
        inline=False
    )

    # ========================================================
    # 🎁 MYSTERY BOX
    # ========================================================

    embed.add_field(
        name="🎁 Mystery Boxes",
        value=(
            "🎁 `!perfil`\n"
            "Através do teu perfil podes abrir as Mystery Boxes "
            "disponíveis.\n\n"

            "As Mystery Boxes podem oferecer:\n"
            "⭐ XP\n"
            "📊 Pontos de Status\n"
            "💰 Moedas\n"
            "🎭 Itens cosméticos\n"
            "👕 Roupas e acessórios\n"
            "⚔️ Equipamentos"
        ),
        inline=False
    )

    # ========================================================
    # 🏋️ TREINAMENTOS
    # ========================================================

    embed.add_field(
        name="🏋️ Treinamentos",
        value=(
            "🥉 `!treinar iniciante`\n"
            "Inicia um treinamento de nível iniciante.\n\n"

            "🥈 `!treinar intermediario`\n"
            "Inicia um treinamento de nível intermediário.\n\n"

            "🥇 `!treinar extremo`\n"
            "Inicia um treinamento de nível extremo.\n\n"

            "✅ `!finalizar`\n"
            "Finaliza o treinamento quando o tempo necessário "
            "for cumprido.\n\n"

            "❌ `!cancelar`\n"
            "Cancela o treinamento atual."
        ),
        inline=False
    )

    # ========================================================
    # 🛡️ STAFF
    # ========================================================

    embed.add_field(
        name="🛡️ Staff",
        value=(
            "🎯 `!givepoints @jogador <quantidade>`\n"
            "Adiciona pontos disponíveis a um jogador.\n\n"

            "📊 `!addatributo @jogador <atributo> <quantidade>`\n"
            "Adiciona diretamente pontos a um atributo.\n\n"

            "🎁 `!addbox @jogador <quantidade>`\n"
            "Adiciona Mystery Boxes a um jogador.\n\n"

            "⭐ `!givexp @jogador <quantidade>`\n"
            "Adiciona XP a um jogador.\n\n"

            "📈 `!setlevel @jogador <nível>`\n"
            "Define o nível de um jogador.\n\n"

            "💰 `!addmoney @jogador <quantidade>`\n"
            "Adiciona moedas à conta de um jogador.\n\n"

            "🏪 `!addproduto`\n"
            "Abre o formulário para adicionar um produto à loja.\n\n"

            "🗑️ `!removerproduto`\n"
            "Abre o formulário para remover um produto da loja."
        ),
        inline=False
    )

    # ========================================================
    # 📖 ATRIBUTOS DISPONÍVEIS
    # ========================================================

    embed.add_field(
        name="📖 Atributos disponíveis",
        value=(
            "⚡ **Velocidade** — rapidez e mobilidade.\n"
            "💪 **Força** — força física e potência dos ataques.\n"
            "🛡️ **Resistência** — capacidade física de suportar esforço.\n"
            "⚔️ **Manejo** — domínio e utilização da espada.\n"
            "💚 **Regeneração** — capacidade de recuperação dos Onis.\n"
            "🌬️ **Fôlego** — capacidade respiratória dos humanos.\n"
            "🩸 **Sangue** — poder relacionado ao sangue dos Onis."
        ),
        inline=False
    )

    # ========================================================
    # FOOTER
    # ========================================================

    embed.set_footer(
        text="👻 . 𝗟ᥲ᥉t 𝗦᥆ᥙᥣ • Sistema de RP, Combate, Economia e Progressão"
    )

    await ctx.send(embed=embed)

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
# !NICHIRIN
# ============================================================

@bot.command()
async def nichirin(ctx, *, cor: str = None):

    if cor is None:

        return await ctx.send(
            "❌ Indica a cor da Nichirin.\n\n"
            "Exemplo:\n"
            "`!nichirin amarela`"
        )


    cor = cor.lower()


    if cor not in CORES_NICHIRIN:

        return await ctx.send(
            "❌ Essa cor de Nichirin não existe."
        )


    cores = obter_cores_nichirin(ctx.author.id)


    if cor not in cores:

        return await ctx.send(
            f"❌ Tu não tens a Nichirin **"
            f"{CORES_NICHIRIN[cor]['nome']}** desbloqueada."
        )


    equipar_item(
        ctx.author.id,
        "nichirin",
        cor
    )


    dados = CORES_NICHIRIN[cor]


    await ctx.send(
        f"🎨 **Nichirin equipada!**\n\n"
        f"{dados['emoji']} Cor: **{dados['nome']}**"
    )

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
# TOKEN
# ============================================================

bot.run(os.getenv("DISCORD_TOKEN"))
