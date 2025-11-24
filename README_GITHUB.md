# 🎥 Sistema de Cámara USB para Raspberry Pi Zero 2W

Sistema optimizado de captura de video USB con **hardware H.264 encoding** y control por **UART**. Graba Full HD (1920x1080@30fps) usando solo **10-15% CPU**.

---

## 🚀 Instalación Rápida

### En tu Raspberry Pi, ejecuta:

```bash
sudo apt-get update && sudo apt-get install -y git
git clone https://github.com/TU_USUARIO/TU_REPO.git camera_system
cd camera_system
sudo bash install.sh
sudo reboot
```

**⚠️ Reemplaza `TU_USUARIO/TU_REPO` con la URL de este repositorio**

---

## ✨ Características

| Característica | Especificación |
|----------------|----------------|
| 🎬 Resolución | **1920x1080 @ 30fps** (Full HD) |
| ⚡ Encoding | **Hardware H.264** (h264_v4l2m2m) |
| 🔥 Uso CPU | **~10-15%** durante grabación |
| 🌡️ Temperatura | **~55°C** (vs ~75°C software) |
| 💾 Formato | **MP4** (H.264 + AAC) |
| 📡 Control | **UART** 115200 baud |
| 🔄 Auto-inicio | **Systemd** service |
| 📊 Bitrate | **8 Mbps** (configurable) |

---

## 📋 Requisitos

- ✅ Raspberry Pi Zero 2W (también compatible con Pi 3/4)
- ✅ Raspbian Lite 32-bit (Bullseye o superior)
- ✅ Cámara USB compatible V4L2
- ✅ Tarjeta SD (mínimo 8GB recomendado)
- ✅ Conexión UART opcional (GPIO 14/15)

---

## 🎮 Comandos UART

Envía comandos en formato JSON por puerto serial (115200 baud):

```json
{"type":"start"}                    // Iniciar grabación
{"type":"stop"}                     // Detener grabación
{"type":"zoom","value":2.0}         // Ajustar zoom
{"type":"brightness","value":150}   // Ajustar brillo
{"type":"status"}                   // Obtener estado
{"type":"ping"}                     // Test de conexión
```

### Desde Arduino:
```cpp
Serial.begin(115200);
Serial.println("{\"type\":\"start\"}");
```

### Desde Python:
```python
import serial, json
ser = serial.Serial('/dev/serial0', 115200)
ser.write(b'{"type":"start"}\n')
```

---

## 📊 Rendimiento

### Comparación Software vs Hardware Encoding

| Métrica | Software (v1.0) | Hardware (v2.0) | Mejora |
|---------|-----------------|-----------------|--------|
| CPU @ 1080p | 80-95% | **10-15%** | **-85%** ⬇️ |
| Temperatura | ~75°C | **~55°C** | **-20°C** ⬇️ |
| Max Res. Fluida | 720p | **1080p** | **+44%** ⬆️ |
| Calidad | Media | **Alta** | ⬆️ |

---

## ⚙️ Configuración

Edita `/etc/camera_system/config.json`:

```json
{
  "camera": {
    "device_id": 0,
    "width": 1920,
    "height": 1080,
    "fps": 30
  },
  "use_hardware_encoder": true,
  "bitrate": "8M",
  "auto_start_recording": false
}
```

**Bitrate options:** `2M` (ahorro espacio) | `4M` (medio) | `8M` (recomendado) | `12M` (máxima calidad)

Después de editar:
```bash
sudo systemctl restart camera_system
```

---

## 🔌 Conexión UART

```
Raspberry Pi GPIO Header:
┌─────────────────────┐
│ PIN 8  (TX/GPIO14)  │──→ RX del dispositivo externo
│ PIN 10 (RX/GPIO15)  │←── TX del dispositivo externo
│ PIN 6  (GND)        │──  GND común
└─────────────────────┘
```

---

## 📝 Uso

### Ver estado del servicio
```bash
sudo systemctl status camera_system
```

### Ver logs en tiempo real
```bash
sudo journalctl -u camera_system -f
```

### Ver videos grabados
```bash
ls -lh /home/pi/videos/
```

### Reiniciar servicio
```bash
sudo systemctl restart camera_system
```

---

## 🧪 Pruebas

### Verificar hardware encoder
```bash
cd ~/camera_system
bash test_hardware_encoder.sh
```

### Test de UART
```bash
cd ~/camera_system
python3 test_uart.py -i
```

---

## 📚 Documentación

| Archivo | Descripción |
|---------|-------------|
| [README.md](README.md) | Documentación completa |
| [INSTALL_FROM_GITHUB.md](INSTALL_FROM_GITHUB.md) | Instalación detallada |
| [QUICKSTART.md](QUICKSTART.md) | Guía rápida 5 minutos |
| [HARDWARE_ENCODING.md](HARDWARE_ENCODING.md) | Detalles técnicos H.264 |
| [EXAMPLES.md](EXAMPLES.md) | Ejemplos de código |
| [CHANGELOG.md](CHANGELOG.md) | Historial de versiones |

---

## 🐛 Solución de Problemas

### Servicio no inicia
```bash
# Ver error detallado
sudo journalctl -u camera_system --no-pager

# Ejecutar manualmente para debug
sudo python3 /opt/camera_system/camera_system.py
```

### Cámara no detectada
```bash
lsusb                           # Ver dispositivos USB
ls /dev/video*                  # Ver dispositivos de video
v4l2-ctl --list-devices         # Info detallada
```

### UART no funciona
```bash
# Verificar que está habilitado
grep "enable_uart" /boot/config.txt

# Si no está, agregar y reiniciar
echo "enable_uart=1" | sudo tee -a /boot/config.txt
sudo reboot
```

---

## 🔄 Actualización

```bash
cd ~/camera_system
git pull origin main
sudo systemctl stop camera_system
sudo cp camera_system.py /opt/camera_system/
sudo cp config.json /etc/camera_system/
sudo systemctl restart camera_system
```

---

## 💾 Almacenamiento

### Tamaño de archivos (aproximado)

| Configuración | MB/min | Horas en 32GB |
|---------------|--------|---------------|
| 720p @ 2Mbps | 15 | 35h |
| 1080p @ 4Mbps | 30 | 17h |
| 1080p @ 8Mbps | 60 | 8.5h |
| 1080p @ 12Mbps | 90 | 5.5h |

---

## 🎯 Casos de Uso

### 🔒 Vigilancia 24/7
```json
{"width": 1280, "height": 720, "fps": 15, "bitrate": "2M", "auto_start_recording": true}
```

### 📹 Grabación de Alta Calidad
```json
{"width": 1920, "height": 1080, "fps": 30, "bitrate": "12M"}
```

### 💾 Ahorro de Espacio
```json
{"width": 1280, "height": 720, "fps": 20, "bitrate": "2M"}
```

---

## 🏗️ Arquitectura

```
Cámara USB → FFmpeg (V4L2) → Hardware H.264 Encoder
                                      ↓
                               Archivo .h264
                                      ↓
                            Conversión a .mp4
                                      ↓
                          /home/pi/videos/*.mp4
```

---

## 📄 Licencia

MIT License - Uso libre para proyectos personales y comerciales

---

## 🤝 Contribuciones

Pull requests son bienvenidos. Para cambios mayores, abre un issue primero.

---

## ⭐ Si te sirvió este proyecto

Dale una ⭐ al repositorio!

---

**Desarrollado para Raspberry Pi Zero 2W**  
**Hardware H.264 Encoding | Full HD @ 30fps | <15% CPU** 🚀
