#!/bin/bash

# Script de prueba para verificar hardware encoder H.264
# Para Raspberry Pi Zero 2W

echo "=== Test de Hardware Encoder H.264 ==="
echo ""

# Verificar que ffmpeg está instalado
if ! command -v ffmpeg &> /dev/null; then
    echo "ERROR: FFmpeg no está instalado"
    echo "Instala con: sudo apt-get install ffmpeg"
    exit 1
fi

echo "[1/5] Verificando codec h264_v4l2m2m..."
if ffmpeg -codecs 2>/dev/null | grep -q "h264_v4l2m2m"; then
    echo "✓ Hardware encoder H.264 disponible"
else
    echo "✗ Hardware encoder NO disponible"
    echo "Intenta cargar el módulo: sudo modprobe bcm2835-v4l2"
    exit 1
fi

echo ""
echo "[2/5] Detectando cámara USB..."
if [ ! -e /dev/video0 ]; then
    echo "✗ No se detectó cámara en /dev/video0"
    echo "Verifica la cámara USB"
    exit 1
fi

echo "✓ Cámara detectada en /dev/video0"
echo ""

echo "[3/5] Información de la cámara:"
v4l2-ctl -d /dev/video0 --info

echo ""
echo "[4/5] Formatos soportados:"
v4l2-ctl -d /dev/video0 --list-formats-ext | head -n 20

echo ""
echo "[5/5] Grabando 10 segundos de prueba con hardware encoder..."
echo "Archivo: /tmp/test_hardware_h264.h264"
echo ""

# Grabar test
ffmpeg -f v4l2 \
    -input_format mjpeg \
    -video_size 1920x1080 \
    -framerate 30 \
    -i /dev/video0 \
    -c:v h264_v4l2m2m \
    -b:v 8M \
    -pix_fmt yuv420p \
    -t 10 \
    /tmp/test_hardware_h264.h264 \
    -y 2>&1 | tail -n 20

if [ -f /tmp/test_hardware_h264.h264 ]; then
    echo ""
    echo "✓ Grabación exitosa"
    
    # Mostrar info del archivo
    echo ""
    echo "Información del video:"
    ffprobe /tmp/test_hardware_h264.h264 2>&1 | grep -E "Duration|Stream|Video"
    
    # Convertir a MP4
    echo ""
    echo "Convirtiendo a MP4..."
    ffmpeg -i /tmp/test_hardware_h264.h264 \
        -c:v copy \
        -movflags +faststart \
        /tmp/test_hardware.mp4 \
        -y 2>&1 | tail -n 5
    
    if [ -f /tmp/test_hardware.mp4 ]; then
        echo ""
        echo "✓ Conversión exitosa"
        echo ""
        echo "Archivos generados:"
        ls -lh /tmp/test_hardware*
        echo ""
        echo "Reproduce con: vlc /tmp/test_hardware.mp4"
    else
        echo "✗ Error en conversión a MP4"
    fi
else
    echo ""
    echo "✗ Error en la grabación"
    exit 1
fi

echo ""
echo "=== Test completado ==="
echo ""
echo "Limpia archivos de test con:"
echo "  rm /tmp/test_hardware*"
