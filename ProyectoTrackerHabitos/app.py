from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/predecir", methods=["POST"])
def predecir():

    nombre = request.form["nombre"]
    sueno = float(request.form["sueno"])
    animo = int(request.form["animo"])
    energia = int(request.form["energia"])
    estres = int(request.form["estres"])
    redes = int(request.form["redes"])
    ejercicio = request.form["ejercicio"]
    cafe = int(request.form["cafe"])

    # Simulación IA por ahora
    score = animo + energia + (10 - estres)

    if sueno >= 7:
        score += 2

    if redes > 180:
        score -= 2

    if ejercicio == "Si":
        score += 2

    probabilidad = min(max(score * 5, 10), 95)

    if probabilidad >= 75:
        mensaje = "🚀 Hoy estás imparable. No rompas la racha."
    elif probabilidad >= 55:
        mensaje = "🔥 Buen día para avanzar. Hazlo ahora."
    else:
        mensaje = "⚡ Empieza pequeño hoy. Lo importante es cumplir."

    return render_template(
        "index.html",
        mensaje=mensaje,
        nombre=nombre,
        probabilidad=probabilidad
    )


if __name__ == "__main__":
    app.run(debug=True)