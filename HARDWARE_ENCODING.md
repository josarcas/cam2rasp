# Hardware H.264 Encoding en Raspberry Pi Zero 2W

## 🚀 Características del Sistema Actualizado

El sistema ahora utiliza el **hardware encoder H.264** de la Raspberry Pi mediante el codec `h264_v4l2m2m` de FFmpeg, lo que permite:

- ✅ **Grabación Full HD (1920x1080)** sin saturar CPU
- ✅ **Bitrate configurable** (por defecto 8Mbps)
- ✅ **Uso mínimo de CPU** (~5-15% vs ~80-95% software)
- ✅ **Mayor duración de batería** (si aplica)
- ✅ **Temperatura más baja** del SoC
- ✅ **Conversión automática** a MP4 al finalizar

## ⚙️ Configuración

### Archivo config.json

```json
{
  "camera": {
    "device_id": 0,
    "width": 1920,         // Resolución 1080p
    "height": 1080,
    "fps": 30
  },
  "use_hardware_encoder": true,  // Activar hardware encoder
  "bitrate": "8M",                // Bitrate del video (8 Mbps)
  "auto_start_recording": false
}
```

### Opciones de Bitrate

| Bitrate | Calidad | Uso | Tamaño/min |
|---------|---------|-----|------------|
| 2M      | Baja    | Streaming | ~15 MB |
| 4M      | Media   | General | ~30 MB |
| 8M      | Alta    | Recomendado | ~60 MB |
| 12M     | Muy Alta| Máxima calidad | ~90 MB |

### Resoluciones Soportadas

El hardware encoder soporta:

- 1920x1080 @ 30fps ✅ **Recomendado**
- 1920x1080 @ 60fps (si cámara lo soporta)
- 1280x720 @ 60fps
- 3840x2160 @ 15fps (4K - experimental)

## 🔧 Cómo Funciona

### Flujo de Hardware Encoding

```
Cámara USB → V4L2 → FFmpeg → Hardware Encoder (h264_v4l2m2m) → Archivo .h264
                                      ↓
                              Conversión automática
                                      ↓
                                  Archivo .MP4
```

### Ventajas vs Software Encoding

| Aspecto | Software (mp4v) | Hardware (H.264) |
|---------|----------------|------------------|
| Uso CPU | 80-95% | 5-15% |
| Temperatura | +15°C | +5°C |
| Calidad | Media | Alta |
| Bitrate | Variable | Constante |
| Resolución máx | 720p fluido | 1080p fluido |

## 📊 Rendimiento

### Raspberry Pi Zero 2W con Hardware Encoder

- **CPU Usage**: ~10-15% durante grabación 1080p@30fps
- **Temperatura**: ~50-60°C (vs ~70-80°C software)
- **Memoria RAM**: ~150-200MB
- **Escritura SD**: ~1MB/s @ 8Mbps bitrate

## 🎮 Comandos UART Adicionales

Los mismos comandos funcionan con hardware encoding:

```json
{"type": "start"}                    // Inicia grabación hardware
{"type": "stop"}                     // Detiene y convierte a MP4
{"type": "zoom", "value": 2.0}      // Ajusta zoom (si soportado)
{"type": "status"}                   // Ver estado de grabación
```

## 🔍 Verificación del Hardware Encoder

### Verificar que FFmpeg tiene el encoder

```bash
ffmpeg -codecs | grep h264_v4l2m2m
```

Debería mostrar:
```
DEV.L. h264   H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10
       h264_v4l2m2m        V4L2 mem2mem H.264 encoder wrapper (codec h264)
```

### Test de hardware encoding

```bash
# Grabar 10 segundos de prueba
ffmpeg -f v4l2 -input_format mjpeg -video_size 1920x1080 \
  -framerate 30 -i /dev/video0 -c:v h264_v4l2m2m \
  -b:v 8M -t 10 test_hardware.h264

# Verificar uso de CPU durante la grabación
top -bn1 | grep ffmpeg
```

### Ver info del video generado

```bash
ffprobe test_hardware.h264
```

## 🐛 Troubleshooting

### Error: "h264_v4l2m2m encoder not found"

```bash
# Verificar módulo v4l2
sudo modprobe bcm2835-v4l2

# Agregar al boot
echo "bcm2835-v4l2" | sudo tee -a /etc/modules
```

### Error: "Cannot allocate memory"

Reducir resolución o bitrate:

```json
{
  "width": 1280,
  "height": 720,
  "bitrate": "4M"
}
```

### Conversión a MP4 falla

Ejecutar manualmente:

```bash
ffmpeg -i video.h264 -c:v copy -movflags +faststart output.mp4
```

### Formato de entrada no soportado

Verificar formatos de cámara:

```bash
v4l2-ctl -d /dev/video0 --list-formats-ext
```

Cambiar en `camera_system.py` línea 114:
```python
'-input_format', 'yuyv422',  # o 'mjpeg'
```

## 🔄 Fallback a Software Encoder

Si el hardware encoder no funciona, el sistema automáticamente usa software:

```json
{
  "use_hardware_encoder": false
}
```

O en el código:
```python
self.use_hardware_encoder = False
```

## 📈 Optimizaciones Adicionales

### GPU Memory Split

Aumentar memoria GPU en `/boot/config.txt`:

```
gpu_mem=256
```

### Overclock (opcional, con precaución)

En `/boot/config.txt`:

```
# Overclock Pi Zero 2W
arm_freq=1200
over_voltage=2
```

⚠️ **Advertencia**: Overclock puede causar inestabilidad y sobrecalentamiento.

### Deshabilitar servicios innecesarios

```bash
sudo systemctl disable bluetooth
sudo systemctl disable wifi-country
sudo systemctl disable hciuart
```

## 📝 Formato de Archivo

### .h264 (Raw stream)

Durante la grabación se genera un archivo `.h264` raw que contiene el stream H.264 puro sin container.

### .mp4 (Container)

Al detener la grabación, automáticamente se convierte a MP4:
- Compatible con todos los reproductores
- Metadata y timestamps correctos
- Optimizado para streaming (faststart)
- Sin re-encoding (conversión instantánea)

## 🎯 Casos de Uso

### Vigilancia continua
```json
{
  "width": 1280,
  "height": 720,
  "fps": 15,
  "bitrate": "2M",
  "auto_start_recording": true
}
```

### Grabación de alta calidad
```json
{
  "width": 1920,
  "height": 1080,
  "fps": 30,
  "bitrate": "12M"
}
```

### Ahorro de espacio
```json
{
  "width": 1280,
  "height": 720,
  "fps": 20,
  "bitrate": "2M"
}
```

## 📊 Estimación de Almacenamiento

| Config | MB/min | Horas en 32GB | Horas en 64GB |
|--------|--------|---------------|---------------|
| 720p @ 2Mbps | 15 | 35h | 70h |
| 720p @ 4Mbps | 30 | 17h | 35h |
| 1080p @ 8Mbps | 60 | 8.5h | 17h |
| 1080p @ 12Mbps | 90 | 5.5h | 11h |

## 🔒 Notas de Seguridad

- Los archivos `.h264` temporales se eliminan automáticamente
- Los MP4 tienen permisos 644 (lectura para todos)
- Ubicación predeterminada: `/home/pi/videos/`

---

**Hardware encoding activado por defecto en el sistema** 🚀
