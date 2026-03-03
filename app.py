import streamlit as st
import sqlite3
import uuid
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table
from reportlab.lib import colors

st.set_page_config(page_title="WMS Suporte", layout="wide")

# ================= AUTO REFRESH =================
if "perfil" in st.session_state:
    st.autorefresh(interval=3000, key="refresh")

# ================= BANCO =================
conn = sqlite3.connect("wms.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS chamados (
    id TEXT,
    usuario TEXT,
    origem TEXT,
    operacao TEXT,
    dados TEXT,
    detalhe TEXT,
    status TEXT,
    responsavel TEXT,
    data TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS chat (
    id TEXT,
    mensagem TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS responsaveis (
    nome TEXT
)
""")

conn.commit()

# Responsáveis padrão
default_resps = ["THIALLISSON","EDVALDO","KELSON","HERNANDES"]
for r in default_resps:
    c.execute("INSERT OR IGNORE INTO responsaveis (nome) VALUES (?)",(r,))
conn.commit()

# ================= LOGIN =================
st.sidebar.title("Login")
tipo = st.sidebar.radio("Tipo",["Usuário","Admin"])

if tipo == "Usuário":
    nome = st.sidebar.text_input("Nome")
    origem = st.sidebar.selectbox("Origem",["TDC","IDC","PDC","DPC","FLD"])

    if st.sidebar.button("Entrar"):
        if nome:
            st.session_state.perfil="Usuario"
            st.session_state.usuario=nome
            st.session_state.origem=origem
            st.rerun()

if tipo=="Admin":
    senha=st.sidebar.text_input("Senha",type="password")
    if st.sidebar.button("Entrar"):
        if senha=="1234":
            st.session_state.perfil="Admin"
            st.rerun()
        else:
            st.error("Senha incorreta")

# ======================================================
# ================= USUÁRIO ============================
# ======================================================

if st.session_state.get("perfil")=="Usuario":

    st.title("WMS - Suporte")

    operacao=st.selectbox("Operação",[
        "Recebimento","Armazenagem","Transferencia",
        "Inventarios","Separação","Expedição"
    ])

    detalhe=st.text_area("Detalhe do Problema *")

    if st.button("Abrir Chamado"):
        if detalhe:
            id_ch=str(uuid.uuid4())[:8]
            data=datetime.now().strftime("%d/%m/%Y %H:%M")

            c.execute("INSERT INTO chamados VALUES (?,?,?,?,?,?,?,?,?)",
                (id_ch,st.session_state.usuario,
                 st.session_state.origem,operacao,
                 "-",detalhe,"Aberto","",data))
            c.execute("INSERT INTO chat VALUES (?,?)",
                (id_ch,f"{st.session_state.usuario}: {detalhe}"))
            conn.commit()
            st.success("Chamado aberto!")

    st.divider()
    st.subheader("Meus Chamados")

    df=pd.read_sql("SELECT * FROM chamados",conn)

    for _,ch in df[df.usuario==st.session_state.usuario].iterrows():

        st.markdown(f"### {ch.id} - {ch.status}")
        if ch.responsavel:
            st.write("Responsável:",ch.responsavel)

        chat_df=pd.read_sql(f"SELECT * FROM chat WHERE id='{ch.id}'",conn)
        for _,m in chat_df.iterrows():
            st.write(m.mensagem)

        if ch.status!="Resolvido":
            msg=st.text_input("Mensagem",key=ch.id)
            if st.button("Enviar",key="b"+ch.id):
                c.execute("INSERT INTO chat VALUES (?,?)",
                    (ch.id,f"{st.session_state.usuario}: {msg}"))
                c.execute("UPDATE chamados SET status='Em Atendimento' WHERE id=?",(ch.id,))
                conn.commit()
                st.rerun()

# ======================================================
# ================= ADMIN ==============================
# ======================================================

if st.session_state.get("perfil")=="Admin":

    st.title("Painel Administrativo")

    menu=st.sidebar.radio("Menu",
        ["Dashboard","Chamados","Responsáveis","Relatórios"])

    df=pd.read_sql("SELECT * FROM chamados",conn)

    if menu=="Dashboard":

        col1,col2,col3,col4=st.columns(4)
        col1.metric("Total",len(df))
        col2.metric("Aberto",len(df[df.status=="Aberto"]))
        col3.metric("Em Atendimento",len(df[df.status=="Em Atendimento"]))
        col4.metric("Resolvido",len(df[df.status=="Resolvido"]))

        st.subheader("Ranking de Produtividade")

        ranking=df[df.status=="Resolvido"].groupby("responsavel").size()
        st.write(ranking)

        if not ranking.empty:
            plt.figure()
            ranking.plot(kind="bar")
            st.pyplot(plt)

    if menu=="Chamados":

        filtro=st.selectbox("Filtrar",
            ["Todos","Aberto","Em Atendimento","Resolvido"])

        for _,ch in df.iterrows():

            if filtro!="Todos" and ch.status!=filtro:
                continue

            st.markdown(f"## {ch.id} - {ch.status}")
            st.write("Usuário:",ch.usuario)
            st.write("Operação:",ch.operacao)

            resps=pd.read_sql("SELECT nome FROM responsaveis",conn)
            lista=[""]+resps["nome"].tolist()

            resp=st.selectbox("Responsável",lista,key=ch.id)

            if st.button("Assumir",key="a"+ch.id):
                c.execute("UPDATE chamados SET responsavel=?,status='Em Atendimento' WHERE id=?",
                    (resp,ch.id))
                c.execute("INSERT INTO chat VALUES (?,?)",
                    (ch.id,f"Sistema: {resp} assumiu o chamado"))
                conn.commit()
                st.rerun()

            if st.button("Resolver",key="r"+ch.id):
                c.execute("UPDATE chamados SET status='Resolvido' WHERE id=?",(ch.id,))
                conn.commit()
                st.rerun()

            chat_df=pd.read_sql(f"SELECT * FROM chat WHERE id='{ch.id}'",conn)
            for _,m in chat_df.iterrows():
                st.write(m.mensagem)

            msg=st.text_input("Responder",key="m"+ch.id)
            if st.button("Enviar",key="e"+ch.id):
                c.execute("INSERT INTO chat VALUES (?,?)",
                    (ch.id,f"Admin: {msg}"))
                conn.commit()
                st.rerun()

            st.divider()

    if menu=="Responsáveis":

        st.subheader("Cadastrar Novo Responsável")
        novo=st.text_input("Nome")

        if st.button("Cadastrar"):
            c.execute("INSERT INTO responsaveis VALUES (?)",(novo.upper(),))
            conn.commit()
            st.success("Cadastrado!")

        st.subheader("Lista Atual")
        st.write(pd.read_sql("SELECT * FROM responsaveis",conn))

    if menu=="Relatórios":

        if st.button("Gerar Relatório PDF"):
            doc=SimpleDocTemplate("relatorio.pdf")
            elements=[]
            styles=getSampleStyleSheet()

            elements.append(Paragraph("Relatório de Chamados",styles["Title"]))
            elements.append(Spacer(1,0.5*inch))

            data=[["ID","Usuário","Status","Responsável"]]
            for _,ch in df.iterrows():
                data.append([ch.id,ch.usuario,ch.status,ch.responsavel])

            table=Table(data)
            elements.append(table)
            doc.build(elements)

            st.success("Relatório gerado como relatorio.pdf")
