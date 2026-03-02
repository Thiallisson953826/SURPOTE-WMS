import streamlit as st
import uuid
import re
import random
import string

st.set_page_config(page_title="WMS Suporte", layout="wide")

# ================= SESSÃO =================
if "convites" not in st.session_state:
    st.session_state.convites = {}

if "usuarios" not in st.session_state:
    st.session_state.usuarios = {}  # email: {matricula, senha}

if "perfil" not in st.session_state:
    st.session_state.perfil = None

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if "chamados" not in st.session_state:
    st.session_state.chamados = {}

# ================= FUNÇÕES =================
def gerar_token():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def validar_nce(nce):
    return re.match(r"^\d{5,14}\.\d$", nce)

# ================= LOGIN =================
st.sidebar.title("Login")

tipo = st.sidebar.selectbox("Tipo", ["Admin", "Usuário"])

# ===== ADMIN =====
if tipo == "Admin":
    senha = st.sidebar.text_input("Senha Admin", type="password")
    if st.sidebar.button("Entrar"):
        if senha == "1234":
            st.session_state.perfil = "Admin"
            st.session_state.usuario_logado = "admin"
        else:
            st.sidebar.error("Senha incorreta")

# ===== USUÁRIO =====
else:
    opcao = st.sidebar.radio("Acesso", ["Criar Perfil", "Entrar"])

    if opcao == "Criar Perfil":
        email = st.sidebar.text_input("Email")
        token = st.sidebar.text_input("Token")
        matricula = st.sidebar.text_input("Matrícula")
        senha = st.sidebar.text_input("Senha", type="password")

        if st.sidebar.button("Criar"):
            if email in st.session_state.convites and st.session_state.convites[email] == token:
                st.session_state.usuarios[email] = {
                    "matricula": matricula,
                    "senha": senha
                }
                st.success("Perfil criado com sucesso!")
            else:
                st.sidebar.error("Convite inválido")

    if opcao == "Entrar":
        matricula = st.sidebar.text_input("Matrícula")
        senha = st.sidebar.text_input("Senha", type="password")

        if st.sidebar.button("Login"):
            for email, dados in st.session_state.usuarios.items():
                if dados["matricula"] == matricula and dados["senha"] == senha:
                    st.session_state.perfil = "Usuário"
                    st.session_state.usuario_logado = email
                    st.success("Login realizado!")
                    st.rerun()
            st.sidebar.error("Dados inválidos")

# ============================================================
# ========================== ADMIN ===========================
# ============================================================
if st.session_state.perfil == "Admin":

    menu = st.radio("", ["Chamados", "Convidar"], horizontal=True)

    if menu == "Convidar":
        st.title("Convidar Usuário")
        email = st.text_input("Email")
        if st.button("Gerar Convite"):
            token = gerar_token()
            st.session_state.convites[email] = token
            st.success(f"Token gerado: {token}")

    if menu == "Chamados":
        st.title("Chamados Abertos")

        if st.session_state.chamados:
            chamado = st.selectbox("Selecionar", list(st.session_state.chamados.keys()))
            chat = st.session_state.chamados[chamado]["chat"]

            for msg in chat:
                st.write(msg)

            resposta = st.text_input("Responder")
            if st.button("Enviar Resposta"):
                chat.append(f"Admin: {resposta}")
                st.rerun()
        else:
            st.info("Nenhum chamado aberto.")

# ============================================================
# ========================== USUÁRIO =========================
# ============================================================
if st.session_state.perfil == "Usuário":

    menu = st.radio("", ["Novo Registro", "Chat", "Meu Perfil"], horizontal=True)

    # ================= NOVO REGISTRO =================
    if menu == "Novo Registro":
        st.title("Abrir Chamado")

        criterio = st.selectbox("Critério", [
            "Recebimento",
            "Armazenagem",
            "Inventário",
            "Separação",
            "Expedição"
        ])

        erro = st.text_area("Detalhar erro")

        valido = True
        dados = {}

        # ===== RECEBIMENTO =====
        if criterio == "Recebimento":
            agenda = st.text_input("Agenda *")
            etiqueta = st.text_input("Etiqueta *")
            nce = st.text_input("NCE (00000.0) *")
            nota = st.text_input("Nota")

            if st.button("Abrir Chamado"):
                if not agenda or not etiqueta or not validar_nce(nce):
                    valido = False
                else:
                    dados = {
                        "Agenda": agenda,
                        "Etiqueta": etiqueta,
                        "NCE": nce,
                        "Nota": nota
                    }

        # ===== ARMAZENAGEM =====
        if criterio == "Armazenagem":
            agenda = st.text_input("Agenda *")
            etiqueta = st.text_input("Etiqueta *")
            nce = st.text_input("NCE *")
            endereco = st.text_input("Endereço *")

            if st.button("Abrir Chamado"):
                if not agenda.isdigit() or not etiqueta.isdigit() or not validar_nce(nce):
                    valido = False
                else:
                    dados = {
                        "Agenda": agenda,
                        "Etiqueta": etiqueta,
                        "NCE": nce,
                        "Endereço": endereco
                    }

        # ===== INVENTÁRIO =====
        if criterio == "Inventário":
            nce = st.text_input("NCE *")
            saida = st.text_input("Endereço Saída *")
            entrada = st.text_input("Endereço Entrada *")

            if st.button("Abrir Chamado"):
                if not validar_nce(nce):
                    valido = False
                else:
                    dados = {
                        "NCE": nce,
                        "Saída": saida,
                        "Entrada": entrada
                    }

        # ===== SEPARAÇÃO =====
        if criterio == "Separação":
            carga = st.text_input("Carga *")
            numero_sep = st.text_input("Número Separação *")
            nce = st.text_input("NCE *")

            if st.button("Abrir Chamado"):
                if not carga.isdigit() or not numero_sep.isdigit() or not validar_nce(nce):
                    valido = False
                else:
                    dados = {
                        "Carga": carga,
                        "Separação": numero_sep,
                        "NCE": nce
                    }

        # ===== EXPEDIÇÃO =====
        if criterio == "Expedição":
            carga = st.text_input("Carga")
            numero_sep = st.text_input("Número Separação")
            nce = st.text_input("NCE")

            if st.button("Abrir Chamado"):
                dados = {
                    "Carga": carga,
                    "Separação": numero_sep,
                    "NCE": nce
                }

        # ===== FINALIZA ABERTURA =====
        if dados:
            id_chamado = str(uuid.uuid4())[:8]
            st.session_state.chamados[id_chamado] = {
                "usuario": st.session_state.usuario_logado,
                "criterio": criterio,
                "dados": dados,
                "chat": [f"Sistema: Chamado aberto - {criterio}",
                         f"Erro informado: {erro}"]
            }
            st.success("Chamado aberto com sucesso!")
            st.rerun()

    # ================= CHAT =================
    if menu == "Chat":
        chamados_usuario = [
            id for id, dados in st.session_state.chamados.items()
            if dados["usuario"] == st.session_state.usuario_logado
        ]

        if chamados_usuario:
            chamado = st.selectbox("Selecionar chamado", chamados_usuario)
            chat = st.session_state.chamados[chamado]["chat"]

            for msg in chat:
                st.write(msg)

            msg = st.text_input("Mensagem")
            if st.button("Enviar"):
                chat.append(f"Usuário: {msg}")
                st.rerun()
        else:
            st.info("Nenhum chamado aberto.")

    # ================= PERFIL =================
    if menu == "Meu Perfil":
        st.title("Meu Perfil")
        st.write(f"Email: {st.session_state.usuario_logado}")
