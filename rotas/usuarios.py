from fastapi import APIRouter, HTTPException, Query
from database import get_engine
from models import Usuario, Grupo, Despesa
from odmantic import ObjectId
import re
from starlette import status
from typing import List



router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"],
)

engine = get_engine()


# Função buscar um usuário ou retornar erro
async def get_usuario_or_404(usuario_id: str) -> Usuario:
    usuario = await engine.find_one(Usuario, Usuario.id == ObjectId(usuario_id))
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


# Criar um usuário
@router.post("/", response_model=Usuario)
async def criar_usuario(usuario: Usuario):
    await engine.save(usuario)
    return usuario


# Atualizar um usuário
@router.put("/{usuario_id}", response_model=Usuario)
async def atualizar_usuario(usuario_id: str, usuario_atualizado: Usuario):
    usuario = await get_usuario_or_404(usuario_id)

    usuario.nome = usuario_atualizado.nome
    usuario.email = usuario_atualizado.email

    await engine.save(usuario)
    return usuario


# Excluir um usuário
@router.delete("/{usuario_id}")
async def excluir_usuario(usuario_id: str):
    usuario = await get_usuario_or_404(usuario_id)
    await engine.delete(usuario)
    return {"message": "Usuário deletado com sucesso!"}


# Ver todos os usuários
# @router.get("/", response_model=list[Usuario])
# async def listar_usuarios():
#     return await engine.find(Usuario)

@router.get(
    "/",
    response_model=List[Usuario],
    status_code=status.HTTP_200_OK
)
async def listar_usuarios(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=5, le=100)
) -> List[Usuario]:
    """
    Retorna uma lista de usuários com paginação, sempre ordenando por 'nome'.
    """

    engine = get_engine()  # Removido 'await'

    usuarios = await engine.find(
        Usuario,
        sort=Usuario.nome,  # Sempre ordena por 'name'
        skip=skip,
        limit=limit
    )

    return usuarios


# Ver um usuário específico pelo ID
@router.get("/{usuario_id}", response_model=Usuario)
async def pegar_usuario_por_id(usuario_id: str):
    return await get_usuario_or_404(usuario_id)


# Busca parcial por nome do usuário
@router.get("/buscar", response_model=list[Usuario])
async def buscar_usuario_por_nome(query: str = Query(..., description="Nome parcial do usuário para busca")):
    regex = re.compile(query, re.IGNORECASE)
    usuarios = await engine.find(Usuario, Usuario.nome.match(regex))
    return usuarios


# Ver todos os grupos de um usuário
@router.get("/{usuario_id}/grupos", response_model=list[Grupo])
async def listar_grupos_do_usuario(usuario_id: str):
    usuario = await get_usuario_or_404(usuario_id)

    grupos = await engine.find(Grupo, Grupo.membros.contains(usuario.id))
    return grupos


# Ver todas as despesas de um usuário
# @router.get("/{usuario_id}/despesas", response_model=list[Despesa])
# async def listar_despesas_do_usuario(usuario_id: str):
#     usuario = await get_usuario_or_404(usuario_id)

#     despesas = await engine.find(Despesa, Despesa.usuarios_ids==usuario.id)
#     return despesas
@router.get("/{usuario_id}/despesas", response_model=list[Despesa])
async def listar_despesas_do_usuario(usuario_id: str):
    usuario = await get_usuario_or_404(usuario_id)

    # Log para verificar o ID do usuário encontrado
    print(f"Usuário encontrado: {usuario}")

    # Buscando despesas onde o ID do usuário está na lista de usuarios_ids
    despesas = await engine.find(Despesa, Despesa.usuarios_ids == usuario.id)
    
    # Log para verificar as despesas encontradas
    print(f"Despesas encontradas: {despesas}")

    return despesas


# Excluir próprio usuário (somente se não houver despesas pendentes)
# @router.delete("/{usuario_id}/autoexcluir")
# async def autoexcluir_usuario(usuario_id: str):
#     usuario = await get_usuario_or_404(usuario_id)

#     despesas_pendentes = await engine.find(Despesa, Despesa.usuarios_ids.contains(usuario.id))
#     if despesas_pendentes:
#         raise HTTPException(status_code=400, detail="Não é possível excluir enquanto houver despesas pendentes")

#     await engine.delete(usuario)
#     return {"message": "Usuário excluído com sucesso!"}

@router.delete("/{usuario_id}/autoexcluir")
async def autoexcluir_usuario(usuario_id: str):
    usuario = await get_usuario_or_404(usuario_id)

    # Modifique a consulta para usar um operador de consulta apropriado
    despesas_pendentes = await engine.find(Despesa, Despesa.usuarios_ids == usuario.id)
    
    if despesas_pendentes:
        raise HTTPException(status_code=400, detail="Não é possível excluir enquanto houver despesas pendentes")

    await engine.delete(usuario)
    return {"message": "Usuário excluído com sucesso!"}