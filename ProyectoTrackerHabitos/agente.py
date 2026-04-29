from modelo_prediccion import ModeloPrediccion


class AgenteIA:

    def __init__(self):
        self.modelo = ModeloPrediccion()
        self.modelo.entrenar()

    def analizar_dia(self, horas_sueno, estado_animo, energia,
                     estres, tiempo_redes, ejercicio, cafe_tazas):

        resultado, probabilidad = self.modelo.predecir(
            horas_sueno,
            estado_animo,
            energia,
            estres,
            tiempo_redes,
            ejercicio,
            cafe_tazas
        )

        mensaje = self.generar_mensaje(
            probabilidad,
            horas_sueno,
            estres,
            tiempo_redes,
            energia
        )

        return resultado, probabilidad, mensaje

    def generar_mensaje(self, probabilidad, horas_sueno,
                        estres, tiempo_redes, energia):

        if probabilidad >= 0.85:
            return "🚀 Hoy estás imparable. No rompas la racha."

        elif probabilidad >= 0.70:
            return "🔥 Vas excelente. Sigue así."

        elif probabilidad >= 0.50:
            return "⚡ Puedes lograrlo. Empieza con 5 minutos."

        else:
            if horas_sueno < 6:
                return "😴 Dormiste poco. Haz una versión pequeña hoy."

            if estres >= 8:
                return "🧘 Mucho estrés. Respira y avanza poco a poco."

            if tiempo_redes > 180:
                return "📵 Menos redes, más progreso."

            if energia <= 4:
                return "☕ Energía baja. Empieza suave."

            return "💪 Hoy cuesta, pero no te rindas."