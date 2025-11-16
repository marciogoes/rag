"""
Sistema de Gestão de Projetos
Desenvolvido por: Marcio Góes do Nascimento

Permite que administradores criem projetos e associem documentos a eles.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class GerenciadorProjetos:
    """Gerenciador de projetos para organização de documentos"""
    
    def __init__(self, arquivo_projetos: str = "data/projetos.json"):
        self.arquivo_projetos = arquivo_projetos
        self._garantir_diretorio()
        self._garantir_arquivo()
    
    def _garantir_diretorio(self):
        """Garante que o diretório data/ existe"""
        Path("data").mkdir(exist_ok=True)
    
    def _garantir_arquivo(self):
        """Garante que o arquivo de projetos existe"""
        if not os.path.exists(self.arquivo_projetos):
            self._salvar_projetos([])
    
    def _carregar_projetos(self) -> List[Dict]:
        """Carrega projetos do arquivo JSON"""
        try:
            with open(self.arquivo_projetos, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar projetos: {e}")
            return []
    
    def _salvar_projetos(self, projetos: List[Dict]):
        """Salva projetos no arquivo JSON"""
        try:
            with open(self.arquivo_projetos, 'w', encoding='utf-8') as f:
                json.dump(projetos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar projetos: {e}")
    
    def criar_projeto(
        self, 
        nome: str, 
        descricao: str, 
        usuario_criador: str
    ) -> Dict:
        """
        Cria um novo projeto (apenas admin)
        
        Args:
            nome: Nome do projeto
            descricao: Descrição do projeto
            usuario_criador: Username de quem criou
            
        Returns:
            Dict com dados do projeto criado
        """
        projetos = self._carregar_projetos()
        
        # Verificar se já existe projeto com esse nome
        if any(p['nome'].lower() == nome.lower() for p in projetos):
            raise ValueError(f"Já existe um projeto com o nome '{nome}'")
        
        # Gerar ID único
        proximo_id = max([p['id'] for p in projetos], default=0) + 1
        
        novo_projeto = {
            "id": proximo_id,
            "nome": nome,
            "descricao": descricao,
            "criado_por": usuario_criador,
            "data_criacao": datetime.now().isoformat(),
            "ativo": True,
            "total_documentos": 0
        }
        
        projetos.append(novo_projeto)
        self._salvar_projetos(projetos)
        
        print(f"✅ Projeto '{nome}' criado com sucesso! ID: {proximo_id}")
        return novo_projeto
    
    def listar_projetos(self, apenas_ativos: bool = True) -> List[Dict]:
        """
        Lista todos os projetos
        
        Args:
            apenas_ativos: Se True, retorna apenas projetos ativos
            
        Returns:
            Lista de projetos
        """
        projetos = self._carregar_projetos()
        
        if apenas_ativos:
            projetos = [p for p in projetos if p.get('ativo', True)]
        
        return projetos
    
    def buscar_projeto(self, projeto_id: int) -> Optional[Dict]:
        """
        Busca um projeto por ID
        
        Args:
            projeto_id: ID do projeto
            
        Returns:
            Dict com dados do projeto ou None
        """
        projetos = self._carregar_projetos()
        
        for projeto in projetos:
            if projeto['id'] == projeto_id:
                return projeto
        
        return None
    
    def buscar_projeto_por_nome(self, nome: str) -> Optional[Dict]:
        """
        Busca um projeto por nome
        
        Args:
            nome: Nome do projeto
            
        Returns:
            Dict com dados do projeto ou None
        """
        projetos = self._carregar_projetos()
        
        for projeto in projetos:
            if projeto['nome'].lower() == nome.lower():
                return projeto
        
        return None
    
    def atualizar_projeto(
        self, 
        projeto_id: int, 
        nome: Optional[str] = None,
        descricao: Optional[str] = None,
        ativo: Optional[bool] = None
    ) -> Dict:
        """
        Atualiza dados de um projeto
        
        Args:
            projeto_id: ID do projeto
            nome: Novo nome (opcional)
            descricao: Nova descrição (opcional)
            ativo: Novo status (opcional)
            
        Returns:
            Dict com dados atualizados
        """
        projetos = self._carregar_projetos()
        
        for i, projeto in enumerate(projetos):
            if projeto['id'] == projeto_id:
                if nome is not None:
                    # Verificar se novo nome já existe
                    if any(p['nome'].lower() == nome.lower() and p['id'] != projeto_id 
                           for p in projetos):
                        raise ValueError(f"Já existe um projeto com o nome '{nome}'")
                    projeto['nome'] = nome
                
                if descricao is not None:
                    projeto['descricao'] = descricao
                
                if ativo is not None:
                    projeto['ativo'] = ativo
                
                projeto['data_atualizacao'] = datetime.now().isoformat()
                projetos[i] = projeto
                self._salvar_projetos(projetos)
                
                print(f"✅ Projeto ID {projeto_id} atualizado com sucesso!")
                return projeto
        
        raise ValueError(f"Projeto ID {projeto_id} não encontrado")
    
    def deletar_projeto(self, projeto_id: int, deletar_documentos: bool = False):
        """
        Deleta ou desativa um projeto
        
        Args:
            projeto_id: ID do projeto
            deletar_documentos: Se True, marca documentos para deleção
        """
        projetos = self._carregar_projetos()
        
        for i, projeto in enumerate(projetos):
            if projeto['id'] == projeto_id:
                if deletar_documentos:
                    # Remover permanentemente
                    projetos.pop(i)
                    print(f"🗑️  Projeto '{projeto['nome']}' deletado permanentemente!")
                else:
                    # Apenas desativar
                    projetos[i]['ativo'] = False
                    projetos[i]['data_desativacao'] = datetime.now().isoformat()
                    print(f"⚠️  Projeto '{projeto['nome']}' desativado!")
                
                self._salvar_projetos(projetos)
                return
        
        raise ValueError(f"Projeto ID {projeto_id} não encontrado")
    
    def incrementar_contador_documentos(self, projeto_id: int):
        """
        Incrementa o contador de documentos de um projeto
        
        Args:
            projeto_id: ID do projeto
        """
        projetos = self._carregar_projetos()
        
        for i, projeto in enumerate(projetos):
            if projeto['id'] == projeto_id:
                projetos[i]['total_documentos'] = projeto.get('total_documentos', 0) + 1
                self._salvar_projetos(projetos)
                return
        
        raise ValueError(f"Projeto ID {projeto_id} não encontrado")
    
    def decrementar_contador_documentos(self, projeto_id: int):
        """
        Decrementa o contador de documentos de um projeto
        
        Args:
            projeto_id: ID do projeto
        """
        projetos = self._carregar_projetos()
        
        for i, projeto in enumerate(projetos):
            if projeto['id'] == projeto_id:
                total = projeto.get('total_documentos', 0)
                projetos[i]['total_documentos'] = max(0, total - 1)
                self._salvar_projetos(projetos)
                return
        
        raise ValueError(f"Projeto ID {projeto_id} não encontrado")
    
    def estatisticas_projeto(self, projeto_id: int) -> Dict:
        """
        Retorna estatísticas de um projeto
        
        Args:
            projeto_id: ID do projeto
            
        Returns:
            Dict com estatísticas
        """
        projeto = self.buscar_projeto(projeto_id)
        
        if not projeto:
            raise ValueError(f"Projeto ID {projeto_id} não encontrado")
        
        return {
            "projeto_id": projeto['id'],
            "nome": projeto['nome'],
            "total_documentos": projeto.get('total_documentos', 0),
            "ativo": projeto.get('ativo', True),
            "criado_em": projeto.get('data_criacao'),
            "criado_por": projeto.get('criado_por')
        }


# Instância global
gerenciador_projetos = GerenciadorProjetos()


if __name__ == "__main__":
    # Teste do sistema
    print("=" * 60)
    print("🗂️  TESTE DO SISTEMA DE PROJETOS")
    print("   Desenvolvido por: Marcio Góes do Nascimento")
    print("=" * 60)
    print()
    
    # Tentar criar projeto teste
    try:
        projeto = gerenciador_projetos.criar_projeto(
            nome="Projeto Teste",
            descricao="Projeto de teste do sistema",
            usuario_criador="marcio"
        )
        print(f"\n📋 Projeto criado: {projeto}")
    except ValueError as e:
        print(f"\n⚠️  {e}")
        print("   Buscando projeto existente...")
        projeto = gerenciador_projetos.buscar_projeto_por_nome("Projeto Teste")
        if projeto:
            print(f"   ✅ Encontrado: [{projeto['id']}] {projeto['nome']}")
    
    # Listar projetos
    print("\n📋 Projetos cadastrados:")
    projetos = gerenciador_projetos.listar_projetos()
    if not projetos:
        print("   Nenhum projeto encontrado")
    else:
        for p in projetos:
            print(f"  - [{p['id']}] {p['nome']}: {p['descricao']}")
    
    print("\n✅ Sistema de projetos funcionando corretamente!")
