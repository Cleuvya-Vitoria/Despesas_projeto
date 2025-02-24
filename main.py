from fastapi import FastAPI
from rotas import grupos, despesas, usuarios

app = FastAPI(title="API de Compartilhamento de Despesas")

@app.get("/")
def root():
    return {"mensagem": "Bem-vindo à API de Compartilhamento de Despesas!"}

app.include_router(grupos.router)
app.include_router(usuarios.router)
app.include_router(despesas.router)