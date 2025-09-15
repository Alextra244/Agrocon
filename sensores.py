import random

def leer_sensor_dht22():
    return random.uniform(15, 35)

def leer_sensor_ds18b20():
    return random.uniform(10, 30)

def leer_sensor_ph():
    return random.uniform(5.5, 8.5)

sensores_disponibles = {
    "DHT22": leer_sensor_dht22,
    "DS18B20": leer_sensor_ds18b20,
    "pH": leer_sensor_ph
}
