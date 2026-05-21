"""
Cliente de IA usando Groq (llama-3.3-70b-versatile).
Genera consejos de hábitos y rutinas de gimnasio en lenguaje natural.
Si la API key no está configurada, usa respuestas de fallback locales.
"""
import os

# Cargar .env solo en local (en Vercel la variable ya está en el entorno)
try:
    from pathlib import Path
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=False, encoding="utf-8")
except Exception:
    pass


class GeminiClient:
    """Mantiene el nombre GeminiClient para no romper imports, pero usa Groq internamente."""

    MODELO = "llama-3.3-70b-versatile"

    def __init__(self):
        self.api_key    = os.getenv("groq_variable", "")
        self.disponible = False
        self._cliente   = None
        self._inicializar()

    def _inicializar(self):
        if not self.api_key or self.api_key == "pega_tu_key_aqui":
            print("⚠️  IA: API key no configurada. Usando respuestas locales.")
            return
        try:
            from groq import Groq
            self._cliente   = Groq(api_key=self.api_key)
            self.disponible = True
            print("✅ Groq conectado correctamente.")
        except Exception as e:
            print(f"⚠️  Groq no disponible: {e}")

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def consejo_habitos(self, datos: dict, probabilidad: float) -> str:
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
            f"Usa emojis. No repitas los datos, solo da el consejo. Responde en español."
        )
        return self._llamar(prompt, fallback=self._consejo_local(datos, probabilidad))

    def generar_rutina(self, datos: dict) -> str:
        if not self.disponible:
            return self._rutina_local(datos)

        lesion_txt = (
            f"⚠️ Lesión a considerar: {datos['lesiones']}. Sustituye o adapta ejercicios que la afecten."
            if datos["lesiones"].lower() not in ("ninguna", "none", "no", "n/a", "")
            else "Sin lesiones reportadas."
        )

        config_map = {
            "Ganar músculo":       "4 series × 8-12 reps | Descanso: 60-90s",
            "Perder grasa":        "3 series × 15-20 reps | Descanso: 30-45s",
            "Mejorar resistencia": "3 series × 20-25 reps | Descanso: 30s",
            "Mantenimiento":       "3 series × 12-15 reps | Descanso: 60s",
        }
        config_series = config_map.get(datos["objetivo"], "3 series × 12 reps | Descanso: 60s")

        prompt = f"""Eres un entrenador personal experto. Genera una rutina de gimnasio semanal COMPLETA para {datos['nombre']}.

PERFIL:
• Objetivo: {datos['objetivo']}
• Nivel: {datos['nivel']}
• Días: {datos['dias']} por semana
• Equipamiento: {datos['equipamiento']}
• Tiempo por sesión: {datos['tiempo']} minutos
• Músculo a priorizar: {datos['musculo']}
• {lesion_txt}
• Configuración base: {config_series}

INSTRUCCIONES:
1. Crea exactamente {datos['dias']} días de entrenamiento.
2. Cada día: 5-7 ejercicios REALES y ESPECÍFICOS.
3. Por cada ejercicio incluye: nombre, series×reps, descanso y descripción técnica breve.
4. Adapta al equipamiento: si es "Peso corporal" NO uses mancuernas ni barras.
5. Adapta al nivel: Principiante=básicos, Intermedio=compuestos+aislamiento, Avanzado=técnicas avanzadas.
6. Al final agrega sección "💊 RECOMENDACIONES" con consejo nutricional, de descanso y de progresión.

FORMATO por día:
📅 DÍA [N] — [Nombre del split] ([grupos musculares])
🔹 [Ejercicio] — [series×reps] | Descanso: [Xs]
   📌 [Descripción técnica breve]

Responde completamente en español."""

        return self._llamar(prompt, fallback=self._rutina_local(datos))

    def chat_libre(self, pregunta: str, nombre: str) -> str:
        if not self.disponible:
            return (
                "⚠️ El servicio de IA no está disponible ahora mismo.\n\n"
                "Puedo ayudarte con el análisis de hábitos o generarte una rutina. "
                "Elige una opción del menú principal."
            )

        system = (
            "Eres Trackito, un asistente experto en fitness, gimnasio y hábitos saludables. "
            "Tu personalidad es motivadora, directa y cercana. Usas emojis con moderación. "
            "SOLO respondes sobre: ejercicio, gym, nutrición deportiva, hábitos saludables, "
            "sueño, estrés y bienestar físico. Si te preguntan algo fuera de ese dominio, "
            "redirige amablemente al tema de fitness. Sé específico y práctico. "
            "Máximo 6 líneas salvo que la pregunta requiera más detalle. Responde en español."
        )

        return self._llamar_chat(system, f"{nombre} pregunta: {pregunta}",
                                 fallback=(
                                     "💪 Puedo responder sobre ejercicios, nutrición y hábitos saludables. "
                                     "En este momento el servicio no está disponible."
                                 ))

    # ------------------------------------------------------------------
    # Llamadas a la API
    # ------------------------------------------------------------------

    def _llamar(self, prompt: str, fallback: str) -> str:
        try:
            resp = self._cliente.chat.completions.create(
                model=self.MODELO,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️  Error Groq: {e}")
            return fallback

    def _llamar_chat(self, system: str, user: str, fallback: str) -> str:
        try:
            resp = self._cliente.chat.completions.create(
                model=self.MODELO,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
                temperature=0.7,
                max_tokens=512,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️  Error Groq: {e}")
            return fallback

    # ------------------------------------------------------------------
    # Fallbacks locales
    # ------------------------------------------------------------------

    def _consejo_local(self, datos: dict, probabilidad: float) -> str:
        nombre  = datos["nombre"]
        prob    = round(probabilidad * 100)
        sueno   = datos["sueno"]
        estres  = datos["estres"]
        redes   = datos["redes"]
        energia = datos["energia"]

        if prob >= 80:  return f"🚀 {nombre}, hoy estás imparable. No rompas la racha."
        if prob >= 60:  return f"🔥 {nombre}, buen momento para avanzar. Aprovéchalo."
        if sueno < 6:   return f"😴 {nombre}, dormiste poco. Haz una versión pequeña del hábito hoy."
        if estres >= 8: return f"🧘 {nombre}, mucho estrés. Respira y avanza poco a poco."
        if redes > 180: return f"📵 {nombre}, menos redes, más progreso."
        if energia <= 4: return f"☕ {nombre}, energía baja. Empieza suave, 5 minutos bastan."
        return f"💪 {nombre}, hoy cuesta, pero no te rindas."

    def _rutina_local(self, datos: dict) -> str:
        objetivo = datos["objetivo"]
        dias     = datos["dias"]
        nivel    = datos["nivel"]
        equipo   = datos["equipamiento"]

        config_map = {
            "Ganar músculo":       ("4×8-12", "60-90s"),
            "Perder grasa":        ("3×15-20", "30-45s"),
            "Mejorar resistencia": ("3×20-25", "30s"),
            "Mantenimiento":       ("3×12-15", "60s"),
        }
        sr, desc = config_map.get(objetivo, ("3×12", "60s"))
        gym = equipo in ("Gimnasio completo", "Mancuernas y barra")

        if gym:
            splits = {
                1: [("Cuerpo completo", "Sentadilla · Press banca · Remo · Press militar · Plancha")],
                2: [("Cuerpo completo A", "Sentadilla · Press banca · Jalón · Curl · Tríceps"),
                    ("Cuerpo completo B", "Peso muerto · Press inclinado · Remo · Hombros · Core")],
                3: [("Empuje", "Press banca · Press inclinado · Press militar · Fondos · Tríceps"),
                    ("Jale", "Dominadas · Remo barra · Jalón · Curl barra · Curl martillo"),
                    ("Piernas", "Sentadilla · Prensa · Curl femoral · Peso muerto rumano · Gemelos")],
                4: [("Pecho/Tríceps", "Press banca · Press inclinado · Aperturas · Fondos · Extensión tríceps"),
                    ("Espalda/Bíceps", "Dominadas · Remo barra · Jalón · Curl barra · Curl martillo"),
                    ("Piernas", "Sentadilla · Prensa · Curl femoral · Peso muerto rumano · Gemelos"),
                    ("Hombros/Core", "Press militar · Elevaciones laterales · Face pulls · Plancha · Crunch")],
            }
        else:
            splits = {
                1: [("Cuerpo completo", "Sentadilla · Flexiones · Remo invertido · Fondos · Plancha")],
                2: [("Cuerpo completo A", "Sentadilla · Flexiones · Dominadas · Plancha · Crunch"),
                    ("Cuerpo completo B", "Zancadas · Flexiones diamante · Superman · Puente glúteos · Burpees")],
                3: [("Empuje", "Flexiones · Flexiones inclinadas · Fondos · Pike push-up · Diamante"),
                    ("Jale", "Dominadas · Remo invertido · Superman · Curl mochila"),
                    ("Piernas", "Sentadilla · Zancadas · Búlgara · Puente glúteos · Gemelos")],
                4: [("Pecho/Tríceps", "Flexiones · Inclinadas · Declinadas · Fondos · Diamante"),
                    ("Espalda/Bíceps", "Dominadas · Remo invertido · Superman · Curl mochila"),
                    ("Piernas", "Sentadilla · Zancadas · Búlgara · Puente glúteos · Step-up"),
                    ("Hombros/Core", "Pike push-up · Elevaciones botella · Plancha · Lateral · Crunch")],
            }

        dias_clave = min(dias, 4)
        dias_rutina = splits.get(dias_clave, splits[3])
        resultado = f"⚙️ **Configuración:** {sr} | Descanso: {desc}\n\n"

        for i, (nombre_dia, ejercicios) in enumerate(dias_rutina, 1):
            resultado += f"📅 **DÍA {i} — {nombre_dia}**\n{ejercicios}\n\n"

        consejos = {
            "Ganar músculo":       "🥩 1.6-2g proteína/kg · 😴 7-9h sueño · 📈 Aumenta peso cada semana",
            "Perder grasa":        "🥗 Déficit 300-500 kcal · 😴 No entrenes más de 5 días seguidos · 🏃 Cardio moderado en días de descanso",
            "Mejorar resistencia": "💧 Hidratación constante · 😴 48h entre sesiones del mismo grupo · ⏱️ Reduce descanso 5s cada semana",
            "Mantenimiento":       "⚖️ Balance calórico · 🔄 Cambia ejercicios cada 4-6 semanas · 😴 Alterna intensidad alta/baja",
        }
        resultado += f"---\n\n💊 **RECOMENDACIONES**\n{consejos.get(objetivo, '💡 Sé consistente y progresivo.')}"
        return resultado
