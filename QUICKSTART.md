# 🚀 Guía Rápida - Sistema de Cámara USB

## ⚡ Instalación en 5 Minutos

### 1️⃣ Copiar Archivos

```bash
# Desde tu PC, copiar a la Raspberry Pi
scp -r raspberry/* pi@<IP_RASPBERRY>:~/camera_system/
```

### 2️⃣ Instalar en Raspberry Pi

```bash
# Conectar por SSH
ssh pi@<IP_RASPBERRY>

# Instalar
cd ~/camera_system
sudo bash install.sh

# Reiniciar
sudo reboot
```

### 3️⃣ Verificar Funcionamiento

```bash
# Ver estado del servicio
sudo systemctl status camera_system

# Ver logs en tiempo real
sudo journalctl -u camera_system -f
```

## 🎮 Uso Básico por UART

### Desde Arduino/ESP32/Microcontrolador

```cpp
Serial.begin(115200);
Serial.println("{\"type\":\"start\"}");  // Iniciar grabación
delay(30000);                            // Grabar 30 segundos
Serial.println("{\"type\":\"stop\"}");   // Detener
```

### Desde Terminal Serial (minicom/screen)

```bash
# Conectar
sudo minicom -b 115200 -D /dev/serial0

# Comandos
{"type":"start"}
{"type":"stop"}
{"type":"zoom","value":2.0}
{"type":"status"}
```

### Desde Python

```python
import serial, json

ser = serial.Serial('/dev/serial0', 115200)
ser.write(b'{"type":"start"}\n')
print(ser.readline().decode())  # Respuesta
```

## 📝 Configuración Rápida

Editar: `/etc/camera_system/config.json`

```json
{
  "camera": {
    "width": 1920,      // Resolución
    "height": 1080,
    "fps": 30
  },
  "bitrate": "8M",      // Calidad (2M, 4M, 8M, 12M)
  "auto_start_recording": false
}
```

Reiniciar después de cambios:
```bash
sudo systemctl restart camera_system
```

## 🎯 Configuraciones Pre-definidas

### 🔒 Vigilancia Continua
```json
{"width": 1280, "height": 720, "fps": 15, "bitrate": "2M", "auto_start_recording": true}
```

### 📹 Alta Calidad
```json
{"width": 1920, "height": 1080, "fps": 30, "bitrate": "12M"}
```

### 💾 Ahorro de Espacio
```json
{"width": 1280, "height": 720, "fps": 20, "bitrate": "2M"}
```

## 🔌 Conexión UART

```
Raspberry Pi GPIO Header:
┌────────────────┐
│ PIN 8  (TX)    │──→ RX del otro dispositivo
│ PIN 10 (RX)    │←─ TX del otro dispositivo  
│ PIN 6  (GND)   │──  GND común
└────────────────┘

Configuración: 115200 baud, 8N1
```

## 📊 Comandos Útiles

```bash
# Ver videos grabados
ls -lh /home/pi/videos/

# Espacio disponible
df -h

# Ver temperatura CPU
vcgencmd measure_temp

# Test de hardware encoder
bash test_hardware_encoder.sh

# Test de UART
python3 test_uart.py -i

# Detener servicio
sudo systemctl stop camera_system

# Iniciar servicio
sudo systemctl start camera_system
```

## 🐛 Solución Rápida de Problemas

### ❌ Cámara no detectada
```bash
lsusb                    # Ver dispositivos USB
ls /dev/video*           # Ver dispositivos de video
v4l2-ctl --list-devices  # Info de cámaras
```

### ❌ UART no funciona
```bash
# Verificar UART habilitado
grep "enable_uart" /boot/config.txt

# Debe mostrar: enable_uart=1
# Si no, agregar y reiniciar
echo "enable_uart=1" | sudo tee -a /boot/config.txt
sudo reboot
```

### ❌ Servicio no inicia
```bash
# Ver error exacto
sudo journalctl -u camera_system --no-pager

# Ejecutar manualmente para debug
sudo python3 /opt/camera_system/camera_system.py
```

### ❌ Sin espacio en SD
```bash
# Ver uso
df -h

# Limpiar videos antiguos
rm /home/pi/videos/video_202411*.mp4
```

## 📈 Rendimiento Esperado

| Config | CPU | Temp | Espacio (1h) |
|--------|-----|------|--------------|
| 720p @ 15fps, 2M | 10% | 50°C | ~900 MB |
| 1080p @ 30fps, 8M | 15% | 55°C | ~3.6 GB |
| 1080p @ 30fps, 12M | 18% | 58°C | ~5.4 GB |

## 🎓 Aprende Más

- **README.md** - Documentación completa
- **HARDWARE_ENCODING.md** - Detalles técnicos del encoder
- **EXAMPLES.md** - Ejemplos de código
- **CHANGELOG.md** - Historial de cambios

## 💡 Tips

1. **Usa Full HD con confianza**: El hardware encoder maneja 1080p@30fps sin problemas
2. **Ajusta bitrate según uso**: 2M para vigilancia, 8M para uso general, 12M para alta calidad
3. **Monitorea espacio**: 1 hora @ 8Mbps ≈ 3.6 GB
4. **Temperatura normal**: 50-60°C durante grabación es esperado
5. **Auto-inicio**: Habilita `auto_start_recording: true` para vigilancia 24/7

## 🆘 Soporte

```bash
# Logs en tiempo real
sudo journalctl -u camera_system -f

# Estado del sistema
sudo systemctl status camera_system

# Archivo de log
tail -f /var/log/camera_system.log
```

---

**Sistema listo para producción** ✅  
**Hardware encoding activado** 🚀  
**Full HD @ 30fps** 🎥
