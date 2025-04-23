import json
from datetime import datetime
import requests

# --- Firebase URL base ---
FIREBASE_BASE_URL = "https://fechadura-faceid-default-rtdb.europe-west1.firebasedatabase.app"

# --- Obter todos os dados (usuarios e acessos) do Firebase ---
def obter_dados_firebase():
    try:
        resposta = requests.get(f"{FIREBASE_BASE_URL}/.json")
        if resposta.status_code == 200:
            return resposta.json()
        else:
            print("Erro ao obter dados do Firebase:", resposta.text)
            return {"usuarios": {}, "acessos": {}}
    except Exception as e:
        print("Erro ao contactar Firebase:", str(e))
        return {"usuarios": {}, "acessos": {}}

# --- Gravar acesso no Firebase ---
def registar_acesso(nome, metodo, status):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    acesso = {
        "usuario": nome,
        "timestamp": timestamp,
        "metodo": metodo,
        "status": status
    }

    try:
        resposta = requests.post(f"{FIREBASE_BASE_URL}/acessos.json", json=acesso)
        if resposta.status_code == 200:
            print("Acesso gravado no Firebase.")
        else:
            print("Erro ao gravar acesso:", resposta.text)
    except Exception as e:
        print("Erro ao contactar Firebase:", str(e))

# --- Autenticar por PIN ---
def autenticar_por_pin(pin_input):
    db = obter_dados_firebase()
    usuarios = db.get("usuarios", {})

    for key, dados in usuarios.items():
        if dados.get("pin") == pin_input:
            registar_acesso(dados["nome"], "PIN", "autenticado")
            print(f"Acesso autorizado para {dados['nome']}")
            return True

    registar_acesso("Desconhecido", "PIN", "falha")
    print("PIN inválido. Acesso negado.")
    return False

# --- Adicionar novo usuário ---
def adicionar_usuario(nome, pin, face_id=""):
    user_id = nome.lower().replace(" ", "_")  # Ex: "Diogo Pinto" -> "diogo_pinto"
    dados = {
        "nome": nome,
        "pin": pin,
        "face_id": face_id
    }

    try:
        resposta = requests.put(f"{FIREBASE_BASE_URL}/usuarios/{user_id}.json", json=dados)
        if resposta.status_code == 200:
            print(f"Usuário '{nome}' adicionado com sucesso.")
        else:
            print("Erro ao adicionar usuário:", resposta.text)
    except Exception as e:
        print("Erro ao contactar Firebase:", str(e))

# --- Função principal ---
def main():
    print("AUTENTICAÇÃO POR PIN")
    print("1. Inserir PIN")
    print("2. Adicionar novo usuário")
    escolha = input("Escolha a opção (1 ou 2): ")

    if escolha == "1":
        pin = input("Insira o PIN: ")
        autenticar_por_pin(pin)

    elif escolha == "2":
        nome = input("Nome do novo usuário: ")
        pin = input("PIN do usuário: ")
        adicionar_usuario(nome, pin)

    else:
        print("Opção inválida.")

# --- Execução ---
if __name__ == "__main__":
    main()
