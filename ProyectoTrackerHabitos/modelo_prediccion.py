"""
Modelo de predicción de hábitos basado en RandomForest.
En producción (Vercel) carga el modelo pre-entrenado desde modelo_habitos.pkl.
En local puede reentrenarse con datos_entrenamiento.csv.
"""
import os
import pandas as pd

RUTA_PKL = os.path.join(os.path.dirname(__file__), "modelo_habitos.pkl")
RUTA_CSV = os.path.join(os.path.dirname(__file__), "datos_entrenamiento.csv")

FEATURES = [
    "horas_sueno", "estado_animo", "energia", "estres",
    "tiempo_redes", "ejercicio", "cafe_tazas"
]


class ModeloPrediccion:

    def __init__(self):
        self.modelo    = None
        self.entrenado = False

    def entrenar(self) -> str:
        """
        Intenta cargar el modelo pre-entrenado (.pkl).
        Si no existe, entrena desde el CSV.
        """
        # 1. Intentar cargar modelo pre-entrenado
        if os.path.exists(RUTA_PKL):
            try:
                import joblib
                self.modelo    = joblib.load(RUTA_PKL)
                self.entrenado = True
                return "✅ Modelo cargado desde archivo pre-entrenado."
            except Exception as e:
                print(f"⚠️ No se pudo cargar el .pkl: {e}")

        # 2. Fallback: entrenar desde CSV
        if not os.path.exists(RUTA_CSV):
            return "⚠️ No se encontró el CSV ni el modelo pre-entrenado. Usando reglas."

        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score

            df = pd.read_csv(RUTA_CSV)
            if df.empty or len(df) < 10:
                return "⚠️ No hay suficientes datos para entrenar."

            X = df[FEATURES]
            y = df["completado"]
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            self.modelo = RandomForestClassifier(n_estimators=100, random_state=42)
            self.modelo.fit(X_train, y_train)
            self.entrenado = True

            precision = accuracy_score(y_test, self.modelo.predict(X_test))
            return f"✅ Modelo entrenado con {len(df)} registros — Precisión: {round(precision * 100, 1)}%"
        except Exception as e:
            return f"⚠️ Error entrenando modelo: {e}. Usando reglas de fallback."

    def predecir(self, horas_sueno, estado_animo, energia,
                 estres, tiempo_redes, ejercicio, cafe_tazas) -> tuple:
        if not self.entrenado or self.modelo is None:
            return self._fallback(horas_sueno, estado_animo, energia,
                                  estres, tiempo_redes, ejercicio, cafe_tazas)

        datos = pd.DataFrame([[horas_sueno, estado_animo, energia, estres,
                               tiempo_redes, ejercicio, cafe_tazas]],
                             columns=FEATURES)
        resultado    = int(self.modelo.predict(datos)[0])
        probabilidad = float(self.modelo.predict_proba(datos)[0][1])
        return resultado, probabilidad

    def _fallback(self, horas_sueno, animo, energia, estres,
                  redes, ejercicio, cafe) -> tuple:
        score = 50
        score += animo * 2 + energia * 2
        score += 10 if horas_sueno >= 7 else -10
        score += -15 if estres >= 8 else (5 if estres <= 4 else 0)
        score += -10 if redes > 180 else (5 if redes <= 60 else 0)
        score += 8 if ejercicio == 1 else 0
        score += -4 if cafe > 3 else 0
        prob = max(5, min(score, 95)) / 100
        return (1 if prob >= 0.5 else 0), prob
