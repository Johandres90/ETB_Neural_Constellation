# Base de Conocimiento - Regulación Financiera SFC (Superintendencia Financiera de Colombia)
## Requerimientos de Ciberseguridad, Riesgo Operativo y Cloud Computing para Clientes Bancarios y Fintech

Este compendio normativo regula la prestación de servicios de telecomunicaciones, enlaces dedicados MPLS/DWDM, colocation e infraestructura en la Nube (IaaS/PaaS) suministrados por **AHOM FIBER IA CORP** a entidades vigiladas por la **Superintendencia Financiera de Colombia (SFC)** (Bancos, Fiduciarias, Comisionistas de Bolsa, Compañías de Financiamiento y Fintechs).

---

## 1. Circular Externa 029 de 2014 (SFC)
### Reforma a la Circular Básica Jurídica (Parte I, Título II, Capítulo I)
**Objeto:** Requerimientos mínimos de seguridad y calidad en la realización de operaciones financieras a través de canales de distribución y redes de telecomunicaciones.

### Requerimientos Técnicos y Cumplimiento de AHOM FIBER IA CORP:
- **Cifrado Fuerte de Extremo a Extremo:** Enlaces dedicados de fibra óptica y canales L2/L3 con soporte de cifrado por hardware (MACsec / IPsec AES-256) y TLS 1.3 en capas superiores.
- **Trazabilidad y Registros de Auditoría Inalterables:** Registro de logs de tráfico (NetFlow/IPFIX, syslog centralizado en SIEM) con marcas de tiempo sincronizadas mediante servidores de tiempo certificados NTP Estrato 1, conservados por un mínimo legal de 5 años.
- **Seguridad en Infraestructura Tercerizada (Data Centers Tier III):**
  - **Acceso Físico Riguroso:** Siete perímetros de control de acceso biométrico (reconocimiento facial e iris), exclusclusas antimanpass y CCTV de alta resolución con retención de grabaciones superior a 90 días en los Data Centers Alma y Prado.
  - **Segregación Lógica de Redes:** Aislamiento total de tráfico financiero mediante VRF (Virtual Routing and Forwarding), VLANs dedicadas IEEE 802.1Q y túneles MPLS no compartidos con tráfico residencial.
- **Disponibilidad y Tolerancia a Fallos:** Enlaces primarios y de respaldo 100% simétricos por rutas físicas totalmente disyuntas (diversidad de ductería y cámaras subterráneas) con conmutación automática en menos de 50 milisegundos.

---

## 2. Circular Externa 007 de 2018 (SFC)
### Requerimientos Mínimos para la Gestión de Riesgos de Ciberseguridad
**Objeto:** Marco integral de gobernanza, prevención, detección, respuesta y recuperación ante amenazas y ataques cibernéticos contra el sistema financiero.

### Requerimientos Técnicos y Cumplimiento de AHOM FIBER IA CORP:
- **Políticas de Ciber-Resiliencia:** Capacidad demostrada de anticipar, resistir, recuperarse y evolucionar ante ciberataques sofisticados dirigidos a la infraestructura de telecomunicaciones y hosting.
- **Monitoreo Continuo SOC/SIEM 24/7/365:**
  - Centro de Operaciones de Seguridad (SOC) dedicado con capacidades de detección automatizada (SOAR, EDR/XDR).
  - Mitigación volumétrica de ataques de Denegación de Servicio Distribuido (Anti-DDoS) con capacidad de depuración (Scrubbing Centers) superior a 2.5 Tbps en borde nacional e internacional.
- **Gestión Continua de Vulnerabilidades y Pruebas de Efectividad:**
  - Escaneos periódicos de vulnerabilidades de red e infraestructura conforme a NIST SP 800-115.
  - Ejercicios de Ethical Hacking y Pentesting anuales ejecutados por firmas independientes acreditadas internacionalmente (CREST / OSCP).
  - Pruebas de ingeniería social y evaluación de configuraciones de seguridad (CIS Benchmarks).
- **Reporte de Incidentes al CSIRT Financiero y a la SFC:**
  - Procedimiento formalizado de notificación y escalamiento de incidentes graves de ciberseguridad a las entidades vigiladas en un plazo máximo de **2 horas**.
  - Articulación directa con el CSIRT Financiero de Asobancaria y el Grupo de Respuesta a Emergencias Cibernéticas de Colombia (ColCERT).

---

## 3. Circular Externa 033 de 2020 (SFC)
### Gestión del Riesgo de Ciberseguridad, Computación en la Nube (Cloud Computing) y Resiliencia Operacional
**Objeto:** Regulación vinculante para la contratación y provisión de servicios en la Nube (IaaS, PaaS, SaaS) e infraestructura de misión crítica para el sector financiero.

### Requerimientos Técnicos y Cumplimiento de AHOM FIBER IA CORP:
- **Derecho de Inspección y Auditabilidad de la SFC (Audit Rights):**
  - AHOM FIBER IA CORP garantiza por contrato el **acceso irrestricto** para inspecciones físicas, técnicas y forenses por parte de los auditores internos de la entidad vigilada, auditores externos y funcionarios delegados de la Superintendencia Financiera de Colombia (SFC).
- **Soberanía y Ubicación de los Datos:**
  - Almacenamiento y procesamiento garantizado dentro del territorio nacional en los Data Centers Alma y Prado (Bogotá D.C. y Sabana), cumpliendo las normas de extraterritorialidad y privacidad en caso de nube híbrida.
- **Acuerdos de Nivel de Servicio (SLA) & Continuidad Operacional:**
  - Disponibilidad garantizada de infraestructura del **99.982%** (Certificación ANSI/TIA-942 Tier III).
  - Planes de Continuidad de Negocio (BCP) y Recuperación ante Desastres (DRP) alineados con **ISO 22301**.
  - Tiempos de recuperación objetivos: **RPO = 0** (Cero pérdida transaccional mediante replicación sincrónica DWDM) y **RTO < 15 minutos**.
- **Segregación de Ambientes Multi-Tenant:**
  - Aislamiento criptográfico y de cómputo para prevenir fugas de información entre co-inquilinos mediante microsegmentación Zero Trust, cifrado granular por cliente y HSM (Hardware Security Modules) certificados FIPS 140-2 Nivel 3.
- **Reversibilidad del Servicio y Salida Segura (Exit Strategy):**
  - Procedimientos documentados y ensayados contractualmente para la portabilidad integral de datos y máquinas virtuales sin bloqueo de proveedor (*no vendor lock-in*).
  - Borrado seguro y sanitización de medios de almacenamiento magnético y de estado sólido según el estándar **NIST SP 800-88 Rev. 1 (Purge/Destroy)** al finalizar el contrato o servicio.

---

## 4. Matriz de Mapeo Normativo: SFC vs. Controles Internacionales

| Regulación SFC | Requisito Principal | Control ISO/IEC 27001:2022 | Marco NIST CSF 2.0 | Solución AHOM FIBER IA CORP |
| :--- | :--- | :--- | :--- | :--- |
| **CE 029/2014** | Cifrado en redes de datos | A.8.24 (Criptografía) | PR.DS-01, PR.DS-02 | Canales ópticos DWDM con cifrado AES-256 en capa física y TLS 1.3 |
| **CE 029/2014** | Control de acceso físico a Data Centers | A.7.1 a A.7.4 (Perímetros y áreas seguras) | PR.AA-05 | 7 perímetros de biometría, CCTV analítico, Data Centers Tier III Alma y Prado |
| **CE 007/2018** | Monitoreo continuo y SOC 24/7 | A.8.16 (Monitoreo de actividades) | DE.CM-01, DE.AE-02 | SOC/SIEM 24/7 con IA predictiva y plataforma Anti-DDoS de 2.5 Tbps |
| **CE 007/2018** | Ethical Hacking & Pentesting | A.8.8 (Gestión de vulnerabilidades técnicas) | ID.RA-01, PR.IP-12 | Pruebas semestrales de intrusión y auditorías de código seguro |
| **CE 007/2018** | Notificación al CSIRT Financiero | A.5.24 a A.5.28 (Gestión de incidentes) | RS.MA-01, RS.CO-02 | Procedimiento de notificación en < 2 horas al CSIRT Financiero y SFC |
| **CE 033/2020** | Auditabilidad plena por la SFC | A.5.36 (Conformidad con políticas y normas) | GV.OV-01, GV.SC-05 | Cláusula contractual abierta de derecho de inspección física y lógica por la SFC |
| **CE 033/2020** | Resiliencia de Nube y DRP | A.8.14 (Redundancia de servicios TIC) | RC.RP-01, PR.IR-01 | Arquitectura activo-activo metro-mirror, Tier III (99.982%), RPO = 0, RTO < 15 min |
| **CE 033/2020** | Borrado seguro (Exit Strategy) | A.8.10 (Eliminación segura de información) | PR.DS-03 | Protocolo de borrado seguro certificado NIST SP 800-88 Rev. 1 |
