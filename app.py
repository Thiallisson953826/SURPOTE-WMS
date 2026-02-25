import streamlit as st
import re

st.set_page_config(page_title="Suporte WMS", layout="wide")

st.title("📦 Sistema de Suporte WMS")

menu = st.sidebar.selectbox(
    "Selecione o Critério",
    [
        "Recebimento",
        "Armazenagem",
        "Transferência",
        "Inventário",
        "Separação",
        "Expedição"
    ]
)

def validar_nce(nce):
    return bool(re.match(r"^\d{5,14}\.\d+$", nce))

def somente_numeros(valor):
    return valor.isdigit()

def endereco_valido(endereco):
    return bool(re.search(r"[A-Za-z]", endereco) and re.search(r"\d", endereco))

if menu == "Recebimento":
    st.header("📥 Recebimento")
    agenda = st.text_input("Agenda *")
    etiqueta = st.text_input("Etiqueta *")
    nce = st.text_input("NCE * (6 a 15 contendo ponto)")
    nota = st.text_input("Nota (opcional)")
    erro = st.text_area("Detalhar erro por escrita *")

    if st.button("Enviar Recebimento"):
        if not agenda:
            st.error("Agenda obrigatória")
        elif not etiqueta:
            st.error("Etiqueta obrigatória")
        elif not validar_nce(nce):
            st.error("NCE inválido")
        else:
            st.success("Recebimento enviado com sucesso!")

elif menu == "Armazenagem":
    st.header("📦 Armazenagem")
    agenda = st.text_input("Agenda * (somente números)")
    etiqueta = st.text_input("Etiqueta * (somente números)")
    nce = st.text_input("NCE *")
    endereco = st.text_input("Endereço * (letras e números)")
    erro = st.text_area("Detalhar erro por escrita *")

    if st.button("Enviar Armazenagem"):
        if not somente_numeros(agenda):
            st.error("Agenda deve conter apenas números")
        elif not somente_numeros(etiqueta):
            st.error("Etiqueta deve conter apenas números")
        elif not validar_nce(nce):
            st.error("NCE inválido")
        elif not endereco_valido(endereco):
            st.error("Endereço deve conter letras e números")
        else:
            st.success("Armazenagem enviada com sucesso!")

elif menu == "Transferência":
    st.header("🔄 Transferência")
    agenda = st.text_input("Agenda * (somente números)")
    etiqueta = st.text_input("Etiqueta * (somente números)")
    nce = st.text_input("NCE *")
    endereco_origem = st.text_input("Endereço Origem *")
    endereco_destino = st.text_input("Endereço Destino *")
    erro = st.text_area("Detalhar erro por escrita *")

    if st.button("Enviar Transferência"):
        if not somente_numeros(agenda):
            st.error("Agenda deve conter apenas números")
        elif not somente_numeros(etiqueta):
            st.error("Etiqueta deve conter apenas números")
        elif not validar_nce(nce):
            st.error("NCE inválido")
        elif not endereco_valido(endereco_origem):
            st.error("Endereço origem inválido")
        elif not endereco_valido(endereco_destino):
            st.error("Endereço destino inválido")
        else:
            st.success("Transferência enviada com sucesso!")

elif menu == "Inventário":
    st.header("📊 Inventário")
    nce = st.text_input("NCE *")
    endereco_saida = st.text_input("Endereço Saída *")
    endereco_entrada = st.text_input("Endereço Entrada *")
    erro = st.text_area("Detalhar erro por escrita *")

    if st.button("Enviar Inventário"):
        if not validar_nce(nce):
            st.error("NCE inválido")
        elif not endereco_valido(endereco_saida):
            st.error("Endereço saída inválido")
        elif not endereco_valido(endereco_entrada):
            st.error("Endereço entrada inválido")
        else:
            st.success("Inventário enviado com sucesso!")

elif menu == "Separação":
    st.header("📦 Separação")
    carga = st.text_input("Carga * (somente números)")
    numero_sep = st.text_input("Número da Separação * (somente números)")
    nce = st.text_input("NCE *")
    erro = st.text_area("Detalhar erro por escrita *")

    if st.button("Enviar Separação"):
        if not somente_numeros(carga):
            st.error("Carga deve conter apenas números")
        elif not somente_numeros(numero_sep):
            st.error("Número da separação deve conter apenas números")
        elif not validar_nce(nce):
            st.error("NCE inválido")
        else:
            st.success("Separação enviada com sucesso!")

elif menu == "Expedição":
    st.header("🚚 Expedição")
    carga = st.text_input("Carga")
    numero_sep = st.text_input("Número da Separação")
    nce = st.text_input("NCE")
    erro = st.text_area("Detalhar erro por escrita *")

    if st.button("Enviar Expedição"):
        st.success("Expedição enviada com sucesso!")
