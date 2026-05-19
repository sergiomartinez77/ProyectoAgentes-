"""
Genera 1000 registros sintéticos de hábitos y los guarda en datos_entrenamiento.csv
Ejecutar una sola vez: python generar_datos.py
"""
import random
import csv
import os
from datetime import datetime, timedelta

RUTA_CSV = os.path.join(os.path.dirname(__file__), "datos_entrenamiento.csv")

COLUMNAS = [
    "horas_sueno", "estado_animo", "energia", "estres",
    "tiempo_redes", "ejercicio", "cafe_tazas", "completado"
]

def generar():
    random.seed(42)
    filas = []
    fecha = datetime(2025, 1, 1)

    for _ in range(1000):
        horas_sueno   = round(random.uniform(4.0, 9.0), 1)
        estado_animo  = random.randint(1, 10)
        energia       = random.randint(1, 10)
        estres        = random.randint(1, 10)
        tiempo_redes  = random.randint(0, 300)
        ejercicio     = random.choice([0, 1])
        cafe_tazas    = random.randint(0, 4)

        # Lógica determinista para etiquetar si completó el hábito
        score = 0
        if horas_sueno >= 7:   score += 2
        if estado_animo >= 6:  score += 2
        if energia >= 6:       score += 2
        if estres <= 5:        score += 2
        if tiempo_redes <= 120: score += 1
        if ejercicio == 1:     score += 1
        if cafe_tazas <= 2:    score += 1

        completado = 1 if score >= 6 else 0

        filas.append([
            horas_sueno, estado_animo, energia, estres,
            tiempo_redes, ejercicio, cafe_tazas, completado
        ])

        fecha += timedelta(days=1)

    with open(RUTA_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNAS)
        writer.writerows(filas)

    print(f"✅ {len(filas)} registros guardados en {RUTA_CSV}")


if __name__ == "__main__":
    generar()
