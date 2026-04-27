import json
from habito import Habito
from agente import Agente

ARCHIVO_DATOS = "data.json"

def cargar_datos():
    try:
        with open(ARCHIVO_DATOS, "r") as f:
            return json.load(f)
    except:
        return {}

def guardar_datos(datos):
    with open(ARCHIVO_DATOS, "w") as f:
        json.dump(datos, f)

def main():
    datos = cargar_datos()
    agente = Agente()

    print("📂 Hábitos registrados:", list(datos.keys()))

    nombre = input("Nombre del hábito: ")

    if nombre not in datos:
        print("🆕 Creando nuevo hábito...")
        datos[nombre] = []
    else:
        print("🔁 Continuando hábito existente...")
        

        cumplido = input("¿Cumpliste el hábito hoy? (s/n): ").lower() == "s"
        datos[nombre].append(1 if cumplido else 0)

        guardar_datos(datos)

        habito = Habito(nombre)
        habito.historial = datos[nombre]

        

        print("\n📊 Historial:", habito.historial)
        print(f"📈 Progreso: {sum(habito.historial)}/{len(habito.historial)} días cumplidos")

        sugerencia = agente.analizar(habito)
        print("🤖 Agente dice:", sugerencia)


if __name__ == "__main__":
        main()