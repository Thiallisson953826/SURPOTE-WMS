import streamlit as st
import uuid
import random
import string

st.set_page_config(page_title="WMS Suporte", layout="wide")

# ================= SESSION =================
if "convites" not in st.session_state:
    st.session_state.convites = {}

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if "perfil" not in st.session_state:
    st.session_state.perfil = None

if "chamados" not in st.session_state:
    st.session_state.chamados = {}

if "chat_ativo" not in st.session_state:
    st.session_state.chat_ativo = None


# ================= FUNÇÃO TOKEN =================
def gerar_token():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


# ================= LOGIN =================
st.sidebar.title("Login")
tipo = st.sidebar.selectbox("Tipo", ["Admin", "Usuário"])

if tipo == "Admin":
    senha = st.sidebar.text_input("Senha Admin", type="password")
    if st.sidebar.button("Entrar"):
        if senha == "1234":
            st.session_state.usuario_logado = "admin"
            st.session_state.perfil = "Admin"
        else:
            st.sidebar.error("Senha incorreta")

else:
    email = st.sidebar.text_input("Email")
    token = st.sidebar.text_input("Token Convite")
    if st.sidebar.button("Entrar"):
        if email in st.session_state.convites and st.session_state.convites[email] == token:
            st.session_state.usuario_logado = email
            st.session_state.perfil = "Usuário"
        else:
            st.sidebar.error("Convite inválido")


# ============================================================
# ============================ ADMIN ==========================
# ============================================================
if st.session_state.perfil == "Admin":

    menu = st.radio("", ["Chamados", "Convidar Usuário"], horizontal=True)

    if menu == "Chamados":
        st.title("Chamados Abertos")

        if st.session_state.chamados:
            chamado_selecionado = st.selectbox(
                "Selecione o chamado",
                list(st.session_state.chamados.keys())
            )

            st.session_state.chat_ativo = chamado_selecionado
            chat = st.session_state.chamados[chamado_selecionado]["chat"]

            st.subheader("Chat")

            for msg in chat:
                st.write(msg)

            resposta = st.text_input("Responder")
            if st.button("Enviar Resposta"):
                if resposta:
                    chat.append(f"Admin: {resposta}")
                    st.rerun()
        else:
            st.info("Nenhum chamado aberto.")

    if menu == "Convidar Usuário":
        st.title("Enviar Convite")
        novo_email = st.text_input("Email do Usuário")

        if st.button("Gerar Convite"):
            if novo_email:
                token = gerar_token()
                st.session_state.convites[novo_email] = token
                st.success(f"Convite gerado!\nEmail: {novo_email}\nToken: {token}")


# ============================================================
# ============================ USUÁRIO ========================
# ============================================================
if st.session_state.perfil == "Usuário":

    menu = st.radio("", ["Novo Registro", "Meu Perfil", "Chat"], horizontal=True)

    # ================= ABRIR CHAMADO =================
    if menu == "Novo Registro":
        st.title("Abrir Chamado")

        operacao = st.selectbox("Operação", [
            "Recebimento",
            "Armazenagem",
            "Transferência",
            "Inventário",
            "Separação",
            "Expedição"
        ])

        descricao = st.text_area("Descreva o problema")

        if st.button("Abrir Chamado"):
            if descricao:
                id_chamado = str(uuid.uuid4())[:8]

                st.session_state.chamados[id_chamado] = {
                    "usuario": st.session_state.usuario_logado,
                    "operacao": operacao,
                    "chat": [f"Sistema: Chamado aberto ({operacao})"]
                }

                st.session_state.chat_ativo = id_chamado
                st.success("Chamado aberto! Vá para o Chat.")
            else:
                st.error("Descreva o problema.")

    # ================= PERFIL =================
    if menu == "Meu Perfil":
        st.title("Meu Perfil")
        st.text_input("Nome Completo")
        st.text_input("Matrícula")
        st.button("Salvar")

    # ================= CHAT =================
    if menu == "Chat":
        st.title("Chat")

        chamados_usuario = [
            id for id, dados in st.session_state.chamados.items()
            if dados["usuario"] == st.session_state.usuario_logado
        ]

        if chamados_usuario:
            chamado_selecionado = st.selectbox("Seu chamado", chamados_usuario)
            chat = st.session_state.chamados[chamado_selecionado]["chat"]

            for msg in chat:
                st.write(msg)

            nova_msg = st.text_input("Mensagem")
            if st.button("Enviar"):
                if nova_msg:
                    chat.append(f"Usuário: {nova_msg}")
                    st.rerun()
        else:
            st.info("Você não possui chamados.")
