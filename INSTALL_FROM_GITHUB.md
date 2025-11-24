# 📥 Instalación desde GitHub

## 🚀 Instalación en Un Solo Comando

### Opción 1: Instalación Automática (Recomendado)

```bash
# Copiar y pegar este comando en tu Raspberry Pi
curl -sSL https://raw.githubusercontent.com/TU_USUARIO/TU_REPO/main/quick_install.sh | sudo bash
```

**Reemplaza `TU_USUARIO` y `TU_REPO` con tu información de GitHub**

---

### Opción 2: Instalación Manual (Paso a Paso)

#### 1️⃣ Conectar a la Raspberry Pi

```bash
ssh pi@<IP_DE_TU_RASPBERRY>
# Contraseña por defecto: raspberry
```

#### 2️⃣ Descargar el Repositorio

```bash
# Instalar git si no lo tienes
sudo apt-get update
sudo apt-get install -y git

# Clonar el repositorio (reemplaza con tu URL)
cd ~
git clone https://github.com/TU_USUARIO/TU_REPO.git camera_system
cd camera_system
```

#### 3️⃣ Ejecutar Instalación

```bash
# Dar permisos de ejecución
chmod +x install.sh

# Ejecutar instalador
sudo bash install.sh
```

#### 4️⃣ Reiniciar

```bash
sudo reboot
```

---

### Opción 3: Instalación con wget (Sin Git)

```bash
# Descargar archivo ZIP
wget https://github.com/TU_USUARIO/TU_REPO/archive/refs/heads/main.zip

# Descomprimir
sudo apt-get install -y unzip
unzip main.zip
cd TU_REPO-main

# Instalar
chmod +x install.sh
sudo bash install.sh

# Reiniciar
sudo reboot
```

---

## ✅ Verificar Instalación

Después del reinicio:

```bash
# Ver estado del servicio
sudo systemctl status camera_system

# Ver logs en tiempo real
sudo journalctl -u camera_system -f

# Verificar que está funcionando
ps aux | grep camera_system
```

---

## 🔧 Comandos Post-Instalación

```bash
# Detener servicio
sudo systemctl stop camera_system

# Iniciar servicio
sudo systemctl start camera_system

# Reiniciar servicio
sudo systemctl restart camera_system

# Ver configuración
cat /etc/camera_system/config.json

# Editar configuración
sudo nano /etc/camera_system/config.json

# Ver videos grabados
ls -lh /home/pi/videos/
```

---

## 🧪 Probar el Sistema

### Test de Hardware Encoder

```bash
cd ~/camera_system
bash test_hardware_encoder.sh
```

### Test de UART

```bash
cd ~/camera_system
python3 test_uart.py
```

---

## 🐛 Solución de Problemas

### No se puede conectar por SSH

```bash
# Desde tu PC, buscar la Raspberry Pi en la red
nmap -sn 192.168.1.0/24

# O usar hostname
ping raspberrypi.local
ssh pi@raspberrypi.local
```

### Error de permisos en install.sh

```bash
chmod +x install.sh
sudo bash install.sh
```

### Git no está instalado

```bash
sudo apt-get update
sudo apt-get install -y git
```

### El servicio no inicia

```bash
# Ver error específico
sudo journalctl -u camera_system --no-pager -n 50

# Ejecutar manualmente para ver error
sudo python3 /opt/camera_system/camera_system.py
```

---

## 📝 Actualización del Sistema

Para actualizar a una nueva versión:

```bash
cd ~/camera_system

# Descargar cambios
git pull origin main

# Detener servicio
sudo systemctl stop camera_system

# Actualizar archivos
sudo cp camera_system.py /opt/camera_system/
sudo cp config.json /etc/camera_system/

# Reiniciar servicio
sudo systemctl restart camera_system
```

---

## 🎯 Inicio Rápido Completo

**Copia y pega todo esto en tu Raspberry Pi:**

```bash
# Actualizar sistema
sudo apt-get update

# Instalar git
sudo apt-get install -y git

# Clonar repositorio (REEMPLAZA CON TU URL)
cd ~
git clone https://github.com/TU_USUARIO/TU_REPO.git camera_system

# Entrar al directorio
cd camera_system

# Ejecutar instalador
sudo bash install.sh

# Reiniciar
sudo reboot
```

**Después del reinicio, verificar:**

```bash
sudo systemctl status camera_system
```

---

## 🔗 URLs de Ejemplo

Reemplaza en los comandos:

```
TU_USUARIO → tu_nombre_github
TU_REPO    → raspberry-camera-system
```

Ejemplo completo:
```bash
git clone https://github.com/tu_nombre_github/raspberry-camera-system.git camera_system
```

---

## ✨ ¡Listo!

El sistema debería estar funcionando. Puedes enviar comandos por UART:

```json
{"type":"start"}
{"type":"stop"}
{"type":"status"}
```

Videos se guardan en: `/home/pi/videos/`
