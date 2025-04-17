# Autenticação por PIN ou QR Code simulada e gravação no Firebase (ou mock JSON)

import json
from datetime import datetime
import requests
from pyzbar.pyzbar import decode
from PIL import Image

# --- Configurações ---

# URL do Firebase Realtime Database (ajusta para o teu projeto)
FIREBASE_ACESSOS_URL = "https://fechadura-faceid-default-rtdb.europe-west1.firebasedatabase.app"

# Nome do ficheiro local com a "base de dados" mockada
FICHEIRO_DB = "mock-dados.json"

# --- Função para ler QR Code a partir de imagem ---
def ler_qr(imagem):
    resultado = decode(Image.open(imagem))
    if resultado:
        return resultado[0].data.decode()  # Extrai o conteúdo do QR code
    return None

# --- Função para autenticar por PIN (inserido ou vindo de QR) ---
def autenticar_por_pin(pin_input, db):
    usuarios = db["usuarios"]
    for key, dados in usuarios.items():
        if dados["pin"] == pin_input:
            registar_acesso(dados["nome"], "PIN", "autenticado", db)
            print(f"\n✅ Acesso autorizado para {dados['nome']}")
            return True

    registar_acesso("Desconhecido", "PIN", "falha", db)
    print("\n❌ PIN inválido. Acesso negado.")
    return False

# --- Função para registar acesso ---
def registar_acesso(nome, metodo, status, db):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    acesso = {
        "usuario": nome,
        "timestamp": timestamp,
        "metodo": metodo,
        "status": status
    }

    # Opcional: gravar localmente no mock JSON
    acesso_id = f"acesso{len(db['acessos']) + 1}"
    db["acessos"][acesso_id] = acesso

    # Enviar para Firebase
    try:
        resposta = requests.post(FIREBASE_ACESSOS_URL, json=acesso)
        if resposta.status_code == 200:
            print("✅ Acesso também gravado no Firebase.")
        else:
            print("⚠️ Erro ao gravar no Firebase:", resposta.text)
    except Exception as e:
        print("⚠️ Exceção ao contactar Firebase:", str(e))

# --- Função principal ---
def main():
    # Carregar dados locais
    with open(FICHEIRO_DB, "r") as f:
        db = json.load(f)

    print("\n🛂 AUTENTICAÇÃO POR PIN OU QR CODE")
    print("1. Inserir PIN manualmente")
    print("2. Ler PIN via QR Code")
    escolha = input("Escolha a opção (1 ou 2): ")

    if escolha == "1":
        pin = input("\nInsere o PIN: ")
    elif escolha == "2":
        caminho = input("\nCaminho da imagem com QR code: ")
        pin = ler_qr(caminho)
        if not pin:
            print("\n❌ Não foi possível ler QR code.")
            return
        print(f"\n📷 PIN lido do QR: {pin}")
    else:
        print("\nOpção inválida.")
        return

    autenticar_por_pin(pin, db)

    # Guardar base de dados atualizada (acessos) localmente
    with open("mock-dados-atualizado.json", "w") as f:
        json.dump(db, f, indent=2)

# --- Execução ---
if __name__ == "__main__":
    main()
