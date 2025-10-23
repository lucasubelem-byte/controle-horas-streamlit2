import streamlit as st
import json
import os
from datetime import datetime

# Caminho do arquivo JSON para armazenar dados
ARQUIVO_DADOS = "dados.json"

# Senha mestre fixa
SENHA_MESTRE = "1b1m"

# Funções auxiliares
def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        return {"usuarios": {}, "historico": []}
    with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# Interface principal
st.set_page_config(page_title="Controle de Horas", page_icon="⏰", layout="centered")
st.title("⏰ Controle de Horas Devidas")

dados = carregar_dados()

aba = st.sidebar.selectbox("Escolha uma opção:", ["Visualizar horas", "Área do Administrador"])

# -------------------------------------------------
# VISUALIZAR HORAS
# -------------------------------------------------
if aba == "Visualizar horas":
    st.header("👀 Ver horas devidas")

    if len(dados["usuarios"]) == 0:
        st.warning("Nenhum usuário cadastrado ainda.")
    else:
        nome = st.selectbox("Selecione seu nome:", list(dados["usuarios"].keys()))
        horas = dados["usuarios"][nome]["horas"]
        st.metric(label=f"Horas devidas por {nome}", value=f"{horas}h")

    st.subheader("📜 Histórico de alterações")
    if len(dados["historico"]) == 0:
        st.info("Nenhuma alteração registrada ainda.")
    else:
        for h in reversed(dados["historico"][-15:]):  # Mostra os 15 últimos
            st.write(f"📅 **{h['data']}** - {h['acao']} **{h['nome']}** → {h['horas']}h")

# -------------------------------------------------
# ÁREA DO ADMINISTRADOR
# -------------------------------------------------
elif aba == "Área do Administrador":
    st.header("🔐 Área do Administrador")
    senha = st.text_input("Digite a senha mestre:", type="password")

    if senha == SENHA_MESTRE:
        opcao = st.selectbox("Escolha uma ação:", [
            "Adicionar horas",
            "Remover horas",
            "Adicionar usuário",
            "Remover usuário"
        ])

        # ---------------------------------------
        # ADICIONAR HORAS
        # ---------------------------------------
        if opcao == "Adicionar horas":
            if len(dados["usuarios"]) == 0:
                st.warning("Nenhum usuário cadastrado ainda.")
            else:
                nome = st.selectbox("Selecione o funcionário:", list(dados["usuarios"].keys()))
                dia = st.date_input("Dia da falta:")
                horas_add = st.number_input("Quantas horas deseja adicionar?", min_value=0.5, step=0.5)
                if st.button("✅ Confirmar adição"):
                    dados["usuarios"][nome]["horas"] += horas_add
                    dados["historico"].append({
                        "data": str(dia),
                        "acao": "Adicionadas horas a",
                        "nome": nome,
                        "horas": horas_add
                    })
                    salvar_dados(dados)
                    st.success(f"{horas_add}h adicionadas a {nome} ({dia}).")

        # ---------------------------------------
        # REMOVER HORAS
        # ---------------------------------------
        elif opcao == "Remover horas":
            if len(dados["usuarios"]) == 0:
                st.warning("Nenhum usuário cadastrado ainda.")
            else:
                nome = st.selectbox("Selecione o funcionário:", list(dados["usuarios"].keys()))
                dia = st.date_input("Dia da correção:")
                horas_rem = st.number_input("Quantas horas deseja remover?", min_value=0.5, step=0.5)
                if st.button("❌ Confirmar remoção"):
                    dados["usuarios"][nome]["horas"] = max(0, dados["usuarios"][nome]["horas"] - horas_rem)
                    dados["historico"].append({
                        "data": str(dia),
                        "acao": "Removidas horas de",
                        "nome": nome,
                        "horas": horas_rem
                    })
                    salvar_dados(dados)
                    st.success(f"{horas_rem}h removidas de {nome} ({dia}).")

        # ---------------------------------------
        # ADICIONAR USUÁRIO
        # ---------------------------------------
        elif opcao == "Adicionar usuário":
            novo_nome = st.text_input("Digite o nome do novo funcionário:")
            if st.button("➕ Adicionar"):
                if novo_nome.strip() == "":
                    st.warning("Digite um nome válido.")
                elif novo_nome in dados["usuarios"]:
                    st.warning("Esse nome já está cadastrado.")
                else:
                    dados["usuarios"][novo_nome] = {"horas": 0}
                    salvar_dados(dados)
                    st.success(f"{novo_nome} adicionado com sucesso.")

        # ---------------------------------------
        # REMOVER USUÁRIO
        # ---------------------------------------
        elif opcao == "Remover usuário":
            if len(dados["usuarios"]) == 0:
                st.warning("Nenhum usuário cadastrado ainda.")
            else:
                nome_remover = st.selectbox("Selecione o funcionário a remover:", list(dados["usuarios"].keys()))
                if st.button("🗑️ Remover"):
                    del dados["usuarios"][nome_remover]
                    salvar_dados(dados)
                    st.success(f"{nome_remover} removido com sucesso.")

    elif senha != "":
        st.error("Senha incorreta.")