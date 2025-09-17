# controlador.py
from datetime import datetime
from sensores import sensores_disponibles
from schedule import cargar_programa_desde_csv

class Controlador:
    def __init__(self):
        self.programa_diario = self._cargar_programa()
        
    def _cargar_programa(self):
        programa_list = cargar_programa_desde_csv()
        programa = {}
        for item in programa_list:
            if len(item) == 3:
                dia, sensor, valor = item
                programa[(int(dia), sensor)] = float(valor)
        return programa

    def get_valor_objetivo(self, nombre_sensor):
        dia_del_año = datetime.now().timetuple().tm_yday
        return self.programa_diario.get((dia_del_año, nombre_sensor))

    def generar_respuesta(self, nombre_sensor, valor_actual):
        valor_objetivo = self.get_valor_objetivo(nombre_sensor)
        
        # Nueva línea para imprimir el día actual
        dia_del_año = datetime.now().timetuple().tm_yday
        print(f"[{nombre_sensor}] Hoy es el día {dia_del_año} del año.")

        if valor_objetivo is None:
            return "Sin valor objetivo para hoy"

        diferencia = valor_actual - valor_objetivo
        print(f"[{nombre_sensor}] Valor actual: {valor_actual:.2f}, Objetivo: {valor_objetivo:.2f}")

        if abs(diferencia) <= 0.5:
            return "En objetivo"
        elif diferencia > 0:
            return "Valor alto -> Necesita bajar"
        else:
            return "Valor bajo -> Necesita subir"