import streamlit as st
import uuid
import re
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="WMS Suporte Profissional", layout="wide")

# ================= SESSION =================
if "chamados" not in st.session_state:
    st.session_state.chamados = {}

if "admin_logado" not in st.session_state:
    st.session_state.admin_logado = False

# ================= FUNÇÕES =================
def validar_nce(nce):
    return re.match(r"^\d{6,}\.\d+$", nce)

def agora():
    return datetime.now().strftime("%d/%m/%Y %H:%M")

# ======================================================
# =================== LOGIN ADMIN =======================
# ======================================================
st.sidebar.title("Administração")
senha = st.sidebar.text_input("Senha Admin", type="password")

if st.sidebar.button("Entrar"):
    if senha == "1234":
        st.session_state.admin_logado = True
    else:
        st.sidebar.error("Senha incorreta")

# ======================================================
# ======================== ADMIN ========================
# ======================================================
if st.session_state.admin_logado:

    st.title("Painel Administrativo")

    chamados = st.session_state.chamados

    total = len(chamados)
    aberto = sum(1 for c in chamados.values() if c["status"]=="Aberto")
    atendimento = sum(1 for c in chamados.values() if c["status"]=="Em Atendimento")
    finalizado = sum(1 for c in chamados.values() if c["status"]=="Finalizado")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total", total)
    c2.metric("Aberto", aberto)
    c3.metric("Em Atendimento", atendimento)
    c4.metric("Finalizado", finalizado)

    st.divider()

    # ===== GRÁFICO POR ORIGEM =====
    if chamados:
        df = pd.DataFrame(chamados.values())
        origem_count = df["origem"].value_counts()

        fig, ax = plt.subplots()
        origem_count.plot(kind="bar", ax=ax)
        st.pyplot(fig)

    st.divider()

    # ===== FILTRO =====
    filtro_status = st.selectbox("Filtrar por Status", ["Todos","Aberto","Em Atendimento","Finalizado"])
    busca_nome = st.text_input("Buscar por Nome")

    chamados_filtrados = {}

    for id_ch, ch in chamados.items():
        if (filtro_status=="Todos" or ch["status"]==filtro_status) and \
           (busca_nome=="" or busca_nome.lower() in ch["nome"].lower()):
            chamados_filtrados[id_ch] = ch

    if chamados_filtrados:

        chamado_id = st.selectbox("Selecionar Chamado", list(chamados_filtrados.keys()))
        chamado = chamados_filtrados[chamado_id]

        st.subheader("Informações")
        st.write("Código:", chamado_id)
        st.write("Nome:", chamado["nome"])
        st.write("Origem:", chamado["origem"])
        st.write("Criado em:", chamado["data"])
        st.write("Status:", chamado["status"])
        st.write("Critério:", chamado["criterio"])
        st.write(chamado["dados"])

        if chamado["status"] != "Finalizado":
            novo_status = st.selectbox("Alterar Status", ["Aberto","Em Atendimento","Finalizado"])
            if st.button("Atualizar Status"):
                chamado["status"] = novo_status
                chamado["chat"].append(f"Sistema: Status alterado para {novo_status}")
                st.rerun()

        st.divider()
        st.subheader("Chat")

        for msg in chamado["chat"]:
            st.write(msg)

        if chamado["status"] != "Finalizado":
            resposta = st.text_input("Responder")
            if st.button("Enviar Resposta"):
                if resposta:
                    chamado["status"] = "Em Atendimento"
                    chamado["chat"].append(f"Admin: {resposta}")
                    st.rerun()

        time.sleep(2)
        st.rerun()

    else:
        st.info("Nenhum chamado encontrado.")

# ======================================================
# ======================= USUÁRIO =======================
# ======================================================
else:

    st.title("Abrir Chamado")

    nome = st.text_input("Seu Nome (simples)")
    origem = st.selectbox("Origem", ["TDC","IDC","PDC","DPC","FLD"])

    criterio = st.selectbox("Critério", [
        "Recebimento",
        "Armazenagem",
        "Inventário",
        "Separação",
        "Expedição"
    ])

    erro = st.text_area("Descreva o problema")
    agenda = st.text_input("Agenda *")
    etiqueta = st.text_input("Etiqueta *")
    nce = st.text_input("NCE (ex: 196369.65421378) *")

    if st.button("Abrir Chamado"):
        if nome and agenda and etiqueta and validar_nce(nce):

            id_chamado = str(uuid.uuid4())[:8]

            st.session_state.chamados[id_chamado] = {
                "nome": nome,
                "origem": origem,
                "criterio": criterio,
                "dados": {
                    "Agenda": agenda,
                    "Etiqueta": etiqueta,
                    "NCE": nce
                },
                "status": "Aberto",
                "data": agora(),
                "chat": [
                    f"Sistema: Chamado aberto em {agora()}",
                    f"Problema: {erro}"
                ]
            }

            st.success(f"Chamado aberto com sucesso! Código: {id_chamado}")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Preencha corretamente os campos obrigatórios.")

    st.divider()
    st.subheader("Consultar Chamado")

    codigo = st.text_input("Digite o código do chamado")

    if codigo in st.session_state.chamados:
        chamado = st.session_state.chamados[codigo]

        st.write("Nome:", chamado["nome"])
        st.write("Status:", chamado["status"])
        st.write("Origem:", chamado["origem"])
        st.write("Criado em:", chamado["data"])

        st.subheader("Chat")

        for msg in chamado["chat"]:
            st.write(msg)

        if chamado["status"] != "Finalizado":
            msg = st.text_input("Enviar mensagem")
            if st.button("Enviar Mensagem"):
                if msg:
                    chamado["chat"].append(f"{chamado['nome']}: {msg}")
                    st.rerun()
    elif codigo != "":
        st.error("Chamado não encontrado.")
