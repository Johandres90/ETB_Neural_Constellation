"""
Módulo de conexión y servicio para ElevenLabs Text-to-Speech (TTS)
AHOM FIBER IA CORP — Neural Constellation
Lee estrictamente las credenciales desde variables de entorno (os.getenv).
"""

import os
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Dict, Any


def _load_dotenv_files() -> None:
    """
    Carga variables desde .env y .env.local en la raíz del proyecto si existen,
    sin sobrescribir variables de entorno ya definidas en el sistema.
    """
    try:
        from dotenv import load_dotenv  # type: ignore
        root_dir = Path(__file__).resolve().parent.parent
        load_dotenv(dotenv_path=root_dir / ".env.local", override=False)
        load_dotenv(dotenv_path=root_dir / ".env", override=False)
        return
    except ImportError:
        pass

    root_dir = Path(__file__).resolve().parent.parent
    for env_filename in (".env.local", ".env"):
        env_path = root_dir / env_filename
        if env_path.exists() and env_path.is_file():
            try:
                for raw_line in env_path.read_text(encoding="utf-8").splitlines():
                    line = raw_line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = val
            except Exception:
                pass


# Cargar archivos .env locales al inicializar el módulo
_load_dotenv_files()


class ElevenLabsService:
    """
    Servicio oficial de integración con la API de ElevenLabs para síntesis de voz neuronal.
    Utiliza exclusivamente os.getenv('ELEVENLABS_API_KEY') y os.getenv('ELEVENLABS_VOICE_ID').
    """

    BASE_URL = "https://api.elevenlabs.io/v1"
    DEFAULT_MODEL = "eleven_multilingual_v2"
    # Voz predeterminada incluida en todas las cuentas (incluyendo Free Tier)
    FALLBACK_PREMADE_VOICE = "EXAVITQu4vr4xnSDxMaL"  # Sarah - Natural, Reassuring

    def __init__(self) -> None:
        _load_dotenv_files()
        self.api_key: Optional[str] = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id: Optional[str] = os.getenv("ELEVENLABS_VOICE_ID")

    def refresh_credentials(self) -> None:
        """Recarga las credenciales desde las variables de entorno."""
        _load_dotenv_files()
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID")

    def is_configured(self) -> bool:
        """Verifica si la API Key y el Voice ID están configurados válidamente."""
        self.refresh_credentials()
        if not self.api_key or not self.voice_id:
            return False
        placeholder_tokens = ("tu_api_key", "your_api_key", "your_elevenlabs", "placeholder")
        if any(tok in self.api_key.lower() for tok in placeholder_tokens):
            return False
        return True

    def get_status(self) -> Dict[str, Any]:
        """Retorna el estado del servicio sin exponer jamás la API Key."""
        configured = self.is_configured()
        return {
            "provider": "ElevenLabs",
            "configured": configured,
            "voice_id_configured": bool(self.voice_id),
            "model_id": self.DEFAULT_MODEL,
        }

    def _call_tts_api(self, text: str, voice_id: str, model_id: str, stability: float, similarity_boost: float, style: float, use_speaker_boost: bool) -> bytes:
        url = f"{self.BASE_URL}/text-to-speech/{voice_id}?output_format=mp3_44100_128"
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": use_speaker_boost,
            },
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            method="POST",
            headers={
                "xi-api-key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
                "User-Agent": "AHOM-FIBER-IA-CORP/3.2",
            },
        )

        with urllib.request.urlopen(req, timeout=20) as response:
            return response.read()

    def synthesize_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        model_id: str = DEFAULT_MODEL,
        stability: float = 0.55,
        similarity_boost: float = 0.80,
        style: float = 0.15,
        use_speaker_boost: bool = True,
    ) -> bytes:
        """
        Convierte texto en audio MP3 utilizando la API REST v1 de ElevenLabs.
        Si la voz configurada es de tipo 'library' y la cuenta es gratuita,
        aplica un fallback transparente a una voz premade autorizada.
        """
        self.refresh_credentials()
        if not self.api_key or not (voice_id or self.voice_id):
            raise ValueError(
                "Credenciales de ElevenLabs no configuradas. Defina ELEVENLABS_API_KEY y ELEVENLABS_VOICE_ID en su archivo .env."
            )

        clean_text = (text or "").strip()
        if not clean_text:
            raise ValueError("El texto para sintetizar no puede estar vacío.")

        primary_voice = voice_id or self.voice_id

        try:
            return self._call_tts_api(
                text=clean_text,
                voice_id=primary_voice,
                model_id=model_id,
                stability=stability,
                similarity_boost=similarity_boost,
                style=style,
                use_speaker_boost=use_speaker_boost,
            )
        except urllib.error.HTTPError as http_err:
            err_body = ""
            try:
                err_body = http_err.read().decode("utf-8", errors="ignore")
            except Exception:
                pass

            # Si la cuenta no tiene permiso para voces de librería de la comunidad (HTTP 402), usar voz premade autorizada
            if http_err.code == 402 and "library_voice" in err_body and primary_voice != self.FALLBACK_PREMADE_VOICE:
                try:
                    return self._call_tts_api(
                        text=clean_text,
                        voice_id=self.FALLBACK_PREMADE_VOICE,
                        model_id=model_id,
                        stability=stability,
                        similarity_boost=similarity_boost,
                        style=style,
                        use_speaker_boost=use_speaker_boost,
                    )
                except Exception as fb_err:
                    raise RuntimeError(f"Error en ElevenLabs: {str(fb_err)}") from fb_err

            raise RuntimeError(
                f"Error HTTP {http_err.code} desde ElevenLabs API: {err_body or http_err.reason}"
            ) from http_err
        except urllib.error.URLError as url_err:
            raise RuntimeError(
                f"Error de conexión con ElevenLabs API: {url_err.reason}"
            ) from url_err


# Instancia singleton para uso en el servidor FastAPI
elevenlabs_service = ElevenLabsService()
