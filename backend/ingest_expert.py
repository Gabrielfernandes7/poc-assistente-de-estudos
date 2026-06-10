import os
import sys
import logging
import ollama
from typing import List, Dict
from app.rag import rag_manager
from app.metadata import metadata_manager

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IngestExpert")

class IngestExpert:
    """
    Script especializado em 'destilar' documentos.
    Transforma texto bruto em resumos estruturados para economizar tokens no RAG.
    """
    
    def __init__(self, model: str = "llama3.2:1b"):
        self.model = model

    def distill_notebook(self, notebook_id: str):
        """Processa todos os arquivos de um notebook para criar resumos destilados."""
        upload_dir = os.path.join("backend", "uploads", notebook_id)
        if not os.path.exists(upload_dir):
            logger.error(f"Diretório do notebook {notebook_id} não encontrado.")
            return

        files = [f for f in os.listdir(upload_dir) if f.endswith(('.pdf', '.md'))]
        
        for filename in files:
            logger.info(f"Iniciando destilação de: {filename}")
            file_path = os.path.join(upload_dir, filename)
            
            # 1. Extração (já com OCR embutido no nosso rag_manager)
            if filename.endswith('.pdf'):
                content = rag_manager.extract_text_from_pdf(file_path)
            else:
                content = rag_manager.extract_text_from_md(file_path)

            if not content:
                continue

            distilled_chunks = []
            
            # 2. Destilação por página/bloco
            for item in content:
                page_num = item["page"]
                text = item["text"]
                
                if len(text) < 200: # Pula blocos irrelevantes
                    continue
                
                logger.info(f"  -> Destilando página {page_num}...")
                
                # Pedimos à IA para extrair a essência (Economia de Tokens)
                prompt = f"""Analise o texto abaixo e extraia apenas os pontos cruciais (fatos, datas, nomes, cláusulas).
Gere um resumo técnico e denso em no máximo 3 parágrafos. 
Mantenha termos jurídicos ou técnicos importantes.

TEXTO:
{text}

RESUMO DESTILADO:"""
                
                try:
                    response = ollama.generate(model=self.model, prompt=prompt)
                    summary = response['response']
                    
                    distilled_chunks.append({
                        "text": f"[RESUMO ESTRUTURADO - PÁG {page_num}]\n{summary}",
                        "page": page_num
                    })
                except Exception as e:
                    logger.error(f"Erro ao destilar página {page_num}: {e}")

            # 3. Armazenar no Banco Vetorial com tag de destilação
            if distilled_chunks:
                # Adicionamos ao banco com um doc_id especial para o RAG priorizar
                rag_manager.add_to_vector_db(
                    notebook_id, 
                    distilled_chunks, 
                    f"DESTILADO_{filename}"
                )
                logger.info(f"Sucesso: {len(distilled_chunks)} blocos destilados salvos para {filename}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 ingest_expert.py <notebook_id> [model_name]")
        sys.exit(1)
    
    nb_id = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else "llama3.2:1b"
    
    expert = IngestExpert(model=model_name)
    expert.distill_notebook(nb_id)
