#!/bin/bash

#═══════════════════════════════════════════════════════════
# Setup Script - Copia y pega esto en tu Raspberry Pi
#═══════════════════════════════════════════════════════════

# IMPORTANTE: Edita esta línea con la URL de tu repositorio
REPO_URL="https://github.com/josarcas/cam2rasp.git"

echo "🚀 Instalando Sistema de Cámara USB..."
echo ""

# Actualizar e instalar git
echo "📦 Instalando dependencias..."
sudo apt-get update -qq
sudo apt-get install -y git

# Clonar repositorio
echo "📥 Descargando desde GitHub..."
cd ~
if [ -d "camera_system" ]; then
    echo "⚠️  Directorio camera_system existe, respaldando..."
    mv camera_system camera_system.backup.$(date +%Y%m%d_%H%M%S)
fi

git clone "$REPO_URL" camera_system

if [ ! -d "camera_system" ]; then
    echo "❌ Error al clonar repositorio"
    echo "Verifica la URL: $REPO_URL"
    exit 1
fi

# Instalar
cd camera_system
echo "⚙️  Ejecutando instalación..."
sudo bash install.sh

echo ""
echo "✅ Instalación completada!"
echo ""
echo "🔄 Reiniciando en 5 segundos..."
sleep 5
sudo reboot
