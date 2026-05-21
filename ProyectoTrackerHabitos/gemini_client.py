"""
Cliente de Gemini para generar consejos y rutinas en lenguaje natural.
Si la API key no está configurada, usa respuestas de fallback locales.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# En Vercel las variables ya están en el entorno del proceso.
# override=False asegura que load_dotenv no pise esas variables con el .env local.
load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=False)


class GeminiClient:

    # Modelos correctos para API v1beta
    # Usar las versiones específicas con número de versión
    MODELOS_DISPONIBLES = [
        "gemini-2.0-flash",         # Modelo más nuevo
        "gemini-1.5-flash-001",     # Versión específica 1.5
        "gemini-1.5-pro-001",       # Versión específica pro
        "gemini-pro",               # Fallback clásico
    ]

    def __init__(self, modelo=None):
        self.api_key    = os.getenv("GEMINI_API_KEY", "")
        self.disponible = False
        self._cliente   = None
        self._modelo_activo = modelo  # Permite override en tests
        self._inicializar()

    def _inicializar(self):
        if not self.api_key or self.api_key == "pega_tu_key_aqui":
            print("⚠️  Gemini: API key no configurada. Usando respuestas locales.")
            return
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            # Si ya se especificó un modelo, usarlo directamente
            if self._modelo_activo:
                try:
                    self._cliente = genai.GenerativeModel(self._modelo_activo)
                    self.disponible = True
                    print(f"✅ Gemini conectado correctamente con modelo: {self._modelo_activo}")
                    return
                except Exception as e:
                    print(f"⚠️  Modelo especificado {self._modelo_activo} no disponible: {str(e)[:100]}")
                    # Continuar intentando con otros modelos
            
            # Intentar con los modelos disponibles en orden de preferencia
            for modelo in self.MODELOS_DISPONIBLES:
                try:
                    print(f"🔍 Intentando con modelo: {modelo}")
                    cliente = genai.GenerativeModel(modelo)
                    # Verificar que funciona con una prueba rápida
                    cliente.generate_content("Prueba")
                    self._cliente = cliente
                    self._modelo_activo = modelo
                    self.disponible = True
                    print(f"✅ Gemini conectado correctamente con modelo: {modelo}")
                    return
                except Exception as modelo_error:
                    error_msg = str(modelo_error).lower()
                    if "429" in error_msg or "quota" in error_msg:
                        print(f"⚠️  Modelo {modelo} rechazado: CUOTA AGOTADA")
                    else:
                        print(f"⚠️  Modelo {modelo} no disponible: {str(modelo_error)[:80]}")
                    continue
            
            # Si ningún modelo funcionó
            print("❌ No se pudo conectar a ningún modelo de Gemini")
            print("💡 Soluciones:")
            print("   1. Crea una NUEVA API key en: https://aistudio.google.com")
            print("   2. Guárdala en el .env como: GEMINI_API_KEY=tu_nueva_key")
            print("   3. Asegúrate de que tu plan tenga cuota disponible")
            print("   4. Si todo falla, el app usará respuestas locales")
            
        except Exception as e:
            print(f"⚠️  Error al conectar Gemini: {e}")

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
            f"⚠️ Lesión a considerar: {datos['lesiones']}. Sustituye o adapta cualquier ejercicio que la afecte."
            if datos["lesiones"].lower() not in ("ninguna", "none", "no", "n/a", "")
            else "Sin lesiones reportadas."
        )

        # Configuración de series/reps según objetivo
        config_map = {
            "Ganar músculo":       "4 series × 8-12 reps | Descanso: 60-90s entre series",
            "Perder grasa":        "3 series × 15-20 reps | Descanso: 30-45s entre series",
            "Mejorar resistencia": "3 series × 20-25 reps | Descanso: 30s entre series",
            "Mantenimiento":       "3 series × 12-15 reps | Descanso: 60s entre series",
        }
        config_series = config_map.get(datos["objetivo"], "3 series × 12 reps | Descanso: 60s")

        prompt = f"""Eres un entrenador personal experto. Genera una rutina de gimnasio semanal COMPLETA y DETALLADA para {datos['nombre']}.

═══════════════════════════════
PERFIL
═══════════════════════════════
• Objetivo: {datos['objetivo']}
• Nivel: {datos['nivel']}
• Días de entrenamiento: {datos['dias']} por semana
• Equipamiento disponible: {datos['equipamiento']}
• Tiempo por sesión: {datos['tiempo']} minutos
• Músculo a priorizar: {datos['musculo']}
• {lesion_txt}
• Configuración base: {config_series}

═══════════════════════════════
INSTRUCCIONES OBLIGATORIAS
═══════════════════════════════
1. Crea exactamente {datos['dias']} días de entrenamiento, distribuidos inteligentemente según el objetivo y los grupos musculares.
2. Cada día debe tener entre 5 y 7 ejercicios REALES y ESPECÍFICOS (no genéricos).
3. Para cada ejercicio incluye OBLIGATORIAMENTE:
   - Nombre exacto del ejercicio
   - Series × repeticiones adaptadas al objetivo
   - Tiempo de descanso
   - Una descripción técnica breve de ejecución (posición, movimiento clave, músculo que trabaja)
4. Adapta los ejercicios al equipamiento: si es "Peso corporal" NO uses mancuernas ni barras.
5. Adapta la dificultad al nivel:
   - Principiante: movimientos básicos, rango de movimiento completo, sin técnicas avanzadas
   - Intermedio: ejercicios compuestos + aislamiento, variantes moderadas
   - Avanzado: técnicas como drop sets, superseries, variantes unilaterales
6. Prioriza el músculo indicado añadiendo un ejercicio extra o más volumen en ese grupo.

═══════════════════════════════
FORMATO EXACTO DE RESPUESTA
═══════════════════════════════
Usa EXACTAMENTE este formato para cada día:

📅 DÍA [número] — [Nombre del split] ([grupos musculares])

🔹 [Nombre del ejercicio] — [X series × Y reps] | Descanso: [Xs]
   📌 [Descripción técnica: cómo ejecutarlo, qué músculo trabaja, punto clave de forma]

[repite para cada ejercicio]

---

Al final de TODOS los días, agrega esta sección:

💊 RECOMENDACIONES PARA {datos['objetivo'].upper()}
🥩 Nutrición: [consejo nutricional específico para el objetivo]
😴 Descanso: [consejo de recuperación y sueño]
📈 Progresión: [cómo avanzar semana a semana]

Responde completamente en español. Sé específico, práctico y motivador."""

        return self._llamar(prompt, fallback=self._rutina_local(datos))

    def chat_libre(self, pregunta: str, nombre: str) -> str:
        """
        Modo conversación libre sobre gym y hábitos saludables.
        Gemini responde cualquier pregunta dentro del dominio.
        """
        if not self.disponible:
            return (
                "⚠️ Gemini no está disponible ahora mismo.\n\n"
                "Puedo ayudarte con el análisis de hábitos o generarte una rutina. "
                "Elige una opción del menú principal."
            )

        prompt = f"""Eres Trackito, un asistente experto en fitness, gimnasio y hábitos saludables. 
Tu personalidad es motivadora, directa y cercana. Usas emojis con moderación.

El usuario se llama {nombre}.

REGLAS ESTRICTAS:
- Solo respondes preguntas sobre: ejercicio, gym, nutrición deportiva, hábitos saludables, sueño, estrés, bienestar físico y mental relacionado con el fitness.
- Si te preguntan algo fuera de ese dominio, responde amablemente que solo puedes ayudar con temas de fitness y hábitos saludables, y sugiere qué podrías responderle.
- Sé específico y práctico. Si te preguntan por un ejercicio, explica cómo hacerlo, músculos que trabaja y errores comunes.
- Respuestas concisas: máximo 5-6 líneas salvo que la pregunta requiera más detalle.
- Responde siempre en español.

Pregunta de {nombre}: {pregunta}"""

        return self._llamar(prompt, fallback=(
            "💪 Puedo responder preguntas sobre ejercicios, nutrición y hábitos saludables. "
            "En este momento Gemini no está disponible, pero puedo generarte una rutina completa "
            "o analizar tus hábitos del día desde el menú principal."
        ))

    def _llamar(self, prompt: str, fallback: str) -> str:
        if not self._cliente:
            print("⚠️  Cliente Gemini no inicializado, usando fallback local.")
            return fallback
        
        try:
            respuesta = self._cliente.generate_content(prompt)
            return respuesta.text.strip()
        except Exception as e:
            error_str = str(e).lower()
            print(f"⚠️  Error Gemini: {error_str[:150]}")
            
            # Error 429: Quota excedida
            if "429" in error_str or "quota" in error_str or "exceeded" in error_str:
                print("💡 Tu cuota de API se agotó. Usa una clave nueva en .env")
                print("   1. Crea una NUEVA API key en: https://aistudio.google.com")
                print("   2. Reemplaza el GEMINI_API_KEY en tu .env")
                return fallback
            
            # Error 404: Modelo no encontrado
            if "404" in error_str or "not found" in error_str:
                print(f"⚠️  Modelo actual ({self._modelo_activo}) no está disponible en v1beta")
                print("🔄 Usando respuestas locales por ahora...")
                return fallback
            
            # Otro error: usar fallback
            print(f"💡 Usando respuestas locales (error: {error_str[:80]})")
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
        """Rutina con ejercicios reales cuando Gemini no está disponible."""
        nombre    = datos["nombre"]
        objetivo  = datos["objetivo"]
        dias      = datos["dias"]
        nivel     = datos["nivel"]
        equipo    = datos["equipamiento"]
        musculo   = datos["musculo"]

        gym = equipo == "Gimnasio completo"
        man = equipo == "Mancuernas y barra"
        bw  = equipo == "Peso corporal"

        config_map = {
            "Ganar músculo":       ("4×8-12", "60-90s"),
            "Perder grasa":        ("3×15-20", "30-45s"),
            "Mejorar resistencia": ("3×20-25", "30s"),
            "Mantenimiento":       ("3×12-15", "60s"),
        }
        series_reps, descanso = config_map.get(objetivo, ("3×12", "60s"))

        def ej(nombre_ej, desc):
            return f"🔹 **{nombre_ej}** — {series_reps} | Descanso: {descanso}\n   📌 {desc}"

        # ── Banco de ejercicios por grupo y equipamiento ──────────────
        if gym or man:
            pecho = [
                ej("Press de banca plano", "Acostado en banco, baja la barra al pecho y empuja. Trabaja pectoral mayor."),
                ej("Press inclinado con mancuernas", "Banco a 30-45°, empuja las mancuernas hacia arriba. Activa pectoral superior."),
                ej("Aperturas en polea baja", "De pie, lleva los cables hacia arriba en arco. Estira y contrae el pectoral."),
                ej("Fondos en paralelas", "Baja el cuerpo doblando codos a 90° y empuja. Pectoral inferior y tríceps."),
            ]
            espalda = [
                ej("Dominadas con agarre prono", "Cuelga de la barra, lleva el pecho hacia ella. Trabaja dorsal y bíceps."),
                ej("Remo con barra", "Espalda recta a 45°, lleva la barra al abdomen. Activa dorsal y romboides."),
                ej("Remo en polea baja", "Sentado, tira del cable hacia el abdomen. Trabaja dorsal medio y romboides."),
                ej("Jalón al pecho", "Sentado, tira de la barra hacia el pecho. Trabaja dorsal ancho."),
            ]
            piernas = [
                ej("Sentadilla con barra", "Pies a ancho de hombros, baja hasta paralelo. Cuádriceps, glúteos y core."),
                ej("Peso muerto rumano", "Espalda recta, baja la barra deslizando por las piernas. Isquiotibiales y glúteos."),
                ej("Prensa de piernas", "Pies en la plataforma, baja hasta 90° y empuja. Cuádriceps y glúteos."),
                ej("Curl femoral en máquina", "Boca abajo, lleva los talones hacia los glúteos. Isquiotibiales."),
                ej("Elevación de talones de pie", "De pie, sube en puntillas lentamente. Gemelos."),
            ]
            hombros = [
                ej("Press militar con barra", "De pie o sentado, empuja la barra sobre la cabeza. Deltoides anterior y medio."),
                ej("Elevaciones laterales", "Brazos ligeramente flexionados, sube hasta la altura del hombro. Deltoides medio."),
                ej("Face pulls en polea", "Tira del cable hacia la cara separando los codos. Deltoides posterior y manguito."),
            ]
            brazos = [
                ej("Curl con barra EZ", "Codos pegados al cuerpo, sube la barra hasta los hombros. Bíceps braquial."),
                ej("Curl martillo", "Agarre neutro, sube la mancuerna. Bíceps y braquiorradial."),
                ej("Extensión de tríceps en polea", "Codos fijos, extiende el cable hacia abajo. Tríceps."),
                ej("Press francés", "Acostado, baja la barra a la frente y extiende. Tríceps largo."),
            ]
        else:  # Peso corporal
            pecho = [
                ej("Flexiones estándar", "Manos a ancho de hombros, baja el pecho al suelo y empuja. Pectoral y tríceps."),
                ej("Flexiones inclinadas", "Manos elevadas en una silla, baja el pecho. Activa pectoral inferior."),
                ej("Flexiones declinadas", "Pies elevados, manos en el suelo. Trabaja pectoral superior."),
                ej("Fondos entre sillas", "Manos en dos sillas, baja doblando codos. Pectoral inferior y tríceps."),
            ]
            espalda = [
                ej("Dominadas", "Cuelga de una barra, lleva el pecho hacia ella. Dorsal y bíceps."),
                ej("Remo invertido", "Bajo una mesa, tira del cuerpo hacia arriba. Dorsal y romboides."),
                ej("Superman", "Boca abajo, levanta brazos y piernas simultáneamente. Erector espinal."),
            ]
            piernas = [
                ej("Sentadilla con peso corporal", "Pies a ancho de hombros, baja hasta paralelo. Cuádriceps y glúteos."),
                ej("Zancadas alternadas", "Da un paso al frente y baja la rodilla trasera. Cuádriceps y glúteos."),
                ej("Sentadilla búlgara", "Pie trasero elevado, baja la rodilla delantera. Cuádriceps y glúteos."),
                ej("Puente de glúteos", "Acostado, sube las caderas apretando glúteos. Glúteos e isquiotibiales."),
                ej("Elevación de talones", "De pie, sube en puntillas lentamente. Gemelos."),
            ]
            hombros = [
                ej("Pike push-up", "Caderas arriba en V invertida, baja la cabeza al suelo. Deltoides anterior."),
                ej("Plancha lateral con rotación", "Plancha lateral, rota el brazo libre bajo el cuerpo. Hombros y core."),
            ]
            brazos = [
                ej("Flexiones diamante", "Manos juntas formando un diamante. Tríceps y pectoral interno."),
                ej("Curl con mochila", "Siéntate, cuelga una mochila del pie y flexiona la rodilla. Bíceps femoral."),
            ]

        # ── Construir días según cantidad ─────────────────────────────
        grupos = {
            "Pecho": pecho, "Espalda": espalda, "Piernas": piernas,
            "Hombros": hombros, "Brazos": brazos
        }

        core = [
            ej("Plancha frontal", "Apoya antebrazos y pies, mantén el cuerpo recto. Core completo."),
            ej("Crunch abdominal", "Acostado, sube el torso contrayendo el abdomen. Recto abdominal."),
            ej("Elevación de piernas", "Acostado, sube las piernas rectas a 90°. Abdomen inferior."),
        ]

        if dias <= 2:
            dias_rutina = [
                ("1", "Cuerpo completo A", pecho[:2] + espalda[:2] + piernas[:2] + core[:1]),
                ("2", "Cuerpo completo B", piernas[2:4] + hombros[:2] + brazos[:2] + core[1:2]),
            ]
        elif dias == 3:
            dias_rutina = [
                ("1", "Empuje — Pecho · Hombros · Tríceps", pecho + hombros[:2] + brazos[2:]),
                ("2", "Jale — Espalda · Bíceps", espalda + brazos[:2]),
                ("3", "Piernas y Core", piernas + core),
            ]
        elif dias == 4:
            dias_rutina = [
                ("1", "Pecho y Tríceps", pecho + brazos[2:]),
                ("2", "Espalda y Bíceps", espalda + brazos[:2]),
                ("3", "Piernas", piernas),
                ("4", "Hombros y Core", hombros + core),
            ]
        else:
            dias_rutina = [
                ("1", "Pecho", pecho + [brazos[2]]),
                ("2", "Espalda", espalda + [brazos[0]]),
                ("3", "Piernas", piernas),
                ("4", "Hombros", hombros + core[:1]),
                ("5", "Brazos y Core", brazos + core[1:]),
            ]

        # Añadir ejercicio extra del músculo priorizado
        extra_map = {
            "Pecho": pecho[-1], "Espalda": espalda[-1], "Piernas": piernas[-1],
            "Hombros": hombros[-1], "Brazos": brazos[-1]
        }

        resultado = f"⚙️ **Configuración:** {series_reps} | Descanso: {descanso}\n\n"

        for num, nombre_dia, ejercicios in dias_rutina[:dias]:
            resultado += f"📅 **DÍA {num} — {nombre_dia}**\n\n"
            for e in ejercicios:
                resultado += e + "\n\n"

        # Recomendaciones finales
        consejos = {
            "Ganar músculo":       ("Consume 1.6–2g de proteína por kg de peso. Prioriza carnes magras, huevos y legumbres.",
                                    "Duerme 7–9h. El músculo crece durante el descanso, no en el gym.",
                                    "Aumenta el peso o las reps cada semana. La progresión es clave."),
            "Perder grasa":        ("Mantén un déficit de 300–500 kcal. No elimines proteína, reduce carbohidratos.",
                                    "El descanso evita el catabolismo muscular. No entrenes más de 5 días seguidos.",
                                    "Añade 20–30 min de cardio moderado los días de descanso."),
            "Mejorar resistencia": ("Hidratación constante. Consume carbohidratos complejos antes de entrenar.",
                                    "Descansa al menos 48h entre sesiones del mismo grupo muscular.",
                                    "Reduce el descanso entre series 5 segundos cada semana."),
            "Mantenimiento":       ("Mantén un balance calórico. Varía las fuentes de proteína.",
                                    "Alterna días de alta y baja intensidad para evitar el sobreentrenamiento.",
                                    "Cambia los ejercicios cada 4–6 semanas para evitar el estancamiento."),
        }
        nut, desc, prog = consejos.get(objetivo, ("Come bien.", "Descansa.", "Progresa."))

        resultado += (
            f"---\n\n"
            f"💊 **RECOMENDACIONES PARA {objetivo.upper()}**\n\n"
            f"🥩 **Nutrición:** {nut}\n\n"
            f"😴 **Descanso:** {desc}\n\n"
            f"📈 **Progresión:** {prog}"
        )

        return resultado
