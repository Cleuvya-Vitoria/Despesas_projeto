from odmantic import Model, Field
from datetime import datetime
from typing import List, Optional

class Grupo(Model):
     # não é necessário definir id manualmente, ele já existe em Model.
    nome: str
    usuarios: List[str] = []  # Lista de IDs dos usuários do grupo
    data_criacao: datetime = datetime.utcnow()  # Data automática de criação

class Usuario(Model):
    nome: str
    email: str
    grupo_id: Optional[str] = None  # O usuário pode ou não estar em um grupo

class Despesa(Model):
    titulo: str
    valor: float
    data: datetime = datetime.utcnow()  # Data automática da despesa
    grupo_id: str  # Referência ao grupo
    usuarios_ids: List[str]  = Field(default_factory=list)  # IDs dos usuários associados #= []  # Lista de IDs dos usuários envolvidos