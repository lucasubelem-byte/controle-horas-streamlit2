import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import secrets
import json

st.set_page_config(page_title="Controle de Horas", page_icon="⏰", layout="centered")

# -----------------------
# CONFIGURAÇÃO GOOGLE SHEETS
# -----------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# --- Opção 1: Usar Streamlit Secrets (recomendado) ---
creds_dict = json.loads(st.secrets["GOOGLE_SHEETS_CREDS"])
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
client = gspread.authorize(creds)

# --- Configurações principais ---
SHEET_ID = st.secrets["SHEET_ID"]
SENHA_MESTRA = st.secrets["MASTER_PW"]
dias_semana_valores = {0:5,1:5,2:5,3:5,4:5,5:4,6:0}  # Segunda=0, Domingo=6

# --- Conecta abas do Google Sheets ---
sheet_horas = client.open_by_key(SHEET_ID).worksheet("Horas")
sheet_senhas = client.open_by_key(SHEET_ID).worksheet("Senhas")
sheet_faltas = client.open_by_key(SHEET_ID).worksheet("Faltas")

# -----------------------
# FUNÇÕES AUXILIARES
# -----------------------
def carregar_horas():
    data = sheet_horas.get_all_records()
    return {row['Nome']: int(row['Horas devidas']) for row in data}

def carregar_senhas():
    data = sheet_senhas.get_all_records()
    return {row['Nome']: row['Senha'] for row in data}

def atualizar_horas(nome, horas):
    data = sheet_horas.get_all_records()
    for i, row in enumerate(data, start=2):
        if row['Nome'] == nome:
            nova_hora = int(row['Horas devidas']) + int(horas)
            sheet_horas.update_cell(i, 2, nova_hora)
            return
    sheet_horas.append_row([nome, int(horas)])

def remover_horas(nome, horas):
    data = sheet_horas.get_all_records()
    for i, row in enumerate(data, start=2):
        if row['Nome'] == nome:
            nova_hora = max(0, int(row['Horas devidas']) - int(horas))
            sheet_horas.update_cell(i, 2, nova_hora)
            return

def registrar_falta(nome, data_falta, horas):
    sheet_faltas.append_row([nome, data_falta.strftime("%d/%m/%Y"), int(horas)])

def alterar_senha_sheet(nome, nova_senha):
    data = sheet_senhas.get_all_records()
    for i, row in enumerate(data, start=2):
        if row['Nome'] == nome:
            sheet_senhas.update_cell(i, 2, nova_senha)
            return
    sheet_senhas.append_row([nome, nova_senha])

def adicionar_nome(nome, senha_inicial="novaSenha123"):
    nomes = list(carregar_horas().keys())
    if nome in nomes:
        return False, "Nome já existe."
    sheet_horas.append_row([nome, 0])
    sheet_senhas.append_row([nome, senha_inicial])
    return True, "Nome adicionado com sucesso."

def remover_nome(nome):
    data_h = sheet_horas.get_all_records()
    for i, row in enumerate(data_h, start=2):
        if row['Nome'] == nome:
            sheet_horas.delete_row(i)
            break
    data_s = sheet_senhas.get_all_records()
    for i, row in enumerate(data_s, start=2):
        if row['Nome'] == nome:
            sheet_senhas.delete_row(i)
            break
    faltas = sheet_faltas.get_all_records()
    restantes = [[r['Nome'], r['Data'], r['Horas']] for r in faltas if r['Nome'] != nome]
    sheet_faltas.clear()
    sheet_faltas.append_row(["Nome", "Data", "Horas"])
    if restantes:
        sheet_faltas.append_rows(restantes)
    return True, "Nome removido com sucesso."

def gerar_senha_aleatoria(n_bytes=6):
    return secrets.token_urlsafe(n_bytes)

# -----------------------
# INTERFACE
# -----------------------
st.title("⏰ Controle de Horas Devidas (Admin Friendly)")

menu = st.radio("Menu", ["Adicionar horas", "Ver total de horas", "Remover horas", 
                         "Alterar senhas (usuário)", "Histórico de faltas", "Gerenciar nomes/segurança"])

horas_devidas = carregar_horas()
senhas_individuais = carregar_senhas()

# Adicionar horas
if menu == "Adicionar horas":
    st.subheader("➕ Adicionar horas (senha individual necessária)")
    nome = st.selectbox("Escolha o nome:", list(horas_devidas.keys()))
    senha = st.text_input("Digite a senha do nome selecionado:", type="password")
    if senha == senhas_individuais.get(nome, ""):
        data_falta = st.date_input("Escolha a data da falta:")
        if st.button("Adicionar horas"):
            dia_semana = data_falta.weekday()
            horas = dias_semana_valores.get(dia_semana, 0)
            if horas == 0:
                st.warning("Data selecionada é domingo — não adiciona horas.")
            else:
                atualizar_horas(nome, horas)
                registrar_falta(nome, data_falta, horas)
                st.success(f"{nome} teve adicionadas {horas}h no dia {data_falta.strftime('%d/%m/%Y')}")
    elif senha:
        st.error("Senha incorreta!")

# Ver total
elif menu == "Ver total de horas":
    st.subheader("📊 Total de horas devidas")
    for nome, total in horas_devidas.items():
        st.write(f"**{nome}:** {total} horas")

# Remover horas
elif menu == "Remover horas":
    st.subheader("🔐 Remover horas (senha mestra necessária)")
    senha = st.text_input("Digite a senha mestra:", type="password")
    if senha == SENHA_MESTRA:
        nome = st.selectbox("Escolha o nome:", list(horas_devidas.keys()))
        horas = st.number_input("Quantas horas deseja remover?", min_value=1, step=1)
        if st.button("Remover horas"):
            remover_horas(nome, horas)
            st.success(f"Removidas {horas}h de {nome}")
    elif senha:
        st.error("Senha mestra incorreta!")

# Alterar senhas
elif menu == "Alterar senhas (usuário)":
    st.subheader("🔑 Alterar senha individual (usuário ou admin)")
    modo = st.radio("Modo:", ["Alterar com senha atual do usuário", "Alterar como admin (senha mestra)"])
    if modo == "Alterar com senha atual do usuário":
        nome = st.selectbox("Escolha o nome:", list(senhas_individuais.keys()))
        senha_atual = st.text_input("Digite a senha atual do usuário:", type="password")
        if senha_atual == senhas_individuais.get(nome, ""):
            nova_senha = st.text_input("Digite a nova senha:", type="password", key="nova_senha_user")
            if st.button("Alterar minha senha"):
                alterar_senha_sheet(nome, nova_senha)
                st.success(f"Senha de {nome} alterada com sucesso.")
        elif senha_atual:
            st.error("Senha atual incorreta.")
    else:
        senha_mestra = st.text_input("Digite a senha mestra:", type="password", key="alterar_com_mestra")
        if senha_mestra == SENHA_MESTRA:
            nome = st.selectbox("Escolha o nome para alterar a senha:", list(senhas_individuais.keys()))
            nova_senha_manual = st.text_input("Senha manual:", type="password")
            if st.button("Definir senha manual"):
                if nova_senha_manual.strip():
                    alterar_senha_sheet(nome, nova_senha_manual.strip())
                    st.success(f"Senha de {nome} definida manualmente.")
                else:
                    st.error("Senha inválida.")
            if st.button("Gerar senha aleatória"):
                senha_gerada = gerar_senha_aleatoria()
                alterar_senha_sheet(nome, senha_gerada)
                st.success(f"Senha de {nome} alterada para: {senha_gerada}")
        elif senha_mestra:
            st.error("Senha mestra incorreta!")

# Histórico de faltas
elif menu == "Histórico de faltas":
    st.subheader("🗓 Histórico de faltas")
    faltas = sheet_faltas.get_all_records()
    if faltas:
        for f in faltas:
            st.write(f"{f['Nome']} — {f['Data']} — {f['Horas']}h")
    else:
        st.info("Nenhuma falta registrada ainda.")

# Gerenciar nomes
elif menu == "Gerenciar nomes/segurança":
    st.subheader("⚙️ Gerenciar nomes (senha mestra necessária)")
    senha = st.text_input("Digite a senha mestra:", type="password", key="gerenciar_nomes")
    if senha == SENHA_MESTRA:
        nova_acao = st.radio("Ação:", ["Adicionar nome", "Remover nome"])
        if nova_acao == "Adicionar nome":
            nome_novo = st.text_input("Digite o nome do novo funcionário:")
            senha_inicial = st.text_input("Senha inicial:", type="password", value="senha123")
            if st.button("Adicionar"):
                sucesso, msg = adicionar_nome(nome_novo, senha_inicial)
                if sucesso:
                    st.success(msg)
                else:
                    st.error(msg)
        else:
            nome_remover = st.selectbox("Escolha o nome a remover:", list(horas_devidas.keys()))
            if st.button("Remover"):
                sucesso, msg = remover_nome(nome_remover)
                if sucesso:
                    st.success(msg)
    elif senha:
        st.error("Senha mestra incorreta!")
