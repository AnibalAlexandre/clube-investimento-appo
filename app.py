"""
Clube de Investimento APPO
Portal Oficial de Cotações BODIVA, Contabilidade e Adesão de Sócios
Aplicação web corporativa privada — Streamlit + PostgreSQL (Neon)
"""

import os
import secrets
import textwrap
import time
import urllib.parse
from datetime import datetime

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
        "tagline": "Portal Oficial de Cotações BODIVA, Contabilidade e Adesão de Sócios",
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
            "🧮 Regra 50/30/20":            "🧮 Regra 50/30/20",
            "📚 Biblioteca Educativa":       "📚 Biblioteca Educativa",
            "🧾 Adesão de Sócios":          "🧾 Adesão de Sócios",
            "ℹ️ Sobre Nós & Estatutos":     "ℹ️ Sobre Nós & Estatutos",
            "🔐 Painel do Administrador":   "🔐 Painel do Administrador",
        },
        # ── página início ────────────────────────────────
        "inicio_hero_sub": "Portal Oficial de Cotações BODIVA, Contabilidade e Adesão de Sócios",
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
        "cot_tab_favoritos": "⭐ Favoritos",
        "cot_tab_todos": "📋 Todos os Activos",
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
        "cont_patrimonio_metric": "Património Total do Clube (Realizado + Investimentos + Reservas)",
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
        "sim_disclaimer": "Simulação educativa com juros compostos mensais constantes — os retornos reais dos mercados variam e não são garantidos. Não constitui aconselhamento de investimento.",
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
        "bodiva_badge": "🇦🇴 BODIVA · Kwanzas (Kz)",
    },

    # ─────────────────────────────────────────────────────
    "English": {
        "tagline": "Official BODIVA Quotes, Accounting and Membership Portal",
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
            "🧮 Regra 50/30/20":            "🧮 50/30/20 Rule",
            "📚 Biblioteca Educativa":       "📚 Learning Library",
            "🧾 Adesão de Sócios":          "🧾 Membership Application",
            "ℹ️ Sobre Nós & Estatutos":     "ℹ️ About Us & Bylaws",
            "🔐 Painel do Administrador":   "🔐 Admin Panel",
        },
        "inicio_hero_sub": "Official BODIVA Quotes, Accounting and Membership Portal",
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
        "cont_patrimonio_metric": "Club Total Net Assets (Paid-up + Investments + Reserves)",
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
        "bodiva_badge": "🇦🇴 BODIVA · Kwanzas (Kz)",
    },

    # ─────────────────────────────────────────────────────
    "Français": {
        "tagline": "Portail Officiel des Cotations BODIVA, Comptabilité et Adhésion",
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
            "🧮 Regra 50/30/20":            "🧮 Règle 50/30/20",
            "📚 Biblioteca Educativa":       "📚 Bibliothèque Éducative",
            "🧾 Adesão de Sócios":          "🧾 Adhésion des Membres",
            "ℹ️ Sobre Nós & Estatutos":     "ℹ️ À propos & Statuts",
            "🔐 Painel do Administrador":   "🔐 Panneau d'Administration",
        },
        "inicio_hero_sub": "Portail Officiel des Cotations BODIVA, Comptabilité et Adhésion",
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
        "cont_patrimonio_metric": "Actif Net Total du Club (Libéré + Investissements + Réserves)",
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
        "bodiva_badge": "🇦🇴 BODIVA · Kwanzas (Kz)",
    },

    # ─────────────────────────────────────────────────────
    "Español": {
        "tagline": "Portal Oficial de Cotizaciones BODIVA, Contabilidad y Adhesión",
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
            "🧮 Regra 50/30/20":            "🧮 Regla 50/30/20",
            "📚 Biblioteca Educativa":       "📚 Biblioteca Educativa",
            "🧾 Adesão de Sócios":          "🧾 Adhesión de Socios",
            "ℹ️ Sobre Nós & Estatutos":     "ℹ️ Sobre Nosotros y Estatutos",
            "🔐 Painel do Administrador":   "🔐 Panel de Administrador",
        },
        "inicio_hero_sub": "Portal Oficial de Cotizaciones BODIVA, Contabilidad y Adhesión",
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
        "cont_patrimonio_metric": "Patrimonio Neto Total del Club (Desembolsado + Inversiones + Reservas)",
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
        "bodiva_badge": "🇦🇴 BODIVA · Kwanzas (Kz)",
    },

    # ─────────────────────────────────────────────────────
    "中文 (Mandarim)": {
        "tagline": "BODIVA官方行情、会计与会员门户",
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
            "🧮 Regra 50/30/20":            "🧮 50/30/20法则",
            "📚 Biblioteca Educativa":       "📚 教育图书馆",
            "🧾 Adesão de Sócios":          "🧾 会员申请",
            "ℹ️ Sobre Nós & Estatutos":     "ℹ️ 关于我们与章程",
            "🔐 Painel do Administrador":   "🔐 管理员面板",
        },
        "inicio_hero_sub": "BODIVA官方行情、会计与会员门户",
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
        "cont_patrimonio_metric": "俱乐部总净资产（实缴 + 投资 + 储备）",
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
        "bodiva_badge": "🇦🇴 BODIVA · 宽扎（Kz）",
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
.appo-ticker-wrap {{ overflow: hidden; white-space: nowrap; background: transparent; border-bottom: 1px solid #ECDEE3; padding: 8px 0; margin-bottom: 16px; }}
.appo-ticker-move {{ display: inline-block; padding-left: 100%; animation: appo-scroll 135s linear infinite; font-family: monospace; font-size: 0.82rem; }}
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


def hero(titulo: str, subtitulo: str, badge: str = None):
    if badge is None:
        badge = t().get("bodiva_badge", "🇦🇴 BODIVA · Kwanzas (Kz)")
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
    tx = t()
    cols = tx["cot_tabela_cols"]
    df_disp = df_activos[["ticker", "nome", "tipo", "preco", "variacao"]].copy()
    df_disp["mercado"] = "🇦🇴 BODIVA"
    df_disp = df_disp.rename(columns={"ticker": cols["ticker"], "nome": cols["nome"], "tipo": cols["tipo"],
                                       "preco": cols["preco"], "variacao": cols["variacao"], "mercado": cols["mercado"]})
    df_disp = df_disp[[cols["ticker"], cols["nome"], cols["tipo"], cols["mercado"], cols["preco"], cols["variacao"]]]
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
8. **Regra 50/30/20** — 50% consumo, 30% investimento, 20% entesouramento.
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
    ("SBAAAAAA", "Standard Bank Angola",        "Ação",  45000.0, 0.0),
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

    for titulo, categoria, conteudo in ARTIGOS_INICIAIS:
        if not consultar_um("SELECT 1 FROM artigos WHERE titulo = %s", (titulo,)):
            executar("INSERT INTO artigos (titulo, categoria, conteudo) VALUES (%s, %s, %s)", (titulo, categoria, conteudo))

    if consultar_um("SELECT COUNT(*) FROM premissas_macro")[0] == 0:
        executar("INSERT INTO premissas_macro (id, inflacao, taxa_livre_risco, premio_risco, beta_banca, beta_telecom, beta_outros) VALUES (1, 0.135, 0.18, 0.055, 1.0, 0.9, 1.0)")

    for empresa, sector, preco, acoes, lucro, ganho, cap_proprio, div_total, g in AVALIACOES_INICIAIS:
        if not consultar_um("SELECT 1 FROM avaliacoes WHERE empresa = %s", (empresa,)):
            executar("INSERT INTO avaliacoes (empresa, sector, preco, acoes_circulacao, lucro_liquido, ganho_pontual, capital_proprio, dividendo_total, crescimento_g) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                     (empresa, sector, preco, acoes, lucro, ganho, cap_proprio, div_total, g))


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
    linha = consultar_um("SELECT capital_subscrito, capital_realizado, investimentos, reservas, actualizado_em FROM resumo_patrimonial WHERE id = 1")
    return {"capital_subscrito": float(linha[0] or 0), "capital_realizado": float(linha[1] or 0),
            "investimentos": float(linha[2]), "reservas": float(linha[3]), "actualizado_em": linha[4]}

def actualizar_resumo_patrimonial(capital_subscrito, capital_realizado, investimentos, reservas):
    executar("UPDATE resumo_patrimonial SET capital_social = %s, capital_subscrito = %s, capital_realizado = %s, investimentos = %s, reservas = %s, actualizado_em = NOW() WHERE id = 1",
             (capital_subscrito, capital_subscrito, capital_realizado, investimentos, reservas))
    total = capital_realizado + investimentos + reservas
    executar("INSERT INTO historico_patrimonio (capital_social, investimentos, reservas, total) VALUES (%s, %s, %s, %s)",
             (capital_realizado, investimentos, reservas, total))

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
    executar("INSERT INTO historico_indice_mercado (registado_em, indice_variacao) VALUES (%s, %s) ON CONFLICT (registado_em) DO UPDATE SET indice_variacao = EXCLUDED.indice_variacao",
             (hoje, valor))

def obter_historico_indice() -> pd.DataFrame:
    return consultar_df("SELECT indice_variacao, registado_em FROM historico_indice_mercado ORDER BY registado_em")

def substituir_activos(df: pd.DataFrame):
    executar("DELETE FROM activos")
    for _, linha in df.iterrows():
        nome = str(linha.get("nome", "")).strip()
        if not nome:
            continue
        tipo     = str(linha.get("tipo", "Ação")).strip() or "Ação"
        preco    = float(linha.get("preco", 0) or 0)
        variacao = float(linha.get("variacao", 0) or 0)
        ticker   = str(linha.get("ticker", "") or "").strip().upper()
        executar("INSERT INTO activos (nome, tipo, preco, variacao, ticker) VALUES (%s, %s, %s, %s, %s)", (nome, tipo, preco, variacao, ticker))
    registar_historico_indice(calcular_indice_mercado(obter_activos()))

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
    tx  = t()
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, tx["pdf_titulo"], ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"{tx['pdf_gerado']} {agora()}", ln=True)
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, tx["pdf_resumo"], ln=True)
    pdf.set_font("Helvetica", "", 11)
    capital_subscrito    = resumo["capital_subscrito"]
    capital_realizado    = resumo["capital_realizado"]
    capital_por_realizar = capital_subscrito - capital_realizado
    investimentos        = resumo["investimentos"]
    reservas             = resumo["reservas"]
    # Patrimonio Total = Capital Realizado (investimentos e reservas sao subdivisoes, nao valores adicionais)
    patrimonio_total     = capital_realizado

    pdf.cell(0, 7, f"Capital Subscrito: {kz(capital_subscrito)}", ln=True)
    pdf.cell(0, 7, f"Capital Realizado (ja entregue): {kz(capital_realizado)}", ln=True)
    pdf.cell(0, 7, f"Capital por Realizar: {kz(capital_por_realizar)}", ln=True)
    pdf.cell(0, 7, f"  - dos quais, Investimentos: {kz(investimentos)}", ln=True)
    pdf.cell(0, 7, f"  - dos quais, Reservas: {kz(reservas)}", ln=True)
    pdf.cell(0, 7, f"Patrimonio Total do Clube (= Capital Realizado): {kz(patrimonio_total)}", ln=True)
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, tx["pdf_activos"], ln=True)
    pdf.set_font("Helvetica", "", 10)
    for _, linha in df_activos.iterrows():
        pdf.cell(0, 6, f"- {linha['nome']} ({linha['tipo']}): {kz(linha['preco'])}", ln=True)
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, tx["pdf_movimentos"], ln=True)
    pdf.set_font("Helvetica", "", 10)
    if df_movimentos.empty:
        pdf.cell(0, 6, tx["pdf_sem_mov"], ln=True)
    else:
        for _, linha in df_movimentos.head(30).iterrows():
            pdf.cell(0, 6, f"- {linha['data_movimento']} | {linha['tipo']} | {kz(linha['montante'])} | {linha['descricao'] or ''}", ln=True)
    return bytes(pdf.output())


# ---------------- Avaliação ----------------
def obter_premissas_macro() -> dict:
    linha = consultar_um("SELECT inflacao, taxa_livre_risco, premio_risco, beta_banca, beta_telecom, beta_outros FROM premissas_macro WHERE id = 1")
    return {"inflacao": float(linha[0]), "taxa_livre_risco": float(linha[1]), "premio_risco": float(linha[2]),
            "beta_banca": float(linha[3]), "beta_telecom": float(linha[4]), "beta_outros": float(linha[5])}

def actualizar_premissas_macro(inflacao, rf, erp, beta_banca, beta_telecom, beta_outros):
    executar("UPDATE premissas_macro SET inflacao=%s, taxa_livre_risco=%s, premio_risco=%s, beta_banca=%s, beta_telecom=%s, beta_outros=%s, actualizado_em=NOW() WHERE id = 1",
             (inflacao, rf, erp, beta_banca, beta_telecom, beta_outros))

def obter_avaliacoes() -> pd.DataFrame:
    return consultar_df("SELECT id, empresa, sector, preco, acoes_circulacao, lucro_liquido, ganho_pontual, capital_proprio, dividendo_total, crescimento_g, actualizado_em FROM avaliacoes ORDER BY empresa")

def substituir_avaliacoes(df: pd.DataFrame):
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


inicializar_bd()

# =========================================================
# AUTENTICAÇÃO
# =========================================================
for _k, _v in [("autenticado", False), ("login_timestamp", None), ("conta_nome", ""), ("conta_email", ""), ("is_admin", False), ("is_premium", False)]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

if st.session_state["autenticado"] and st.session_state["login_timestamp"]:
    if time.time() - st.session_state["login_timestamp"] > TEMPO_LIMITE_SESSAO_SEGUNDOS:
        st.session_state["autenticado"] = False
        st.session_state["login_timestamp"] = None
        st.warning("A tua sessão expirou por inactividade. Inicia sessão novamente.")


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
                st.rerun()
            else:
                registar_acesso(email, False)
                st.error(tx["erro_login"])


if not st.session_state["autenticado"]:
    pagina_login()
    st.stop()

# =========================================================
# BARRA LATERAL
# =========================================================
tx = t()
render_html(f'<div class="appo-sidebar-header">{logo_svg(50)}<div><p class="appo-sidebar-sub">Clube de Investimento</p><div class="appo-sidebar-word">APPO</div></div></div>')
st.sidebar.selectbox("🌐 Idioma / Language", LISTA_IDIOMAS, key="idioma")
selo_premium = " · ⭐ Premium" if st.session_state["is_premium"] else ""
st.sidebar.caption(f"{tx['sessao']}: {st.session_state['conta_nome']} ({st.session_state['conta_email']}){selo_premium}")
st.sidebar.divider()

PAGINAS = [
    "🏠 Início & Análises", "📈 Cotações & Activos", "💰 Contabilidade & Finanças",
    "📊 Histórico & Relatórios", "📐 Avaliação de Activos", "💱 Conversor de Moeda",
    "🧪 Simulador de Investimento", "🧮 Regra 50/30/20",
    "📚 Biblioteca Educativa", "🧾 Adesão de Sócios", "ℹ️ Sobre Nós & Estatutos",
]
if st.session_state["is_admin"]:
    PAGINAS.append("🔐 Painel do Administrador")

pagina = st.sidebar.radio("Navegação", PAGINAS, label_visibility="collapsed", format_func=lambda k: tx["nav_map"].get(k, k))

st.sidebar.divider()
if st.sidebar.button(tx["terminar_sessao"]):
    for chave in ["autenticado", "login_timestamp", "conta_id", "conta_nome", "conta_email", "is_admin", "is_premium"]:
        st.session_state.pop(chave, None)
    st.rerun()

st.sidebar.caption(f"Última actualização da página: {agora()}")

_df_activos_ticker = obter_activos()
ticker_tape(_df_activos_ticker)

# =========================================================
# PÁGINA: INÍCIO & ANÁLISES
# =========================================================
if pagina == "🏠 Início & Análises":
    tx = t()
    hero("Clube de Investimento APPO", tx["inicio_hero_sub"])

    resumo = obter_resumo_patrimonial()
    total_patrimonio = resumo["capital_realizado"] + resumo["investimentos"] + resumo["reservas"]

    col1, col2 = st.columns(2)
    col1.metric(tx["inicio_capital_subscrito"], kz(resumo["capital_subscrito"]))
    col2.metric(tx["inicio_capital_realizado"],  kz(resumo["capital_realizado"]),
                delta=(f"{resumo['capital_realizado']/resumo['capital_subscrito']*100:.0f}% {tx['inicio_pct_subscrito']}" if resumo["capital_subscrito"] else None),
                delta_color="off")
    col3, col4, col5 = st.columns(3)
    col3.metric(tx["inicio_investimentos"],   kz(resumo["investimentos"]))
    col4.metric(tx["inicio_reservas"],        kz(resumo["reservas"]))
    col5.metric(tx["inicio_patrimonio_total"], kz(total_patrimonio))

    indice = calcular_indice_mercado(_df_activos_ticker)
    st.metric(tx["inicio_indice_label"], pct_bruto(indice), delta=pct_bruto(indice))
    st.caption(tx["inicio_indice_caption"])
    st.divider()

    st.subheader(tx["inicio_distribuicao"])
    cats = tx["inicio_distribuicao_cats"]
    st.bar_chart(pd.DataFrame({"Categoria": cats,
                               "Montante (Kz)": [resumo["capital_realizado"], resumo["investimentos"], resumo["reservas"]]}).set_index("Categoria"))

    st.divider()
    banner_capa(IMG_GRAFICO, tx["inicio_capa_texto"], altura=130, escurecimento=0.48)

    st.subheader(tx["inicio_cotacoes_destaque"])
    if not _df_activos_ticker.empty:
        st.dataframe(tabela_cotacoes_estilizada(_df_activos_ticker), hide_index=True)

# =========================================================
# PÁGINA: COTAÇÕES & ACTIVOS
# =========================================================
elif pagina == "📈 Cotações & Activos":
    tx = t()
    hero("📈 " + tx["nav_map"]["📈 Cotações & Activos"].replace("📈 ", ""), tx["cot_hero_sub"], "🇦🇴 BODIVA DIRECTA")

    df_activos = _df_activos_ticker
    if df_activos.empty:
        st.info(tx["cot_fav_info"])
    else:
        st.subheader(tx["cot_indice_titulo"])
        indice = calcular_indice_mercado(df_activos)
        col_i1, col_i2 = st.columns([1, 2])
        col_i1.metric(tx["cot_indice_metric"], pct_bruto(indice), delta=pct_bruto(indice))
        col_i1.caption(tx["cot_indice_caption"])
        df_hist_indice = obter_historico_indice()
        with col_i2:
            if len(df_hist_indice) >= 2:
                df_hist_indice["registado_em"] = pd.to_datetime(df_hist_indice["registado_em"])
                st.line_chart(df_hist_indice.set_index("registado_em")[["indice_variacao"]].rename(columns={"indice_variacao": tx["cot_indice_hist_label"]}))
            else:
                st.info(tx["cot_indice_hist_info"])
        st.markdown(tx["cot_tendencia_semanal"])
        if len(df_hist_indice) >= 2:
            df_semanal = df_hist_indice.set_index("registado_em").resample("W")[["indice_variacao"]].mean().rename(columns={"indice_variacao": tx["cot_indice_hist_label"]})
            if len(df_semanal) >= 2:
                st.line_chart(df_semanal)
            else:
                st.caption(tx["cot_tendencia_sem_caption1"])
        else:
            st.caption(tx["cot_tendencia_sem_caption2"])
        st.divider()

        aba_fav, aba_todos = st.tabs([tx["cot_tab_favoritos"], tx["cot_tab_todos"]])
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
                st.dataframe(tabela_cotacoes_estilizada(df_activos[df_activos["nome"].isin(novos_nomes)]), hide_index=True)
            else:
                st.info(tx["cot_fav_info"])

        with aba_todos:
            tipos        = [tx["cot_filtrar_todos"]] + sorted(df_activos["tipo"].unique().tolist())
            filtro_tipo  = st.selectbox(tx["cot_filtrar_tipo"], tipos)
            df_filtrado  = df_activos if filtro_tipo == tx["cot_filtrar_todos"] else df_activos[df_activos["tipo"] == filtro_tipo]
            st.dataframe(tabela_cotacoes_estilizada(df_filtrado), hide_index=True)
            st.caption(f"{tx['cot_ultima_actualizacao']} {df_filtrado['actualizado_em'].max()}")
            st.download_button(tx["cot_descarregar_csv"],
                               data=df_filtrado[["ticker", "nome", "tipo", "preco", "variacao"]].to_csv(index=False).encode("utf-8"),
                               file_name="cotacoes_appo.csv", mime="text/csv")
            st.divider()
            st.subheader(tx["cot_comparacao"])
            cols_tb = tx["cot_tabela_cols"]
            st.bar_chart(df_filtrado.set_index("nome")[["preco"]].rename(columns={"preco": tx["cot_preco_kz"]}))

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
    total_patrimonio = resumo["capital_realizado"] + resumo["investimentos"] + resumo["reservas"]
    st.metric(tx["cont_patrimonio_metric"], kz(total_patrimonio))
    st.caption(f"{tx['cont_ultima_actualizacao']} {resumo['actualizado_em']}")

# =========================================================
# PÁGINA: HISTÓRICO & RELATÓRIOS
# =========================================================
elif pagina == "📊 Histórico & Relatórios":
    tx = t()
    hero("📊 " + tx["nav_map"]["📊 Histórico & Relatórios"].replace("📊 ", ""), tx["hist_hero_sub"])
    df_historico = obter_historico_patrimonio()
    if df_historico.empty or len(df_historico) < 2:
        st.info(tx["hist_poucos_pontos"])
    else:
        st.caption(tx["hist_caption"])
        st.line_chart(df_historico.set_index("registado_em")[["total"]].rename(columns={"total": tx["hist_patrimonio_label"]}))

    st.divider()
    st.subheader(tx["hist_movimentos"])
    df_movimentos = obter_movimentos()
    if df_movimentos.empty:
        st.info(tx["hist_sem_movimentos"])
    else:
        df_exibir = df_movimentos.copy()
        df_exibir["montante_fmt"] = df_exibir["montante"].apply(kz)
        cols_h = tx["hist_cols"]
        st.dataframe(df_exibir[["tipo", "descricao", "montante_fmt", "data_movimento", "criado_em"]].rename(columns=cols_h), hide_index=True)
        st.download_button(tx["hist_descarregar_mov"],
                           data=df_movimentos.to_csv(index=False).encode("utf-8"),
                           file_name="movimentos_appo.csv", mime="text/csv")

    st.divider()
    st.subheader(tx["hist_exportar"])
    if st.button(tx["hist_gerar_pdf"]):
        resumo    = obter_resumo_patrimonial()
        pdf_bytes = gerar_relatorio_pdf(resumo, obter_activos(), df_movimentos)
        nome_pdf  = tx["pdf_nome_ficheiro"].format(data=datetime.now().strftime("%Y%m%d"))
        st.download_button(tx["hist_descarregar_pdf"], data=pdf_bytes, file_name=nome_pdf, mime="application/pdf")

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

            st.download_button(tx["aval_descarregar_comp"],
                               data=df_comp.to_csv(index=False).encode("utf-8"),
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
    st.subheader(tx["conv_historico_titulo"])
    df_hist_cambio = obter_historico_cambio()
    if len(df_hist_cambio) >= 2:
        moeda_grafico = st.selectbox(tx["conv_historico_select"], ["usd", "eur", "gbp", "zar", "cny", "brl"], format_func=lambda x: x.upper())
        st.line_chart(df_hist_cambio.set_index("registado_em")[[moeda_grafico]].rename(
            columns={moeda_grafico: f"{tx['conv_historico_label']} {moeda_grafico.upper()}"}))
        st.caption(tx["conv_historico_caption"])
    else:
        st.info(tx["conv_historico_info"])

# =========================================================
# PÁGINA: SIMULADOR DE INVESTIMENTO — BODIVA VIRTUAL
# =========================================================
elif pagina == "🧪 Simulador de Investimento":
    tx = t()
    hero("🧪 BODIVA Virtual — Simulador de Investimento", "Começa com 3 000 000 Kz e testa as tuas estratégias na bolsa angolana sem risco real", "🎮 Home Broker APPO · Dinheiro Virtual")

    # Inicializar carteira virtual na sessão
    if "sim_carteira" not in st.session_state:
        st.session_state["sim_carteira"] = {}   # {ticker: {"qtd": int, "preco_medio": float}}
        st.session_state["sim_saldo_caixa"] = 3_000_000.0
        st.session_state["sim_historico"] = []  # lista de operações

    df_activos_sim = _df_activos_ticker.copy()

    aba_broker, aba_carteira, aba_compostos = st.tabs(["📊 Home Broker APPO", "💼 Minha Carteira Virtual", "📈 Simulador de Juros Compostos"])

    # ── ABA 1: HOME BROKER ──────────────────────────────────────────
    with aba_broker:
        render_html(f"""
        <div style="background:linear-gradient(120deg,#0B3D91,#1a6fcc); border-radius:12px; padding:16px 20px; margin-bottom:16px; color:#fff;">
            <div style="font-size:0.8rem; opacity:0.8; letter-spacing:1px; text-transform:uppercase;">Saldo disponível em caixa</div>
            <div style="font-size:2.2rem; font-weight:700; margin:4px 0;">{kz(st.session_state['sim_saldo_caixa'])}</div>
            <div style="font-size:0.75rem; opacity:0.7;">💡 Dinheiro virtual — sem risco real · Dotação inicial: 3 000 000 Kz</div>
        </div>
        """)

        if df_activos_sim.empty:
            st.info("Ainda não existem activos cotados para negociar.")
        else:
            col_sel, col_dir = st.columns([1.4, 1])
            with col_sel:
                st.subheader("📋 Painel de Cotações")
                acoes_sim = df_activos_sim[df_activos_sim["tipo"] == "Ação"] if not df_activos_sim.empty else df_activos_sim
                if not acoes_sim.empty:
                    st.dataframe(
                        acoes_sim[["ticker","nome","preco","variacao"]].rename(
                            columns={"ticker":"Ticker","nome":"Activo","preco":"Preço (Kz)","variacao":"Variação (%)"}
                        ).style.format({"Preço (Kz)": kz, "Variação (%)": pct_bruto})
                        .applymap(lambda v: cor_variacao(v), subset=["Variação (%)"]),
                        hide_index=True
                    )

            with col_dir:
                st.subheader("🔄 Ordem de Compra / Venda")
                opcoes_ativos = {f"{r['ticker']} — {r['nome']}": r for _, r in acoes_sim.iterrows()} if not acoes_sim.empty else {}
                if opcoes_ativos:
                    activo_sel_label = st.selectbox("Seleccionar activo", list(opcoes_ativos.keys()))
                    activo_sel = opcoes_ativos[activo_sel_label]
                    preco_unitario = float(activo_sel["preco"])
                    ticker_sel = activo_sel["ticker"]

                    st.metric("Preço unitário", kz(preco_unitario))

                    tipo_ordem = st.radio("Tipo de ordem", ["🟢 Comprar", "🔴 Vender"], horizontal=True)
                    qtd = st.number_input("Quantidade (acções)", min_value=1, value=1, step=1)
                    custo_total = qtd * preco_unitario

                    st.metric("Custo total", kz(custo_total))

                    if tipo_ordem == "🟢 Comprar":
                        pode = st.session_state["sim_saldo_caixa"] >= custo_total
                        if st.button("✅ Executar Compra", disabled=not pode):
                            st.session_state["sim_saldo_caixa"] -= custo_total
                            cart = st.session_state["sim_carteira"]
                            if ticker_sel in cart:
                                total_qtd = cart[ticker_sel]["qtd"] + qtd
                                total_custo = cart[ticker_sel]["qtd"] * cart[ticker_sel]["preco_medio"] + custo_total
                                cart[ticker_sel] = {"qtd": total_qtd, "preco_medio": total_custo / total_qtd, "nome": activo_sel["nome"]}
                            else:
                                cart[ticker_sel] = {"qtd": qtd, "preco_medio": preco_unitario, "nome": activo_sel["nome"]}
                            st.session_state["sim_historico"].append({"op": "COMPRA", "ticker": ticker_sel, "qtd": qtd, "preco": preco_unitario, "total": custo_total})
                            st.success(f"✅ Compra executada: {qtd} × {ticker_sel} a {kz(preco_unitario)}")
                            st.rerun()
                        if not pode:
                            st.warning(f"Saldo insuficiente. Necessitas de {kz(custo_total)} mas tens {kz(st.session_state['sim_saldo_caixa'])}.")
                    else:
                        cart = st.session_state["sim_carteira"]
                        qtd_disponivel = cart.get(ticker_sel, {}).get("qtd", 0)
                        st.caption(f"Tens {qtd_disponivel} acções de {ticker_sel} em carteira.")
                        pode_vender = qtd_disponivel >= qtd
                        if st.button("✅ Executar Venda", disabled=not pode_vender):
                            receita = qtd * preco_unitario
                            st.session_state["sim_saldo_caixa"] += receita
                            cart[ticker_sel]["qtd"] -= qtd
                            if cart[ticker_sel]["qtd"] == 0:
                                del cart[ticker_sel]
                            st.session_state["sim_historico"].append({"op": "VENDA", "ticker": ticker_sel, "qtd": qtd, "preco": preco_unitario, "total": receita})
                            st.success(f"✅ Venda executada: {qtd} × {ticker_sel} a {kz(preco_unitario)}")
                            st.rerun()
                        if not pode_vender:
                            st.warning(f"Não tens acções suficientes para vender ({qtd_disponivel} disponíveis).")

        st.divider()
        st.subheader("📜 Histórico de Ordens")
        if st.session_state["sim_historico"]:
            df_hist_sim = pd.DataFrame(reversed(st.session_state["sim_historico"]))
            df_hist_sim["total"] = df_hist_sim["total"].apply(kz)
            df_hist_sim["preco"] = df_hist_sim["preco"].apply(kz)
            st.dataframe(df_hist_sim.rename(columns={"op":"Operação","ticker":"Ticker","qtd":"Qtd","preco":"Preço Unit.","total":"Total"}), hide_index=True)
        else:
            st.info("Ainda não executaste nenhuma ordem. Começa a negociar no painel acima!")

        if st.button("🔄 Reiniciar carteira virtual (voltar a 3 000 000 Kz)"):
            st.session_state["sim_carteira"] = {}
            st.session_state["sim_saldo_caixa"] = 3_000_000.0
            st.session_state["sim_historico"] = []
            st.rerun()

    # ── ABA 2: CARTEIRA VIRTUAL ──────────────────────────────────────
    with aba_carteira:
        st.subheader("💼 Composição da Minha Carteira Virtual")
        cart = st.session_state["sim_carteira"]
        saldo_caixa = st.session_state["sim_saldo_caixa"]

        if not cart:
            st.info("A tua carteira virtual está vazia. Vai ao Home Broker e compra as tuas primeiras acções!")
        else:
            linhas_cart = []
            valor_total_carteira = saldo_caixa
            for ticker_c, dados_c in cart.items():
                preco_actual = float(df_activos_sim[df_activos_sim["ticker"] == ticker_c]["preco"].values[0]) if ticker_c in df_activos_sim["ticker"].values else dados_c["preco_medio"]
                valor_actual = dados_c["qtd"] * preco_actual
                valor_custo  = dados_c["qtd"] * dados_c["preco_medio"]
                pl           = valor_actual - valor_custo
                pl_pct       = (pl / valor_custo * 100) if valor_custo else 0
                valor_total_carteira += valor_actual
                linhas_cart.append({
                    "Ticker": ticker_c, "Nome": dados_c["nome"],
                    "Qtd": dados_c["qtd"],
                    "Preço Médio": kz(dados_c["preco_medio"]),
                    "Preço Actual": kz(preco_actual),
                    "Valor Actual": kz(valor_actual),
                    "P&L": kz(pl),
                    "P&L (%)": f"{pl_pct:+.2f}%"
                })

            df_cart = pd.DataFrame(linhas_cart)
            st.dataframe(df_cart, hide_index=True)

            col_r1, col_r2, col_r3, col_r4 = st.columns(4)
            col_r1.metric("Saldo em Caixa", kz(saldo_caixa))
            col_r2.metric("Valor em Acções", kz(valor_total_carteira - saldo_caixa))
            col_r3.metric("Patrimônio Total Virtual", kz(valor_total_carteira))
            variacao_total = valor_total_carteira - 3_000_000
            col_r4.metric("Ganho/Perda Total", kz(variacao_total), delta=f"{variacao_total/3_000_000*100:+.2f}%")

            nota_indicador("O <b>P&L</b> (Profit & Loss) mostra o ganho ou perda não realizado em cada posição — a diferença entre o preço que pagaste e o preço actual de mercado.")

        st.divider()
        render_html("""
        <div style="background:#F6EFF2; border-radius:10px; padding:14px 18px; font-size:0.85rem; color:#4A3038;">
            <b>⚠️ Nota importante:</b> Esta é uma carteira <b>completamente virtual</b>. Os preços usados são os que o administrador do Clube actualiza manualmente na plataforma —
            não são cotações em tempo real da BODIVA. O objectivo é <b>aprender a raciocinar como investidor</b> e praticar a construção de carteiras, sem qualquer risco financeiro real.
        </div>
        """)

    # ── ABA 3: JUROS COMPOSTOS ────────────────────────────────────────
    with aba_compostos:
        st.subheader("📈 Simulador de Juros Compostos")
        col1, col2 = st.columns(2)
        valor_inicial  = col1.number_input("Valor inicial (Kz)", min_value=0.0, value=100000.0, step=10000.0)
        contrib_mensal = col2.number_input("Contribuição mensal (Kz)", min_value=0.0, value=20000.0, step=5000.0)
        col3, col4, col5 = st.columns(3)
        taxa_anual   = col3.slider("Taxa de retorno anual esperada (%)", 0.0, 40.0, 12.0, 0.5)
        anos         = col4.slider("Prazo (anos)", 1, 30, 10)
        inflacao_sim = col5.slider("Inflação anual assumida (%)", 0.0, 40.0, 13.5, 0.5)

        taxa_mensal     = (1 + taxa_anual   / 100) ** (1 / 12) - 1
        inflacao_mensal = (1 + inflacao_sim / 100) ** (1 / 12) - 1
        saldo           = valor_inicial
        total_investido = valor_inicial
        pontos = []
        for mes in range(1, anos * 12 + 1):
            saldo           = saldo * (1 + taxa_mensal) + contrib_mensal
            total_investido += contrib_mensal
            if mes % 12 == 0:
                saldo_real = saldo / ((1 + inflacao_mensal) ** mes)
                pontos.append({"Ano": mes // 12, "Saldo Nominal": saldo, "Total Investido": total_investido, "Saldo Real (poder de compra)": saldo_real})

        df_sim = pd.DataFrame(pontos).set_index("Ano")
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Saldo Final (nominal)", kz(saldo))
        col_b.metric("Total Investido", kz(total_investido))
        col_c.metric("Juros Compostos Ganhos", kz(saldo - total_investido))
        st.bar_chart(df_sim[["Saldo Nominal", "Total Investido"]])
        saldo_real_final = df_sim["Saldo Real (poder de compra)"].iloc[-1]
        st.caption(f"Saldo final em poder de compra de hoje (descontada a inflação de {inflacao_sim:.1f}%/ano): {kz(saldo_real_final)}")
        nota_indicador(f"Com inflação de {inflacao_sim:.1f}%/ano, o teu saldo de {kz(saldo)} nominal equivale apenas a {kz(saldo_real_final)} em poder de compra actual. A inflação angolana corrói significativamente os retornos nominais.")
        st.caption("Simulação educativa com juros compostos mensais constantes. Não constitui aconselhamento de investimento.")
        texto_sim = f"Simulei {kz(valor_inicial)} + {kz(contrib_mensal)}/mês durante {anos} anos a {taxa_anual:.1f}%/ano = {kz(saldo)} — Clube de Investimento APPO"
        botoes_partilha(texto_sim)

# =========================================================
# PÁGINA: REGRA 50/30/20
# =========================================================
elif pagina == "🧮 Regra 50/30/20":
    tx = t()
    hero("🧮 " + tx["nav_map"]["🧮 Regra 50/30/20"].replace("🧮 ", ""), tx["r50_hero_sub"], "📐 " + tx["r50_rendimento"])
    rendimento = st.number_input(tx["r50_rendimento"], min_value=0.0, step=5000.0, value=250000.0, format="%.2f")
    alvo_consumo, alvo_inv, alvo_entes = rendimento * 0.50, rendimento * 0.30, rendimento * 0.20

    st.subheader(tx["r50_alocacao"])
    col1, col2, col3 = st.columns(3)
    col1.metric(tx["r50_consumo"],       kz(alvo_consumo))
    col2.metric(tx["r50_investimento"],  kz(alvo_inv))
    col3.metric(tx["r50_entesouramento"],kz(alvo_entes))
    st.bar_chart(pd.DataFrame({"Categoria": [tx["r50_consumo"], tx["r50_investimento"], tx["r50_entesouramento"]],
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

# =========================================================
# PÁGINA: BIBLIOTECA EDUCATIVA
# =========================================================
elif pagina == "📚 Biblioteca Educativa":
    tx = t()
    hero("📚 " + tx["nav_map"]["📚 Biblioteca Educativa"].replace("📚 ", ""), tx["bib_hero_sub"])
    df_artigos = obter_artigos()
    if df_artigos.empty:
        st.info(tx["bib_sem_artigos"])
    else:
        todas_label = tx["bib_todas"]
        categorias  = [todas_label] + sorted(df_artigos["categoria"].unique().tolist())
        filtro      = st.selectbox(tx["bib_filtrar"], categorias)
        filtro_bd   = None if filtro == todas_label else filtro
        for _, artigo in obter_artigos(filtro_bd).iterrows():
            with st.expander(f"{ICONES_CATEGORIA.get(artigo['categoria'], '📄')} {artigo['titulo']}", key=f"artigo_exp_{artigo['id']}"):
                banner_categoria(artigo["categoria"])
                st.caption(f"{tx['bib_publicado']} {artigo['criado_em']}")
                st.markdown(artigo["conteudo"])   # conteúdo mantém-se em PT conforme acordado

# =========================================================
# PÁGINA: ADESÃO DE SÓCIOS
# =========================================================
elif pagina == "🧾 Adesão de Sócios":
    tx = t()
    hero("🧾 " + tx["nav_map"]["🧾 Adesão de Sócios"].replace("🧾 ", ""), tx["ades_hero_sub"])
    with st.form("form_adesao", clear_on_submit=True):
        nome        = st.text_input(tx["ades_nome"])
        col1, col2  = st.columns(2)
        email_ad    = col1.text_input(tx["ades_email"])
        telefone    = col2.text_input(tx["ades_telefone"])
        bi          = st.text_input(tx["ades_bi"])
        contribuicao= st.number_input(tx["ades_contribuicao"], min_value=0.0, step=5000.0)
        aceite      = st.checkbox(tx["ades_aceite"])
        enviar      = st.form_submit_button(tx["ades_btn"])
    if enviar:
        if not nome or not aceite:
            st.error(tx["ades_erro"])
        else:
            inserir_socio(nome, email_ad, telefone, bi, contribuicao)
            st.success(tx["ades_sucesso"])

# =========================================================
# PÁGINA: SOBRE NÓS & ESTATUTOS
# =========================================================
elif pagina == "ℹ️ Sobre Nós & Estatutos":
    tx = t()
    hero("ℹ️ " + tx["nav_map"]["ℹ️ Sobre Nós & Estatutos"].replace("ℹ️ ", ""), tx["sobre_hero_sub"])
    st.subheader(tx["sobre_quem_somos"])
    st.markdown(tx["sobre_quem_texto"])
    st.subheader(tx["sobre_principios"])
    st.markdown(TEXTO_PRINCIPIOS)   # mantém-se em PT
    st.subheader(tx["sobre_estatutos"])
    st.markdown(tx["sobre_estatutos_texto"])
    st.caption(tx["sobre_nota"])

# =========================================================
# PÁGINA: PAINEL DO ADMINISTRADOR (mantém-se em PT)
# =========================================================
elif pagina == "🔐 Painel do Administrador":
    hero("Painel do Administrador", "Gestão de conteúdo, cotações, movimentos, sócios, contas e avaliações")

    aba_resumo, aba_activos, aba_aval, aba_movimentos, aba_biblioteca, aba_socios, aba_contas, aba_seguranca = st.tabs(
        ["Resumo Patrimonial", "Cotações & Activos", "Avaliação", "Movimentos", "Biblioteca", "Sócios", "Contas", "Segurança"])

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

    with aba_activos:
        st.subheader("Editar Cotações & Activos")
        st.caption("Cada vez que guardas, o Índice APPO é recalculado e um novo ponto é registado no histórico.")
        df_activos_admin = obter_activos()
        df_editado = st.data_editor(
            df_activos_admin[["ticker", "nome", "tipo", "preco", "variacao"]], num_rows="dynamic", key="editor_activos",
            column_config={
                "ticker": st.column_config.TextColumn("Ticker", max_chars=12),
                "nome": "Nome do activo", "tipo": "Tipo",
                "preco":    st.column_config.NumberColumn("Preço (Kz)", min_value=0.0, step=0.01, format="%.2f"),
                "variacao": st.column_config.NumberColumn("Variação (%)", step=0.01, format="%.2f"),
            })
        if st.button("Guardar alterações às cotações"):
            substituir_activos(df_editado)
            st.success("Cotações e Índice APPO actualizados com sucesso.")
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
            titulo_artigo   = st.text_input("Título do artigo")
            categoria_artigo= st.selectbox("Categoria", ["Institucional", "Educação", "Análise de Mercado", "Referência"])
            conteudo_artigo = st.text_area("Conteúdo (Markdown suportado)", value=texto_extraido, height=280)
            publicar        = st.form_submit_button("Publicar artigo")
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
            st.dataframe(df_socios_exibir.rename(columns={"nome": "Nome", "email": "E-mail", "telefone": "Telefone",
                                                           "bi": "Nº BI", "contribuicao_inicial": "Contribuição Inicial",
                                                           "criado_em": "Submetido em"}), hide_index=True)

    with aba_contas:
        st.subheader("Criar conta de acesso para um sócio")
        with st.form("form_nova_conta", clear_on_submit=True):
            nome_conta     = st.text_input("Nome completo")
            email_conta    = st.text_input("E-mail (usado para entrar)")
            password_conta = st.text_input("Palavra-passe inicial", type="password")
            admin_conta    = st.checkbox("Esta conta é administradora")
            criar_conta    = st.form_submit_button("Criar conta")
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
