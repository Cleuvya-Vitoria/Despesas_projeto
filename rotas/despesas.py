from fastapi import APIRouter, HTTPException, Query # paginação teve o query
from database import get_engine
from models import Despesa, Grupo, Usuario
from odmantic import ObjectId

from starlette import status
from typing import List


router = APIRouter(
    prefix="/despesas",
    tags=["despesas"],
)

engine = get_engine()


# 📌 Função auxiliar para buscar uma despesa ou retornar erro 404
async def get_despesa_or_404(despesa_id: str) -> Despesa:
    despesa = await engine.find_one(Despesa, Despesa.id == ObjectId(despesa_id))
    if not despesa:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    return despesa


# Criar uma despesa
@router.post("/", response_model=Despesa)
async def criar_despesa(despesa: Despesa):
    await engine.save(despesa)
    return despesa


# Atualizar uma despesa
@router.put("/{despesa_id}", response_model=Despesa)
async def atualizar_despesa(despesa_id: str, despesa_atualizada: Despesa):
    despesa = await get_despesa_or_404(despesa_id)

    despesa.titulo = despesa_atualizada.titulo
    despesa.valor = despesa_atualizada.valor
    despesa.data = despesa_atualizada.data
    despesa.grupo_id = despesa_atualizada.grupo_id
    despesa.usuarios_ids = despesa_atualizada.usuarios_ids

    await engine.save(despesa)
    return despesa


# Excluir uma despesa
@router.delete("/{despesa_id}")
async def excluir_despesa(despesa_id: str):
    despesa = await get_despesa_or_404(despesa_id)
    await engine.delete(despesa)
    return {"message": "Despesa deletada com sucesso!"}


# Listar todas as despesas
# @router.get("/", response_model=list[Despesa])
# async def listar_todas_despesas():
#     return await engine.find(Despesa)

@router.get(
    "/",
    response_model=List[Despesa],
    status_code=status.HTTP_200_OK
)
async def listar_todas_despesas(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=5, le=100)
) -> List[Despesa]:
    """
    Retorna uma lista de despesas com paginação, sempre ordenando por 'data'.
    """

    engine = get_engine()  # Sem 'await', pois get_engine() não é assíncrono

    despesas = await engine.find(
        Despesa,
        sort=Despesa.data,  # Ordenação padrão por 'data'
        skip=skip,
        limit=limit
    )

    return despesas


# Buscar despesa pelo ID
@router.get("/{despesa_id}", response_model=Despesa)
async def pegar_despesa_por_id(despesa_id: str):
    return await get_despesa_or_404(despesa_id)


# Listar despesas por grupo
@router.get("/grupo/{grupo_id}", response_model=list[Despesa])
async def listar_despesas_por_grupo(grupo_id: str):
    grupo = await engine.find_one(Grupo, Grupo.id == ObjectId(grupo_id))

    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")

    despesas = await engine.find(Despesa, Despesa.grupo_id == grupo.id)
    return despesas


# Listar todas as despesas de um usuário
# @router.get("/usuario/{usuario_id}", response_model=list[Despesa])
# async def listar_despesas_por_usuario(usuario_id: str):
#     usuario = await engine.find_one(Usuario, Usuario.id == ObjectId(usuario_id))

#     if not usuario:
#         raise HTTPException(status_code=404, detail="Usuário não encontrado")

#     despesas = await engine.find(Despesa, Despesa.usuarios_ids==usuario.id)
#     return despesas
@router.get("/usuario/{usuario_id}", response_model=list[Despesa])
async def listar_despesas_por_usuario(usuario_id: str):
    # Encontra o usuário usando o ID como string
    usuario = await engine.find_one(Usuario, Usuario.id == usuario_id)

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Busca despesas onde o id do usuário está contido na lista de usuarios_ids
    despesas = await engine.find(Despesa, Despesa.usuarios_ids == usuario.id)
    
    return despesas