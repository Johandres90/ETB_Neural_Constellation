"""
Main FastAPI Server - ETB Neural Constellation
Endpoints para chat interactivo, entrenamiento en caliente y despacho de la jerarquía 3D.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from core_engine.agent_manager import AgentManager

# Inicialización de la aplicación FastAPI
app = FastAPI(
    title="ETB Neural Constellation Backend",
    description="Motor de agentes corporativos jerárquicos y entrenamiento modular para ETB",
    version="2.6.0"
)

# Habilitar CORS para permitir consumo desde Three.js en cualquier puerto local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instancia central del Gestor de Agentes
kb_path = Path(__file__).resolve().parent.parent / "knowledge_base"
agent_manager = AgentManager(kb_root_path=str(kb_path))

# Modelos Pydantic para validación de datos
class ChatRequest(BaseModel):
    sender: str = Field(default="user", description="Identificador del emisor")
    target_agent: str = Field(default="master", description="ID del agente destino o departamento")
    message: str = Field(..., min_length=1, description="Contenido de la consulta o instrucción")
    history: Optional[List[Dict[str, Any]]] = Field(default=None, description="Historial previo de la conversación para continuidad contextual")

class TrainRequest(BaseModel):
    department: str = Field(..., description="ID del departamento a entrenar")
    content: str = Field(..., min_length=5, description="Texto o documento de conocimiento a integrar")
    topic: Optional[str] = Field(default=None, description="Título o tema del entrenamiento")


@app.get("/api/health")
def health_check():
    """Estado de salud del backend y telemetría de agentes."""
    return {
        "status": "healthy",
        "system": "ETB Neural Constellation Core Engine",
        "version": "2.6.0",
        "total_agents": len(agent_manager.agents),
        "knowledge_base_path": str(agent_manager.kb_root)
    }


@app.get("/api/agents")
def get_agents():
    """Retorna la lista de todos los agentes y el estado de sus bases de conocimiento."""
    return {
        "status": "success",
        "agents": agent_manager.get_all_agents()
    }


@app.get("/api/hierarchy")
def get_hierarchy():
    """Retorna el grafo jerárquico tridimensional de nodos y sinapsis de ETB para Three.js."""
    return agent_manager.get_hierarchy()


@app.post("/api/chat")
def chat_endpoint(payload: ChatRequest):
    """
    Recibe una consulta de chat dirigida a un agente específico o al Agente Máster con historial contextual.
    """
    try:
        response_data = agent_manager.generate_response(
            target_agent=payload.target_agent,
            message=payload.message,
            sender=payload.sender,
            history=payload.history
        )
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando chat: {str(e)}")


@app.post("/api/train")
def train_endpoint(payload: TrainRequest):
    """
    Guarda nuevo conocimiento modular en caliente en el departamento correspondiente y recarga la memoria.
    """
    try:
        train_result = agent_manager.train_agent(
            agent_id=payload.department,
            content=payload.content,
            topic=payload.topic
        )
        return train_result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante el entrenamiento: {str(e)}")


# Servir interfaz web desde el directorio frontend
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/")
    async def serve_index():
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Frontend index.html no encontrado en frontend/."}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run("core_engine.main:app", host=host, port=port, reload=False)
