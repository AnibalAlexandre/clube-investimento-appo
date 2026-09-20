"""
Clube de Investimento APPO
Portal Oficial de Cotações BODIVA, Contabilidade e Adesão de Sócios
Aplicação web corporativa privada — Streamlit + PostgreSQL (Neon)
"""

import os
import secrets
import time
from datetime import datetime

import bcrypt
import pandas as pd
import psycopg2
import psycopg2.extras
import streamlit as st
from fpdf import FPDF
from pypdf import PdfReader

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(
    page_title="Clube de Investimento APPO",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# IDENTIDADE VISUAL (CSS + logótipo em SVG, sem depender de imagens externas)
# =========================================================
CSS_APPO = """
<style>
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #ffffff 0%, #F1F4F9 100%);
    border: 1px solid #E2E8F0;
    border-left: 4px solid #0B3D91;
    border-radius: 10px;
    padding: 14px 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.appo-hero {
    background: linear-gradient(120deg, #0B2E5E 0%, #0B3D91 55%, #1B6FBF 100%);
    color: #FFFFFF;
    border-radius: 14px;
    padding: 26px 30px;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 18px;
}
.appo-hero h1 { margin: 0; font-size: 1.7rem; line-height: 1.2; }
.appo-hero p { margin: 4px 0 0 0; opacity: 0.85; font-size: 0.92rem; }
.appo-badge {
    display: inline-block;
    background: rgba(255,255,255,0.16);
    padding: 3px 11px;
    border-radius: 999px;
    font-size: 0.72rem;
    margin-top: 10px;
    letter-spacing: 0.3px;
}
.appo-sidebar-title { display:flex; align-items:center; gap:10px; margin-bottom: 2px; }
.appo-sidebar-title span { font-weight: 700; font-size: 1.15rem; color: #0B3D91; }
</style>
"""
st.markdown(CSS_APPO, unsafe_allow_html=True)


def logo_svg(tamanho: int = 42) -> str:
    """Logótipo abstracto (onda/pomba), desenhado em SVG — não depende de nenhuma imagem externa."""
    return f"""
    <svg width="{tamanho}" height="{tamanho}" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <path d="M4 40 C18 22,34 15,60 6 C48 18,40 24,36 34 C46 32,54 34,60 40
                 C48 38,40 40,32 46 C26 50,16 52,4 40 Z" fill="#E8B84B" opacity="0.9"/>
        <path d="M4 40 C18 27,30 22,52 14 C42 22,34 28,30 36 C38 35,44 37,48 41
                 C38 39,30 41,24 46 C18 50,10 50,4 40 Z" fill="#FFFFFF"/>
    </svg>
    """


def hero(titulo: str, subtitulo: str, badge: str = "🇦🇴 BODIVA · Kwanzas (Kz)"):
    st.markdown(
        f"""
        <div class="appo-hero">
            {logo_svg(46)}
            <div>
                <h1>{titulo}</h1>
                <p>{subtitulo}</p>
                <span class="appo-badge">{badge}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# CONSTANTES E SEGREDOS
# =========================================================
DATABASE_URL = os.environ.get("DATABASE_URL")
ADMIN_EMAIL_INICIAL = os.environ.get("ADMIN_EMAIL", "admin@appo.co.ao")
ADMIN_PASSWORD_INICIAL = os.environ.get("ADMIN_PASSWORD_INICIAL", "MudarAgora123!")
TEMPO_LIMITE_SESSAO_SEGUNDOS = 60 * 60  # 60 minutos de inactividade

if not DATABASE_URL:
    st.error(
        "A variável de ambiente DATABASE_URL não está definida. "
        "Configura-a nas definições do serviço na Render (ver guia de implementação)."
    )
    st.stop()


def agora() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def kz(valor) -> str:
    """Formata um número como Kwanzas, ao estilo angolano (espaço como separador de milhar)."""
    try:
        inteiro = int(round(float(valor)))
    except (TypeError, ValueError):
        return "0 Kz"
    sinal = "-" if inteiro < 0 else ""
    inteiro = abs(inteiro)
    texto = f"{inteiro:,}".replace(",", " ")
    return f"{sinal}{texto} Kz"


def pct(valor) -> str:
    """Formata um número como percentagem, com sinal explícito."""
    try:
        return f"{float(valor):+.2f}%"
    except (TypeError, ValueError):
        return "0.00%"


def cor_variacao(v) -> str:
    try:
        v = float(v)
    except (TypeError, ValueError):
        return ""
    if v > 0:
        return "color:#16A34A; font-weight:600;"
    if v < 0:
        return "color:#DC2626; font-weight:600;"
    return "color:#6B7280;"


def tabela_cotacoes_estilizada(df_activos: pd.DataFrame):
    """Recebe um DataFrame com colunas ticker/nome/tipo/preco/variacao e devolve um
    pandas Styler pronto a passar ao st.dataframe, com o aspecto de um home broker:
    ticker em monospace, preço formatado em Kz, variação a verde/vermelho."""
    df_disp = df_activos[["ticker", "nome", "tipo", "preco", "variacao"]].copy()
    df_disp["mercado"] = "🇦🇴 BODIVA"
    df_disp = df_disp.rename(
        columns={
            "ticker": "Ticker",
            "nome": "Activo",
            "tipo": "Tipo",
            "preco": "Preço",
            "variacao": "Variação",
            "mercado": "Mercado",
        }
    )
    df_disp = df_disp[["Ticker", "Activo", "Tipo", "Mercado", "Preço", "Variação"]]
    return (
        df_disp.style.format({"Preço": kz, "Variação": pct})
        .applymap(cor_variacao, subset=["Variação"])
        .set_properties(subset=["Ticker"], **{"font-family": "monospace", "letter-spacing": "0.4px"})
        .set_properties(subset=["Preço"], **{"font-weight": "600"})
    )


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False


# =========================================================
# CONTEÚDO EDUCATIVO INICIAL (usado apenas para semear a base de dados)
# =========================================================
TEXTO_PRINCIPIOS = """
### Missão

O Clube de Investimento APPO existe para promover a literacia financeira e o acesso
disciplinado ao mercado de capitais angolano, permitindo que os seus sócios construam
património de forma colectiva, informada e sustentável através da Bolsa de Dívida e
Valores de Angola (BODIVA).

### Princípios Fundamentais

1. **Disciplina antes de intuição** — toda a alocação de capital segue um processo de
   análise documentado, nunca impulso.
2. **Horizonte de longo prazo** — a volatilidade normal do mercado é aceite como parte
   do ciclo, não como motivo de venda precipitada.
3. **Diversificação prudente** — o capital é distribuído entre dívida pública e acções
   de diferentes emitentes cotados na BODIVA.
4. **Transparência e prestação de contas** — todas as posições e resultados são
   registados e disponibilizados aos sócios.
5. **Literacia financeira como pilar** — o Clube mantém uma biblioteca educativa
   actualizada para que cada sócio compreenda os mecanismos do mercado.
6. **Decisões colectivas** — nenhum sócio actua unilateralmente em nome do Clube.
7. **Gestão de risco activa** — mantém-se sempre uma reserva de liquidez para
   aproveitar oportunidades sem vender posições em momentos desfavoráveis.
8. **Regra 50/30/20** — cada sócio é encorajado a não gastar mais de 50% do seu
   rendimento mensal total (incluindo extras) em consumo, a alocar 30% a investimento,
   e a reservar 20% para entesouramento.
"""

TEXTO_EX_DIVIDENDO = """
A **data ex-dividendo** é o dia a partir do qual quem compra uma acção já não tem
direito a receber o próximo dividendo anunciado. Só quem já era detentor da acção
antes dessa data recebe o pagamento.

**Sequência típica:** anúncio → data ex-dividendo (o preço ajusta-se em baixa,
aproximadamente no valor do dividendo) → data de registo → data de pagamento.
"""

TEXTO_RATEIO = """
O **rateio** é o mecanismo usado quando a procura por acções numa Oferta Pública de
Venda (OPV) excede a oferta disponível. Em vez de servir os pedidos por ordem de
chegada, a bolsa distribui as acções proporcionalmente entre os subscritores.

**Exemplo real (BODIVA, Julho de 2026):** na OPV da Unitel, a procura pelos 7,5
milhões de acções colocadas à venda ultrapassou os 9 milhões de títulos — cerca de
120% acima da oferta — pelo que se aplicou rateio.
"""

TEXTO_OPV_UNITEL = """
Em Julho de 2026, o Estado angolano, através do IGAPE, colocou à venda **15% do
capital social da Unitel** através de uma OPV enquadrada no PROPRIV.

**Números principais:**
- Acções colocadas à venda: 7,5 milhões (13% ao público, 2% aos trabalhadores)
- Intervalo de preço: 36.036 – 40.040 Kz por acção
- Período de subscrição: 6 a 24 de Julho de 2026
- Procura total: 9.054.299 títulos (~120% acima da oferta)
- Montante encaixado pelo Estado: ~300,3 mil milhões de Kz

**Contexto:** foi a maior OPV de sempre em Angola, e a primeira empresa de
telecomunicações admitida à negociação na BODIVA. O arranque da operação provocou
uma queda generalizada nas outras acções cotadas, por realocação de liquidez dos
investidores.
"""

TEXTO_OPV_SBA = """
A 11 de Setembro de 2026, o Estado angolano lançou a OPV de **34% do capital social
do Standard Bank Angola (SBA)**, tornando-o a terceira instituição bancária angolana
em bolsa.

**Números principais:**
- Acções colocadas à venda: 4,76 milhões (24% reservado ao Standard Bank Group, 10%
  ao público)
- Intervalo de preço para o público: 41.220 – 50.000 Kz por acção
- Período de subscrição: 11 a 25 de Setembro de 2026
- Valor bruto máximo estimado: ~208,5 mil milhões de Kz

**Contexto:** o Standard Bank Group (accionista de referência) exerceu o seu direito
de preferência para reforçar a posição, em vez de a reduzir. Ao contrário da Unitel,
a própria BODIVA (enquanto empresa cotada) manteve-se resiliente ao anúncio desta OPV.
"""

# (ticker, nome, tipo, preco, variacao)
ACTIVOS_INICIAIS = [
    ("UNTLAAAA", "Unitel", "Ação", 38000.0, 0.0),
    ("SBAAAAAA", "Standard Bank Angola", "Ação", 45000.0, 0.0),
    ("BFAAAAAA", "Banco de Fomento Angola (BFA)", "Ação", 12500.0, 0.0),
    ("BDVAAAAA", "BODIVA", "Ação", 82400.0, 0.0),
]

ARTIGOS_INICIAIS = [
    ("Princípios e Filosofia de Investimento do Clube", "Institucional", TEXTO_PRINCIPIOS),
    ("O que é a Data Ex-Dividendo?", "Educação", TEXTO_EX_DIVIDENDO),
    ("O que é o Rateio?", "Educação", TEXTO_RATEIO),
    ("Análise da OPV da Unitel (2026)", "Análise de Mercado", TEXTO_OPV_UNITEL),
    ("Análise da OPV do Standard Bank Angola (2026)", "Análise de Mercado", TEXTO_OPV_SBA),
]

# =========================================================
# BASE DE DADOS (PostgreSQL via Neon) — com reconexão automática
# =========================================================
@st.cache_resource
def obter_ligacao():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn


def _com_reconexao(func):
    """Corre func(conn); se a ligação tiver sido fechada pelo servidor (comum em bases
    de dados gratuitas como a Neon após inactividade), reconecta e tenta uma vez mais."""
    try:
        return func(obter_ligacao())
    except (psycopg2.OperationalError, psycopg2.InterfaceError):
        obter_ligacao.clear()
        return func(obter_ligacao())


def executar(sql, parametros=None):
    def _run(conn):
        with conn.cursor() as cur:
            cur.execute(sql, parametros or ())

    _com_reconexao(_run)


def consultar_um(sql, parametros=None):
    def _run(conn):
        with conn.cursor() as cur:
            cur.execute(sql, parametros or ())
            return cur.fetchone()

    return _com_reconexao(_run)


def consultar_df(sql, parametros=None) -> pd.DataFrame:
    def _run(conn):
        return pd.read_sql_query(sql, conn, params=parametros or ())

    return _com_reconexao(_run)


def inicializar_bd():
    executar(
        """
        CREATE TABLE IF NOT EXISTS contas (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN NOT NULL DEFAULT FALSE,
            criado_em TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """
    )
    executar(
        """
        CREATE TABLE IF NOT EXISTS log_acessos (
            id SERIAL PRIMARY KEY,
            email TEXT,
            sucesso BOOLEAN NOT NULL,
            criado_em TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """
    )
    executar(
        """
        CREATE TABLE IF NOT EXISTS resumo_patrimonial (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            capital_social NUMERIC NOT NULL,
            investimentos NUMERIC NOT NULL,
            reservas NUMERIC NOT NULL,
            actualizado_em TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """
    )
    executar(
        """
        CREATE TABLE IF NOT EXISTS historico_patrimonio (
            id SERIAL PRIMARY KEY,
            capital_social NUMERIC NOT NULL,
            investimentos NUMERIC NOT NULL,
            reservas NUMERIC NOT NULL,
            total NUMERIC NOT NULL,
            registado_em TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """
    )
    executar(
        """
        CREATE TABLE IF NOT EXISTS movimentos (
            id SERIAL PRIMARY KEY,
            tipo TEXT NOT NULL,
            descricao TEXT,
            montante NUMERIC NOT NULL,
            data_movimento DATE NOT NULL,
            criado_em TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """
    )
    executar(
        """
        CREATE TABLE IF NOT EXISTS activos (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL,
            preco NUMERIC NOT NULL,
            variacao NUMERIC NOT NULL DEFAULT 0,
            actualizado_em TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """
    )
    # Migração: garante a coluna 'ticker' mesmo em bases de dados criadas antes desta versão.
    executar("ALTER TABLE activos ADD COLUMN IF NOT EXISTS ticker TEXT NOT NULL DEFAULT ''")
    executar(
        """
        CREATE TABLE IF NOT EXISTS artigos (
            id SERIAL PRIMARY KEY,
            titulo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            criado_em TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """
    )
    executar(
        """
        CREATE TABLE IF NOT EXISTS socios (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            email TEXT,
            telefone TEXT,
            bi TEXT,
            contribuicao_inicial NUMERIC,
            criado_em TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """
    )

    # --- Semear dados iniciais, só se as tabelas estiverem vazias ---
    if consultar_um("SELECT COUNT(*) FROM contas")[0] == 0:
        executar(
            "INSERT INTO contas (nome, email, password_hash, is_admin) VALUES (%s, %s, %s, %s)",
            ("Administrador", ADMIN_EMAIL_INICIAL, hash_password(ADMIN_PASSWORD_INICIAL), True),
        )

    if consultar_um("SELECT COUNT(*) FROM resumo_patrimonial")[0] == 0:
        executar(
            "INSERT INTO resumo_patrimonial (id, capital_social, investimentos, reservas) "
            "VALUES (1, %s, %s, %s)",
            (15500000.0, 12300000.0, 3200000.0),
        )
        executar(
            "INSERT INTO historico_patrimonio (capital_social, investimentos, reservas, total) "
            "VALUES (%s, %s, %s, %s)",
            (15500000.0, 12300000.0, 3200000.0, 15500000.0 + 12300000.0 + 3200000.0),
        )

    if consultar_um("SELECT COUNT(*) FROM activos")[0] == 0:
        for ticker, nome, tipo, preco, var in ACTIVOS_INICIAIS:
            executar(
                "INSERT INTO activos (nome, tipo, preco, variacao, ticker) VALUES (%s, %s, %s, %s, %s)",
                (nome, tipo, preco, var, ticker),
            )
    else:
        # Preenche o ticker em activos já existentes (criados antes desta versão) que ainda não o têm.
        for ticker, nome, tipo, preco, var in ACTIVOS_INICIAIS:
            executar(
                "UPDATE activos SET ticker = %s WHERE nome = %s AND (ticker IS NULL OR ticker = '')",
                (ticker, nome),
            )

    if consultar_um("SELECT COUNT(*) FROM artigos")[0] == 0:
        for titulo, categoria, conteudo in ARTIGOS_INICIAIS:
            executar(
                "INSERT INTO artigos (titulo, categoria, conteudo) VALUES (%s, %s, %s)",
                (titulo, categoria, conteudo),
            )


# ---------------- Contas ----------------
def obter_conta_por_email(email: str):
    return consultar_um(
        "SELECT id, nome, email, password_hash, is_admin FROM contas WHERE email = %s", (email,)
    )


def inserir_conta(nome, email, password, is_admin):
    executar(
        "INSERT INTO contas (nome, email, password_hash, is_admin) VALUES (%s, %s, %s, %s)",
        (nome, email, hash_password(password), is_admin),
    )


def listar_contas() -> pd.DataFrame:
    return consultar_df(
        "SELECT id, nome, email, is_admin, criado_em FROM contas ORDER BY criado_em DESC"
    )


def contar_admins() -> int:
    return consultar_um("SELECT COUNT(*) FROM contas WHERE is_admin = TRUE")[0]


def repor_password(conta_id: int) -> str:
    nova_password = secrets.token_urlsafe(9)
    executar(
        "UPDATE contas SET password_hash = %s WHERE id = %s", (hash_password(nova_password), conta_id)
    )
    return nova_password


def eliminar_conta(conta_id: int):
    executar("DELETE FROM contas WHERE id = %s", (conta_id,))


def registar_acesso(email: str, sucesso: bool):
    executar("INSERT INTO log_acessos (email, sucesso) VALUES (%s, %s)", (email, sucesso))


def obter_log_acessos() -> pd.DataFrame:
    return consultar_df(
        "SELECT email, sucesso, criado_em FROM log_acessos ORDER BY criado_em DESC LIMIT 50"
    )


# ---------------- Resumo patrimonial e histórico ----------------
def obter_resumo_patrimonial() -> dict:
    linha = consultar_um(
        "SELECT capital_social, investimentos, reservas, actualizado_em FROM resumo_patrimonial WHERE id = 1"
    )
    return {
        "capital_social": float(linha[0]),
        "investimentos": float(linha[1]),
        "reservas": float(linha[2]),
        "actualizado_em": linha[3],
    }


def actualizar_resumo_patrimonial(capital_social, investimentos, reservas):
    executar(
        "UPDATE resumo_patrimonial SET capital_social = %s, investimentos = %s, reservas = %s, "
        "actualizado_em = NOW() WHERE id = 1",
        (capital_social, investimentos, reservas),
    )
    total = capital_social + investimentos + reservas
    executar(
        "INSERT INTO historico_patrimonio (capital_social, investimentos, reservas, total) "
        "VALUES (%s, %s, %s, %s)",
        (capital_social, investimentos, reservas, total),
    )


def obter_historico_patrimonio() -> pd.DataFrame:
    return consultar_df(
        "SELECT registado_em, total FROM historico_patrimonio ORDER BY registado_em"
    )


# ---------------- Movimentos ----------------
def inserir_movimento(tipo, descricao, montante, data_movimento):
    executar(
        "INSERT INTO movimentos (tipo, descricao, montante, data_movimento) VALUES (%s, %s, %s, %s)",
        (tipo, descricao, montante, data_movimento),
    )


def obter_movimentos() -> pd.DataFrame:
    return consultar_df(
        "SELECT tipo, descricao, montante, data_movimento, criado_em FROM movimentos "
        "ORDER BY data_movimento DESC, criado_em DESC"
    )


# ---------------- Activos ----------------
def obter_activos() -> pd.DataFrame:
    return consultar_df(
        "SELECT id, ticker, nome, tipo, preco, variacao, actualizado_em FROM activos ORDER BY nome"
    )


def substituir_activos(df: pd.DataFrame):
    executar("DELETE FROM activos")
    for _, linha in df.iterrows():
        nome = str(linha.get("nome", "")).strip()
        if not nome:
            continue
        tipo = str(linha.get("tipo", "Ação")).strip() or "Ação"
        preco = float(linha.get("preco", 0) or 0)
        variacao = float(linha.get("variacao", 0) or 0)
        ticker = str(linha.get("ticker", "") or "").strip().upper()
        executar(
            "INSERT INTO activos (nome, tipo, preco, variacao, ticker) VALUES (%s, %s, %s, %s, %s)",
            (nome, tipo, preco, variacao, ticker),
        )


# ---------------- Artigos ----------------
def obter_artigos(categoria: str = None) -> pd.DataFrame:
    if categoria and categoria != "Todas":
        return consultar_df(
            "SELECT id, titulo, categoria, conteudo, criado_em FROM artigos WHERE categoria = %s "
            "ORDER BY criado_em DESC",
            (categoria,),
        )
    return consultar_df("SELECT id, titulo, categoria, conteudo, criado_em FROM artigos ORDER BY criado_em DESC")


def inserir_artigo(titulo, categoria, conteudo):
    executar(
        "INSERT INTO artigos (titulo, categoria, conteudo) VALUES (%s, %s, %s)", (titulo, categoria, conteudo)
    )


def eliminar_artigo(artigo_id: int):
    executar("DELETE FROM artigos WHERE id = %s", (artigo_id,))


# ---------------- Sócios (pedidos de adesão) ----------------
def inserir_socio(nome, email, telefone, bi, contribuicao_inicial):
    executar(
        "INSERT INTO socios (nome, email, telefone, bi, contribuicao_inicial) VALUES (%s, %s, %s, %s, %s)",
        (nome, email, telefone, bi, contribuicao_inicial),
    )


def obter_socios() -> pd.DataFrame:
    return consultar_df(
        "SELECT nome, email, telefone, bi, contribuicao_inicial, criado_em FROM socios ORDER BY criado_em DESC"
    )


def extrair_texto_pdf(ficheiro) -> str:
    leitor = PdfReader(ficheiro)
    partes = [pagina.extract_text() or "" for pagina in leitor.pages]
    return "\n\n".join(partes).strip()


def gerar_relatorio_pdf(resumo, df_activos, df_movimentos) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Clube de Investimento APPO", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Relatorio gerado em {agora()}", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Resumo Patrimonial", ln=True)
    pdf.set_font("Helvetica", "", 11)
    total = resumo["capital_social"] + resumo["investimentos"] + resumo["reservas"]
    pdf.cell(0, 7, f"Capital Social: {kz(resumo['capital_social'])}", ln=True)
    pdf.cell(0, 7, f"Investimentos: {kz(resumo['investimentos'])}", ln=True)
    pdf.cell(0, 7, f"Reservas: {kz(resumo['reservas'])}", ln=True)
    pdf.cell(0, 7, f"Total: {kz(total)}", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Activos em Carteira", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for _, linha in df_activos.iterrows():
        pdf.cell(0, 6, f"- {linha['nome']} ({linha['tipo']}): {kz(linha['preco'])}", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Movimentos Recentes", ln=True)
    pdf.set_font("Helvetica", "", 10)
    if df_movimentos.empty:
        pdf.cell(0, 6, "Sem movimentos registados.", ln=True)
    else:
        for _, linha in df_movimentos.head(30).iterrows():
            data_txt = str(linha["data_movimento"])
            pdf.cell(
                0, 6,
                f"- {data_txt} | {linha['tipo']} | {kz(linha['montante'])} | {linha['descricao'] or ''}",
                ln=True,
            )

    saida = pdf.output()
    return bytes(saida)


inicializar_bd()

# =========================================================
# AUTENTICAÇÃO — CONTAS INDIVIDUAIS
# =========================================================
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "login_timestamp" not in st.session_state:
    st.session_state["login_timestamp"] = None
if "conta_nome" not in st.session_state:
    st.session_state["conta_nome"] = ""
if "conta_email" not in st.session_state:
    st.session_state["conta_email"] = ""
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

# Expirar sessão por inactividade
if st.session_state["autenticado"] and st.session_state["login_timestamp"]:
    if time.time() - st.session_state["login_timestamp"] > TEMPO_LIMITE_SESSAO_SEGUNDOS:
        st.session_state["autenticado"] = False
        st.session_state["login_timestamp"] = None
        st.warning("A tua sessão expirou por inactividade. Inicia sessão novamente.")


def pagina_login():
    col_esq, col_centro, col_dir = st.columns([1, 1.4, 1])
    with col_centro:
        st.markdown(
            f"""<div style="text-align:center; margin-top:24px;">{logo_svg(64)}</div>""",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<h2 style='text-align:center; margin-bottom:0;'>Clube de Investimento APPO</h2>",
            unsafe_allow_html=True,
        )
        st.caption(
            "<div style='text-align:center;'>Portal Oficial de Cotações BODIVA, Contabilidade e Adesão de Sócios</div>",
            unsafe_allow_html=True,
        )
        st.markdown("#### Acesso reservado a sócios")
        with st.form("form_login"):
            email = st.text_input("E-mail")
            password = st.text_input("Palavra-passe", type="password")
            submeter = st.form_submit_button("Entrar")
        if submeter:
            conta = obter_conta_por_email(email.strip().lower())
            if conta and verificar_password(password, conta[3]):
                registar_acesso(email, True)
                st.session_state["autenticado"] = True
                st.session_state["login_timestamp"] = time.time()
                st.session_state["conta_id"] = conta[0]
                st.session_state["conta_nome"] = conta[1]
                st.session_state["conta_email"] = conta[2]
                st.session_state["is_admin"] = bool(conta[4])
                st.rerun()
            else:
                registar_acesso(email, False)
                st.error("E-mail ou palavra-passe incorrectos. Contacta um administrador do Clube.")


if not st.session_state["autenticado"]:
    pagina_login()
    st.stop()

# =========================================================
# BARRA LATERAL / NAVEGAÇÃO
# =========================================================
st.sidebar.markdown(
    f"""
    <div class="appo-sidebar-title">
        {logo_svg(34)}
        <span>Clube APPO</span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.caption(f"Sessão: {st.session_state['conta_nome']} ({st.session_state['conta_email']})")
st.sidebar.divider()

PAGINAS = [
    "🏠 Início & Análises",
    "📈 Cotações & Activos",
    "💰 Contabilidade & Finanças",
    "📊 Histórico & Relatórios",
    "🧮 Regra 50/30/20",
    "📚 Biblioteca Educativa",
    "🧾 Adesão de Sócios",
    "ℹ️ Sobre Nós & Estatutos",
]
if st.session_state["is_admin"]:
    PAGINAS.append("🔐 Painel do Administrador")

pagina = st.sidebar.radio("Navegação", PAGINAS, label_visibility="collapsed")

st.sidebar.divider()
if st.sidebar.button("Terminar sessão"):
    for chave in ["autenticado", "login_timestamp", "conta_id", "conta_nome", "conta_email", "is_admin"]:
        st.session_state.pop(chave, None)
    st.rerun()

st.sidebar.caption(f"Última actualização da página: {agora()}")

# =========================================================
# PÁGINA: INÍCIO & ANÁLISES
# =========================================================
if pagina == "🏠 Início & Análises":
    hero("Clube de Investimento APPO", "Portal Oficial de Cotações BODIVA, Contabilidade e Adesão de Sócios")

    resumo = obter_resumo_patrimonial()
    total_patrimonio = resumo["capital_social"] + resumo["investimentos"] + resumo["reservas"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Capital Social", kz(resumo["capital_social"]))
    col2.metric("Investimentos", kz(resumo["investimentos"]))
    col3.metric("Reservas", kz(resumo["reservas"]))
    col4.metric("Património Total", kz(total_patrimonio))
    st.caption(f"Última actualização do resumo patrimonial: {resumo['actualizado_em']}")
    st.divider()

    st.subheader("Distribuição do Património")
    df_patrimonio = pd.DataFrame(
        {
            "Categoria": ["Capital Social", "Investimentos", "Reservas"],
            "Montante (Kz)": [resumo["capital_social"], resumo["investimentos"], resumo["reservas"]],
        }
    ).set_index("Categoria")
    st.bar_chart(df_patrimonio)

    st.divider()
    st.subheader("📌 Cotações em destaque")
    df_activos = obter_activos()
    if not df_activos.empty:
        st.dataframe(tabela_cotacoes_estilizada(df_activos), hide_index=True)

# =========================================================
# PÁGINA: COTAÇÕES & ACTIVOS
# =========================================================
elif pagina == "📈 Cotações & Activos":
    hero("Cotações & Activos", "Instrumentos financeiros cotados na BODIVA acompanhados pelo Clube", "🇦🇴 BODIVA DIRECTA")

    df_activos = obter_activos()
    if df_activos.empty:
        st.info("Ainda não existem activos registados.")
    else:
        tipos = ["Todos"] + sorted(df_activos["tipo"].unique().tolist())
        filtro_tipo = st.selectbox("Filtrar por tipo de activo", tipos)
        df_filtrado = df_activos if filtro_tipo == "Todos" else df_activos[df_activos["tipo"] == filtro_tipo]

        st.dataframe(tabela_cotacoes_estilizada(df_filtrado), hide_index=True)
        st.caption(f"Última actualização: {df_filtrado['actualizado_em'].max()}")

        st.divider()
        st.subheader("Comparação de preços")
        st.bar_chart(df_filtrado.set_index("nome")[["preco"]].rename(columns={"preco": "Preço (Kz)"}))

# =========================================================
# PÁGINA: CONTABILIDADE & FINANÇAS
# =========================================================
elif pagina == "💰 Contabilidade & Finanças":
    hero("Contabilidade & Finanças", "Resumo Contabilístico e Patrimonial do Clube")

    resumo = obter_resumo_patrimonial()
    df_resumo = pd.DataFrame(
        [
            {
                "Categoria": "Capital Social",
                "Descrição": "Capital subscrito e realizado pelos membros fundadores e associados",
                "Montante": kz(resumo["capital_social"]),
                "Moeda": "AOA",
            },
            {
                "Categoria": "Investimentos",
                "Descrição": "Carteira de acções e instrumentos financeiros cotados na BODIVA",
                "Montante": kz(resumo["investimentos"]),
                "Moeda": "AOA",
            },
            {
                "Categoria": "Reservas",
                "Descrição": "Fundo de estabilização e liquidez para novas oportunidades",
                "Montante": kz(resumo["reservas"]),
                "Moeda": "AOA",
            },
        ]
    )
    st.dataframe(df_resumo, hide_index=True)
    total_patrimonio = resumo["capital_social"] + resumo["investimentos"] + resumo["reservas"]
    st.metric("Património Total do Clube", kz(total_patrimonio))
    st.caption(f"Última actualização: {resumo['actualizado_em']}")

# =========================================================
# PÁGINA: HISTÓRICO & RELATÓRIOS
# =========================================================
elif pagina == "📊 Histórico & Relatórios":
    hero("Histórico & Relatórios", "Evolução do património do Clube ao longo do tempo, e exportação de relatórios")

    df_historico = obter_historico_patrimonio()
    if df_historico.empty or len(df_historico) < 2:
        st.info(
            "Ainda há poucos pontos de histórico. À medida que o resumo patrimonial for "
            "actualizado no Painel do Administrador, este gráfico vai ganhando forma."
        )
    else:
        st.caption(
            "Cada ponto deste gráfico representa uma actualização do resumo patrimonial "
            "(Capital Social + Investimentos + Reservas), feita no Painel do Administrador. "
            "O eixo vertical está em Kwanzas (Kz)."
        )
        df_grafico = df_historico.set_index("registado_em")[["total"]].rename(
            columns={"total": "Património Total (Kz)"}
        )
        st.line_chart(df_grafico)

    st.divider()
    st.subheader("Movimentos registados")
    df_movimentos = obter_movimentos()
    if df_movimentos.empty:
        st.info("Ainda não existem movimentos registados.")
    else:
        df_exibir = df_movimentos.copy()
        df_exibir["montante"] = df_exibir["montante"].apply(kz)
        st.dataframe(
            df_exibir.rename(
                columns={
                    "tipo": "Tipo",
                    "descricao": "Descrição",
                    "montante": "Montante",
                    "data_movimento": "Data",
                    "criado_em": "Registado em",
                }
            ),
            hide_index=True,
        )

    st.divider()
    st.subheader("Exportar relatório")
    if st.button("Gerar relatório em PDF"):
        resumo = obter_resumo_patrimonial()
        pdf_bytes = gerar_relatorio_pdf(resumo, obter_activos(), df_movimentos)
        st.download_button(
            "Descarregar relatório em PDF",
            data=pdf_bytes,
            file_name=f"relatorio_appo_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
        )

# =========================================================
# PÁGINA: REGRA 50/30/20 DO CLUBE
# =========================================================
elif pagina == "🧮 Regra 50/30/20":
    hero(
        "Regra 50/30/20 do Clube",
        "Princípio nº 8: 50% Consumo · 30% Investimento · 20% Entesouramento",
        "📐 Rendimento mensal total, incluindo extras",
    )

    rendimento = st.number_input(
        "Rendimento mensal total (Kz)", min_value=0.0, step=5000.0, value=250000.0, format="%.2f"
    )
    alvo_consumo = rendimento * 0.50
    alvo_investimento = rendimento * 0.30
    alvo_entesouramento = rendimento * 0.20

    st.subheader("Alocação recomendada")
    col1, col2, col3 = st.columns(3)
    col1.metric("Consumo (50%)", kz(alvo_consumo))
    col2.metric("Investimento (30%)", kz(alvo_investimento))
    col3.metric("Entesouramento (20%)", kz(alvo_entesouramento))

    df_alvo = pd.DataFrame(
        {
            "Categoria": ["Consumo", "Investimento", "Entesouramento"],
            "Valor recomendado (Kz)": [alvo_consumo, alvo_investimento, alvo_entesouramento],
        }
    ).set_index("Categoria")
    st.bar_chart(df_alvo)

    st.divider()
    st.subheader("Compara com os teus gastos reais (opcional)")
    with st.form("form_orcamento_real"):
        col_a, col_b, col_c = st.columns(3)
        real_consumo = col_a.number_input("Gasto real — Consumo (Kz)", min_value=0.0, step=1000.0)
        real_investimento = col_b.number_input("Gasto real — Investimento (Kz)", min_value=0.0, step=1000.0)
        real_entesouramento = col_c.number_input("Entesouramento real (Kz)", min_value=0.0, step=1000.0)
        comparar = st.form_submit_button("Comparar")

    if comparar:
        st.markdown("#### Resultado da comparação")
        col1, col2, col3 = st.columns(3)
        col1.metric("Consumo", kz(real_consumo), delta=kz(real_consumo - alvo_consumo), delta_color="inverse")
        col2.metric(
            "Investimento", kz(real_investimento), delta=kz(real_investimento - alvo_investimento), delta_color="normal"
        )
        col3.metric(
            "Entesouramento",
            kz(real_entesouramento),
            delta=kz(real_entesouramento - alvo_entesouramento),
            delta_color="normal",
        )
        if real_entesouramento < alvo_entesouramento:
            st.warning("O teu entesouramento real está abaixo dos 20% recomendados pelo princípio do Clube.")
        else:
            st.success("Estás a cumprir, ou a superar, a meta de 20% de entesouramento.")

# =========================================================
# PÁGINA: BIBLIOTECA EDUCATIVA
# =========================================================
elif pagina == "📚 Biblioteca Educativa":
    hero("Biblioteca Educativa", "Princípios do Clube e artigos sobre o mercado de capitais angolano")

    df_artigos = obter_artigos()
    if df_artigos.empty:
        st.info("Ainda não existem artigos publicados.")
    else:
        categorias = ["Todas"] + sorted(df_artigos["categoria"].unique().tolist())
        filtro_categoria = st.selectbox("Filtrar por categoria", categorias)
        for _, artigo in obter_artigos(filtro_categoria).iterrows():
            with st.expander(
                f"{artigo['titulo']}  —  _{artigo['categoria']}_",
                key=f"artigo_exp_{artigo['id']}",
            ):
                st.caption(f"Publicado em {artigo['criado_em']}")
                st.markdown(artigo["conteudo"])

# =========================================================
# PÁGINA: ADESÃO DE SÓCIOS
# =========================================================
elif pagina == "🧾 Adesão de Sócios":
    hero("Adesão de Sócios", "Preenche o formulário para solicitar a tua adesão ao Clube de Investimento APPO")

    with st.form("form_adesao", clear_on_submit=True):
        nome = st.text_input("Nome completo *")
        col1, col2 = st.columns(2)
        email = col1.text_input("E-mail")
        telefone = col2.text_input("Telefone / WhatsApp")
        bi = st.text_input("Número do Bilhete de Identidade")
        contribuicao = st.number_input("Contribuição inicial pretendida (Kz)", min_value=0.0, step=5000.0)
        aceite = st.checkbox("Declaro que li e aceite os Estatutos do Clube de Investimento APPO *")
        enviar = st.form_submit_button("Submeter pedido de adesão")

    if enviar:
        if not nome or not aceite:
            st.error("Preenche o nome completo e aceita os Estatutos para submeter o pedido.")
        else:
            inserir_socio(nome, email, telefone, bi, contribuicao)
            st.success(
                "Pedido de adesão submetido com sucesso! Um administrador do Clube irá entrar em "
                "contacto para confirmar a tua adesão e criar a tua conta de acesso."
            )

# =========================================================
# PÁGINA: SOBRE NÓS & ESTATUTOS
# =========================================================
elif pagina == "ℹ️ Sobre Nós & Estatutos":
    hero("Sobre Nós & Estatutos", "A missão, os princípios e o enquadramento estatutário do Clube")

    st.subheader("Quem somos")
    st.markdown(
        "O **Clube de Investimento APPO** é uma associação de investidores angolanos que "
        "junta capital de forma colectiva para investir no mercado de capitais nacional, "
        "através da Bolsa de Dívida e Valores de Angola (BODIVA)."
    )
    st.subheader("Princípios e Filosofia de Investimento")
    st.markdown(TEXTO_PRINCIPIOS)
    st.subheader("Estatutos — pontos-chave")
    st.markdown(
        """
- **Natureza:** associação de investidores, conforme Estatutos formalmente registados.
- **Órgãos sociais:** Assembleia de Sócios, Comissão de Gestão e Conselho Fiscal.
- **Admissão de sócios:** sujeita a aprovação da Comissão de Gestão.
- **Deliberações:** decisões de investimento relevantes exigem deliberação colectiva.
- **Distribuição de resultados:** proporcional à quota de capital de cada sócio.
        """
    )
    st.caption(
        "Nota interna: o texto acima é um modelo de referência, a substituir pelos "
        "Estatutos formalmente aprovados e registados do Clube assim que estiverem disponíveis."
    )

# =========================================================
# PÁGINA: PAINEL DO ADMINISTRADOR
# =========================================================
elif pagina == "🔐 Painel do Administrador":
    hero("Painel do Administrador", "Gestão de conteúdo, cotações, movimentos, sócios e contas")

    aba_resumo, aba_activos, aba_movimentos, aba_biblioteca, aba_socios, aba_contas, aba_seguranca = st.tabs(
        ["Resumo Patrimonial", "Cotações & Activos", "Movimentos", "Biblioteca", "Sócios", "Contas", "Segurança"]
    )

    with aba_resumo:
        st.subheader("Editar Resumo Patrimonial")
        st.caption("Cada alteração aqui cria automaticamente um novo ponto no histórico do Clube.")
        resumo = obter_resumo_patrimonial()
        with st.form("form_editar_resumo"):
            novo_capital = st.number_input("Capital Social (Kz)", min_value=0.0, step=10000.0, value=float(resumo["capital_social"]))
            novo_investimentos = st.number_input("Investimentos (Kz)", min_value=0.0, step=10000.0, value=float(resumo["investimentos"]))
            novas_reservas = st.number_input("Reservas (Kz)", min_value=0.0, step=10000.0, value=float(resumo["reservas"]))
            guardar_resumo = st.form_submit_button("Guardar alterações")
        if guardar_resumo:
            actualizar_resumo_patrimonial(novo_capital, novo_investimentos, novas_reservas)
            st.success("Resumo patrimonial actualizado e novo ponto de histórico registado.")
            st.rerun()

    with aba_activos:
        st.subheader("Editar Cotações & Activos")
        st.caption("Edita os valores directamente na tabela, incluindo o código do activo (ticker).")
        df_activos = obter_activos()
        df_editado = st.data_editor(
            df_activos[["ticker", "nome", "tipo", "preco", "variacao"]],
            num_rows="dynamic",
            key="editor_activos",
            column_config={
                "ticker": st.column_config.TextColumn("Ticker", max_chars=12),
                "nome": "Nome do activo",
                "tipo": "Tipo",
                "preco": st.column_config.NumberColumn("Preço (Kz)", min_value=0.0, step=100.0),
                "variacao": st.column_config.NumberColumn("Variação (%)", step=0.1),
            },
        )
        if st.button("Guardar alterações às cotações"):
            substituir_activos(df_editado)
            st.success("Cotações actualizadas com sucesso.")
            st.rerun()

    with aba_movimentos:
        st.subheader("Registar novo movimento")
        with st.form("form_novo_movimento", clear_on_submit=True):
            tipo_mov = st.selectbox(
                "Tipo",
                ["Entrada de Capital", "Compra de Activo", "Venda de Activo", "Saída/Despesa", "Ajuste de Reserva"],
            )
            descricao_mov = st.text_input("Descrição")
            montante_mov = st.number_input("Montante (Kz)", min_value=0.0, step=1000.0)
            data_mov = st.date_input("Data do movimento")
            registar_mov = st.form_submit_button("Registar movimento")
        if registar_mov:
            inserir_movimento(tipo_mov, descricao_mov, montante_mov, data_mov)
            st.success("Movimento registado com sucesso.")
            st.rerun()

        st.divider()
        st.subheader("Movimentos existentes")
        df_mov_admin = obter_movimentos()
        if not df_mov_admin.empty:
            df_mov_admin = df_mov_admin.copy()
            df_mov_admin["montante"] = df_mov_admin["montante"].apply(kz)
        st.dataframe(df_mov_admin, hide_index=True)

    with aba_biblioteca:
        st.subheader("Adicionar novo artigo")
        modo = st.radio("Fonte do conteúdo", ["Carregar PDF", "Escrever manualmente"], horizontal=True, key="modo_artigo")
        texto_extraido = ""
        if modo == "Carregar PDF":
            ficheiro_pdf = st.file_uploader("Carregar ficheiro PDF", type=["pdf"], key="uploader_pdf")
            if ficheiro_pdf is not None:
                try:
                    texto_extraido = extrair_texto_pdf(ficheiro_pdf)
                    st.success("Texto extraído do PDF com sucesso. Revê antes de publicar.")
                except Exception as erro:
                    st.error(f"Não foi possível ler o PDF: {erro}")
        with st.form("form_novo_artigo", clear_on_submit=True):
            titulo_artigo = st.text_input("Título do artigo")
            categoria_artigo = st.selectbox("Categoria", ["Institucional", "Educação", "Análise de Mercado", "Referência"])
            conteudo_artigo = st.text_area("Conteúdo (Markdown suportado)", value=texto_extraido, height=280)
            publicar = st.form_submit_button("Publicar artigo")
        if publicar:
            if not titulo_artigo or not conteudo_artigo:
                st.error("Preenche o título e o conteúdo do artigo.")
            else:
                inserir_artigo(titulo_artigo, categoria_artigo, conteudo_artigo)
                st.success("Artigo publicado.")
                st.rerun()

        st.divider()
        st.subheader("Artigos existentes")
        for _, artigo in obter_artigos().iterrows():
            col_a, col_b, col_c = st.columns([3, 1.5, 1])
            col_a.write(artigo["titulo"])
            col_b.write(artigo["categoria"])
            if col_c.button("Eliminar", key=f"eliminar_artigo_{artigo['id']}"):
                eliminar_artigo(int(artigo["id"]))
                st.rerun()

    with aba_socios:
        st.subheader("Pedidos de adesão recebidos")
        df_socios = obter_socios()
        if df_socios.empty:
            st.info("Ainda não existem pedidos de adesão.")
        else:
            df_socios_exibir = df_socios.copy()
            df_socios_exibir["contribuicao_inicial"] = df_socios_exibir["contribuicao_inicial"].apply(kz)
            st.dataframe(
                df_socios_exibir.rename(
                    columns={
                        "nome": "Nome",
                        "email": "E-mail",
                        "telefone": "Telefone",
                        "bi": "Nº BI",
                        "contribuicao_inicial": "Contribuição Inicial",
                        "criado_em": "Submetido em",
                    }
                ),
                hide_index=True,
            )

    with aba_contas:
        st.subheader("Criar conta de acesso para um sócio")
        with st.form("form_nova_conta", clear_on_submit=True):
            nome_conta = st.text_input("Nome completo")
            email_conta = st.text_input("E-mail (usado para entrar)")
            password_conta = st.text_input("Palavra-passe inicial", type="password")
            admin_conta = st.checkbox("Esta conta é administradora")
            criar_conta = st.form_submit_button("Criar conta")
        if criar_conta:
            if not nome_conta or not email_conta or not password_conta:
                st.error("Preenche todos os campos.")
            else:
                try:
                    inserir_conta(nome_conta, email_conta.strip().lower(), password_conta, admin_conta)
                    st.success(f"Conta criada para {email_conta}.")
                    st.rerun()
                except psycopg2.errors.UniqueViolation:
                    obter_ligacao().rollback()
                    st.error("Já existe uma conta com este e-mail.")

        st.divider()
        st.subheader("Contas existentes")
        df_contas = listar_contas()
        for _, conta in df_contas.iterrows():
            col_a, col_b, col_c, col_d = st.columns([2.5, 1, 1.2, 1.2])
            col_a.write(f"{conta['nome']} — {conta['email']}")
            col_b.write("Admin" if conta["is_admin"] else "Sócio")
            if col_c.button("Repor password", key=f"repor_{conta['id']}"):
                nova = repor_password(int(conta["id"]))
                st.info(f"Nova palavra-passe para {conta['email']}: **{nova}** (copia e envia ao sócio agora — não voltará a aparecer)")
            pode_eliminar = not (conta["is_admin"] and contar_admins() <= 1)
            if col_d.button("Eliminar", key=f"eliminar_conta_{conta['id']}", disabled=not pode_eliminar):
                eliminar_conta(int(conta["id"]))
                st.rerun()

    with aba_seguranca:
        st.subheader("Registo de tentativas de acesso (últimas 50)")
        df_log = obter_log_acessos()
        if df_log.empty:
            st.info("Ainda não há registos de acesso.")
        else:
            st.dataframe(
                df_log.rename(columns={"email": "E-mail", "sucesso": "Sucesso", "criado_em": "Data/Hora"}),
                hide_index=True,
            )
