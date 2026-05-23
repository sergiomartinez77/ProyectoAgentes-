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

# ──────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT BASE — define la personalidad y conocimiento de Trackito
# ──────────────────────────────────────────────────────────────────────
SYSTEM_TRACKITO = """Eres Trackito, un asistente de fitness y hábitos saludables altamente especializado.

CONOCIMIENTO Y ESPECIALIDAD:
- Entrenamiento de fuerza: periodización, progresión de cargas, splits (PPL, Upper/Lower, Full Body, Bro Split)
- Nutrición deportiva: macronutrientes, timing de comidas, suplementación básica (proteína, creatina, cafeína)
- Hábitos saludables: sueño, manejo del estrés, hidratación, rutinas de recuperación
- Biomecánica: técnica correcta de ejercicios compuestos (sentadilla, peso muerto, press, dominadas)
- Psicología del deporte: motivación, adherencia, manejo de rachas y recaídas

PRINCIPIOS QUE SIGUES:
- La progresión de sobrecarga es la base del progreso muscular
- El descanso y la nutrición son tan importantes como el entrenamiento
- La consistencia supera a la intensidad a largo plazo
- Adaptas las recomendaciones al nivel, equipamiento y objetivos del usuario
- Nunca recomiendas esteroides ni sustancias prohibidas
- Siempre priorizas la técnica correcta sobre el peso

PERSONALIDAD:
- Directo, motivador y empático
- Usas emojis con moderación para hacer el texto visual
- Respuestas concisas pero completas
- Hablas en español siempre
- Tratas al usuario por su nombre cuando lo conoces

RESTRICCIONES:
- Solo respondes sobre fitness, gym, nutrición deportiva y hábitos saludables
- Si te preguntan algo fuera del dominio, redirige amablemente al tema de fitness
- No das diagnósticos médicos ni reemplazas a un profesional de salud"""


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
        user_msg = f"""Analiza el estado del día de {datos['nombre']} y da un consejo personalizado:

- Horas de sueño: {datos['sueno']}h
- Estado de ánimo: {datos['animo']}/10
- Nivel de energía: {datos['energia']}/10
- Nivel de estrés: {datos['estres']}/10
- Tiempo en redes sociales: {datos['redes']} minutos
- Tazas de café: {datos['cafe']}
- Ejercicio hoy: {datos['ejercicio']}
- Probabilidad de cumplir hábito (modelo IA): {prob_pct}%

Da un consejo específico, accionable y motivador en máximo 3 oraciones. 
Menciona el factor más crítico de su día y qué hacer al respecto.
Usa 1-2 emojis relevantes."""

        return self._llamar_chat(SYSTEM_TRACKITO, user_msg,
                                 fallback=self._consejo_local(datos, probabilidad))

    def generar_rutina(self, datos: dict) -> str:
        if not self.disponible:
            return self._rutina_local(datos)

        lesion_txt = (
            f"IMPORTANTE - Lesión/zona a evitar: {datos['lesiones']}. "
            f"Sustituye cualquier ejercicio que la afecte por una alternativa segura."
            if datos["lesiones"].lower() not in ("ninguna", "none", "no", "n/a", "")
            else "Sin lesiones reportadas."
        )

        config_map = {
            "Ganar músculo":       ("4 series × 8-12 reps", "60-90 segundos"),
            "Perder grasa":        ("3 series × 15-20 reps", "30-45 segundos"),
            "Mejorar resistencia": ("3 series × 20-25 reps", "30 segundos"),
            "Mantenimiento":       ("3 series × 12-15 reps", "60 segundos"),
        }
        series, descanso = config_map.get(datos["objetivo"], ("3 series × 12 reps", "60 segundos"))

        user_msg = f"""Crea una rutina de gimnasio semanal COMPLETA y DETALLADA para {datos['nombre']}.

PERFIL DEL USUARIO:
- Objetivo principal: {datos['objetivo']}
- Nivel de experiencia: {datos['nivel']}
- Días disponibles para entrenar: {datos['dias']} días por semana
- Equipamiento disponible: {datos['equipamiento']}
- Duración de cada sesión: {datos['tiempo']} minutos
- Grupo muscular a priorizar: {datos['musculo']}
- {lesion_txt}

CONFIGURACIÓN BASE:
- Series y repeticiones: {series}
- Descanso entre series: {descanso}

INSTRUCCIONES OBLIGATORIAS:
1. Crea exactamente {datos['dias']} días de entrenamiento con nombres descriptivos del split
2. Cada día debe tener entre 5 y 7 ejercicios REALES y ESPECÍFICOS (no genéricos)
3. Para CADA ejercicio incluye OBLIGATORIAMENTE:
   • Nombre exacto del ejercicio
   • Series × repeticiones específicas
   • Tiempo de descanso
   • Descripción técnica: posición inicial, movimiento, músculo principal trabajado y error común a evitar
4. Si el equipamiento es "Peso corporal", NO uses mancuernas, barras ni máquinas
5. Si el equipamiento es "Mancuernas y barra en casa", no uses máquinas de cable ni poleas
6. Adapta la complejidad al nivel:
   - Principiante: movimientos básicos, rango completo, sin técnicas avanzadas
   - Intermedio: compuestos + aislamiento, variantes moderadas
   - Avanzado: superseries, drop sets, variantes unilaterales, técnicas de intensidad
7. Añade volumen extra en el grupo muscular priorizado
8. Al final incluye la sección RECOMENDACIONES con:
   - Nutrición específica para el objetivo
   - Protocolo de descanso y recuperación
   - Plan de progresión para las próximas 4 semanas

FORMATO EXACTO:
📅 DÍA [N] — [Nombre del split] | [Grupos musculares]

🔹 [Nombre del ejercicio] — [X series × Y reps] | Descanso: [tiempo]
   📌 Técnica: [posición inicial]. [movimiento principal]. Trabaja: [músculo]. Error común: [error a evitar].

[repite para cada ejercicio del día]

---

💊 RECOMENDACIONES PERSONALIZADAS PARA {datos['objetivo'].upper()}
🥩 Nutrición: [consejo específico con números concretos]
😴 Recuperación: [protocolo de descanso]
📈 Progresión semanas 1-4: [plan concreto de progresión]"""

        return self._llamar_chat(SYSTEM_TRACKITO, user_msg,
                                 fallback=self._rutina_local(datos))

    def chat_libre(self, pregunta: str, nombre: str) -> str:
        if not self.disponible:
            return (
                "⚠️ El servicio de IA no está disponible ahora mismo.\n\n"
                "Puedo ayudarte con el análisis de hábitos o generarte una rutina. "
                "Elige una opción del menú principal."
            )

        user_msg = f"{nombre} pregunta: {pregunta}"
        return self._llamar_chat(
            SYSTEM_TRACKITO,
            user_msg,
            fallback="💪 En este momento el servicio no está disponible. Intenta de nuevo en unos segundos."
        )

    # ------------------------------------------------------------------
    # Llamadas a la API
    # ------------------------------------------------------------------

    def _llamar(self, prompt: str, fallback: str) -> str:
        try:
            resp = self._cliente.chat.completions.create(
                model=self.MODELO,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2048,
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
                max_tokens=2048,
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
