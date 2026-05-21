"""
Cliente de Gemini para generar consejos y rutinas en lenguaje natural.
Si la API key no está configurada, usa respuestas de fallback locales.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env desde la carpeta del proyecto, sin importar desde dónde se ejecute
load_dotenv(dotenv_path=Path(__file__).parent / ".env")


class GeminiClient:

    MODELO = "gemini-2.0-flash-lite"

    def __init__(self):
        self.api_key    = os.getenv("GEMINI_API_KEY", "")
        self.disponible = False
        self._cliente   = None
        self._inicializar()

    def _inicializar(self):
        if not self.api_key or self.api_key == "pega_tu_key_aqui":
            print("⚠️  Gemini: API key no configurada. Usando respuestas locales.")
            return
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            # Verificar que la key es válida con una llamada mínima
            self._cliente   = genai.GenerativeModel(self.MODELO)
            self.disponible = True
            print("✅ Gemini conectado correctamente.")
        except Exception as e:
            print(f"⚠️  Gemini no disponible: {e}")
            print("💡 Genera una nueva key en aistudio.google.com y actualiza el .env")

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def consejo_habitos(self, datos: dict, probabilidad: float) -> str:
        """
        Genera un consejo personalizado de hábitos usando Gemini.
        datos: dict con nombre, sueno, animo, energia, estres, redes, cafe, ejercicio
        probabilidad: float 0.0–1.0 del modelo RandomForest
        """
        if not self.disponible:
            return self._consejo_local(datos, probabilidad)

        prob_pct = round(probabilidad * 100)
        prompt = (
            f"Eres un coach de hábitos motivador y empático. "
            f"El usuario se llama {datos['nombre']}. "
            f"Hoy durmió {datos['sueno']} horas, su ánimo es {datos['animo']}/10, "
            f"energía {datos['energia']}/10, estrés {datos['estres']}/10, "
            f"lleva {datos['redes']} minutos en redes sociales, "
            f"tomó {datos['cafe']} tazas de café y "
            f"{'sí hizo' if datos['ejercicio'] == 'Si' else 'no hizo'} ejercicio. "
            f"Un modelo de IA predice que tiene {prob_pct}% de probabilidad de cumplir su hábito hoy. "
            f"Da un consejo personalizado, directo y motivador en máximo 3 oraciones. "
            f"Usa emojis. No repitas los datos, solo da el consejo."
        )
        return self._llamar(prompt, fallback=self._consejo_local(datos, probabilidad))

    def generar_rutina(self, datos: dict) -> str:
        """
        Genera una rutina de gimnasio personalizada usando Gemini.
        datos: dict con nombre, objetivo, nivel, dias, equipamiento, tiempo, musculo, lesiones
        """
        if not self.disponible:
            return self._rutina_local(datos)

        lesion_txt = (
            f"Tiene una lesión en: {datos['lesiones']}. Adapta o elimina ejercicios que la afecten."
            if datos["lesiones"].lower() not in ("ninguna", "none", "no", "n/a", "")
            else "Sin lesiones."
        )

        prompt = f"""Eres un entrenador personal experto y motivador. Crea una rutina de gimnasio semanal completa y personalizada para {datos['nombre']}.

PERFIL DEL USUARIO:
- Objetivo: {datos['objetivo']}
- Nivel: {datos['nivel']}
- Días disponibles: {datos['dias']} por semana
- Equipamiento: {datos['equipamiento']}
- Tiempo por sesión: {datos['tiempo']} minutos
- Músculo a priorizar: {datos['musculo']}
- {lesion_txt}

FORMATO OBLIGATORIO DE RESPUESTA:
Para cada día de entrenamiento usa exactamente esta estructura:

📅 DÍA X — [NOMBRE DEL DÍA] ([grupos musculares])
[Para cada ejercicio:]
• [Emoji] [Nombre del ejercicio] — [series]×[reps] | Descanso: [tiempo]
  💡 [Descripción breve de cómo ejecutarlo correctamente en 1 línea]

Reglas:
- Incluye entre 5 y 7 ejercicios por día según el tiempo disponible
- Elige ejercicios apropiados para el nivel y equipamiento indicados
- Para nivel Principiante: prioriza ejercicios básicos y compuestos con técnica simple
- Para nivel Intermedio: mezcla compuestos con algunos de aislamiento
- Para nivel Avanzado: incluye variantes más exigentes y técnicas avanzadas
- Adapta series/reps al objetivo: músculo (4×8-12), grasa (3×15-20), resistencia (3×20-25), mantenimiento (3×12-15)
- Al final agrega una sección "💊 RECOMENDACIONES" con 3 consejos: uno nutricional, uno de descanso y uno específico para el objetivo
- Usa emojis para hacerlo visual y motivador
- Responde en español"""

        return self._llamar(prompt, fallback=self._rutina_local(datos))

    # ------------------------------------------------------------------
    # Llamada a la API
    # ------------------------------------------------------------------

    def _llamar(self, prompt: str, fallback: str) -> str:
        try:
            respuesta = self._cliente.generate_content(prompt)
            return respuesta.text.strip()
        except Exception as e:
            print(f"⚠️  Error Gemini: {e}")
            return fallback

    # ------------------------------------------------------------------
    # Fallbacks locales (cuando no hay API key)
    # ------------------------------------------------------------------

    def _consejo_local(self, datos: dict, probabilidad: float) -> str:
        nombre = datos["nombre"]
        prob   = round(probabilidad * 100)
        sueno  = datos["sueno"]
        estres = datos["estres"]
        redes  = datos["redes"]
        energia = datos["energia"]

        if prob >= 80:
            return f"🚀 {nombre}, hoy estás imparable. No rompas la racha."
        if prob >= 60:
            return f"🔥 {nombre}, buen momento para avanzar. Aprovéchalo."
        if sueno < 6:
            return f"😴 {nombre}, dormiste poco. Haz una versión pequeña del hábito hoy."
        if estres >= 8:
            return f"🧘 {nombre}, mucho estrés. Respira y avanza poco a poco."
        if redes > 180:
            return f"📵 {nombre}, menos redes, más progreso."
        if energia <= 4:
            return f"☕ {nombre}, energía baja. Empieza suave, 5 minutos bastan."
        return f"💪 {nombre}, hoy cuesta, pero no te rindas."

    def _rutina_local(self, datos: dict) -> str:
        """Rutina básica de fallback cuando Gemini no está disponible."""
        nombre   = datos["nombre"]
        objetivo = datos["objetivo"]
        dias     = datos["dias"]
        nivel    = datos["nivel"]

        if objetivo == "Ganar músculo":
            config = "4 series × 8–12 reps | Descanso: 60–90s"
        elif objetivo == "Perder grasa":
            config = "3 series × 15–20 reps | Descanso: 30–45s"
        elif objetivo == "Mejorar resistencia":
            config = "3 series × 20–25 reps | Descanso: 30s"
        else:
            config = "3 series × 10–15 reps | Descanso: 60s"

        return (
            f"💪 Rutina básica para {nombre} ({objetivo} · {nivel})\n\n"
            f"⚙️ Configuración: {config}\n\n"
            f"📅 Distribuye tus {dias} días entre: Empuje (pecho/hombros/tríceps), "
            f"Jale (espalda/bíceps) y Piernas.\n\n"
            f"🥩 Consejo: Consume 1.6–2g de proteína por kg de peso corporal y duerme 7–9h."
        )
