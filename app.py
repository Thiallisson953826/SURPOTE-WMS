import streamlit as st
import uuid

st.set_page_config(page_title="WMS Suporte", layout="wide")

# ================= ESTILO =================
st.markdown("""
<style>
.main {background-color: #0f172a;}
header {visibility: hidden;}

.navbar {
    background-color: #111827;
    padding: 15px 30px;
    border-radius: 12px;
}

.card {
    background: white;
    padding: 25px;
    border-radius: 12px;
    margin-top: 20px;
}

.chat-box {
    background: #f9fafb;
    padding: 15px;
    border-radius: 10px;
    height: 300px;
    overflow-y: auto;
    border: 1px solid #ddd;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ================= SESSION =================
if "convites" not in st.session_state:
    st.session_state.convites = {}

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if "perfil" not in st.session_state:
    st.session_state.perfil = None

if "chat" not in st.session_state:
    st.session_state.chat = []

# ================= LOGIN =================
st.sidebar.title("Login")

tipo = st.sidebar.selectbox("Tipo", ["Admin", "Usuário"])

# ===== ADMIN LOGIN =====
if tipo == "Admin":
    senha = st.sidebar.text_input("Senha Admin", type="password")
    if st.sidebar.button("Entrar"):
        if senha == "1234":   # 🔥 SENHA ALTERADA AQUI
            st.session_state.usuario_logado = "admin"
            st.session_state.perfil = "Admin"
        else:
            st.sidebar.error("Senha incorreta")

# ===== USUÁRIO LOGIN =====
else:
    email = st.sidebar.text_input("Email")
    token = st.sidebar.text_input("Token Convite")
    if st.sidebar.button("Entrar"):
        if email in st.session_state.convites and st.session_state.convites[email] == token:
            st.session_state.usuario_logado = email
            st.session_state.perfil = "Usuário"
        else:
            st.sidebar.error("Convite inválido")

# ================= NAVBAR =================
if st.session_state.perfil:

    if st.session_state.perfil == "Admin":
        menu = st.radio(
            "",
            ["WMS", "Chamados", "Meu Perfil", "Usuários"],
            horizontal=True,
            label_visibility="collapsed"
        )
    else:
        menu = st.radio(
            "",
            ["Novo Registro", "Meu Perfil", "Chat"],
            horizontal=True,
            label_visibility="collapsed"
        )

# =====================================================
# ====================== ADMIN =========================
# =====================================================
if st.session_state.perfil == "Admin":

    if menu == "WMS":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("Painel Administrativo")
        st.write("Visão geral do sistema.")
        st.markdown('</div>', unsafe_allow_html=True)

    if menu == "Chamados":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("Chamados Abertos")
        st.write("🔹 Chamado #001 - Em andamento")
        st.write("🔹 Chamado #002 - Aguardando usuário")
        st.markdown('</div>', unsafe_allow_html=True)

    if menu == "Meu Perfil":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("Perfil Admin")
        st.text_input("Nome")
        st.text_input("Email")
        st.button("Salvar")
        st.markdown('</div>', unsafe_allow_html=True)

    if menu == "Usuários":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("Convidar Usuário")

        novo_email = st.text_input("Email do Usuário")

        if st.button("Enviar Convite"):
            if novo_email:
                token = str(uuid.uuid4())[:8]
                st.session_state.convites[novo_email] = token
                st.success(f"Convite gerado!\n\nEmail: {novo_email}\nToken: {token}")
                st.info("Envie esse token por email ao usuário.")

        st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# ====================== USUÁRIO =======================
# =====================================================
if st.session_state.perfil == "Usuário":

    if menu == "Novo Registro":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("Abrir Chamado")

        operacao = st.selectbox("Operação", [
            "Recebimento",
            "Armazenagem",
            "Transferência",
            "Inventário",
            "Separação",
            "Expedição"
        ])

        nce = st.text_input("NCE (ex: 12345.1)")
        descricao = st.text_area("Descreva o problema")

        if st.button("Abrir Chamado"):
            if nce and descricao:
                st.session_state.chat = []
                st.session_state.chat.append("Suporte: Chamado recebido.")
                st.session_state.chat.append("Suporte: Nosso time já foi notificado.")
                st.success("Chamado aberto! Vá para o Chat.")
                st.rerun()  # 🔥 já atualiza para ir pro chat
            else:
                st.error("Preencha todos os campos.")

        st.markdown('</div>', unsafe_allow_html=True)

    if menu == "Meu Perfil":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("Finalizar Cadastro")
        st.text_input("Nome Completo")
        st.text_input("Matrícula")
        st.button("Salvar Cadastro")
        st.markdown('</div>', unsafe_allow_html=True)

    if menu == "Chat":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("Chat com Suporte")

        st.markdown('<div class="chat-box">', unsafe_allow_html=True)
        for msg in st.session_state.chat:
            st.write(msg)
        st.markdown('</div>', unsafe_allow_html=True)

        nova_msg = st.text_input("Mensagem")
        if st.button("Enviar"):
            if nova_msg:
                st.session_state.chat.append(f"Você: {nova_msg}")
                st.success("Mensagem enviada.")
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
