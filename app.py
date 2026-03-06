import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import io
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Suporte WMS", layout="wide")

# ---------------- BANCO ----------------

conn = sqlite3.connect("chamados.db",check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS chamados(
id INTEGER PRIMARY KEY AUTOINCREMENT,
usuario TEXT,
origem TEXT,
processo TEXT,
dados TEXT,
erro TEXT,
status TEXT,
responsavel TEXT,
data TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS chat(
id INTEGER PRIMARY KEY AUTOINCREMENT,
chamado_id INTEGER,
autor TEXT,
mensagem TEXT,
data TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS responsaveis(
nome TEXT
)
""")

conn.commit()

# responsáveis padrão
padrao = ["Thiallisson","Kelson","Edvaldo","Hernandes"]

for r in padrao:
    if not c.execute("SELECT * FROM responsaveis WHERE nome=?",(r,)).fetchone():
        c.execute("INSERT INTO responsaveis VALUES(?)",(r,))
conn.commit()

# ----------- PDF ------------

def gerar_pdf(ch):

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    p.drawString(50,800,f"Chamado {ch[0]}")
    p.drawString(50,770,f"Usuario: {ch[1]}")
    p.drawString(50,740,f"Origem: {ch[2]}")
    p.drawString(50,710,f"Processo: {ch[3]}")
    p.drawString(50,680,f"Dados: {ch[4]}")
    p.drawString(50,650,f"Erro: {ch[5]}")
    p.drawString(50,620,f"Status: {ch[6]}")
    p.drawString(50,590,f"Responsavel: {ch[7]}")
    p.drawString(50,560,f"Data: {ch[8]}")

    p.save()
    buffer.seek(0)
    return buffer

# ----------- MENU HOME -----------

if "tela" not in st.session_state:
    st.session_state.tela="home"

# HOME
if st.session_state.tela=="home":

    st.title("Sistema Suporte WMS")

    col1,col2 = st.columns(2)

    if col1.button("USUÁRIO"):
        st.session_state.tela="usuario_login"
        st.rerun()

    if col2.button("ADMIN"):
        st.session_state.tela="admin_login"
        st.rerun()

# LOGIN USUARIO
if st.session_state.tela=="usuario_login":

    st.button("HOME",on_click=lambda:st.session_state.update(tela="home"))

    st.title("Login Usuário")

    nome = st.text_input("Nome")

    origem = st.selectbox("Origem",["TDC","IDC","PDC","DPC","FLD"])

    if st.button("Entrar"):

        st.session_state.usuario = nome
        st.session_state.origem = origem
        st.session_state.tela="abrir"
        st.rerun()

# LOGIN ADMIN
if st.session_state.tela=="admin_login":

    st.button("HOME",on_click=lambda:st.session_state.update(tela="home"))

    senha = st.text_input("Senha",type="password")

    if st.button("Entrar"):

        if senha=="1234":
            st.session_state.tela="admin"
            st.rerun()
        else:
            st.error("Senha incorreta")

# ABRIR CHAMADO
if st.session_state.tela=="abrir":

    st.button("HOME",on_click=lambda:st.session_state.update(tela="home"))

    st.title("Abrir Chamado")

    processo = st.selectbox("Processo",[
        "RECEBIMENTO","ARMAZENAGEM","TRANSFERENCIA","INVENTARIOS","SEPARACAO","EXPEDICAO"
    ])

    dados = {}

    if processo=="RECEBIMENTO":

        dados["nota"]=st.text_input("NOTA")
        dados["agenda"]=st.text_input("AGENDA")
        dados["nce"]=st.text_input("NCE")

    if processo=="ARMAZENAGEM":

        dados["agenda"]=st.text_input("AGENDA")
        dados["etiqueta"]=st.text_input("ETIQUETA")
        dados["endereco"]=st.text_input("ENDEREÇO")

    if processo=="TRANSFERENCIA":

        dados["saida"]=st.text_input("ENDEREÇO SAIDA")
        dados["entrada"]=st.text_input("ENDEREÇO ENTRADA")
        dados["nce"]=st.text_input("NCE")

    if processo=="INVENTARIOS":

        dados["nce"]=st.text_input("NCE")
        dados["endereco"]=st.text_input("ENDEREÇO")

    if processo=="SEPARACAO":

        dados["carga"]=st.text_input("CARGA")
        dados["separacao"]=st.text_input("SEPARAÇÃO")
        dados["nota"]=st.text_input("NOTA")

    if processo=="EXPEDICAO":

        dados["carga"]=st.text_input("CARGA")
        dados["separacao"]=st.text_input("SEPARAÇÃO")
        dados["nota"]=st.text_input("NOTA")

    erro = st.text_area("Informação do erro")

    if st.button("ABRIR CHAMADO"):

        c.execute("""
        INSERT INTO chamados(usuario,origem,processo,dados,erro,status,responsavel,data)
        VALUES(?,?,?,?,?,?,?,?)
        """,(
        st.session_state.usuario,
        st.session_state.origem,
        processo,
        str(dados),
        erro,
        "ABERTO",
        "",
        datetime.now().strftime("%d/%m/%Y %H:%M")
        ))

        conn.commit()

        st.success("Chamado aberto")

# ADMIN
if st.session_state.tela=="admin":

    st.button("HOME",on_click=lambda:st.session_state.update(tela="home"))

    st.title("Painel Admin")

    df = pd.read_sql("SELECT * FROM chamados ORDER BY id DESC",conn)

    for i,row in df.iterrows():

        st.markdown("---")

        st.subheader(f"Chamado {row.id}")

        st.write(row.usuario,row.processo,row.status)

        resp = st.selectbox(
            "Responsavel",
            pd.read_sql("SELECT nome FROM responsaveis",conn)["nome"],
            key=row.id
        )

        if st.button("Assumir",key=f"a{row.id}"):

            c.execute("UPDATE chamados SET responsavel=?,status='EM ATENDIMENTO' WHERE id=?",(resp,row.id))
            conn.commit()
            st.rerun()

        # CHAT

        st.write("Chat")

        chat = pd.read_sql(f"SELECT * FROM chat WHERE chamado_id={row.id}",conn)

        for _,m in chat.iterrows():
            st.write(m.autor,":",m.mensagem)

        msg = st.text_input("Mensagem",key=f"m{row.id}")

        if st.button("Enviar",key=f"s{row.id}"):

            c.execute("""
            INSERT INTO chat(chamado_id,autor,mensagem,data)
            VALUES(?,?,?,?)
            """,(row.id,"ADMIN",msg,datetime.now()))

            conn.commit()
            st.rerun()

        # PDF

        chamado = c.execute("SELECT * FROM chamados WHERE id=?",(row.id,)).fetchone()

        pdf = gerar_pdf(chamado)

        st.download_button("Baixar PDF",pdf,file_name=f"chamado_{row.id}.pdf")
