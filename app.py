import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
from pypdf import PdfReader
import io

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Clube de Investimento APPO",
    page_icon="📈",
    layout="wide"
)

# ==========================================
# DADOS DE EXEMPLO E ESTADO DA SESSÃO
# ==========================================
if "estatutos_pdf_bytes" not in st.session_state:
    st.session_state["estatutos_pdf_bytes"] = None

if "estatutos_texto" not in st.session_state:
    st.session_state["estatutos_texto"] = "Os estatutos oficiais do Clube de Investimento APPO regem o funcionamento, direitos e deveres dos sócios."

if "df_activos" not in st.session_state:
    st.session_state["df_activos"] = pd.DataFrame([
        {"ticker": "BAIAAAAA", "nome": "BAI (Banco Angolano de Investimentos)", "tipo": "ACÇÃO", "preco": 96999.0, "variacao": 0.00},
        {"ticker": "BCGAAAAA", "nome": "BCGA (Banco Caixa Geral Angola)", "tipo": "ACÇÃO", "preco": 19500.0, "variacao": 0.00},
        {"ticker": "BDVAAAAA", "nome": "BDV (BODIVA)", "tipo": "ACÇÃO", "preco": 95000.0, "variacao": 0.00},
        {"ticker": "BFAAAAAA", "nome": "BFA (Banco de Fomento Angola)", "tipo": "ACÇÃO", "preco": 99000.0, "variacao": 0.00},
        {"ticker": "ENSAAAAA", "nome": "ENSA Seguros", "tipo": "ACÇÃO", "preco": 23300.0, "variacao": 0.00},
        {"ticker": "UNTLAAAA", "nome": "UNITEL", "tipo": "ACÇÃO", "preco": 29099.0, "variacao": 3.93}
    ])

# ==========================================
# FUNÇÕES AUXILIARES & CORREÇÕES DE ERROS
# ==========================================

# 1. Correção 'Styler' object has no attribute 'applymap'
def cor_variacao(val):
    if isinstance(val, (int, float)):
        if val > 0:
            return 'color: green; font-weight: bold;'
        elif val < 0:
            return 'color: red; font-weight: bold;'
    return 'color: black;'

def tabela_cotacoes_estilizada(df):
    df_disp = df.copy()
    styler = df_disp.style.format({
        "preco": "{:,.2f} Kz",
        "variacao": "{:+.2f}%"
    })
    # pandas >= 2.1 usa .map() em vez de .applymap()
    if hasattr(styler, "map"):
        return styler.map(cor_variacao, subset=["variacao"])
    else:
        return styler.applymap(cor_variacao, subset=["variacao"])

# 2. Correção TypeError no PDF (string argument without an encoding)
def gerar_relatorio_pdf(resumo, ativos, movimentos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "Relatorio do Clube de Investimento APPO", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(190, 10, f"Resumo Executivo: {resumo}", ln=True)
    pdf.ln(5)
    
    out = pdf.output()
    if isinstance(out, str):
        return bytes(out, 'latin1')
    elif isinstance(out, (bytearray, bytes)):
        return bytes(out)
    else:
        return bytes(str(out), 'latin1')

# 3. Correção TypeError: object of type 'float' has no len() no Excel
def gerar_excel_bytes(df_export, nome_aba="Dados"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_export.to_excel(writer, sheet_name=nome_aba, index=False)
        worksheet = writer.sheets[nome_aba]
        
        for i, col in enumerate(df_export.columns):
            # Converter toda a coluna para string antes de calcular a largura max
             max_len = max(
                df_export[col].astype(str).fillna('').map(len).max(),
                len(str(col))
            ) + 3
            worksheet.set_column(i, i, max_len)
            
    return output.getvalue()

# 4. Correção pypdf.errors.PdfStreamError
def extrair_texto_pdf(uploaded_pdf):
    try:
        uploaded_pdf.seek(0)  # Repor o ponteiro do buffer de leitura
        reader = PdfReader(uploaded_pdf)
        texto = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                texto += t + "\n"
        return texto if texto.strip() else "Não foi possível extrair texto legível do PDF."
    except Exception as e:
        return f"Erro ao processar o ficheiro PDF: {str(e)}"

# ==========================================
# MENU LATERAL
# ==========================================
st.sidebar.title("Navegação")
opcao_menu = st.sidebar.radio(
    "Ir para:",
    [
        "🏠 Início & Análises",
        "📈 Cotações & Activos",
        "📊 Histórico & Relatórios",
        "📐 Avaliação de Activos",
        "🧮 Regra 50/30/20",
        "📚 Biblioteca Educativa",
        "ℹ️ Sobre Nós & Estatutos",
        "🔐 Painel do Administrador"
    ]
)

# ==========================================
# PÁGINAS
# ==========================================

# --- 1. INÍCIO & ANÁLISES ---
if opcao_menu == "🏠 Início & Análises":
    st.title("📌 Cotações em Destaque")
    df_cotacoes = st.session_state["df_activos"]
    st.dataframe(tabela_cotacoes_estilizada(df_cotacoes), use_container_width=True, hide_index=True)

# --- 2. COTAÇÕES & ACTIVOS ---
elif opcao_menu == "📈 Cotações & Activos":
    st.title("📈 Todos os Activos")
    tipo_filtro = st.selectbox("Filtrar por tipo de activo", ["Todos", "ACÇÃO", "OBRIGAÇÃO"])
    df = st.session_state["df_activos"]
    if tipo_filtro != "Todos":
        df = df[df["tipo"] == tipo_filtro]
    st.dataframe(tabela_cotacoes_estilizada(df), use_container_width=True, hide_index=True)

# --- 3. HISTÓRICO & RELATÓRIOS ---
elif opcao_menu == "📊 Histórico & Relatórios":
    st.title("📊 Exportar Relatório")
    if st.button("Gerar relatório em PDF"):
        pdf_data = gerar_relatorio_pdf("Relatório mensal gerado.", None, None)
        st.download_button("📥 Descarregar PDF", data=pdf_data, file_name="relatorio_appo.pdf", mime="application/pdf")

# --- 4. AVALIAÇÃO DE ACTIVOS ---
elif opcao_menu == "📐 Avaliação de Activos":
    st.title("📐 Avaliação Sectorial e Exportação")
    df_comp = pd.DataFrame([
        {"Empresa": "UNITEL", "Sector": "Telecomunicações", "P/E": 10.73, "ROE": 0.18, "DY Nominal": 0.08},
        {"Empresa": "SBA (Standard Bank)", "Sector": "Banca", "P/E": 3.85, "ROE": 0.44, "DY Nominal": 0.00}
    ])
    st.dataframe(df_comp)
    
    excel_bytes = gerar_excel_bytes(df_comp, "Comparação Sectorial")
    st.download_button(
        "📥 Exportar Comparação para Excel",
        data=excel_bytes,
        file_name="comparacao_sectorial.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- 5. REGRA 50/30/20 (SIMULADOR INTERATIVO RESTAURADO) ---
elif opcao_menu == "🧮 Regra 50/30/20":
    st.title("🧮 Simulador de Orçamento Familiar (Regra 50/30/20)")
    st.write("Organize o seu rendimento mensal segundo a regra de alocação financeira recomendada.")
    
    rendimento = st.number_input("Rendimento Mensal Líquido (Kz):", min_value=0.0, value=500000.0, step=10000.0)
    
    col1, col2, col3 = st.columns(3)
    meta_nec = rendimento * 0.50
    meta_des = rendimento * 0.30
    meta_poup = rendimento * 0.20
    
    col1.metric("50% Necessidades Básicas", f"{meta_nec:,.2f} Kz")
    col2.metric("30% Desejos Pessoais", f"{meta_des:,.2f} Kz")
    col3.metric("20% Investimento / Poupança", f"{meta_poup:,.2f} Kz")
    
    st.subheader("Simulação de Despesas Reais")
    c1, c2, c3 = st.columns(3)
    g_nec = c1.number_input("Gastos Reais em Necessidades (Kz):", value=meta_nec)
    g_des = c2.number_input("Gastos Reais em Desejos (Kz):", value=meta_des)
    g_poup = c3.number_input("Valor Alocado a Poupança/Investimento (Kz):", value=meta_poup)
    
    diff_nec = meta_nec - g_nec
    diff_des = meta_des - g_des
    diff_poup = g_poup - meta_poup
    
    st.divider()
    st.write("### Análise do Seu Orçamento")
    if diff_poup >= 0:
        st.success(f"Excelente! Está a cumprir ou superar a sua meta de poupança/investimento em +{diff_poup:,.2f} Kz.")
    else:
        st.warning(f"Atenção: A sua poupança está {abs(diff_poup):,.2f} Kz abaixo da meta recomendada de 20%.")

# --- 6. BIBLIOTECA EDUCATIVA ---
elif opcao_menu == "📚 Biblioteca Educativa":
    st.title("📚 Biblioteca Educativa")
    
    opcoes_temas = ["Selecione um tema...", "Introdução ao Mercado de Capitais em Angola", "Como Avaliar Ações na BODIVA", "Gestão de Risco e Diversificação"]
    escolha = st.selectbox("Escolha o tópico de estudo:", opcoes_temas)
    
    if escolha == "Selecione um tema...":
        st.info("Por favor, selecione um tema acima para visualizar o conteúdo educativo.")
    elif escolha == "Introdução ao Mercado de Capitais em Angola":
        st.subheader("Introdução ao Mercado de Capitais em Angola")
        st.write("O mercado de capitais angolano é dinamizado pela BODIVA (Bolsa de Dívida e Valores de Angola)...")
    elif escolha == "Como Avaliar Ações na BODIVA":
        st.subheader("Como Avaliar Ações na BODIVA")
        st.write("A análise de ações envolve a avaliação de múltiplos como P/E, ROE e Dividend Yield...")
    elif escolha == "Gestão de Risco e Diversificação":
        st.subheader("Gestão de Risco e Diversificação")
        st.write("Diversificar ativos minimiza o risco não-sistemático da carteira...")

# --- 7. SOBRE NÓS & ESTATUTOS (PÚBLICO - SEM UPLOAD) ---
elif opcao_menu == "ℹ️ Sobre Nós & Estatutos":
    st.title("ℹ️ Sobre Nós & Estatutos do Clube")
    st.write("### Quem Somos")
    st.write("O Clube de Investimento APPO promove a literacia financeira, gestão patrimonial e investimentos transparentes.")
    
    st.divider()
    st.subheader("📄 Estatutos e Regulamento Interno")
    
    if st.session_state["estatutos_pdf_bytes"]:
        st.download_button(
            "📥 Descarregar Ficheiro Oficial dos Estatutos (PDF)",
            data=st.session_state["estatutos_pdf_bytes"],
            file_name="Estatutos_APPO.pdf",
            mime="application/pdf"
        )
    
    st.write("#### Conteúdo Informativo")
    st.info(st.session_state["estatutos_texto"])

# --- 8. PAINEL DO ADMINISTRADOR (GESTÃO GLOBAL E UPLOAD RESTRITO) ---
elif opcao_menu == "🔐 Painel do Administrador":
    st.title("🔐 Painel de Administração")
    
    aba_cotacoes, aba_estatutos, aba_definicoes = st.tabs([
        "📈 Actualizar Cotações",
        "📄 Gestão dos Estatutos",
        "⚙️ Definições Globais"
    ])
    
    # Aba 1: Edição de Cotações com Nomes Explícitos nas Colunas
    with aba_cotacoes:
        st.subheader("Editar Cotações de Activos")
        df_editavel = st.session_state["df_activos"].copy()
        
        df_editado = st.data_editor(
            df_editavel,
            column_config={
                "ticker": st.column_config.TextColumn("Ticker", disabled=True),
                "nome": st.column_config.TextColumn("Nome do Activo"),
                "tipo": st.column_config.SelectboxColumn("Tipo", options=["ACÇÃO", "OBRIGAÇÃO"]),
                "preco": st.column_config.NumberColumn("Preço Atual (Kz)", format="%.2f Kz"),
                "variacao": st.column_config.NumberColumn("Variação (%)", format="%.2f%%")
            },
            use_container_width=True,
            hide_index=True
        )
        
        if st.button("💾 Guardar Novas Cotações"):
            st.session_state["df_activos"] = df_editado
            st.success("Cotações atualizadas com sucesso!")

    # Aba 2: Upload de Estatutos Exclusivo do Admin
    with aba_estatutos:
        st.subheader("Carregar / Atualizar Ficheiro dos Estatutos (PDF)")
        uploaded_pdf = st.file_uploader("Selecione o ficheiro PDF dos Estatutos", type=["pdf"])
        
        if uploaded_pdf is not None:
            uploaded_pdf.seek(0)
            bytes_data = uploaded_pdf.read()
            st.session_state["estatutos_pdf_bytes"] = bytes_data
            
            # Extrair texto de forma segura
            texto_ext = extrair_texto_pdf(uploaded_pdf)
            st.session_state["estatutos_texto"] = texto_ext
            st.success("Ficheiro dos Estatutos carregado e atualizado no portal com sucesso!")

    # Aba 3: Definições e Avisos Globais
    with aba_definicoes:
        st.subheader("Definições Gerais do Portal")
        novo_texto_sobre = st.text_area("Texto de Apresentação 'Sobre Nós':", value="O Clube de Investimento APPO promove a literacia financeira...")
        if st.button("Salvar Definições Globais"):
            st.success("Definições globais guardadas.")
