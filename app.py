# Importamos las bibliotecas necesarias
from fastapi import FastAPI
from flask import Flask, render_template
from fastapi.middleware.wsgi import WSGIMiddleware
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import threading
import time
from typing import Dict, List, Optional
from pydantic import BaseModel

# Creamos una instancia de la aplicación FastAPI
fastapi_app = FastAPI()

# Creamos una instancia de la aplicación Flask
flask_app = Flask(__name__)

# Variable global para almacenar los datos de criptomonedas
dataCryptos = []  # Cambiamos a una lista vacía

# Modelo para representar el precio de las criptomonedas
class USDModel(BaseModel):
    price: float
    volume_24h: float
    percent_change_1h: float
    percent_change_24h: float
    market_cap: float
    
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
    quote: QuoteModel  # Contiene datos de la criptomoneda en diferentes monedas

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



@fastapi_app.get("/cryptos/{id}", response_model=CryptoModel)
def get_crypto(id) -> CryptoModel:    
    id = int(id)
    for crypto in dataCryptos:
        print(crypto)
        if crypto['id'] == id:
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
data_thread.daemon = True  # Hacemos que el hilo se cierre al terminar la aplicación
data_thread.start()  # Iniciamos el hilo

# Ejecutamos la aplicación FastAPI
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(fastapi_app, host='0.0.0.0', port=4000, log_level="info")  # Iniciamos el servidor en el puerto 4000
