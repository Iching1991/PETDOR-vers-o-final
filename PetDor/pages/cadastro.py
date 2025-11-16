# pages/cadastro.py

import streamlit as st
from auth.user import cadastrar_usuario

def render_cadastro_page():
    st.title("📋 Cadastro de Usuário PET DOR")

    nome = st.text_input("Nome completo")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    confirmar_senha = st.text_input("Confirmar senha", type="password")

    if st.button("📝 Cadastrar"):
        sucesso, msg = cadastrar_usuario(nome, email, senha, confirmar_senha)
        if sucesso:
            st.success(msg)
        else:
            st.error(msg)

    if st.button("← Voltar ao Login"):
        st.session_state["menu"] = "login"
        st.experimental_rerun()


