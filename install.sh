#!/bin/bash

# Script de instalación para Sistema de Cámara USB
# Para Raspberry Pi Zero 2W con Raspbian Lite 32-bit

# No usar set -e para permitir que paquetes opcionales fallen sin detener el script

echo "=== Instalación del Sistema de Cámara USB ==="
echo ""

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then 
    echo "ERROR: Este script debe ejecutarse como root"
    echo "Usa: sudo bash install.sh"
    exit 1
fi

echo "[1/7] Actualizando sistema..."
apt-get update

echo "[2/7] Instalando dependencias del sistema..."

# Paquetes esenciales (siempre necesarios)
ESSENTIAL_PACKAGES="python3-pip python3-dev v4l-utils ffmpeg"

# Paquetes opcionales de OpenCV (intentar instalar si están disponibles)
OPENCV_PACKAGES="python3-opencv libopencv-dev"

# Paquetes legacy (solo si están disponibles)
LEGACY_PACKAGES="libatlas-base-dev libjasper-dev libqtgui4 libqt4-test libhdf5-serial-dev"

# Paquetes modernos alternativos
MODERN_PACKAGES="libatlas3-base libhdf5-dev"

echo "   Instalando paquetes esenciales..."
apt-get install -y $ESSENTIAL_PACKAGES

echo "   Instalando OpenCV..."
apt-get install -y $OPENCV_PACKAGES 2>/dev/null || echo "   ⚠ Algunos paquetes de OpenCV no disponibles (no crítico)"

echo "   Instalando paquetes modernos..."
apt-get install -y $MODERN_PACKAGES 2>/dev/null || echo "   ⚠ Algunos paquetes modernos no disponibles (no crítico)"

echo "   Verificando paquetes legacy..."
for pkg in $LEGACY_PACKAGES; do
    apt-get install -y $pkg 2>/dev/null || echo "   ⚠ $pkg no disponible (no crítico para FFmpeg)"
done

echo "   ✓ Dependencias principales instaladas"

echo "[3/7] Instalando dependencias Python..."
pip3 install -r requirements.txt

echo "[4/7] Habilitando UART en Raspberry Pi..."

# Detectar ubicación de config.txt (cambia en Bookworm+)
CONFIG_FILE=""
if [ -f /boot/firmware/config.txt ]; then
    CONFIG_FILE="/boot/firmware/config.txt"
elif [ -f /boot/config.txt ]; then
    CONFIG_FILE="/boot/config.txt"
fi

if [ -n "$CONFIG_FILE" ]; then
    # Habilitar UART en config.txt si no está habilitado
    if ! grep -q "enable_uart=1" "$CONFIG_FILE"; then
        echo "enable_uart=1" >> "$CONFIG_FILE"
        echo "   ✓ UART habilitado en $CONFIG_FILE"
    else
        echo "   ✓ UART ya está habilitado"
    fi
else
    echo "   ⚠ No se encontró config.txt (verificar manualmente)"
fi

# Detectar ubicación de cmdline.txt
CMDLINE_FILE=""
if [ -f /boot/firmware/cmdline.txt ]; then
    CMDLINE_FILE="/boot/firmware/cmdline.txt"
elif [ -f /boot/cmdline.txt ]; then
    CMDLINE_FILE="/boot/cmdline.txt"
fi

# Deshabilitar consola serial en UART
if [ -n "$CMDLINE_FILE" ]; then
    sed -i.backup 's/console=serial0,115200 //' "$CMDLINE_FILE"
    sed -i 's/console=ttyAMA0,115200 //' "$CMDLINE_FILE"
    echo "   ✓ Consola serial deshabilitada"
fi

echo "[5/7] Creando directorios..."
mkdir -p /opt/camera_system
mkdir -p /etc/camera_system
mkdir -p /home/pi/videos
chown -R pi:pi /home/pi/videos

echo "[6/7] Copiando archivos..."

if [ ! -f camera_system.py ]; then
    echo "   ✗ ERROR: No se encuentra camera_system.py"
    exit 1
fi

if [ ! -f config.json ]; then
    echo "   ✗ ERROR: No se encuentra config.json"
    exit 1
fi

if [ ! -f camera_system.service ]; then
    echo "   ✗ ERROR: No se encuentra camera_system.service"
    exit 1
fi

cp camera_system.py /opt/camera_system/
cp config.json /etc/camera_system/
chmod +x /opt/camera_system/camera_system.py
echo "   ✓ Archivos copiados"

echo "[7/7] Configurando servicio systemd..."
cp camera_system.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable camera_system.service

echo ""
echo "=== Instalación completada ==="
echo ""
echo "El sistema se iniciará automáticamente al arrancar."
echo ""

# Verificar FFmpeg
echo "Verificando hardware encoder..."
if ffmpeg -codecs 2>/dev/null | grep -q "h264_v4l2m2m"; then
    echo "   ✓ Hardware H.264 encoder disponible"
else
    echo "   ⚠ Hardware encoder no detectado (se usará software fallback)"
    echo "     Ejecuta: sudo modprobe bcm2835-v4l2"
fi

echo ""
echo "Comandos útiles:"
echo "  sudo systemctl start camera_system    # Iniciar servicio"
echo "  sudo systemctl stop camera_system     # Detener servicio"
echo "  sudo systemctl status camera_system   # Ver estado"
echo "  sudo journalctl -u camera_system -f   # Ver logs en tiempo real"
echo ""
echo "IMPORTANTE: Se recomienda reiniciar para aplicar cambios de UART"
echo "  sudo reboot"
echo ""
