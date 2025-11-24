#!/bin/bash

# Script de instalación para Sistema de Cámara USB
# Para Raspberry Pi Zero 2W con Raspbian Lite 32-bit

set -e

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
apt-get install -y \
    python3-pip \
    python3-dev \
    python3-opencv \
    libopencv-dev \
    libatlas-base-dev \
    libjasper-dev \
    libqtgui4 \
    libqt4-test \
    libhdf5-dev \
    libhdf5-serial-dev \
    v4l-utils \
    ffmpeg

echo "[3/7] Instalando dependencias Python..."
pip3 install -r requirements.txt

echo "[4/7] Habilitando UART en Raspberry Pi..."
# Habilitar UART en config.txt si no está habilitado
if ! grep -q "enable_uart=1" /boot/config.txt; then
    echo "enable_uart=1" >> /boot/config.txt
    echo "UART habilitado en /boot/config.txt"
fi

# Deshabilitar consola serial en UART
if [ -f /boot/cmdline.txt ]; then
    sed -i 's/console=serial0,115200 //' /boot/cmdline.txt
    sed -i 's/console=ttyAMA0,115200 //' /boot/cmdline.txt
    echo "Consola serial deshabilitada"
fi

echo "[5/7] Creando directorios..."
mkdir -p /opt/camera_system
mkdir -p /etc/camera_system
mkdir -p /home/pi/videos
chown -R pi:pi /home/pi/videos

echo "[6/7] Copiando archivos..."
cp camera_system.py /opt/camera_system/
cp config.json /etc/camera_system/
chmod +x /opt/camera_system/camera_system.py

echo "[7/7] Configurando servicio systemd..."
cp camera_system.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable camera_system.service

echo ""
echo "=== Instalación completada ==="
echo ""
echo "El sistema se iniciará automáticamente al arrancar."
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
