import streamlit as st
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Sistema de Chamados", layout="wide")

# ---------------- BANCO ----------------
conn = sqlite3.connect("chamados.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS chamados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT,
    titulo TEXT,
    descricao TEXT,
    prioridade TEXT,
    categoria TEXT,
    status TEXT,
    responsavel TEXT,
    data TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS chat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chamado_id INTEGER,
    autor TEXT,
    mensagem TEXT,
    data TEXT
)
""")

conn.commit()

# ---------------- CSS BONITO ----------------
st.markdown("""
<style>
.big-title {font-size:28px;font-weight:bold;color:#1f77b4;}
.card {
    background-color:#f8f9fa;
    padding:15px;
    border-radius:10px;
    margin-bottom:10px;
}
.stButton>button {
    border-radius:8px;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN ----------------
st.markdown("<div class='big-title'>🎫 Sistema de Chamados</div>", unsafe_allow_html=True)

perfil = st.sidebar.selectbox("Tipo de acesso", ["Usuário", "Admin"])

# =====================================================
# ===================== USUÁRIO =======================
# =====================================================
if perfil == "Usuário":

    st.subheader("Abrir Chamado")

    usuario = st.text_input("Seu Nome")
    titulo = st.text_input("Título do Problema")

    categoria = st.selectbox(
        "Categoria",
        ["Sistema", "Coletor", "Rede", "Estoque", "Outro"]
    )

    prioridade = st.selectbox(
        "Prioridade",
        ["Baixa", "Média", "Alta", "Urgente"]
    )

    descricao = st.text_area("Descreva o problema")

    if st.button("🚀 Abrir Chamado", type="primary"):

        if not usuario or not titulo or not descricao:
            st.error("Preencha todos os campos obrigatórios!")
        else:
            c.execute("""
                INSERT INTO chamados 
                (usuario, titulo, descricao, prioridade, categoria, status, responsavel, data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                usuario,
                titulo,
                descricao,
                prioridade,
                categoria,
                "Aberto",
                "",
                datetime.now().strftime("%d/%m/%Y %H:%M")
            ))
            conn.commit()
            st.success("Chamado aberto com sucesso!")

# =====================================================
# ====================== ADMIN ========================
# =====================================================
if perfil == "Admin":

    abas = st.tabs(["📋 Chamados", "💬 Chat"])

    # ---------------- LISTA CHAMADOS ----------------
    with abas[0]:

        st.subheader("Chamados Recebidos")

        chamados = c.execute("SELECT * FROM chamados ORDER BY id DESC").fetchall()

        for ch in chamados:
            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)

                st.markdown(f"""
                **ID:** {ch[0]}  
                **Usuário:** {ch[1]}  
                **Título:** {ch[2]}  
                **Categoria:** {ch[5]}  
                **Prioridade:** {ch[4]}  
                **Status:** {ch[6]}  
                **Responsável:** {ch[7] if ch[7] else 'Não definido'}  
                **Data:** {ch[8]}
                """)

                col1, col2 = st.columns(2)

                with col1:
                    novo_resp = st.text_input(
                        f"Definir responsável ID {ch[0]}",
                        key=f"resp_{ch[0]}"
                    )
                    if st.button(f"Designar ID {ch[0]}", key=f"btn_{ch[0]}"):
                        c.execute("""
                            UPDATE chamados 
                            SET responsavel=?, status='Em Atendimento'
                            WHERE id=?
                        """, (novo_resp, ch[0]))
                        conn.commit()
                        st.success("Responsável definido!")

                with col2:
                    if st.button(f"Encerrar ID {ch[0]}", key=f"close_{ch[0]}"):
                        c.execute("""
                            UPDATE chamados 
                            SET status='Finalizado'
                            WHERE id=?
                        """, (ch[0],))
                        conn.commit()
                        st.success("Chamado encerrado!")

                st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- CHAT ----------------
    with abas[1]:

        st.subheader("Chat do Chamado")

        chamado_id = st.number_input("Digite o ID do chamado", min_value=1, step=1)

        mensagens = c.execute(
            "SELECT * FROM chat WHERE chamado_id=? ORDER BY id",
            (chamado_id,)
        ).fetchall()

        for msg in mensagens:
            st.write(f"**{msg[2]}:** {msg[3]} ({msg[4]})")

        nova_msg = st.text_input("Mensagem")
        if st.button("Enviar Mensagem"):

            if nova_msg:
                c.execute("""
                    INSERT INTO chat (chamado_id, autor, mensagem, data)
                    VALUES (?, ?, ?, ?)
                """, (
                    chamado_id,
                    "Admin",
                    nova_msg,
                    datetime.now().strftime("%d/%m/%Y %H:%M")
                ))
                conn.commit()
                st.success("Mensagem enviada!")
