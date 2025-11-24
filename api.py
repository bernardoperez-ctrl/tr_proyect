from fastapi import FastAPI
import jwt
import time
import requests

app = FastAPI()

# --- CONFIGURACIÓN (LLENA ESTOS DATOS) ---

# 1. Tu Integration Key (Client ID)
client_id = "ddbd0494-9311-462e-ad4c-2bd682626b45"

# 2. Tu User ID (IMPORTANTE: Es el ID largo con guiones, NO tu email)
# Lo puedes ver en Apps and Keys -> Arriba donde dice "My Account Information" -> User ID
user_id = "a8a19aa3-e45b-48fa-a4fa-ac65983744c6"

# 3. Servidor de Auth (account-d es para DEMO)
oauth_server = "account-d.docusign.com"
base_url = "https://account-d.docusign.com/oauth/token"

# 4. Nombre de tu archivo de llave privada (el que guardaste en el Paso 1)
private_key_filename = "private_key.pem"

# -----------------------------------------

def obtener_token_jwt():
    # Leemos la llave privada del archivo
    try:
        with open(private_key_filename, 'r') as f:
            private_key = f.read()
    except FileNotFoundError:
        print(f"Error: No encuentro el archivo '{private_key_filename}'")
        return

    # Creamos el "Claim" (los datos del token)
    iat = int(time.time())
    exp = iat + 3600 # El token dura 1 hora

    payload = {
        "iss": client_id,       # Quién emite (Tu App)
        "sub": user_id,         # A nombre de quién (Tu Usuario)
        "aud": oauth_server,    # Audiencia (DocuSign)
        "iat": iat,             # Cuándo se creó
        "exp": exp,             # Cuándo expira
        "scope": "signature impersonation" # Permisos requeridos
    }

    # Generamos el JWT firmado con tu llave privada
    try:
        token_jwt_generado = jwt.encode(
            payload,
            private_key,
            algorithm="RS256"
        )
        print(token_jwt_generado)
        print(f"\n1. JWT Generado exitosamente (Firma RSA creada).")
    except Exception as e:
        print(f"Error generando JWT: {e}")
        return

    # Ahora intercambiamos ese JWT por el Access Token real
    print("2. Contactando a DocuSign para obtener Access Token...")

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        'assertion': token_jwt_generado
    }

    response = requests.post(base_url, headers=headers, data=data)

    if response.status_code == 200:
        access_token = response.json().get("access_token")
        print("\n¡ÉXITO! ------------------------------------------------")
        print(f"Access Token recibido: {access_token}")
        print("Este token ya sirve para llamar a la API igual que en Postman.")
        return access_token
    else:
        print(f"\nError al obtener token: {response.status_code}")
        print(response.text)

@app.get("/token")
def obtener_token():
    return obtener_token_jwt()
