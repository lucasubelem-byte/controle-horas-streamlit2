import streamlit as st
from datetime import datetime
import json
import os

st.set_page_config(page_title="Controle de Horas", layout="wide")

# ===== Senha mestra =====
senha_mestra = "Ralf71"

# ===== Arquivo JSON =====
ARQUIVO_DADOS = "dados.json"

# Carregar dados do JSON
if os.path.exists(ARQUIVO_DADOS):
    with open(ARQUIVO_DADOS, "r") as f:
        usuarios = json.load(f)
else:
    usuarios = {
        "Lucas Uva": {"horas": [], "faltas": []},
        "Luis": {"horas": [], "faltas": []},
        "Matheus": {"horas": [], "faltas": []},
        "Raphaela": {"horas": [], "faltas": []},
        "Ralf": {"horas": [], "faltas": []},
        "Julia": {"horas": [], "faltas": []},
        "Withyna": {"horas": [], "faltas": []},
        "Melissa": {"horas": [], "faltas": []},
        "Ana": {"horas": [], "faltas": []},
        "Leandro": {"horas": [], "faltas": []},
    }

# Função para salvar JSON
def salvar_dados():
    with open(ARQUIVO_DADOS, "w") as f:
        json.dump(usuarios, f, indent=4)

# ===== Funções =====
def adicionar_horas(nome):
    dia = st.date_input("Escolha o dia da falta", key=f"data_add_{nome}")
    dia_str = dia.strftime("%d/%m/%Y")
    horas_adicionar = st.number_input(
        "Quantidade de horas a adicionar:",
        min_value=0,
        step=1,
        format="%d",
        key=f"horas_add_{nome}"
    )
    if st.button("✅ Confirmar adição", key=f"btn_add_{nome}"):
        if horas_adicionar > 0:
            usuarios[nome]["horas"].append(horas_adicionar)
            usuarios[nome]["faltas"].append(dia_str)
            salvar_dados()
            st.success(f"{horas_adicionar} horas adicionadas para {nome} no dia {dia_str}")
        else:
            st.warning("Digite uma quantidade válida de horas.")

def remover_horas(nome):
    if usuarios[nome]["horas"]:
        total_horas = sum(usuarios[nome]["horas"])
        qtd = st.number_input(
            f"Quantas horas deseja remover? (Total: {total_horas})",
            min_value=1,
            max_value=total_horas,
            step=1,
            format="%d",
            key=f"qtd_rem_{nome}"
        )
        if st.button(f"🗑 Remover horas de {nome}", key=f"btn_rem_{nome}"):
            restante = qtd
            while restante > 0 and usuarios[nome]["horas"]:
                if usuarios[nome]["horas"][-1] <= restante:
                    restante -= usuarios[nome]["horas"][-1]
                    usuarios[nome]["horas"].pop()
                    usuarios[nome]["faltas"].pop()
                else:
                    usuarios[nome]["horas"][-1] -= restante
                    restante = 0
            salvar_dados()
            st.success(f"{qtd} horas removidas de {nome}")
    else:
        st.warning(f"{nome} não possui horas a remover.")

def ver_horas():
    st.subheader("📊 Horas devidas")
    for nome, dados in usuarios.items():
        with st.expander(f"{nome} - {sum(dados['horas'])} horas"):
            if dados["faltas"]:
                for dia, h in zip(dados["faltas"], dados["horas"]):
                    st.write(f"{dia}: {int(h)} horas")
            else:
                st.write("Nenhuma falta registrada.")

def admin_panel():
    st.subheader("🔒 Painel Admin")
    senha = st.text_input("Senha mestra:", type="password", key="senha_admin")
    if senha == senha_mestra:
        op = st.selectbox("Escolha a operação:", ["Adicionar/Remover horas", "Adicionar usuário", "Remover usuário"])
        
        if op == "Adicionar/Remover horas":
            nome = st.selectbox("Escolha o usuário:", list(usuarios.keys()))
            st.markdown("### ➕ Adicionar horas")
            adicionar_horas(nome)
            st.markdown("### ➖ Remover horas")
            remover_horas(nome)

        elif op == "Adicionar usuário":
            nome_novo = st.text_input("Nome do novo usuário")
            if st.button("Adicionar"):
                if nome_novo and nome_novo not in usuarios:
                    usuarios[nome_novo] = {"horas": [], "faltas": []}
                    salvar_dados()
                    st.success(f"Usuário {nome_novo} adicionado!")
                else:
                    st.error("Usuário já existe ou nome inválido.")

        elif op == "Remover usuário":
            if usuarios:
                nome_remover = st.selectbox("Escolha o usuário para remover:", list(usuarios.keys()))
                if st.button("Remover"):
                    usuarios.pop(nome_remover)
                    salvar_dados()
                    st.success(f"Usuário {nome_remover} removido!")
            else:
                st.info("Nenhum usuário para remover.")
    elif senha:
        st.error("Senha mestra incorreta!")

# ===== Interface Principal =====
st.title("⏱ Controle de Horas Devidas")

acao = st.radio("Escolha uma ação:", ["Ver horas", "Admin"])

if acao == "Ver horas":
    ver_horas()
else:
    admin_panel()