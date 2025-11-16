"""
Rotas de API para Gestão de Projetos
Desenvolvido por: Marcio Góes do Nascimento

Apenas administradores podem criar, editar e deletar projetos.
Todos os usuários podem listar e visualizar projetos.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from auth import usuario_atual
from projetos import gerenciador_projetos

# Router para projetos
router = APIRouter(prefix="/projetos", tags=["Projetos"])


# Modelos Pydantic
class ProjetoCriar(BaseModel):
    nome: str
    descricao: str


class ProjetoAtualizar(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    ativo: Optional[bool] = None


class ProjetoResponse(BaseModel):
    id: int
    nome: str
    descricao: str
    criado_por: str
    data_criacao: str
    ativo: bool
    total_documentos: int


# Funções auxiliares
def verificar_admin(usuario: dict):
    """Verifica se o usuário é administrador"""
    if usuario['username'] != 'admin':
        raise HTTPException(
            status_code=403,
            detail="Apenas administradores podem realizar esta ação"
        )


# Rotas

@router.get("/", response_model=List[ProjetoResponse])
async def listar_projetos(
    apenas_ativos: bool = True,
    current_user: dict = Depends(usuario_atual)
):
    """
    Lista todos os projetos
    
    - Todos os usuários autenticados podem listar projetos
    - Por padrão, retorna apenas projetos ativos
    """
    try:
        projetos = gerenciador_projetos.listar_projetos(apenas_ativos=apenas_ativos)
        return projetos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{projeto_id}", response_model=ProjetoResponse)
async def buscar_projeto(
    projeto_id: int,
    current_user: dict = Depends(usuario_atual)
):
    """
    Busca um projeto por ID
    
    - Todos os usuários autenticados podem visualizar projetos
    """
    try:
        projeto = gerenciador_projetos.buscar_projeto(projeto_id)
        
        if not projeto:
            raise HTTPException(
                status_code=404,
                detail=f"Projeto ID {projeto_id} não encontrado"
            )
        
        return projeto
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=ProjetoResponse)
async def criar_projeto(
    projeto: ProjetoCriar,
    current_user: dict = Depends(usuario_atual)
):
    """
    Cria um novo projeto
    
    - **APENAS ADMINISTRADORES** podem criar projetos
    """
    try:
        # Verificar se é admin
        verificar_admin(current_user)
        
        novo_projeto = gerenciador_projetos.criar_projeto(
            nome=projeto.nome,
            descricao=projeto.descricao,
            usuario_criador=current_user['username']
        )
        
        return novo_projeto
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{projeto_id}", response_model=ProjetoResponse)
async def atualizar_projeto(
    projeto_id: int,
    dados: ProjetoAtualizar,
    current_user: dict = Depends(usuario_atual)
):
    """
    Atualiza um projeto existente
    
    - **APENAS ADMINISTRADORES** podem atualizar projetos
    """
    try:
        # Verificar se é admin
        verificar_admin(current_user)
        
        projeto_atualizado = gerenciador_projetos.atualizar_projeto(
            projeto_id=projeto_id,
            nome=dados.nome,
            descricao=dados.descricao,
            ativo=dados.ativo
        )
        
        return projeto_atualizado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{projeto_id}")
async def deletar_projeto(
    projeto_id: int,
    deletar_documentos: bool = False,
    current_user: dict = Depends(usuario_atual)
):
    """
    Deleta ou desativa um projeto
    
    - **APENAS ADMINISTRADORES** podem deletar projetos
    - Por padrão, apenas desativa (ativo=False)
    - Se deletar_documentos=True, remove permanentemente
    """
    try:
        # Verificar se é admin
        verificar_admin(current_user)
        
        gerenciador_projetos.deletar_projeto(
            projeto_id=projeto_id,
            deletar_documentos=deletar_documentos
        )
        
        acao = "deletado permanentemente" if deletar_documentos else "desativado"
        
        return {
            'success': True,
            'message': f'Projeto {acao} com sucesso'
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{projeto_id}/estatisticas")
async def estatisticas_projeto(
    projeto_id: int,
    current_user: dict = Depends(usuario_atual)
):
    """
    Retorna estatísticas de um projeto
    
    - Todos os usuários autenticados podem ver estatísticas
    """
    try:
        stats = gerenciador_projetos.estatisticas_projeto(projeto_id)
        return stats
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
