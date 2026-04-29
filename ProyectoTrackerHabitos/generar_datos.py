import mysql.connector
import random
from datetime import datetime, timedelta

# ==========================================
# CONFIGURACIÓN DE CONEXIÓN
# ==========================================
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Sergioroot123.",
    database="proyecto_tracker"
)

cursor = conexion.cursor()

# ==========================================
# DATOS BASE
# ==========================================
fecha = datetime(2025, 1, 1)

habitos = [
    "Gym",
    "Estudiar",
    "Leer",
    "Meditar",
    "Programar",
    "Caminar"
]

climas = [
    "Soleado",
    "Lluvia",
    "Nublado",
    "Ventoso"
]

# ==========================================
# GENERAR 1000 REGISTROS
# ==========================================
for i in range(1000):

    habito = random.choice(habitos)

    horas_sueno = round(random.uniform(4.0, 9.0), 1)
    estado_animo = random.randint(1, 10)
    energia = random.randint(1, 10)
    estres = random.randint(1, 10)

    clima = random.choice(climas)

    dia_semana = fecha.strftime("%A")

    hora = random.randint(5, 22)
    minuto = random.randint(0, 59)
    hora_registro = f"{hora:02d}:{minuto:02d}:00"

    tiempo_redes = random.randint(0, 300)

    ejercicio = random.choice([0, 1])

    cafe_tazas = random.randint(0, 4)

    # ==========================================
    # LÓGICA PARA DEFINIR SI COMPLETÓ EL HÁBITO
    # ==========================================
    score = 0

    if horas_sueno >= 7:
        score += 2

    if estado_animo >= 6:
        score += 2

    if energia >= 6:
        score += 2

    if estres <= 5:
        score += 2

    if tiempo_redes <= 120:
        score += 1

    if ejercicio == 1:
        score += 1

    if cafe_tazas <= 2:
        score += 1

    completado = 1 if score >= 6 else 0

    # ==========================================
    # INSERT SQL
    # ==========================================
    sql = """
    INSERT INTO registros_diarios
    (
        fecha,
        habito,
        completado,
        horas_sueno,
        estado_animo,
        energia,
        estres,
        clima,
        dia_semana,
        hora_registro,
        tiempo_redes,
        ejercicio,
        cafe_tazas
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    valores = (
        fecha.strftime("%Y-%m-%d"),
        habito,
        completado,
        horas_sueno,
        estado_animo,
        energia,
        estres,
        clima,
        dia_semana,
        hora_registro,
        tiempo_redes,
        ejercicio,
        cafe_tazas
    )

    cursor.execute(sql, valores)

    # avanzar 1 día
    fecha += timedelta(days=1)

# ==========================================
# GUARDAR CAMBIOS
# ==========================================
conexion.commit()

print("✅ 1000 registros insertados correctamente.")

cursor.close()
conexion.close()