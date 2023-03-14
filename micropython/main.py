import network
import socket
from time import sleep
from picozero import DistanceSensor, LED, pico_led
import machine
from machine import Timer, Pin
from dht import DHT22
import re
import urequests as requests

hostname = 'opensour'
network.hostname(hostname)

green = LED(13)
red = LED(14)

ds = DistanceSensor(echo=6, trigger=7)
dht22_sensor = DHT22(Pin(28, Pin.IN,Pin.PULL_UP))

wlan = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)

def connect(ssid, password):
    wlan.active(True)
    wlan.connect(ssid, password)
    
    i = 0
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        pico_led.toggle()
        sleep(1)
        i += 1
        if i > 30:
            return None
        
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def connect_AF():
    mac = ap_if.config('mac')
    ssid = network.hostname() + '_' + hex(mac[4])[2:] + hex(mac[5])[2:]
    ap_if.config(
        ssid=ssid,
        security=0)
    ap_if.active(True)
    ip = ap_if.ifconfig()[0]
    hostname = network.hostname()
    print(f'Open on {ip} as {hostname}')
    return ip

def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    try:
        connection.bind(address)
    except OSError:
        machine.reset()
    connection.listen(1)
    return connection

def webpage_form():
    if wifi_ok:
        wifi_status = "<font color=\"Lime\">ok</font>"
    else:
        wifi_status = "<font color=\"Red\">failed</font>"
    if request_ok:
        aws_status = "<font color=\"Lime\">ok</font>"
    else:
        aws_status = "<font color=\"Red\">failed</font>"
    #Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            <body>
            <form action="/setup">
                <details>
                    <summary>Wifi configuration (STATUS: {wifi_status})</summary>
                    <p>Wifi network name: <input type="text" name="network" value="{ssid}" /></p>
                    <p>Network password: <input type="password" name="password" /></p>
                </details>
                <details>
                    <summary>AWS configuration (STATUS: {aws_status})</summary>
                    <p>Host string: <input type="text" name="host" value="{host}" /></p>
                </details>
                <p><input type="submit" value="Update" /></p>
            </form>
            </body>
            </html>
            """
    return str(html)

def webpage_done():
    #Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            <body>
            Connecting...
            </body>
            </html>
            """
    return str(html)

def serve(connection):
    #Start a web server
    state = 'OFF'
    temperature = 0
    while True:
        print(connection)
        client = connection.accept()[0]
        print(client)
        request = client.recv(1024)
        request = str(request)
        try:
            url = request.split()[1]
        except IndexError:
            pass
        url = url.replace("%3A", ":")
        url = url.replace("%2F", "/")
        url = url.replace("%3F", "?")
        url = url.replace("%3D", "=")
        x = re.search("/setup\?network=(.*?)&password=(.*?)&host=(.*)", url)
        if x != None:
            network_name = x.group(1)
            network_password = x.group(2)
            if network_password == "":
                network_password = password
            network_host = x.group(3)
            file = open("wifi_data.txt", "w")
            file.write(network_name + "\n" + network_password + "\n" + network_host)
            file.close()
            html = webpage_done()
            client.send(html)
            client.close()
            break
        else:
            html = webpage_form()
            client.send(html)
            client.close()
            
def metricLoop(timer):
    red.off()
    green.brightness = 0.2
    url = host
    dist = ds.distance
#    print("[HC-SR04] distance:", dist)
    if dist != None:
        url += "&distance=" + str(dist * 100)
    dht22_sensor.measure()
    temp = dht22_sensor.temperature()
    humi = dht22_sensor.humidity()
#    print("[DHT22] temperature:", temp, '°C')
#    print("[DHT22] humidity:", humi, '%')
    if humi != None:
        url += "&humidity=" + str(humi)
    if temp != None:
        url += "&temperature=" + str(temp)
    print(url)
    try: 
        request = requests.get(url)
        if request.status_code != 200:
            print("Error during request")
            print(request.status_code)
            print(request.content)
            red.on()
        request.close()
    except OSError as e:
        red.on()
        print(e)
    green.brightness = 0

# setup wifi


wifi_ok = False
request_ok = False
ssid = ""
password = ""
host = ""

while True:
    try:
        red.off()
        file = open("wifi_data.txt", "r")
        ssid = file.readline().rstrip("\n")
        password = file.readline().rstrip("\n")
        host = file.readline().rstrip("\n")
        file.close()
        
        ip = connect(ssid, password)
    except OSError:
        ip = None
    
    if ip == None:
        pico_led.off()
        red.on()
        ip = connect_AF()
        connection = open_socket(ip)
        serve(connection)
    else:
        wifi_ok = True
        try: 
            request = requests.get(host)
            if request.status_code != 200:
                print("Error during request")
                print(request.status_code)
                print(request.content)
                request_ok = False
            else:
                print("initial request ok")
                request_ok = True
            request.close()
        except OSError:
            request_ok = False
        except ValueError:
            request_ok = False
            
        if not request_ok:
            red.on()
            connection = open_socket(ip)
            serve(connection)
        else:
            pico_led.on()
            break

# setup timer
timer = Timer()
timer.init(period=60000, mode=Timer.PERIODIC, callback=metricLoop)
