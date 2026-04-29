import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from dataBase import conectar


class ModeloPrediccion:

    def __init__(self):
        self.modelo = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )

    def entrenar(self):

        conexion = conectar()

        query = """
        SELECT
            horas_sueno,
            estado_animo,
            energia,
            estres,
            tiempo_redes,
            ejercicio,
            cafe_tazas,
            completado
        FROM registros_diarios
        """

        df = pd.read_sql(query, conexion)

        X = df.drop("completado", axis=1)
        y = df["completado"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            random_state=42
        )

        self.modelo.fit(X_train, y_train)

        predicciones = self.modelo.predict(X_test)

        precision = accuracy_score(y_test, predicciones)

        print("✅ Modelo entrenado")
        print("🎯 Precisión:", round(precision * 100, 2), "%")

        conexion.close()

    def predecir(self, horas_sueno, estado_animo, energia,
                 estres, tiempo_redes, ejercicio, cafe_tazas):

        datos = [[
            horas_sueno,
            estado_animo,
            energia,
            estres,
            tiempo_redes,
            ejercicio,
            cafe_tazas
        ]]

        resultado = self.modelo.predict(datos)[0]
        probabilidad = self.modelo.predict_proba(datos)[0][1]

        return resultado, probabilidad