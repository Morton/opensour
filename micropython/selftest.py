from picozero import DistanceSensor, LED, pico_led, pinout, pico_temp_sensor
from time import sleep
from machine import Pin
from dht import DHT22
import network

def countdown(prefix, n):
    for x in range(n):
        print(prefix + str(n - x) + "s")
        sleep(1)
    return

print("   ____                    _____                  ")
print("  / __ \                  / ____|                 ")
print(" | |  | |_ __   ___ _ __ | (___   ___  _   _ _ __ ")
print(" | |  | | '_ \ / _ \ '_ \ \___ \ / _ \| | | | '__|")
print(" | |__| | |_) |  __/ | | |____) | (_) | |_| | |   ")
print("  \____/| .__/ \___|_| |_|_____/ \___/ \__,_|_|   ")
print("        | |                                       ")
print("        |_|  Hardware Self-Test                   ")
print("")

print("[PICO_LED] Testing onboard LED")
print("[PICO_LED]   LED on")
pico_led.on()
countdown("[PICO_LED]     ", 3)
pico_led.off()
print()

print("[DUAL_LED] Testing dual LED")
green = LED(13)
red = LED(14)
print("[DUAL_LED]   LED should be green")
green.on()
countdown("[DUAL_LED]     ", 3)
green.off()
print("[DUAL_LED]   LED should be red")
red.on()
countdown("[DUAL_LED]     ", 3)
red.off()
print()

print("[DHT22] Testing temperature sensor")
dht22_sensor = DHT22(Pin(28, Pin.IN,Pin.PULL_UP))
dht22_sensor.measure()
temp = dht22_sensor.temperature()
humi = dht22_sensor.humidity()
print("[DHT22]   temperature:", temp, '°C')
print("[DHT22]   humidity:", humi, '%')
print("[DHT22]   internal temperature for comparison:", pico_temp_sensor.temp, '°C')
countdown("[DHT22]     ", 3)
print()

print("[HC-SR04] Testing distance sensor")
ds = DistanceSensor(echo=6, trigger=7)
print("[HC-SR04]   distance:", ds.distance)
print("[HC-SR04]     10s")
sleep(2)
print("[HC-SR04]   distance:", ds.distance)
print("[HC-SR04]     8s")
sleep(2)
print("[HC-SR04]   distance:", ds.distance)
print("[HC-SR04]     6s")
sleep(2)
print("[HC-SR04]   distance:", ds.distance)
print("[HC-SR04]     4s")
sleep(2)
print("[HC-SR04]   distance:", ds.distance)
print("[HC-SR04]     2s")
sleep(2)
print("[HC-SR04]   distance:", ds.distance)
print()


print("[WIFI] Testing wifi")
print("[WIFI]   wifi supported by board:", hasattr(network, "WLAN"))
if hasattr(network, "WLAN"):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    wifis = wlan.scan()
    print("[WIFI]   networks found:")
    for wifi in wifis:
        print("[WIFI]     ", wifi[0])
print()
