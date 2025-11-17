# PetDor/app.py
import streamlit as st
from fpdf import FPDF
from datetime import datetime
import bcrypt

from connection import conectar_db
from database.migration import migrar_banco_completo

# -------------------------------
# 🔰 Inicialização do banco
# -------------------------------
migrar_banco_completo()

st.set_page_config(page_title="PETDOR – Avaliação de Dor", layout="centered")

# -------------------------------
# 📌 Funções auxiliares
# -------------------------------
def criar_hash(senha):
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

def validar_senha(senha, senha_hash):
    return bcrypt.checkpw(senha.encode(), senha_hash.encode())

# -------------------------------
# 🔐 Usuários
# -------------------------------
def cadastrar_usuario(nome, email, senha, confirmar):
    if senha != confirmar:
        return False, "As senhas não conferem"
    if len(senha) < 6:
        return False, "A senha deve ter pelo menos 6 caracteres"
    
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE email = ?", (email.lower().strip(),))
    if cur.fetchone():
        conn.close()
        return False, "Email já cadastrado"
    
    senha_hash = criar_hash(senha)
    cur.execute(
        "INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)",
        (nome.strip().title(), email.lower().strip(), senha_hash)
    )
    conn.commit()
    conn.close()
    return True, "Conta criada com sucesso!"

def login(email, senha):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios WHERE email = ?", (email.lower().strip(),))
    user = cur.fetchone()
    conn.close()
    if user and validar_senha(senha, user["senha_hash"]):
        return user
    return None

# -------------------------------
# 🔑 Reset de senha
# -------------------------------
def reset_password_request(email):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE email = ?", (email.lower().strip(),))
    user = cur.fetchone()
    if not user:
        return None
    token = bcrypt.gensalt().decode()
    exp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute(
        "INSERT INTO password_resets (usuario_id, token, expires_at) VALUES (?, ?, ?)",
        (user["id"], token, exp)
    )
    conn.commit()
    conn.close()
    return token

def reset_password(token, nova_senha):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT usuario_id FROM password_resets WHERE token = ? AND used = 0", (token,))
    pr = cur.fetchone()
    if not pr:
        return False
    senha_hash = criar_hash(nova_senha)
    cur.execute("UPDATE usuarios SET senha_hash = ? WHERE id = ?", (senha_hash, pr["usuario_id"]))
    cur.execute("UPDATE password_resets SET used = 1 WHERE token = ?", (token,))
    conn.commit()
    conn.close()
    return True

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
st.title("🐾 PETDOR – Sistema de Avaliação de Dor")
menu = st.sidebar.selectbox("Menu", ["Login", "Criar Conta", "Redefinir Senha"])

# LOGIN
if menu == "Login":
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        user = login(email, senha)
        if user:
            st.success(f"Bem-vindo, {user['nome']}!")
            st.session_state.user = user
        else:
            st.error("Credenciais inválidas.")

    if "user" in st.session_state:
        user = st.session_state.user
        st.subheader("Cadastrar novo Pet")
        with st.form("pet_form"):
            nome_pet = st.text_input("Nome")
            especie = st.text_input("Espécie")
            raca = st.text_input("Raça")
            peso = st.number_input("Peso (kg)", step=0.1)
            if st.form_submit_button("Salvar Pet"):
                cadastrar_pet(user["id"], nome_pet, especie, raca, peso)
                st.success("Pet cadastrado com sucesso!")

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

# CRIAR CONTA
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

# RESET SENHA
elif menu == "Redefinir Senha":
    email = st.text_input("Seu e-mail")
    if st.button("Enviar token"):
        token = reset_password_request(email)
        if token:
            st.info(f"Token gerado: {token}\n\nCopie e cole abaixo.")
        else:
            st.error("E-mail não encontrado.")
    token = st.text_input("Token")
    nova = st.text_input("Nova senha", type="password")
    if st.button("Alterar senha"):
        if reset_password(token, nova):
            st.success("Senha alterada com sucesso!")
        else:
            st.error("Token inválido ou expirado.")


