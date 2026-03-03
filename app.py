import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="SUPORTE WMS", layout="wide")

# =========================
# CSS
# =========================
st.markdown("""
<style>
.main { border-top: 10px solid black; }
div[data-testid="stRadio"] > div {
    background-color: black;
    padding: 10px;
}
div[data-testid="stRadio"] label {
    color: white !important;
    font-weight: bold;
}
.stButton>button {
    background-color: black;
    color: white;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# =========================
# SESSION STATE
# =========================
if "logado" not in st.session_state:
    st.session_state.logado = False

if "perfil" not in st.session_state:
    st.session_state.perfil = ""

if "responsaveis" not in st.session_state:
    st.session_state.responsaveis = ["Thiallisson","Kelson","Edvaldo","Hernandes"]

if "chamados" not in st.session_state:
    st.session_state.chamados = []

# =========================
# LOGIN
# =========================
if not st.session_state.logado:

    st.title("Login - Suporte WMS")

    usuario = st.text_input("Usuário")
    nome = st.text_input("Nome")
    origem = st.selectbox("Origem", ["TDC","IDC","PDC","DPC","FLD"])
    senha = st.text_input("Senha (admin)", type="password")

    if st.button("Entrar"):

        if senha == "1234":
            st.session_state.perfil = "Admin"
        else:
            st.session_state.perfil = "Usuario"

        st.session_state.usuario = usuario
        st.session_state.nome = nome
        st.session_state.origem = origem
        st.session_state.logado = True
        st.rerun()

    st.stop()

# =========================
# MENU
# =========================
menu = st.radio("", ["Abrir Chamado","Admin","Logout"], horizontal=True)

if menu == "Logout":
    st.session_state.logado = False
    st.rerun()

# =========================
# VALIDAR
# =========================
def validar(tipo,dados):
    regras = {
        "Recebimento":["Nota","NCE"],
        "Armazenagem":["Agenda","Etiqueta"],
        "Transferência":["Endereço Saída","Endereço Entrada","NCE"],
        "Inventário":["NCE","Endereço"],
        "Separação":["Carga","Nota"],
        "Expedição":["Carga","Separação","Nota"]
    }
    for campo in regras[tipo]:
        if not dados.get(campo):
            return False,campo
    return True,None

# =========================
# ABRIR CHAMADO
# =========================
if menu == "Abrir Chamado":

    st.title("Abertura de Chamado")

    tipo = st.selectbox("Tipo",["Recebimento","Armazenagem","Transferência","Inventário","Separação","Expedição"])

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
        end_saida = st.text_input("Endereço Saída *")
        end_entrada = st.text_input("Endereço Entrada *")
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

    descricao = st.text_area("Descrição detalhada do erro *")

    responsavel = st.selectbox("Responsável", st.session_state.responsaveis)

    if st.button("Criar Chamado"):

        dados = {
            "Data":datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Tipo":tipo,
            "Nota":nota,
            "Agenda":agenda,
            "NCE":nce,
            "Etiqueta":etiqueta,
            "Endereço":endereco,
            "Endereço Saída":end_saida,
            "Endereço Entrada":end_entrada,
            "Carga":carga,
            "Separação":separacao,
            "Descrição":descricao,
            "Responsável":responsavel,
            "Status":"Aberto",
            "Chat":[]
        }

        valido,campo = validar(tipo,dados)

        if not descricao:
            st.error("Descrição é obrigatória")
        elif not valido:
            st.error(f"Campo obrigatório: {campo}")
        else:
            st.session_state.chamados.append(dados)
            st.success("Chamado criado")

# =========================
# ADMIN
# =========================
if menu == "Admin":

    if st.session_state.perfil != "Admin":
        st.error("Acesso restrito ao Admin")
        st.stop()

    st.title("Painel Administrativo")

    # Gerenciar Responsáveis
    st.subheader("Gerenciar Responsáveis")

    novo_nome = st.text_input("Novo Responsável")
    if st.button("Adicionar"):
        if novo_nome:
            st.session_state.responsaveis.append(novo_nome)

    remover = st.selectbox("Remover Responsável", [""]+st.session_state.responsaveis)
    if st.button("Remover"):
        if remover:
            st.session_state.responsaveis.remove(remover)

    st.divider()

    # Chamados
    for i,ch in enumerate(st.session_state.chamados):

        with st.expander(f"{i+1} - {ch['Tipo']} - {ch['Status']}"):

            st.write(ch)

            novo_status = st.selectbox("Status",["Aberto","Em Atendimento","Finalizado"], key=f"status{i}")
            ch["Status"] = novo_status

            resolvido_por = st.text_input("Resolvido por", key=f"resolvido{i}")
            if resolvido_por:
                ch["Resolvido por"] = resolvido_por

            mensagem = st.text_input("Chat", key=f"chat{i}")
            if st.button("Enviar", key=f"btn{i}"):
                ch["Chat"].append(f"{st.session_state.nome}: {mensagem}")

            for msg in ch["Chat"]:
                st.write(msg)

            if st.button("Excluir Chamado", key=f"exc{i}"):
                st.session_state.chamados.pop(i)
                st.rerun()
