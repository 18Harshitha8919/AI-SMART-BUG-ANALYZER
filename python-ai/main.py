import os
import io
import pandas as pd
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from faiss_store import faiss_store, KNOWLEDGEBASE_DIR, get_transformer_model
# SentenceTransformer initialization
app = FastAPI(title="AI Smart Bug Analyzer & Fix Advisor Service", description="Embedding and FAISS Vector Database microservice")

# Pydantic schemas
class EmbedRequest(BaseModel):
    texts: List[str]

class IndexItem(BaseModel):
    document: str
    metadata: Dict[str, Any]

class IndexRequest(BaseModel):
    items: List[IndexItem]

class SearchRequest(BaseModel):
    query: str
    k: int = 5

@app.get("/")
def health_check():
    return {
        "status": "online",
        "model": "all-MiniLM-L6-v2",
        "faiss_records": len(faiss_store.metadata),
        "using_faiss": faiss_store.index is not None
    }

@app.post("/embed")
def get_embeddings(request: EmbedRequest):
    try:
        model = get_transformer_model()
        embeddings = model.encode(request.texts)
        if hasattr(embeddings, "tolist"):
            embeddings = embeddings.tolist()
        return {"embeddings": embeddings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate embeddings: {e}")

@app.post("/index")
def add_to_index(request: IndexRequest):
    if not request.items:
        return {"message": "No documents provided"}
        
    try:
        documents = [item.document for item in request.items]
        metadatas = [item.metadata for item in request.items]
        
        # Generate embeddings
        model = get_transformer_model()
        embeddings = model.encode(documents)
        if hasattr(embeddings, "tolist"):
            embeddings = embeddings.tolist()
            
        faiss_store.add_documents(documents, metadatas, embeddings)
        return {"message": f"Successfully indexed {len(documents)} document chunks"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write index: {e}")

@app.post("/search")
def search_index(request: SearchRequest):
    try:
        # Embed query text
        model = get_transformer_model()
        query_embed = model.encode(request.query)
        if hasattr(query_embed, "tolist"):
            query_embed = query_embed.tolist()
            
        results = faiss_store.search(query_embed, k=request.k)
        
        # Clean results for response
        formatted_results = []
        for item in results:
            formatted_results.append({
                "score": item["score"],
                "bug_id": item["metadata"].get("bug_id"),
                "project": item["metadata"].get("project"),
                "component": item["metadata"].get("component"),
                "severity": item["metadata"].get("severity"),
                "description": item["metadata"].get("description"),
                "resolution": item["metadata"].get("resolution"),
                "root_cause": item["metadata"].get("root_cause"),
                "status": item["metadata"].get("status"),
                "source": item["metadata"].get("source"),
                "chunk_content": item["metadata"].get("chunk_content")
            })
            
        return {"results": formatted_results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")

class UpdateMetadataRequest(BaseModel):
    bug_id: str
    updates: Dict[str, Any]

@app.post("/knowledge/update")
def update_knowledge_metadata(request: UpdateMetadataRequest):
    try:
        updated_count = 0
        for item in faiss_store.metadata:
            if item.get("bug_id") == request.bug_id:
                for k, v in request.updates.items():
                    item[k] = v
                updated_count += 1
        if updated_count > 0:
            faiss_store.save()
        return {"message": "Success", "updated_count": updated_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update metadata: {e}")

@app.post("/clear")
def clear_index():
    try:
        faiss_store.clear()
        return {"message": "FAISS vector database cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear index: {e}")

@app.post("/process-file")
async def process_file(file: UploadFile = File(...)):
    filename = file.filename or "unknown.txt"
    ext = os.path.splitext(filename.lower())[1]
    
    contents = await file.read()
    text = ""
    
    try:
        if ext in ['.txt', '.log']:
            text = contents.decode('utf-8', errors='ignore')
            
        elif ext == '.pdf':
            try:
                import PyPDF2
                pdf_file = io.BytesIO(contents)
                reader = PyPDF2.PdfReader(pdf_file)
                pages_text = []
                for idx in range(len(reader.pages)):
                    pages_text.append(reader.pages[idx].extract_text() or "")
                text = "\n".join(pages_text)
            except Exception as e:
                text = f"[PDF Parse Error: {e}]"
                
        elif ext in ['.docx']:
            try:
                import docx
                doc_file = io.BytesIO(contents)
                doc = docx.Document(doc_file)
                text = "\n".join([p.text for p in doc.paragraphs])
            except Exception as e:
                text = f"[DOCX Parse Error: {e}]"
                
        elif ext == '.csv':
            try:
                # Use pandas to load csv and print markdown table format
                df = pd.read_csv(io.BytesIO(contents))
                text = df.to_markdown(index=False)
            except Exception as e:
                # Fallback to standard decode
                text = contents.decode('utf-8', errors='ignore')
                
        else:
            # Fallback - attempt text decode
            text = contents.decode('utf-8', errors='ignore')
            
        return {"filename": filename, "extracted_text": text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting document text: {e}")

# Register clean architecture agent endpoints
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from routes.agent_routes import router as agent_router
app.include_router(agent_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
