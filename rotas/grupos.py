from fastapi import APIRouter, HTTPException, Query
from database import get_engine
from models import Grupo, Usuario, Despesa
from odmantic import ObjectId
import re

router = APIRouter(
    prefix="/grupos",
    tags=["grupos"],
)

engine = get_engine()


#Função auxiliar para buscar um grupo ou retornar erro 404
async def get_grupo_or_404(grupo_id: str) -> Grupo:
    grupo = await engine.find_one(Grupo, Grupo.id == ObjectId(grupo_id))
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    return grupo


# Criar um grupo
@router.post("/", response_model=Grupo)
async def criar_grupo(grupo: Grupo):
    await engine.save(grupo)
    return grupo


# Atualizar um grupo (todos os dados)
@router.put("/{grupo_id}", response_model=Grupo)
async def atualizar_grupo(grupo_id: str, grupo_atualizado: Grupo):
    grupo = await get_grupo_or_404(grupo_id)
    grupo.nome = grupo_atualizado.nome
    grupo.usuarios = grupo_atualizado.usuarios
    await engine.save(grupo)
    return grupo


@router.delete("/{grupo_id}")
async def excluir_grupo(grupo_id: str):
    grupo = await get_grupo_or_404(grupo_id)
    await engine.delete(grupo)
    return {"message": "Grupo deletado com sucesso!"}


# Adicionar usuário ao grupo
@router.post("/{grupo_id}/usuarios/{usuario_id}")
async def adicionar_usuario_ao_grupo(grupo_id: str, usuario_id: str):
    grupo = await get_grupo_or_404(grupo_id)
    usuario = await engine.find_one(Usuario, Usuario.id == ObjectId(usuario_id))

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if usuario.id in grupo.usuarios:
        raise HTTPException(status_code=400, detail="Usuário já está no grupo")

    grupo.usuarios.append(usuario.id)
    await engine.save(grupo)

    return {"message": "Usuário adicionado ao grupo com sucesso!"}


# Remover usuário do grupo
@router.delete("/{grupo_id}/usuarios/{usuario_id}")
async def remover_usuario_do_grupo(grupo_id: str, usuario_id: str):
    grupo = await get_grupo_or_404(grupo_id)

    if usuario_id not in grupo.usuarios:
        raise HTTPException(status_code=404, detail="Usuário não encontrado no grupo")

    grupo.usuarios.remove(usuario_id)
    await engine.save(grupo)

    return {"message": "Usuário removido do grupo com sucesso!"}


# Ver todos os usuários de um grupo
@router.get("/{grupo_id}/usuarios", response_model=list[Usuario])
async def listar_usuarios_do_grupo(grupo_id: str):
    grupo = await get_grupo_or_404(grupo_id)

    usuarios = await engine.find(Usuario, Usuario.id.in_(grupo.usuarios))
    return usuarios


# Adicionar despesa ao grupo
@router.post("/{grupo_id}/despesas/{despesa_id}")
async def adicionar_despesa_ao_grupo(grupo_id: str, despesa_id: str):
    grupo = await get_grupo_or_404(grupo_id)
    despesa = await engine.find_one(Despesa, Despesa.id == ObjectId(despesa_id))

    if not despesa:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")

    if despesa.id in grupo.despesas:
        raise HTTPException(status_code=400, detail="Despesa já adicionada ao grupo")

    grupo.despesas.append(despesa.id)
    await engine.save(grupo)

    return {"message": "Despesa adicionada ao grupo com sucesso!"}


# Remover despesa do grupo
@router.delete("/{grupo_id}/despesas/{despesa_id}")
async def remover_despesa_do_grupo(grupo_id: str, despesa_id: str):
    grupo = await get_grupo_or_404(grupo_id)

    if despesa_id not in grupo.despesas:
        raise HTTPException(status_code=404, detail="Despesa não encontrada no grupo")

    grupo.despesas.remove(despesa_id)
    await engine.save(grupo)

    return {"message": "Despesa removida do grupo com sucesso!"}


# Ver todas as despesas de um grupo
@router.get("/{grupo_id}/despesas", response_model=list[Despesa])
async def listar_despesas_do_grupo(grupo_id: str):
    grupo = await get_grupo_or_404(grupo_id)

    despesas = await engine.find(Despesa, Despesa.id.in_(grupo.despesas))
    return despesas


# Ver todos os grupos
@router.get("/", response_model=list[Grupo])
async def listar_todos_grupos():
    return await engine.find(Grupo)


# Ver um grupo específico pelo ID
@router.get("/{grupo_id}", response_model=Grupo)
async def pegar_grupo_por_id(grupo_id: str):
    return await get_grupo_or_404(grupo_id)


# Busca parcial nos nomes dos grupos
@router.get("/buscar", response_model=list[Grupo])
async def buscar_grupo_por_nome(query: str = Query(..., description="Nome parcial do grupo para busca")):
    regex = re.compile(query, re.IGNORECASE)
    grupos = await engine.find(Grupo, Grupo.nome.match(regex))
    return grupos


# Ver todos os grupos em ordem alfabética
@router.get("/ordenados", response_model=list[Grupo])
async def listar_grupos_ordenados():
    return await engine.find(Grupo, sort=Grupo.nome)