# 📋 Pasos para Instalar desde GitHub

## 🎯 Método Recomendado (Más Simple)

### Paso 1: Conecta a tu Raspberry Pi

Desde tu computadora:

```bash
ssh pi@192.168.1.XX
```

> Reemplaza `192.168.1.XX` con la IP de tu Raspberry Pi
> 
> Contraseña por defecto: `raspberry`

---

### Paso 2: Copia y pega estos 3 comandos

**Comando 1:** Instalar Git
```bash
sudo apt-get update && sudo apt-get install -y git
```

**Comando 2:** Descargar el proyecto (⚠️ CAMBIA LA URL)
```bash
git clone https://github.com/TU_USUARIO/TU_REPO.git camera_system
```

**Comando 3:** Instalar
```bash
cd camera_system && sudo bash install.sh
```

---

### Paso 3: Reinicia

```bash
sudo reboot
```

---

### Paso 4: Verifica que funciona

Después del reinicio, conéctate de nuevo y ejecuta:

```bash
sudo systemctl status camera_system
```

Si ves **"active (running)"** en verde → ✅ ¡Funciona!

---

## 📝 Ejemplo Completo con URLs Reales

Si tu repositorio está en:
```
https://github.com/jcarlos/raspberry-camera-system
```

Entonces ejecutas:

```bash
# 1. Conectar
ssh pi@192.168.1.100

# 2. Instalar git
sudo apt-get update && sudo apt-get install -y git

# 3. Clonar TU repositorio
git clone https://github.com/jcarlos/raspberry-camera-system.git camera_system

# 4. Instalar
cd camera_system && sudo bash install.sh

# 5. Reiniciar
sudo reboot
```

---

## 🚀 Método Alternativo (Un Solo Comando)

Si editaste el archivo `quick_install.sh` en GitHub con tu URL, puedes hacer:

```bash
curl -sSL https://raw.githubusercontent.com/TU_USUARIO/TU_REPO/main/quick_install.sh | sudo bash
```

---

## 🔍 Cómo Encontrar la IP de tu Raspberry Pi

### Opción 1: Con hostname
```bash
ping raspberrypi.local
```

### Opción 2: Escanear la red (desde tu PC)
```bash
# Windows
arp -a

# Linux/Mac
sudo nmap -sn 192.168.1.0/24
```

### Opción 3: Router
Busca en la interfaz web de tu router los dispositivos conectados.

---

## ✅ Lista de Verificación

- [ ] Raspberry Pi conectada a la red
- [ ] Conoces la IP de la Raspberry Pi
- [ ] Puedes conectarte por SSH
- [ ] Subiste los archivos a GitHub
- [ ] Tienes la URL de tu repositorio
- [ ] Cambiaste `TU_USUARIO/TU_REPO` por la URL real
- [ ] Conectaste la cámara USB
- [ ] Tienes espacio en la SD (al menos 8GB)

---

## 🎮 Después de Instalar

### Ver estado
```bash
sudo systemctl status camera_system
```

### Ver logs
```bash
sudo journalctl -u camera_system -f
```

### Enviar comando por UART
```bash
# Desde otro dispositivo conectado al UART
echo '{"type":"status"}' > /dev/serial0
```

### Ver videos grabados
```bash
ls -lh /home/pi/videos/
```

---

## 🐛 Si Algo Sale Mal

### No puedo conectar por SSH

1. Verifica que SSH está habilitado en la Raspberry Pi
2. Si es primera vez, crea archivo `ssh` vacío en la SD:
   ```bash
   touch /boot/ssh
   ```

### Error al clonar repositorio

- Verifica la URL de tu repositorio
- Asegúrate que el repositorio es público
- Verifica conexión a internet de la Raspberry Pi:
  ```bash
  ping google.com
  ```

### Instalación falla

Ejecuta manualmente para ver el error:
```bash
cd ~/camera_system
sudo bash install.sh
```

### Servicio no inicia

Ver logs de error:
```bash
sudo journalctl -u camera_system --no-pager
```

Ejecutar manualmente:
```bash
sudo python3 /opt/camera_system/camera_system.py
```

---

## 📞 Comandos Útiles

```bash
# Reiniciar servicio
sudo systemctl restart camera_system

# Detener servicio
sudo systemctl stop camera_system

# Ver configuración
cat /etc/camera_system/config.json

# Editar configuración
sudo nano /etc/camera_system/config.json

# Temperatura del sistema
vcgencmd measure_temp

# Espacio en disco
df -h

# Test de cámara
v4l2-ctl --list-devices
```

---

## 🎓 ¿Ahora Qué?

1. ✅ Sistema instalado y funcionando
2. 📡 Conecta dispositivo al UART (opcional)
3. 🎥 Envía comandos de grabación
4. 📹 Videos se guardan en `/home/pi/videos/`
5. ⚙️ Ajusta configuración según tus necesidades

Ver documentación completa en `README.md`

---

**¡Listo para grabar Full HD @ 30fps! 🎥✨**
