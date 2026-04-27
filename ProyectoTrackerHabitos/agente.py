from red_neuronal import RedNeuronal

class Agente:

    def __init__(self):
        self.red = RedNeuronal()

    def analizar(self, habito):
        historial = habito.historial
        total = len(historial)

        if total == 0:
            return "Empieza a registrar tu hábito."

        # porcentaje de éxito
        exitos = sum(historial)
        porcentaje = (exitos / total) * 100

        # rachas
        racha_exito = habito.racha_exito()
        racha_fallo = habito.racha_fallo()

        # 📈 tendencia reciente
        recientes = historial[-5:]
        tendencia = sum(recientes) / len(recientes)

        #  nivel
        if porcentaje >= 80:
            nivel = "Experto 🧠"
        elif porcentaje >= 60:
            nivel = "Intermedio ⚡"
        else:
            nivel = "Principiante 🌱"

        # RED NEURONAL (si hay suficientes datos)
        mensaje_nn = ""

        if len(historial) >= 4:
            self.red.entrenar(historial)
            ultimos = historial[-3:]
            pred = self.red.predecir(ultimos)

            if pred > 0.7:
                mensaje_nn = f"🔮 Alta probabilidad de éxito mañana ({pred:.2f})"
            elif pred > 0.4:
                mensaje_nn = f"🤔 Probabilidad media mañana ({pred:.2f})"
            else:
                mensaje_nn = f"⚠️ Riesgo de fallar mañana ({pred:.2f})"

        # DECISIONES 
        if racha_fallo >= 3:
            mensaje = f"⚠️ Muchas fallas en '{habito.nombre}'. Baja la dificultad o cambia el horario."

        elif racha_exito >= 5:
            mensaje = f"🔥 Excelente constancia en '{habito.nombre}'. Sube el nivel."

        elif tendencia < 0.4:
            mensaje = f"📉 Estás bajando en '{habito.nombre}'. Intenta hacerlo más fácil o dividirlo."

        elif porcentaje < 50:
            mensaje = f"😬 Bajo rendimiento ({porcentaje:.0f}%). Necesitas mejorar la disciplina."

        else:
            mensaje = f"📊 Vas bien ({porcentaje:.0f}% éxito) - Nivel: {nivel}"

        #  combinar ambos
        if mensaje_nn:
            return f"{mensaje}\n{mensaje_nn}"
        else:
            return mensaje