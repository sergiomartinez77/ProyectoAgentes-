"""
Motor del chatbot híbrido:
  - RandomForest  → predicción numérica de probabilidad (modelo_prediccion.py)
  - Gemini        → consejos y rutinas en lenguaje natural (gemini_client.py)
  - Flujo de chat → recolección de datos paso a paso
"""
from modelo_prediccion import ModeloPrediccion
from gemini_client import GeminiClient


class IAPro:

    # ------------------------------------------------------------------
    # PASOS POR FLUJO
    # ------------------------------------------------------------------
    PASOS_HABITOS = ["sueno", "animo", "energia", "estres", "redes", "cafe", "ejercicio"]
    PASOS_GYM     = ["objetivo", "nivel", "dias", "equipamiento", "tiempo", "musculo", "lesiones"]

    # ------------------------------------------------------------------
    # PREGUNTAS
    # ------------------------------------------------------------------
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
        "2️⃣ Generar rutina de gimnasio\n\n"
        "Responde con **1** o **2**."
    )

    def __init__(self):
        self.sesiones = {}

        # Inicializar modelo ML
        self.modelo = ModeloPrediccion()
        resultado_entrenamiento = self.modelo.entrenar()
        print(resultado_entrenamiento)

        # Inicializar cliente Gemini
        self.gemini = GeminiClient()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def responder(self, session_id: str, mensaje: str) -> str:
        mensaje = mensaje.strip()

        if session_id not in self.sesiones or mensaje == "__inicio__":
            self.sesiones[session_id] = {"flujo": "nombre", "paso": "nombre", "datos": {}}
            return "¡Hola! Soy Trackito, tu asistente de hábitos ⚡ ¿Cómo te llamas?"

        sesion = self.sesiones[session_id]
        flujo  = sesion["flujo"]
        paso   = sesion["paso"]

        # ── Nombre ───────────────────────────────────────────────────
        if flujo == "nombre":
            if not mensaje:
                return "⚠️ El nombre no puede estar vacío. ¿Cómo te llamas?"
            sesion["datos"]["nombre"] = mensaje.strip().capitalize()
            sesion["flujo"] = "menu"
            sesion["paso"]  = "menu"
            return f"Hola, **{sesion['datos']['nombre']}** 👋\n\n{self.MENU}"

        # ── Menú ─────────────────────────────────────────────────────
        if flujo == "menu":
            if mensaje == "1":
                sesion["flujo"] = "habitos"
                sesion["paso"]  = "sueno"
                return self.PREGUNTAS_HABITOS["sueno"]
            elif mensaje == "2":
                sesion["flujo"] = "gym"
                sesion["paso"]  = "objetivo"
                return self.PREGUNTAS_GYM["objetivo"]
            return f"⚠️ Responde con **1** o **2**.\n\n{self.MENU}"

        # ── Flujo hábitos ─────────────────────────────────────────────
        if flujo == "habitos":
            error = self._guardar_habito(sesion, paso, mensaje)
            if error:
                return f"⚠️ {error}\n\n{self.PREGUNTAS_HABITOS[paso]}"
            siguiente = self._siguiente(self.PASOS_HABITOS, paso)
            if siguiente:
                sesion["paso"] = siguiente
                return self.PREGUNTAS_HABITOS[siguiente]
            resultado = self._analizar_habitos(sesion["datos"])
            self._reset_a_menu(sesion)
            return resultado

        # ── Flujo gym ─────────────────────────────────────────────────
        if flujo == "gym":
            error = self._guardar_gym(sesion, paso, mensaje)
            if error:
                return f"⚠️ {error}\n\n{self.PREGUNTAS_GYM[paso]}"
            siguiente = self._siguiente(self.PASOS_GYM, paso)
            if siguiente:
                sesion["paso"] = siguiente
                return self.PREGUNTAS_GYM[siguiente]
            resultado = self._generar_rutina(sesion["datos"])
            self._reset_a_menu(sesion)
            return resultado

        return "❌ Estado desconocido. Escribe 'reiniciar'."

    def reiniciar(self, session_id: str) -> str:
        if session_id in self.sesiones:
            del self.sesiones[session_id]
        return "🔄 Sesión reiniciada.\n\n¡Hola! Soy Trackito, tu asistente de hábitos ⚡ ¿Cómo te llamas?"

    # ------------------------------------------------------------------
    # Helpers de flujo
    # ------------------------------------------------------------------

    def _siguiente(self, pasos, actual):
        idx = pasos.index(actual)
        return pasos[idx + 1] if idx + 1 < len(pasos) else None

    def _reset_a_menu(self, sesion):
        nombre = sesion["datos"].get("nombre", "")
        sesion["flujo"] = "menu"
        sesion["paso"]  = "menu"
        sesion["datos"] = {"nombre": nombre}

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
    # Análisis de hábitos (RandomForest + Gemini)
    # ------------------------------------------------------------------

    def _analizar_habitos(self, d: dict) -> str:
        nombre    = d["nombre"]
        ejercicio_num = 1 if d["ejercicio"] == "Si" else 0

        # 1. Predicción con RandomForest
        resultado, probabilidad = self.modelo.predecir(
            d["sueno"], d["animo"], d["energia"], d["estres"],
            d["redes"], ejercicio_num, d["cafe"]
        )

        prob_pct = round(probabilidad * 100)
        barra    = "█" * round(prob_pct / 10) + "░" * (10 - round(prob_pct / 10))
        riesgo   = self._riesgo(prob_pct)
        hora     = self._mejor_hora(d["energia"])

        # 2. Consejo generado por Gemini
        consejo = self.gemini.consejo_habitos(d, probabilidad)

        return (
            f"📊 **Análisis de {nombre}**\n\n"
            f"🎯 Probabilidad de cumplir tu hábito hoy: **{prob_pct}%**\n"
            f"[{barra}]\n\n"
            f"⚠️ Nivel de riesgo: **{riesgo}**\n"
            f"⏰ Mejor hora para actuar: **{hora}**\n\n"
            f"{consejo}\n\n"
            f"---\n"
            f"¿Qué quieres hacer ahora?\n\n{self.MENU}"
        )

    # ------------------------------------------------------------------
    # Rutina de gym (Gemini)
    # ------------------------------------------------------------------

    def _generar_rutina(self, d: dict) -> str:
        nombre = d["nombre"]

        # Gemini genera la rutina completa
        rutina = self.gemini.generar_rutina(d)

        advertencia = ""
        lesiones = d.get("lesiones", "ninguna").lower()
        if lesiones not in ("ninguna", "none", "no", "n/a", ""):
            advertencia = f"⚠️ **Lesión a considerar: {d['lesiones']}**\n\n"

        return (
            f"🏋️ **Rutina de {nombre}**\n\n"
            f"🎯 Objetivo: **{d['objetivo']}** | 📊 Nivel: **{d['nivel']}**\n"
            f"📅 Días: **{d['dias']}/semana** | ⏱️ Tiempo: **{d['tiempo']} min/sesión**\n"
            f"🏠 Equipamiento: **{d['equipamiento']}**\n\n"
            f"{advertencia}"
            f"---\n\n"
            f"{rutina}\n\n"
            f"---\n"
            f"¿Qué quieres hacer ahora?\n\n{self.MENU}"
        )

    # ------------------------------------------------------------------
    # Helpers de análisis
    # ------------------------------------------------------------------

    def _riesgo(self, prob: int) -> str:
        if prob >= 75: return "Bajo 🟢"
        if prob >= 50: return "Medio 🟡"
        return "Alto 🔴"

    def _mejor_hora(self, energia: int) -> str:
        if energia >= 8: return "7:00 AM"
        if energia >= 5: return "6:30 PM"
        return "8:00 PM"
