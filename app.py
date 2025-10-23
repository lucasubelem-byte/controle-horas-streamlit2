import streamlit as st
import json
import os
from datetime import datetime

# Caminho do arquivo JSON
ARQUIVO_DADOS = "dados.json"

# Função para carregar dados
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r") as f:
            return json.load(f)
    else:
        return {}

# Função para salvar dados
def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w") as f:
        json.dump(dados, f, indent=4)

# Carrega os dados ao iniciar
dados = carregar_dados()

st.title("⏰ Controle de Horas Devidas")

# Seção de visualização
st.header("🔍 Visualizar Horas e Faltas")
nome = st.selectbox("Selecione seu nome:", list(dados.keys()))

if nome:
    horas = dados[nome].get("horas", [])
    faltas = dados[nome].get("faltas", [])
    total_horas = sum(h["quantidade"] for h in horas)

    st.subheader(f"👤 {nome}")
    st.write(f"**Total de horas devidas:** {total_horas} horas")

    if horas:
        st.write("### 📅 Histórico de Horas")
        for h in horas:
            st.write(f"- {h['dia']}: {h['quantidade']}h")
    else:
        st.info("Nenhuma hora registrada.")

    if faltas:
        st.write("### ⚠️ Faltas Registradas")
        for f in faltas:
            st.write(f"- {f}")
    else:
        st.info("Nenhuma falta registrada.")

st.divider()

# Seção de administração
st.header("🔐 Área do Administrador")

senha_admin = st.text_input("Digite a senha de administrador:", type="password")

if senha_admin == "1b1m":
    st.success("Acesso concedido!")

    opcao = st.radio("Escolha uma ação:", ["Adicionar horas", "Remover horas"])

    if opcao == "Adicionar horas":
        nome_alvo = st.selectbox("Selecione o usuário:", list(dados.keys()), key="add_user")
        dia = st.text_input("Dia (ex: 23/10/2025):", value=datetime.now().strftime("%d/%m/%Y"))
        horas_adicionar = st.number_input("Quantidade de horas a adicionar:", min_value=0.0, step=0.5)

        if st.button("✅ Confirmar adição"):
            if horas_adicionar > 0:
                dados[nome_alvo]["horas"].append({"dia": dia, "quantidade": horas_adicionar})
                salvar_dados(dados)
                st.success(f"{horas_adicionar}h adicionadas para {nome_alvo} no dia {dia}.")
            else:
                st.warning("Digite uma quantidade válida de horas.")

    elif opcao == "Remover horas":
        nome_alvo = st.selectbox("Selecione o usuário:", list(dados.keys()), key="remove_user")

        if len(dados[nome_alvo]["horas"]) == 0:
            st.info("Nenhuma hora para remover.")
        else:
            horas_list = [f"{h['dia']} - {h['quantidade']}h" for h in dados[nome_alvo]["horas"]]
            hora_remover = st.selectbox("Selecione a hora a remover:", horas_list)

            if st.button("🗑 Remover hora selecionada"):
                indice = horas_list.index(hora_remover)
                removida = dados[nome_alvo]["horas"].pop(indice)
                salvar_dados(dados)
                st.success(f"Removida {removida['quantidade']}h de {nome_alvo} ({removida['dia']}).")

else:
    if senha_admin != "":
        st.error("Senha incorreta.")