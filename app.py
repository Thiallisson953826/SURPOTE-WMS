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
.main {background-color:#f4f6f9;}
.block-container {padding-top:2rem;}
.stButton>button {
    background-color:#004aad;
    color:white;
    border-radius:8px;
    height:40px;
}
.chat-box {
    background:white;
    padding:10px;
    border-radius:8px;
    margin-bottom:5px;
    box-shadow:0px 1px 3px rgba(0,0,0,0.1);
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
    detalhe TEXT,
    status TEXT,
    responsavel TEXT,
    data TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS chat (
    id TEXT,
    mensagem TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS responsaveis (
    nome TEXT UNIQUE
)""")

for nome in ["THIALLISSON","EDVALDO","KELSON","HERNANDES"]:
    try:
        c.execute("INSERT INTO responsaveis VALUES (?)",(nome,))
    except:
        pass

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

# =========================================================
# ================= PERFIL USUÁRIO ========================
# =========================================================

if st.session_state.get("perfil") == "Usuario":

    st.title("WMS - Suporte")

    operacao = st.selectbox("Operação",[
        "Recebimento","Armazenagem","Transferencia",
        "Inventarios","Separação","Expedição"
    ])

    detalhe = st.text_area("Detalhe do Problema *")

    if st.button("Abrir Chamado"):
        if detalhe:
            id_ch = str(uuid.uuid4())[:8]
            data = datetime.now().strftime("%d/%m/%Y %H:%M")

            c.execute("INSERT INTO chamados VALUES (?,?,?,?,?,?,?,?)",
                (id_ch,
                 st.session_state.usuario,
                 st.session_state.origem,
                 operacao,
                 detalhe,
                 "Aberto",
                 "",
                 data))

            c.execute("INSERT INTO chat VALUES (?,?)",
                (id_ch,f"{st.session_state.usuario}: {detalhe}"))

            conn.commit()
            st.success("Chamado aberto com sucesso!")

    st.divider()
    st.subheader("Meus Chamados")

    df = pd.read_sql("SELECT * FROM chamados",conn)
    meus = df[df.usuario == st.session_state.usuario]

    for _,ch in meus.iterrows():

        st.markdown(f"### Chamado {ch.id} - {ch.status}")

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

        st.divider()

# =========================================================
# ================= PERFIL ADMIN ==========================
# =========================================================

if st.session_state.get("perfil") == "Admin":

    st.title("Painel Administrativo")

    menu = st.sidebar.radio("Menu",
        ["Dashboard","Chamados","Responsáveis","Relatório"])

    df = pd.read_sql("SELECT * FROM chamados",conn)

    # DASHBOARD
    if menu == "Dashboard":
        col1,col2,col3,col4 = st.columns(4)
        col1.metric("Total",len(df))
        col2.metric("Aberto",len(df[df.status=="Aberto"]))
        col3.metric("Em Atendimento",len(df[df.status=="Em Atendimento"]))
        col4.metric("Resolvido",len(df[df.status=="Resolvido"]))

        st.subheader("Ranking de Produtividade")
        ranking = df[df.status=="Resolvido"].groupby("responsavel").size()
        st.write(ranking)

    # CHAMADOS
    if menu == "Chamados":

        filtro = st.selectbox("Filtrar por Status",
            ["Todos","Aberto","Em Atendimento","Resolvido"])

        for _,ch in df.iterrows():

            if filtro != "Todos" and ch.status != filtro:
                continue

            st.markdown(f"## Chamado {ch.id} - {ch.status}")
            st.write("Usuário:",ch.usuario)
            st.write("Origem:",ch.origem)
            st.write("Operação:",ch.operacao)
            st.write("Detalhe:",ch.detalhe)

            resps = pd.read_sql("SELECT nome FROM responsaveis",conn)
            lista = [""] + resps["nome"].tolist()

            resp = st.selectbox("Responsável",lista,key="resp"+ch.id)

            if st.button("Assumir Chamado",key="a"+ch.id):
                if resp:
                    c.execute("UPDATE chamados SET responsavel=?, status='Em Atendimento' WHERE id=?",
                        (resp,ch.id))
                    c.execute("INSERT INTO chat VALUES (?,?)",
                        (ch.id,f"Sistema: {resp} assumiu o chamado"))
                    conn.commit()
                    st.rerun()

            if st.button("Resolver Chamado",key="r"+ch.id):
                c.execute("UPDATE chamados SET status='Resolvido' WHERE id=?",(ch.id,))
                conn.commit()
                st.rerun()

            chat_df = pd.read_sql(f"SELECT * FROM chat WHERE id='{ch.id}'",conn)

            for _,m in chat_df.iterrows():
                st.markdown(f"<div class='chat-box'>{m.mensagem}</div>", unsafe_allow_html=True)

            msg = st.text_input("Responder",key="m"+ch.id)
            if st.button("Enviar Resposta",key="e"+ch.id):
                if msg:
                    c.execute("INSERT INTO chat VALUES (?,?)",
                        (ch.id,f"Admin: {msg}"))
                    conn.commit()
                    st.rerun()

            st.divider()

    # RESPONSÁVEIS
    if menu == "Responsáveis":
        novo = st.text_input("Novo Responsável")
        if st.button("Cadastrar"):
            if novo:
                try:
                    c.execute("INSERT INTO responsaveis VALUES (?)",(novo.upper(),))
                    conn.commit()
                    st.success("Responsável cadastrado!")
                except:
                    st.warning("Nome já existe")

        st.write(pd.read_sql("SELECT * FROM responsaveis",conn))

    # RELATÓRIO
    if menu == "Relatório":
        if st.button("Gerar Relatório PDF"):
            doc = SimpleDocTemplate("relatorio.pdf")
            elements = []
            styles = getSampleStyleSheet()

            elements.append(Paragraph("Relatório de Chamados",styles["Title"]))
            elements.append(Spacer(1,0.5*inch))

            data = [["ID","Usuário","Status","Responsável"]]

            for _,ch in df.iterrows():
                data.append([ch.id,ch.usuario,ch.status,ch.responsavel])

            table = Table(data)
            elements.append(table)
            doc.build(elements)

            st.success("Relatório gerado como relatorio.pdf")
