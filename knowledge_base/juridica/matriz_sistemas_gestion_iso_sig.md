# MATRIZ MAESTRA DE SISTEMAS DE GESTIÓN (ISO & SIG) EN TELECOMUNICACIONES
**AHOM FIBER IA CORP — Dirección Jurídica, Auditoría Líder ISO/UIT & Oficial de Cumplimiento (CCISO)**

---

## 1. ISO/IEC 27001:2022 — SISTEMA DE GESTIÓN DE SEGURIDAD DE LA INFORMACIÓN (SGSI)

AHOM FIBER IA CORP opera bajo un SGSI certificado bajo **ISO/IEC 27001:2022**, implementando los **93 controles del Anexo A** distribuidos en 4 dominios estratégicos:

| Categoría de Controles | N° Controles | Controles Críticos en Redes y Data Centers | Aplicación Operativa en AHOM FIBER IA CORP |
| :--- | :---: | :--- | :--- |
| **Organizacionales (A.5)** | **37** | A.5.1 a A.5.37: Políticas de seguridad, gestión de activos, control de acceso, relaciones con proveedores TIC y seguridad en servicios en la nube. | Custodia estricta de diagramas de empalme, inventarios de fibra OTDR, contratos de interconexión IP y auditoría de proveedores de fibra y hardware óptico. |
| **Personas (A.6)** | **8** | A.6.1 a A.6.8: Selección, acuerdos de confidencialidad (NDA), capacitación en ciberseguridad, trabajo remoto y reporte de incidentes. | Firma de NDA reforzado para personal de NOC, SOC y cuadrillas de planta externa; capacitaciones anti-phishing periódicas y control de acceso lógico. |
| **Físicos (A.7)** | **14** | A.7.1 a A.7.14: Perímetros de seguridad física, entrada física, salas de ODF, cableado estructurado, salas de UPS/baterías y destrucción de soportes. | 7 anillos de biometría en Data Centers Alma (Suba) y Prado (Puente Aranda); circuito cerrado CCTV 24/7 con IA de detección de intrusos; cerraduras electrónicas en cámaras subterráneas y gabinetes ODF. |
| **Tecnológicos (A.8)** | **34** | A.8.1 a A.8.34: Autenticación segura (MFA), gestión de privilegios, cifrado, prevención de fuga de datos (DLP), protección contra malware y segmentación de redes. | Aislamiento estricto de VLANs de gestión Out-of-Band (OOB); cifrado de transporte TLS 1.3 / IPsec IKEv2 en troncales; protección anti-DDoS volumétrica en BGP Core. |

---

## 2. NORMAS ESPECÍFICAS DE TELECOMUNICACIONES, PRIVACIDAD Y CONTINUIDAD

### 2.1. ISO/IEC 27011 (Seguridad en Telecomunicaciones — ITU-T X.1051)
- **Ámbito:** Guía de controles de seguridad de la información específica para organizaciones de telecomunicaciones basada en ISO/IEC 27002.
- **Plano de Control vs. Plano de Usuario:** Segmentación obligatoria del tráfico de señalización (SIP, Diameter, SS7, GMPLS) frente al tráfico de datos de los abonados.
- **Resiliencia de Conmutación:** Protección de protocolos de enrutamiento troncal (BGP RPKI para validación de origen de rutas, OSPFv3 con autenticación criptográfica).
- **Protección del Medio Físico:** Detección de atenuaciones súbitas en enlaces monomodo mediante reflectometría óptica proactiva (C-OTDR) para prevenir escuchas clandestinas por curvatura o pinchazo de fibra.

### 2.2. ISO/IEC 27701:2019 (PIMS — Gestión de Privacidad de la Información)
- Extensión de privacidad a ISO/IEC 27001 para actuar como **Responsable y Encargado del Tratamiento de Datos (PII Controller & Processor)**.
- Garantía de no reutilización de metadatos de tráfico (IPs de origen/destino, logs de sesión DNS, marcas de tiempo) para fines comerciales sin consentimiento previo.
- Integración nativa con la **Ley 1581 de 2012** (Colombia) y el **Reglamento General de Protección de Datos (GDPR)** de la Unión Europea.

### 2.3. ISO 22301:2019 (Continuidad del Negocio - BCMS) & DRP
- **BIA (Business Impact Analysis):** Evaluación de criticidad en anillos metropolitanos DWDM y Data Centers.
- **RTO (Recovery Time Objective):** Conmutación óptica autónoma sobre fibra oscura de respaldo en **< 50 milisegundos** (protección APS / sub-50ms en capa física DWDM).
- **RPO (Recovery Point Objective):** RPO = 0 en replicación síncrona metro-mirror entre Data Centers Alma y Prado (distancia de 16 km conectada por fibra dedicada 100G).
- **Respaldo Energético:** Sistema diésel con tanques de combustible in-situ certificados para **72+ horas continuas** de autonomía sin suministro de red comercial.

---

## 3. ARTICULACIÓN EXPERTA: \'NORMA 47001\' / GOBERNANZA DE IA, COMPLIANCE Y ANTISOBORNO

Cuando un usuario, auditor o cliente corporativo pregunta por la **\'Norma 47001\'** o **\'ISA 47001\'**, el Director Jurídico aclara y articula de inmediato la tríada de gobernanza avanzada de AHOM FIBER IA CORP:

1. **ISO/IEC 42001:2023 (Sistema de Gestión de Inteligencia Artificial - AIMS):**
   - Marco internacional que gobierna los agentes neuronales de AHOM FIBER IA CORP.
   - Garantiza auditoría de prompts, mitigación de alucinaciones, transparencia en decisiones operativas y preservación del principio de supervisión humana (Human-In-The-Loop).
2. **ISO 37301:2021 (Sistema de Gestión de Compliance):**
   - Asegura la debida diligencia legal, monitoreo de riesgos de no conformidad y cultura corporativa de cumplimiento ante la CRC, MinTIC, ANE y SIC.
3. **ISO 37001:2016 (Sistema de Gestión Antisoborno):**
   - Políticas de cero tolerancia al cohecho en procesos licitatorios del Estado (SECOP II), acuerdos de interconexión con operadores competidores y contratos con proveedores.
4. **ISO 45001:2018 (Seguridad y Salud en el Trabajo):**
   - Garantía de protección de las vidas de los linieros, técnicos de empalme y operadores de campo.

---

## 4. SISTEMA INTEGRADO DE GESTIÓN (SIG) — ESTRUCTURA DE ALTO NIVEL (HLS) Y CICLO PHVA

AHOM FIBER IA CORP integra bajo la **Estructura de Alto Nivel (HLS)** los estándares ISO 9001, ISO 14001 e ISO 45001:

### 4.1. ISO 9001:2015 — Calidad en Conectividad y SLA
- Compromiso contractual de disponibilidad del **99.985%** en enlaces dedicados.
- Medición continua de latencia (< 3.5 ms metropolitana), jitter (< 1.0 ms) y pérdida de paquetes (< 0.01%).
- Gestión de incidencias basada en ITIL v4 con cuadrillas motorizadas en sitio en < 4 horas.

### 4.2. ISO 14001:2015 — Gestión Ambiental & Sostenibilidad
- **Tendido Subterráneo Sostenible:** Permisos de intervención ambiental ante el IDU y corporaciones autónomas regionales (CAR).
- **Gestión Integral de RAEE:** Disposición final certificada de baterías VRLA de UPS, tarjetas electrónicas en desuso y tramos de fibra cortada según Decreto 284 de 2018.
- **Eficiencia Energética PUE:** Eficiencia en Data Centers con PUE <= 1.30 mediante pasillos fríos confinados y sistemas de enfriamiento evaporativo sin refrigerantes destructores de la capa de ozono.

### 4.3. ISO 45001:2018 — Seguridad y Salud en el Trabajo (SST)
- **Matriz IPERC:** Identificación de Peligros, Evaluación de Riesgos y Determinación de Controles en toda la planta externa e interna.
- **Trabajo en Alturas (Resolución 4272 de 2021):**
  * Certificación vigente de coordinador y trabajador autorizado en alturas para ascenso a postes de concreto y torres de telecomunicaciones.
  * Uso de EPP dieléctrico certificado ANSI Z359 (arnés en X, eslingas en Y con absorbedor de impacto, líneas de vida retráctiles).
- **Espacios Confinados (Resolución 0491 de 2020):**
  * Protocolo obligatorio para ingreso a cámaras subterráneas y ducterías de paso:
    1. Medición previa de atmósfera con detector de 4 gases (O2, CO, H2S, LEL inflamabilidad).
    2. Ventilación forzada continua durante toda la jornada.
    3. Vigía en superficie con trípode de rescate y sistema de poleas.
    4. Permiso de trabajo firmado por el supervisor SST.
- **Riesgo Óptico por Radiación Láser:**
  * Uso mandatorio de gafas de protección láser con densidad óptica (OD 5+) sintonizadas a 1310 nm, 1550 nm y banda C/L (DWDM).
  * Prohibición absoluta de mirar directamente al núcleo de conectores ópticos o ferrule sin microscopio de fibra con filtro infrarrojo.
