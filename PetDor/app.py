# PetDor/app.py
import streamlit as st
from datetime import datetime
from fpdf import FPDF
import bcrypt
import logging

# -------------------------------
# 🔌 Conexão e Migração
# -------------------------------
from database.connection import conectar_db
from database.migration import migrar_banco_completo
from auth.user import cadastrar_usuario, autenticar_usuario
from database.models import buscar_usuario_por_id

# -------------------------------
# 🔰 Inicialização do banco
# -------------------------------
migrar_banco_completo()  # Cria todas as tabelas se não existirem

# -------------------------------
# 📌 Funções auxiliares
# -------------------------------
def criar_hash(senha):
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

def validar_senha(senha, senha_hash):
    return bcrypt.checkpw(senha.encode(), senha_hash.encode())

# -------------------------------
# 📋 CRUD Pets
# -------------------------------
def cadastrar_pet(tutor_id, nome, especie, raca=None, peso=None):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO pets (tutor_id, nome, especie, raca, peso) VALUES (?, ?, ?, ?, ?)",
        (tutor_id, nome, especie, raca, peso)
    )
    conn.commit()
    conn.close()

def listar_pets(tutor_id):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM pets WHERE tutor_id = ?", (tutor_id,))
    pets = cur.fetchall()
    conn.close()
    return pets

# -------------------------------
# 📝 Avaliações
# -------------------------------
def registrar_avaliacao(pet_id, usuario_id, percentual, observacoes):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO avaliacoes (pet_id, usuario_id, percentual_dor, observacoes) VALUES (?, ?, ?, ?)",
        (pet_id, usuario_id, percentual, observacoes)
    )
    conn.commit()
    conn.close()

# -------------------------------
# 📄 PDF
# -------------------------------
def gerar_pdf(nome_pet, percentual, obs):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 10, "Relatório PETDOR", ln=True)
    pdf.cell(0, 10, f"Pet: {nome_pet}", ln=True)
    pdf.cell(0, 10, f"Percentual de dor: {percentual}%", ln=True)
    pdf.multi_cell(0, 10, f"Observações:\n{obs}")
    filename = f"relatorio_{nome_pet}.pdf"
    pdf.output(filename)
    return filename

# -------------------------------
# 🎨 Interface Streamlit
# -------------------------------
st.set_page_config(page_title="PETDOR – Avaliação de Dor", layout="centered")
st.title("🐾 PETDOR – Sistema de Avaliação de Dor")

menu = st.sidebar.selectbox("Menu", ["Login", "Criar Conta"])

# -------------------------------
# LOGIN
# -------------------------------
if menu == "Login":
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        ok, msg, user_id = autenticar_usuario(email, senha)
        if ok:
            st.success(msg)
            st.session_state.user_id = user_id
        else:
            st.error(msg)

    # Fluxo principal após login
    if "user_id" in st.session_state:
        user = buscar_usuario_por_id(st.session_state.user_id)
        st.subheader(f"Bem-vindo, {user['nome']}!")

        # Cadastrar Pet
        st.subheader("Cadastrar novo Pet")
        with st.form("pet_form"):
            nome_pet = st.text_input("Nome")
            especie = st.text_input("Espécie")
            raca = st.text_input("Raça")
            peso = st.number_input("Peso (kg)", step=0.1)
            if st.form_submit_button("Salvar Pet"):
                cadastrar_pet(user["id"], nome_pet, especie, raca, peso)
                st.success("Pet cadastrado com sucesso!")

        # Avaliações
        st.subheader("Suas avaliações")
        pets = listar_pets(user["id"])
        pet_selec = st.selectbox("Escolha o pet", [p["nome"] for p in pets] if pets else [])
        if pet_selec:
            pet = next(p for p in pets if p["nome"] == pet_selec)
            percentual = st.slider("Percentual de Dor (%)", 0, 100, 50)
            obs = st.text_area("Observações")
            if st.button("Registrar Avaliação"):
                registrar_avaliacao(pet["id"], user["id"], percentual, obs)
                st.success("Avaliação salva!")
            if st.button("Gerar PDF"):
                filename = gerar_pdf(pet["nome"], percentual, obs)
                with open(filename, "rb") as f:
                    st.download_button("Baixar PDF", f, file_name=filename)

# -------------------------------
# CRIAR CONTA
# -------------------------------
elif menu == "Criar Conta":
    nome = st.text_input("Nome")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    confirmar = st.text_input("Confirmar senha", type="password")
    if st.button("Criar"):
        ok, msg = cadastrar_usuario(nome, email, senha, confirmar)
        if ok:
            st.success(msg)
        else:
            st.error(msg)
