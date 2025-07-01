🏠 Control Inteligente de Focos
Sistema de control de focos inteligentes por voz usando OpenAI, Flask y Tuya API. Permite controlar dispositivos IoT mediante comandos de lenguaje natural.
✨ Características
🎤 Control por voz: Interpreta comandos en lenguaje natural usando OpenAI GPT
💡 Control completo: Enciende/apaga, cambia colores e intensidad
🌈 6 colores disponibles: Rojo, verde, azul, amarillo, rosado, violeta
📱 API REST: Endpoints para integración con aplicaciones
🔧 Tuya Integration: Compatible con dispositivos Tuya IoT
🔒 Configuración segura: Variables de entorno para credenciales

🚀 Instalación
Prerrequisitos

Python 3.7+
Cuenta OpenAI con API Key
Dispositivo Tuya compatible
Credenciales Tuya Developer

1. Clonar el repositorio
bashgit clone <tu-repositorio>
cd control-foco-inteligente
2. Crear entorno virtual
bashpython -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
3. Instalar dependencias
bashpip install -r requirements.txt
4. Configurar variables de entorno
bashcp .env.example .env
Edita el archivo .env con tus credenciales:
bash# OpenAI Configuration
OPENAI_API_KEY=sk-tu-api-key-de-openai

# Tuya API Configuration
TUYA_ACCESS_ID=tu-access-id
TUYA_ACCESS_KEY=tu-access-key
TUYA_DEVICE_ID=tu-device-id
TUYA_API_ENDPOINT=https://openapi.tuyaus.com
TUYA_MQ_ENDPOINT=wss://mqe.tuyaus.com:8285/

# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True
5. Ejecutar la aplicación
bashpython app.py
La aplicación estará disponible en http://localhost:5000
🔧 Configuración Tuya
Obtener credenciales Tuya

Registrarse en Tuya IoT Platform
Crear un nuevo proyecto Cloud Development
Obtener Access ID y Access Secret
Vincular tu dispositivo y obtener Device ID

Configurar dispositivo
Asegúrate de que tu foco inteligente esté:

Conectado a la app Tuya Smart
Vinculado a tu proyecto en Tuya IoT Platform
El Device ID coincida con el configurado

📡 API Endpoints
Control por comandos de voz
httpPOST /dialogflow
Content-Type: application/json

{
    "mensaje": "enciende la luz en azul al 80%"
}
Respuesta:
json{
    "respuesta": "Configurando luz azul al 80%",
    "accion": "modificar_completo",
    "estado": true
}
Control directo
Estado del foco
httpGET /foco/estado
Encender foco
httpPOST /foco/encender
Apagar foco
httpPOST /foco/apagar
🎯 Ejemplos de comandos
Comandos básicos

"enciende la luz"
"apaga el foco"
"prende la lámpara"

Control de color

"ponla en azul"
"cámbiala a rojo"
"quiero color verde"

Control de intensidad

"bájala al 50%"
"ponla al máximo"
"intensidad al 25%"

Comandos combinados

"enciende la luz roja al 80%"
"ponla azul y bájala al 30%"
"luz amarilla suave"

🌈 Colores disponibles
ColorValor HSVRojo0°Verde120°Azul240°Amarillo60°Rosado330°Violeta270°
📁 Estructura del proyecto
control-foco-inteligente/
├── app.py                 # Aplicación principal Flask
├── requirements.txt       # Dependencias Python
├── .env                  # Variables de entorno (no incluir en git)
├── .env.example          # Plantilla de configuración
├── .gitignore           # Archivos a ignorar en git
└── README.md            # Documentación
🔍 Funciones principales
procesar_con_openai(texto)
Interpreta comandos de voz usando OpenAI GPT-3.5-turbo y extrae:

Acción a realizar
Color deseado
Intensidad de brillo
Genera respuesta amigable

controlar_foco_real(encender, color, intensidad)
Ejecuta comandos en el dispositivo Tuya:

Maneja modo color y modo blanco
Ajusta brillo e intensidad
Envía comandos a la API Tuya

🛠️ Troubleshooting
Error: "No se pudo conectar a Tuya"

Verifica credenciales Tuya en .env
Confirma que el dispositivo esté online
Revisa permisos del proyecto en Tuya IoT Platform

Error: "OpenAI API error"

Verifica tu API Key de OpenAI
Confirma que tienes créditos disponibles
Revisa límites de rate limiting

Error: "Device not responding"

Confirma que el DEVICE_ID sea correcto
Verifica conexión WiFi del dispositivo
Reinicia el dispositivo si es necesario

Logs de debugging
La aplicación muestra logs detallados:
🤖 Respuesta OpenAI: {"accion": "encender", ...}
📤 Enviando comandos a Tuya: [{"code": "switch_led", "value": true}]
🔧 Tuya API response: {"success": true}
📊 Monitoreo
Estado de la aplicación
bashcurl http://localhost:5000/foco/estado