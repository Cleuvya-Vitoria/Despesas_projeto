from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
import os

# Carregar variáveis do arquivo .env
load_dotenv()

# URL do MongoDB do arquivo .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Valida se a URL foi carregada corretamente
if not DATABASE_URL:
    raise ValueError("A variável de ambiente DATABASE_URL não foi definida.")

# Criar o cliente do MongoDB
client = AsyncIOMotorClient(DATABASE_URL)

# Definir o banco de dados a ser usado
db = client.get_database("facilitae")

# Criar uma instância do AIOEngine do ODMantic
engine = AIOEngine(client=client, database="facilitae")

# Função para retornar a instância do AIOEngine
def get_engine() -> AIOEngine:
    return engine