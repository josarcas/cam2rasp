# Ejemplos de Uso - Sistema de Cámara USB

## 📡 Ejemplos de Comandos UART

### Ejemplo 1: Control Básico de Grabación

```python
import serial
import json
import time

# Conectar a UART
ser = serial.Serial('/dev/serial0', 115200, timeout=1)

# Iniciar grabación
cmd = {"type": "start"}
ser.write(f"{json.dumps(cmd)}\n".encode())
response = ser.readline().decode().strip()
print(f"Respuesta: {response}")

# Esperar 30 segundos
time.sleep(30)

# Detener grabación
cmd = {"type": "stop"}
ser.write(f"{json.dumps(cmd)}\n".encode())
response = ser.readline().decode().strip()
print(f"Respuesta: {response}")

ser.close()
```

### Ejemplo 2: Control con Zoom

```python
import serial
import json

ser = serial.Serial('/dev/serial0', 115200, timeout=1)

# Iniciar grabación
ser.write(b'{"type":"start"}\n')
print(ser.readline().decode())

# Zoom 1.5x después de 5 segundos
time.sleep(5)
ser.write(b'{"type":"zoom","value":1.5}\n')
print(ser.readline().decode())

# Zoom 2.0x después de 5 segundos más
time.sleep(5)
ser.write(b'{"type":"zoom","value":2.0}\n')
print(ser.readline().decode())

# Volver a zoom 1.0x
time.sleep(5)
ser.write(b'{"type":"zoom","value":1.0}\n')
print(ser.readline().decode())

# Detener
time.sleep(5)
ser.write(b'{"type":"stop"}\n')
print(ser.readline().decode())

ser.close()
```

### Ejemplo 3: Monitor de Estado

```python
import serial
import json
import time

ser = serial.Serial('/dev/serial0', 115200, timeout=1)

while True:
    # Solicitar estado cada 5 segundos
    ser.write(b'{"type":"status"}\n')
    response = ser.readline().decode().strip()
    
    try:
        status = json.loads(response)
        print(f"Estado: {status}")
        
        if status.get('recording'):
            print(f"  Grabando: {status.get('filename')}")
        else:
            print("  No está grabando")
    except:
        print(f"Error al parsear: {response}")
    
    time.sleep(5)
```

### Ejemplo 4: Control desde Arduino

```cpp
// Arduino conectado a UART de Raspberry Pi

void setup() {
  Serial.begin(115200);
  delay(2000);  // Esperar inicialización
  
  // Iniciar grabación
  Serial.println("{\"type\":\"start\"}");
  delay(1000);
  
  // Leer respuesta
  if (Serial.available()) {
    String response = Serial.readStringUntil('\n');
    // Procesar respuesta...
  }
}

void loop() {
  // Cada minuto, verificar estado
  delay(60000);
  Serial.println("{\"type\":\"status\"}");
  
  if (Serial.available()) {
    String response = Serial.readStringUntil('\n');
    // Procesar respuesta...
  }
}
```

### Ejemplo 5: Control desde Bash

```bash
#!/bin/bash

# Configurar puerto UART
stty -F /dev/serial0 115200 cs8 -cstopb -parenb

# Función para enviar comando
send_cmd() {
    echo "$1" > /dev/serial0
    sleep 0.2
    cat /dev/serial0 &
    sleep 0.3
    killall cat 2>/dev/null
}

# Iniciar grabación
send_cmd '{"type":"start"}'

# Grabar por 1 minuto
sleep 60

# Detener grabación
send_cmd '{"type":"stop"}'
```

## 🎬 Scripts de Automatización

### Script 1: Grabación Programada

```bash
#!/bin/bash
# grab_programado.sh - Graba a horas específicas

UART_PORT="/dev/serial0"

# Función para enviar comando
send_uart() {
    echo "$1" > $UART_PORT
}

# Grabar de 8 AM a 6 PM
while true; do
    HORA=$(date +%H)
    
    if [ $HORA -ge 8 ] && [ $HORA -lt 18 ]; then
        # Horario de grabación
        send_uart '{"type":"status"}'
        sleep 1
        
        # Si no está grabando, iniciar
        # (Aquí deberías leer la respuesta UART)
        send_uart '{"type":"start"}'
    else
        # Fuera de horario, detener
        send_uart '{"type":"stop"}'
        sleep 300  # Esperar 5 minutos
    fi
    
    sleep 60  # Check cada minuto
done
```

### Script 2: Grabación por Sensor

```python
#!/usr/bin/env python3
# grab_sensor.py - Graba cuando detecta movimiento

import serial
import json
import RPi.GPIO as GPIO
import time

# Configurar GPIO para sensor PIR
PIR_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

# Configurar UART
ser = serial.Serial('/dev/serial0', 115200, timeout=1)

recording = False

def start_recording():
    global recording
    if not recording:
        ser.write(b'{"type":"start"}\n')
        print("Movimiento detectado - Grabando")
        recording = True

def stop_recording():
    global recording
    if recording:
        ser.write(b'{"type":"stop"}\n')
        print("Sin movimiento - Detenido")
        recording = False

print("Monitor de movimiento activo")

try:
    while True:
        if GPIO.input(PIR_PIN):
            start_recording()
            time.sleep(30)  # Grabar al menos 30 segundos
        else:
            if recording:
                time.sleep(10)  # Esperar 10s antes de detener
                if not GPIO.input(PIR_PIN):
                    stop_recording()
        
        time.sleep(1)
        
except KeyboardInterrupt:
    stop_recording()
    GPIO.cleanup()
    ser.close()
```

### Script 3: Rotación de Videos

```bash
#!/bin/bash
# rotar_videos.sh - Elimina videos antiguos cuando SD está llena

VIDEO_DIR="/home/pi/videos"
MAX_USAGE=85  # Porcentaje máximo de uso de SD

# Obtener uso actual
USAGE=$(df -h | grep /dev/root | awk '{print $5}' | sed 's/%//')

if [ $USAGE -gt $MAX_USAGE ]; then
    echo "SD al ${USAGE}% - Limpiando videos antiguos..."
    
    # Eliminar videos más antiguos (mantener últimos 10)
    cd $VIDEO_DIR
    ls -t video_*.mp4 | tail -n +11 | xargs rm -f
    
    echo "Limpieza completada"
fi
```

### Script 4: Backup Automático

```bash
#!/bin/bash
# backup_videos.sh - Copia videos a servidor externo

VIDEO_DIR="/home/pi/videos"
BACKUP_SERVER="user@192.168.1.100"
BACKUP_DIR="/backup/camera"

# Buscar videos no respaldados (sin .backup tag)
for video in $VIDEO_DIR/video_*.mp4; do
    if [ -f "$video" ] && [ ! -f "${video}.backup" ]; then
        echo "Respaldando: $(basename $video)"
        
        # Copiar a servidor
        scp "$video" "${BACKUP_SERVER}:${BACKUP_DIR}/"
        
        if [ $? -eq 0 ]; then
            # Marcar como respaldado
            touch "${video}.backup"
            echo "Respaldo exitoso"
        else
            echo "Error en respaldo"
        fi
    fi
done
```

## 🎛️ Configuraciones Especiales

### Config 1: Vigilancia 24/7

```json
{
  "camera": {
    "device_id": 0,
    "width": 1280,
    "height": 720,
    "fps": 15
  },
  "use_hardware_encoder": true,
  "bitrate": "2M",
  "auto_start_recording": true
}
```

**Uso**: Vigilancia continua con bajo consumo de espacio.

### Config 2: Alta Calidad Eventos

```json
{
  "camera": {
    "device_id": 0,
    "width": 1920,
    "height": 1080,
    "fps": 30
  },
  "use_hardware_encoder": true,
  "bitrate": "12M",
  "auto_start_recording": false
}
```

**Uso**: Grabación manual de eventos importantes con máxima calidad.

### Config 3: Timelapse

```json
{
  "camera": {
    "device_id": 0,
    "width": 1920,
    "height": 1080,
    "fps": 5
  },
  "use_hardware_encoder": true,
  "bitrate": "4M",
  "auto_start_recording": true
}
```

**Uso**: Timelapse de larga duración (5 fps = 6x velocidad).

## 🔌 Integración con Otros Sistemas

### Integración con Home Assistant

```yaml
# configuration.yaml
shell_command:
  camera_start: 'echo "{\"type\":\"start\"}" > /dev/ttyUSB0'
  camera_stop: 'echo "{\"type\":\"stop\"}" > /dev/ttyUSB0'
  camera_status: 'echo "{\"type\":\"status\"}" > /dev/ttyUSB0'

automation:
  - alias: 'Grabar cuando salgo'
    trigger:
      - platform: state
        entity_id: device_tracker.my_phone
        to: 'not_home'
    action:
      - service: shell_command.camera_start
```

### Integración con Node-RED

```javascript
// Node-RED function node
const SerialPort = require('serialport');
const port = new SerialPort('/dev/serial0', { baudRate: 115200 });

msg.payload = {
    type: "start"
};

port.write(JSON.stringify(msg.payload) + '\n');

return msg;
```

### API REST Simple (Flask)

```python
# api_camera.py - API REST para controlar cámara
from flask import Flask, jsonify
import serial

app = Flask(__name__)
ser = serial.Serial('/dev/serial0', 115200, timeout=1)

@app.route('/camera/start', methods=['POST'])
def start():
    ser.write(b'{"type":"start"}\n')
    response = ser.readline().decode().strip()
    return jsonify({"response": response})

@app.route('/camera/stop', methods=['POST'])
def stop():
    ser.write(b'{"type":"stop"}\n')
    response = ser.readline().decode().strip()
    return jsonify({"response": response})

@app.route('/camera/status', methods=['GET'])
def status():
    ser.write(b'{"type":"status"}\n')
    response = ser.readline().decode().strip()
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 📊 Monitoreo y Análisis

### Monitor de Temperatura y CPU

```python
#!/usr/bin/env python3
# monitor.py - Monitorea rendimiento durante grabación

import time
import os

def get_cpu_temp():
    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
        temp = float(f.read()) / 1000.0
    return temp

def get_cpu_usage():
    with open('/proc/stat', 'r') as f:
        line = f.readline()
    # Parsear y calcular CPU usage
    return 0  # Simplificado

while True:
    temp = get_cpu_temp()
    print(f"Temperatura: {temp:.1f}°C")
    
    # Verificar espacio en disco
    stat = os.statvfs('/home/pi/videos')
    free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
    print(f"Espacio libre: {free_gb:.1f} GB")
    
    time.sleep(60)
```

---

**Más ejemplos y casos de uso en la documentación completa**
