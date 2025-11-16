import os
from typing import List, Dict, Any
from pathlib import Path

try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False
    print("⚠️ PyPDF2 não instalado. Execute: pip install PyPDF2")


class DocumentProcessor:
    """Classe para processar documentos PDF e TXT"""
    
    SUPPORTED_FORMATS = {
        '.txt': 'process_txt',
        '.md': 'process_txt',
    }
    
    def __init__(self):
        if HAS_PDF:
            self.SUPPORTED_FORMATS['.pdf'] = 'process_pdf'
        
        print(f"✅ Formatos suportados: {', '.join(self.SUPPORTED_FORMATS.keys())}")
    
    def process_file(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Processa um arquivo e extrai seu conteúdo textual
        
        Args:
            file_path: Caminho do arquivo
            filename: Nome original do arquivo
            
        Returns:
            Dicionário com conteúdo e metadados
        """
        ext = Path(filename).suffix.lower()
        
        if ext not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Formato não suportado: {ext}. "
                f"Formatos aceitos: {', '.join(self.SUPPORTED_FORMATS.keys())}"
            )
        
        processor_method = getattr(self, self.SUPPORTED_FORMATS[ext])
        content = processor_method(file_path)
        
        return {
            'content': content,
            'filename': filename,
            'format': ext,
            'size': os.path.getsize(file_path)
        }
    
    def process_pdf(self, file_path: str) -> str:
        """Extrai texto de arquivos PDF"""
        if not HAS_PDF:
            raise ImportError("PyPDF2 não instalado. Execute: pip install PyPDF2")
        
        text = []
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
            
            if not text:
                return "Erro: Não foi possível extrair texto do PDF. O arquivo pode estar protegido ou ser apenas imagens."
            
            return '\n\n'.join(text)
        
        except Exception as e:
            return f"Erro ao processar PDF: {str(e)}"
    
    def process_txt(self, file_path: str) -> str:
        """Lê arquivos de texto simples"""
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return file.read()
            except UnicodeDecodeError:
                continue
        
        raise ValueError("Não foi possível decodificar o arquivo de texto")
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Divide o texto em chunks com overlap para melhor contexto
        
        Args:
            text: Texto a ser dividido
            chunk_size: Tamanho de cada chunk
            overlap: Sobreposição entre chunks
            
        Returns:
            Lista de chunks de texto
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            
            # Tenta quebrar no final de uma frase
            if end < text_length:
                for separator in ['. ', '\n', ' ']:
                    last_sep = text[start:end].rfind(separator)
                    if last_sep != -1:
                        end = start + last_sep + len(separator)
                        break
            
            chunks.append(text[start:end].strip())
            start = end - overlap if end < text_length else end
        
        return chunks
