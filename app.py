import streamlit as st
import re

st.set_page_config(page_title="WMS Suporte", layout="wide")

# ===== ESTILO =====
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
.topbar h1 {color: white; margin: 0;}
.card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}
.chat-box {
    background: #ffffff;
    padding: 15px;
    border-radius: 10px;
    height: 300px;
    overflow-y: auto;
    border: 1px solid #ddd;
    margin-bottom: 10px;
}
.user-msg {color: blue;}
.admin-msg {color: green;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="topbar"><h1>📦 WMS Suporte</h1></div>', unsafe_allow_html=True)

# ===== FUNÇÃO VALIDAÇÃO =====
def validar_nce(nce):
    return bool(re.match(r"^\d{5,14}\.\d+$", nce))

# ===== CONTROLE CHAT =====
if "chat_ativo" not in st.session_state:
    st.session_state.chat_ativo = False

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

# ===== PERFIL =====
perfil = st.sidebar.selectbox("Perfil", ["Usuário", "Admin"])

# =====================================================
# ===================== USUÁRIO =======================
# =====================================================
if perfil == "Usuário":

    menu = st.sidebar.radio("Menu", ["Abrir Chamado", "Meu Perfil", "Chat"])

    # -------- ABRIR CHAMADO --------
    if menu == "Abrir Chamado":
        st.subheader("Abrir Chamado")

        operacao = st.selectbox(
            "Operação",
            ["Recebimento", "Armazenagem", "Transferência",
             "Inventário", "Separação", "Expedição"]
        )

        nce = st.text_input("NCE * (ex: 12345.1)")
        descricao = st.text_area("Descreva o problema *")

        if st.button("Abrir Chamado"):
            if not validar_nce(nce) or not descricao:
                st.error("Preencha corretamente os campos obrigatórios.")
            else:
                st.session_state.chat_ativo = True
                st.session_state.mensagens = []
                st.session_state.mensagens.append(
                    {"autor": "admin", "texto": "Chamado recebido. Suporte já está analisando."}
                )
                st.success("Chamado aberto com sucesso! 👇 Chat iniciado.")

        # CHAT AUTOMÁTICO
        if st.session_state.chat_ativo:
            st.subheader("Chat do Chamado")

            st.markdown('<div class="chat-box">', unsafe_allow_html=True)
            for msg in st.session_state.mensagens:
                if msg["autor"] == "usuario":
                    st.markdown(f'<p class="user-msg">Você: {msg["texto"]}</p>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<p class="admin-msg">Suporte: {msg["texto"]}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            nova_msg = st.text_input("Digite sua mensagem")
            if st.button("Enviar"):
                if nova_msg:
                    st.session_state.mensagens.append(
                        {"autor": "usuario", "texto": nova_msg}
                    )
                    st.success("Mensagem enviada!")

    # -------- MEU PERFIL --------
    elif menu == "Meu Perfil":
        st.subheader("Cadastro do Usuário")
        matricula = st.text_input("Matrícula *")
        nome = st.text_input("Nome Completo *")

        if st.button("Salvar Perfil"):
            if not matricula or not nome:
                st.error("Preencha os campos obrigatórios.")
            else:
                st.success("Perfil atualizado com sucesso!")

    # -------- CHAT GERAL --------
    elif menu == "Chat":
        st.subheader("Chat Online")

        if not st.session_state.chat_ativo:
            st.info("Nenhum chamado ativo.")
        else:
            st.markdown('<div class="chat-box">', unsafe_allow_html=True)
            for msg in st.session_state.mensagens:
                if msg["autor"] == "usuario":
                    st.markdown(f'<p class="user-msg">Você: {msg["texto"]}</p>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<p class="admin-msg">Suporte: {msg["texto"]}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            nova_msg = st.text_input("Digite sua mensagem")
            if st.button("Enviar"):
                if nova_msg:
                    st.session_state.mensagens.append(
                        {"autor": "usuario", "texto": nova_msg}
                    )
                    st.success("Mensagem enviada!")

# =====================================================
# ======================= ADMIN =======================
# =====================================================
elif perfil == "Admin":

    menu = st.sidebar.radio("Menu", ["Chamados Abertos", "Chat Online", "Usuários"])

    # -------- TELA PRINCIPAL ADMIN --------
    if menu == "Chamados Abertos":
        st.subheader("Chamados Abertos")

        st.markdown("""
        🔹 Chamado #001 - Recebimento - Em andamento  
        🔹 Chamado #002 - Inventário - Aguardando resposta  
        🔹 Chamado #003 - Separação - Novo  
        """)

    # -------- CHAT ONLINE --------
    elif menu == "Chat Online":
        st.subheader("Chat Online com Usuário")

        if not st.session_state.chat_ativo:
            st.info("Nenhum chamado ativo no momento.")
        else:
            st.markdown('<div class="chat-box">', unsafe_allow_html=True)
            for msg in st.session_state.mensagens:
                if msg["autor"] == "usuario":
                    st.markdown(f'<p class="user-msg">Usuário: {msg["texto"]}</p>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<p class="admin-msg">Você: {msg["texto"]}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            resposta = st.text_input("Responder usuário")
            if st.button("Enviar Resposta"):
                if resposta:
                    st.session_state.mensagens.append(
                        {"autor": "admin", "texto": resposta}
                    )
                    st.success("Resposta enviada!")

    # -------- USUÁRIOS --------
    elif menu == "Usuários":
        st.subheader("Gerenciamento de Usuários")
        st.info("Área reservada para controle de usuários.")
