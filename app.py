import streamlit as st
import re

st.set_page_config(page_title="WMS Suporte", layout="wide")

st.markdown("""
<style>
.main {background-color: #f4f6f9;}
header {visibility: hidden;}
.topbar {
    background-color: #0f172a;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 20px;
}
.topbar h1 {
    color: white;
    margin: 0;
}
.card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="topbar"><h1>📦 WMS Suporte</h1></div>', unsafe_allow_html=True)

perfil = st.sidebar.selectbox("Perfil", ["Usuário", "Admin"])

menu_opcoes = ["WMS", "Meu Perfil"]
if perfil == "Admin":
    menu_opcoes.append("Usuários")

menu = st.sidebar.radio("Menu", menu_opcoes)

def validar_nce(nce):
    return bool(re.match(r"^\d{5,14}\.\d+$", nce))

def somente_numeros(valor):
    return valor.isdigit()

def endereco_valido(endereco):
    return bool(re.search(r"[A-Za-z]", endereco) and re.search(r"\d", endereco))

if menu == "WMS":
    st.subheader("Origem do Documento")
    origem = st.radio("", ["TDC", "DPC", "IDC", "PDC", "FLD"], horizontal=True)

    operacao = st.selectbox(
        "Operação",
        ["Recebimento", "Armazenagem", "Transferência", "Inventário", "Separação", "Expedição"]
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)

    if operacao == "Recebimento":
        agenda = st.text_input("Agenda *")
        etiqueta = st.text_input("Etiqueta *")
        nce = st.text_input("NCE * (6 a 15 contendo ponto)")
        erro = st.text_area("Detalhar necessidade *")

        if st.button("Registrar"):
            if not agenda or not etiqueta or not validar_nce(nce):
                st.error("Preencha corretamente os campos obrigatórios")
            else:
                st.success("Chamado enviado ao suporte!")

    elif operacao == "Armazenagem":
        agenda = st.text_input("Agenda *")
        etiqueta = st.text_input("Etiqueta *")
        nce = st.text_input("NCE *")
        endereco = st.text_input("Endereço *")

        if st.button("Registrar"):
            if not somente_numeros(agenda) or not somente_numeros(etiqueta):
                st.error("Agenda e Etiqueta devem conter apenas números")
            elif not validar_nce(nce):
                st.error("NCE inválido")
            elif not endereco_valido(endereco):
                st.error("Endereço inválido")
            else:
                st.success("Chamado enviado ao suporte!")

    elif operacao == "Transferência":
        quantidade = st.text_input("Quantidade *")
        nce = st.text_input("NCE *")

        if st.button("Registrar"):
            if not somente_numeros(quantidade):
                st.error("Quantidade deve conter apenas números")
            elif not validar_nce(nce):
                st.error("NCE inválido")
            else:
                st.success("Chamado enviado ao suporte!")

    elif operacao == "Inventário":
        nce = st.text_input("NCE *")
        saida = st.text_input("Endereço Saída *")
        entrada = st.text_input("Endereço Entrada *")

        if st.button("Registrar"):
            if not validar_nce(nce):
                st.error("NCE inválido")
            elif not endereco_valido(saida) or not endereco_valido(entrada):
                st.error("Endereço inválido")
            else:
                st.success("Chamado enviado ao suporte!")

    elif operacao == "Separação":
        carga = st.text_input("Carga *")
        numero = st.text_input("Número da Separação *")
        nce = st.text_input("NCE *")

        if st.button("Registrar"):
            if not somente_numeros(carga) or not somente_numeros(numero):
                st.error("Carga e Número devem conter apenas números")
            elif not validar_nce(nce):
                st.error("NCE inválido")
            else:
                st.success("Chamado enviado ao suporte!")

    elif operacao == "Expedição":
        st.text_input("Carga")
        st.text_input("Número da Separação")
        st.text_input("NCE")

        if st.button("Registrar"):
            st.success("Chamado enviado ao suporte!")

    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Meu Perfil":
    st.subheader("Cadastro do Usuário")
    matricula = st.text_input("Matrícula *")
    nome = st.text_input("Nome Completo *")

    if st.button("Salvar"):
        if not matricula or not nome:
            st.error("Preencha os campos obrigatórios")
        else:
            st.success("Perfil atualizado com sucesso!")

elif menu == "Usuários" and perfil == "Admin":
    st.subheader("Gerenciamento de Usuários")
    st.info("Área futura para cadastro de usuários.")

