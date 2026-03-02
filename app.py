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
    st.session_state.usuarios = {}

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
    if not nce:
        return False
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
            st.rerun()
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
                st.success("Perfil criado!")
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

        if st.button("Gerar Token"):
            token = gerar_token()
            st.session_state.convites[email] = token
            st.success(f"Token: {token}")

    if menu == "Chamados":
        st.title("Chamados Abertos")

        if st.session_state.chamados:
            chamado = st.selectbox("Selecionar", list(st.session_state.chamados.keys()))
            dados = st.session_state.chamados[chamado]

            st.subheader("Dados")
            st.write(dados["criterio"])
            st.write(dados["dados"])

            st.subheader("Chat")
            for msg in dados["chat"]:
                st.write(msg)

            resposta = st.text_input("Responder")
            if st.button("Enviar Resposta"):
                if resposta:
                    dados["chat"].append(f"Admin: {resposta}")
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

        with st.form("form_chamado"):

            criterio = st.selectbox("Critério", [
                "Recebimento",
                "Armazenagem",
                "Inventário",
                "Separação",
                "Expedição"
            ])

            erro = st.text_area("Detalhar erro")

            agenda = etiqueta = nce = nota = endereco = ""
            carga = numero_sep = saida = entrada = ""

            if criterio == "Recebimento":
                agenda = st.text_input("Agenda *")
                etiqueta = st.text_input("Etiqueta *")
                nce = st.text_input("NCE (00000.0) *")
                nota = st.text_input("Nota")

            elif criterio == "Armazenagem":
                agenda = st.text_input("Agenda *")
                etiqueta = st.text_input("Etiqueta *")
                nce = st.text_input("NCE *")
                endereco = st.text_input("Endereço *")

            elif criterio == "Inventário":
                nce = st.text_input("NCE *")
                saida = st.text_input("Endereço Saída *")
                entrada = st.text_input("Endereço Entrada *")

            elif criterio == "Separação":
                carga = st.text_input("Carga *")
                numero_sep = st.text_input("Número Separação *")
                nce = st.text_input("NCE *")

            elif criterio == "Expedição":
                carga = st.text_input("Carga")
                numero_sep = st.text_input("Número Separação")
                nce = st.text_input("NCE")

            submitted = st.form_submit_button("Abrir Chamado")

            if submitted:

                valido = True
                dados = {}

                if criterio == "Recebimento":
                    if not agenda or not etiqueta or not validar_nce(nce):
                        valido = False
                    else:
                        dados = {"Agenda": agenda, "Etiqueta": etiqueta, "NCE": nce, "Nota": nota}

                elif criterio == "Armazenagem":
                    if not agenda or not etiqueta or not validar_nce(nce) or not endereco:
                        valido = False
                    else:
                        dados = {"Agenda": agenda, "Etiqueta": etiqueta, "NCE": nce, "Endereço": endereco}

                elif criterio == "Inventário":
                    if not validar_nce(nce) or not saida or not entrada:
                        valido = False
                    else:
                        dados = {"NCE": nce, "Saída": saida, "Entrada": entrada}

                elif criterio == "Separação":
                    if not carga or not numero_sep or not validar_nce(nce):
                        valido = False
                    else:
                        dados = {"Carga": carga, "Separação": numero_sep, "NCE": nce}

                elif criterio == "Expedição":
                    dados = {"Carga": carga, "Separação": numero_sep, "NCE": nce}

                if valido and dados:

                    id_chamado = str(uuid.uuid4())[:8]

                    st.session_state.chamados[id_chamado] = {
                        "usuario": st.session_state.usuario_logado,
                        "criterio": criterio,
                        "dados": dados,
                        "chat": [
                            f"Sistema: Chamado aberto - {criterio}",
                            f"Erro: {erro}"
                        ]
                    }

                    st.success("Chamado aberto com sucesso!")
                    st.session_state.menu = "Chat"
                    st.rerun()

                else:
                    st.error("Preencha corretamente os campos obrigatórios.")

    # ================= CHAT =================
    if menu == "Chat":
        chamados_usuario = [
            id for id, dados in st.session_state.chamados.items()
            if dados["usuario"] == st.session_state.usuario_logado
        ]

        if chamados_usuario:
            chamado = st.selectbox("Selecionar Chamado", chamados_usuario)
            dados = st.session_state.chamados[chamado]

            for msg in dados["chat"]:
                st.write(msg)

            msg = st.text_input("Mensagem")
            if st.button("Enviar"):
                if msg:
                    dados["chat"].append(f"Usuário: {msg}")
                    st.rerun()
        else:
            st.info("Você ainda não possui chamados.")

    if menu == "Meu Perfil":
        st.title("Meu Perfil")
        st.write("Email:", st.session_state.usuario_logado)
