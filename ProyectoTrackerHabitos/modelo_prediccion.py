"""
Modelo de predicción de hábitos basado en RandomForest.
Se entrena con datos_entrenamiento.csv y predice la probabilidad
de que el usuario complete su hábito hoy.
"""
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

RUTA_CSV = os.path.join(os.path.dirname(__file__), "datos_entrenamiento.csv")

FEATURES = [
    "horas_sueno", "estado_animo", "energia", "estres",
    "tiempo_redes", "ejercicio", "cafe_tazas"
]


class ModeloPrediccion:

    def __init__(self):
        self.modelo    = RandomForestClassifier(n_estimators=100, random_state=42)
        self.entrenado = False

    # ------------------------------------------------------------------
    # Entrenamiento
    # ------------------------------------------------------------------

    def entrenar(self) -> str:
        """
        Carga el CSV, entrena el modelo y devuelve un string con el resultado.
        Si el CSV no existe, genera los datos primero.
        """
        if not os.path.exists(RUTA_CSV):
            self._generar_csv()

        df = pd.read_csv(RUTA_CSV)

        if df.empty or len(df) < 10:
            return "⚠️ No hay suficientes datos para entrenar el modelo."

        X = df[FEATURES]
        y = df["completado"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.modelo.fit(X_train, y_train)
        self.entrenado = True

        precision = accuracy_score(y_test, self.modelo.predict(X_test))
        return f"✅ Modelo entrenado con {len(df)} registros — Precisión: {round(precision * 100, 1)}%"

    # ------------------------------------------------------------------
    # Predicción
    # ------------------------------------------------------------------

    def predecir(self, horas_sueno, estado_animo, energia,
                 estres, tiempo_redes, ejercicio, cafe_tazas) -> tuple[int, float]:
        """
        Devuelve (resultado: 0|1, probabilidad: 0.0–1.0).
        Si el modelo no está entrenado, usa el score de reglas como fallback.
        """
        if not self.entrenado:
            return self._fallback(horas_sueno, estado_animo, energia,
                                  estres, tiempo_redes, ejercicio, cafe_tazas)

        datos = pd.DataFrame([[horas_sueno, estado_animo, energia, estres,
                               tiempo_redes, ejercicio, cafe_tazas]],
                             columns=FEATURES)

        resultado    = int(self.modelo.predict(datos)[0])
        probabilidad = float(self.modelo.predict_proba(datos)[0][1])
        return resultado, probabilidad

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _fallback(self, horas_sueno, animo, energia, estres,
                  redes, ejercicio, cafe) -> tuple[int, float]:
        """Score de reglas como respaldo si el modelo no está listo."""
        score = 50
        score += animo * 2 + energia * 2
        score += 10 if horas_sueno >= 7 else -10
        score += -15 if estres >= 8 else (5 if estres <= 4 else 0)
        score += -10 if redes > 180 else (5 if redes <= 60 else 0)
        score += 8 if ejercicio == 1 else 0
        score += -4 if cafe > 3 else 0
        prob = max(5, min(score, 95)) / 100
        return (1 if prob >= 0.5 else 0), prob

    def _generar_csv(self):
        """Genera el CSV de entrenamiento si no existe."""
        from generar_datos import generar
        generar()
