import discord
from discord.ext import commands
import psycopg2
import asyncio
import math
import os
from datetime import datetime, timezone, timedelta


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
CARGO_ADM = 1388566858390573246
CARGO_FUNDADOR = 1386441239125295237


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

    cargos_staff = [
        1388566955069280287,  # Moderador
        1388566858390573246,  # ADM
        1386441239125295237   # Fundador
    ]


    if not any(cargo.id in cargos_staff for cargo in ctx.author.roles):

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
        description="Comandos disponíveis do 👻 . 𝗟ᥲ᥉t 𝗦᥆ᥙᥣ",
        color=discord.Color.dark_red()
    )

    embed.add_field(
        name="📊 Atributos",
        value=(
            "`!atributos`\n"
            "Mostra os teus atributos.\n\n"

            "`!atributos @jogador`\n"
            "Mostra os atributos de outro jogador.\n\n"

            "`!add <quantidade> <atributo>`\n"
            "Distribui pontos do inventário."
        ),
        inline=False
    )

    embed.add_field(
        name="🏋️ Treinos",
        value=(
            "`!treinar iniciante`\n"
            "Inicia um treino iniciante.\n\n"

            "`!treinar intermediario`\n"
            "Inicia um treino intermediário.\n\n"

            "`!treinar extremo`\n"
            "Inicia um treino extremo.\n\n"

            "`!finalizar`\n"
            "Finaliza o treino depois do tempo necessário.\n\n"

            "`!cancelar`\n"
            "Cancela o treino atual sem receber pontos."

        ),
        inline=False
    )

    embed.add_field(
        name="🛡️ Staff",
value=(
    "`!givepoints @jogador <quantidade>`\n"
    "Adiciona pontos ao inventário de um jogador.\n\n"

    "`!addatributo @jogador <atributo> <quantidade>`\n"
    "Adiciona pontos diretamente nos atributos de um jogador (Staff)."
),
inline=False
)

    embed.set_footer(
        text="👻 . 𝗟ᥲ᥉t 𝗦᥆ᥙᥣ • Sistema de Atributos e Treinos"
    )

    await ctx.send(embed=embed)


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

    valores = {
        "velocidade": velocidade,
        "forca": forca,
        "resistencia": resistencia,
        "manejo": manejo,
        "regeneracao": regeneracao,
        "folego": folego,
        "sangue": sangue
    }

    permitidos = ATRIBUTOS_PERMITIDOS[tipo]
    limite = LIMITES[tipo]

    embed = discord.Embed(
        title=f"📊 Atributos de {alvo.display_name}",
        color=discord.Color.dark_red()
    )

    for atributo, dados in ATRIBUTOS.items():

        emoji = dados["emoji"]
        nome = dados["nome"]
        valor = valores[atributo]

        if atributo in permitidos:

            texto = (
                f"{emoji} **{nome}**\n"
                f"`{valor}/{limite}`"
            )

        else:

            texto = (
                f"{emoji} **{nome}**\n"
                f"`🚫 Bloqueado`"
            )

        embed.add_field(
            name="\u200b",
            value=texto,
            inline=True
        )

    embed.add_field(
        name="📦 Pontos disponíveis",
        value=f"**{pontos}**",
        inline=False
    )

    embed.add_field(
        name="👤 Classe",
        value=f"**{tipo.capitalize()}**",
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
# !GIVEPOINTS
# ============================================================

@bot.command()
async def givepoints(ctx, membro: discord.Member, quantidade: int):

    if not isinstance(ctx.author, discord.Member):
        return


    if not eh_staff(ctx.author):

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
# TOKEN
# ============================================================

bot.run(os.getenv("DISCORD_TOKEN"))
