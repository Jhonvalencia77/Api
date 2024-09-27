from fastapi import FastAPI   #Nos permite construir apis y hacer documentación fácil
from flask import Flask, render_template  # renderizar archivos HTML, solicitudes HTTP
from fastapi.middleware.wsgi import WSGIMiddleware  #Permite utilizar flask sobre fastapi
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects  #Gestionar los errores
import json         #datos en formato JSON
import threading    #múltiples operaciones en paralelo
import time         #Contar segundos
from typing import Dict, List, Optional    
from pydantic import BaseModel

# Creamos una instancia de la aplicación FastAPI
fastapi_app = FastAPI()

# Creamos una instancia de la aplicación Flask
flask_app = Flask(__name__)

# Creamos una lista para almacenar los datos de criptomonedas
dataCryptos = []  

# Modelo para representar el precio de las criptomonedas
class USDModel(BaseModel):
    price: float
    volume_24h: float
    percent_change_1h: float
    percent_change_24h: float
    market_cap: float

#De esta manera USD Es un diccionario y las claves son los valores en USDModel
class QuoteModel(BaseModel):
    USD: USDModel
    

# Modelo para representar una criptomoneda
class CryptoModel(BaseModel):
    id: int
    name: str
    symbol: str
    slug: str
    num_market_pairs: int
    date_added: str
    tags: List[str]
    max_supply: Optional[int]
    circulating_supply: float
    total_supply: float
    cmc_rank: int
    last_updated: str
    quote: QuoteModel  # hacemos que quote sea un diccionario que contiene USD

# Función para acceder a la API de criptomonedas
def Acceso_API():
    global dataCryptos  # Usamos la variable global
    api_key = 'd1c51888-744b-4368-82c9-e8ff4f3ab22b'  # Clave de la API
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"  # URL de la API
    parameters = {
        'start': '1',
        'limit': '10',  # Limitamos la consulta a 10 criptomonedas
        'convert': 'USD'  # Queremos los precios en USD
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,  # Agregamos la clave de la API en los encabezados
    }

    session = Session()  # Creamos una sesión para hacer la solicitud
    session.headers.update(headers)  # Actualizamos los encabezados de la sesión

    try:
        response = session.get(url, params=parameters)  # Hacemos la solicitud a la API
        dataCryptos = json.loads(response.text)['data']  # Guardamos solo la parte de 'data'        
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)  # Manejamos posibles errores

# Ruta para la página principal
@flask_app.route('/', methods=['GET'])
def index():
    Acceso_API()  # Llamamos a la función para obtener los datos
    return render_template('index.html', data=dataCryptos)  # Renderizamos la plantilla con los datos

# Endpoint para obtener los datos de criptomonedas
@fastapi_app.get("/cryptos", response_model=List[CryptoModel])
def get_cryptos() -> List[CryptoModel]:
    return dataCryptos  # Devolvemos los datos de criptomonedas


#Definimos el endpoint /cryptos/{id} para exponer datos de API REST
@fastapi_app.get("/cryptos/{id}", response_model=CryptoModel)
def get_crypto(id) -> CryptoModel:    
    id = int(id)
    for crypto in dataCryptos: #Ciclo itera a través de la lista de criptomonedas        
        if crypto['id'] == id: #Comparamos el id de la criptomoneda actual con el id proporcionado en URL
            return crypto  # Devuelve la criptomoneda encontrada 



# Montamos la aplicación Flask dentro de FastAPI
fastapi_app.mount("/", WSGIMiddleware(flask_app))

# Función que se ejecuta cada 60 segundos para actualizar los datos
def update_data():
    while True:
        Acceso_API()  # Actualizamos los datos
        time.sleep(60)  # Esperamos 60 segundos antes de actualizar nuevamente

# Iniciamos un hilo para que la función update_data corra en segundo plano
data_thread = threading.Thread(target=update_data)
data_thread.daemon = True  
data_thread.start()  # Iniciamos el hilo

'''
# Ejecutamos la aplicación FastAPI
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(fastapi_app, host='0.0.0.0', port=4000, log_level="info")  # Iniciamos el servidor en el puerto 4000
'''