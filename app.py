from flask import Flask, request, jsonify
from tuya_connector import TuyaOpenAPI
import openai
import os
import uuid
import requests
import time
import hashlib
import hmac
import json
import re
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)

# Configuración OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configuración Tuya (mantiene tu configuración actual)
API_ENDPOINT = os.getenv("TUYA_API_ENDPOINT")
MQ_ENDPOINT = os.getenv("TUYA_MQ_ENDPOINT")

ACCESS_ID = os.getenv("TUYA_ACCESS_ID")
ACCESS_KEY = os.getenv("TUYA_ACCESS_KEY")
DEVICE_ID = os.getenv("TUYA_DEVICE_ID")

estado_foco = {
    "encendido": False,
    "color": None,  # p.ej. "azul"
    "intensidad": 100,  # porcentaje 1-100
}

openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
openapi.connect()

COLOR_MAP = {
    "rojo": 0,
    "verde": 120,
    "azul": 240,
    "amarillo": 60,
    "rosado": 330,
    "violeta": 270,
}


def controlar_foco_real(encender=None, color=None, intensidad=None):
    comandos = []

    # Actualizar estado si viene color/intensidad nuevos
    if color:
        estado_foco["color"] = color

    if intensidad is not None:
        try:
            intensidad = int(intensidad)
            intensidad = max(1, min(100, intensidad))
            estado_foco["intensidad"] = intensidad
        except:
            pass

    # Si hay color en estado, mandar modo color y color_data con brillo actual
    if estado_foco["color"]:
        comandos.append({"code": "work_mode", "value": "colour"})
        hue = COLOR_MAP.get(estado_foco["color"], 0)
        brillo_tuya = int((estado_foco["intensidad"] / 100) * 1000)
        comandos.append(
            {"code": "colour_data_v2", "value": {"h": hue, "s": 1000, "v": brillo_tuya}}
        )
    else:
        # Si no hay color (modo blanco), mandar solo brillo con bright_value_v2
        brillo_tuya = int((estado_foco["intensidad"] / 100) * 1000)
        comandos.append({"code": "bright_value_v2", "value": brillo_tuya})

    # Comando switch_led si viene
    if encender is not None:
        comandos.append({"code": "switch_led", "value": encender})
        estado_foco["encendido"] = encender

    if not comandos:
        print("⚠️ No hay comandos para enviar a Tuya.")
        return False

    print("📤 Enviando comandos a Tuya:", comandos)

    try:
        response = openapi.post(
            f"/v1.0/iot-03/devices/{DEVICE_ID}/commands", {"commands": comandos}
        )
        print("🔧 Tuya API response:", response)
        return response.get("success", False)
    except Exception as e:
        print("❌ Error enviando comando a Tuya:", e)
        return False


def procesar_con_openai(texto):
    """
    Usa OpenAI para interpretar el comando de voz y extraer parámetros
    """
    prompt = f"""
Eres un asistente que interpreta comandos de voz para controlar un foco inteligente.
Analiza el siguiente texto y extrae la información relevante.

Texto: "{texto}"

Responde SOLO con un JSON válido con la siguiente estructura:
{{
    "accion": "una de: encender, apagar, modificar_color, modificar_intensidad, modificar_completo",
    "color": "uno de: rojo, verde, azul, amarillo, rosado, violeta, o null si no se menciona",
    "intensidad": "número del 1 al 100, o null si no se menciona",
    "respuesta": "una respuesta amigable confirmando la acción"
}}

Ejemplos:
- "enciende la luz" → {{"accion": "encender", "color": null, "intensidad": null, "respuesta": "Encendiendo la luz"}}
- "ponla en azul" → {{"accion": "modificar_color", "color": "azul", "intensidad": null, "respuesta": "Cambiando color a azul"}}
- "bájala al 50%" → {{"accion": "modificar_intensidad", "color": null, "intensidad": 50, "respuesta": "Ajustando intensidad al 50%"}}
- "ponla roja al 80%" → {{"accion": "modificar_completo", "color": "rojo", "intensidad": 80, "respuesta": "Configurando luz roja al 80%"}}

Analiza el texto y responde:
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un experto en interpretar comandos de voz para dispositivos inteligentes. Responde siempre con JSON válido.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=200,
        )

        resultado_texto = response.choices[0].message.content.strip()
        print(f"🤖 Respuesta OpenAI: {resultado_texto}")

        # Limpiar la respuesta para asegurar que sea JSON válido
        if "```json" in resultado_texto:
            resultado_texto = (
                resultado_texto.split("```json")[1].split("```")[0].strip()
            )
        elif "```" in resultado_texto:
            resultado_texto = resultado_texto.split("```")[1].strip()

        return json.loads(resultado_texto)

    except json.JSONDecodeError as e:
        print(f"❌ Error parseando JSON de OpenAI: {e}")
        return {
            "accion": "encender",
            "color": None,
            "intensidad": None,
            "respuesta": "No pude entender el comando, pero encenderé la luz",
        }
    except Exception as e:
        print(f"❌ Error con OpenAI API: {e}")
        return {
            "accion": "encender",
            "color": None,
            "intensidad": None,
            "respuesta": "Hubo un error, pero encenderé la luz",
        }


@app.route("/dialogflow", methods=["POST"])
def procesar_texto():
    data = request.get_json()
    texto = data.get("mensaje", "")

    if not texto:
        return jsonify({"error": "No se recibió ningún mensaje"}), 400

    try:
        # Usar OpenAI en lugar de Dialogflow
        resultado = procesar_con_openai(texto)

        action = resultado.get("accion")
        color = resultado.get("color")
        intensidad = resultado.get("intensidad")
        fulfillment_text = resultado.get("respuesta")

        print(f"DEBUG => acción: {action}, color: {color}, intensidad: {intensidad}")

        encender = None

        if action in ["encender", "luces.encender"]:
            encender = True
            estado_foco["encendido"] = True

        elif action in ["apagar", "luces.apagar"]:
            encender = False
            estado_foco["encendido"] = False

        elif action == "modificar_intensidad":
            encender = True
            estado_foco["encendido"] = True

        elif action == "modificar_color":
            encender = True
            estado_foco["encendido"] = True

        elif action == "modificar_completo":
            encender = True
            estado_foco["encendido"] = True

        print(
            f"DEBUG => acción: {action}, color: {color}, intensidad: {intensidad}, encender: {encender}"
        )
        controlar_foco_real(encender=encender, color=color, intensidad=intensidad)

        return jsonify(
            {
                "respuesta": fulfillment_text,
                "accion": action,
                "estado": estado_foco["encendido"],
            }
        )

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": "No se pudo procesar el comando"}), 500


@app.route("/foco/estado", methods=["GET"])
def estado():
    return jsonify({"encendido": estado_foco["encendido"]})


@app.route("/foco/encender", methods=["POST"])
def encender():
    estado_foco["encendido"] = True
    controlar_foco_real(encender=True)
    return jsonify({"mensaje": "Foco encendido", "encendido": True})


@app.route("/foco/apagar", methods=["POST"])
def apagar():
    estado_foco["encendido"] = False
    controlar_foco_real(encender=False)
    return jsonify({"mensaje": "Foco apagado", "encendido": False})


if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", 5000)),
        debug=os.getenv("FLASK_DEBUG", "True").lower() == "true",
    )
