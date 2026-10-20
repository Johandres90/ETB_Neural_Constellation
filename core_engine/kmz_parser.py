"""
KMZ & KML Parser Engine - AHOM FIBER IA CORP
Procesamiento robusto de archivos geoespaciales (.kmz y .kml) para telecomunicaciones.
Extrae trazados de fibra óptica, cajas NAP, mufas de empalme, cámaras subterráneas y polígonos de cobertura.
"""

import io
import re
import math
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


def haversine_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """Calcula la distancia geodésica en metros entre dos puntos (lat, lon)."""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371000.0  # Radio terrestre en metros

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return R * c


def parse_coordinates_string(coords_str: str) -> List[Tuple[float, float, float]]:
    """Parsea una cadena de coordenadas KML (lon,lat,alt lon,lat,alt ...)."""
    coords = []
    if not coords_str:
        return coords

    # Limpiar saltos de línea y espacios
    tokens = coords_str.strip().split()
    for token in tokens:
        parts = token.strip().split(',')
        if len(parts) >= 2:
            try:
                lon = float(parts[0])
                lat = float(parts[1])
                alt = float(parts[2]) if len(parts) > 2 else 0.0
                coords.append((lat, lon, alt))
            except ValueError:
                continue
    return coords


def strip_namespace(tag: str) -> str:
    """Remueve el namespace XML si está presente (ej. {http://www.opengis.net/kml/2.2}Placemark -> Placemark)."""
    if '}' in tag:
        return tag.split('}', 1)[1]
    return tag


def parse_kmz_or_kml_bytes(file_bytes: bytes, filename: str = "red_fibra.kmz") -> Dict[str, Any]:
    """
    Decodifica e interpreta un archivo .kmz o .kml en bytes.
    Retorna un diccionario estructurado con metadatos, elementos pasivos y trazados lineales.
    """
    kml_content = None
    is_kmz = False

    # Intentar abrir como archivo ZIP (KMZ)
    if zipfile.is_zipfile(io.BytesIO(file_bytes)):
        is_kmz = True
        with zipfile.ZipFile(io.BytesIO(file_bytes), 'r') as z:
            # Buscar archivo .kml dentro del ZIP (usualmente doc.kml)
            kml_files = [n for n in z.namelist() if n.lower().endswith('.kml')]
            if not kml_files:
                raise ValueError("El archivo .KMZ no contiene ningún archivo .kml válido en su interior.")
            # Preferir doc.kml si existe, o el primero
            target_kml = "doc.kml" if "doc.kml" in kml_files else kml_files[0]
            kml_content = z.read(target_kml).decode('utf-8', errors='replace')
    else:
        # Tratar como archivo KML plano
        try:
            kml_content = file_bytes.decode('utf-8', errors='replace')
        except Exception:
            raise ValueError("No se pudo interpretar el archivo como KMZ o KML válido.")

    return _parse_kml_text(kml_content, filename, is_kmz)


def _parse_kml_text(kml_text: str, filename: str, is_kmz: bool) -> Dict[str, Any]:
    """Parsea el contenido XML de un KML y clasifica elementos de red óptica."""
    root = ET.fromstring(kml_text)

    doc_name = filename
    doc_desc = ""

    # Buscar nombre y descripción general
    for elem in root.iter():
        tag = strip_namespace(elem.tag)
        if tag == "Document":
            for child in elem:
                ctag = strip_namespace(child.tag)
                if ctag == "name" and child.text:
                    doc_name = child.text.strip()
                elif ctag == "description" and child.text:
                    doc_desc = child.text.strip()
            break

    naps = []
    mufas = []
    postes = []
    camaras = []
    centrales = []
    otros_puntos = []
    trazados_fibra = []
    poligonos_cobertura = []

    total_longitud_fibra_metros = 0.0
    all_lats = []
    all_lons = []

    for elem in root.iter():
        tag = strip_namespace(elem.tag)
        if tag != "Placemark":
            continue

        p_name = "Sin Nombre"
        p_desc = ""
        p_extended: Dict[str, str] = {}

        point_coord = None
        line_coords = []
        poly_coords = []

        for child in elem:
            ctag = strip_namespace(child.tag)
            if ctag == "name" and child.text:
                p_name = child.text.strip()
            elif ctag == "description" and child.text:
                p_desc = child.text.strip()
            elif ctag == "ExtendedData":
                for sub in child.iter():
                    stag = strip_namespace(sub.tag)
                    if stag in ["Data", "SimpleData"]:
                        attr_name = sub.attrib.get("name", "")
                        for val_node in sub:
                            if strip_namespace(val_node.tag) == "value" and val_node.text:
                                p_extended[attr_name] = val_node.text.strip()
                        if not p_extended.get(attr_name) and sub.text:
                            p_extended[attr_name] = sub.text.strip()
            elif ctag == "Point":
                for pchild in child:
                    if strip_namespace(pchild.tag) == "coordinates" and pchild.text:
                        parsed = parse_coordinates_string(pchild.text)
                        if parsed:
                            point_coord = parsed[0]
            elif ctag in ["LineString", "MultiGeometry"]:
                for lchild in child.iter():
                    if strip_namespace(lchild.tag) == "coordinates" and lchild.text:
                        line_coords = parse_coordinates_string(lchild.text)
            elif ctag == "Polygon":
                for pchild in child.iter():
                    if strip_namespace(pchild.tag) == "coordinates" and pchild.text:
                        poly_coords = parse_coordinates_string(pchild.text)

        # Registro de puntos geográficos
        if point_coord:
            lat, lon, alt = point_coord
            all_lats.append(lat)
            all_lons.append(lon)
            item = {
                "name": p_name,
                "lat": lat,
                "lon": lon,
                "alt": alt,
                "description": p_desc,
                "attributes": p_extended
            }
            name_lower = p_name.lower()
            if any(k in name_lower for k in ["nap", "caja", "dispersion", "splitter"]):
                naps.append(item)
            elif any(k in name_lower for k in ["mufa", "fosc", "empalme", "torpedo"]):
                mufas.append(item)
            elif any(k in name_lower for k in ["poste", "pole", "apoyo"]) or re.match(r"^p[-_\d]", name_lower):
                postes.append(item)
            elif any(k in name_lower for k in ["camara", "pozo", "manhole", "cam"]):
                camaras.append(item)
            elif any(k in name_lower for k in ["olt", "central", "nodo", "hub", "torre", "cabecera"]):
                centrales.append(item)
            else:
                otros_puntos.append(item)

        # Registro de trazados lineales (cables / ductos)
        if line_coords and len(line_coords) >= 2:
            seg_len = 0.0
            for i in range(len(line_coords) - 1):
                c1 = (line_coords[i][0], line_coords[i][1])
                c2 = (line_coords[i+1][0], line_coords[i+1][1])
                seg_len += haversine_distance(c1, c2)
                all_lats.extend([c1[0], c2[0]])
                all_lons.extend([c1[1], c2[1]])

            total_longitud_fibra_metros += seg_len
            trazados_fibra.append({
                "name": p_name,
                "puntos": len(line_coords),
                "longitud_metros": round(seg_len, 2),
                "longitud_km": round(seg_len / 1000.0, 3),
                "coordenadas": [(round(c[0], 6), round(c[1], 6)) for c in line_coords[:50]],  # Muestreo
                "attributes": p_extended
            })

        # Registro de polígonos
        if poly_coords:
            poligonos_cobertura.append({
                "name": p_name,
                "vertices": len(poly_coords),
                "description": p_desc
            })

    bounding_box = None
    if all_lats and all_lons:
        bounding_box = {
            "min_lat": round(min(all_lats), 6),
            "max_lat": round(max(all_lats), 6),
            "min_lon": round(min(all_lons), 6),
            "max_lon": round(max(all_lons), 6),
            "center": (round(sum(all_lats) / len(all_lats), 6), round(sum(all_lons) / len(all_lons), 6))
        }

    return {
        "status": "success",
        "file_type": "KMZ" if is_kmz else "KML",
        "filename": filename,
        "document_name": doc_name,
        "description": doc_desc,
        "parsed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metrics": {
            "total_km_fibra": round(total_longitud_fibra_metros / 1000.0, 2),
            "total_metros_fibra": round(total_longitud_fibra_metros, 1),
            "total_trazados": len(trazados_fibra),
            "total_naps": len(naps),
            "total_mufas": len(mufas),
            "total_postes": len(postes),
            "total_camaras": len(camaras),
            "total_centrales_olt": len(centrales),
            "total_poligonos_cobertura": len(poligonos_cobertura),
            "total_elementos_registrados": (len(naps) + len(mufas) + len(postes) +
                                            len(camaras) + len(centrales) + len(otros_puntos) +
                                            len(trazados_fibra) + len(poligonos_cobertura))
        },
        "bounding_box": bounding_box,
        "elements": {
            "naps": naps[:100],  # Límites para memoria
            "mufas": mufas[:50],
            "postes": postes[:100],
            "camaras": camaras[:50],
            "centrales_olt": centrales[:20],
            "trazados": trazados_fibra[:50],
            "poligonos": poligonos_cobertura[:20]
        }
    }


def generate_kmz_knowledge_markdown(data: Dict[str, Any]) -> str:
    """Convierte los datos del KMZ en un documento de conocimiento Markdown completo para RAG."""
    m = data["metrics"]
    bbox = data.get("bounding_box") or {}
    center = bbox.get("center", (0.0, 0.0))

    md = f"""# Mapa de Red Cartográfico GIS: {data['document_name']}
- **Archivo Origen:** `{data['filename']}` ({data['file_type']})
- **Fecha de Procesamiento:** {data['parsed_at']}
- **Coordenadas Centrales del Despliegue:** Latitud {center[0]}, Longitud {center[1]}
- **Bounding Box (Área de Influencia):**
  - Latitud: {bbox.get('min_lat')} a {bbox.get('max_lat')}
  - Longitud: {bbox.get('min_lon')} a {bbox.get('max_lon')}

---

## 📊 Telemetría y Métricas del Trazado Geoespacial
- **Longitud Total de Fibra Óptica Trazada:** **{m['total_km_fibra']} km** ({m['total_metros_fibra']} metros).
- **Segmentos / Trazados de Red:** {m['total_trazados']} rutas lineales independientes.
- **Cajas NAP (Dispersión Óptica):** **{m['total_naps']} NAPs** georreferenciadas.
- **Mufas de Empalme (FOSC):** **{m['total_mufas']} mufas** registradas.
- **Postería / Apoyos Aéreos:** **{m['total_postes']} postes** identificados.
- **Cámaras / Pozos Subterráneos:** **{m['total_camaras']} cámaras** de inspección.
- **Cabeceras OLT / Centrales:** **{m['total_centrales_olt']} nodos principales**.
- **Polígonos de Cobertura Comercial:** **{m['total_poligonos_cobertura']} zonas** delimitadas.

---

## 📍 Inventario de Elementos Pasivos de Red (Georreferenciados)

### Cajas NAP Identificadas ({len(data['elements']['naps'])} primeras):
"""
    if data['elements']['naps']:
        for nap in data['elements']['naps']:
            md += f"- **{nap['name']}:** Coordenadas `({nap['lat']}, {nap['lon']})`"
            if nap.get('description'):
                md += f" — Info: {nap['description']}"
            md += "\n"
    else:
        md += "_No se detectaron cajas NAP con nomenclatura explícita._\n"

    md += f"\n### Mufas de Empalme y FOSC ({len(data['elements']['mufas'])} primeras):\n"
    if data['elements']['mufas']:
        for mufa in data['elements']['mufas']:
            md += f"- **{mufa['name']}:** Coordenadas `({mufa['lat']}, {mufa['lon']})`\n"
    else:
        md += "_No se detectaron mufas de empalme con nomenclatura explícita._\n"

    md += f"\n### Trazados de Cable y Rutas Troncales ({len(data['elements']['trazados'])} primeras):\n"
    if data['elements']['trazados']:
        for tr in data['elements']['trazados']:
            md += f"- **{tr['name']}:** Longitud **{tr['longitud_km']} km** ({tr['longitud_metros']} m) con {tr['puntos']} vértices de trazado.\n"
    else:
        md += "_No se detectaron líneas de cable independientes._\n"

    md += """
---

## 🧭 Directrices de Factibilidad y Respuesta del Agente GIS
1. **Factibilidad de Cobertura:** Para determinar si un cliente o dirección tiene factibilidad, el Agente GIS calcula la distancia mínima entre las coordenadas consultadas y la caja NAP más cercana del inventario.
2. **Capacidad de Red:** Si la distancia es menor a 180 metros, se declara **Factibilidad Técnica Inmediata** para acometida drop.
3. **Auditoría de Ruta:** En caso de cortes o mantenimiento, el Agente GIS localiza el trazado troncal y la mufa aguas arriba que alimenta la zona afectada.
"""
    return md


def build_kmz_bytes(
    location_name: str,
    center_lat: float,
    center_lon: float,
    naps: Optional[List[Dict[str, Any]]] = None,
    mufas: Optional[List[Dict[str, Any]]] = None,
    postes: Optional[List[Dict[str, Any]]] = None,
    camaras: Optional[List[Dict[str, Any]]] = None,
    line_coords: Optional[List[Tuple[float, float]]] = None,
    total_km: float = 1.47
) -> bytes:
    """
    Construye un archivo .KMZ profesional compatible al 100% con Google Earth y QGIS.
    Empaqueta:
      - doc.kml con estilos, carpetas organizadas y tablas HTML de telemetría.
      - files/Poste.png (icono oficial de poste)
      - files/Camara doble.png (icono oficial de cámara doble subterránea)
    """
    import base64
    from core_engine.gis_icons_b64 import POSTE_PNG_B64, CAMARA_DOBLE_PNG_B64

    poste_png_bytes = base64.b64decode(POSTE_PNG_B64)
    camara_png_bytes = base64.b64decode(CAMARA_DOBLE_PNG_B64)

    # Coordenadas por defecto si no vienen provistas
    lat = float(center_lat)
    lon = float(center_lon)

    if not naps:
        naps = [
            {"name": "NAP-01 (16p)", "lat": round(lat + 0.0006, 6), "lon": round(lon - 0.0008, 6), "puertos": 16, "potencia": "-19.2 dBm"},
            {"name": "NAP-02 (16p)", "lat": round(lat + 0.0012, 6), "lon": round(lon + 0.0005, 6), "puertos": 16, "potencia": "-19.5 dBm"},
            {"name": "NAP-03 (16p)", "lat": round(lat + 0.0004, 6), "lon": round(lon + 0.0018, 6), "puertos": 16, "potencia": "-19.8 dBm"},
            {"name": "NAP-04 (16p)", "lat": round(lat - 0.0008, 6), "lon": round(lon + 0.0028, 6), "puertos": 16, "potencia": "-20.1 dBm"},
        ]

    if not mufas:
        mufas = [
            {"name": "Mufa FOSC Principal", "lat": round(lat - 0.0010, 6), "lon": round(lon - 0.0015, 6), "tipo": "FOSC 400 48 FO"}
        ]

    if not postes:
        postes = [
            {"name": f"P-{i+1:02d} Concreto 8m", "lat": round(lat - 0.0015 + i*0.0007, 6), "lon": round(lon - 0.0018 + i*0.0006, 6)}
            for i in range(6)
        ]

    if not camaras:
        camaras = [
            {"name": "Cámara Doble CD-01", "lat": round(lat - 0.0020, 6), "lon": round(lon - 0.0022, 6)},
            {"name": "Cámara Doble CD-02", "lat": round(lat + 0.0002, 6), "lon": round(lon + 0.0008, 6)},
        ]

    if not line_coords:
        line_coords = [
            (round(lat - 0.0025, 6), round(lon - 0.0030, 6)),
            (round(lat - 0.0018, 6), round(lon - 0.0020, 6)),
            (round(lat - 0.0010, 6), round(lon - 0.0015, 6)),
            (round(lat + 0.0000, 6), round(lon + 0.0000, 6)),
            (round(lat + 0.0006, 6), round(lon + 0.0012, 6)),
            (round(lat + 0.0015, 6), round(lon + 0.0025, 6)),
        ]

    coords_kml_str = "\n            ".join(f"{pt[1]},{pt[0]},0" for pt in line_coords)

    # Construcción de KML
    kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>AHOM FIBER - Red de Fibra Óptica: {location_name}</name>
    <description><![CDATA[
      <h3>AHOM FIBER IA CORP - Red de Telecomunicaciones</h3>
      <p><b>Ubicación:</b> {location_name}</p>
      <p><b>Longitud Total de Fibra:</b> {total_km} km</p>
      <p><b>Total NAPs:</b> {len(naps)} Cajas (Capacidad: {len(naps)*16} Puertos GPON)</p>
      <p><b>Postes Aéreos:</b> {len(postes)} | <b>Cámaras Subterráneas:</b> {len(camaras)}</p>
      <p><i>Generado automáticamente por el Agente de Ingeniería GIS</i></p>
    ]]></description>

    <!-- Estilos de Red con Iconos Personalizados en files/ -->
    <Style id="stylePoste">
      <IconStyle>
        <scale>1.1</scale>
        <Icon><href>files/Poste.png</href></Icon>
      </IconStyle>
    </Style>

    <Style id="styleCamara">
      <IconStyle>
        <scale>1.1</scale>
        <Icon><href>files/Camara doble.png</href></Icon>
      </IconStyle>
    </Style>

    <Style id="styleNAP">
      <IconStyle>
        <color>ff00ff00</color>
        <scale>1.1</scale>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/target.png</href></Icon>
      </IconStyle>
    </Style>

    <Style id="styleMufa">
      <IconStyle>
        <color>ff00aaff</color>
        <scale>1.2</scale>
        <Icon><href>http://maps.google.com/mapfiles/kml/shapes/caution.png</href></Icon>
      </IconStyle>
    </Style>

    <Style id="styleFibraTroncal">
      <LineStyle>
        <color>ffffff00</color>
        <width>4</width>
      </LineStyle>
    </Style>

    <!-- Carpeta 1: Trazado Fibra Óptica -->
    <Folder>
      <name>1. Trazado Fibra Óptica</name>
      <open>1</open>
      <Placemark>
        <name>Tendido Troncal &amp; Distribución ({total_km} km)</name>
        <styleUrl>#styleFibraTroncal</styleUrl>
        <description><![CDATA[
          <table border="1" cellpadding="4" style="border-collapse:collapse;font-family:sans-serif;font-size:12px;">
            <tr bgcolor="#0f172a" style="color:#22d3ee;"><th>Parámetro</th><th>Especificación</th></tr>
            <tr><td><b>Cable Óptico</b></td><td>ADSS Monomodo ITU-T G.652D 48 Hilos</td></tr>
            <tr><td><b>Longitud de Ruta</b></td><td>{total_km} km</td></tr>
            <tr><td><b>Atenuación Estimada</b></td><td>-{(float(total_km)*0.35 + 14.5):.1f} dBm</td></tr>
            <tr><td><b>Sede / Municipio</b></td><td>{location_name}</td></tr>
          </table>
        ]]></description>
        <LineString>
          <tessellate>1</tessellate>
          <coordinates>
            {coords_kml_str}
          </coordinates>
        </LineString>
      </Placemark>
    </Folder>

    <!-- Carpeta 2: Postería y Cámaras -->
    <Folder>
      <name>2. Postería y Cámaras Subterráneas</name>
"""
    for cam in camaras:
        kml += f"""      <Placemark>
        <name>{cam['name']}</name>
        <styleUrl>#styleCamara</styleUrl>
        <description><![CDATA[
          <b>Tipo:</b> Cámara Doble Subterránea de Inspección y Paso<br>
          <b>Coordenadas:</b> ({cam['lat']}, {cam['lon']})<br>
          <b>Ductería:</b> 4 Vías PVC 4 pulgadas con subductos PEAD
        ]]></description>
        <Point><coordinates>{cam['lon']},{cam['lat']},0</coordinates></Point>
      </Placemark>
"""
    for p in postes:
        kml += f"""      <Placemark>
        <name>{p['name']}</name>
        <styleUrl>#stylePoste</styleUrl>
        <description><![CDATA[
          <b>Tipo:</b> Poste de Concreto para Tendido Aéreo de Fibra<br>
          <b>Coordenadas:</b> ({p['lat']}, {p['lon']})<br>
          <b>Vano Promedio:</b> 38 metros con herrajes tipo D y cruceta
        ]]></description>
        <Point><coordinates>{p['lon']},{p['lat']},0</coordinates></Point>
      </Placemark>
"""
    kml += """    </Folder>

    <!-- Carpeta 3: Cajas NAP / Mufas FOSC -->
    <Folder>
      <name>3. Cajas NAP y Mufas FOSC</name>
"""
    for m in mufas:
        kml += f"""      <Placemark>
        <name>{m['name']}</name>
        <styleUrl>#styleMufa</styleUrl>
        <description><![CDATA[
          <table border="1" cellpadding="3" style="border-collapse:collapse;font-size:12px;">
            <tr><td><b>Elemento</b></td><td>Mufa FOSC 400 de Empalme por Fusión</td></tr>
            <tr><td><b>Capacidad</b></td><td>48 Fusiones Ópticas (Bandejas 12F)</td></tr>
            <tr><td><b>Coordenadas</b></td><td>({m['lat']}, {m['lon']})</td></tr>
          </table>
        ]]></description>
        <Point><coordinates>{m['lon']},{m['lat']},0</coordinates></Point>
      </Placemark>
"""
    for n in naps:
        puertos = n.get('puertos', 16)
        pot = n.get('potencia', '-19.4 dBm')
        kml += f"""      <Placemark>
        <name>{n['name']}</name>
        <styleUrl>#styleNAP</styleUrl>
        <description><![CDATA[
          <table border="1" cellpadding="3" style="border-collapse:collapse;font-size:12px;">
            <tr bgcolor="#064e3b" style="color:#34d399;"><th colspan="2">Caja NAP GPON FTTH</th></tr>
            <tr><td><b>Capacidad</b></td><td>{puertos} Puertos SC/APC</td></tr>
            <tr><td><b>Splitter</b></td><td>1:16 Balanceado PLC</td></tr>
            <tr><td><b>Potencia Rx</b></td><td>{pot}</td></tr>
            <tr><td><b>Coordenadas</b></td><td>({n['lat']}, {n['lon']})</td></tr>
          </table>
        ]]></description>
        <Point><coordinates>{n['lon']},{n['lat']},0</coordinates></Point>
      </Placemark>
"""
    kml += """    </Folder>
  </Document>
</kml>"""

    # Empaquetar en memoria como archivo ZIP (KMZ)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("doc.kml", kml.encode("utf-8"))
        z.writestr("files/Poste.png", poste_png_bytes)
        z.writestr("files/Camara doble.png", camara_png_bytes)

    return buf.getvalue()
