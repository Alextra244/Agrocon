# schedule.py
import csv
import os

def cargar_programa_desde_csv(nombre_archivo=""):
    """
    Carga el programa de control diario desde un archivo CSV.
    El formato del archivo debe ser: dia_del_año,nombre_sensor,valor_objetivo
    """
    if (nombre_archivo == ""):
        nombre_archivo = os.path.dirname(os.path.abspath(__file__)) + "/programa_control.csv"

    if not os.path.exists(nombre_archivo):
        print(f"Advertencia: No se encontró el archivo '{nombre_archivo}'. Usando un programa de ejemplo.")
        return [
            (1, "DHT22", 25.0),
            (1, "pH", 6.8)
        ]

    programa = []
    print(f"✅ Archivo '{nombre_archivo}' encontrado. Intentando leer...")
    
    try:
        with open(nombre_archivo, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for i, fila in enumerate(reader):
                if not fila or len(fila) < 3:
                    print(f"Advertencia: La fila {i+1} del CSV está vacía o tiene un formato incorrecto: {fila}")
                    continue
                try:
                    dia = int(fila[0].strip())
                    sensor = fila[1].strip()
                    valor = float(fila[2].strip())
                    programa.append((dia, sensor, valor))
                except (ValueError, IndexError):
                    print(f"Advertencia: Fila {i+1} inválida en el archivo CSV: {fila}. Se ha omitido.")
    except Exception as e:
        print(f"Error al abrir o leer el archivo CSV: {e}")
        print("Usando un programa de ejemplo como alternativa.")
        return [
            (1, "DHT22", 25.0),
            (1, "pH", 6.8)
        ]

    return programa