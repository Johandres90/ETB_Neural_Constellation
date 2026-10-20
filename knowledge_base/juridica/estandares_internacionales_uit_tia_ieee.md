# COMPENDIO DE ESTÁNDARES INTERNACIONALES DE TELECOMUNICACIONES E INFRAESTRUCTURA
**UIT / ITU · ANSI/TIA · IEEE · IETF · Uptime Institute · NIST · GDPR**
**AHOM FIBER IA CORP — Dirección Jurídica, Auditoría Líder ISO/UIT & Oficial de Cumplimiento (CCISO)**

---

## 1. UNIÓN INTERNACIONAL DE TELECOMUNICACIONES (UIT / ITU)

### 1.1. Sector ITU-T (Estandarización de Telecomunicaciones)

| Estándar ITU-T | Descripción Técnica | Aplicación en AHOM FIBER IA CORP |
| :--- | :--- | :--- |
| **ITU-T G.652.D** | Fibra óptica monomodo estándar sin pico de agua (Low Water Peak) | Despliegue en redes de transporte y distribución metropolitana (atenuación <= 0.35 dB/km @ 1310nm y <= 0.21 dB/km @ 1550nm). |
| **ITU-T G.655** | Fibra con dispersión desplazada no nula (NZDSF) | Empleada en enlaces DWDM troncales de larga distancia para mitigar efectos no lineales (FWM, XPM, SPM). |
| **ITU-T G.657 (A1/A2)** | Fibra monomodo insensible a macrocurvaturas | Acometidas de última milla FTTH en edificios y ducterías estrechas (radio de curvatura mínimo de 7.5 mm sin pérdida de señal). |
| **ITU-T G.984.x** | Redes Ópticas Pasivas con Capacidad de Gigabit (GPON) | Arquitectura punto a multipunto con splitters ópticos pasivos (2.488 Gbps bajada / 1.244 Gbps subida). |
| **ITU-T G.9807.1** | Redes Ópticas Pasivas XGS-PON a 10 Gigabit Simétricas | Enlaces corporativos dedicados simétricos de 10 Gbps sobre la misma infraestructura de fibra existente en coexistencia WDM. |
| **ITU-T G.694.1** | Grilla de frecuencias espectrales para DWDM | Espaciamiento de canal de 50 GHz y 100 GHz en la banda C (1530 nm - 1565 nm) para transporte multicanal de 100G/400G por hilo. |
| **Recomendación X.805** | Arquitectura de seguridad integral para sistemas que proveen comunicaciones de extremo a extremo | Define 8 dimensiones de seguridad (Control de acceso, Autenticación, No repudio, Confidencialidad, Integridad, Disponibilidad, Privacidad, Auditoría) en 3 planos (Gestión, Control y Usuario). |

### 1.2. Sector ITU-R (Radiocomunicaciones)
- Coordinación internacional de frecuencias y tratados de radiocomunicaciones para evitar interferencias en enlaces transfronterizos y satelitales.

---

## 2. ESTÁNDARES DE DATA CENTERS Y CABLEADO (ANSI/TIA & UPTIME INSTITUTE)

### 2.1. Clasificación de Data Centers (ANSI/TIA-942 & Uptime Institute)

| Nivel de Tier | Disponibilidad Anual | Arquitectura Eléctrica y Mecánica | Concurrencia Mantenible | Impacto Operativo en Mantenimiento |
| :--- | :---: | :---: | :---: | :--- |
| **Tier I** | 99.671% (28.8 h caída/año) | Ruta única sin componentes redundantes (N) | No | Requiere apagado total para mantenimiento preventivo. |
| **Tier II** | 99.741% (22.7 h caída/año) | Ruta única con componentes redundantes (N+1) | No | Mantenimiento de rutas críticas requiere paradas programadas. |
| **Tier III** | **99.982% (1.6 h caída/año)** | **Múltiples rutas activas/pasivas (N+1 o 2N)** | **SÍ (Concurrente Mantenible)** | **Cero interrupciones:** Cualquier componente puede ser reparado o reemplazado sin afectar la carga de TI activa. |
| **Tier IV** | 99.995% (0.4 h caída/año) | Rutas independientes activas y tolerantes a fallos (2N+1) | SÍ (Tolerancia a Fallas) | Soporta fallos catastróficos automáticos sin impacto en la carga. |

*AHOM FIBER IA CORP opera los Data Centers **Alma** (Suba) y **Prado** (Puente Aranda) bajo certificación de diseño y facilidad **Tier III**.*

### 2.2. Estándares de Planta Externa y Cableado Estructurado
- **ANSI/TIA-568:** Cableado estructurado para edificios comerciales (Categorías 6A, 7A y fibra óptica multimodo OM4/OM5 y monomodo OS2).
- **ANSI/TIA-758:** Estándar de Planta Externa de Telecomunicaciones (Customer-Owned Outside Plant - OSP) para diseño de ductos, cámaras subterráneas y tendidos aéreos.
- **ANSI/TIA-606:** Estándar de administración, etiquetado y registros de infraestructura de telecomunicaciones (codificación de cables, bandejas ODF y enlaces).

---

## 3. MARCOS GLOBALES DE REDES, CIBERSEGURIDAD Y PRIVACIDAD

### 3.1. IEEE (Institute of Electrical and Electronics Engineers)
- **IEEE 802.3:** Familia de estándares Ethernet sobre par trenzado y fibra óptica:
  * 10GBASE-LR (10 Gbps monomodo hasta 10 km).
  * 40GBASE-LR4 y 100GBASE-LR4 (transporte óptico en 4 longitudes de onda WDM).
  * 400GBASE-FR4 para interconexión de centros de datos de última generación.
- **IEEE 802.1Q:** Etiquetado de VLANs (Virtual LANs) y priorización de tráfico (QoS 802.1p) para garantizar baja latencia en voz y video.

### 3.2. IETF (Internet Engineering Task Force) — Protocolos Troncales
- **RFC 4271 (BGP-4):** Protocolo de enrutamiento dinámico exterior con validación de seguridad RPKI.
- **RFC 5340 (OSPFv3):** Protocolo de enrutamiento interior para redes IPv4 e IPv6.
- **RFC 3031 (MPLS):** Conmutación de etiquetas multiprotocolo para ingeniería de tráfico y VPNs corporativas L2/L3.
- **RFC 8200 (IPv6):** Protocolo de Internet versión 6 nativo con direccionamiento global dual-stack.
- **RFC 8446 (TLS 1.3):** Cifrado seguro de transporte con secreto perfecto hacia adelante (PFS) y eliminación de algoritmos obsoletos.

### 3.3. Marcos Internacionales de Privacidad y Ciberseguridad
- **GDPR (Reglamento General de Protección de Datos de la UE):**
  * Cumplimiento estricto en el tratamiento de datos de empresas multinacionales con sede en la Unión Europea.
  * Cláusulas contractuales tipo (SCC) para transferencias internacionales de datos.
- **NIST Cybersecurity Framework 2.0 (CSF):**
  * 6 funciones núcleo: **Gobernar (GV), Identificar (ID), Proteger (PR), Detectar (DE), Responder (RS) y Recuperar (RC)**.
- **PCI-DSS v4.0 (Payment Card Industry Data Security Standard):**
  * Cumplimiento obligatorio en redes que procesan transacciones financieras, pasarelas de pago y facturación en línea.
- **Controles CIS v8 & OWASP Top 10:**
  * Mitigación de vulnerabilidades web, prevención de inyecciones y endurecimiento (hardening) de servidores y equipos de red.
