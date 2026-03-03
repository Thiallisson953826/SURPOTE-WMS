import streamlit as st
from datetime import datetime

st.set_page_config(page_title="SUPORTE WMS", layout="wide")

# ================= ESTILO MODERNO =================
st.markdown("""
<style>
.main {background-color:#f4f6fa;}
.topbar {
    background-color:#111;
    padding:15px;
    border-radius:0 0 15px 15px;
}
.topbar h1 {color:white;}
.card {
    background:white;
    padding:20px;
    border-radius:15px;
    box-shadow:0px 4px 15px rgba(0,0,0,0.08);
    margin-bottom:20px;
}
.stButton>button {
    border-radius:8px;
    font-weight:bold;
    height:40px;
}
.btn-primary button {background:#0052cc;color:white;}
.btn-success button {background:#28a745;color:white;}
.btn-danger button {background:#dc3545;color:white;}
.status-aberto {color:#dc3545;font-weight:bold;}
.status-andamento {color:#ffc107;font-weight:bold;}
.status-finalizado {color:#28a745;font-weight:bold;}
</style>
""", unsafe_allow_html=True)

# ================= ESTADO =================
if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"

if "chamados" not in st.session_state:
    st.session_state.chamados = []

if "responsaveis" not in st.session_state:
    st.session_state.responsaveis = ["THIALLISSON","KELSON","EDVALDO","HERNANDES"]

# ================= PAGINA INICIAL =================
if st.session_state.pagina == "inicio":
    st.markdown("<div class='topbar'><h1>SUPORTE WMS</h1></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    if col1.button("Entrar como Usuário"):
        st.session_state.pagina = "usuario"
    if col2.button("Entrar como Admin"):
        st.session_state.pagina = "login_admin"

# ================= LOGIN ADMIN =================
elif st.session_state.pagina == "login_admin":
    st.title("Login Admin")
    senha = st.text_input("Senha", type="password")

    col1, col2 = st.columns(2)
    if col1.button("Entrar"):
        if senha == "1234":
            st.session_state.pagina = "admin"
        else:
            st.error("Senha incorreta")

    if col2.button("Voltar"):
        st.session_state.pagina = "inicio"

# ================= TELA USUARIO =================
elif st.session_state.pagina == "usuario":

    st.markdown("<div class='topbar'><h1>Abrir Chamado</h1></div>", unsafe_allow_html=True)

    if st.button("Voltar"):
        st.session_state.pagina = "inicio"

    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        nome = st.text_input("Seu Nome")
        origem = st.selectbox("Origem", ["TDC","IDC","PDC","DPC","FLD"])

        tipo = st.selectbox("Tipo de Operação", [
            "Recebimento","Armazenagem","Transferência",
            "Inventário","Separação","Expedição"
        ])

        descricao = st.text_area("Descreva o problema *")

        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🚀 Enviar Chamado"):

        if not nome or not descricao:
            st.error("Preencha Nome e Descrição")
        else:
            chamado = {
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Nome": nome,
                "Origem": origem,
                "Tipo": tipo,
                "Descricao": descricao,
                "Status": "Aberto",
                "Responsavel": None,
                "Chat": [f"{nome}: {descricao}"]
            }

            st.session_state.chamados.append(chamado)
            st.success("Chamado enviado com sucesso!")

# ================= TELA ADMIN =================
elif st.session_state.pagina == "admin":

    st.markdown("<div class='topbar'><h1>Painel Administrativo</h1></div>", unsafe_allow_html=True)

    if st.button("Logout"):
        st.session_state.pagina = "inicio"

    st.subheader("Gerenciar Responsáveis")

    col1, col2 = st.columns(2)

    novo = col1.text_input("Novo Responsável")
    if col1.button("Adicionar"):
        if novo:
            st.session_state.responsaveis.append(novo.upper())

    remover = col2.selectbox("Remover Responsável", [""] + st.session_state.responsaveis)
    if col2.button("Remover"):
        if remover:
            st.session_state.responsaveis.remove(remover)

    st.divider()
    st.subheader("Chamados")

    if not st.session_state.chamados:
        st.info("Nenhum chamado aberto.")

    for i, ch in enumerate(st.session_state.chamados):

        with st.expander(f"{ch['Tipo']} - {ch['Nome']}"):

            # STATUS COLORIDO
            if ch["Status"] == "Aberto":
                st.markdown("<p class='status-aberto'>Aberto</p>", unsafe_allow_html=True)
            elif ch["Status"] == "Em Atendimento":
                st.markdown("<p class='status-andamento'>Em Atendimento</p>", unsafe_allow_html=True)
            else:
                st.markdown("<p class='status-finalizado'>Finalizado</p>", unsafe_allow_html=True)

            st.write("Origem:", ch["Origem"])
            st.write("Descrição:", ch["Descricao"])

            # ADMIN ESCOLHE RESPONSAVEL
            responsavel = st.selectbox(
                "Designar Responsável",
                ["Selecione"] + st.session_state.responsaveis,
                key=f"resp{i}"
            )

            if st.button("Designar", key=f"btnresp{i}"):
                if responsavel != "Selecione":
                    ch["Responsavel"] = responsavel
                    ch["Status"] = "Em Atendimento"

            # ALTERAR STATUS
            novo_status = st.selectbox(
                "Alterar Status",
                ["Aberto","Em Atendimento","Finalizado"],
                key=f"status{i}"
            )
            ch["Status"] = novo_status

            st.markdown("### 💬 Chat")

            for msg in ch["Chat"]:
                st.write(msg)

            nova_msg = st.text_input("Mensagem", key=f"msg{i}")

            if st.button("Enviar Mensagem", key=f"btnmsg{i}"):
                if nova_msg:
                    ch["Chat"].append(f"ADMIN: {nova_msg}")

            if st.button("Excluir Chamado", key=f"del{i}"):
                st.session_state.chamados.pop(i)
                st.success("Chamado excluído")
