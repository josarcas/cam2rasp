#!/usr/bin/env python3
"""
Sistema de captura de video USB con control UART para Raspberry Pi Zero 2W
Optimizado para usar todos los recursos disponibles del sistema
"""

import cv2
import serial
import threading
import queue
import time
import os
import logging
from datetime import datetime
from pathlib import Path
import json
import signal
import sys
import subprocess
import shlex

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/camera_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CameraController:
    """Controla la cámara USB y gestiona grabación de video"""
    
    def __init__(self, config):
        self.config = config
        self.camera = None
        self.is_recording = False
        self.video_writer = None
        self.ffmpeg_process = None
        self.current_filename = None
        self.frame_queue = queue.Queue(maxsize=30)
        self.command_queue = queue.Queue()
        self.use_hardware_encoder = config.get('use_hardware_encoder', True)
        
    def initialize_camera(self):
        """Inicializa la cámara USB"""
        try:
            # Si usa hardware encoder, FFmpeg captura directamente desde /dev/videoX
            # No necesitamos abrir la cámara con OpenCV
            if self.use_hardware_encoder:
                # Solo verificar que el dispositivo existe
                device_path = f"/dev/video{self.config['camera']['device_id']}"
                if not os.path.exists(device_path):
                    raise Exception(f"Cámara USB no encontrada: {device_path}")
                logger.info(f"Cámara USB detectada: {device_path} (hardware encoding)")
                return True
            
            # Si usa software encoder, abrir con OpenCV
            self.camera = cv2.VideoCapture(self.config['camera']['device_id'])
            
            # Configurar resolución y FPS
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config['camera']['width'])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config['camera']['height'])
            self.camera.set(cv2.CAP_PROP_FPS, self.config['camera']['fps'])
            
            # Configurar buffer para reducir latencia
            self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            if not self.camera.isOpened():
                raise Exception("No se pudo abrir la cámara USB")
                
            logger.info("Cámara USB inicializada correctamente (software encoding)")
            return True
            
        except Exception as e:
            logger.error(f"Error al inicializar cámara: {e}")
            return False
    
    def start_recording(self):
        """Inicia la grabación de video con hardware H.264 encoder"""
        if self.is_recording:
            logger.warning("Ya se está grabando")
            return False
            
        try:
            # Crear directorio de videos si no existe
            video_dir = Path(self.config['storage']['video_path'])
            video_dir.mkdir(parents=True, exist_ok=True)
            
            # Generar nombre de archivo con timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.current_filename = video_dir / f"video_{timestamp}.h264"
            
            if self.use_hardware_encoder:
                # Usar hardware encoder con FFmpeg y V4L2
                self._start_hardware_recording()
            else:
                # Fallback a software encoder
                self._start_software_recording()
            
            self.is_recording = True
            logger.info(f"Grabación iniciada (H.264 hardware): {self.current_filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error al iniciar grabación: {e}")
            return False
    
    def _start_hardware_recording(self):
        """Inicia grabación usando hardware encoder H.264"""
        device_id = self.config['camera']['device_id']
        width = self.config['camera']['width']
        height = self.config['camera']['height']
        fps = self.config['camera']['fps']
        bitrate = self.config.get('bitrate', '4M')
        
        # Usar ffmpeg con hardware acceleration V4L2
        # El encoder h264_v4l2m2m usa el hardware encoder de la Raspberry Pi
        ffmpeg_cmd = [
            'ffmpeg',
            '-f', 'v4l2',
            '-input_format', 'mjpeg',  # o 'yuyv422' dependiendo de la cámara
            '-video_size', f'{width}x{height}',
            '-framerate', str(fps),
            '-i', f'/dev/video{device_id}',
            '-c:v', 'h264_v4l2m2m',  # Hardware encoder
            '-b:v', bitrate,
            '-pix_fmt', 'yuv420p',
            '-preset', 'ultrafast',
            '-tune', 'zerolatency',
            '-g', str(fps * 2),  # GOP size
            '-f', 'h264',
            str(self.current_filename)
        ]
        
        logger.info(f"Comando FFmpeg: {' '.join(ffmpeg_cmd)}")
        
        # Iniciar proceso FFmpeg
        self.ffmpeg_process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        
        logger.info("Hardware encoder H.264 iniciado")
    
    def _start_software_recording(self):
        """Fallback a grabación por software"""
        fourcc = cv2.VideoWriter_fourcc(*'H264')
        fps = self.config['camera']['fps']
        frame_size = (self.config['camera']['width'], self.config['camera']['height'])
        
        self.video_writer = cv2.VideoWriter(
            str(self.current_filename),
            fourcc,
            fps,
            frame_size
        )
        
        if not self.video_writer.isOpened():
            raise Exception("No se pudo crear el archivo de video")
    
    def stop_recording(self):
        """Detiene la grabación de video"""
        if not self.is_recording:
            return False
            
        self.is_recording = False
        
        # Detener hardware encoder (FFmpeg)
        if self.ffmpeg_process:
            try:
                # Enviar señal de terminación suave
                self.ffmpeg_process.stdin.write(b'q')
                self.ffmpeg_process.stdin.flush()
                self.ffmpeg_process.wait(timeout=5)
            except:
                # Forzar terminación si no responde
                self.ffmpeg_process.terminate()
                self.ffmpeg_process.wait(timeout=2)
            finally:
                self.ffmpeg_process = None
                logger.info(f"Hardware encoder detenido")
        
        # Detener software encoder
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
            
        logger.info(f"Grabación finalizada: {self.current_filename}")
        
        # Convertir .h264 a .mp4 para compatibilidad
        if str(self.current_filename).endswith('.h264'):
            self._convert_to_mp4()
            
        return True
    
    def _convert_to_mp4(self):
        """Convierte archivo H.264 raw a MP4 container"""
        try:
            h264_file = self.current_filename
            mp4_file = str(h264_file).replace('.h264', '.mp4')
            
            # Conversión rápida sin re-encoding
            convert_cmd = [
                'ffmpeg',
                '-i', str(h264_file),
                '-c:v', 'copy',  # No re-encode
                '-movflags', '+faststart',
                '-y',
                mp4_file
            ]
            
            result = subprocess.run(
                convert_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30
            )
            
            if result.returncode == 0:
                # Eliminar archivo H.264 original
                os.remove(h264_file)
                self.current_filename = Path(mp4_file)
                logger.info(f"Convertido a MP4: {mp4_file}")
            else:
                logger.warning(f"No se pudo convertir a MP4: {result.stderr.decode()}")
                
        except Exception as e:
            logger.error(f"Error en conversión a MP4: {e}")
    
    def capture_frames(self):
        """Captura frames de la cámara continuamente"""
        logger.info("Iniciando captura de frames")
        
        while True:
            # Cuando usa hardware encoder, FFmpeg captura directamente
            # Solo necesitamos procesar comandos
            if self.use_hardware_encoder and self.is_recording:
                # Procesar comandos de la cola
                try:
                    while not self.command_queue.empty():
                        cmd = self.command_queue.get_nowait()
                        self.process_camera_command(cmd)
                except queue.Empty:
                    pass
                
                time.sleep(0.1)  # Pausa más larga cuando usa hardware
                continue
            
            # Modo software encoder: capturar frames con OpenCV
            if self.camera is None or not self.camera.isOpened():
                logger.error("Cámara no disponible")
                time.sleep(1)
                continue
            
            ret, frame = self.camera.read()
            
            if not ret:
                logger.warning("Error al capturar frame")
                continue
            
            # Si está grabando con software encoder, escribir frame
            if self.is_recording and self.video_writer:
                try:
                    self.video_writer.write(frame)
                except Exception as e:
                    logger.error(f"Error al escribir frame: {e}")
            
            # Procesar comandos de la cola
            try:
                while not self.command_queue.empty():
                    cmd = self.command_queue.get_nowait()
                    self.process_camera_command(cmd)
            except queue.Empty:
                pass
            
            # Pequeña pausa para no saturar CPU
            time.sleep(0.001)
    
    def process_camera_command(self, command):
        """Procesa comandos para la cámara (zoom, etc)"""
        try:
            cmd_type = command.get('type', '')
            
            if cmd_type == 'zoom':
                zoom_level = command.get('value', 1.0)
                # Configurar zoom si la cámara lo soporta
                self.camera.set(cv2.CAP_PROP_ZOOM, zoom_level)
                logger.info(f"Zoom ajustado a: {zoom_level}")
                
            elif cmd_type == 'focus':
                focus_value = command.get('value', 0)
                self.camera.set(cv2.CAP_PROP_FOCUS, focus_value)
                logger.info(f"Focus ajustado a: {focus_value}")
                
            elif cmd_type == 'brightness':
                brightness = command.get('value', 128)
                self.camera.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
                logger.info(f"Brillo ajustado a: {brightness}")
                
            elif cmd_type == 'start_record':
                self.start_recording()
                
            elif cmd_type == 'stop_record':
                self.stop_recording()
                
            else:
                logger.warning(f"Comando desconocido: {cmd_type}")
                
        except Exception as e:
            logger.error(f"Error al procesar comando de cámara: {e}")
    
    def send_usb_command(self, command):
        """Agrega comando a la cola para ser procesado"""
        self.command_queue.put(command)
    
    def cleanup(self):
        """Limpia recursos de la cámara"""
        logger.info("Limpiando recursos de cámara")
        self.stop_recording()
        
        if self.camera:
            self.camera.release()
            self.camera = None


class UARTController:
    """Controla comunicación UART del header GPIO"""
    
    def __init__(self, config, camera_controller):
        self.config = config
        self.camera_controller = camera_controller
        self.serial_port = None
        self.is_running = False
        
    def initialize_uart(self):
        """Inicializa puerto UART"""
        try:
            uart_config = self.config['uart']
            self.serial_port = serial.Serial(
                port=uart_config['port'],
                baudrate=uart_config['baudrate'],
                bytesize=uart_config['bytesize'],
                parity=uart_config['parity'],
                stopbits=uart_config['stopbits'],
                timeout=uart_config['timeout']
            )
            
            logger.info(f"UART inicializado: {uart_config['port']} @ {uart_config['baudrate']}")
            return True
            
        except Exception as e:
            logger.error(f"Error al inicializar UART: {e}")
            return False
    
    def uart_communication_loop(self):
        """Loop principal de comunicación UART"""
        logger.info("Iniciando loop de comunicación UART")
        self.is_running = True
        
        while self.is_running:
            try:
                # Leer datos del UART
                if self.serial_port and self.serial_port.in_waiting > 0:
                    data = self.serial_port.readline().decode('utf-8').strip()
                    
                    if data:
                        logger.info(f"UART RX: {data}")
                        response = self.process_uart_command(data)
                        
                        # Enviar respuesta
                        if response:
                            self.send_uart_data(response)
                
                time.sleep(0.01)  # Pequeña pausa
                
            except serial.SerialException as e:
                logger.error(f"Error en comunicación UART: {e}")
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error inesperado en UART loop: {e}")
                time.sleep(1)
    
    def process_uart_command(self, data):
        """Procesa comandos recibidos por UART"""
        try:
            # Intentar parsear como JSON
            try:
                command = json.loads(data)
            except json.JSONDecodeError:
                # Si no es JSON, parsear como comando simple
                parts = data.split()
                if len(parts) < 1:
                    return {"status": "error", "message": "comando vacío"}
                
                command = {"type": parts[0]}
                if len(parts) > 1:
                    command["value"] = parts[1]
            
            # Ejecutar comando
            cmd_type = command.get('type', '').lower()
            
            if cmd_type == 'start':
                success = self.camera_controller.start_recording()
                return {"status": "ok" if success else "error", "command": "start_recording"}
                
            elif cmd_type == 'stop':
                success = self.camera_controller.stop_recording()
                return {"status": "ok" if success else "error", "command": "stop_recording"}
                
            elif cmd_type == 'zoom':
                value = float(command.get('value', 1.0))
                self.camera_controller.send_usb_command({'type': 'zoom', 'value': value})
                return {"status": "ok", "command": "zoom", "value": value}
                
            elif cmd_type == 'focus':
                value = int(command.get('value', 0))
                self.camera_controller.send_usb_command({'type': 'focus', 'value': value})
                return {"status": "ok", "command": "focus", "value": value}
                
            elif cmd_type == 'brightness':
                value = int(command.get('value', 128))
                self.camera_controller.send_usb_command({'type': 'brightness', 'value': value})
                return {"status": "ok", "command": "brightness", "value": value}
                
            elif cmd_type == 'status':
                return {
                    "status": "ok",
                    "recording": self.camera_controller.is_recording,
                    "filename": str(self.camera_controller.current_filename) if self.camera_controller.current_filename else None
                }
                
            elif cmd_type == 'ping':
                return {"status": "ok", "message": "pong"}
                
            else:
                return {"status": "error", "message": f"comando desconocido: {cmd_type}"}
                
        except Exception as e:
            logger.error(f"Error al procesar comando UART: {e}")
            return {"status": "error", "message": str(e)}
    
    def send_uart_data(self, data):
        """Envía datos por UART"""
        try:
            if self.serial_port and self.serial_port.is_open:
                # Convertir a JSON si es dict
                if isinstance(data, dict):
                    data = json.dumps(data)
                
                # Enviar con newline
                self.serial_port.write(f"{data}\n".encode('utf-8'))
                logger.info(f"UART TX: {data}")
                
        except Exception as e:
            logger.error(f"Error al enviar datos por UART: {e}")
    
    def cleanup(self):
        """Limpia recursos UART"""
        logger.info("Limpiando recursos UART")
        self.is_running = False
        
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()


class CameraSystem:
    """Sistema principal que coordina cámara y UART"""
    
    def __init__(self, config_path='/etc/camera_system/config.json'):
        self.config = self.load_config(config_path)
        self.camera_controller = CameraController(self.config)
        self.uart_controller = UARTController(self.config, self.camera_controller)
        self.threads = []
        self.is_running = False
        
        # Configurar señales para shutdown limpio
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def load_config(self, config_path):
        """Carga configuración desde archivo JSON"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuración cargada desde {config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"Archivo de configuración no encontrado, usando valores por defecto")
            return self.get_default_config()
        except Exception as e:
            logger.error(f"Error al cargar configuración: {e}")
            return self.get_default_config()
    
    def get_default_config(self):
        """Retorna configuración por defecto"""
        return {
            "camera": {
                "device_id": 0,
                "width": 1280,
                "height": 720,
                "fps": 30
            },
            "storage": {
                "video_path": "/home/pi/videos"
            },
            "uart": {
                "port": "/dev/serial0",
                "baudrate": 115200,
                "bytesize": 8,
                "parity": "N",
                "stopbits": 1,
                "timeout": 1
            }
        }
    
    def signal_handler(self, signum, frame):
        """Maneja señales de sistema para shutdown limpio"""
        logger.info(f"Señal recibida: {signum}")
        self.stop()
        sys.exit(0)
    
    def start(self):
        """Inicia el sistema completo"""
        logger.info("=== Iniciando Sistema de Cámara USB ===")
        
        # Inicializar cámara
        if not self.camera_controller.initialize_camera():
            logger.error("No se pudo inicializar la cámara")
            return False
        
        # Inicializar UART
        if not self.uart_controller.initialize_uart():
            logger.error("No se pudo inicializar UART")
            return False
        
        self.is_running = True
        
        # Iniciar thread de captura de frames
        camera_thread = threading.Thread(
            target=self.camera_controller.capture_frames,
            daemon=True,
            name="CameraThread"
        )
        camera_thread.start()
        self.threads.append(camera_thread)
        
        # Iniciar thread de comunicación UART
        uart_thread = threading.Thread(
            target=self.uart_controller.uart_communication_loop,
            daemon=True,
            name="UARTThread"
        )
        uart_thread.start()
        self.threads.append(uart_thread)
        
        logger.info("Sistema iniciado correctamente")
        logger.info("Esperando comandos por UART...")
        
        # Auto-iniciar grabación si está configurado
        if self.config.get('auto_start_recording', False):
            time.sleep(2)  # Esperar a que todo se estabilice
            self.camera_controller.start_recording()
        
        return True
    
    def run(self):
        """Mantiene el sistema ejecutándose"""
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Interrupción de teclado recibida")
            self.stop()
    
    def stop(self):
        """Detiene el sistema limpiamente"""
        logger.info("=== Deteniendo Sistema de Cámara USB ===")
        self.is_running = False
        
        # Limpiar recursos
        self.camera_controller.cleanup()
        self.uart_controller.cleanup()
        
        # Esperar a que threads terminen
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=2)
        
        logger.info("Sistema detenido")


def main():
    """Función principal"""
    # Verificar que se ejecuta como root o con permisos adecuados
    if os.geteuid() != 0:
        logger.warning("Se recomienda ejecutar como root para acceso completo a hardware")
    
    # Crear e iniciar sistema
    system = CameraSystem()
    
    if system.start():
        system.run()
    else:
        logger.error("No se pudo iniciar el sistema")
        sys.exit(1)


if __name__ == "__main__":
    main()
