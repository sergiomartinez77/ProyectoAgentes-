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
    import google.generativeai as genai
    key = os.getenv("GEMINI_API_KEY", "")
    genai.configure(api_key=key)
    resultados = {}
    for modelo in ["gemini-2.0-flash", "gemini-2.0-flash-exp", "gemini-2.0-flash-lite", "gemini-1.5-flash", "gemini-1.5-pro"]:
        try:
            r = genai.GenerativeModel(modelo).generate_content("Di solo: OK")
            resultados[modelo] = r.text.strip()
        except Exception as e:
            resultados[modelo] = f"ERROR: {str(e)[:120]}"
    return jsonify(resultados)


if __name__ == "__main__":
    app.run(debug=True)
