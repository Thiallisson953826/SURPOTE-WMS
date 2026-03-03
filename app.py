import streamlit as st
from datetime import datetime

st.set_page_config(page_title="SUPORTE WMS", layout="wide")

# ================= ESTILO =================
st.markdown("""
<style>
.main { border-top: 8px solid black; }
.stButton>button {
    background-color: black;
    color: white;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ================= SESSION =================
if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"

if "chamados" not in st.session_state:
    st.session_state.chamados = []

if "responsaveis" not in st.session_state:
    st.session_state.responsaveis = ["THIALLISSON","KELSON","EDVALDO","HERNANDES"]

# ================= INICIO =================
if st.session_state.pagina == "inicio":

    st.title("SUPORTE WMS")

    col1, col2 = st.columns(2)

    if col1.button("Usuário"):
        st.session_state.pagina = "login_usuario"
        st.rerun()

    if col2.button("Admin"):
        st.session_state.pagina = "login_admin"
        st.rerun()

# ================= LOGIN USUARIO =================
elif st.session_state.pagina == "login_usuario":

    st.title("Login Usuário")

    nome = st.text_input("Nome")
    origem = st.selectbox("Origem", ["TDC","IDC","PDC","DPC","FLD"])

    col1, col2 = st.columns(2)

    if col1.button("Entrar"):
        if nome:
            st.session_state.nome = nome
            st.session_state.origem = origem
            st.session_state.pagina = "usuario"
            st.rerun()

    if col2.button("Voltar"):
        st.session_state.pagina = "inicio"
        st.rerun()

# ================= LOGIN ADMIN =================
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

# ================= TELA USUARIO =================
elif st.session_state.pagina == "usuario":

    st.title("Abrir Chamado")

    if st.button("Logout"):
        st.session_state.pagina = "inicio"
        st.rerun()

    tipo = st.selectbox("Tipo",[
        "Recebimento","Armazenagem","Transferência",
        "Inventário","Separação","Expedição"
    ])

    descricao = st.text_area("Descrição detalhada do erro *")

    responsavel = st.selectbox("Responsável", st.session_state.responsaveis)

    if st.button("Enviar Chamado"):

        if not descricao:
            st.error("Descrição é obrigatória")
        else:
            chamado = {
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Usuario": st.session_state.nome,
                "Origem": st.session_state.origem,
                "Tipo": tipo,
                "Descricao": descricao,
                "Responsavel": responsavel,
                "Status": "Aberto",
                "Chat": [
                    f"{st.session_state.nome}: Chamado aberto - {descricao}"
                ]
            }

            st.session_state.chamados.append(chamado)

            st.success("Chamado enviado com sucesso")
            st.rerun()

# ================= TELA ADMIN =================
elif st.session_state.pagina == "admin":

    st.title("Painel Admin")

    if st.button("Logout"):
        st.session_state.pagina = "inicio"
        st.rerun()

    st.subheader("Gerenciar Responsáveis")

    novo = st.text_input("Novo responsável")
    if st.button("Adicionar"):
        if novo:
            st.session_state.responsaveis.append(novo.upper())
            st.success("Adicionado")

    remover = st.selectbox("Remover responsável", [""] + st.session_state.responsaveis)
    if st.button("Remover"):
        if remover:
            st.session_state.responsaveis.remove(remover)
            st.success("Removido")

    st.divider()

    st.subheader("Chamados")

    if not st.session_state.chamados:
        st.info("Nenhum chamado aberto.")
    else:
        for i, ch in enumerate(st.session_state.chamados):

            with st.expander(f"{i+1} - {ch['Tipo']} - {ch['Status']}"):

                st.write("Usuário:", ch["Usuario"])
                st.write("Origem:", ch["Origem"])
                st.write("Responsável:", ch["Responsavel"])
                st.write("Descrição:", ch["Descricao"])

                novo_status = st.selectbox(
                    "Status",
                    ["Aberto","Em Atendimento","Finalizado"],
                    index=["Aberto","Em Atendimento","Finalizado"].index(ch["Status"]),
                    key=f"status{i}"
                )
                ch["Status"] = novo_status

                resolvido = st.text_input("Resolvido por", key=f"res{i}")
                if resolvido:
                    ch["Resolvido por"] = resolvido

                st.markdown("### Chat")

                for msg in ch["Chat"]:
                    st.write(msg)

                nova_msg = st.text_input("Mensagem", key=f"msg{i}")

                if st.button("Enviar Mensagem", key=f"btn{i}"):
                    if nova_msg:
                        ch["Chat"].append(f"ADMIN: {nova_msg}")
                        st.rerun()

                if st.button("Excluir Chamado", key=f"del{i}"):
                    st.session_state.chamados.pop(i)
                    st.rerun()
