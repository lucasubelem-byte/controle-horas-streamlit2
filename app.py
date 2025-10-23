import streamlit as st
import json
import os
from datetime import date

ARQUIVO_DADOS = "dados.json"
SENHA_ADMIN = "1234"  # senha mestre

# ========== FUNÇÕES DE DADOS ==========

# Garante que o arquivo exista
if not os.path.exists(ARQUIVO_DADOS):
    with open(ARQUIVO_DADOS, "w") as f:
        json.dump({"usuarios": {}}, f)

# Carregar dados com segurança
def carregar_dados():
    try:
        with open(ARQUIVO_DADOS, "r") as f:
            dados = json.load(f)
        if "usuarios" not in dados:
            dados["usuarios"] = {}
        return dados
    except (json.JSONDecodeError, FileNotFoundError):
        with open(ARQUIVO_DADOS, "w") as f:
            json.dump({"usuarios": {}}, f)
        return {"usuarios": {}}

# Salvar dados
def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w") as f:
        json.dump(dados, f, indent=4)

dados = carregar_dados()

# ========== INTERFACE PRINCIPAL ==========

st.title("📘 Controle de Horas - Equipe")

menu = st.sidebar.selectbox(
    "Menu", ["Visualizar Horas", "Área do Administrador"]
)

# ========== VISUALIZAR HORAS ==========

if menu == "Visualizar Horas":
    st.subheader("🔍 Verificar Horas de Usuário")
    nome = st.text_input("Digite o nome do usuário").strip().lower()

    if nome:
        if nome in dados["usuarios"]:
            info = dados["usuarios"][nome]
            st.success(f"Usuário: {nome.capitalize()}")
            st.write(f"**Total de horas devidas:** {info['horas']} horas")
            if "ultimo_dia" in info:
                st.write(f"**Último registro:** {info['ultimo_dia']}")
        else:
            st.warning("Usuário não encontrado!")

# ========== ÁREA DO ADMINISTRADOR ==========

elif menu == "Área do Administrador":
    st.subheader("⚙️ Acesso Restrito")
    senha = st.text_input("Digite a senha de administrador:", type="password")

    if senha == SENHA_ADMIN:
        st.success("Acesso autorizado ✅")

        acao = st.radio("Escolha uma ação:", ["Adicionar Horas", "Remover Horas"])

        if acao == "Adicionar Horas":
            nome = st.text_input("Nome do usuário para adicionar horas").strip().lower()
            dia = st.date_input("Escolha o dia do registro", date.today())
            horas = st.number_input("Quantas horas deseja adicionar?", min_value=0.0, step=0.5)

            if st.button("Adicionar"):
                if nome not in dados["usuarios"]:
                    dados["usuarios"][nome] = {"horas": 0, "ultimo_dia": ""}
                dados["usuarios"][nome]["horas"] += horas
                dados["usuarios"][nome]["ultimo_dia"] = str(dia)
                salvar_dados(dados)
                st.success(f"{horas} horas adicionadas para {nome.capitalize()} no dia {dia}.")

        elif acao == "Remover Horas":
            nome = st.text_input("Nome do usuário para remover horas").strip().lower()

            if nome in dados["usuarios"]:
                horas = st.number_input("Quantas horas deseja remover?", min_value=0.0, step=0.5)

                if st.button("Remover"):
                    dados["usuarios"][nome]["horas"] = max(
                        0, dados["usuarios"][nome]["horas"] - horas
                    )
                    salvar_dados(dados)
                    st.success(f"{horas} horas removidas de {nome.capitalize()}.")
            else:
                st.warning("Usuário não encontrado!")

    elif senha:
        st.error("Senha incorreta ❌")