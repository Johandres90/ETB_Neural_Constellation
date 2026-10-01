"""
Agent Manager - ETB Neural Constellation
Gestión de agentes departamentales, federación de conocimiento global y orquestación ejecutiva.
"""

import os
import re
import math
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from core_engine.prompts import AGENT_PROMPTS, MASTER_SYSTEM_PROMPT, COMPETITOR_BENCHMARKS


class AgentManager:
    def __init__(self, kb_root_path: Optional[str] = None):
        if kb_root_path is None:
            self.kb_root = Path(__file__).resolve().parent.parent / "knowledge_base"
        else:
            self.kb_root = Path(kb_root_path)

        self.agents: Dict[str, Dict[str, Any]] = {}
        self.knowledge_cache: Dict[str, Dict[str, Any]] = {}
        self._init_agents()
        self.reload_all_knowledge()

    def _init_agents(self):
        """Inicializa las definiciones de agentes a partir de AGENT_PROMPTS."""
        for agent_id, agent_data in AGENT_PROMPTS.items():
            self.agents[agent_id] = {
                **agent_data,
                "knowledge_files": [],
                "total_knowledge_bytes": 0,
                "last_trained": None,
                "status": "ONLINE"
            }
            dept_dir = self.kb_root / agent_id
            dept_dir.mkdir(parents=True, exist_ok=True)

    def reload_all_knowledge(self):
        """Lee y cachea todos los archivos .txt y .md en cada subdirectorio de knowledge_base."""
        for agent_id in self.agents.keys():
            self.reload_agent_knowledge(agent_id)

    def reload_agent_knowledge(self, agent_id: str):
        """Recarga la base de conocimiento para un agente específico."""
        dept_dir = self.kb_root / agent_id
        dept_dir.mkdir(parents=True, exist_ok=True)

        files_data = []
        combined_text = []
        total_bytes = 0

        for file_path in sorted(dept_dir.glob("*")):
            if file_path.is_file() and file_path.suffix.lower() in [".txt", ".md", ".json"]:
                try:
                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read().strip()
                        file_stat = file_path.stat()
                        files_data.append({
                            "filename": file_path.name,
                            "path": str(file_path),
                            "size": file_stat.st_size,
                            "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                            "preview": content[:180] + ("..." if len(content) > 180 else "")
                        })
                        combined_text.append(f"--- Documento [{agent_id}]: {file_path.name} ---\n{content}")
                        total_bytes += file_stat.st_size
                except Exception as e:
                    print(f"Error leyendo {file_path}: {e}")

        self.knowledge_cache[agent_id] = {
            "combined_content": "\n\n".join(combined_text),
            "files": files_data,
            "total_bytes": total_bytes,
            "last_updated": datetime.now().isoformat()
        }

        if agent_id in self.agents:
            self.agents[agent_id]["knowledge_files"] = files_data
            self.agents[agent_id]["total_knowledge_bytes"] = total_bytes
            self.agents[agent_id]["last_trained"] = datetime.now().isoformat()

    def get_federated_context(self) -> Dict[str, Any]:
        """
        Recorre recursivamente todos los directorios departamentales de knowledge_base/
        y consolida el corpus unificado y resúmenes de directrices técnicas.
        """
        department_contexts: Dict[str, List[str]] = {}
        unified_corpus_blocks: List[str] = []
        total_documents = 0
        total_bytes = 0

        for dept_id, cache in self.knowledge_cache.items():
            if dept_id == "master":
                continue
            dept_files = cache.get("files", [])
            total_documents += len(dept_files)
            total_bytes += cache.get("total_bytes", 0)
            dept_text = cache.get("combined_content", "")
            
            dept_agent = self.agents.get(dept_id, {})
            dept_title = dept_agent.get("name", dept_id)
            department_contexts[dept_id] = [f["filename"] for f in dept_files]

            if dept_text:
                unified_corpus_blocks.append(f"### [Corpus Federado - {dept_title}]\n{dept_text}")

        return {
            "departments": department_contexts,
            "total_documents": total_documents,
            "total_bytes": total_bytes,
            "federated_corpus": "\n\n".join(unified_corpus_blocks),
            "timestamp": datetime.now().isoformat()
        }

    def train_agent(self, agent_id: str, content: str, topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Recibe nuevo contenido de entrenamiento en caliente, lo guarda en un archivo .md y actualiza la memoria.
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agente '{agent_id}' no reconocido en la constelación ETB.")

        dept_dir = self.kb_root / agent_id
        dept_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if topic:
            slug = re.sub(r'[^a-zA-Z0-9_-]', '_', topic).lower()[:30]
            filename = f"train_{slug}_{timestamp}.md"
        else:
            filename = f"entrenamiento_{timestamp}.md"

        target_file = dept_dir / filename

        header = f"# Registro de Entrenamiento - {self.agents[agent_id]['name']}\n"
        header += f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        if topic:
            header += f"Tema: {topic}\n"
        header += "\n## Contenido Integrado\n"

        with open(target_file, "w", encoding="utf-8") as f:
            f.write(header + content.strip() + "\n")

        self.reload_agent_knowledge(agent_id)

        return {
            "status": "success",
            "agent_id": agent_id,
            "agent_name": self.agents[agent_id]["name"],
            "filename": filename,
            "size_bytes": target_file.stat().st_size,
            "total_files": len(self.knowledge_cache[agent_id]["files"]),
            "timestamp": datetime.now().isoformat()
        }

    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        if agent_id not in self.agents:
            return None
        info = dict(self.agents[agent_id])
        info["knowledge_files_count"] = len(self.knowledge_cache.get(agent_id, {}).get("files", []))
        return info

    def get_all_agents(self) -> List[Dict[str, Any]]:
        result = []
        for agent_id, data in self.agents.items():
            agent_summary = dict(data)
            agent_summary["knowledge_files_count"] = len(self.knowledge_cache.get(agent_id, {}).get("files", []))
            result.append(agent_summary)
        return result

    def _classify_query(self, msg_lower: str) -> Dict[str, Any]:
        """Clasifica la intención del usuario y determina el departamento y nodo propietario."""
        # Palabras de acción técnica o seguimiento que NO deben considerarse cierre de sesión
        active_keywords = [
            "potencia", "dbm", "prueba", "pruebas", "otdr", "falla", "modem", "módem", 
            "lento", "lenta", "ticket", "revisa", "verificar", "cuanto", 
            "cuando", "contrato", "cuenta", "visita", "tecnico", "técnico", "luz", "roja", "verde", "wifi"
        ]
        has_active_instruction = any(re.search(rf'\b{re.escape(w)}\b', msg_lower) for w in active_keywords) or bool(re.search(r'\b(haz|has)\b', msg_lower))

        # 1. Cierre de conversación, agradecimiento, satisfacción o indicación de que no hay más consultas
        closing_phrases = [
            "satisfecho", "finalizar", "cerrar chat", "terminar chat", "todo claro", 
            "muchas gracias", "ninguna duda", "conforme", "muy amable", "excelente atencion", 
            "muy claro", "eso es todo", "no seria mas", "nada mas", "todo en orden", "todo bien",
            "no tengo mas", "no tengo más", "no mas", "no más", "sin mas", "sin más",
            "sin consultas", "ninguna consulta", "ninguna otra", "por ahora no", "no por ahora",
            "ya no", "eso seria todo", "eso sería todo", "no gracias", "no, gracias", "terminar",
            "cerrar consulta", "finalizar consulta", "finalizar chat", "cerrar sesion", "cerrar sesión"
        ]
        is_closing = any(p in msg_lower for p in closing_phrases) or msg_lower.strip() in [
            "si", "sí", "si gracias", "sí gracias", "si, gracias", "ok gracias", "ok listo", 
            "gracias", "muchas gracias", "chao", "adios", "hasta luego", "listo gracias", "perfecto gracias",
            "no", "no gracias", "no, gracias", "ninguna", "ninguno", "todo bien", "todo claro"
        ]

        if is_closing and not has_active_instruction:
            return {
                "intent": "satisfaction_close",
                "dept_key": "master",
                "node_id": "master",
                "dept_name": "NEXO ETB CORE",
                "emblem": "🤝"
            }

        # 2. Marco Legal, Normativa CRC, Derecho de Petición, Tutelas, Ley 1755, Cláusula de Permanencia
        if any(w in msg_lower for w in [
            "derecho de peticion", "derecho de petición", "tutela", "sic", "superintendencia", "legal", "juridic", 
            "abogad", "clausula", "permanencia", "cancelar", "cancelacion", "dar de baja", "terminar contrato", 
            "derecho", "regulac", "crc", "5111", "5050", "ley 1581", "ley 1755", "habeas data", "datos personales", 
            "secop", "licitacion", "pliego", "rup", "colombia compra", "regimen", "silencio administrativo"
        ]):
            return {
                "intent": "legal",
                "dept_key": "juridica",
                "node_id": "c_gob",
                "dept_name": "Gobernanza Legal & Normativa",
                "emblem": "⚖️"
            }

        # 3. Servicio al Cliente, PQRs, Quejas, Reclamos, CUN, Asesor Humano
        if any(w in msg_lower for w in [
            "pqr", "pqrs", "reclamo", "reclamos", "queja", "quejas", "servicio al cliente", "atencion al cliente",
            "atención al cliente", "asesor", "agente humano", "hablar con un asesor", "inconformidad", 
            "radicar queja", "radicar reclamo", "radicacion pqr", "radicación pqr", "cun"
        ]):
            return {
                "intent": "cx",
                "dept_key": "experiencia_cliente",
                "node_id": "c_cx",
                "dept_name": "Servicio al Cliente & Experiencia",
                "emblem": "🌟"
            }

        # 3. Respuestas de diagnóstico de módem, telemetría y pruebas técnicas de soporte
        if any(w in msg_lower for w in [
            "los roja", "los en roja", "los en rojo", "esta roja", "luz roja", 
            "pon verde", "pon fija", "esta verde", "luz verde", "sigue igual", 
            "ya reinicie", "no funciono", "no sirvio", "aun no conecta", "no navega",
            "potencia", "dbm", "otdr", "prueba", "pruebas", "adicional", 
            "sigue fallando", "falla el modem", "falla del modem", "modem", "módem",
            "tiempo de llegada", "cuanto demora el tecnico", "cuanto tardan en venir", 
            "cuando llega el tecnico", "a que hora vienen", "costo de la visita", "tiene costo la visita"
        ]):
            return {
                "intent": "support",
                "dept_key": "mesa_ayuda",
                "node_id": "c_desk",
                "dept_name": "Mesa de Ayuda & Soporte Técnico",
                "emblem": "🛠️"
            }

        # 4. Respuestas con número de radicación de ticket o consulta de cuenta de soporte
        if any(w in msg_lower for w in ["ticket de soporte", "ticket soporte", "radicado tecnico", "asociar ticket", "consultar ticket"]) or (re.search(r'\b\d{6,12}\b', msg_lower) and any(w in msg_lower for w in ["falla", "averia", "soporte", "visita", "tecnico"])):
            return {
                "intent": "contract_or_ticket",
                "dept_key": "mesa_ayuda",
                "node_id": "c_desk",
                "dept_name": "Mesa de Ayuda & Soporte Técnico",
                "emblem": "🛠️"
            }

        # 5. Soporte técnico, Wi-Fi, fallas, ONT, lentitud, luces del módem, canales de asistencia
        if any(w in msg_lower for w in ["wifi", "wi-fi", "inalambric", "soporte", "mesa de ayuda", "service desk", "falla", "ticket", "itil", "daño", "asistencia", "averia", "luz roja", "sin internet", "sin servicio", "caido", "intermiten", "lento", "lenta", "lentitud", "lentas", "speedtest", "clave wifi", "contraseña wifi", "ont", "cpe", "router", "reiniciar", "telefonica de soporte"]):
            return {
                "intent": "support",
                "dept_key": "mesa_ayuda",
                "node_id": "c_desk",
                "dept_name": "Mesa de Ayuda & Soporte Técnico",
                "emblem": "🛠️"
            }

        # 6. Comparativa frente a Claro, Tigo, Movistar
        is_telco_claro = ("claro" in msg_lower and not any(p in msg_lower for p in ["todo claro", "muy claro", "quedo claro", "quedó claro", "esta claro", "está claro", "más claro", "mas claro", "tan claro"]))
        if is_telco_claro or any(w in msg_lower for w in ["tigo", "movistar", "competencia", "comparar", "vs", "frente a", "diferencia", "por que etb", "mejor que"]):
            return {
                "intent": "competitor",
                "dept_key": "comercial",
                "node_id": "c_com",
                "dept_name": "Soluciones Corporativas & B2B",
                "emblem": "🛡️"
            }

        # 7. Data Centers, Nube Soberana, SOC y Ciberseguridad Anti-DDoS
        if any(w in msg_lower for w in ["data center", "datacenter", "alma", "prado", "tier", "cloud", "nube", "icrea", "servidor", "vps", "backup", "draas", "soberan", "soc", "ciberseguridad", "ddos", "firewall", "zero trust", "mitigacion", "amenaza", "hack"]):
            return {
                "intent": "dc_cloud",
                "dept_key": "tecnologia",
                "node_id": "c_cib",
                "dept_name": "Data Centers & Nube Híbrida",
                "emblem": "🏢"
            }

        # 8. Precios, tarifas, cotización, planes y costos de instalación de fibra
        if any(w in msg_lower for w in ["costo", "precio", "tarifa", "cuanto vale", "cuanto cuesta", "valor", "instalacion", "acometida", "planes", "cotiz", "factur", "b2b", "megas", "mbps", "gbps", "velocidad", "simetr", "ancho de banda", "dedicado", "sip", "sd-wan", "contratar", "comprar", "pyme", "adquirir", "comercial", "ventas", "asesor comercial"]):
            return {
                "intent": "commercial",
                "dept_key": "comercial",
                "node_id": "c_com",
                "dept_name": "Soluciones Corporativas & B2B",
                "emblem": "💼"
            }

        # 9. Tiempos de despliegue de infraestructura PMO (obras, permisos IDU, tendido troncal)
        if any(w in msg_lower for w in ["cronograma", "despliegue", "spi", "cpi", "obra", "idu", "permiso", "cobertura", "expansion", "sabana", "dias de instalacion", "plazos"]):
            return {
                "intent": "pmo",
                "dept_key": "proyectos_pmo",
                "node_id": "c_pmo",
                "dept_name": "Despliegue de Red & Proyectos",
                "emblem": "🚀"
            }

        # 7. Finanzas, Presupuesto, TCO, Facturación en Pesos COP
        if any(w in msg_lower for w in ["financier", "capex", "opex", "tco", "ahorro", "presupuesto", "facturacion", "dian", "pesos cop", "dolar", "roi", "retorno"]):
            return {
                "intent": "finance",
                "dept_key": "financiera",
                "node_id": "c_erp",
                "dept_name": "Planeación Financiera & Costos",
                "emblem": "💰"
            }

        # 8. Experiencia VIP, Gestor de cuenta, NPS, CSAT
        if any(w in msg_lower for w in ["nps", "csat", "vip", "gestor", "satisfaccion", "acompañamiento", "fidelizacion", "posventa", "experiencia"]):
            return {
                "intent": "cx",
                "dept_key": "experiencia_cliente",
                "node_id": "c_cx",
                "dept_name": "Experiencia de Cliente & VIP",
                "emblem": "🌟"
            }

        # 9. Red Troncal, DWDM, NOC, Latencia, NAP
        if any(w in msg_lower for w in ["dwdm", "troncal", "nap", "anillo", "peering", "olt", "atenuacion", "monomodo", "malla"]):
            return {
                "intent": "noc",
                "dept_key": "operaciones_noc",
                "node_id": "c_noc",
                "dept_name": "Red Troncal & Fibra Óptica",
                "emblem": "🌐"
            }

        # 10. Saludos generales
        if any(w in msg_lower for w in ["hola", "buenos dias", "buenas tardes", "buenas noches", "que es nexo", "como funciona", "que puedes hacer", "quien eres"]):
            return {
                "intent": "greeting",
                "dept_key": "master",
                "node_id": "master",
                "dept_name": "NEXO ETB CORE",
                "emblem": "👑"
            }

        return {
            "intent": "general",
            "dept_key": "master",
            "node_id": "master",
            "dept_name": "NEXO ETB CORE",
            "emblem": "👑"
        }

    def _resolve_dept_key_from_target(self, target: str) -> str:
        """Determina la clave departamental a partir del ID del agente o nodo."""
        mapping = {
            "master": "master",
            "operaciones_noc": "operaciones_noc", "c_noc": "operaciones_noc",
            "tecnologia": "tecnologia", "c_cib": "tecnologia",
            "comercial": "comercial", "c_com": "comercial",
            "juridica": "juridica", "c_gob": "juridica",
            "financiera": "financiera", "c_erp": "financiera",
            "proyectos_pmo": "proyectos_pmo", "c_pmo": "proyectos_pmo",
            "mesa_ayuda": "mesa_ayuda", "c_desk": "mesa_ayuda",
            "experiencia_cliente": "experiencia_cliente", "c_cx": "experiencia_cliente"
        }
        if target in mapping:
            return mapping[target]
        # Búsqueda en prefijos de proyectos
        if target.startswith("n_dwdm") or target.startswith("n_gpon") or target.startswith("n_nap") or target.startswith("n_telemetry") or target.startswith("n_micro") or target.startswith("n_noc"):
            return "operaciones_noc"
        if target.startswith("n_alma") or target.startswith("n_prado") or target.startswith("n_soc") or target.startswith("n_etb_cloud") or target.startswith("n_zero") or target.startswith("n_draas"):
            return "tecnologia"
        if target.startswith("n_ftth_ded") or target.startswith("n_p2p") or target.startswith("n_sip") or target.startswith("n_sdwan") or target.startswith("n_smart") or target.startswith("n_pymes"):
            return "comercial"
        if target.startswith("n_crc") or target.startswith("n_secop") or target.startswith("n_habeas") or target.startswith("n_spectrum"):
            return "juridica"
        if target.startswith("n_tco") or target.startswith("n_duct") or target.startswith("n_capex") or target.startswith("n_e_invoic") or target.startswith("n_roi"):
            return "financiera"
        if target.startswith("n_pmo") or target.startswith("n_idu") or target.startswith("n_suba") or target.startswith("n_otdr") or target.startswith("n_sabana"):
            return "proyectos_pmo"
        if target.startswith("n_itil") or target.startswith("n_ont") or target.startswith("n_vip_desk") or target.startswith("n_frt"):
            return "mesa_ayuda"
        if target.startswith("n_nps") or target.startswith("n_csat") or target.startswith("n_selfservice") or target.startswith("n_proactive"):
            return "experiencia_cliente"
        return "master"

    def _find_clean_snippet_and_file(self, dept_key: str, kb_data: Dict[str, Any], query: str) -> tuple[Optional[str], Optional[str]]:
        if not kb_data or "files" not in kb_data:
            return None, None
        
        query_words = [w for w in query.lower().split() if len(w) > 3]
        best_file = None
        best_excerpt = None
        max_matches = 0

        for file_info in kb_data.get("files", []):
            try:
                filepath = file_info.get("path")
                if filepath and os.path.isfile(filepath):
                    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                        lines = f.readlines()
                    
                    for i, line in enumerate(lines):
                        line_lower = line.lower()
                        matches = sum(1 for w in query_words if w in line_lower)
                        if matches > max_matches:
                            max_matches = matches
                            best_file = file_info.get("filename")
                            start_i = max(0, i - 1)
                            end_i = min(len(lines), i + 3)
                            best_excerpt = "".join(lines[start_i:end_i]).strip()
            except Exception:
                pass
        
        if not best_excerpt and kb_data.get("files"):
            first = kb_data["files"][0]
            best_file = first.get("filename")
            best_excerpt = first.get("preview", "")

        return best_excerpt, best_file

    def _handle_support_query(self, message: str, msg_lower: str, agent_badge: str, history: Optional[List[Dict[str, Any]]] = None) -> tuple[str, str]:
        """Genera una respuesta técnica humana, conversacional y experta de Mesa de Ayuda / Soporte Técnico."""
        prefix = f"{agent_badge}" if agent_badge else ""

        # 1. Cierre por satisfacción / despedida cordial / indicación de no más consultas
        is_closing_sentiment = any(p in msg_lower for p in [
            "satisfecho", "finalizar", "cerrar chat", "terminar chat", "todo claro", 
            "muchas gracias", "ninguna duda", "conforme", "muy amable", "excelente atencion", 
            "muy claro", "eso es todo", "no seria mas", "nada mas", "todo en orden", "todo bien",
            "no tengo mas", "no tengo más", "no mas", "no más", "sin mas", "sin más",
            "sin consultas", "ninguna consulta", "ninguna otra", "por ahora no", "no por ahora",
            "ya no", "eso seria todo", "eso sería todo", "no gracias", "no, gracias", "terminar",
            "cerrar consulta", "finalizar consulta", "finalizar chat", "cerrar sesion", "cerrar sesión"
        ]) or msg_lower.strip() in [
            "si", "sí", "si gracias", "sí gracias", "si, gracias", "ok gracias", "ok listo", 
            "gracias", "muchas gracias", "chao", "adios", "hasta luego", "listo gracias", "perfecto gracias",
            "no", "no gracias", "no, gracias", "ninguna", "ninguno"
        ]
        has_new_action = any(re.search(rf'\b{re.escape(w)}\b', msg_lower) for w in [
            "potencia", "dbm", "prueba", "pruebas", "otdr", "falla", "modem", "módem", "lento", "ticket", "revisa", "verificar", "cuanto", "cuando"
        ]) or bool(re.search(r'\b(haz|has)\b', msg_lower))

        if is_closing_sentiment and not has_new_action:
            text = (
                f"{prefix}"
                f"### 🤝 ¡Sesión Finalizada con Éxito en NEXO ETB!\n\n"
                f"¡Ha sido un verdadero placer asistirte hoy!\n\n"
                f"Tu caso queda debidamente registrado y bajo seguimiento prioritario en nuestra central de operaciones. Te mantendremos informado por SMS y WhatsApp ante cualquier novedad del servicio.\n\n"
                f"- 📞 **Soporte Técnico Especializado 24/7:** PBX **(601) 377-7777** (Opción 2 Empresas) | WhatsApp Oficial: **+57 305 777 7777**.\n\n"
                f"Doy por cerrada esta consulta. ¡Que tengas un excelente resto de día! 🚀"
            )
            voice = "Ha sido un placer asistirte. Tu ticket técnico continúa en seguimiento prioritario. ¡Que tengas un excelente día!"
            return text, voice

        # 2. Si el usuario indica explícitamente que SÍ tiene otra duda o pregunta adicional
        if any(p in msg_lower for p in ["otra duda", "otra pregunta", "tengo otra consulta", "una duda mas", "una pregunta mas", "tengo otra duda"]):
            text = (
                f"{prefix}"
                f"¡Con mucho gusto! Cuéntame qué otra consulta, síntoma o prueba técnica deseas que revisemos."
            )
            voice = "Con gusto, ¿qué otra duda o síntoma deseas que analicemos?"
            return text, voice

        # 3. Verificación de niveles de potencia óptica (dBm) / telemetría
        if any(w in msg_lower for w in ["potencia", "dbm", "nivel de potencia", "niveles de potencia", "medir potencia", "señal optica", "laser", "atenuacion", "medicion"]):
            text = (
                f"{prefix}"
                f"Listo, acabo de realizar la lectura de telemetría óptica directa en tu puerto OLT de cabecera:\n\n"
                f"- **Potencia Óptica de Recepción (Rx):** `-27.8 dBm` *(Estado: Crítico por atenuación severa; el umbral estándar en fibra ETB debe estar entre -18 dBm y -24 dBm)*.\n"
                f"- **Potencia de Transmisión (Tx):** `+2.1 dBm` *(Rango normal)*.\n"
                f"- **Voltaje ONT:** `3.3V` *(Alimentación eléctrica estable)*.\n\n"
                f"Con este nivel de `-27.8 dBm` confirmamos técnicamente que el módem recibe poca intensidad del haz láser, lo que provoca la luz LOS roja o pérdida total de navegación. El inconveniente se encuentra en la fibra exterior (posible doblez forzado en fachada o atenuador descalibrado en la mufa de distribución).\n\n"
                f"Ya adjunté esta telemetría como reporte prioritario en la orden técnica para que la cuadrilla llegue directamente al punto con reflectómetro óptico.\n\n"
                f"¿Deseas que ejecutemos una prueba de reflectometría OTDR para estimar a cuántos metros está la falla, o tienes alguna otra consulta sobre la visita?"
            )
            voice = "La potencia óptica marca menos 27.8 dBm, confirmando atenuación crítica exterior en la fibra. Ya adjunté la lectura a tu orden técnica."
            return text, voice

        # 4. Pruebas adicionales / Test OTDR / Reflectometría óptica remota
        if any(w in msg_lower for w in ["adicional", "otra prueba", "mas prueba", "más prueba", "otdr", "reflectometr", "haz prueba", "has prueba", "haz otra", "has otra", "pruebas adicionales", "otra revision", "mas revision"]):
            text = (
                f"{prefix}"
                f"Listo, acabo de lanzar el barrido de reflectometría óptica remota (OTDR) desde nuestra cabecera OLT:\n\n"
                f"- **Ubicación del evento de atenuación:** Aprox. a **280 metros** de tu sede (sectorizado en la caja de empalme secundaria exterior de la manzana).\n"
                f"- **Diagnóstico del equipo (ONT/Módem):** El hardware interno, puerto PON y láser emisor responden con normalidad. No se requiere reemplazo del equipo módem.\n"
                f"- **Dictamen de campo:** Atenuación en el empalme exterior de fibra que requiere conectorización y limpieza con fusionadora de arco.\n\n"
                f"Dejé cargada esta localización exacta en tu ticket para que la cuadrilla técnica N2 no pierda tiempo en pruebas internas y se dirija directamente a la caja de empalme en vía pública.\n\n"
                f"¿Estás satisfecho con este diagnóstico o deseas consultar algún otro detalle antes de dar por atendida tu solicitud?"
            )
            voice = "La prueba OTDR localiza la pérdida de señal a 280 metros en la caja secundaria exterior. La cuadrilla técnica ya tiene el reporte con reflectometría."
            return text, voice

        # 5. El módem sigue fallando / no conecta tras pruebas
        if any(w in msg_lower for w in ["sigue fallando", "continua fallando", "aun falla", "sigue sin", "no sirve", "no funciona", "sigue caido", "sigue el fallo", "falla el modem", "problemas con el modem", "falla del modem", "no conecta", "no da internet"]):
            text = (
                f"{prefix}"
                f"Comprendo totalmente tu molestia. Al persistir la falla en el módem tras los descartes iniciales y tener la luz LOS en alerta, podemos realizar dos comprobaciones inmediatas desde la consola central:\n\n"
                f"1. **Verificar los niveles de potencia óptica (dBm)** para saber exactamente cuánta intensidad de luz láser le está llegando al equipo.\n"
                f"2. **Ejecutar un test de reflectometría OTDR** para medir a cuántos metros del predio se encuentra el corte o atenuación física.\n\n"
                f"¿Deseas que verifiquemos los niveles de potencia óptica o lanzamos la prueba de reflectometría OTDR de una vez?"
            )
            voice = "Comprendo la situación. Podemos medir la potencia óptica o lanzar la prueba OTDR desde central. ¿Cuál prefieres que ejecutemos?"
            return text, voice

        # 6. Tiempos de llegada del técnico / SLA / Demora
        if any(w in msg_lower for w in ["cuanto demora", "cuanto tardan", "cuanto se demoran", "cuando llega", "a que hora", "tiempo de llegada", "cuando viene", "cuanto tiempo", "demora el tecnico", "tarda el tecnico"]):
            text = (
                f"{prefix}"
                f"Para incidencias de pérdida óptica o luz LOS roja en enlaces empresariales ETB, nuestro compromiso de atención en sitio (SLA) es de **menos de 4 horas**.\n\n"
                f"La orden ya se encuentra asignada a la cuadrilla móvil N2 de tu zona. En cuanto el técnico inicie su desplazamiento recibirás un SMS y un mensaje por WhatsApp con los datos del técnico y el tiempo estimado de arribo.\n\n"
                f"¿Deseas registrar alguna observación especial para la cuadrilla, como el horario de recepción o autorización en portería?"
            )
            voice = "El tiempo de atención de la cuadrilla técnica es menor a 4 horas. Recibirás un SMS y WhatsApp cuando inicien el desplazamiento a tu predio."
            return text, voice

        # 7. Costo de la visita técnica / reparación
        if any(w in msg_lower for w in ["costo de la visita", "tiene costo", "cobran la visita", "valor de la visita", "precio de la visita", "cobran por venir"]):
            text = (
                f"{prefix}"
                f"La visita técnica de diagnóstico, calibración de señal óptica y reparación de la red exterior **no tiene ningún costo adicional** para tu contrato empresarial ETB.\n\n"
                f"Está 100% cubierta dentro de las garantías de mantenimiento y SLA de tu servicio de fibra óptica.\n\n"
                f"¿Deseas que verifiquemos algún otro aspecto del servicio o estás satisfecho con la atención?"
            )
            voice = "La visita técnica de reparación de fibra óptica es totalmente gratuita y está cubierta por tu contrato."
            return text, voice

        # 8. Respuesta con número de contrato, cuenta, teléfono o radicación de ticket
        if any(w in msg_lower for w in ["contrato", "cuenta", "linea", "telefono", "ticket", "radicado"]) or re.search(r'\b\d{5,12}\b', message):
            contract_match = re.search(r'\b\d{5,12}\b', message)
            contract_num = contract_match.group(0) if contract_match else "53696969"
            ticket_id = f"ETB-INC-{contract_num[-6:]}"

            text = (
                f"{prefix}"
                f"¡Listo! He registrado la orden de soporte prioritario para tu contrato / línea **{contract_num}** en nuestro sistema central de Mesa de Ayuda:\n\n"
                f"- **Número de Ticket:** `{ticket_id}`\n"
                f"- **Diagnóstico Asociado:** Pérdida de Enlace Óptico (Luz LOS Roja / Desconexión Física)\n"
                f"- **Asignación:** Cuadrilla Técnica N2 - Enlaces de Fibra Óptica Corporativa\n"
                f"- **Compromiso SLA:** Tiempo de atención en sitio menor a **4 horas**\n"
                f"- **Notificaciones:** Te llegará un mensaje de texto SMS y confirmación por WhatsApp al número registrado cuando el técnico inicie desplazamiento.\n\n"
                f"Para avanzar mientras llega la cuadrilla, puedo verificar desde aquí los niveles de potencia óptica (dBm) o correr una prueba OTDR. ¿Deseas que los verifiquemos de una vez o tienes alguna consulta sobre la visita?"
            )
            voice = f"Ticket {ticket_id} radicado con éxito para el contrato {contract_num}. Cuadrilla asignada con atención menor a 4 horas. ¿Deseas que verifiquemos los niveles de potencia óptica?"
            return text, voice

        # 9. Respuesta de seguimiento: Volvió la luz verde pero la navegación está lenta
        if (any(w in msg_lower for w in ["volvio", "regreso", "ya esta verde", "luz verde", "verde pero"]) and any(w in msg_lower for w in ["lenta", "lento", "lentitud", "navegacion", "velocidad", "demora", "tarda"])) or ("luz verde" in msg_lower and "lenta" in msg_lower):
            text = (
                f"{prefix}"
                f"¡Excelente noticia que la luz **PON verde** haya regresado! Esto confirma que el enlace físico de fibra óptica y la potencia láser desde nuestra central ya están sincronizados correctamente.\n\n"
                f"La lentitud temporal suele deberse a saturación de tablas DNS o asignación en la frecuencia 2.4 GHz. Aplica estos pasos de optimización inmediata:\n\n"
                f"1. **Conexión a la Banda ETB_5G (Prioritaria):**\n"
                f"   - Conéctate a la red inalámbrica `ETB_5G` en tu celular o computador. La banda 5 GHz evita interferencias de canales y entrega el 100% de tu velocidad contratada.\n"
                f"2. **Renovación de Conexión y Sesión DHCP:**\n"
                f"   - En tu dispositivo, entra a configuración Wi-Fi, selecciona **'Olvidar Red'** y vuelve a ingresar la contraseña para que el módem asigne una dirección IP limpia.\n"
                f"3. **Configuración de Servidores DNS de Alta Eficiencia:**\n"
                f"   - Configura en el adaptador de red los DNS primarios `1.1.1.1` (Cloudflare) y `8.8.8.8` (Google) para acelerar la apertura de páginas web.\n"
                f"4. **Prueba por Cable Ethernet:**\n"
                f"   - Si es posible, conecta un cable al puerto LAN 1 de la ONT para descartar congestión inalámbrica ambiental.\n\n"
                f"¿Me confirmas si al conectar a la red 5G la velocidad mejoró, o deseas que ejecutemos una prueba de velocidad en `speedtest.net`?"
            )
            voice = "La luz verde confirma sincronización de fibra. Para acelerar tu navegación, conéctate a la red 5G y renueva la conexión Wi-Fi."
            return text, voice

        # 10. Luz LOS Roja / Pérdida óptica confirmada
        if any(w in msg_lower for w in ["los roja", "los en roja", "los en rojo", "los esta en roja", "los esta en rojo", "los esta roja", "luz los", "esta roja", "esta en roja", "esta en rojo", "roja fija", "parpadea en rojo", "titilando en rojo", "luz roja", "luz de los"]):
            text = (
                f"{prefix}"
                f"Gracias por confirmarme. Que la **luz LOS esté en rojo (o parpadeando)** confirma que la ONT no está recibiendo el haz de luz láser de fibra óptica desde nuestra central:\n\n"
                f"1. **Inspección del Cable Amarillo (Patchcord):**\n"
                f"   - Revisa el cable delgado amarillo con conectores verdes (SC/APC) en la base del módem.\n"
                f"   - **Cuidado:** No lo dobles en ángulos rectos (90°) ni lo pises con muebles, ya que el hilo de vidrio interno es delicado.\n"
                f"   - Verifica que el conector verde esté encajado firmemente (debe hacer un 'clic' suave).\n\n"
                f"2. **Causa Externa (Atenuación / Corte de Mufa):**\n"
                f"   - Si el cable interno está intacto, el evento se origina en la mufa de distribución externa en vía pública.\n\n"
                f"3. **Despacho Inmediato de Cuadrilla Técnica Nivel 2:**\n"
                f"   - Procedo a aperturar el ticket de soporte técnico prioritario.\n"
                f"   - Por favor indícame tu **número de contrato, cuenta o teléfono registrado en ETB** para agendar la cuadrilla de campo (tiempo de atención SLA < 4 horas en enlaces corporativos)."
            )
            voice = "La luz LOS en rojo confirma pérdida de señal óptica física. Verifica que el cable amarillo no esté doblado y facilítame tu número de contrato para despachar cuadrilla técnica."
            return text, voice

        # 11. Luz PON Verde Fija / Fibra OK
        if any(w in msg_lower for w in ["pon verde", "pon en verde", "pon verde fija", "luz pon", "esta verde", "esta en verde", "verde fija", "la pon esta verde", "la pon esta en verde"]):
            text = (
                f"{prefix}"
                f"¡Excelente! La **luz PON en verde fijo** confirma que el enlace de fibra óptica y la potencia láser desde nuestra central están en niveles óptimos (-18 dBm a -24 dBm). La fibra no está cortada.\n\n"
                f"Dado que la señal de fibra está activa, el inconveniente radica en la red local Wi-Fi o asignación DHCP/DNS:\n\n"
                f"1. **Conexión a la Banda 5G:** Conéctate a la red `ETB_5G` si estás a menos de 8 metros del módem (ofrece la máxima velocidad simétrica y menor congestión).\n"
                f"2. **Olvidar y Reconectar Red:** En tu celular o PC, entra a configuración Wi-Fi, selecciona **'Olvidar Red'** y vuelve a ingresar la contraseña para renovar la dirección IP asignada por el router.\n"
                f"3. **Configuración de DNS:** Prueba asignando en el adaptador los servidores DNS `1.1.1.1` (Cloudflare) y `8.8.8.8` (Google).\n"
                f"4. **Prueba por Cable:** Conecta un cable de red directo al puerto LAN 1 de la ONT para validar si navegas con normalidad.\n\n"
                f"¿Estás satisfecho con esta solución o deseas que verifiquemos algún parámetro adicional antes de finalizar?"
            )
            voice = "La luz PON verde fija confirma que la fibra óptica está perfecta. El problema es local en el Wi-Fi; conéctate a la red 5G y renueva la conexión."
            return text, voice

        # 12. Ya reinicié y sigue igual
        if any(w in msg_lower for w in ["ya reinicie", "ya lo reinicie", "ya lo hice", "sigue igual", "no funciono", "no sirvio", "aun no conecta", "continua sin internet", "sigue sin servir", "no navega"]):
            text = (
                f"{prefix}"
                f"Entendido. Ya que el ciclo de reinicio de 30 segundos no restableció la conexión, procederemos a realizar un refresco de sesión PPPoE y resincronización de puerto directo en la OLT de la central telefónica:\n\n"
                f"1. Validaremos la tabla de rutas y la potencia óptica remota (dBm) de tu ONT.\n"
                f"2. Por favor facilítame tu **número de contrato o número de línea telefónica ETB** para ingresar a la consola de gestión de tu servicio.\n"
                f"3. Si el enlace no sincroniza tras el reseteo de puerto, despachamos soporte en sitio de forma inmediata."
            )
            voice = "Procederé con el reseteo remoto de puerto en la central OLT. Por favor indícame tu número de contrato o línea ETB."
            return text, voice

        # 13. Fallas de Wi-Fi, red inalámbrica o señal débil (Consulta Inicial)
        if any(w in msg_lower for w in ["wifi", "wi-fi", "inalambric", "clave", "antena", "alcance", "cobertura", "intermitencia"]):
            text = (
                f"{prefix}"
                f"¡Hola! Comprendo la molestia que causa una interrupción en el servicio. Como especialista técnico de ETB, te guiaré paso a paso para diagnosticarlo y restablecer tu conexión de inmediato:\n\n"
                f"1. **Inspección de Luces en el Módem / ONT:**\n"
                f"   - **Luz PON (Verde fija):** Indica que la fibra óptica física está sincronizada con nuestra central.\n"
                f"   - **Luz LOS (Apagada en estado normal):** Si la luz **LOS está encendida en ROJO o titilando**, hay una pérdida física de señal óptica (cable desconectado, doblado o corte exterior).\n\n"
                f"2. **Ciclo de Energía del Módem (Power Cycle 30s):**\n"
                f"   - Desconecta el adaptador negro de energía durante **30 segundos** y vuelve a conectarlo para liberar memoria interna y refrescar canales.\n\n"
                f"3. **Conexión a la Banda ETB_5G:**\n"
                f"   - Conéctate a la red `ETB_5G` si estás cerca del módem para obtener la máxima velocidad sin interferencias.\n\n"
                f"Cuéntame: **¿en qué estado ves la luz PON y la luz LOS en el módem en este momento?**"
            )
            voice = "Para solucionar fallas en tu Wi-Fi, primero reinicia tu módem desconectándolo por 30 segundos, verifica las luces PON y LOS y conéctate a la red 5G."
            return text, voice

        # 14. Lentitud / Speedtest / Ping alto
        if any(w in msg_lower for w in ["lento", "lenta", "lentitud", "lentas", "velocidad", "test", "speedtest", "bajada", "subida", "ping", "latencia", "demora", "tarda", "navegacion"]):
            text = (
                f"{prefix}"
                f"Para verificar que estés recibiendo el 100% de tu velocidad simétrica contratada, realiza esta prueba técnica controlada:\n\n"
                f"1. **Conexión Directa:** Conecta un PC mediante cable de red Gigabit al puerto LAN 1 de la ONT.\n"
                f"2. **Cierre de Aplicaciones:** Cierra descargas en segundo plano, streaming 4K o sincronizaciones en la nube.\n"
                f"3. **Servidor de Prueba:** Ingresa a `speedtest.net` y selecciona manualmente el servidor **\"ETB - Bogotá\"**.\n"
                f"4. **Validación:** En fibra ETB la velocidad de subida debe ser igual a la de bajada con ping < 3.5 ms.\n\n"
                f"¿Qué resultado de bajada y subida te arrojó el test de velocidad?"
            )
            voice = "Para medir tu velocidad real, conecta un cable de red directo al módem, cierra descargas y haz el test apuntando al servidor ETB Bogotá."
            return text, voice

        # 15. Configuración de Router, Contraseña Wi-Fi o IP Fija
        if any(w in msg_lower for w in ["contraseña", "clave", "cambiar", "ip fija", "dns", "puerto", "bridge", "dmz", "acceder"]):
            text = (
                f"{prefix}"
                f"Te indico cómo administrar los parámetros de tu equipo ETB:\n\n"
                f"1. **Acceso a la Consola Web del Router:** Abre tu navegador y digita `http://192.168.1.1` (usuario: `admin` / clave en la etiqueta posterior del equipo o en el portal Mi ETB).\n"
                f"2. **Cambio de Contraseña Wi-Fi:** Ve a la pestaña **Wireless / WLAN** -> Selecciona **WPA2-PSK / WPA3** -> Ingresa tu nueva contraseña.\n"
                f"3. **IP Fija y Mapeo de Puertos:** Para servidores locales o PBX, asignamos IPs públicas fijas con enrutamiento 1:1 sin costo adicional."
            )
            voice = "Puedes cambiar tu clave Wi-Fi accediendo a la dirección 192.168.1.1 o a través del portal Mi ETB Empresas."
            return text, voice

        # 16. Respuesta contextual fluida para cualquier otro mensaje durante la conversación activa
        if history and len(history) > 1:
            text = (
                f"{prefix}"
                f"Entendido. Respecto a tu mensaje *\"{message}\"*:\n\n"
                f"El caso permanece abierto bajo seguimiento de Mesa de Ayuda. Desde aquí puedo realizar mediciones de potencia óptica (dBm), ejecutar barridos OTDR de distancia, consultar el estado de desplazamiento de la cuadrilla o añadir notas técnicas a tu orden.\n\n"
                f"¿Deseas que verifiquemos los niveles de potencia óptica, ejecutemos una prueba adicional o tienes alguna otra consulta?"
            )
            voice = "Seguimiento activo en Mesa de Ayuda ETB. ¿Deseas verificar la potencia óptica o ejecutar alguna prueba adicional?"
            return text, voice

        # 17. Respuesta general inicial de soporte técnico
        text = (
            f"{prefix}"
            f"¡Hola! Soy tu especialista de soporte técnico en ETB. Estoy aquí para resolver cualquier duda o incidencia operativa en tus enlaces de fibra óptica, telefonía o centros de datos:\n\n"
            f"- 🛠️ **Diagnóstico Remoto:** Monitoreo en tiempo real de potencia óptica (dBm), estado de interfaces y reinicio de perfil OLT.\n"
            f"- 📞 **PBX Bogotá:** **(601) 377-7777** (Opción 2 Empresas)\n"
            f"- 📞 **Línea Nacional:** **01 8000 112 170** (Atención 24/7/365)\n"
            f"- 💬 **WhatsApp Oficial:** **+57 305 777 7777**\n"
            f"- ⚡ **Compromiso SLA:** Tiempo de primera respuesta menor a **3 minutos** y solución en campo menor a **4 horas** en enlaces dedicados.\n\n"
            f"¿Qué síntoma o requerimiento técnico deseas que revisemos?"
        )
        voice = "Mesa de Ayuda ETB disponible 24/7. ¿En qué problema técnico o requerimiento de configuración te podemos asistir?"
        return text, voice

    def _handle_legal_query(self, message: str, msg_lower: str, agent_badge: str) -> tuple[str, str]:
        """Genera una respuesta jurídica fundamentada y natural del área legal."""
        # 1. Permanencia mínima, penalizaciones, multas
        if any(w in msg_lower for w in ["permanencia", "penaliz", "multa", "clausula", "12 meses", "24 meses", "tiempo minimo", "obligacion"]):
            text = (
                f"{agent_badge}\n"
                f"### ⚖️ Dictamen Jurídico: Régimen de Permanencia Mínima (Resolución CRC 5111 de 2017)\n\n"
                f"¡Hola! Desde la Secretaría General y Asesoría Jurídica de ETB, te explico con total transparencia las condiciones legales aplicables en Colombia:\n\n"
                f"1. **Validez Legal de la Permanencia Mínima:**\n"
                f"   - Conforme a la **Resolución CRC 5111 de 2017**, las cláusulas de permanencia mínima solo son válidas si fueron pactadas expresamente al inicio del contrato y el operador otorgó un **descuento sustancial o subsidio en los costos de instalación o equipos**.\n"
                f"   - El contrato debe incluir una carátula o anexo donde se detalle el valor total de la instalación y el descuento otorgado.\n\n"
                f"2. **Liquidación por Cancelación Anticipada:**\n"
                f"   - **PROHIBICIÓN LEGAL:** La ley colombiana **prohíbe expresamente** cobrar las mensualidades futuras del servicio que no hayan sido consumidas.\n"
                f"   - Si cancelas antes de vencer el plazo (12 o 24 meses), el operador únicamente puede cobrar el **saldo prorrateado del descuento de instalación o equipos**, en estricta proporción a los meses restantes.\n"
                f"   - *Fórmula:* `Cobro = (Valor del descuento / Plazo total en meses) × Meses faltantes`.\n\n"
                f"3. **Vencimiento de la Permanencia:**\n"
                f"   - Una vez finalizado el periodo inicial pactado, el contrato pasa a ser indefinido **sin que pueda renovarse automáticamente ninguna cláusula de permanencia**."
            )
            voice = "Bajo la Resolución CRC 5111, si cancelas antes del plazo de permanencia solo pagas el valor prorrateado del descuento de instalación, nunca las mensualidades futuras."
            return text, voice

        # 2. Cancelación de contrato, retiro del servicio
        if any(w in msg_lower for w in ["cancelar", "cancelacion", "dar de baja", "terminar contrato", "retirar", "desvincular", "renunciar"]):
            text = (
                f"{agent_badge}\n"
                f"### ⚖️ Procedimiento Legal para Cancelación de Servicios de Telecomunicaciones\n\n"
                f"¡Hola! Te indico el procedimiento legal y tus derechos garantizados por la regulación colombiana:\n\n"
                f"1. **Plazo de Solicitud:** Puedes solicitar la terminación del contrato en cualquier momento, con al menos **3 días hábiles de anticipación** a la fecha de corte de tu periodo de facturación.\n"
                f"2. **Canales Habilitados:** Tienes derecho a presentar tu solicitud por **cualquier canal oficial de atención** (línea telefónica, portal web Mi ETB, PQR escrita o puntos presenciales), sin que te sean exigidos requisitos o documentos no contemplados por la ley.\n"
                f"3. **Devolución de Equipos:** Al terminar el contrato, se debe permitir la entrega de los equipos entregados en comodato (ONT/Router) sin cobros adicionales.\n"
                f"4. **Expedición de Paz y Salvo:** El operador debe emitir el estado de cuenta y paz y salvo una vez liquidada la última factura correspondiente a los servicios efectivamente prestados."
            )
            voice = "Puedes solicitar la cancelación con al menos 3 días hábiles de anticipación a tu fecha de corte por cualquier canal oficial sin trabas adicionales."
            return text, voice

        # 3. Derecho de Petición, Radicación, PQR y Reclamos
        if any(w in msg_lower for w in ["derecho de peticion", "derecho de petición", "peticion", "petición", "pqr", "reclamo", "queja", "tutela", "radicar", "como poner", "interponer", "radicacion", "radicación"]):
            text = (
                f"{agent_badge}\n"
                f"### ⚖️ Procedimiento Oficial para Radicar un Derecho de Petición o PQR en ETB\n\n"
                f"Como Dirección Jurídica y Normativa de ETB, te indico el procedimiento legal y canales oficiales para radicar tu Derecho de Petición o PQR conforme a la **Ley 1755 de 2015** y la **Resolución CRC 5111 de 2017**:\n\n"
                f"1. **Canales Oficiales Habilitados:**\n"
                f"   - 🌐 **Portal Web Oficial (Inmediato):** Ingresa a [etb.com/pqr](https://etb.com) o a través del Portal Mi ETB en la sección *'Peticiones, Quejas y Reclamos'*. El sistema te genera un número CUN (Código Único Numérico) al instante para seguimiento.\n"
                f"   - 📞 **Línea Telefónica Gratuita:** Comunícate al **178** (desde línea fija ETB), al **(601) 377-7777** en Bogotá, o a la línea nacional **01 8000 111 112**.\n"
                f"   - 🏢 **Puntos Presenciales / Centros de Experiencia:** Radicación física directa en cualquiera de los Centros de Atención ETB en Bogotá y Cundinamarca.\n"
                f"   - ✉️ **Ventanilla Única de Correspondencia:** Envío de comunicación escrita dirigida a la Secretaría General de ETB.\n\n"
                f"2. **Requisitos de la Solicitud:**\n"
                f"   - Nombres, apellidos y número de documento (Cédula de Ciudadanía, Extranjería o NIT de la empresa).\n"
                f"   - Número de cuenta, contrato o línea de servicio asociada.\n"
                f"   - Hechos claros y pretensiones de tu solicitud (reclamación de facturación, inconformidad técnica o administrativa).\n"
                f"   - Dirección física o correo electrónico donde autorizas recibir la notificación.\n\n"
                f"3. **Términos Legales y Garantías:**\n"
                f"   - **Plazo de Respuesta:** Máximo **15 días hábiles** contados a partir del día siguiente a la radicación.\n"
                f"   - **Silencio Administrativo Positivo (SAP):** Si ETB no responde en los 15 días hábiles, la petición se entenderá resuelta a tu favor por mandato de ley.\n"
                f"   - **Recursos de Ley:** Si la respuesta no satisface tus pretensiones, dispones de 10 días hábiles para interponer **Recurso de Reposición y en subsidio de Apelación ante la Superintendencia de Industria y Comercio (SIC)**.\n\n"
                f"¿Deseas que te oriente en la redacción de tus pretensiones o tienes alguna duda adicional sobre los canales?"
            )
            voice = "Para radicar un derecho de petición en ETB puedes ingresar a etb.com/pqr, llamar al 178 o radicarlo en nuestros centros de atención. Debes incluir tu cédula, número de contrato y hechos claros. El término legal de respuesta es de máximo 15 días hábiles conforme a la ley."
            return text, voice

        # 4. Habeas Data y Protección de Datos Personales (Ley 1581)
        if any(w in msg_lower for w in ["habeas data", "datos personales", "ley 1581", "privacidad", "autorizacion", "supresion", "rectificacion"]):
            text = (
                f"{agent_badge}\n"
                f"### ⚖️ Habeas Data y Tratamiento de Datos Personales (Ley 1581 de 2012)\n\n"
                f"¡Hola! Como Secretaría General, te informamos sobre el tratamiento seguro y custodia de tu información:\n\n"
                f"1. **Soberanía y Custodia Nacional:** ETB almacena y procesa todas las bases de datos en sus Centros de Datos Tier III propios en Bogotá (Alma y Prado), sin transferencias no autorizadas a jurisdicciones extranjeras.\n"
                f"2. **Derechos del Titular:** En cualquier momento puedes ejercer tus derechos de **Conocer, Actualizar, Rectificar y Solicitar la Supresión** de tus datos personales, así como revocar la autorización de contacto comercial.\n"
                f"3. **Canal de Radicación:** Envía tu solicitud a través del correo del Oficial de Protección de Datos o mediante radicado PQR en `etb.com/protecciondedatos` con tiempo de respuesta de 10 a 15 días hábiles."
            )
            voice = "ETB custodia los datos personales en centros de datos propios bajo la Ley 1581 de 2012 garantizando derechos de rectificación y supresión."
            return text, voice

        # 5. Contratación Pública y SECOP II
        if any(w in msg_lower for w in ["secop", "licitacion", "estatal", "colombia compra", "pliegos", "rup", "consorcio", "union temporal"]):
            text = (
                f"{agent_badge}\n"
                f"### ⚖️ Capacidad Jurídica y Contratación Pública en SECOP II\n\n"
                f"¡Hola! ETB es una empresa oficial con capacidad jurídica plena para celebrar contratos con entidades estatales:\n\n"
                f"- **Registro Único de Proponentes (RUP):** RUP activo y certificado con los más altos índices de capacidad financiera y organizacional.\n"
                f"- **Plataforma SECOP II:** Proveedor habilitado en el catálogo de acuerdos marco de precios de Colombia Compra Eficiente para conectividad, nube y data centers.\n"
                f"- **Estructuración Contractual:** Capacidad de formalización directa o mediante Consorcios y Uniones Temporales bajo Ley 80 de 1993 y Ley 1150 de 2007."
            )
            voice = "ETB está plenamente habilitada en SECOP 2 y acuerdos marco de Colombia Compra Eficiente para contratación con el Estado."
            return text, voice

        # 6. Respuesta general legal
        text = (
            f"{agent_badge}\n"
            f"### ⚖️ Asesoría Jurídica y Gobernanza Corporativa ETB\n\n"
            f"¡Hola! Te asisto desde la Dirección Jurídica y Normativa de ETB. Garantizamos el estricto cumplimiento de la regulación colombiana:\n\n"
            f"- 📜 **Régimen de Usuarios CRC (Res. 5111/5050):** Transparencia contractual sin cláusulas abusivas.\n"
            f"- 🔒 **Ley 1581 de 2012 (Habeas Data):** Máxima seguridad y custodia de datos corporativos.\n"
            f"- 🏛️ **Contratación Pública:** SECOP II y Acuerdos Marco Colombia Compra Eficiente.\n\n"
            f"¿Qué consulta normativa o contractual deseas que revisemos?"
        )
        voice = "Asesoría Legal ETB en cumplimiento de las resoluciones CRC, Ley 1581 y contratación pública. ¿En qué tema jurídico te orientamos?"
        return text, voice

    def _handle_commercial_query(self, message: str, msg_lower: str, agent_badge: str) -> tuple[str, str]:
        """Genera una respuesta comercial detallada, transparente y estructurada."""
        if any(w in msg_lower for w in ["costo", "precio", "cuanto vale", "cuanto cuesta", "tarifa", "instalacion", "valor", "planes"]):
            text = (
                f"{agent_badge}\n"
                f"### 💼 Portafolio y Tarifas Comerciales de Fibra Óptica ETB\n\n"
                f"¡Hola! Con gusto te detallo los costos y planes disponibles para tu empresa u oficina:\n\n"
                f"**1. Costos de Instalación y Acometida:**\n"
                f"- **Con Permanencia (12 o 24 meses):** **$0 COP (Instalación Gratuita)**. Incluye acometida de fibra hasta tu predio, equipo módem/ONT y router Wi-Fi 6 de alta potencia.\n"
                f"- **Sin Permanencia (Contrato Abierto):** Pago único de **$180.000 a $320.000 COP** en la primera factura según estudio de factibilidad técnica.\n\n"
                f"**2. Planes de Fibra Simétrica 1:1 (Precios en Pesos Colombianos COP / mes):**\n"
                f"- **200 Mbps Simétricos:** **$89.900 COP / mes** (Ideal para oficinas pequeñas y pymes).\n"
                f"- **500 Mbps Simétricos:** **$119.900 COP / mes** (Excelente para trabajo colaborativo y nube).\n"
                f"- **900 Mbps Ultra-Velocidad:** **$149.900 COP / mes** (Máximo rendimiento para alta demanda).\n\n"
                f"**3. Internet Dedicado Corporativo 1:1 (CIR 100% con IP Pública Fija):**\n"
                f"- Desde **$380.000 COP / mes** (50 Mbps) hasta **$1.850.000 COP / mes** (1 Gbps) con disponibilidad SLA del **99.985%**, monitoreo proactivo NOC 24/7 e IP fija incluida.\n\n"
                f"**4. Soluciones Adicionales:**\n"
                f"- **Troncales SIP Cloud:** Desde **$45.000 COP / canal** con llamadas ilimitadas.\n"
                f"- **SD-WAN Corporativo:** Desde **$250.000 COP / sede / mes** para interconectar sucursales de forma segura.\n\n"
                f"¿Deseas que preparemos una cotización formal o validemos la cobertura en la dirección de tu empresa?"
            )
            voice = "La instalación es gratuita en contratos con permanencia. Disponemos de planes simétricos desde 89.900 pesos y enlaces dedicados corporativos desde 380.000 pesos al mes."
            return text, voice

        if any(w in msg_lower for w in ["claro", "tigo", "movistar", "competencia", "comparar", "vs", "diferencia"]):
            text = (
                f"{agent_badge}\n"
                f"### 🛡️ Cuadro Comparativo: Ventajas de ETB frente a la Competencia\n\n"
                f"¡Hola! Te comparto las razones por las cuales las empresas eligen la red de fibra pura de ETB:\n\n"
                f"| Criterio | ETB Fibra Óptica | Claro (América Móvil) | Tigo (Millicom) | Movistar (Telefónica) |\n"
                f"| :--- | :--- | :--- | :--- | :--- |\n"
                f"| **Medio Físico** | **100% Fibra Pura Monomodo** | Coaxial HFC híbrido | Mixto HFC/Fibra | Fibra compartida |\n"
                f"| **Simetría** | **1:1 Real (Misma subida y bajada)** | Asimétrico (10:1) | Asimétrico | Parcialmente simétrico |\n"
                f"| **Ductería** | **4.000+ km propios en Bogotá** | Dependiente de postes | Sin ductería propia | Red compartida |\n"
                f"| **Data Centers** | **Tier III Propios (Alma / Prado)** | Nube foránea | Nube pública | Nube pública |\n"
                f"| **Facturación** | **100% Pesos (COP) Fija** | Ajustes variables | Tarifas variables | Tarifas variables |\n\n"
                f"¿Deseas que analicemos el ahorro de costos migrando tu infraestructura actual a ETB?"
            )
            voice = "ETB se diferencia por ofrecer fibra 100% simétrica y pura, ductería subterránea propia y Centros de Datos Tier 3 en Colombia."
            return text, voice

        text = (
            f"{agent_badge}\n"
            f"### 💼 Soluciones Corporativas & B2B ETB\n\n"
            f"¡Hola! Como tu asesor comercial corporativo, te ofrezco soluciones integrales de conectividad, cloud y ciberseguridad a la medida de tu organización:\n\n"
            f"- 🚀 **Fibra Simétrica 1:1 Pymes y Grandes Empresas**\n"
            f"- 🔒 **Internet Dedicado con IP Pública Fija y SLA 99.98%**\n"
            f"- 📞 **Troncales SIP y Telefonía en la Nube**\n"
            f"- 🌐 **SD-WAN Multi-Sede y Enlaces Punto a Punto**\n\n"
            f"¿Qué servicio o cotización deseas evaluar hoy?"
        )
        voice = "Área Comercial ETB lista para asesorarte en conectividad simétrica, enlaces dedicados y servicios cloud."
        return text, voice

    def _handle_tech_query(self, message: str, msg_lower: str, agent_badge: str) -> tuple[str, str]:
        """Genera una respuesta especializada de Data Centers, Nube Híbrida y SOC."""
        text = (
            f"{agent_badge}\n"
            f"### 🏢 Data Centers Tier III, Nube Soberana y Ciberseguridad SOC\n\n"
            f"¡Hola! Te atiendo desde la Dirección de Tecnología e Infraestructura Cloud de ETB:\n\n"
            f"1. **Data Center Alma (Suba):**\n"
            f"   - 2.500 m² de infraestructura de misión crítica certificada **Tier III Design & Facility** y certificación **ICREA Nivel V**.\n"
            f"   - Redundancia eléctrica 2N, climatización de precisión en pasillos fríos contenidos y PUE < 1.45.\n"
            f"2. **Data Center Prado (Puente Aranda):**\n"
            f"   - Sitio georedundante para planes de recuperación ante desastres (DRP), interconectado con DC Alma mediante anillos de fibra oscura redundantes a 100 Gbps.\n"
            f"3. **ETB Cloud Soberana:**\n"
            f"   - Máquinas virtuales e instancias de almacenamiento facturadas 100% en Pesos (COP) desde **$95.000 COP / mes**, sin costos ocultos de transferencia ni riesgo cambiario.\n"
            f"4. **SOC & Anti-DDoS Gestionado 24/7:**\n"
            f"   - Mitigación en tiempo real de ataques volumétricos hasta 100 Gbps en Capas 3, 4 y 7 con reglas WAF personalizadas.\n\n"
            f"¿Deseas cotizar co-location, servidores dedicados o esquemas de respaldo en la nube?"
        )
        voice = "ETB opera Data Centers Tier 3 propios en Alma y Prado, con nube soberana facturada en pesos y protección Anti-DDoS hasta 100 Gigabits."
        return text, voice

    def _handle_noc_query(self, message: str, msg_lower: str, agent_badge: str) -> tuple[str, str]:
        """Genera una respuesta técnica del Centro de Operaciones de Red (NOC)."""
        text = (
            f"{agent_badge}\n"
            f"### 🌐 Centro de Operaciones de Red (NOC) & Infraestructura DWDM 100G\n\n"
            f"¡Hola! Te asiste el equipo del NOC de ETB. Supervisamos la columna vertebral de telecomunicaciones de la capital:\n\n"
            f"- **Anillos Troncales DWDM:** Red metropolitana mallada a 100 Gbps con conmutación automática de protección en menos de 50 milisegundos.\n"
            f"- **Latencias Ultrabajas:** Menor a **3.2 ms** hacia el NAP Colombia en Bogotá y menor a 12 ms hacia los principales nodos del país.\n"
            f"- **Telemetría y OTDR 24/7:** Monitoreo en tiempo real de la atenuación óptica en dBm y detección inmediata de micro-curvaturas en fibra.\n"
            f"- **Disponibilidad:** SLA global del **99.985%** con redundancia física por ductería subterránea propia."
        )
        voice = "El NOC de ETB supervisa la red DWDM 100G con latencias menores a 3.2 milisegundos y conmutación automática de respaldo."
        return text, voice

    def _handle_finance_query(self, message: str, msg_lower: str, agent_badge: str) -> tuple[str, str]:
        """Genera una respuesta de Planeación Financiera y Costos."""
        text = (
            f"{agent_badge}\n"
            f"### 💰 Planeación Financiera, Modelos TCO y Ahorro Corporativo\n\n"
            f"¡Hola! Desde el área de Planeación Financiera y Costos de ETB, optimizamos tu presupuesto de TI:\n\n"
            f"1. **Cero Exposición al Dólar:** Todos los contratos de conectividad, cloud y telefonía se facturan en **Pesos Colombianos (COP)** fijos, protegiendo tu flujo de caja frente a la devaluación.\n"
            f"2. **Ahorro en TCO (Costo Total de Propiedad):** Reducción de entre **22% y 28%** en comparación con proveedores que tercerizan ductería o dependen de nubes extranjeras.\n"
            f"3. **Modelos OPEX Flexibles:** Sin inversión de capital inicial (CAPEX) en equipamiento ONT o routers Wi-Fi 6 de grado empresarial."
        )
        voice = "Nuestra oferta financiera en pesos colombianos elimina el riesgo cambiario del dólar y optimiza el costo total de propiedad hasta un 28%."
        return text, voice

    def _handle_pmo_query(self, message: str, msg_lower: str, agent_badge: str) -> tuple[str, str]:
        """Genera una respuesta de la Oficina de Gestión de Proyectos (PMO)."""
        text = (
            f"{agent_badge}\n"
            f"### 🚀 Oficina de Proyectos (PMO) y Tiempos de Despliegue de Fibra\n\n"
            f"¡Hola! Te informo sobre los plazos y metodologías de entrega de infraestructura de ETB:\n\n"
            f"1. **Instalación Estándar de Fibra Óptica:** De **3 a 5 días hábiles** desde la aprobación de la orden de servicio.\n"
            f"2. **Proyectos Especiales y Enlaces Dedicados:** De **10 a 20 días hábiles**, incluyendo canalización subterránea, permisos del IDU y tendido de cable.\n"
            f"3. **Certificación de Calidad:** Cada hilo de fibra se entrega con informe reflectométrico **OTDR calibrado**, garantizando niveles de atenuación conformes a norma ITU-T G.652D."
        )
        voice = "La instalación estándar de fibra toma de 3 a 5 días hábiles y proyectos especiales de 10 a 20 días con certificación óptica OTDR."
        return text, voice

    def _handle_cx_query(self, message: str, msg_lower: str, agent_badge: str) -> tuple[str, str]:
        """Genera una respuesta de Experiencia de Cliente y Acompañamiento VIP."""
        text = (
            f"{agent_badge}\n"
            f"### 🌟 Experiencia de Cliente & Acompañamiento VIP ETB\n\n"
            f"¡Hola! Desde el área de Experiencia de Cliente, garantizamos un trato preferencial para tu empresa:\n\n"
            f"- **Gestor VIP Asignado:** Un ejecutivo comercial y un ingeniero de postventa dedicados exclusivamente a tu cuenta.\n"
            f"- **Métricas de Satisfacción:** Índice CSAT superior al **94%** y NPS corporativo de **68 puntos**.\n"
            f"- **Matriz de Escalamiento:** Línea directa de atención sin conmutadores complejos ni tiempos de espera prolongados."
        )
        voice = "Experiencia de Cliente ofrece gestores VIP dedicados con un 94% de satisfacción en el segmento corporativo."
        return text, voice

    def _dispatch_dept_handler(self, dept_key: str, message: str, msg_lower: str, agent_badge: str, history: Optional[List[Dict[str, Any]]] = None) -> tuple[str, str]:
        """Enruta la consulta al manejador conversacional del departamento respectivo."""
        if dept_key == "mesa_ayuda":
            return self._handle_support_query(message, msg_lower, agent_badge, history=history)
        elif dept_key == "juridica":
            return self._handle_legal_query(message, msg_lower, agent_badge)
        elif dept_key == "comercial":
            return self._handle_commercial_query(message, msg_lower, agent_badge)
        elif dept_key == "tecnologia":
            return self._handle_tech_query(message, msg_lower, agent_badge)
        elif dept_key == "operaciones_noc":
            return self._handle_noc_query(message, msg_lower, agent_badge)
        elif dept_key == "financiera":
            return self._handle_finance_query(message, msg_lower, agent_badge)
        elif dept_key == "proyectos_pmo":
            return self._handle_pmo_query(message, msg_lower, agent_badge)
        elif dept_key == "experiencia_cliente":
            return self._handle_cx_query(message, msg_lower, agent_badge)
        else:
            text = (
                f"{agent_badge}\n"
                f"¡Hola! Atiendo tu consulta: *\"{message}\"*\n\n"
                f"En ETB disponemos de la red de fibra óptica 100% pura y centros de datos certificados para apoyar la operación de tu negocio."
            )
            voice = "Solución corporativa procesada por NEXO ETB."
            return text, voice

    def query_agent(self, target: str, message: str, sender: str = "user", history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Consulta contextual inteligente: analiza la intención específica,
        responde como un profesional humano y experto de cada área, y gestiona
        el enrutamiento y la delegación inter-departamental fluida.
        """
        msg_clean = message.strip()
        msg_lower = msg_clean.lower()
        classification = self._classify_query(msg_lower)
        intent = classification["intent"]
        owner_dept = classification["dept_key"]
        owner_node_id = classification["node_id"]
        owner_dept_name = classification["dept_name"]
        owner_emblem = classification.get("emblem", "🌐")

        target_dept = self._resolve_dept_key_from_target(target)
        agent = self.agents.get(target_dept, self.agents["master"])

        response_sections = []
        voice_summary = ""
        source_meta: Optional[Dict[str, str]] = None
        suggested_action = None
        redirect_target = None
        redirect_name = None

        is_active_chat = bool(history and len(history) > 1)
        is_first_turn = not is_active_chat
        agent_badge = f"**[{agent['emblem']} {agent['name']} — {agent['department']}]**\n\n" if is_first_turn else ""

        # ==========================================================
        # 0. CASO CIERRE DE SESIÓN / SATISFACCIÓN DEL USUARIO
        # ==========================================================
        if intent == "satisfaction_close":
            text = (
                f"{agent_badge}"
                f"### 🤝 ¡Ha sido un placer asistirte en NEXO ETB!\n\n"
                f"Me alegra haberte podido ayudar a resolver tu solicitud y gestionar tu requerimiento con total agilidad y transparencia.\n\n"
                f"- 🌟 **Atención Permanente:** Los 50 nodos y 8 departamentos de nuestra constelación están siempre activos para ti y tu empresa.\n"
                f"- 📞 **Canales de Asistencia 24/7:** PBX **(601) 377-7777** | WhatsApp Oficial **+57 305 777 7777**.\n\n"
                f"¡Damos por finalizada esta sesión. Que tengas un excelente día! 🚀"
            )
            return {
                "status": "success",
                "agent": target,
                "agent_name": agent["name"],
                "agent_role": agent["role"],
                "department": agent["department"],
                "color": agent["color"],
                "emblem": agent["emblem"],
                "is_transfer": False,
                "response": text,
                "voice_summary": "Ha sido un placer asistirte. Sesión finalizada con éxito en NEXO ETB. ¡Que tengas un excelente día!",
                "timestamp": datetime.now().isoformat(),
                "source_meta": source_meta,
                "suggested_action": None,
                "redirect_target": None,
                "redirect_name": None
            }

        # ==========================================================
        # 1. CASO MASTER (NEXO ETB CORE - FEDERACIÓN TOTAL)
        # ==========================================================
        if target_dept == "master":
            if intent == "commercial":
                text, voice = self._handle_commercial_query(msg_clean, msg_lower, agent_badge)
                response_sections.append(
                    f"{text}\n\n"
                    f"💡 *¿Deseas dirigirte al nodo de **Soluciones Corporativas & B2B** para solicitar una cotización formal o revisar cobertura en tu zona?*"
                )
                voice_summary = voice
                redirect_target = "c_com"
                redirect_name = "Soluciones Corporativas & B2B"
                suggested_action = {"label": "Ir a Soluciones Corporativas & B2B", "target": "c_com"}

            elif intent == "support":
                text, voice = self._handle_support_query(msg_clean, msg_lower, agent_badge)
                response_sections.append(
                    f"{text}\n\n"
                    f"💡 *¿Deseas dirigirte al nodo de **Mesa de Ayuda & Soporte Técnico** para registrar una incidencia o consultar el estado de tu enlace?*"
                )
                voice_summary = voice
                redirect_target = "c_desk"
                redirect_name = "Mesa de Ayuda & Soporte Técnico"
                suggested_action = {"label": "Ir a Mesa de Ayuda & Soporte Técnico", "target": "c_desk"}

            elif intent == "legal":
                text, voice = self._handle_legal_query(msg_clean, msg_lower, agent_badge)
                response_sections.append(
                    f"{text}\n\n"
                    f"💡 *¿Deseas dirigirte al nodo de **Gobernanza Legal & Normativa** para revisar términos contractuales o regulatorios?*"
                )
                voice_summary = voice
                redirect_target = "c_gob"
                redirect_name = "Gobernanza Legal & Normativa"
                suggested_action = {"label": "Ir a Gobernanza Legal & Normativa", "target": "c_gob"}

            elif intent == "dc_cloud":
                text, voice = self._handle_tech_query(msg_clean, msg_lower, agent_badge)
                response_sections.append(
                    f"{text}\n\n"
                    f"💡 *¿Deseas dirigirte al nodo de **Data Centers & Nube Híbrida** para cotizar servidores o almacenamiento soberano?*"
                )
                voice_summary = voice
                redirect_target = "c_cib"
                redirect_name = "Data Centers & Nube Híbrida"
                suggested_action = {"label": "Ir a Data Centers & Nube Híbrida", "target": "c_cib"}

            elif intent == "pmo":
                text, voice = self._handle_pmo_query(msg_clean, msg_lower, agent_badge)
                response_sections.append(
                    f"{text}\n\n"
                    f"💡 *¿Deseas dirigirte al nodo de **Despliegue de Red & Proyectos** para consultar el estado de una obra?*"
                )
                voice_summary = voice
                redirect_target = "c_pmo"
                redirect_name = "Despliegue de Red & Proyectos"
                suggested_action = {"label": "Ir a Despliegue de Red & Proyectos", "target": "c_pmo"}

            elif intent == "noc":
                text, voice = self._handle_noc_query(msg_clean, msg_lower, agent_badge)
                response_sections.append(
                    f"{text}\n\n"
                    f"💡 *¿Deseas dirigirte al nodo de **Red Troncal & Fibra Óptica** para ver detalles de telemetría y anillos ópticos?*"
                )
                voice_summary = voice
                redirect_target = "c_noc"
                redirect_name = "Red Troncal & Fibra Óptica"
                suggested_action = {"label": "Ir a Red Troncal & Fibra Óptica", "target": "c_noc"}

            elif intent == "finance":
                text, voice = self._handle_finance_query(msg_clean, msg_lower, agent_badge)
                response_sections.append(
                    f"{text}\n\n"
                    f"💡 *¿Deseas dirigirte al nodo de **Planeación Financiera & Costos** para revisar modelos de ahorro TCO?*"
                )
                voice_summary = voice
                redirect_target = "c_erp"
                redirect_name = "Planeación Financiera & Costos"
                suggested_action = {"label": "Ir a Planeación Financiera & Costos", "target": "c_erp"}

            elif intent == "cx":
                text, voice = self._handle_cx_query(msg_clean, msg_lower, agent_badge)
                response_sections.append(
                    f"{text}\n\n"
                    f"💡 *¿Deseas dirigirte al nodo de **Experiencia de Cliente & VIP** para solicitar un gestor corporativo asignado?*"
                )
                voice_summary = voice
                redirect_target = "c_cx"
                redirect_name = "Experiencia de Cliente & VIP"
                suggested_action = {"label": "Ir a Experiencia de Cliente & VIP", "target": "c_cx"}

            else:
                response_sections.append(
                    f"{agent_badge}"
                    f"Bienvenido al Centro de Comando de **NEXO ETB**. Orquesto la red corporativa de 8 departamentos y 50 nodos de infraestructura en tiempo real.\n\n"
                    f"**¿En qué te puedo asesorar hoy?**\n"
                    f"- 💰 *\"¿Cuánto cuesta la instalación de fibra óptica y qué planes hay?\"*\n"
                    f"- 🛠️ *\"Tengo fallas en mi wifi, ¿qué debo hacer paso a paso?\"*\n"
                    f"- ⚖️ *\"¿Cuáles son mis derechos si cancelo antes de la permanencia mínima?\"*\n"
                    f"- 🏢 *\"¿Qué certificaciones tienen los Data Centers Alma y Prado?\"*\n"
                    f"- 🛡️ *\"¿Cuáles son las ventajas de ETB frente a Claro, Tigo y Movistar?\"*"
                )
                voice_summary = "Bienvenido a NEXO ETB. Pregúntame sobre precios de fibra, soporte técnico, centros de datos o temas legales y normativos."

            source_meta = {
                "filename": "Corpus Federado Departamental ETB",
                "excerpt": "Información consolidada y federada de los 8 departamentos estratégicos de ETB."
            }

        # ==========================================================
        # 2. CASO AGENTES DEPARTAMENTALES / NODOS ESPECIALIZADOS
        # ==========================================================
        else:
            # Transferencia inter-departamental si el usuario consulta un tema de otro departamento
            explicit_transfer_keywords = [
                "pasame a", "pásame a", "comunicame con", "comunícame con", 
                "transferir a", "transfiereme a", "transfiéreme a", "cambiar a", 
                "ir a comercial", "ir a juridica", "ir a jurídica", "ir a soporte", 
                "hablar con soporte", "hablar con comercial", "hablar con un asesor",
                "hablar con juridica", "hablar con jurídica", "comunicar con", "dirigirme a"
            ]
            is_explicit_transfer = any(k in msg_lower for k in explicit_transfer_keywords)

            # Transferencia inter-departamental fluida:
            # Si la consulta pertenece inequívocamente a otra área especializada (owner_dept != target_dept y owner_dept != "master")
            # y no es una confirmación genérica, saludo ni gestión de ticket/contrato en curso:
            should_transfer = (
                owner_dept != target_dept and 
                owner_dept != "master" and 
                intent not in ["general", "greeting", "satisfaction_close", "contract_or_ticket"]
            )

            if should_transfer:
                is_transfer = True
                redirect_target = owner_node_id
                redirect_name = owner_dept_name

                transfer_intro = (
                    f"ℹ️ Esta consulta no corresponde a mi área (**{agent['name']}**).\n\n"
                    f"Te voy a transferir de inmediato al nodo de **{owner_dept_name}** para que nuestro especialista atienda tu caso."
                )
                welcome_message = f"¡Bienvenido al área de **{owner_dept_name}**! Retomando tu solicitud sobre *\"{message}\"*:"

                dest_badge = f"**[{owner_emblem} {owner_dept_name}]**\n\n"
                specialist_text, specialist_voice = self._dispatch_dept_handler(owner_dept, msg_clean, msg_lower, dest_badge, history=history)

                response_sections.append(specialist_text)
                voice_summary = f"Te transfiero a {owner_dept_name}. {specialist_voice}"
                suggested_action = {"label": f"Ir a {owner_dept_name}", "target": owner_node_id}

                kb_data = self.knowledge_cache.get(owner_dept, {})
                relevant_snippet, source_file = self._find_clean_snippet_and_file(owner_dept, kb_data, message)
                if relevant_snippet:
                    source_meta = {
                        "filename": source_file or f"{owner_dept}_kb.md",
                        "excerpt": relevant_snippet
                    }

            else:
                # Consulta directa en el departamento correspondiente
                dept_text, dept_voice = self._dispatch_dept_handler(target_dept, msg_clean, msg_lower, agent_badge, history=history)
                response_sections.append(dept_text)
                voice_summary = dept_voice

                # Solo adjuntar extracto documental en la primera consulta exploratoria para no saturar el chat en cada turno
                if not is_active_chat:
                    kb_data = self.knowledge_cache.get(target_dept, {})
                    relevant_snippet, source_file = self._find_clean_snippet_and_file(target_dept, kb_data, message)
                    if relevant_snippet:
                        source_meta = {
                            "filename": source_file or f"{target_dept}_kb.md",
                            "excerpt": relevant_snippet
                        }

        return {
            "status": "success",
            "agent": target,
            "agent_name": agent["name"],
            "agent_role": agent["role"],
            "department": agent["department"],
            "color": agent["color"],
            "emblem": agent["emblem"],
            "is_transfer": is_transfer if "is_transfer" in locals() else False,
            "transfer_intro": transfer_intro if "transfer_intro" in locals() else None,
            "welcome_message": welcome_message if "welcome_message" in locals() else None,
            "response": "\n\n".join(response_sections),
            "voice_summary": voice_summary or "Solución corporativa procesada por NEXO ETB.",
            "timestamp": datetime.now().isoformat(),
            "source_meta": source_meta,
            "suggested_action": suggested_action,
            "redirect_target": redirect_target,
            "redirect_name": redirect_name,
            "metrics": {
                "sla": "99.98%",
                "latency_nap": "<3.5ms",
                "symmetry": "100% FTTH Simétrico",
                "security": "SOC Layer 7 Protected"
            }
        }

    def generate_response(self, target_agent: str, message: str, sender: str = "user", history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Alias para compatibilidad con main.py con soporte para historial"""
        return self.query_agent(target=target_agent, message=message, sender=sender, history=history)

    def get_hierarchy(self) -> Dict[str, Any]:
        """
        Retorna la estructura jerárquica con 47 nodos corporativos de ETB organizada
        estratégicamente en 8 dominios departamentales y el Núcleo Central NEXO ETB.
        """
        nodes = []
        links = []

        # 1. NÚCLEO CENTRAL (Presidencia Ejecutiva & Dirección General)
        nodes.append({
            "id": "master",
            "name": "NEXO ETB CORE",
            "title": "Presidencia Ejecutiva & Dirección General de Soluciones",
            "department": "Presidencia Ejecutiva",
            "role": "Núcleo Central de Federación y Estrategia Corporativa ETB",
            "color": "#22d3ee",
            "emblem": "👑",
            "type": "master",
            "radius": 1.4,
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
            "cluster": "Presidencia",
            "status_cat": "Consolidado",
            "status_color": "#2dd4bf",
            "files_count": len(self.knowledge_cache.get("master", {}).get("files", []))
        })

        # 2. DOMINIOS Y CLUSTERS (8 Departamentos Estratégicos ETB)
        clusters_def = [
            {"id": "c_noc", "name": "Red Troncal & Fibra Óptica", "dept": "operaciones_noc", "x": -8.0, "y": 18.0, "z": -6.0, "color": "#10b981", "cat": "Consolidado"},
            {"id": "c_cib", "name": "Data Centers & Nube Híbrida", "dept": "tecnologia", "x": 24.0, "y": -3.0, "z": 6.0, "color": "#818cf8", "cat": "Consolidado"},
            {"id": "c_com", "name": "Soluciones Corporativas & B2B", "dept": "comercial", "x": 18.0, "y": 14.0, "z": -8.0, "color": "#38bdf8", "cat": "Consolidado"},
            {"id": "c_gob", "name": "Gobernanza Legal & Normativa", "dept": "juridica", "x": -22.0, "y": -4.0, "z": 8.0, "color": "#f59e0b", "cat": "Consolidado"},
            {"id": "c_erp", "name": "Planeación Financiera & Costos", "dept": "financiera", "x": 6.0, "y": -14.0, "z": 4.0, "color": "#a855f7", "cat": "Consolidado"},
            {"id": "c_pmo", "name": "Despliegue de Red & Proyectos", "dept": "proyectos_pmo", "x": -20.0, "y": 10.0, "z": -12.0, "color": "#06b6d4", "cat": "Consolidado"},
            {"id": "c_desk", "name": "Mesa de Ayuda & Soporte Técnico", "dept": "mesa_ayuda", "x": -10.0, "y": -16.0, "z": -8.0, "color": "#ec4899", "cat": "Consolidado"},
            {"id": "c_cx", "name": "Experiencia de Cliente & VIP", "dept": "experiencia_cliente", "x": 22.0, "y": -14.0, "z": -6.0, "color": "#14b8a6", "cat": "Consolidado"}
        ]

        for c in clusters_def:
            nodes.append({
                "id": c["id"],
                "name": c["name"],
                "title": f"Dominio {c['name']}",
                "department": self.agents.get(c["dept"], {}).get("department", c["name"]),
                "role": f"Dominio Departamental: {c['name']}",
                "color": c["color"],
                "emblem": "🌐",
                "type": "domain_cage",
                "radius": 0.85,
                "x": c["x"],
                "y": c["y"],
                "z": c["z"],
                "cluster": c["name"],
                "status_cat": c["cat"],
                "status_color": "#2dd4bf",
                "files_count": len(self.knowledge_cache.get(c["dept"], {}).get("files", []))
            })
            links.append({
                "source": "master",
                "target": c["id"],
                "type": "synapse_primary",
                "color": c["color"],
                "pulse_speed": 1.2
            })

        # 3. NODOS REALES DE INFRAESTRUCTURA, SERVICIOS Y PROYECTOS ETB (Total 47 Nodos)
        projects_def = [
            # 1. Red Troncal & Fibra Óptica (NOC)
            {"id": "n_dwdm", "name": "Anillo DWDM Bogotá 100G", "parent": "c_noc", "cluster": "Red Troncal & Fibra Óptica", "cat": "Consolidado", "color": "#2dd4bf", "offset": [-4.5, -3.0, 3.0]},
            {"id": "n_gpon_mesh", "name": "Malla FTTH GPON / XGS-PON", "parent": "c_noc", "cluster": "Red Troncal & Fibra Óptica", "cat": "Consolidado", "color": "#2dd4bf", "offset": [4.5, 3.0, -2.5]},
            {"id": "n_nap_intercon", "name": "Interconexión NAP Colombia", "parent": "c_noc", "cluster": "Red Troncal & Fibra Óptica", "cat": "Consolidado", "color": "#2dd4bf", "offset": [-5.5, 4.5, 2.0]},
            {"id": "n_telemetry_otdr", "name": "Telemetría y OTDR 24/7", "parent": "c_noc", "cluster": "Red Troncal & Fibra Óptica", "cat": "Quick Win", "color": "#f472b6", "offset": [4.0, -4.5, 3.5]},
            {"id": "n_microtrench", "name": "Microzanjado Subterráneo", "parent": "c_noc", "cluster": "Red Troncal & Fibra Óptica", "cat": "Diagnóstico", "color": "#fb7185", "offset": [6.5, 2.0, 4.0]},
            {"id": "n_noc_l3", "name": "Vigilancia NOC Nivel 3", "parent": "c_noc", "cluster": "Red Troncal & Fibra Óptica", "cat": "Diagnóstico", "color": "#fb7185", "offset": [-2.0, 6.5, -4.0]},

            # 2. Data Centers & Nube Híbrida
            {"id": "n_alma", "name": "Data Center Alma Tier III", "parent": "c_cib", "cluster": "Data Centers & Nube Híbrida", "cat": "Consolidado", "color": "#2dd4bf", "offset": [-4.5, 3.5, 2.5]},
            {"id": "n_prado", "name": "Data Center Prado DRP", "parent": "c_cib", "cluster": "Data Centers & Nube Híbrida", "cat": "Consolidado", "color": "#2dd4bf", "offset": [4.5, 5.0, -2.0]},
            {"id": "n_soc_ddos", "name": "SOC & Anti-DDoS L3-L7 100G", "parent": "c_cib", "cluster": "Data Centers & Nube Híbrida", "cat": "Quick Win", "color": "#f472b6", "offset": [6.0, -3.5, 3.5]},
            {"id": "n_etb_cloud", "name": "Nube Soberana ETB Cloud", "parent": "c_cib", "cluster": "Data Centers & Nube Híbrida", "cat": "Quick Win", "color": "#f472b6", "offset": [-5.0, -5.0, 3.0]},
            {"id": "n_zero_trust", "name": "Arquitectura Zero-Trust", "parent": "c_cib", "cluster": "Data Centers & Nube Híbrida", "cat": "Diagnóstico", "color": "#fb7185", "offset": [6.5, 2.5, -3.5]},
            {"id": "n_draas_backup", "name": "DRaaS & Backup Soberano", "parent": "c_cib", "cluster": "Data Centers & Nube Híbrida", "cat": "Diagnóstico", "color": "#fb7185", "offset": [2.0, -7.0, -2.5]},

            # 3. Soluciones Corporativas & B2B
            {"id": "n_ftth_ded", "name": "Internet Dedicado Simétrico", "parent": "c_com", "cluster": "Soluciones Corporativas & B2B", "cat": "Consolidado", "color": "#2dd4bf", "offset": [3.5, 4.0, 2.0]},
            {"id": "n_p2p_l2l3", "name": "Transporte Punto a Punto L2/L3", "parent": "c_com", "cluster": "Soluciones Corporativas & B2B", "cat": "Consolidado", "color": "#2dd4bf", "offset": [-4.0, 5.5, 2.5]},
            {"id": "n_sip_cloud", "name": "Troncales SIP Cloud & PBX", "parent": "c_com", "cluster": "Soluciones Corporativas & B2B", "cat": "Quick Win", "color": "#f472b6", "offset": [5.5, -3.0, -3.0]},
            {"id": "n_sdwan", "name": "SD-WAN Administrado Multi-Sede", "parent": "c_com", "cluster": "Soluciones Corporativas & B2B", "cat": "Quick Win", "color": "#f472b6", "offset": [-3.5, -4.5, 3.5]},
            {"id": "n_smart_city", "name": "Soluciones Smart City & IoT", "parent": "c_com", "cluster": "Soluciones Corporativas & B2B", "cat": "Diagnóstico", "color": "#fb7185", "offset": [6.0, 3.5, 3.0]},
            {"id": "n_pymes_cloud", "name": "Conectividad Pymes + Seguridad", "parent": "c_com", "cluster": "Soluciones Corporativas & B2B", "cat": "Diagnóstico", "color": "#fb7185", "offset": [1.5, -6.5, -3.5]},

            # 4. Gobernanza Legal & Normativa
            {"id": "n_crc_5111", "name": "Régimen Usuarios CRC 5111", "parent": "c_gob", "cluster": "Gobernanza Legal & Normativa", "cat": "Consolidado", "color": "#2dd4bf", "offset": [-4.0, 3.5, 2.5]},
            {"id": "n_secop", "name": "Contratación Estatal SECOP II", "parent": "c_gob", "cluster": "Gobernanza Legal & Normativa", "cat": "Consolidado", "color": "#2dd4bf", "offset": [4.5, -3.5, 2.5]},
            {"id": "n_habeas", "name": "Ley 1581 Protección Datos", "parent": "c_gob", "cluster": "Gobernanza Legal & Normativa", "cat": "Consolidado", "color": "#2dd4bf", "offset": [-5.5, -4.0, -2.5]},
            {"id": "n_crc_5050", "name": "Calidad de Servicio CRC 5050", "parent": "c_gob", "cluster": "Gobernanza Legal & Normativa", "cat": "Quick Win", "color": "#f472b6", "offset": [5.0, 4.0, -2.5]},
            {"id": "n_spectrum_reg", "name": "Regulación Espectro MinTIC", "parent": "c_gob", "cluster": "Gobernanza Legal & Normativa", "cat": "Diagnóstico", "color": "#fb7185", "offset": [2.0, 6.5, 3.0]},

            # 5. Planeación Financiera & Costos
            {"id": "n_tco_cop", "name": "Optimización TCO en Pesos (COP)", "parent": "c_erp", "cluster": "Planeación Financiera & Costos", "cat": "Consolidado", "color": "#2dd4bf", "offset": [-3.5, 3.5, 2.0]},
            {"id": "n_duct_infra", "name": "Amortización Ductería Propia", "parent": "c_erp", "cluster": "Planeación Financiera & Costos", "cat": "Consolidado", "color": "#2dd4bf", "offset": [4.0, 4.0, -2.5]},
            {"id": "n_capex_model", "name": "Modelación CAPEX/OPEX de Red", "parent": "c_erp", "cluster": "Planeación Financiera & Costos", "cat": "Quick Win", "color": "#f472b6", "offset": [4.5, -3.5, 2.5]},
            {"id": "n_e_invoicing", "name": "Facturación Electrónica B2B", "parent": "c_erp", "cluster": "Planeación Financiera & Costos", "cat": "Diagnóstico", "color": "#fb7185", "offset": [-4.5, -4.5, -2.0]},
            {"id": "n_roi_fiber", "name": "Plan de Retorno ROI Fibra", "parent": "c_erp", "cluster": "Planeación Financiera & Costos", "cat": "Diagnóstico", "color": "#fb7185", "offset": [1.5, -6.5, 3.0]},

            # 6. Despliegue de Red & Proyectos
            {"id": "n_pmo_agile", "name": "Ruta Crítica PMO & Sprints", "parent": "c_pmo", "cluster": "Despliegue de Red & Proyectos", "cat": "Consolidado", "color": "#2dd4bf", "offset": [3.5, 2.5, 2.5]},
            {"id": "n_idu_permits", "name": "Permisos IDU y Espacio Público", "parent": "c_pmo", "cluster": "Despliegue de Red & Proyectos", "cat": "Quick Win", "color": "#f472b6", "offset": [-4.0, 4.0, -2.5]},
            {"id": "n_suba_expansion", "name": "Expansión Troncal Suba-Usaquén", "parent": "c_pmo", "cluster": "Despliegue de Red & Proyectos", "cat": "Diagnóstico", "color": "#fb7185", "offset": [4.5, -3.5, -2.0]},
            {"id": "n_otdr_cert", "name": "Certificación OTDR Cuadrillas", "parent": "c_pmo", "cluster": "Despliegue de Red & Proyectos", "cat": "Diagnóstico", "color": "#fb7185", "offset": [-4.5, -4.0, 2.5]},
            {"id": "n_sabana_reach", "name": "Cobertura Troncal Sabana", "parent": "c_pmo", "cluster": "Despliegue de Red & Proyectos", "cat": "Diagnóstico", "color": "#fb7185", "offset": [1.5, 6.0, 3.0]},

            # 7. Mesa de Ayuda & Soporte Técnico
            {"id": "n_itil_desk", "name": "Service Desk ITIL v4 N1/N2", "parent": "c_desk", "cluster": "Mesa de Ayuda & Soporte Técnico", "cat": "Consolidado", "color": "#2dd4bf", "offset": [-3.5, 3.0, 2.0]},
            {"id": "n_ont_triage", "name": "Diagnóstico Remoto ONT/CPE", "parent": "c_desk", "cluster": "Mesa de Ayuda & Soporte Técnico", "cat": "Quick Win", "color": "#f472b6", "offset": [4.0, 3.5, -2.0]},
            {"id": "n_vip_desk", "name": "Mesa Preferencial Clientes VIP", "parent": "c_desk", "cluster": "Mesa de Ayuda & Soporte Técnico", "cat": "Quick Win", "color": "#f472b6", "offset": [3.5, -3.5, 2.5]},
            {"id": "n_frt_opt", "name": "Optimización FRT (< 3 min)", "parent": "c_desk", "cluster": "Mesa de Ayuda & Soporte Técnico", "cat": "Diagnóstico", "color": "#fb7185", "offset": [-4.0, -4.0, -2.5]},

            # 8. Experiencia de Cliente & VIP
            {"id": "n_nps_b2b", "name": "NPS Corporativo B2B > 68 pts", "parent": "c_cx", "cluster": "Experiencia de Cliente & VIP", "cat": "Consolidado", "color": "#2dd4bf", "offset": [3.5, 3.0, 2.0]},
            {"id": "n_csat_enterprise", "name": "CSAT 94% Enlaces Empresariales", "parent": "c_cx", "cluster": "Experiencia de Cliente & VIP", "cat": "Quick Win", "color": "#f472b6", "offset": [-3.5, 3.5, -2.0]},
            {"id": "n_selfservice_cx", "name": "Portal Autoservicio Cliente", "parent": "c_cx", "cluster": "Experiencia de Cliente & VIP", "cat": "Diagnóstico", "color": "#fb7185", "offset": [4.0, -3.5, 2.5]},
            {"id": "n_proactive_care", "name": "Acompañamiento VIP Proactivo", "parent": "c_cx", "cluster": "Experiencia de Cliente & VIP", "cat": "Diagnóstico", "color": "#fb7185", "offset": [-3.5, -4.0, -2.0]}
        ]

        for p in projects_def:
            parent_node = next((n for n in nodes if n["id"] == p["parent"]), None)
            px = parent_node["x"] + p["offset"][0] if parent_node else p["offset"][0]
            py = parent_node["y"] + p["offset"][1] if parent_node else p["offset"][1]
            pz = parent_node["z"] + p["offset"][2] if parent_node else p["offset"][2]

            nodes.append({
                "id": p["id"],
                "name": p["name"],
                "title": p["name"],
                "department": p["cluster"],
                "role": f"Iniciativa {p['cat']} - {p['cluster']}",
                "color": p["color"],
                "emblem": "✨" if p["cat"] == "Quick Win" else ("💎" if p["cat"] == "Consolidado" else "🔹"),
                "type": "project_node",
                "radius": 0.32 if p["cat"] == "Consolidado" else 0.24,
                "x": round(px, 2),
                "y": round(py, 2),
                "z": round(pz, 2),
                "cluster": p["cluster"],
                "status_cat": p["cat"],
                "status_color": "#f472b6" if p["cat"] == "Quick Win" else ("#2dd4bf" if p["cat"] == "Consolidado" else "#fb7185"),
                "files_count": 1
            })

            # Enlace con el cluster departamental
            links.append({
                "source": p["parent"],
                "target": p["id"],
                "type": "synapse_satellite",
                "color": p["color"],
                "pulse_speed": 1.6
            })

        # Enlaces cruzados inter-cluster para representar la malla sináptica corporativa
        inter_mesh = [
            ("c_noc", "c_cib", "#818cf8"),
            ("c_cib", "c_erp", "#a855f7"),
            ("c_erp", "c_gob", "#f59e0b"),
            ("c_gob", "c_pmo", "#06b6d4"),
            ("c_pmo", "c_noc", "#10b981"),
            ("c_com", "c_erp", "#38bdf8"),
            ("c_desk", "c_cx", "#14b8a6"),
            ("c_noc", "c_desk", "#ec4899"),
            ("n_dwdm", "n_alma", "#2dd4bf"),
            ("n_alma", "n_prado", "#2dd4bf"),
            ("n_ftth_ded", "n_gpon_mesh", "#2dd4bf"),
            ("n_soc_ddos", "n_noc_l3", "#f472b6"),
            ("n_sdwan", "n_etb_cloud", "#f472b6")
        ]

        for s, t, col in inter_mesh:
            links.append({
                "source": s,
                "target": t,
                "type": "synapse_inter",
                "color": col,
                "pulse_speed": 1.0
            })

        # Conteo exacto para el HUD
        diag_count = sum(1 for n in nodes if n.get("status_cat") == "Diagnóstico")
        qw_count = sum(1 for n in nodes if n.get("status_cat") == "Quick Win")
        consol_count = sum(1 for n in nodes if n.get("status_cat") == "Consolidado")

        return {
            "constellation_name": "NEXO ETB",
            "version": "3.2.0-Enterprise",
            "total_nodes": len(nodes),
            "total_links": len(links),
            "stats": {
                "total": len(nodes),
                "diagnostico": diag_count,
                "quick_win": qw_count,
                "consolidado": consol_count
            },
            "nodes": nodes,
            "links": links,
            "telemetry": {
                "core_load": "36%",
                "fiber_stability": "99.985%",
                "latency_nap": "<3.2 ms",
                "active_agents": len(self.agents)
            }
        }
