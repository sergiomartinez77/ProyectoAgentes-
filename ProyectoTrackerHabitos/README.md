# 🤖 Tracker IA — Chatbot de Hábitos

Chatbot inteligente que analiza tus hábitos diarios y genera rutinas de gimnasio personalizadas.

Usa un modelo **híbrido**:
- **RandomForest** (scikit-learn) → predice la probabilidad de cumplir tu hábito con base en tus datos del día
- **Gemini API** (Google) → genera consejos y rutinas en lenguaje natural

---

## ✨ Funcionalidades

- 📊 **Análisis de hábitos**: ingresa tus datos del día (sueño, ánimo, energía, estrés, etc.) y el modelo predice tu probabilidad de éxito
- 🏋️ **Rutina de gimnasio**: genera una rutina semanal personalizada según tu objetivo, nivel y equipamiento
- 💬 **Interfaz de chat**: conversación fluida con botones de respuesta rápida
- 🔄 **Sesiones independientes**: cada usuario tiene su propio estado de conversación

---

## 🗂️ Estructura del proyecto

```
ProyectoTrackerHabitos/
├── app.py                  # Servidor Flask + endpoints API
├── ia2.py                  # Orquestador del chatbot (flujos de conversación)
├── modelo_prediccion.py    # Modelo RandomForest
├── gemini_client.py        # Cliente de Gemini API
├── generar_datos.py        # Generador del CSV de entrenamiento
├── templates/
│   └── index.html          # Interfaz del chatbot
├── static/
│   └── style.css           # Estilos
├── .env.example            # Plantilla de variables de entorno
└── requirements.txt        # Dependencias
```

---

## 🚀 Cómo correrlo localmente

### 1. Clonar el repositorio

```bash
git clone https://github.com/sergiomartinez77/ProyectoAgentes-.git
cd ProyectoAgentes-/ProyectoTrackerHabitos
```

### 2. Crear y activar un entorno virtual (recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Correr la aplicación

```bash
python app.py
```

Abre tu navegador en: **http://127.0.0.1:5000**

---

## 📦 Dependencias principales

| Librería | Uso |
|---|---|
| Flask | Servidor web y API REST |
| scikit-learn | Modelo RandomForest |
| pandas | Manejo del CSV de entrenamiento |
| google-generativeai | Cliente de Gemini API |
| python-dotenv | Carga de variables de entorno |

---

## 🔌 Endpoints de la API

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Interfaz del chatbot |
| `POST` | `/api/chat` | Enviar mensaje al bot `{ "mensaje": "texto" }` |
| `POST` | `/api/reset` | Reiniciar la sesión actual |

---

## 🧠 Cómo funciona el modelo híbrido

```
Usuario responde preguntas
          ↓
    ia2.py (orquestador)
     ↓              ↓
RandomForest      Gemini API
(probabilidad     (consejo/rutina
 numérica)         en lenguaje natural)
     ↓              ↓
      Respuesta final al usuario
```

El RandomForest se entrena con variables como horas de sueño, estado de ánimo, energía, estrés, tiempo en redes, café y ejercicio para predecir si el usuario completará su hábito. Gemini toma esa predicción y genera un mensaje personalizado.

---

## 📊 Reentrenar con tus propios datos

Reemplaza `datos_entrenamiento.csv` con tu propio archivo manteniendo estas columnas:

```
horas_sueno, estado_animo, energia, estres, tiempo_redes, ejercicio, cafe_tazas, completado
```

El modelo se reentrena automáticamente cada vez que inicias la aplicación.
