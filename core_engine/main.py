"""
Main FastAPI Server - AHOM FIBER IA CORP Neural Constellation
Endpoints para chat interactivo, entrenamiento en caliente, síntesis de voz ElevenLabs y despacho de la jerarquía 3D.
"""

import os
import re
import socket
from pathlib import Path
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from core_engine.kmz_parser import parse_kmz_or_kml_bytes, generate_kmz_knowledge_markdown
from core_engine.elevenlabs_service import elevenlabs_service
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel, Field

from core_engine.agent_manager import AgentManager

# Inicialización de la aplicación FastAPI
app = FastAPI(
    title="AHOM FIBER IA CORP Neural Constellation Backend",
    description="Motor de agentes corporativos jerárquicos y entrenamiento modular para AHOM FIBER IA CORP",
    version="3.2.0"
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

class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Texto a sintetizar con ElevenLabs")
    voice_id: Optional[str] = Field(default=None, description="Voice ID opcional (usa ELEVENLABS_VOICE_ID por defecto)")


@app.get("/api/health")
def health_check():
    """Estado de salud del backend y telemetría de agentes."""
    return {
        "status": "healthy",
        "system": "AHOM FIBER IA CORP Neural Constellation Core Engine",
        "version": "3.2.0",
        "total_agents": len(agent_manager.agents),
        "knowledge_base_path": str(agent_manager.kb_root),
        "elevenlabs": elevenlabs_service.get_status()
    }


@app.get("/api/tts/status")
def tts_status_endpoint():
    """Retorna el estado de configuración del servicio ElevenLabs sin exponer credenciales."""
    return elevenlabs_service.get_status()


@app.post("/api/tts")
def tts_post_endpoint(payload: TTSRequest):
    """Sintetiza voz neuronal utilizando ElevenLabs leyendo API Key y Voice ID desde variables de entorno."""
    try:
        audio_bytes = elevenlabs_service.synthesize_speech(
            text=payload.text,
            voice_id=payload.voice_id
        )
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={"Cache-Control": "no-store"}
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re_err:
        raise HTTPException(status_code=502, detail=str(re_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en síntesis ElevenLabs: {str(e)}")


@app.get("/api/tts")
def tts_get_endpoint(text: str, voice_id: Optional[str] = None):
    """Endpoint GET para streaming directo de audio ElevenLabs desde reproductores HTML5 Audio."""
    try:
        audio_bytes = elevenlabs_service.synthesize_speech(
            text=text,
            voice_id=voice_id
        )
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={"Cache-Control": "no-store"}
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re_err:
        raise HTTPException(status_code=502, detail=str(re_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en síntesis ElevenLabs: {str(e)}")


@app.get("/api/agents")
def get_agents():
    """Retorna la lista de todos los agentes y el estado de sus bases de conocimiento."""
    return {
        "status": "success",
        "agents": agent_manager.get_all_agents()
    }


@app.get("/api/hierarchy")
def get_hierarchy():
    """Retorna el grafo jerárquico tridimensional de nodos y sinapsis de AHOM FIBER IA CORP para Three.js."""
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


@app.post("/api/upload-kmz")
async def upload_kmz_endpoint(file: UploadFile = File(...)):
    """
    Recibe un archivo .kmz o .kml subido por el usuario,
    lo parsea extrayendo rutas de fibra, NAPs, mufas y coordenadas,
    y entrena en caliente al Agente de Ingeniería GIS.
    """
    try:
        content_bytes = await file.read()
        filename = file.filename or "red_fibra.kmz"
        
        parsed_data = parse_kmz_or_kml_bytes(content_bytes, filename=filename)
        md_report = generate_kmz_knowledge_markdown(parsed_data)
        
        # Entrenar en caliente al agente de ingenieria_gis
        train_result = agent_manager.train_agent(
            agent_id="ingenieria_gis",
            content=md_report,
            topic=f"Mapa GIS: {parsed_data.get('document_name', filename)}"
        )
        
        return {
            "status": "success",
            "message": f"Archivo '{filename}' procesado e integrado exitosamente en el Agente de Ingeniería GIS.",
            "metrics": parsed_data.get("metrics"),
            "bounding_box": parsed_data.get("bounding_box"),
            "document_name": parsed_data.get("document_name"),
            "file_type": parsed_data.get("file_type"),
            "elements_sample": parsed_data.get("elements"),
            "training": train_result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error procesando archivo KMZ/KML: {str(e)}")


@app.get("/api/generate-kmz")
async def generate_kmz_endpoint(
    location: str = "Ricaurte Cundinamarca",
    lat: float = 4.2777,
    lon: float = -74.7718,
    total_km: float = 1.47
):
    """
    Genera y descarga un archivo .KMZ profesional compatible con Google Earth,
    conteniendo doc.kml y la subcarpeta files/ con los íconos Poste.png y Camara doble.png.
    """
    from core_engine.kmz_parser import build_kmz_bytes

    kmz_bytes = build_kmz_bytes(
        location_name=location,
        center_lat=lat,
        center_lon=lon,
        total_km=total_km
    )
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', location)
    filename = f"{safe_name}_Red_Fibra_AHOM.kmz"

    return Response(
        content=kmz_bytes,
        media_type="application/vnd.google-earth.kmz",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


# Servir recursos estáticos y frontend
root_project_dir = Path(__file__).resolve().parent.parent
frontend_dir = root_project_dir / "frontend"
assets_dir = root_project_dir / "assets"

if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/")
    async def serve_index():
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Frontend index.html no encontrado en frontend/."}


def get_free_port(preferred_port: int = 8000) -> int:
    """Verifica si el puerto preferido está libre; si está ocupado busca el siguiente disponible."""
    for p in range(preferred_port, preferred_port + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("0.0.0.0", p))
                return p
            except OSError:
                continue
    return preferred_port


if __name__ == "__main__":
    import uvicorn
    requested_port = int(os.environ.get("PORT", 8000))
    chosen_port = get_free_port(requested_port)
    host = os.environ.get("HOST", "0.0.0.0")

    if chosen_port != requested_port:
        print(f"⚠️ El puerto {requested_port} está en uso por otra aplicación.")
        print(f"🚀 Iniciando servidor automáticamente en: http://localhost:{chosen_port}")
    else:
        print(f"🚀 Iniciando servidor en: http://localhost:{chosen_port}")

    uvicorn.run("core_engine.main:app", host=host, port=chosen_port, reload=False)
