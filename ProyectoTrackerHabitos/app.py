from flask import Flask, render_template, request, jsonify, session
from ia2 import IAPro
import uuid
import os

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static"),
)
app.secret_key = os.environ.get("SECRET_KEY", "tracker_habitos_secret_key")

# Singleton: se inicializa una vez por proceso/worker
_ia_instance = None

def get_ia():
    global _ia_instance
    if _ia_instance is None:
        _ia_instance = IAPro()
    return _ia_instance


@app.route("/")
def inicio():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    if not data or "mensaje" not in data:
        return jsonify({"error": "Falta el campo 'mensaje'"}), 400

    session_id = session.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        session["session_id"] = session_id

    mensaje = data["mensaje"].strip()
    ia = get_ia()

    if mensaje.lower() in ("reiniciar", "reset", "nuevo", "restart"):
        respuesta = ia.reiniciar(session_id)
    else:
        respuesta = ia.responder(session_id, mensaje)

    return jsonify({"respuesta": respuesta})


@app.route("/api/reset", methods=["POST"])
def reset():
    session_id = session.get("session_id", str(uuid.uuid4()))
    session["session_id"] = session_id
    respuesta = get_ia().reiniciar(session_id)
    return jsonify({"respuesta": respuesta})


@app.route("/api/debug")
def debug():
    """Endpoint temporal para diagnosticar Gemini en Vercel."""
    import os
    key = os.getenv("GEMINI_API_KEY", "NO_ENCONTRADA")
    key_preview = key[:8] + "..." if len(key) > 8 else key
    ia = get_ia()

    # Intentar una llamada real a Gemini
    test_result = "no_probado"
    test_error  = None
    try:
        resp = ia.gemini._cliente.generate_content("Di solo: OK")
        test_result = resp.text.strip()
    except Exception as e:
        test_result = "error"
        test_error  = str(e)

    return jsonify({
        "key_presente":      key != "NO_ENCONTRADA",
        "key_preview":       key_preview,
        "gemini_disponible": ia.gemini.disponible,
        "test_llamada":      test_result,
        "test_error":        test_error,
    })


if __name__ == "__main__":
    app.run(debug=True)
