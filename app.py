import streamlit as st
from datetime import datetime

st.set_page_config(page_title="SUPORTE WMS", layout="wide")

# =========================
# CSS
# =========================
st.markdown("""
<style>
.main { border-top: 10px solid black; }
.stButton>button {
    background-color: black;
    color: white;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# =========================
# SESSION STATE INICIAL
# =========================
if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"

if "responsaveis" not in st.session_state:
    st.session_state.responsaveis = ["Thiallisson","Kelson","Edvaldo","Hernandes"]

if "chamados" not in st.session_state:
    st.session_state.chamados = []

# =========================
# PAGINA INICIAL
# =========================
if st.session_state.pagina == "inicio":

    st.title("SUPORTE WMS")

    col1, col2 = st.columns(2)

    if col1.button("Login Usuário"):
        st.session_state.pagina = "login_usuario"
        st.rerun()

    if col2.button("Login Admin"):
        st.session_state.pagina = "login_admin"
        st.rerun()

# =========================
# LOGIN USUARIO
# =========================
elif st.session_state.pagina == "login_usuario":

    st.title("Login Usuário")

    usuario = st.text_input("Usuário")
    nome = st.text_input("Nome")
    origem = st.selectbox("Origem", ["TDC","IDC","PDC","DPC","FLD"])

    col1, col2 = st.columns(2)

    if col1.button("Entrar"):
        if usuario and nome:
            st.session_state.usuario = usuario
            st.session_state.nome = nome
            st.session_state.origem = origem
            st.session_state.pagina = "usuario"
            st.rerun()

    if col2.button("Voltar"):
        st.session_state.pagina = "inicio"
        st.rerun()

# =========================
# LOGIN ADMIN
# =========================
elif st.session_state.pagina == "login_admin":

    st.title("Login Admin")

    senha = st.text_input("Senha", type="password")

    col1, col2 = st.columns(2)

    if col1.button("Entrar"):
        if senha == "1234":
            st.session_state.pagina = "admin"
            st.rerun()
        else:
            st.error("Senha incorreta")

    if col2.button("Voltar"):
        st.session_state.pagina = "inicio"
        st.rerun()

# =========================
# TELA USUARIO
# =========================
elif st.session_state.pagina == "usuario":

    st.title("Abrir Chamado")

    if st.button("Logout"):
        st.session_state.pagina = "inicio"
        st.rerun()

    tipo = st.selectbox("Tipo",[
        "Recebimento","Armazenagem","Transferência",
        "Inventário","Separação","Expedição"
    ])

    nota = agenda = nce = etiqueta = endereco = ""
    end_saida = end_entrada = carga = separacao = ""

    if tipo == "Recebimento":
        nota = st.text_input("Nota *")
        agenda = st.text_input("Agenda")
        nce = st.text_input("NCE *")

    elif tipo == "Armazenagem":
        agenda = st.text_input("Agenda *")
        etiqueta = st.text_input("Etiqueta *")
        endereco = st.text_input("Endereço")

    elif tipo == "Transferência":
        end_saida = st.text_input("Endereço Saída *")
        end_entrada = st.text_input("Endereço Entrada *")
        nce = st.text_input("NCE *")

    elif tipo == "Inventário":
        nce = st.text_input("NCE *")
        endereco = st.text_input("Endereço *")

    elif tipo == "Separação":
        carga = st.text_input("Carga *")
        separacao = st.text_input("Separação")
        nota = st.text_input("Nota *")

    elif tipo == "Expedição":
        carga = st.text_input("Carga *")
        separacao = st.text_input("Separação *")
        nota = st.text_input("Nota *")

    descricao = st.text_area("Descrição do erro *")

    responsavel = st.selectbox("Responsável", st.session_state.responsaveis)

    if st.button("Criar Chamado"):

        chamado = {
            "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Usuario": st.session_state.nome,
            "Tipo": tipo,
            "Nota": nota,
            "Agenda": agenda,
            "NCE": nce,
            "Etiqueta": etiqueta,
            "Endereço": endereco,
            "Endereço Saída": end_saida,
            "Endereço Entrada": end_entrada,
            "Carga": carga,
            "Separação": separacao,
            "Descrição": descricao,
            "Responsável": responsavel,
            "Status": "Aberto",
            "Chat": [f"{st.session_state.nome}: Chamado aberto"]
        }

        st.session_state.chamados.append(chamado)

        st.success("Chamado criado e enviado ao Admin")
        st.rerun()

# =========================
# TELA ADMIN
# =========================
elif st.session_state.pagina == "admin":

    st.title("Painel Admin")

    if st.button("Logout"):
        st.session_state.pagina = "inicio"
        st.rerun()

    st.subheader("Gerenciar Responsáveis")

    novo = st.text_input("Novo Nome")
    if st.button("Adicionar"):
        if novo:
            st.session_state.responsaveis.append(novo)

    st.divider()

    for i, ch in enumerate(st.session_state.chamados):

        with st.expander(f"{i+1} - {ch['Tipo']} - {ch['Status']}"):

            st.write(ch)

            status = st.selectbox(
                "Status",
                ["Aberto","Em Atendimento","Finalizado"],
                key=f"status{i}"
            )
            ch["Status"] = status

            resolver = st.text_input("Resolvido por", key=f"res{i}")
            if resolver:
                ch["Resolvido por"] = resolver

            msg = st.text_input("Mensagem", key=f"chat{i}")
            if st.button("Enviar", key=f"btn{i}"):
                ch["Chat"].append(f"Admin: {msg}")

            for m in ch["Chat"]:
                st.write(m)

            if st.button("Excluir", key=f"del{i}"):
                st.session_state.chamados.pop(i)
                st.rerun()
