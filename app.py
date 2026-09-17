import streamlit as st
import pandas as pd
from PIL import Image
import os

# Configuração da página
st.set_page_config(
    page_title="Clube de Investimento APPO",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# BARRA LATERAL E IDENTIDADE VISUAL
# ---------------------------------------------------------
st.sidebar.markdown("# Clube APPO")
st.sidebar.markdown("---")

# Tentativa de carregar a logomarca se estiver presente no diretório
logo_path = "image_244e62.png"  # Ajuste o nome se necessário
if os.path.exists(logo_path):
    try:
        image = Image.open(logo_path)
        st.sidebar.image(image, use_container_width=True)
    except:
        st.sidebar.info("Logomarca do Clube APPO")
else:
    st.sidebar.markdown("### 🕒 APPO")

st.sidebar.markdown("### Navegação")
menu = st.sidebar.radio(
    "Escolha a secção:",
    ["Painel Principal (Home)", "Orçamento & Rendimentos (50/30/20)", "Património & BODIVA", "Valuation & Análises", "Painel do Administrador"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Estado do Sistema:** Operacional 🟢")
st.sidebar.markdown("**Padrão:** Moeda em Kz (Kwanzas) | PT-AO")

# ---------------------------------------------------------
# 1. PAINEL PRINCIPAL (HOME)
# ---------------------------------------------------------
if menu == "Painel Principal (Home)":
    st.title("Clube de Investimento APPO")
    st.subheader("Painel de Gestão, Controlo Patrimonial e Estratégia")
    
    st.markdown("""
    Bem-vindo à plataforma oficial de gestão do **Clube de Investimento APPO**. 
    Este espaço foi criado para centralizar o planeamento financeiro familiar e os investimentos nos mercados de capitais, com foco primordial no mercado angolano (**BODIVA**).
    """)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Património Global Estimado", value="16 238 319,90 Kz", delta="+12.4% este ano")
    with col2:
        st.metric(label="Investido na BODIVA", value="5 867 524,36 Kz", delta="Ativo na BFA Capital Markets")
    with col3:
        st.metric(label="Reserva / Entesouramento", value="3 247 663,98 Kz", delta="Liquidez Segura")

    st.markdown("---")
    st.markdown("### 👥 Membros Fundadores do Clube")
    
    df_membros = pd.DataFrame({
        "Membro": ["Anibal Alexandre Pereira da Costa (Administrador)", "Cônjuge (Esposa)", "Filho 1", "Filho 2"],
        "Papel / Contributo": ["Gestor / Fundador", "Co-Fundadora", "Membro", "Membro"],
        "Quota Inicial (Kz)": ["5 000 000,00", "1 000 000,00", "500 000,00", "500 000,00"]
    })
    st.dataframe(df_membros, use_container_width=True)

# ---------------------------------------------------------
# 2. ORÇAMENTO & RENDIMENTOS (50/30/20)
# ---------------------------------------------------------
elif menu == "Orçamento & Rendimentos (50/30/20)":
    st.title("Planeamento de Rendimentos e Orçamento")
    st.markdown("Gestão baseada no Título de Vencimento (Faculdade de Economia de Benguela / AFAN) aplicando a regra estrita de alocação: **50% Consumo, 30% Investimento, 20% Reserva**.")

    # Dados base retirados do recibo de vencimento apresentado
    salario_liquido = 878319.90
    fundo_afan_pendente = 7500000.00 # A receber até ao final do ano da AFAN na Catumbela

    st.markdown("### 📊 Análise do Vencimento Atual (Junho/2026)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Líquido Mensal", f"{salario_liquido:,.2f} Kz")
        consumo = salario_liquido * 0.50
        investimento = salario_liquido * 0.30
        reserva = salario_liquido * 0.20
        
        st.markdown(f"""
        * **Consumo (50%):** `{consumo:,.2f} Kz`
        * **Investimento BODIVA (30%):** `{investimento:,.2f} Kz`
        * **Reserva / Entesouramento (20%):** `{reserva:,.2f} Kz`
        """)
    with col2:
        st.markdown("### 🏛️ Crédito a Receber (AFAN - Catumbela)")
        st.info(f"Montante devido pela Academia da Força Aérea: **{fundo_afan_pendente:,.2f} Kz** (Previsão de entrada até ao final do ano).")
        reserva_afan = fundo_afan_pendente * 0.20
        invest_afan = fundo_afan_pendente * 0.80
        st.markdown(f"""
        * Destino da Reserva (20%): `{reserva_afan:,.2f} Kz`
        * Destino para Investimento BODIVA (80% / restante): `{invest_afan:,.2f} Kz`
        """)

# ---------------------------------------------------------
# 3. PATRIMÓNIO & BODIVA
# ---------------------------------------------------------
elif menu == "Património & BODIVA":
    st.title("Gestão de Ativos e Posições na BODIVA")
    st.markdown("Controlo detalhado da carteira de títulos negociados via BFA Capital Markets, discriminando o saldo disponível do capital cativo em subscrições.")

    st.markdown("### 💼 Posições Atuais em Carteira")
    df_carteira = pd.DataFrame({
        "Título": ["ENSA ACÇÃO", "BFA ACÇÃO", "BFA AÇÃO"],
        "Mercado": ["BODIVA ACÇÕES", "BODIVA ACÇÕES", "BODIVA ACÇÕES"],
        "Quantidade": [36, 4, 1],
        "Aquisição (Kz)": ["1 301 041,33", "362 651,48", "193 832,41"],
        "Valor Atual (Kz)": ["1 130 904,00", "360 000,00", "190 000,00"],
        "Estado": ["Ativo", "Ativo", "Ativo"]
    })
    st.dataframe(df_carteira, use_container_width=True)

    st.markdown("### 🔒 Ordens e Subscrições Cativas (Bookbuilding)")
    st.markdown("""
    *Os valores abaixo encontram-se cativos em subscrições e ordens ainda não totalmente executadas, não fazendo parte do saldo livre de negociação imediata.*
    """)
    df_cativos = pd.DataFrame({
        "ID Ordem": ["2026W-XW0HXF1Q3ZA", "2026W-0H0H9HYDI277", "2026M-ID-0307936476"],
        "Título": ["ENSA ACÇÃO", "BFA ACÇÃO", "ENSA ACÇÃO"],
        "Tipo": ["Bookbuilding", "Pore.com.", "Publicidade Geral"],
        "Montante Cativo (Kz)": ["500 000,00", "350 000,00", "10 000,00"],
        "Estado": ["Emitida / Cativo", "Pendente", "Ativa"]
    })
    st.dataframe(df_cativos, use_container_width=True)

# ---------------------------------------------------------
# 4. VALUATION & ANÁLISES
# ---------------------------------------------------------
elif menu == "Valuation & Análises":
    st.title("Serviços de Análise e Valuation")
    st.markdown("Ferramentas de avaliação de empresas cotadas e curadoria de inteligência de mercado nacional e internacional.")

    tab1, tab2 = st.tabs(["Valuation Básica (Grátis)", "Relatórios e Bastidores (Premium)"])

    with tab1:
        st.subheader("Ferramenta de Valuation Simplificada (Metodologia Li Lu / Damodaran)")
        st.markdown("Insira os parâmetros fundamentais para estimar o valor intrínseco básico de um ativo:")
        
        lucro_acao = st.number_input("Lucro por Ação (LPA / EPS em Kz):", value=150.0)
        crescimento_estimado = st.slider("Taxa de Crescimento Esperada (%)", 0.0, 30.0, 8.0)
        taxa_desconto = st.slider("Taxa de Desconto / WACC (%)", 5.0, 25.0, 12.0)
        
        if st.button("Calcular Valuation Teórico"):
            valor_intrinsico = lucro_acao * (1 + crescimento_estimado/100) / (taxa_desconto/100)
            st.success(f"O Valor Intrínseco Estimado por Ação é de aproximadamente **{valor_intrinsico:,.2f} Kz**.")

    with tab2:
        st.subheader("📚 Curadoria de Fontes Especializadas")
        st.markdown("""
        Aceda a relatórios e análises aprofundadas de referência:
        * **Nacionais:** [BODIVA](https://www.bodiva.ao/), [IGAPE Relatórios](https://igape.minfin.gov.ao/sep/relatorios), [KitadInvest Stocks](https://kitadinvest.com/stocks), [Eaglestone](https://www.eaglestone.eu/pt/o-grupo/sobre/), [360 Angola](https://360angola.com/).
        * **Internacionais & Banca em Análise:** [Bloomberg](https://www.bloomberg.com.br/sobre-a-bloomberg/), [Deloitte Angola (Banca em Análise)](https://www.deloitte.com/), Revista Expansão, Exame, e [EFG Hermes](https://efghermesresearch.com/home).
        """)

# ---------------------------------------------------------
# 5. PAINEL DO ADMINISTRADOR
# ---------------------------------------------------------
elif menu == "Painel do Administrador":
    st.title("Área de Gestão e Publicação do Administrador")
    st.markdown("Publique orientações estratégicas, notas de mercado ou artigos diretamente para os membros e visitantes do clube, sem necessidade de editar o código-fonte.")

    senha = st.text_input("Palavra-passe de Administrador:", type="password")
    
    if senha == "appo2026": # Palavra-passe configurável
        st.success("Acesso autorizado com sucesso!")
        
        titulo_artigo = st.text_input("Título da Publicação / Orientação:")
        conteudo_artigo = st.text_area("Corpo do Artigo / Nota:")
        
        if st.button("Publicar na Aplicação"):
            if titulo_artigo and conteudo_artigo:
                st.success(f"Artigo '{titulo_artigo}' publicado com sucesso na página pública!")
                # Aqui registaria o artigo num ficheiro ou base de dados local
            else:
                st.warning("Preencha todos os campos antes de publicar.")
    elif senha != "":
        st.error("Palavra-passe incorreta.")
