"""
Motor del chatbot híbrido — diseño STATELESS.
El estado de la sesión se pasa como parámetro y se devuelve modificado,
permitiendo que el caller (app.py) lo persista donde quiera (cookie, DB, etc.)
"""
from modelo_prediccion import ModeloPrediccion
from gemini_client import GeminiClient


class IAPro:

    PASOS_HABITOS = ["sueno", "animo", "energia", "estres", "redes", "cafe", "ejercicio"]
    PASOS_GYM     = ["objetivo", "nivel", "dias", "equipamiento", "tiempo", "musculo", "lesiones"]

    PREGUNTAS_HABITOS = {
        "sueno":     "¿Cuántas horas dormiste anoche? (ej: 7.5)",
        "animo":     "¿Cómo está tu estado de ánimo hoy? Del 1 al 10.",
        "energia":   "¿Cuánta energía sientes ahora? Del 1 al 10.",
        "estres":    "¿Qué tan estresado estás hoy? Del 1 al 10.",
        "redes":     "¿Cuántos minutos llevas en redes sociales hoy? (ej: 90)",
        "cafe":      "¿Cuántas tazas de café tomaste hoy?",
        "ejercicio": "¿Hiciste ejercicio hoy? Responde sí o no.",
    }

    PREGUNTAS_GYM = {
        "objetivo": (
            "¿Cuál es tu objetivo principal?\n"
            "1️⃣ Ganar músculo\n2️⃣ Perder grasa\n"
            "3️⃣ Mejorar resistencia\n4️⃣ Mantenimiento\n"
            "Responde con el número."
        ),
        "nivel": (
            "¿Cuál es tu nivel de experiencia?\n"
            "1️⃣ Principiante (menos de 6 meses)\n"
            "2️⃣ Intermedio (6 meses – 2 años)\n"
            "3️⃣ Avanzado (más de 2 años)\n"
            "Responde con el número."
        ),
        "dias":         "¿Cuántos días a la semana puedes entrenar? (1-7)",
        "equipamiento": (
            "¿Con qué equipamiento cuentas?\n"
            "1️⃣ Gimnasio completo\n"
            "2️⃣ Mancuernas y barra en casa\n"
            "3️⃣ Solo peso corporal\n"
            "Responde con el número."
        ),
        "tiempo":   "¿Cuántos minutos tienes por sesión? (ej: 60)",
        "musculo":  (
            "¿Algún músculo que quieras priorizar?\n"
            "1️⃣ Pecho\n2️⃣ Espalda\n3️⃣ Piernas\n"
            "4️⃣ Hombros\n5️⃣ Brazos\n6️⃣ Sin preferencia\n"
            "Responde con el número."
        ),
        "lesiones": "¿Tienes alguna lesión o zona que debas evitar? (ej: rodilla) o escribe 'ninguna'.",
    }

    OBJETIVOS = {"1": "Ganar músculo", "2": "Perder grasa", "3": "Mejorar resistencia", "4": "Mantenimiento"}
    NIVELES   = {"1": "Principiante", "2": "Intermedio", "3": "Avanzado"}
    EQUIPOS   = {"1": "Gimnasio completo", "2": "Mancuernas y barra", "3": "Peso corporal"}
    MUSCULOS  = {"1": "Pecho", "2": "Espalda", "3": "Piernas", "4": "Hombros", "5": "Brazos", "6": "Sin preferencia"}

    MENU = (
        "¿Qué quieres hacer hoy?\n\n"
        "1️⃣ Análisis de hábitos diarios\n"
        "2️⃣ Generar rutina de gimnasio\n"
        "3️⃣ Pregúntame sobre gym o hábitos\n\n"
        "Responde con **1**, **2** o **3**."
    )

    def __init__(self):
        self.modelo = ModeloPrediccion()
        print(self.modelo.entrenar())
        self.gemini = GeminiClient()

    # ------------------------------------------------------------------
    # API pública — STATELESS
    # El estado (sesion) se recibe y se devuelve modificado.
    # app.py es responsable de persistirlo en la cookie.
    # ------------------------------------------------------------------

    def sesion_nueva(self) -> dict:
        """Devuelve un estado de sesión inicial."""
        return {"flujo": "nombre", "paso": "nombre", "datos": {}}

    def responder(self, sesion: dict, mensaje: str) -> tuple[str, dict]:
        """
        Procesa el mensaje y devuelve (respuesta, sesion_actualizada).
        sesion es un dict con flujo, paso y datos.
        """
        mensaje = mensaje.strip()

        flujo = sesion.get("flujo", "nombre")
        paso  = sesion.get("paso", "nombre")

        # ── Nombre ───────────────────────────────────────────────────
        if flujo == "nombre":
            if not mensaje or mensaje == "__inicio__":
                return "¡Hola! Soy Trackito, tu asistente de hábitos ⚡ ¿Cómo te llamas?", sesion
            sesion["datos"]["nombre"] = mensaje.strip().capitalize()
            sesion["flujo"] = "menu"
            sesion["paso"]  = "menu"
            return f"Hola, **{sesion['datos']['nombre']}** 👋\n\n{self.MENU}", sesion

        # ── Menú ─────────────────────────────────────────────────────
        if flujo == "menu":
            if mensaje == "1":
                sesion["flujo"] = "habitos"
                sesion["paso"]  = "sueno"
                return self.PREGUNTAS_HABITOS["sueno"], sesion
            elif mensaje == "2":
                sesion["flujo"] = "gym"
                sesion["paso"]  = "objetivo"
                return self.PREGUNTAS_GYM["objetivo"], sesion
            elif mensaje == "3":
                sesion["flujo"] = "libre"
                sesion["paso"]  = "libre"
                return (
                    "💬 Modo libre activado. Puedes preguntarme sobre ejercicios, "
                    "nutrición, técnica, hábitos saludables o lo que necesites.\n\n"
                    "Escribe **menú** en cualquier momento para volver al inicio."
                ), sesion
            return f"⚠️ Responde con **1**, **2** o **3**.\n\n{self.MENU}", sesion

        # ── Flujo hábitos ─────────────────────────────────────────────
        if flujo == "habitos":
            error = self._guardar_habito(sesion, paso, mensaje)
            if error:
                return f"⚠️ {error}\n\n{self.PREGUNTAS_HABITOS[paso]}", sesion
            siguiente = self._siguiente(self.PASOS_HABITOS, paso)
            if siguiente:
                sesion["paso"] = siguiente
                return self.PREGUNTAS_HABITOS[siguiente], sesion
            resultado = self._analizar_habitos(sesion["datos"])
            sesion = self._reset_a_menu(sesion)
            return resultado, sesion

        # ── Flujo gym ─────────────────────────────────────────────────
        if flujo == "gym":
            error = self._guardar_gym(sesion, paso, mensaje)
            if error:
                return f"⚠️ {error}\n\n{self.PREGUNTAS_GYM[paso]}", sesion
            siguiente = self._siguiente(self.PASOS_GYM, paso)
            if siguiente:
                sesion["paso"] = siguiente
                return self.PREGUNTAS_GYM[siguiente], sesion
            resultado = self._generar_rutina(sesion["datos"])
            sesion = self._reset_a_menu(sesion)
            return resultado, sesion

        # ── Flujo libre ───────────────────────────────────────────────
        if flujo == "libre":
            if mensaje.lower() in ("menu", "menú", "volver", "inicio", "salir"):
                sesion = self._reset_a_menu(sesion)
                return f"De vuelta al menú principal 👋\n\n{self.MENU}", sesion
            nombre = sesion["datos"].get("nombre", "")
            respuesta = self.gemini.chat_libre(mensaje, nombre)
            return respuesta + "\n\n_Escribe **menú** para volver al inicio._", sesion

        # Estado desconocido → reiniciar
        sesion = self.sesion_nueva()
        return "¡Hola! Soy Trackito, tu asistente de hábitos ⚡ ¿Cómo te llamas?", sesion

    def reiniciar(self, sesion: dict) -> tuple[str, dict]:
        sesion = self.sesion_nueva()
        return "🔄 Sesión reiniciada.\n\n¡Hola! Soy Trackito, tu asistente de hábitos ⚡ ¿Cómo te llamas?", sesion

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _siguiente(self, pasos, actual):
        idx = pasos.index(actual)
        return pasos[idx + 1] if idx + 1 < len(pasos) else None

    def _reset_a_menu(self, sesion: dict) -> dict:
        nombre = sesion.get("datos", {}).get("nombre", "")
        return {"flujo": "menu", "paso": "menu", "datos": {"nombre": nombre}}

    # ------------------------------------------------------------------
    # Validación hábitos
    # ------------------------------------------------------------------

    def _guardar_habito(self, sesion, paso, valor):
        datos = sesion["datos"]
        try:
            if paso == "sueno":
                v = float(valor.replace(",", "."))
                if not (0 <= v <= 24): return "Las horas deben estar entre 0 y 24."
                datos["sueno"] = v
            elif paso in ("animo", "energia", "estres"):
                v = int(valor)
                if not (1 <= v <= 10): return "El valor debe ser entre 1 y 10."
                datos[paso] = v
            elif paso == "redes":
                v = int(valor)
                if v < 0: return "Los minutos no pueden ser negativos."
                datos["redes"] = v
            elif paso == "cafe":
                v = int(valor)
                if v < 0: return "Las tazas no pueden ser negativas."
                datos["cafe"] = v
            elif paso == "ejercicio":
                v = valor.lower()
                if v in ("si", "sí", "s", "yes", "y", "1"):
                    datos["ejercicio"] = "Si"
                elif v in ("no", "n", "0"):
                    datos["ejercicio"] = "No"
                else:
                    return "Responde 'sí' o 'no'."
        except ValueError:
            return "No entendí ese valor. Asegúrate de escribir un número."
        return None

    # ------------------------------------------------------------------
    # Validación gym
    # ------------------------------------------------------------------

    def _guardar_gym(self, sesion, paso, valor):
        datos = sesion["datos"]
        try:
            if paso == "objetivo":
                if valor not in self.OBJETIVOS: return "Elige una opción del 1 al 4."
                datos["objetivo"] = self.OBJETIVOS[valor]
            elif paso == "nivel":
                if valor not in self.NIVELES: return "Elige una opción del 1 al 3."
                datos["nivel"] = self.NIVELES[valor]
            elif paso == "dias":
                v = int(valor)
                if not (1 <= v <= 7): return "Los días deben estar entre 1 y 7."
                datos["dias"] = v
            elif paso == "equipamiento":
                if valor not in self.EQUIPOS: return "Elige una opción del 1 al 3."
                datos["equipamiento"] = self.EQUIPOS[valor]
            elif paso == "tiempo":
                v = int(valor)
                if not (10 <= v <= 180): return "El tiempo debe estar entre 10 y 180 minutos."
                datos["tiempo"] = v
            elif paso == "musculo":
                if valor not in self.MUSCULOS: return "Elige una opción del 1 al 6."
                datos["musculo"] = self.MUSCULOS[valor]
            elif paso == "lesiones":
                datos["lesiones"] = valor.strip().capitalize()
        except ValueError:
            return "No entendí ese valor. Asegúrate de escribir un número."
        return None

    # ------------------------------------------------------------------
    # Análisis hábitos
    # ------------------------------------------------------------------

    def _analizar_habitos(self, d: dict) -> str:
        nombre        = d["nombre"]
        ejercicio_num = 1 if d["ejercicio"] == "Si" else 0

        resultado, probabilidad = self.modelo.predecir(
            d["sueno"], d["animo"], d["energia"], d["estres"],
            d["redes"], ejercicio_num, d["cafe"]
        )

        prob_pct = round(probabilidad * 100)
        barra    = "█" * round(prob_pct / 10) + "░" * (10 - round(prob_pct / 10))
        riesgo   = self._riesgo(prob_pct)
        hora     = self._mejor_hora(d["energia"])
        consejo  = self.gemini.consejo_habitos(d, probabilidad)

        return (
            f"📊 **Análisis de {nombre}**\n\n"
            f"🎯 Probabilidad de cumplir tu hábito hoy: **{prob_pct}%**\n"
            f"[{barra}]\n\n"
            f"⚠️ Nivel de riesgo: **{riesgo}**\n"
            f"⏰ Mejor hora para actuar: **{hora}**\n\n"
            f"{consejo}\n\n"
            f"---\n¿Qué quieres hacer ahora?\n\n{self.MENU}"
        )

    # ------------------------------------------------------------------
    # Rutina gym
    # ------------------------------------------------------------------

    def _generar_rutina(self, d: dict) -> str:
        rutina      = self.gemini.generar_rutina(d)
        advertencia = ""
        if d.get("lesiones", "ninguna").lower() not in ("ninguna", "none", "no", "n/a", ""):
            advertencia = f"⚠️ **Lesión a considerar: {d['lesiones']}**\n\n"

        return (
            f"🏋️ **Rutina de {d['nombre']}**\n\n"
            f"🎯 Objetivo: **{d['objetivo']}** | 📊 Nivel: **{d['nivel']}**\n"
            f"📅 Días: **{d['dias']}/semana** | ⏱️ Tiempo: **{d['tiempo']} min/sesión**\n"
            f"🏠 Equipamiento: **{d['equipamiento']}**\n\n"
            f"{advertencia}---\n\n{rutina}\n\n"
            f"---\n¿Qué quieres hacer ahora?\n\n{self.MENU}"
        )

    def _riesgo(self, prob):
        if prob >= 75: return "Bajo 🟢"
        if prob >= 50: return "Medio 🟡"
        return "Alto 🔴"

    def _mejor_hora(self, energia):
        if energia >= 8: return "7:00 AM"
        if energia >= 5: return "6:30 PM"
        return "8:00 PM"
