from flask import Flask, render_template, request, jsonify, session
from ia2 import IAPro
import os

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static"),
)
app.secret_key = os.environ.get("SECRET_KEY", "trackito_secret_2024_xk9")

# IAPro es stateless: solo necesita el modelo ML y Gemini, no guarda sesiones
_ia_instance = None

def get_ia():
    global _ia_instance
    if _ia_instance is None:
        _ia_instance = IAPro()
    return _ia_instance


@app.route("/")
def inicio():
    # Inicializar sesión vacía si no existe
    if "chat_state" not in session:
        session["chat_state"] = {"flujo": "nombre", "paso": "nombre", "datos": {}}
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    if not data or "mensaje" not in data:
        return jsonify({"error": "Falta el campo 'mensaje'"}), 400

    mensaje = data["mensaje"].strip()
    ia      = get_ia()

    # Inicio de conversación — solo inicializar estado y saludar
    if mensaje == "__inicio__":
        estado = ia.sesion_nueva()
        session["chat_state"] = estado
        return jsonify({"respuesta": "¡Hola! Soy Trackito, tu asistente de hábitos ⚡ ¿Cómo te llamas?"})

    # Leer estado desde la cookie, crear uno nuevo si no existe
    estado = session.get("chat_state")
    if not estado:
        estado = ia.sesion_nueva()

    # Comando de reinicio
    if mensaje.lower() in ("reiniciar", "reset", "nuevo", "restart"):
        respuesta, estado = ia.reiniciar(estado)
        session["chat_state"] = estado
        return jsonify({"respuesta": respuesta})

    # Procesar mensaje normal
    respuesta, estado = ia.responder(estado, mensaje)
    session["chat_state"] = estado
    session.modified = True

    return jsonify({"respuesta": respuesta})


@app.route("/api/reset", methods=["POST"])
def reset():
    ia = get_ia()
    estado = session.get("chat_state", ia.sesion_nueva())
    respuesta, estado = ia.reiniciar(estado)
    session["chat_state"] = estado
    return jsonify({"respuesta": respuesta})


@app.route("/api/status")
def status():
    ia = get_ia()
    test_error = None
    test_ok = False
    if ia.gemini.disponible:
        try:
            r = ia.gemini._llamar_chat("Di solo: OK", "test", "FAIL")
            test_ok = r != "FAIL"
        except Exception as e:
            test_error = str(e)[:120]
    return jsonify({
        "groq_disponible": ia.gemini.disponible,
        "test_ok": test_ok,
        "test_error": test_error,
        "modelo": ia.gemini.MODELO,
    })


if __name__ == "__main__":
    app.run(debug=True)
