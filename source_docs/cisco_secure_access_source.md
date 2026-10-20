# Documentación Técnica Oficial: Cisco Secure Access (SSE) — Gobernanza de IA Generativa y DLP AI Guardrails

## 1. Resumen del Producto y Arquitectura
**Cisco Secure Access** es la solución convergente de *Security Service Edge (SSE)* en la nube de Cisco. Integra capacidades de Secure Web Gateway (SWG), Cloud Access Security Broker (CASB), Zero Trust Network Access (ZTNA) y Data Loss Prevention (DLP) en línea dentro de un único panel de administración.

Para gobernar el uso de herramientas de Inteligencia Artificial Generativa (GenAI) en la empresa y prevenir la fuga de datos por **Shadow AI** (empleados que utilizan herramientas de IA públicas no aprobadas por TI), Cisco Secure Access utiliza dos módulos principales:
- **AI Access** (Descubrimiento y Perfilado de Riesgo de Aplicaciones GenAI).
- **Data Loss Prevention (DLP) con reglas `AI Guardrails`** (Inspección en línea de contenido y prevención de exfiltración).

## 2. Descubrimiento de Shadow AI (`AI Access`)
El panel **AI Access** detecta automáticamente qué aplicaciones de IA Generativa están utilizando los usuarios en toda la organización (por ejemplo, asistentes de código, chatbots públicos, herramientas de resumen de documentos).
- Clasifica cada aplicación según su índice de riesgo empresarial (retención de datos para entrenamiento del proveedor, postura de privacidad, cumplimiento normativo).
- Permite distinguir entre herramientas corporativas aprobadas (*Sanctioned AI*) y aplicaciones no aprobadas (*Shadow AI*).

## 3. Prerrequisito Técnico Obligatorio: Inspección HTTPS (`HTTPS Inspection`)
Las interacciones con plataformas de IA Generativa (prompts de texto, respuestas del modelo y carga de archivos) viajan cifradas mediante sesiones TLS/HTTPS.
- **Requisito Crítico**: Para que el motor DLP y las reglas `AI Guardrails` puedan inspeccionar el contenido de un prompt o archivo subido, **la inspección HTTPS (descifrado TLS) DEBE estar habilitada en la regla de la Política de Acceso (`Access Policy`) correspondiente**.
- **Error Común de Configuración (Misconfiguration)**: Si un ingeniero crea una regla DLP `AI Guardrails` pero olvida habilitar el descifrado HTTPS en la política de acceso para el grupo de usuarios o categoría de aplicaciones GenAI, el motor DLP solo verá el encabezado TLS cifrado. La regla DLP tendrá **cero coincidencias (0 hits)** porque nunca podrá leer el texto del prompt.
- Además, si la Política de Acceso bloquea por completo la aplicación a nivel de URL/Categoría antes de llegar al motor DLP, el tráfico se corta de inmediato y no queda sesión para inspeccionar a nivel de prompt.

## 4. Clasificación y Control en Línea (`AI Guardrails` en Políticas DLP)
Dentro de la política **Data Loss Prevention (DLP)**, los administradores configuran una regla de tipo **`AI Guardrails`**:
- **Alcance de Inspección**: Inspecciona en tiempo real **prompts enviados por el usuario, respuestas devueltas por el modelo de IA y cargas de archivos (file uploads)**.
- **Clasificadores Integrados**: Detecta código fuente propietario (*Source Code*), credenciales/claves API, datos personales (PII), información financiera y propiedad intelectual más allá de simples expresiones regulares (regex).
- **Acciones Disponibles**:
  - `Monitor` (Monitorear): Registra el evento y el fragmento detectado en los logs de seguridad sin interrumpir al usuario.
  - `Block` (Bloquear): Intercepta y bloquea el envío del prompt o archivo que contiene datos sensibles.

## 5. Estrategia Recomendada de Despliegue (Rollout Strategy)
Cisco recomienda una implementación gradual en **5 pasos**: **Descubrir (`Discover`), Descifrar (`Decrypt`), Clasificar (`Classify`), Controlar (`Enforce`) y Refinar (`Refine`)**:
1. **Evitar el bloqueo masivo inicial**: Bloquear toda la categoría de aplicaciones de IA de golpe interrumpe flujos de trabajo legítimos (como asistentes de código aprobados antes de una entrega) y empuja a los empleados a usar dispositivos personales o redes móviles fuera del control corporativo.
2. **Iniciar en modo `Monitor`**: Desplegar la regla `AI Guardrails` primero con la acción **`Monitor`** durante 1 a 2 semanas para establecer una línea base de uso real (*baseline*).
3. **Ajustar falsos positivos y pasar a `Block`**: Analizar los eventos registrados, excluir falsos positivos y finalmente cambiar la acción a **`Block`** en las aplicaciones no aprobadas o clasificadores críticos con total confianza operativa.
