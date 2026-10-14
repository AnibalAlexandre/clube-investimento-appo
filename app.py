"""
Clube de Investimento APPO
APPO — Educação Financeira e Área Privada de Investimentos
Aplicação web corporativa privada — Streamlit + PostgreSQL (Neon)
"""

import os
import secrets
import html as _html_pub
import textwrap
import time
import traceback
import urllib.parse
import smtplib
import socket
import ssl
from email.message import EmailMessage
from datetime import datetime
from pathlib import Path

import bcrypt
import pandas as pd
import psycopg2
import psycopg2.extras
import requests
import streamlit as st
from fpdf import FPDF
from pypdf import PdfReader

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(page_title="Clube de Investimento APPO", page_icon="🕐", layout="wide", initial_sidebar_state="expanded")


def render_html(html: str):
    st.markdown(textwrap.dedent(html).strip(), unsafe_allow_html=True)


# =========================================================
# IMAGENS
# =========================================================
# Painel de cotações tipo Bloomberg — azul néon, gráficos de velas, dados vibrantes (Pexels CC0)
IMG_SKYLINE = "https://images.pexels.com/photos/6801648/pexels-photo-6801648.jpeg?auto=compress&cs=tinysrgb&w=1600"
IMG_GRAFICO = "https://images.pexels.com/photos/6802042/pexels-photo-6802042.jpeg?auto=compress&cs=tinysrgb&w=1600"
IMG_REUNIAO = "https://images.pexels.com/photos/7567443/pexels-photo-7567443.jpeg?auto=compress&cs=tinysrgb&w=1600"
IMG_LIVROS  = "https://images.pexels.com/photos/6801874/pexels-photo-6801874.jpeg?auto=compress&cs=tinysrgb&w=1600"
IMAGENS_CATEGORIA = {"Institucional": IMG_REUNIAO, "Educação": IMG_LIVROS, "Análise de Mercado": IMG_GRAFICO, "Referência": IMG_SKYLINE}

# =========================================================
# TRADUÇÕES COMPLETAS
# =========================================================
TRADUCOES = {
    # ─────────────────────────────────────────────────────
    "Português": {
        # ── sistema / login ──────────────────────────────
        "tagline": "APPO — Educação Financeira e Área Privada de Investimentos",
        "login_titulo": "Acesso reservado a sócios",
        "email": "E-mail", "password": "Palavra-passe", "entrar": "Entrar",
        "erro_login": "E-mail ou palavra-passe incorrectos. Contacta um administrador do Clube.",
        "sessao": "Sessão", "terminar_sessao": "Terminar sessão",
        # ── navegação ────────────────────────────────────
        "nav_map": {
            "🏠 Início & Análises":         "🏠 Início & Análises",
            "📈 Cotações & Activos":         "📈 Cotações & Activos",
            "💰 Contabilidade & Finanças":  "💰 Contabilidade & Finanças",
            "📊 Histórico & Relatórios":    "📊 Histórico & Relatórios",
            "📐 Avaliação de Activos":       "📐 Avaliação de Activos",
            "💱 Conversor de Moeda":         "💱 Conversor de Moeda",
            "🧪 Simulador de Investimento": "🧪 Simulador de Investimento",
            "🧮 Princípio 50/30/20":            "🧮 Princípio 50/30/20",
            "📚 Biblioteca Educativa":       "📚 Biblioteca & Research",
            "🧾 Adesão de Sócios":          "🧾 Manifestação de Interesse",
            "ℹ️ Sobre Nós & Estatutos":     "ℹ️ Sobre Nós & Estatutos",
            "🔐 Painel do Administrador":   "🔐 Painel do Administrador",
        },
        # ── página início ────────────────────────────────
        "inicio_hero_sub": "APPO — Capacidade Financeira Prática. Organize o seu dinheiro e tome decisões autónomas.",
        "inicio_capital_subscrito": "Capital Subscrito",
        "inicio_capital_realizado": "Capital Realizado",
        "inicio_pct_subscrito": "% do subscrito",
        "inicio_investimentos": "Investimentos",
        "inicio_reservas": "Reservas",
        "inicio_patrimonio_total": "Património Total",
        "inicio_indice_label": "📊 Índice APPO (média das acções cotadas)",
        "inicio_indice_caption": "Como teria valorizado uma carteira investida em partes iguais em todas as acções acompanhadas pelo Clube.",
        "inicio_distribuicao": "Distribuição do Património",
        "inicio_distribuicao_cats": ["Capital Realizado", "Investimentos", "Reservas"],
        "inicio_cotacoes_destaque": "📌 Cotações em destaque",
        "inicio_capa_texto": "Disciplina, transparência e visão de longo prazo",
        # ── cotações ────────────────────────────────────
        "cot_hero_sub": "Instrumentos financeiros cotados na BODIVA acompanhados pelo Clube",
        "cot_indice_titulo": "📊 Índice APPO — cotação média do mercado",
        "cot_indice_metric": "Variação média de hoje",
        "cot_indice_caption": "Se tivesses investido em partes iguais em todas as acções cotadas pelo Clube, a tua carteira teria variado, em média, este valor.",
        "cot_indice_hist_label": "Índice APPO — diário (%)",
        "cot_indice_hist_info": "O histórico diário do Índice APPO vai-se formando a cada dia em que o administrador actualizar as cotações.",
        "cot_tendencia_semanal": "##### Tendência semanal do Índice APPO",
        "cot_tendencia_sem_caption1": "Ainda não há pelo menos duas semanas de histórico para mostrar a tendência semanal.",
        "cot_tendencia_sem_caption2": "Ainda não há histórico suficiente para a vista semanal.",
        "cot_tab_favoritos": "⭐ Os meus favoritos",
        "cot_tab_todos": "🔭 Universo do Clube",
        "cot_fav_escolher": "Escolher os teus activos favoritos",
        "cot_fav_info": "Ainda não marcaste nenhum activo como favorito. Usa a caixa acima.",
        "cot_filtrar_tipo": "Filtrar por tipo de activo",
        "cot_filtrar_todos": "Todos",
        "cot_ultima_actualizacao": "Última actualização:",
        "cot_descarregar_csv": "⬇️ Descarregar tabela em CSV",
        "cot_comparacao": "Comparação de preços",
        "cot_preco_kz": "Preço (Kz)",
        "cot_tabela_cols": {"ticker": "Ticker", "nome": "Activo", "tipo": "Tipo", "preco": "Preço", "variacao": "Variação", "mercado": "Mercado"},
        # ── contabilidade ────────────────────────────────
        "cont_hero_sub": "Resumo Contabilístico e Patrimonial do Clube",
        "cont_df_cols": ["Categoria", "Descrição", "Montante", "Moeda"],
        "cont_df_rows": [
            ("Capital Subscrito",  "Total de capital comprometido pelos sócios",                    "AOA"),
            ("Capital Realizado",  "Parte do capital subscrito já efectivamente paga",              "AOA"),
            ("Investimentos",      "Carteira de acções e instrumentos financeiros cotados na BODIVA","AOA"),
            ("Reservas",           "Fundo de estabilização e liquidez para novas oportunidades",    "AOA"),
        ],
        "cont_patrimonio_metric": "Património Total do Clube",
        "cont_ultima_actualizacao": "Última actualização:",
        # ── histórico ────────────────────────────────────
        "hist_hero_sub": "Evolução do património do Clube ao longo do tempo, e exportação de relatórios",
        "hist_poucos_pontos": "Ainda há poucos pontos de histórico. Este gráfico vai ganhando forma com o tempo.",
        "hist_caption": "Cada ponto representa uma actualização do resumo patrimonial. Eixo vertical em Kwanzas (Kz).",
        "hist_patrimonio_label": "Património Total (Kz)",
        "hist_movimentos": "Movimentos registados",
        "hist_sem_movimentos": "Ainda não existem movimentos registados.",
        "hist_cols": {"tipo": "Tipo", "descricao": "Descrição", "montante_fmt": "Montante", "data_movimento": "Data", "criado_em": "Registado em"},
        "hist_descarregar_mov": "⬇️ Descarregar movimentos em CSV",
        "hist_exportar": "Exportar relatório",
        "hist_gerar_pdf": "Gerar relatório em PDF",
        "hist_descarregar_pdf": "Descarregar relatório em PDF",
        # ── avaliação ────────────────────────────────────
        "aval_hero_sub": "Múltiplos e valor justo (DDM) das empresas cotadas, com dados reais do Clube",
        "aval_empresa": "Empresa",
        "aval_sector": "Sector",
        "aval_cap_mercado": "Capitalização de mercado:",
        "aval_preco": "Preço Actual",
        "aval_pe": "P/E", "aval_pbv": "P/BV", "aval_dy": "Dividend Yield",
        "aval_nota1": "<b>P/E</b> = anos de lucro que pagas pelo preço. <b>P/BV</b> = preço face ao valor contabilístico. <b>Dividend Yield</b> = retorno anual em dividendos.",
        "aval_vj": "Valor Justo (DDM)", "aval_upside": "Upside / Downside", "aval_ke": "Custo de Capital (Ke)",
        "aval_nota2": "<b>Valor Justo (DDM)</b> é uma estimativa. <b>Upside/Downside</b> compara com o mercado. <b>Ke</b> é o retorno mínimo exigido pelo risco do sector.",
        "aval_subvalorizado": "O modelo DDM sugere uma acção potencialmente subvalorizada face ao mercado.",
        "aval_sobrevalorizado": "O modelo DDM sugere uma acção potencialmente sobrevalorizada face ao mercado.",
        "aval_justo": "O modelo DDM sugere que o preço de mercado está próximo do valor estimado.",
        "aval_ddm_caption": "DDM/Gordon Growth: Valor Justo = D1 ÷ (Ke − g). Usar como cross-check, nunca isoladamente.",
        "aval_premium_titulo": "⭐ Análise Aprofundada (Premium)",
        "aval_premium_lock": "<div class='appo-premium-lock'><strong>Esta secção é exclusiva para sócios Premium.</strong><br/>Comparação sectorial, sensibilidade, ROE e Dividend Yield real.<br/><br/>Fala com um administrador para activares o Premium.</div>",
        "aval_roe": "ROE", "aval_payout": "Payout", "aval_dy_real": "Dividend Yield Real",
        "aval_nota3": "<b>ROE</b> = rentabilidade sobre o capital próprio. <b>Payout</b> = fracção do lucro distribuída. <b>DY Real</b> = yield descontado da inflação.",
        "aval_sensibilidade": "##### Tabela de Sensibilidade — Valor Justo (Kz por acção)",
        "aval_comparacao": "##### Comparação Sectorial (todas as empresas)",
        "aval_comp_cols": {"Empresa": "Empresa", "Sector": "Sector", "P/E": "P/E", "P/BV": "P/BV", "ROE": "ROE", "DY Nominal": "DY Nominal", "Upside DDM": "Upside DDM"},
        "aval_descarregar_comp": "⬇️ Descarregar comparação sectorial em CSV",
        "aval_sem_dados": "Ainda não existem avaliações registadas.",
        # ── conversor ────────────────────────────────────
        "conv_hero_sub": "Taxas de câmbio automáticas, actualizadas diariamente, com o Kwanza incluído",
        "conv_de": "De", "conv_para": "Para", "conv_valor": "Valor",
        "conv_equivale": "equivale a",
        "conv_taxa": "Taxa:",
        "conv_actualizado": "Actualizado:",
        "conv_erro": "Esta moeda não está disponível na fonte de dados neste momento.",
        "conv_aviso": "Não foi possível obter as taxas de câmbio neste momento. Tenta novamente dentro de instantes.",
        "conv_tabela_titulo": "Tabela rápida (a partir de 1 Kz)",
        "conv_tabela_col": "1 Kz equivale a",
        "conv_tabela_indisponivel": "Tabela indisponível de momento.",
        "conv_historico_titulo": "📈 Tendência do Kwanza (histórico próprio, acumulado automaticamente)",
        "conv_historico_select": "Ver tendência de",
        "conv_historico_label": "1 AOA em",
        "conv_historico_info": "Ainda há poucos dias de histórico acumulado. Volta aqui em dias diferentes para veres a tendência a formar-se sozinha.",
        "conv_historico_caption": "Este histórico é construído automaticamente pela própria app — sem ninguém precisar de inserir nada — sempre que alguém abre esta página num novo dia.",
        # ── simulador ────────────────────────────────────
        "sim_hero_sub": "Projecta o crescimento do teu investimento ao longo do tempo, com juros compostos",
        "sim_valor_inicial": "Valor inicial (Kz)",
        "sim_contrib_mensal": "Contribuição mensal (Kz)",
        "sim_taxa": "Taxa de retorno anual esperada (%)",
        "sim_anos": "Prazo (anos)",
        "sim_inflacao": "Inflação anual assumida (%)",
        "sim_saldo_nominal": "Saldo Final (nominal)",
        "sim_total_investido": "Total Investido",
        "sim_juros": "Juros Compostos Ganhos",
        "sim_chart_cols": {"Saldo Nominal": "Saldo Nominal", "Total Investido": "Total Investido"},
        "sim_caption1": "Saldo final em poder de compra de hoje (descontada a inflação assumida de",
        "sim_caption2": "%/ano):",
        "sim_disclaimer": "Ambiente de treino pedagógico com dados de mercado de referência. As simulações servem para estudo de cenários e não constituem recomendação de compra/venda.",
        "sim_partilha": "Simulei {vi} + {cm}/mês durante {a} anos a {t}%/ano = {sf} — Clube de Investimento APPO",
        # ── regra 50/30/20 ───────────────────────────────
        "r50_hero_sub": "Princípio nº 8: 50% Consumo · 30% Investimento · 20% Entesouramento",
        "r50_rendimento": "Rendimento mensal total (Kz)",
        "r50_alocacao": "Alocação recomendada",
        "r50_consumo": "Consumo (50%)", "r50_investimento": "Investimento (30%)", "r50_entesouramento": "Entesouramento (20%)",
        "r50_comparar_titulo": "Compara com os teus gastos reais (opcional)",
        "r50_real_consumo": "Gasto real — Consumo (Kz)",
        "r50_real_investimento": "Gasto real — Investimento (Kz)",
        "r50_real_entesouramento": "Entesouramento real (Kz)",
        "r50_comparar_btn": "Comparar",
        "r50_resultado": "#### Resultado da comparação",
        "r50_aviso": "O teu entesouramento real está abaixo dos 20% recomendados pelo princípio do Clube.",
        "r50_sucesso": "Estás a cumprir, ou a superar, a meta de 20% de entesouramento.",
        # ── biblioteca ───────────────────────────────────
        "bib_hero_sub": "Princípios do Clube e artigos sobre o mercado de capitais angolano",
        "bib_sem_artigos": "Ainda não existem artigos publicados.",
        "bib_filtrar": "Filtrar por categoria",
        "bib_todas": "Todas",
        "bib_publicado": "Publicado em",
        # ── adesão ───────────────────────────────────────
        "ades_hero_sub": "Preenche o formulário para solicitar a tua adesão ao Clube de Investimento APPO",
        "ades_nome": "Nome completo *",
        "ades_email": "E-mail",
        "ades_telefone": "Telefone / WhatsApp",
        "ades_bi": "Número do Bilhete de Identidade",
        "ades_contribuicao": "Contribuição inicial pretendida (Kz)",
        "ades_aceite": "Declaro que li e aceite os Estatutos do Clube de Investimento APPO *",
        "ades_btn": "Submeter pedido de adesão",
        "ades_erro": "Preenche o nome completo e aceita os Estatutos para submeter o pedido.",
        "ades_sucesso": "Pedido de adesão submetido com sucesso! Um administrador do Clube irá entrar em contacto.",
        # ── sobre nós ────────────────────────────────────
        "sobre_hero_sub": "A missão, os princípios e o enquadramento estatutário do Clube",
        "sobre_quem_somos": "Quem somos",
        "sobre_quem_texto": "O **Clube de Investimento APPO** é uma associação de investidores angolanos que junta capital de forma colectiva para investir no mercado de capitais nacional, através da Bolsa de Dívida e Valores de Angola (BODIVA).",
        "sobre_principios": "Princípios e Filosofia de Investimento",
        "sobre_estatutos": "Estatutos — pontos-chave",
        "sobre_estatutos_texto": """
- **Natureza:** associação de investidores, conforme Estatutos formalmente registados.
- **Órgãos sociais:** Assembleia de Sócios, Comissão de Gestão e Conselho Fiscal.
- **Admissão de sócios:** sujeita a aprovação da Comissão de Gestão.
- **Deliberações:** decisões de investimento relevantes exigem deliberação colectiva.
- **Distribuição de resultados:** proporcional à quota de capital de cada sócio.
""",
        "sobre_nota": "Nota interna: modelo de referência, a substituir pelos Estatutos formalmente aprovados e registados do Clube.",
        # ── partilha ─────────────────────────────────────
        "partilha_wa": "💬 WhatsApp", "partilha_tw": "𝕏 X / Twitter", "partilha_fb": "📘 Facebook",
        "conv_partilha": "{v} {de} = {r} {para} — Clube de Investimento APPO",
        # ── pdf ──────────────────────────────────────────
        "pdf_titulo": "Clube de Investimento APPO",
        "pdf_gerado": "Relatorio gerado em",
        "pdf_resumo": "Resumo Patrimonial",
        "pdf_subscrito": "Capital Subscrito:",
        "pdf_realizado": "Capital Realizado:",
        "pdf_investimentos": "Investimentos:",
        "pdf_reservas": "Reservas:",
        "pdf_total": "Total:",
        "pdf_activos": "Activos em Carteira",
        "pdf_movimentos": "Movimentos Recentes",
        "pdf_sem_mov": "Sem movimentos registados.",
        "pdf_nome_ficheiro": "relatorio_appo_{data}.pdf",
        # ── barómetro (hero) ─────────────────────────────
        "bodiva_badge": "🇦🇴 Mercado angolano · Kwanzas (Kz)",
    },

    # ─────────────────────────────────────────────────────
    "English": {
        "tagline": "APPO — Financial Education and Private Investment Area",
        "login_titulo": "Members-only access",
        "email": "E-mail", "password": "Password", "entrar": "Sign in",
        "erro_login": "Incorrect e-mail or password. Contact a Club administrator.",
        "sessao": "Session", "terminar_sessao": "Sign out",
        "nav_map": {
            "🏠 Início & Análises":         "🏠 Home & Analysis",
            "📈 Cotações & Activos":         "📈 Quotes & Assets",
            "💰 Contabilidade & Finanças":  "💰 Accounting & Finance",
            "📊 Histórico & Relatórios":    "📊 History & Reports",
            "📐 Avaliação de Activos":       "📐 Asset Valuation",
            "💱 Conversor de Moeda":         "💱 Currency Converter",
            "🧪 Simulador de Investimento": "🧪 Investment Simulator",
            "🧮 Princípio 50/30/20":            "🧮 50/30/20 Rule",
            "📚 Biblioteca Educativa":       "📚 Learning Library",
            "🧾 Adesão de Sócios":          "🧾 Expression of Interest",
            "ℹ️ Sobre Nós & Estatutos":     "ℹ️ About Us & Bylaws",
            "🔐 Painel do Administrador":   "🔐 Admin Panel",
        },
        "inicio_hero_sub": "APPO — Financial Education and Private Investment Area",
        "inicio_capital_subscrito": "Subscribed Capital",
        "inicio_capital_realizado": "Paid-up Capital",
        "inicio_pct_subscrito": "% of subscribed",
        "inicio_investimentos": "Investments",
        "inicio_reservas": "Reserves",
        "inicio_patrimonio_total": "Total Net Assets",
        "inicio_indice_label": "📊 APPO Index (average of listed shares)",
        "inicio_indice_caption": "How a portfolio invested equally across all Club-tracked shares would have performed.",
        "inicio_distribuicao": "Asset Distribution",
        "inicio_distribuicao_cats": ["Paid-up Capital", "Investments", "Reserves"],
        "inicio_cotacoes_destaque": "📌 Featured Quotes",
        "inicio_capa_texto": "Discipline, transparency and long-term vision",
        "cot_hero_sub": "Financial instruments listed on BODIVA tracked by the Club",
        "cot_indice_titulo": "📊 APPO Index — average market quote",
        "cot_indice_metric": "Average change today",
        "cot_indice_caption": "If you had invested equally across all Club-tracked listed shares, your portfolio would have changed by this average.",
        "cot_indice_hist_label": "APPO Index — daily (%)",
        "cot_indice_hist_info": "The daily APPO Index history builds up each day the administrator updates quotes.",
        "cot_tendencia_semanal": "##### APPO Index — Weekly Trend",
        "cot_tendencia_sem_caption1": "Not enough weeks of history yet to show the weekly trend.",
        "cot_tendencia_sem_caption2": "Not enough history for the weekly view yet.",
        "cot_tab_favoritos": "⭐ Favourites",
        "cot_tab_todos": "📋 All Assets",
        "cot_fav_escolher": "Choose your favourite assets",
        "cot_fav_info": "You haven't marked any asset as a favourite yet. Use the box above.",
        "cot_filtrar_tipo": "Filter by asset type",
        "cot_filtrar_todos": "All",
        "cot_ultima_actualizacao": "Last updated:",
        "cot_descarregar_csv": "⬇️ Download table as CSV",
        "cot_comparacao": "Price comparison",
        "cot_preco_kz": "Price (Kz)",
        "cot_tabela_cols": {"ticker": "Ticker", "nome": "Asset", "tipo": "Type", "preco": "Price", "variacao": "Change", "mercado": "Market"},
        "cont_hero_sub": "Accounting and Balance Sheet Summary of the Club",
        "cont_df_cols": ["Category", "Description", "Amount", "Currency"],
        "cont_df_rows": [
            ("Subscribed Capital",  "Total capital committed by members",                          "AOA"),
            ("Paid-up Capital",     "Portion of subscribed capital already paid in",               "AOA"),
            ("Investments",         "Portfolio of shares and financial instruments listed on BODIVA","AOA"),
            ("Reserves",            "Stabilisation and liquidity fund for new opportunities",      "AOA"),
        ],
        "cont_patrimonio_metric": "Club Total Net Assets",
        "cont_ultima_actualizacao": "Last updated:",
        "hist_hero_sub": "Club asset evolution over time and report exports",
        "hist_poucos_pontos": "Not enough data points yet. This chart will fill in over time.",
        "hist_caption": "Each point represents a balance-sheet update. Vertical axis in Kwanzas (Kz).",
        "hist_patrimonio_label": "Total Net Assets (Kz)",
        "hist_movimentos": "Recorded Transactions",
        "hist_sem_movimentos": "No transactions recorded yet.",
        "hist_cols": {"tipo": "Type", "descricao": "Description", "montante_fmt": "Amount", "data_movimento": "Date", "criado_em": "Recorded at"},
        "hist_descarregar_mov": "⬇️ Download transactions as CSV",
        "hist_exportar": "Export report",
        "hist_gerar_pdf": "Generate PDF report",
        "hist_descarregar_pdf": "Download PDF report",
        "aval_hero_sub": "Multiples and fair value (DDM) of listed companies, using real Club data",
        "aval_empresa": "Company",
        "aval_sector": "Sector",
        "aval_cap_mercado": "Market capitalisation:",
        "aval_preco": "Current Price",
        "aval_pe": "P/E", "aval_pbv": "P/BV", "aval_dy": "Dividend Yield",
        "aval_nota1": "<b>P/E</b> = years of earnings you pay for the price. <b>P/BV</b> = price vs book value. <b>Dividend Yield</b> = annual dividend return.",
        "aval_vj": "Fair Value (DDM)", "aval_upside": "Upside / Downside", "aval_ke": "Cost of Equity (Ke)",
        "aval_nota2": "<b>Fair Value (DDM)</b> is an estimate. <b>Upside/Downside</b> compares to the market. <b>Ke</b> is the minimum return required for the sector's risk.",
        "aval_subvalorizado": "The DDM model suggests a potentially undervalued share.",
        "aval_sobrevalorizado": "The DDM model suggests a potentially overvalued share.",
        "aval_justo": "The DDM model suggests the market price is close to the estimated value.",
        "aval_ddm_caption": "DDM/Gordon Growth: Fair Value = D1 ÷ (Ke − g). Use as a cross-check, never in isolation.",
        "aval_premium_titulo": "⭐ In-depth Analysis (Premium)",
        "aval_premium_lock": "<div class='appo-premium-lock'><strong>This section is exclusive to Premium members.</strong><br/>Sector comparison, sensitivity, ROE and real Dividend Yield.<br/><br/>Contact an administrator to activate Premium.</div>",
        "aval_roe": "ROE", "aval_payout": "Payout", "aval_dy_real": "Real Dividend Yield",
        "aval_nota3": "<b>ROE</b> = return on equity. <b>Payout</b> = share of profit distributed. <b>Real DY</b> = yield net of inflation.",
        "aval_sensibilidade": "##### Sensitivity Table — Fair Value (Kz per share)",
        "aval_comparacao": "##### Sector Comparison (all companies)",
        "aval_comp_cols": {"Empresa": "Company", "Sector": "Sector", "P/E": "P/E", "P/BV": "P/BV", "ROE": "ROE", "DY Nominal": "Nominal DY", "Upside DDM": "DDM Upside"},
        "aval_descarregar_comp": "⬇️ Download sector comparison as CSV",
        "aval_sem_dados": "No valuations recorded yet.",
        "conv_hero_sub": "Automatic exchange rates, updated daily, with the Kwanza included",
        "conv_de": "From", "conv_para": "To", "conv_valor": "Amount",
        "conv_equivale": "is equivalent to",
        "conv_taxa": "Rate:",
        "conv_actualizado": "Updated:",
        "conv_erro": "This currency is not available in the data source at the moment.",
        "conv_aviso": "Could not fetch exchange rates at this moment. Please try again shortly.",
        "conv_tabela_titulo": "Quick table (from 1 Kz)",
        "conv_tabela_col": "1 Kz equals",
        "conv_tabela_indisponivel": "Table unavailable at the moment.",
        "conv_historico_titulo": "📈 Kwanza Trend (own history, accumulated automatically)",
        "conv_historico_select": "Show trend for",
        "conv_historico_label": "1 AOA in",
        "conv_historico_info": "Not enough days of history yet. Come back on different days to watch the trend build itself.",
        "conv_historico_caption": "This history is built automatically by the app — without anyone entering anything — each time someone opens this page on a new day.",
        "sim_hero_sub": "Project the growth of your investment over time using compound interest",
        "sim_valor_inicial": "Initial amount (Kz)",
        "sim_contrib_mensal": "Monthly contribution (Kz)",
        "sim_taxa": "Expected annual return rate (%)",
        "sim_anos": "Time horizon (years)",
        "sim_inflacao": "Assumed annual inflation (%)",
        "sim_saldo_nominal": "Final Balance (nominal)",
        "sim_total_investido": "Total Invested",
        "sim_juros": "Compound Interest Earned",
        "sim_chart_cols": {"Saldo Nominal": "Nominal Balance", "Total Investido": "Total Invested"},
        "sim_caption1": "Final balance in today's purchasing power (discounting assumed inflation of",
        "sim_caption2": "%/year):",
        "sim_disclaimer": "Educational simulation with constant monthly compound interest — real market returns vary and are not guaranteed. This is not investment advice.",
        "sim_partilha": "I simulated {vi} + {cm}/month for {a} years at {t}%/year = {sf} — APPO Investment Club",
        "r50_hero_sub": "Principle #8: 50% Spending · 30% Investing · 20% Saving",
        "r50_rendimento": "Total monthly income (Kz)",
        "r50_alocacao": "Recommended allocation",
        "r50_consumo": "Spending (50%)", "r50_investimento": "Investing (30%)", "r50_entesouramento": "Saving (20%)",
        "r50_comparar_titulo": "Compare with your actual spending (optional)",
        "r50_real_consumo": "Actual spending — Consumption (Kz)",
        "r50_real_investimento": "Actual spending — Investment (Kz)",
        "r50_real_entesouramento": "Actual saving (Kz)",
        "r50_comparar_btn": "Compare",
        "r50_resultado": "#### Comparison result",
        "r50_aviso": "Your actual saving is below the 20% recommended by the Club's principle.",
        "r50_sucesso": "You are meeting, or exceeding, the 20% saving target.",
        "bib_hero_sub": "Club principles and articles on the Angolan capital market",
        "bib_sem_artigos": "No articles published yet.",
        "bib_filtrar": "Filter by category",
        "bib_todas": "All",
        "bib_publicado": "Published on",
        "ades_hero_sub": "Fill in the form to apply for membership of the APPO Investment Club",
        "ades_nome": "Full name *",
        "ades_email": "E-mail",
        "ades_telefone": "Phone / WhatsApp",
        "ades_bi": "Identity Card number",
        "ades_contribuicao": "Intended initial contribution (Kz)",
        "ades_aceite": "I declare that I have read and accepted the Bylaws of the APPO Investment Club *",
        "ades_btn": "Submit membership application",
        "ades_erro": "Please fill in the full name and accept the Bylaws to submit the application.",
        "ades_sucesso": "Membership application submitted successfully! A Club administrator will be in touch.",
        "sobre_hero_sub": "The mission, principles and statutory framework of the Club",
        "sobre_quem_somos": "Who we are",
        "sobre_quem_texto": "The **APPO Investment Club** is an association of Angolan investors that pools capital collectively to invest in the national capital market through the Angola Debt and Securities Exchange (BODIVA).",
        "sobre_principios": "Investment Principles and Philosophy",
        "sobre_estatutos": "Bylaws — key points",
        "sobre_estatutos_texto": """
- **Nature:** investor association, under formally registered Bylaws.
- **Governing bodies:** Members' Assembly, Management Committee and Supervisory Board.
- **Membership:** subject to approval by the Management Committee.
- **Resolutions:** significant investment decisions require collective deliberation.
- **Profit distribution:** proportional to each member's capital share.
""",
        "sobre_nota": "Internal note: reference model, to be replaced by the Club's formally approved and registered Bylaws.",
        "partilha_wa": "💬 WhatsApp", "partilha_tw": "𝕏 X / Twitter", "partilha_fb": "📘 Facebook",
        "conv_partilha": "{v} {de} = {r} {para} — APPO Investment Club",
        "pdf_titulo": "APPO Investment Club",
        "pdf_gerado": "Report generated on",
        "pdf_resumo": "Balance Sheet Summary",
        "pdf_subscrito": "Subscribed Capital:",
        "pdf_realizado": "Paid-up Capital:",
        "pdf_investimentos": "Investments:",
        "pdf_reservas": "Reserves:",
        "pdf_total": "Total:",
        "pdf_activos": "Portfolio Assets",
        "pdf_movimentos": "Recent Transactions",
        "pdf_sem_mov": "No transactions recorded.",
        "pdf_nome_ficheiro": "appo_report_{data}.pdf",
        "bodiva_badge": "🇦🇴 Mercado angolano · Kwanzas (Kz)",
    },

    # ─────────────────────────────────────────────────────
    "Français": {
        "tagline": "APPO — Éducation financière et espace privé d'investissement",
        "login_titulo": "Accès réservé aux membres",
        "email": "E-mail", "password": "Mot de passe", "entrar": "Se connecter",
        "erro_login": "E-mail ou mot de passe incorrect. Contactez un administrateur du Club.",
        "sessao": "Session", "terminar_sessao": "Se déconnecter",
        "nav_map": {
            "🏠 Início & Análises":         "🏠 Accueil & Analyses",
            "📈 Cotações & Activos":         "📈 Cotations & Actifs",
            "💰 Contabilidade & Finanças":  "💰 Comptabilité & Finances",
            "📊 Histórico & Relatórios":    "📊 Historique & Rapports",
            "📐 Avaliação de Activos":       "📐 Évaluation des Actifs",
            "💱 Conversor de Moeda":         "💱 Convertisseur de Devises",
            "🧪 Simulador de Investimento": "🧪 Simulateur d'Investissement",
            "🧮 Princípio 50/30/20":            "🧮 Règle 50/30/20",
            "📚 Biblioteca Educativa":       "📚 Bibliothèque Éducative",
            "🧾 Adesão de Sócios":          "🧾 Manifestation d'intérêt",
            "ℹ️ Sobre Nós & Estatutos":     "ℹ️ À propos & Statuts",
            "🔐 Painel do Administrador":   "🔐 Panneau d'Administration",
        },
        "inicio_hero_sub": "APPO — Éducation financière et espace privé d'investissement",
        "inicio_capital_subscrito": "Capital Souscrit",
        "inicio_capital_realizado": "Capital Libéré",
        "inicio_pct_subscrito": "% du souscrit",
        "inicio_investimentos": "Investissements",
        "inicio_reservas": "Réserves",
        "inicio_patrimonio_total": "Actif Net Total",
        "inicio_indice_label": "📊 Indice APPO (moyenne des actions cotées)",
        "inicio_indice_caption": "Comment un portefeuille investi à parts égales dans toutes les actions suivies par le Club aurait évolué.",
        "inicio_distribuicao": "Répartition du Patrimoine",
        "inicio_distribuicao_cats": ["Capital Libéré", "Investissements", "Réserves"],
        "inicio_cotacoes_destaque": "📌 Cotations en vedette",
        "inicio_capa_texto": "Discipline, transparence et vision à long terme",
        "cot_hero_sub": "Instruments financiers cotés à la BODIVA suivis par le Club",
        "cot_indice_titulo": "📊 Indice APPO — cotation moyenne du marché",
        "cot_indice_metric": "Variation moyenne aujourd'hui",
        "cot_indice_caption": "Si vous aviez investi à parts égales dans toutes les actions cotées suivies par le Club, votre portefeuille aurait varié en moyenne de cette valeur.",
        "cot_indice_hist_label": "Indice APPO — journalier (%)",
        "cot_indice_hist_info": "L'historique journalier de l'Indice APPO se constitue chaque jour où l'administrateur met à jour les cotations.",
        "cot_tendencia_semanal": "##### Tendance hebdomadaire de l'Indice APPO",
        "cot_tendencia_sem_caption1": "Pas encore assez de semaines d'historique pour afficher la tendance hebdomadaire.",
        "cot_tendencia_sem_caption2": "Pas encore assez d'historique pour la vue hebdomadaire.",
        "cot_tab_favoritos": "⭐ Favoris",
        "cot_tab_todos": "📋 Tous les Actifs",
        "cot_fav_escolher": "Choisir vos actifs favoris",
        "cot_fav_info": "Vous n'avez pas encore marqué d'actif comme favori. Utilisez la liste ci-dessus.",
        "cot_filtrar_tipo": "Filtrer par type d'actif",
        "cot_filtrar_todos": "Tous",
        "cot_ultima_actualizacao": "Dernière mise à jour :",
        "cot_descarregar_csv": "⬇️ Télécharger le tableau en CSV",
        "cot_comparacao": "Comparaison des prix",
        "cot_preco_kz": "Prix (Kz)",
        "cot_tabela_cols": {"ticker": "Ticker", "nome": "Actif", "tipo": "Type", "preco": "Prix", "variacao": "Variation", "mercado": "Marché"},
        "cont_hero_sub": "Résumé Comptable et Patrimonial du Club",
        "cont_df_cols": ["Catégorie", "Description", "Montant", "Devise"],
        "cont_df_rows": [
            ("Capital Souscrit",   "Total du capital engagé par les membres",                      "AOA"),
            ("Capital Libéré",     "Partie du capital souscrit déjà effectivement versée",         "AOA"),
            ("Investissements",    "Portefeuille d'actions et instruments financiers cotés BODIVA", "AOA"),
            ("Réserves",           "Fonds de stabilisation et de liquidité pour nouvelles opportunités","AOA"),
        ],
        "cont_patrimonio_metric": "Actif Net Total du Club",
        "cont_ultima_actualizacao": "Dernière mise à jour :",
        "hist_hero_sub": "Évolution du patrimoine du Club dans le temps et exports de rapports",
        "hist_poucos_pontos": "Pas encore assez de points de données. Ce graphique se précisera avec le temps.",
        "hist_caption": "Chaque point représente une mise à jour du bilan. Axe vertical en Kwanzas (Kz).",
        "hist_patrimonio_label": "Actif Net Total (Kz)",
        "hist_movimentos": "Transactions enregistrées",
        "hist_sem_movimentos": "Aucune transaction enregistrée pour l'instant.",
        "hist_cols": {"tipo": "Type", "descricao": "Description", "montante_fmt": "Montant", "data_movimento": "Date", "criado_em": "Enregistré le"},
        "hist_descarregar_mov": "⬇️ Télécharger les transactions en CSV",
        "hist_exportar": "Exporter le rapport",
        "hist_gerar_pdf": "Générer un rapport PDF",
        "hist_descarregar_pdf": "Télécharger le rapport PDF",
        "aval_hero_sub": "Multiples et juste valeur (DDM) des sociétés cotées, avec données réelles du Club",
        "aval_empresa": "Société",
        "aval_sector": "Secteur",
        "aval_cap_mercado": "Capitalisation boursière :",
        "aval_preco": "Prix Actuel",
        "aval_pe": "P/E", "aval_pbv": "P/VNC", "aval_dy": "Rendement du dividende",
        "aval_nota1": "<b>P/E</b> = années de bénéfices payés. <b>P/VNC</b> = prix vs valeur comptable. <b>Rendement du dividende</b> = retour annuel en dividendes.",
        "aval_vj": "Juste Valeur (DDM)", "aval_upside": "Potentiel / Risque", "aval_ke": "Coût des Fonds Propres (Ke)",
        "aval_nota2": "<b>Juste Valeur (DDM)</b> est une estimation. <b>Potentiel/Risque</b> compare au marché. <b>Ke</b> = rendement minimum exigé selon le risque du secteur.",
        "aval_subvalorizado": "Le modèle DDM suggère une action potentiellement sous-évaluée.",
        "aval_sobrevalorizado": "Le modèle DDM suggère une action potentiellement surévaluée.",
        "aval_justo": "Le modèle DDM suggère que le prix de marché est proche de la valeur estimée.",
        "aval_ddm_caption": "DDM/Gordon Growth : Juste Valeur = D1 ÷ (Ke − g). À utiliser comme vérification croisée, jamais isolément.",
        "aval_premium_titulo": "⭐ Analyse Approfondie (Premium)",
        "aval_premium_lock": "<div class='appo-premium-lock'><strong>Cette section est réservée aux membres Premium.</strong><br/>Comparaison sectorielle, sensibilité, ROE et rendement réel.<br/><br/>Contactez un administrateur pour activer le Premium.</div>",
        "aval_roe": "ROE", "aval_payout": "Taux de distribution", "aval_dy_real": "Rendement Réel",
        "aval_nota3": "<b>ROE</b> = rentabilité des fonds propres. <b>Taux de distribution</b> = part du bénéfice distribuée. <b>Rendement Réel</b> = rendement net d'inflation.",
        "aval_sensibilidade": "##### Tableau de Sensibilité — Juste Valeur (Kz par action)",
        "aval_comparacao": "##### Comparaison Sectorielle (toutes les sociétés)",
        "aval_comp_cols": {"Empresa": "Société", "Sector": "Secteur", "P/E": "P/E", "P/BV": "P/VNC", "ROE": "ROE", "DY Nominal": "Rendement Nominal", "Upside DDM": "Potentiel DDM"},
        "aval_descarregar_comp": "⬇️ Télécharger la comparaison sectorielle en CSV",
        "aval_sem_dados": "Aucune évaluation enregistrée pour l'instant.",
        "conv_hero_sub": "Taux de change automatiques, mis à jour quotidiennement, avec le Kwanza inclus",
        "conv_de": "De", "conv_para": "Vers", "conv_valor": "Montant",
        "conv_equivale": "équivaut à",
        "conv_taxa": "Taux :",
        "conv_actualizado": "Mis à jour :",
        "conv_erro": "Cette devise n'est pas disponible dans la source de données pour le moment.",
        "conv_aviso": "Impossible d'obtenir les taux de change pour le moment. Réessayez dans quelques instants.",
        "conv_tabela_titulo": "Tableau rapide (à partir de 1 Kz)",
        "conv_tabela_col": "1 Kz équivaut à",
        "conv_tabela_indisponivel": "Tableau indisponible pour le moment.",
        "conv_historico_titulo": "📈 Tendance du Kwanza (historique propre, accumulé automatiquement)",
        "conv_historico_select": "Afficher la tendance pour",
        "conv_historico_label": "1 AOA en",
        "conv_historico_info": "Pas encore assez de jours d'historique. Revenez à différentes dates pour voir la tendance se former.",
        "conv_historico_caption": "Cet historique est constitué automatiquement par l'application — sans aucune saisie manuelle — chaque fois que quelqu'un ouvre cette page un nouveau jour.",
        "sim_hero_sub": "Projetez la croissance de votre investissement dans le temps avec les intérêts composés",
        "sim_valor_inicial": "Montant initial (Kz)",
        "sim_contrib_mensal": "Contribution mensuelle (Kz)",
        "sim_taxa": "Taux de rendement annuel attendu (%)",
        "sim_anos": "Horizon (années)",
        "sim_inflacao": "Inflation annuelle supposée (%)",
        "sim_saldo_nominal": "Solde Final (nominal)",
        "sim_total_investido": "Total Investi",
        "sim_juros": "Intérêts Composés Gagnés",
        "sim_chart_cols": {"Saldo Nominal": "Solde Nominal", "Total Investido": "Total Investi"},
        "sim_caption1": "Solde final en pouvoir d'achat d'aujourd'hui (inflation supposée de",
        "sim_caption2": "%/an) :",
        "sim_disclaimer": "Simulation éducative avec intérêts composés mensuels constants — les rendements réels varient et ne sont pas garantis. Ne constitue pas un conseil en investissement.",
        "sim_partilha": "J'ai simulé {vi} + {cm}/mois pendant {a} ans à {t}%/an = {sf} — Club d'Investissement APPO",
        "r50_hero_sub": "Principe n°8 : 50% Dépenses · 30% Investissement · 20% Épargne",
        "r50_rendimento": "Revenu mensuel total (Kz)",
        "r50_alocacao": "Allocation recommandée",
        "r50_consumo": "Dépenses (50%)", "r50_investimento": "Investissement (30%)", "r50_entesouramento": "Épargne (20%)",
        "r50_comparar_titulo": "Comparez avec vos dépenses réelles (optionnel)",
        "r50_real_consumo": "Dépenses réelles — Consommation (Kz)",
        "r50_real_investimento": "Dépenses réelles — Investissement (Kz)",
        "r50_real_entesouramento": "Épargne réelle (Kz)",
        "r50_comparar_btn": "Comparer",
        "r50_resultado": "#### Résultat de la comparaison",
        "r50_aviso": "Votre épargne réelle est inférieure aux 20% recommandés par le principe du Club.",
        "r50_sucesso": "Vous respectez, ou dépassez, l'objectif d'épargne de 20%.",
        "bib_hero_sub": "Principes du Club et articles sur le marché des capitaux angolais",
        "bib_sem_artigos": "Aucun article publié pour l'instant.",
        "bib_filtrar": "Filtrer par catégorie",
        "bib_todas": "Toutes",
        "bib_publicado": "Publié le",
        "ades_hero_sub": "Remplissez le formulaire pour demander votre adhésion au Club d'Investissement APPO",
        "ades_nome": "Nom complet *",
        "ades_email": "E-mail",
        "ades_telefone": "Téléphone / WhatsApp",
        "ades_bi": "Numéro de carte d'identité",
        "ades_contribuicao": "Contribution initiale souhaitée (Kz)",
        "ades_aceite": "Je déclare avoir lu et accepté les Statuts du Club d'Investissement APPO *",
        "ades_btn": "Soumettre la demande d'adhésion",
        "ades_erro": "Veuillez saisir votre nom complet et accepter les Statuts pour soumettre la demande.",
        "ades_sucesso": "Demande d'adhésion soumise avec succès ! Un administrateur du Club vous contactera.",
        "sobre_hero_sub": "La mission, les principes et le cadre statutaire du Club",
        "sobre_quem_somos": "Qui sommes-nous",
        "sobre_quem_texto": "Le **Club d'Investissement APPO** est une association d'investisseurs angolais qui met en commun des capitaux pour investir sur le marché des capitaux national via la Bourse angolaise (BODIVA).",
        "sobre_principios": "Principes et Philosophie d'Investissement",
        "sobre_estatutos": "Statuts — points clés",
        "sobre_estatutos_texto": """
- **Nature :** association d'investisseurs, régie par des Statuts formellement enregistrés.
- **Organes :** Assemblée des Membres, Commission de Gestion et Conseil de Surveillance.
- **Admission :** soumise à l'approbation de la Commission de Gestion.
- **Délibérations :** les décisions d'investissement importantes requièrent une délibération collective.
- **Répartition des résultats :** proportionnelle à la quote-part de capital de chaque membre.
""",
        "sobre_nota": "Note interne : modèle de référence, à remplacer par les Statuts formellement approuvés et enregistrés du Club.",
        "partilha_wa": "💬 WhatsApp", "partilha_tw": "𝕏 X / Twitter", "partilha_fb": "📘 Facebook",
        "conv_partilha": "{v} {de} = {r} {para} — Club d'Investissement APPO",
        "pdf_titulo": "Club d'Investissement APPO",
        "pdf_gerado": "Rapport généré le",
        "pdf_resumo": "Résumé du Bilan",
        "pdf_subscrito": "Capital Souscrit :",
        "pdf_realizado": "Capital Libéré :",
        "pdf_investimentos": "Investissements :",
        "pdf_reservas": "Réserves :",
        "pdf_total": "Total :",
        "pdf_activos": "Actifs en Portefeuille",
        "pdf_movimentos": "Transactions Récentes",
        "pdf_sem_mov": "Aucune transaction enregistrée.",
        "pdf_nome_ficheiro": "rapport_appo_{data}.pdf",
        "bodiva_badge": "🇦🇴 Mercado angolano · Kwanzas (Kz)",
    },

    # ─────────────────────────────────────────────────────
    "Español": {
        "tagline": "APPO — Educación financiera y área privada de inversiones",
        "login_titulo": "Acceso reservado a socios",
        "email": "Correo electrónico", "password": "Contraseña", "entrar": "Entrar",
        "erro_login": "Correo o contraseña incorrectos. Contacta a un administrador del Club.",
        "sessao": "Sesión", "terminar_sessao": "Cerrar sesión",
        "nav_map": {
            "🏠 Início & Análises":         "🏠 Inicio y Análisis",
            "📈 Cotações & Activos":         "📈 Cotizaciones y Activos",
            "💰 Contabilidade & Finanças":  "💰 Contabilidad y Finanzas",
            "📊 Histórico & Relatórios":    "📊 Historial e Informes",
            "📐 Avaliação de Activos":       "📐 Valoración de Activos",
            "💱 Conversor de Moeda":         "💱 Conversor de Moneda",
            "🧪 Simulador de Investimento": "🧪 Simulador de Inversión",
            "🧮 Princípio 50/30/20":            "🧮 Regla 50/30/20",
            "📚 Biblioteca Educativa":       "📚 Biblioteca Educativa",
            "🧾 Adesão de Sócios":          "🧾 Manifestación de interés",
            "ℹ️ Sobre Nós & Estatutos":     "ℹ️ Sobre Nosotros y Estatutos",
            "🔐 Painel do Administrador":   "🔐 Panel de Administrador",
        },
        "inicio_hero_sub": "APPO — Educación financiera y área privada de inversiones",
        "inicio_capital_subscrito": "Capital Suscrito",
        "inicio_capital_realizado": "Capital Desembolsado",
        "inicio_pct_subscrito": "% del suscrito",
        "inicio_investimentos": "Inversiones",
        "inicio_reservas": "Reservas",
        "inicio_patrimonio_total": "Patrimonio Neto Total",
        "inicio_indice_label": "📊 Índice APPO (media de acciones cotizadas)",
        "inicio_indice_caption": "Cómo habría evolucionado una cartera invertida a partes iguales en todas las acciones seguidas por el Club.",
        "inicio_distribuicao": "Distribución del Patrimonio",
        "inicio_distribuicao_cats": ["Capital Desembolsado", "Inversiones", "Reservas"],
        "inicio_cotacoes_destaque": "📌 Cotizaciones destacadas",
        "inicio_capa_texto": "Disciplina, transparencia y visión a largo plazo",
        "cot_hero_sub": "Instrumentos financieros cotizados en BODIVA seguidos por el Club",
        "cot_indice_titulo": "📊 Índice APPO — cotización media del mercado",
        "cot_indice_metric": "Variación media hoy",
        "cot_indice_caption": "Si hubieras invertido a partes iguales en todas las acciones cotizadas del Club, tu cartera habría variado, en promedio, este valor.",
        "cot_indice_hist_label": "Índice APPO — diario (%)",
        "cot_indice_hist_info": "El historial diario del Índice APPO se va formando cada día que el administrador actualiza las cotizaciones.",
        "cot_tendencia_semanal": "##### Tendencia semanal del Índice APPO",
        "cot_tendencia_sem_caption1": "Aún no hay suficientes semanas de historial para mostrar la tendencia semanal.",
        "cot_tendencia_sem_caption2": "Aún no hay historial suficiente para la vista semanal.",
        "cot_tab_favoritos": "⭐ Favoritos",
        "cot_tab_todos": "📋 Todos los Activos",
        "cot_fav_escolher": "Elige tus activos favoritos",
        "cot_fav_info": "Aún no has marcado ningún activo como favorito. Usa la lista de arriba.",
        "cot_filtrar_tipo": "Filtrar por tipo de activo",
        "cot_filtrar_todos": "Todos",
        "cot_ultima_actualizacao": "Última actualización:",
        "cot_descarregar_csv": "⬇️ Descargar tabla en CSV",
        "cot_comparacao": "Comparación de precios",
        "cot_preco_kz": "Precio (Kz)",
        "cot_tabela_cols": {"ticker": "Ticker", "nome": "Activo", "tipo": "Tipo", "preco": "Precio", "variacao": "Variación", "mercado": "Mercado"},
        "cont_hero_sub": "Resumen Contable y Patrimonial del Club",
        "cont_df_cols": ["Categoría", "Descripción", "Importe", "Divisa"],
        "cont_df_rows": [
            ("Capital Suscrito",      "Total de capital comprometido por los socios",               "AOA"),
            ("Capital Desembolsado",  "Parte del capital suscrito ya efectivamente pagada",         "AOA"),
            ("Inversiones",           "Cartera de acciones e instrumentos financieros en BODIVA",   "AOA"),
            ("Reservas",              "Fondo de estabilización y liquidez para nuevas oportunidades","AOA"),
        ],
        "cont_patrimonio_metric": "Patrimonio Neto Total del Club",
        "cont_ultima_actualizacao": "Última actualización:",
        "hist_hero_sub": "Evolución del patrimonio del Club a lo largo del tiempo y exportación de informes",
        "hist_poucos_pontos": "Aún hay pocos puntos de datos. Este gráfico irá tomando forma con el tiempo.",
        "hist_caption": "Cada punto representa una actualización del balance. Eje vertical en Kwanzas (Kz).",
        "hist_patrimonio_label": "Patrimonio Neto Total (Kz)",
        "hist_movimentos": "Transacciones registradas",
        "hist_sem_movimentos": "Aún no hay transacciones registradas.",
        "hist_cols": {"tipo": "Tipo", "descricao": "Descripción", "montante_fmt": "Importe", "data_movimento": "Fecha", "criado_em": "Registrado el"},
        "hist_descarregar_mov": "⬇️ Descargar transacciones en CSV",
        "hist_exportar": "Exportar informe",
        "hist_gerar_pdf": "Generar informe PDF",
        "hist_descarregar_pdf": "Descargar informe PDF",
        "aval_hero_sub": "Múltiplos y valor razonable (DDM) de las empresas cotizadas, con datos reales del Club",
        "aval_empresa": "Empresa",
        "aval_sector": "Sector",
        "aval_cap_mercado": "Capitalización de mercado:",
        "aval_preco": "Precio Actual",
        "aval_pe": "P/E", "aval_pbv": "P/VC", "aval_dy": "Rentabilidad por dividendo",
        "aval_nota1": "<b>P/E</b> = años de beneficio que pagas. <b>P/VC</b> = precio vs valor contable. <b>Rentabilidad por dividendo</b> = retorno anual en dividendos.",
        "aval_vj": "Valor Razonable (DDM)", "aval_upside": "Potencial / Riesgo", "aval_ke": "Coste del Capital (Ke)",
        "aval_nota2": "<b>Valor Razonable (DDM)</b> es una estimación. <b>Potencial/Riesgo</b> compara con el mercado. <b>Ke</b> = retorno mínimo exigido por el riesgo del sector.",
        "aval_subvalorizado": "El modelo DDM sugiere una acción potencialmente infravalorada.",
        "aval_sobrevalorizado": "El modelo DDM sugiere una acción potencialmente sobrevalorada.",
        "aval_justo": "El modelo DDM sugiere que el precio de mercado está próximo al valor estimado.",
        "aval_ddm_caption": "DDM/Gordon Growth: Valor Razonable = D1 ÷ (Ke − g). Usar como verificación cruzada, nunca de forma aislada.",
        "aval_premium_titulo": "⭐ Análisis Profundo (Premium)",
        "aval_premium_lock": "<div class='appo-premium-lock'><strong>Esta sección es exclusiva para socios Premium.</strong><br/>Comparación sectorial, sensibilidad, ROE y rentabilidad real.<br/><br/>Habla con un administrador para activar el Premium.</div>",
        "aval_roe": "ROE", "aval_payout": "Tasa de distribución", "aval_dy_real": "Rentabilidad Real",
        "aval_nota3": "<b>ROE</b> = rentabilidad sobre fondos propios. <b>Tasa de distribución</b> = fracción del beneficio distribuida. <b>Rentabilidad Real</b> = yield descontado de la inflación.",
        "aval_sensibilidade": "##### Tabla de Sensibilidad — Valor Razonable (Kz por acción)",
        "aval_comparacao": "##### Comparación Sectorial (todas las empresas)",
        "aval_comp_cols": {"Empresa": "Empresa", "Sector": "Sector", "P/E": "P/E", "P/BV": "P/VC", "ROE": "ROE", "DY Nominal": "Rentab. Nominal", "Upside DDM": "Potencial DDM"},
        "aval_descarregar_comp": "⬇️ Descargar comparación sectorial en CSV",
        "aval_sem_dados": "Aún no hay valoraciones registradas.",
        "conv_hero_sub": "Tipos de cambio automáticos, actualizados diariamente, con el Kwanza incluido",
        "conv_de": "De", "conv_para": "A", "conv_valor": "Importe",
        "conv_equivale": "equivale a",
        "conv_taxa": "Tipo:",
        "conv_actualizado": "Actualizado:",
        "conv_erro": "Esta divisa no está disponible en la fuente de datos en este momento.",
        "conv_aviso": "No se pudieron obtener los tipos de cambio en este momento. Inténtalo de nuevo en unos instantes.",
        "conv_tabela_titulo": "Tabla rápida (a partir de 1 Kz)",
        "conv_tabela_col": "1 Kz equivale a",
        "conv_tabela_indisponivel": "Tabla no disponible en este momento.",
        "conv_historico_titulo": "📈 Tendencia del Kwanza (historial propio, acumulado automáticamente)",
        "conv_historico_select": "Ver tendencia de",
        "conv_historico_label": "1 AOA en",
        "conv_historico_info": "Aún hay pocos días de historial acumulado. Vuelve en días diferentes para ver cómo se va formando la tendencia.",
        "conv_historico_caption": "Este historial se construye automáticamente por la propia app — sin que nadie tenga que introducir nada — cada vez que alguien abre esta página un nuevo día.",
        "sim_hero_sub": "Proyecta el crecimiento de tu inversión a lo largo del tiempo con interés compuesto",
        "sim_valor_inicial": "Importe inicial (Kz)",
        "sim_contrib_mensal": "Aportación mensual (Kz)",
        "sim_taxa": "Tasa de rentabilidad anual esperada (%)",
        "sim_anos": "Plazo (años)",
        "sim_inflacao": "Inflación anual supuesta (%)",
        "sim_saldo_nominal": "Saldo Final (nominal)",
        "sim_total_investido": "Total Invertido",
        "sim_juros": "Interés Compuesto Ganado",
        "sim_chart_cols": {"Saldo Nominal": "Saldo Nominal", "Total Investido": "Total Invertido"},
        "sim_caption1": "Saldo final en poder adquisitivo de hoy (descontando la inflación supuesta de",
        "sim_caption2": "%/año):",
        "sim_disclaimer": "Simulación educativa con interés compuesto mensual constante — los rendimientos reales del mercado varían y no están garantizados. No constituye asesoramiento de inversión.",
        "sim_partilha": "Simulé {vi} + {cm}/mes durante {a} años al {t}%/año = {sf} — Club de Inversión APPO",
        "r50_hero_sub": "Principio n.º 8: 50% Gastos · 30% Inversión · 20% Ahorro",
        "r50_rendimento": "Renta mensual total (Kz)",
        "r50_alocacao": "Asignación recomendada",
        "r50_consumo": "Gastos (50%)", "r50_investimento": "Inversión (30%)", "r50_entesouramento": "Ahorro (20%)",
        "r50_comparar_titulo": "Compara con tus gastos reales (opcional)",
        "r50_real_consumo": "Gasto real — Consumo (Kz)",
        "r50_real_investimento": "Gasto real — Inversión (Kz)",
        "r50_real_entesouramento": "Ahorro real (Kz)",
        "r50_comparar_btn": "Comparar",
        "r50_resultado": "#### Resultado de la comparación",
        "r50_aviso": "Tu ahorro real está por debajo del 20% recomendado por el principio del Club.",
        "r50_sucesso": "Estás cumpliendo, o superando, el objetivo de ahorro del 20%.",
        "bib_hero_sub": "Principios del Club y artículos sobre el mercado de capitales angoleño",
        "bib_sem_artigos": "Aún no hay artículos publicados.",
        "bib_filtrar": "Filtrar por categoría",
        "bib_todas": "Todas",
        "bib_publicado": "Publicado el",
        "ades_hero_sub": "Completa el formulario para solicitar tu adhesión al Club de Inversión APPO",
        "ades_nome": "Nombre completo *",
        "ades_email": "Correo electrónico",
        "ades_telefone": "Teléfono / WhatsApp",
        "ades_bi": "Número del Documento de Identidad",
        "ades_contribuicao": "Aportación inicial prevista (Kz)",
        "ades_aceite": "Declaro que he leído y acepto los Estatutos del Club de Inversión APPO *",
        "ades_btn": "Enviar solicitud de adhesión",
        "ades_erro": "Rellena el nombre completo y acepta los Estatutos para enviar la solicitud.",
        "ades_sucesso": "¡Solicitud de adhesión enviada con éxito! Un administrador del Club se pondrá en contacto contigo.",
        "sobre_hero_sub": "La misión, los principios y el marco estatutario del Club",
        "sobre_quem_somos": "Quiénes somos",
        "sobre_quem_texto": "El **Club de Inversión APPO** es una asociación de inversores angoleños que reúne capital colectivamente para invertir en el mercado de capitales nacional a través de la Bolsa de Angola (BODIVA).",
        "sobre_principios": "Principios y Filosofía de Inversión",
        "sobre_estatutos": "Estatutos — puntos clave",
        "sobre_estatutos_texto": """
- **Naturaleza:** asociación de inversores, conforme a Estatutos formalmente registrados.
- **Órganos:** Asamblea de Socios, Comisión de Gestión y Consejo de Supervisión.
- **Admisión:** sujeta a aprobación de la Comisión de Gestión.
- **Deliberaciones:** las decisiones de inversión relevantes requieren deliberación colectiva.
- **Distribución de resultados:** proporcional a la cuota de capital de cada socio.
""",
        "sobre_nota": "Nota interna: modelo de referencia, a sustituir por los Estatutos formalmente aprobados y registrados del Club.",
        "partilha_wa": "💬 WhatsApp", "partilha_tw": "𝕏 X / Twitter", "partilha_fb": "📘 Facebook",
        "conv_partilha": "{v} {de} = {r} {para} — Club de Inversión APPO",
        "pdf_titulo": "Club de Inversión APPO",
        "pdf_gerado": "Informe generado el",
        "pdf_resumo": "Resumen del Balance",
        "pdf_subscrito": "Capital Suscrito:",
        "pdf_realizado": "Capital Desembolsado:",
        "pdf_investimentos": "Inversiones:",
        "pdf_reservas": "Reservas:",
        "pdf_total": "Total:",
        "pdf_activos": "Activos en Cartera",
        "pdf_movimentos": "Transacciones Recientes",
        "pdf_sem_mov": "Sin transacciones registradas.",
        "pdf_nome_ficheiro": "informe_appo_{data}.pdf",
        "bodiva_badge": "🇦🇴 Mercado angolano · Kwanzas (Kz)",
    },

    # ─────────────────────────────────────────────────────
    "中文 (Mandarim)": {
        "tagline": "APPO — 金融教育与私人投资专区",
        "login_titulo": "仅限会员访问",
        "email": "电子邮件", "password": "密码", "entrar": "登录",
        "erro_login": "邮箱或密码错误。请联系俱乐部管理员。",
        "sessao": "会话", "terminar_sessao": "退出登录",
        "nav_map": {
            "🏠 Início & Análises":         "🏠 首页与分析",
            "📈 Cotações & Activos":         "📈 行情与资产",
            "💰 Contabilidade & Finanças":  "💰 会计与财务",
            "📊 Histórico & Relatórios":    "📊 历史与报告",
            "📐 Avaliação de Activos":       "📐 资产估值",
            "💱 Conversor de Moeda":         "💱 货币换算器",
            "🧪 Simulador de Investimento": "🧪 投资模拟器",
            "🧮 Princípio 50/30/20":            "🧮 50/30/20法则",
            "📚 Biblioteca Educativa":       "📚 教育图书馆",
            "🧾 Adesão de Sócios":          "🧾 意向登记",
            "ℹ️ Sobre Nós & Estatutos":     "ℹ️ 关于我们与章程",
            "🔐 Painel do Administrador":   "🔐 管理员面板",
        },
        "inicio_hero_sub": "APPO — 金融教育与私人投资专区",
        "inicio_capital_subscrito": "认缴资本",
        "inicio_capital_realizado": "实缴资本",
        "inicio_pct_subscrito": "% 已认缴",
        "inicio_investimentos": "投资",
        "inicio_reservas": "储备",
        "inicio_patrimonio_total": "总净资产",
        "inicio_indice_label": "📊 APPO指数（上市股票均值）",
        "inicio_indice_caption": "若将资金平均投资于俱乐部跟踪的所有上市股票，组合的平均表现。",
        "inicio_distribuicao": "资产分布",
        "inicio_distribuicao_cats": ["实缴资本", "投资", "储备"],
        "inicio_cotacoes_destaque": "📌 重点行情",
        "inicio_capa_texto": "纪律、透明与长期视野",
        "cot_hero_sub": "俱乐部跟踪的BODIVA上市金融工具",
        "cot_indice_titulo": "📊 APPO指数 — 市场平均行情",
        "cot_indice_metric": "今日平均涨跌幅",
        "cot_indice_caption": "若等权重投资俱乐部跟踪的所有上市股票，组合平均涨跌幅即此值。",
        "cot_indice_hist_label": "APPO指数 — 日变动（%）",
        "cot_indice_hist_info": "管理员每次更新行情，日APPO指数历史数据便自动增加一个新点。",
        "cot_tendencia_semanal": "##### APPO指数周趋势",
        "cot_tendencia_sem_caption1": "历史数据不足两周，暂无法显示周趋势。",
        "cot_tendencia_sem_caption2": "历史数据不足，暂无法显示周视图。",
        "cot_tab_favoritos": "⭐ 自选",
        "cot_tab_todos": "📋 全部资产",
        "cot_fav_escolher": "选择您的自选资产",
        "cot_fav_info": "您尚未将任何资产设为自选。请使用上方列表。",
        "cot_filtrar_tipo": "按资产类型筛选",
        "cot_filtrar_todos": "全部",
        "cot_ultima_actualizacao": "最后更新：",
        "cot_descarregar_csv": "⬇️ 下载CSV表格",
        "cot_comparacao": "价格比较",
        "cot_preco_kz": "价格（Kz）",
        "cot_tabela_cols": {"ticker": "代码", "nome": "资产", "tipo": "类型", "preco": "价格", "variacao": "涨跌幅", "mercado": "市场"},
        "cont_hero_sub": "俱乐部会计与资产负债概览",
        "cont_df_cols": ["类别", "说明", "金额", "货币"],
        "cont_df_rows": [
            ("认缴资本", "成员承诺的总资本",           "AOA"),
            ("实缴资本", "已实际缴纳的认缴资本部分",   "AOA"),
            ("投资",     "BODIVA上市的股票与金融工具组合","AOA"),
            ("储备",     "稳定基金及新机会流动性基金", "AOA"),
        ],
        "cont_patrimonio_metric": "俱乐部总净资产",
        "cont_ultima_actualizacao": "最后更新：",
        "hist_hero_sub": "俱乐部资产随时间的变化及报告导出",
        "hist_poucos_pontos": "数据点尚少，图表将随时间逐步完善。",
        "hist_caption": "每个点代表一次资产负债更新。纵轴单位为宽扎（Kz）。",
        "hist_patrimonio_label": "总净资产（Kz）",
        "hist_movimentos": "已记录交易",
        "hist_sem_movimentos": "暂无交易记录。",
        "hist_cols": {"tipo": "类型", "descricao": "说明", "montante_fmt": "金额", "data_movimento": "日期", "criado_em": "记录时间"},
        "hist_descarregar_mov": "⬇️ 下载交易CSV",
        "hist_exportar": "导出报告",
        "hist_gerar_pdf": "生成PDF报告",
        "hist_descarregar_pdf": "下载PDF报告",
        "aval_hero_sub": "上市公司的市盈率倍数与公允价值（DDM），含俱乐部真实数据",
        "aval_empresa": "公司",
        "aval_sector": "行业",
        "aval_cap_mercado": "市值：",
        "aval_preco": "当前价格",
        "aval_pe": "市盈率", "aval_pbv": "市净率", "aval_dy": "股息收益率",
        "aval_nota1": "<b>市盈率</b> = 您为价格支付的盈利年数。<b>市净率</b> = 价格与账面价值之比。<b>股息收益率</b> = 年度股息回报。",
        "aval_vj": "公允价值（DDM）", "aval_upside": "上行/下行空间", "aval_ke": "权益成本（Ke）",
        "aval_nota2": "<b>公允价值（DDM）</b>为估算值。<b>上行/下行空间</b>与市场比较。<b>Ke</b> = 该行业风险所要求的最低回报。",
        "aval_subvalorizado": "DDM模型显示该股票可能被低估。",
        "aval_sobrevalorizado": "DDM模型显示该股票可能被高估。",
        "aval_justo": "DDM模型显示市场价格接近估算价值。",
        "aval_ddm_caption": "DDM/戈登增长模型：公允价值 = D1 ÷ (Ke − g)。仅作交叉验证，切勿单独使用。",
        "aval_premium_titulo": "⭐ 深度分析（高级会员）",
        "aval_premium_lock": "<div class='appo-premium-lock'><strong>本部分仅限高级会员使用。</strong><br/>行业比较、敏感性分析、ROE及实际股息收益率。<br/><br/>请联系管理员开通高级权限。</div>",
        "aval_roe": "净资产收益率", "aval_payout": "分红比率", "aval_dy_real": "实际股息收益率",
        "aval_nota3": "<b>净资产收益率</b> = 净利润/净资产。<b>分红比率</b> = 已分配利润比例。<b>实际股息收益率</b> = 扣除通胀后的收益率。",
        "aval_sensibilidade": "##### 敏感性分析表 — 公允价值（每股 Kz）",
        "aval_comparacao": "##### 行业对比（所有公司）",
        "aval_comp_cols": {"Empresa": "公司", "Sector": "行业", "P/E": "市盈率", "P/BV": "市净率", "ROE": "净资产收益率", "DY Nominal": "名义股息率", "Upside DDM": "DDM上行空间"},
        "aval_descarregar_comp": "⬇️ 下载行业对比CSV",
        "aval_sem_dados": "暂无估值记录。",
        "conv_hero_sub": "自动汇率，每日更新，含宽扎",
        "conv_de": "从", "conv_para": "至", "conv_valor": "金额",
        "conv_equivale": "等于",
        "conv_taxa": "汇率：",
        "conv_actualizado": "更新时间：",
        "conv_erro": "该货币暂时无法从数据源获取。",
        "conv_aviso": "暂时无法获取汇率，请稍后再试。",
        "conv_tabela_titulo": "快速换算表（以1宽扎为基准）",
        "conv_tabela_col": "1 Kz等于",
        "conv_tabela_indisponivel": "表格暂时不可用。",
        "conv_historico_titulo": "📈 宽扎走势（自有历史，自动积累）",
        "conv_historico_select": "显示走势货币",
        "conv_historico_label": "1 AOA兑",
        "conv_historico_info": "历史数据天数尚少，请在不同日期访问以观察走势自然形成。",
        "conv_historico_caption": "此历史数据由应用自动积累——无需任何人工录入——每当有人在新的一天打开本页时自动更新。",
        "sim_hero_sub": "利用复利预测您的投资随时间的增长",
        "sim_valor_inicial": "初始金额（Kz）",
        "sim_contrib_mensal": "每月供款（Kz）",
        "sim_taxa": "预期年化收益率（%）",
        "sim_anos": "投资期限（年）",
        "sim_inflacao": "假设年通胀率（%）",
        "sim_saldo_nominal": "最终余额（名义）",
        "sim_total_investido": "总投入",
        "sim_juros": "所得复利",
        "sim_chart_cols": {"Saldo Nominal": "名义余额", "Total Investido": "总投入"},
        "sim_caption1": "以今日购买力计算的最终余额（扣除假设通胀率",
        "sim_caption2": "%/年）：",
        "sim_disclaimer": "以固定月复利计算的教育性模拟——实际市场收益会变动且无法保证。本内容不构成投资建议。",
        "sim_partilha": "我模拟了 {vi} + {cm}/月，{a}年，年化{t}% = {sf} — APPO投资俱乐部",
        "r50_hero_sub": "第8条原则：50%消费 · 30%投资 · 20%储蓄",
        "r50_rendimento": "月总收入（Kz）",
        "r50_alocacao": "推荐分配",
        "r50_consumo": "消费（50%）", "r50_investimento": "投资（30%）", "r50_entesouramento": "储蓄（20%）",
        "r50_comparar_titulo": "与您的实际支出对比（可选）",
        "r50_real_consumo": "实际支出 — 消费（Kz）",
        "r50_real_investimento": "实际支出 — 投资（Kz）",
        "r50_real_entesouramento": "实际储蓄（Kz）",
        "r50_comparar_btn": "对比",
        "r50_resultado": "#### 对比结果",
        "r50_aviso": "您的实际储蓄低于俱乐部原则建议的20%。",
        "r50_sucesso": "您已达到或超过20%储蓄目标。",
        "bib_hero_sub": "俱乐部原则及安哥拉资本市场文章",
        "bib_sem_artigos": "暂无已发布文章。",
        "bib_filtrar": "按类别筛选",
        "bib_todas": "全部",
        "bib_publicado": "发布于",
        "ades_hero_sub": "填写表格申请加入APPO投资俱乐部",
        "ades_nome": "全名 *",
        "ades_email": "电子邮件",
        "ades_telefone": "电话 / WhatsApp",
        "ades_bi": "身份证号码",
        "ades_contribuicao": "拟初始供款（Kz）",
        "ades_aceite": "我声明已阅读并接受APPO投资俱乐部章程 *",
        "ades_btn": "提交入会申请",
        "ades_erro": "请填写全名并接受章程后再提交申请。",
        "ades_sucesso": "入会申请提交成功！俱乐部管理员将与您联系。",
        "sobre_hero_sub": "俱乐部的使命、原则及章程框架",
        "sobre_quem_somos": "关于我们",
        "sobre_quem_texto": "**APPO投资俱乐部**是一个安哥拉投资者协会，通过安哥拉债务与证券交易所（BODIVA）集体汇集资本，共同投资于国家资本市场。",
        "sobre_principios": "投资原则与理念",
        "sobre_estatutos": "章程 — 要点",
        "sobre_estatutos_texto": """
- **性质：** 依据正式注册章程成立的投资者协会。
- **管理机构：** 会员大会、管理委员会和监事会。
- **入会：** 须经管理委员会批准。
- **决议：** 重要投资决定须经集体审议。
- **收益分配：** 按各会员资本份额比例分配。
""",
        "sobre_nota": "内部说明：参考模板，待俱乐部正式批准注册章程后替换。",
        "partilha_wa": "💬 WhatsApp", "partilha_tw": "𝕏 X / Twitter", "partilha_fb": "📘 Facebook",
        "conv_partilha": "{v} {de} = {r} {para} — APPO投资俱乐部",
        "pdf_titulo": "APPO投资俱乐部",
        "pdf_gerado": "报告生成于",
        "pdf_resumo": "资产负债概览",
        "pdf_subscrito": "认缴资本：",
        "pdf_realizado": "实缴资本：",
        "pdf_investimentos": "投资：",
        "pdf_reservas": "储备：",
        "pdf_total": "合计：",
        "pdf_activos": "投资组合资产",
        "pdf_movimentos": "近期交易",
        "pdf_sem_mov": "暂无交易记录。",
        "pdf_nome_ficheiro": "appo_报告_{data}.pdf",
        "bodiva_badge": "🇦🇴 安哥拉市场 · 宽扎（Kz）",
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

CSS_APPO_BASE = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --appo-vinho: #7C1F3E;
  --appo-vinho-esc: #5E1830;
  --appo-navy: #1E293B;
  --appo-cinza: #F8FAFC;
  --appo-borda: #E2E8F0;
  --appo-suave: #64748B;
}

/* Tipografia corporativa (sem tocar nos ícones do Streamlit) */
.stApp, .stApp p, .stApp li, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp button, .stApp input, .stApp textarea, .stApp [data-baseweb="tab"], .stApp [data-testid="stMetricValue"],
.stApp [data-testid="stMetricLabel"], .stApp [data-testid="stCaptionContainer"] {
  font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
.stApp h1, .stApp h2, .stApp h3, .stApp h4 { color: var(--appo-navy); letter-spacing: -0.01em; font-weight: 700; }

[data-testid="stAppViewContainer"] { background: var(--appo-cinza); }
[data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid var(--appo-borda); }
[data-testid="stHeader"] { background: transparent; }

/* Botões e separadores */
button[kind="primary"], button[data-testid="stBaseButton-primary"] { background: var(--appo-vinho); border-color: var(--appo-vinho); color: #FFFFFF; font-weight: 600; }
button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover { background: var(--appo-vinho-esc); border-color: var(--appo-vinho-esc); color: #FFFFFF; }
button[data-baseweb="tab"][aria-selected="true"] { color: var(--appo-vinho); }
div[data-baseweb="tab-highlight"] { background-color: var(--appo-vinho); }

/* Indicadores: cartões limpos, sem gradientes nem sombras */
div[data-testid="stMetric"] { background: #FFFFFF; border: 1px solid var(--appo-borda); border-radius: 10px; padding: 14px 16px; }
div[data-testid="stMetricLabel"] { color: var(--appo-suave); font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; }
div[data-testid="stMetricValue"] { color: var(--appo-navy); font-weight: 700; font-variant-numeric: tabular-nums; }
div[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 12px; }

/* Cabeçalho de página */
.appo-hero { background: var(--appo-navy); color: #FFFFFF; border-left: 5px solid var(--appo-vinho); border-radius: 12px; padding: 22px 28px; margin-bottom: 18px; display: flex; align-items: center; gap: 18px; }
.appo-hero h1 { margin: 0; font-size: 1.55rem; line-height: 1.25; color: #FFFFFF; font-weight: 700; }
.appo-hero p { margin: 4px 0 0 0; color: #CBD5E1; font-size: 0.92rem; }
.appo-badge { display: inline-block; border: 1px solid #475569; color: #E2E8F0; padding: 2px 10px; border-radius: 999px; font-size: 0.72rem; margin-top: 10px; letter-spacing: 0.02em; }

/* Marca */
.appo-sidebar-header { display: flex; align-items: center; gap: 12px; margin-bottom: 4px; }
.appo-sidebar-sub { font-size: 0.66rem; color: var(--appo-suave); letter-spacing: 0.12em; text-transform: uppercase; margin: 0; }
.appo-sidebar-word { font-family: 'Inter', sans-serif; font-weight: 800; font-size: 1.4rem; letter-spacing: 0.18em; color: var(--appo-vinho); line-height: 1.1; margin-top: 2px; }
.appo-wordmark { font-family: 'Inter', sans-serif; font-weight: 800; letter-spacing: 0.22em; font-size: 2.6rem; color: var(--appo-vinho); text-align: center; margin-top: 4px; line-height: 1.1; }

/* Blocos de apoio */
.appo-premium-lock { background: #FFFFFF; border: 1px dashed var(--appo-vinho); border-radius: 10px; padding: 18px 20px; text-align: center; }
.appo-indicador-nota { background: #F1F5F9; border-radius: 8px; padding: 10px 14px; font-size: 0.85rem; color: #334155; margin: 6px 0 4px 0; }
.appo-categoria-banner { border-radius: 10px 10px 0 0; padding: 10px 18px; display: flex; align-items: center; gap: 12px; margin: -1rem -1rem 12px -1rem; }
.appo-categoria-banner span { color: #FFFFFF; font-weight: 700; letter-spacing: 0.06em; font-size: 0.74rem; text-transform: uppercase; }
.appo-capa { background: var(--appo-navy); border-left: 5px solid var(--appo-vinho); border-radius: 12px; margin-bottom: 18px; display: flex; align-items: center; }
.appo-capa span { color: #FFFFFF; font-weight: 600; padding: 16px 24px; font-size: 1.05rem; }
.appo-card { background: #FFFFFF; border: 1px solid var(--appo-borda); border-radius: 12px; padding: 16px 18px; }
.appo-kicker { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--appo-suave); font-weight: 600; }

/* Cotações em fita */
.appo-ticker-wrap { overflow: hidden; white-space: nowrap; background: #FFFFFF; border-top: 1px solid var(--appo-borda); border-bottom: 1px solid var(--appo-borda); padding: 8px 0; margin-bottom: 16px; }
.appo-ticker-move { display: inline-block; padding-left: 100%; animation: appo-scroll 135s linear infinite; font-family: 'Inter', sans-serif; font-variant-numeric: tabular-nums; font-size: 0.8rem; }
@keyframes appo-scroll { 0% { transform: translate(0,0); } 100% { transform: translate(-100%,0); } }

.appo-share a { text-decoration: none; color: #FFFFFF; padding: 6px 14px; border-radius: 8px; font-size: 0.82rem; font-weight: 600; }
"""


# ---------------------------------------------------------
# Camada visual executiva (fundos claros; gradientes roxo -> vermelho -> laranja; sombras suaves).
# É sempre aplicada DEPOIS do CSS base (e do appo.css, se existir), por isso prevalece.
# ---------------------------------------------------------
CSS_APPO_FINCITE = """
:root {
  --fx-roxo: #6D28D9; --fx-vermelho: #E11D48; --fx-laranja: #F97316; --fx-tinta: #1B1033;
  --fx-grad: linear-gradient(100deg, #6D28D9 0%, #E11D48 55%, #F97316 100%);
  --fx-sombra: 0 10px 30px rgba(76, 29, 149, 0.10);
  --fx-sombra-suave: 0 4px 14px rgba(27, 16, 51, 0.07);
}
[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(900px 380px at 100% -8%, rgba(249, 115, 22, 0.10), transparent 62%),
    radial-gradient(800px 360px at -8% 0%, rgba(109, 40, 217, 0.08), transparent 62%),
    #FBFAFE;
}
.stApp h1, .stApp h2, .stApp h3 { color: var(--fx-tinta); font-weight: 800; letter-spacing: -0.02em; }

/* Cabeçalho de página: claro, com barra e brilho em gradiente */
.appo-hero { position: relative; overflow: hidden; background: linear-gradient(120deg, #FFFFFF 0%, #F6F1FF 48%, #FFF1EA 100%);
  color: var(--fx-tinta); border: 1px solid #EEE7FA; border-left: 0; border-radius: 18px; padding: 24px 30px 24px 34px; box-shadow: var(--fx-sombra); }
.appo-hero::before { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 7px; background: linear-gradient(180deg, #6D28D9, #E11D48 55%, #F97316); }
.appo-hero::after { content: ""; position: absolute; right: -60px; top: -80px; width: 260px; height: 260px; border-radius: 50%;
  background: radial-gradient(circle, rgba(249, 115, 22, 0.22), rgba(225, 29, 72, 0.12) 45%, transparent 70%); pointer-events: none; }
.appo-hero h1 { background: var(--fx-grad); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; color: transparent;
  font-weight: 800; font-size: 1.75rem; letter-spacing: -0.02em; }
.appo-hero p { color: #475569; font-size: 0.95rem; }
.appo-badge { border: 1px solid #E4D4FB; color: #6D28D9; background: #FAF5FF; font-weight: 600; }
.appo-capa { background: linear-gradient(120deg, #FFFFFF, #F6F1FF 55%, #FFF1EA); border: 1px solid #EEE7FA; border-left: 6px solid var(--fx-vermelho); box-shadow: var(--fx-sombra-suave); }
.appo-capa span { color: var(--fx-tinta); }

/* Cartões e indicadores */
.appo-card, .fx-card { background: #FFFFFF; border: 1px solid #EFE9FA; border-radius: 18px; box-shadow: var(--fx-sombra-suave); padding: 18px 20px; }
div[data-testid="stMetric"] { border: 1px solid #EFE9FA; border-radius: 16px; box-shadow: var(--fx-sombra-suave); }
div[data-testid="stMetricValue"] { font-weight: 800; }
button[kind="primary"], button[data-testid="stBaseButton-primary"] { background: var(--fx-grad); border: 0; border-radius: 12px; }
button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover { filter: brightness(1.06); background: var(--fx-grad); border: 0; }
button[data-baseweb="tab"][aria-selected="true"] { color: var(--fx-roxo); }
div[data-baseweb="tab-highlight"] { background: var(--fx-grad); height: 3px; }

/* Faixas de estado e etiquetas */
.fx-estado { display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px; border-radius: 999px; font-size: 0.82rem; font-weight: 600; border: 1px solid #E5E7EB; background: #FFFFFF; }
.fx-estado.ok { color: #166534; border-color: #BBF7D0; background: #F0FDF4; }
.fx-estado.aviso { color: #9A3412; border-color: #FED7AA; background: #FFF7ED; }
.fx-estado.erro { color: #9F1239; border-color: #FECDD3; background: #FFF1F2; }
.fx-kicker { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.12em; font-weight: 700; color: var(--fx-roxo); }
.fx-titulo-secao { font-size: 1.5rem; font-weight: 800; letter-spacing: -0.02em; background: var(--fx-grad); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; margin: 4px 0 2px 0; }
.fx-aviso-membros { background: #FFFFFF; border: 1px solid #EFE9FA; border-left: 5px solid var(--fx-laranja); border-radius: 12px; padding: 10px 14px; font-size: 0.85rem; color: #334155; margin: 8px 0 12px 0; }

/* Biblioteca: dois níveis bem visíveis */
.fx-nivel { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 6px 0 18px 0; }
.fx-nivel-card { border-radius: 20px; padding: 22px 24px; box-shadow: var(--fx-sombra); position: relative; overflow: hidden; }
.fx-nivel-card .fx-nivel-kicker { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.14em; font-weight: 700; opacity: 0.85; }
.fx-nivel-card .fx-nivel-titulo { font-size: 1.7rem; font-weight: 800; letter-spacing: -0.02em; margin: 6px 0 6px 0; line-height: 1.15; }
.fx-nivel-card p { margin: 0 0 10px 0; font-size: 0.92rem; line-height: 1.45; }
.fx-nivel-card .fx-nivel-n { display: inline-block; font-size: 0.78rem; font-weight: 700; padding: 4px 12px; border-radius: 999px; }
.fx-nivel-ini { background: linear-gradient(135deg, #FFFFFF 0%, #F3F8FF 100%); border: 1px solid #DCE8FB; color: #1B1033; }
.fx-nivel-ini .fx-nivel-n { background: #E8F0FE; color: #1D4ED8; }
.fx-nivel-inv { background: linear-gradient(120deg, #6D28D9 0%, #E11D48 58%, #F97316 100%); color: #FFFFFF; }
.fx-nivel-inv .fx-nivel-n { background: rgba(255, 255, 255, 0.22); color: #FFFFFF; }
.fx-cta { background: linear-gradient(120deg, #FFF7ED, #FDF2F8 55%, #F5F3FF); border: 1px solid #F9D8C2; border-radius: 18px; padding: 18px 22px; margin: 10px 0; box-shadow: var(--fx-sombra-suave); }
.fx-cta b { font-size: 1.15rem; letter-spacing: -0.01em; }
@media (max-width: 760px) { .fx-nivel { grid-template-columns: 1fr; } .fx-nivel-card .fx-nivel-titulo { font-size: 1.35rem; } }
"""


# ---------------------------------------------------------
# Fase 1 — sistema visual: tipografia, cartões KPI, expansores, botões, serviços, páginas institucionais
# ---------------------------------------------------------
CSS_APPO_FASE1 = """
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .appo-hero h1, .fx-kpi-v, .fx-titulo-secao, .fx-nivel-titulo, .fx-servico-nome, .fx-bloco-titulo {
  font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, 'Segoe UI', sans-serif; }

/* Cartões de indicadores (compactos) */
.fx-kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(178px, 1fr)); gap: 12px; margin: 4px 0 14px 0; }
.fx-kpi { background: #FFFFFF; border: 1px solid #EFE9FA; border-radius: 14px; padding: 11px 14px 12px 14px; box-shadow: var(--fx-sombra-suave); }
.fx-kpi.destaque { background: linear-gradient(135deg, #FFFFFF, #F6F1FF 60%, #FFF1EA); border-color: #E4D4FB; }
.fx-kpi-topo { display: flex; align-items: center; gap: 8px; }
.fx-kpi-ico { width: 28px; height: 28px; border-radius: 9px; display: grid; place-items: center; font-size: 0.9rem;
  background: linear-gradient(135deg, #F3E8FF, #FFE4E6 60%, #FFEDD5); }
.fx-kpi-t { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.08em; color: #64748B; font-weight: 700; line-height: 1.2; }
.fx-kpi-v { font-size: 1.28rem; font-weight: 800; color: var(--fx-tinta); margin-top: 6px; font-variant-numeric: tabular-nums; letter-spacing: -0.02em; }
.fx-kpi-s { font-size: 0.72rem; color: #64748B; margin-top: 1px; }
.fx-kpi-s.up { color: #0D9488; font-weight: 700; } .fx-kpi-s.down { color: #E11D48; font-weight: 700; }
.fx-bar { height: 6px; border-radius: 99px; background: #EEE9F8; margin-top: 8px; overflow: hidden; }
.fx-bar > i { display: block; height: 100%; border-radius: 99px; background: var(--fx-grad); }

/* Títulos clicáveis (expansores): vivos, com barra em gradiente */
div[data-testid="stExpander"] { position: relative; overflow: hidden; border: 1px solid #EFE9FA; border-radius: 16px; background: #FFFFFF;
  box-shadow: var(--fx-sombra-suave); margin-bottom: 10px; }
div[data-testid="stExpander"]::before { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 5px; background: var(--fx-grad); }
div[data-testid="stExpander"] summary { padding: 0.7rem 1rem 0.7rem 1.35rem; }
div[data-testid="stExpander"] summary p { font-weight: 700; font-size: 1.02rem; color: var(--fx-tinta); }
div[data-testid="stExpander"] summary:hover, div[data-testid="stExpander"] details[open] > summary { background: linear-gradient(90deg, #F6F1FF, #FFF4ED); }

/* Botões secundários e de descarga com a mesma linguagem do botão primário */
button[kind="secondary"], button[data-testid="stBaseButton-secondary"], div[data-testid="stDownloadButton"] button {
  border: 1.5px solid #D9C9F7; color: #5B21B6; background: #FFFFFF; font-weight: 700; border-radius: 12px; box-shadow: 0 3px 10px rgba(109, 40, 217, 0.08); }
button[kind="secondary"]:hover, button[data-testid="stBaseButton-secondary"]:hover, div[data-testid="stDownloadButton"] button:hover {
  border-color: transparent; color: #FFFFFF; background: var(--fx-grad); }
button[kind="secondary"]:hover p, button[data-testid="stBaseButton-secondary"]:hover p, div[data-testid="stDownloadButton"] button:hover p { color: #FFFFFF; }
div[data-testid="stProgress"] div[role="progressbar"] > div { background: var(--fx-grad) !important; }

/* Biblioteca: cartões de nível mais pequenos */
.fx-nivel { gap: 12px; margin: 2px 0 12px 0; }
.fx-nivel-card { padding: 12px 18px; border-radius: 16px; }
.fx-nivel-card .fx-nivel-kicker { font-size: 0.62rem; }
.fx-nivel-card .fx-nivel-titulo { font-size: 1.12rem; margin: 3px 0 3px 0; }
.fx-nivel-card p { font-size: 0.78rem; margin: 0 0 6px 0; line-height: 1.35; }
.fx-nivel-card .fx-nivel-n { font-size: 0.7rem; padding: 2px 10px; }

/* Serviços de educação */
.fx-servico { background: #FFFFFF; border: 1px solid #EFE9FA; border-radius: 18px; box-shadow: var(--fx-sombra-suave); overflow: hidden; margin: 14px 0 4px 0; }
.fx-servico-topo { height: 8px; }
.fx-servico.fx-g0 .fx-servico-topo { background: linear-gradient(90deg, #6D28D9, #E11D48); }
.fx-servico.fx-g1 .fx-servico-topo { background: linear-gradient(90deg, #E11D48, #F97316); }
.fx-servico.fx-g2 .fx-servico-topo { background: linear-gradient(90deg, #6D28D9, #7C1F3E); }
.fx-servico.fx-g3 .fx-servico-topo { background: linear-gradient(90deg, #F97316, #FBBF24); }
.fx-servico-corpo { padding: 14px 20px 16px 20px; }
.fx-servico-nome { font-size: 1.2rem; font-weight: 800; color: var(--fx-tinta); letter-spacing: -0.01em; }
.fx-servico-desc { color: #475569; font-size: 0.92rem; line-height: 1.5; margin: 6px 0 10px 0; }
.fx-chip { display: inline-block; background: linear-gradient(120deg, #6D28D9, #E11D48 70%, #F97316); color: #FFFFFF; font-weight: 700; font-size: 0.82rem; padding: 4px 14px; border-radius: 999px; }
.fx-chip-nota { color: #64748B; font-size: 0.8rem; margin-left: 10px; font-style: italic; }

/* Páginas institucionais */
.fx-bloco-grelha { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; margin: 8px 0 16px 0; }
.fx-bloco { background: #FFFFFF; border: 1px solid #EFE9FA; border-radius: 18px; padding: 18px 20px; box-shadow: var(--fx-sombra-suave); position: relative; overflow: hidden; }
.fx-bloco::after { content: ""; position: absolute; right: -30px; top: -30px; width: 110px; height: 110px; border-radius: 50%;
  background: radial-gradient(circle, rgba(249, 115, 22, 0.16), rgba(109, 40, 217, 0.08) 60%, transparent 72%); }
.fx-bloco-titulo { font-size: 1.15rem; font-weight: 800; color: var(--fx-tinta); margin: 2px 0 6px 0; }
.fx-bloco-texto { color: #475569; font-size: 0.92rem; line-height: 1.55; }
.fx-quem { background: linear-gradient(120deg, #FFFFFF, #F6F1FF 55%, #FFF1EA); border: 1px solid #EEE7FA; border-radius: 20px; padding: 22px 26px; box-shadow: var(--fx-sombra); margin: 6px 0 16px 0; }
.fx-quem .fx-quem-texto { font-size: 1.08rem; line-height: 1.6; color: #1B1033; font-weight: 500; }
.fx-aviso-risco { background: #FFF7ED; border: 1px solid #FED7AA; border-left: 5px solid #F97316; border-radius: 14px; padding: 14px 18px; color: #7C2D12; font-size: 0.9rem; line-height: 1.5; margin: 12px 0; }
"""


_FONTE_TITULOS = "@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');\n"


def _carregar_css() -> str:
    """Usa appo.css (ao lado do app.py) se existir; caso contrário, o CSS incluído acima."""
    try:
        f = Path(__file__).with_name("appo.css")
        if f.exists():
            return _FONTE_TITULOS + f.read_text(encoding="utf-8") + CSS_APPO_FINCITE + CSS_APPO_FASE1
    except Exception:
        pass
    return _FONTE_TITULOS + CSS_APPO_BASE + CSS_APPO_FINCITE + CSS_APPO_FASE1


st.markdown(f"<style>{_carregar_css()}</style>", unsafe_allow_html=True)


def logo_svg(tamanho: int = 46, cor: str = COR_MARCA) -> str:
    return (
        f'<svg width="{tamanho}" height="{tamanho}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><g>'
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


def _esc(v) -> str:
    """Escapa texto antes de o inserir em HTML."""
    return _html_pub.escape(str(v if v is not None else ""))


def hero(titulo: str, subtitulo: str, badge: str = None):
    if badge is None:
        badge = t().get("bodiva_badge", "🇦🇴 Kwanzas (Kz)")
    render_html(f'<div class="appo-hero">{logo_svg(48, COR_MARCA)}<div><h1>{_esc(titulo)}</h1><p>{_esc(subtitulo)}</p><span class="appo-badge">{_esc(badge)}</span></div></div>')


def banner_capa(imagem_url: str, texto: str, altura: int = 170, escurecimento: float = 0.5):
    """Faixa institucional sem imagem de fundo (os parâmetros de imagem mantêm-se por compatibilidade)."""
    render_html(f'<div class="appo-capa" style="min-height:{max(56, int(altura * 0.45))}px;"><span>{_esc(texto)}</span></div>')


CORES_CATEGORIA = {"Institucional": COR_MARCA, "Educação": "#1F6F5C", "Análise de Mercado": "#1E293B", "Referência": "#8A6A26"}
ICONES_CATEGORIA = {"Institucional": "🏛️", "Educação": "📖", "Análise de Mercado": "📊", "Referência": "📎"}


IMAGENS_CATEGORIA = {"Institucional": IMG_REUNIAO, "Educação": IMG_LIVROS, "Análise de Mercado": IMG_GRAFICO, "Referência": IMG_SKYLINE}


def banner_categoria(categoria: str):
    icone = ICONES_CATEGORIA.get(categoria, "📄")
    cor = CORES_CATEGORIA.get(categoria, COR_MARCA)
    url = IMAGENS_CATEGORIA.get(categoria)
    if url:
        render_html(f'<div style="position:relative;height:150px;border-radius:12px;overflow:hidden;margin-bottom:10px;background:{cor} url(\'{url}\') center/cover no-repeat;">'
                    f'<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(20,5,12,0.02) 35%,rgba(20,5,12,0.62) 100%);"></div>'
                    f'<span style="position:absolute;left:18px;bottom:12px;color:#fff;font-weight:700;font-size:0.8rem;letter-spacing:0.08em;text-transform:uppercase;">{icone} {_esc(categoria)}</span></div>')
        return
    render_html(f'<div class="appo-categoria-banner" style="background:{cor};"><span style="font-size:1.1rem;">{icone}</span><span>{_esc(categoria)}</span></div>')


def nota_indicador(texto: str):
    render_html(f'<div class="appo-indicador-nota">💡 {texto}</div>')


# Logótipos das empresas cotadas: coloque os ficheiros em «logos/» ao lado do app.py, com o nome do ticker sem os 'A' finais
# (ex.: logos/SBAO.png, logos/UNTL.png, logos/BFA.png). Sem ficheiro, mostra-se um selo com as iniciais (nunca falha).
_PASTA_LOGOS = Path(__file__).resolve().parent / "logos"
_CACHE_LOGOS = {}


def logo_data_uri(ticker) -> str:
    """Data-URI do logótipo (para st.column_config.ImageColumn); vazio se não houver ficheiro."""
    base = str(ticker or "").strip().upper().rstrip("A")
    try:
        import base64 as _b64
        for ext, mime in ((".png", "image/png"), (".jpg", "image/jpeg"), (".webp", "image/webp")):
            f = _PASTA_LOGOS / f"{base}{ext}"
            if base and f.is_file() and f.stat().st_size < 400_000:
                return f"data:{mime};base64," + _b64.b64encode(f.read_bytes()).decode()
    except Exception:
        pass
    return ""


def cfg_logo() -> dict:
    try:
        return {"Logo": st.column_config.ImageColumn(" ", width="small")}
    except Exception:
        return {}


def logo_activo_html(ticker, nome="", px: int = 18) -> str:
    base = str(ticker or "").strip().upper().rstrip("A")
    chave = (base, px)
    if chave in _CACHE_LOGOS:
        return _CACHE_LOGOS[chave]
    html_logo = ""
    try:
        import base64 as _b64
        for ext, mime in ((".png", "image/png"), (".jpg", "image/jpeg"), (".jpeg", "image/jpeg"), (".webp", "image/webp"), (".svg", "image/svg+xml")):
            f = _PASTA_LOGOS / f"{base}{ext}"
            if base and f.is_file() and f.stat().st_size < 400_000:
                dados = _b64.b64encode(f.read_bytes()).decode()
                html_logo = (f'<img src="data:{mime};base64,{dados}" alt="" style="height:{px}px;width:{px}px;object-fit:contain;'
                             f'border-radius:4px;vertical-align:middle;margin-right:6px;">')
                break
    except Exception:
        html_logo = ""
    if not html_logo:
        ini = _html_pub.escape((base[:2] or str(nome or "?")[:2]).upper())
        html_logo = (f'<span style="display:inline-block;height:{px}px;width:{px}px;line-height:{px}px;text-align:center;border-radius:50%;'
                     f'font-size:{max(px // 2 - 1, 7)}px;font-weight:700;color:#FFFFFF;vertical-align:middle;margin-right:6px;'
                     f'background:linear-gradient(135deg,#6D28D9,#E11D48 60%,#F97316);">{ini}</span>')
    _CACHE_LOGOS[chave] = html_logo
    return html_logo


def ticker_tape(df_activos: pd.DataFrame):
    if df_activos.empty:
        return
    itens = []
    for _, a in df_activos.iterrows():
        v = float(a["variacao"])
        cor = "#0D9488" if v > 0 else ("#DC2626" if v < 0 else "#6B7280")
        itens.append(f'<span style="color:{cor}; margin-right:36px;">{logo_activo_html(a["ticker"], a["nome"])}{_esc(a["ticker"] or a["nome"])} &nbsp;{kz(a["preco"])} &nbsp;({pct_bruto(v)})</span>')
    conteudo = "".join(itens) * 3
    render_html(f'<div class="appo-ticker-wrap"><div class="appo-ticker-move"><span>{conteudo}</span></div></div>')


def botoes_partilha(texto: str):
    cod = urllib.parse.quote(texto)
    wa  = f"https://wa.me/?text={cod}"
    tw  = f"https://twitter.com/intent/tweet?text={cod}"
    fb  = f"https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fclube-investimento-appo.onrender.com&quote={cod}"
    tx  = t()
    render_html(
        f"""
        <div class="appo-share" style="display:flex; gap:10px; margin-top:10px; flex-wrap:wrap;">
            <a href="{wa}" target="_blank" style="background:#25D366;">{tx['partilha_wa']}</a>
            <a href="{tw}" target="_blank" style="background:#111;">{tx['partilha_tw']}</a>
            <a href="{fb}" target="_blank" style="background:#1877F2;">{tx['partilha_fb']}</a>
        </div>
        """
    )


# =========================================================
# CONSTANTES E SEGREDOS
# =========================================================
DATABASE_URL = os.environ.get("DATABASE_URL")
ADMIN_EMAIL_INICIAL    = os.environ.get("ADMIN_EMAIL", "admin@appo.co.ao")
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
    sinal   = "-" if inteiro < 0 else ""
    inteiro = abs(inteiro)
    return f"{sinal}{f'{inteiro:,}'.replace(',', ' ')} Kz"


def pct(valor) -> str:
    try:
        return f"{float(valor)*100:+.2f}%"
    except (TypeError, ValueError):
        return "0.00%"


def pct_bruto(valor) -> str:
    try:
        v = float(valor)
        if v == 0:
            return "0.00%"
        return f"{v:+.2f}%"
    except (TypeError, ValueError):
        return "0.00%"


def kz2(valor) -> str:
    """Formato de corretora: 94 600,00"""
    try:
        return f"{float(valor):,.2f}".replace(",", " ").replace(".", ",")
    except (TypeError, ValueError):
        return "0,00"


def _fmt_dt(v) -> str:
    try:
        return v.strftime("%d/%m/%Y | %H:%M:%S")
    except Exception:
        return "—"


def multiplo(v) -> str:
    if v is None:
        return "n/d"
    try:
        return f"{float(v):.2f}x"
    except (TypeError, ValueError):
        return "n/d"


def cor_variacao(v) -> str:
    try:
        v = float(v)
    except (TypeError, ValueError):
        return ""
    if v > 0:
        return "color:#0D9488; font-weight:600;"
    if v < 0:
        return "color:#DC2626; font-weight:600;"
    return "color:#6B7280;"


def tabela_cotacoes_estilizada(df_activos: pd.DataFrame):
    tx = t()
    cols = tx["cot_tabela_cols"]
    df_disp = df_activos[["ticker", "nome", "tipo", "preco", "variacao"]].copy()
    df_disp.insert(0, "Logo", df_disp["ticker"].map(logo_data_uri))
    df_disp["mercado"] = "🇦🇴 BODIVA"
    df_disp = df_disp.rename(columns={"ticker": cols["ticker"], "nome": cols["nome"], "tipo": cols["tipo"],
                                       "preco": cols["preco"], "variacao": cols["variacao"], "mercado": cols["mercado"]})
    df_disp = df_disp[["Logo", cols["ticker"], cols["nome"], cols["tipo"], cols["mercado"], cols["preco"], cols["variacao"]]]
    return (
        df_disp.style
        .format({cols["preco"]: kz, cols["variacao"]: pct_bruto})
        .map(cor_variacao, subset=[cols["variacao"]])
        .set_properties(subset=[cols["ticker"]], **{"font-family": "monospace", "letter-spacing": "0.4px"})
        .set_properties(subset=[cols["preco"]], **{"font-weight": "600"})
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
    dados    = resposta.json()
    if dados.get("result") != "success":
        raise ValueError("Falha ao obter taxas de câmbio.")
    return {"rates": dados["rates"], "actualizado": dados.get("time_last_update_utc", "")}


# ---------------- Painéis de gráficos (estilo home broker) ----------------
PERIODOS_GRAFICO = ["1d", "7d", "1m", "3m", "6m", "1a", "5a"]
_PERIODO_DIAS = {"1d": 1, "7d": 7, "1m": 30, "3m": 91, "6m": 182, "1a": 365, "5a": 1826}
_PERIODO_PASSO = {"1d": 1, "7d": 1, "1m": 1, "3m": 3, "6m": 7, "1a": 7, "5a": 30}
_PERIODO_NOME = {"1d": "último dia face ao anterior", "7d": "últimos 7 dias", "1m": "último mês", "3m": "últimos 3 meses",
                 "6m": "último semestre", "1a": "último ano", "5a": "últimos 5 anos"}
CAMBIO_DADOS_DESDE = "2024-03-02"  # primeiro dia disponível na fonte aberta de câmbio


def _numero_flex(valor):
    """'94 600,00' | '94600.0000' | 94600 -> float; None se não for número."""
    if valor is None or isinstance(valor, (dict, list, bool)):
        return None
    if isinstance(valor, (int, float)):
        return None if valor != valor else float(valor)
    t_ = str(valor).replace("\u00a0", "").replace(" ", "").replace("Kz", "").strip()
    if not t_:
        return None
    if "," in t_ and "." in t_:
        dec = "," if t_.rfind(",") > t_.rfind(".") else "."
        mil = "." if dec == "," else ","
        t_ = t_.replace(mil, "").replace(dec, ".")
    elif "," in t_ or "." in t_:
        sep = "," if "," in t_ else "."
        partes = t_.split(sep)
        milhares = len(partes) > 2 or (len(partes[1]) == 3 and 1 <= len(partes[0]) <= 3)
        t_ = "".join(partes) if milhares else partes[0] + "." + partes[1]
    try:
        return float(t_)
    except ValueError:
        return None


def registar_cotacoes_hoje(df_activos_: pd.DataFrame, sobrepor: bool = False):
    """Guarda a cotação de hoje de cada activo no histórico. Só substitui um valor já existente (por exemplo, o fecho
    importado da BODIVA) quando `sobrepor` é verdadeiro, ou seja, quando o administrador grava cotações.
    Nunca interrompe quem chama."""
    try:
        hoje = datetime.now().date()
        for _, r in df_activos_.iterrows():
            tk = str(r.get("ticker") or "").strip().upper()
            pr = _num_seguro(r.get("preco"), default=0.0)
            if tk and pr > 0:
                executar("INSERT INTO historico_cotacoes (dia, ticker, preco) VALUES (%s, %s, %s) "
                         "ON CONFLICT (ticker, dia) DO " + ("UPDATE SET preco = EXCLUDED.preco" if sobrepor else "NOTHING"),
                         (hoje, tk, pr))
    except Exception:
        pass


def obter_opv(ticker: str):
    """(preço, data|None) da OPV do título, ou None. Compara o ticker sem os 'A' finais."""
    linha = consultar_um("SELECT preco, data FROM opv_activos WHERE RTRIM(ticker, 'A') = RTRIM(%s, 'A') LIMIT 1", (ticker,))
    return (float(linha[0]), linha[1]) if linha else None


def guardar_opv(ticker: str, preco: float, data=None):
    exigir_admin()
    executar("INSERT INTO opv_activos (ticker, preco, data) VALUES (%s, %s, %s) "
             "ON CONFLICT (ticker) DO UPDATE SET preco = EXCLUDED.preco, data = EXCLUDED.data", (ticker.strip().upper(), preco, data))


def eliminar_opv(ticker: str):
    exigir_admin()
    executar("DELETE FROM opv_activos WHERE ticker = %s", (ticker,))


def obter_serie_cotacao(ticker: str, periodo: str) -> pd.DataFrame:
    """Série (Data, Valor) do título. Compara o ticker sem os 'A' finais, para que 'BFAAAAA' e 'BFAAAAAA' sejam o mesmo
    título; se houver os dois no mesmo dia, prevalece o ticker mais comprido (o da BODIVA)."""
    from datetime import timedelta
    base = ("SELECT DISTINCT ON (dia) dia AS \"Data\", preco AS \"Valor\" FROM historico_cotacoes "
            "WHERE RTRIM(ticker, 'A') = RTRIM(%s, 'A') {filtro} ORDER BY dia, LENGTH(ticker) DESC")
    if periodo == "1d":
        df = consultar_df("SELECT * FROM (" + base.format(filtro="") + ") t ORDER BY \"Data\" DESC LIMIT 2", (ticker,))
        df = df.sort_values("Data").reset_index(drop=True)
    else:
        inicio = datetime.now().date() - timedelta(days=_PERIODO_DIAS[periodo])
        df = consultar_df(base.format(filtro="AND dia >= %s"), (ticker, inicio))
    if not df.empty:
        df["Valor"] = df["Valor"].astype(float)
    return df


def importar_historico_cotacoes(df_ficheiro: pd.DataFrame, ticker_forcado: str = "") -> tuple:
    """Importa linhas (data, ticker, preço) de um CSV/Excel. Devolve (linhas_importadas, linhas_ignoradas)."""
    exigir_admin()
    import unicodedata

    def norm(c):
        return "".join(ch for ch in unicodedata.normalize("NFKD", str(c).strip().lower()) if not unicodedata.combining(ch))

    cols = {norm(c): c for c in df_ficheiro.columns}

    def achar(opcoes):
        for o in opcoes:
            for k, original in cols.items():
                if k == o or o in k:
                    return original
        return None

    c_data = achar(["data", "date", "dia", "category"])
    c_tk = achar(["ticker", "codigo", "simbolo", "symbol", "cevama"])
    c_pr = achar(["preco", "cotacao", "fecho", "close", "price", "ultimo"])
    if not (c_data and c_pr and (c_tk or ticker_forcado)):
        raise ValueError("Não encontrei as colunas de data e preço (e de ticker, se não escolher o título). "
                         "Use cabeçalhos como: data, ticker, preco.")
    import re as _re
    ok = bad = 0
    registos = {}
    for _, r in df_ficheiro.iterrows():
        bruto = str(r[c_data]).strip()
        if _re.match(r"^\d{4}-\d{1,2}-\d{1,2}", bruto):
            d = pd.to_datetime(bruto[:10], format="%Y-%m-%d", errors="coerce")   # ISO: nunca troca dia e mês
        else:
            d = pd.to_datetime(bruto, dayfirst=True, errors="coerce")
        tk = (str(ticker_forcado).strip().upper() if ticker_forcado else str(r[c_tk] or "").strip().upper())
        pr = _numero_flex(r[c_pr])
        if pd.isna(d) or not tk or not pr or pr <= 0:
            bad += 1
            continue
        registos[(tk, d.date())] = pr          # a última linha de cada (ticker, dia) prevalece
    itens = list(registos.items())
    for i in range(0, len(itens), 200):         # inserção em blocos: muito mais rápido do que linha a linha
        bloco = itens[i:i + 200]
        sql = "INSERT INTO historico_cotacoes (dia, ticker, preco) VALUES " + ",".join(["(%s, %s, %s)"] * len(bloco)) + \
              " ON CONFLICT (ticker, dia) DO UPDATE SET preco = EXCLUDED.preco"
        params = []
        for (tk, dia), pr in bloco:
            params += [dia, tk, pr]
        executar(sql, tuple(params))
        ok += len(bloco)
    return ok, bad


@st.cache_data(ttl=3600, show_spinner=False)
def obter_serie_cambio_aoa(moeda: str, periodo: str = "1m") -> pd.DataFrame:
    """Kz por 1 unidade de `moeda` ao longo do período, a partir de uma fonte aberta (fawazahmed0/exchange-api,
    sem chave; um ficheiro por dia, disponível desde 02/03/2024). Períodos longos usam amostragem (3, 7 ou 30 dias)."""
    from concurrent.futures import ThreadPoolExecutor
    from datetime import date, timedelta
    base = moeda.lower()
    hoje = date.today()
    minimo = date.fromisoformat(CAMBIO_DADOS_DESDE)
    datas = [hoje - timedelta(days=i) for i in range(0, _PERIODO_DIAS[periodo] + 1, _PERIODO_PASSO[periodo])]
    datas = [d for d in datas if d >= minimo]

    def um_dia(d):
        versao = "latest" if d == hoje else d.isoformat()
        for url in (f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{versao}/v1/currencies/{base}.json",
                    f"https://{versao}.currency-api.pages.dev/v1/currencies/{base}.json"):
            try:
                r = requests.get(url, timeout=8)
                if r.status_code == 200:
                    j = r.json()
                    return str(j.get("date") or d.isoformat()), float(j[base]["aoa"])
            except Exception:
                continue
        return None

    with ThreadPoolExecutor(max_workers=10) as ex:
        resultados = [x for x in ex.map(um_dia, datas) if x]
    unico = {}
    for dt, v in resultados:
        unico[dt] = v
    df = pd.DataFrame({"Data": list(unico.keys()), "Valor": list(unico.values())})
    if df.empty:
        return pd.DataFrame(columns=["Data", "Valor"])
    return df.sort_values("Data").reset_index(drop=True)


def _camadas_serie(alt, df, eixo_x, eixo_y, base, unidade):
    """Área com gradiente suave, linha fina e, ao passar o rato, guia vertical, ponto e etiqueta com data e valor."""
    cor = "#A8607B"
    try:
        grad = alt.Gradient(gradient="linear", x1=1, x2=1, y1=1, y2=0,
                            stops=[alt.GradientStop(color="rgba(239,185,136,0.0)", offset=0), alt.GradientStop(color="rgba(217,138,130,0.14)", offset=0.55), alt.GradientStop(color="rgba(142,124,195,0.26)", offset=1)])
        area = alt.Chart(df).mark_area(color=grad, interpolate="monotone").encode(x=eixo_x, y=eixo_y, y2="_base:Q")
    except Exception:
        area = alt.Chart(df).mark_area(opacity=0.12, color=cor, interpolate="monotone").encode(x=eixo_x, y=eixo_y, y2="_base:Q")
    camadas = area + base.mark_line(color=cor, strokeWidth=1.5, interpolate="monotone")
    try:
        try:
            sel = alt.selection_point(fields=["Data"], nearest=True, on="mouseover", empty=False)
            juntar = lambda ch: ch.add_params(sel)
        except AttributeError:
            sel = alt.selection(type="single", fields=["Data"], nearest=True, on="mouseover", empty="none")
            juntar = lambda ch: ch.add_selection(sel)
        pontos = juntar(base.mark_point(opacity=0, size=140))
        destaque = base.mark_circle(color=cor, size=55).encode(opacity=alt.condition(sel, alt.value(1), alt.value(0)))
        guia = alt.Chart(df).mark_rule(color="#94A3B8", strokeDash=[4, 4], strokeWidth=1).encode(
            x=eixo_x, opacity=alt.condition(sel, alt.value(0.9), alt.value(0)))
        camadas = camadas + guia + pontos + destaque
    except Exception:
        traceback.print_exc()
    try:
        camadas.to_dict()   # valida a especificação na versão de Altair instalada; se falhar, usa o estilo simples
    except Exception:
        traceback.print_exc()
        simples = alt.Chart(df).mark_area(opacity=0.12, color=cor, interpolate="monotone").encode(x=eixo_x, y=eixo_y, y2="_base:Q")
        camadas = simples + base.mark_line(color=cor, strokeWidth=1.5, interpolate="monotone")
    return camadas


def grafico_area_simples(df: pd.DataFrame, rotulo: str, altura: int = 260):
    """Série temporal simples (índice = data, uma coluna de valores) no mesmo estilo dos painéis de cotação."""
    import altair as alt
    d = df.reset_index().iloc[:, :2].copy()
    d.columns = ["Data", "Valor"]
    d["Data"] = pd.to_datetime(d["Data"])
    d = d.dropna().sort_values("Data")
    if len(d) < 2:
        st.info("Ainda não há pontos suficientes para desenhar o gráfico.")
        return
    vmin, vmax = float(d["Valor"].min()), float(d["Valor"].max())
    pad = (vmax - vmin) * 0.15 or abs(vmax) * 0.05 or 1.0
    d["_base"] = vmin - pad
    eixo_x = alt.X("Data:T", title=None, axis=alt.Axis(format="%d/%m/%y", labelColor="#6B6B6B", grid=False))
    eixo_y = alt.Y("Valor:Q", title=None, scale=alt.Scale(domain=[vmin - pad, vmax + pad], zero=False),
                   axis=alt.Axis(orient="right", labelColor="#6B6B6B", gridColor="#EADFE4", format=",.2f"))
    base = alt.Chart(d).encode(x=eixo_x, y=eixo_y, tooltip=[alt.Tooltip("Data:T", format="%d/%m/%Y", title="Data"),
                                                           alt.Tooltip("Valor:Q", format=",.2f", title=str(rotulo))])
    st.altair_chart(_camadas_serie(alt, d, eixo_x, eixo_y, base, str(rotulo)).properties(height=altura), use_container_width=True)


def painel_grafico(titulo: str, subtitulo: str, serie: pd.DataFrame, unidade: str, periodo: str, nota: str = "", referencia=None):
    """Painel no estilo do home broker: cabeçalho, indicadores do período e gráfico de área na cor do Clube."""
    import html as _h
    import altair as alt
    render_html(f"""<div style="border-bottom:3px solid #E11D48;padding-bottom:6px;margin:6px 0 12px 0;">
    <span style="font-size:1.2rem;font-weight:800;color:#1A1A2E;">{_h.escape(titulo)}</span>
    <span style="color:#8A7B80;font-size:0.8rem;margin-left:10px;">{_h.escape(subtitulo)}</span></div>""")
    if serie is None or serie.empty:
        st.info("Ainda não há dados para este período.")
        return
    df = serie.copy()
    df["Data"] = pd.to_datetime(df["Data"])
    ultimo, primeiro = float(df["Valor"].iloc[-1]), float(df["Valor"].iloc[0])
    var = (ultimo / primeiro - 1) * 100 if primeiro else 0.0
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Último valor", f"{ultimo:,.2f} {unidade}")
    from datetime import timedelta
    inicio_janela = datetime.now().date() - timedelta(days=_PERIODO_DIAS[periodo])
    d0 = df["Data"].iloc[0].date()
    rotulo_var = (f"Variação (desde {d0:%d/%m/%y})" if periodo != "1d" and d0 > inicio_janela + timedelta(days=10)
                  else f"Variação ({_PERIODO_NOME[periodo]})")
    m2.metric(rotulo_var, pct_bruto(var), delta=pct_bruto(var) if len(df) > 1 else None)
    m3.metric("Máximo do período", f"{df['Valor'].max():,.2f}")
    m4.metric("Mínimo do período", f"{df['Valor'].min():,.2f}")
    if len(df) < 2:
        st.info("Só existe um registo neste período, por isso ainda não há linha para desenhar. "
                "A série cresce a cada nova actualização.")
    else:
        vmin, vmax = float(df["Valor"].min()), float(df["Valor"].max())
        if referencia:
            vmin, vmax = min(vmin, referencia[1]), max(vmax, referencia[1])
        pad = (vmax - vmin) * 0.15 or vmax * 0.01
        df["_base"] = vmin - pad
        span_dias = (df["Data"].max() - df["Data"].min()).days
        if span_dias <= 14:
            eixo_datas = alt.Axis(format="%d/%m", labelColor="#6B6B6B", grid=False, tickCount={"interval": "day", "step": 1})
        elif span_dias <= 100:
            eixo_datas = alt.Axis(format="%d/%m/%y", labelColor="#6B6B6B", grid=False, tickCount={"interval": "week", "step": 1})
        else:
            eixo_datas = alt.Axis(format="%d/%m/%y", labelColor="#6B6B6B", grid=False)
        eixo_x = alt.X("Data:T", title=None, axis=eixo_datas)
        eixo_y = alt.Y("Valor:Q", title=None, scale=alt.Scale(domain=[vmin - pad, vmax + pad], zero=False),
                       axis=alt.Axis(orient="right", labelColor="#6B6B6B", gridColor="#EADFE4", format=",.2f"))
        base = alt.Chart(df).encode(
            x=eixo_x, y=eixo_y,
            tooltip=[alt.Tooltip("Data:T", format="%d/%m/%Y", title="Data"),
                     alt.Tooltip("Valor:Q", format=",.2f", title=unidade)])
        # a área fecha na base visível do gráfico (y2), e não no zero, que está fora do eixo
        camadas = _camadas_serie(alt, df, eixo_x, eixo_y, base, unidade)
        if referencia:
            ref_df = pd.DataFrame({"y": [float(referencia[1])], "txt": [referencia[0]]})
            esc_y = alt.Scale(domain=[vmin - pad, vmax + pad], zero=False)
            eixo_ref = alt.Axis(orient="right", labelColor="#6B6B6B", gridColor="#EADFE4", format=",.2f")
            camadas = camadas + alt.Chart(ref_df).mark_rule(color="#6B6B6B", strokeDash=[6, 4], strokeWidth=1.4).encode(
                y=alt.Y("y:Q", title=None, scale=esc_y, axis=eixo_ref)) + alt.Chart(ref_df).mark_text(
                align="left", dx=6, dy=-7, color="#6B6B6B", fontSize=11).encode(
                y=alt.Y("y:Q", title=None, scale=esc_y, axis=eixo_ref), text="txt:N", x=alt.value(2))
        st.altair_chart(camadas.properties(height=340), use_container_width=True)
    if referencia:
        var_ref = (ultimo / referencia[1] - 1) * 100 if referencia[1] else 0.0
        st.markdown(f"🏷️ **{referencia[0]}** · variação desde a OPV: **{pct_bruto(var_ref)}**")
    if nota:
        st.caption(nota)


# ---------------- Cotações directas da BODIVA ----------------
# Mesmo endpoint e mesma lógica de pesquisa do script Apps Script do Google Sheets
# (que já foi testado e encontra os 7 títulos). Só LÊ dados; nada é gravado
# sem o admin confirmar na pré-visualização.
URL_BODIVA_RESUMO = "https://www.bodiva.ao/website/api/GetAllMarketSummary_no.php"


def _num_bodiva(valor):
    """Converte um valor vindo da BODIVA em preço (>100 e diferente de 2026), ou None."""
    if valor is None or isinstance(valor, (dict, list, bool)):
        return None
    if isinstance(valor, (int, float)):
        num = float(valor)
    else:
        t_ = str(valor).replace("\u00a0", "").replace(" ", "").strip()
        if not t_:
            return None
        if "," in t_ and "." in t_:
            dec = "," if t_.rfind(",") > t_.rfind(".") else "."
            mil = "." if dec == "," else ","
            t_ = t_.replace(mil, "").replace(dec, ".")
        elif "," in t_ or "." in t_:
            sep = "," if "," in t_ else "."
            partes = t_.split(sep)
            # um só separador: é de milhares apenas se vier exactamente 3 dígitos
            # depois dele e no máximo 3 antes (ex.: 94.600); em qualquer outro
            # caso é decimal (ex.: 94600.0000, 94600,00, 30600.5)
            milhares = len(partes) > 2 or (len(partes[1]) == 3 and 1 <= len(partes[0]) <= 3)
            if milhares:
                t_ = "".join(partes)
            else:
                t_ = partes[0] + "." + partes[1]
        try:
            num = float(t_)
        except ValueError:
            return None
    return num if (num > 100 and num != 2026) else None


_CHAVES_PRECO_BODIVA = [
    "ultimo_preco", "ultimopreco", "last_price", "lastprice",
    "preco_fecho", "precofecho", "close_price", "closeprice",
    "cotacao", "preco", "price", "ultimo", "last", "fecho", "close", "valor",
]


def _preco_do_objecto_bodiva(obj):
    if not isinstance(obj, dict):
        return None
    for chave in _CHAVES_PRECO_BODIVA:
        for prop, val in obj.items():
            if str(prop).lower() == chave or chave in str(prop).lower():
                v = _num_bodiva(val)
                if v is not None:
                    return v
    return None


def _procurar_em_json_bodiva(dados, ticker):
    import json as _json
    lista = dados if isinstance(dados, list) else [dados]
    base = ticker.rstrip("A")
    for item in lista:
        txt = _json.dumps(item, ensure_ascii=False).upper()
        if ticker in txt or (len(base) >= 4 and base in txt):
            v = _preco_do_objecto_bodiva(item)
            if v is not None:
                return v
    filhos = dados.values() if isinstance(dados, dict) else (dados if isinstance(dados, list) else [])
    for filho in filhos:
        if isinstance(filho, (dict, list)):
            v = _procurar_em_json_bodiva(filho, ticker)
            if v is not None:
                return v
    return None


def _procurar_em_texto_bodiva(conteudo, ticker):
    import re as _re
    texto = conteudo.upper()
    base = ticker.rstrip("A")
    pos = texto.find(ticker)
    if pos == -1 and len(base) >= 4:
        pos = texto.find(base)
    if pos == -1:
        return None
    trecho = conteudo[pos:pos + 300]
    padrao = r':\s*"?(\d{1,3}(?:[ .]\d{3})+(?:,\d{1,2})?|\d+(?:[.,]\d{1,2})?)"?'
    for m in _re.finditer(padrao, trecho):
        v = _num_bodiva(_re.sub(r'^:\s*"?', "", m.group(0)).rstrip('"'))
        if v is not None:
            return v
    return None


def buscar_cotacoes_bodiva(tickers) -> dict:
    """Devolve {ticker: preço ou None}. Levanta excepção se a BODIVA não responder."""
    cabecalhos = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.bodiva.ao/",
    }
    try:
        resp = requests.get(URL_BODIVA_RESUMO, headers=cabecalhos, timeout=20)
    except requests.exceptions.SSLError:
        # O servidor da BODIVA não envia a cadeia completa de certificados (os
        # navegadores e o Google conseguem completá-la, o Python não). Como são
        # dados públicos, só de leitura, e o admin confere os preços na
        # pré-visualização antes de gravar, repete-se o pedido sem verificar o certificado.
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        resp = requests.get(URL_BODIVA_RESUMO, headers=cabecalhos, timeout=20, verify=False)
    if resp.status_code != 200:
        raise ValueError(f"A BODIVA respondeu com o código HTTP {resp.status_code}.")
    conteudo = resp.text
    try:
        dados = resp.json()
    except ValueError:
        dados = None
    resultado = {}
    for tk in tickers:
        tk = str(tk or "").strip().upper()
        if not tk:
            continue
        preco = _procurar_em_json_bodiva(dados, tk) if dados is not None else None
        if preco is None:
            preco = _procurar_em_texto_bodiva(conteudo, tk)
        resultado[tk] = preco
    return resultado



# =========================================================
# CONTEÚDO EDUCATIVO (fica em PT — conforme acordado)
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
8. **Princípio 50/30/20** — 50% consumo, 30% investimento, 20% entesouramento.
9. **Nenhuma posição sem tese registada**
"""

TEXTO_EX_DIVIDENDO        = "A **data ex-dividendo** é o dia a partir do qual quem compra uma acção já não tem direito ao próximo dividendo anunciado."
TEXTO_RATEIO              = "O **rateio** distribui proporcionalmente as acções de uma OPV quando a procura excede a oferta."
TEXTO_OPV_UNITEL          = "Em Julho de 2026, o Estado colocou à venda 15% do capital da Unitel via OPV — a maior de sempre em Angola."
TEXTO_OPV_SBA             = "Em Setembro de 2026, o Estado lançou a OPV de 34% do Standard Bank Angola."
TEXTO_INVESTIDOR_VS_TRADER= "Segundo Benjamin Graham, um investidor sente-se dono do negócio, exige margem de segurança, e pensa diferente da maioria."
TEXTO_DIVIDENDOS_GUIA     = "Três datas decidem se recebes um dividendo: Assembleia Geral, data de registo (a que importa), e data de pagamento."
TEXTO_DANGOTE             = "A Dangote Refinery abriu capital na NGX em 2026 — mercado fora do âmbito da BODIVA, referência educativa."
TEXTO_REGRAS_BODIVA       = "Regra BODIVA 2/18: dispersão mínima 5%, lote mínimo 1 acção, variação máxima 25% estática, liquidação D+1."

ACTIVOS_INICIAIS = [
    ("UNTLAAAA", "Unitel",                     "Ação",  38000.0, 0.0),
    ("SBAOAAAA", "Standard Bank Angola",        "Ação",  45000.0, 0.0),
    ("BFAAAAAA", "Banco de Fomento Angola (BFA)","Ação", 12500.0, 0.0),
    ("BDVAAAAA", "BODIVA",                      "Ação",  82400.0, 0.0),
]

ARTIGOS_INICIAIS = [
    ("Princípios e Filosofia de Investimento do Clube", "Institucional",      TEXTO_PRINCIPIOS),
    ("O que é a Data Ex-Dividendo?",                    "Educação",           TEXTO_EX_DIVIDENDO),
    ("O que é o Rateio?",                               "Educação",           TEXTO_RATEIO),
    ("Análise da OPV da Unitel (2026)",                 "Análise de Mercado", TEXTO_OPV_UNITEL),
    ("Análise da OPV do Standard Bank Angola (2026)",   "Análise de Mercado", TEXTO_OPV_SBA),
    ("Investidor vs. Trader — os três princípios de Benjamin Graham", "Educação", TEXTO_INVESTIDOR_VS_TRADER),
    ("Dividendos na BODIVA: as três datas que decidem se recebes",    "Educação", TEXTO_DIVIDENDOS_GUIA),
    ("A OPV da Dangote Petroleum Refinery — análise comparativa",     "Análise de Mercado", TEXTO_DANGOTE),
    ("Regras de Negociação da BODIVA (Regra Nº 2/18)",                "Referência", TEXTO_REGRAS_BODIVA),
]

AVALIACOES_INICIAIS = [
    ("BFA",            "Banca",                      100500.0, 15000000,  233140000000, 0, 365250000000, 139885149600, 0.08),
    ("BAI",            "Banca",                       93900.0, 19450000,  295918000000, 0, 838000000000, 147841239768, 0.08),
    ("BCGA",           "Banca",                       19800.0, 20000000,   44143653000, 0, 256000000000,  21630389955, 0.06),
    ("ENSA",           "Seguros",                     26500.0,  2400000,    6360917000, 0,           0,   3880154744, 0.05),
    ("BDV (BODIVA)",   "Infra-estrutura de Mercado",  81000.0,   600000,    2609155000, 0,  9120000000,  1565495329, 0.10),
    ("UNITEL",         "Telecomunicações",            34000.0, 50000000,  158368000000, 220800000000, 925000000000, 40000000000, 0.04),
    ("SBA (Standard Bank)", "Banca",                 41220.0, 14000000,  150000000000, 0, 340900000000,           0, 0.08),
]

# =========================================================
# BASE DE DADOS
# =========================================================
@st.cache_resource
def obter_ligacao():
    # connect_timeout + keepalives: evitam que a app fique pendurada para sempre
    # numa ligação morta (ex.: a Neon suspende a base de dados por inactividade).
    conn = psycopg2.connect(DATABASE_URL, connect_timeout=15,
                            keepalives=1, keepalives_idle=30, keepalives_interval=10, keepalives_count=3)
    conn.autocommit = True
    # Se outra sessão tiver a tabela bloqueada, falha ao fim de 20 s em vez de esperar eternamente.
    try:
        with conn.cursor() as _cur:
            _cur.execute("SET lock_timeout = '20s'")
    except Exception:
        pass
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
    # Simulador de Investimento — persistido por sócio (antes só vivia em
    # st.session_state, por isso desaparecia ao sair/voltar a entrar).
    executar("""CREATE TABLE IF NOT EXISTS sim_estado (
                    conta_email TEXT PRIMARY KEY,
                    saldo_caixa NUMERIC NOT NULL DEFAULT 3000000
                )""")
    executar("""CREATE TABLE IF NOT EXISTS sim_posicoes (
                    conta_email TEXT NOT NULL,
                    ticker TEXT NOT NULL,
                    nome TEXT NOT NULL,
                    qtd NUMERIC NOT NULL,
                    preco_medio NUMERIC NOT NULL,
                    PRIMARY KEY (conta_email, ticker)
                )""")
    executar("""CREATE TABLE IF NOT EXISTS sim_historico (
                    id SERIAL PRIMARY KEY,
                    conta_email TEXT NOT NULL,
                    operacao TEXT NOT NULL,
                    ticker TEXT NOT NULL,
                    qtd NUMERIC NOT NULL,
                    preco_unit NUMERIC NOT NULL,
                    total NUMERIC NOT NULL,
                    criado_em TIMESTAMP NOT NULL DEFAULT NOW()
                )""")
    # Orçamento pessoal/familiar de cada sócio (Princípio 50/30/20) — guardado como JSON
    executar("""CREATE TABLE IF NOT EXISTS orcamento_pessoal (
                    conta_email TEXT PRIMARY KEY,
                    dados TEXT NOT NULL,
                    actualizado_em TIMESTAMP NOT NULL DEFAULT NOW()
                )""")
    # Carteira REAL do Clube (dinheiro verdadeiro, investido de facto na BFA) —
    # distinta do Simulador (dinheiro fictício, para treino). Editável pelo
    # admin no painel; é esta tabela que alimenta o relatório PDF, substituindo
    # o antigo dicionário fixo CARTEIRA_REAL escrito no código.
    executar("""CREATE TABLE IF NOT EXISTS carteira_real (
                    id SERIAL PRIMARY KEY,
                    ticker TEXT NOT NULL,
                    nome TEXT NOT NULL,
                    qtd NUMERIC NOT NULL DEFAULT 0,
                    valor_aquisicao NUMERIC NOT NULL DEFAULT 0,
                    actualizado_em TIMESTAMP NOT NULL DEFAULT NOW()
                )""")
    executar("""CREATE TABLE IF NOT EXISTS activos (id SERIAL PRIMARY KEY, nome TEXT NOT NULL, tipo TEXT NOT NULL, preco NUMERIC NOT NULL, variacao NUMERIC NOT NULL DEFAULT 0, actualizado_em TIMESTAMP NOT NULL DEFAULT NOW())""")
    executar("ALTER TABLE activos ADD COLUMN IF NOT EXISTS ticker TEXT NOT NULL DEFAULT ''")
    executar("ALTER TABLE activos ADD COLUMN IF NOT EXISTS preco_anterior NUMERIC NOT NULL DEFAULT 0")  # legado, já não é usado para calcular variação
    executar("ALTER TABLE activos ADD COLUMN IF NOT EXISTS preco_abertura_dia NUMERIC")
    executar("ALTER TABLE activos ADD COLUMN IF NOT EXISTS data_abertura_dia DATE")
    executar("""CREATE TABLE IF NOT EXISTS artigos (id SERIAL PRIMARY KEY, titulo TEXT NOT NULL, categoria TEXT NOT NULL, conteudo TEXT NOT NULL, criado_em TIMESTAMP NOT NULL DEFAULT NOW())""")
    executar("ALTER TABLE artigos ADD COLUMN IF NOT EXISTS nivel TEXT")   # NULL = automático, pela categoria
    executar("""CREATE TABLE IF NOT EXISTS unidades_movimentos (id SERIAL PRIMARY KEY, data DATE NOT NULL, socio TEXT NOT NULL, socio_email TEXT, tipo TEXT NOT NULL, montante NUMERIC NOT NULL, vup NUMERIC NOT NULL, unidades NUMERIC NOT NULL, criado_em TIMESTAMP NOT NULL DEFAULT NOW())""")
    executar("""CREATE TABLE IF NOT EXISTS cotas_config (id INTEGER PRIMARY KEY CHECK (id = 1), valor_nominal NUMERIC NOT NULL DEFAULT 100000, limite_cotas NUMERIC, entrada_minima NUMERIC NOT NULL DEFAULT 100000)""")
    executar("INSERT INTO cotas_config (id, limite_cotas) VALUES (1, 100) ON CONFLICT (id) DO NOTHING")
    executar("""CREATE TABLE IF NOT EXISTS historico_vup (dia DATE PRIMARY KEY, vlg NUMERIC NOT NULL, unidades NUMERIC NOT NULL, vup NUMERIC NOT NULL)""")
    executar("""CREATE TABLE IF NOT EXISTS opv_activos (ticker TEXT PRIMARY KEY, preco NUMERIC NOT NULL, data DATE)""")
    executar("INSERT INTO opv_activos (ticker, preco, data) VALUES ('SBAOAAAA', 50000, '2026-09-28') ON CONFLICT (ticker) DO NOTHING")
    executar("INSERT INTO opv_activos (ticker, preco, data) VALUES ('UNTLAAAA', 40040, NULL) ON CONFLICT (ticker) DO NOTHING")
    # ---- Actualização "Educação e Serviços / Área privada": migrações apenas aditivas (nada é apagado) ----
    executar("ALTER TABLE contas ADD COLUMN IF NOT EXISTS is_participante BOOLEAN NOT NULL DEFAULT FALSE")
    executar("ALTER TABLE contas ADD COLUMN IF NOT EXISTS nivel TEXT NOT NULL DEFAULT 'iniciante'")
    executar("ALTER TABLE contas ADD COLUMN IF NOT EXISTS trocar_password BOOLEAN NOT NULL DEFAULT FALSE")
    executar("""CREATE TABLE IF NOT EXISTS perfil_investidor (id SERIAL PRIMARY KEY, conta_id INTEGER NOT NULL, versao INTEGER NOT NULL DEFAULT 1, respostas TEXT NOT NULL, pontuacoes TEXT NOT NULL, perfil TEXT NOT NULL, portal TEXT NOT NULL, criado_em TIMESTAMP NOT NULL DEFAULT NOW())""")
    executar("CREATE INDEX IF NOT EXISTS idx_perfil_conta ON perfil_investidor (conta_id, criado_em)")
    executar("""CREATE TABLE IF NOT EXISTS pedidos_recuperacao (id SERIAL PRIMARY KEY, email TEXT NOT NULL, contacto TEXT, estado TEXT NOT NULL DEFAULT 'pendente', criado_em TIMESTAMP NOT NULL DEFAULT NOW(), resolvido_em TIMESTAMP, resolvido_por TEXT)""")
    executar("""CREATE TABLE IF NOT EXISTS base_indice_appo (ticker TEXT PRIMARY KEY, preco_base NUMERIC NOT NULL, fonte TEXT, actualizado_em TIMESTAMP NOT NULL DEFAULT NOW())""")
    # único preço de 19/08/2026 confirmado por documento: o da compra de UNITEL (nota de execução), às 14:49
    executar("INSERT INTO base_indice_appo (ticker, preco_base, fonte) VALUES ('UNTLAAAA', 36000, 'Nota de Execução de 19/08/2026 (negócio das 14:49, BFA CM)') ON CONFLICT (ticker) DO NOTHING")
    # restantes preços-base, segundo as cotações da BODIVA indicadas pelo administrador; só entram se o título ainda não tiver base
    for _tk, _pb, _fonte in [("BAIAAAAA", 97200, "BODIVA, cotações de 19/08/2026"), ("BCGAAAAA", 20000, "BODIVA, cotações de 19/08/2026"),
                             ("BDVAAAAA", 84000, "BODIVA, cotações de 19/08/2026"), ("BFAAAAAA", 100000, "BODIVA, cotações de 19/08/2026"),
                             ("ENSAAAAA", 29000, "BODIVA, cotações de 19/08/2026"),
                             ("SBAOAAAA", 62500, "BODIVA, primeiro preço em bolsa (30/09/2026): não estava cotada a 19/08/2026")]:
        executar("INSERT INTO base_indice_appo (ticker, preco_base, fonte) SELECT %s, %s, %s WHERE NOT EXISTS "
                 "(SELECT 1 FROM base_indice_appo WHERE RTRIM(ticker, 'A') = RTRIM(%s, 'A'))", (_tk, _pb, _fonte, _tk))
    executar("""CREATE TABLE IF NOT EXISTS auditoria (id SERIAL PRIMARY KEY, quando TIMESTAMP NOT NULL DEFAULT NOW(), utilizador TEXT, accao TEXT NOT NULL, entidade TEXT, entidade_id TEXT, antes TEXT, depois TEXT, motivo TEXT)""")
    executar("""CREATE TABLE IF NOT EXISTS balanco_privado (id SERIAL PRIMARY KEY, data_ref DATE NOT NULL, dinheiro_disponivel NUMERIC NOT NULL DEFAULT 0, outros_activos NUMERIC NOT NULL DEFAULT 0, passivos NUMERIC NOT NULL DEFAULT 0, fonte TEXT, titularidade TEXT, estado TEXT NOT NULL DEFAULT 'Provisório', origem TEXT, criado_por TEXT, criado_em TIMESTAMP NOT NULL DEFAULT NOW(), validado_por TEXT, validado_em TIMESTAMP)""")
    for _col, _tipo in [("classe", "TEXT"), ("estado", "TEXT"), ("origem", "TEXT"), ("referencia", "TEXT"), ("fundamento", "TEXT"),
                        ("motivo_anulacao", "TEXT"), ("anulado_por", "TEXT"), ("anulado_em", "TIMESTAMP"), ("criado_por", "TEXT"),
                        ("efeito_caixa", "NUMERIC"), ("antes", "TEXT"), ("depois", "TEXT")]:
        executar(f"ALTER TABLE unidades_movimentos ADD COLUMN IF NOT EXISTS {_col} {_tipo}")
    executar("UPDATE unidades_movimentos SET classe = CASE WHEN tipo = 'Subscrição inicial' THEN 'Fundadora' ELSE 'Ordinária' END WHERE classe IS NULL")
    executar("UPDATE unidades_movimentos SET estado = 'Por rever', origem = 'Legado (lançado antes da revisão)' WHERE estado IS NULL")
    executar("CREATE UNIQUE INDEX IF NOT EXISTS ux_unidades_referencia ON unidades_movimentos (referencia) WHERE referencia IS NOT NULL")
    executar("ALTER TABLE cotas_config ADD COLUMN IF NOT EXISTS peso_voto_fundadora NUMERIC NOT NULL DEFAULT 1")
    executar("ALTER TABLE cotas_config ADD COLUMN IF NOT EXISTS unidades_base_validada BOOLEAN NOT NULL DEFAULT FALSE")
    executar("ALTER TABLE cotas_config ADD COLUMN IF NOT EXISTS admissao_activa BOOLEAN NOT NULL DEFAULT FALSE")
    executar("ALTER TABLE cotas_config ADD COLUMN IF NOT EXISTS data_base DATE")
    executar("ALTER TABLE cotas_config ADD COLUMN IF NOT EXISTS fundamento_base TEXT")
    executar("ALTER TABLE historico_vup ADD COLUMN IF NOT EXISTS estado TEXT")
    executar("""CREATE TABLE IF NOT EXISTS servicos_catalogo (id SERIAL PRIMARY KEY, codigo TEXT UNIQUE NOT NULL, nome TEXT NOT NULL, descricao TEXT, preco NUMERIC, nota_preco TEXT, tipo TEXT NOT NULL DEFAULT 'educativo', activo BOOLEAN NOT NULL DEFAULT TRUE, visivel_publico BOOLEAN NOT NULL DEFAULT TRUE, contratavel BOOLEAN NOT NULL DEFAULT FALSE, ordem INTEGER NOT NULL DEFAULT 0)""")
    executar("""CREATE TABLE IF NOT EXISTS pedidos_servicos (id SERIAL PRIMARY KEY, criado_em TIMESTAMP NOT NULL DEFAULT NOW(), servico_id INTEGER, servico_nome TEXT, nome TEXT NOT NULL, email TEXT, telefone TEXT, participantes INTEGER NOT NULL DEFAULT 1, mensagem TEXT, estado_servico TEXT NOT NULL DEFAULT 'Recebido', estado_pagamento TEXT NOT NULL DEFAULT 'Por confirmar', pagamento_confirmado_por TEXT, pagamento_confirmado_em TIMESTAMP, pagamento_nota TEXT)""")
    executar("""CREATE TABLE IF NOT EXISTS manifestacoes_interesse (id SERIAL PRIMARY KEY, criado_em TIMESTAMP NOT NULL DEFAULT NOW(), nome TEXT NOT NULL, email TEXT, telefone TEXT, mensagem TEXT, consentimento BOOLEAN NOT NULL DEFAULT FALSE, estado TEXT NOT NULL DEFAULT 'Recebida')""")
    executar("ALTER TABLE manifestacoes_interesse ADD COLUMN IF NOT EXISTS profissao TEXT")
    executar("""CREATE TABLE IF NOT EXISTS historico_privado (id SERIAL PRIMARY KEY, descricao TEXT NOT NULL, valor_estimado NUMERIC, estado TEXT NOT NULL DEFAULT 'Estimativa não reconciliada', nota TEXT, criado_em TIMESTAMP NOT NULL DEFAULT NOW())""")
    executar("""CREATE TABLE IF NOT EXISTS identidades_socios (nome_interno TEXT PRIMARY KEY, rotulo_publico TEXT NOT NULL)""")
    executar("""CREATE TABLE IF NOT EXISTS carteira_referencia (ticker TEXT PRIMARY KEY, qtd NUMERIC NOT NULL, fonte TEXT)""")
    executar("""CREATE TABLE IF NOT EXISTS config_app (chave TEXT PRIMARY KEY, valor TEXT)""")
    executar("""CREATE TABLE IF NOT EXISTS despesas_admin (id SERIAL PRIMARY KEY, data DATE NOT NULL, descricao TEXT NOT NULL, categoria TEXT, valor NUMERIC NOT NULL, fornecedor TEXT, estado TEXT NOT NULL DEFAULT 'Proposta', aprovada_por TEXT, aprovada_em TIMESTAMP, nota TEXT, criado_por TEXT, criado_em TIMESTAMP NOT NULL DEFAULT NOW())""")
    _seed_servicos = [
        ("primeiros_passos_bodiva", "Primeiros passos na BODIVA", "Workshop em grupo, guia próprio e sessão de perguntas sobre o funcionamento da bolsa, acções, dividendos, riscos e comissões.", 5000, "Preço experimental de teste (editável); não é preço de mercado comprovado.", "educativo", True, True, True, 1),
        ("demonstracoes_financeiras", "Leitura de demonstrações financeiras", "Como ler o balanço, a demonstração de resultados e os principais indicadores, com exercícios.", None, "Sob consulta", "educativo", True, True, False, 2),
        ("valuation_educativo", "Métodos de valuation (educativo)", "Os métodos explicados com exercícios e pressupostos. Não inclui recomendações de compra ou venda.", None, "Sob consulta", "educativo", True, True, False, 3),
        ("sessoes_instituicoes", "Sessões para empresas, escolas e associações", "Sessões educativas à medida do público, incluindo planeamento financeiro e a regra 50/30/20.", None, "Sob consulta", "educativo", True, True, False, 4),
        ("programa_capacidade_financeira", "Programa de Capacidade Financeira", "Percurso com diagnóstico, treino prático e acompanhamento da evolução, baseado no modelo de Kempson et al. (conhecimento, atitude e comportamento em cinco domínios).", None, "Sob consulta", "educativo", True, True, False, 5),
        ("priv_analise_accao", "Análise de uma acção (proposta privada)", "Proposta interna; não activa até validar o enquadramento profissional e regulatório.", 60000, "Proposta privada", "consultoria", False, False, False, 10),
        ("priv_relatorio_completo", "Relatório de valuation completo (proposta privada)", "Proposta interna; não activa até validar o enquadramento profissional e regulatório.", 180000, "Proposta privada", "consultoria", False, False, False, 11),
        ("priv_consultoria_mensal", "Consultoria contínua mensal (proposta privada)", "Proposta interna; não activa até validar o enquadramento profissional e regulatório.", 120000, "Proposta privada (por mês)", "consultoria", False, False, False, 12),
    ]
    for _s in _seed_servicos:
        executar("INSERT INTO servicos_catalogo (codigo, nome, descricao, preco, nota_preco, tipo, activo, visivel_publico, contratavel, ordem) "
                 "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (codigo) DO NOTHING", _s)
    executar("INSERT INTO config_app (chave, valor) VALUES ('contacto_publico_email', 'clube.investimento.appo@gmail.com') ON CONFLICT (chave) DO NOTHING")
    if not consultar_um("SELECT 1 FROM historico_privado LIMIT 1"):
        executar("INSERT INTO historico_privado (descricao, valor_estimado, estado, nota) VALUES (%s, %s, %s, %s)",
                 ("Fase experimental anterior (2024 até hoje), descontinuada: perdas e dispêndios históricos estimados", 3000000,
                  "Estimativa não reconciliada",
                  "Documentação incompleta. Não é activo do Clube, não é automaticamente dívida aos fundadores e não entra no património, no VUP nem no preço de entrada."))
    if not consultar_um("SELECT 1 FROM carteira_referencia LIMIT 1"):
        for _tk, _q in (("BFAAAAAA", 2), ("BAIAAAAA", 4), ("UNTLAAAA", 38)):
            executar("INSERT INTO carteira_referencia (ticker, qtd, fonte) VALUES (%s, %s, %s) ON CONFLICT (ticker) DO NOTHING",
                     (_tk, _q, "Referência informada pelo administrador (06/10/2026); a validar com o extracto do homebroker"))
    executar("""CREATE TABLE IF NOT EXISTS historico_cotacoes (dia DATE NOT NULL, ticker TEXT NOT NULL, preco NUMERIC NOT NULL, PRIMARY KEY (ticker, dia))""")
    executar("""CREATE TABLE IF NOT EXISTS documentos_pdf (id SERIAL PRIMARY KEY, titulo TEXT NOT NULL, categoria TEXT NOT NULL, descricao TEXT, nome_ficheiro TEXT NOT NULL, tipo TEXT NOT NULL DEFAULT 'biblioteca', tamanho INTEGER NOT NULL, conteudo BYTEA NOT NULL, criado_em TIMESTAMP NOT NULL DEFAULT NOW())""")
    for _col in ("versao", "estado_aprovacao", "nota"):
        executar(f"ALTER TABLE documentos_pdf ADD COLUMN IF NOT EXISTS {_col} TEXT")
    executar("""CREATE TABLE IF NOT EXISTS socios (id SERIAL PRIMARY KEY, nome TEXT NOT NULL, email TEXT, telefone TEXT, bi TEXT, contribuicao_inicial NUMERIC, criado_em TIMESTAMP NOT NULL DEFAULT NOW())""")
    executar("""CREATE TABLE IF NOT EXISTS premissas_macro (id INTEGER PRIMARY KEY CHECK (id = 1), inflacao NUMERIC NOT NULL DEFAULT 0.135, taxa_livre_risco NUMERIC NOT NULL DEFAULT 0.18, premio_risco NUMERIC NOT NULL DEFAULT 0.055, beta_banca NUMERIC NOT NULL DEFAULT 1.0, beta_telecom NUMERIC NOT NULL DEFAULT 0.9, beta_outros NUMERIC NOT NULL DEFAULT 1.0, actualizado_em TIMESTAMP NOT NULL DEFAULT NOW())""")
    executar("""CREATE TABLE IF NOT EXISTS avaliacoes (id SERIAL PRIMARY KEY, empresa TEXT UNIQUE NOT NULL, sector TEXT NOT NULL, preco NUMERIC NOT NULL DEFAULT 0, acoes_circulacao NUMERIC NOT NULL DEFAULT 0, lucro_liquido NUMERIC NOT NULL DEFAULT 0, ganho_pontual NUMERIC NOT NULL DEFAULT 0, capital_proprio NUMERIC NOT NULL DEFAULT 0, dividendo_total NUMERIC NOT NULL DEFAULT 0, crescimento_g NUMERIC NOT NULL DEFAULT 0.08, actualizado_em TIMESTAMP NOT NULL DEFAULT NOW())""")
    executar("""CREATE TABLE IF NOT EXISTS favoritos (conta_id INTEGER NOT NULL, activo_id INTEGER NOT NULL, PRIMARY KEY (conta_id, activo_id))""")
    executar("""CREATE TABLE IF NOT EXISTS historico_cambio_aoa (registado_em DATE PRIMARY KEY, usd NUMERIC, eur NUMERIC, gbp NUMERIC, zar NUMERIC, cny NUMERIC, brl NUMERIC)""")
    executar("""CREATE TABLE IF NOT EXISTS historico_indice_mercado (registado_em DATE PRIMARY KEY, indice_variacao NUMERIC NOT NULL)""")

    executar("""CREATE TABLE IF NOT EXISTS capacidade_diagnosticos (id SERIAL PRIMARY KEY, conta_email TEXT NOT NULL, criado_em TIMESTAMP NOT NULL DEFAULT NOW(), versao TEXT, respostas TEXT, resultados TEXT)""")
    executar("CREATE INDEX IF NOT EXISTS ix_cap_diag_conta ON capacidade_diagnosticos (conta_email, criado_em)")
    if consultar_um("SELECT COUNT(*) FROM contas")[0] == 0:
        executar("INSERT INTO contas (nome, email, password_hash, is_admin) VALUES (%s, %s, %s, %s)",
                 ("Administrador", ADMIN_EMAIL_INICIAL, hash_password(ADMIN_PASSWORD_INICIAL), True))

    if consultar_um("SELECT COUNT(*) FROM resumo_patrimonial")[0] == 0:
        executar("INSERT INTO resumo_patrimonial (id, capital_social, capital_subscrito, capital_realizado, investimentos, reservas) VALUES (1, %s, %s, %s, %s, %s)",
                 (10000000.0, 10000000.0, 5000000.0, 1866677.0, 2832885.0))
        executar("INSERT INTO historico_patrimonio (capital_social, investimentos, reservas, total) VALUES (%s, %s, %s, %s)",
                 (5000000.0, 1866677.0, 2832885.0, 5000000.0 + 1866677.0 + 2832885.0))
    else:
        linha = consultar_um("SELECT capital_subscrito, capital_realizado, capital_social FROM resumo_patrimonial WHERE id = 1")
        if linha and linha[0] is None:
            valor_antigo = float(linha[2])
            executar("UPDATE resumo_patrimonial SET capital_subscrito = %s, capital_realizado = %s WHERE id = 1",
                     (valor_antigo, valor_antigo * 0.5))

    if consultar_um("SELECT COUNT(*) FROM activos")[0] == 0:
        for ticker, nome, tipo, preco, var in ACTIVOS_INICIAIS:
            executar("INSERT INTO activos (nome, tipo, preco, variacao, ticker) VALUES (%s, %s, %s, %s, %s)", (nome, tipo, preco, var, ticker))
    else:
        for ticker, nome, tipo, preco, var in ACTIVOS_INICIAIS:
            executar("UPDATE activos SET ticker = %s WHERE nome = %s AND (ticker IS NULL OR ticker = '')", (ticker, nome))
    # ticker correcto do Standard Bank Angola na BODIVA: SBAOAAAA (versões antigas gravavam SBAAAAAA)
    executar("UPDATE activos SET ticker = 'SBAOAAAA' WHERE ticker = 'SBAAAAAA'")

    for titulo, categoria, conteudo in ARTIGOS_INICIAIS:
        if not consultar_um("SELECT 1 FROM artigos WHERE titulo = %s", (titulo,)):
            executar("INSERT INTO artigos (titulo, categoria, conteudo) VALUES (%s, %s, %s)", (titulo, categoria, conteudo))
    # o artigo antigo mantém o nome «Regra 50/30/20» na base de dados: actualiza-o para «Princípio» (idempotente)
    executar("UPDATE artigos SET conteudo = REPLACE(REPLACE(conteudo, 'Regra 50/30/20', 'Princípio 50/30/20'), 'regra 50/30/20', 'princípio 50/30/20') "
             "WHERE POSITION('egra 50/30/20' IN conteudo) > 0")

    if consultar_um("SELECT COUNT(*) FROM premissas_macro")[0] == 0:
        executar("INSERT INTO premissas_macro (id, inflacao, taxa_livre_risco, premio_risco, beta_banca, beta_telecom, beta_outros) VALUES (1, 0.135, 0.18, 0.055, 1.0, 0.9, 1.0)")

    for empresa, sector, preco, acoes, lucro, ganho, cap_proprio, div_total, g in AVALIACOES_INICIAIS:
        if not consultar_um("SELECT 1 FROM avaliacoes WHERE empresa = %s", (empresa,)):
            executar("INSERT INTO avaliacoes (empresa, sector, preco, acoes_circulacao, lucro_liquido, ganho_pontual, capital_proprio, dividendo_total, crescimento_g) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                     (empresa, sector, preco, acoes, lucro, ganho, cap_proprio, div_total, g))


# ---------------- Papéis, permissões, auditoria e cálculo decimal ----------------
from contextlib import contextmanager
from decimal import Decimal, ROUND_HALF_EVEN


def eh_admin() -> bool:
    return bool(st.session_state.get("autenticado")) and bool(st.session_state.get("is_admin"))


def eh_participante() -> bool:
    """Participante dos investimentos existentes (ou administrador). Comprar formação ou ter conta NÃO dá este papel."""
    return bool(st.session_state.get("autenticado")) and (bool(st.session_state.get("is_admin")) or bool(st.session_state.get("is_participante")))


def exigir_admin():
    if not eh_admin():
        raise PermissionError("Acesso reservado ao administrador.")


def exigir_participante():
    if not eh_participante():
        raise PermissionError("Acesso reservado aos participantes dos investimentos.")


# ---- Portais de Educação: Iniciante e Investidor (resultam do Perfil de Investidor; o nível NÃO é o Premium) ----
NIVEIS = {"iniciante": "Iniciante", "investidor": "Investidor"}


def aviso_discreto(texto: str):
    """Aviso informativo ou legal em letra pequena e cinzento claro (não compete com o conteúdo)."""
    render_html(f'<p class="appo-aviso" style="font-size:0.58rem;line-height:1.3;color:#A3AEBD;margin:0.35rem 0 0 0;">{_esc(texto)}</p>')


def nota_interna(texto: str):
    """Nota para a equipa: só o administrador a vê."""
    if eh_admin():
        st.caption("🔒 " + texto)


def nivel_actual() -> str:
    n = str(st.session_state.get("nivel") or "iniciante")
    return n if n in NIVEIS else "iniciante"


def eh_investidor() -> bool:
    """Portal Investidor: administrador, participantes dos investimentos ou conta cujo perfil indicou o nível Investidor."""
    return bool(st.session_state.get("autenticado")) and (eh_admin() or eh_participante() or nivel_actual() == "investidor")


def utilizador_actual() -> str:
    return str(st.session_state.get("conta_email") or "sistema")


def registar_auditoria(accao, entidade="", entidade_id="", antes=None, depois=None, motivo="", cur=None):
    """Rasto de auditoria: quem fez o quê, quando, com o retrato anterior e posterior. Pode correr dentro de uma transacção (cur)."""
    import json as _json
    params = (utilizador_actual(), accao, entidade, str(entidade_id),
              _json.dumps(antes, ensure_ascii=False, default=str) if antes is not None else None,
              _json.dumps(depois, ensure_ascii=False, default=str) if depois is not None else None, motivo or "")
    sql = "INSERT INTO auditoria (utilizador, accao, entidade, entidade_id, antes, depois, motivo) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    if cur is not None:
        cur.execute(sql, params)
    else:
        executar(sql, params)


D = Decimal


def dec(v) -> Decimal:
    """Converte para Decimal sem passar por erros de vírgula flutuante."""
    if v is None:
        return D("0")
    if isinstance(v, Decimal):
        return v
    return D(str(v))


def q2(x) -> Decimal:
    """Montantes em Kz: 2 casas, arredondamento half-even."""
    return dec(x).quantize(D("0.01"), rounding=ROUND_HALF_EVEN)


def q4(x) -> Decimal:
    """Valor da unidade (VUP): 4 casas, arredondamento half-even."""
    return dec(x).quantize(D("0.0001"), rounding=ROUND_HALF_EVEN)


def q6(x) -> Decimal:
    """Unidades: 6 casas, arredondamento half-even. O total de unidades é a soma dos registos já arredondados."""
    return dec(x).quantize(D("0.000001"), rounding=ROUND_HALF_EVEN)


@contextmanager
def transaccao():
    """Ligação própria e transacção única (tudo ou nada) para operações financeiras. Devolve um cursor."""
    conn = psycopg2.connect(DATABASE_URL, connect_timeout=15)
    try:
        with conn.cursor() as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------- Contas ----------------
def obter_conta_por_email(email: str):
    return consultar_um("SELECT id, nome, email, password_hash, is_admin, is_premium, is_participante, nivel, trocar_password FROM contas WHERE email = %s", (email,))

def inserir_conta(nome, email, password, is_admin):
    exigir_admin()
    executar("INSERT INTO contas (nome, email, password_hash, is_admin) VALUES (%s, %s, %s, %s)", (nome, email, hash_password(password), is_admin))

def listar_contas() -> pd.DataFrame:
    exigir_admin()
    return consultar_df("SELECT id, nome, email, is_admin, is_premium, is_participante, criado_em FROM contas ORDER BY criado_em DESC")

def contar_admins() -> int:
    return consultar_um("SELECT COUNT(*) FROM contas WHERE is_admin = TRUE")[0]

def alternar_premium(conta_id: int, valor: bool):
    exigir_admin()
    executar("UPDATE contas SET is_premium = %s WHERE id = %s", (valor, conta_id))
    registar_auditoria("Premium " + ("activado" if valor else "removido"), "conta", conta_id)


def definir_participante(conta_id: int, valor: bool):
    """Marca/desmarca uma conta como participante dos investimentos existentes (decisão do administrador, auditada)."""
    exigir_admin()
    antes = consultar_um("SELECT is_participante FROM contas WHERE id = %s", (conta_id,))
    executar("UPDATE contas SET is_participante = %s WHERE id = %s", (valor, conta_id))
    registar_auditoria("Participante " + ("atribuído" if valor else "removido"), "conta", conta_id,
                       antes={"is_participante": bool(antes[0]) if antes else None}, depois={"is_participante": valor})

def repor_password(conta_id: int) -> str:
    exigir_admin()
    nova_password = secrets.token_urlsafe(9)
    executar("UPDATE contas SET password_hash = %s, trocar_password = TRUE WHERE id = %s", (hash_password(nova_password), conta_id))
    return nova_password

def registar_pedido_recuperacao(email: str, contacto: str):
    """Pedido público (sem sessão), tratado pelo administrador. Não revela se a conta existe; ignora repetições nas últimas 24 h."""
    email = (email or "").strip().lower()
    ja = consultar_um("SELECT 1 FROM pedidos_recuperacao WHERE email = %s AND estado = 'pendente' AND criado_em > NOW() - INTERVAL '24 hours'", (email,))
    if not ja:
        executar("INSERT INTO pedidos_recuperacao (email, contacto) VALUES (%s, %s)", (email, (contacto or "").strip()))


def obter_pedidos_recuperacao() -> pd.DataFrame:
    exigir_admin()
    return consultar_df("SELECT id, email, contacto, estado, criado_em, resolvido_em, resolvido_por FROM pedidos_recuperacao "
                        "ORDER BY (estado = 'pendente') DESC, criado_em DESC LIMIT 100")


def resolver_pedido_recuperacao(pedido_id: int, repor: bool):
    """Repõe a palavra-passe (devolve a provisória) ou ignora o pedido. Tudo fica auditado."""
    exigir_admin()
    p = consultar_um("SELECT email, estado FROM pedidos_recuperacao WHERE id = %s", (int(pedido_id),))
    if not p or p[1] != "pendente":
        raise ValueError("Este pedido já foi tratado ou não existe.")
    nova = None
    if repor:
        c = consultar_um("SELECT id FROM contas WHERE email = %s", (p[0],))
        if not c:
            raise ValueError("Não existe nenhuma conta com este e-mail. Confirma o e-mail com a pessoa ou ignora o pedido.")
        nova = repor_password(int(c[0]))
    estado = "resolvido" if repor else "ignorado"
    executar("UPDATE pedidos_recuperacao SET estado = %s, resolvido_em = NOW(), resolvido_por = %s WHERE id = %s", (estado, utilizador_actual(), int(pedido_id)))
    registar_auditoria("recuperacao_password_" + estado, "pedido_recuperacao", pedido_id, depois={"email": p[0]})
    return nova


def alterar_password_propria(conta_id, actual: str, nova: str, repetida: str):
    """Devolve uma mensagem de erro, ou None se a palavra-passe foi alterada."""
    if not conta_id:
        return "Sessão inválida."
    if len(nova or "") < 8:
        return "A nova palavra-passe deve ter pelo menos 8 caracteres."
    if nova != repetida:
        return "A repetição não coincide com a nova palavra-passe."
    r = consultar_um("SELECT password_hash FROM contas WHERE id = %s", (int(conta_id),))
    if not r or not verificar_password(actual or "", r[0]):
        return "A palavra-passe actual não está correcta."
    if nova == actual:
        return "A nova palavra-passe tem de ser diferente da actual."
    executar("UPDATE contas SET password_hash = %s, trocar_password = FALSE WHERE id = %s", (hash_password(nova), int(conta_id)))
    registar_auditoria("password_alterada", "conta", conta_id)
    return None


# ---- Envio de e-mail (smtplib). A palavra-passe de aplicação do Gmail NUNCA vai no código: define SMTP_PASSWORD na Render ----
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465") or 465)
SMTP_USER = os.environ.get("SMTP_USER", "clube.investimento.appo@gmail.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
APP_URL = os.environ.get("APP_URL", "https://clube-investimento-appo.onrender.com")
# Envio por HTTPS através de um script do Gmail do Clube (Google Apps Script): não usa portas SMTP, por isso funciona no plano gratuito da Render
EMAIL_RELAY_URL = os.environ.get("EMAIL_RELAY_URL", "")
EMAIL_RELAY_TOKEN = os.environ.get("EMAIL_RELAY_TOKEN", "")


def smtp_configurado() -> bool:
    return bool(SMTP_USER and SMTP_PASSWORD)


def email_configurado() -> bool:
    return bool(EMAIL_RELAY_URL and EMAIL_RELAY_TOKEN) or smtp_configurado()


def estado_email() -> str:
    if EMAIL_RELAY_URL and EMAIL_RELAY_TOKEN:
        return "✅ Envio de e-mail activo (script do Gmail do Clube, por HTTPS)."
    if smtp_configurado():
        return "✅ Envio de e-mail por SMTP (não funciona no plano gratuito da Render)."
    return "⚠️ Envio de e-mail por configurar: até lá, usa o botão de WhatsApp."


def _enviar_via_relay(destinatario: str, assunto: str, texto: str):
    try:
        r = requests.post(EMAIL_RELAY_URL, json={"token": EMAIL_RELAY_TOKEN, "to": destinatario, "subject": assunto, "body": texto}, timeout=25)
    except requests.RequestException:
        return False, "Não foi possível contactar o script de envio de e-mail. Tenta novamente dentro de instantes."
    try:
        dados = r.json()
    except ValueError:
        return False, "O script de envio respondeu de forma inesperada: confirma que está publicado como «Aplicação Web», com acesso para «Qualquer pessoa»."
    if not isinstance(dados, dict):
        return False, "Resposta inválida do script de envio."
    if dados.get("ok"):
        return True, None
    return False, "O script de envio recusou o pedido: " + str(dados.get("erro") or "motivo desconhecido")


def enviar_email(destinatario: str, assunto: str, texto: str):
    """Devolve (True, None) se o e-mail foi entregue ao servidor, ou (False, mensagem de erro em português)."""
    destinatario = (destinatario or "").strip()
    if not email_configurado():
        return False, ("O envio de e-mail ainda não está configurado: define EMAIL_RELAY_URL e EMAIL_RELAY_TOKEN (script do Gmail do Clube) "
                       "ou, num plano pago da Render, SMTP_PASSWORD, nas variáveis de ambiente.")
    if not _REGEX_EMAIL.match(destinatario):
        return False, "O endereço de e-mail é inválido."
    if EMAIL_RELAY_URL and EMAIL_RELAY_TOKEN:
        return _enviar_via_relay(destinatario, assunto, texto)
    msg = EmailMessage()
    msg["From"] = f"Clube de Investimento APPO <{SMTP_USER}>"
    msg["To"] = destinatario
    msg["Subject"] = assunto
    msg.set_content(texto)
    try:
        contexto = ssl.create_default_context()
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=contexto, timeout=12) as srv:
                srv.login(SMTP_USER, SMTP_PASSWORD)
                srv.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=12) as srv:
                srv.starttls(context=contexto)
                srv.login(SMTP_USER, SMTP_PASSWORD)
                srv.send_message(msg)
        return True, None
    except smtplib.SMTPAuthenticationError:
        return False, "O Gmail recusou o início de sessão: SMTP_PASSWORD tem de ser uma palavra-passe de aplicação (com verificação em 2 passos activa), não a palavra-passe normal."
    except (socket.timeout, TimeoutError, ConnectionError, OSError):
        return False, ("Não foi possível ligar ao servidor de e-mail. Se a app corre num plano gratuito da Render, as portas SMTP (465 e 587) estão bloqueadas: "
                       "usa o script do Gmail do Clube (EMAIL_RELAY_URL e EMAIL_RELAY_TOKEN) ou passa a um plano pago.")
    except Exception as exc:
        traceback.print_exc()
        return False, f"Não foi possível enviar o e-mail ({type(exc).__name__})."


def texto_email_nova_password(email: str, password: str):
    assunto = "Clube de Investimento APPO: nova palavra-passe"
    corpo = (f"Olá,\n\nO administrador do Clube de Investimento APPO repôs o acesso à tua conta ({email}).\n\n"
             f"Palavra-passe provisória: {password}\n\n"
             f"Entra em {APP_URL} e escolhe logo uma palavra-passe só tua: a app pede-o no primeiro acesso.\n\n"
             "Se não fizeste este pedido, avisa o administrador.\n\nClube de Investimento APPO")
    return assunto, corpo


def ligacao_whatsapp(contacto: str, texto: str):
    """Ligação wa.me com a mensagem já escrita (o administrador só carrega em enviar). Devolve None se o número não for utilizável."""
    import re as _re_w
    digitos = _re_w.sub(r"\D", "", contacto or "")
    if digitos.startswith("00"):
        digitos = digitos[2:]
    if len(digitos) == 9 and digitos.startswith("9"):
        digitos = "244" + digitos
    if len(digitos) < 11:
        return None
    return f"https://wa.me/{digitos}?text={urllib.parse.quote(texto)}"


def botao_ligacao(rotulo: str, url: str):
    if hasattr(st, "link_button"):
        st.link_button(rotulo, url)
    else:
        st.markdown(f"[{rotulo}]({url})")


def repor_e_enviar_por_email(email: str, contacto: str, repor_fn):
    """Repõe a palavra-passe (repor_fn devolve a provisória) e tenta enviá-la por e-mail; se falhar, mostra-a ao administrador com envio alternativo."""
    nova = repor_fn()
    assunto, corpo = texto_email_nova_password(email, nova)
    ok, erro = enviar_email(email, assunto, corpo)
    if ok:
        st.success(f"Nova palavra-passe enviada para {email}. Pede à pessoa para confirmar a receção (e para ver o spam).")
        return
    st.warning(erro)
    st.info(f"A palavra-passe de {email} já foi reposta. Provisória (envia por outro canal): **{nova}**")
    url = ligacao_whatsapp(contacto, f"Olá! A tua palavra-passe provisória do APPO é: {nova}. Entra em {APP_URL} e escolhe logo uma só tua.")
    if url:
        botao_ligacao("📲 Enviar por WhatsApp", url)


def eliminar_conta(conta_id: int):
    exigir_admin()
    executar("DELETE FROM perfil_investidor WHERE conta_id = %s", (conta_id,))
    executar("DELETE FROM contas WHERE id = %s", (conta_id,))

def registar_acesso(email: str, sucesso: bool):
    executar("INSERT INTO log_acessos (email, sucesso) VALUES (%s, %s)", (email, sucesso))

def obter_log_acessos() -> pd.DataFrame:
    exigir_admin()
    return consultar_df("SELECT email, sucesso, criado_em FROM log_acessos ORDER BY criado_em DESC LIMIT 50")


# ---------------- Resumo patrimonial ----------------
def obter_resumo_patrimonial() -> dict:
    exigir_participante()
    linha = consultar_um("SELECT capital_subscrito, capital_realizado, investimentos, reservas, actualizado_em FROM resumo_patrimonial WHERE id = 1")
    return {"capital_subscrito": float(linha[0] or 0), "capital_realizado": float(linha[1] or 0),
            "investimentos": float(linha[2]), "reservas": float(linha[3]), "actualizado_em": linha[4]}

def actualizar_resumo_patrimonial(capital_subscrito, capital_realizado, investimentos, reservas):
    exigir_admin()
    executar("UPDATE resumo_patrimonial SET capital_social = %s, capital_subscrito = %s, capital_realizado = %s, investimentos = %s, reservas = %s, actualizado_em = NOW() WHERE id = 1",
             (capital_subscrito, capital_subscrito, capital_realizado, investimentos, reservas))
    total = capital_realizado  # investimentos e reservas são partes do capital realizado
    executar("INSERT INTO historico_patrimonio (capital_social, investimentos, reservas, total) VALUES (%s, %s, %s, %s)",
             (capital_realizado, investimentos, reservas, total))

def obter_historico_patrimonio() -> pd.DataFrame:
    exigir_participante()
    # o Património Total do Clube é o Capital Realizado (investimentos e reservas são partes dele);
    # a coluna 'total' antiga somava as três coisas e contava duas vezes.
    return consultar_df("SELECT registado_em, capital_social AS total FROM historico_patrimonio ORDER BY registado_em")


def obter_historico_patrimonio_admin(limite: int = 40) -> pd.DataFrame:
    exigir_admin()
    return consultar_df("SELECT id, registado_em, capital_social, investimentos, reservas FROM historico_patrimonio "
                        "ORDER BY registado_em DESC LIMIT %s", (int(limite),))


def eliminar_registo_historico(registo_id: int):
    exigir_admin()
    executar("DELETE FROM historico_patrimonio WHERE id = %s", (int(registo_id),))


# ---------------- Valor da Unidade de Participação (VUP) ----------------
def obter_cotas_config() -> dict:
    """Regras da estrutura de unidades (cotas): valor nominal, limite, entrada mínima, votos por unidade Fundadora, estado da base."""
    linha = consultar_um("SELECT valor_nominal, limite_cotas, entrada_minima, peso_voto_fundadora, unidades_base_validada, "
                         "admissao_activa, data_base, fundamento_base FROM cotas_config WHERE id = 1")
    if not linha:
        return {"valor_nominal": 100000.0, "limite_cotas": 0.0, "entrada_minima": 0.0, "peso_voto_fundadora": 1.0,
                "unidades_base_validada": False, "admissao_activa": False, "data_base": None, "fundamento_base": ""}
    return {"valor_nominal": float(linha[0]), "limite_cotas": float(linha[1] or 0), "entrada_minima": float(linha[2] or 0),
            "peso_voto_fundadora": float(linha[3] or 1), "unidades_base_validada": bool(linha[4]), "admissao_activa": bool(linha[5]),
            "data_base": linha[6], "fundamento_base": linha[7] or ""}


def guardar_cotas_config(valor_nominal: float, limite_cotas: float, entrada_minima: float, peso_voto_fundadora: float = 1.0):
    exigir_admin()
    antes = obter_cotas_config()
    executar("INSERT INTO cotas_config (id, valor_nominal, limite_cotas, entrada_minima, peso_voto_fundadora) VALUES (1, %s, %s, %s, %s) "
             "ON CONFLICT (id) DO UPDATE SET valor_nominal = EXCLUDED.valor_nominal, limite_cotas = EXCLUDED.limite_cotas, "
             "entrada_minima = EXCLUDED.entrada_minima, peso_voto_fundadora = EXCLUDED.peso_voto_fundadora",
             (valor_nominal, limite_cotas, entrada_minima, peso_voto_fundadora))
    registar_auditoria("Regras de unidades alteradas", "cotas_config", 1, antes=antes,
                       depois={"valor_nominal": valor_nominal, "limite_cotas": limite_cotas, "entrada_minima": entrada_minima,
                               "peso_voto_fundadora": peso_voto_fundadora})


def adicionar_votos(df_mov: pd.DataFrame, peso_fundadora: float) -> pd.DataFrame:
    """Acrescenta 'votos': cada unidade Fundadora vale `peso_fundadora` votos (proposta pendente de formalização); a Ordinária vale 1."""
    out = df_mov.copy()
    if out.empty:
        out["votos"] = pd.Series(dtype=float)
        return out
    if "classe" not in out.columns:
        out["classe"] = "Ordinária"
    out["classe"] = out["classe"].fillna("Ordinária")
    out["votos"] = out.apply(lambda r: float(r["unidades"]) * (float(peso_fundadora) if r["classe"] == "Fundadora" else 1.0), axis=1)
    return out


NOME_ADMIN_PUBLICO = "Aníbal Alexandre Pereira da Costa"
ROTULO_ADMIN_PUBLICO = NOME_ADMIN_PUBLICO + " — Administrador Executivo"
_ROMANOS = ["II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]


def _norm_nome(n) -> str:
    import unicodedata
    base = "".join(c for c in unicodedata.normalize("NFKD", str(n or "")) if not unicodedata.combining(c))
    return " ".join(base.lower().split())


def rotulos_publicos(nomes: list) -> dict:
    """Mapeia nomes internos para o rótulo mostrável: só o administrador é identificado; os restantes são 'Sócio II', 'Sócio III'...
    A anonimização é apenas de apresentação: os registos internos mantêm as identidades."""
    guardados = {}
    try:
        guardados = {_norm_nome(r["nome_interno"]): r["rotulo_publico"] for _, r in consultar_df("SELECT nome_interno, rotulo_publico FROM identidades_socios").iterrows()}
    except Exception:
        pass
    usados = set(guardados.values())
    livres = [f"Sócio {r}" for r in _ROMANOS if f"Sócio {r}" not in usados]
    out = {}
    for n in nomes:
        k = _norm_nome(n)
        if k == _norm_nome(NOME_ADMIN_PUBLICO):
            out[n] = ROTULO_ADMIN_PUBLICO
        elif k in guardados:
            out[n] = guardados[k]
        else:
            out[n] = livres.pop(0) if livres else "Sócio"
    return out


def calcular_subscricoes_iniciais(capital, valor_nominal, fundadores: list) -> list:
    """Hipótese de estrutura inicial: reparte o capital de referência pelas percentagens acordadas (não prova contribuições).
    Decimal; o resto de arredondamento vai para o maior titular, para o total bater certo. ValueError com mensagem clara."""
    linhas = []
    for f in fundadores:
        nome = str(f.get("Sócio") or "").strip()
        pct = _numero_flex(f.get("% do capital")) or 0.0
        if not nome and pct <= 0:
            continue
        if not nome or pct <= 0:
            raise ValueError("Cada linha precisa de um nome e de uma percentagem superior a zero.")
        linhas.append((nome, str(f.get("E-mail da conta (opcional)") or "").strip().lower() or None, dec(pct)))
    if not linhas:
        raise ValueError("Preencha os participantes e as respectivas percentagens.")
    total = sum(p for _, _, p in linhas)
    if abs(total - D(100)) > D("0.01"):
        raise ValueError(f"As percentagens somam {total:.2f}%; têm de somar exactamente 100%.")
    capital, valor_nominal = dec(capital), dec(valor_nominal)
    if capital <= 0 or valor_nominal <= 0:
        raise ValueError("O capital de referência e o valor nominal têm de ser superiores a zero.")
    montantes = [q2(capital * p / D(100)) for _, _, p in linhas]
    resto = q2(capital) - sum(montantes)
    if resto != 0:
        montantes[max(range(len(linhas)), key=lambda i: linhas[i][2])] += resto
    return [{"socio": n, "email": e, "pct": p, "montante": m, "cotas": q6(m / valor_nominal)} for (n, e, p), m in zip(linhas, montantes)]


def avaliar_carteira_real() -> dict:
    """Investimentos a preços de avaliação registados na app. Decimal. Devolve valor, custo, data dos preços e linhas sem preço."""
    exigir_participante()
    cart = obter_carteira_real()
    ativos = obter_activos()
    por_tk = {str(r["ticker"]).strip().upper().rstrip("A"): r for _, r in ativos.iterrows() if str(r["ticker"]).strip()}
    por_nome = {str(r["nome"]).strip().upper(): r for _, r in ativos.iterrows()}
    va, vq, datas, sem_preco = D(0), D(0), [], []
    for _, l in cart.iterrows():
        chave = str(l["ticker"] or "").strip().upper().rstrip("A")
        ativo = por_tk.get(chave) if chave else None
        if ativo is None:
            ativo = por_nome.get(str(l["nome"] or "").strip().upper())
        if ativo is None:
            sem_preco.append(str(l["nome"]))
        else:
            va += dec(l["qtd"]) * dec(ativo["preco"])
            if ativo.get("actualizado_em") is not None:
                datas.append(ativo["actualizado_em"])
        vq += dec(l["valor_aquisicao"])
    return {"valor": q2(va), "custo": q2(vq), "data_precos": max(datas) if datas else None, "sem_preco": sem_preco}


def valor_carteira_real_actual() -> tuple:
    av = avaliar_carteira_real()
    return float(av["valor"]), float(av["custo"])


def obter_ultimo_balanco():
    exigir_participante()
    return consultar_um("SELECT id, data_ref, dinheiro_disponivel, outros_activos, passivos, fonte, titularidade, estado, origem "
                        "FROM balanco_privado ORDER BY data_ref DESC, id DESC LIMIT 1")


def obter_vup_info() -> dict:
    """Valor da unidade = património líquido validado / unidades em circulação.
    Património líquido = investimentos a preços de avaliação + dinheiro disponível + outros activos comprovados - passivos.
    O capital realizado NÃO entra (evita dupla contagem). Estado: Não calculado | Provisório | Validado."""
    exigir_participante()
    av = avaliar_carteira_real()
    bal = obter_ultimo_balanco()
    cfg = obter_cotas_config()
    un_val = dec(consultar_um("SELECT COALESCE(SUM(unidades), 0) FROM unidades_movimentos WHERE estado = 'Validado'")[0])
    un_rever = dec(consultar_um("SELECT COALESCE(SUM(unidades), 0) FROM unidades_movimentos WHERE estado = 'Por rever'")[0])
    base = consultar_um("SELECT vup, data FROM unidades_movimentos WHERE estado = 'Validado' ORDER BY data, id LIMIT 1")
    motivos = []
    if bal is None:
        motivos.append("Falta registar o balanço (dinheiro disponível, outros activos e passivos).")
    if un_val <= 0:
        motivos.append("Não há unidades validadas em circulação.")
    if av["sem_preco"]:
        motivos.append("Há posições sem preço de avaliação: " + ", ".join(av["sem_preco"]) + ".")
    dinheiro = dec(bal[2]) if bal else D(0)
    outros = dec(bal[3]) if bal else D(0)
    passivos = dec(bal[4]) if bal else D(0)
    nav = q2(av["valor"] + dinheiro + outros - passivos)
    if motivos:
        estado, vup = "Não calculado", D(0)
    else:
        vup = q4(nav / un_val)
        estado = "Validado" if (bal[7] == "Validado" and cfg["unidades_base_validada"]) else "Provisório"
    return {"valor_carteira": float(av["valor"]), "custo_carteira": float(av["custo"]), "reservas": float(dinheiro), "dinheiro": float(dinheiro),
            "outros": float(outros), "passivos": float(passivos), "vlg": float(nav), "nav": nav, "unidades": float(un_val),
            "unidades_por_rever": float(un_rever), "vup": float(vup), "vup_dec": vup,
            "vup_base": float(base[0]) if base else 0.0, "data_base": base[1] if base else None,
            "estado": estado, "motivos": motivos, "data_precos": av["data_precos"], "balanco": bal}


def registar_vup_hoje():
    """Grava o VUP de hoje (com o seu estado) no histórico. Não grava se o indicador não for calculável. Nunca interrompe quem chama."""
    try:
        i = obter_vup_info()
        if i["estado"] != "Não calculado" and i["unidades"] > 0 and i["vup"] > 0:
            executar("INSERT INTO historico_vup (dia, vlg, unidades, vup, estado) VALUES (%s, %s, %s, %s, %s) "
                     "ON CONFLICT (dia) DO UPDATE SET vlg = EXCLUDED.vlg, unidades = EXCLUDED.unidades, vup = EXCLUDED.vup, estado = EXCLUDED.estado",
                     (datetime.now().date(), i["vlg"], i["unidades"], i["vup"], i["estado"]))
    except Exception:
        pass


def obter_serie_vup(periodo: str) -> pd.DataFrame:
    exigir_participante()
    from datetime import timedelta
    if periodo == "1d":
        df = consultar_df('SELECT dia AS "Data", vup AS "Valor" FROM historico_vup ORDER BY dia DESC LIMIT 2')
        df = df.sort_values("Data").reset_index(drop=True)
    else:
        inicio = datetime.now().date() - timedelta(days=_PERIODO_DIAS[periodo])
        df = consultar_df('SELECT dia AS "Data", vup AS "Valor" FROM historico_vup WHERE dia >= %s ORDER BY dia', (inicio,))
    if not df.empty:
        df["Valor"] = df["Valor"].astype(float)
    return df


def obter_unidades_movimentos(incluir_anulados: bool = True) -> pd.DataFrame:
    exigir_participante()
    filtro = "" if incluir_anulados else "WHERE estado <> 'Anulado' "
    df = consultar_df("SELECT id, data, socio, socio_email, tipo, classe, estado, origem, referencia, montante, vup, unidades, efeito_caixa, "
                      "fundamento, motivo_anulacao, anulado_por, anulado_em, criado_por, criado_em FROM unidades_movimentos "
                      + filtro + "ORDER BY data DESC, id DESC")
    if not df.empty and not eh_admin():
        # participante não-admin: vê apenas os seus próprios movimentos
        email = str(st.session_state.get("conta_email") or "").strip().lower()
        df = df[df["socio_email"].fillna("").str.lower() == email]
    return df


def registar_balanco(data_ref, dinheiro, outros, passivos, fonte, titularidade, estado="Provisório"):
    """Novo retrato do património (nunca se editam retratos antigos). 'Validado' só por decisão explícita do administrador."""
    exigir_admin()
    ant = obter_ultimo_balanco()
    val = estado == "Validado"
    with transaccao() as cur:
        cur.execute("INSERT INTO balanco_privado (data_ref, dinheiro_disponivel, outros_activos, passivos, fonte, titularidade, estado, origem, "
                    "criado_por, validado_por, validado_em) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
                    (data_ref, q2(dinheiro), q2(outros), q2(passivos), fonte, titularidade, estado, "Registo manual", utilizador_actual(),
                     utilizador_actual() if val else None, datetime.now() if val else None))
        novo_id = cur.fetchone()[0]
        registar_auditoria("Balanço registado", "balanco_privado", novo_id,
                           antes={"id": ant[0], "dinheiro": ant[2], "outros": ant[3], "passivos": ant[4], "estado": ant[7]} if ant else None,
                           depois={"dinheiro": q2(dinheiro), "outros": q2(outros), "passivos": q2(passivos), "estado": estado}, cur=cur)
    return novo_id


def validar_balanco(balanco_id: int, nota: str = ""):
    exigir_admin()
    with transaccao() as cur:
        cur.execute("UPDATE balanco_privado SET estado = 'Validado', validado_por = %s, validado_em = NOW() WHERE id = %s AND estado <> 'Validado'",
                    (utilizador_actual(), int(balanco_id)))
        registar_auditoria("Balanço validado", "balanco_privado", balanco_id, motivo=nota, cur=cur)


def registar_operacao_unidades(tipo, socio, socio_email, montante, classe, data_op, referencia, fundamento="", vup_historico=None) -> dict:
    """Subscrição ou resgate autorizado. Tudo numa transacção: calcula com o balanço validado anterior à operação, regista o
    movimento, o novo retrato do dinheiro disponível e a auditoria. Bloqueia execuções simultâneas e duplicações (referência única)."""
    exigir_admin()
    if tipo not in ("Subscrição", "Resgate"):
        raise ValueError("Operação inválida.")
    montante = q2(montante)
    if montante <= 0 or not str(socio or "").strip():
        raise ValueError("Indique o participante e um montante superior a zero.")
    if classe not in ("Fundadora", "Ordinária"):
        raise ValueError("Classe inválida.")
    hoje = datetime.now().date()
    if data_op > hoje:
        raise ValueError("A data da operação não pode ser futura.")
    if not str(referencia or "").strip():
        raise ValueError("Falta a referência da operação.")
    av = avaliar_carteira_real()
    with transaccao() as cur:
        cur.execute("SELECT limite_cotas, entrada_minima, unidades_base_validada FROM cotas_config WHERE id = 1 FOR UPDATE")
        c = cur.fetchone()
        limite, entrada_min, base_ok = dec(c[0] or 0), dec(c[1] or 0), bool(c[2])
        cur.execute("SELECT id, dinheiro_disponivel, outros_activos, passivos, estado, fonte, titularidade, data_ref FROM balanco_privado "
                    "ORDER BY data_ref DESC, id DESC LIMIT 1")
        bal = cur.fetchone()
        if not bal or bal[4] != "Validado":
            raise ValueError("O balanço mais recente não está validado: valide-o antes de emitir ou resgatar unidades.")
        if not base_ok:
            raise ValueError("A base de unidades ainda não está reconciliada e validada.")
        cur.execute("SELECT COALESCE(SUM(unidades), 0) FROM unidades_movimentos WHERE estado = 'Validado'")
        un_total = dec(cur.fetchone()[0])
        if un_total <= 0:
            raise ValueError("Não há unidades validadas em circulação.")
        dinheiro, outros, passivos = dec(bal[1]), dec(bal[2]), dec(bal[3])
        nav = q2(av["valor"] + dinheiro + outros - passivos)
        vup_hoje = q4(nav / un_total)
        if data_op < hoje:
            if not str(fundamento or "").strip() or vup_historico is None or dec(vup_historico) <= 0:
                raise ValueError("Data anterior a hoje: indique o valor da unidade aplicável nessa data e o fundamento (regularização).")
            vup_op, origem = q4(vup_historico), "Regularização"
        else:
            vup_op, origem = vup_hoje, "Operação autorizada"
        unidades = q6(montante / vup_op)
        if tipo == "Subscrição":
            if montante < entrada_min:
                raise ValueError(f"A entrada mínima é de {q2(entrada_min)} Kz.")
            if limite > 0 and un_total + unidades > limite:
                raise ValueError(f"A emissão levaria as unidades a {un_total + unidades} (limite pendente de formalização: {limite}). "
                                 "Ultrapassar o limite exige decisão documentada e, provavelmente, alteração do Estatuto.")
            sinal = 1
        else:
            cur.execute("SELECT COALESCE(SUM(unidades), 0) FROM unidades_movimentos WHERE estado = 'Validado' AND classe = %s "
                        "AND lower(trim(socio)) = lower(trim(%s))", (classe, socio))
            disponiveis = dec(cur.fetchone()[0])
            if unidades > disponiveis:
                raise ValueError(f"O participante tem {disponiveis} unidades {classe}s; o resgate pedido equivale a {unidades}.")
            if montante > dinheiro:
                raise ValueError("Liquidez insuficiente: o dinheiro disponível registado não cobre este resgate.")
            sinal = -1
        efeito = montante * sinal
        nav_dep, un_dep = q2(nav + efeito), un_total + sinal * unidades
        antes = {"nav": nav, "unidades": un_total, "vup": vup_hoje, "dinheiro": dinheiro}
        depois = {"nav": nav_dep, "unidades": un_dep, "vup": q4(nav_dep / un_dep) if un_dep > 0 else None, "dinheiro": dinheiro + efeito}
        import json as _json
        try:
            cur.execute("INSERT INTO unidades_movimentos (data, socio, socio_email, tipo, classe, estado, origem, referencia, fundamento, montante, vup, "
                        "unidades, efeito_caixa, criado_por, antes, depois) VALUES (%s, %s, %s, %s, %s, 'Validado', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
                        (data_op, socio.strip(), socio_email or None, tipo, classe, origem, referencia.strip(), fundamento or "",
                         montante * sinal, vup_op, unidades * sinal, efeito, utilizador_actual(),
                         _json.dumps(antes, default=str), _json.dumps(depois, default=str)))
        except psycopg2.errors.UniqueViolation:
            raise ValueError("Operação duplicada: esta referência já foi utilizada.")
        mov_id = cur.fetchone()[0]
        cur.execute("INSERT INTO balanco_privado (data_ref, dinheiro_disponivel, outros_activos, passivos, fonte, titularidade, estado, origem, "
                    "criado_por, validado_por, validado_em) VALUES (%s, %s, %s, %s, %s, %s, 'Validado', %s, %s, %s, NOW())",
                    (hoje, q2(dinheiro + efeito), q2(outros), q2(passivos), bal[5], bal[6], f"Derivado da operação {referencia.strip()}",
                     utilizador_actual(), utilizador_actual()))
        registar_auditoria(f"{tipo} de unidades", "unidades_movimentos", mov_id, antes=antes, depois=depois, motivo=fundamento or "", cur=cur)
    return {"id": mov_id, "unidades": unidades, "vup": vup_op, "origem": origem, "antes": antes, "depois": depois}


def anular_movimento_unidades(mov_id: int, motivo: str):
    """Anulação (estorno) com motivo, responsável e data. Nunca apaga. Se o movimento teve efeito em caixa, regista o estorno do dinheiro."""
    exigir_admin()
    if not str(motivo or "").strip():
        raise ValueError("Indique o motivo da anulação.")
    with transaccao() as cur:
        cur.execute("SELECT 1 FROM cotas_config WHERE id = 1 FOR UPDATE")
        cur.execute("SELECT id, socio, classe, estado, unidades, efeito_caixa, referencia FROM unidades_movimentos WHERE id = %s", (int(mov_id),))
        m = cur.fetchone()
        if not m:
            raise ValueError("Movimento não encontrado.")
        if m[3] == "Anulado":
            raise ValueError("O movimento já está anulado.")
        cur.execute("UPDATE unidades_movimentos SET estado = 'Anulado', motivo_anulacao = %s, anulado_por = %s, anulado_em = NOW() WHERE id = %s",
                    (motivo.strip(), utilizador_actual(), int(mov_id)))
        cur.execute("SELECT COALESCE(SUM(unidades), 0) FROM unidades_movimentos WHERE estado = 'Validado' AND classe = %s "
                    "AND lower(trim(socio)) = lower(trim(%s))", (m[2], m[1]))
        if dec(cur.fetchone()[0]) < 0:
            raise ValueError("A anulação deixaria o participante com unidades negativas; anule primeiro os movimentos posteriores.")
        efeito = dec(m[5]) if m[5] is not None else D(0)
        if efeito != 0:
            cur.execute("SELECT dinheiro_disponivel, outros_activos, passivos, fonte, titularidade FROM balanco_privado ORDER BY data_ref DESC, id DESC LIMIT 1")
            b = cur.fetchone()
            cur.execute("INSERT INTO balanco_privado (data_ref, dinheiro_disponivel, outros_activos, passivos, fonte, titularidade, estado, origem, "
                        "criado_por, validado_por, validado_em) VALUES (%s, %s, %s, %s, %s, %s, 'Validado', %s, %s, %s, NOW())",
                        (datetime.now().date(), q2(dec(b[0]) - efeito), q2(dec(b[1])), q2(dec(b[2])), b[3], b[4],
                         f"Estorno do movimento {m[6]}", utilizador_actual(), utilizador_actual()))
        registar_auditoria("Movimento de unidades anulado", "unidades_movimentos", mov_id, antes={"estado": m[3]}, depois={"estado": "Anulado"},
                           motivo=motivo.strip(), cur=cur)


def validar_movimento_unidades(mov_id: int, fundamento: str):
    """Aceita um movimento 'Por rever' (acordo/estimativa) como base de unidades. Não cria nem move dinheiro."""
    exigir_admin()
    if not str(fundamento or "").strip():
        raise ValueError("Indique o fundamento da validação (documento, acordo, contribuição comprovada...).")
    with transaccao() as cur:
        cur.execute("UPDATE unidades_movimentos SET estado = 'Validado', fundamento = %s WHERE id = %s AND estado = 'Por rever'", (fundamento.strip(), int(mov_id)))
        if cur.rowcount != 1:
            raise ValueError("Só movimentos 'Por rever' podem ser validados.")
        registar_auditoria("Movimento de unidades validado", "unidades_movimentos", mov_id, antes={"estado": "Por rever"},
                           depois={"estado": "Validado"}, motivo=fundamento.strip(), cur=cur)


def corrigir_movimento_unidades(mov_id: int, data, socio: str, montante: float, vup: float, classe: str):
    """Corrige um movimento ainda 'Por rever' (os validados corrigem-se anulando e registando de novo). Auditado."""
    exigir_admin()
    if float(vup) <= 0 or float(montante) <= 0 or not str(socio or "").strip():
        raise ValueError("Indique participante, montante e valor da unidade superiores a zero.")
    with transaccao() as cur:
        cur.execute("SELECT data, socio, montante, vup, unidades, classe, estado FROM unidades_movimentos WHERE id = %s", (int(mov_id),))
        a = cur.fetchone()
        if not a or a[6] != "Por rever":
            raise ValueError("Só movimentos 'Por rever' podem ser corrigidos.")
        m = q2(montante)
        un = q6(m / q4(vup))
        cur.execute("UPDATE unidades_movimentos SET data=%s, socio=%s, montante=%s, vup=%s, unidades=%s, classe=%s WHERE id=%s",
                    (data, socio.strip(), m, q4(vup), un, classe, int(mov_id)))
        registar_auditoria("Movimento de unidades corrigido", "unidades_movimentos", mov_id,
                           antes={"data": a[0], "socio": a[1], "montante": a[2], "vup": a[3], "unidades": a[4], "classe": a[5]},
                           depois={"data": data, "socio": socio, "montante": m, "vup": q4(vup), "unidades": un, "classe": classe}, cur=cur)


def adoptar_estrutura_inicial(linhas: list, valor_nominal: float, data_base, fundamento: str, base_reconciliada: bool):
    """Adopta a estrutura de unidades como REORGANIZAÇÃO (não é entrada de dinheiro e não cria movimentos financeiros).
    Só é possível enquanto não houver unidades validadas. Exige fundamento documentado."""
    exigir_admin()
    if not str(fundamento or "").strip():
        raise ValueError("Indique o fundamento da adopção da estrutura (acta, acordo, critério usado).")
    if not linhas:
        raise ValueError("Não há linhas para registar.")
    with transaccao() as cur:
        cur.execute("SELECT 1 FROM cotas_config WHERE id = 1 FOR UPDATE")
        cur.execute("SELECT COUNT(*) FROM unidades_movimentos WHERE estado = 'Validado'")
        if cur.fetchone()[0] > 0:
            raise ValueError("Já existem unidades validadas: a estrutura inicial só se adopta uma vez.")
        for i, r in enumerate(linhas, start=1):
            ref = f"REORG-{data_base:%Y%m%d}-{i}"
            try:
                cur.execute("INSERT INTO unidades_movimentos (data, socio, socio_email, tipo, classe, estado, origem, referencia, fundamento, montante, vup, "
                            "unidades, efeito_caixa, criado_por) VALUES (%s, %s, %s, 'Reorganização inicial', 'Fundadora', 'Validado', 'Reorganização inicial', %s, %s, %s, %s, %s, 0, %s)",
                            (data_base, r["socio"], r["email"], ref, fundamento.strip(), q2(r["montante"]), q4(valor_nominal), q6(r["cotas"]), utilizador_actual()))
            except psycopg2.errors.UniqueViolation:
                raise ValueError("Esta estrutura já foi registada com a mesma data-base.")
        cur.execute("UPDATE cotas_config SET data_base = %s, fundamento_base = %s, unidades_base_validada = %s, valor_nominal = %s WHERE id = 1",
                    (data_base, fundamento.strip(), bool(base_reconciliada), q4(valor_nominal)))
        registar_auditoria("Estrutura inicial de unidades adoptada", "cotas_config", 1,
                           depois={"data_base": data_base, "linhas": [(r["socio"], r["montante"], r["cotas"]) for r in linhas],
                                   "base_reconciliada": bool(base_reconciliada)}, motivo=fundamento.strip(), cur=cur)


def definir_base_reconciliada(valor: bool, nota: str):
    exigir_admin()
    executar("UPDATE cotas_config SET unidades_base_validada = %s WHERE id = 1", (bool(valor),))
    registar_auditoria("Base de unidades " + ("reconciliada" if valor else "marcada como não reconciliada"), "cotas_config", 1, motivo=nota)


def secao_vup_inicio():
    """Cartões, participação pessoal e evolução do VUP, na página Início. Não aparece enquanto não houver unidades."""
    try:
        info = obter_vup_info()
    except Exception:
        return
    if info["unidades"] <= 0 or info["vup"] <= 0:
        return
    rent = (info["vup"] / info["vup_base"] - 1) * 100 if info["vup_base"] > 0 else 0.0
    st.divider()
    st.subheader("📐 Valor da Cota (VUP)")
    c1, c2, c3 = st.columns(3)
    c1.metric("VUP actual", f"{kz2(info['vup'])} Kz")
    c2.metric("Rentabilidade desde o início", pct_bruto(rent), delta=pct_bruto(rent))
    c3.metric("Valor líquido global", kz(info["vlg"]))
    st.caption("O VUP é o preço de uma cota do Clube: o valor líquido (carteira a preços de mercado mais reservas de liquidez) "
               "dividido pelas cotas em circulação. É a referência para novas entradas e saídas de sócios.")
    email = str(st.session_state.get("conta_email", "") or "").strip().lower()
    if email:
        mov = obter_unidades_movimentos()
        meu = mov[mov["socio_email"].fillna("").str.lower() == email] if not mov.empty else mov
        if not meu.empty and float(meu["unidades"].sum()) > 0:
            un_m, ap_m = float(meu["unidades"].sum()), float(meu["montante"].sum())
            val_m = un_m * info["vup"]
            st.markdown("**A minha participação**")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Cotas", f"{un_m:,.2f}".replace(",", " "))
            m2.metric("Valor actual", kz(val_m))
            m3.metric("Capital aportado (líquido)", kz(ap_m))
            m4.metric("Ganho / perda", kz(val_m - ap_m), delta=pct_bruto((val_m / ap_m - 1) * 100) if ap_m > 0 else None)
            st.caption(f"Detém {un_m / info['unidades'] * 100:.2f}% das cotas do Clube.")
    periodo_vup = st.radio("Período", PERIODOS_GRAFICO, index=3, horizontal=True, key="vup_periodo")
    painel_grafico("Valor da cota (VUP)", "Kz por cota", obter_serie_vup(periodo_vup), "Kz", periodo_vup)


def _pdf_kpis_vup(pdf, info):
    """Faixa de quatro indicadores: valor líquido, unidades, VUP e rentabilidade desde o início."""
    rent = (info["vup"] / info["vup_base"] - 1) * 100 if info["vup_base"] > 0 else 0.0
    itens = [("Valor líquido global", kz(info["vlg"])),
             ("Cotas em circulação", f"{info['unidades']:,.2f}".replace(",", " ").replace(".", ",")),
             ("Valor da cota (VUP)", kz2(info["vup"]) + " Kz"),
             ("Rentabilidade desde o início", pct_bruto(rent))]
    x0, largura = pdf.l_margin, pdf.w - pdf.l_margin - pdf.r_margin
    w = (largura - 3 * 4) / 4
    y = pdf.get_y() + 1
    for i, (rot, val) in enumerate(itens):
        x = x0 + i * (w + 4)
        pdf.set_fill_color(244, 236, 239)
        pdf.rect(x, y, w, 15, style="F")
        pdf.set_fill_color(124, 31, 62)
        pdf.rect(x, y, 1.2, 15, style="F")
        pdf.set_xy(x + 3, y + 1.5)
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(110, 110, 110)
        pdf.cell(w - 4, 4, rot)
        pdf.set_xy(x + 3, y + 6.5)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(124, 31, 62)
        pdf.cell(w - 4, 6, val)
    pdf.set_y(y + 19)
    pdf.set_text_color(0, 0, 0)


# ---------------- Movimentos ----------------
def inserir_movimento(tipo, descricao, montante, data_movimento):
    exigir_admin()
    executar("INSERT INTO movimentos (tipo, descricao, montante, data_movimento) VALUES (%s, %s, %s, %s)", (tipo, descricao, montante, data_movimento))

def obter_movimentos() -> pd.DataFrame:
    exigir_participante()
    return consultar_df("SELECT tipo, descricao, montante, data_movimento, criado_em FROM movimentos ORDER BY data_movimento DESC, criado_em DESC")


# ---------------- Activos + Favoritos + Índice ----------------
def obter_activos() -> pd.DataFrame:
    return consultar_df(
        "SELECT id, ticker, nome, tipo, preco, variacao, "
        "preco_abertura_dia, data_abertura_dia, actualizado_em "
        "FROM activos ORDER BY nome")


def obter_estado_simulador(email: str):
    """Carrega (ou cria, se for a 1ª vez) o saldo, carteira e histórico
    persistidos deste sócio no Simulador de Investimento."""
    if not email:
        return 3_000_000.0, {}, []

    linha = consultar_um("SELECT saldo_caixa FROM sim_estado WHERE conta_email = %s", (email,))
    if linha is None:
        executar("INSERT INTO sim_estado (conta_email, saldo_caixa) VALUES (%s, %s)", (email, 3_000_000.0))
        saldo = 3_000_000.0
    else:
        saldo = float(linha[0])

    df_pos = consultar_df(
        "SELECT ticker, nome, qtd, preco_medio FROM sim_posicoes WHERE conta_email = %s", (email,))
    carteira = {
        str(r["ticker"]): {"qtd": float(r["qtd"]), "preco_medio": float(r["preco_medio"]), "nome": str(r["nome"])}
        for _, r in df_pos.iterrows()
    }

    df_hist = consultar_df(
        'SELECT operacao AS "Operação", ticker AS "Ticker", qtd AS "Qtd", '
        'preco_unit AS "Preço Unit.", total AS "Total" FROM sim_historico '
        "WHERE conta_email = %s ORDER BY id DESC LIMIT 200", (email,))
    historico = df_hist.to_dict("records") if not df_hist.empty else []

    return saldo, carteira, historico


def guardar_saldo_simulador(email: str, saldo: float):
    if email:
        executar("UPDATE sim_estado SET saldo_caixa = %s WHERE conta_email = %s", (saldo, email))


def guardar_posicao_simulador(email: str, ticker: str, dados):
    """dados=None remove a posição (venda total deste activo)."""
    if not email or not ticker:
        return
    if dados is None:
        executar("DELETE FROM sim_posicoes WHERE conta_email = %s AND ticker = %s", (email, ticker))
    else:
        executar("""
            INSERT INTO sim_posicoes (conta_email, ticker, nome, qtd, preco_medio)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (conta_email, ticker)
            DO UPDATE SET nome = EXCLUDED.nome, qtd = EXCLUDED.qtd, preco_medio = EXCLUDED.preco_medio
        """, (email, ticker, dados["nome"], dados["qtd"], dados["preco_medio"]))


def registar_operacao_simulador(email: str, operacao: str, ticker: str, qtd: float, preco_unit: float, total: float):
    if email:
        executar(
            "INSERT INTO sim_historico (conta_email, operacao, ticker, qtd, preco_unit, total) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (email, operacao, ticker, qtd, preco_unit, total))


def reiniciar_simulador_db(email: str):
    if email:
        executar("DELETE FROM sim_posicoes WHERE conta_email = %s", (email,))
        executar("DELETE FROM sim_historico WHERE conta_email = %s", (email,))
        executar("UPDATE sim_estado SET saldo_caixa = 3000000 WHERE conta_email = %s", (email,))


# ---------------- Exportação para Excel (formatada, nas cores do Clube) ----------------
def xlsx_disponivel() -> bool:
    try:
        import openpyxl  # noqa: F401
        return True
    except ImportError:
        return False


def _xlsx_estilos():
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    lado = Side(style="thin", color="E3D2D8")
    return {
        "borda": Border(left=lado, right=lado, top=lado, bottom=lado),
        "f_bord": PatternFill("solid", fgColor="7C1F3E"),
        "f_bord_esc": PatternFill("solid", fgColor="5E1830"),
        "f_claro": PatternFill("solid", fgColor="F4ECEF"),
        "f_creme": PatternFill("solid", fgColor="FBF8F6"),
        "f_branco": PatternFill("solid", fgColor="FFFFFF"),
        "Font": Font, "Alignment": Alignment,
    }


def _xlsx_banner(ws, ncols: int, titulo: str, subtitulo: str):
    """Faixa institucional (3 linhas) + título do documento; devolve a próxima linha livre."""
    from openpyxl.utils import get_column_letter
    e = _xlsx_estilos()
    ultima = get_column_letter(ncols)
    textos = [
        ("CLUBE DE INVESTIMENTO APPO", e["Font"](name="Calibri", size=18, bold=True, color="FFFFFF"), e["f_bord"], 30),
        ("Casa nº 5 - Zona C, Av. Ministro Vieira Machado, Benguela, Angola  |  NIF: 001669404BA035  |  "
         "Tel.: 940 762 278 / 937 696 088  |  clube.investimento.appo@gmail.com",
         e["Font"](name="Calibri", size=8, color="F4ECEF"), e["f_bord"], 16),
        (titulo, e["Font"](name="Calibri", size=13, bold=True, color="7C1F3E"), e["f_claro"], 26),
    ]
    for i, (txt, fonte, fundo, alt) in enumerate(textos, start=1):
        ws.merge_cells(f"A{i}:{ultima}{i}")
        c = ws[f"A{i}"]
        c.value, c.font, c.fill = txt, fonte, fundo
        c.alignment = e["Alignment"](horizontal="left", vertical="center", indent=1)
        for col in range(1, ncols + 1):
            ws.cell(row=i, column=col).fill = fundo
        ws.row_dimensions[i].height = alt
    ws.merge_cells(f"A4:{ultima}4")
    ws["A4"].value = subtitulo
    ws["A4"].font = e["Font"](name="Calibri", size=9, italic=True, color="6B6B6B")
    ws["A4"].alignment = e["Alignment"](horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[4].height = 18
    ws.sheet_view.showGridLines = False
    return 6


def _xlsx_rodape(ws, linha: int, ncols: int, nota: str = ""):
    from openpyxl.utils import get_column_letter
    e = _xlsx_estilos()
    ultima = get_column_letter(ncols)
    if nota:
        ws.merge_cells(f"A{linha}:{ultima}{linha}")
        ws[f"A{linha}"].value = nota
        ws[f"A{linha}"].font = e["Font"](name="Calibri", size=8, italic=True, color="6B6B6B")
        ws[f"A{linha}"].alignment = e["Alignment"](wrap_text=True, vertical="top", indent=1)
        ws.row_dimensions[linha].height = 36
        linha += 1
    ws.merge_cells(f"A{linha}:{ultima}{linha}")
    ws[f"A{linha}"].value = "Documento gerado automaticamente pela plataforma APPO. Uso interno e reservado."
    ws[f"A{linha}"].font = e["Font"](name="Calibri", size=8, italic=True, color="9A9A9A")
    ws[f"A{linha}"].alignment = e["Alignment"](horizontal="center")
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.oddFooter.center.text = "Clube de Investimento APPO  |  Página &P de &N"


def _xlsx_cor_sinal(ws, intervalos, positivo_bom=True):
    """Texto verde para valores > 0 e vermelho para < 0 (ou o inverso), por formatação condicional."""
    from openpyxl.formatting.rule import CellIsRule
    from openpyxl.styles import Font
    verde, verm = Font(color="16A34A", bold=True), Font(color="DC2626", bold=True)
    for ref in intervalos:
        ws.conditional_formatting.add(ref, CellIsRule(operator="greaterThan", formula=["0"], font=verde if positivo_bom else verm))
        ws.conditional_formatting.add(ref, CellIsRule(operator="lessThan", formula=["0"], font=verm if positivo_bom else verde))


def gerar_xlsx_tabela(titulo, subtitulo, colunas, linhas, larguras, formatos, folha="Dados", nota="", cor_cond=()) -> bytes:
    """Tabela institucional: faixa do Clube, cabeçalho bordeaux, linhas alternadas, filtros e painel fixo."""
    import io
    from openpyxl import Workbook
    from openpyxl.utils import get_column_letter
    e = _xlsx_estilos()
    wb = Workbook()
    ws = wb.active
    ws.title = folha[:31]
    n = len(colunas)
    for i, w in enumerate(larguras, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    cab = _xlsx_banner(ws, n, titulo, subtitulo)
    for j, nome in enumerate(colunas, start=1):
        c = ws.cell(row=cab, column=j, value=nome)
        c.font = e["Font"](name="Calibri", size=10, bold=True, color="FFFFFF")
        c.fill, c.border = e["f_bord"], e["borda"]
        c.alignment = e["Alignment"](horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[cab].height = 30
    for i, linha in enumerate(linhas):
        r = cab + 1 + i
        fundo = e["f_creme"] if i % 2 else e["f_branco"]
        for j, valor in enumerate(linha, start=1):
            c = ws.cell(row=r, column=j, value=("n/d" if valor is None else valor))
            c.fill, c.border = fundo, e["borda"]
            c.font = e["Font"](name="Calibri", size=10, color="1A1A2E")
            eh_num = isinstance(valor, (int, float)) and not isinstance(valor, bool)
            if formatos[j - 1] and (eh_num or hasattr(valor, "year")):
                c.number_format = formatos[j - 1]
            c.alignment = e["Alignment"](horizontal="right" if eh_num else ("center" if valor is None else "left"),
                                         vertical="center", indent=0 if eh_num else 1)
        ws.row_dimensions[r].height = 20
    ultima_linha = cab + len(linhas)
    ws.freeze_panes = ws.cell(row=cab + 1, column=1)
    if linhas:
        ws.auto_filter.ref = f"A{cab}:{get_column_letter(n)}{ultima_linha}"
        _xlsx_cor_sinal(ws, [f"{get_column_letter(j)}{cab + 1}:{get_column_letter(j)}{ultima_linha}" for j in cor_cond])
    _xlsx_rodape(ws, ultima_linha + 2, n, nota)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def gerar_xlsx_cotacoes(df) -> bytes:
    colunas = ["Ticker", "Título", "Tipo", "Cotação (Kz)", "Variação diária (%)", "Última actualização"]
    verde_verm = '+0.00"%";-0.00"%";0.00"%"'
    linhas = []
    for _, r in df.iterrows():
        act = r.get("actualizado_em")
        try:
            act = act.to_pydatetime().replace(tzinfo=None)
        except Exception:
            act = None
        linhas.append([str(r.get("ticker") or ""), str(r["nome"]), str(r["tipo"]), float(r["preco"]), float(r["variacao"]), act])
    from datetime import datetime as _dt
    base = gerar_xlsx_tabela(
        "Cotações da BODIVA - Carteira de Activos Seguidos", f"Gerado em {_dt.now():%d/%m/%Y %H:%M}  |  Fonte: BODIVA (actualização pelo administrador)",
        colunas, linhas, [14, 44, 12, 16, 18, 22], [None, None, None, '#,##0.00', verde_verm, "dd/mm/yyyy hh:mm"], folha="Cotações", cor_cond=(5,),
        nota="Cotações em kwanzas (Kz). A variação diária compara a última cotação com a de abertura do dia.")
    return base


def gerar_xlsx_comparacao(linhas) -> bytes:
    """linhas: [empresa, sector, pe, pbv, roe, dy_nominal, upside] com valores numéricos (fracções) ou None."""
    from datetime import datetime as _dt
    colunas = ["Empresa", "Sector", "P/E (x)", "P/BV (x)", "ROE", "Dividend Yield nominal", "Upside DDM"]
    verde_verm = '+0.00%;-0.00%;0.00%'
    return gerar_xlsx_tabela(
        "Comparação Sectorial - Avaliação de Activos", f"Gerado em {_dt.now():%d/%m/%Y %H:%M}  |  Modelo de avaliação do Clube (DDM)",
        colunas, linhas, [26, 30, 12, 12, 14, 20, 16],
        [None, None, '0.00"x"', '0.00"x"', verde_verm, '0.00%', verde_verm], folha="Comparação sectorial", cor_cond=(5, 7),
        nota="P/E = preço sobre lucro; P/BV = preço sobre valor contabilístico; ROE = rentabilidade do capital próprio; "
             "Upside DDM = diferença entre o valor justo estimado e o preço de mercado. O DDM depende das premissas "
             "de crescimento (g) e custo de capital (Ke): use-o como referência, não como verdade absoluta.")


def gerar_xlsx_orcamento(df_rec, df_desp, categorias) -> bytes:
    """Orçamento mensal com fórmulas vivas (somas, % das receitas, comparação 50/30/20) e linhas extra para preencher."""
    import io
    from datetime import datetime as _dt
    from openpyxl import Workbook
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation
    e = _xlsx_estilos()
    wb = Workbook()
    ws = wb.active
    ws.title = "Orçamento mensal"
    larg = [40, 26, 18, 18, 18, 18]
    n = len(larg)
    for i, w in enumerate(larg, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    r = _xlsx_banner(ws, n, "Orçamento Mensal Pessoal ou Familiar - Princípio 50/30/20",
                     f"Gerado em {_dt.now():%d/%m/%Y %H:%M}  |  Pode editar os valores a azul: as somas e comparações actualizam-se sozinhas.")
    FMT = '#,##0'
    entrada = e["Font"](name="Calibri", size=10, color="1F4E9E")
    normal = e["Font"](name="Calibri", size=10, color="1A1A2E")
    negrito = e["Font"](name="Calibri", size=10, bold=True, color="7C1F3E")

    def seccao(linha, texto):
        ws.merge_cells(f"A{linha}:{get_column_letter(n)}{linha}")
        c = ws[f"A{linha}"]
        c.value, c.font, c.fill = texto, e["Font"](name="Calibri", size=11, bold=True, color="FFFFFF"), e["f_bord"]
        c.alignment = e["Alignment"](vertical="center", indent=1)
        for col in range(1, n + 1):
            ws.cell(row=linha, column=col).fill = e["f_bord"]
        ws.row_dimensions[linha].height = 22

    def cabecalho(linha, nomes):
        for j, nome in enumerate(nomes, start=1):
            c = ws.cell(row=linha, column=j, value=nome)
            c.font = e["Font"](name="Calibri", size=10, bold=True, color="7C1F3E")
            c.fill, c.border = e["f_claro"], e["borda"]
            c.alignment = e["Alignment"](horizontal="center", vertical="center", wrap_text=True)
        ws.row_dimensions[linha].height = 26

    def celula(linha, col, valor, fonte=normal, fmt=None, num=False, zebra=0):
        c = ws.cell(row=linha, column=col, value=valor)
        c.font, c.border = fonte, e["borda"]
        c.fill = e["f_creme"] if zebra % 2 else e["f_branco"]
        if fmt:
            c.number_format = fmt
        c.alignment = e["Alignment"](horizontal="right" if num else "left", vertical="center", indent=0 if num else 1)
        return c

    EXTRA = 4
    # 1. Receitas
    seccao(r, "1. RECEITAS DO MÊS")
    r += 1
    cabecalho(r, ["Descrição", "Tipo", "Valor (Kz)"])
    r += 1
    rec_ini = r
    recs = [(str(x["Descrição"] or ""), x["Valor (Kz)"]) for _, x in df_rec.iterrows()
            if str(x["Descrição"] or "").strip() or (x["Valor (Kz)"] == x["Valor (Kz)"] and x["Valor (Kz)"])]
    for i in range(len(recs) + EXTRA):
        d, v = recs[i] if i < len(recs) else ("", None)
        celula(r, 1, d or None, entrada, zebra=i)
        celula(r, 2, "Receita", normal, zebra=i)
        celula(r, 3, (float(v) if v == v and v is not None else None), entrada, FMT, True, zebra=i)
        r += 1
    rec_fim = r - 1
    celula(r, 1, "TOTAL DE RECEITAS", negrito); celula(r, 2, None, negrito)
    celula(r, 3, f"=SUM(C{rec_ini}:C{rec_fim})", negrito, FMT, True)
    for col in (1, 2, 3):
        ws.cell(row=r, column=col).fill = e["f_claro"]
    tot_rec = f"$C${r}"
    r += 2

    # 2. Despesas
    seccao(r, "2. DESPESAS E POUPANÇA DO MÊS")
    r += 1
    cabecalho(r, ["Descrição", "Categoria", "Valor (Kz)", "% das receitas"])
    r += 1
    des_ini = r
    desp = [(str(x["Categoria"] or ""), str(x["Descrição"] or ""), x["Valor (Kz)"]) for _, x in df_desp.iterrows()
            if str(x["Descrição"] or "").strip() or (x["Valor (Kz)"] == x["Valor (Kz)"] and x["Valor (Kz)"])]
    for i in range(len(desp) + EXTRA):
        cat, d, v = desp[i] if i < len(desp) else ("", "", None)
        celula(r, 1, d or None, entrada, zebra=i)
        celula(r, 2, cat or None, entrada, zebra=i)
        celula(r, 3, (float(v) if v == v and v is not None else None), entrada, FMT, True, zebra=i)
        celula(r, 4, f"=IF(AND({tot_rec}>0,C{r}<>\"\"),C{r}/{tot_rec},\"\")", normal, "0.0%", True, zebra=i)
        r += 1
    des_fim = r - 1
    dv = DataValidation(type="list", formula1='"' + ",".join(categorias) + '"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"B{des_ini}:B{des_fim}")
    celula(r, 1, "TOTAL DE DESPESAS E POUPANÇA", negrito); celula(r, 2, None, negrito)
    celula(r, 3, f"=SUM(C{des_ini}:C{des_fim})", negrito, FMT, True)
    celula(r, 4, f"=IF({tot_rec}>0,C{r}/{tot_rec},\"\")", negrito, "0.0%", True)
    for col in (1, 2, 3, 4):
        ws.cell(row=r, column=col).fill = e["f_claro"]
    tot_des = f"$C${r}"
    r += 2

    # 3. Resultado
    seccao(r, "3. RESULTADO - COMPARAÇÃO COM A REGRA 50/30/20")
    r += 1
    cabecalho(r, ["Categoria", "Meta (% das receitas)", "Meta (Kz)", "O seu orçamento (Kz)", "Diferença (Kz)", "Orçamento (% das receitas)"])
    r += 1
    metas = [0.50, 0.30, 0.20]
    for i, (cat, meta) in enumerate(zip(categorias, metas)):
        celula(r, 1, cat, normal, zebra=i)
        celula(r, 2, meta, normal, "0%", True, zebra=i)
        celula(r, 3, f"={tot_rec}*B{r}", normal, FMT, True, zebra=i)
        celula(r, 4, f"=SUMIF($B${des_ini}:$B${des_fim},A{r},$C${des_ini}:$C${des_fim})", normal, FMT, True, zebra=i)
        celula(r, 5, f"=D{r}-C{r}", normal, '+#,##0;-#,##0;0', True, zebra=i)
        _xlsx_cor_sinal(ws, [f"E{r}"], positivo_bom=(i != 0))
        celula(r, 6, f"=IF({tot_rec}>0,D{r}/{tot_rec},\"\")", normal, "0.0%", True, zebra=i)
        r += 1
    celula(r, 1, "SALDO POR ALOCAR (receitas - despesas e poupança)", negrito)
    for col in (2, 3, 5, 6):
        celula(r, col, None, negrito)
    celula(r, 4, f"={tot_rec}-{tot_des}", negrito, '#,##0;-#,##0;0', True)
    _xlsx_cor_sinal(ws, [f"D{r}"])
    for col in range(1, 7):
        ws.cell(row=r, column=col).fill = e["f_claro"]
    r += 2
    _xlsx_rodape(ws, r, n, "Consumo: ideal até 50% das receitas (diferença positiva = a gastar acima da meta). "
                           "Investimento (30%) e Entesouramento (20%): metas mínimas de poupança (diferença negativa = falta poupar).")
    ws.freeze_panes = "A6"
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _xlsx_seguro(funcao):
    """Corre a geração do Excel sem nunca deixar a página falhar: devolve bytes ou None."""
    try:
        if not xlsx_disponivel():
            st.warning("Excel indisponível: falta a biblioteca openpyxl no servidor (adiciona 'openpyxl' ao requirements.txt). Usa o CSV como alternativa.")
            return None
        return funcao()
    except Exception as _e_xl:
        traceback.print_exc()
        st.warning(f"Não foi possível gerar o Excel agora ({type(_e_xl).__name__}: {_e_xl}). Usa o CSV como alternativa.")
        return None


ORC_CATEGORIAS = ["Consumo (50%)", "Investimento (30%)", "Entesouramento (20%)"]


def orcamento_modelo_inicial() -> dict:
    """Modelo de orçamento mensal pré-preenchido (valores a 0, para o sócio preencher)."""
    return {
        "receitas": [
            {"Descrição": "Salário / rendimento principal", "Valor (Kz)": 0.0},
            {"Descrição": "Outras receitas", "Valor (Kz)": 0.0},
        ],
        "despesas": [
            {"Categoria": ORC_CATEGORIAS[0], "Descrição": d, "Valor (Kz)": 0.0}
            for d in ["Renda de casa", "Alimentação", "Transporte", "Energia e água",
                      "Telecomunicações", "Saúde", "Educação", "Lazer e outros"]
        ] + [
            {"Categoria": ORC_CATEGORIAS[1], "Descrição": "Acções / investimentos (BODIVA)", "Valor (Kz)": 0.0},
            {"Categoria": ORC_CATEGORIAS[2], "Descrição": "Fundo de emergência / poupança", "Valor (Kz)": 0.0},
        ],
    }


def obter_orcamento(email: str) -> dict:
    import json as _json
    modelo = orcamento_modelo_inicial()
    if not email:
        return modelo
    linha = consultar_um("SELECT dados FROM orcamento_pessoal WHERE conta_email = %s", (email,))
    if not linha:
        return modelo
    try:
        d = _json.loads(linha[0])
        if isinstance(d.get("receitas"), list) and isinstance(d.get("despesas"), list):
            return d
    except (ValueError, TypeError):
        pass
    return modelo


def guardar_orcamento(email: str, dados: dict):
    import json as _json
    if not email:
        return
    executar(
        "INSERT INTO orcamento_pessoal (conta_email, dados) VALUES (%s, %s) "
        "ON CONFLICT (conta_email) DO UPDATE SET dados = EXCLUDED.dados, actualizado_em = NOW()",
        (email, _json.dumps(dados, ensure_ascii=False, default=float)))


def obter_carteira_real() -> pd.DataFrame:
    """Posições reais do Clube (dinheiro verdadeiro), para o relatório PDF. Só participantes."""
    exigir_participante()
    return consultar_df(
        "SELECT id, ticker, nome, qtd, valor_aquisicao, actualizado_em "
        "FROM carteira_real ORDER BY nome")


def substituir_carteira_real(df: pd.DataFrame):
    """
    Substitui a carteira real do Clube a partir da tabela editada pelo admin.
    Cada linha é uma posição: ticker, nome, quantidade de acções detidas, e o
    valor TOTAL pago na aquisição (não o preço unitário — o relatório divide
    por qtd para obter o preço médio, tal como fazia o dicionário fixo antigo).
    """
    exigir_admin()
    executar("DELETE FROM carteira_real")
    for _, linha in df.iterrows():
        nome = str(linha.get("nome", "")).strip()
        if not nome:
            continue
        ticker = str(linha.get("ticker", "") or "").strip().upper()
        qtd    = _num_seguro(linha.get("qtd"), default=0.0)
        val_aq = _num_seguro(linha.get("valor_aquisicao"), default=0.0)
        executar(
            "INSERT INTO carteira_real (ticker, nome, qtd, valor_aquisicao) VALUES (%s, %s, %s, %s)",
            (ticker, nome, qtd, val_aq))

def _eh_accao(tipo) -> bool:
    """Reconhece 'Ação', 'ACÇÃO', 'Acção', 'Acao', 'Ações'... (a tabela de cotações usa 'ACÇÃO')."""
    import unicodedata
    n = "".join(c for c in unicodedata.normalize("NFKD", str(tipo or "")) if not unicodedata.combining(c)).upper().strip()
    return n.startswith("AC") and (n.endswith("AO") or n.endswith("OES"))


def calcular_indice_mercado(df_activos: pd.DataFrame) -> float:
    acoes = df_activos[df_activos["tipo"].apply(_eh_accao)] if not df_activos.empty else df_activos
    return float(acoes["variacao"].mean()) if not acoes.empty else 0.0

def registar_historico_indice(valor: float):
    hoje = datetime.now().date()
    executar("INSERT INTO historico_indice_mercado (registado_em, indice_variacao) VALUES (%s, %s) ON CONFLICT (registado_em) DO UPDATE SET indice_variacao = EXCLUDED.indice_variacao",
             (hoje, valor))

def obter_historico_indice() -> pd.DataFrame:
    return consultar_df("SELECT indice_variacao, registado_em FROM historico_indice_mercado ORDER BY registado_em")

def _num_seguro(valor, default=0.0):
    """Converte para float de forma segura; nunca lança excepção, nunca devolve NaN."""
    try:
        v = float(valor)
    except (TypeError, ValueError):
        return default
    return default if v != v else v  # v != v só é True quando v é NaN


def substituir_activos(df: pd.DataFrame):
    """
    Substitui a tabela de activos, recalculando a variação % de cada um face
    ao PREÇO DE ABERTURA DO DIA — a mesma convenção da BFA/BODIVA: a "variação
    diária" só muda quando o dia civil muda, nunca simplesmente por o admin ter
    voltado a gravar a tabela (esse era o motivo real do "zera tudo": a versão
    anterior comparava sempre com a última gravação, não com a abertura do dia).

    Regra por activo (identificado pelo ticker):
      - Se é a primeira vez que este ticker aparece, ou se a sua última
        referência de abertura é de um dia diferente de hoje: hoje começa um
        novo "dia de referência" — o preço de abertura de hoje passa a ser o
        último preço conhecido deste activo ANTES desta gravação.
      - Se já houve uma gravação hoje para este activo, a abertura do dia
        MANTÉM-SE (não se move a cada gravação) — só a variação face a essa
        abertura é que se recalcula com o preço novo.
      - Variação = (preço novo − preço de abertura do dia) ÷ preço de abertura
        do dia × 100.

    Protecções mantidas:
      - Tickers em branco ou duplicados nunca são usados como chave de
        comparação (avisa, não sobrepõe silenciosamente).
      - Preços não numéricos / NaN tratados como 0, nunca chegam à divisão.
      - Se não há preço de abertura válido (activo novo) ou o preço novo é 0,
        a variação é 0 — nunca se divide por zero.
      - Variações acima de ±500% num só dia geram aviso visível (tipicamente
        um erro de dígitos no preço introduzido).
    """
    exigir_admin()
    df_anterior = obter_activos()
    hoje = datetime.now().date()

    referencia: dict[str, dict] = {}
    tickers_duplicados = set()
    for _, r in df_anterior.iterrows():
        tk = str(r.get("ticker", "") or "").strip().upper()
        if not tk:
            continue
        preco_r = _num_seguro(r.get("preco"), default=None)
        if preco_r is None:
            continue
        if tk in referencia:
            tickers_duplicados.add(tk)
        referencia[tk] = {
            "preco": preco_r,
            "preco_abertura": _num_seguro(r.get("preco_abertura_dia"), default=None),
            "data_abertura": r.get("data_abertura_dia"),
        }

    if tickers_duplicados:
        st.warning(
            "⚠️ Tickers duplicados na tabela de activos: "
            f"{', '.join(sorted(tickers_duplicados))}. "
            "A variação % destes activos pode estar a comparar o preço errado — "
            "corrige os tickers para que sejam únicos."
        )

    # os favoritos guardam o id do activo; como a tabela é regravada (ids novos), lembra-os por ticker/nome
    try:
        fav_antigos = consultar_df("SELECT f.conta_id, a.ticker, a.nome FROM favoritos f JOIN activos a ON a.id = f.activo_id")
    except Exception:
        fav_antigos = pd.DataFrame(columns=["conta_id", "ticker", "nome"])
    executar("DELETE FROM activos")
    avisos_variacao_extrema = []

    for _, linha in df.iterrows():
        nome = str(linha.get("nome", "")).strip()
        if not nome:
            continue
        tipo   = str(linha.get("tipo", "Ação")).strip() or "Ação"
        preco  = _num_seguro(linha.get("preco"), default=0.0)
        ticker = str(linha.get("ticker", "") or "").strip().upper()
        ref = referencia.get(ticker) if ticker else None

        if ref is None:
            # activo novo para este ticker: hoje É a abertura dele
            preco_abertura, data_abertura = preco, hoje
        elif ref["data_abertura"] is None or ref["data_abertura"] != hoje:
            # mudou o dia (ou nunca teve referência válida): fixa a abertura
            # de hoje como o último preço conhecido antes desta gravação
            preco_abertura = ref["preco"] if ref["preco"] else preco
            data_abertura  = hoje
        else:
            # já houve gravação hoje: mantém a MESMA abertura, não a desloca
            preco_abertura = ref["preco_abertura"] if ref["preco_abertura"] else preco
            data_abertura  = ref["data_abertura"]

        if not preco_abertura or not preco:
            variacao = 0.0
        else:
            variacao = round((preco - preco_abertura) / preco_abertura * 100, 2)
            if abs(variacao) > 500:
                avisos_variacao_extrema.append(f"{ticker or nome}: {variacao:+.2f}%")

        executar(
            "INSERT INTO activos (nome, tipo, preco, variacao, ticker, preco_abertura_dia, data_abertura_dia) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (nome, tipo, preco, variacao, ticker, preco_abertura, data_abertura))

    if avisos_variacao_extrema:
        st.warning(
            "⚠️ Variação invulgarmente elevada num só dia — confirma se não houve "
            "um erro de dígitos ao introduzir o preço: " + "; ".join(avisos_variacao_extrema)
        )

    novos_activos = obter_activos()
    try:
        por_ticker = {str(r["ticker"]).strip().upper(): int(r["id"]) for _, r in novos_activos.iterrows() if str(r["ticker"]).strip()}
        por_nome = {str(r["nome"]).strip().upper(): int(r["id"]) for _, r in novos_activos.iterrows()}
        for _, f in fav_antigos.iterrows():
            novo_id = por_ticker.get(str(f["ticker"] or "").strip().upper()) or por_nome.get(str(f["nome"] or "").strip().upper())
            if novo_id:
                executar("INSERT INTO favoritos (conta_id, activo_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (int(f["conta_id"]), novo_id))
        executar("DELETE FROM favoritos WHERE activo_id NOT IN (SELECT id FROM activos)")
    except Exception:
        pass
    registar_historico_indice(calcular_indice_mercado(novos_activos))
    registar_cotacoes_hoje(novos_activos, sobrepor=True)
    registar_vup_hoje()

def obter_favoritos(conta_id: int) -> set:
    df = consultar_df("SELECT activo_id FROM favoritos WHERE conta_id = %s", (conta_id,))
    return set(df["activo_id"].tolist())

def definir_favoritos(conta_id: int, ids_seleccionados: list):
    executar("DELETE FROM favoritos WHERE conta_id = %s", (conta_id,))
    for aid in ids_seleccionados:
        executar("INSERT INTO favoritos (conta_id, activo_id) VALUES (%s, %s)", (conta_id, aid))


# ---------------- Câmbio ----------------
def registar_historico_cambio(rates: dict):
    hoje = datetime.now().date()
    executar("INSERT INTO historico_cambio_aoa (registado_em, usd, eur, gbp, zar, cny, brl) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (registado_em) DO NOTHING",
             (hoje, rates.get("USD"), rates.get("EUR"), rates.get("GBP"), rates.get("ZAR"), rates.get("CNY"), rates.get("BRL")))

def obter_historico_cambio() -> pd.DataFrame:
    return consultar_df("SELECT registado_em, usd, eur, gbp, zar, cny, brl FROM historico_cambio_aoa ORDER BY registado_em")


# ---------------- Artigos ----------------
_NIVEL_POR_CATEGORIA = {"Educação": "iniciante", "Institucional": "iniciante", "Análise de Mercado": "investidor", "Referência": "investidor"}


def nivel_efectivo_artigo(categoria, nivel) -> str:
    """Nível escolhido pelo administrador; se não houver, decide-se pela categoria."""
    if nivel in NIVEIS:
        return nivel
    return _NIVEL_POR_CATEGORIA.get(str(categoria), "iniciante")


def obter_artigos(categoria: str = None) -> pd.DataFrame:
    if categoria and categoria != "Todas":
        df = consultar_df("SELECT id, titulo, categoria, conteudo, criado_em, nivel FROM artigos WHERE categoria = %s ORDER BY criado_em DESC", (categoria,))
    else:
        df = consultar_df("SELECT id, titulo, categoria, conteudo, criado_em, nivel FROM artigos ORDER BY criado_em DESC")
    df["nivel_efectivo"] = [nivel_efectivo_artigo(c, n) for c, n in zip(df["categoria"], df["nivel"])]
    return df

def inserir_artigo(titulo, categoria, conteudo, nivel=None):
    exigir_admin()
    executar("INSERT INTO artigos (titulo, categoria, conteudo, nivel) VALUES (%s, %s, %s, %s)", (titulo, categoria, conteudo, nivel if nivel in NIVEIS else None))

def definir_nivel_artigo(artigo_id: int, nivel):
    """nivel = 'iniciante', 'investidor' ou None (automático, pela categoria)."""
    exigir_admin()
    antes = consultar_um("SELECT nivel FROM artigos WHERE id = %s", (int(artigo_id),))
    executar("UPDATE artigos SET nivel = %s WHERE id = %s", (nivel if nivel in NIVEIS else None, int(artigo_id)))
    registar_auditoria("nivel_artigo", "artigo", artigo_id, antes={"nivel": antes[0] if antes else None}, depois={"nivel": nivel})


def _mostrar_artigos(df: pd.DataFrame, tx: dict):
    if df.empty:
        st.info("Ainda não há artigos neste nível e categoria.")
        return
    for _, artigo in df.iterrows():
        with st.expander(f"{ICONES_CATEGORIA.get(artigo['categoria'], '📄')} {artigo['titulo']}", key=f"artigo_exp_{artigo['id']}"):
            banner_categoria(artigo["categoria"])
            st.caption(f"{tx['bib_publicado']} {artigo['criado_em']}")
            st.markdown(artigo["conteudo"])   # conteúdo mantém-se em PT conforme acordado

def eliminar_artigo(artigo_id: int):
    exigir_admin()
    executar("DELETE FROM artigos WHERE id = %s", (artigo_id,))


# ---------------- Documentos PDF (Biblioteca e Estatuto) ----------------
PDF_TAMANHO_MAX = 15 * 1024 * 1024  # 15 MB


def inserir_documento(titulo, categoria, descricao, nome_ficheiro, conteudo: bytes, tipo="biblioteca"):
    exigir_admin()
    executar(
        "INSERT INTO documentos_pdf (titulo, categoria, descricao, nome_ficheiro, tipo, tamanho, conteudo) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (titulo, categoria, descricao or "", nome_ficheiro, tipo, len(conteudo), psycopg2.Binary(conteudo)))


def obter_documentos(tipo="biblioteca") -> pd.DataFrame:
    return consultar_df(
        "SELECT id, titulo, categoria, descricao, nome_ficheiro, tamanho, criado_em FROM documentos_pdf "
        "WHERE tipo = %s ORDER BY criado_em DESC", (tipo,))


def eliminar_documento(doc_id: int):
    exigir_admin()
    executar("DELETE FROM documentos_pdf WHERE id = %s", (int(doc_id),))


@st.cache_data(ttl=600, show_spinner=False)
def obter_pdf_bytes(doc_id: int) -> bytes:
    linha = consultar_um("SELECT conteudo FROM documentos_pdf WHERE id = %s", (int(doc_id),))
    return bytes(linha[0]) if linha else b""


_HTML_VISUALIZADOR_PDF = """
<div id="vwr" style="height:__ALT__px;overflow-y:auto;background:#EDE6E9;border:1px solid #ECDEE3;border-radius:8px;padding:8px;box-sizing:border-box;font-family:sans-serif;color:#7C1F3E;">A carregar documento…</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
<script>
(function () {
  var box = document.getElementById('vwr');
  try {
    pdfjsLib.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
    var raw = atob("__B64__");
    var data = new Uint8Array(raw.length);
    for (var i = 0; i < raw.length; i++) { data[i] = raw.charCodeAt(i); }
    pdfjsLib.getDocument({data: data}).promise.then(function (pdf) {
      box.innerHTML = "";
      var chain = Promise.resolve();
      for (var n = 1; n <= pdf.numPages; n++) {
        (function (num) {
          chain = chain.then(function () { return pdf.getPage(num).then(function (page) {
            var largura = box.clientWidth - 20;
            var v0 = page.getViewport({scale: 1});
            var esc = (largura / v0.width) * (window.devicePixelRatio || 1);
            var vp = page.getViewport({scale: esc});
            var c = document.createElement('canvas');
            c.width = vp.width; c.height = vp.height;
            c.style.width = largura + 'px'; c.style.display = 'block';
            c.style.margin = '0 auto 10px auto'; c.style.boxShadow = '0 1px 4px rgba(0,0,0,0.25)';
            box.appendChild(c);
            return page.render({canvasContext: c.getContext('2d'), viewport: vp}).promise;
          }); });
        })(n);
      }
    }).catch(function (e) { box.innerHTML = "Não foi possível mostrar o documento no ecrã. Use o botão de descarregar."; });
  } catch (e) { box.innerHTML = "Não foi possível mostrar o documento no ecrã. Use o botão de descarregar."; }
})();
</script>
"""


def bloco_documento_pdf(doc_id: int, nome_ficheiro: str, chave: str, altura: int = 760):
    """Caixa de selecção 'Abrir documento': mostra o PDF no ecrã e o botão de descarregar (só carrega quando aberto)."""
    if st.checkbox("📖 Abrir documento", key=f"abrir_pdf_{chave}"):
        dados = obter_pdf_bytes(int(doc_id))
        if not dados:
            st.warning("Documento não encontrado.")
            return
        st.download_button("⬇️ Descarregar PDF", data=dados, file_name=nome_ficheiro or "documento.pdf",
                           mime="application/pdf", key=f"dl_pdf_{chave}")
        import base64 as _b64
        import streamlit.components.v1 as _components
        _components.html(_HTML_VISUALIZADOR_PDF.replace("__ALT__", str(altura - 20)).replace(
            "__B64__", _b64.b64encode(dados).decode()), height=altura)



# ---------------- Sócios ----------------
def inserir_socio(nome, email, telefone, bi, contribuicao_inicial):
    executar("INSERT INTO socios (nome, email, telefone, bi, contribuicao_inicial) VALUES (%s, %s, %s, %s, %s)", (nome, email, telefone, bi, contribuicao_inicial))

def obter_socios() -> pd.DataFrame:
    exigir_admin()
    return consultar_df("SELECT nome, email, telefone, bi, contribuicao_inicial, criado_em FROM socios ORDER BY criado_em DESC")

def extrair_texto_pdf(ficheiro) -> str:
    leitor = PdfReader(ficheiro)
    return "\n\n".join(pagina.extract_text() or "" for pagina in leitor.pages).strip()


def _pdf_linha(pdf, label, valor, bold=False):
    pdf.set_font("Helvetica", "B" if bold else "", 10)
    pdf.set_fill_color(246, 239, 242)
    pdf.cell(105, 7, label, border="B", fill=bold, ln=False)
    pdf.cell(0, 7, valor, border="B", align="R", fill=bold, ln=True)


def _pdf_secao(pdf, titulo):
    pdf.ln(4)
    pdf.set_fill_color(124, 31, 62)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, f"  {titulo}", ln=True, fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(1)


# ---------------- Gráficos do relatório PDF (desenhados com o próprio FPDF, sem bibliotecas extra) ----------------
_PDF_PALETA = [(124, 31, 62), (166, 72, 106), (94, 24, 48), (200, 130, 150), (150, 110, 120), (210, 180, 190), (70, 50, 60)]


def _pdf_nome_curto(nome: str) -> str:
    """'BAI (ACÇÃO)' -> 'BAI'; 'Acção Unitel' -> 'Unitel'."""
    import re as _re
    n = _re.sub(r"\s*\(.*?\)", "", str(nome)).strip()
    for pref in ("Acção ", "Ação ", "ACÇÃO ", "AÇÃO "):
        if n.startswith(pref):
            n = n[len(pref):].strip()
    return n or str(nome)


def _pdf_grafico_composicao(pdf, linhas):
    """Barra horizontal 100%: nome e peso de cada activo; a legenda traz os valores em Kz."""
    total = sum(max(l["val_act"], 0) for l in linhas)
    if total <= 0:
        return
    x0 = pdf.l_margin
    largura = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, "Composição da carteira (por valor actual)", ln=True)
    y = pdf.get_y() + 1
    x = x0
    for i, l in enumerate(linhas):
        peso = max(l["val_act"], 0) / total
        w = largura * peso
        pdf.set_fill_color(*_PDF_PALETA[i % len(_PDF_PALETA)])
        pdf.rect(x, y, w, 11, style="F")
        pdf.set_text_color(255, 255, 255)
        nome = _pdf_nome_curto(l["nome"])
        pdf.set_font("Helvetica", "B", 7)
        cabe_nome = pdf.get_string_width(nome) + 3 <= w
        if w > 9:
            if cabe_nome:
                pdf.set_xy(x, y + 1.3)
                pdf.cell(w, 4.2, nome, align="C")
                pdf.set_xy(x, y + 5.6)
            else:
                pdf.set_xy(x, y + 3.4)
            pdf.cell(w, 4.2, f"{peso * 100:.1f}%", align="C")
        x += w
    # legenda: nome completo e valor em Kz (a percentagem já está nas barras)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(40, 40, 40)
    ly = y + 14
    for i, l in enumerate(linhas):
        cx = x0 + (i % 2) * (largura / 2)
        cy = ly + (i // 2) * 5
        pdf.set_fill_color(*_PDF_PALETA[i % len(_PDF_PALETA)])
        pdf.rect(cx, cy + 0.8, 3, 3, style="F")
        pdf.set_xy(cx + 4.5, cy)
        pdf.cell(largura / 2 - 6, 4.5, f"{_pdf_nome_curto(l['nome'])[:34]}  -  {kz(l['val_act'])}")
    pdf.set_y(ly + ((len(linhas) + 1) // 2) * 5 + 2)
    pdf.set_text_color(0, 0, 0)


def _pdf_grafico_mais_valias(pdf, linhas, x0, y0, w, h):
    """Barras verticais: ganho (verde) ou perda (vermelho) por activo."""
    pdf.set_xy(x0, y0)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(w, 6, "Mais-valias por activo (Kz)")
    vals = [l["mais_valia"] for l in linhas]
    vmax, vmin = max(0, max(vals)), min(0, min(vals))
    rng = (vmax - vmin) or 1
    top = y0 + 12
    bottom = top + h

    def yv(v):
        return top + (vmax - v) / rng * h

    pdf.set_draw_color(170, 170, 170)
    pdf.set_line_width(0.2)
    pdf.line(x0, yv(0), x0 + w, yv(0))
    n = len(linhas)
    slot = w / n
    bw = min(slot * 0.6, 22)
    for i, l in enumerate(linhas):
        v = vals[i]
        bx = x0 + slot * i + (slot - bw) / 2
        y1, y2 = yv(max(v, 0)), yv(min(v, 0))
        pdf.set_fill_color(*((22, 163, 74) if v >= 0 else (220, 38, 38)))
        pdf.rect(bx, y1, bw, max(y2 - y1, 0.3), style="F")
        pdf.set_font("Helvetica", "", 6.5)
        pdf.set_text_color(60, 60, 60)
        pdf.set_xy(bx - 5, (y1 - 3.8) if v >= 0 else (y2 + 0.5))
        pdf.cell(bw + 10, 3.5, kz(v), align="C")
        pdf.set_xy(x0 + slot * i, bottom + 6)
        pdf.cell(slot, 3.5, (l["ticker"] or l["nome"])[:9], align="C")
    pdf.set_text_color(0, 0, 0)


def _pdf_grafico_evolucao(pdf, df_hist, x0, y0, w, h):
    """Linha: evolução do património do Clube (histórico diário)."""
    pdf.set_xy(x0, y0)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(w, 6, "Evolução do património do Clube (Kz)")
    if df_hist is None or len(df_hist) < 2:
        pdf.set_xy(x0, y0 + 14)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(120, 120, 120)
        pdf.multi_cell(w, 4.5, "O histórico ainda está a ser construído: o gráfico aparece a partir do segundo registo diário do património.")
        pdf.set_text_color(0, 0, 0)
        return
    d = df_hist.tail(60)
    ys = [float(v) for v in d["total"]]
    datas = [str(v)[:10] for v in d["registado_em"]]
    ymin, ymax = min(ys), max(ys)
    if ymax == ymin:
        pad = abs(ymax) * 0.05 or 1.0
        ymin, ymax = ymin - pad, ymax + pad
    esq = 24
    px0, pw = x0 + esq, w - esq
    top = y0 + 12
    bottom = top + h
    pdf.set_draw_color(225, 225, 225)
    pdf.set_line_width(0.2)
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_text_color(90, 90, 90)
    for k in range(4):
        gy = top + h * k / 3
        pdf.line(px0, gy, px0 + pw, gy)
        pdf.set_xy(x0, gy - 1.8)
        pdf.cell(esq - 2, 3.5, kz(ymax - (ymax - ymin) * k / 3), align="R")
    n = len(ys)
    pts = [(px0 + pw * i / (n - 1), top + (ymax - v) / (ymax - ymin) * h) for i, v in enumerate(ys)]
    pdf.set_draw_color(124, 31, 62)
    pdf.set_line_width(0.6)
    for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):
        pdf.line(xa, ya, xb, yb)
    if n <= 20:
        pdf.set_fill_color(124, 31, 62)
        for (xp, yp) in pts:
            pdf.rect(xp - 0.7, yp - 0.7, 1.4, 1.4, style="F")
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_text_color(90, 90, 90)
    pdf.set_xy(px0, bottom + 2)
    pdf.cell(30, 3.5, datas[0], align="L")
    pdf.set_xy(px0 + pw - 30, bottom + 2)
    pdf.cell(30, 3.5, datas[-1], align="R")
    pdf.set_text_color(0, 0, 0)


def _pdf_sector(l) -> str:
    """Sector do activo, a partir do ticker/nome (Telecomunicações, Banca/Finanças ou Outros)."""
    chave = f"{l['ticker']} {l['nome']}".upper()
    if "UNTL" in chave or "UNITEL" in chave:
        return "Telecomunicações"
    if any(k in chave for k in ("BAIA", "BFA", "SBA", "STANDARD", "BCGA", "CAIXA", "BDVA", "BODIVA", "ENSA")):
        return "Banca/Finanças"
    return "Outros"


def _pdf_barras_limite(pdf, titulo, itens, x0, y0, w, limite):
    """Barras horizontais (rótulo, %) com linha vertical no limite; vermelho se o limite for excedido."""
    pdf.set_xy(x0, y0)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(w, 6, titulo)
    lab_w, linha_h = min(46, w * 0.32), 8
    pmax = max([p for _, p in itens] + [limite * 1.5])
    pw = w - lab_w - 16
    top = y0 + 9
    for i, (rot, p) in enumerate(itens):
        y = top + i * linha_h
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(40, 40, 40)
        pdf.set_xy(x0, y + 1)
        pdf.cell(lab_w - 2, 5, rot[:26], align="R")
        bw = pw * p / pmax
        pdf.set_fill_color(*((220, 38, 38) if p > limite else (22, 163, 74)))
        pdf.rect(x0 + lab_w, y + 0.5, max(bw, 0.3), 6, style="F")
        pdf.set_xy(x0 + lab_w + max(bw, pw * limite / pmax) + 1.5, y + 1)
        pdf.cell(14, 5, f"{p:.1f}%")
    lx = x0 + lab_w + pw * limite / pmax
    pdf.set_draw_color(220, 38, 38)
    pdf.set_line_width(0.4)
    pdf.line(lx, top - 1, lx, top + len(itens) * linha_h)
    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_text_color(220, 38, 38)
    pdf.set_xy(lx - 15, top + len(itens) * linha_h + 0.5)
    pdf.cell(30, 3.5, f"limite {limite:.0f}%", align="C")
    pdf.set_text_color(0, 0, 0)
    return top + len(itens) * linha_h + 6


def _pdf_barras_simples(pdf, titulo, itens, x0, y0, w, cor=(124, 31, 62)):
    """Barras horizontais (rótulo, %) numa só série."""
    pdf.set_xy(x0, y0)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(w, 6, titulo)
    lab_w, linha_h = min(46, w * 0.32), 8
    pmax = max([p for _, p in itens] + [1]) * 1.15
    pw = w - lab_w - 14
    top = y0 + 9
    for i, (rot, p) in enumerate(itens):
        y = top + i * linha_h
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(40, 40, 40)
        pdf.set_xy(x0, y + 1)
        pdf.cell(lab_w - 2, 5, rot[:22], align="R")
        bw = pw * p / pmax
        pdf.set_fill_color(*cor)
        pdf.rect(x0 + lab_w, y + 0.5, max(bw, 0.3), 6, style="F")
        pdf.set_xy(x0 + lab_w + bw + 1, y + 1)
        pdf.cell(14, 5, f"{p:.1f}%")
    pdf.set_text_color(0, 0, 0)
    return top + len(itens) * linha_h + 2


def _pdf_barras_duplas(pdf, titulo, itens, x0, y0, w):
    """Por activo, duas barras: % do número de títulos e % do valor da carteira."""
    pdf.set_xy(x0, y0)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(w, 6, titulo)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_fill_color(166, 72, 106)
    pdf.rect(x0, y0 + 7.3, 3, 3, style="F")
    pdf.set_xy(x0 + 4.5, y0 + 6.8)
    pdf.cell(40, 4, "Quantidade de títulos")
    pdf.set_fill_color(124, 31, 62)
    pdf.rect(x0 + 48, y0 + 7.3, 3, 3, style="F")
    pdf.set_xy(x0 + 52.5, y0 + 6.8)
    pdf.cell(40, 4, "Valor monetário")
    lab_w, linha_h = 40, 11
    pmax = max([max(a, b) for _, a, b in itens] + [1])
    pw = w - lab_w - 14
    top = y0 + 13
    for i, (rot, pq, pv) in enumerate(itens):
        y = top + i * linha_h
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(40, 40, 40)
        pdf.set_xy(x0, y + 2.5)
        pdf.cell(lab_w - 2, 5, rot[:22], align="R")
        for k, (p, cor) in enumerate(((pq, (166, 72, 106)), (pv, (124, 31, 62)))):
            by = y + k * 4.6
            bw = pw * p / pmax
            pdf.set_fill_color(*cor)
            pdf.rect(x0 + lab_w, by, max(bw, 0.3), 4, style="F")
            pdf.set_font("Helvetica", "", 6.5)
            pdf.set_xy(x0 + lab_w + bw + 1, by - 0.2)
            pdf.cell(12, 4.4, f"{p:.1f}%")
    pdf.set_text_color(0, 0, 0)
    return top + len(itens) * linha_h + 2


# =========================================================
# INFRA-ESTRUTURA EXTRA + COMPONENTES DO RELATÓRIO PDF INSTITUCIONAL
# =========================================================
@st.cache_resource
def _garantir_tabelas_extra() -> bool:
    """Tabelas/colunas novas (mercado BODIVA, configuração, inflação). Idempotente; corre uma vez por processo."""
    executar("""CREATE TABLE IF NOT EXISTS mercado_bodiva (
        ticker TEXT PRIMARY KEY, nome TEXT, tipo TEXT, preco NUMERIC, variacao NUMERIC, volume NUMERIC,
        fonte TEXT, actualizado_em TIMESTAMP NOT NULL DEFAULT NOW())""")
    executar("CREATE TABLE IF NOT EXISTS config_mercado (chave TEXT PRIMARY KEY, valor TEXT)")
    for _col, _tp in (("inflacao_homologa", "NUMERIC"), ("inflacao_vigente_m", "NUMERIC"), ("inflacao_projectada", "NUMERIC"),
                      ("inflacao_ref", "TEXT"), ("inflacao_data", "DATE")):
        executar(f"ALTER TABLE premissas_macro ADD COLUMN IF NOT EXISTS {_col} {_tp}")
    return True


# ---------- Texto seguro para o PDF (fonte Helvetica = Latin-1) ----------
_PDF_TROCAS = {"\u2013": "-", "\u2014": "-", "\u2212": "-", "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
               "\u2026": "...", "\u2022": "-", "\u2192": "->", "\u2190": "<-", "\u2265": ">=", "\u2264": "<=",
               "\u2605": "*", "\u20ac": "EUR", "\u00a0": " ", "\u2248": "~", "\u0394": "Delta", "\u03c3": "sigma",
               "\u03b1": "alpha", "\u03b2": "beta"}


def _pdf_txt(s) -> str:
    """Troca pontuação Unicode e remove o que a fonte base não suporta (emojis, etc.), para o PDF nunca falhar."""
    s = "" if s is None else str(s)
    for k, v in _PDF_TROCAS.items():
        s = s.replace(k, v)
    return "".join(c for c in s if ord(c) < 256)


class _FPDFSeguro(FPDF):
    """FPDF que limpa o texto antes de o escrever: um carácter fora de Latin-1 (ex.: '–' numa descrição)
    já não faz falhar o relatório inteiro."""
    def cell(self, *args, **kwargs):
        args = list(args)
        if len(args) >= 3:
            args[2] = _pdf_txt(args[2])
        for k in ("text", "txt"):
            if k in kwargs:
                kwargs[k] = _pdf_txt(kwargs[k])
        return super().cell(*args, **kwargs)

    def multi_cell(self, *args, **kwargs):
        args = list(args)
        if len(args) >= 3:
            args[2] = _pdf_txt(args[2])
        for k in ("text", "txt"):
            if k in kwargs:
                kwargs[k] = _pdf_txt(kwargs[k])
        return super().multi_cell(*args, **kwargs)


_PDF_PALETA_FX = [(109, 40, 217), (225, 29, 72), (249, 115, 22), (124, 31, 62), (168, 85, 247),
                  (251, 146, 60), (244, 63, 94), (99, 102, 241), (190, 24, 93), (180, 83, 9)]


def _pdf_fmt(v, casas: int = 2, sinal: bool = True, sufixo: str = "%") -> str:
    if v is None or (isinstance(v, float) and v != v):
        return "n/d"
    try:
        return (f"{float(v):+.{casas}f}" if sinal else f"{float(v):.{casas}f}") + sufixo
    except (TypeError, ValueError):
        return "n/d"


def _pdf_corta(pdf, txt: str, largura: float) -> str:
    txt = _pdf_txt(txt)
    while len(txt) > 1 and pdf.get_string_width(txt) > largura - 2:
        txt = txt[:-1]
    return txt


def _pdf_paragrafo(pdf, titulo: str, texto: str):
    larg = pdf.w - pdf.l_margin - pdf.r_margin
    if pdf.get_y() > pdf.h - 48:
        pdf.add_page("L")
    pdf.set_xy(pdf.l_margin, pdf.get_y())
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(109, 40, 217)
    pdf.cell(larg, 6, titulo, ln=True)
    pdf.set_xy(pdf.l_margin, pdf.get_y())
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(larg, 4.8, texto)
    pdf.set_xy(pdf.l_margin, pdf.get_y() + 2)
    pdf.set_text_color(0, 0, 0)


def _pdf_tabela(pdf, cab, linhas, larg, alinh=None, h=6.0, negrito=(), sinal_cols=(), tam=7.5):
    """Tabela com cabeçalho repetido em nova página; verde/vermelho nas colunas de sinal."""
    alinh = alinh or (["L"] + ["R"] * (len(cab) - 1))

    def _cab():
        pdf.set_xy(pdf.l_margin, pdf.get_y())
        pdf.set_font("Helvetica", "B", tam)
        pdf.set_fill_color(236, 222, 227)
        pdf.set_text_color(0, 0, 0)
        for i, (c, w) in enumerate(zip(cab, larg)):
            pdf.cell(w, h + 1.5, _pdf_corta(pdf, c, w), border="B", fill=True, ln=(i == len(cab) - 1), align="C")

    _cab()
    for k, linha in enumerate(linhas):
        if pdf.get_y() + h > pdf.h - 22:
            pdf.add_page("L")
            _cab()
        pdf.set_xy(pdf.l_margin, pdf.get_y())
        pdf.set_fill_color(250, 248, 246) if k % 2 == 0 else pdf.set_fill_color(255, 255, 255)
        for i, (v, w) in enumerate(zip(linha, larg)):
            txt = _pdf_txt(v)
            pdf.set_font("Helvetica", "B" if k in negrito else "", tam)
            cor = (0, 0, 0)
            if i in sinal_cols and txt not in ("n/d", "") and txt[:1] in "+-":
                cor = (22, 163, 74) if txt[:1] == "+" else (220, 38, 38)
            pdf.set_text_color(*cor)
            pdf.cell(w, h, _pdf_corta(pdf, txt, w), border="B", fill=True, ln=(i == len(linha) - 1), align=alinh[i])
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(pdf.l_margin, pdf.get_y() + 1)


def _pdf_donut(pdf, itens, cx, cy, r, r_int, titulo, centro=""):
    """Gráfico de anel desenhado com polígonos (sem bibliotecas extra). `itens` = [(rótulo, valor, texto_valor)].
    Se o FPDF não tiver `polygon`, desenha só a legenda."""
    import math
    itens = [(n, float(v), tv) for n, v, tv in itens if v and float(v) > 0]
    pdf.set_xy(cx - r - 6, cy - r - 9)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(60, 30, 90)
    pdf.cell(2 * r + 12, 6, titulo, align="C")
    total = sum(v for _, v, _ in itens)
    if total <= 0:
        return cy + r
    ang = -math.pi / 2
    pdf.set_draw_color(255, 255, 255)
    pdf.set_line_width(0.5)
    for i, (_, v, _) in enumerate(itens):
        fim = ang + 2 * math.pi * v / total
        passos = max(3, int((fim - ang) / (2 * math.pi) * 120))
        ext = [(cx + r * math.cos(ang + (fim - ang) * j / passos), cy + r * math.sin(ang + (fim - ang) * j / passos)) for j in range(passos + 1)]
        inte = [(cx + r_int * math.cos(fim - (fim - ang) * j / passos), cy + r_int * math.sin(fim - (fim - ang) * j / passos)) for j in range(passos + 1)]
        pdf.set_fill_color(*_PDF_PALETA_FX[i % len(_PDF_PALETA_FX)])
        try:
            pdf.polygon(ext + inte, style="DF")
        except Exception:
            break
        ang = fim
    pdf.set_line_width(0.2)
    pdf.set_draw_color(0, 0, 0)
    if centro:
        pdf.set_xy(cx - r_int, cy - 4)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(27, 16, 51)
        pdf.cell(2 * r_int, 4, centro, align="C")
    # legenda
    ly = cy + r + 5
    pdf.set_font("Helvetica", "", 7)
    for i, (n, v, tv) in enumerate(itens[:9]):
        pdf.set_fill_color(*_PDF_PALETA_FX[i % len(_PDF_PALETA_FX)])
        pdf.rect(cx - r - 4, ly + 0.9, 2.6, 2.6, style="F")
        pdf.set_xy(cx - r, ly)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(2 * r + 8, 4.4, _pdf_corta(pdf, f"{n}: {v / total * 100:.1f}%  {tv}", 2 * r + 8))
        ly += 4.4
    pdf.set_text_color(0, 0, 0)
    return ly


def _rotulo_horiz(a: dict, p: str, curto: bool = True) -> str:
    nomes_c = {"1d": "Intradia", "7d": "Semanal 7D", "3m": "Trimestral", "6m": "Semestral", "1a": "Anual YoY", "5a": "Longo prazo 5A"}
    nomes_l = dict(HORIZ_RENT)
    if p == "5a" and a.get("acumulado") and a.get("inicio_comum") is not None:
        return f"Acum. {a['inicio_comum']:%d/%m/%y}"
    return nomes_c[p] if curto else nomes_l[p]


def _pdf_bloco_executivo(pdf, a: dict, resumo: dict, mercado, linhas_carteira: list):
    """Sumário executivo, matriz multitemporal (com Alpha), inflação real, risco e composição em anéis."""
    larg = pdf.w - pdf.l_margin - pdf.r_margin
    ps = [p for p, _ in HORIZ_RENT]
    # ---- 1. Sumário executivo e teses ----
    pdf.add_page("L")
    _pdf_secao(pdf, "SUMARIO EXECUTIVO E TESES DE INVESTIMENTO")
    for titulo, texto in gerar_comentario_executivo(a, resumo, mercado):
        _pdf_paragrafo(pdf, titulo, texto)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(120, 120, 120)
    pdf.set_xy(pdf.l_margin, pdf.get_y())
    pdf.multi_cell(larg, 3.8, "Comentario gerado automaticamente a partir dos dados da plataforma (cotacoes, carteira e premissas macro). "
                              "Tem natureza informativa e nao constitui recomendacao personalizada de investimento.")
    pdf.set_text_color(0, 0, 0)

    # ---- 2. Matriz comparativa ----
    pdf.add_page("L")
    _pdf_secao(pdf, "MATRIZ COMPARATIVA DE DESEMPENHO - CARTEIRA vs INDICES vs INFLACAO")
    cab = ["Indicador"] + [_rotulo_horiz(a, p) for p in ps]
    W = [58] + [round((larg - 58) / 6, 2)] * 6
    f = lambda d: [_pdf_fmt(d.get(p)) for p in ps]
    fpp = lambda d: [_pdf_fmt(d.get(p), sufixo=" p.p.") for p in ps]
    inf = a["inflacao"]
    real = a["real"]
    lin = [
        ["Carteira do Clube (nominal)"] + f(a["ret_carteira"]),
        ["Indice APPO"] + f(a["ret_appo"]),
        ["Indice BODIVA"] + f(a["ret_bodiva"]),
        ["Alpha vs Indice APPO"] + fpp(a["alpha_appo"]),
        ["Alpha vs Indice BODIVA"] + fpp(a["alpha_bodiva"]),
        ["Inflacao homologa (YoY) no periodo"] + [_pdf_fmt(inf[p]["yoy"], sinal=False) for p in ps],
        ["Inflacao vigente no periodo"] + [_pdf_fmt(inf[p]["vig"], sinal=False) for p in ps],
        ["Inflacao projectada no periodo"] + [_pdf_fmt(inf[p]["proj"], sinal=False) for p in ps],
        ["Rentab. real (deflac. YoY)"] + [_pdf_fmt(real[p]["yoy"]) if real.get(p) else "n/d" for p in ps],
        ["Rentab. real (deflac. vigente)"] + [_pdf_fmt(real[p]["vig"]) if real.get(p) else "n/d" for p in ps],
        ["Rentab. real (deflac. projectada)"] + [_pdf_fmt(real[p]["proj"]) if real.get(p) else "n/d" for p in ps],
    ]
    _pdf_tabela(pdf, cab, lin, W, negrito=(0, 3, 4, 8), sinal_cols=tuple(range(1, 7)))
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(120, 120, 120)
    nota = ("Rentabilidade de preco (sem dividendos nem custos de transaccao); alpha = excesso de retorno da carteira face ao indice, em pontos percentuais, "
            "na mesma janela temporal. Janelas sem historico completo aparecem como n/d. ")
    if a.get("acumulado"):
        nota += f"A coluna de longo prazo e acumulada desde {a['inicio_comum']:%d/%m/%Y}, a data comum das tres series. "
    nota += "Indice BODIVA: cotacao media encadeada (entradas de novos titulos nao geram saltos). Carteira: quantidades actuais mantidas durante o periodo."
    pdf.set_xy(pdf.l_margin, pdf.get_y())
    pdf.multi_cell(larg, 3.8, nota)
    pdf.set_text_color(0, 0, 0)

    _pdf_secao(pdf, "RENTABILIDADE MULTITEMPORAL POR TITULO (em vez de uma unica coluna Var.%)")
    cab2 = ["Titulo", "Peso"] + [_rotulo_horiz(a, p) for p in ps]
    W2 = [52, 18] + [round((larg - 70) / 6, 2)] * 6
    lin2 = [[_pdf_nome_curto(t["nome"]), f"{t['peso'] * 100:.1f}%"] + [_pdf_fmt(t["ret"].get(p)) for p in ps] for t in a["titulos"]]
    lin2.append(["CARTEIRA", "100%"] + f(a["ret_carteira"]))
    _pdf_tabela(pdf, cab2, lin2, W2, alinh=["L", "R"] + ["R"] * 6, negrito=(len(lin2) - 1,), sinal_cols=tuple(range(2, 8)))

    # ---- 3. Inflação e poder de compra ----
    pdf.add_page("L")
    _pdf_secao(pdf, "AJUSTE MACROECONOMICO - INFLACAO REAL DE ANGOLA E PODER DE COMPRA")
    pr = a["premissas"]
    vig_anual = ((1 + pr["inflacao_vigente_m"]) ** 12 - 1) * 100
    ref = pr.get("inflacao_ref") or "valores por defeito - por confirmar com o INE"
    lin3 = [
        ["Inflacao homologa (YoY)", f"{pr['inflacao_homologa'] * 100:.2f}%", "Ganho/perda real de poder de compra nos ultimos 12 meses"],
        ["Inflacao vigente (ultima leitura mensal)", f"{pr['inflacao_vigente_m'] * 100:.2f}% m/m  (~{vig_anual:.1f}% anualizada)", "Pulso conjuntural imediato"],
        ["Inflacao projectada (proximos 12 meses)", f"{pr['inflacao_projectada'] * 100:.2f}%", "Teste de stress e preservacao de capital a medio/longo prazo"],
    ]
    _pdf_tabela(pdf, ["Dimensao", "Valor", "Leitura"], lin3, [75, 75, larg - 150], alinh=["L", "L", "L"], h=6.5, tam=8)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(120, 120, 120)
    pdf.set_xy(pdf.l_margin, pdf.get_y())
    pdf.cell(larg, 4, f"Fonte/data das premissas: {ref}", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)
    cab4 = ["Rentabilidade real"] + [_rotulo_horiz(a, p) for p in ps]
    lin4 = [["Carteira - nominal"] + f(a["ret_carteira"]),
            ["Real (deflacionada pela inflacao YoY)"] + [_pdf_fmt(real[p]["yoy"]) if real.get(p) else "n/d" for p in ps],
            ["Real (inflacao vigente)"] + [_pdf_fmt(real[p]["vig"]) if real.get(p) else "n/d" for p in ps],
            ["Real (inflacao projectada)"] + [_pdf_fmt(real[p]["proj"]) if real.get(p) else "n/d" for p in ps],
            ["Poder de compra (YoY)"] + [("Ganho" if real[p]["yoy"] > 0 else "Perda") if real.get(p) else "n/d" for p in ps]]
    _pdf_tabela(pdf, cab4, lin4, W, negrito=(1,), sinal_cols=tuple(range(1, 7)))
    pdf.ln(2)
    _pdf_paragrafo(pdf, "Teste de stress - poder de compra de 100 000 Kz mantidos sem rendimento",
                   "Mostra quanto valeria hoje o capital se ficasse parado, e que retorno nominal acumulado seria preciso para o preservar.")
    base_inf = pr["inflacao_projectada"]
    stress = []
    for nome_c, ip in (("Projectada", base_inf), ("Projectada + 5 p.p. (stress)", base_inf + 0.05)):
        stress.append([f"Poder de compra em {nome_c}"] + [f"{100000 / (1 + ip) ** n:,.0f} Kz".replace(",", " ") for n in (1, 3, 5)])
        stress.append([f"Retorno nominal necessario ({nome_c})"] + [f"{((1 + ip) ** n - 1) * 100:.1f}%" for n in (1, 3, 5)])
    _pdf_tabela(pdf, ["Cenario", "1 ano", "3 anos", "5 anos"], stress, [100, 49, 49, larg - 198], alinh=["L", "R", "R", "R"], h=6)

    # ---- 4. Risco ----
    pdf.add_page("L")
    _pdf_secao(pdf, "ANALISE DE RISCO E DESVIO PADRAO")
    rk = a["risco"]
    def _g(nome, chave, casas=2, suf="%", sinal=False):
        return [_pdf_fmt(rk[x].get(chave), casas, sinal, suf) if rk.get(x) else "n/d" for x in ("carteira", "appo", "bodiva")]
    lin5 = [["Observacoes (retornos)"] + [str(rk[x]["n"]) if rk.get(x) else "n/d" for x in ("carteira", "appo", "bodiva")],
            ["Desvio padrao diario (sigma)"] + _g("", "sigma_d"),
            ["Volatilidade anualizada (sigma x raiz de 252)"] + _g("", "sigma_a"),
            ["Drawdown maximo"] + _g("", "dd_max"),
            ["VaR historico 95% (1 dia)"] + _g("", "var95"),
            ["Tracking error vs Indice APPO (anualizado)"] + [_pdf_fmt(rk["carteira"].get("te"), 2, False, "%"), "-", "-"],
            ["Information ratio vs Indice APPO"] + [_pdf_fmt(rk["carteira"].get("ir"), 2, False, ""), "-", "-"],
            ["Beta vs Indice BODIVA"] + [_pdf_fmt(rk["carteira"].get("beta"), 2, False, ""), "-", "-"],
            ["Sharpe (Rf das premissas)"] + [_pdf_fmt(rk["carteira"].get("sharpe"), 2, False, ""), "-", "-"]]
    _pdf_tabela(pdf, ["Metrica", "Carteira", "Indice APPO", "Indice BODIVA"], lin5, [95, 50, 50, larg - 195], alinh=["L", "R", "R", "R"], h=6.2, tam=8)
    pdf.ln(2)
    cab6 = ["Titulo", "Peso", "Volat. anual.", "Drawdown max.", "Contrib. p/ risco total", "Peso / Risco"]
    lin6, alertas = [], []
    for t_ in a["titulos"]:
        c_ = t_.get("contrib")
        rel = (f"{c_ / t_['peso']:.2f}x" if c_ is not None and t_["peso"] > 0 else "n/d")
        lin6.append([_pdf_nome_curto(t_["nome"]), f"{t_['peso'] * 100:.1f}%", _pdf_fmt(t_.get("sigma_a"), 2, False),
                     _pdf_fmt(t_.get("dd_max"), 2, False), _pdf_fmt(c_ * 100 if c_ is not None else None, 1, False), rel])
        if c_ is not None and t_["peso"] > 0 and c_ / t_["peso"] > 1.25:
            alertas.append(f"{_pdf_nome_curto(t_['nome'])} contribui {c_ * 100:.1f}% do risco com {t_['peso'] * 100:.1f}% do peso")
    _pdf_tabela(pdf, cab6, lin6, [62, 28, 34, 36, 45, larg - 205], alinh=["L", "R", "R", "R", "R", "R"], h=6)
    cc = a["concentracao"]
    txt_ef = (f"Numero efectivo de activos (1/HHI): {cc['n_efectivo']:.1f} em {len(a['titulos'])} posicoes. "
              + ("Desalinhamento peso/risco: " + "; ".join(alertas) + "." if alertas else "A contribuicao para o risco esta alinhada com os pesos da carteira."))
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(40, 40, 40)
    pdf.set_xy(pdf.l_margin, pdf.get_y() + 1)
    pdf.multi_cell(larg, 4.6, txt_ef)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(120, 120, 120)
    pdf.set_xy(pdf.l_margin, pdf.get_y() + 1)
    n_obs = rk["carteira"]["n"] if rk.get("carteira") else 0
    pdf.multi_cell(larg, 3.8, f"Metricas calculadas sobre {n_obs} retornos observados (preco de fecho registado). Com amostras curtas (<30) os valores sao indicativos. "
                              "Contribuicao para o risco = peso x covariancia com a carteira / variancia total.")
    pdf.set_text_color(0, 0, 0)

    # ---- 5. Composição em anéis ----
    if linhas_carteira:
        pdf.add_page("L")
        _pdf_secao(pdf, "COMPOSICAO DA CARTEIRA (GRAFICOS DE ANEL)")
        y0 = pdf.get_y() + 14
        r, ri = 24, 14
        cxs = [pdf.l_margin + larg / 6, pdf.l_margin + larg / 2, pdf.l_margin + 5 * larg / 6]
        por_val = [(_pdf_nome_curto(l["nome"]), max(l["val_act"], 0), kz(l["val_act"])) for l in linhas_carteira]
        por_qtd = [(_pdf_nome_curto(l["nome"]), max(l["qtd"], 0), f"{l['qtd']:,.0f} tit.".replace(",", " ")) for l in linhas_carteira]
        sect = {}
        for l in linhas_carteira:
            sect[_pdf_sector(l)] = sect.get(_pdf_sector(l), 0.0) + max(l["val_act"], 0)
        por_sec = [(k, v, kz(v)) for k, v in sorted(sect.items(), key=lambda x: -x[1])]
        tot = sum(max(l["val_act"], 0) for l in linhas_carteira)
        _pdf_donut(pdf, por_val, cxs[0], y0 + r, r, ri, "Por activo (valor actual)", kz(tot))
        _pdf_donut(pdf, por_qtd, cxs[1], y0 + r, r, ri, "Por activo (quantidade de titulos)", "")
        _pdf_donut(pdf, por_sec, cxs[2], y0 + r, r, ri, "Por sector", "")
        y1 = y0 + r + 5 + 4.4 * 9 + 22
        if y1 + 70 < pdf.h - 20:
            res_liq = float(resumo.get("reservas", 0) or 0)
            por_rea = float(resumo.get("capital_subscrito", 0) or 0) - float(resumo.get("capital_realizado", 0) or 0)
            fundo = [("Carteira de acoes", tot, kz(tot)), ("Reservas de liquidez", res_liq, kz(res_liq)), ("Capital por realizar", max(por_rea, 0), kz(max(por_rea, 0)))]
            _pdf_donut(pdf, fundo, cxs[1], y1 + r, r, ri, "Estrutura do fundo global", "")


def gerar_relatorio_pdf(resumo, df_activos, df_movimentos) -> bytes:
    tx  = t()
    pdf = _FPDFSeguro()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page("L")  # Landscape
    pdf.set_margins(left=20, top=30, right=30)  # esq 2cm, sup 3cm, dir 3cm
    pdf.set_fill_color(124, 31, 62)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "  CLUBE DE INVESTIMENTO APPO", ln=True, fill=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(0, 5, "  Casa nº 5 - Zona C, Av. Ministro Vieira Machado, Benguela, Angola", ln=True, fill=True)
    pdf.cell(0, 5, "  NIF: 001669404BA035  |  Tel.: 940 762 278 / 937 696 088  |  clube.investimento.appo@gmail.com", ln=True, fill=True)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 5, f"  Relatorio Patrimonial  |  Gerado em: {agora()}", ln=True, fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)
    _pdf_secao(pdf, "RESUMO PATRIMONIAL")
    cap_sub  = resumo["capital_subscrito"]
    cap_real = resumo["capital_realizado"]
    cap_por  = cap_sub - cap_real
    invest   = resumo["investimentos"]
    reservas = resumo["reservas"]
    _pdf_linha(pdf, "Capital Subscrito (total comprometido pelos socios)", kz(cap_sub))
    _pdf_linha(pdf, "Capital Realizado", kz(cap_real))
    _pdf_linha(pdf, "Capital por Realizar", kz(cap_por))
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(15, 6, "", ln=False)
    pdf.cell(90, 6, "dos quais, aplicado em Investimentos:", ln=False)
    pdf.cell(0, 6, kz(invest), align="R", ln=True)
    pdf.cell(15, 6, "", ln=False)
    pdf.cell(90, 6, "dos quais, em Reservas de Liquidez:", ln=False)
    pdf.cell(0, 6, kz(reservas), align="R", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(1)
    _pdf_linha(pdf, "PATRIMONIO TOTAL DO CLUBE", kz(cap_real), bold=True)
    # Carteira Real do Clube — dados registados nas avaliações com qtd e preco aquisição
    _pdf_secao(pdf, "CARTEIRA DE INVESTIMENTOS DO CLUBE")
    # Cruzar activos cotados com avaliações para obter qtd e preco aquisição
    df_aval_pdf = obter_avaliacoes()
    # Carteira REAL do Clube — lida ao vivo da tabela carteira_real (editável
    # pelo admin em "Painel do Administrador › Carteira Real"), já não de um
    # dicionário fixo no código. Se a tabela estiver vazia, o relatório mostra
    # isso mesmo, em vez de números antigos congelados.
    carteira_real_df = obter_carteira_real()
    df_cotacoes_pdf = df_activos.copy()
    linhas_carteira = []
    valor_total_carteira = 0.0
    mais_valias_total = 0.0
    # Limpar tickers da BD (podem vir como "UNTLAAAA" ou campo nome pode ter variações)
    df_cotacoes_pdf["ticker_clean"] = df_cotacoes_pdf["ticker"].str.strip().str.upper()
    for _, pos in carteira_real_df.iterrows():
        ticker_r = str(pos["ticker"] or "").strip().upper()
        row_cot = df_cotacoes_pdf[df_cotacoes_pdf["ticker_clean"] == ticker_r] if ticker_r else pd.DataFrame()
        if row_cot.empty:
            # recurso: se o ticker não bateu certo (ex.: activo entretanto
            # renomeado em Cotações), tenta encontrar pelo nome antes de
            # desistir e mostrar 0 — mais seguro do que esconder a posição.
            nome_r = str(pos["nome"] or "").strip().upper()
            if nome_r:
                row_cot = df_cotacoes_pdf[df_cotacoes_pdf["nome"].str.strip().str.upper() == nome_r]
        preco_act = float(row_cot["preco"].values[0]) if not row_cot.empty else 0.0
        var_dia   = float(row_cot["variacao"].values[0]) if not row_cot.empty else 0.0
        qtd       = float(pos["qtd"])
        val_aq    = float(pos["valor_aquisicao"])
        preco_aq  = val_aq / qtd if qtd else 0
        # Se cotação actual não disponível, usar valor de aquisição (sem mais-valia)
        val_act   = round(qtd * preco_act, 2) if preco_act and preco_act > 0 else val_aq
        mais_valia= val_act - val_aq
        mais_valia_pct = (mais_valia / val_aq * 100) if val_aq else 0
        valor_total_carteira += val_act
        mais_valias_total    += mais_valia
        linhas_carteira.append({
            "ticker": ticker_r, "nome": str(pos["nome"]), "qtd": qtd,
            "preco_aq": preco_aq, "preco_act": preco_act,
            "val_aq": val_aq, "val_act": val_act,
            "mais_valia": mais_valia, "mais_valia_pct": mais_valia_pct,
            "var_dia": var_dia,
        })

    # mesma ordem de Cotações & Activos (alfabética pelo nome do activo)
    linhas_carteira.sort(key=lambda l: l["nome"].strip().upper())
    if not linhas_carteira:
        pdf.set_font("Helvetica", "I", 9)
        pdf.cell(0, 7, "Sem posicoes registadas na carteira.", ln=True)
    else:
        # Cabeçalho tabela
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(236, 222, 227)
        # Landscape A4 útil = 297 - 20(esq) - 30(dir) = 247mm
        # [20+48+10+28+28+32+32+30+19] = 247 exacto
        W = [20, 48, 10, 28, 28, 32, 32, 30, 19]
        headers = ["Ticker","Nome","Qtd","P. Aquis.(Kz)","P. Actual(Kz)","V. Aquis.(Kz)","V. Actual(Kz)","Mais-Valia","Mais-V.%"]
        for h, w in zip(headers[:-1], W[:-1]):
            pdf.cell(w, 7, h, border="B", fill=True, ln=False, align="C")
        pdf.cell(0, 7, headers[-1], border="B", fill=True, ln=True, align="C")

        pdf.set_font("Helvetica", "", 8)
        for i, l in enumerate(linhas_carteira):
            fill = i % 2 == 0
            if fill:
                pdf.set_fill_color(250, 248, 246)
            else:
                pdf.set_fill_color(255, 255, 255)
            mv = l["mais_valia"]
            cor_mv = (107,114,128) if round(mv) == 0 else ((22,163,74) if mv > 0 else (220,38,38))

            def _c(txt, w, align="C", color=None, bold=False):
                if color:
                    pdf.set_text_color(*color)
                if bold:
                    pdf.set_font("Helvetica","B",8)
                pdf.cell(w, 6, str(txt), border="B", fill=fill, align=align, ln=False)
                if color or bold:
                    pdf.set_text_color(0,0,0)
                    pdf.set_font("Helvetica","",8)

            _c(l["ticker"][:8],       W[0])
            _c(l["nome"][:20],        W[1], "L")
            _c(str(l["qtd"]),         W[2])
            _c(kz(l["preco_aq"]),     W[3], "R")
            _c(kz(l["preco_act"]),    W[4], "R")
            _c(kz(l["val_aq"]),       W[5], "R")
            _c(kz(l["val_act"]),      W[6], "R")
            _c(kz(mv),                W[7], "R", cor_mv, True)
            vp = round(float(l["mais_valia_pct"]), 2)
            cor_vp = (107,114,128) if vp == 0 else ((22,163,74) if vp > 0 else (220,38,38))
            pdf.set_text_color(*cor_vp)
            pdf.set_font("Helvetica","B",8)
            pdf.cell(0, 6, pct_bruto(vp), border="B", fill=fill, align="R", ln=True)
            pdf.set_text_color(0,0,0)
            pdf.set_font("Helvetica","",8)

        # Totais
        pdf.ln(1)
        pdf.set_font("Helvetica","B",9)
        pdf.set_fill_color(236, 222, 227)
        mv_total_pct = (mais_valias_total / (valor_total_carteira - mais_valias_total) * 100) if (valor_total_carteira - mais_valias_total) else 0
        # W = [22,52,12,32,32,38,38,32,0] — soma fixas = 260, ultima=0
        # soma até V.Actual = 20+48+10+28+28+32+32 = 198
        soma_ate_vact = 20+48+10+28+28+32
        pdf.cell(soma_ate_vact, 7, "TOTAL DA CARTEIRA", border="B", fill=True, ln=False, align="R")
        pdf.cell(32, 7, kz(valor_total_carteira), border="B", fill=True, align="R", ln=False)
        cor_tot = (107,114,128) if round(mais_valias_total) == 0 else ((22,163,74) if mais_valias_total > 0 else (220,38,38))
        pdf.set_text_color(*cor_tot)
        pdf.cell(30, 7, kz(mais_valias_total), border="B", fill=True, align="R", ln=False)
        pdf.cell(19, 7, pct_bruto(round(mv_total_pct, 2)), border="B", fill=True, align="R", ln=True)
        pdf.set_text_color(0,0,0)
    # ---- Relatório executivo: sumário, matriz multitemporal + Alpha, inflação real, risco e gráficos de anel ----
    if linhas_carteira:
        try:
            _analise_pdf = calcular_analise_completa(df_activos)
            try:
                _mercado_pdf = ler_mercado_guardado()
            except Exception:
                _mercado_pdf = None
            if _analise_pdf.get("ok"):
                _pdf_bloco_executivo(pdf, _analise_pdf, resumo, _mercado_pdf, linhas_carteira)
            else:
                pdf.add_page("L")
                _pdf_secao(pdf, "RELATORIO EXECUTIVO")
                pdf.set_font("Helvetica", "I", 9)
                pdf.multi_cell(0, 5, "Seccao analitica indisponivel: " + str(_analise_pdf.get("motivo") or "dados insuficientes."))
        except Exception:
            traceback.print_exc()
            pdf.set_text_color(0, 0, 0)
    # Análise gráfica (página própria): composição, mais-valias por activo e evolução do património
    if linhas_carteira:
        try:
            pdf.add_page("L")
            _pdf_secao(pdf, "ANÁLISE GRÁFICA DA CARTEIRA")
            try:
                _vi_pdf = obter_vup_info()
            except Exception:
                _vi_pdf = None
            if _vi_pdf and _vi_pdf["unidades"] > 0 and _vi_pdf["vup"] > 0:
                _pdf_kpis_vup(pdf, _vi_pdf)
            _pdf_grafico_composicao(pdf, linhas_carteira)
            y_g = pdf.get_y() + 3
            if y_g + 76 > pdf.h - 20:
                pdf.add_page("L")
                y_g = pdf.get_y()
            _pdf_grafico_mais_valias(pdf, linhas_carteira, pdf.l_margin, y_g, 115, 50)
            try:
                df_hist_pdf = obter_historico_patrimonio()
            except Exception:
                df_hist_pdf = None
            _pdf_grafico_evolucao(pdf, df_hist_pdf, pdf.l_margin + 130, y_g, 117, 50)
            pdf.set_y(y_g + 72)
            pdf.set_text_color(0, 0, 0)
        except Exception:
            # os gráficos são um complemento: se algo falhar, o relatório sai na mesma, sem eles
            pdf.set_text_color(0, 0, 0)
        try:
            _tot_cart = sum(max(l["val_act"], 0) for l in linhas_carteira)
            _tot_qtd = sum(max(l["qtd"], 0) for l in linhas_carteira)
            _fundo = _tot_cart + float(resumo.get("reservas", 0) or 0)
            if _tot_cart > 0 and _tot_qtd > 0 and _fundo > 0:
                pdf.add_page("L")
                _pdf_secao(pdf, "CONCENTRAÇÃO E GOVERNANÇA DA CARTEIRA")
                y1 = pdf.get_y() + 2
                larg3 = 77
                x_a, x_b, x_c = pdf.l_margin, pdf.l_margin + larg3 + 8, pdf.l_margin + 2 * (larg3 + 8)
                itens_qtd = [(_pdf_nome_curto(l["nome"]), max(l["qtd"], 0) / _tot_qtd * 100) for l in linhas_carteira]
                itens_val = [(_pdf_nome_curto(l["nome"]), max(l["val_act"], 0) / _tot_cart * 100) for l in linhas_carteira]
                itens_act = [(_pdf_nome_curto(l["nome"]), max(l["val_act"], 0) / _fundo * 100) for l in linhas_carteira]
                f_a = _pdf_barras_simples(pdf, "Quantidade de títulos (% da carteira)", itens_qtd, x_a, y1, larg3, (166, 72, 106))
                f_b = _pdf_barras_simples(pdf, "Valor monetário (% da carteira)", itens_val, x_b, y1, larg3, (124, 31, 62))
                f_c = _pdf_barras_limite(pdf, "Peso no fundo global (limite 10%)", itens_act, x_c, y1, larg3, 10)
                fim_esq, fim_dir = max(f_a, f_b), f_c
                y2 = max(fim_esq, fim_dir) + 4
                por_sector = {}
                for l in linhas_carteira:
                    sct = _pdf_sector(l)
                    por_sector[sct] = por_sector.get(sct, 0.0) + max(l["val_act"], 0)
                itens_sec = sorted(((k, v / _fundo * 100) for k, v in por_sector.items()), key=lambda t: -t[1])
                fim_sec = _pdf_barras_limite(pdf, "Peso de cada sector no fundo global (limite: 20%)", itens_sec,
                                             pdf.l_margin, y2, 118, 20)
                # resumo de conformidade
                pdf.set_xy(pdf.l_margin + 130, y2)
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_text_color(0, 0, 0)
                pdf.cell(117, 6, "Cumprimento dos limites do Clube")
                excessos = [(f"{_pdf_nome_curto(l['nome'])}", max(l["val_act"], 0) / _fundo * 100) for l in linhas_carteira
                            if max(l["val_act"], 0) / _fundo * 100 > 10]
                excessos_s = [(k, p_) for k, p_ in itens_sec if p_ > 20]
                pdf.set_xy(pdf.l_margin + 130, y2 + 8)
                pdf.set_font("Helvetica", "", 8)
                if excessos or excessos_s:
                    pdf.set_text_color(220, 38, 38)
                    linhas_txt = [f"- {n}: {p_:.1f}% do fundo global (limite por activo: 10%)." for n, p_ in excessos]
                    linhas_txt += [f"- Sector {n}: {p_:.1f}% do fundo global (limite por sector: 20%)." for n, p_ in excessos_s]
                    pdf.multi_cell(117, 4.5, "\n".join(linhas_txt))
                else:
                    pdf.set_text_color(22, 163, 74)
                    pdf.multi_cell(117, 4.5, "Todos os limites de concentração (10% por activo e 20% por sector) estão a ser cumpridos.")
                pdf.set_text_color(120, 120, 120)
                pdf.set_font("Helvetica", "I", 7)
                pdf.set_xy(pdf.l_margin, max(fim_sec, pdf.get_y()) + 4)
                pdf.multi_cell(0, 3.8, "Fundo global = valor actual da carteira + reservas de liquidez. "
                                       "Sectores atribuídos pela app (Banca/Finanças inclui banca, seguros e BODIVA). "
                                       "O peso em títulos e em valor refere-se apenas à carteira de acções.")
                pdf.set_text_color(0, 0, 0)
        except Exception:
            pdf.set_text_color(0, 0, 0)
    _pdf_secao(pdf, "MOVIMENTOS RECENTES")
    if df_movimentos.empty:
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 7, tx["pdf_sem_mov"], ln=True)
    else:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(236, 222, 227)
        pdf.cell(28, 7, "Data",     border="B", fill=True, ln=False)
        pdf.cell(50, 7, "Tipo",     border="B", fill=True, ln=False)
        pdf.cell(70, 7, "Descricao",border="B", fill=True, ln=False)
        pdf.cell(0,  7, "Montante", border="B", fill=True, align="R", ln=True)
        pdf.set_font("Helvetica", "", 9)
        for i, (_, linha) in enumerate(df_movimentos.head(30).iterrows()):
            fill = i % 2 == 0
            if fill:
                pdf.set_fill_color(250, 248, 246)
            else:
                pdf.set_fill_color(255, 255, 255)
            pdf.cell(28, 6, str(linha["data_movimento"]),           border="B", fill=fill, ln=False)
            pdf.cell(50, 6, str(linha["tipo"])[:26],                border="B", fill=fill, ln=False)
            pdf.cell(70, 6, str(linha.get("descricao","") or "")[:38], border="B", fill=fill, ln=False)
            pdf.cell(0,  6, kz(linha["montante"]),                  border="B", fill=fill, align="R", ln=True)
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, "Clube de Investimento APPO  |  clube.investimento.appo@gmail.com  |  Benguela, Angola", align="C", ln=True)
    pdf.cell(0, 5, "Documento gerado automaticamente pela plataforma APPO. Uso interno e reservado.", align="C", ln=True)
    return bytes(pdf.output())


# ---------------- Avaliação ----------------
def obter_premissas_macro() -> dict:
    _garantir_tabelas_extra()
    linha = consultar_um("SELECT inflacao, taxa_livre_risco, premio_risco, beta_banca, beta_telecom, beta_outros, "
                         "inflacao_homologa, inflacao_vigente_m, inflacao_projectada, inflacao_ref, inflacao_data FROM premissas_macro WHERE id = 1")
    base = float(linha[0])
    return {"inflacao": base, "taxa_livre_risco": float(linha[1]), "premio_risco": float(linha[2]),
            "beta_banca": float(linha[3]), "beta_telecom": float(linha[4]), "beta_outros": float(linha[5]),
            # três medidas para os relatórios; sem valor guardado, usam-se valores por defeito derivados da inflação anual
            "inflacao_homologa": float(linha[6]) if linha[6] is not None else base,
            "inflacao_vigente_m": float(linha[7]) if linha[7] is not None else (1 + base) ** (1 / 12) - 1,
            "inflacao_projectada": float(linha[8]) if linha[8] is not None else base,
            "inflacao_ref": linha[9] or "", "inflacao_data": linha[10]}


def actualizar_inflacao_macro(homologa: float, vigente_m: float, projectada: float, ref: str):
    """Valores em fracção (0.135 = 13,5%). `vigente_m` é a variação mensal mais recente."""
    exigir_admin()
    _garantir_tabelas_extra()
    executar("UPDATE premissas_macro SET inflacao_homologa=%s, inflacao_vigente_m=%s, inflacao_projectada=%s, inflacao_ref=%s, inflacao_data=CURRENT_DATE WHERE id = 1",
             (homologa, vigente_m, projectada, ref.strip()))
    registar_auditoria("inflacao_macro", "premissas", "1", depois={"homologa": homologa, "vigente_m": vigente_m, "projectada": projectada, "ref": ref.strip()})


def actualizar_premissas_macro(inflacao, rf, erp, beta_banca, beta_telecom, beta_outros):
    exigir_admin()
    executar("UPDATE premissas_macro SET inflacao=%s, taxa_livre_risco=%s, premio_risco=%s, beta_banca=%s, beta_telecom=%s, beta_outros=%s, actualizado_em=NOW() WHERE id = 1",
             (inflacao, rf, erp, beta_banca, beta_telecom, beta_outros))

def obter_avaliacoes() -> pd.DataFrame:
    return consultar_df("SELECT id, empresa, sector, preco, acoes_circulacao, lucro_liquido, ganho_pontual, capital_proprio, dividendo_total, crescimento_g, actualizado_em FROM avaliacoes ORDER BY empresa")

def substituir_avaliacoes(df: pd.DataFrame):
    exigir_admin()
    executar("DELETE FROM avaliacoes")
    for _, linha in df.iterrows():
        empresa = str(linha.get("empresa", "")).strip()
        if not empresa:
            continue
        executar("INSERT INTO avaliacoes (empresa, sector, preco, acoes_circulacao, lucro_liquido, ganho_pontual, capital_proprio, dividendo_total, crescimento_g) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                 (empresa, str(linha.get("sector", "") or ""), float(linha.get("preco", 0) or 0),
                  float(linha.get("acoes_circulacao", 0) or 0), float(linha.get("lucro_liquido", 0) or 0),
                  float(linha.get("ganho_pontual", 0) or 0), float(linha.get("capital_proprio", 0) or 0),
                  float(linha.get("dividendo_total", 0) or 0), float(linha.get("crescimento_g", 0) or 0)))

def ke_por_sector(sector: str, premissas: dict) -> float:
    if sector == "Banca":
        beta = premissas["beta_banca"]
    elif sector == "Telecomunicações":
        beta = premissas["beta_telecom"]
    else:
        beta = premissas["beta_outros"]
    return premissas["taxa_livre_risco"] + beta * premissas["premio_risco"]

def calcular_metricas_avaliacao(av: dict, premissas: dict) -> dict:
    preco             = av["preco"]
    acoes             = av["acoes_circulacao"] or 0
    lucro_normalizado = av["lucro_liquido"] - av["ganho_pontual"]
    eps    = (av["lucro_liquido"] / acoes) if acoes else 0
    pe     = (preco / eps) if eps and eps > 0 else None
    bvps   = (av["capital_proprio"] / acoes) if acoes and av["capital_proprio"] else 0
    pbv    = (preco / bvps) if bvps and bvps > 0 else None
    dps    = (av["dividendo_total"] / acoes) if acoes else 0
    payout = (av["dividendo_total"] / av["lucro_liquido"]) if av["lucro_liquido"] else None
    dy_nominal = (dps / preco) if preco else 0
    dy_real    = dy_nominal - premissas["inflacao"]
    roe    = (lucro_normalizado / av["capital_proprio"]) if av["capital_proprio"] else None
    ke     = ke_por_sector(av["sector"], premissas)
    g      = av["crescimento_g"]
    d1     = dps * (1 + g)
    valor_justo = (d1 / (ke - g)) if ke > g else None
    upside = ((valor_justo - preco) / preco) if (valor_justo is not None and preco) else None
    return {"cap_mercado": preco * acoes, "eps": eps, "pe": pe, "pbv": pbv, "dps": dps,
            "payout": payout, "dy_nominal": dy_nominal, "dy_real": dy_real, "roe": roe,
            "ke": ke, "valor_justo": valor_justo, "upside": upside}


@st.cache_resource(show_spinner="A preparar a base de dados…")
def _arranque_bd():
    inicializar_bd()
    _garantir_tabelas_extra()
    return True


try:
    _arranque_bd()
except Exception as _erro_bd:
    st.error(f"Não foi possível preparar a base de dados: {type(_erro_bd).__name__}: {_erro_bd}")
    st.stop()

# =========================================================
# AUTENTICAÇÃO
# =========================================================
for _k, _v in [("autenticado", False), ("login_timestamp", None), ("conta_nome", ""), ("conta_email", ""), ("is_admin", False), ("is_premium", False), ("is_participante", False), ("nivel", "iniciante"), ("perfil", None), ("perfil_data", None), ("trocar_password", False)]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

if st.session_state["autenticado"] and st.session_state["login_timestamp"]:
    if time.time() - st.session_state["login_timestamp"] > TEMPO_LIMITE_SESSAO_SEGUNDOS:
        st.session_state["autenticado"] = False
        st.session_state["login_timestamp"] = None
        st.warning("A tua sessão expirou por inactividade. Inicia sessão novamente.")


# =========================================================
# EDUCAÇÃO & SERVIÇOS · MANIFESTAÇÃO DE INTERESSE · DESPESAS DO GRUPO
# (as áreas públicas NÃO dão acesso à carteira nem tornam ninguém participante dos investimentos)
# =========================================================
import re as _re_pub

TEXTO_MANIFESTACAO = ("Manifestação de interesse — este pedido não constitui admissão, atribuição de cotas nem autorização para transferir dinheiro. "
                      "As novas admissões dependem da definição e validação da estrutura aplicável.")
MSG_INSCRICAO = "Inscrição recebida. A confirmação e as instruções de pagamento serão comunicadas posteriormente."
AVISO_EDUCACAO = ("Conteúdo educativo e informativo, sem recomendações personalizadas de compra ou venda. "
                  "A inscrição num serviço educativo não representa subscrição de valores mobiliários nem atribuição de participação patrimonial. "
                  "O APPO é uma iniciativa independente de educação financeira, sem vínculo com a BODIVA, a CMC ou correctoras.")
ESTADOS_SERVICO = ["Recebido", "Confirmado", "Cancelado", "Concluído"]
ESTADOS_MANIFESTACAO = ["Recebida", "Em análise", "Arquivada"]
ESTADOS_DESPESA = ["Proposta", "Aprovada", "Rejeitada"]
_REGEX_EMAIL = _re_pub.compile(r"^[^@\s]{1,64}@[^@\s]{1,200}\.[^@\s]{2,}$")


def validar_contacto(nome: str, email: str, telefone: str):
    """Devolve uma mensagem de erro ou None se os dados de contacto forem aceitáveis."""
    nome, email, telefone = (nome or "").strip(), (email or "").strip(), (telefone or "").strip()
    if len(nome) < 2 or len(nome) > 120:
        return "Indique o seu nome (2 a 120 caracteres)."
    if not email and not telefone:
        return "Indique pelo menos um contacto: e-mail ou telefone."
    if email and not _REGEX_EMAIL.match(email):
        return "O e-mail indicado não parece válido."
    if len(telefone) > 30:
        return "O telefone indicado é demasiado longo."
    return None


def _pode_enviar(chave: str, segundos: int = 30) -> bool:
    """Limite simples por sessão para evitar envios repetidos por engano ou abuso."""
    agora = time.time()
    if agora - float(st.session_state.get(chave, 0)) < segundos:
        return False
    st.session_state[chave] = agora
    return True


def obter_servicos_publicos() -> pd.DataFrame:
    # Só serviços educativos, activos e visíveis: as propostas de consultoria nunca aparecem em público.
    return consultar_df("SELECT id, nome, descricao, preco, nota_preco, contratavel FROM servicos_catalogo "
                        "WHERE activo = TRUE AND visivel_publico = TRUE AND tipo = 'educativo' ORDER BY ordem, id")


def registar_pedido_servico(servico_id: int, nome: str, email: str, telefone: str, participantes: int, mensagem: str):
    s = consultar_um("SELECT id, nome FROM servicos_catalogo WHERE id = %s AND activo = TRUE AND visivel_publico = TRUE AND tipo = 'educativo'", (int(servico_id),))
    if not s:
        raise ValueError("Este serviço já não está disponível.")
    executar("INSERT INTO pedidos_servicos (servico_id, servico_nome, nome, email, telefone, participantes, mensagem) VALUES (%s, %s, %s, %s, %s, %s, %s)",
             (s[0], s[1], nome.strip(), email.strip() or None, telefone.strip() or None, int(participantes), (mensagem or "").strip()[:1000] or None))


def registar_manifestacao_interesse(nome: str, email: str, telefone: str, mensagem: str, profissao: str = ""):
    executar("INSERT INTO manifestacoes_interesse (nome, email, telefone, mensagem, profissao, consentimento) VALUES (%s, %s, %s, %s, %s, TRUE)",
             (nome.strip(), email.strip() or None, telefone.strip() or None, (mensagem or "").strip()[:1000] or None, (profissao or "").strip()[:120] or None))


def pagina_educacao_servicos():
    st.markdown("### 🎓 APPO — Educação Financeira")
    st.write("O APPO nasceu em Benguela, em 2024, como um grupo de estudo e prática de investimento. Aqui encontra formação, guias e ferramentas educativas "
             "sobre o mercado angolano: BODIVA, acções, dividendos, riscos e comissões, leitura de demonstrações financeiras, valuation com exercícios e planeamento financeiro (regra 50/30/20).")
    aviso_discreto(AVISO_EDUCACAO)
    st.markdown("#### Formação e workshops")
    try:
        df = obter_servicos_publicos()
    except Exception:
        st.warning("O catálogo não está disponível neste momento. Tente novamente dentro de instantes.")
        return
    if df.empty:
        st.info("Brevemente. Entretanto, pode deixar o seu contacto na secção «Manifestação de interesse».")
        return
    for _, s in df.iterrows():
        sid = int(s["id"])
        _preco_txt = (f"{kz(s['preco'])} por participante" if pd.notna(s["preco"]) else "Sob consulta")
        _nota_p = str(s["nota_preco"] or "").strip() if pd.notna(s["preco"]) else ""
        render_html(f'<div class="fx-servico fx-g{sid % 4}"><div class="fx-servico-topo"></div><div class="fx-servico-corpo">'
                    f'<div class="fx-servico-nome">{_esc(s["nome"])}</div><div class="fx-servico-desc">{_esc(s["descricao"] or "")}</div>'
                    f'<span class="fx-chip">💰 {_esc(_preco_txt)}</span>' + (f'<span class="fx-chip-nota">{_esc(_nota_p)}</span>' if _nota_p else "") + '</div></div>')
        with st.container():
            rotulo = "Pedir inscrição" if bool(s["contratavel"]) else "Pedir informações"
            with st.expander(rotulo):
                with st.form(f"form_pedido_{sid}", clear_on_submit=True):
                    _pn, _ap = st.columns(2)
                    _nome_p = _pn.text_input("Nome próprio", key=f"ped_nome_{sid}", max_chars=60)
                    _apelido = _ap.text_input("Apelido(s)", key=f"ped_apel_{sid}", max_chars=60)
                    nome = f"{_nome_p.strip()} {_apelido.strip()}".strip()
                    c1, c2 = st.columns(2)
                    email = c1.text_input("E-mail", key=f"ped_email_{sid}", max_chars=200)
                    tel = c2.text_input("Telefone", key=f"ped_tel_{sid}", max_chars=30)
                    n_part = st.number_input("Número de participantes", min_value=1, max_value=200, value=1, step=1, key=f"ped_n_{sid}")
                    msg = st.text_area("Mensagem (opcional)", key=f"ped_msg_{sid}", max_chars=1000)
                    ok = st.checkbox("Autorizo o APPO a usar estes dados apenas para responder a este pedido.", key=f"ped_ok_{sid}")
                    enviar = st.form_submit_button(rotulo)
                if enviar:
                    erro = "Indique o nome próprio e o apelido." if not (_nome_p.strip() and _apelido.strip()) else validar_contacto(nome, email, tel)
                    if erro:
                        st.error(erro)
                    elif not ok:
                        st.error("É necessário autorizar o uso dos dados para responder ao pedido.")
                    elif not _pode_enviar("ultimo_pedido_servico"):
                        st.warning("Aguarde alguns segundos antes de enviar outro pedido.")
                    else:
                        try:
                            registar_pedido_servico(sid, nome, email, tel, int(n_part), msg)
                            st.success(MSG_INSCRICAO)
                        except Exception as e:
                            st.error(f"Não foi possível registar o pedido: {e}")
    aviso_discreto("Valores indicativos, sujeitos a alteração. Nenhum pagamento é pedido nesta página.")


def pagina_manifestacao_interesse():
    st.markdown("### 🤝 Manifestação de interesse")
    st.info(TEXTO_MANIFESTACAO)
    aviso_discreto("Nesta fase pedimos apenas o necessário: nome, contacto, profissão e motivação. Não pedimos capital, BI, NIF, morada nem origem de fundos — esses dados só são solicitados, mais tarde, se avançar para a admissão formal, e ficam acessíveis apenas aos administradores.")
    with st.form("form_manifestacao", clear_on_submit=True):
        _pn, _ap = st.columns(2)
        _nome_p = _pn.text_input("Nome próprio", max_chars=60)
        _apelido = _ap.text_input("Apelido(s)", max_chars=60)
        nome = f"{_nome_p.strip()} {_apelido.strip()}".strip()
        c1, c2 = st.columns(2)
        email = c1.text_input("E-mail", max_chars=200)
        tel = c2.text_input("Telefone", max_chars=30)
        profissao = st.text_input("Profissão", max_chars=120)
        msg = st.text_area("Motivação: porque quer participar no Clube?", max_chars=1000)
        ok = st.checkbox("Compreendo que isto não é uma admissão e consinto, de forma expressa, que o APPO trate estes dados apenas para me contactar sobre este assunto, nos termos da Lei n.º 22/11 (Lei da Protecção de Dados Pessoais).")
        enviar = st.form_submit_button("Enviar manifestação de interesse")
    if enviar:
        erro = "Indique o nome próprio e o apelido." if not (_nome_p.strip() and _apelido.strip()) else validar_contacto(nome, email, tel)
        if erro:
            st.error(erro)
        elif not ok:
            st.error("É necessário confirmar que compreende o âmbito deste pedido.")
        elif not _pode_enviar("ultima_manifestacao"):
            st.warning("Aguarde alguns segundos antes de enviar outro pedido.")
        else:
            try:
                registar_manifestacao_interesse(nome, email, tel, msg, profissao)
                st.success("Manifestação de interesse recebida. Entraremos em contacto, se e quando houver novidades.")
            except Exception as e:
                st.error(f"Não foi possível registar o pedido: {e}")


# ---------------- Administração (sempre protegida no código, não só escondida) ----------------
def actualizar_estado_pedido(pid: int, novo_estado: str):
    exigir_admin()
    if novo_estado not in ESTADOS_SERVICO:
        raise ValueError("Estado inválido.")
    antes = consultar_um("SELECT estado_servico FROM pedidos_servicos WHERE id = %s", (int(pid),))
    if not antes:
        raise ValueError("Pedido inexistente.")
    with transaccao() as cur:
        cur.execute("UPDATE pedidos_servicos SET estado_servico = %s WHERE id = %s", (novo_estado, int(pid)))
        registar_auditoria("pedido_estado_servico", "pedidos_servicos", pid, antes={"estado_servico": antes[0]}, depois={"estado_servico": novo_estado}, cur=cur)


def confirmar_pagamento_pedido(pid: int, nota: str):
    """O recebimento só é confirmado pelo administrador, com nota, e fica auditado. Um comprovativo recebido não confirma nada por si."""
    exigir_admin()
    if not (nota or "").strip():
        raise ValueError("Indique uma nota (referência, data, forma de recebimento).")
    antes = consultar_um("SELECT estado_pagamento FROM pedidos_servicos WHERE id = %s", (int(pid),))
    if not antes:
        raise ValueError("Pedido inexistente.")
    if antes[0] == "Confirmado":
        raise ValueError("O pagamento já está confirmado.")
    with transaccao() as cur:
        cur.execute("UPDATE pedidos_servicos SET estado_pagamento = 'Confirmado', pagamento_confirmado_por = %s, pagamento_confirmado_em = NOW(), pagamento_nota = %s "
                    "WHERE id = %s AND estado_pagamento <> 'Confirmado'", (utilizador_actual(), nota.strip(), int(pid)))
        registar_auditoria("pagamento_confirmado", "pedidos_servicos", pid, antes={"estado_pagamento": antes[0]}, depois={"estado_pagamento": "Confirmado"}, motivo=nota.strip(), cur=cur)


def actualizar_estado_manifestacao(mid: int, novo_estado: str):
    exigir_admin()
    if novo_estado not in ESTADOS_MANIFESTACAO:
        raise ValueError("Estado inválido.")
    antes = consultar_um("SELECT estado FROM manifestacoes_interesse WHERE id = %s", (int(mid),))
    if not antes:
        raise ValueError("Registo inexistente.")
    with transaccao() as cur:
        cur.execute("UPDATE manifestacoes_interesse SET estado = %s WHERE id = %s", (novo_estado, int(mid)))
        registar_auditoria("manifestacao_estado", "manifestacoes_interesse", mid, antes={"estado": antes[0]}, depois={"estado": novo_estado}, cur=cur)


def actualizar_servico_catalogo(sid: int, preco, nota_preco: str, activo: bool, visivel: bool, contratavel: bool):
    exigir_admin()
    antes = consultar_um("SELECT tipo, preco, nota_preco, activo, visivel_publico, contratavel FROM servicos_catalogo WHERE id = %s", (int(sid),))
    if not antes:
        raise ValueError("Serviço inexistente.")
    if antes[0] != "educativo":
        raise ValueError("As propostas de consultoria ficam bloqueadas até o enquadramento profissional e regulatório ser validado.")
    if preco is not None and preco < 0:
        raise ValueError("O preço não pode ser negativo.")
    with transaccao() as cur:
        cur.execute("UPDATE servicos_catalogo SET preco = %s, nota_preco = %s, activo = %s, visivel_publico = %s, contratavel = %s WHERE id = %s",
                    (preco, (nota_preco or "").strip() or None, bool(activo), bool(visivel), bool(contratavel), int(sid)))
        registar_auditoria("catalogo_alterado", "servicos_catalogo", sid,
                           antes={"preco": antes[1], "nota_preco": antes[2], "activo": antes[3], "visivel": antes[4], "contratavel": antes[5]},
                           depois={"preco": preco, "nota_preco": nota_preco, "activo": activo, "visivel": visivel, "contratavel": contratavel}, cur=cur)


def registar_despesa_admin(data, descricao: str, categoria: str, valor, fornecedor: str, nota: str):
    exigir_admin()
    v = dec(valor)
    if v <= 0:
        raise ValueError("O valor deve ser maior que zero.")
    if not (descricao or "").strip():
        raise ValueError("Indique a descrição.")
    with transaccao() as cur:
        cur.execute("INSERT INTO despesas_admin (data, descricao, categoria, valor, fornecedor, estado, nota, criado_por) VALUES (%s, %s, %s, %s, %s, 'Proposta', %s, %s) RETURNING id",
                    (data, descricao.strip(), (categoria or "").strip() or None, v, (fornecedor or "").strip() or None, (nota or "").strip() or None, utilizador_actual()))
        novo_id = cur.fetchone()[0]
        registar_auditoria("despesa_proposta", "despesas_admin", novo_id, depois={"descricao": descricao.strip(), "valor": str(v)}, cur=cur)


def decidir_despesa_admin(did: int, aprovar: bool, motivo: str):
    exigir_admin()
    if not (motivo or "").strip():
        raise ValueError("Indique o fundamento da decisão (ex.: deliberação dos participantes).")
    antes = consultar_um("SELECT estado FROM despesas_admin WHERE id = %s", (int(did),))
    if not antes:
        raise ValueError("Despesa inexistente.")
    if antes[0] != "Proposta":
        raise ValueError("Só se decide sobre despesas em estado «Proposta».")
    novo = "Aprovada" if aprovar else "Rejeitada"
    with transaccao() as cur:
        cur.execute("UPDATE despesas_admin SET estado = %s, aprovada_por = %s, aprovada_em = NOW(), nota = COALESCE(nota || ' | ', '') || %s WHERE id = %s AND estado = 'Proposta'",
                    (novo, utilizador_actual(), motivo.strip(), int(did)))
        registar_auditoria("despesa_decisao", "despesas_admin", did, antes={"estado": antes[0]}, depois={"estado": novo}, motivo=motivo.strip(), cur=cur)


def painel_educacao_servicos_admin():
    exigir_admin()
    sub_ped, sub_man, sub_cat = st.tabs(["Pedidos e inscrições", "Manifestações de interesse", "Catálogo"])
    with sub_ped:
        df = consultar_df("SELECT id, criado_em, servico_nome, nome, email, telefone, participantes, mensagem, estado_servico, estado_pagamento, "
                          "pagamento_confirmado_por, pagamento_confirmado_em, pagamento_nota FROM pedidos_servicos ORDER BY id DESC LIMIT 500")
        if df.empty:
            st.info("Ainda não há pedidos.")
        else:
            st.dataframe(df, hide_index=True)
            st.caption("O estado do serviço e o estado do pagamento são independentes. Um pedido ou comprovativo recebido não é pagamento: só o administrador confirma o recebimento, com nota, e fica auditado.")
            _ids = [int(i) for i in df["id"].tolist()]
            pid = st.selectbox("Pedido", _ids, key="adm_ped_sel",
                               format_func=lambda i: f"#{i} · {df.loc[df['id'] == i, 'nome'].iloc[0]} · {df.loc[df['id'] == i, 'servico_nome'].iloc[0]}")
            lin = df[df["id"] == pid].iloc[0]
            c1, c2 = st.columns(2)
            with c1:
                _idx = ESTADOS_SERVICO.index(lin["estado_servico"]) if lin["estado_servico"] in ESTADOS_SERVICO else 0
                novo = st.selectbox("Estado do serviço", ESTADOS_SERVICO, index=_idx, key=f"adm_est_{pid}")
                if st.button("Guardar estado do serviço", key=f"adm_est_btn_{pid}"):
                    try:
                        actualizar_estado_pedido(int(pid), novo)
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
            with c2:
                st.markdown(f"Pagamento: **{lin['estado_pagamento']}**")
                if lin["estado_pagamento"] != "Confirmado":
                    nota = st.text_input("Nota do recebimento (obrigatória)", key=f"adm_pag_nota_{pid}")
                    if st.button("Confirmar recebimento do pagamento", key=f"adm_pag_btn_{pid}"):
                        try:
                            confirmar_pagamento_pedido(int(pid), nota)
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
    with sub_man:
        dfm = consultar_df("SELECT id, criado_em, nome, email, telefone, profissao, mensagem, consentimento, estado FROM manifestacoes_interesse ORDER BY id DESC LIMIT 500")
        st.caption("Registos de interesse. Não são admissões nem dão direito a cotas. A admissão futura continua desactivada.")
        if dfm.empty:
            st.info("Ainda não há manifestações de interesse.")
        else:
            st.dataframe(dfm, hide_index=True)
            _mids = [int(i) for i in dfm["id"].tolist()]
            mid = st.selectbox("Registo", _mids, key="adm_man_sel", format_func=lambda i: f"#{i} · {dfm.loc[dfm['id'] == i, 'nome'].iloc[0]}")
            _est = dfm.loc[dfm["id"] == mid, "estado"].iloc[0]
            nm = st.selectbox("Estado", ESTADOS_MANIFESTACAO, index=ESTADOS_MANIFESTACAO.index(_est) if _est in ESTADOS_MANIFESTACAO else 0, key=f"adm_man_est_{mid}")
            if st.button("Guardar estado", key=f"adm_man_btn_{mid}"):
                try:
                    actualizar_estado_manifestacao(int(mid), nm)
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    with sub_cat:
        dfc = consultar_df("SELECT id, nome, tipo, preco, nota_preco, activo, visivel_publico, contratavel FROM servicos_catalogo ORDER BY ordem, id")
        st.dataframe(dfc, hide_index=True)
        st.caption("As propostas de consultoria ficam bloqueadas (inactivas e não contratáveis) até validar o enquadramento profissional e regulatório.")
        _edu = dfc[dfc["tipo"] == "educativo"]
        if not _edu.empty:
            _sids = [int(i) for i in _edu["id"].tolist()]
            sid = st.selectbox("Serviço educativo a editar", _sids, key="adm_cat_sel", format_func=lambda i: str(_edu.loc[_edu["id"] == i, "nome"].iloc[0]))
            r = _edu[_edu["id"] == sid].iloc[0]
            with st.form(f"form_cat_{sid}"):
                sem_preco = st.checkbox("Sob consulta (sem preço)", value=pd.isna(r["preco"]))
                preco = st.number_input("Preço por participante (Kz)", min_value=0.0, step=500.0, value=0.0 if pd.isna(r["preco"]) else float(r["preco"]))
                nota_p = st.text_input("Nota do preço", value=str(r["nota_preco"] or ""))
                a1, a2, a3 = st.columns(3)
                activo = a1.checkbox("Activo", value=bool(r["activo"]))
                visivel = a2.checkbox("Visível ao público", value=bool(r["visivel_publico"]))
                contr = a3.checkbox("Aceita inscrições", value=bool(r["contratavel"]))
                if st.form_submit_button("Guardar serviço"):
                    try:
                        actualizar_servico_catalogo(int(sid), None if sem_preco else preco, nota_p, activo, visivel, contr)
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))


def painel_despesas_admin():
    exigir_admin()
    st.caption("Despesas aprovadas do grupo (informação especializada, ferramentas, IA, contabilidade, funcionamento). Não servem para pagar aos fundadores nem para recuperar perdas históricas. "
               "A regra de repartição dos custos deve ser aprovada pelos participantes; a aplicação não a escolhe sozinha.")
    df = consultar_df("SELECT id, data, descricao, categoria, valor, fornecedor, estado, aprovada_por, aprovada_em, nota FROM despesas_admin ORDER BY data DESC, id DESC LIMIT 500")
    if not df.empty:
        st.dataframe(df, hide_index=True)
        _tot = consultar_um("SELECT COALESCE(SUM(valor), 0) FROM despesas_admin WHERE estado = 'Aprovada'")[0]
        st.metric("Total de despesas aprovadas", kz(_tot))
        _pend = [int(i) for i in df.loc[df["estado"] == "Proposta", "id"].tolist()]
        if _pend:
            did = st.selectbox("Despesa em proposta", _pend, key="adm_desp_sel", format_func=lambda i: f"#{i} · {df.loc[df['id'] == i, 'descricao'].iloc[0]}")
            mot = st.text_input("Fundamento da decisão (obrigatório)", key=f"adm_desp_mot_{did}")
            b1, b2 = st.columns(2)
            if b1.button("Aprovar", key=f"adm_desp_ok_{did}"):
                try:
                    decidir_despesa_admin(int(did), True, mot)
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
            if b2.button("Rejeitar", key=f"adm_desp_no_{did}"):
                try:
                    decidir_despesa_admin(int(did), False, mot)
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    else:
        st.info("Ainda não há despesas registadas.")
    with st.expander("Registar despesa (fica como «Proposta»)"):
        with st.form("form_despesa_admin", clear_on_submit=True):
            d1, d2 = st.columns(2)
            _data = d1.date_input("Data", value=datetime.now().date())
            _valor = d2.number_input("Valor (Kz)", min_value=0.0, step=500.0)
            _desc = st.text_input("Descrição")
            e1, e2 = st.columns(2)
            _cat = e1.text_input("Categoria (ex.: ferramentas, IA, contabilidade)")
            _forn = e2.text_input("Fornecedor")
            _nota = st.text_input("Nota / referência do documento comprovativo")
            if st.form_submit_button("Registar proposta"):
                try:
                    registar_despesa_admin(_data, _desc, _cat, _valor, _forn, _nota)
                    st.rerun()
                except Exception as e:
                    st.error(str(e))


# =========================================================
# CAPACIDADE FINANCEIRA — diagnóstico, treino e ferramentas
# Modelo de Kempson et al. (2005): 3 componentes (conhecimento, atitude, comportamento) × 5 domínios.
# Instrumento educativo; não é uma escala psicometricamente validada.
# =========================================================
DOMINIOS_CF = {
    "D1": "Fazer face às despesas",
    "D2": "Manter o controlo",
    "D3": "Planear o futuro",
    "D4": "Escolher produtos",
    "D5": "Manter-se informado e obter ajuda",
}
COMPONENTES_CF = {"K": "Conhecimento", "A": "Atitude e confiança", "B": "Comportamento"}
ESCALA_FREQ = ["Nunca", "Raramente", "Às vezes", "Frequentemente", "Sempre"]
ESCALA_CONC = ["Discordo totalmente", "Discordo", "Neutro", "Concordo", "Concordo totalmente"]
_NAO_SEI = "Não sei"

ITENS_CF = [
    # ---- Conhecimento (resposta certa/errada) ----
    {"id": "k1", "dom": "D2", "comp": "K", "tipo": "mc", "correcta": 1,
     "texto": "Depositou 500.000 Kz numa conta com juro de 5% ao ano. Ao fim de 2 anos, sem levantamentos, o saldo será:",
     "opcoes": ["Exactamente 550.000 Kz", "Mais de 550.000 Kz", "Menos de 550.000 Kz", _NAO_SEI]},
    {"id": "k2", "dom": "D1", "comp": "K", "tipo": "mc", "correcta": 1,
     "texto": "Se a inflação anual for 10% e o juro da sua poupança for 6%, ao fim de um ano o poder de compra do dinheiro depositado:",
     "opcoes": ["Aumenta", "Diminui", "Permanece igual", _NAO_SEI]},
    {"id": "k3", "dom": "D3", "comp": "K", "tipo": "mc", "correcta": 1,
     "texto": "Diversificar uma carteira de investimentos significa:",
     "opcoes": ["Aplicar todo o capital num único activo de baixo risco", "Distribuir o capital por diferentes activos para reduzir o risco total",
                "Aplicar apenas em activos de elevada rentabilidade esperada", _NAO_SEI]},
    {"id": "k4", "dom": "D3", "comp": "K", "tipo": "mc", "correcta": 0,
     "texto": "Em geral, a relação entre risco e retorno esperado de um investimento é:",
     "opcoes": ["Maior risco tende a acompanhar maior retorno esperado", "Menor risco tende a acompanhar maior retorno esperado",
                "Não existe qualquer relação", _NAO_SEI]},
    {"id": "k5", "dom": "D4", "comp": "K", "tipo": "mc", "correcta": 1,
     "texto": "O que é um dividendo?",
     "opcoes": ["Uma taxa cobrada pelo banco pela manutenção da conta", "Uma parte dos lucros de uma empresa distribuída aos seus accionistas",
                "O valor nominal de uma obrigação do tesouro", _NAO_SEI]},
    {"id": "k6", "dom": "D4", "comp": "K", "tipo": "mc", "correcta": 1,
     "texto": "Os Bilhetes do Tesouro (BT) emitidos pelo Estado angolano são:",
     "opcoes": ["Acções de empresas públicas cotadas na BODIVA",
                "Títulos de dívida pública de curto prazo (menos de 1 ano), remunerados por desconto",
                "Depósitos a prazo garantidos pelo Banco Nacional de Angola", _NAO_SEI]},
    {"id": "k7", "dom": "D5", "comp": "K", "tipo": "mc", "correcta": 1,
     "texto": "Qual é a entidade reguladora e supervisora do mercado de capitais angolano?",
     "opcoes": ["Banco Nacional de Angola (BNA)", "Comissão do Mercado de Capitais (CMC)", "Ministério das Finanças (MINFIN)", _NAO_SEI]},
    {"id": "k8", "dom": "D5", "comp": "K", "tipo": "mc", "correcta": 1,
     "texto": "Para um investidor individual comprar e vender títulos na BODIVA é necessário, em regra:",
     "opcoes": ["Ter conta directamente na BODIVA, sem intermediários", "Recorrer a uma sociedade correctora autorizada pela CMC",
                "Ser funcionário de uma instituição financeira", _NAO_SEI]},
    # ---- Atitude e confiança (concordância 1–5) ----
    {"id": "a1", "dom": "D1", "comp": "A", "tipo": "conc", "texto": "Sinto-me confiante para equilibrar o meu orçamento mesmo quando o rendimento varia."},
    {"id": "a2", "dom": "D2", "comp": "A", "tipo": "conc", "texto": "Sei, em cada momento, quanto gasto e para onde vai o meu dinheiro."},
    {"id": "a3", "dom": "D3", "comp": "A", "tipo": "conc", "texto": "Sinto-me capaz de planear o meu futuro financeiro (reserva, objectivos, investimento)."},
    {"id": "a4", "dom": "D4", "comp": "A", "tipo": "conc", "texto": "Sei escolher produtos financeiros adequados ao meu perfil e aos meus objectivos."},
    {"id": "a5", "dom": "D5", "comp": "A", "tipo": "conc", "texto": "Sei como proceder, na prática, para começar a investir hoje."},
    {"id": "a6", "dom": "D4", "comp": "A", "tipo": "conc", "meta": True, "texto": "Considero que compreendo bem o que são os Bilhetes do Tesouro."},
    # ---- Comportamento (frequência / concordância 1–5) ----
    {"id": "b1", "dom": "D1", "comp": "B", "tipo": "freq", "texto": "Consigo cobrir as despesas do mês sem recorrer a empréstimos ou dívidas."},
    {"id": "b2", "dom": "D2", "comp": "B", "tipo": "freq", "texto": "Registo as minhas receitas e despesas (caderno, folha de cálculo ou aplicação)."},
    {"id": "b3", "dom": "D2", "comp": "B", "tipo": "freq", "texto": "Pago as contas e as dívidas dentro do prazo."},
    {"id": "b4", "dom": "D3", "comp": "B", "tipo": "conc", "texto": "Tenho uma reserva de emergência para pelo menos 3 meses de despesas essenciais."},
    {"id": "b5", "dom": "D3", "comp": "B", "tipo": "freq", "texto": "Poupo uma parte do meu rendimento todos os meses."},
    {"id": "b6", "dom": "D4", "comp": "B", "tipo": "freq", "texto": "Antes de contratar um produto financeiro, comparo custos (comissões, taxas) e condições."},
    {"id": "b7", "dom": "D5", "comp": "B", "tipo": "freq", "texto": "Procuro informação em fontes fiáveis antes de tomar uma decisão financeira importante."},
]
_ITEM_CF = {i["id"]: i for i in ITENS_CF}

ACOES_CF = {
    ("D1", "K"): ("Perceba como a inflação corrói o poder de compra e porque é que o rendimento real é o que conta.", "Reserva de emergência e inflação"),
    ("D1", "A"): ("Treine com números: calcule o seu rendimento prudente e veja que o essencial fica coberto mesmo no pior mês.", "Orçamento com rendimento variável"),
    ("D1", "B"): ("Defina um «ordenado» mensal estável a partir do rendimento prudente e guarde o excedente dos meses melhores.", "Orçamento com rendimento variável"),
    ("D2", "K"): ("Reveja juros simples e compostos e veja o efeito do tempo no simulador de juros compostos.", "Simulador de Investimento"),
    ("D2", "A"): ("Faça 30 dias de registo de todas as despesas: a confiança vem de conhecer os números.", "Princípio 50/30/20 (orçamento mensal)"),
    ("D2", "B"): ("Dedique 10 minutos por semana a registar receitas e despesas e pague as contas no dia em que recebe.", "Princípio 50/30/20 (orçamento mensal)"),
    ("D3", "K"): ("Estude diversificação e a relação risco–retorno e aplique-as na carteira virtual.", "Simulador de Investimento"),
    ("D3", "A"): ("Defina um objectivo concreto (valor e prazo) e divida-o em metas mensais.", "Reserva de emergência e inflação"),
    ("D3", "B"): ("Construa a reserva de emergência por etapas e automatize a poupança no dia do recebimento.", "Reserva de emergência e inflação"),
    ("D4", "K"): ("Distinga depósito a prazo, bilhete do Tesouro, obrigação e acção: liquidez, risco, prazo e rendimento real.", "Comparador de instrumentos"),
    ("D4", "A"): ("Compare instrumentos pelo rendimento real antes de decidir; a confiança constrói-se com prática simulada.", "Comparador de instrumentos"),
    ("D4", "B"): ("Antes de contratar, compare sempre custos (comissões, taxas), prazo e liquidez numa tabela.", "Comparador de instrumentos"),
    ("D5", "K"): ("Conheça o circuito: quem regula, onde se negoceia e porque é necessária uma correctora autorizada.", "Primeiro investimento guiado"),
    ("D5", "A"): ("Siga o percurso guiado do primeiro investimento, passo a passo, e treine no Home Broker virtual.", "Primeiro investimento guiado"),
    ("D5", "B"): ("Escolha 2 ou 3 fontes fiáveis e reserve 30 minutos por semana para as ler antes de decidir.", "Biblioteca Educativa"),
}

LICOES_CF = {
    "D1": ("Fazer face às despesas com rendimento irregular",
           "Quando o rendimento varia, planeie pelo mês fraco, não pelo mês bom. O «rendimento prudente» (média dos 3 meses mais baixos) é a base do orçamento; "
           "o que sobra nos meses melhores alimenta um fundo de alisamento. Em Kwanzas, a inflação faz com que dinheiro parado perca poder de compra.",
           "Introduza os últimos 6 meses de rendimento na ferramenta de orçamento variável e veja se o essencial fica coberto no pior cenário."),
    "D2": ("Manter o controlo",
           "Controlo é saber quanto entra, quanto sai e para onde vai. Um registo simples e regular vale mais do que uma folha complicada. "
           "Pagar a tempo evita juros e multas; os juros compostos funcionam a favor de quem poupa e contra quem deve.",
           "Durante 30 dias registe todas as despesas no orçamento mensal e compare com a regra 50/30/20."),
    "D3": ("Planear o futuro",
           "Planear é transformar objectivos em metas mensais. A reserva de emergência (3 a 6 meses de despesas essenciais, mais se o rendimento for variável) vem antes de investir. "
           "Diversificar reduz o risco; maior retorno esperado costuma exigir maior risco.",
           "Calcule a sua reserva-alvo ajustada à inflação e defina quanto poupar por mês para a atingir."),
    "D4": ("Escolher produtos",
           "Escolher bem é comparar o rendimento REAL (depois de inflação e impostos), a liquidez, o risco e os custos. Um Bilhete do Tesouro é dívida pública de curto prazo "
           "emitida ao desconto; não é um depósito bancário. Dividendos não são garantidos.",
           "Preencha o comparador com as taxas actuais que encontrar e compare o rendimento real de cada instrumento."),
    "D5": ("Manter-se informado e obter ajuda",
           "Informar-se é saber quem regula (CMC), onde se negoceia (BODIVA) e por que via se acede (sociedade correctora autorizada). "
           "Saber onde procurar ajuda fiável é parte da capacidade financeira; pedir informação não é fraqueza.",
           "Siga o percurso guiado do primeiro investimento e anote as dúvidas que precisa de esclarecer com a correctora."),
}

PASSOS_PRIMEIRO_INVESTIMENTO = [
    ("Reserva de emergência", "Antes de investir, tenha 3 a 6 meses de despesas essenciais em liquidez (mais se o rendimento for variável)."),
    ("Objectivo e prazo", "Defina para quê e para quando: um objectivo a 1 ano e um a 10 anos pedem instrumentos diferentes."),
    ("Quanto pode investir", "Use o orçamento para saber quanto sobra de forma regular, sem comprometer o essencial. A regra 50/30/20 é uma referência, não uma obrigação."),
    ("Perceber os instrumentos", "Compare depósito a prazo, Bilhetes do Tesouro, Obrigações do Tesouro e acções: liquidez, risco, prazo e rendimento real."),
    ("Escolher o intermediário", "Para negociar na BODIVA é necessária uma sociedade correctora autorizada pela CMC. Confirme a autorização junto da CMC e peça a tabela de comissões por escrito."),
    ("Custos e prazos", "Pergunte pelas comissões de corretagem, custódia e impostos, e pelo prazo de liquidação. Os custos percepcionados são uma das maiores barreiras na evidência da UKB."),
    ("Treinar sem risco", "Pratique no Home Broker virtual (dinheiro fictício) para perder o medo do procedimento."),
    ("Primeira operação pequena", "Comece com um montante que não afecte o essencial, registe a tese e reveja ao fim de um período definido."),
]


def nivel_capacidade(score):
    if score is None:
        return "—"
    if score < 40:
        return "Inicial"
    if score < 60:
        return "Em desenvolvimento"
    if score < 80:
        return "Sólida"
    return "Avançada"


def pontuar_diagnostico(respostas: dict) -> dict:
    """Pontua (0–100) cada célula domínio×componente, os totais por domínio e componente e o índice geral. Itens sem resposta não contam."""
    celulas_pts = {}
    for it in ITENS_CF:
        if it.get("meta"):
            continue
        r = respostas.get(it["id"])
        if r is None:
            continue
        pts = 100.0 if (it["tipo"] == "mc" and int(r) == it["correcta"]) else (0.0 if it["tipo"] == "mc" else (int(r) - 1) / 4 * 100)
        celulas_pts.setdefault((it["dom"], it["comp"]), []).append(pts)
    celulas = {k: sum(v) / len(v) for k, v in celulas_pts.items()}

    def media(vals):
        vals = [v for v in vals if v is not None]
        return sum(vals) / len(vals) if vals else None

    por_dom = {d: media([celulas.get((d, c)) for c in COMPONENTES_CF]) for d in DOMINIOS_CF}
    por_comp = {c: media([celulas.get((d, c)) for d in DOMINIOS_CF]) for c in COMPONENTES_CF}
    geral = media(list(por_comp.values()))
    lacuna = (por_comp["K"] - por_comp["B"]) if (por_comp["K"] is not None and por_comp["B"] is not None) else None
    auto_bt, k6 = respostas.get("a6"), respostas.get("k6")
    incompetencia = bool(auto_bt is not None and k6 is not None and int(auto_bt) >= 4 and int(k6) != _ITEM_CF["k6"]["correcta"])
    return {"celulas": celulas, "dominios": por_dom, "componentes": por_comp, "geral": geral, "lacuna_kb": lacuna,
            "incompetencia_bt": incompetencia, "nivel": nivel_capacidade(geral)}


def plano_de_accao(resultado: dict, maximo: int = 3) -> list:
    """Até `maximo` acções, para as células com pontuação mais baixa (< 70)."""
    fracas = sorted([(v, k) for k, v in resultado["celulas"].items() if v < 70])[:maximo]
    return [{"dominio": DOMINIOS_CF[d], "componente": COMPONENTES_CF[c], "pontos": v, "accao": ACOES_CF[(d, c)][0], "ferramenta": ACOES_CF[(d, c)][1]}
            for v, (d, c) in fracas]


def orcamento_variavel(rendimentos: list, essenciais: float) -> dict:
    """Rendimento prudente = média dos 3 meses mais baixos. «Ordenado» alisado = rendimento prudente; o excedente vai para um fundo de alisamento."""
    r = [float(x) for x in rendimentos if x is not None and float(x) > 0]
    if len(r) < 3:
        raise ValueError("Indique o rendimento de pelo menos 3 meses.")
    if essenciais < 0:
        raise ValueError("As despesas essenciais não podem ser negativas.")
    baixos = sorted(r)[:3]
    prudente = sum(baixos) / 3
    media = sum(r) / len(r)
    desvio = (sum((x - media) ** 2 for x in r) / len(r)) ** 0.5
    fundo, linhas, fundo_min = 0.0, [], 0.0
    for i, x in enumerate(r, start=1):
        fundo += x - prudente
        fundo_min = min(fundo_min, fundo)
        linhas.append({"Mês": i, "Rendimento": x, "«Ordenado» alisado": prudente, "Fundo de alisamento": fundo})
    return {"prudente": prudente, "media": media, "minimo": min(r), "maximo": max(r), "variabilidade": (desvio / media) if media else 0.0,
            "cobre_essencial": prudente >= essenciais, "essenciais_pct": (essenciais / prudente) if prudente else None,
            "folga": prudente - essenciais, "fundo_final": fundo, "fundo_min": fundo_min,
            "consumo_50": prudente * 0.5, "investimento_30": prudente * 0.3, "entesouramento_20": prudente * 0.2, "linhas": linhas}


def reserva_emergencia(despesas_essenciais: float, meses_alvo: float, inflacao_anual: float, meses_para_construir: int,
                       poupanca_actual: float = 0.0, taxa_anual: float = 0.0) -> dict:
    """Reserva-alvo a preços de hoje e a preços futuros (inflação), poupança mensal necessária e perda de poder de compra do dinheiro parado."""
    if despesas_essenciais <= 0 or meses_alvo <= 0:
        raise ValueError("Indique despesas essenciais e meses-alvo superiores a zero.")
    n = int(meses_para_construir)
    if n < 1:
        raise ValueError("O prazo para construir a reserva deve ser de pelo menos 1 mês.")
    alvo_hoje = despesas_essenciais * meses_alvo
    alvo_futuro = alvo_hoje * (1 + inflacao_anual) ** (n / 12)
    r_m = (1 + taxa_anual) ** (1 / 12) - 1
    fv_actual = poupanca_actual * (1 + r_m) ** n
    falta = max(0.0, alvo_futuro - fv_actual)
    contribuicao = (falta * r_m / ((1 + r_m) ** n - 1)) if r_m > 0 else falta / n
    return {"alvo_hoje": alvo_hoje, "alvo_futuro": alvo_futuro, "falta": falta, "contribuicao_mensal": contribuicao,
            "poder_compra_parado": poupanca_actual / (1 + inflacao_anual) ** (n / 12), "n": n}


def comparar_instrumentos(inflacao: float, imposto: float, taxas: dict) -> list:
    """Rendimento nominal → líquido de imposto → real (descontada a inflação). Valores ilustrativos escolhidos pelo utilizador."""
    out = []
    for nome, nominal in taxas.items():
        liquido = nominal * (1 - imposto)
        real = (1 + liquido) / (1 + inflacao) - 1
        out.append({"Instrumento": nome, "Nominal (% ao ano)": nominal * 100, "Líquido de imposto (%)": liquido * 100, "Real (%)": real * 100})
    return out


CARACTERISTICAS_INSTRUMENTOS = pd.DataFrame([
    {"Instrumento": "Depósito a prazo", "Liquidez": "Baixa a média (levantamento antecipado conforme o contrato)", "Risco": "Baixo: risco do banco",
     "Rendimento": "Taxa contratada para o prazo", "Prazo": "Definido no contrato", "Custos": "Confirme com o banco", "Acesso": "Balcão do banco"},
    {"Instrumento": "Bilhete do Tesouro (BT)", "Liquidez": "Média: mercado secundário com liquidez limitada", "Risco": "Soberano (Estado emissor). Não é um depósito bancário",
     "Rendimento": "Emitido ao desconto: ganho = valor nominal − preço pago", "Prazo": "91 a 364 dias", "Custos": "Comissões do intermediário", "Acesso": "Correctora ou banco autorizado"},
    {"Instrumento": "Obrigação do Tesouro (OT)", "Liquidez": "Média: mercado secundário com liquidez limitada", "Risco": "Soberano; o preço varia com as taxas de juro até ao vencimento",
     "Rendimento": "Cupões periódicos + devolução do capital", "Prazo": "2 anos ou mais", "Custos": "Comissões do intermediário", "Acesso": "Correctora ou banco autorizado"},
    {"Instrumento": "Acção cotada na BODIVA", "Liquidez": "Variável: mercado com liquidez limitada", "Risco": "Elevado: preço e dividendos variam",
     "Rendimento": "Dividendos (não garantidos) + variação do preço", "Prazo": "Sem prazo; horizonte longo", "Custos": "Comissões de corretagem", "Acesso": "Sociedade correctora autorizada pela CMC"},
])


# ---------------- Persistência (cada conta só vê os seus próprios resultados) ----------------
def guardar_diagnostico_cf(resultado: dict, respostas: dict):
    import json as _json
    if not st.session_state.get("autenticado"):
        return
    executar("INSERT INTO capacidade_diagnosticos (conta_email, versao, respostas, resultados) VALUES (%s, %s, %s, %s)",
             (utilizador_actual(), "1", _json.dumps(respostas), _json.dumps({"geral": resultado["geral"], "componentes": resultado["componentes"],
                                                                            "dominios": resultado["dominios"]}, default=float)))


def obter_diagnosticos_cf() -> pd.DataFrame:
    if not st.session_state.get("autenticado"):
        return pd.DataFrame()
    return consultar_df("SELECT id, criado_em, resultados FROM capacidade_diagnosticos WHERE conta_email = %s ORDER BY criado_em", (utilizador_actual(),))


def _ir_para(destino: str):
    st.session_state["nav_pagina"] = destino


# ---------------- Interface ----------------
def _mostrar_resultado_cf(res: dict):
    st.markdown("#### Resultado")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Índice geral", f"{res['geral']:.0f}/100" if res["geral"] is not None else "—", help=f"Nível: {res['nivel']}")
    for col, c in zip((c2, c3, c4), COMPONENTES_CF):
        v = res["componentes"][c]
        col.metric(COMPONENTES_CF[c], f"{v:.0f}/100" if v is not None else "—")
    st.caption(f"Nível global: **{res['nivel']}**. Cada componente é a média dos cinco domínios; o índice geral é a média dos três componentes.")
    linhas = {DOMINIOS_CF[d]: {COMPONENTES_CF[c]: res["celulas"].get((d, c)) for c in COMPONENTES_CF} for d in DOMINIOS_CF}
    df = pd.DataFrame(linhas).T
    fx_barras(df.fillna(0), height=300)
    st.dataframe(df.round(0).fillna("—"), use_container_width=True)
    if res["lacuna_kb"] is not None and res["lacuna_kb"] >= 15:
        st.info(f"O seu conhecimento ({res['componentes']['K']:.0f}) está acima do seu comportamento ({res['componentes']['B']:.0f}). "
                "É um padrão comum: saber não basta, é preciso transformar o conhecimento em hábitos e em passos práticos. O plano abaixo vai nessa direcção.")
    if res["incompetencia_bt"]:
        st.warning("Disse compreender bem os Bilhetes do Tesouro, mas a resposta sobre o que são não coincidiu. É frequente confundi-los com depósitos a prazo: "
                   "reveja a ficha «Comparador de instrumentos» na aba Ferramentas.")
    st.markdown("#### O seu plano de acção")
    plano = plano_de_accao(res)
    if not plano:
        st.success("Todas as áreas estão acima de 70/100. Mantenha os hábitos e avance para o percurso do primeiro investimento.")
    for i, p in enumerate(plano, start=1):
        with st.container(border=True):
            st.markdown(f"**{i}. {p['dominio']} · {p['componente']}** ({p['pontos']:.0f}/100)")
            st.write(p["accao"])
            st.caption(f"Ferramenta sugerida: {p['ferramenta']}")


def diagnostico_cf(prefixo: str, guardar: bool):
    st.markdown("Responda com sinceridade: não há respostas «más», só um ponto de partida. Demora cerca de 5 minutos.")
    with st.form(f"form_diag_{prefixo}"):
        respostas = {}
        for comp, titulo in (("K", "Parte 1 · Conhecimento"), ("A", "Parte 2 · Atitude e confiança"), ("B", "Parte 3 · Comportamento")):
            _its = [x for x in ITENS_CF if x["comp"] == comp]
            with st.expander(f"{titulo}  ·  {len(_its)} perguntas"):
                for it in _its:
                    escala = it.get("opcoes") or (ESCALA_FREQ if it["tipo"] == "freq" else ESCALA_CONC)
                    escolha = st.radio(it["texto"], escala, index=None, key=f"diag_{prefixo}_{it['id']}", horizontal=(it["tipo"] != "mc"))
                    respostas[it["id"]] = escala.index(escolha) if (escolha is not None and it["tipo"] == "mc") else (escala.index(escolha) + 1 if escolha is not None else None)
        enviar = st.form_submit_button("Ver o meu resultado", type="primary")
    if enviar:
        em_falta = [k for k, v in respostas.items() if v is None]
        if em_falta:
            st.error(f"Faltam {len(em_falta)} resposta(s). Responda a todas as perguntas para ver o resultado.")
        else:
            res = pontuar_diagnostico(respostas)
            st.session_state[f"diag_res_{prefixo}"] = res
            if guardar:
                try:
                    guardar_diagnostico_cf(res, respostas)
                    st.session_state[f"diag_gravado_{prefixo}"] = True
                except Exception:
                    st.session_state[f"diag_gravado_{prefixo}"] = False
    res = st.session_state.get(f"diag_res_{prefixo}")
    if res:
        _mostrar_resultado_cf(res)
        if guardar and st.session_state.get(f"diag_gravado_{prefixo}"):
            st.caption("Resultado guardado na sua conta. Repita o diagnóstico daqui a algumas semanas para medir a evolução.")
        elif not guardar:
            st.caption("Este resultado não fica guardado. Crie ou use uma conta para acompanhar a evolução ao longo do tempo.")


def ferramenta_orcamento_variavel(prefixo: str):
    st.markdown("**Orçamento com rendimento variável.** Indique o que recebeu nos últimos meses e as suas despesas essenciais mensais (renda de casa, alimentação, transporte, saúde, dívidas).")
    cols = st.columns(3)
    vals = []
    for i in range(6):
        vals.append(cols[i % 3].number_input(f"Mês {i + 1} (Kz)", min_value=0.0, step=5000.0, value=0.0, key=f"ov_{prefixo}_{i}"))
    ess = st.number_input("Despesas essenciais por mês (Kz)", min_value=0.0, step=5000.0, value=0.0, key=f"ov_ess_{prefixo}")
    if sum(1 for v in vals if v > 0) < 3:
        st.info("Preencha pelo menos 3 meses para ver o resultado.")
        return
    try:
        r = orcamento_variavel(vals, ess)
    except ValueError as e:
        st.warning(str(e))
        return
    m1, m2, m3 = st.columns(3)
    m1.metric("Rendimento prudente", kz(r["prudente"]), help="Média dos 3 meses mais baixos")
    m2.metric("Rendimento médio", kz(r["media"]))
    m3.metric("Variabilidade", f"{r['variabilidade'] * 100:.0f}%", help="Desvio-padrão em % da média")
    if r["cobre_essencial"]:
        st.success(f"O rendimento prudente cobre o essencial, com folga de {kz(r['folga'])} por mês.")
    else:
        st.warning(f"O rendimento prudente não cobre o essencial: faltam {kz(-r['folga'])} por mês. Reveja despesas ou procure estabilizar parte do rendimento.")
    if r["essenciais_pct"] is not None and r["essenciais_pct"] > 0.5:
        st.caption(f"Os essenciais pesam {r['essenciais_pct'] * 100:.0f}% do rendimento prudente, acima dos 50% que a regra 50/30/20 reserva ao consumo.")
    st.markdown("**Como distribuir o «ordenado» alisado (regra 50/30/20 sobre o rendimento prudente)**")
    a1, a2, a3 = st.columns(3)
    a1.metric("Consumo (50%)", kz(r["consumo_50"]))
    a2.metric("Investimento (30%)", kz(r["investimento_30"]))
    a3.metric("Entesouramento (20%)", kz(r["entesouramento_20"]))
    df = pd.DataFrame(r["linhas"]).set_index("Mês")
    fx_linhas(df[["Rendimento", "«Ordenado» alisado"]], height=240)
    st.caption(f"Fundo de alisamento ao fim de {len(df)} meses: {kz(r['fundo_final'])}. Os meses acima do rendimento prudente enchem o fundo; os abaixo, esvaziam-no.")


def ferramenta_reserva(prefixo: str):
    st.markdown("**Reserva de emergência ajustada à inflação.** A reserva-alvo cresce com a inflação até ao dia em que a terminar de a construir.")
    try:
        infl_def = float(obter_premissas_macro()["inflacao"]) * 100
    except Exception:
        infl_def = 13.5
    c1, c2 = st.columns(2)
    ess = c1.number_input("Despesas essenciais por mês (Kz)", min_value=0.0, step=5000.0, value=0.0, key=f"re_ess_{prefixo}")
    meses = c2.slider("Meses de cobertura", 1, 12, 6, key=f"re_meses_{prefixo}", help="3 meses para rendimento estável; 6 ou mais se for variável")
    c3, c4, c5 = st.columns(3)
    infl = c3.number_input("Inflação anual assumida (%)", min_value=0.0, max_value=100.0, value=round(infl_def, 1), step=0.5, key=f"re_infl_{prefixo}")
    prazo = c4.slider("Meses para construir", 1, 60, 12, key=f"re_prazo_{prefixo}")
    actual = c5.number_input("Já tenho guardado (Kz)", min_value=0.0, step=5000.0, value=0.0, key=f"re_act_{prefixo}")
    taxa = st.number_input("Rendimento anual do local onde a guarda (%, 0 se for dinheiro parado)", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key=f"re_tx_{prefixo}")
    if ess <= 0:
        st.info("Indique as despesas essenciais mensais.")
        return
    try:
        r = reserva_emergencia(ess, meses, infl / 100, prazo, actual, taxa / 100)
    except ValueError as e:
        st.warning(str(e))
        return
    m1, m2, m3 = st.columns(3)
    m1.metric("Reserva-alvo a preços de hoje", kz(r["alvo_hoje"]))
    m2.metric(f"Reserva-alvo daqui a {r['n']} meses", kz(r["alvo_futuro"]), help="Com a inflação assumida")
    m3.metric("Poupar por mês", kz(r["contribuicao_mensal"]))
    if actual > 0:
        st.caption(f"Se o que já tem ({kz(actual)}) ficar parado, daqui a {r['n']} meses terá o poder de compra de {kz(r['poder_compra_parado'])} de hoje.")
    if r["falta"] <= 0:
        st.success("Com o que já tem, e com o rendimento indicado, a reserva-alvo fica coberta no prazo.")


def ferramenta_comparador(prefixo: str):
    st.markdown("**Comparador de instrumentos.** Introduza taxas actuais que encontrar (os valores abaixo são apenas exemplos, não cotações). O que conta é o rendimento REAL.")
    st.caption("Confirme sempre as taxas, os impostos e as comissões aplicáveis junto da instituição.")
    c1, c2 = st.columns(2)
    infl = c1.number_input("Inflação anual (%)", min_value=0.0, max_value=100.0, value=13.5, step=0.5, key=f"cp_infl_{prefixo}")
    imp = c2.number_input("Imposto sobre o rendimento (%) — confirme a taxa aplicável", min_value=0.0, max_value=100.0, value=0.0, step=0.5, key=f"cp_imp_{prefixo}")
    d1, d2, d3, d4 = st.columns(4)
    dp = d1.number_input("Depósito a prazo (% ao ano)", min_value=0.0, value=10.0, step=0.5, key=f"cp_dp_{prefixo}")
    bt = d2.number_input("Bilhete do Tesouro (% ao ano)", min_value=0.0, value=14.0, step=0.5, key=f"cp_bt_{prefixo}")
    ot = d3.number_input("Obrigação do Tesouro (% ao ano)", min_value=0.0, value=17.0, step=0.5, key=f"cp_ot_{prefixo}")
    ac = d4.number_input("Acção: dividendo + crescimento esperado (% ao ano)", min_value=0.0, value=15.0, step=0.5, key=f"cp_ac_{prefixo}",
                         help="Hipótese do utilizador; dividendos e preços não são garantidos")
    linhas = comparar_instrumentos(infl / 100, imp / 100, {"Depósito a prazo": dp / 100, "Bilhete do Tesouro": bt / 100, "Obrigação do Tesouro": ot / 100, "Acção BODIVA": ac / 100})
    df = pd.DataFrame(linhas)
    fx_barras(df.set_index("Instrumento")[["Real (%)"]], height=240)
    st.dataframe(df.round(2), hide_index=True, use_container_width=True)
    pior = df.loc[df["Real (%)"] < 0, "Instrumento"].tolist()
    if pior:
        st.warning("Com estes pressupostos, o rendimento real é negativo em: " + ", ".join(pior) + ". O dinheiro perde poder de compra.")
    st.markdown("**Características qualitativas**")
    st.dataframe(CARACTERISTICAS_INSTRUMENTOS, hide_index=True, use_container_width=True)
    aviso_discreto("Uma acção tem risco de preço e os dividendos não são garantidos; o rendimento mostrado é uma hipótese, não uma previsão.")


def pagina_capacidade_financeira(autenticado: bool):
    pref = "app" if autenticado else "pub"
    st.markdown("### 🧠 Capacidade financeira prática")
    st.write("Capacidade financeira é mais do que saber: é conseguir aplicar o que se sabe, com confiança, nas decisões do dia-a-dia. "
             "Aqui mede o seu ponto de partida em 5 domínios e treina o que mais precisa.")
    nomes = ["🔎 Diagnóstico", "🏋️ Treino", "🧰 Ferramentas", "🚀 Primeiro investimento"] + (["📈 A minha evolução"] if autenticado else []) + ["📚 Fundamentos"]
    abas = st.tabs(nomes)
    with abas[0]:
        diagnostico_cf(pref, guardar=autenticado)
    with abas[1]:
        st.write("Cinco domínios, um exercício prático em cada. Comece pelo domínio com a pontuação mais baixa no diagnóstico.")
        for d, (titulo, ideia, exercicio) in LICOES_CF.items():
            with st.expander(f"{d[1]}. {titulo}"):
                st.write(ideia)
                st.markdown(f"**Exercício:** {exercicio}")
    with abas[2]:
        ferr = st.radio("Ferramenta", ["Orçamento com rendimento variável", "Reserva de emergência e inflação", "Comparador de instrumentos"],
                        horizontal=True, key=f"cf_ferr_{pref}")
        if ferr.startswith("Orçamento"):
            ferramenta_orcamento_variavel(pref)
        elif ferr.startswith("Reserva"):
            ferramenta_reserva(pref)
        else:
            ferramenta_comparador(pref)
        if autenticado:
            st.divider()
            b1, b2, b3 = st.columns(3)
            b1.button("Orçamento mensal 50/30/20", on_click=_ir_para, args=("🧮 Princípio 50/30/20",), key=f"go_r50_{pref}")
            b2.button("Simulador e Home Broker virtual", on_click=_ir_para, args=("🧪 Simulador de Investimento",), key=f"go_sim_{pref}")
            b3.button("Cotações da BODIVA", on_click=_ir_para, args=("📈 Cotações & Activos",), key=f"go_cot_{pref}")
    with abas[3]:
        st.write("Um percurso em 8 passos para o primeiro investimento. É educativo: não recomenda nenhum produto nem substitui o aconselhamento do intermediário.")
        for i, (titulo, texto) in enumerate(PASSOS_PRIMEIRO_INVESTIMENTO, start=1):
            with st.container(border=True):
                st.markdown(f"**{i}. {titulo}**")
                st.write(texto)
    if autenticado:
        with abas[4]:
            try:
                dfd = obter_diagnosticos_cf()
            except Exception:
                dfd = pd.DataFrame()
            if dfd.empty:
                st.info("Ainda não guardou nenhum diagnóstico. Faça o primeiro na aba Diagnóstico.")
            else:
                import json as _json
                linhas = []
                for _, r in dfd.iterrows():
                    res = _json.loads(r["resultados"]) if isinstance(r["resultados"], str) else r["resultados"]
                    linhas.append({"Data": pd.to_datetime(r["criado_em"]), "Geral": res.get("geral"),
                                   **{COMPONENTES_CF[c]: (res.get("componentes") or {}).get(c) for c in COMPONENTES_CF}})
                dv = pd.DataFrame(linhas).set_index("Data")
                fx_linhas(dv, height=280)
                if len(dv) >= 2 and dv["Geral"].iloc[0] is not None and dv["Geral"].iloc[-1] is not None:
                    st.metric("Evolução do índice geral", f"{dv['Geral'].iloc[-1]:.0f}/100", delta=f"{dv['Geral'].iloc[-1] - dv['Geral'].iloc[0]:+.0f} desde o primeiro diagnóstico")
                st.dataframe(dv.round(0), use_container_width=True)
    with abas[-1]:
        st.markdown("##### O modelo")
        st.write("Kempson, Collard e Moore (2005) propuseram a capacidade financeira como a combinação de três componentes (conhecimento, atitude e comportamento) "
                 "em cinco domínios da vida financeira. O diagnóstico desta página usa essa matriz.")
        matriz = pd.DataFrame({DOMINIOS_CF[d]: {COMPONENTES_CF[c]: ACOES_CF[(d, c)][0] for c in COMPONENTES_CF} for d in DOMINIOS_CF}).T
        st.dataframe(matriz, use_container_width=True)
        st.markdown("##### Porque se treina o comportamento, e não só o conhecimento")
        st.write("Em dois estudos na Faculdade de Economia da UKB (86 e 100 estudantes), o conhecimento teórico era sólido, mas só 9% identificou correctamente os Bilhetes do Tesouro, "
                 "a auto-confiança era mais baixa no «como fazer na prática» e as barreiras mais citadas foram os custos de corretagem e a falta de tempo. "
                 "Por isso o treino desta app insiste em procedimentos, comparação de custos e prática simulada.")
        st.markdown("##### Fontes")
        st.markdown(
            "- Kempson, E., Collard, S., & Moore, N. (2005). *Measuring financial capability: An exploratory study*. Financial Services Authority (Reino Unido).\n"
            "- Johnson, E., & Sherraden, M. S. (2007). From financial literacy to financial capability among youth. *Journal of Sociology & Social Welfare*, 34(3).\n"
            "- Kempson, E., Perotti, V., & Scott, K. (2013). *Measuring financial capability: A new instrument and results from low- and middle-income countries*. World Bank (Russia Financial Literacy and Education Trust Fund; 12 países).\n"
            "- OECD/INFE (2023). *OECD/INFE 2023 International Survey of Adult Financial Literacy* (39 países; conhecimento, comportamento e atitudes).\n"
            "- Money and Pensions Service (2020). *UK Strategy for Financial Wellbeing 2020–2030*; Money Advice Service (2015). *Financial Capability Strategy for the UK*.\n"
            "- Casaco (2023), Molossande (2026) e Costa (2026): estudos e síntese na FE-UKB sobre capacidade financeira e mercado de capitais angolano.")
        aviso_discreto("O diagnóstico é um instrumento educativo inspirado nestes modelos; não é uma escala psicometricamente validada nem substitui aconselhamento financeiro.")


# =========================================================
# PERFIL DE INVESTIDOR (SUITABILITY): perguntas → perfil de risco → portal recomendado
# Instrumento educativo de autoconhecimento: não é recomendação personalizada de compra ou venda.
# O portal (Iniciante / Investidor) resulta do diagnóstico, não de uma escolha livre.
# =========================================================
import json as _json_perfil
from datetime import timedelta

VERSAO_PERFIL = 1
DIAS_ENTRE_REPETICOES = 7
HORIZONTES = ["Menos de 1 ano", "1 a 3 anos", "3 a 5 anos", "Mais de 5 anos"]
MIN_CONHECIMENTO_INVESTIDOR = 4   # pontos em 7 (4 perguntas de conhecimento + experiência)
AVISO_PERFIL = ("Instrumento educativo de autoconhecimento: orienta o teu percurso na plataforma. "
                "Não é uma recomendação personalizada nem substitui a avaliação de adequação feita por uma entidade autorizada.")
TITULOS_SEC_PERFIL = {"A": "A · A tua situação financeira", "B": "B · O objectivo e o prazo", "C": "C · Como reages ao risco", "D": "D · O que já sabes"}
BENS_OPCOES = ["Casa ou terreno", "Viatura", "Negócio próprio", "Poupanças ou depósitos",
               "Investimentos financeiros (acções, BT, OT, fundos)", "Nenhum dos anteriores"]

QUESTOES_PERFIL = [
    {"id": "rend", "sec": "A", "t": "Como descreves a estabilidade do teu rendimento?",
     "op": [("Irregular ou sem rendimento próprio", 0), ("Variável, com meses fracos", 1), ("Estável, mas depende de uma única fonte", 2), ("Estável e com mais de uma fonte", 3)]},
    {"id": "reserva", "sec": "A", "t": "Sem rendimento, durante quantos meses conseguirias pagar as tuas despesas com dinheiro disponível (sem contar o que queres investir)?",
     "op": [("Menos de 1 mês", 0), ("1 a 3 meses", 1), ("3 a 6 meses", 2), ("Mais de 6 meses", 3)]},
    {"id": "dividas", "sec": "A", "t": "Que parte do teu rendimento mensal vai para prestações e dívidas?",
     "op": [("Mais de 50%", 0), ("Entre 30% e 50%", 1), ("Entre 10% e 30%", 2), ("Menos de 10% ou nenhuma", 3)]},
    {"id": "dependentes", "sec": "A", "t": "Quantas pessoas dependem do teu rendimento (além de ti)?",
     "op": [("5 ou mais", 0), ("3 ou 4", 1), ("1 ou 2", 2), ("Nenhuma", 3)]},
    {"id": "bens", "sec": "A", "t": "Que bens possuis? (escolhe todos os que se aplicam)", "multi": True},
    {"id": "peso", "sec": "A", "t": "O valor que pretendes investir representa que parte de tudo o que possuis, depois de descontar o que deves?",
     "op": [("Mais de 50%", 0), ("Entre 25% e 50%", 1), ("Entre 10% e 25%", 2), ("Menos de 10%", 3)]},
    {"id": "horizonte", "sec": "B", "t": "Quando vais precisar deste dinheiro?",
     "op": [("Em menos de 1 ano", 0), ("Daqui a 1 a 3 anos", 1), ("Daqui a 3 a 5 anos", 2), ("Só daqui a mais de 5 anos", 3)]},
    {"id": "liquidez", "sec": "B", "t": "Com que probabilidade poderás ter de levantar este dinheiro de repente (doença, desemprego, emergência)?",
     "op": [("É provável nos próximos meses", 0), ("Pode acontecer", 1), ("É improvável", 2), ("É praticamente impossível", 3)]},
    {"id": "queda", "sec": "C", "t": "Investiste 100 000 Kz e, um mês depois, valem 80 000 Kz. O que fazes?",
     "op": [("Vendo tudo para não perder mais", 0), ("Vendo uma parte", 1), ("Mantenho e espero", 2), ("Aproveito para comprar mais", 3)]},
    {"id": "resultado", "sec": "C", "t": "Qual destes resultados possíveis, num ano, preferes? (valores ilustrativos)",
     "op": [("Ganho pequeno e quase certo, sem perdas", 0), ("Entre −5% e +15%", 1), ("Entre −15% e +30%", 2), ("Entre −30% e +50%", 3)]},
    {"id": "perda", "sec": "C", "t": "Se perdesses o dinheiro que queres investir, o que aconteceria?",
     "op": [("Não conseguiria pagar despesas essenciais", 0), ("Teria de mudar planos importantes", 1), ("Ficaria desconfortável, mas conseguiria continuar", 2), ("Seria um contratempo pequeno", 3)]},
    {"id": "experiencia", "sec": "D", "t": "Que experiência tens com investimentos?",
     "op": [("Nenhuma", 0), ("Só depósitos a prazo, BT ou OT", 1), ("Já comprei acções ou fundos", 2), ("Invisto regularmente há mais de 2 anos", 3)]},
    {"id": "q_acao", "sec": "D", "t": "Uma acção representa:",
     "op": [("Um empréstimo feito à empresa", 0), ("Uma fracção da propriedade da empresa", 1), ("Um depósito garantido pelo Estado", 0)]},
    {"id": "q_bt", "sec": "D", "t": "Um Bilhete do Tesouro (BT) é:",
     "op": [("Um depósito a prazo garantido pelo Estado", 0), ("Dívida pública de curto prazo emitida pelo Estado", 1), ("Uma acção de uma empresa pública", 0)]},
    {"id": "q_div", "sec": "D", "t": "Diversificar uma carteira serve para:",
     "op": [("Reduzir o risco de depender de um único activo", 1), ("Garantir que nunca há perdas", 0), ("Aumentar o valor do dividendo", 0)]},
    {"id": "q_pe", "sec": "D", "t": "Se o P/E de uma empresa é 10x, isso significa que:",
     "op": [("A empresa paga 10% de dividendo", 0), ("A acção subiu 10% este ano", 0), ("O preço da acção é cerca de 10 vezes o lucro anual por acção", 1)]},
]
_QP = {q["id"]: q for q in QUESTOES_PERFIL}
_QUIZ = ["q_acao", "q_bt", "q_div", "q_pe"]

DESCRICAO_PERFIL = {
    "Conservador": "Dás prioridade a proteger o capital e a ter o dinheiro disponível. Os instrumentos de menor risco são o teu ponto de partida natural.",
    "Moderado": "Aceitas oscilações moderadas em troca de maior potencial de retorno, desde que o prazo seja suficiente para as absorver.",
    "Dinâmico": "Aceitas oscilações fortes e tens margem financeira e prazo para as suportar. Mesmo assim, o risco concentra-se: diversifica.",
}


def _pts_perfil(r: dict, qid: str) -> int:
    return dict(_QP[qid]["op"])[r[qid]]


def calcular_perfil(r: dict) -> dict:
    """Pontua as respostas. O perfil é o mais cauteloso entre capacidade, prazo e tolerância ('o elo mais fraco'); alguns sinais de alerta limitam o risco."""
    n_bens = len([b for b in r["bens"] if b != BENS_OPCOES[-1]])
    cap = sum(_pts_perfil(r, i) for i in ["rend", "reserva", "dividas", "dependentes", "peso"]) + min(3, n_bens)
    hor = _pts_perfil(r, "horizonte") + _pts_perfil(r, "liquidez")
    tol = sum(_pts_perfil(r, i) for i in ["queda", "resultado", "perda"])
    quiz = sum(_pts_perfil(r, i) for i in _QUIZ)
    conh = quiz + _pts_perfil(r, "experiencia")

    alertas, bloq_portal = [], False
    if _pts_perfil(r, "reserva") <= 1:
        alertas.append("A tua reserva de emergência cobre menos de 3 meses de despesas: antes de assumir risco de mercado, constrói esta reserva em dinheiro disponível ou depósitos.")
        bloq_portal = True
    if _pts_perfil(r, "horizonte") == 0:
        alertas.append("Vais precisar deste dinheiro em menos de 1 ano: não deve ficar exposto a activos cujo preço pode cair, como acções e fundos de acções.")
        bloq_portal = True
    if _pts_perfil(r, "perda") == 0:
        alertas.append("Perder este dinheiro comprometeria despesas essenciais: não é dinheiro para arriscar.")
        bloq_portal = True
    bloq_risco = bloq_portal
    if _pts_perfil(r, "dividas") == 0:
        alertas.append("Mais de metade do teu rendimento vai para dívidas: vale a pena avaliar primeiro a redução de dívidas caras, antes de assumir risco de mercado.")
        bloq_risco = True

    base = min(cap / 18.0, hor / 6.0, tol / 9.0)
    if bloq_risco or base < 0.34:
        perfil = "Conservador"
    elif base < 0.67:
        perfil = "Moderado"
    else:
        perfil = "Dinâmico"

    portal = "investidor" if (conh >= MIN_CONHECIMENTO_INVESTIDOR and not bloq_portal) else "iniciante"
    motivos = []
    if portal == "iniciante":
        if bloq_portal:
            motivos.append("há sinais de alerta na tua situação (ver acima): o primeiro passo é protegê-la")
        if conh < MIN_CONHECIMENTO_INVESTIDOR:
            motivos.append(f"o teu resultado de conhecimento e experiência foi {conh}/7 (o portal Investidor pede pelo menos {MIN_CONHECIMENTO_INVESTIDOR})")
    return {"perfil": perfil, "portal": portal, "bloq_risco": bloq_risco, "alertas": alertas, "motivos": motivos,
            "horizonte_idx": _pts_perfil(r, "horizonte"),
            "pontos": {"capacidade": cap, "prazo": hor, "tolerancia": tol, "conhecimento": conh},
            "maximos": {"capacidade": 18, "prazo": 6, "tolerancia": 9, "conhecimento": 7}}


# ---- Adequação por tipo de instrumento (regras gerais de prazo e perfil; sem produtos nem recomendações individuais) ----
_A, _C, _N = "Adequado", "Com cautela", "Não adequado"
_CLASSE_ADEQ = {_A: "A", _C: "C", _N: "N"}
_ACCOES = {0: (_N, _N, _N), 1: (_N, _N, _N), 2: (_N, _C, _C), 3: (_C, _A, _A)}   # por prazo: (Conservador, Moderado, Dinâmico)
_PERFIS_ORDEM = ["Conservador", "Moderado", "Dinâmico"]


def adequacao_instrumentos(h: int, perfil: str, bloq_risco: bool):
    h = max(0, min(3, int(h)))
    ip = _PERFIS_ORDEM.index(perfil) if perfil in _PERFIS_ORDEM else 0
    risco = _N if (bloq_risco or h <= 1) else _ACCOES[h][ip]
    if bloq_risco:
        pq_risco = "Há sinais de alerta na tua situação (reserva, prazo, dívidas ou capacidade de suportar perdas) que devem ser resolvidos antes de assumir este risco."
    elif h <= 1:
        pq_risco = "Os preços podem cair e demorar anos a recuperar: dinheiro com data marcada nos próximos 3 anos não deve ficar exposto."
    elif risco == _N:
        pq_risco = "Com este prazo e perfil, o risco de precisares de vender com perda é elevado."
    elif risco == _C:
        pq_risco = "Possível apenas com uma parte pequena e diversificada: o prazo ou o perfil ainda deixam pouca margem."
    else:
        pq_risco = "O prazo e o perfil permitem absorver oscilações, mas o risco continua: diversifica e respeita os limites da carteira."
    return [
        ("Liquidez e depósitos à ordem", _A, "Disponível quando precisares; é o lugar do dinheiro com data marcada e da reserva de emergência."),
        ("Depósitos a prazo", _C if h == 0 else _A, "Escolhe um prazo que termine antes da data em que precisas do dinheiro; levantar antes pode ter penalização."),
        ("Dívida pública (BT e OT)", _C if h == 0 else _A, "Escolhe vencimentos até à data em que precisas do dinheiro: vender antes do vencimento pode implicar perda."),
        ("Fundos de investimento com acções", risco, pq_risco + " A diversificação reduz, mas não elimina, o risco."),
        ("Acções cotadas na BODIVA", risco, pq_risco + " O mercado angolano tem pouca liquidez: pode ser difícil vender ao preço desejado."),
    ]


def _tabela_adequacao_html(linhas) -> str:
    corpo = "".join(f'<tr><td><b>{_esc(c)}</b></td><td><span class="appo-adeq appo-adeq-{_CLASSE_ADEQ[n]}">{_esc(n)}</span></td><td>{_esc(p)}</td></tr>' for c, n, p in linhas)
    return f'<table class="appo-adeq-tab"><thead><tr><th>Tipo de instrumento</th><th>Adequação</th><th>Porquê</th></tr></thead><tbody>{corpo}</tbody></table>'


# ---- Base de dados ----
def obter_ultimo_perfil(conta_id):
    if not conta_id:
        return None
    r = consultar_um("SELECT perfil, portal, pontuacoes, criado_em, NOW() FROM perfil_investidor WHERE conta_id = %s ORDER BY criado_em DESC, id DESC LIMIT 1", (int(conta_id),))
    if not r:
        return None
    try:
        res = _json_perfil.loads(r[2])
    except Exception:
        res = {}
    return {"perfil": r[0], "portal": r[1], "res": res, "criado_em": r[3], "agora": r[4]}


def guardar_perfil(conta_id: int, respostas: dict, res: dict):
    anterior = consultar_um("SELECT nivel FROM contas WHERE id = %s", (int(conta_id),))
    with transaccao() as cur:
        cur.execute("INSERT INTO perfil_investidor (conta_id, versao, respostas, pontuacoes, perfil, portal) VALUES (%s, %s, %s, %s, %s, %s)",
                    (int(conta_id), VERSAO_PERFIL, _json_perfil.dumps(respostas, ensure_ascii=False), _json_perfil.dumps(res, ensure_ascii=False), res["perfil"], res["portal"]))
        cur.execute("UPDATE contas SET nivel = %s WHERE id = %s", (res["portal"], int(conta_id)))
        registar_auditoria("perfil_calculado", "conta", conta_id, antes={"nivel": anterior[0] if anterior else None},
                           depois={"nivel": res["portal"], "perfil": res["perfil"]}, cur=cur)


def definir_nivel_conta(conta_id: int, nivel: str, motivo: str):
    exigir_admin()
    if nivel not in NIVEIS:
        raise ValueError("Nível inválido.")
    if not (motivo or "").strip():
        raise ValueError("Indica o motivo do ajuste.")
    anterior = consultar_um("SELECT nivel FROM contas WHERE id = %s", (int(conta_id),))
    with transaccao() as cur:
        cur.execute("UPDATE contas SET nivel = %s WHERE id = %s", (nivel, int(conta_id)))
        registar_auditoria("nivel_ajustado_admin", "conta", conta_id, antes={"nivel": anterior[0] if anterior else None}, depois={"nivel": nivel}, motivo=motivo.strip(), cur=cur)


def obter_perfis_resumo() -> pd.DataFrame:
    exigir_admin()
    return consultar_df("SELECT c.email AS email, c.nivel AS portal, p.perfil AS perfil, p.criado_em AS calculado_em FROM contas c "
                        "LEFT JOIN LATERAL (SELECT perfil, criado_em FROM perfil_investidor WHERE conta_id = c.id ORDER BY criado_em DESC, id DESC LIMIT 1) p ON TRUE "
                        "ORDER BY c.criado_em DESC")


def _carregar_perfil_sessao(conta_id):
    u = obter_ultimo_perfil(conta_id)
    st.session_state["perfil"] = u["perfil"] if u else None
    st.session_state["perfil_data"] = u["criado_em"] if u else None


def tem_perfil() -> bool:
    return bool(st.session_state.get("perfil"))


# ---- Interface ----
CSS_PERFIL = """
.appo-portal { border-radius: 12px; padding: 16px 18px; color: #FFFFFF; margin: 4px 0 10px 0; }
.appo-portal-ini { background: #0F766E; }
.appo-portal-inv { background: var(--appo-vinho, #7C1F3E); }
.appo-portal-pleno { background: #475569; }
.appo-portal-rot { font-size: 0.68rem; letter-spacing: 0.14em; text-transform: uppercase; opacity: 0.85; margin: 0; }
.appo-portal-nome { font-size: 1.45rem; font-weight: 800; line-height: 1.15; margin: 2px 0; }
.appo-portal-sub { font-size: 0.82rem; opacity: 0.92; margin: 0; }
.appo-perfil-topo { border: 1px solid var(--appo-borda, #E2E8F0); border-left: 6px solid var(--appo-vinho, #7C1F3E); background: #FFFFFF; border-radius: 12px; padding: 20px 24px; margin-bottom: 16px; }
.appo-perfil-rotulo { font-size: 0.72rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--appo-suave, #64748B); }
.appo-perfil-nome { font-size: 2rem; font-weight: 800; color: var(--appo-vinho, #7C1F3E); line-height: 1.15; }
.appo-perfil-topo p { margin: 6px 0 0 0; color: #334155; }
.appo-pcard { border-radius: 14px; padding: 22px 24px; border: 2px solid var(--appo-borda, #E2E8F0); background: #FFFFFF; min-height: 170px; }
.appo-pcard h3 { margin: 0 0 6px 0; font-size: 1.4rem; }
.appo-pcard p { margin: 0; color: #334155; }
.appo-pcard-ini.appo-pcard-rec { border-color: #0F766E; background: #F0FDFA; }
.appo-pcard-inv.appo-pcard-rec { border-color: var(--appo-vinho, #7C1F3E); background: #FDF2F5; }
.appo-pcard-off { opacity: 0.6; }
.appo-fita { display: inline-block; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em; color: #FFFFFF; padding: 3px 10px; border-radius: 999px; margin-bottom: 8px; }
.appo-pcard-ini .appo-fita { background: #0F766E; }
.appo-pcard-inv .appo-fita { background: var(--appo-vinho, #7C1F3E); }
.appo-adeq-tab { width: 100%; border-collapse: collapse; font-size: 0.92rem; }
.appo-adeq-tab th { text-align: left; padding: 8px 10px; color: var(--appo-suave, #64748B); border-bottom: 2px solid var(--appo-borda, #E2E8F0); font-weight: 600; }
.appo-adeq-tab td { padding: 10px; border-bottom: 1px solid var(--appo-borda, #E2E8F0); vertical-align: top; }
.appo-adeq { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 0.78rem; font-weight: 700; white-space: nowrap; }
.appo-adeq-A { background: #DCFCE7; color: #166534; }
.appo-adeq-C { background: #FEF3C7; color: #92400E; }
.appo-adeq-N { background: #FEE2E2; color: #991B1B; }
.appo-aviso { font-size: 0.58rem !important; line-height: 1.3; color: #A3AEBD; margin: 0.35rem 0 0 0; }
"""
st.markdown(f"<style>{CSS_PERFIL}</style>", unsafe_allow_html=True)


def _cartao_portal_lateral():
    """Cartão grande e colorido com o portal da conta. O portal resulta do perfil: não há seletor livre."""
    if eh_admin() or eh_participante():
        cls, nome = "appo-portal-pleno", "Acesso completo"
        sub = "Portal Investidor e área do Clube" if eh_participante() else "Administração"
    elif eh_investidor():
        cls, nome = "appo-portal-inv", "Portal Investidor"
        sub = f"Perfil {st.session_state.get('perfil')}" if tem_perfil() else "Perfil por fazer"
    else:
        cls, nome = "appo-portal-ini", "Portal Iniciante"
        sub = f"Perfil {st.session_state.get('perfil')}" if tem_perfil() else "Perfil por fazer"
    render_html(f'<div class="appo-portal {cls}"><div class="appo-portal-nome">{_esc(nome)}</div><p class="appo-portal-sub">{_esc(sub)}</p></div>')
    if not tem_perfil() and not (eh_admin() or eh_participante()):
        st.button("🧭 Fazer o meu perfil", on_click=_ir_para, args=("🧭 Perfil de Investidor",), key="lat_perfil", use_container_width=True, type="primary")


def _cartoes_portais(portal_rec: str):
    c1, c2 = st.columns(2)
    for col, chave, titulo, texto in [
        (c1, "ini", "Portal Iniciante", "Fundamentos, Biblioteca e diagnóstico de capacidade financeira. Constrói a base antes de assumir risco."),
        (c2, "inv", "Portal Investidor", "Cotações, avaliação de activos, simulador, conversor e Princípio 50/30/20."),
    ]:
        recomendado = (("ini" if portal_rec == "iniciante" else "inv") == chave)
        fita = '<span class="appo-fita">O TEU PORTAL</span><br>' if recomendado else ""
        extra = "" if recomendado else " appo-pcard-off"
        nota = "" if recomendado else '<p style="margin-top:8px;font-size:0.85rem;">Abre-se quando o teu perfil o permitir.</p>'
        col.markdown(f'<div class="appo-pcard appo-pcard-{chave}{" appo-pcard-rec" if recomendado else ""}{extra}">{fita}<h3>{_esc(titulo)}</h3><p>{_esc(texto)}</p>{nota}</div>', unsafe_allow_html=True)


def _mostrar_resultado_perfil(u: dict):
    res = u["res"] or {}
    perfil = u["perfil"]
    render_html(f'<div class="appo-perfil-topo"><span class="appo-perfil-rotulo">O teu perfil de risco</span>'
                f'<div class="appo-perfil-nome">{_esc(perfil)}</div><p>{_esc(DESCRICAO_PERFIL.get(perfil, ""))}</p></div>')
    _cartoes_portais(u["portal"])
    st.markdown("")
    pts, mx = res.get("pontos", {}), res.get("maximos", {})
    st.markdown("##### Como chegámos aqui")
    for chave, rotulo in [("capacidade", "Capacidade financeira para suportar perdas"), ("prazo", "Prazo e necessidade de liquidez"),
                          ("tolerancia", "Tolerância emocional ao risco"), ("conhecimento", "Conhecimento e experiência")]:
        if chave in pts and mx.get(chave):
            st.caption(f"{rotulo}: {pts[chave]}/{mx[chave]}")
            st.progress(min(1.0, max(0.0, pts[chave] / mx[chave])))
    st.caption("O perfil de risco segue a dimensão mais cautelosa entre capacidade, prazo e tolerância; o portal depende também do conhecimento e dos sinais de alerta.")
    for a in res.get("alertas", []):
        st.warning(a)
    if u["portal"] == "iniciante" and res.get("motivos"):
        st.info("Estás no portal Iniciante porque " + "; ".join(res["motivos"]) + ". Podes refazer o perfil passados " + f"{DIAS_ENTRE_REPETICOES} dias, depois de estudares a Biblioteca.")
    h = int(res.get("horizonte_idx", 0))
    st.markdown(f"##### Adequação por tipo de instrumento · prazo indicado: {HORIZONTES[max(0, min(3, h))]}")
    render_html(_tabela_adequacao_html(adequacao_instrumentos(h, perfil, bool(res.get("bloq_risco")))))
    try:
        st.caption(f"Perfil calculado em {u['criado_em']:%d/%m/%Y}.")
    except Exception:
        pass
    aviso_discreto(AVISO_PERFIL)


def _pode_refazer_perfil(u) -> bool:
    if eh_admin() or not u:
        return True
    try:
        return (u["agora"] - u["criado_em"]).days >= DIAS_ENTRE_REPETICOES
    except Exception:
        return True


def _formulario_perfil(conta_id: int):
    st.caption(f"{len(QUESTOES_PERFIL)} perguntas em {len(TITULOS_SEC_PERFIL)} secções, cerca de 3 minutos. Abre cada título para responder.")
    with st.form("form_perfil_investidor"):
        respostas = {}
        for sec in TITULOS_SEC_PERFIL:
            _qs = [q for q in QUESTOES_PERFIL if q["sec"] == sec]
            with st.expander(f"{TITULOS_SEC_PERFIL[sec]}  ·  {len(_qs)} perguntas"):
                for q in _qs:
                    if q.get("multi"):
                        respostas[q["id"]] = st.multiselect(q["t"], BENS_OPCOES, key=f"pf_{q['id']}")
                    else:
                        respostas[q["id"]] = st.radio(q["t"], [o[0] for o in q["op"]], index=None, key=f"pf_{q['id']}")
        enviar = st.form_submit_button("Calcular o meu perfil", type="primary")
    if not enviar:
        return
    em_falta = [q for q in QUESTOES_PERFIL if not respostas[q["id"]]]
    if em_falta:
        st.error(f"Faltam {len(em_falta)} resposta(s). Primeira por responder, na secção «{TITULOS_SEC_PERFIL[em_falta[0]['sec']]}»: «{em_falta[0]['t']}»")
        return
    if BENS_OPCOES[-1] in respostas["bens"] and len(respostas["bens"]) > 1:
        st.error("Em «Que bens possuis?», «Nenhum dos anteriores» não pode ser escolhido junto com outros bens.")
        return
    res = calcular_perfil(respostas)
    guardar_perfil(conta_id, respostas, res)
    st.session_state["nivel"] = res["portal"]
    _carregar_perfil_sessao(conta_id)
    st.success("Perfil calculado e guardado.")
    st.rerun()


def _verificador_objectivo(u):
    st.markdown("Diz para que é o dinheiro e quando vais precisar dele. O APPO mostra que tipos de instrumento fazem, ou não, sentido para esse prazo.")
    if not u:
        st.info("Faz primeiro o teu perfil, no separador «O meu perfil»: o verificador usa o teu perfil de risco.")
        return
    objectivos = ["Viagem ou férias", "Propinas ou educação", "Reserva de emergência", "Comprar casa ou terreno", "Comprar viatura",
                  "Casamento ou evento familiar", "Abrir ou reforçar um negócio", "Saúde ou imprevistos",
                  "Reforma ou futuro dos filhos", "Fazer crescer poupança a longo prazo", "Outro (especifica)"]
    c1, c2 = st.columns(2)
    objectivo = c1.selectbox("Objectivo do dinheiro", objectivos, key="ver_obj")
    if objectivo == "Outro (especifica)":
        _outro = c1.text_input("Qual é o objectivo?", key="ver_outro", max_chars=80)
        objectivo = (_outro or "").strip() or "Outro objectivo"
    horizonte = c2.selectbox("Quando vais precisar dele?", HORIZONTES, index=1, key="ver_hor")
    h = HORIZONTES.index(horizonte)
    bloq = bool((u["res"] or {}).get("bloq_risco"))
    if objectivo == "Reserva de emergência":
        h, bloq = 0, True
        st.caption("A reserva de emergência deve estar sempre disponível, qualquer que seja o prazo.")
    st.markdown(f"##### «{objectivo}» · {horizonte} · perfil {u['perfil']}")
    render_html(_tabela_adequacao_html(adequacao_instrumentos(h, u["perfil"], bloq)))
    aviso_discreto(AVISO_PERFIL)


def pagina_perfil_investidor():
    conta_id = st.session_state.get("conta_id")
    u = obter_ultimo_perfil(conta_id)
    aba_perfil, aba_ver = st.tabs(["🧭 O meu perfil", "🎯 Verificador de objectivo"])
    with aba_perfil:
        if u:
            _mostrar_resultado_perfil(u)
            st.divider()
            if _pode_refazer_perfil(u):
                with st.expander("Refazer o perfil"):
                    _formulario_perfil(conta_id)
            else:
                try:
                    quando = u["criado_em"] + timedelta(days=DIAS_ENTRE_REPETICOES)
                    st.info(f"Podes refazer o perfil a partir de {quando:%d/%m/%Y}.")
                except Exception:
                    st.info(f"Podes refazer o perfil passados {DIAS_ENTRE_REPETICOES} dias.")
        else:
            st.markdown("Responde com sinceridade: não há respostas certas, só respostas úteis. Demora cerca de 4 minutos e ajusta o teu portal ao teu momento.")
            _formulario_perfil(conta_id)
            aviso_discreto(AVISO_PERFIL)
    with aba_ver:
        _verificador_objectivo(u)



# =========================================================
# ÍNDICES: «Índice BODIVA» (cotação média) e «Índice APPO» (variação média desde 19/08/2026, base 100)
# =========================================================
DATA_BASE_APPO = pd.Timestamp("2026-08-19")


def _tk_norm(t) -> str:
    """Mesma regra de comparação dos tickers que o resto da app (sem os 'A' finais)."""
    return str(t or "").strip().upper().rstrip("A")


def obter_bases_indice_appo(com_fonte: bool = False):
    df = consultar_df("SELECT ticker, preco_base, fonte FROM base_indice_appo")
    if com_fonte:
        return df
    return {_tk_norm(r["ticker"]): float(r["preco_base"]) for _, r in df.iterrows()} if not df.empty else {}


def guardar_bases_indice_appo(df: pd.DataFrame):
    exigir_admin()
    n = 0
    for _, r in df.iterrows():
        tk = str(r.get("ticker") or "").strip().upper()
        pb = r.get("preco_base")
        if not tk:
            continue
        if pb is None or pd.isna(pb) or float(pb) <= 0:
            executar("DELETE FROM base_indice_appo WHERE ticker = %s", (tk,))
        else:
            executar("INSERT INTO base_indice_appo (ticker, preco_base, fonte) VALUES (%s, %s, %s) ON CONFLICT (ticker) DO UPDATE SET "
                     "preco_base = EXCLUDED.preco_base, fonte = EXCLUDED.fonte, actualizado_em = NOW()", (tk, float(pb), str(r.get("fonte") or "").strip()))
            n += 1
    registar_auditoria("bases_indice_appo", "indice", "APPO", depois={"precos_base": n})


def obter_painel_precos(tickers_norm: set) -> pd.DataFrame:
    """Preço diário (linhas = datas, colunas = títulos). Dias sem registo mantêm o último preço conhecido."""
    df = consultar_df("SELECT DISTINCT ON (dia, RTRIM(ticker, 'A')) dia, RTRIM(ticker, 'A') AS tk, preco FROM historico_cotacoes "
                      "ORDER BY dia, RTRIM(ticker, 'A'), LENGTH(ticker) DESC")
    if df.empty:
        return pd.DataFrame()
    df = df[df["tk"].isin(tickers_norm)].copy()
    if df.empty:
        return pd.DataFrame()
    df["dia"] = pd.to_datetime(df["dia"])
    df["preco"] = df["preco"].astype(float)
    return df.pivot_table(index="dia", columns="tk", values="preco", aggfunc="last").sort_index().ffill()


def calcular_indice_bodiva(painel: pd.DataFrame) -> pd.Series:
    """Cotação média (Kz) das acções cotadas em cada dia."""
    return painel.mean(axis=1, skipna=True).dropna()


def calcular_indice_appo(painel: pd.DataFrame, bases: dict, data_base=DATA_BASE_APPO):
    """Variação média (peso igual) de todas as acções face ao preço-base de 19/08/2026, base 100.
    Quando entra uma acção nova, encadeia-se a série, para a entrada não causar um salto artificial."""
    pb = painel[painel.index >= data_base]
    if pb.empty:
        return None, {}
    rel, sem_base = {}, []
    for tk in pb.columns:
        s_tk = pb[tk].dropna()
        if s_tk.empty:
            continue
        base = bases.get(tk)
        if not base or base <= 0:
            base = float(s_tk.iloc[0])
            sem_base.append(tk)
        rel[tk] = pb[tk] / base
    R = pd.DataFrame(rel).dropna(how="all")
    if R.empty:
        return None, {}
    valores = {R.index[0]: 100.0 * float(R.iloc[0].mean())}
    for i in range(1, len(R)):
        ant, act = R.iloc[i - 1], R.iloc[i]
        conj = [c for c in R.columns if pd.notna(ant[c]) and pd.notna(act[c])]
        m_ant = float(ant[conj].mean()) if conj else 0.0
        razao = (float(act[conj].mean()) / m_ant) if m_ant else 1.0
        valores[R.index[i]] = valores[R.index[i - 1]] * razao
    return pd.Series(valores).sort_index(), {"sem_base": sem_base, "inicio": R.index[0]}


def janela_periodo(serie: pd.Series, periodo: str):
    """(janela, variação %, janela completa?) para 1d, 7d, 1m, 3m, 6m, 1a, 5a."""
    if len(serie) < 2:
        return serie, None, False
    fim = serie.index[-1]
    if periodo == "1d":
        janela, completa = serie.iloc[-2:], True
    else:
        ini = fim - pd.Timedelta(days=_PERIODO_DIAS[periodo])
        antes = serie[serie.index <= ini]
        completa = len(antes) > 0
        janela = serie[serie.index >= antes.index[-1]] if completa else serie
    base = float(janela.iloc[0])
    return janela, ((float(serie.iloc[-1]) / base - 1) * 100 if base else None), completa


def resumo_indice_appo(df_activos: pd.DataFrame):
    """(valor, variação 1d %) do Índice APPO, ou None se ainda não há dados suficientes."""
    try:
        acoes = df_activos[df_activos["tipo"].apply(_eh_accao)] if not df_activos.empty else df_activos
        tickers = {_tk_norm(t) for t in acoes["ticker"] if str(t or "").strip()} if not acoes.empty else set()
        painel = obter_painel_precos(tickers) if tickers else pd.DataFrame()
        if painel.empty:
            return None
        serie, _ = calcular_indice_appo(painel, obter_bases_indice_appo())
        if serie is None or len(serie) < 2:
            return None
        _, var1d, _ = janela_periodo(serie, "1d")
        return float(serie.iloc[-1]), var1d
    except Exception:
        traceback.print_exc()
        return None


def _painel_indices(df_activos: pd.DataFrame):
    acoes = df_activos[df_activos["tipo"].apply(_eh_accao)] if not df_activos.empty else df_activos
    nomes = {_tk_norm(r["ticker"]): str(r["nome"]) for _, r in acoes.iterrows() if str(r["ticker"] or "").strip()} if not acoes.empty else {}
    if not nomes:
        st.info("Ainda não há acções registadas.")
        return
    painel = obter_painel_precos(set(nomes))
    if painel.empty or len(painel) < 2:
        st.info("Ainda não há histórico de cotações suficiente. O administrador pode importar a série de cada título em Cotações & Activos.")
        return
    periodo = st.radio("Período", PERIODOS_GRAFICO, index=PERIODOS_GRAFICO.index("1m"), horizontal=True, key="per_indices", label_visibility="collapsed")
    aba_appo, aba_bodiva = st.tabs(["Índice APPO", "Índice BODIVA"])
    with aba_appo:
        serie, info = calcular_indice_appo(painel, obter_bases_indice_appo())
        if serie is None or len(serie) < 2:
            st.info("O Índice APPO começa em 19/08/2026: ainda não há cotações desde essa data.")
        else:
            janela, var, completa = janela_periodo(serie, periodo)
            c1, c2 = st.columns(2)
            c1.metric("Índice APPO (100 = 19/08/2026)", f"{serie.iloc[-1]:.2f}", delta=(f"{var:+.2f}% em {periodo}" if var is not None else None))
            c2.metric("Desde 19/08/2026", f"{serie.iloc[-1] - 100:+.2f}%")
            grafico_area_simples(janela.to_frame("Índice APPO"), "Índice APPO")
            st.caption("Variação média de todas as acções cotadas face ao seu preço em 19/08/2026, o dia em que o Clube começou a investir (todas com o mesmo peso).")
            if not completa:
                st.caption(f"Histórico disponível só desde {serie.index[0]:%d/%m/%Y}; o período escolhido é mais longo.")
            if info.get("sem_base"):
                lista = ", ".join(nomes.get(t, t) for t in info["sem_base"])
                st.caption(f"Sem preço-base de 19/08/2026 para: {lista}. Para estas usa-se o primeiro preço disponível; o administrador pode completar em Cotações & Activos.")
    with aba_bodiva:
        serie_b = calcular_indice_bodiva(painel)
        janela_b, var_b, completa_b = janela_periodo(serie_b, periodo)
        st.metric("Índice BODIVA (cotação média)", kz(serie_b.iloc[-1]), delta=(f"{var_b:+.2f}% em {periodo}" if var_b is not None else None))
        grafico_area_simples(janela_b.to_frame("Cotação média (Kz)"), "Cotação média (Kz)")
        st.caption(f"Média simples das cotações das {painel.shape[1]} acções cotadas em cada dia. Muda também quando entra uma nova acção; para medir a variação, usa o Índice APPO.")
        if not completa_b:
            st.caption(f"Histórico disponível só desde {serie_b.index[0]:%d/%m/%Y}; o período escolhido é mais longo.")


# =========================================================
# MOTOR ANALÍTICO MULTITEMPORAL
# Rentabilidade (1D · 7D · 3M · 6M · 1A · 5A/acumulado) da carteira e dos índices APPO e BODIVA,
# Alpha, ajuste à inflação de Angola (homóloga, vigente, projectada) e métricas de risco.
# =========================================================
HORIZ_RENT = [("1d", "Intradia (1D)"), ("7d", "Semanal (7D)"), ("3m", "Trimestral (3M)"),
              ("6m", "Semestral (6M)"), ("1a", "Anual (YoY)"), ("5a", "Longo prazo (5A)")]


def serie_valor_encadeada(painel: pd.DataFrame, qtds: dict) -> pd.Series:
    """Série base 100 do valor de um cabaz (quantidade x preço). Quando um título entra no cabaz, a série é
    encadeada sobre os títulos comuns, para a entrada não criar um salto artificial."""
    cols = [c for c in painel.columns if qtds.get(c, 0) and qtds[c] > 0]
    if not cols:
        return pd.Series(dtype=float)
    V = painel[cols].mul(pd.Series({c: float(qtds[c]) for c in cols}), axis=1)
    valores, anterior, ultimo = {}, None, 100.0
    for dia, linha in V.iterrows():
        if linha.notna().sum() == 0:
            continue
        if anterior is None:
            valores[dia], ultimo = 100.0, 100.0
        else:
            comuns = linha.notna() & anterior.notna()
            den = float(anterior[comuns].sum()) if comuns.any() else 0.0
            razao = float(linha[comuns].sum()) / den if den > 0 else 1.0
            ultimo = ultimo * razao
            valores[dia] = ultimo
        anterior = linha
    return pd.Series(valores).sort_index()


def _ret_pct(serie, periodo: str, inicio_comum=None):
    """Variação % no horizonte. None se a janela não está completa (excepto 5A em modo acumulado)."""
    if serie is None or len(serie) < 2:
        return None
    if periodo == "5a" and inicio_comum is not None:
        s = serie[serie.index >= inicio_comum]
        if len(s) < 2 or not float(s.iloc[0]):
            return None
        return (float(s.iloc[-1]) / float(s.iloc[0]) - 1) * 100
    _, var, completa = janela_periodo(serie, periodo)
    return var if completa else None


def _dias_horizonte(serie_ref, periodo: str, inicio_comum=None) -> float:
    if periodo == "1d":
        if serie_ref is not None and len(serie_ref) >= 2:
            return float(max((serie_ref.index[-1] - serie_ref.index[-2]).days, 1))
        return 1.0
    if periodo == "5a" and inicio_comum is not None and serie_ref is not None and len(serie_ref):
        s = serie_ref[serie_ref.index >= inicio_comum]
        if len(s) >= 2:
            return float(max((s.index[-1] - s.index[0]).days, 1))
    return float(_PERIODO_DIAS[periodo])


def inflacao_no_periodo(dias: float, yoy: float, vig_m: float, proj: float) -> dict:
    """Inflação acumulada (%) em `dias`, a partir da taxa homóloga, da variação mensal vigente e da projectada."""
    return {"yoy": ((1 + yoy) ** (dias / 365.0) - 1) * 100,
            "vig": ((1 + vig_m) ** (dias / 30.4375) - 1) * 100,
            "proj": ((1 + proj) ** (dias / 365.0) - 1) * 100,
            "dias": dias}


def retorno_real(nominal, inflacao_pct):
    if nominal is None or inflacao_pct is None:
        return None
    return ((1 + nominal / 100.0) / (1 + inflacao_pct / 100.0) - 1) * 100


def metricas_risco(serie, ref=None, rf_anual=None) -> dict:
    """σ diário/anualizado, drawdown, VaR 95%, e (face a `ref`) tracking error, information ratio e beta."""
    import numpy as np
    if serie is None or len(serie) < 3:
        return {"n": 0}
    s = serie.dropna()
    r = s.pct_change().dropna()
    n = len(r)
    out = {"n": n}
    if n >= 2:
        out["sigma_d"] = float(r.std(ddof=1)) * 100
        out["sigma_a"] = out["sigma_d"] * (252 ** 0.5)
    out["dd_max"] = float((s / s.cummax() - 1).min()) * 100
    if n >= 20:
        out["var95"] = float(np.percentile(r, 5)) * 100
    if ref is not None and len(ref) >= 3:
        rr = ref.dropna().pct_change().dropna()
        j = pd.concat([r.rename("a"), rr.rename("b")], axis=1, join="inner").dropna()
        if len(j) >= 5:
            dif = j["a"] - j["b"]
            sd = float(dif.std(ddof=1))
            if sd > 0:
                out["te"] = sd * (252 ** 0.5) * 100
                out["ir"] = float(dif.mean()) * 252 / (sd * (252 ** 0.5))
            vb = float(j["b"].var(ddof=1))
            if vb > 0:
                out["beta"] = float(j["a"].cov(j["b"])) / vb
    if rf_anual is not None and n >= 30 and out.get("sigma_a"):
        out["sharpe"] = (float(r.mean()) * 252 - rf_anual) / (out["sigma_a"] / 100)
    return out


def calcular_analise_multitemporal(painel, carteira, tk_accoes, premissas, df_activos=None, bases=None) -> dict:
    """Devolve um dicionário com tudo o que a página e o PDF precisam. `ok` False + `motivo` quando não há dados."""
    import numpy as np
    res = {"ok": False, "motivo": "", "avisos": []}
    if painel is None or painel.empty or len(painel) < 2:
        res["motivo"] = "Ainda não há histórico de cotações suficiente (são precisos pelo menos 2 dias)."
        return res
    if carteira is None or carteira.empty:
        res["motivo"] = "A carteira real do Clube está vazia (Painel do Administrador › Carteira Real)."
        return res
    precos_activos = {}
    if df_activos is not None and not df_activos.empty:
        precos_activos = {_tk_norm(r["ticker"]): _num_seguro(r["preco"]) for _, r in df_activos.iterrows() if str(r["ticker"] or "").strip()}
    posicoes, qtds = [], {}
    for _, p in carteira.iterrows():
        tk, qtd = _tk_norm(p["ticker"]), _num_seguro(p["qtd"])
        if not tk or qtd <= 0:
            continue
        s_tk = painel[tk].dropna() if tk in painel.columns else pd.Series(dtype=float)
        preco = precos_activos.get(tk) or (float(s_tk.iloc[-1]) if len(s_tk) else 0.0)
        valor, custo = qtd * preco, _num_seguro(p["valor_aquisicao"])
        if tk in painel.columns and len(s_tk) >= 2:
            qtds[tk] = qtds.get(tk, 0) + qtd
        else:
            res["avisos"].append(f"{p['nome']}: sem histórico de cotações; fica fora das séries de rentabilidade e risco.")
        posicoes.append({"tk": tk, "ticker": str(p["ticker"] or "").strip().upper(), "nome": str(p["nome"]), "qtd": qtd, "preco_act": preco,
                         "valor": valor, "custo": custo, "mais_valia": valor - custo,
                         "mais_valia_pct": ((valor / custo - 1) * 100) if custo else None, "tem_serie": tk in qtds})
    total = sum(x["valor"] for x in posicoes)
    if not posicoes or total <= 0:
        res["motivo"] = "Não foi possível valorizar a carteira (faltam quantidades ou cotações)."
        return res
    for x in posicoes:
        x["peso"] = x["valor"] / total
    s_cart = serie_valor_encadeada(painel, qtds)
    if len(s_cart) < 2:
        res["motivo"] = "Os títulos em carteira ainda não têm histórico suficiente."
        return res
    painel_acc = painel[[c for c in painel.columns if c in tk_accoes]]
    s_appo = None
    if not painel_acc.empty:
        s_appo, _ = calcular_indice_appo(painel_acc, bases or {})
    s_bod = serie_valor_encadeada(painel_acc, {c: 1.0 for c in painel_acc.columns}) if not painel_acc.empty else pd.Series(dtype=float)
    base_series = [s for s in (s_cart, s_appo, s_bod) if s is not None and len(s) >= 2]
    usar_acum = not all(janela_periodo(s, "5a")[2] for s in base_series)
    inicio_comum = max(s.index[0] for s in base_series) if usar_acum else None

    ps = [p for p, _ in HORIZ_RENT]
    linha = lambda s: {p: _ret_pct(s, p, inicio_comum) for p in ps}
    ret_c, ret_a, ret_b = linha(s_cart), linha(s_appo), linha(s_bod)
    dif = lambda x, y: {p: (x[p] - y[p]) if x[p] is not None and y[p] is not None else None for p in ps}

    yoy, vig, proj = premissas["inflacao_homologa"], premissas["inflacao_vigente_m"], premissas["inflacao_projectada"]
    infl = {p: inflacao_no_periodo(_dias_horizonte(s_cart, p, inicio_comum), yoy, vig, proj) for p in ps}
    real = {p: ({k: retorno_real(ret_c[p], infl[p][k]) for k in ("yoy", "vig", "proj")} if ret_c[p] is not None else None) for p in ps}

    for x in posicoes:
        if x["tem_serie"]:
            s_t = painel[x["tk"]].dropna()
            x["ret"] = {p: _ret_pct(s_t, p, inicio_comum) for p in ps}
            rk = metricas_risco(s_t)
            x["sigma_a"], x["dd_max"] = rk.get("sigma_a"), rk.get("dd_max")
        else:
            x["ret"], x["sigma_a"], x["dd_max"] = {p: None for p in ps}, None, None
        x["contrib"] = None
    com_serie = [x for x in posicoes if x["tem_serie"]]
    try:
        R = painel[[x["tk"] for x in com_serie]].pct_change().dropna(how="any")
        if len(com_serie) >= 1 and len(R) >= 10:
            w = np.array([x["valor"] for x in com_serie], dtype=float)
            w = w / w.sum()
            cov = R.cov().values
            var_p = float(w @ cov @ w)
            if var_p > 0:
                mc = w * (cov @ w) / var_p
                for x, c in zip(com_serie, mc):
                    x["contrib"] = float(c)
    except Exception:
        pass
    posicoes.sort(key=lambda x: -x["valor"])
    hhi = sum(x["peso"] ** 2 for x in posicoes)
    rf = premissas.get("taxa_livre_risco")
    res.update({
        "ok": True, "ret_carteira": ret_c, "ret_appo": ret_a, "ret_bodiva": ret_b,
        "alpha_appo": dif(ret_c, ret_a), "alpha_bodiva": dif(ret_c, ret_b),
        "inflacao": infl, "real": real, "acumulado": usar_acum, "inicio_comum": inicio_comum,
        "titulos": posicoes, "premissas": premissas, "valor_total": total, "custo_total": sum(x["custo"] for x in posicoes),
        "concentracao": {"hhi": hhi, "n_efectivo": (1 / hhi) if hhi else 0.0, "maior": (posicoes[0]["nome"], posicoes[0]["peso"])},
        "risco": {"carteira": metricas_risco(s_cart, s_appo if s_appo is not None and len(s_appo) >= 3 else None, rf),
                  "appo": metricas_risco(s_appo) if s_appo is not None else {},
                  "bodiva": metricas_risco(s_bod)},
        "datas": {"ini": s_cart.index[0], "fim": s_cart.index[-1], "n_obs": len(s_cart)},
        "serie_carteira": s_cart, "serie_appo": s_appo, "serie_bodiva": s_bod,
    })
    # beta face ao Índice BODIVA (a métrica de risco da carteira só calculou TE/IR face ao APPO)
    rb = metricas_risco(s_cart, s_bod if len(s_bod) >= 3 else None)
    if "beta" in rb:
        res["risco"]["carteira"]["beta"] = rb["beta"]
    if len(s_cart) < 20:
        res["avisos"].append(f"Apenas {len(s_cart)} dias de histórico: as métricas de risco são indicativas. Importa o histórico de cotações (Painel do Administrador › Cotações & Activos) para as tornar robustas.")
    return res


def calcular_analise_completa(df_activos: pd.DataFrame) -> dict:
    """Lê cotações, carteira real e premissas na BD e corre o motor."""
    carteira = obter_carteira_real()
    prem = obter_premissas_macro()
    acoes = df_activos[df_activos["tipo"].apply(_eh_accao)] if not df_activos.empty else df_activos
    tk_acc = {_tk_norm(x) for x in acoes["ticker"] if str(x or "").strip()} if not acoes.empty else set()
    tk_cart = {_tk_norm(x) for x in carteira["ticker"] if str(x or "").strip()} if not carteira.empty else set()
    painel = obter_painel_precos(tk_acc | tk_cart) if (tk_acc | tk_cart) else pd.DataFrame()
    return calcular_analise_multitemporal(painel, carteira, tk_acc, prem, df_activos, obter_bases_indice_appo())


@st.cache_data(ttl=120, show_spinner=False)
def _analise_cacheada():
    return calcular_analise_completa(obter_activos())


def obter_analise() -> dict:
    exigir_participante()
    try:
        return _analise_cacheada()
    except Exception as e:
        traceback.print_exc()
        return {"ok": False, "motivo": f"Erro no cálculo analítico: {type(e).__name__}: {e}", "avisos": []}


def _melhor_horizonte(a: dict):
    for p, _ in reversed(HORIZ_RENT):
        if a["ret_carteira"].get(p) is not None:
            return p
    return None


def gerar_comentario_executivo(a: dict, resumo: dict, mercado=None) -> list:
    """Comentário macro e teses de investimento, gerados por regras a partir dos dados (lista de (título, texto))."""
    out = []
    pr = a["premissas"]
    # 1) Mercado
    txt = ""
    if mercado is not None and not mercado.empty and "variacao" in mercado.columns:
        v = pd.to_numeric(mercado["variacao"], errors="coerce").dropna()
        if len(v):
            sobem, descem = int((v > 0).sum()), int((v < 0).sum())
            m = mercado.assign(_v=pd.to_numeric(mercado["variacao"], errors="coerce")).dropna(subset=["_v"])
            top, bot = m.loc[m["_v"].idxmax()], m.loc[m["_v"].idxmin()]
            txt = (f"A BODIVA tem {len(mercado)} titulos cotados na tabela de mercado; na ultima sessao registada {sobem} subiram, {descem} desceram "
                   f"e {len(v) - sobem - descem} ficaram estaveis. Maior subida: {top['ticker']} ({top['_v']:+.2f}%); maior queda: {bot['ticker']} ({bot['_v']:+.2f}%). ")
    if a["serie_appo"] is not None and len(a["serie_appo"]) >= 2:
        txt += f"O Indice APPO esta em {float(a['serie_appo'].iloc[-1]):.2f} pontos (base 100 em 19/08/2026)."
    out.append(("Panorama do mercado (BODIVA)", txt or "Sem dados de mercado suficientes para um panorama; a leitura baseia-se nos titulos acompanhados pelo Clube."))
    # 2) Desempenho e alpha
    p = _melhor_horizonte(a)
    if p:
        rc, ra, rb = a["ret_carteira"][p], a["ret_appo"].get(p), a["ret_bodiva"].get(p)
        rot_h = (f"acumulado desde {a['inicio_comum']:%d/%m/%Y}" if (p == "5a" and a.get("acumulado") and a.get("inicio_comum") is not None)
                 else _rotulo_horiz(a, p, curto=False))
        t2 = f"No horizonte {rot_h}, a carteira do Clube rendeu {rc:+.2f}%"
        if ra is not None and rb is not None:
            al_a, al_b = rc - ra, rc - rb
            t2 += (f", contra {ra:+.2f}% do Indice APPO e {rb:+.2f}% do Indice BODIVA: alpha de {al_a:+.2f} p.p. face ao APPO e {al_b:+.2f} p.p. face a BODIVA. "
                   + ("A carteira supera ambos os indices." if al_a > 0 and al_b > 0 else
                      "A carteira fica abaixo de ambos os indices." if al_a < 0 and al_b < 0 else "O resultado e misto face aos dois indices."))
        else:
            t2 += ". Os indices de referencia ainda nao tem historico comparavel neste horizonte."
        out.append(("Desempenho e Alpha", t2))
        # 3) Inflação
        rr = a["real"].get(p)
        if rr:
            t3 = (f"Com a inflacao homologa de {pr['inflacao_homologa'] * 100:.2f}%, a rentabilidade real no mesmo horizonte e {rr['yoy']:+.2f}% "
                  f"({'ganho' if rr['yoy'] > 0 else 'perda'} de poder de compra). Deflacionada pela inflacao vigente ({pr['inflacao_vigente_m'] * 100:.2f}% m/m) e de {rr['vig']:+.2f}%, "
                  f"e pela projectada ({pr['inflacao_projectada'] * 100:.2f}% a 12 meses) de {rr['proj']:+.2f}%. "
                  f"Para preservar o capital nos proximos 12 meses a carteira precisa de render pelo menos {pr['inflacao_projectada'] * 100:.1f}% nominais.")
            out.append(("Ajuste a inflacao e poder de compra", t3))
    # 4) Risco
    rk, cc = a["risco"]["carteira"], a["concentracao"]
    t4 = f"A maior posicao e {cc['maior'][0]} com {cc['maior'][1] * 100:.1f}% da carteira; o numero efectivo de activos e {cc['n_efectivo']:.1f}. "
    if rk.get("sigma_a") is not None:
        t4 += f"A volatilidade anualizada estimada e {rk['sigma_a']:.1f}% e o drawdown maximo observado {rk['dd_max']:.1f}%."
    else:
        t4 += "Ainda nao ha observacoes suficientes para estimar a volatilidade."
    out.append(("Risco e concentracao", t4))
    # 5) Teses
    teses = []
    rr = a["real"].get(p) if p else None
    if rr and rr["proj"] < 0:
        teses.append("Tese 1 - Preservacao de capital: o retorno actual nao cobre a inflacao projectada; favorecer titulos com rendimento esperado "
                     f"acima de {pr['inflacao_projectada'] * 100:.1f}% e rever posicoes de baixa liquidez ou sem dividendo.")
    else:
        teses.append("Tese 1 - Preservacao de capital: o retorno actual cobre a inflacao projectada; manter a disciplina e testar a carteira com um cenario de inflacao 5 p.p. mais alta.")
    if cc["maior"][1] > 0.40:
        teses.append(f"Tese 2 - Diversificacao: {cc['maior'][0]} pesa mais de 40% da carteira; avaliar reforcos noutros sectores respeitando os limites do Clube (10% por activo, 20% por sector no fundo global).")
    else:
        teses.append("Tese 2 - Diversificacao: a concentracao esta em nivel aceitavel; manter a monitorizacao dos limites do Clube (10% por activo, 20% por sector no fundo global).")
    pior = [t_ for t_ in a["titulos"] if p and t_["ret"].get(p) is not None]
    if pior:
        pi = min(pior, key=lambda t_: t_["ret"][p])
        teses.append(f"Tese 3 - Revisao de posicoes: {_pdf_nome_curto(pi['nome'])} e o pior contributo no horizonte ({pi['ret'][p]:+.2f}%); confirmar se a tese registada continua valida (Principio 9).")
    out.append(("Teses de investimento e posicionamento tatico da APPO", "\n".join(teses)))
    return out


# =========================================================
# MERCADO BODIVA — TODOS OS TÍTULOS COTADOS (automático de minuto a minuto + resgate manual do administrador)
# =========================================================
def _nk(k) -> str:
    import unicodedata
    n = "".join(c for c in unicodedata.normalize("NFKD", str(k)) if not unicodedata.combining(c))
    return "".join(c for c in n.lower() if c.isalnum())


_MK_TICKER = ("ticker", "symbol", "simbolo", "sigla", "codigo", "cod", "isin")
_MK_NOME = ("nome", "name", "designacao", "descricao", "description", "emitente", "titulo", "security")
_MK_PRECO = ("ultimopreco", "lastprice", "precofecho", "closeprice", "cotacao", "precoultimo", "preco", "price", "ultimo", "last", "fecho", "close", "valor")
_MK_PRECO_EXCL = ("anterior", "abertura", "open", "max", "min", "prev", "var", "vol", "quant", "media", "avg", "change", "percent", "pct",
                  "oferta", "procura", "bid", "ask", "compra", "venda", "qtd", "total")
_MK_VAR = ("variacao", "variation", "var", "change", "chg", "percent", "pct")
_MK_ANT = ("precoanterior", "fechoanterior", "anterior", "previous", "prev")
_MK_VOL = ("volume", "quantidade", "qtd", "negociad", "quantity", "qty")
_MK_TIPO = ("tipo", "type", "categoria", "classe", "class", "segmento", "mercado", "market")


def _valor_por_chaves(d: dict, candidatos, excluir=()):
    chaves = {_nk(k): k for k in d}
    for c in candidatos:                               # 1) nome exacto
        if c in chaves and not any(x in c for x in excluir):
            v = d[chaves[c]]
            if v not in (None, "") and not isinstance(v, (dict, list)):
                return v
    for c in candidatos:                               # 2) nome que contém o candidato
        for nk, k in chaves.items():
            if c in nk and not any(x in nk for x in excluir):
                v = d[k]
                if v not in (None, "") and not isinstance(v, (dict, list)):
                    return v
    return None


def _registos_para_df(registos: list) -> pd.DataFrame:
    """Converte uma lista de dicionários (JSON da BODIVA, linha de HTML ou de ficheiro) na tabela de mercado."""
    linhas = []
    for d in registos:
        if not isinstance(d, dict):
            continue
        tk = _valor_por_chaves(d, _MK_TICKER) or d.get("__chave__")
        preco = _numero_flex(_valor_por_chaves(d, _MK_PRECO, _MK_PRECO_EXCL))
        if not tk or preco is None or preco <= 0:
            continue
        var = _numero_flex(_valor_por_chaves(d, _MK_VAR, ("abs",)))
        if var is not None and abs(var) > 100:
            var = None
        if var is None:
            ant = _numero_flex(_valor_por_chaves(d, _MK_ANT))
            if ant and ant > 0:
                var = (preco / ant - 1) * 100
        vol = _numero_flex(_valor_por_chaves(d, _MK_VOL, ("valor",)))
        linhas.append({"ticker": str(tk).strip().upper(), "nome": str(_valor_por_chaves(d, _MK_NOME) or "").strip(),
                       "tipo": str(_valor_por_chaves(d, _MK_TIPO) or "").strip(), "preco": preco, "variacao": var, "volume": vol})
    if not linhas:
        return pd.DataFrame(columns=["ticker", "nome", "tipo", "preco", "variacao", "volume"])
    return pd.DataFrame(linhas).drop_duplicates("ticker", keep="last").reset_index(drop=True)


def _listas_de_registos(dados, _prof: int = 0):
    if _prof > 6:
        return
    if isinstance(dados, list):
        if dados and all(isinstance(x, dict) for x in dados[:5]):
            yield dados
        for x in dados[:50]:
            if isinstance(x, (dict, list)):
                yield from _listas_de_registos(x, _prof + 1)
    elif isinstance(dados, dict):
        if len(dados) >= 3 and all(isinstance(v, dict) for v in dados.values()):
            yield [dict(v, __chave__=k) for k, v in dados.items()]
        for v in dados.values():
            if isinstance(v, (dict, list)):
                yield from _listas_de_registos(v, _prof + 1)


def _parsear_resposta_bodiva(resp) -> pd.DataFrame:
    melhor = pd.DataFrame()
    try:
        dados = resp.json()
    except ValueError:
        dados = None
    if dados is not None:
        for lista in _listas_de_registos(dados):
            df = _registos_para_df(lista)
            if len(df) > len(melhor):
                melhor = df
    if melhor.empty:   # recurso: tabela HTML
        try:
            import io
            for tab in pd.read_html(io.StringIO(resp.text)):
                df = _registos_para_df(tab.to_dict("records"))
                if len(df) > len(melhor):
                    melhor = df
        except Exception:
            pass
    return melhor


def _pedido_bodiva():
    cabecalhos = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*", "Referer": "https://www.bodiva.ao/",
    }
    try:
        resp = requests.get(URL_BODIVA_RESUMO, headers=cabecalhos, timeout=20)
    except requests.exceptions.SSLError:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        resp = requests.get(URL_BODIVA_RESUMO, headers=cabecalhos, timeout=20, verify=False)   # dados públicos, só de leitura
    if resp.status_code != 200:
        raise ValueError(f"A BODIVA respondeu com o código HTTP {resp.status_code}.")
    return resp


def cfg_mercado_get(chave: str, padrao: str = "") -> str:
    _garantir_tabelas_extra()
    linha = consultar_um("SELECT valor FROM config_mercado WHERE chave = %s", (chave,))
    return linha[0] if linha and linha[0] is not None else padrao


def cfg_mercado_set(chave: str, valor: str):
    exigir_admin()
    _garantir_tabelas_extra()
    executar("INSERT INTO config_mercado (chave, valor) VALUES (%s, %s) ON CONFLICT (chave) DO UPDATE SET valor = EXCLUDED.valor", (chave, valor))


def _guardar_mercado(df: pd.DataFrame, fonte: str):
    _garantir_tabelas_extra()
    nn = lambda v: None if v is None or (isinstance(v, float) and v != v) else float(v)
    linhas = [(r["ticker"], r["nome"], r["tipo"], nn(r["preco"]), nn(r["variacao"]), nn(r["volume"]), fonte) for _, r in df.iterrows()]
    sql = ("INSERT INTO mercado_bodiva (ticker, nome, tipo, preco, variacao, volume, fonte, actualizado_em) VALUES (%s,%s,%s,%s,%s,%s,%s,NOW()) "
           "ON CONFLICT (ticker) DO UPDATE SET nome = COALESCE(NULLIF(EXCLUDED.nome, ''), mercado_bodiva.nome), "
           "tipo = COALESCE(NULLIF(EXCLUDED.tipo, ''), mercado_bodiva.tipo), preco = EXCLUDED.preco, variacao = EXCLUDED.variacao, "
           "volume = EXCLUDED.volume, fonte = EXCLUDED.fonte, actualizado_em = NOW()")

    def _run(conn):
        with conn.cursor() as cur:
            psycopg2.extras.execute_batch(cur, sql, linhas)
    _com_reconexao(_run)


def ler_mercado_guardado() -> pd.DataFrame:
    _garantir_tabelas_extra()
    df = consultar_df("SELECT ticker, nome, tipo, preco, variacao, volume, fonte, actualizado_em FROM mercado_bodiva ORDER BY nome, ticker")
    for c in ("preco", "variacao", "volume"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def _gravar_historico_clube(df: pd.DataFrame):
    """Opcional (ligado pelo administrador): regista no histórico o último preço do dia dos títulos do Clube."""
    if cfg_mercado_get("auto_historico", "0") != "1":
        return
    activos = obter_activos()
    mapa = {_tk_norm(r["ticker"]): float(r["preco"]) for _, r in activos.iterrows() if str(r["ticker"] or "").strip()}
    hoje = datetime.now().date()
    for _, r in df.iterrows():
        atual = mapa.get(_tk_norm(r["ticker"]))
        if atual is None or r["preco"] is None or r["preco"] <= 0:
            continue
        if atual > 0 and abs(r["preco"] / atual - 1) > 0.5:      # mesma salvaguarda de ±50% do fluxo manual
            continue
        executar("INSERT INTO historico_cotacoes (dia, ticker, preco) VALUES (%s, %s, %s) ON CONFLICT (ticker, dia) DO UPDATE SET preco = EXCLUDED.preco",
                 (hoje, str(r["ticker"]).strip().upper(), float(r["preco"])))


@st.cache_data(ttl=55, show_spinner=False)
def _mercado_bodiva_remoto() -> dict:
    """Vai à BODIVA no máximo uma vez por minuto (cache partilhada) e guarda o resultado na base de dados."""
    ts = datetime.now()
    try:
        df = _parsear_resposta_bodiva(_pedido_bodiva())
        if df.empty:
            return {"ok": False, "erro": "A resposta da BODIVA não contém títulos reconhecíveis (o formato pode ter mudado).", "ts": ts, "n": 0}
        _guardar_mercado(df, "Automática (BODIVA)")
        try:
            _gravar_historico_clube(df)
        except Exception:
            traceback.print_exc()
        return {"ok": True, "erro": None, "ts": ts, "n": len(df)}
    except Exception as e:
        return {"ok": False, "erro": f"{type(e).__name__}: {e}", "ts": ts, "n": 0}


def importar_mercado_manual(df_ficheiro: pd.DataFrame) -> tuple:
    """Resgate manual: grava a tabela de mercado a partir de um CSV/Excel do administrador. (importadas, ignoradas)"""
    exigir_admin()
    df = _registos_para_df(df_ficheiro.to_dict("records"))
    if df.empty:
        return 0, len(df_ficheiro)
    _guardar_mercado(df, f"Manual (ficheiro) · {utilizador_actual()}")
    try:
        _gravar_historico_clube(df)
    except Exception:
        pass
    registar_auditoria("mercado_manual", "mercado", "BODIVA", depois={"linhas": len(df)})
    return len(df), max(len(df_ficheiro) - len(df), 0)


def gerar_xlsx_mercado(df: pd.DataFrame) -> bytes:
    linhas = [[r["ticker"], r["nome"], r["tipo"], r["preco"], r["variacao"], r["volume"], r["fonte"],
               r["actualizado_em"].strftime("%d/%m/%Y %H:%M") if pd.notna(r["actualizado_em"]) else ""] for _, r in df.iterrows()]
    return gerar_xlsx_tabela("Mercado BODIVA - todos os títulos cotados", f"Gerado em {agora()}",
                             ["Ticker", "Título", "Tipo", "Preço (Kz)", "Var. %", "Volume", "Fonte", "Actualizado"], linhas,
                             [14, 38, 16, 16, 10, 14, 26, 18], [None, None, None, "#,##0.00", '+0.00;-0.00;0.00', "#,##0", None, None],
                             folha="Mercado BODIVA", nota="Dados públicos da BODIVA; confirma sempre no site oficial antes de decidir.", cor_cond=(5,))


def _mercado_corpo():
    estado = _mercado_bodiva_remoto()
    df = ler_mercado_guardado()
    admin = eh_admin()
    if estado["ok"]:
        render_html(f'<span class="fx-estado ok">🟢 Ligado à BODIVA · actualizado às {estado["ts"]:%H:%M:%S} · {estado["n"]} títulos · nova leitura automática a cada minuto</span>')
    elif not df.empty:
        ult = df["actualizado_em"].max()
        render_html(f'<span class="fx-estado aviso">🟠 Ligação automática indisponível · a mostrar os últimos valores guardados '
                    f'({ult:%d/%m/%Y %H:%M}, {_esc(str(df.sort_values("actualizado_em").iloc[-1]["fonte"]))})</span>')
    else:
        render_html('<span class="fx-estado erro">🔴 Sem dados de mercado de momento. O administrador pode carregar a tabela manualmente.</span>')
    if admin and estado["erro"]:
        st.caption(f"Detalhe técnico (só administradores): {estado['erro']}")
    render_html('<div class="fx-aviso-membros"><b>Nota para os membros:</b> as cotações vêm da BODIVA e são lidas automaticamente de minuto a minuto. '
                'Se a leitura falhar, mostramos o último valor validado, com a respectiva fonte, data e hora, para que nunca vejas dados sem origem. '
                'Confirma sempre no site oficial antes de decidir.</div>')
    if df.empty:
        st.info("Ainda não há títulos na tabela de mercado.")
        return
    v = df["variacao"]
    sobem, descem = int((v > 0).sum()), int((v < 0).sum())
    estaveis = len(df) - sobem - descem
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Títulos cotados", len(df))
    c2.metric("🟢 A subir", sobem)
    c3.metric("🔴 A descer", descem)
    c4.metric("⚪ Estáveis / s.d.", estaveis)
    f1, f2 = st.columns([2, 1])
    q = f1.text_input("🔎 Procurar título ou ticker", key="mkt_q", placeholder="Ex.: BAI, Unitel…")
    tipos = ["Todos"] + sorted([t_ for t_ in df["tipo"].dropna().unique().tolist() if str(t_).strip()])
    tipo_f = f2.selectbox("Tipo", tipos, key="mkt_tipo")
    vis = df.copy()
    if q.strip():
        m = q.strip().lower()
        vis = vis[vis["ticker"].str.lower().str.contains(m, na=False) | vis["nome"].str.lower().str.contains(m, na=False)]
    if tipo_f != "Todos":
        vis = vis[vis["tipo"] == tipo_f]
    tabela = vis.rename(columns={"ticker": "Ticker", "nome": "Título", "tipo": "Tipo", "preco": "Preço (Kz)", "variacao": "Var. %",
                                 "volume": "Volume", "fonte": "Fonte", "actualizado_em": "Actualizado"})
    sty = (tabela.style.format({"Preço (Kz)": kz2, "Var. %": lambda x: "—" if pd.isna(x) else pct_bruto(x),
                                "Volume": lambda x: "—" if pd.isna(x) else f"{x:,.0f}".replace(",", " "),
                                "Actualizado": lambda x: x.strftime("%d/%m %H:%M") if pd.notna(x) else "—"})
           .map(cor_variacao, subset=["Var. %"]))
    st.dataframe(sty, hide_index=True)
    with st.expander("🍩 Amplitude e composição do mercado", expanded=True):
        g1, g2 = st.columns(2)
        with g1:
            grafico_anel(pd.DataFrame({"Estado": ["A subir", "A descer", "Estáveis / s.d."], "Títulos": [sobem, descem, estaveis]}),
                         "Estado", "Títulos", "Amplitude do mercado", centro_valor=str(len(df)), paleta=["#0D9488", "#E11D48", "#94A3B8"], formato="num", chave="anel_amplitude")
        with g2:
            tp = df.assign(Tipo=df["tipo"].replace("", "Sem tipo")).groupby("Tipo").size().reset_index(name="Títulos")
            grafico_anel(tp, "Tipo", "Títulos", "Títulos por tipo", centro_valor=str(len(df)), formato="num", chave="anel_tipos")
    d1, d2 = st.columns(2)
    xl = _xlsx_seguro(lambda: gerar_xlsx_mercado(tabela.rename(columns={"Ticker": "ticker", "Título": "nome", "Tipo": "tipo", "Preço (Kz)": "preco",
                                                                         "Var. %": "variacao", "Volume": "volume", "Fonte": "fonte", "Actualizado": "actualizado_em"})))
    if xl:
        d1.download_button("⬇️ Descarregar Excel (mercado)", data=xl, file_name=f"mercado_bodiva_{datetime.now():%Y%m%d}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_mkt_xlsx")
    d2.download_button("⬇️ Descarregar CSV (mercado)", data=vis.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
                       file_name=f"mercado_bodiva_{datetime.now():%Y%m%d}.csv", mime="text/csv", key="dl_mkt_csv")


# Actualização automática: o fragmento volta a correr de 60 em 60 segundos sem recarregar a página toda.
_mercado_fragmento = st.fragment(run_every=60)(_mercado_corpo) if hasattr(st, "fragment") else _mercado_corpo


def _admin_mercado():
    st.markdown("#### 🛟 Área do administrador · resgate manual e diagnóstico")
    st.caption("Se a leitura automática falhar, carrega aqui a tabela do teu computador. Os dados ficam guardados e visíveis para todos os membros, com a indicação de fonte manual.")
    with st.expander("📥 Carregar tabela de mercado (CSV ou Excel)"):
        st.caption("Colunas aceites (cabeçalhos flexíveis): **ticker**, **nome**, **tipo**, **preço** (ou cotação/último), **variação** e **volume**.")
        modelo = "ticker;nome;tipo;preco;variacao;volume\nBAIAAAAA;BAI;ACÇÃO;94600;1,25;350\n"
        st.download_button("Modelo de ficheiro (CSV)", data=modelo.encode("utf-8-sig"), file_name="modelo_mercado_bodiva.csv", mime="text/csv", key="mkt_modelo")
        f = st.file_uploader("Ficheiro de mercado", type=["csv", "xlsx"], key="mkt_up")
        if f is not None and st.button("Importar tabela de mercado", key="mkt_imp"):
            try:
                dfi = pd.read_csv(f, sep=None, engine="python", encoding="utf-8-sig") if f.name.lower().endswith(".csv") else pd.read_excel(f)
                if len(dfi) > 5000:
                    st.error("O ficheiro tem demasiadas linhas (máximo 5 000).")
                else:
                    ok, mau = importar_mercado_manual(dfi)
                    (st.success if ok else st.error)(f"Importados {ok} títulos" + (f"; {mau} linhas ignoradas (ticker ou preço inválidos)." if mau else ".") if ok else
                                                     "Nenhuma linha válida: confirma os cabeçalhos (ticker, preço…).")
            except Exception as e:
                st.error(f"Não foi possível importar: {e}")
    with st.expander("⚙️ Opções de automatização"):
        auto_h = st.toggle("Gravar automaticamente no histórico o preço dos títulos do Clube (último preço do dia)",
                           value=cfg_mercado_get("auto_historico", "0") == "1", key="mkt_auto_hist")
        if auto_h != (cfg_mercado_get("auto_historico", "0") == "1"):
            cfg_mercado_set("auto_historico", "1" if auto_h else "0")
            st.rerun()
        if st.button("✅ Aplicar estes preços aos activos do Clube (salvaguarda ±50%)", key="mkt_aplicar"):
            mk = ler_mercado_guardado()
            mapa = {_tk_norm(r["ticker"]): float(r["preco"]) for _, r in mk.iterrows()}
            novo = obter_activos()[["ticker", "nome", "tipo", "preco"]].copy()
            n = 0
            for i in novo.index:
                p_nov = mapa.get(_tk_norm(novo.at[i, "ticker"]))
                p_at = float(novo.at[i, "preco"])
                if p_nov and not (p_at > 0 and abs(p_nov / p_at - 1) > 0.5):
                    novo.at[i, "preco"] = p_nov
                    n += 1
            substituir_activos(novo)
            st.success(f"{n} activos actualizados. Índice APPO e variações recalculados.")
            st.rerun()
    with st.expander("🧪 Diagnóstico da ligação à BODIVA"):
        if st.button("Testar ligação agora", key="mkt_diag"):
            try:
                resp = _pedido_bodiva()
                st.write(f"HTTP {resp.status_code} · {resp.headers.get('Content-Type', '?')} · {len(resp.content)} bytes")
                df = _parsear_resposta_bodiva(resp)
                st.write(f"Títulos reconhecidos: **{len(df)}**")
                try:
                    amostra = next(iter(_listas_de_registos(resp.json())), [])
                    if amostra:
                        st.caption("Campos do primeiro registo (para adaptar o leitor, se preciso):")
                        st.code(", ".join(map(str, amostra[0].keys())))
                except Exception:
                    st.caption("A resposta não é JSON.")
                if not df.empty:
                    st.dataframe(df.head(15), hide_index=True)
                else:
                    st.code(resp.text[:1500])
            except Exception as e:
                st.error(f"Falhou: {e}")


def painel_mercado_bodiva():
    """Tabela de mercado completa (todos os títulos cotados), com actualização automática e resgate manual."""
    _garantir_tabelas_extra()
    _mercado_fragmento()
    if eh_admin():
        st.divider()
        _admin_mercado()


# =========================================================
# COMPONENTES VISUAIS: gráficos de anel, biblioteca por níveis, Histórico & Relatórios avançado
# =========================================================
_PALETA_FX = ["#8E7CC3", "#A8607B", "#D98A82", "#EFB988", "#B3A5DB", "#C98BA0", "#F3CBA4", "#B59A86", "#9AA0C8", "#D6A3B3"]


def grafico_anel(df: pd.DataFrame, cat: str, val: str, titulo: str = "", centro_titulo: str = "Total", centro_valor: str = "",
                 altura: int = 320, formato: str = "kz", paleta=None, chave: str = None):
    """Gráfico de anel rico: etiquetas de peso nas fatias, legenda, tooltip (valor, peso) e total ao centro."""
    d = df[[cat, val]].copy()
    d[val] = pd.to_numeric(d[val], errors="coerce")
    d = d[d[val] > 0].reset_index(drop=True)
    if titulo:
        st.markdown(f"**{titulo}**")
    if d.empty:
        st.caption("Sem dados para este gráfico.")
        return
    total = float(d[val].sum())
    d["Peso"] = d[val] / total
    d["Valor"] = d[val].apply(kz if formato == "kz" else (lambda v: f"{v:,.0f}".replace(",", " ")))
    try:
        import altair as alt
        cores = alt.Scale(domain=d[cat].tolist(), range=(paleta or _PALETA_FX)[:max(len(d), 1)] if paleta else (_PALETA_FX * 3)[:len(d)])
        base = alt.Chart(d).encode(theta=alt.Theta(f"{val}:Q", stack=True),
                                   color=alt.Color(f"{cat}:N", scale=cores, legend=alt.Legend(orient="bottom", title=None, columns=2, labelLimit=220)),
                                   tooltip=[alt.Tooltip(f"{cat}:N", title="Item"), alt.Tooltip("Valor:N", title="Valor"), alt.Tooltip("Peso:Q", format=".1%", title="Peso")])
        arco = base.mark_arc(innerRadius=78, outerRadius=128, cornerRadius=5, padAngle=0.02, stroke="#FFFFFF", strokeWidth=2)
        rotulos = base.transform_filter(alt.datum.Peso >= 0.06).mark_text(radius=103, size=11, fontWeight="bold", color="#FFFFFF").encode(text=alt.Text("Peso:Q", format=".0%"))
        L = 300
        centro = alt.Chart(pd.DataFrame({"t": [centro_valor or (kz(total) if formato == "kz" else f"{total:,.0f}".replace(",", " "))], "s": [centro_titulo]}))
        c1 = centro.mark_text(size=20, fontWeight="bold", color="#1B1033", dy=-6).encode(text="t:N", x=alt.value(L / 2), y=alt.value(L / 2))
        c2 = centro.mark_text(size=11, color="#64748B", dy=14).encode(text="s:N", x=alt.value(L / 2), y=alt.value(L / 2))
        graf = alt.layer(arco, rotulos, c1, c2).properties(width=L, height=altura - 20).configure_view(strokeWidth=0)
        st.altair_chart(graf, use_container_width=True)
    except Exception:
        st.dataframe(d[[cat, "Valor", "Peso"]].assign(Peso=d["Peso"].map("{:.1%}".format)), hide_index=True)


# ---------------------------------------------------------
# Biblioteca: "Para iniciantes" / "Para investidores" com destaque imediato
# ---------------------------------------------------------
def _css_niveis_biblioteca():
    render_html("""<style>
    div[data-baseweb="tab-list"] { gap: 12px; border-bottom: 0; padding: 4px 0 10px 0; }
    button[data-baseweb="tab"] { height: auto; padding: 8px 18px; border-radius: 12px; background: #FFFFFF; border: 2px solid #EDE7F6;
      box-shadow: 0 6px 18px rgba(76, 29, 149, 0.08); transition: transform .12s ease, box-shadow .12s ease; }
    button[data-baseweb="tab"]:hover { transform: translateY(-2px); box-shadow: 0 10px 24px rgba(76, 29, 149, 0.16); }
    button[data-baseweb="tab"] p { font-size: 0.95rem; font-weight: 800; letter-spacing: -0.01em; }
    button[data-baseweb="tab"]:nth-of-type(1)[aria-selected="true"] { background: linear-gradient(120deg, #1D4ED8, #6D28D9); border-color: transparent; }
    button[data-baseweb="tab"]:nth-of-type(2)[aria-selected="true"] { background: linear-gradient(120deg, #6D28D9, #E11D48 60%, #F97316); border-color: transparent; }
    button[data-baseweb="tab"][aria-selected="true"] p { color: #FFFFFF; }
    div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] { display: none; }
    </style>""")


def biblioteca_por_nivel(df_f: pd.DataFrame, tx: dict):
    n_ini = int((df_f["nivel_efectivo"] == "iniciante").sum())
    n_inv = int((df_f["nivel_efectivo"] == "investidor").sum())
    render_html(
        '<div class="fx-nivel">'
        '<div class="fx-nivel-card fx-nivel-ini"><div class="fx-nivel-kicker">Começa aqui</div><div class="fx-nivel-titulo">🌱 Para iniciantes</div>'
        '<p>Conceitos explicados passo a passo, sem jargão. O melhor ponto de partida para quem está a conhecer o mercado.</p>'
        f'<span class="fx-nivel-n">{n_ini} artigos</span></div>'
        '<div class="fx-nivel-card fx-nivel-inv"><div class="fx-nivel-kicker">Nível avançado</div><div class="fx-nivel-titulo">🚀 Para investidores</div>'
        '<p>Análises de OPV, regras de negociação e leitura de mercado para quem já investe ou está pronto para o fazer.</p>'
        f'<span class="fx-nivel-n">{n_inv} artigos</span></div></div>')
    if eh_investidor():
        _css_niveis_biblioteca()
        t_ini, t_inv = st.tabs(["🌱 PARA INICIANTES", "🚀 SE ÉS INVESTIDOR, CLICA AQUI →"])
        with t_ini:
            _mostrar_artigos(df_f[df_f["nivel_efectivo"] == "iniciante"], tx)
        with t_inv:
            _mostrar_artigos(df_f[df_f["nivel_efectivo"] == "investidor"], tx)
    else:
        render_html('<div class="fx-titulo-secao">🌱 Para iniciantes</div>')
        _mostrar_artigos(df_f[df_f["nivel_efectivo"] == "iniciante"], tx)
        if n_inv:
            render_html('<div class="fx-cta"><div class="fx-kicker">Já investes?</div><b>🚀 Se és investidor, clica aqui</b><br>'
                        f'Há {n_inv} artigos avançados no portal Investidor. Faz o teu perfil para desbloquear o acesso.</div>')
            st.button("🚀 Se és investidor, clica aqui", on_click=_ir_para, args=("🧭 Perfil de Investidor",), key="bib_cta_inv", type="primary")


# ---------------------------------------------------------
# Excel multi-folha da análise
# ---------------------------------------------------------
def _xlsx_preencher_folha(ws, titulo, subtitulo, colunas, linhas, larguras, formatos, nota="", cor_cond=()):
    from openpyxl.utils import get_column_letter
    e = _xlsx_estilos()
    n = len(colunas)
    for i, w in enumerate(larguras, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    cab = _xlsx_banner(ws, n, titulo, subtitulo)
    for j, nome in enumerate(colunas, start=1):
        c = ws.cell(row=cab, column=j, value=nome)
        c.font = e["Font"](name="Calibri", size=10, bold=True, color="FFFFFF")
        c.fill, c.border = e["f_bord"], e["borda"]
        c.alignment = e["Alignment"](horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[cab].height = 30
    for i, linha in enumerate(linhas):
        r = cab + 1 + i
        fundo = e["f_creme"] if i % 2 else e["f_branco"]
        for j, valor in enumerate(linha, start=1):
            c = ws.cell(row=r, column=j, value=("n/d" if valor is None or (isinstance(valor, float) and valor != valor) else valor))
            c.fill, c.border = fundo, e["borda"]
            c.font = e["Font"](name="Calibri", size=10, color="1A1A2E")
            eh_num = isinstance(valor, (int, float)) and not isinstance(valor, bool) and valor == valor
            if formatos[j - 1] and eh_num:
                c.number_format = formatos[j - 1]
            c.alignment = e["Alignment"](horizontal="right" if eh_num else ("center" if c.value == "n/d" else "left"), vertical="center", indent=0 if eh_num else 1)
        ws.row_dimensions[r].height = 20
    ultima = cab + len(linhas)
    ws.freeze_panes = ws.cell(row=cab + 1, column=2)
    if linhas:
        _xlsx_cor_sinal(ws, [f"{get_column_letter(j)}{cab + 1}:{get_column_letter(j)}{ultima}" for j in cor_cond])
    _xlsx_rodape(ws, ultima + 2, n, nota)


def gerar_xlsx_analise(a: dict) -> bytes:
    import io
    from openpyxl import Workbook
    ps = [p for p, _ in HORIZ_RENT]
    rot = [_rotulo_horiz(a, p, curto=False) for p in ps]
    fpp = '+0.00;-0.00;0.00'
    wb = Workbook()
    sub = f"Gerado em {agora()} · dados até {a['datas']['fim']:%d/%m/%Y}"
    inf, real = a["inflacao"], a["real"]
    L1 = [["Carteira do Clube (nominal, %)"] + [a["ret_carteira"][p] for p in ps],
          ["Índice APPO (%)"] + [a["ret_appo"][p] for p in ps], ["Índice BODIVA (%)"] + [a["ret_bodiva"][p] for p in ps],
          ["Alpha vs Índice APPO (p.p.)"] + [a["alpha_appo"][p] for p in ps], ["Alpha vs Índice BODIVA (p.p.)"] + [a["alpha_bodiva"][p] for p in ps],
          ["Inflação homóloga (YoY) no período (%)"] + [inf[p]["yoy"] for p in ps], ["Inflação vigente no período (%)"] + [inf[p]["vig"] for p in ps],
          ["Inflação projectada no período (%)"] + [inf[p]["proj"] for p in ps],
          ["Rentabilidade real (YoY) (%)"] + [real[p]["yoy"] if real.get(p) else None for p in ps],
          ["Rentabilidade real (vigente) (%)"] + [real[p]["vig"] if real.get(p) else None for p in ps],
          ["Rentabilidade real (projectada) (%)"] + [real[p]["proj"] if real.get(p) else None for p in ps]]
    _xlsx_preencher_folha(wb.active, "Matriz comparativa de desempenho", sub, ["Indicador"] + rot, L1, [40] + [17] * 6, [None] + [fpp] * 6,
                          "Rentabilidade de preço (sem dividendos nem custos). Alpha = excesso de retorno face ao índice, na mesma janela.", cor_cond=tuple(range(2, 8)))
    wb.active.title = "Matriz comparativa"
    L2 = [[t_["nome"], t_["peso"], t_["valor"], t_["custo"], t_["mais_valia"]] + [t_["ret"][p] for p in ps] + [t_["sigma_a"], t_["dd_max"], (t_["contrib"] * 100) if t_["contrib"] is not None else None] for t_ in a["titulos"]]
    _xlsx_preencher_folha(wb.create_sheet("Por título"), "Rentabilidade multitemporal por título", sub,
                          ["Título", "Peso", "Valor actual (Kz)", "Custo (Kz)", "Mais-valia (Kz)"] + rot + ["Volat. anual. (%)", "Drawdown máx. (%)", "Contrib. risco (%)"], L2,
                          [30, 9, 18, 18, 18] + [15] * 6 + [15, 15, 15], [None, "0.0%", "#,##0", "#,##0", "#,##0"] + [fpp] * 6 + ["0.00", "0.00", "0.0"],
                          cor_cond=(5,) + tuple(range(6, 12)))
    pr = a["premissas"]
    L3 = [["Inflação homóloga (YoY)", pr["inflacao_homologa"] * 100, "Ganho/perda real de poder de compra (12 meses)"],
          ["Inflação vigente (variação mensal)", pr["inflacao_vigente_m"] * 100, "Pulso conjuntural imediato"],
          ["Inflação projectada (12 meses)", pr["inflacao_projectada"] * 100, "Stress e preservação de capital"]]
    _xlsx_preencher_folha(wb.create_sheet("Inflação"), "Inflação de Angola (premissas)", sub, ["Dimensão", "Valor (%)", "Leitura"], L3, [38, 14, 55], [None, "0.00", None],
                          nota=f"Fonte/data: {pr.get('inflacao_ref') or 'valores por defeito - por confirmar com o INE'}")
    rk = a["risco"]
    g = lambda ch: [rk[x].get(ch) if rk.get(x) else None for x in ("carteira", "appo", "bodiva")]
    L4 = [["Observações"] + g("n"), ["Desvio padrão diário (%)"] + g("sigma_d"), ["Volatilidade anualizada (%)"] + g("sigma_a"), ["Drawdown máximo (%)"] + g("dd_max"),
          ["VaR histórico 95% (1 dia, %)"] + g("var95"), ["Tracking error vs APPO (%)", rk["carteira"].get("te"), None, None],
          ["Information ratio vs APPO", rk["carteira"].get("ir"), None, None], ["Beta vs Índice BODIVA", rk["carteira"].get("beta"), None, None],
          ["Sharpe", rk["carteira"].get("sharpe"), None, None]]
    _xlsx_preencher_folha(wb.create_sheet("Risco"), "Análise de risco e desvio padrão", sub, ["Métrica", "Carteira", "Índice APPO", "Índice BODIVA"], L4,
                          [40, 16, 16, 16], [None, "0.00", "0.00", "0.00"], nota="Com poucas observações (<30) as métricas são indicativas.")
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ---------------------------------------------------------
# Página Histórico & Relatórios
# ---------------------------------------------------------
def _df_matriz(a: dict) -> pd.DataFrame:
    ps = [p for p, _ in HORIZ_RENT]
    cols = [_rotulo_horiz(a, p, curto=False) for p in ps]
    inf, real = a["inflacao"], a["real"]
    linhas = {
        "Carteira do Clube (nominal)": a["ret_carteira"], "Índice APPO": a["ret_appo"], "Índice BODIVA": a["ret_bodiva"],
        "Alpha vs Índice APPO (p.p.)": a["alpha_appo"], "Alpha vs Índice BODIVA (p.p.)": a["alpha_bodiva"],
        "Inflação homóloga (YoY)": {p: inf[p]["yoy"] for p in ps}, "Inflação vigente": {p: inf[p]["vig"] for p in ps},
        "Inflação projectada": {p: inf[p]["proj"] for p in ps},
        "Rentabilidade real (YoY)": {p: real[p]["yoy"] if real.get(p) else None for p in ps},
        "Rentabilidade real (vigente)": {p: real[p]["vig"] if real.get(p) else None for p in ps},
        "Rentabilidade real (projectada)": {p: real[p]["proj"] if real.get(p) else None for p in ps}}
    return pd.DataFrame({k: [v.get(p) for p in ps] for k, v in linhas.items()}, index=cols).T.astype(float)


def _fmt_pct_nd(v):
    return "n/d" if pd.isna(v) else f"{v:+.2f}%"


def _aba_rentabilidade(a: dict, tx):
    ps = [p for p, _ in HORIZ_RENT]
    p = _melhor_horizonte(a)
    c1, c2, c3, c4 = st.columns(4)
    if p:
        rot = _rotulo_horiz(a, p, curto=False)
        c1.metric(f"Carteira · {rot}", _fmt_pct_nd(a["ret_carteira"][p]))
        aa, ab = a["alpha_appo"].get(p), a["alpha_bodiva"].get(p)
        c2.metric("Alpha vs APPO", "n/d" if aa is None else f"{aa:+.2f} p.p.", delta=None if aa is None else ("acima" if aa > 0 else "abaixo"))
        c3.metric("Alpha vs BODIVA", "n/d" if ab is None else f"{ab:+.2f} p.p.", delta=None if ab is None else ("acima" if ab > 0 else "abaixo"))
        rr = a["real"].get(p)
        c4.metric("Rentab. real (YoY)", "n/d" if not rr else f"{rr['yoy']:+.2f}%", delta=None if not rr else ("ganho de poder de compra" if rr["yoy"] > 0 else "perda de poder de compra"))
    st.markdown("##### Matriz comparativa multitemporal")
    m = _df_matriz(a)
    linhas_cor = [i for i in m.index if not i.startswith("Inflação")]
    sty = m.style.format(_fmt_pct_nd).map(cor_variacao, subset=pd.IndexSlice[linhas_cor, :])
    st.dataframe(sty)
    st.caption("Alpha = retorno da carteira − retorno do índice na mesma janela (p.p.). Janelas sem histórico completo aparecem como n/d. "
               + (f"A coluna de longo prazo é acumulada desde {a['inicio_comum']:%d/%m/%Y} (data comum às três séries). " if a.get("acumulado") else "")
               + "Rentabilidade de preço: não inclui dividendos nem custos. Índice BODIVA = cotação média encadeada.")
    st.markdown("##### Rentabilidade multitemporal por título")
    tab = pd.DataFrame([{"Título": _pdf_nome_curto(t_["nome"]), "Peso": t_["peso"] * 100, **{_rotulo_horiz(a, p_, curto=False): t_["ret"].get(p_) for p_ in ps}} for t_ in a["titulos"]])
    cols_ret = [c for c in tab.columns if c not in ("Título", "Peso")]
    st.dataframe(tab.style.format({"Peso": "{:.1f}%", **{c: _fmt_pct_nd for c in cols_ret}}).map(cor_variacao, subset=cols_ret), hide_index=True)
    if a["serie_appo"] is not None and len(a["serie_appo"]) >= 2:
        st.markdown("##### Carteira vs índices (base 100 na data comum)")
        ini = max(a["serie_carteira"].index[0], a["serie_appo"].index[0], a["serie_bodiva"].index[0])
        comp = pd.concat([a["serie_carteira"].rename("Carteira"), a["serie_appo"].rename("Índice APPO"), a["serie_bodiva"].rename("Índice BODIVA")], axis=1).ffill()
        comp = comp[comp.index >= ini].dropna()
        if len(comp) >= 2:
            fx_linhas(comp / comp.iloc[0] * 100)


def _aba_inflacao(a: dict):
    pr = a["premissas"]
    if not pr.get("inflacao_ref"):
        st.warning("As três medidas de inflação estão com valores por defeito. O administrador deve inserir os dados do INE em "
                   "Painel do Administrador › Avaliação › Inflação de Angola.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Inflação homóloga (YoY)", f"{pr['inflacao_homologa'] * 100:.2f}%", help="Ganho ou perda real de poder de compra nos últimos 12 meses.")
    c2.metric("Inflação vigente (mensal)", f"{pr['inflacao_vigente_m'] * 100:.2f}% m/m", delta=f"≈ {((1 + pr['inflacao_vigente_m']) ** 12 - 1) * 100:.1f}% anualizada", delta_color="off", help="Pulso conjuntural imediato.")
    c3.metric("Inflação projectada (12M)", f"{pr['inflacao_projectada'] * 100:.2f}%", help="Teste de stress e preservação de capital.")
    st.caption(f"Fonte/data: {pr.get('inflacao_ref') or 'por confirmar'}")
    ps = [p for p, _ in HORIZ_RENT]
    cols = [_rotulo_horiz(a, p, curto=False) for p in ps]
    real = a["real"]
    tab = pd.DataFrame({"Carteira (nominal)": [a["ret_carteira"][p] for p in ps],
                        "Real · inflação YoY": [real[p]["yoy"] if real.get(p) else None for p in ps],
                        "Real · inflação vigente": [real[p]["vig"] if real.get(p) else None for p in ps],
                        "Real · inflação projectada": [real[p]["proj"] if real.get(p) else None for p in ps]}, index=cols).astype(float)
    st.markdown("##### Rentabilidade real por horizonte")
    st.dataframe(tab.T.style.format(_fmt_pct_nd).map(cor_variacao))
    st.markdown("##### Teste de stress · poder de compra de 100 000 Kz sem rendimento")
    ip = pr["inflacao_projectada"]
    linhas = []
    for nome, i_ in (("Inflação projectada", ip), ("Projectada + 5 p.p. (stress)", ip + 0.05)):
        linhas.append({"Cenário": nome, **{f"{n} ano(s)": f"{100000 / (1 + i_) ** n:,.0f} Kz".replace(",", " ") for n in (1, 3, 5)}})
        linhas.append({"Cenário": f"Retorno nominal necessário · {nome}", **{f"{n} ano(s)": f"{((1 + i_) ** n - 1) * 100:.1f}%" for n in (1, 3, 5)}})
    st.dataframe(pd.DataFrame(linhas), hide_index=True)


def _aba_risco(a: dict):
    rk = a["risco"]
    cart = rk["carteira"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Volatilidade anualizada", "n/d" if cart.get("sigma_a") is None else f"{cart['sigma_a']:.2f}%", help="Desvio padrão diário × √252.")
    c2.metric("Desvio padrão diário", "n/d" if cart.get("sigma_d") is None else f"{cart['sigma_d']:.2f}%")
    c3.metric("Drawdown máximo", "n/d" if cart.get("dd_max") is None else f"{cart['dd_max']:.2f}%")
    c4.metric("VaR 95% (1 dia)", "n/d" if cart.get("var95") is None else f"{cart['var95']:.2f}%", help="Precisa de pelo menos 20 observações.")
    nd = lambda v, c=2, s="": "n/d" if v is None else f"{v:.{c}f}{s}"
    tab = pd.DataFrame([
        ["Observações"] + [str(rk[x].get("n", 0)) if rk.get(x) else "n/d" for x in ("carteira", "appo", "bodiva")],
        ["Volatilidade anualizada"] + [nd(rk[x].get("sigma_a"), 2, "%") if rk.get(x) else "n/d" for x in ("carteira", "appo", "bodiva")],
        ["Drawdown máximo"] + [nd(rk[x].get("dd_max"), 2, "%") if rk.get(x) else "n/d" for x in ("carteira", "appo", "bodiva")],
        ["Tracking error vs APPO", nd(cart.get("te"), 2, "%"), "—", "—"], ["Information ratio vs APPO", nd(cart.get("ir")), "—", "—"],
        ["Beta vs Índice BODIVA", nd(cart.get("beta")), "—", "—"], ["Sharpe (Rf das premissas)", nd(cart.get("sharpe")), "—", "—"]],
        columns=["Métrica", "Carteira", "Índice APPO", "Índice BODIVA"])
    st.dataframe(tab, hide_index=True)
    st.markdown("##### Risco por título")
    rt = pd.DataFrame([{"Título": _pdf_nome_curto(t_["nome"]), "Peso (%)": t_["peso"] * 100, "Volat. anual. (%)": t_["sigma_a"], "Drawdown máx. (%)": t_["dd_max"],
                        "Contrib. risco (%)": (t_["contrib"] * 100) if t_["contrib"] is not None else None} for t_ in a["titulos"]])
    st.dataframe(rt.style.format({c: (lambda v: "n/d" if pd.isna(v) else f"{v:.2f}") for c in rt.columns if c != "Título"}), hide_index=True)
    cc = a["concentracao"]
    st.caption(f"Número efectivo de activos (1/HHI): {cc['n_efectivo']:.1f} · maior posição: {cc['maior'][0]} ({cc['maior'][1] * 100:.1f}%). "
               "Contribuição para o risco = peso × covariância com a carteira ÷ variância total.")
    if cart.get("n", 0) < 30:
        st.info("Poucas observações: as métricas de risco são indicativas até haver mais histórico de cotações.")


def _aba_composicao(a: dict, resumo: dict):
    tit = pd.DataFrame([{"Activo": _pdf_nome_curto(t_["nome"]), "Valor": t_["valor"], "Qtd": t_["qtd"],
                         "Sector": _pdf_sector({"ticker": t_["ticker"], "nome": t_["nome"]})} for t_ in a["titulos"]])
    c1, c2 = st.columns(2)
    with c1:
        grafico_anel(tit, "Activo", "Valor", "Carteira por activo (valor actual)", centro_titulo="Valor da carteira", chave="anel_ativo")
    with c2:
        grafico_anel(tit, "Activo", "Qtd", "Carteira por activo (quantidade de títulos)", centro_titulo="Títulos", formato="num", chave="anel_qtd")
    c3, c4 = st.columns(2)
    with c3:
        grafico_anel(tit.groupby("Sector", as_index=False)["Valor"].sum(), "Sector", "Valor", "Carteira por sector", centro_titulo="Valor da carteira", chave="anel_sector")
    with c4:
        res_liq = float(resumo.get("reservas", 0) or 0)
        por_real = max(float(resumo.get("capital_subscrito", 0) or 0) - float(resumo.get("capital_realizado", 0) or 0), 0)
        fundo = pd.DataFrame({"Componente": ["Carteira de acções", "Reservas de liquidez", "Capital por realizar"], "Valor": [a["valor_total"], res_liq, por_real]})
        grafico_anel(fundo, "Componente", "Valor", "Estrutura do fundo global", centro_titulo="Fundo global", chave="anel_fundo")
    mv = pd.DataFrame({"Item": ["Custo de aquisição", "Mais-valia"], "Valor": [min(a["custo_total"], a["valor_total"]), max(a["valor_total"] - a["custo_total"], 0)]})
    if a["valor_total"] > a["custo_total"] > 0:
        grafico_anel(mv, "Item", "Valor", "Valor actual: custo vs mais-valia", centro_titulo="Valor actual", paleta=["#6D28D9", "#0D9488"], chave="anel_mv")


def _aba_historico_movimentos(tx, df_movimentos):
    df_historico = obter_historico_patrimonio()
    if df_historico.empty or len(df_historico) < 2:
        st.info(tx["hist_poucos_pontos"])
    else:
        st.caption(tx["hist_caption"])
        grafico_area_simples(df_historico.set_index("registado_em")[["total"]], tx["hist_patrimonio_label"])
    st.divider()
    st.subheader(tx["hist_movimentos"])
    if df_movimentos.empty:
        st.info(tx["hist_sem_movimentos"])
        return
    df_exibir = df_movimentos.copy()
    df_exibir["montante_fmt"] = df_exibir["montante"].apply(kz)
    st.dataframe(df_exibir[["tipo", "descricao", "montante_fmt", "data_movimento", "criado_em"]].rename(columns=tx["hist_cols"]), hide_index=True)
    c1, c2 = st.columns(2)
    xl = _xlsx_seguro(lambda: gerar_xlsx_tabela(
        "Movimentos do Clube", f"Gerado em {agora()}", ["Data", "Tipo", "Descrição", "Montante (Kz)"],
        [[r["data_movimento"], r["tipo"], r["descricao"], float(r["montante"])] for _, r in df_movimentos.iterrows()],
        [14, 26, 46, 20], ["dd/mm/yyyy", None, None, "#,##0"], folha="Movimentos", cor_cond=(4,)))
    if xl:
        c1.download_button("⬇️ Descarregar Excel (movimentos)", data=xl, file_name="movimentos_appo.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_mov_xlsx")
    c2.download_button(tx["hist_descarregar_mov"], data=df_movimentos.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
                       file_name="movimentos_appo.csv", mime="text/csv", key="dl_mov_csv")


def _aba_relatorios(tx, a: dict, df_movimentos):
    st.subheader(tx["hist_exportar"])
    st.caption("O relatório PDF institucional inclui: sumário executivo e teses, matriz comparativa multitemporal com Alpha, "
               "ajuste à inflação (homóloga, vigente e projectada), risco e desvio padrão, e gráficos de anel.")
    if st.button("📄 " + tx["hist_gerar_pdf"], type="primary", key="btn_gerar_pdf"):
        with st.spinner("A gerar o relatório…"):
            try:
                pdf_bytes = gerar_relatorio_pdf(obter_resumo_patrimonial(), obter_activos(), df_movimentos)
                st.session_state["pdf_relatorio"] = (pdf_bytes, tx["pdf_nome_ficheiro"].format(data=datetime.now().strftime("%Y%m%d")), agora())
            except Exception as e:
                st.session_state.pop("pdf_relatorio", None)
                traceback.print_exc()
                st.error(f"Não foi possível gerar o PDF: {type(e).__name__}: {e}")
    # o botão de descarga fica FORA do `if st.button`, senão desaparece no rerun que o próprio clique provoca
    if st.session_state.get("pdf_relatorio"):
        dados, nome, quando = st.session_state["pdf_relatorio"]
        st.download_button(f"⬇️ {tx['hist_descarregar_pdf']} (gerado às {quando[-5:]})", data=dados, file_name=nome, mime="application/pdf", key="dl_relatorio_pdf")
    st.divider()
    if a.get("ok"):
        xl = _xlsx_seguro(lambda: gerar_xlsx_analise(a))
        if xl:
            st.download_button("⬇️ Descarregar Excel · análise multitemporal (4 folhas)", data=xl, file_name=f"analise_appo_{datetime.now():%Y%m%d}.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_analise_xlsx")
        m = _df_matriz(a)
        st.download_button("⬇️ Descarregar CSV · matriz comparativa", data=m.to_csv(sep=";", decimal=",").encode("utf-8-sig"), file_name="matriz_comparativa_appo.csv", mime="text/csv", key="dl_matriz_csv")
    else:
        st.caption("As exportações analíticas ficam disponíveis assim que houver histórico de cotações e carteira registada.")


def pagina_historico_relatorios(tx):
    df_movimentos = obter_movimentos()
    resumo = obter_resumo_patrimonial()
    a = obter_analise()
    abas = st.tabs(["📈 Rentabilidade & Alpha", "🌡️ Inflação real", "⚖️ Risco", "🍩 Composição", "🗂️ Histórico & Movimentos", "📄 Relatórios & Excel"])
    funcoes = [lambda: _aba_rentabilidade(a, tx), lambda: _aba_inflacao(a), lambda: _aba_risco(a), lambda: _aba_composicao(a, resumo)]
    for i, funcao in enumerate(funcoes):
        with abas[i]:
            if not a.get("ok"):
                st.info(a.get("motivo") or "Análise indisponível de momento.")
                continue
            funcao()
            if i == 0:
                for av in a.get("avisos", []):
                    st.caption("⚠️ " + av)
    with abas[4]:
        _aba_historico_movimentos(tx, df_movimentos)
    with abas[5]:
        _aba_relatorios(tx, a, df_movimentos)



# =========================================================
# FASE 1 — componentes: cartões KPI, gráficos na paleta do Clube, conteúdo institucional editável
# =========================================================
_PALETA_SERIES = ["#8E7CC3", "#A8607B", "#D98A82", "#EFB988", "#B3A5DB", "#C98BA0", "#F3CBA4", "#B59A86"]
COR_PRECO = "#A8607B"          # cotações/preços: vinho do Clube (o gradiente das áreas vai de roxo a vinho, vermelho e laranja)


def kpi_card(icone: str, titulo: str, valor: str, sub: str = None, progresso: float = None, tom: str = None, destaque: bool = False) -> str:
    barra = ""
    if progresso is not None:
        barra = f'<div class="fx-bar"><i style="width:{max(0.0, min(float(progresso), 1.0)) * 100:.0f}%"></i></div>'
    s = f'<div class="fx-kpi-s {tom or ""}">{_esc(sub)}</div>' if sub else ""
    return (f'<div class="fx-kpi{" destaque" if destaque else ""}"><div class="fx-kpi-topo"><span class="fx-kpi-ico">{icone}</span>'
            f'<span class="fx-kpi-t">{_esc(titulo)}</span></div><div class="fx-kpi-v">{_esc(valor)}</div>{s}{barra}</div>')


def kpi_linha(cartoes: list):
    render_html('<div class="fx-kpis">' + "".join(cartoes) + "</div>")


def fx_barras(df: pd.DataFrame, height: int = 300, **_):
    """Barras na paleta do Clube: uma série = gradiente roxo→vinho→vermelho→laranja; várias = barras agrupadas."""
    try:
        import altair as alt
        d = df.copy()
        d.index = d.index.astype(str)
        d.index.name = "Item"
        L = d.reset_index().melt("Item", var_name="Série", value_name="Valor")
        x = alt.X("Item:N", sort=None, title=None, scale=alt.Scale(paddingInner=0.3, paddingOuter=0.2), axis=alt.Axis(labelAngle=0, labelLimit=150, labelColor="#475569"))
        y = alt.Y("Valor:Q", title=None, axis=alt.Axis(format="~s", gridColor="#EDE9F7", labelColor="#64748B"))
        tip = [alt.Tooltip("Item:N", title="Item"), alt.Tooltip("Série:N", title="Série"), alt.Tooltip("Valor:Q", format=",.2f", title="Valor")]
        if d.shape[1] == 1:
            grad = alt.Gradient(gradient="linear", x1=1, x2=1, y1=0, y2=1,
                                stops=[alt.GradientStop(color="#9C8FCF", offset=0), alt.GradientStop(color="#A8607B", offset=0.4), alt.GradientStop(color="#D98A82", offset=0.75), alt.GradientStop(color="#EFB988", offset=1)])
            ch = alt.Chart(L).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, color=grad).encode(x=x, y=y, tooltip=tip)
        else:
            ch = alt.Chart(L).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                x=x, xOffset="Série:N", y=y, tooltip=tip,
                color=alt.Color("Série:N", scale=alt.Scale(range=_PALETA_SERIES), legend=alt.Legend(orient="bottom", title=None)))
        st.altair_chart(ch.properties(height=height).configure_view(strokeWidth=0), use_container_width=True)
    except Exception:
        traceback.print_exc()
        getattr(st, "bar_chart")(df, height=height)


def fx_linhas(df: pd.DataFrame, height: int = 260, **_):
    """Linhas suaves na paleta do Clube, com pontos e dicas ao passar o rato."""
    try:
        import altair as alt
        d = df.copy()
        temporal = isinstance(d.index, pd.DatetimeIndex)
        d.index.name = "Data"
        L = d.reset_index().melt("Data", var_name="Série", value_name="Valor").dropna()
        x = (alt.X("Data:T", title=None, axis=alt.Axis(format="%d/%m/%y", grid=False, labelColor="#64748B")) if temporal
             else alt.X("Data:N", sort=None, title=None, axis=alt.Axis(labelAngle=0, labelColor="#64748B")))
        cor = (alt.Color("Série:N", scale=alt.Scale(range=_PALETA_SERIES), legend=alt.Legend(orient="bottom", title=None)))
        ch = alt.Chart(L).mark_line(strokeWidth=2.4, interpolate="monotone", point=alt.OverlayMarkDef(size=36, filled=True)).encode(
            x=x, y=alt.Y("Valor:Q", title=None, scale=alt.Scale(zero=False), axis=alt.Axis(gridColor="#EDE9F7", labelColor="#64748B")), color=cor,
            tooltip=[alt.Tooltip("Data:T" if temporal else "Data:N", title="Data"), alt.Tooltip("Série:N", title="Série"), alt.Tooltip("Valor:Q", format=",.2f", title="Valor")])
        st.altair_chart(ch.properties(height=height).configure_view(strokeWidth=0), use_container_width=True)
    except Exception:
        traceback.print_exc()
        getattr(st, "line_chart")(df, height=height)


ORC_GRUPOS = [
    ("Consumo (50%)", "🏠", 0.50, "Necessidades e estilo de vida: renda ou prestação da casa, alimentação, transporte, saúde, educação, água/luz/internet, telefone, lazer…"),
    ("Investimento (30%)", "📈", 0.30, "O que pões a render: acções, BT/OT, fundos, cotas do Clube, formação que aumenta o teu rendimento…"),
    ("Entesouramento (20%)", "🛡️", 0.20, "A tua rede de segurança: reserva de emergência, depósito a prazo, poupança para objectivos…"),
]


# ---------------------------------------------------------
# Conteúdo institucional editável (Sobre Nós, FAQ, avisos) — o administrador gere no Painel › Site & Sobre Nós
# ---------------------------------------------------------
_SITE_SEMENTES = [
    ("cartao", "Missão", "Promover a literacia financeira e o acesso disciplinado ao mercado de capitais angolano, permitindo que os sócios construam património de forma colectiva, informada e sustentável.", 10),
    ("cartao", "Visão", "Ser uma referência angolana de educação e prática de investimento em grupo, com decisões transparentes e fundamentadas. (Texto-base: edita-o no Painel do Administrador.)", 20),
    ("cartao", "Valores", "Disciplina, transparência, prestação de contas, diversificação prudente e decisões colectivas.", 30),
    ("faq", "O APPO é uma corretora ou dá conselhos personalizados?", "Não. O APPO é uma iniciativa independente de educação financeira e de investimento em grupo, sem vínculo com a BODIVA, a CMC ou corretoras. O conteúdo é educativo e não constitui recomendação personalizada.", 40),
    ("faq", "Como posso tornar-me sócio?", "Através da página **Adesão de Sócios**. A admissão está sujeita a aprovação da Comissão de Gestão.", 50),
    ("faq", "O que significa investir no mercado de capitais?", "Comprar títulos (acções, obrigações, etc.) esperando valorização ou rendimento. Há risco de perda do capital; por isso começamos pela formação.", 60),
    ("aviso", "Aviso de risco", "Investir envolve risco, incluindo a perda total ou parcial do capital. Rentabilidades passadas não garantem resultados futuros. A informação desta plataforma é educativa.", 90),
]


@st.cache_resource
def _garantir_tabela_site() -> bool:
    executar("""CREATE TABLE IF NOT EXISTS conteudo_site (id SERIAL PRIMARY KEY, secao TEXT NOT NULL DEFAULT 'sobre', tipo TEXT NOT NULL DEFAULT 'cartao',
                titulo TEXT NOT NULL, texto TEXT NOT NULL DEFAULT '', ordem INTEGER NOT NULL DEFAULT 100, visivel BOOLEAN NOT NULL DEFAULT TRUE)""")
    if consultar_um("SELECT COUNT(*) FROM conteudo_site")[0] == 0:
        for tp, ti, tx_, od in _SITE_SEMENTES:
            executar("INSERT INTO conteudo_site (secao, tipo, titulo, texto, ordem) VALUES ('sobre', %s, %s, %s, %s)", (tp, ti, tx_, od))
    return True


def obter_conteudo_site(todos: bool = False) -> pd.DataFrame:
    _garantir_tabela_site()
    return consultar_df("SELECT id, tipo, titulo, texto, ordem, visivel FROM conteudo_site " + ("" if todos else "WHERE visivel ") + "ORDER BY ordem, id")


def guardar_conteudo_site(df: pd.DataFrame):
    exigir_admin()
    _garantir_tabela_site()
    n = 0
    executar("DELETE FROM conteudo_site")
    for _, r in df.iterrows():
        titulo = str(r.get("titulo") or "").strip()
        if not titulo:
            continue
        tipo = str(r.get("tipo") or "cartao").strip()
        executar("INSERT INTO conteudo_site (secao, tipo, titulo, texto, ordem, visivel) VALUES ('sobre', %s, %s, %s, %s, %s)",
                 (tipo if tipo in ("cartao", "faq", "aviso") else "cartao", titulo, str(r.get("texto") or ""),
                  int(_num_seguro(r.get("ordem"), 100)), bool(r.get("visivel", True)) if pd.notna(r.get("visivel")) else True))
        n += 1
    registar_auditoria("conteudo_site", "site", "sobre", depois={"blocos": n})


def painel_site_admin():
    st.subheader("Site & Sobre Nós")
    st.caption("Gere os blocos da página «Sobre Nós». **Cartão** = aparece na grelha (texto simples); **FAQ** = pergunta clicável (aceita markdown); "
               "**Aviso** = faixa de alerta. A ordem é numérica (menor primeiro).")
    df = obter_conteudo_site(todos=True)[["tipo", "titulo", "texto", "ordem", "visivel"]]
    ed = st.data_editor(df, num_rows="dynamic", hide_index=True, key="ed_site", column_config={
        "tipo": st.column_config.SelectboxColumn("Tipo", options=["cartao", "faq", "aviso"], required=True, width="small"),
        "titulo": st.column_config.TextColumn("Título", width="medium"), "texto": st.column_config.TextColumn("Texto", width="large"),
        "ordem": st.column_config.NumberColumn("Ordem", step=10, width="small"), "visivel": st.column_config.CheckboxColumn("Visível", width="small")})
    if st.button("💾 Guardar blocos", type="primary", key="site_guardar"):
        guardar_conteudo_site(ed)
        st.success("Conteúdo actualizado.")
        st.rerun()


def pagina_sobre_nos(tx: dict):
    render_html(f'<div class="fx-quem"><div class="fx-kicker">Quem somos</div><div class="fx-quem-texto">{_esc(tx["sobre_quem_texto"].replace("**", ""))}</div></div>')
    try:
        blocos = obter_conteudo_site()
    except Exception:
        blocos = pd.DataFrame(columns=["tipo", "titulo", "texto"])
    cart = blocos[blocos["tipo"] == "cartao"]
    if not cart.empty:
        render_html('<div class="fx-bloco-grelha">' + "".join(
            f'<div class="fx-bloco"><div class="fx-kicker">APPO</div><div class="fx-bloco-titulo">{_esc(r["titulo"])}</div>'
            f'<div class="fx-bloco-texto">{_esc(r["texto"]).replace(chr(10), "<br>")}</div></div>' for _, r in cart.iterrows()) + "</div>")
    with st.expander("🧭 " + tx["sobre_principios"]):
        st.markdown(TEXTO_PRINCIPIOS)
    with st.expander("📜 " + tx["sobre_estatutos"]):
        st.markdown(tx["sobre_estatutos_texto"])
        _df_est = obter_documentos("estatuto") if eh_participante() else pd.DataFrame()
        if not _df_est.empty:
            _est = _df_est.iloc[0]
            st.markdown(f"**📜 {_est['titulo']}**")
            st.caption(f"{_est['criado_em']} · {_est['tamanho'] / 1048576:.1f} MB")
            bloco_documento_pdf(int(_est["id"]), _est["nome_ficheiro"], f"estatuto_{int(_est['id'])}", altura=820)
    faqs = blocos[blocos["tipo"] == "faq"]
    if not faqs.empty:
        st.markdown("##### Perguntas frequentes")
        for _, r in faqs.iterrows():
            with st.expander("❓ " + str(r["titulo"])):
                st.markdown(r["texto"])
    for _, r in blocos[blocos["tipo"] == "aviso"].iterrows():
        render_html(f'<div class="fx-aviso-risco"><b>⚠️ {_esc(r["titulo"])}.</b> {_esc(r["texto"])}</div>')
    nota_interna(tx["sobre_nota"])


def _painel_inicio_aluno():
    """Início simples: um único próximo passo, atalhos essenciais e o mercado só quando é pedido."""
    nome = str(st.session_state.get("conta_nome") or "").split(" ")[0]
    st.markdown(f"### Bem-vindo, {_html_pub.escape(nome)}" if nome else "### Bem-vindo")
    try:
        dfd = obter_diagnosticos_cf()
    except Exception:
        dfd = pd.DataFrame()
    if not tem_perfil():
        render_html('<div class="appo-perfil-topo"><span class="appo-perfil-rotulo">Primeiro passo</span><div class="appo-perfil-nome" style="font-size:1.4rem;">Faz o teu perfil de investidor</div>'
                    '<p>Em cerca de 4 minutos, o APPO ajusta o teu portal ao teu perfil de risco e à tua experiência.</p></div>')
        st.button("🧭 Fazer o meu perfil", on_click=_ir_para, args=("🧭 Perfil de Investidor",), key="ini_perfil", type="primary")
    elif dfd.empty:
        render_html('<div class="appo-perfil-topo"><span class="appo-perfil-rotulo">Próximo passo</span><div class="appo-perfil-nome" style="font-size:1.4rem;">Mede a tua capacidade financeira</div>'
                    '<p>Um diagnóstico curto mostra onde estás e que treino te ajuda mais.</p></div>')
        st.button("🔎 Fazer o diagnóstico", on_click=_ir_para, args=("🧠 Capacidade Financeira",), key="ini_cf", type="primary")
    else:
        import json as _json
        ult = dfd.iloc[-1]["resultados"]
        ult = _json.loads(ult) if isinstance(ult, str) else ult
        st.metric("A tua capacidade financeira", f"{ult.get('geral', 0):.0f}/100")
        st.button("🧠 Continuar a treinar", on_click=_ir_para, args=("🧠 Capacidade Financeira",), key="ini_cf", type="primary")
    st.markdown("##### Atalhos")
    b1, b2, b3 = st.columns(3)
    b1.button("📚 Biblioteca", on_click=_ir_para, args=("📚 Biblioteca Educativa",), key="ini_bib")
    if eh_investidor():
        b2.button("🧮 Princípio 50/30/20", on_click=_ir_para, args=("🧮 Princípio 50/30/20",), key="ini_r50")
        b3.button("🧪 Simulador", on_click=_ir_para, args=("🧪 Simulador de Investimento",), key="ini_sim")
    else:
        b2.button("🧭 O meu perfil", on_click=_ir_para, args=("🧭 Perfil de Investidor",), key="ini_rev")
        b3.button("🎓 Educação & Serviços", on_click=_ir_para, args=("🎓 Educação & Serviços",), key="ini_edu")
    with st.expander("📈 Cotações de referência"):
        if not _df_activos_ticker.empty:
            st.dataframe(tabela_cotacoes_estilizada(_df_activos_ticker), hide_index=True)
        aviso_discreto("Dados de mercado de referência actualizados pelo administrador; não são cotações em tempo real.")



def pagina_login():
    col_esq, col_centro, col_dir = st.columns([1, 1.4, 1])
    with col_centro:
        st.selectbox("🌐", LISTA_IDIOMAS, key="idioma", label_visibility="collapsed")
        tx = t()
        banner_capa(IMG_SKYLINE, "Crescimento Sustentável, Foco no Longo Prazo", altura=150, escurecimento=0.42)
        logo_com_texto(110)
        render_html(f'<p style="text-align:center; opacity:0.75; margin-top:6px;">{tx["tagline"]}</p>')
        st.markdown(f"#### {tx['login_titulo']}")
        with st.form("form_login"):
            email    = st.text_input(tx["email"])
            password = st.text_input(tx["password"], type="password")
            submeter = st.form_submit_button(tx["entrar"])
        with st.expander("Esqueci-me da palavra-passe"):
            st.caption("Indica o e-mail da tua conta e um telemóvel ou WhatsApp. O administrador contacta-te para confirmar que és tu e repor o acesso.")
            with st.form("form_recuperar_pw", clear_on_submit=True):
                rec_email = st.text_input("E-mail da conta", key="rec_email", max_chars=200)
                rec_tel = st.text_input("Telemóvel ou WhatsApp", key="rec_tel", max_chars=30)
                rec_enviar = st.form_submit_button("Pedir ajuda")
            if rec_enviar:
                _e = (rec_email or "").strip()
                if not _REGEX_EMAIL.match(_e) or len((rec_tel or "").strip()) < 6:
                    st.error("Indica um e-mail válido e um telemóvel para te podermos contactar.")
                elif not _pode_enviar("ultimo_pedido_recup", 30):
                    st.warning("Aguarda alguns segundos antes de enviar outro pedido.")
                else:
                    try:
                        registar_pedido_recuperacao(_e, rec_tel)
                    except Exception:
                        traceback.print_exc()
                    st.success("Pedido enviado. Se existir uma conta com este e-mail, o administrador vai contactar-te em breve.")
        if submeter:
            conta = obter_conta_por_email(email.strip().lower())
            if conta and verificar_password(password, conta[3]):
                registar_acesso(email, True)
                st.session_state["autenticado"]     = True
                st.session_state["login_timestamp"] = time.time()
                st.session_state["conta_id"]        = conta[0]
                st.session_state["conta_nome"]      = conta[1]
                st.session_state["conta_email"]     = conta[2]
                st.session_state["is_admin"]        = bool(conta[4])
                st.session_state["is_premium"]      = bool(conta[5])
                st.session_state["is_participante"] = bool(conta[6])
                st.session_state["nivel"]           = str(conta[7] or "iniciante")
                st.session_state["trocar_password"] = bool(conta[8])
                try:
                    _carregar_perfil_sessao(conta[0])
                except Exception:
                    traceback.print_exc()
                st.rerun()
            else:
                registar_acesso(email, False)
                st.error(tx["erro_login"])


if not st.session_state["autenticado"]:
    _aba_entrar, _aba_cf, _aba_edu, _aba_int = st.tabs(["🔐 Entrar", "🧠 Capacidade Financeira", "🎓 Educação & Serviços", "🤝 Manifestação de interesse"])
    with _aba_entrar:
        pagina_login()
    with _aba_cf:
        pagina_capacidade_financeira(False)
    with _aba_edu:
        pagina_educacao_servicos()
    with _aba_int:
        pagina_manifestacao_interesse()
    st.stop()

# Palavra-passe reposta pelo administrador: a pessoa tem de escolher uma só sua antes de continuar
if st.session_state.get("trocar_password"):
    st.markdown("### Escolhe a tua nova palavra-passe")
    st.info("O administrador repôs o teu acesso. Por segurança, define agora uma palavra-passe só tua.")
    with st.form("form_troca_obrigatoria"):
        _tp_a = st.text_input("Palavra-passe provisória (a que recebeste)", type="password")
        _tp_n = st.text_input("Nova palavra-passe (mín. 8 caracteres)", type="password")
        _tp_r = st.text_input("Repetir a nova palavra-passe", type="password")
        _tp_ok = st.form_submit_button("Guardar e continuar", type="primary")
    if _tp_ok:
        _tp_err = alterar_password_propria(st.session_state.get("conta_id"), _tp_a, _tp_n, _tp_r)
        if _tp_err:
            st.error(_tp_err)
        else:
            st.session_state["trocar_password"] = False
            st.rerun()
    if st.button("Terminar sessão", key="troca_sair"):
        for _ch in ["autenticado", "login_timestamp", "conta_id", "conta_nome", "conta_email", "is_admin", "is_premium", "is_participante", "nivel", "perfil", "perfil_data", "_perfil_visto", "trocar_password"]:
            st.session_state.pop(_ch, None)
        st.rerun()
    st.stop()

# =========================================================
# BARRA LATERAL
# =========================================================
tx = t()
render_html(f'<div class="appo-sidebar-header">{logo_svg(50)}<div><p class="appo-sidebar-sub">Clube de Investimento</p><div class="appo-sidebar-word">APPO</div></div></div>')
st.sidebar.selectbox("🌐 Idioma / Language", LISTA_IDIOMAS, key="idioma")
selo_premium = " · ⭐ Premium" if st.session_state["is_premium"] else ""
st.sidebar.caption(f"{tx['sessao']}: {st.session_state['conta_nome']} ({st.session_state['conta_email']}){selo_premium}")
with st.sidebar:
    _cartao_portal_lateral()
st.sidebar.divider()

PAGINAS = ["🏠 Início & Análises", "🧭 Perfil de Investidor", "🧠 Capacidade Financeira"]
if eh_participante():
    PAGINAS += ["💰 Contabilidade & Finanças", "📊 Histórico & Relatórios"]   # área patrimonial restrita
if eh_investidor():   # Portal Investidor (níveis avançados)
    PAGINAS += ["📈 Cotações & Activos", "📐 Avaliação de Activos", "🧪 Simulador de Investimento", "🧮 Princípio 50/30/20", "💱 Conversor de Moeda"]
PAGINAS += ["📚 Biblioteca Educativa", "🎓 Educação & Serviços", "🧾 Adesão de Sócios", "ℹ️ Sobre Nós & Estatutos"]
if st.session_state["is_admin"]:
    PAGINAS.append("🔐 Painel do Administrador")
if st.session_state.get("nav_pagina") not in PAGINAS:
    st.session_state["nav_pagina"] = PAGINAS[0]
# Primeira visita sem perfil: aterra no Perfil de Investidor (uma só vez; pode sair quando quiser)
if (not tem_perfil()) and not (eh_admin() or eh_participante()) and not st.session_state.get("_perfil_visto"):
    st.session_state["nav_pagina"] = "🧭 Perfil de Investidor"
    st.session_state["_perfil_visto"] = True

pagina = st.sidebar.radio("Navegação", PAGINAS, key="nav_pagina", label_visibility="collapsed", format_func=lambda k: tx["nav_map"].get(k, k))

st.sidebar.caption("Versão da app: 2026-10-14 · B (logótipos, Universo do Clube)")
st.sidebar.divider()
with st.sidebar.expander("🔑 Alterar palavra-passe"):
    with st.form("form_alterar_pw", clear_on_submit=True):
        _pw_a = st.text_input("Palavra-passe actual", type="password")
        _pw_n = st.text_input("Nova palavra-passe (mín. 8 caracteres)", type="password")
        _pw_r = st.text_input("Repetir a nova palavra-passe", type="password")
        _pw_ok = st.form_submit_button("Guardar")
    if _pw_ok:
        _err_pw = alterar_password_propria(st.session_state.get("conta_id"), _pw_a, _pw_n, _pw_r)
        if _err_pw:
            st.error(_err_pw)
        else:
            st.success("Palavra-passe alterada.")
if st.sidebar.button(tx["terminar_sessao"]):
    for chave in ["autenticado", "login_timestamp", "conta_id", "conta_nome", "conta_email", "is_admin", "is_premium", "is_participante", "nivel", "perfil", "perfil_data", "_perfil_visto", "trocar_password"]:
        st.session_state.pop(chave, None)
    st.rerun()

st.sidebar.caption(f"Última actualização da página: {agora()}")

_df_activos_ticker = obter_activos()
ticker_tape(_df_activos_ticker)

# =========================================================
# PÁGINA: INÍCIO & ANÁLISES
# =========================================================
try:
    if pagina == "🏠 Início & Análises":
        tx = t()
        hero("Clube de Investimento APPO", tx["inicio_hero_sub"])

        if not eh_participante():
            _painel_inicio_aluno()
            st.stop()

        resumo = obter_resumo_patrimonial()
        total_patrimonio = resumo["capital_realizado"]  # investimentos e reservas são parte do realizado

        _sub, _real, _inv, _res = (float(resumo[k] or 0) for k in ("capital_subscrito", "capital_realizado", "investimentos", "reservas"))
        _cartoes = [
            kpi_card("🏦", tx["inicio_capital_subscrito"], kz(_sub), "Compromisso total dos sócios"),
            kpi_card("💳", tx["inicio_capital_realizado"], kz(_real), (f"{_real / _sub * 100:.0f}{tx['inicio_pct_subscrito']}" if _sub else None), (_real / _sub if _sub else None)),
            kpi_card("📈", tx["inicio_investimentos"], kz(_inv), (f"{_inv / _real * 100:.0f}% do realizado" if _real else None), (_inv / _real if _real else None)),
            kpi_card("🛡️", tx["inicio_reservas"], kz(_res), (f"{_res / _real * 100:.0f}% do realizado" if _real else None), (_res / _real if _real else None)),
            kpi_card("🧮", tx["inicio_patrimonio_total"], kz(total_patrimonio), "Capital realizado", destaque=True),
        ]
        _res_idx = resumo_indice_appo(_df_activos_ticker)
        if _res_idx:
            _v1 = _res_idx[1]
            _cartoes.append(kpi_card("📊", "Índice APPO (100 = 19/08/2026)", f"{_res_idx[0]:.2f}",
                                     (f"{_v1:+.2f}% em 1d" if _v1 is not None else None), None, ("up" if (_v1 or 0) > 0 else "down" if (_v1 or 0) < 0 else None)))
        else:
            _ind = calcular_indice_mercado(_df_activos_ticker)
            _cartoes.append(kpi_card("📊", tx["inicio_indice_label"], pct_bruto(_ind), None, None, ("up" if _ind > 0 else "down" if _ind < 0 else None)))
        kpi_linha(_cartoes)
        st.caption("Índice APPO: variação média de todas as acções cotadas desde o dia em que o Clube começou a investir." if _res_idx else tx["inicio_indice_caption"])
        st.divider()

        st.subheader(tx["inicio_distribuicao"])
        cats = tx["inicio_distribuicao_cats"]
        fx_barras(pd.DataFrame({"Categoria": cats,
                                   "Montante (Kz)": [resumo["capital_realizado"], resumo["investimentos"], resumo["reservas"]]}).set_index("Categoria"))

        st.divider()
        banner_capa(IMG_GRAFICO, tx["inicio_capa_texto"], altura=130, escurecimento=0.48)

        st.subheader(tx["inicio_cotacoes_destaque"])
        if not _df_activos_ticker.empty:
            st.dataframe(tabela_cotacoes_estilizada(_df_activos_ticker), hide_index=True)

        secao_vup_inicio()

    # =========================================================
    # PÁGINA: COTAÇÕES & ACTIVOS
    # =========================================================
    elif pagina == "📈 Cotações & Activos":
        tx = t()
        hero("📈 " + tx["nav_map"]["📈 Cotações & Activos"].replace("📈 ", ""), tx["cot_hero_sub"], "🇦🇴 Dados BODIVA")

        df_activos = _df_activos_ticker
        if df_activos.empty:
            st.info(tx["cot_fav_info"])
            painel_mercado_bodiva()
        else:
            st.subheader("📊 Índices")
            _painel_indices(df_activos)
            st.divider()

            aba_mkt, aba_fav, aba_todos, aba_graf = st.tabs(["🌐 Mercado BODIVA", tx["cot_tab_favoritos"], tx["cot_tab_todos"], "📊 Gráficos do Clube"])
            with aba_mkt:
                painel_mercado_bodiva()
            conta_id          = st.session_state["conta_id"]
            favoritos_actuais = obter_favoritos(conta_id)

            with aba_fav:
                opcoes           = dict(zip(df_activos["nome"], df_activos["id"]))
                seleccionados_nomes = [nome for nome, aid in opcoes.items() if aid in favoritos_actuais]
                novos_nomes      = st.multiselect(tx["cot_fav_escolher"], options=list(opcoes.keys()), default=seleccionados_nomes)
                if set(novos_nomes) != set(seleccionados_nomes):
                    definir_favoritos(conta_id, [opcoes[n] for n in novos_nomes])
                    st.rerun()
                if novos_nomes:
                    st.dataframe(tabela_cotacoes_estilizada(df_activos[df_activos["nome"].isin(novos_nomes)]), hide_index=True, column_config=cfg_logo())
                else:
                    st.info(tx["cot_fav_info"])

            with aba_todos:
                st.caption("Todos os activos que o Clube acompanha — cotados na BODIVA ou não —, organizados por classe.")
                _classes = {"Todas": None, "📈 Ações": ("ação", "acao", "acç"), "🏛️ Obrigações": ("obrig", "bilhete", "título público", "titulo publico"), "📊 Fundos": ("fundo",)}
                _cl = st.radio("Classe de activo", list(_classes), horizontal=True, key="cot_classe")
                _chaves = _classes[_cl]
                df_filtrado = df_activos if _chaves is None else df_activos[df_activos["tipo"].astype(str).str.lower().apply(lambda v: any(c in v for c in _chaves))]
                if df_filtrado.empty:
                    st.info(f"O Clube ainda não acompanha activos nesta classe ({_cl.split(' ', 1)[-1]}). "
                            "O administrador pode registá-los em Painel do Administrador › Cotações & Activos.")
                st.dataframe(tabela_cotacoes_estilizada(df_filtrado), hide_index=True, column_config=cfg_logo())
                st.caption(f"{tx['cot_ultima_actualizacao']} {df_filtrado['actualizado_em'].max()}")
                _xl_cot = _xlsx_seguro(lambda: gerar_xlsx_cotacoes(df_filtrado))
                if _xl_cot:
                    st.download_button("⬇️ Descarregar Excel (formatado)", data=_xl_cot, file_name="cotacoes_appo.xlsx",
                                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_cot_xlsx")
                st.download_button(tx["cot_descarregar_csv"],
                                   data=df_filtrado[["ticker", "nome", "tipo", "preco", "variacao"]].to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
                                   file_name="cotacoes_appo.csv", mime="text/csv")
                st.divider()
                st.subheader(tx["cot_comparacao"])
                cols_tb = tx["cot_tabela_cols"]
                if not df_filtrado.empty:
                    fx_barras(df_filtrado.set_index("nome")[["preco"]].rename(columns={"preco": tx["cot_preco_kz"]}))

            with aba_graf:
                registar_cotacoes_hoje(df_activos)
                try:
                    _tk_cart = {str(x).strip().upper() for x in obter_carteira_real()["ticker"]}
                except Exception:
                    _tk_cart = set()
                _ops = []
                for _, _a in df_activos.iterrows():
                    _t = str(_a.get("ticker") or "").strip().upper()
                    if _t:
                        _ops.append((("★ " if _t in _tk_cart else "") + str(_a["nome"]), _t, str(_a["nome"])))
                _ops.sort(key=lambda x: (not x[0].startswith("★"), x[0]))
                if not _ops:
                    if eh_admin():
                        st.info("Registe os tickers dos activos em Painel do Administrador → Cotações & Activos.")
                    else:
                        st.caption("As cotações de referência ainda estão a ser preparadas.")
                else:
                    gc1, gc2 = st.columns([2, 3])
                    _rot = gc1.selectbox("Título (★ = em carteira do Clube)", [o[0] for o in _ops], key="graf_titulo")
                    _periodo = gc2.radio("Período", PERIODOS_GRAFICO, index=2, horizontal=True, key="graf_periodo")
                    _sel = next(o for o in _ops if o[0] == _rot)
                    _opv = obter_opv(_sel[1])
                    _ref = ((f"Preço da OPV: {_opv[0]:,.0f} Kz".replace(",", " ") + (f" ({_opv[1]:%d/%m/%Y})" if _opv[1] else "")), _opv[0]) if _opv else None
                    painel_grafico(_sel[2].upper(), f"{_sel[1]}  |  BODIVA  |  AOA", obter_serie_cotacao(_sel[1], _periodo), "Kz", _periodo, referencia=_ref,
                                   nota=("O histórico do Clube é gravado de cada vez que as cotações são actualizadas (um valor por dia, "
                                         "o último desse dia). Quanto mais actualizações, mais completo o gráfico. "
                                         "Não há valores dentro do dia (intraday)."))

    # =========================================================
    # PÁGINA: CONTABILIDADE & FINANÇAS
    # =========================================================
    elif pagina == "💰 Contabilidade & Finanças":
        tx = t()
        hero("💰 " + tx["nav_map"]["💰 Contabilidade & Finanças"].replace("💰 ", ""), tx["cont_hero_sub"])
        resumo   = obter_resumo_patrimonial()
        cols_df  = tx["cont_df_cols"]
        rows_df  = tx["cont_df_rows"]
        montantes= [kz(resumo["capital_subscrito"]), kz(resumo["capital_realizado"]), kz(resumo["investimentos"]), kz(resumo["reservas"])]
        df_resumo = pd.DataFrame([{cols_df[0]: r[0], cols_df[1]: r[1], cols_df[2]: m, cols_df[3]: r[2]}
                                   for r, m in zip(rows_df, montantes)])
        st.dataframe(df_resumo, hide_index=True)
        total_patrimonio = resumo["capital_realizado"]  # investimentos e reservas são subdivisões do realizado
        st.metric(tx["cont_patrimonio_metric"], kz(total_patrimonio))
        st.caption(f"{tx['cont_ultima_actualizacao']} {resumo['actualizado_em']}")

    # =========================================================
    # PÁGINA: HISTÓRICO & RELATÓRIOS
    # =========================================================
    elif pagina == "📊 Histórico & Relatórios":
        tx = t()
        hero("📊 " + tx["nav_map"]["📊 Histórico & Relatórios"].replace("📊 ", ""), tx["hist_hero_sub"])
        pagina_historico_relatorios(tx)

    # =========================================================
    # PÁGINA: AVALIAÇÃO DE ACTIVOS
    # =========================================================
    elif pagina == "📐 Avaliação de Activos":
        tx = t()
        hero("📐 " + tx["nav_map"]["📐 Avaliação de Activos"].replace("📐 ", ""), tx["aval_hero_sub"])
        premissas = obter_premissas_macro()
        df_aval   = obter_avaliacoes()

        if df_aval.empty:
            st.info(tx["aval_sem_dados"])
        else:
            empresa_sel = st.selectbox(tx["aval_empresa"], df_aval["empresa"].tolist())
            av_linha    = df_aval[df_aval["empresa"] == empresa_sel].iloc[0]
            av = {"sector": av_linha["sector"], "preco": float(av_linha["preco"]),
                  "acoes_circulacao": float(av_linha["acoes_circulacao"]), "lucro_liquido": float(av_linha["lucro_liquido"]),
                  "ganho_pontual": float(av_linha["ganho_pontual"]), "capital_proprio": float(av_linha["capital_proprio"]),
                  "dividendo_total": float(av_linha["dividendo_total"]), "crescimento_g": float(av_linha["crescimento_g"])}
            m = calcular_metricas_avaliacao(av, premissas)

            st.caption(f"{tx['aval_sector']}: {av['sector']} · {tx['aval_cap_mercado']} {kz(m['cap_mercado'])}")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(tx["aval_preco"], kz(av["preco"]))
            col2.metric(tx["aval_pe"],    multiplo(m["pe"]))
            col3.metric(tx["aval_pbv"],   multiplo(m["pbv"]))
            col4.metric(tx["aval_dy"],    pct(m["dy_nominal"]))
            nota_indicador(tx["aval_nota1"])

            col5, col6, col7 = st.columns(3)
            col5.metric(tx["aval_vj"],     kz(m["valor_justo"]) if m["valor_justo"] is not None else "n/d")
            col6.metric(tx["aval_upside"], pct(m["upside"])     if m["upside"]      is not None else "n/d")
            col7.metric(tx["aval_ke"],     pct(m["ke"]))
            nota_indicador(tx["aval_nota2"])

            if m["valor_justo"] is None:
                st.warning("Premissas inválidas para o modelo: o crescimento assumido (g) tem de ser inferior ao custo de capital (Ke). Ajuste as premissas no painel do administrador.")
            if m["upside"] is not None:
                if m["upside"] > 0.15:
                    st.success(tx["aval_subvalorizado"])
                elif m["upside"] < -0.15:
                    st.warning(tx["aval_sobrevalorizado"])
                else:
                    st.info(tx["aval_justo"])

            st.caption(tx["aval_ddm_caption"])
            st.divider()
            st.subheader(tx["aval_premium_titulo"])

            if not st.session_state["is_premium"]:
                render_html(tx["aval_premium_lock"])
            else:
                col_a, col_b, col_c = st.columns(3)
                col_a.metric(tx["aval_roe"],    pct(m["roe"])    if m["roe"]    is not None else "n/d")
                col_b.metric(tx["aval_payout"], pct(m["payout"]) if m["payout"] is not None else "n/d")
                col_c.metric(tx["aval_dy_real"], pct(m["dy_real"]))
                nota_indicador(tx["aval_nota3"])

                st.markdown(tx["aval_sensibilidade"])
                ke_base, g_base = m["ke"], av["crescimento_g"]
                cenarios_g  = [max(0.0, g_base - 0.02), g_base, g_base + 0.02]
                cenarios_ke = [ke_base - 0.02, ke_base, ke_base + 0.02]
                linhas = []
                for ke_c in cenarios_ke:
                    linha = {}
                    for g_c in cenarios_g:
                        linha[f"g={g_c*100:.1f}%"] = kz((m["dps"] * (1 + g_c)) / (ke_c - g_c)) if ke_c > g_c else "—"
                    linhas.append(linha)
                st.dataframe(pd.DataFrame(linhas, index=[f"Ke={ke_c*100:.1f}%" for ke_c in cenarios_ke]))

                st.markdown(tx["aval_comparacao"])
                cols_comp = tx["aval_comp_cols"]
                linhas_comp = []
                linhas_xlsx_comp = []
                for _, l in df_aval.iterrows():
                    av_l = {"sector": l["sector"], "preco": float(l["preco"]), "acoes_circulacao": float(l["acoes_circulacao"]),
                            "lucro_liquido": float(l["lucro_liquido"]), "ganho_pontual": float(l["ganho_pontual"]),
                            "capital_proprio": float(l["capital_proprio"]), "dividendo_total": float(l["dividendo_total"]),
                            "crescimento_g": float(l["crescimento_g"])}
                    m_l = calcular_metricas_avaliacao(av_l, premissas)
                    linhas_comp.append({cols_comp["Empresa"]: l["empresa"], cols_comp["Sector"]: l["sector"],
                                         cols_comp["P/E"]: multiplo(m_l["pe"]), cols_comp["P/BV"]: multiplo(m_l["pbv"]),
                                         cols_comp["ROE"]: pct(m_l["roe"]) if m_l["roe"] is not None else "n/d",
                                         cols_comp["DY Nominal"]: pct(m_l["dy_nominal"]),
                                         cols_comp["Upside DDM"]: pct(m_l["upside"]) if m_l["upside"] is not None else "n/d"})
                    linhas_xlsx_comp.append([l["empresa"], l["sector"], m_l["pe"], m_l["pbv"], m_l["roe"], m_l["dy_nominal"], m_l["upside"]])
                df_comp = pd.DataFrame(linhas_comp)
                st.dataframe(df_comp, hide_index=True)

                # Interpretação automática da tabela comparativa
                with st.expander("💡 Como interpretar esta tabela?"):
                    st.markdown("""
**P/E (Price-to-Earnings):** Quantos anos de lucro estás a pagar pelo preço actual.
- P/E < 8x → potencialmente barato para o contexto angolano
- P/E 8–15x → zona de fair value
- P/E > 15x → caro, exige crescimento elevado para justificar

**P/BV (Price-to-Book Value):** Preço face ao valor contabilístico dos activos.
- P/BV < 1x → estás a comprar activos abaixo do valor de balanço (atenção: pode indicar problema estrutural)
- P/BV 1–2x → razoável para banca angolana
- P/BV > 2x → só justificado por ROE elevado e consistente

**ROE (Return on Equity):** Rentabilidade do capital próprio.
- ROE > 15% → empresa cria valor acima do custo de capital estimado (Ke ≈ 18%)
- ROE < Ke → empresa destrói valor para o accionista a longo prazo

**Dividend Yield (DY Nominal):** Retorno em dividendos ao preço actual.
- Com inflação angolana ~13,5%, um DY < 13,5% significa retorno real negativo em dividendos

**Upside DDM:** Diferença entre o valor justo estimado pelo modelo DDM e o preço de mercado.
- Positivo → modelo sugere subvalorização; Negativo → sobrevalorização
- ⚠️ O DDM é sensível às premissas de crescimento (g) e custo de capital (Ke) — usar sempre como uma referência, não como verdade absoluta.
                """)

                _xl_comp = _xlsx_seguro(lambda: gerar_xlsx_comparacao(linhas_xlsx_comp))
                if _xl_comp:
                    st.download_button("⬇️ Descarregar Excel (formatado)", data=_xl_comp, file_name="comparacao_sectorial_appo.xlsx",
                                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_comp_xlsx")
                st.download_button(tx["aval_descarregar_comp"],
                                   data=df_comp.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
                                   file_name="comparacao_sectorial_appo.csv", mime="text/csv")

    # =========================================================
    # PÁGINA: CONVERSOR DE MOEDA
    # =========================================================
    elif pagina == "💱 Conversor de Moeda":
        tx = t()
        hero("💱 " + tx["nav_map"]["💱 Conversor de Moeda"].replace("💱 ", ""), tx["conv_hero_sub"], "💱 exchangerate-api.com (aberta)")

        MOEDAS = ["AOA", "USD", "EUR", "GBP", "ZAR", "CNY", "BRL"]
        col1, col2, col3 = st.columns(3)
        moeda_de  = col1.selectbox(tx["conv_de"],   MOEDAS, index=0)
        moeda_para= col2.selectbox(tx["conv_para"], MOEDAS, index=1)
        valor     = col3.number_input(tx["conv_valor"], min_value=0.0, value=1000.0, step=100.0)

        try:
            dados_cambio = obter_taxas_cambio(moeda_de)
            if moeda_de == "AOA":
                registar_historico_cambio(dados_cambio["rates"])
            taxa = dados_cambio["rates"].get(moeda_para)
            if taxa is None:
                st.error(tx["conv_erro"])
            else:
                resultado = valor * taxa
                st.metric(f"{valor:,.2f} {moeda_de} {tx['conv_equivale']}", f"{resultado:,.2f} {moeda_para}")
                st.caption(f"{tx['conv_taxa']} 1 {moeda_de} = {taxa:.6f} {moeda_para}. {tx['conv_actualizado']} {dados_cambio['actualizado']}.")
                texto_partilha = tx["conv_partilha"].format(v=f"{valor:,.2f}", de=moeda_de, r=f"{resultado:,.2f}", para=moeda_para)
                botoes_partilha(texto_partilha)
        except Exception:
            st.warning(tx["conv_aviso"])

        st.divider()
        st.subheader(tx["conv_tabela_titulo"])
        try:
            dados_kz = obter_taxas_cambio("AOA")
            registar_historico_cambio(dados_kz["rates"])
            col_eq = tx["conv_tabela_col"]
            linhas = [{"Moeda": m, col_eq: f"{dados_kz['rates'].get(m, 0):.6f} {m}"} for m in MOEDAS if m != "AOA"]
            st.dataframe(pd.DataFrame(linhas), hide_index=True)
        except Exception:
            st.caption(tx["conv_tabela_indisponivel"])

        st.divider()
        st.subheader("📈 Evolução do câmbio do Kwanza")
        cg_a, cg_b = st.columns([1, 3])
        moeda_graf = cg_a.selectbox("Moeda", ["USD", "EUR", "GBP", "ZAR", "CNY", "BRL"], key="conv_graf_moeda")
        periodo_cambio = cg_b.radio("Período", PERIODOS_GRAFICO, index=2, horizontal=True, key="conv_graf_periodo")
        try:
            serie_cambio = obter_serie_cambio_aoa(moeda_graf, periodo_cambio)
        except Exception:
            serie_cambio = pd.DataFrame(columns=["Data", "Valor"])
        painel_grafico(f"{moeda_graf} / AOA", f"Kz por 1 {moeda_graf}", serie_cambio, "Kz", periodo_cambio,
                       nota=("Taxas indicativas de mercado (fonte aberta: fawazahmed0/exchange-api), uma por dia; "
                             f"os dados existem desde {CAMBIO_DADOS_DESDE[8:]}/{CAMBIO_DADOS_DESDE[5:7]}/{CAMBIO_DADOS_DESDE[:4]}, "
                             "por isso o período de 5 anos mostra só o que há desde essa data. Não há valores dentro do dia (intraday). "
                             "Podem diferir da taxa oficial do BNA e das praticadas pelos bancos."))

    # =========================================================
    # PÁGINA: SIMULADOR — HOME BROKER APPO + JUROS COMPOSTOS
    # =========================================================
    elif pagina == "🧪 Simulador de Investimento":
        tx = t()
        hero("🧪 Home Broker APPO — BODIVA Virtual",
             "Opera a bolsa angolana sem risco real · Dotação inicial: 3 000 000 Kz",
             "🎮 BODIVA Virtual · Dinheiro fictício")

        # ── carregar estado persistido deste sócio (uma vez por sessão) ─
        _email_sim = st.session_state.get("conta_email", "")
        if st.session_state.get("sim_carregado_para") != _email_sim:
            _saldo0, _cart0, _hist0 = obter_estado_simulador(_email_sim)
            st.session_state["sim_carteira"]    = _cart0
            st.session_state["sim_saldo_caixa"] = _saldo0
            st.session_state["sim_historico"]   = _hist0
            st.session_state["sim_carregado_para"] = _email_sim
        if "sim_qtd_sel" not in st.session_state:
            st.session_state["sim_qtd_sel"] = {}

        df_activos_sim = _df_activos_ticker.copy()
        # Filtro robusto: aceita Ação, ACÇÃO, Acao, etc.
        if not df_activos_sim.empty:
            acoes_sim = df_activos_sim[
                df_activos_sim["tipo"].str.upper().str.replace("Ç","C").str.replace("Ã","A").str.contains("A", na=False)
            ].copy()
        else:
            acoes_sim = pd.DataFrame()

        aba_broker, aba_carteira, aba_ordens, aba_compostos = st.tabs(
            ["📊 Mercado", "💼 Carteira", "🧾 Ordens", "📈 Juros Compostos"])

        import html as _html

        # Estilo "home broker" claro, nas cores do Clube (bordeaux / cinzento avermelhado) — só nesta página
        render_html("""<style>
    .bfa-wrap{background:#FFFFFF;border:1px solid #ECDEE3;border-radius:8px;overflow-x:auto;margin-bottom:12px;}
    .bfa-tbl{width:100%;border-collapse:collapse;font-size:0.8rem;color:#1A1A2E;}
    .bfa-tbl th{color:#7C1F3E;font-weight:700;text-align:right;padding:9px 10px;background:#F4ECEF;border-bottom:2px solid #7C1F3E;font-size:0.7rem;white-space:nowrap;text-transform:uppercase;letter-spacing:0.4px;}
    .bfa-tbl td{padding:10px;text-align:right;border-bottom:1px solid #F0E6EA;background:#FFFFFF;white-space:nowrap;}
    .bfa-tbl tr:nth-child(even) td{background:#FBF8F6;}
    .bfa-tbl tr.sel td{background:#F1E2E7;}
    .bfa-tbl tr.tot td{background:#F4ECEF;font-weight:700;border-top:2px solid #7C1F3E;}
    .bfa-tbl th.l,.bfa-tbl td.l{text-align:left;}
    .bfa-up{color:#0D9488;}.bfa-dn{color:#DC2626;}.bfa-fl{color:#6B7280;}
    .bfa-bar{background:#FBF8F6;border:1px solid #ECDEE3;border-radius:8px;padding:12px 20px;display:flex;gap:34px;flex-wrap:wrap;align-items:flex-end;margin-bottom:12px;}
    .bfa-bar .k{font-size:0.62rem;color:#8A7B80;text-transform:uppercase;letter-spacing:1px;display:block;margin-bottom:3px;}
    .bfa-bar .v{font-size:1.02rem;color:#1A1A2E;font-weight:700;background:#F4ECEF;padding:4px 10px;border-radius:4px;display:inline-block;}
    .bfa-ticket{background:#FBF8F6;border:1px solid #ECDEE3;border-left:4px solid #7C1F3E;border-radius:8px;padding:16px 22px;margin:10px 0;display:flex;gap:40px;flex-wrap:wrap;align-items:center;}
    .bfa-ticket .nome{font-size:1.25rem;font-weight:800;color:#1A1A2E;}
    .bfa-ticket .sub{font-size:0.7rem;color:#8A7B80;margin-top:3px;}
    .bfa-ticket .k{font-size:0.62rem;color:#8A7B80;text-transform:uppercase;display:block;}
    .bfa-ticket .big{font-size:1.7rem;font-weight:800;color:#7C1F3E;}
    .bfa-ticket .m{font-size:1.0rem;font-weight:700;color:#1A1A2E;}
    button[kind="primary"],button[data-testid="stBaseButton-primary"]{background:#6E3B4A !important;border-color:#6E3B4A !important;color:#FFFFFF !important;}
    button[kind="primary"]:hover,button[data-testid="stBaseButton-primary"]:hover{background:#592E3B !important;border-color:#592E3B !important;}
    button[kind="secondary"],button[data-testid="stBaseButton-secondary"]{background:#E9D6DB !important;border-color:#D9BCC4 !important;color:#4A2A33 !important;}
    button[kind="secondary"]:hover,button[data-testid="stBaseButton-secondary"]:hover{background:#DEC4CB !important;}
    </style>""")

        # título → preço / variação actuais (chave = ticker, ou nome se não houver ticker)
        _mapa_preco, _mapa_var = {}, {}
        if not df_activos_sim.empty:
            for _, _r in df_activos_sim.iterrows():
                _k = str(_r.get("ticker") or "").strip().upper() or str(_r["nome"])
                _mapa_preco[_k] = float(_r["preco"])
                _mapa_var[_k]   = float(_r["variacao"])

        # ══════════════════════════════════════════════════════════════
        # ABA 1 — MERCADO + PAINEL DE NEGOCIAÇÃO (estilo BFA Capital Markets)
        # ══════════════════════════════════════════════════════════════
        with aba_broker:
            saldo_caixa = st.session_state["sim_saldo_caixa"]
            cart        = st.session_state["sim_carteira"]
            valor_acoes = sum(d["qtd"] * _mapa_preco.get(k, d["preco_medio"]) for k, d in cart.items())
            patrimonio  = saldo_caixa + valor_acoes
            var_total   = patrimonio - 3_000_000
            cls_vt      = "bfa-up" if var_total >= 0 else "bfa-dn"

            render_html(f"""<div class="bfa-bar">
        <div><span class="k">Conta</span><span class="v">Virtual APPO</span></div>
        <div><span class="k">Titular</span><span class="v">{_html.escape(str(st.session_state.get('conta_nome', '')).upper())}</span></div>
        <div><span class="k">Saldo negociação</span><span class="v">{kz2(saldo_caixa)}</span></div>
        <div><span class="k">Em acções</span><span class="v">{kz2(valor_acoes)}</span></div>
        <div><span class="k">Património total</span><span class="v">{kz2(patrimonio)}</span></div>
        <div><span class="k">Ganho / perda</span><span class="v {cls_vt}">{kz2(var_total)} ({var_total/3_000_000*100:+.2f}%)</span></div>
        </div>""")

            _msg = st.session_state.pop("sim_msg", None)
            if _msg:
                st.success(_msg)

            if acoes_sim.empty:
                st.info("Ainda não existem acções cotadas para negociar.")
            else:
                _lista = []
                for _, row in acoes_sim.iterrows():
                    _tk = str(row.get("ticker") or "").strip().upper()
                    _lista.append({
                        "chave": _tk or str(row["nome"]), "nome": str(row["nome"]), "tk": _tk,
                        "preco": float(row["preco"]), "var": float(row["variacao"]),
                        "act": row.get("actualizado_em"),
                    })
                _rotulos = [x["nome"] + (f"  ({x['tk']})" if x["tk"] else "") for x in _lista]
                if st.session_state.get("sim_sel") not in _rotulos:
                    st.session_state["sim_sel"] = _rotulos[0]
                _sel = st.session_state["sim_sel"]

                _linhas_html = []
                for x, rot in zip(_lista, _rotulos):
                    v    = x["var"]
                    cls  = "bfa-up" if v > 0 else ("bfa-dn" if v < 0 else "bfa-fl")
                    seta = "↑" if v > 0 else ("↓" if v < 0 else "—")
                    qc   = cart.get(x["chave"], {}).get("qtd", 0)
                    sel  = " class='sel'" if rot == _sel else ""
                    _linhas_html.append(
                        f"<tr{sel}><td class='l'><b>{_html.escape(x['nome'].upper())}</b></td>"
                        f"<td class='l'>{_html.escape(x['tk'] or '—')}</td><td class='l'>BODIVA ACÇÕES</td>"
                        f"<td><b>{kz2(x['preco'])}</b></td><td>AOA</td><td>{_fmt_dt(x['act'])}</td>"
                        f"<td class='{cls}'>{pct_bruto(v)} {seta}</td><td>{qc:g}</td></tr>")
                render_html(
                    "<div class='bfa-wrap'><table class='bfa-tbl'><thead><tr>"
                    "<th class='l'>título</th><th class='l'>ticker</th><th class='l'>mercado</th>"
                    "<th>cotação</th><th>moeda</th><th>últ. cotação</th><th>% var. diária</th><th>em carteira</th>"
                    "</tr></thead><tbody>" + "".join(_linhas_html) + "</tbody></table></div>")

                st.selectbox("Título a negociar", _rotulos, key="sim_sel")
                a        = _lista[_rotulos.index(st.session_state["sim_sel"])]
                ent      = cart.get(a["chave"], {})
                qtd_cart = ent.get("qtd", 0)
                cls_a    = "bfa-up" if a["var"] > 0 else ("bfa-dn" if a["var"] < 0 else "bfa-fl")
                pm_txt   = kz2(ent["preco_medio"]) if ent else "—"
                render_html(f"""<div class="bfa-ticket">
            <div><div class="nome">{_html.escape(a['nome'].upper())}</div>
            <div class="sub">{_html.escape(a['tk'] or '—')} &nbsp;|&nbsp; BODIVA ACÇÕES &nbsp;|&nbsp; AOA</div></div>
            <div><span class="k">Cotação</span><span class="big">{kz2(a['preco'])}</span></div>
            <div><span class="k">Variação</span><span class="m {cls_a}">{pct_bruto(a['var'])}</span></div>
            <div><span class="k">Em carteira</span><span class="m">{qtd_cart:g}</span></div>
            <div><span class="k">Preço médio</span><span class="m">{pm_txt}</span></div>
            </div>""")

                # confirmação de ordem pendente
                pend = st.session_state.get("sim_ordem_pend")
                if pend:
                    _tp = pend["qtd"] * pend["preco"]
                    st.info(f"**Confirmar ordem de {'COMPRA' if pend['op'] == 'C' else 'VENDA'}** — "
                            f"{pend['qtd']:g} × {pend['nome']} a {kz2(pend['preco'])} = **{kz2(_tp)} Kz**")
                    cc1, cc2, _ = st.columns([1, 1, 2])
                    if cc1.button("✅ Confirmar ordem", key="sim_conf", type="primary", use_container_width=True):
                        ch, nm, tkp, q, p = pend["chave"], pend["nome"], pend["tk"], pend["qtd"], pend["preco"]
                        valor = q * p
                        oper  = None
                        if pend["op"] == "C":
                            if st.session_state["sim_saldo_caixa"] >= valor:
                                st.session_state["sim_saldo_caixa"] -= valor
                                if ch in cart:
                                    tq = cart[ch]["qtd"] + q
                                    tc = cart[ch]["qtd"] * cart[ch]["preco_medio"] + valor
                                    cart[ch] = {"qtd": tq, "preco_medio": tc / tq, "nome": nm}
                                else:
                                    cart[ch] = {"qtd": q, "preco_medio": p, "nome": nm}
                                oper = "✅ COMPRA"
                        else:
                            if cart.get(ch, {}).get("qtd", 0) >= q:
                                st.session_state["sim_saldo_caixa"] += valor
                                cart[ch]["qtd"] -= q
                                if cart[ch]["qtd"] <= 0:
                                    del cart[ch]
                                oper = "🔴 VENDA"
                        if oper is None:
                            st.session_state.pop("sim_ordem_pend", None)
                            st.session_state["sim_msg"] = "Ordem não executada: saldo ou quantidade insuficiente."
                            st.rerun()
                        else:
                            st.session_state["sim_historico"].insert(0, {
                                "Operação": oper, "Ticker": tkp or nm, "Qtd": q, "Preço Unit.": p, "Total": valor})
                            guardar_saldo_simulador(_email_sim, st.session_state["sim_saldo_caixa"])
                            guardar_posicao_simulador(_email_sim, ch, cart.get(ch))
                            registar_operacao_simulador(_email_sim, oper, tkp or nm, q, p, valor)
                            st.session_state.pop("sim_ordem_pend", None)
                            st.session_state["sim_msg"] = f"{oper} executada: {q:g} × {nm} a {kz2(p)} Kz."
                            st.rerun()
                    if cc2.button("✖ Cancelar", key="sim_canc", use_container_width=True):
                        st.session_state.pop("sim_ordem_pend", None)
                        st.rerun()

                c1, c2, c3 = st.columns(3)
                qtd_op = int(c1.number_input("Quantidade", min_value=1, value=1, step=1, key="sim_qtd_op"))
                total  = qtd_op * a["preco"]
                c2.metric("Preço (cotação de mercado)", kz2(a["preco"]))
                c3.metric("Valor da ordem", kz2(total))
                b1, b2, _ = st.columns([1, 1, 2])
                comprar = b1.button("＋ Comprar", key="sim_btn_buy", type="primary", use_container_width=True)
                vender  = b2.button("－ Vender", key="sim_btn_sell", type="secondary", use_container_width=True,
                                    disabled=(qtd_cart < qtd_op))
                if comprar or vender:
                    if comprar and saldo_caixa < total:
                        st.warning(f"Saldo insuficiente — necessitas {kz2(total)} Kz, tens {kz2(saldo_caixa)} Kz.")
                    else:
                        st.session_state["sim_ordem_pend"] = {
                            "op": "C" if comprar else "V", "chave": a["chave"], "nome": a["nome"],
                            "tk": a["tk"], "qtd": qtd_op, "preco": a["preco"]}
                        st.rerun()

                aviso_discreto("Ambiente de treino pedagógico com dados de mercado de referência, actualizados pelo administrador (não em tempo real). "
                               "As simulações servem para estudo de cenários e não constituem recomendação de compra/venda.")

        # ══════════════════════════════════════════════════════════════
        # ABA 2 — CARTEIRA (estilo BFA Capital Markets)
        # ══════════════════════════════════════════════════════════════
        with aba_carteira:
            cart        = st.session_state["sim_carteira"]
            saldo_caixa = st.session_state["sim_saldo_caixa"]
            if not cart:
                st.info("A tua carteira virtual está vazia. Vai ao Mercado e compra as tuas primeiras acções!")
            else:
                _vals      = {k: d["qtd"] * _mapa_preco.get(k, d["preco_medio"]) for k, d in cart.items()}
                _tot_acoes = sum(_vals.values())
                _tot_aq    = sum(d["qtd"] * d["preco_medio"] for d in cart.values())
                _linhas_c  = []
                for k, d in cart.items():
                    p_act  = _mapa_preco.get(k, d["preco_medio"])
                    var_d  = _mapa_var.get(k, 0.0)
                    v_act  = _vals[k]
                    v_aq   = d["qtd"] * d["preco_medio"]
                    pl     = v_act - v_aq
                    cls_pl = "bfa-up" if pl > 0 else ("bfa-dn" if pl < 0 else "bfa-fl")
                    cls_vd = "bfa-up" if var_d > 0 else ("bfa-dn" if var_d < 0 else "bfa-fl")
                    peso   = (v_act / _tot_acoes * 100) if _tot_acoes else 0
                    _linhas_c.append(
                        f"<tr><td class='l'><b>{_html.escape(str(d['nome']).upper())}</b></td><td class='l'>{_html.escape(k)}</td>"
                        f"<td class='l'>BODIVA ACÇÕES</td><td>{d['qtd']:g}</td><td>{kz2(p_act)}</td><td>AOA</td>"
                        f"<td>{kz2(v_act)}</td><td>{kz2(v_aq)}</td><td class='{cls_pl}'>{kz2(pl)}</td>"
                        f"<td class='{cls_vd}'>{pct_bruto(var_d)}</td><td>{peso:.2f}%</td></tr>")
                _pl_t   = _tot_acoes - _tot_aq
                cls_plt = "bfa-up" if _pl_t > 0 else ("bfa-dn" if _pl_t < 0 else "bfa-fl")
                _linhas_c.append(
                    f"<tr class='tot'><td class='l' colspan='6'>TOTAL</td><td>{kz2(_tot_acoes)}</td>"
                    f"<td>{kz2(_tot_aq)}</td><td class='{cls_plt}'>{kz2(_pl_t)}</td><td></td><td>100,00%</td></tr>")
                render_html(
                    "<div class='bfa-wrap'><table class='bfa-tbl'><thead><tr>"
                    "<th class='l'>título</th><th class='l'>ticker</th><th class='l'>mercado</th>"
                    "<th>quantidade</th><th>cotação</th><th>moeda</th><th>valor actual</th><th>aquisição</th>"
                    "<th>valias potenciais</th><th>var. diária</th><th>% carteira</th>"
                    "</tr></thead><tbody>" + "".join(_linhas_c) + "</tbody></table></div>")

                col_r1, col_r2, col_r3, col_r4 = st.columns(4)
                col_r1.metric("Saldo negociação", kz2(saldo_caixa))
                col_r2.metric("Valor em acções", kz2(_tot_acoes))
                col_r3.metric("Património total", kz2(saldo_caixa + _tot_acoes))
                var_t = saldo_caixa + _tot_acoes - 3_000_000
                col_r4.metric("Ganho/Perda total", kz2(var_t), delta=f"{var_t/3_000_000*100:+.2f}%")
                nota_indicador("<b>Valias potenciais</b> = diferença entre o valor actual e o que pagaste (ganho/perda ainda não realizado).")

        # ══════════════════════════════════════════════════════════════
        # ABA 3 — ORDENS (histórico) + reiniciar
        # ══════════════════════════════════════════════════════════════
        with aba_ordens:
            st.subheader("📜 Histórico de Ordens")
            if st.session_state["sim_historico"]:
                df_h = pd.DataFrame(st.session_state["sim_historico"])
                for _c in ("Preço Unit.", "Total"):
                    if _c in df_h.columns:
                        df_h[_c] = df_h[_c].apply(lambda v: kz2(v) if isinstance(v, (int, float)) else v)
                st.dataframe(df_h, hide_index=True)
            else:
                st.info("Ainda não executaste nenhuma ordem.")

            if st.button("🔄 Reiniciar carteira virtual (voltar a 3 000 000 Kz)", type="secondary"):
                reiniciar_simulador_db(_email_sim)
                st.session_state["sim_carteira"] = {}
                st.session_state["sim_saldo_caixa"] = 3_000_000.0
                st.session_state["sim_historico"] = []
                st.session_state.pop("sim_ordem_pend", None)
                for k in list(st.session_state.keys()):
                    if k.startswith("sim_qtd_") and k != "sim_qtd_op":
                        del st.session_state[k]
                st.rerun()

        # ══════════════════════════════════════════════════════════════
        # ABA 4 — JUROS COMPOSTOS
        # ══════════════════════════════════════════════════════════════
        with aba_compostos:
            st.subheader("📈 Simulador de Juros Compostos")
            col1, col2 = st.columns(2)
            valor_inicial  = col1.number_input("Valor inicial (Kz)", min_value=0.0, value=100000.0, step=10000.0)
            contrib_mensal = col2.number_input("Contribuição mensal (Kz)", min_value=0.0, value=20000.0, step=5000.0)
            col3, col4, col5 = st.columns(3)
            taxa_anual   = col3.slider("Taxa de retorno anual esperada (%)", 0.0, 40.0, 12.0, 0.5)
            anos         = col4.slider("Prazo (anos)", 1, 30, 10)
            inflacao_sim = col5.slider("Inflação anual assumida (%)", 0.0, 40.0, 13.5, 0.5)

            taxa_m   = (1 + taxa_anual   / 100) ** (1 / 12) - 1
            infl_m   = (1 + inflacao_sim / 100) ** (1 / 12) - 1
            saldo_c  = valor_inicial
            total_inv= valor_inicial
            pontos   = []
            for mes in range(1, anos * 12 + 1):
                saldo_c   = saldo_c * (1 + taxa_m) + contrib_mensal
                total_inv += contrib_mensal
                if mes % 12 == 0:
                    pontos.append({
                        "Ano": mes // 12,
                        "Saldo Nominal": saldo_c,
                        "Total Investido": total_inv,
                        "Saldo Real": saldo_c / ((1 + infl_m) ** mes),
                    })

            df_sim = pd.DataFrame(pontos).set_index("Ano")
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Saldo Final (nominal)", kz(saldo_c))
            col_b.metric("Total Investido",       kz(total_inv))
            col_c.metric("Juros Compostos",       kz(saldo_c - total_inv))
            fx_barras(df_sim[["Saldo Nominal", "Total Investido"]])
            saldo_real_f = df_sim["Saldo Real"].iloc[-1]
            st.caption(f"Saldo final em poder de compra de hoje (inflação {inflacao_sim:.1f}%/ano): {kz(saldo_real_f)}")
            nota_indicador(f"Com inflação de {inflacao_sim:.1f}%/ano, o teu saldo nominal de {kz(saldo_c)} equivale apenas a {kz(saldo_real_f)} em poder de compra actual.")
            aviso_discreto("Ambiente de treino pedagógico. As simulações servem para estudo de cenários e não constituem recomendação de compra/venda.")
            botoes_partilha(f"Simulei {kz(valor_inicial)} + {kz(contrib_mensal)}/mês durante {anos} anos a {taxa_anual:.1f}%/ano = {kz(saldo_c)} — Clube de Investimento APPO")

    # =========================================================
    # PÁGINA: REGRA 50/30/20
    # =========================================================
    elif pagina == "🧮 Princípio 50/30/20":
        tx = t()
        hero("🧮 " + tx["nav_map"]["🧮 Princípio 50/30/20"].replace("🧮 ", ""), tx["r50_hero_sub"], "📐 " + tx["r50_rendimento"])
        aviso_discreto("O princípio 50/30/20 é uma referência educativa, não uma regra adequada a todas as pessoas. Para medir o seu ponto de partida, faça o diagnóstico em Capacidade Financeira.")
        tab_regra, tab_orc = st.tabs(["🧮 Princípio 50/30/20", "📒 Meu Orçamento Mensal"])

        with tab_regra:
            rendimento = st.number_input(tx["r50_rendimento"], min_value=0.0, step=5000.0, value=250000.0, format="%.2f")
            alvo_consumo, alvo_inv, alvo_entes = rendimento * 0.50, rendimento * 0.30, rendimento * 0.20

            st.subheader(tx["r50_alocacao"])
            col1, col2, col3 = st.columns(3)
            col1.metric(tx["r50_consumo"],       kz(alvo_consumo))
            col2.metric(tx["r50_investimento"],  kz(alvo_inv))
            col3.metric(tx["r50_entesouramento"],kz(alvo_entes))
            fx_barras(pd.DataFrame({"Categoria": [tx["r50_consumo"], tx["r50_investimento"], tx["r50_entesouramento"]],
                                       "Valor recomendado (Kz)": [alvo_consumo, alvo_inv, alvo_entes]}).set_index("Categoria"))

            st.divider()
            st.subheader(tx["r50_comparar_titulo"])
            with st.form("form_orcamento_real"):
                col_a, col_b, col_c = st.columns(3)
                real_consumo      = col_a.number_input(tx["r50_real_consumo"],       min_value=0.0, step=1000.0)
                real_investimento = col_b.number_input(tx["r50_real_investimento"],  min_value=0.0, step=1000.0)
                real_entes        = col_c.number_input(tx["r50_real_entesouramento"],min_value=0.0, step=1000.0)
                comparar = st.form_submit_button(tx["r50_comparar_btn"])
            if comparar:
                st.markdown(tx["r50_resultado"])
                col1, col2, col3 = st.columns(3)
                col1.metric(tx["r50_consumo"],       kz(real_consumo),      delta=kz(real_consumo      - alvo_consumo), delta_color="inverse")
                col2.metric(tx["r50_investimento"],  kz(real_investimento), delta=kz(real_investimento - alvo_inv),     delta_color="normal")
                col3.metric(tx["r50_entesouramento"],kz(real_entes),        delta=kz(real_entes        - alvo_entes),   delta_color="normal")
                if real_entes < alvo_entes:
                    st.warning(tx["r50_aviso"])
                else:
                    st.success(tx["r50_sucesso"])

        with tab_orc:
            _email_orc = st.session_state.get("conta_email", "")
            st.subheader("📒 Orçamento mensal pessoal ou familiar")
            st.caption("Preencha as receitas e os gastos do mês (em kwanzas inteiros). A app compara automaticamente "
                       "com a Princípio 50/30/20 e mostra quanto está a poupar e a investir. O orçamento fica gravado na sua conta.")

            if st.session_state.get("orc_carregado_para") != _email_orc:
                _d0 = obter_orcamento(_email_orc)
                st.session_state["orc_rec_base"]  = pd.DataFrame(_d0["receitas"], columns=["Descrição", "Valor (Kz)"])
                st.session_state["orc_desp_base"] = pd.DataFrame(_d0["despesas"], columns=["Categoria", "Descrição", "Valor (Kz)"])
                st.session_state["orc_carregado_para"] = _email_orc
            _ver = st.session_state.get("orc_versao", 0)

            _cfg_valor = st.column_config.NumberColumn("Valor (Kz)", min_value=0, step=100, format="%d")
            st.markdown("**1. Receitas do mês**")
            df_rec = st.data_editor(
                st.session_state["orc_rec_base"], num_rows="dynamic", key=f"orc_rec_{_ver}", hide_index=True,
                column_config={"Descrição": st.column_config.TextColumn("Descrição"), "Valor (Kz)": _cfg_valor})
            st.markdown("**2. Despesas e poupança do mês** — abre cada grupo e detalha o que vais comprar ou pagar")
            _bd = st.session_state["orc_desp_base"].copy()
            _bd.loc[~_bd["Categoria"].isin(ORC_CATEGORIAS), "Categoria"] = ORC_CATEGORIAS[0]
            _rec_prev = float(sum(_num_seguro(v) for v in df_rec["Valor (Kz)"]))
            _partes = []
            for _gi, (_cat, _ico, _meta, _sug) in enumerate(ORC_GRUPOS):
                _b = _bd[_bd["Categoria"] == _cat][["Descrição", "Valor (Kz)"]].reset_index(drop=True)
                with st.expander(f"{_ico} {_cat}"):
                    st.caption(_sug)
                    _e = st.data_editor(_b, num_rows="dynamic", key=f"orc_desp_{_gi}_{_ver}", hide_index=True,
                                        column_config={"Descrição": st.column_config.TextColumn("O que vais comprar / pagar"), "Valor (Kz)": _cfg_valor})
                    _sub = float(sum(_num_seguro(v) for v in _e["Valor (Kz)"]))
                    if _rec_prev > 0:
                        st.progress(min(_sub / (_rec_prev * _meta), 1.0))
                        st.caption(f"Subtotal {kz(_sub)} · meta {_meta * 100:.0f}% das receitas = {kz(_rec_prev * _meta)}")
                    else:
                        st.caption(f"Subtotal {kz(_sub)}")
                _e = _e.copy()
                _e["Categoria"] = _cat
                _partes.append(_e[["Categoria", "Descrição", "Valor (Kz)"]])
            df_desp = pd.concat(_partes, ignore_index=True)

            rec_total = float(sum(_num_seguro(v) for v in df_rec["Valor (Kz)"]))
            _dd = df_desp.copy()
            _dd["_v"] = _dd["Valor (Kz)"].apply(_num_seguro)
            tot_cat = {c: float(_dd.loc[_dd["Categoria"] == c, "_v"].sum()) for c in ORC_CATEGORIAS}
            sem_cat = int(((_dd["Categoria"].isna()) & (_dd["_v"] > 0)).sum())
            desp_total = sum(tot_cat.values())
            saldo_livre = rec_total - desp_total
            poup_total = tot_cat[ORC_CATEGORIAS[1]] + tot_cat[ORC_CATEGORIAS[2]]

            st.divider()
            st.markdown("**3. Resultado**")
            if sem_cat:
                st.warning(f"{sem_cat} linha(s) com valor mas sem categoria foram ignoradas no cálculo.")
            if rec_total <= 0:
                st.info("Introduza as suas receitas para ver a comparação com a Princípio 50/30/20.")
            else:
                alvos = {ORC_CATEGORIAS[0]: rec_total * 0.50, ORC_CATEGORIAS[1]: rec_total * 0.30, ORC_CATEGORIAS[2]: rec_total * 0.20}
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Receitas", kz(rec_total))
                k2.metric("Despesas + poupança planeadas", kz(desp_total))
                k3.metric("Saldo por alocar", kz(saldo_livre))
                k4.metric("Poupado + investido", f"{poup_total / rec_total * 100:.0f}%", help="Investimento + Entesouramento, em % das receitas (meta: 50%)")

                c1, c2, c3 = st.columns(3)
                for col, cat, inv in ((c1, ORC_CATEGORIAS[0], "inverse"), (c2, ORC_CATEGORIAS[1], "normal"), (c3, ORC_CATEGORIAS[2], "normal")):
                    col.metric(f"{cat}", kz(tot_cat[cat]), delta=f"{kz(tot_cat[cat] - alvos[cat])} face à meta ({kz(alvos[cat])})", delta_color=inv)
                fx_barras(pd.DataFrame(
                    {"O seu orçamento (Kz)": [tot_cat[c] for c in ORC_CATEGORIAS], "Recomendado 50/30/20 (Kz)": [alvos[c] for c in ORC_CATEGORIAS]},
                    index=ORC_CATEGORIAS))

                if desp_total > rec_total:
                    st.error(f"Os gastos e a poupança planeados superam as receitas em {kz(-saldo_livre)}. Reduza o consumo antes de pensar em investir.")
                else:
                    if tot_cat[ORC_CATEGORIAS[0]] > alvos[ORC_CATEGORIAS[0]]:
                        st.warning(f"O consumo ({tot_cat[ORC_CATEGORIAS[0]] / rec_total * 100:.0f}% das receitas) está acima dos 50% recomendados — "
                                   f"tente reduzir cerca de {kz(tot_cat[ORC_CATEGORIAS[0]] - alvos[ORC_CATEGORIAS[0]])}.")
                    if tot_cat[ORC_CATEGORIAS[1]] < alvos[ORC_CATEGORIAS[1]]:
                        st.info(f"Para chegar aos 30% de investimento faltam {kz(alvos[ORC_CATEGORIAS[1]] - tot_cat[ORC_CATEGORIAS[1]])} por mês.")
                    if tot_cat[ORC_CATEGORIAS[2]] < alvos[ORC_CATEGORIAS[2]]:
                        st.info(f"Para chegar aos 20% de entesouramento (reserva) faltam {kz(alvos[ORC_CATEGORIAS[2]] - tot_cat[ORC_CATEGORIAS[2]])} por mês.")
                    if (tot_cat[ORC_CATEGORIAS[0]] <= alvos[ORC_CATEGORIAS[0]] and tot_cat[ORC_CATEGORIAS[1]] >= alvos[ORC_CATEGORIAS[1]]
                            and tot_cat[ORC_CATEGORIAS[2]] >= alvos[ORC_CATEGORIAS[2]]):
                        st.success("Parabéns — o seu orçamento cumpre a Princípio 50/30/20.")
                    if saldo_livre > 0:
                        st.info(f"Tem {kz(saldo_livre)} ainda por alocar: distribua-os pelas linhas de investimento e entesouramento.")
                if poup_total > 0:
                    st.caption(f"Ao ritmo actual, poupa e investe {kz(poup_total)} por mês: cerca de {kz(poup_total * 12)} em 12 meses "
                               "(sem juros). Veja o efeito dos juros compostos no Simulador de Investimento.")

            b1, b2, b3 = st.columns(3)
            if b1.button("💾 Guardar orçamento", type="primary", key="orc_guardar", use_container_width=True):
                def _recs(df):
                    return df.astype(object).where(df.notna(), None).to_dict("records")
                guardar_orcamento(_email_orc, {"receitas": _recs(df_rec), "despesas": _recs(df_desp)})
                # a base da sessão passa a ser o que ficou gravado; assim, ao sair da página e voltar,
                # os dados continuam lá. O editor recomeça com uma chave nova a partir dessa base.
                st.session_state["orc_rec_base"]  = df_rec.reset_index(drop=True).copy()
                st.session_state["orc_desp_base"] = df_desp.reset_index(drop=True).copy()
                st.session_state["orc_versao"] = _ver + 1
                st.session_state["orc_msg"] = "Orçamento guardado na sua conta."
                st.rerun()
            if b2.button("↺ Repor modelo inicial", key="orc_repor", use_container_width=True):
                _m = orcamento_modelo_inicial()
                st.session_state["orc_rec_base"]  = pd.DataFrame(_m["receitas"], columns=["Descrição", "Valor (Kz)"])
                st.session_state["orc_desp_base"] = pd.DataFrame(_m["despesas"], columns=["Categoria", "Descrição", "Valor (Kz)"])
                st.session_state["orc_versao"] = _ver + 1
                st.rerun()
            _xl_orc = _xlsx_seguro(lambda: gerar_xlsx_orcamento(df_rec, df_desp, ORC_CATEGORIAS))
            if _xl_orc:
                b3.download_button("⬇️ Descarregar Excel", data=_xl_orc, file_name="orcamento_mensal_appo.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   use_container_width=True, key="dl_orc_xlsx")
            else:
                _csv = pd.concat([
                    df_rec.assign(Tipo="Receita", Categoria=""),
                    df_desp.assign(Tipo="Despesa"),
                ], ignore_index=True)[["Tipo", "Categoria", "Descrição", "Valor (Kz)"]].to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")
                b3.download_button("⬇️ Descarregar (CSV)", data=_csv, file_name="orcamento_mensal.csv", mime="text/csv", use_container_width=True)
            _om = st.session_state.pop("orc_msg", None)
            if _om:
                st.success(_om)


    # =========================================================
    # PÁGINA: BIBLIOTECA EDUCATIVA
    # =========================================================
    elif pagina == "📚 Biblioteca Educativa":
        tx = t()
        hero("📚 " + tx["nav_map"]["📚 Biblioteca Educativa"].replace("📚 ", ""), tx["bib_hero_sub"])
        df_artigos = obter_artigos()
        df_docs_bib = obter_documentos("biblioteca")
        if not df_docs_bib.empty:
            st.subheader("📄 Publicações em PDF")
            for _, doc in df_docs_bib.iterrows():
                with st.expander(f"{ICONES_CATEGORIA.get(doc['categoria'], '📄')} {doc['titulo']}"):
                    st.caption(f"{doc['categoria']} · {tx['bib_publicado']} {doc['criado_em']} · {doc['tamanho'] / 1048576:.1f} MB")
                    if str(doc["descricao"] or "").strip():
                        st.write(doc["descricao"])
                    bloco_documento_pdf(int(doc["id"]), doc["nome_ficheiro"], f"bib_{int(doc['id'])}")
            if not df_artigos.empty:
                st.subheader("📝 Artigos")
        if df_artigos.empty:
            if df_docs_bib.empty:
                st.info(tx["bib_sem_artigos"])
        else:
            todas_label = tx["bib_todas"]
            categorias  = [todas_label] + sorted(df_artigos["categoria"].unique().tolist())
            filtro      = st.selectbox(tx["bib_filtrar"], categorias)
            filtro_bd   = None if filtro == todas_label else filtro
            _df_f = obter_artigos(filtro_bd)
            biblioteca_por_nivel(_df_f, tx)

    # =========================================================
    # PÁGINA: CAPACIDADE FINANCEIRA
    # =========================================================
    elif pagina == "🧭 Perfil de Investidor":
        hero("🧭 Perfil de Investidor", "Descobre o teu perfil de risco e o portal que melhor se ajusta ao teu momento", badge="🇦🇴 Kwanzas (Kz)")
        pagina_perfil_investidor()

    elif pagina == "🧠 Capacidade Financeira":
        hero("🧠 Capacidade Financeira", "Diagnóstico, treino e ferramentas para decidir com autonomia", badge="🇦🇴 Kwanzas (Kz)")
        pagina_capacidade_financeira(True)

    # =========================================================
    # PÁGINA: EDUCAÇÃO & SERVIÇOS
    # =========================================================
    elif pagina == "🎓 Educação & Serviços":
        hero("🎓 Educação & Serviços", "Formação, materiais e ferramentas educativas do APPO", badge="🇦🇴 Educação financeira · Kwanzas (Kz)")
        pagina_educacao_servicos()

    # =========================================================
    # PÁGINA: MANIFESTAÇÃO DE INTERESSE (antiga «Adesão de Sócios»; a chave interna mantém-se)
    # =========================================================
    elif pagina == "🧾 Adesão de Sócios":
        tx = t()
        hero("🧾 " + tx["nav_map"]["🧾 Adesão de Sócios"].replace("🧾 ", ""), "Regista o teu interesse numa futura participação. Não é uma admissão.", badge="🇦🇴 APPO")
        pagina_manifestacao_interesse()

    # =========================================================
    # PÁGINA: SOBRE NÓS & ESTATUTOS
    # =========================================================
    elif pagina == "ℹ️ Sobre Nós & Estatutos":
        tx = t()
        hero("ℹ️ " + tx["nav_map"]["ℹ️ Sobre Nós & Estatutos"].replace("ℹ️ ", ""), tx["sobre_hero_sub"])
        pagina_sobre_nos(tx)

    # =========================================================
    # PÁGINA: PAINEL DO ADMINISTRADOR (mantém-se em PT)
    # =========================================================
    elif pagina == "🔐 Painel do Administrador":
        hero("Painel do Administrador", "Gestão de conteúdo, cotações, movimentos, sócios, contas e avaliações")

        aba_resumo, aba_unidades, aba_activos, aba_carteira_real, aba_aval, aba_movimentos, aba_biblioteca, aba_socios, aba_contas, aba_seguranca, aba_edu_serv, aba_despesas, aba_site = st.tabs(
            ["Resumo Patrimonial", "Unidades (VUP)", "Cotações & Activos", "Carteira Real", "Avaliação", "Movimentos", "Biblioteca", "Sócios", "Contas", "Segurança", "Educação & Serviços", "Despesas do grupo", "Site & Sobre Nós"])
        with aba_edu_serv:
            painel_educacao_servicos_admin()
        with aba_despesas:
            painel_despesas_admin()
        with aba_site:
            painel_site_admin()

        with aba_resumo:
            st.subheader("Editar Resumo Patrimonial")
            st.caption("O Capital Realizado deve ser sempre ≤ ao Capital Subscrito.")
            resumo = obter_resumo_patrimonial()
            with st.form("form_editar_resumo"):
                novo_subscrito  = st.number_input("Capital Subscrito (Kz)",  min_value=0.0, step=10000.0, value=float(resumo["capital_subscrito"]))
                novo_realizado  = st.number_input("Capital Realizado (Kz)",  min_value=0.0, step=10000.0, value=float(resumo["capital_realizado"]))
                novo_invest     = st.number_input("Investimentos (Kz)",      min_value=0.0, step=10000.0, value=float(resumo["investimentos"]))
                novas_reservas  = st.number_input("Reservas (Kz)",           min_value=0.0, step=10000.0, value=float(resumo["reservas"]))
                guardar_resumo  = st.form_submit_button("Guardar alterações")
            if guardar_resumo:
                if novo_realizado > novo_subscrito:
                    st.error("O Capital Realizado não pode ser maior do que o Capital Subscrito.")
                else:
                    actualizar_resumo_patrimonial(novo_subscrito, novo_realizado, novo_invest, novas_reservas)
                    st.success("Resumo patrimonial actualizado e novo ponto de histórico registado.")
                    st.rerun()

            st.divider()
            st.subheader("Histórico de património (alimenta os gráficos)")
            st.caption("Cada vez que guarda o resumo acima, regista-se um ponto com o Capital Realizado desse momento. "
                       "Elimine aqui os pontos de teste ou com valores errados.")
            _hist_adm = obter_historico_patrimonio_admin()
            if _hist_adm.empty:
                st.info("Ainda não há pontos de histórico.")
            else:
                for _, _h in _hist_adm.iterrows():
                    hc1, hc2, hc3 = st.columns([2, 3, 1])
                    hc1.write(str(_h["registado_em"])[:16])
                    hc2.write(f"Capital realizado: {kz(_h['capital_social'])}")
                    if hc3.button("Eliminar", key=f"del_hist_{int(_h['id'])}"):
                        eliminar_registo_historico(int(_h["id"]))
                        st.rerun()

        with aba_unidades:
            exigir_admin()
            st.subheader("📐 Património líquido, unidades e VUP")
            st.info("O VUP é o património líquido validado dividido pelas unidades em circulação. Ganhos e perdas alteram o valor das unidades. "
                    "Emissões e cancelamentos alteram a sua quantidade. Transferências entre participantes alteram a titularidade, não a quantidade total.")
            _msg_c = st.session_state.pop("cotas_msg", None)
            if _msg_c:
                st.success(_msg_c)
            _cfg = obter_cotas_config()
            _vi = obter_vup_info()
            _bal = _vi["balanco"]

            # ---------- A. Estado actual ----------
            _cor = {"Não calculado": "🔴", "Provisório": "🟠", "Validado": "🟢"}[_vi["estado"]]
            st.markdown(f"**Estado do indicador:** {_cor} {_vi['estado']}")
            for _mot in _vi["motivos"]:
                st.warning(_mot)
            if _vi["estado"] == "Provisório":
                st.caption("Provisório: o balanço mais recente e/ou a base de unidades ainda não foram validados. Não apresente este valor como certeza contabilística.")
            u1, u2, u3, u4 = st.columns(4)
            u1.metric("Património líquido", kz(_vi["vlg"]) if _vi["estado"] != "Não calculado" else "—")
            u2.metric("Unidades validadas", f"{_vi['unidades']:,.6f}".replace(",", " "))
            u3.metric("VUP", (kz2(_vi["vup"]) + " Kz") if _vi["estado"] != "Não calculado" else "—")
            _rent_u = (_vi["vup"] / _vi["vup_base"] - 1) * 100 if _vi["vup_base"] > 0 and _vi["estado"] != "Não calculado" else None
            u4.metric(f"Variação desde a data-base ({_vi['data_base']:%d/%m/%Y})" if _vi["data_base"] else "Variação desde a data-base",
                      pct_bruto(_rent_u) if _rent_u is not None else "—")
            st.caption("A variação conta a partir da data-base das unidades; não representa o desempenho desde 2024 nem esconde as perdas históricas (ver registo histórico privado, abaixo).")
            if _vi["unidades_por_rever"] > 0:
                st.warning(f"Há {_vi['unidades_por_rever']:,.4f} unidades 'Por rever' (lançadas antes desta revisão). Não entram no VUP até serem validadas, corrigidas ou anuladas (secção 5).".replace(",", " "))
            _dp = _vi["data_precos"]
            st.caption(f"Investimentos a preços de avaliação da app: {kz(_vi['valor_carteira'])} (data dos preços: {_dp:%d/%m/%Y %H:%M}; preços inseridos pelo administrador, não são tempo real)."
                       if _dp else f"Investimentos a preços de avaliação da app: {kz(_vi['valor_carteira'])} (sem data de actualização registada).")

            # ---------- B. Balanço ----------
            with st.expander("1. Balanço: dinheiro disponível, outros activos e passivos", expanded=_bal is None):
                if _bal:
                    st.write(f"**Último retrato:** {_bal[1]:%d/%m/%Y}  ·  dinheiro disponível {kz2(_bal[2])} Kz  ·  outros activos {kz2(_bal[3])} Kz  ·  "
                             f"passivos {kz2(_bal[4])} Kz  ·  estado: **{_bal[7]}**")
                    st.caption(f"Fonte: {_bal[5] or '—'}  ·  Titularidade: {_bal[6] or '—'}  ·  Origem: {_bal[8] or '—'}")
                    if _bal[7] != "Validado":
                        if st.button("Validar este retrato", key="validar_balanco_btn"):
                            validar_balanco(int(_bal[0]), "Validado pelo administrador")
                            st.session_state["cotas_msg"] = "Balanço validado."
                            st.rerun()
                st.caption("Os retratos não se editam: cada actualização cria um novo, e os anteriores ficam guardados. Dinheiro disponível: o que está efectivamente "
                           "disponível (extracto do homebroker/banco). Ordens vivas podem imobilizar saldo; ordens não executadas não são posições. "
                           "O capital realizado e as 'reservas' do Resumo Patrimonial não entram neste cálculo.")
                with st.form("form_balanco"):
                    b1, b2 = st.columns(2)
                    _b_data = b1.date_input("Data do retrato", value=datetime.now().date())
                    _b_din = b2.text_input("Dinheiro disponível (Kz)", value="")
                    b3, b4 = st.columns(2)
                    _b_out = b3.text_input("Outros activos e direitos comprovados (Kz)", value="0")
                    _b_pas = b4.text_input("Passivos e obrigações (Kz)", value="0")
                    _b_fonte = st.text_input("Fonte (ex.: extracto do homebroker de 05/10/2026)")
                    _b_tit = st.text_input("Titularidade da conta/activos (ex.: conta pessoal do administrador; acordo documentado?)")
                    _b_val = st.checkbox("Marcar já como Validado (confirmei os valores com documentos)")
                    _b_ok = st.form_submit_button("Registar novo retrato")
                if _b_ok:
                    _din, _out, _pas = _numero_flex(_b_din), _numero_flex(_b_out), _numero_flex(_b_pas)
                    if _din is None or _out is None or _pas is None or min(_din, _out, _pas) < 0:
                        st.error("Indique números válidos (≥ 0) nos três campos, por exemplo 2014073,93.")
                    elif not _b_fonte.strip():
                        st.error("Indique a fonte do retrato.")
                    else:
                        registar_balanco(_b_data, _din, _out, _pas, _b_fonte.strip(), _b_tit.strip(), "Validado" if _b_val else "Provisório")
                        registar_vup_hoje()
                        st.session_state["cotas_msg"] = "Retrato registado."
                        st.rerun()

            # ---------- C. Regras ----------
            with st.expander("2. Regras (propostas pendentes de formalização)"):
                st.caption("Estas regras são propostas, não regras comprovadas dos Estatutos, enquanto não houver deliberação documentada. "
                           "100 unidades não equivalem necessariamente a 10 000 000 Kz quando o VUP varia. Os direitos de governação são separados da participação económica: "
                           "todas as unidades valem o mesmo dinheiro; o peso do voto das unidades Fundadoras é uma proposta (1 = sem privilégio).")
                with st.form("form_cotas_cfg"):
                    fc1, fc2, fc3, fc4 = st.columns(4)
                    _n_c = fc1.number_input("Valor nominal de referência (Kz)", min_value=1000.0, value=float(_cfg["valor_nominal"]), step=1000.0)
                    _l_c = fc2.number_input("Limite de unidades (0 = sem limite)", min_value=0.0, value=float(_cfg["limite_cotas"]), step=10.0)
                    _m_c = fc3.number_input("Entrada mínima (Kz)", min_value=0.0, value=float(_cfg["entrada_minima"]), step=10000.0)
                    _p_c = fc4.number_input("Votos por unidade Fundadora", min_value=1.0, value=float(_cfg["peso_voto_fundadora"]), step=1.0)
                    if st.form_submit_button("Guardar regras"):
                        guardar_cotas_config(float(_n_c), float(_l_c), float(_m_c), float(_p_c))
                        st.session_state["cotas_msg"] = "Regras guardadas (propostas pendentes de formalização)."
                        st.rerun()
                st.markdown(f"**Admissão de novos participantes:** 🔒 DESACTIVADA. Só poderá ser activada por decisão documentada e enquadramento validado, "
                            "não por um botão. Entretanto, recolhem-se apenas manifestações de interesse.")
                _rec = st.checkbox("A base de unidades foi reconciliada com contribuições comprovadas, acordos e perdas", value=_cfg["unidades_base_validada"], key="base_rec_chk")
                if _rec != _cfg["unidades_base_validada"]:
                    _nota_rec = st.text_input("Fundamento desta alteração (obrigatório)", key="base_rec_nota")
                    if st.button("Confirmar alteração do estado da base", key="base_rec_btn"):
                        if not _nota_rec.strip():
                            st.error("Indique o fundamento.")
                        else:
                            definir_base_reconciliada(_rec, _nota_rec.strip())
                            registar_vup_hoje()
                            st.rerun()

            # ---------- D. Estrutura inicial ----------
            _validadas = int(consultar_um("SELECT COUNT(*) FROM unidades_movimentos WHERE estado = 'Validado'")[0])
            with st.expander("3. Adopção da estrutura inicial de unidades (reorganização, não é entrada de dinheiro)", expanded=_validadas == 0):
                if _validadas > 0:
                    st.info("Já existe uma estrutura de unidades validada. Só se adopta uma vez; alterações fazem-se por anulação documentada.")
                else:
                    _rs = obter_resumo_patrimonial()
                    st.warning(f"HIPÓTESE: {kz(_rs['capital_realizado'])} ÷ {kz(_cfg['valor_nominal'])} = {_rs['capital_realizado'] / _cfg['valor_nominal']:.5f} unidades. "
                               "Não é uma reconstrução comprovada das contribuições históricas e não prova quem entregou cada montante. "
                               "Esta etapa regista um ACORDO de participação como reorganização: não cria transferências bancárias nem movimentos financeiros.")
                    _cap_base = st.number_input("Capital de referência a repartir (Kz)", min_value=0.0, step=1000.0, value=float(round(_rs["capital_realizado"])), key="cotas_cap_base")
                    _base_f = pd.DataFrame({"Sócio": [NOME_ADMIN_PUBLICO, "", "", "", ""], "E-mail da conta (opcional)": [""] * 5,
                                            "% do capital": [55.0, 15.0, 10.0, 10.0, 10.0]})
                    st.caption("Percentagens de referência inicialmente acordadas: 55%, 15%, 10%, 10%, 10%. Escreva o nome real de cada participante (fica só nos registos internos).")
                    _fund = st.data_editor(_base_f, num_rows="dynamic", hide_index=True, key="cotas_fundadores",
                                           column_config={"% do capital": st.column_config.NumberColumn("% do capital", min_value=0.0, max_value=100.0, step=0.5, format="%.2f")})
                    try:
                        _subs = calcular_subscricoes_iniciais(float(_cap_base), _cfg["valor_nominal"], _fund.to_dict("records"))
                    except ValueError as _e:
                        _subs = None
                        st.info(str(_e))
                    if _subs:
                        _prev = pd.DataFrame(_subs)
                        _prev["montante"] = _prev["montante"].apply(lambda v: kz2(v) + " Kz")
                        _prev["cotas"] = _prev["cotas"].apply(lambda v: f"{v:,.6f}".replace(",", " "))
                        _prev["pct"] = _prev["pct"].apply(lambda v: f"{v:.2f}%")
                        st.dataframe(_prev[["socio", "pct", "montante", "cotas"]].rename(columns={"socio": "Participante", "pct": "% acordada", "montante": "Valor de referência", "cotas": "Unidades"}), hide_index=True)
                        _d_base = st.date_input("Data-base da adopção", value=datetime.now().date(), key="data_base_in")
                        _fund_txt = st.text_area("Fundamento da adopção (acta, acordo, critério)", key="fund_base_txt", height=80)
                        _rec_now = st.checkbox("Declaro que a base foi reconciliada (se não, o VUP fica 'Provisório')", key="rec_now_chk")
                        if st.button("Adoptar estrutura inicial", type="primary", key="cotas_criar"):
                            try:
                                adoptar_estrutura_inicial(_subs, _cfg["valor_nominal"], _d_base, _fund_txt, _rec_now)
                                registar_vup_hoje()
                                st.session_state["cotas_msg"] = "Estrutura inicial adoptada como reorganização."
                                st.rerun()
                            except ValueError as _e2:
                                st.error(str(_e2))

            # ---------- E. Operações ----------
            st.markdown("**4. Entrada ou saída de um participante (operação autorizada)**")
            st.caption("Calcula ao VUP aprovado ANTES da operação. Regista a operação, o novo retrato do dinheiro disponível e a auditoria, tudo de uma só vez. "
                       "Não é possível emitir ao valor nominal para contornar o VUP. Não há reembolso imediato garantido: prazos, liquidez e custos dependem das regras aplicáveis.")
            _contas_u = listar_contas()
            _opc_u = [f"{r['nome']} — {r['email']}" for _, r in _contas_u.iterrows()] + ["Outro (escrever o nome)"]
            if "ref_op" not in st.session_state:
                st.session_state["ref_op"] = f"OP-{datetime.now():%Y%m%d%H%M%S}-{secrets.token_hex(3)}"
            with st.form("form_unidades"):
                _sel_u = st.selectbox("Participante", _opc_u)
                _nome_u = st.text_input("Nome (só se escolheu 'Outro')")
                f1, f2 = st.columns(2)
                _tipo_u = f1.selectbox("Operação", ["Subscrição", "Resgate"])
                _classe_u = f2.selectbox("Classe", ["Ordinária", "Fundadora"], help="Fundadora só se esse participante já for fundador. A classe é uma proposta pendente de formalização.")
                f3, f4 = st.columns(2)
                _mont_u = f3.text_input("Montante (Kz)", value="")
                _data_u = f4.date_input("Data da operação", value=datetime.now().date())
                _vh_u = st.text_input("Valor da unidade nessa data (só se a data for anterior a hoje: regularização)", value="")
                _fund_u = st.text_area("Fundamento / observações (obrigatório em regularizações)", height=70)
                st.caption(f"Referência desta operação (impede duplicações): {st.session_state['ref_op']}")
                _ok_u = st.form_submit_button("Registar operação")
            if _ok_u:
                if _sel_u.startswith("Outro"):
                    _socio_u, _mail_u = _nome_u.strip(), None
                else:
                    _linha_u = _contas_u.iloc[_opc_u.index(_sel_u)]
                    _socio_u, _mail_u = str(_linha_u["nome"]), str(_linha_u["email"])
                _m = _numero_flex(_mont_u)
                _vh = _numero_flex(_vh_u) if _vh_u.strip() else None
                if _m is None or _m <= 0:
                    st.error("Indique um montante válido (ex.: 500000).")
                else:
                    try:
                        _r = registar_operacao_unidades(_tipo_u, _socio_u, _mail_u, _m, _classe_u, _data_u, st.session_state["ref_op"], _fund_u, _vh)
                        registar_vup_hoje()
                        st.session_state.pop("ref_op", None)
                        st.session_state["cotas_msg"] = (f"{_tipo_u} registada: {_r['unidades']} unidades ao VUP de {_r['vup']} Kz ({_r['origem']}). "
                                                         "O dinheiro disponível foi actualizado no novo retrato.")
                        st.rerun()
                    except ValueError as _e3:
                        st.error(str(_e3))

            # ---------- F. Revisão / movimentos ----------
            _mov_u = obter_unidades_movimentos()
            st.markdown("**5. Movimentos de unidades (revisão, correcção e anulação)**")
            if _mov_u.empty:
                st.info("Ainda não há movimentos.")
            else:
                st.caption("'Por rever': lançados antes desta revisão; não entram no VUP. Podem ser corrigidos e depois validados com fundamento, ou anulados. "
                           "Movimentos validados não se editam nem se apagam: anulam-se com motivo (fica o rasto), e se houve efeito em caixa regista-se o estorno.")
                for _, _m in _mov_u.head(30).iterrows():
                    _mid = int(_m["id"])
                    _est = str(_m["estado"])
                    with st.expander(f"{_m['data']}  ·  {_m['socio']}  ·  {_m['tipo']}  ·  {_est}  ·  {kz2(_m['montante'])} Kz  ·  {float(_m['unidades']):,.6f} un.".replace(",", " ")):
                        st.write(f"Origem: {_m['origem'] or '—'}  ·  Referência: {_m['referencia'] or '—'}  ·  VUP aplicado: {kz2(_m['vup'])} Kz  ·  Classe: {_m['classe'] or '—'}")
                        if _m["fundamento"]:
                            st.write(f"Fundamento: {_m['fundamento']}")
                        if _est == "Anulado":
                            st.write(f"Anulado por {_m['anulado_por']} em {str(_m['anulado_em'])[:16]}: {_m['motivo_anulacao']}")
                        if _est == "Por rever":
                            with st.form(f"form_edit_mov_{_mid}"):
                                e1, e2 = st.columns(2)
                                _e_socio = e1.text_input("Participante", value=str(_m["socio"]))
                                _e_data = e2.date_input("Data", value=_m["data"])
                                e3, e4, e5 = st.columns(3)
                                _e_mont = e3.text_input("Montante (Kz)", value=f"{abs(float(_m['montante'])):.2f}".replace(".", ","))
                                _e_vup = e4.text_input("Valor da unidade nesse dia (Kz)", value=f"{float(_m['vup']):.4f}".replace(".", ","))
                                _e_cls = e5.selectbox("Classe", ["Fundadora", "Ordinária"], index=0 if str(_m["classe"]) == "Fundadora" else 1)
                                _gc = st.form_submit_button("Guardar correcção")
                            if _gc:
                                try:
                                    corrigir_movimento_unidades(_mid, _e_data, _e_socio, _numero_flex(_e_mont) or 0, _numero_flex(_e_vup) or 0, _e_cls)
                                    st.session_state["cotas_msg"] = "Movimento corrigido (auditado)."
                                    st.rerun()
                                except ValueError as _e4:
                                    st.error(str(_e4))
                            _fv = st.text_input("Fundamento da validação", key=f"fv_{_mid}")
                            if st.button("Validar movimento", key=f"val_{_mid}"):
                                try:
                                    validar_movimento_unidades(_mid, _fv)
                                    registar_vup_hoje()
                                    st.session_state["cotas_msg"] = "Movimento validado."
                                    st.rerun()
                                except ValueError as _e5:
                                    st.error(str(_e5))
                        if _est != "Anulado":
                            _mot = st.text_input("Motivo da anulação", key=f"mot_{_mid}")
                            if st.button("Anular movimento", key=f"anu_{_mid}"):
                                try:
                                    anular_movimento_unidades(_mid, _mot)
                                    registar_vup_hoje()
                                    st.session_state["cotas_msg"] = "Movimento anulado (com estorno em caixa, se aplicável)."
                                    st.rerun()
                                except ValueError as _e6:
                                    st.error(str(_e6))

                # posições (só movimentos validados)
                _val = _mov_u[_mov_u["estado"] == "Validado"]
                if not _val.empty:
                    st.markdown("**6. Posição de cada participante (apenas movimentos validados)**")
                    _mv = adicionar_votos(_val, _cfg["peso_voto_fundadora"])
                    _pos = _mv.groupby(["socio", "classe"]).agg(unidades=("unidades", "sum"), aportado=("efeito_caixa", "sum"), votos=("votos", "sum")).reset_index()
                    _pos = _pos[_pos["unidades"].abs() > 1e-9]
                    _tot_un, _tot_vt = float(_pos["unidades"].sum()), float(_pos["votos"].sum())
                    _rot = rotulos_publicos(list(_pos["socio"].unique()))
                    _pos["Apresentação pública"] = _pos["socio"].map(_rot)
                    _pos["% das unidades"] = _pos["unidades"].apply(lambda v: f"{v / _tot_un * 100:.2f}%" if _tot_un > 0 else "—")
                    _pos["% dos votos"] = _pos["votos"].apply(lambda v: f"{v / _tot_vt * 100:.2f}%" if _tot_vt > 0 else "—")
                    _pos["Valor actual"] = _pos["unidades"].apply(lambda v: kz2(v * _vi["vup"]) + " Kz" if _vi["estado"] != "Não calculado" else "—")
                    _pos["unidades"] = _pos["unidades"].apply(lambda v: f"{v:,.6f}".replace(",", " "))
                    _pos["Entradas em dinheiro (líquidas)"] = _pos["aportado"].apply(lambda v: kz2(v) + " Kz")
                    st.dataframe(_pos[["socio", "Apresentação pública", "classe", "unidades", "% das unidades", "% dos votos", "Entradas em dinheiro (líquidas)", "Valor actual"]].rename(
                        columns={"socio": "Participante (interno)", "classe": "Classe", "unidades": "Unidades"}), hide_index=True)
                    st.caption("As 'entradas em dinheiro' só contam subscrições e resgates autorizados; as unidades da reorganização inicial não são dinheiro entregue.")

            # ---------- G. Registo histórico privado + reconciliação ----------
            with st.expander("7. Registo histórico privado e reconciliação"):
                st.caption("Registo interno, fora do património, do VUP e do preço de entrada. Não é auditado nem integralmente comprovado.")
                for _, _h in consultar_df("SELECT id, descricao, valor_estimado, estado, nota, criado_em FROM historico_privado ORDER BY id").iterrows():
                    st.write(f"**{_h['descricao']}**: ~{kz2(_h['valor_estimado'])} Kz — *{_h['estado']}*")
                    st.caption(_h["nota"] or "")
                _rsm = obter_resumo_patrimonial()
                _nav_txt = kz2(_vi["vlg"]) + " Kz" if _vi["estado"] != "Não calculado" else "não calculado"
                st.write(f"Capital realizado declarado: {kz2(_rsm['capital_realizado'])} Kz  ·  Património líquido calculado: {_nav_txt}")
                st.caption("A diferença entre as duas rubricas ainda não está reconciliada e não se atribui a nenhuma causa; faça a reconciliação com documentos antes de a usar em decisões.")

        with aba_activos:
            st.subheader("Editar Cotações & Activos")
            st.caption("Cada vez que guardas, o Índice APPO é recalculado e um novo ponto é registado no histórico.")
            df_activos_admin = obter_activos()
            # Mostrar variação actual (read-only) para referência
            df_admin_display = df_activos_admin[["ticker", "nome", "tipo", "preco", "variacao"]].copy()
            df_admin_display = df_admin_display.rename(columns={"variacao": "Var.% (auto)"})
            df_admin_display["Var.% (auto)"] = df_admin_display["Var.% (auto)"].apply(pct_bruto)
            st.caption("A variação % é calculada automaticamente ao guardar. Edita apenas o preço.")
            df_editado = st.data_editor(
                df_activos_admin[["ticker", "nome", "tipo", "preco"]], num_rows="dynamic", key="editor_activos",
                column_config={
                    "ticker": st.column_config.TextColumn("Ticker", max_chars=12),
                    "nome": "Nome do activo", "tipo": "Tipo",
                    "preco": st.column_config.NumberColumn("Preço (Kz)", min_value=0.0, step=0.01, format="%.2f"),
                })
            st.dataframe(df_admin_display[["ticker", "Var.% (auto)"]], hide_index=True)
            # ---- Actualização directa a partir da BODIVA (com pré-visualização) ----
            st.markdown("**Actualização directa a partir da BODIVA**")
            st.caption("Vai buscar as cotações à BODIVA para os tickers registados acima (gravados). "
                       "Nada é gravado até confirmar na pré-visualização.")
            if st.button("🔄 Buscar cotações na BODIVA"):
                try:
                    _tks = [str(x or "").strip().upper() for x in df_activos_admin["ticker"] if str(x or "").strip()]
                    st.session_state["bodiva_prev"] = buscar_cotacoes_bodiva(_tks)
                except Exception as _e:
                    st.session_state.pop("bodiva_prev", None)
                    st.error(f"Não foi possível obter as cotações da BODIVA agora ({_e}). "
                             "Pode continuar a editar os preços manualmente.")
            _prev = st.session_state.get("bodiva_prev")
            if _prev:
                _linhas_prev = []
                for _, _r in df_activos_admin.iterrows():
                    _tk = str(_r["ticker"] or "").strip().upper()
                    _novo = _prev.get(_tk)
                    _atual = float(_r["preco"])
                    _suspeito = (_novo is not None and _atual > 0 and abs(_novo / _atual - 1) > 0.5)
                    _linhas_prev.append({
                        "Ticker": _tk, "Nome": _r["nome"],
                        "Preço na app (Kz)": _atual,
                        "Preço BODIVA (Kz)": _novo if _novo is not None else "não encontrado",
                        "Estado": ("⚠️ variação >50% — não será aplicado" if _suspeito
                                   else ("sem alteração" if _novo is not None and _novo == _atual
                                         else ("a actualizar" if _novo is not None else "mantém preço actual"))),
                    })
                st.dataframe(pd.DataFrame(_linhas_prev), hide_index=True)
                if st.button("✅ Aplicar cotações da BODIVA e guardar"):
                    _df_novo = df_activos_admin[["ticker", "nome", "tipo", "preco"]].copy()
                    for _i in _df_novo.index:
                        _novo = _prev.get(str(_df_novo.at[_i, "ticker"] or "").strip().upper())
                        _atual = float(_df_novo.at[_i, "preco"])
                        if _novo is not None and not (_atual > 0 and abs(_novo / _atual - 1) > 0.5):
                            _df_novo.at[_i, "preco"] = _novo
                    substituir_activos(_df_novo)
                    st.session_state.pop("bodiva_prev", None)
                    st.success("Cotações da BODIVA aplicadas. Índice APPO e variações actualizados.")
                    st.rerun()

            with st.expander("🏷️ Preço da OPV (oferta pública de venda) — referência nos gráficos"):
                st.caption("Aparece nos gráficos como uma linha tracejada, com a variação desde a OPV.")
                _tks_opv = [str(x).strip().upper() for x in df_activos_admin["ticker"] if str(x).strip()]
                oc1, oc2, oc3 = st.columns([2, 1.5, 1.5])
                _t_opv = oc1.selectbox("Título", _tks_opv, key="opv_tk")
                _p_opv = oc2.number_input("Preço da OPV (Kz)", min_value=0.0, step=100.0, key="opv_pr")
                _d_opv = oc3.date_input("Data (opcional)", value=None, key="opv_dt")
                if st.button("Guardar preço da OPV", key="opv_btn"):
                    if _p_opv > 0:
                        guardar_opv(_t_opv, float(_p_opv), _d_opv)
                        st.success("Preço da OPV guardado.")
                        st.rerun()
                    else:
                        st.error("Indique um preço superior a zero.")
                _opvs = consultar_df("SELECT ticker, preco, data FROM opv_activos ORDER BY ticker")
                for _, _o in _opvs.iterrows():
                    od1, od2 = st.columns([4, 1])
                    od1.write(f"{_o['ticker']}  ·  {float(_o['preco']):,.0f} Kz".replace(",", " ") + (f"  ·  {_o['data']}" if _o["data"] else ""))
                    if od2.button("Eliminar", key=f"del_opv_{_o['ticker']}"):
                        eliminar_opv(_o["ticker"])
                        st.rerun()

            with st.expander("📥 Importar histórico de cotações (CSV ou Excel)"):
                st.caption("Para preencher o passado nos gráficos. O ficheiro precisa de três colunas, com cabeçalhos como "
                           "**data**, **ticker** e **preço** (ex.: 02/10/2026; BAIAAAAA; 94600). Aceita as exportações da BODIVA/BFA se tiverem estas colunas.")
                _f_hist = st.file_uploader("Ficheiro de histórico", type=["csv", "xlsx"], key="hist_cot_up")
                _tks_app = [str(x).strip().upper() for x in df_activos_admin["ticker"] if str(x).strip()]
                _tk_esc = st.selectbox("Se o ficheiro for de UM só título (sem coluna de ticker), escolha o título:",
                                       ["(o ficheiro já traz a coluna de ticker)"] + _tks_app, key="hist_cot_tk")
                _tk_forcado = "" if _tk_esc.startswith("(") else _tk_esc
                if _f_hist is not None and st.button("Importar histórico", key="hist_cot_btn"):
                    try:
                        if _f_hist.name.lower().endswith(".csv"):
                            _dfh = pd.read_csv(_f_hist, sep=None, engine="python", encoding="utf-8-sig")
                        else:
                            _dfh = pd.read_excel(_f_hist)
                        if len(_dfh) > 20000:
                            st.error("O ficheiro tem demasiadas linhas (máximo 20 000).")
                        else:
                            _ok, _mau = importar_historico_cotacoes(_dfh, _tk_forcado)
                            st.success(f"Importadas {_ok} cotações" + (f"; {_mau} linhas ignoradas (data, ticker ou preço inválidos)." if _mau else "."))
                    except Exception as _e:
                        st.error(f"Não foi possível importar: {_e}")

            if st.button("Guardar alterações às cotações"):
                substituir_activos(df_editado)
                st.success("Cotações e Índice APPO actualizados com sucesso.")
                st.rerun()

        with aba_carteira_real:
            st.subheader("Editar Carteira Real do Clube")
            st.caption(
                "Posições REAIS, com dinheiro verdadeiro, investidas de facto pelo Clube "
                "(ex.: na BFA Capital Markets). É esta tabela que alimenta o relatório PDF — "
                "diferente do Simulador de Investimento, que é só treino com dinheiro fictício."
            )
            df_activos_lista = obter_activos()
            if df_activos_lista.empty:
                st.warning("Ainda não há activos em Cotações & Activos — regista-os lá primeiro.")
            else:
                # Mapa nome-visível → ticker real, para a lista de escolha. Isto
                # elimina a classe de bugs em que o ticker escrito à mão (aqui ou
                # em Cotações) não batia certo entre painéis, e o relatório ou
                # não encontrava preço nenhum, ou "colava" a todos o preço do
                # primeiro activo com ticker em branco.
                df_activos_lista["rotulo"] = df_activos_lista.apply(
                    lambda r: f"{r['nome']}" + (f"  ({r['ticker']})" if str(r['ticker'] or '').strip() else "  ⚠️ sem ticker — define-o em Cotações & Activos"),
                    axis=1)
                mapa_rotulo_para_ticker = dict(zip(df_activos_lista["rotulo"], df_activos_lista["ticker"]))
                mapa_rotulo_para_nome   = dict(zip(df_activos_lista["rotulo"], df_activos_lista["nome"]))

                df_carteira_admin = obter_carteira_real()
                # construir a coluna "rotulo" de cada posição já guardada, para o
                # selector mostrar a escolha actual correcta
                if not df_carteira_admin.empty:
                    # só tickers não vazios entram no mapa (evita colisões entre activos sem ticker)
                    tk_para_rotulo = {str(v).strip().upper(): k for k, v in mapa_rotulo_para_ticker.items() if str(v or "").strip()}
                    nome_para_rotulo = {str(v).strip().upper(): k for k, v in mapa_rotulo_para_nome.items()}

                    def _resolver_rotulo(linha):
                        r = tk_para_rotulo.get(str(linha["ticker"] or "").strip().upper())
                        if r is None:
                            r = nome_para_rotulo.get(str(linha["nome"] or "").strip().upper())
                        return r

                    df_carteira_admin["rotulo"] = df_carteira_admin.apply(_resolver_rotulo, axis=1)
                    if df_carteira_admin["rotulo"].isna().any():
                        st.warning("⚠️ Há posições gravadas antes que já não correspondem a nenhum activo de Cotações & Activos "
                                   "(ticker ou nome alterado). Escolhe o activo certo na lista para essas linhas e grava.")
                    # mesma ordem de Cotações & Activos (BAI no topo, etc.)
                    ordem_rotulos = {r: i for i, r in enumerate(df_activos_lista["rotulo"])}
                    df_carteira_admin["_ordem"] = df_carteira_admin["rotulo"].map(ordem_rotulos).fillna(9999)
                    df_carteira_admin = df_carteira_admin.sort_values("_ordem", kind="stable")
                    df_carteira_admin["gravado_como"] = df_carteira_admin["nome"]
                    tabela_base = df_carteira_admin[["rotulo", "gravado_como", "qtd", "valor_aquisicao"]].reset_index(drop=True)
                    tabela_base["valor_aquisicao"] = tabela_base["valor_aquisicao"].apply(
                        lambda v: f"{float(v):.2f}".replace(".", ","))

                    # Diagnóstico: o que o relatório PDF está realmente a usar, linha a linha
                    _preco_por_rotulo = dict(zip(df_activos_lista["rotulo"], df_activos_lista["preco"]))
                    _diag = []
                    for _, _p in df_carteira_admin.iterrows():
                        _pr = _preco_por_rotulo.get(_p["rotulo"]) if _p["rotulo"] is not None else None
                        _pr = float(_pr) if _pr is not None and pd.notna(_pr) else 0.0
                        _diag.append({
                            "Gravado como": _p["nome"],
                            "Activo ligado (ticker)": _p["rotulo"] if _p["rotulo"] is not None else "⚠️ sem correspondência",
                            "Qtd": _p["qtd"],
                            "Preço actual (Kz)": _pr,
                            "Valor actual (Kz)": round(float(_p["qtd"]) * _pr, 2),
                        })
                    st.caption("Ligação actual de cada posição ao activo (é isto que o relatório PDF usa). "
                               "Se o nome em 'Gravado como' não corresponde ao 'Activo ligado', "
                               "corrija o activo na tabela abaixo e grave. Preço a 0 = activo sem cotação em Cotações & Activos.")
                    st.dataframe(pd.DataFrame(_diag), hide_index=True)
                else:
                    st.info("Ainda não há nenhuma posição registada na carteira real.")
                    tabela_base = pd.DataFrame({"rotulo": pd.Series(dtype="object"), "gravado_como": pd.Series(dtype="object"),
                                                "qtd": pd.Series(dtype="float"), "valor_aquisicao": pd.Series(dtype="object")})

                df_editado_carteira = st.data_editor(
                    tabela_base, num_rows="dynamic", key="editor_carteira_real",
                    disabled=["gravado_como"],
                    column_config={
                        "gravado_como": st.column_config.TextColumn("Gravado como (só leitura)"),
                        "rotulo": st.column_config.SelectboxColumn(
                            "Activo", options=list(mapa_rotulo_para_ticker.keys()), required=True,
                            help="Escolhe da lista de Cotações & Activos — garante que o relatório encontra sempre o preço certo."),
                        "qtd": st.column_config.NumberColumn("Quantidade de acções", min_value=0.0, step=1.0),
                        "valor_aquisicao": st.column_config.TextColumn(
                            "Valor TOTAL pago na aquisição (Kz)",
                            help="Escreva com vírgula ou ponto nos cêntimos (ex.: 362031,48). Não é o preço unitário — é o custo total desta posição."),
                    })

                def _parse_valor_kz(txt):
                    """Aceita 362031,48 | 362031.48 | 1.311.562,53 | 1 311 562,53 | 1,311,562.53 | 'Kz'."""
                    if txt is None or (isinstance(txt, float) and pd.isna(txt)):
                        return None
                    t_ = str(txt).replace("Kz", "").replace("\u00a0", "").replace(" ", "").strip()
                    if not t_:
                        return None
                    if "," in t_ and "." in t_:
                        dec = "," if t_.rfind(",") > t_.rfind(".") else "."
                        mil = "." if dec == "," else ","
                        t_ = t_.replace(mil, "").replace(dec, ".")
                    elif "," in t_ or "." in t_:
                        sep = "," if "," in t_ else "."
                        partes = t_.split(sep)
                        if len(partes) == 2 and 1 <= len(partes[1]) <= 2:
                            t_ = partes[0] + "." + partes[1]      # separador decimal
                        else:
                            t_ = "".join(partes)                   # separador de milhares
                    try:
                        return float(t_)
                    except ValueError:
                        return None

                if st.button("Guardar alterações à Carteira Real"):
                    linhas_validas = df_editado_carteira.dropna(subset=["rotulo"]).copy()
                    linhas_validas = linhas_validas[linhas_validas["rotulo"].isin(mapa_rotulo_para_ticker)].copy()
                    linhas_validas["valor_aquisicao"] = linhas_validas["valor_aquisicao"].apply(_parse_valor_kz)
                    if linhas_validas["valor_aquisicao"].isna().any():
                        st.error("Há valores de aquisição inválidos ou em branco. Escreva só números (ex.: 362031,48). Nada foi gravado.")
                        st.stop()
                    if len(linhas_validas) < len(df_editado_carteira):
                        st.warning("Algumas linhas sem activo escolhido foram ignoradas — selecciona um activo da lista em cada linha antes de gravar.")
                    df_para_gravar = pd.DataFrame({
                        "ticker": linhas_validas["rotulo"].map(mapa_rotulo_para_ticker),
                        "nome":   linhas_validas["rotulo"].map(mapa_rotulo_para_nome),
                        "qtd":    linhas_validas["qtd"],
                        "valor_aquisicao": linhas_validas["valor_aquisicao"],
                    })
                    substituir_carteira_real(df_para_gravar)
                    st.success("Carteira real actualizada. O relatório PDF passa já a reflectir estes valores.")
                    st.rerun()

            with st.expander("Preços-base do Índice APPO (19/08/2026)"):
                st.caption("O Índice APPO mede a variação média de todas as acções cotadas desde o dia em que o Clube começou a investir (19/08/2026). "
                           "Indica o preço de cada acção nesse dia (resumo de mercado da BODIVA, Kitadinvest ou histórico do homebroker). "
                           "As notas de execução só mostram os teus próprios negócios, não o mercado. Sem preço-base, usa-se o primeiro preço disponível no histórico.")
                _acoes_adm = df_activos_admin[df_activos_admin["tipo"].apply(_eh_accao)]
                _bases_df = obter_bases_indice_appo(com_fonte=True)
                _bases_d = {_tk_norm(r["ticker"]): r for _, r in _bases_df.iterrows()} if not _bases_df.empty else {}
                _linhas_b = [{"ticker": r["ticker"], "nome": r["nome"],
                              "preco_base": (float(_bases_d[_tk_norm(r["ticker"])]["preco_base"]) if _tk_norm(r["ticker"]) in _bases_d else None),
                              "fonte": (str(_bases_d[_tk_norm(r["ticker"])]["fonte"] or "") if _tk_norm(r["ticker"]) in _bases_d else "")}
                             for _, r in _acoes_adm.iterrows()]
                if not _linhas_b:
                    st.info("Ainda não há acções registadas.")
                else:
                    _bases_ed = st.data_editor(pd.DataFrame(_linhas_b), key="editor_bases_appo", hide_index=True, disabled=["ticker", "nome"],
                                               column_config={"ticker": "Ticker", "nome": "Acção",
                                                              "preco_base": st.column_config.NumberColumn("Preço em 19/08/2026 (Kz)", min_value=0.0, step=0.01, format="%.2f"),
                                                              "fonte": st.column_config.TextColumn("Fonte")})
                    if st.button("Guardar preços-base", key="guardar_bases_appo"):
                        guardar_bases_indice_appo(_bases_ed)
                        st.success("Preços-base guardados. O Índice APPO foi recalculado.")
                        st.rerun()

        with aba_aval:
            st.subheader("Premissas Macro (CAPM)")
            premissas = obter_premissas_macro()
            with st.form("form_premissas"):
                col1, col2, col3 = st.columns(3)
                infl = col1.number_input("Inflação anual", min_value=0.0, max_value=1.0, value=premissas["inflacao"], step=0.005, format="%.3f")
                rf   = col2.number_input("Taxa livre de risco (Rf)", min_value=0.0, max_value=1.0, value=premissas["taxa_livre_risco"], step=0.005, format="%.3f")
                erp  = col3.number_input("Prémio de risco de mercado (ERP)", min_value=0.0, max_value=1.0, value=premissas["premio_risco"], step=0.005, format="%.3f")
                col4, col5, col6 = st.columns(3)
                bb = col4.number_input("Beta — Banca",           min_value=0.0, max_value=3.0, value=premissas["beta_banca"],   step=0.05)
                bt = col5.number_input("Beta — Telecom",         min_value=0.0, max_value=3.0, value=premissas["beta_telecom"], step=0.05)
                bo = col6.number_input("Beta — Outros sectores", min_value=0.0, max_value=3.0, value=premissas["beta_outros"],  step=0.05)
                guardar_premissas = st.form_submit_button("Guardar premissas")
            if guardar_premissas:
                actualizar_premissas_macro(infl, rf, erp, bb, bt, bo)
                st.success("Premissas macro actualizadas.")
                st.rerun()

            st.markdown("**Inflação de Angola (alimenta os relatórios e a análise de rentabilidade real)**")
            st.caption("Insere as três leituras a partir do INE ou do BNA. Enquanto não o fizeres, os relatórios usam a inflação anual acima como valor por defeito e avisam disso.")
            with st.form("form_inflacao"):
                ci1, ci2, ci3 = st.columns(3)
                _ih = ci1.number_input("Inflação homóloga (YoY, %)", min_value=0.0, max_value=500.0, value=round(premissas["inflacao_homologa"] * 100, 2), step=0.1, format="%.2f")
                _iv = ci2.number_input("Inflação vigente (variação mensal, %)", min_value=0.0, max_value=50.0, value=round(premissas["inflacao_vigente_m"] * 100, 2), step=0.05, format="%.2f")
                _ip = ci3.number_input("Inflação projectada (próximos 12 meses, %)", min_value=0.0, max_value=500.0, value=round(premissas["inflacao_projectada"] * 100, 2), step=0.1, format="%.2f")
                _iref = st.text_input("Fonte e data (ex.: INE, Setembro/2026)", value=premissas["inflacao_ref"])
                _gi = st.form_submit_button("Guardar inflação")
            if _gi:
                actualizar_inflacao_macro(_ih / 100, _iv / 100, _ip / 100, _iref)
                st.success("Inflação actualizada.")
                st.rerun()

            st.divider()
            st.subheader("Dados de Avaliação por Empresa")
            df_aval_admin = obter_avaliacoes()
            df_aval_editado = st.data_editor(
                df_aval_admin[["empresa", "sector", "preco", "acoes_circulacao", "lucro_liquido", "ganho_pontual", "capital_proprio", "dividendo_total", "crescimento_g"]],
                num_rows="dynamic", key="editor_avaliacoes",
                column_config={
                    "empresa": "Empresa", "sector": "Sector",
                    "preco":             st.column_config.NumberColumn("Preço (Kz)", min_value=0.0, step=0.01, format="%.2f"),
                    "acoes_circulacao":  st.column_config.NumberColumn("Acções em circulação", min_value=0.0, step=1000.0),
                    "lucro_liquido":     st.column_config.NumberColumn("Lucro líquido (Kz)", step=1000000.0),
                    "ganho_pontual":     st.column_config.NumberColumn("Ganho pontual não recorrente (Kz)", step=1000000.0),
                    "capital_proprio":   st.column_config.NumberColumn("Capital próprio (Kz)", min_value=0.0, step=1000000.0),
                    "dividendo_total":   st.column_config.NumberColumn("Dividendo total distribuído (Kz)", min_value=0.0, step=1000000.0),
                    "crescimento_g":     st.column_config.NumberColumn("Crescimento assumido (g)", min_value=0.0, max_value=1.0, step=0.01, format="%.2f"),
                })
            if st.button("Guardar alterações às avaliações"):
                substituir_avaliacoes(df_aval_editado)
                st.success("Avaliações actualizadas com sucesso.")
                st.rerun()

        with aba_movimentos:
            st.subheader("Registar novo movimento")
            with st.form("form_novo_movimento", clear_on_submit=True):
                tipo_mov    = st.selectbox("Tipo", ["Entrada de Capital", "Compra de Activo", "Venda de Activo", "Saída/Despesa", "Ajuste de Reserva"])
                descricao_mov = st.text_input("Descrição")
                montante_mov  = st.number_input("Montante (Kz)", min_value=0.0, step=1000.0)
                data_mov      = st.date_input("Data do movimento")
                registar_mov  = st.form_submit_button("Registar movimento")
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
            st.subheader("Adicionar novo artigo (texto)")
            st.info("📌 Para publicar um PDF **tal como é** (com gráficos, imagens e formatação), use a secção "
                    "**\"📄 Publicar documento PDF\"**, mais abaixo nesta página. Este formulário cria um artigo só de texto.")
            modo = st.radio("Fonte do conteúdo", ["Extrair só o texto de um PDF (perde gráficos e imagens)", "Escrever manualmente"],
                            horizontal=True, key="modo_artigo")
            texto_extraido = ""
            if modo.startswith("Extrair"):
                ficheiro_pdf = st.file_uploader("Ficheiro PDF (só o texto será aproveitado)", type=["pdf"], key="uploader_pdf")
                if ficheiro_pdf is not None:
                    try:
                        texto_extraido = extrair_texto_pdf(ficheiro_pdf)
                        st.success("Texto extraído com sucesso. Revê antes de publicar.")
                    except Exception as erro:
                        st.error(f"Não foi possível ler o PDF: {erro}")
            with st.form("form_novo_artigo", clear_on_submit=True):
                titulo_artigo   = st.text_input("Título do artigo")
                categoria_artigo= st.selectbox("Categoria", ["Institucional", "Educação", "Análise de Mercado", "Referência"])
                nivel_artigo    = st.selectbox("Nível", ["Automático (pela categoria)", "Iniciante", "Investidor"])
                conteudo_artigo = st.text_area("Conteúdo (Markdown suportado)", value=texto_extraido, height=280)
                publicar        = st.form_submit_button("Publicar artigo")
            if publicar:
                if not titulo_artigo or not conteudo_artigo:
                    st.error("Preenche o título e o conteúdo do artigo.")
                else:
                    inserir_artigo(titulo_artigo, categoria_artigo, conteudo_artigo, {"Iniciante": "iniciante", "Investidor": "investidor"}.get(nivel_artigo))
                    st.success("Artigo publicado.")
                    st.rerun()
            st.divider()
            st.subheader("Artigos existentes")
            for _, artigo in obter_artigos().iterrows():
                col_a, col_b, col_c = st.columns([3, 1.5, 1])
                col_a.write(artigo["titulo"])
                col_b.write(f"{artigo['categoria']} · {NIVEIS[artigo['nivel_efectivo']]}")
                if col_c.button("Eliminar", key=f"eliminar_artigo_{artigo['id']}"):
                    eliminar_artigo(int(artigo["id"]))
                    st.rerun()
            with st.expander("Ajustar o nível de um artigo"):
                _df_art = obter_artigos()
                if _df_art.empty:
                    st.info("Sem artigos.")
                else:
                    _mapa_art = {f"{r['titulo']} (#{r['id']})": int(r["id"]) for _, r in _df_art.iterrows()}
                    _esc_art = st.selectbox("Artigo", list(_mapa_art.keys()), key="niv_art_sel")
                    _esc_niv = st.selectbox("Nível", ["Automático (pela categoria)", "Iniciante", "Investidor"], key="niv_art_niv")
                    if st.button("Aplicar nível", key="niv_art_aplicar"):
                        definir_nivel_artigo(_mapa_art[_esc_art], {"Iniciante": "iniciante", "Investidor": "investidor"}.get(_esc_niv))
                        st.success("Nível actualizado.")
                        st.rerun()

            st.divider()
            st.subheader("📄 Publicar documento PDF (com gráficos e imagens)")
            st.caption("O PDF original é guardado tal como está: os sócios podem lê-lo no ecrã ou descarregá-lo, "
                       "com gráficos, imagens e formatação. Tamanho máximo: 15 MB.")
            with st.form("form_doc_pdf", clear_on_submit=True):
                f_pdf  = st.file_uploader("Ficheiro PDF", type=["pdf"], key="doc_pdf_up")
                t_doc  = st.text_input("Título do documento")
                c_doc  = st.selectbox("Categoria", ["Institucional", "Educação", "Análise de Mercado", "Referência"], key="doc_pdf_cat")
                d_doc  = st.text_area("Descrição curta (opcional)", height=80)
                pub_doc = st.form_submit_button("Publicar documento")
            if pub_doc:
                if f_pdf is None or not t_doc.strip():
                    st.error("Escolha o ficheiro PDF e escreva o título.")
                else:
                    _bytes = f_pdf.getvalue()
                    if not _bytes.startswith(b"%PDF"):
                        st.error("O ficheiro não parece ser um PDF válido.")
                    elif len(_bytes) > PDF_TAMANHO_MAX:
                        st.error(f"O ficheiro tem {len(_bytes) / 1048576:.1f} MB — o máximo é 15 MB. Comprima o PDF e tente de novo.")
                    else:
                        inserir_documento(t_doc.strip(), c_doc, d_doc.strip(), f_pdf.name, _bytes, "biblioteca")
                        st.success("Documento publicado na Biblioteca Educativa.")
                        st.rerun()
            _docs_adm = obter_documentos("biblioteca")
            if not _docs_adm.empty:
                st.markdown("**Documentos PDF publicados**")
                for _, _d in _docs_adm.iterrows():
                    ca, cb, cc = st.columns([3, 1.5, 1])
                    ca.write(f"{_d['titulo']}  ·  {_d['tamanho'] / 1048576:.1f} MB")
                    cb.write(_d["categoria"])
                    if cc.button("Eliminar", key=f"eliminar_doc_{int(_d['id'])}"):
                        eliminar_documento(int(_d["id"]))
                        st.rerun()

            st.divider()
            st.subheader("📜 Estatuto do Clube (PDF)")
            _df_est_adm = obter_documentos("estatuto")
            if not _df_est_adm.empty:
                _e = _df_est_adm.iloc[0]
                ce1, ce2 = st.columns([3, 1])
                ce1.info(f"Estatuto publicado: {_e['nome_ficheiro']} ({_e['tamanho'] / 1048576:.1f} MB, {_e['criado_em']})")
                if ce2.button("Eliminar estatuto", key="eliminar_estatuto"):
                    eliminar_documento(int(_e["id"]))
                    st.rerun()
            with st.form("form_estatuto_pdf", clear_on_submit=True):
                f_est   = st.file_uploader("Ficheiro PDF do Estatuto (substitui o anterior)", type=["pdf"], key="estatuto_pdf_up")
                pub_est = st.form_submit_button("Publicar estatuto")
            if pub_est:
                if f_est is None:
                    st.error("Escolha o ficheiro PDF do Estatuto.")
                else:
                    _b = f_est.getvalue()
                    if not _b.startswith(b"%PDF"):
                        st.error("O ficheiro não parece ser um PDF válido.")
                    elif len(_b) > PDF_TAMANHO_MAX:
                        st.error(f"O ficheiro tem {len(_b) / 1048576:.1f} MB — o máximo é 15 MB.")
                    else:
                        executar("DELETE FROM documentos_pdf WHERE tipo = 'estatuto'")
                        inserir_documento("Estatuto do Clube de Investimento APPO", "Institucional", "", f_est.name, _b, "estatuto")
                        st.success("Estatuto publicado. Já aparece em Sobre Nós & Estatutos.")
                        st.rerun()

        with aba_socios:
            st.subheader("Pedidos de adesão recebidos")
            df_socios = obter_socios()
            if df_socios.empty:
                st.info("Ainda não existem pedidos de adesão.")
            else:
                df_socios_exibir = df_socios.copy()
                df_socios_exibir["contribuicao_inicial"] = df_socios_exibir["contribuicao_inicial"].apply(kz)
                st.dataframe(df_socios_exibir.rename(columns={"nome": "Nome", "email": "E-mail", "telefone": "Telefone",
                                                               "bi": "Nº BI", "contribuicao_inicial": "Contribuição Inicial",
                                                               "criado_em": "Submetido em"}), hide_index=True)

        with aba_contas:
            st.subheader("Criar conta de acesso para um sócio")
            with st.form("form_nova_conta", clear_on_submit=True):
                _np_c, _ap_c   = st.columns(2)
                _nome_c        = _np_c.text_input("Nome próprio")
                _apelido_c     = _ap_c.text_input("Apelido(s)")
                nome_conta     = f"{_nome_c.strip()} {_apelido_c.strip()}".strip()
                email_conta    = st.text_input("E-mail (usado para entrar)")
                password_conta = st.text_input("Palavra-passe inicial", type="password")
                admin_conta    = st.checkbox("Esta conta é administradora")
                criar_conta    = st.form_submit_button("Criar conta")
            if criar_conta:
                if not (_nome_c.strip() and _apelido_c.strip()) or not email_conta or not password_conta:
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
                col_a, col_b, col_c, col_d, col_m, col_e = st.columns([2.1, 0.8, 1.0, 1.0, 1.3, 0.9])
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
                if col_m.button("✉️ Enviar nova por e-mail", key=f"mail_{conta['id']}"):
                    repor_e_enviar_por_email(str(conta["email"]), "", lambda cid=int(conta["id"]): repor_password(cid))
                pode_eliminar = not (conta["is_admin"] and contar_admins() <= 1)
                if col_e.button("Eliminar", key=f"eliminar_conta_{conta['id']}", disabled=not pode_eliminar):
                    eliminar_conta(int(conta["id"]))
                    st.rerun()

            st.divider()
            _ped = obter_pedidos_recuperacao()
            _pend = _ped[_ped["estado"] == "pendente"] if not _ped.empty else _ped
            st.subheader(f"Pedidos de recuperação de palavra-passe ({len(_pend)} pendente(s))")
            st.caption(estado_email())
            st.caption("Confirma a identidade da pessoa (chamada ou WhatsApp) antes de repor. A palavra-passe provisória aparece uma só vez: envia-a por canal seguro e pede à pessoa para a alterar na barra lateral.")
            if _pend.empty:
                st.info("Sem pedidos pendentes.")
            for _, _p in _pend.iterrows():
                _c1, _c2, _c3, _c4, _c5 = st.columns([2.2, 1.3, 1.9, 1.1, 0.9])
                _c1.write(f"**{_p['email']}**")
                _c2.write(str(_p["contacto"] or "—"))
                if _c3.button("✉️ Enviar nova palavra-passe por e-mail", key=f"rec_mail_{_p['id']}", type="primary"):
                    try:
                        repor_e_enviar_por_email(str(_p["email"]), str(_p["contacto"] or ""), lambda pid=int(_p["id"]): resolver_pedido_recuperacao(pid, True))
                    except ValueError as _err:
                        st.error(str(_err))
                if _c4.button("Repor e mostrar", key=f"rec_repor_{_p['id']}"):
                    try:
                        _nova = resolver_pedido_recuperacao(int(_p["id"]), True)
                        st.success(f"Palavra-passe provisória para {_p['email']}: **{_nova}**")
                        _url_wa = ligacao_whatsapp(str(_p["contacto"] or ""), f"Olá! A tua palavra-passe provisória do APPO é: {_nova}. Entra em {APP_URL} e escolhe logo uma só tua.")
                        if _url_wa:
                            botao_ligacao("📲 Enviar por WhatsApp", _url_wa)
                    except ValueError as _err:
                        st.error(str(_err))
                if _c5.button("Ignorar", key=f"rec_ign_{_p['id']}"):
                    try:
                        resolver_pedido_recuperacao(int(_p["id"]), False)
                        st.rerun()
                    except ValueError as _err:
                        st.error(str(_err))

            st.divider()
            st.subheader("Perfis e portais")
            st.caption("O portal de cada conta resulta do perfil de investidor. Só o administrador pode ajustar um portal, com motivo registado na auditoria.")
            df_pf = obter_perfis_resumo()
            if df_pf.empty:
                st.info("Ainda não há contas.")
            else:
                st.dataframe(df_pf.rename(columns={"email": "E-mail", "portal": "Portal", "perfil": "Perfil de risco", "calculado_em": "Perfil calculado em"}), hide_index=True)
            with st.expander("Ajustar o portal de uma conta (excepção)"):
                with st.form("form_ajustar_portal", clear_on_submit=True):
                    alvo = st.selectbox("Conta", df_contas["email"].tolist())
                    novo_portal = st.selectbox("Novo portal", list(NIVEIS.keys()), format_func=lambda v: NIVEIS[v])
                    motivo_portal = st.text_input("Motivo (obrigatório)")
                    aplicar_portal = st.form_submit_button("Aplicar ajuste")
                if aplicar_portal:
                    try:
                        cid = int(df_contas.loc[df_contas["email"] == alvo, "id"].iloc[0])
                        definir_nivel_conta(cid, novo_portal, motivo_portal)
                        st.success("Portal ajustado e registado na auditoria.")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))

        with aba_seguranca:
            st.subheader("Registo de tentativas de acesso (últimas 50)")
            df_log = obter_log_acessos()
            if df_log.empty:
                st.info("Ainda não há registos de acesso.")
            else:
                st.dataframe(df_log.rename(columns={"email": "E-mail", "sucesso": "Sucesso", "criado_em": "Data/Hora"}), hide_index=True)

except PermissionError:
    st.info("Esta área é reservada aos participantes dos investimentos ou ao administrador.")
except (psycopg2.Error, requests.RequestException):
    traceback.print_exc()
    st.error("Não foi possível concluir o pedido neste momento (base de dados ou serviço externo). Tente novamente dentro de instantes.")
except Exception:
    traceback.print_exc()
    st.error("Ocorreu um erro inesperado nesta página. Tente novamente; se persistir, contacte o administrador.")
