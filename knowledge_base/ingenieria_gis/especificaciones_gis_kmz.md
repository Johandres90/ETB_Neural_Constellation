# Base de Conocimiento - Ingeniería GIS & Diseño de Red (KMZ / KML)
AHOM FIBER IA CORP

## 1. Misión del Agente GIS y Especialidad Cartográfica
El Agente de Ingeniería GIS es el especialista de AHOM FIBER IA CORP responsable de la ingesta, decodificación, interpretación espacial y auditoría de archivos cartográficos en formato **.KMZ** (Keyhole Markup Language Zipped) y **.KML**.

Su propósito es traducir archivos geoespaciales de Google Earth, QGIS y AutoCAD Map en conocimiento operacional estructurado para la planificación de fibra óptica (FTTH/GPON), tendido troncal, análisis de factibilidad y soporte técnico.

---

## 2. Anatomía de un Archivo KMZ para Telecomunicaciones

Un archivo `.kmz` es un contenedor comprimido (ZIP) que alberga al menos un archivo `doc.kml` o `*.kml`, junto con posibles recursos gráficos (iconos de mufas, postes, NAPs, fotos de campo).

### Elementos Geoespaciales Clave:
1. **Placemarks de Punto (Coordinates: Lon, Lat, Alt):**
   - **NAPs (Network Access Points):** Cajas de dispersión óptica con splitters 1:8 o 1:16. Identifican capacidad instalada, puertos ocupados y puertos libres.
   - **Mufas de Empalme (FOSC):** Puntos de sangrado y empalme por fusión entre cables troncales y de distribución.
   - **Postería y Apoyos:** Postes de concreto o madera (8m, 10m, 12m) con indicación de vanos aéreos y retenidas.
   - **Cámaras / Pozos Subterráneos:** Cámaras de paso y cajas de inspección en ductería subterránea.
   - **Cabeceras OLT / Hubs / Centros de Cómputo:** Puntos de origen de la señal óptica hacia los anillos de transporte.

2. **Trazados Lineales (LineString / MultiLineString):**
   - **Tendido Troncal (Feeder Cable):** Cables de alta capacidad monomodo (96F, 144F, 288F).
   - **Red de Distribución:** Enlaces entre mufas de sangrado y cajas NAP (24F, 48F, 72F).
   - **Acometidas de Clientes (Drop Óptico):** Cable drop plano o redondo de 1 a 4 hilos (longitud máxima recomendada: 180 metros).
   - **Cálculo de Longitud:** Suma geodésica mediante fórmula de Haversine con adición de reservas técnicas de cable (15 a 20 metros por cámara o mufa).

3. **Zonas y Polígonos (Polygon / LinearRing):**
   - **Zonas de Cobertura Comercial:** Delimitación de barrios, comunas, zonas francas o parques industriales donde AHOM FIBER tiene red comercialmente activa.
   - **Distritos de Red (ODN Clusters):** Áreas alimentadas por un splitter primario o una tarjeta PON específica.

4. **Metadatos y Atributos (ExtendedData / SimpleData):**
   - Códigos de circuito, calibres de fibra (G.652.D / G.657.A2), atenuación medida en dB, fechas de instalación y contratistas responsables.

---

## 3. Protocolo de Diagnóstico y Consultas KMZ
Cuando un usuario consulta sobre un archivo KMZ cargado:
- **Resumen Cuantitativo Inmediato:** Total de metros/kilómetros de fibra, cantidad de NAPs, mufas, postes y cámaras detectadas.
- **Factibilidad por Coordenadas o Dirección:** Determina la distancia euclidiana/geodésica al NAP más cercano. Si la distancia es < 180m, se declara factibilidad técnica inmediata.
- **Topología de Red:** Explica el camino que sigue la fibra desde la OLT o cámara cabecera hasta el usuario final.
- **Auditoría Técnica:** Alerta si hay vanos de cable excesivamente largos (> 60 metros entre postes sin soporte) o pérdidas de continuidad.
