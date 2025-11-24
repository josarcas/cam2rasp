#!/bin/bash

#═══════════════════════════════════════════════════════════
# Script de Instalación Rápida desde GitHub
# Sistema de Cámara USB para Raspberry Pi Zero 2W
#═══════════════════════════════════════════════════════════

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
REPO_URL="https://github.com/TU_USUARIO/TU_REPO.git"  # CAMBIAR ESTO
INSTALL_DIR="$HOME/camera_system"

echo -e "${BLUE}"
echo "═══════════════════════════════════════════════════════"
echo "  Sistema de Cámara USB - Instalación desde GitHub"
echo "  Raspberry Pi Zero 2W - Hardware H.264 Encoding"
echo "═══════════════════════════════════════════════════════"
echo -e "${NC}"

# Verificar que se ejecuta como root si es necesario para ciertos pasos
if [ "$EUID" -ne 0 ] && [ "$1" != "--user" ]; then
    echo -e "${YELLOW}[!] Este script necesita permisos sudo para instalar${NC}"
    echo -e "${YELLOW}[!] Reejecutando con sudo...${NC}"
    sudo bash "$0" --root
    exit $?
fi

echo -e "${GREEN}[1/8] Verificando sistema...${NC}"
# Verificar que es Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo -e "${RED}[✗] No se detectó Raspberry Pi${NC}"
    exit 1
fi

MODEL=$(cat /proc/device-tree/model)
echo "      Modelo: $MODEL"

echo ""
echo -e "${GREEN}[2/8] Actualizando repositorios del sistema...${NC}"
apt-get update -qq

echo ""
echo -e "${GREEN}[3/8] Instalando Git...${NC}"
if ! command -v git &> /dev/null; then
    apt-get install -y git
    echo "      ✓ Git instalado"
else
    echo "      ✓ Git ya está instalado"
fi

echo ""
echo -e "${GREEN}[4/8] Descargando proyecto desde GitHub...${NC}"

# Verificar que REPO_URL fue cambiado
if [[ "$REPO_URL" == *"TU_USUARIO"* ]] || [[ "$REPO_URL" == *"TU_REPO"* ]]; then
    echo -e "${RED}[✗] ERROR: Debes editar REPO_URL en este script${NC}"
    echo -e "${YELLOW}    Abre el script y cambia TU_USUARIO y TU_REPO${NC}"
    exit 1
fi

# Eliminar instalación anterior si existe
if [ -d "$INSTALL_DIR" ]; then
    echo "      ⚠ Instalación anterior encontrada, respaldando..."
    mv "$INSTALL_DIR" "${INSTALL_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Clonar repositorio
echo "      Descargando desde: $REPO_URL"
git clone "$REPO_URL" "$INSTALL_DIR"

if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${RED}[✗] Error al descargar el repositorio${NC}"
    exit 1
fi

cd "$INSTALL_DIR"
echo "      ✓ Repositorio descargado en $INSTALL_DIR"

echo ""
echo -e "${GREEN}[5/8] Dando permisos de ejecución...${NC}"
chmod +x install.sh
chmod +x test_hardware_encoder.sh 2>/dev/null || true
chmod +x test_uart.py 2>/dev/null || true
echo "      ✓ Permisos configurados"

echo ""
echo -e "${GREEN}[6/8] Ejecutando instalador principal...${NC}"
echo "      (Esto puede tomar varios minutos)"
echo ""

# Ejecutar instalador principal
bash install.sh

echo ""
echo -e "${GREEN}[7/8] Verificando instalación...${NC}"

# Verificar que los archivos se copiaron
if [ -f /opt/camera_system/camera_system.py ]; then
    echo "      ✓ Programa principal instalado"
else
    echo -e "${RED}      ✗ Error: Programa no instalado${NC}"
    exit 1
fi

if [ -f /etc/camera_system/config.json ]; then
    echo "      ✓ Configuración instalada"
else
    echo -e "${RED}      ✗ Error: Configuración no instalada${NC}"
    exit 1
fi

if [ -f /etc/systemd/system/camera_system.service ]; then
    echo "      ✓ Servicio systemd instalado"
else
    echo -e "${RED}      ✗ Error: Servicio no instalado${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}[8/8] Configuración final...${NC}"

# Verificar que UART está habilitado
if ! grep -q "enable_uart=1" /boot/config.txt; then
    echo "      Habilitando UART..."
    echo "enable_uart=1" >> /boot/config.txt
fi

echo "      ✓ UART configurado"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}            ✓ INSTALACIÓN COMPLETADA${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📍 Archivos instalados:${NC}"
echo "   • Programa:       /opt/camera_system/camera_system.py"
echo "   • Configuración:  /etc/camera_system/config.json"
echo "   • Servicio:       /etc/systemd/system/camera_system.service"
echo "   • Videos:         /home/pi/videos/"
echo ""
echo -e "${BLUE}📡 Configuración UART:${NC}"
echo "   • Puerto:         /dev/serial0"
echo "   • Baudrate:       115200"
echo "   • Conexión:       PIN 8 (TX), PIN 10 (RX), PIN 6 (GND)"
echo ""
echo -e "${BLUE}🎮 Comandos disponibles:${NC}"
echo "   • sudo systemctl status camera_system    # Ver estado"
echo "   • sudo systemctl restart camera_system   # Reiniciar"
echo "   • sudo journalctl -u camera_system -f    # Ver logs"
echo "   • ls -lh /home/pi/videos/                # Ver videos"
echo ""
echo -e "${BLUE}🧪 Scripts de prueba:${NC}"
echo "   • cd ~/camera_system && bash test_hardware_encoder.sh"
echo "   • cd ~/camera_system && python3 test_uart.py -i"
echo ""
echo -e "${YELLOW}⚠ IMPORTANTE: Se recomienda reiniciar el sistema${NC}"
echo ""
echo -e "${GREEN}Reiniciar ahora? [S/n]${NC}"
read -r response

if [[ "$response" =~ ^([sS]|)$ ]]; then
    echo ""
    echo -e "${BLUE}Reiniciando en 3 segundos...${NC}"
    sleep 3
    reboot
else
    echo ""
    echo -e "${YELLOW}No olvides reiniciar manualmente:${NC}"
    echo "  sudo reboot"
    echo ""
fi
