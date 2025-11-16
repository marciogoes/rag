"""
Funções de Exportação por Projeto
Desenvolvido por: Marcio Góes do Nascimento

Exporta documentos separados por projeto
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from projetos import gerenciador_projetos


class ExportadorProjetos:
    """Exportador de documentos separados por projeto"""
    
    def __init__(self, rag_engine, export_dir: str = "./exports"):
        self.rag_engine = rag_engine
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(exist_ok=True)
    
    def _agrupar_por_projeto(self, results: dict) -> Dict[int, List[dict]]:
        """
        Agrupa documentos por projeto_id
        
        Args:
            results: Resultados do ChromaDB
            
        Returns:
            Dict com projeto_id como chave e lista de documentos como valor
        """
        documentos_por_projeto = {}
        
        for i in range(len(results['ids'])):
            metadata = results['metadatas'][i] if results['metadatas'] else {}
            projeto_id = metadata.get('projeto_id', 0)  # 0 = sem projeto
            
            if projeto_id not in documentos_por_projeto:
                documentos_por_projeto[projeto_id] = []
            
            documentos_por_projeto[projeto_id].append({
                'id': results['ids'][i],
                'conteudo': results['documents'][i],
                'metadata': metadata
            })
        
        return documentos_por_projeto
    
    def exportar_json_por_projeto(self, usuario_exportador: dict) -> str:
        """
        Exporta documentos para JSON separados por projeto
        
        Args:
            usuario_exportador: Dict com dados do usuário que está exportando
            
        Returns:
            Caminho do arquivo JSON exportado
        """
        results = self.rag_engine.collection.get()
        documentos_por_projeto = self._agrupar_por_projeto(results)
        
        dados_exportados = {
            'exportado_por': usuario_exportador['nome'],
            'data_exportacao': datetime.now().isoformat(),
            'desenvolvedor': 'Marcio Góes do Nascimento',
            'total_projetos': len(documentos_por_projeto),
            'total_documentos': len(set([m.get('doc_id') for m in results['metadatas']])),
            'total_chunks': len(results['ids']),
            'projetos': []
        }
        
        # Para cada projeto, adicionar informações
        for projeto_id, documentos in documentos_por_projeto.items():
            projeto_info = {
                'projeto_id': projeto_id,
                'total_chunks': len(documentos),
                'documentos': documentos
            }
            
            # Se projeto_id != 0, buscar informações do projeto
            if projeto_id != 0:
                projeto = gerenciador_projetos.buscar_projeto(projeto_id)
                if projeto:
                    projeto_info['nome_projeto'] = projeto['nome']
                    projeto_info['descricao_projeto'] = projeto['descricao']
                    projeto_info['criado_por'] = projeto['criado_por']
            else:
                projeto_info['nome_projeto'] = 'Sem Projeto'
                projeto_info['descricao_projeto'] = 'Documentos não associados a projetos'
            
            dados_exportados['projetos'].append(projeto_info)
        
        # Salvar arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_path = self.export_dir / f"export_por_projeto_{usuario_exportador['username']}_{timestamp}.json"
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(dados_exportados, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON exportado: {export_path}")
        return str(export_path)
    
    def exportar_csv_por_projeto(self, usuario_exportador: dict) -> str:
        """
        Exporta documentos para CSV com coluna de projeto
        
        Args:
            usuario_exportador: Dict com dados do usuário que está exportando
            
        Returns:
            Caminho do arquivo CSV exportado
        """
        results = self.rag_engine.collection.get()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_path = self.export_dir / f"export_por_projeto_{usuario_exportador['username']}_{timestamp}.csv"
        
        with open(export_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'ID',
                'Projeto_ID',
                'Nome_Projeto',
                'Conteudo',
                'Arquivo',
                'Formato',
                'Chunk',
                'Exportado_Por'
            ])
            
            for i in range(len(results['ids'])):
                metadata = results['metadatas'][i] if results['metadatas'] else {}
                projeto_id = metadata.get('projeto_id', 0)
                
                # Buscar nome do projeto
                if projeto_id != 0:
                    projeto = gerenciador_projetos.buscar_projeto(projeto_id)
                    nome_projeto = projeto['nome'] if projeto else 'Projeto Desconhecido'
                else:
                    nome_projeto = 'Sem Projeto'
                
                writer.writerow([
                    results['ids'][i],
                    projeto_id,
                    nome_projeto,
                    results['documents'][i],
                    metadata.get('filename', ''),
                    metadata.get('format', ''),
                    metadata.get('chunk_index', ''),
                    usuario_exportador['nome']
                ])
        
        print(f"✅ CSV exportado: {export_path}")
        return str(export_path)
    
    def exportar_projeto_especifico_json(
        self, 
        projeto_id: int, 
        usuario_exportador: dict
    ) -> str:
        """
        Exporta apenas documentos de um projeto específico para JSON
        
        Args:
            projeto_id: ID do projeto a ser exportado
            usuario_exportador: Dict com dados do usuário que está exportando
            
        Returns:
            Caminho do arquivo JSON exportado
        """
        # Buscar informações do projeto
        projeto = gerenciador_projetos.buscar_projeto(projeto_id)
        if not projeto:
            raise ValueError(f"Projeto ID {projeto_id} não encontrado")
        
        # Buscar documentos do projeto
        results = self.rag_engine.collection.get(
            where={"projeto_id": projeto_id}
        )
        
        dados_exportados = {
            'exportado_por': usuario_exportador['nome'],
            'data_exportacao': datetime.now().isoformat(),
            'desenvolvedor': 'Marcio Góes do Nascimento',
            'projeto': {
                'id': projeto['id'],
                'nome': projeto['nome'],
                'descricao': projeto['descricao'],
                'criado_por': projeto['criado_por'],
                'data_criacao': projeto['data_criacao']
            },
            'total_chunks': len(results['ids']),
            'documentos': []
        }
        
        for i in range(len(results['ids'])):
            dados_exportados['documentos'].append({
                'id': results['ids'][i],
                'conteudo': results['documents'][i],
                'metadata': results['metadatas'][i] if results['metadatas'] else {}
            })
        
        # Salvar arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_projeto_safe = projeto['nome'].replace(' ', '_').replace('/', '_')
        export_path = self.export_dir / f"projeto_{nome_projeto_safe}_{timestamp}.json"
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(dados_exportados, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Projeto '{projeto['nome']}' exportado: {export_path}")
        return str(export_path)
    
    def exportar_projeto_especifico_csv(
        self, 
        projeto_id: int, 
        usuario_exportador: dict
    ) -> str:
        """
        Exporta apenas documentos de um projeto específico para CSV
        
        Args:
            projeto_id: ID do projeto a ser exportado
            usuario_exportador: Dict com dados do usuário que está exportando
            
        Returns:
            Caminho do arquivo CSV exportado
        """
        # Buscar informações do projeto
        projeto = gerenciador_projetos.buscar_projeto(projeto_id)
        if not projeto:
            raise ValueError(f"Projeto ID {projeto_id} não encontrado")
        
        # Buscar documentos do projeto
        results = self.rag_engine.collection.get(
            where={"projeto_id": projeto_id}
        )
        
        # Salvar arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_projeto_safe = projeto['nome'].replace(' ', '_').replace('/', '_')
        export_path = self.export_dir / f"projeto_{nome_projeto_safe}_{timestamp}.csv"
        
        with open(export_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'ID',
                'Conteudo',
                'Arquivo',
                'Formato',
                'Chunk',
                'Exportado_Por'
            ])
            
            for i in range(len(results['ids'])):
                metadata = results['metadatas'][i] if results['metadatas'] else {}
                
                writer.writerow([
                    results['ids'][i],
                    results['documents'][i],
                    metadata.get('filename', ''),
                    metadata.get('format', ''),
                    metadata.get('chunk_index', ''),
                    usuario_exportador['nome']
                ])
        
        print(f"✅ Projeto '{projeto['nome']}' exportado: {export_path}")
        return str(export_path)


if __name__ == "__main__":
    print("=" * 60)
    print("📦 TESTE DO EXPORTADOR DE PROJETOS")
    print("   Desenvolvido por: Marcio Góes do Nascimento")
    print("=" * 60)
    print("\n✅ Exportador pronto para uso!")
