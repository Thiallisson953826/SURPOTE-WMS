import streamlit as st
import uuid
from datetime import datetime

st.set_page_config(page_title="WMS Suporte", layout="wide")

# ================= SESSION =================
if "usuarios" not in st.session_state:
    st.session_state.usuarios = {}

if "chamados" not in st.session_state:
    st.session_state.chamados = {}

if "perfil" not in st.session_state:
    st.session_state.perfil = None

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

# ================= FUNÇÕES =================
def agora():
    return datetime.now().strftime("%d/%m/%Y %H:%M")

def criar_chamado(dados):
    id_chamado = str(uuid.uuid4())[:8]
    st.session_state.chamados[id_chamado] = dados
    return id_chamado

# =========================================================
# ===================== LOGIN =============================
# =========================================================

st.sidebar.title("Login")

tipo = st.sidebar.radio("Tipo de Acesso", ["Usuário", "Admin"])

if tipo == "Usuário":
    nome = st.sidebar.text_input("Nome")
    origem = st.sidebar.selectbox("Origem", ["TDC","IDC","PDC","DPC","FLD"])

    if st.sidebar.button("Entrar"):
        if nome:
            st.session_state.perfil = "Usuario"
            st.session_state.usuario_logado = nome
            st.session_state.usuarios[nome] = origem
            st.rerun()

else:
    senha = st.sidebar.text_input("Senha Admin", type="password")
    if st.sidebar.button("Entrar"):
        if senha == "1234":
            st.session_state.perfil = "Admin"
            st.rerun()
        else:
            st.sidebar.error("Senha incorreta")

# =========================================================
# ===================== USUÁRIO ===========================
# =========================================================

if st.session_state.perfil == "Usuario":

    st.title("WMS - Suporte")

    operacao = st.selectbox("Operação", [
        "Recebimento",
        "Armazenagem",
        "Transferencia",
        "Inventarios",
        "Separação",
        "Expedição"
    ])

    dados_form = {}
    obrigatorios_ok = True

    if operacao == "Recebimento":
        dados_form["Nota"] = st.text_input("Nota *")
        dados_form["Agenda"] = st.text_input("Agenda (Opcional)")
        dados_form["NCE"] = st.text_input("NCE *")

        if not dados_form["Nota"] or not dados_form["NCE"]:
            obrigatorios_ok = False

    if operacao == "Armazenagem":
        dados_form["Agenda"] = st.text_input("Agenda *")
        dados_form["Etiqueta"] = st.text_input("Etiqueta *")
        dados_form["Endereço"] = st.text_input("Endereço (Opcional)")

        if not dados_form["Agenda"] or not dados_form["Etiqueta"]:
            obrigatorios_ok = False

    if operacao == "Transferencia":
        dados_form["Endereço Saida"] = st.text_input("Endereço Saída *")
        dados_form["Endereço Entrada"] = st.text_input("Endereço Entrada *")
        dados_form["NCE"] = st.text_input("NCE *")

        if not dados_form["Endereço Saida"] or not dados_form["Endereço Entrada"] or not dados_form["NCE"]:
            obrigatorios_ok = False

    if operacao == "Inventarios":
        dados_form["NCE"] = st.text_input("NCE *")
        dados_form["Endereço"] = st.text_input("Endereço *")

        if not dados_form["NCE"] or not dados_form["Endereço"]:
            obrigatorios_ok = False

    if operacao == "Separação":
        dados_form["Carga"] = st.text_input("Carga *")
        dados_form["Separação"] = st.text_input("Separação (Opcional)")
        dados_form["Nota"] = st.text_input("Nota *")

        if not dados_form["Carga"] or not dados_form["Nota"]:
            obrigatorios_ok = False

    if operacao == "Expedição":
        dados_form["Carga"] = st.text_input("Carga *")
        dados_form["Separação"] = st.text_input("Separação *")
        dados_form["Nota"] = st.text_input("Nota *")

        if not dados_form["Carga"] or not dados_form["Separação"] or not dados_form["Nota"]:
            obrigatorios_ok = False

    detalhe = st.text_area("Detalhe do Problema *")

    if st.button("Abrir Chamado"):
        if obrigatorios_ok and detalhe:
            id_ch = criar_chamado({
                "usuario": st.session_state.usuario_logado,
                "origem": st.session_state.usuarios[st.session_state.usuario_logado],
                "operacao": operacao,
                "dados": dados_form,
                "detalhe": detalhe,
                "status": "Aberto",
                "data": agora(),
                "chat": [
                    f"Sistema: Chamado aberto em {agora()}",
                    f"Usuário: {detalhe}"
                ]
            })
            st.success(f"Chamado aberto! Código: {id_ch}")
            st.rerun()
        else:
            st.error("Preencha todos os campos obrigatórios.")

    st.divider()
    st.subheader("Meus Chamados")

    for id_ch, ch in st.session_state.chamados.items():
        if ch["usuario"] == st.session_state.usuario_logado:

            st.markdown(f"### Chamado {id_ch} - {ch['status']}")
            st.write("Operação:", ch["operacao"])
            st.write("Dados:", ch["dados"])

            st.subheader("Chat")
            for msg in ch["chat"]:
                st.write(msg)

            if ch["status"] != "Resolvido":
                msg = st.text_input(f"Mensagem {id_ch}", key=id_ch)
                if st.button(f"Enviar {id_ch}"):
                    if msg:
                        ch["chat"].append(f"{st.session_state.usuario_logado}: {msg}")
                        ch["status"] = "Em Atendimento"
                        st.rerun()

# =========================================================
# ===================== ADMIN =============================
# =========================================================

if st.session_state.perfil == "Admin":

    st.title("Painel Administrativo")

    menu = st.sidebar.radio("Menu", ["Dashboard","Chamados","Usuários"])

    if menu == "Dashboard":
        total = len(st.session_state.chamados)
        aberto = sum(1 for c in st.session_state.chamados.values() if c["status"]=="Aberto")
        atendimento = sum(1 for c in st.session_state.chamados.values() if c["status"]=="Em Atendimento")
        resolvido = sum(1 for c in st.session_state.chamados.values() if c["status"]=="Resolvido")

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Total", total)
        c2.metric("Aberto", aberto)
        c3.metric("Em Atendimento", atendimento)
        c4.metric("Resolvido", resolvido)

    if menu == "Chamados":

        for id_ch, ch in list(st.session_state.chamados.items()):

            st.markdown(f"## {id_ch} - {ch['status']}")
            st.write("Usuário:", ch["usuario"])
            st.write("Origem:", ch["origem"])
            st.write("Operação:", ch["operacao"])
            st.write("Dados:", ch["dados"])

            novo_status = st.selectbox("Alterar Status", ["Aberto","Em Atendimento","Resolvido"], key=id_ch)
            if st.button("Atualizar", key="u"+id_ch):
                ch["status"] = novo_status
                ch["chat"].append(f"Sistema: Status alterado para {novo_status}")
                st.rerun()

            if st.button("Excluir Chamado", key="e"+id_ch):
                del st.session_state.chamados[id_ch]
                st.rerun()

            st.subheader("Chat")
            for msg in ch["chat"]:
                st.write(msg)

            msg_admin = st.text_input("Responder", key="r"+id_ch)
            if st.button("Enviar Resposta", key="b"+id_ch):
                if msg_admin:
                    ch["chat"].append(f"Admin: {msg_admin}")
                    ch["status"] = "Em Atendimento"
                    st.rerun()

            st.divider()

    if menu == "Usuários":

        for user in list(st.session_state.usuarios.keys()):
            st.write(user, "-", st.session_state.usuarios[user])
            if st.button(f"Excluir {user}"):
                del st.session_state.usuarios[user]
                st.rerun()
