import streamlit as st
import sqlite3
import uuid
from datetime import datetime
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="WMS Suporte", layout="wide")

# ================= AUTO REFRESH =================
st_autorefresh(interval=3000, key="refresh")

# ================= ESTILO =================
st.markdown("""
<style>
.main {background-color:#eef2f7;}
.block-container {padding-top:2rem;}
.card {
    background:white;
    padding:20px;
    border-radius:12px;
    box-shadow:0px 4px 10px rgba(0,0,0,0.05);
    margin-bottom:20px;
}
.chat-box {
    background:#f8f9fa;
    padding:10px;
    border-radius:8px;
    margin-bottom:5px;
}
.stButton>button {
    background-color:#004aad;
    color:white;
    border-radius:8px;
    height:40px;
}
</style>
""", unsafe_allow_html=True)

# ================= BANCO =================
conn = sqlite3.connect("wms.db", check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS chamados (
    id TEXT,
    usuario TEXT,
    origem TEXT,
    operacao TEXT,
    campos TEXT,
    detalhe TEXT,
    status TEXT,
    responsavel TEXT,
    data TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS chat (
    id TEXT,
    mensagem TEXT
)""")

conn.commit()

# ================= LOGIN =================
st.sidebar.title("Login")
tipo = st.sidebar.radio("Tipo de Acesso",["Usuário","Admin"])

if tipo == "Usuário":
    nome = st.sidebar.text_input("Nome")
    origem = st.sidebar.selectbox("Origem",["TDC","IDC","PDC","DPC","FLD"])

    if st.sidebar.button("Entrar"):
        if nome:
            st.session_state.perfil="Usuario"
            st.session_state.usuario=nome
            st.session_state.origem=origem
            st.rerun()

if tipo == "Admin":
    senha = st.sidebar.text_input("Senha",type="password")
    if st.sidebar.button("Entrar"):
        if senha == "1234":
            st.session_state.perfil="Admin"
            st.rerun()
        else:
            st.error("Senha incorreta")

# ======================================================
# ================= USUÁRIO ============================
# ======================================================

if st.session_state.get("perfil") == "Usuario":

    st.title("📦 WMS - Abertura de Chamado")

    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        operacao = st.selectbox("Operação",[
            "Recebimento","Armazenagem","Transferencia",
            "Inventarios","Separação","Expedição"
        ])

        campos = {}
        obrigatorio_ok = True

        # RECEBIMENTO
        if operacao == "Recebimento":
            campos["Nota"] = st.text_input("Nota *")
            campos["Agenda"] = st.text_input("Agenda (Opcional)")
            campos["NCE"] = st.text_input("NCE *")

            if not campos["Nota"] or not campos["NCE"]:
                obrigatorio_ok = False

        # ARMAZENAGEM
        if operacao == "Armazenagem":
            campos["Agenda"] = st.text_input("Agenda *")
            campos["Etiqueta"] = st.text_input("Etiqueta *")
            campos["Endereço"] = st.text_input("Endereço (Opcional)")

            if not campos["Agenda"] or not campos["Etiqueta"]:
                obrigatorio_ok = False

        # TRANSFERENCIA
        if operacao == "Transferencia":
            campos["Endereço Saída"] = st.text_input("Endereço de Saída *")
            campos["Endereço Entrada"] = st.text_input("Endereço de Entrada *")
            campos["NCE"] = st.text_input("NCE *")

            if not campos["Endereço Saída"] or not campos["Endereço Entrada"] or not campos["NCE"]:
                obrigatorio_ok = False

        # INVENTARIOS
        if operacao == "Inventarios":
            campos["NCE"] = st.text_input("NCE *")
            campos["Endereço"] = st.text_input("Endereço *")

            if not campos["NCE"] or not campos["Endereço"]:
                obrigatorio_ok = False

        # SEPARAÇÃO
        if operacao == "Separação":
            campos["Carga"] = st.text_input("Carga *")
            campos["Separação"] = st.text_input("Separação (Opcional)")
            campos["Nota"] = st.text_input("Nota *")

            if not campos["Carga"] or not campos["Nota"]:
                obrigatorio_ok = False

        # EXPEDIÇÃO
        if operacao == "Expedição":
            campos["Carga"] = st.text_input("Carga *")
            campos["Separação"] = st.text_input("Separação *")
            campos["Nota"] = st.text_input("Nota *")

            if not campos["Carga"] or not campos["Separação"] or not campos["Nota"]:
                obrigatorio_ok = False

        detalhe = st.text_area("Detalhe do Problema *")

        if st.button("🚀 Abrir Chamado"):
            if obrigatorio_ok and detalhe:
                id_ch = str(uuid.uuid4())[:8]
                data = datetime.now().strftime("%d/%m/%Y %H:%M")

                c.execute("INSERT INTO chamados VALUES (?,?,?,?,?,?,?,?,?)",
                    (id_ch,
                     st.session_state.usuario,
                     st.session_state.origem,
                     operacao,
                     str(campos),
                     detalhe,
                     "Aberto",
                     "",
                     data))

                c.execute("INSERT INTO chat VALUES (?,?)",
                    (id_ch,f"{st.session_state.usuario}: {detalhe}"))

                conn.commit()
                st.success("Chamado aberto com sucesso!")
            else:
                st.error("Preencha todos os campos obrigatórios!")

        st.markdown("</div>", unsafe_allow_html=True)

    # HISTÓRICO
    st.subheader("📋 Meus Chamados")
    df = pd.read_sql("SELECT * FROM chamados",conn)
    meus = df[df.usuario == st.session_state.usuario]

    for _,ch in meus.iterrows():

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"### Chamado {ch.id} - {ch.status}")
        st.write("Operação:",ch.operacao)
        st.write("Dados:",ch.campos)

        if ch.responsavel:
            st.write("Responsável:",ch.responsavel)

        chat_df = pd.read_sql(f"SELECT * FROM chat WHERE id='{ch.id}'",conn)
        for _,m in chat_df.iterrows():
            st.markdown(f"<div class='chat-box'>{m.mensagem}</div>", unsafe_allow_html=True)

        if ch.status != "Resolvido":
            msg = st.text_input("Mensagem",key=ch.id)
            if st.button("Enviar",key="u"+ch.id):
                if msg:
                    c.execute("INSERT INTO chat VALUES (?,?)",
                        (ch.id,f"{st.session_state.usuario}: {msg}"))
                    c.execute("UPDATE chamados SET status='Em Atendimento' WHERE id=?",(ch.id,))
                    conn.commit()
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
