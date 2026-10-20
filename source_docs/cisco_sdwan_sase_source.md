# Documentación Técnica Oficial: Integración de Cisco Catalyst SD-WAN con Cisco Secure Access (Túneles SASE)

## 1. Resumen Arquitectónico
La integración de **Cisco Catalyst SD-WAN** (administrado desde **Cisco Catalyst SD-WAN Manager**, anteriormente vManage) con **Cisco Secure Access** permite conectar sucursales remotas (*Branch Sites*) hacia la nube de seguridad SSE mediante túneles **IPSec IKEv2** automatizados o manuales, formando una arquitectura **SASE (Secure Access Service Edge)** completa.

## 2. Componentes Clave
- **Cisco Catalyst SD-WAN Manager (vManage)**: Orquestador central que despliega plantillas de características (*Feature Templates* / *Configuration Groups*) hacia los routers de borde.
- **Cisco Catalyst SD-WAN Edge (IOS-XE)**: Routers de sucursal que establecen túneles IPSec activos/pasivos hacia los centros de datos regionales de **Cisco Secure Access** (*Network Tunnel Groups*).
- **IPSec IKEv2 con FQDN PSK**: Protocolo de autenticación utilizado para identificar cada túnel de sucursal ante la nube de Cisco Secure Access.

## 3. Prerrequisitos Técnicos Obligatorios
1. **Suscripción activa a Cisco Secure Access** con licenciamiento para *Network Tunnel Groups*.
2. **Conectividad en la VPN de Transporte (`VPN 0` / Transport WAN)**: La interfaz física de salida a Internet en el router SD-WAN Edge debe tener alcanzabilidad UDP 500 y UDP 4500 hacia las IPs de los hubs de Cisco Secure Access.
3. **Formato de Identidad IKEv2 (FQDN)**: El identificador local IKE (`IKE Local ID`) configurado en el router SD-WAN debe coincidir exactamente con el formato FQDN generado en el portal de Cisco Secure Access (por ejemplo: `sucursal01@id-org-tunel.sse.cisco.com`).

## 4. Errores Comunes de Configuración (Misconfigurations)
- **Error #1 — Desajuste de IKE ID / PSK**: Configurar la dirección IP pública de la sucursal como identificador IKE en lugar del string FQDN de Cisco Secure Access provoca que la Fase 1 de IKEv2 falle con `AUTH_FAILED`.
- **Error #2 — Asimetría de MTU y MSS Clamping**: No configurar `ip tcp adjust-mss 1360` y `ip mtu 1400` en la interfaz `Tunnel` IPSec provoca que las sesiones TLS pesadas (como portales SaaS o descargas de actualizaciones) se congelen por fragmentación de paquetes descartados.
- **Error #3 — Enrutamiento de Service VPN sin NAT/DIA adecuado**: Redirigir todo el tráfico de la VPN de Servicio (`VPN 10`) al túnel SASE sin habilitar *Dead Peer Detection (DPD)* deja a la sucursal sin salida a Internet si el túnel primario cae y no conmuta al secundario.

## 5. Estrategia Recomendada de Despliegue
1. **Fase 1 (Sitio Piloto con ECMP / Redundancia)**: Configurar un `Network Tunnel Group` con túneles primario y secundario hacia dos centros de datos distintos de Cisco Secure Access y validar el estado `UP/UP` de IKEv2 e IPSec.
2. **Fase 2 (Política de Tráfico Selectiva - AAR)**: Utilizar *Application-Aware Routing (AAR)* en SD-WAN para enviar primero solo una subred de prueba hacia el túnel SASE, verificando que `ip tcp adjust-mss 1360` esté activo.
3. **Fase 3 (Despliegue Masivo por Plantilla)**: Una vez validado el rendimiento y la conmutación por error (DPD), aplicar el *Configuration Group* a todas las sucursales de producción.
