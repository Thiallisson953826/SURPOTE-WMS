import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================

st.set_page_config(
    page_title="SUPORTE WMS",
    layout="wide"
)

# ==========================================
# CSS PERSONALIZADO
# ==========================================

st.markdown("""
<style>

html, body, [class*="css"]  {
    font-family: Arial;
}

.main {
    border-top: 10px solid black;
}

div[data-testid="stRadio"] > div {
    background-color: black;
    padding: 15px;
    border-radius: 0 0 15px 15px;
}

div[data-testid="stRadio"] label {
    color: white !important;
    font-weight: bold;
}

.stButton>button {
    background-color: black;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    height: 45px;
}

.stTextInput>div>div>input {
    border: 2px solid black;
}

.stSelectbox>div>div {
    border: 2px solid black;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE
# ==========================================

if "chamados" not in st.session_state:
    st.session_state.chamados = pd.DataFrame(
        columns=[
            "Data",
            "Tipo",
            "Nota",
            "Agenda",
            "NCE",
            "Etiqueta",
            "Endereço",
            "Endereço Saída",
            "Endereço Entrada",
            "Carga",
            "Separação"
        ]
    )

# ==========================================
# FUNÇÃO VALIDAR CAMPOS
# ==========================================

def validar_campos(tipo, dados):
    obrigatorios = []

    if tipo == "Recebimento":
        obrigatorios = ["Nota", "NCE"]

    elif tipo == "Armazenagem":
        obrigatorios = ["Agenda", "Etiqueta"]

    elif tipo == "Transferência":
        obrigatorios = ["Endereço Saída", "Endereço Entrada", "NCE"]

    elif tipo == "Inventário":
        obrigatorios = ["NCE", "Endereço"]

    elif tipo == "Separação":
        obrigatorios = ["Carga", "Nota"]

    elif tipo == "Expedição":
        obrigatorios = ["Carga", "Separação", "Nota"]

    for campo in obrigatorios:
        if not dados.get(campo):
            return False, campo

    return True, None

# ==========================================
# FUNÇÃO ABRIR CHAMADO
# ==========================================

def abrir_chamado():

    st.title("Abertura de Chamado")

    tipo = st.selectbox("Tipo de Operação", [
        "Recebimento",
        "Armazenagem",
        "Transferência",
        "Inventário",
        "Separação",
        "Expedição"
    ])

    nota = agenda = nce = etiqueta = endereco = ""
    end_saida = end_entrada = carga = separacao = ""

    if tipo == "Recebimento":
        nota = st.text_input("Nota *")
        agenda = st.text_input("Agenda (Opcional)")
        nce = st.text_input("NCE *")

    elif tipo == "Armazenagem":
        agenda = st.text_input("Agenda *")
        etiqueta = st.text_input("Etiqueta *")
        endereco = st.text_input("Endereço (Opcional)")

    elif tipo == "Transferência":
        end_saida = st.text_input("Endereço de Saída *")
        end_entrada = st.text_input("Endereço de Entrada *")
        nce = st.text_input("NCE *")

    elif tipo == "Inventário":
        nce = st.text_input("NCE *")
        endereco = st.text_input("Endereço *")

    elif tipo == "Separação":
        carga = st.text_input("Carga *")
        separacao = st.text_input("Separação (Opcional)")
        nota = st.text_input("Nota *")

    elif tipo == "Expedição":
        carga = st.text_input("Carga *")
        separacao = st.text_input("Separação *")
        nota = st.text_input("Nota *")

    if st.button("Criar Chamado"):

        dados = {
            "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Tipo": tipo,
            "Nota": nota,
            "Agenda": agenda,
            "NCE": nce,
            "Etiqueta": etiqueta,
            "Endereço": endereco,
            "Endereço Saída": end_saida,
            "Endereço Entrada": end_entrada,
            "Carga": carga,
            "Separação": separacao
        }

        valido, campo = validar_campos(tipo, dados)

        if not valido:
            st.error(f"O campo '{campo}' é obrigatório!")
            return

        novo_df = pd.DataFrame([dados])
        st.session_state.chamados = pd.concat(
            [st.session_state.chamados, novo_df],
            ignore_index=True
        )

        st.success("Chamado criado com sucesso!")

# ==========================================
# FUNÇÃO ADMIN
# ==========================================

def tela_admin():

    st.title("Painel Administrativo")

    df = st.session_state.chamados

    if df.empty:
        st.warning("Nenhum chamado registrado.")
        return

    st.dataframe(df, use_container_width=True)

    st.subheader("Filtros")

    filtro_tipo = st.selectbox(
        "Filtrar por Tipo",
        ["Todos"] + list(df["Tipo"].unique())
    )

    if filtro_tipo != "Todos":
        df = df[df["Tipo"] == filtro_tipo]

    st.dataframe(df, use_container_width=True)

    if st.button("Limpar Todos Chamados"):
        st.session_state.chamados = df.iloc[0:0]
        st.success("Chamados apagados.")

# ==========================================
# MENU SUPERIOR
# ==========================================

menu = st.radio(
    "",
    ["Abrir Chamado", "Admin"],
    horizontal=True
)

# ==========================================
# RENDERIZAÇÃO
# ==========================================

if menu == "Abrir Chamado":
    abrir_chamado()

elif menu == "Admin":
    tela_admin()
