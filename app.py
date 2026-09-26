"""
Clube de Investimento APPO
Portal Oficial de Cotações BODIVA, Contabilidade e Adesão de Sócios
Aplicação web corporativa privada — Streamlit + PostgreSQL (Neon)
"""

import io
import os
import secrets
import textwrap
import time
import urllib.parse
from datetime import datetime, timedelta

import bcrypt
import pandas as pd
import psycopg2
import psycopg2.extras
import requests
import streamlit as st
from fpdf import FPDF
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from pypdf import PdfReader

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(page_title="Clube de Investimento APPO", page_icon="🕐", layout="wide", initial_sidebar_state="expanded")


def render_html(html: str):
    st.markdown(textwrap.dedent(html).strip(), unsafe_allow_html=True)


# =========================================================
# IMAGENS (Unsplash, licença livre)
# =========================================================
IMG_SKYLINE = "https://images.unsplash.com/photo-1602552283771-c533ac53ce80?fm=jpg&q=70&w=1600&auto=format&fit=crop"
IMG_GRAFICO = "https://images.unsplash.com/photo-1745270917449-c2e2c5806586?fm=jpg&q=70&w=1600&auto=format&fit=crop"
IMG_REUNIAO = "https://images.unsplash.com/photo-1517048676732-d65bc937f952?fm=jpg&q=70&w=1600&auto=format&fit=crop"
IMG_LIVROS = "https://images.unsplash.com/photo-1517673132405-a56a62b18caf?fm=jpg&q=70&w=1600&auto=format&fit=crop"
IMAGENS_CATEGORIA = {"Institucional": IMG_REUNIAO, "Educação": IMG_LIVROS, "Análise de Mercado": IMG_GRAFICO, "Referência": IMG_SKYLINE}

# =========================================================
# IDIOMAS
# =========================================================
TRADUCOES = {
    "Português": {
        "tagline": "Portal Oficial de Cotações BODIVA, Contabilidade e Adesão de Sócios",
        "login_titulo": "Acesso reservado a sócios", "email": "E-mail", "password": "Palavra-passe", "entrar": "Entrar",
        "erro_login": "E-mail ou palavra-passe incorrectos. Contacta um administrador do Clube.",
        "sessao": "Sessão", "terminar_sessao": "Terminar sessão",
        "nav_map": {
            "🏠 Início & Análises": "🏠 Início & Análises", "📈 Cotações & Activos": "📈 Cotações & Activos",
            "💰 Contabilidade & Finanças": "💰 Contabilidade & Finanças", "📊 Histórico & Relatórios": "📊 Histórico & Relatórios",
            "📐 Avaliação de Activos": "📐 Avaliação de Activos", "💱 Conversor de Moeda": "💱 Conversor de Moeda",
            "🧪 Simulador de Investimento": "🧪 Simulador de Investimento", "🧮 Regra 50/30/20": "🧮 Regra 50/30/20",
            "📚 Biblioteca Educativa": "📚 Biblioteca Educativa", "🧾 Adesão de Sócios": "🧾 Adesão de Sócios",
            "ℹ️ Sobre Nós & Estatutos": "ℹ️ Sobre Nós & Estatutos", "🔐 Painel do Administrador": "🔐 Painel do Administrador",
        },
    },
    "English": {
        "tagline": "Official BODIVA Quotes, Accounting and Membership Portal",
        "login_titulo": "Members-only access", "email": "E-mail", "password": "Password", "entrar": "Sign in",
        "erro_login": "Incorrect e-mail or password. Contact a Club administrator.",
        "sessao": "Session", "terminar_sessao": "Sign out",
        "nav_map": {
            "🏠 Início & Análises": "🏠 Home & Analysis", "📈 Cotações & Activos": "📈 Quotes & Assets",
            "💰 Contabilidade & Finanças": "💰 Accounting & Finance", "📊 Histórico & Relatórios": "📊 History & Reports",
            "📐 Avaliação de Activos": "📐 Asset Valuation", "💱 Conversor de Moeda": "💱 Currency Converter",
            "🧪 Simulador de Investimento": "🧪 Investment Simulator", "🧮 Regra 50/30/20": "🧮 50/30/20 Rule",
            "📚 Biblioteca Educativa": "📚 Learning Library", "🧾 Adesão de Sócios": "🧾 Membership Application",
            "ℹ️ Sobre Nós & Estatutos": "ℹ️ About Us & Bylaws", "🔐 Painel do Administrador": "🔐 Admin Panel",
        },
    },
    "Français": {
        "tagline": "Portail Officiel des Cotations BODIVA, Comptabilité et Adhésion",
        "login_titulo": "Accès réservé aux membres", "email": "E-mail", "password": "Mot de passe", "entrar": "Se connecter",
        "erro_login": "E-mail ou mot de passe incorrect. Contactez un administrateur.",
        "sessao": "Session", "terminar_sessao": "Se déconnecter",
        "nav_map": {
            "🏠 Início & Análises": "🏠 Accueil & Analyses", "📈 Cotações & Activos": "📈 Cotations & Actifs",
            "💰 Contabilidade & Finanças": "💰 Comptabilité & Finances", "📊 Histórico & Relatórios": "📊 Historique & Rapports",
            "📐 Avaliação de Activos": "📐 Évaluation des Actifs", "💱 Conversor de Moeda": "💱 Convertisseur de Devises",
            "🧪 Simulador de Investimento": "🧪 Simulateur d'Investissement", "🧮 Regra 50/30/20": "🧮 Règle 50/30/20",
            "📚 Biblioteca Educativa": "📚 Bibliothèque Éducative", "🧾 Adesão de Sócios": "🧾 Adhésion des Membres",
            "ℹ️ Sobre Nós & Estatutos": "ℹ️ À propos & Statuts", "🔐 Painel do Administrador": "🔐 Panneau d'Administration",
        },
    },
    "Español": {
        "tagline": "Portal Oficial de Cotizaciones BODIVA, Contabilidad y Adhesión",
        "login_titulo": "Acceso reservado a socios", "email": "Correo electrónico", "password": "Contraseña", "entrar": "Entrar",
        "erro_login": "Correo o contraseña incorrectos. Contacta a un administrador del Club.",
        "sessao": "Sesión", "terminar_sessao": "Cerrar sesión",
        "nav_map": {
            "🏠 Início & Análises": "🏠 Inicio y Análisis", "📈 Cotações & Activos": "📈 Cotizaciones y Activos",
            "💰 Contabilidade & Finanças": "💰 Contabilidad y Finanzas", "📊 Histórico & Relatórios": "📊 Historial e Informes",
            "📐 Avaliação de Activos": "📐 Valoración de Activos", "💱 Conversor de Moeda": "💱 Conversor de Moneda",
            "🧪 Simulador de Investimento": "🧪 Simulador de Inversión", "🧮 Regra 50/30/20": "🧮 Regla 50/30/20",
            "📚 Biblioteca Educativa": "📚 Biblioteca Educativa", "🧾 Adesão de Sócios": "🧾 Adhesión de Socios",
            "ℹ️ Sobre Nós & Estatutos": "ℹ️ Sobre Nosotros y Estatutos", "🔐 Painel do Administrador": "🔐 Panel de Administrador",
        },
    },
    "中文 (Mandarim)": {
        "tagline": "BODIVA官方行情、会计与会员门户",
        "login_titulo": "仅限会员访问", "email": "电子邮件", "password": "密码", "entrar": "登录",
        "erro_login": "邮箱或密码错误。请联系俱乐部管理员。",
        "sessao": "会话", "terminar_sessao": "退出登录",
        "nav_map": {
            "🏠 Início & Análises": "🏠 首页与分析", "📈 Cotações & Activos": "📈 行情与资产",
            "💰 Contabilidade & Finanças": "💰 会计与财务", "📊 Histórico & Relatórios": "📊 历史与报告",
            "📐 Avaliação de Activos": "📐 资产估值", "💱 Conversor de Moeda": "💱 货币换算器",
            "🧪 Simulador de Investimento": "🧪 投资模拟器", "🧮 Regra 50/30/20": "🧮 50/30/20法则",
            "📚 Biblioteca Educativa": "📚 教育图书馆", "🧾 Adesão de Sócios": "🧾 会员申请",
            "ℹ️ Sobre Nós & Estatutos": "ℹ️ 关于我们与章程", "🔐 Painel do Administrador": "🔐 管理员面板",
        },
    },
}
LISTA_IDIOMAS = list(TRADUCOES.keys())
if "idioma" not in st.session_state:
    st.session_state["idioma"] = "Português"


def t() -> dict:
    return TRADUCOES[st.session_state["idioma"]]


# =========================================================
# IDENTIDADE VISUAL
# =========================================================
COR_MARCA = "#7C1F3E"

CSS_APPO = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Luckiest+Guy&family=Baloo+2:wght@600;700&display=swap');
[data-testid="stAppViewContainer"] {{ background: #FBF8F6; }}
[data-testid="stHeader"] {{ background: transparent; }}
div[data-testid="stMetric"] {{ background: linear-gradient(135deg, #ffffff 0%, #F6EFF2 100%); border: 1px solid #ECDEE3; border-left: 4px solid {COR_MARCA}; border-radius: 10px; padding: 14px 16px; box-shadow: 0 1px 4px rgba(124,31,62,0.08); }}
.appo-hero {{ position: relative; overflow: hidden; background: linear-gradient(120deg, #4A1226 0%, {COR_MARCA} 55%, #A6486A 100%); color: #FFFFFF; border-radius: 14px; padding: 24px 30px; margin-bottom: 18px; display: flex; align-items: center; gap: 16px; }}
.appo-hero::before {{ content: ""; position: absolute; inset: 0; background-image: repeating-linear-gradient(135deg, rgba(255,255,255,0.06) 0px, rgba(255,255,255,0.06) 2px, transparent 2px, transparent 16px); pointer-events: none; }}
.appo-hero > * {{ position: relative; z-index: 1; }}
.appo-hero h1 {{ margin: 0; font-size: 1.6rem; line-height: 1.2; }}
.appo-hero p {{ margin: 4px 0 0 0; opacity: 0.9; font-size: 0.9rem; }}
.appo-badge {{ display: inline-block; background: rgba(255,255,255,0.18); padding: 3px 11px; border-radius: 999px; font-size: 0.72rem; margin-top: 10px; letter-spacing: 0.3px; }}
.appo-sidebar-header {{ display:flex; align-items:center; gap:12px; margin-bottom: 4px; }}
.appo-sidebar-sub {{ font-size: 0.66rem; color:#9a8a90; letter-spacing:1.5px; text-transform:uppercase; margin:0; }}
.appo-sidebar-word {{ font-family: 'Luckiest Guy', cursive; font-weight: 400; font-size: 1.7rem; color: {COR_MARCA}; line-height: 1; margin-top: 2px; }}
.appo-premium-lock {{ background: #FBF4F0; border: 1px dashed {COR_MARCA}; border-radius: 10px; padding: 18px 20px; text-align: center; }}
.appo-wordmark {{ font-family: 'Luckiest Guy', cursive; font-weight: 400; letter-spacing: 1px; font-size: 3.4rem; color: {COR_MARCA}; text-align: center; margin-top: 4px; line-height: 1; text-shadow: 1px 2px 0 rgba(124,31,62,0.18); }}
.appo-indicador-nota {{ background: #F6EFF2; border-radius: 8px; padding: 10px 14px; font-size: 0.85rem; color: #4A3038; margin: 6px 0 4px 0; }}
.appo-categoria-banner {{ border-radius: 10px 10px 0 0; padding: 12px 18px; display: flex; align-items: center; gap: 12px; margin: -1rem -1rem 12px -1rem; }}
.appo-categoria-banner span {{ color: #fff; font-weight: 700; letter-spacing: 0.6px; font-size: 0.78rem; text-transform: uppercase; }}
.appo-capa {{ position: relative; border-radius: 14px; overflow: hidden; margin-bottom: 18px; background-size: cover; background-position: center; display: flex; align-items: flex-end; }}
.appo-capa-overlay {{ position: absolute; inset: 0; }}
.appo-capa span {{ position: relative; z-index: 1; color: #fff; font-weight: 700; padding: 16px 22px; font-size: 1.05rem; text-shadow: 0 1px 4px rgba(0,0,0,0.5); }}
.appo-categoria-foto {{ position: relative; border-radius: 10px 10px 0 0; margin: -1rem -1rem 12px -1rem; height: 140px; background-size: cover; background-position: center; display: flex; align-items: flex-end; }}
.appo-categoria-foto-overlay {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,0.05) 0%, rgba(0,0,0,0.55) 100%); border-radius: 10px 10px 0 0; }}
.appo-categoria-foto span {{ position: relative; z-index: 1; color: #fff; font-weight: 700; padding: 12px 18px; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.6px; }}
.appo-ticker-wrap {{ overflow: hidden; white-space: nowrap; background: none; border-top: 1px solid #ECDEE3; border-bottom: 1px solid #ECDEE3; padding: 8px 0; margin: 0 0 16px 0; }}
.appo-ticker-move {{ display: inline-block; padding-left: 100%; animation: appo-scroll 130s linear infinite; font-family: monospace; font-size: 0.82rem; }}
@keyframes appo-scroll {{ 0% {{ transform: translate(0,0); }} 100% {{ transform: translate(-100%,0); }} }}
.appo-share a {{ text-decoration:none; color:#fff; padding:6px 14px; border-radius:8px; font-size:0.82rem; font-weight:600; }}
</style>
"""
st.markdown(CSS_APPO, unsafe_allow_html=True)


def logo_svg(tamanho: int = 46, cor: str = COR_MARCA) -> str:
    return (
        f'<svg width="{tamanho}" height="{tamanho}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">'
        f'<defs><filter id="sombraAPPO" x="-30%" y="-30%" width="160%" height="160%">'
        f'<feDropShadow dx="0" dy="1.5" stdDeviation="1.6" flood-color="#000000" flood-opacity="0.28"/></filter></defs>'
        f'<g filter="url(#sombraAPPO)">'
        f'<circle cx="50" cy="40" r="31" fill="none" stroke="{cor}" stroke-width="7.5"/>'
        f'<line x1="50" y1="40" x2="50" y2="19" stroke="{cor}" stroke-width="6.5" stroke-linecap="round"/>'
        f'<line x1="50" y1="40" x2="65" y2="51" stroke="{cor}" stroke-width="6.5" stroke-linecap="round"/>'
        f'<circle cx="50" cy="40" r="5" fill="{cor}"/>'
        f'<line x1="14" y1="40" x2="21" y2="40" stroke="{cor}" stroke-width="5" stroke-linecap="round"/>'
        f'<line x1="79" y1="40" x2="86" y2="40" stroke="{cor}" stroke-width="5" stroke-linecap="round"/>'
        f'<line x1="50" y1="1" x2="50" y2="8" stroke="{cor}" stroke-width="5" stroke-linecap="round"/>'
        f'<path d="M 22 68 A 33 33 0 0 0 70 70" fill="none" stroke="{cor}" stroke-width="7.5" stroke-linecap="round"/>'
        f'<polygon points="70,70 60,65 66,78" fill="{cor}"/></g></svg>'
    )


def logo_com_texto(tamanho: int = 130, cor: str = COR_MARCA):
    render_html(f'<div style="text-align:center; margin-top:10px;">{logo_svg(tamanho, cor)}<div class="appo-wordmark">APPO</div></div>')


def hero(titulo: str, subtitulo: str, badge: str = "🇦🇴 BODIVA · Kwanzas (Kz)"):
    render_html(f'<div class="appo-hero">{logo_svg(58, "#FFFFFF")}<div><h1>{titulo}</h1><p>{subtitulo}</p><span class="appo-badge">{badge}</span></div></div>')


def banner_capa(imagem_url: str, texto: str, altura: int = 170, escurecimento: float = 0.5):
    render_html(
        f"""
        <div class="appo-capa" style="height:{altura}px; background-image:url('{imagem_url}');">
            <div class="appo-capa-overlay" style="background:linear-gradient(180deg, rgba(20,5,12,0.05) 0%, rgba(20,5,12,{escurecimento}) 100%);"></div>
            <span>{texto}</span>
        </div>
        """
    )


CORES_CATEGORIA = {"Institucional": COR_MARCA, "Educação": "#1F6F5C", "Análise de Mercado": "#0B3D91", "Referência": "#8A6A26"}
ICONES_CATEGORIA = {"Institucional": "🏛️", "Educação": "📖", "Análise de Mercado": "📊", "Referência": "📎"}


def banner_categoria(categoria: str):
    icone = ICONES_CATEGORIA.get(categoria, "📄")
    imagem = IMAGENS_CATEGORIA.get(categoria)
    if imagem:
        render_html(f'<div class="appo-categoria-foto" style="background-image:url(\'{imagem}\');"><div class="appo-categoria-foto-overlay"></div><span>{icone} {categoria}</span></div>')
    else:
        cor = CORES_CATEGORIA.get(categoria, COR_MARCA)
        render_html(f'<div class="appo-categoria-banner" style="background:linear-gradient(120deg, {cor}cc, {cor});"><span style="font-size:1.3rem;">{icone}</span><span>{categoria}</span></div>')


def nota_indicador(texto: str):
    render_html(f'<div class="appo-indicador-nota">💡 {texto}</div>')


def ticker_tape(df_activos: pd.DataFrame):
    if df_activos.empty:
        return
    itens = []
    for _, a in df_activos.iterrows():
        v = float(a["variacao"])
        cor = "#16A34A" if v > 0 else ("#DC2626" if v < 0 else "#6B7280")
        itens.append(f'<span style="color:{cor}; margin-right:36px;">{a["ticker"] or a["nome"]} &nbsp;{kz(a["preco"])} &nbsp;({v:+.2f}%)</span>')
    conteudo = "".join(itens) * 3
    render_html(f'<div class="appo-ticker-wrap"><div class="appo-ticker-move"><span>{conteudo}</span></div></div>')


def botoes_partilha(texto: str):
    cod = urllib.parse.quote(texto)
    wa = f"https://wa.me/?text={cod}"
    tw = f"https://twitter.com/intent/tweet?text={cod}"
    fb = f"https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fclube-investimento-appo.onrender.com&quote={cod}"
    render_html(
        f"""
        <div class="appo-share" style="display:flex; gap:10px; margin-top:10px; flex-wrap:wrap;">
            <a href="{wa}" target="_blank" style="background:#25D366;">💬 WhatsApp</a>
            <a href="{tw}" target="_blank" style="background:#111;">𝕏 X / Twitter</a>
            <a href="{fb}" target="_blank" style="background:#1877F2;">📘 Facebook</a>
        </div>
        """
    )


# =========================================================
# CONSTANTES E SEGREDOS
# =========================================================
DATABASE_URL = os.environ.get("DATABASE_URL")
ADMIN_EMAIL_INICIAL = os.environ.get("ADMIN_EMAIL", "admin@appo.co.ao")
ADMIN_PASSWORD_INICIAL = os.environ.get("ADMIN_PASSWORD_INICIAL", "MudarAgora123!")
TEMPO_LIMITE_SESSAO_SEGUNDOS = 60 * 60

if not DATABASE_URL:
    st.error("A variável de ambiente DATABASE_URL não está definida. Configura-a nas definições do serviço na Render.")
    st.stop()


def agora() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def kz(valor) -> str:
    try:
        inteiro = int(round(float(valor)))
    except (TypeError, ValueError):
        return "0 Kz"
    sinal = "-" if inteiro < 0 else ""
    inteiro = abs(inteiro)
    return f"{sinal}{f'{inteiro:,}'.replace(',', ' ')} Kz"


def pct(valor) -> str:
    try:
        return f"{float(valor)*100:+.2f}%"
    except (TypeError, ValueError):
        return "0.00%"


def pct_bruto(valor) -> str:
    try:
        return f"{float(valor):+.2f}%"
    except (TypeError, ValueError):
        return "0.00%"


def multiplo(v) -> str:
    if v is None:
        return "n/d"
    try:
        return f"{float(v):.2f}x"
    except (TypeError, ValueError):
        return "n/d"


def fmt_dt(valor) -> str:
    """Formata datas/horas de forma legível (sem microssegundos) para captions e exportações."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return "n/d"
    if isinstance(valor, str):
        return valor
    try:
        return pd.Timestamp(valor).strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(valor)


def gerar_excel_bytes(df: pd.DataFrame, nome_folha: str = "Dados", colunas_moeda: list = None, colunas_percentagem: list = None, colunas_data: list = None, colunas_multiplo: list = None) -> bytes:
    """Gera um ficheiro .xlsx devidamente formatado (cabeçalho, larguras, moeda/percentagem), evitando o
    problema clássico de CSVs que abrem 'atabalhoados' no Excel em Portugal (onde a vírgula é o separador decimal)."""
    colunas_moeda = colunas_moeda or []
    colunas_percentagem = colunas_percentagem or []
    colunas_data = colunas_data or []
    colunas_multiplo = colunas_multiplo or []
    df_export = df.copy()
    for coluna in colunas_data:
        if coluna in df_export.columns:
            df_export[coluna] = df_export[coluna].apply(fmt_dt)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_export.to_excel(writer, sheet_name=nome_folha, index=False)
        planilha = writer.sheets[nome_folha]
        fonte_cabecalho = Font(bold=True, color="FFFFFF")
        fundo_cabecalho = PatternFill("solid", fgColor="7C1F3E")
        for indice_coluna, nome_coluna in enumerate(df_export.columns, start=1):
            celula_cabecalho = planilha.cell(row=1, column=indice_coluna)
            celula_cabecalho.font = fonte_cabecalho
            celula_cabecalho.fill = fundo_cabecalho
            celula_cabecalho.alignment = Alignment(horizontal="center")
            if len(df_export) > 0:
                largura_conteudo = int(df_export[nome_coluna].astype(str).map(len).max())
            else:
                largura_conteudo = 8
            largura = max(12, min(42, largura_conteudo + 4, len(str(nome_coluna)) + 6))
            planilha.column_dimensions[get_column_letter(indice_coluna)].width = largura
            if nome_coluna in colunas_moeda:
                for linha in range(2, len(df_export) + 2):
                    planilha.cell(row=linha, column=indice_coluna).number_format = '#,##0 "Kz"'
            if nome_coluna in colunas_percentagem:
                for linha in range(2, len(df_export) + 2):
                    planilha.cell(row=linha, column=indice_coluna).number_format = "+0.00%;-0.00%"
            if nome_coluna in colunas_multiplo:
                for linha in range(2, len(df_export) + 2):
                    planilha.cell(row=linha, column=indice_coluna).number_format = '0.00"x"'
        planilha.freeze_panes = "A2"
    return buffer.getvalue()


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
    df_disp = df_activos[["ticker", "nome", "tipo", "preco", "variacao"]].copy()
    df_disp["mercado"] = "🇦🇴 BODIVA"
    df_disp = df_disp.rename(columns={"ticker": "Ticker", "nome": "Activo", "tipo": "Tipo", "preco": "Preço", "variacao": "Variação", "mercado": "Mercado"})
    df_disp = df_disp[["Ticker", "Activo", "Tipo", "Mercado", "Preço", "Variação"]]
    return (
        df_disp.style.format({"Preço": kz, "Variação": pct_bruto}).applymap(cor_variacao, subset=["Variação"])
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


@st.cache_data(ttl=3600, show_spinner=False)
def obter_taxas_cambio(base: str) -> dict:
    resposta = requests.get(f"https://open.er-api.com/v6/latest/{base}", timeout=8)
    dados = resposta.json()
    if dados.get("result") != "success":
        raise ValueError("Falha ao obter taxas de câmbio.")
    return {"rates": dados["rates"], "actualizado": dados.get("time_last_update_utc", "")}


# =========================================================
# CONTEÚDO EDUCATIVO
# =========================================================
TEXTO_PRINCIPIOS = """
### Missão
O Clube de Investimento APPO existe para promover a literacia financeira e o acesso
disciplinado ao mercado de capitais angolano, permitindo que os seus sócios construam
património de forma colectiva, informada e sustentável através da Bolsa de Dívida e
Valores de Angola (BODIVA).

### Princípios Fundamentais
1. **Disciplina antes de intuição**
2. **Horizonte de longo prazo**
3. **Diversificação prudente**
4. **Transparência e prestação de contas**
5. **Literacia financeira como pilar**
6. **Decisões colectivas**
7. **Gestão de risco activa**
8. **Regra 50/30/20** — 50% consumo, 30% investimento, 20% entesouramento.
9. **Nenhuma posição sem tese registada**
"""

TEXTO_EX_DIVIDENDO = "A **data ex-dividendo** é o dia a partir do qual quem compra uma acção já não tem direito ao próximo dividendo anunciado."
TEXTO_RATEIO = "O **rateio** distribui proporcionalmente as acções de uma OPV quando a procura excede a oferta."
TEXTO_OPV_UNITEL = "Em Julho de 2026, o Estado colocou à venda 15% do capital da Unitel via OPV — a maior de sempre em Angola."
TEXTO_OPV_SBA = "Em Setembro de 2026, o Estado lançou a OPV de 34% do Standard Bank Angola."
TEXTO_INVESTIDOR_VS_TRADER = "Segundo Benjamin Graham, um investidor sente-se dono do negócio, exige margem de segurança, e pensa diferente da maioria."
TEXTO_DIVIDENDOS_GUIA = "Três datas decidem se recebes um dividendo: Assembleia Geral, data de registo (a que importa), e data de pagamento."
TEXTO_DANGOTE = "A Dangote Refinery abriu capital na NGX em 2026 — mercado fora do âmbito da BODIVA, referência educativa."
TEXTO_REGRAS_BODIVA = "Regra BODIVA 2/18: dispersão mínima 5%, lote mínimo 1 acção, variação máxima 25% estática, liquidação D+1."

ACTIVOS_INICIAIS = [
    ("UNTLAAAA", "Unitel", "Ação", 38000.0, 0.0), ("SBAAAAAA", "Standard Bank Angola", "Ação", 45000.0, 0.0),
    ("BFAAAAAA", "Banco de Fomento Angola (BFA)", "Ação", 12500.0, 0.0), ("BDVAAAAA", "BODIVA", "Ação", 82400.0, 0.0),
]

ARTIGOS_INICIAIS = [
    ("Princípios e Filosofia de Investimento do Clube", "Institucional", TEXTO_PRINCIPIOS),
    ("O que é a Data Ex-Dividendo?", "Educação", TEXTO_EX_DIVIDENDO),
    ("O que é o Rateio?", "Educação", TEXTO_RATEIO),
    ("Análise da OPV da Unitel (2026)", "Análise de Mercado", TEXTO_OPV_UNITEL),
    ("Análise da OPV do Standard Bank Angola (2026)", "Análise de Mercado", TEXTO_OPV_SBA),
    ("Investidor vs. Trader — os três princípios de Benjamin Graham", "Educação", TEXTO_INVESTIDOR_VS_TRADER),
    ("Dividendos na BODIVA: as três datas que decidem se recebes", "Educação", TEXTO_DIVIDENDOS_GUIA),
    ("A OPV da Dangote Petroleum Refinery — análise comparativa", "Análise de Mercado", TEXTO_DANGOTE),
    ("Regras de Negociação da BODIVA (Regra Nº 2/18)", "Referência", TEXTO_REGRAS_BODIVA),
]

AVALIACOES_INICIAIS = [
    ("BFA", "Banca", 100500.0, 15000000, 233140000000, 0, 365250000000, 139885149600, 0.08),
    ("BAI", "Banca", 93900.0, 19450000, 295918000000, 0, 838000000000, 147841239768, 0.08),
    ("BCGA", "Banca", 19800.0, 20000000, 44143653000, 0, 256000000000, 21630389955, 0.06),
    ("ENSA", "Seguros", 26500.0, 2400000, 6360917000, 0, 0, 3880154744, 0.05),
    ("BDV (BODIVA)", "Infra-estrutura de Mercado", 81000.0, 600000, 2609155000, 0, 9120000000, 1565495329, 0.10),
    ("UNITEL", "Telecomunicações", 34000.0, 50000000, 158368000000, 220800000000, 925000000000, 40000000000, 0.04),
    ("SBA (Standard Bank)", "Banca", 41220.0, 14000000, 150000000000, 0, 340900000000, 0, 0.08),
]

# =========================================================
# BASE DE DADOS — com reconexão automática
# =========================================================
@st.cache_resource
def obter_ligacao():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn


def _com_reconexao(func):
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
    executar("""CREATE TABLE IF NOT EXISTS contas (id SERIAL PRIMARY KEY, nome TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, is_admin BOOLEAN NOT NULL DEFAULT FALSE, criado_em TIMESTAMP NOT NULL DEFAULT NOW())""")
    executar("ALTER TABLE contas ADD COLUMN IF NOT EXISTS is_premium BOOLEAN NOT NULL DEFAULT FALSE")
    executar("""CREATE TABLE IF NOT EXISTS log_acessos (id SERIAL PRIMARY KEY, email TEXT, sucesso BOOLEAN NOT NULL, criado_em TIMESTAMP NOT NULL DEFAULT NOW())""")
    executar("""CREATE TABLE IF NOT EXISTS resumo_patrimonial (id INTEGER PRIMARY KEY CHECK (id = 1), capital_social NUMERIC NOT NULL, investimentos NUMERIC NOT NULL, reservas NUMERIC NOT NULL, actualizado_em TIMESTAMP NOT NULL DEFAULT NOW())""")
    executar("ALTER TABLE resumo_patrimonial ADD COLUMN IF NOT EXISTS capital_subscrito NUMERIC")
    executar("ALTER TABLE resumo_patrimonial ADD COLUMN IF NOT EXISTS capital_realizado NUMERIC")
    executar("""CREATE TABLE IF NOT EXISTS historico_patrimonio (id SERIAL PRIMARY KEY, capital_social NUMERIC NOT NULL, investimentos NUMERIC NOT NULL, reservas NUMERIC NOT NULL, total NUMERIC NOT NULL, registado_em TIMESTAMP NOT NULL DEFAULT NOW())""")
    executar("""CREATE TABLE IF NOT EXISTS movimentos (id SERIAL PRIMARY KEY, tipo TEXT NOT NULL, descricao TEXT, montante NUMERIC NOT NULL, data_movimento DATE NOT NULL, criado_em TIMESTAMP NOT NULL DEFAULT NOW())""")
    executar("""CREATE TABLE IF NOT EXISTS activos (id SERIAL PRIMARY KEY, nome TEXT NOT NULL, tipo TEXT NOT NULL, preco NUMERIC NOT NULL, variacao NUMERIC NOT NULL DEFAULT 0, actualizado_em TIMESTAMP NOT NULL DEFAULT NOW())""")
    executar("ALTER TABLE activos ADD COLUMN IF NOT EXISTS ticker TEXT NOT NULL DEFAULT ''")
    executar("""CREATE TABLE IF NOT EXISTS artigos (id SERIAL PRIMARY KEY, titulo TEXT NOT NULL, categoria TEXT NOT NULL, conteudo TEXT NOT NULL, criado_em TIMESTAMP NOT NULL DEFAULT NOW())""")
    executar("""CREATE TABLE IF NOT EXISTS socios (id SERIAL PRIMARY KEY, nome TEXT NOT NULL, email TEXT, telefone TEXT, bi TEXT, contribuicao_inicial NUMERIC, criado_em TIMESTAMP NOT NULL DEFAULT NOW())""")
    executar("""CREATE TABLE IF NOT EXISTS premissas_macro (id INTEGER PRIMARY KEY CHECK (id = 1), inflacao NUMERIC NOT NULL DEFAULT 0.135, taxa_livre_risco NUMERIC NOT NULL DEFAULT 0.18, premio_risco NUMERIC NOT NULL DEFAULT 0.055, beta_banca NUMERIC NOT NULL DEFAULT 1.0, beta_telecom NUMERIC NOT NULL DEFAULT 0.9, beta_outros NUMERIC NOT NULL DEFAULT 1.0, actualizado_em TIMESTAMP NOT NULL DEFAULT NOW())""")
    executar("""CREATE TABLE IF NOT EXISTS avaliacoes (id SERIAL PRIMARY KEY, empresa TEXT UNIQUE NOT NULL, sector TEXT NOT NULL, preco NUMERIC NOT NULL DEFAULT 0, acoes_circulacao NUMERIC NOT NULL DEFAULT 0, lucro_liquido NUMERIC NOT NULL DEFAULT 0, ganho_pontual NUMERIC NOT NULL DEFAULT 0, capital_proprio NUMERIC NOT NULL DEFAULT 0, dividendo_total NUMERIC NOT NULL DEFAULT 0, crescimento_g NUMERIC NOT NULL DEFAULT 0.08, actualizado_em TIMESTAMP NOT NULL DEFAULT NOW())""")
    executar("""CREATE TABLE IF NOT EXISTS favoritos (conta_id INTEGER NOT NULL, activo_id INTEGER NOT NULL, PRIMARY KEY (conta_id, activo_id))""")
    executar("""CREATE TABLE IF NOT EXISTS historico_cambio_aoa (registado_em DATE PRIMARY KEY, usd NUMERIC, eur NUMERIC, gbp NUMERIC, zar NUMERIC, cny NUMERIC, brl NUMERIC)""")
    executar("""CREATE TABLE IF NOT EXISTS historico_indice_mercado (registado_em DATE PRIMARY KEY, indice_variacao NUMERIC NOT NULL)""")

    if consultar_um("SELECT COUNT(*) FROM contas")[0] == 0:
        executar("INSERT INTO contas (nome, email, password_hash, is_admin) VALUES (%s, %s, %s, %s)", ("Administrador", ADMIN_EMAIL_INICIAL, hash_password(ADMIN_PASSWORD_INICIAL), True))

    if consultar_um("SELECT COUNT(*) FROM resumo_patrimonial")[0] == 0:
        executar("INSERT INTO resumo_patrimonial (id, capital_social, capital_subscrito, capital_realizado, investimentos, reservas) VALUES (1, %s, %s, %s, %s, %s)", (10000000.0, 10000000.0, 5000000.0, 1866677.0, 2832885.0))
        executar("INSERT INTO historico_patrimonio (capital_social, investimentos, reservas, total) VALUES (%s, %s, %s, %s)", (5000000.0, 1866677.0, 2832885.0, 5000000.0 + 1866677.0 + 2832885.0))
    else:
        linha = consultar_um("SELECT capital_subscrito, capital_realizado, capital_social FROM resumo_patrimonial WHERE id = 1")
        if linha and linha[0] is None:
            valor_antigo = float(linha[2])
            executar("UPDATE resumo_patrimonial SET capital_subscrito = %s, capital_realizado = %s WHERE id = 1", (valor_antigo, valor_antigo * 0.5))

    if consultar_um("SELECT COUNT(*) FROM activos")[0] == 0:
        for ticker, nome, tipo, preco, var in ACTIVOS_INICIAIS:
            executar("INSERT INTO activos (nome, tipo, preco, variacao, ticker) VALUES (%s, %s, %s, %s, %s)", (nome, tipo, preco, var, ticker))
    else:
        for ticker, nome, tipo, preco, var in ACTIVOS_INICIAIS:
            executar("UPDATE activos SET ticker = %s WHERE nome = %s AND (ticker IS NULL OR ticker = '')", (ticker, nome))

    for titulo, categoria, conteudo in ARTIGOS_INICIAIS:
        if not consultar_um("SELECT 1 FROM artigos WHERE titulo = %s", (titulo,)):
            executar("INSERT INTO artigos (titulo, categoria, conteudo) VALUES (%s, %s, %s)", (titulo, categoria, conteudo))

    if consultar_um("SELECT COUNT(*) FROM premissas_macro")[0] == 0:
        executar("INSERT INTO premissas_macro (id, inflacao, taxa_livre_risco, premio_risco, beta_banca, beta_telecom, beta_outros) VALUES (1, 0.135, 0.18, 0.055, 1.0, 0.9, 1.0)")

    for empresa, sector, preco, acoes, lucro, ganho, cap_proprio, div_total, g in AVALIACOES_INICIAIS:
        if not consultar_um("SELECT 1 FROM avaliacoes WHERE empresa = %s", (empresa,)):
            executar("INSERT INTO avaliacoes (empresa, sector, preco, acoes_circulacao, lucro_liquido, ganho_pontual, capital_proprio, dividendo_total, crescimento_g) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (empresa, sector, preco, acoes, lucro, ganho, cap_proprio, div_total, g))


# ---------------- Contas ----------------
def obter_conta_por_email(email: str):
    return consultar_um("SELECT id, nome, email, password_hash, is_admin, is_premium FROM contas WHERE email = %s", (email,))


def inserir_conta(nome, email, password, is_admin):
    executar("INSERT INTO contas (nome, email, password_hash, is_admin) VALUES (%s, %s, %s, %s)", (nome, email, hash_password(password), is_admin))


def listar_contas() -> pd.DataFrame:
    return consultar_df("SELECT id, nome, email, is_admin, is_premium, criado_em FROM contas ORDER BY criado_em DESC")


def contar_admins() -> int:
    return consultar_um("SELECT COUNT(*) FROM contas WHERE is_admin = TRUE")[0]


def alternar_premium(conta_id: int, valor: bool):
    executar("UPDATE contas SET is_premium = %s WHERE id = %s", (valor, conta_id))


def repor_password(conta_id: int) -> str:
    nova_password = secrets.token_urlsafe(9)
    executar("UPDATE contas SET password_hash = %s WHERE id = %s", (hash_password(nova_password), conta_id))
    return nova_password


def eliminar_conta(conta_id: int):
    executar("DELETE FROM contas WHERE id = %s", (conta_id,))


def registar_acesso(email: str, sucesso: bool):
    executar("INSERT INTO log_acessos (email, sucesso) VALUES (%s, %s)", (email, sucesso))


def obter_log_acessos() -> pd.DataFrame:
    return consultar_df("SELECT email, sucesso, criado_em FROM log_acessos ORDER BY criado_em DESC LIMIT 50")


# ---------------- Resumo patrimonial ----------------
def obter_resumo_patrimonial() -> dict:
    """O Capital Realizado NÃO é um valor independente: é sempre igual à soma de Investimentos + Reservas,
    porque é exactamente isso que ele é — o dinheiro que os sócios já entregaram, e que neste momento está
    aplicado (Investimentos) ou guardado como liquidez (Reservas). O Capital Subscrito é apenas a promessa
    total; o que falta entregar é Capital Subscrito − Capital Realizado (nos termos da Lei das Sociedades
    Comerciais, que dá até um exercício económico para realizar o capital subscrito)."""
    linha = consultar_um("SELECT capital_subscrito, investimentos, reservas, actualizado_em FROM resumo_patrimonial WHERE id = 1")
    capital_subscrito = float(linha[0] or 0)
    investimentos = float(linha[1])
    reservas = float(linha[2])
    capital_realizado = investimentos + reservas
    return {
        "capital_subscrito": capital_subscrito,
        "capital_realizado": capital_realizado,
        "capital_por_realizar": max(capital_subscrito - capital_realizado, 0.0),
        "investimentos": investimentos,
        "reservas": reservas,
        "actualizado_em": linha[3],
    }


def actualizar_resumo_patrimonial(capital_subscrito, investimentos, reservas):
    capital_realizado = investimentos + reservas
    executar("UPDATE resumo_patrimonial SET capital_social = %s, capital_subscrito = %s, capital_realizado = %s, investimentos = %s, reservas = %s, actualizado_em = NOW() WHERE id = 1", (capital_realizado, capital_subscrito, capital_realizado, investimentos, reservas))
    executar("INSERT INTO historico_patrimonio (capital_social, investimentos, reservas, total) VALUES (%s, %s, %s, %s)", (capital_realizado, investimentos, reservas, capital_realizado))


def obter_historico_patrimonio() -> pd.DataFrame:
    return consultar_df("SELECT registado_em, total FROM historico_patrimonio ORDER BY registado_em")


# ---------------- Movimentos ----------------
def inserir_movimento(tipo, descricao, montante, data_movimento):
    executar("INSERT INTO movimentos (tipo, descricao, montante, data_movimento) VALUES (%s, %s, %s, %s)", (tipo, descricao, montante, data_movimento))


def obter_movimentos() -> pd.DataFrame:
    return consultar_df("SELECT tipo, descricao, montante, data_movimento, criado_em FROM movimentos ORDER BY data_movimento DESC, criado_em DESC")


# ---------------- Activos + Favoritos + Índice ----------------
def obter_activos() -> pd.DataFrame:
    return consultar_df("SELECT id, ticker, nome, tipo, preco, variacao, actualizado_em FROM activos ORDER BY nome")


def calcular_indice_mercado(df_activos: pd.DataFrame) -> float:
    acoes = df_activos[df_activos["tipo"] == "Ação"]
    return float(acoes["variacao"].mean()) if not acoes.empty else 0.0


def registar_historico_indice(valor: float):
    hoje = datetime.now().date()
    executar(
        "INSERT INTO historico_indice_mercado (registado_em, indice_variacao) VALUES (%s, %s) "
        "ON CONFLICT (registado_em) DO UPDATE SET indice_variacao = EXCLUDED.indice_variacao",
        (hoje, valor),
    )


def obter_historico_indice() -> pd.DataFrame:
    return consultar_df("SELECT indice_variacao, registado_em FROM historico_indice_mercado ORDER BY registado_em")


def substituir_activos(df: pd.DataFrame):
    """A Variação (%) já não é escrita manualmente: é sempre calculada comparando o novo preço com o preço
    que estava registado antes desta gravação para o mesmo activo (por nome). Assim, o Barómetro BODIVA
    passa a reflectir sempre a variação real face à cotação anterior."""
    precos_anteriores = {linha["nome"]: float(linha["preco"]) for _, linha in obter_activos().iterrows()}
    executar("DELETE FROM activos")
    for _, linha in df.iterrows():
        nome = str(linha.get("nome", "")).strip()
        if not nome:
            continue
        tipo = str(linha.get("tipo", "Ação")).strip() or "Ação"
        preco_novo = float(linha.get("preco", 0) or 0)
        ticker = str(linha.get("ticker", "") or "").strip().upper()
        preco_antigo = precos_anteriores.get(nome)
        variacao = ((preco_novo - preco_antigo) / preco_antigo) * 100 if preco_antigo else 0.0
        executar("INSERT INTO activos (nome, tipo, preco, variacao, ticker) VALUES (%s, %s, %s, %s, %s)", (nome, tipo, preco_novo, variacao, ticker))
    registar_historico_indice(calcular_indice_mercado(obter_activos()))


def obter_favoritos(conta_id: int) -> set:
    df = consultar_df("SELECT activo_id FROM favoritos WHERE conta_id = %s", (conta_id,))
    return set(df["activo_id"].tolist())


def definir_favoritos(conta_id: int, ids_seleccionados: list):
    executar("DELETE FROM favoritos WHERE conta_id = %s", (conta_id,))
    for aid in ids_seleccionados:
        executar("INSERT INTO favoritos (conta_id, activo_id) VALUES (%s, %s)", (conta_id, aid))


# ---------------- Câmbio (automático + histórico automático) ----------------
def registar_historico_cambio(rates: dict):
    hoje = datetime.now().date()
    executar(
        "INSERT INTO historico_cambio_aoa (registado_em, usd, eur, gbp, zar, cny, brl) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (registado_em) DO NOTHING",
        (hoje, rates.get("USD"), rates.get("EUR"), rates.get("GBP"), rates.get("ZAR"), rates.get("CNY"), rates.get("BRL")),
    )


def obter_historico_cambio() -> pd.DataFrame:
    return consultar_df("SELECT registado_em, usd, eur, gbp, zar, cny, brl FROM historico_cambio_aoa ORDER BY registado_em")


# ---------------- Artigos ----------------
def obter_artigos(categoria: str = None) -> pd.DataFrame:
    if categoria and categoria != "Todas":
        return consultar_df("SELECT id, titulo, categoria, conteudo, criado_em FROM artigos WHERE categoria = %s ORDER BY criado_em DESC", (categoria,))
    return consultar_df("SELECT id, titulo, categoria, conteudo, criado_em FROM artigos ORDER BY criado_em DESC")


def inserir_artigo(titulo, categoria, conteudo):
    executar("INSERT INTO artigos (titulo, categoria, conteudo) VALUES (%s, %s, %s)", (titulo, categoria, conteudo))


def eliminar_artigo(artigo_id: int):
    executar("DELETE FROM artigos WHERE id = %s", (artigo_id,))


# ---------------- Sócios ----------------
def inserir_socio(nome, email, telefone, bi, contribuicao_inicial):
    executar("INSERT INTO socios (nome, email, telefone, bi, contribuicao_inicial) VALUES (%s, %s, %s, %s, %s)", (nome, email, telefone, bi, contribuicao_inicial))


def obter_socios() -> pd.DataFrame:
    return consultar_df("SELECT nome, email, telefone, bi, contribuicao_inicial, criado_em FROM socios ORDER BY criado_em DESC")


def extrair_texto_pdf(ficheiro) -> str:
    leitor = PdfReader(ficheiro)
    return "\n\n".join(pagina.extract_text() or "" for pagina in leitor.pages).strip()


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
    pdf.cell(0, 7, f"Capital Subscrito: {kz(resumo['capital_subscrito'])}", ln=True)
    pdf.cell(0, 7, f"Capital Realizado (ja entregue): {kz(resumo['capital_realizado'])}", ln=True)
    pdf.cell(0, 7, f"Capital por Realizar: {kz(resumo['capital_por_realizar'])}", ln=True)
    pdf.cell(0, 7, f"  - dos quais, Investimentos: {kz(resumo['investimentos'])}", ln=True)
    pdf.cell(0, 7, f"  - dos quais, Reservas: {kz(resumo['reservas'])}", ln=True)
    pdf.cell(0, 7, f"Patrimonio Total do Clube (= Capital Realizado): {kz(resumo['capital_realizado'])}", ln=True)
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
            pdf.cell(0, 6, f"- {linha['data_movimento']} | {linha['tipo']} | {kz(linha['montante'])} | {linha['descricao'] or ''}", ln=True)
    return bytes(pdf.output())


# ---------------- Avaliação (fundamentais + DDM) ----------------
def obter_premissas_macro() -> dict:
    linha = consultar_um("SELECT inflacao, taxa_livre_risco, premio_risco, beta_banca, beta_telecom, beta_outros FROM premissas_macro WHERE id = 1")
    return {"inflacao": float(linha[0]), "taxa_livre_risco": float(linha[1]), "premio_risco": float(linha[2]), "beta_banca": float(linha[3]), "beta_telecom": float(linha[4]), "beta_outros": float(linha[5])}


def actualizar_premissas_macro(inflacao, rf, erp, beta_banca, beta_telecom, beta_outros):
    executar("UPDATE premissas_macro SET inflacao=%s, taxa_livre_risco=%s, premio_risco=%s, beta_banca=%s, beta_telecom=%s, beta_outros=%s, actualizado_em=NOW() WHERE id = 1", (inflacao, rf, erp, beta_banca, beta_telecom, beta_outros))


def obter_avaliacoes() -> pd.DataFrame:
    return consultar_df("SELECT id, empresa, sector, preco, acoes_circulacao, lucro_liquido, ganho_pontual, capital_proprio, dividendo_total, crescimento_g, actualizado_em FROM avaliacoes ORDER BY empresa")


def substituir_avaliacoes(df: pd.DataFrame):
    executar("DELETE FROM avaliacoes")
    for _, linha in df.iterrows():
        empresa = str(linha.get("empresa", "")).strip()
        if not empresa:
            continue
        executar(
            "INSERT INTO avaliacoes (empresa, sector, preco, acoes_circulacao, lucro_liquido, ganho_pontual, capital_proprio, dividendo_total, crescimento_g) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (empresa, str(linha.get("sector", "") or ""), float(linha.get("preco", 0) or 0), float(linha.get("acoes_circulacao", 0) or 0), float(linha.get("lucro_liquido", 0) or 0), float(linha.get("ganho_pontual", 0) or 0), float(linha.get("capital_proprio", 0) or 0), float(linha.get("dividendo_total", 0) or 0), float(linha.get("crescimento_g", 0) or 0)),
        )


def ke_por_sector(sector: str, premissas: dict) -> float:
    if sector == "Banca":
        beta = premissas["beta_banca"]
    elif sector == "Telecomunicações":
        beta = premissas["beta_telecom"]
    else:
        beta = premissas["beta_outros"]
    return premissas["taxa_livre_risco"] + beta * premissas["premio_risco"]


def calcular_metricas_avaliacao(av: dict, premissas: dict) -> dict:
    preco = av["preco"]
    acoes = av["acoes_circulacao"] or 0
    lucro_normalizado = av["lucro_liquido"] - av["ganho_pontual"]
    eps = (av["lucro_liquido"] / acoes) if acoes else 0
    pe = (preco / eps) if eps and eps > 0 else None
    bvps = (av["capital_proprio"] / acoes) if acoes and av["capital_proprio"] else 0
    pbv = (preco / bvps) if bvps and bvps > 0 else None
    dps = (av["dividendo_total"] / acoes) if acoes else 0
    payout = (av["dividendo_total"] / av["lucro_liquido"]) if av["lucro_liquido"] else None
    dy_nominal = (dps / preco) if preco else 0
    dy_real = dy_nominal - premissas["inflacao"]
    roe = (lucro_normalizado / av["capital_proprio"]) if av["capital_proprio"] else None
    ke = ke_por_sector(av["sector"], premissas)
    g = av["crescimento_g"]
    d1 = dps * (1 + g)
    valor_justo = (d1 / (ke - g)) if ke > g else None
    upside = ((valor_justo - preco) / preco) if (valor_justo is not None and preco) else None
    return {"cap_mercado": preco * acoes, "eps": eps, "pe": pe, "pbv": pbv, "dps": dps, "payout": payout, "dy_nominal": dy_nominal, "dy_real": dy_real, "roe": roe, "ke": ke, "valor_justo": valor_justo, "upside": upside}


inicializar_bd()

# =========================================================
# AUTENTICAÇÃO
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
if "is_premium" not in st.session_state:
    st.session_state["is_premium"] = False

if st.session_state["autenticado"] and st.session_state["login_timestamp"]:
    if time.time() - st.session_state["login_timestamp"] > TEMPO_LIMITE_SESSAO_SEGUNDOS:
        st.session_state["autenticado"] = False
        st.session_state["login_timestamp"] = None
        st.warning("A tua sessão expirou por inactividade. Inicia sessão novamente.")


def pagina_login():
    col_esq, col_centro, col_dir = st.columns([1, 1.4, 1])
    with col_centro:
        st.selectbox("🌐", LISTA_IDIOMAS, key="idioma", label_visibility="collapsed")
        textos = t()
        banner_capa(IMG_SKYLINE, "Crescimento Sustentável, Foco no Longo Prazo", altura=150, escurecimento=0.42)
        logo_com_texto(110)
        render_html(f'<p style="text-align:center; opacity:0.75; margin-top:6px;">{textos["tagline"]}</p>')
        st.markdown(f"#### {textos['login_titulo']}")
        with st.form("form_login"):
            email = st.text_input(textos["email"])
            password = st.text_input(textos["password"], type="password")
            submeter = st.form_submit_button(textos["entrar"])
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
                st.session_state["is_premium"] = bool(conta[5])
                st.rerun()
            else:
                registar_acesso(email, False)
                st.error(textos["erro_login"])


if not st.session_state["autenticado"]:
    pagina_login()
    st.stop()

# =========================================================
# BARRA LATERAL
# =========================================================
textos = t()
render_html(f'<div class="appo-sidebar-header">{logo_svg(50)}<div><p class="appo-sidebar-sub">Clube de Investimento</p><div class="appo-sidebar-word">APPO</div></div></div>')
st.sidebar.selectbox("🌐 Idioma / Language", LISTA_IDIOMAS, key="idioma")
selo_premium = " · ⭐ Premium" if st.session_state["is_premium"] else ""
st.sidebar.caption(f"{textos['sessao']}: {st.session_state['conta_nome']} ({st.session_state['conta_email']}){selo_premium}")
st.sidebar.divider()

PAGINAS = [
    "🏠 Início & Análises", "📈 Cotações & Activos", "💰 Contabilidade & Finanças", "📊 Histórico & Relatórios",
    "📐 Avaliação de Activos", "💱 Conversor de Moeda", "🧪 Simulador de Investimento", "🧮 Regra 50/30/20",
    "📚 Biblioteca Educativa", "🧾 Adesão de Sócios", "ℹ️ Sobre Nós & Estatutos",
]
if st.session_state["is_admin"]:
    PAGINAS.append("🔐 Painel do Administrador")

pagina = st.sidebar.radio("Navegação", PAGINAS, label_visibility="collapsed", format_func=lambda k: textos["nav_map"].get(k, k))

st.sidebar.divider()
if st.sidebar.button(textos["terminar_sessao"]):
    for chave in ["autenticado", "login_timestamp", "conta_id", "conta_nome", "conta_email", "is_admin", "is_premium"]:
        st.session_state.pop(chave, None)
    st.rerun()

st.sidebar.caption(f"Última actualização da página: {agora()}")

# Fita de cotações, visível em todas as páginas
_df_activos_ticker = obter_activos()
ticker_tape(_df_activos_ticker)

# =========================================================
# PÁGINA: INÍCIO & ANÁLISES
# =========================================================
if pagina == "🏠 Início & Análises":
    hero("Clube de Investimento APPO", "Portal Oficial de Cotações BODIVA, Contabilidade e Adesão de Sócios")

    resumo = obter_resumo_patrimonial()
    total_patrimonio = resumo["capital_realizado"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Capital Subscrito", kz(resumo["capital_subscrito"]))
    col2.metric("Capital Realizado (já entregue)", kz(resumo["capital_realizado"]), delta=(f"{resumo['capital_realizado']/resumo['capital_subscrito']*100:.0f}% do subscrito" if resumo["capital_subscrito"] else None), delta_color="off")
    col3.metric("Capital por Realizar", kz(resumo["capital_por_realizar"]))
    col4, col5, col6 = st.columns(3)
    col4.metric("Investimentos", kz(resumo["investimentos"]))
    col5.metric("Reservas", kz(resumo["reservas"]))
    col6.metric("Património Total do Clube", kz(total_patrimonio))
    st.caption("Património Total = Investimentos + Reservas, que é exactamente o Capital Realizado (o dinheiro já entregue pelos sócios). O Capital por Realizar ainda não entrou no Clube, por isso não conta para o património actual.")

    indice = calcular_indice_mercado(_df_activos_ticker)
    st.metric("📊 Barómetro BODIVA (cotação média do dia)", pct_bruto(indice), delta=pct_bruto(indice))
    st.caption("Mostra se o conjunto das acções acompanhadas pelo Clube subiu ou desceu, em média, no dia — um indicador do mercado BODIVA, não necessariamente o desempenho da carteira do Clube.")
    st.divider()

    st.subheader("Distribuição do Capital do Clube")
    st.bar_chart(pd.DataFrame({"Categoria": ["Investimentos", "Reservas", "Por Realizar"], "Montante (Kz)": [resumo["investimentos"], resumo["reservas"], resumo["capital_por_realizar"]]}).set_index("Categoria"))
    st.caption("Investimentos e Reservas somam o Capital Realizado (o património actual). \"Por Realizar\" é a parte do Capital Subscrito que os sócios ainda vão entregar.")

    st.divider()
    banner_capa(IMG_GRAFICO, "Disciplina, transparência e visão de longo prazo", altura=130, escurecimento=0.48)

    st.subheader("📌 Cotações em destaque")
    if not _df_activos_ticker.empty:
        st.dataframe(tabela_cotacoes_estilizada(_df_activos_ticker), hide_index=True)

# =========================================================
# PÁGINA: COTAÇÕES & ACTIVOS
# =========================================================
elif pagina == "📈 Cotações & Activos":
    hero("Cotações & Activos", "Instrumentos financeiros cotados na BODIVA acompanhados pelo Clube", "🇦🇴 BODIVA DIRECTA")

    df_activos = _df_activos_ticker
    if df_activos.empty:
        st.info("Ainda não existem activos registados.")
    else:
        st.subheader("📊 Barómetro BODIVA — Cotação Média das Acções Negociadas")
        indice = calcular_indice_mercado(df_activos)
        col_i1, col_i2 = st.columns([1, 2])
        col_i1.metric("Variação média de hoje", pct_bruto(indice), delta=pct_bruto(indice))
        col_i1.caption("Indica se o mercado acompanhado pelo Clube (as acções cotadas na BODIVA) subiu ou desceu, em média, hoje — não reflecte necessariamente a carteira do Clube.")
        df_hist_indice = obter_historico_indice()
        with col_i2:
            if len(df_hist_indice) >= 2:
                df_hist_indice["registado_em"] = pd.to_datetime(df_hist_indice["registado_em"])
                st.line_chart(df_hist_indice.set_index("registado_em")[["indice_variacao"]].rename(columns={"indice_variacao": "Barómetro BODIVA — diário (%)"}))
            else:
                st.info("O histórico diário do Barómetro BODIVA vai-se formando a cada dia em que o administrador actualizar as cotações.")
        st.markdown("##### Tendência Semanal do Barómetro BODIVA")
        if len(df_hist_indice) >= 2:
            df_semanal = df_hist_indice.set_index("registado_em").resample("W")[["indice_variacao"]].mean().rename(columns={"indice_variacao": "Barómetro BODIVA — média semanal (%)"})
            if len(df_semanal) >= 2:
                st.line_chart(df_semanal)
            else:
                st.caption("Ainda não há pelo menos duas semanas de histórico para mostrar a tendência semanal.")
        else:
            st.caption("Ainda não há histórico suficiente para a vista semanal.")
        st.divider()

        aba_fav, aba_todos = st.tabs(["⭐ Favoritos", "📋 Todos os Activos"])
        conta_id = st.session_state["conta_id"]
        favoritos_actuais = obter_favoritos(conta_id)

        with aba_fav:
            opcoes = dict(zip(df_activos["nome"], df_activos["id"]))
            seleccionados_nomes = [nome for nome, aid in opcoes.items() if aid in favoritos_actuais]
            novos_nomes = st.multiselect("Escolher os teus activos favoritos", options=list(opcoes.keys()), default=seleccionados_nomes)
            if set(novos_nomes) != set(seleccionados_nomes):
                definir_favoritos(conta_id, [opcoes[n] for n in novos_nomes])
                st.rerun()
            if novos_nomes:
                st.dataframe(tabela_cotacoes_estilizada(df_activos[df_activos["nome"].isin(novos_nomes)]), hide_index=True)
            else:
                st.info("Ainda não marcaste nenhum activo como favorito. Usa a caixa acima.")

        with aba_todos:
            tipos = ["Todos"] + sorted(df_activos["tipo"].unique().tolist())
            filtro_tipo = st.selectbox("Filtrar por tipo de activo", tipos)
            df_filtrado = df_activos if filtro_tipo == "Todos" else df_activos[df_activos["tipo"] == filtro_tipo]
            st.dataframe(tabela_cotacoes_estilizada(df_filtrado), hide_index=True)
            st.caption(f"Última actualização: {fmt_dt(df_filtrado['actualizado_em'].max())}")
            df_export_cotacoes = df_filtrado[["ticker", "nome", "tipo", "preco", "variacao"]].rename(columns={"ticker": "Ticker", "nome": "Activo", "tipo": "Tipo", "preco": "Preço (Kz)", "variacao": "Variação (%)"})
            df_export_cotacoes["Variação (%)"] = df_export_cotacoes["Variação (%)"] / 100
            st.download_button(
                "⬇️ Descarregar tabela em Excel",
                data=gerar_excel_bytes(df_export_cotacoes, "Cotações", colunas_moeda=["Preço (Kz)"], colunas_percentagem=["Variação (%)"]),
                file_name="cotacoes_appo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
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
            {"Categoria": "Capital Subscrito", "Descrição": "Total de capital que os sócios se comprometeram a entregar", "Montante": kz(resumo["capital_subscrito"]), "Moeda": "AOA"},
            {"Categoria": "Capital Realizado", "Descrição": "Parte do capital subscrito já efectivamente entregue (= Investimentos + Reservas)", "Montante": kz(resumo["capital_realizado"]), "Moeda": "AOA"},
            {"Categoria": "Capital por Realizar", "Descrição": "Diferença entre o Subscrito e o Realizado, ainda a entregar pelos sócios", "Montante": kz(resumo["capital_por_realizar"]), "Moeda": "AOA"},
            {"Categoria": "  ↳ Investimentos", "Descrição": "Parte do capital realizado aplicada em acções e instrumentos cotados na BODIVA", "Montante": kz(resumo["investimentos"]), "Moeda": "AOA"},
            {"Categoria": "  ↳ Reservas", "Descrição": "Parte do capital realizado mantida em liquidez, como fundo de estabilização", "Montante": kz(resumo["reservas"]), "Moeda": "AOA"},
        ]
    )
    st.dataframe(df_resumo, hide_index=True)
    total_patrimonio = resumo["capital_realizado"]
    st.metric("Património Total do Clube (Investimentos + Reservas = Capital Realizado)", kz(total_patrimonio))
    st.caption("O Capital Subscrito ainda não entregue não conta como património do Clube — é apenas uma promessa dos sócios, prevista na Lei das Sociedades Comerciais para ser realizada dentro do exercício económico.")
    st.caption(f"Última actualização: {fmt_dt(resumo['actualizado_em'])}")

# =========================================================
# PÁGINA: HISTÓRICO & RELATÓRIOS
# =========================================================
elif pagina == "📊 Histórico & Relatórios":
    hero("Histórico & Relatórios", "Evolução do património do Clube ao longo do tempo, e exportação de relatórios")
    df_historico = obter_historico_patrimonio()
    if df_historico.empty or len(df_historico) < 2:
        st.info("Ainda há poucos pontos de histórico. Este gráfico vai ganhando forma com o tempo.")
    else:
        st.caption("Cada ponto representa uma actualização do resumo patrimonial. Eixo vertical em Kwanzas (Kz).")
        st.line_chart(df_historico.set_index("registado_em")[["total"]].rename(columns={"total": "Património Total (Kz)"}))

    st.divider()
    st.subheader("Movimentos registados")
    df_movimentos = obter_movimentos()
    if df_movimentos.empty:
        st.info("Ainda não existem movimentos registados.")
    else:
        df_exibir = df_movimentos.copy()
        df_exibir["montante_fmt"] = df_exibir["montante"].apply(kz)
        df_exibir["registado_fmt"] = df_exibir["criado_em"].apply(fmt_dt)
        st.dataframe(df_exibir[["tipo", "descricao", "montante_fmt", "data_movimento", "registado_fmt"]].rename(columns={"tipo": "Tipo", "descricao": "Descrição", "montante_fmt": "Montante", "data_movimento": "Data", "registado_fmt": "Registado em"}), hide_index=True)
        df_export_mov = df_movimentos.rename(columns={"tipo": "Tipo", "descricao": "Descrição", "montante": "Montante (Kz)", "data_movimento": "Data", "criado_em": "Registado em"})
        st.download_button(
            "⬇️ Descarregar movimentos em Excel",
            data=gerar_excel_bytes(df_export_mov, "Movimentos", colunas_moeda=["Montante (Kz)"], colunas_data=["Registado em"]),
            file_name="movimentos_appo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    st.divider()
    st.subheader("Exportar relatório")
    if st.button("Gerar relatório em PDF"):
        resumo = obter_resumo_patrimonial()
        pdf_bytes = gerar_relatorio_pdf(resumo, obter_activos(), df_movimentos)
        st.download_button("Descarregar relatório em PDF", data=pdf_bytes, file_name=f"relatorio_appo_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf")

# =========================================================
# PÁGINA: AVALIAÇÃO DE ACTIVOS
# =========================================================
elif pagina == "📐 Avaliação de Activos":
    hero("Avaliação de Activos", "Múltiplos e valor justo (DDM) das empresas cotadas, com dados reais do Clube")
    premissas = obter_premissas_macro()
    df_aval = obter_avaliacoes()

    if df_aval.empty:
        st.info("Ainda não existem avaliações registadas.")
    else:
        empresa_sel = st.selectbox("Empresa", df_aval["empresa"].tolist())
        av_linha = df_aval[df_aval["empresa"] == empresa_sel].iloc[0]
        av = {"sector": av_linha["sector"], "preco": float(av_linha["preco"]), "acoes_circulacao": float(av_linha["acoes_circulacao"]), "lucro_liquido": float(av_linha["lucro_liquido"]), "ganho_pontual": float(av_linha["ganho_pontual"]), "capital_proprio": float(av_linha["capital_proprio"]), "dividendo_total": float(av_linha["dividendo_total"]), "crescimento_g": float(av_linha["crescimento_g"])}
        m = calcular_metricas_avaliacao(av, premissas)

        st.caption(f"Sector: {av['sector']} · Capitalização de mercado: {kz(m['cap_mercado'])}")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Preço Actual", kz(av["preco"]))
        col2.metric("P/E", multiplo(m["pe"]))
        col3.metric("P/BV", multiplo(m["pbv"]))
        col4.metric("Dividend Yield", pct(m["dy_nominal"]))
        nota_indicador("<b>P/E</b> = anos de lucro que pagas pelo preço. <b>P/BV</b> = preço face ao valor contabilístico. <b>Dividend Yield</b> = retorno anual em dividendos.")

        col5, col6, col7 = st.columns(3)
        col5.metric("Valor Justo (DDM)", kz(m["valor_justo"]) if m["valor_justo"] is not None else "n/d")
        col6.metric("Upside / Downside", pct(m["upside"]) if m["upside"] is not None else "n/d")
        col7.metric("Custo de Capital (Ke)", pct(m["ke"]))
        nota_indicador("<b>Valor Justo (DDM)</b> é uma estimativa. <b>Upside/Downside</b> compara com o mercado. <b>Ke</b> é o retorno mínimo exigido pelo risco do sector.")

        if m["upside"] is not None:
            if m["upside"] > 0.15:
                st.success("O modelo DDM sugere uma acção potencialmente subvalorizada face ao mercado.")
            elif m["upside"] < -0.15:
                st.warning("O modelo DDM sugere uma acção potencialmente sobrevalorizada face ao mercado.")
            else:
                st.info("O modelo DDM sugere que o preço de mercado está próximo do valor estimado.")

        st.caption("DDM/Gordon Growth: Valor Justo = D1 ÷ (Ke − g). Usar como cross-check, nunca isoladamente.")

        st.divider()
        st.subheader("⭐ Análise Aprofundada (Premium)")

        if not st.session_state["is_premium"]:
            render_html('<div class="appo-premium-lock"><strong>Esta secção é exclusiva para sócios Premium.</strong><br/>Comparação sectorial, sensibilidade, ROE e Dividend Yield real.<br/><br/>Fala com um administrador para activares o Premium.</div>')
        else:
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("ROE", pct(m["roe"]) if m["roe"] is not None else "n/d")
            col_b.metric("Payout", pct(m["payout"]) if m["payout"] is not None else "n/d")
            col_c.metric("Dividend Yield Real", pct(m["dy_real"]))
            nota_indicador("<b>ROE</b> = rentabilidade sobre o capital próprio. <b>Payout</b> = fracção do lucro distribuída. <b>DY Real</b> = yield descontado da inflação.")

            st.markdown("##### Tabela de Sensibilidade — Valor Justo (Kz por acção)")
            nota_indicador(
                "Esta tabela responde a: <b>\"e se as nossas suposições estivessem um pouco erradas?\"</b> O Valor Justo (DDM) depende de duas "
                "estimativas que ninguém sabe ao certo: o <b>Ke</b> (retorno que exigimos pelo risco do sector) e o <b>g</b> (crescimento futuro "
                "assumido para os dividendos). Cada linha é um cenário diferente de Ke, cada coluna um cenário diferente de g. Regra geral: quanto "
                "<b>maior o g</b> (mais optimista sobre o crescimento) ou <b>menor o Ke</b> (menos risco exigido), <b>maior</b> o valor justo estimado — "
                "e vice-versa. Se o valor justo variar muito de canto a canto da tabela, é sinal de que a avaliação desta empresa é sensível às "
                "suposições, e deve ser usada com mais cautela; se variar pouco, a estimativa é mais robusta."
            )
            ke_base, g_base = m["ke"], av["crescimento_g"]
            cenarios_g = [max(0.0, g_base - 0.02), g_base, g_base + 0.02]
            cenarios_ke = [ke_base - 0.02, ke_base, ke_base + 0.02]
            linhas = []
            for ke_c in cenarios_ke:
                linha = {}
                for g_c in cenarios_g:
                    linha[f"g={g_c*100:.1f}%"] = kz((m["dps"] * (1 + g_c)) / (ke_c - g_c)) if ke_c > g_c else "—"
                linhas.append(linha)
            st.dataframe(pd.DataFrame(linhas, index=[f"Ke={ke_c*100:.1f}%" for ke_c in cenarios_ke]))

            st.markdown("##### Comparação Sectorial (todas as empresas)")
            nota_indicador(
                "Compara todas as empresas acompanhadas lado a lado pelos mesmos indicadores: <b>P/E</b> (quantos anos de lucro pagas pelo preço "
                "actual — mais baixo pode ser mais barato, mas verifica sempre a razão); <b>P/BV</b> (preço face ao valor contabilístico da empresa); "
                "<b>ROE</b> (rentabilidade que a empresa gera sobre o capital próprio dos seus accionistas — quanto maior, melhor, em geral); "
                "<b>DY Nominal</b> (retorno anual só em dividendos, antes de descontar a inflação); e <b>Upside DDM</b> (se positivo, o modelo sugere "
                "que a acção pode estar barata face ao seu valor justo estimado; se negativo, pode estar cara). Usa esta tabela para comparar "
                "empresas do mesmo sector entre si — comparar banca com telecomunicações, por exemplo, é menos directo, porque têm níveis de risco "
                "e de crescimento muito diferentes. Nenhum destes números, isolado, é uma recomendação de compra ou venda."
            )
            linhas_comp = []
            for _, l in df_aval.iterrows():
                av_l = {"sector": l["sector"], "preco": float(l["preco"]), "acoes_circulacao": float(l["acoes_circulacao"]), "lucro_liquido": float(l["lucro_liquido"]), "ganho_pontual": float(l["ganho_pontual"]), "capital_proprio": float(l["capital_proprio"]), "dividendo_total": float(l["dividendo_total"]), "crescimento_g": float(l["crescimento_g"])}
                m_l = calcular_metricas_avaliacao(av_l, premissas)
                linhas_comp.append({
                    "Empresa": l["empresa"], "Sector": l["sector"],
                    "P/E": m_l["pe"] if m_l["pe"] is not None else None,
                    "P/BV": m_l["pbv"] if m_l["pbv"] is not None else None,
                    "ROE": m_l["roe"] if m_l["roe"] is not None else None,
                    "DY Nominal": m_l["dy_nominal"],
                    "Upside DDM": m_l["upside"] if m_l["upside"] is not None else None,
                })
            df_comp = pd.DataFrame(linhas_comp)
            df_comp_exibir = df_comp.copy()
            df_comp_exibir["P/E"] = df_comp_exibir["P/E"].apply(multiplo)
            df_comp_exibir["P/BV"] = df_comp_exibir["P/BV"].apply(multiplo)
            df_comp_exibir["ROE"] = df_comp_exibir["ROE"].apply(lambda v: pct(v) if v is not None else "n/d")
            df_comp_exibir["DY Nominal"] = df_comp_exibir["DY Nominal"].apply(pct)
            df_comp_exibir["Upside DDM"] = df_comp_exibir["Upside DDM"].apply(lambda v: pct(v) if v is not None else "n/d")
            st.dataframe(df_comp_exibir, hide_index=True)
            st.download_button(
                "⬇️ Descarregar comparação sectorial em Excel",
                data=gerar_excel_bytes(df_comp, "Comparação Sectorial", colunas_percentagem=["ROE", "DY Nominal", "Upside DDM"], colunas_multiplo=["P/E", "P/BV"]),
                file_name="comparacao_sectorial_appo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

# =========================================================
# PÁGINA: CONVERSOR DE MOEDA (automático + histórico automático)
# =========================================================
elif pagina == "💱 Conversor de Moeda":
    hero("Conversor de Moeda", "Taxas de câmbio automáticas, actualizadas diariamente, com o Kwanza incluído", "💱 exchangerate-api.com (aberta)")

    MOEDAS = ["AOA", "USD", "EUR", "GBP", "ZAR", "CNY", "BRL"]
    col1, col2, col3 = st.columns(3)
    moeda_de = col1.selectbox("De", MOEDAS, index=0)
    moeda_para = col2.selectbox("Para", MOEDAS, index=1)
    valor = col3.number_input("Valor", min_value=0.0, value=1000.0, step=100.0)

    try:
        dados_cambio = obter_taxas_cambio(moeda_de)
        if moeda_de == "AOA":
            registar_historico_cambio(dados_cambio["rates"])
        taxa = dados_cambio["rates"].get(moeda_para)
        if taxa is None:
            st.error("Esta moeda não está disponível na fonte de dados neste momento.")
        else:
            resultado = valor * taxa
            st.metric(f"{valor:,.2f} {moeda_de} equivale a", f"{resultado:,.2f} {moeda_para}")
            st.caption(f"Taxa: 1 {moeda_de} = {taxa:.6f} {moeda_para}. Actualizado: {dados_cambio['actualizado']}.")
            botoes_partilha(f"{valor:,.2f} {moeda_de} = {resultado:,.2f} {moeda_para} — Clube de Investimento APPO")
    except Exception:
        st.warning("Não foi possível obter as taxas de câmbio neste momento. Tenta novamente dentro de instantes.")

    st.divider()
    st.subheader("Tabela rápida (a partir de 1 Kz)")
    try:
        dados_kz = obter_taxas_cambio("AOA")
        registar_historico_cambio(dados_kz["rates"])
        linhas = [{"Moeda": m, "1 Kz equivale a": f"{dados_kz['rates'].get(m, 0):.6f} {m}"} for m in MOEDAS if m != "AOA"]
        st.dataframe(pd.DataFrame(linhas), hide_index=True)
    except Exception:
        st.caption("Tabela indisponível de momento.")

    st.divider()
    st.subheader("📈 Evolução das Cotações do Kwanza")
    df_hist_cambio = obter_historico_cambio()
    if len(df_hist_cambio) >= 2:
        df_hist_cambio["registado_em"] = pd.to_datetime(df_hist_cambio["registado_em"])
        col_m, col_p = st.columns([1, 2])
        moeda_grafico = col_m.selectbox("Moeda", ["usd", "eur", "gbp", "zar", "cny", "brl"], format_func=lambda x: x.upper())
        periodo = col_p.radio("Período", ["7D", "1M", "3M", "6M", "1A", "Máx.", "Personalizado"], horizontal=True)

        data_min, data_max = df_hist_cambio["registado_em"].min(), df_hist_cambio["registado_em"].max()
        janelas = {"7D": 7, "1M": 30, "3M": 91, "6M": 182, "1A": 365}
        if periodo == "Personalizado":
            col_di, col_df = st.columns(2)
            data_inicio = col_di.date_input("Data Início", value=max(data_min, data_max - timedelta(days=30)).date(), min_value=data_min.date(), max_value=data_max.date())
            data_fim = col_df.date_input("Data Fim", value=data_max.date(), min_value=data_min.date(), max_value=data_max.date())
            df_periodo = df_hist_cambio[(df_hist_cambio["registado_em"] >= pd.Timestamp(data_inicio)) & (df_hist_cambio["registado_em"] <= pd.Timestamp(data_fim))]
        elif periodo == "Máx.":
            df_periodo = df_hist_cambio
        else:
            limite = data_max - timedelta(days=janelas[periodo])
            df_periodo = df_hist_cambio[df_hist_cambio["registado_em"] >= limite]

        if len(df_periodo) >= 2:
            st.line_chart(df_periodo.set_index("registado_em")[[moeda_grafico]].rename(columns={moeda_grafico: f"1 AOA em {moeda_grafico.upper()}"}))
        else:
            st.info("Ainda não há pontos suficientes neste período em concreto — experimenta um período mais alargado.")
        st.caption(
            "Este gráfico é construído com o histórico diário que a própria app vai acumulando automaticamente, sem ninguém precisar de inserir nada, "
            "sempre que alguém abre esta página num novo dia. Nota importante: não existe, de momento, uma fonte externa gratuita de cotações "
            "históricas do Kwanza (a maioria exige uma subscrição paga); por isso este histórico só cobre os dias em que a app esteve activa e alguém "
            "visitou esta página — não recua a datas anteriores ao início da recolha. Se quiseres um histórico verdadeiramente completo desde já "
            "(30 dias, 1 ano, etc.), a alternativa é subscrever uma API paga de câmbio histórico (ex.: exchangerate.host/apilayer) e eu integro-a."
        )
    else:
        st.info("Ainda há poucos dias de histórico acumulado. Volta aqui em dias diferentes para veres a tendência a formar-se — ou considera uma API paga de câmbio histórico para preencher o passado de imediato.")

# =========================================================
# PÁGINA: SIMULADOR DE INVESTIMENTO
# =========================================================
elif pagina == "🧪 Simulador de Investimento":
    hero("Simulador de Investimento", "Projecta o crescimento do teu investimento ao longo do tempo, com juros compostos")

    col1, col2 = st.columns(2)
    valor_inicial = col1.number_input("Valor inicial (Kz)", min_value=0.0, value=100000.0, step=10000.0)
    contrib_mensal = col2.number_input("Contribuição mensal (Kz)", min_value=0.0, value=20000.0, step=5000.0)
    col3, col4, col5 = st.columns(3)
    taxa_anual = col3.slider("Taxa de retorno anual esperada (%)", 0.0, 40.0, 12.0, 0.5)
    anos = col4.slider("Prazo (anos)", 1, 30, 10)
    inflacao_sim = col5.slider("Inflação anual assumida (%)", 0.0, 40.0, 13.5, 0.5)

    taxa_mensal = (1 + taxa_anual / 100) ** (1 / 12) - 1
    inflacao_mensal = (1 + inflacao_sim / 100) ** (1 / 12) - 1
    saldo = valor_inicial
    total_investido = valor_inicial
    pontos = []
    for mes in range(1, anos * 12 + 1):
        saldo = saldo * (1 + taxa_mensal) + contrib_mensal
        total_investido += contrib_mensal
        if mes % 12 == 0:
            saldo_real = saldo / ((1 + inflacao_mensal) ** mes)
            pontos.append({"Ano": mes // 12, "Saldo Nominal": saldo, "Total Investido": total_investido, "Saldo Real (poder de compra de hoje)": saldo_real})

    df_sim = pd.DataFrame(pontos).set_index("Ano")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Saldo Final (nominal)", kz(saldo))
    col_b.metric("Total Investido", kz(total_investido))
    col_c.metric("Juros Compostos Ganhos", kz(saldo - total_investido))
    st.bar_chart(df_sim[["Saldo Nominal", "Total Investido"]])
    st.caption(f"Saldo final em poder de compra de hoje (descontada a inflação assumida de {inflacao_sim:.1f}%/ano): {kz(df_sim['Saldo Real (poder de compra de hoje)'].iloc[-1])}")
    st.caption("Simulação educativa com juros compostos mensais constantes — os retornos reais dos mercados variam e não são garantidos. Não constitui aconselhamento de investimento.")
    botoes_partilha(f"Simulei {kz(valor_inicial)} + {kz(contrib_mensal)}/mês durante {anos} anos a {taxa_anual:.1f}%/ano = {kz(saldo)} — Clube de Investimento APPO")

# =========================================================
# PÁGINA: REGRA 50/30/20
# =========================================================
elif pagina == "🧮 Regra 50/30/20":
    hero("Regra 50/30/20 do Clube", "Princípio nº 8: 50% Consumo · 30% Investimento · 20% Entesouramento", "📐 Rendimento mensal total, incluindo extras")
    rendimento = st.number_input("Rendimento mensal total (Kz)", min_value=0.0, step=5000.0, value=250000.0, format="%.2f")
    alvo_consumo, alvo_investimento, alvo_entesouramento = rendimento * 0.50, rendimento * 0.30, rendimento * 0.20

    st.subheader("Alocação recomendada")
    col1, col2, col3 = st.columns(3)
    col1.metric("Consumo (50%)", kz(alvo_consumo))
    col2.metric("Investimento (30%)", kz(alvo_investimento))
    col3.metric("Entesouramento (20%)", kz(alvo_entesouramento))
    st.bar_chart(pd.DataFrame({"Categoria": ["Consumo", "Investimento", "Entesouramento"], "Valor recomendado (Kz)": [alvo_consumo, alvo_investimento, alvo_entesouramento]}).set_index("Categoria"))

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
        col2.metric("Investimento", kz(real_investimento), delta=kz(real_investimento - alvo_investimento), delta_color="normal")
        col3.metric("Entesouramento", kz(real_entesouramento), delta=kz(real_entesouramento - alvo_entesouramento), delta_color="normal")
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
            with st.expander(f"{ICONES_CATEGORIA.get(artigo['categoria'], '📄')} {artigo['titulo']}", key=f"artigo_exp_{artigo['id']}"):
                banner_categoria(artigo["categoria"])
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
            st.success("Pedido de adesão submetido com sucesso! Um administrador do Clube irá entrar em contacto.")

# =========================================================
# PÁGINA: SOBRE NÓS & ESTATUTOS
# =========================================================
elif pagina == "ℹ️ Sobre Nós & Estatutos":
    hero("Sobre Nós & Estatutos", "A missão, os princípios e o enquadramento estatutário do Clube")
    st.subheader("Quem somos")
    st.markdown("O **Clube de Investimento APPO** é uma associação de investidores angolanos que junta capital de forma colectiva para investir no mercado de capitais nacional, através da Bolsa de Dívida e Valores de Angola (BODIVA).")
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
    st.caption("Nota interna: modelo de referência, a substituir pelos Estatutos formalmente aprovados e registados do Clube.")

# =========================================================
# PÁGINA: PAINEL DO ADMINISTRADOR
# =========================================================
elif pagina == "🔐 Painel do Administrador":
    hero("Painel do Administrador", "Gestão de conteúdo, cotações, movimentos, sócios, contas e avaliações")

    aba_resumo, aba_activos, aba_aval, aba_movimentos, aba_biblioteca, aba_socios, aba_contas, aba_seguranca = st.tabs(
        ["Resumo Patrimonial", "Cotações & Activos", "Avaliação", "Movimentos", "Biblioteca", "Sócios", "Contas", "Segurança"]
    )

    with aba_resumo:
        st.subheader("Editar Resumo Patrimonial")
        st.caption("O Capital Realizado já não se edita directamente: é sempre igual a Investimentos + Reservas (é o mesmo dinheiro, só que aplicado ou guardado). Edita apenas o Capital Subscrito, os Investimentos e as Reservas.")
        resumo = obter_resumo_patrimonial()
        with st.form("form_editar_resumo"):
            novo_subscrito = st.number_input("Capital Subscrito (Kz)", min_value=0.0, step=10000.0, value=float(resumo["capital_subscrito"]))
            novo_investimentos = st.number_input("Investimentos (Kz)", min_value=0.0, step=10000.0, value=float(resumo["investimentos"]))
            novas_reservas = st.number_input("Reservas (Kz)", min_value=0.0, step=10000.0, value=float(resumo["reservas"]))
            novo_realizado_preview = novo_investimentos + novas_reservas
            st.metric("Capital Realizado (calculado automaticamente)", kz(novo_realizado_preview))
            st.caption(f"Capital por Realizar (calculado): {kz(max(novo_subscrito - novo_realizado_preview, 0.0))}")
            guardar_resumo = st.form_submit_button("Guardar alterações")
        if guardar_resumo:
            if novo_realizado_preview > novo_subscrito:
                st.error("Investimentos + Reservas não pode ser maior do que o Capital Subscrito — isso significaria realizar mais capital do que os sócios prometeram.")
            else:
                actualizar_resumo_patrimonial(novo_subscrito, novo_investimentos, novas_reservas)
                st.success("Resumo patrimonial actualizado e novo ponto de histórico registado.")
                st.rerun()

    with aba_activos:
        st.subheader("Editar Cotações & Activos")
        st.caption("A Variação (%) já não se preenche à mão: ao guardares, é calculada automaticamente comparando o novo Preço com o preço que estava registado antes desta gravação para o mesmo activo. Um activo novo (sem preço anterior) começa com 0.00%. O Barómetro BODIVA e o seu histórico são recalculados de seguida.")
        df_activos = obter_activos()
        df_editado = st.data_editor(
            df_activos[["ticker", "nome", "tipo", "preco"]], num_rows="dynamic", key="editor_activos",
            column_config={
                "ticker": st.column_config.TextColumn("Ticker", max_chars=12), "nome": "Nome do activo", "tipo": "Tipo",
                "preco": st.column_config.NumberColumn("Preço (Kz)", min_value=0.0, step=0.01, format="%.2f"),
            },
        )
        if st.button("Guardar alterações às cotações"):
            substituir_activos(df_editado)
            st.success("Cotações guardadas. Variação calculada automaticamente e Barómetro BODIVA actualizado com sucesso.")
            st.rerun()

    with aba_aval:
        st.subheader("Premissas Macro (CAPM)")
        premissas = obter_premissas_macro()
        with st.form("form_premissas"):
            col1, col2, col3 = st.columns(3)
            infl = col1.number_input("Inflação anual", min_value=0.0, max_value=1.0, value=premissas["inflacao"], step=0.005, format="%.3f")
            rf = col2.number_input("Taxa livre de risco (Rf)", min_value=0.0, max_value=1.0, value=premissas["taxa_livre_risco"], step=0.005, format="%.3f")
            erp = col3.number_input("Prémio de risco de mercado (ERP)", min_value=0.0, max_value=1.0, value=premissas["premio_risco"], step=0.005, format="%.3f")
            col4, col5, col6 = st.columns(3)
            bb = col4.number_input("Beta — Banca", min_value=0.0, max_value=3.0, value=premissas["beta_banca"], step=0.05)
            bt = col5.number_input("Beta — Telecom", min_value=0.0, max_value=3.0, value=premissas["beta_telecom"], step=0.05)
            bo = col6.number_input("Beta — Outros sectores", min_value=0.0, max_value=3.0, value=premissas["beta_outros"], step=0.05)
            guardar_premissas = st.form_submit_button("Guardar premissas")
        if guardar_premissas:
            actualizar_premissas_macro(infl, rf, erp, bb, bt, bo)
            st.success("Premissas macro actualizadas.")
            st.rerun()

        st.divider()
        st.subheader("Dados de Avaliação por Empresa")
        df_aval = obter_avaliacoes()
        df_aval_editado = st.data_editor(
            df_aval[["empresa", "sector", "preco", "acoes_circulacao", "lucro_liquido", "ganho_pontual", "capital_proprio", "dividendo_total", "crescimento_g"]],
            num_rows="dynamic", key="editor_avaliacoes",
            column_config={
                "empresa": "Empresa", "sector": "Sector", "preco": st.column_config.NumberColumn("Preço (Kz)", min_value=0.0, step=0.01, format="%.2f"),
                "acoes_circulacao": st.column_config.NumberColumn("Acções em circulação", min_value=0.0, step=1000.0),
                "lucro_liquido": st.column_config.NumberColumn("Lucro líquido (Kz)", step=1000000.0),
                "ganho_pontual": st.column_config.NumberColumn("Ganho pontual não recorrente (Kz)", step=1000000.0),
                "capital_proprio": st.column_config.NumberColumn("Capital próprio (Kz)", min_value=0.0, step=1000000.0),
                "dividendo_total": st.column_config.NumberColumn("Dividendo total distribuído (Kz)", min_value=0.0, step=1000000.0),
                "crescimento_g": st.column_config.NumberColumn("Crescimento assumido (g)", min_value=0.0, max_value=1.0, step=0.01, format="%.2f"),
            },
        )
        if st.button("Guardar alterações às avaliações"):
            substituir_avaliacoes(df_aval_editado)
            st.success("Avaliações actualizadas com sucesso.")
            st.rerun()

    with aba_movimentos:
        st.subheader("Registar novo movimento")
        with st.form("form_novo_movimento", clear_on_submit=True):
            tipo_mov = st.selectbox("Tipo", ["Entrada de Capital", "Compra de Activo", "Venda de Activo", "Saída/Despesa", "Ajuste de Reserva"])
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
                    st.success("Texto extraído com sucesso. Revê antes de publicar.")
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
            st.dataframe(df_socios_exibir.rename(columns={"nome": "Nome", "email": "E-mail", "telefone": "Telefone", "bi": "Nº BI", "contribuicao_inicial": "Contribuição Inicial", "criado_em": "Submetido em"}), hide_index=True)

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
        st.caption("Activa o acesso Premium depois de confirmares o pagamento do sócio.")
        df_contas = listar_contas()
        for _, conta in df_contas.iterrows():
            col_a, col_b, col_c, col_d, col_e = st.columns([2.3, 0.9, 1.1, 1.1, 1.1])
            col_a.write(f"{conta['nome']} — {conta['email']}")
            col_b.write("Admin" if conta["is_admin"] else "Sócio")
            if conta["is_premium"]:
                if col_c.button("Remover Premium", key=f"despremium_{conta['id']}"):
                    alternar_premium(int(conta["id"]), False)
                    st.rerun()
            else:
                if col_c.button("Tornar Premium", key=f"premium_{conta['id']}"):
                    alternar_premium(int(conta["id"]), True)
                    st.rerun()
            if col_d.button("Repor password", key=f"repor_{conta['id']}"):
                nova = repor_password(int(conta["id"]))
                st.info(f"Nova palavra-passe para {conta['email']}: **{nova}**")
            pode_eliminar = not (conta["is_admin"] and contar_admins() <= 1)
            if col_e.button("Eliminar", key=f"eliminar_conta_{conta['id']}", disabled=not pode_eliminar):
                eliminar_conta(int(conta["id"]))
                st.rerun()

    with aba_seguranca:
        st.subheader("Registo de tentativas de acesso (últimas 50)")
        df_log = obter_log_acessos()
        if df_log.empty:
            st.info("Ainda não há registos de acesso.")
        else:
            st.dataframe(df_log.rename(columns={"email": "E-mail", "sucesso": "Sucesso", "criado_em": "Data/Hora"}), hide_index=True)
