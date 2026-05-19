from flask import Flask, render_template, request, jsonify, session
from ia2 import IAPro
import uuid

app = Flask(__name__)
app.secret_key = "tracker_habitos_secret_key"

ia = IAPro()


@app.route("/")
def inicio():
    # Asignar session_id único si no existe
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Endpoint principal del chatbot.
    Recibe: { "mensaje": "texto del usuario" }
    Devuelve: { "respuesta": "texto del bot" }
    """
    data = request.get_json(silent=True)

    if not data or "mensaje" not in data:
        return jsonify({"error": "Falta el campo 'mensaje'"}), 400

    session_id = session.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        session["session_id"] = session_id

    mensaje = data["mensaje"].strip()

    # Comando especial para reiniciar
    if mensaje.lower() in ("reiniciar", "reset", "nuevo", "restart"):
        respuesta = ia.reiniciar(session_id)
    else:
        respuesta = ia.responder(session_id, mensaje)

    return jsonify({"respuesta": respuesta})


@app.route("/api/reset", methods=["POST"])
def reset():
    """Reinicia la sesión del usuario."""
    session_id = session.get("session_id", str(uuid.uuid4()))
    session["session_id"] = session_id
    respuesta = ia.reiniciar(session_id)
    return jsonify({"respuesta": respuesta})


if __name__ == "__main__":
    app.run(debug=True)
