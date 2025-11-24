#!/usr/bin/env python3
"""
Script de prueba para comunicación UART
Envía comandos de prueba y muestra respuestas
"""

import serial
import time
import json
import sys

def test_uart(port='/dev/serial0', baudrate=115200):
    """Prueba comunicación UART"""
    
    print(f"=== Test de Comunicación UART ===")
    print(f"Puerto: {port}")
    print(f"Baudrate: {baudrate}")
    print()
    
    try:
        # Abrir puerto serial
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=2
        )
        
        print("✓ Puerto UART abierto correctamente")
        time.sleep(1)
        
        # Lista de comandos de prueba
        test_commands = [
            {"type": "ping"},
            {"type": "status"},
            {"type": "start"},
            {"type": "zoom", "value": 1.5},
            {"type": "brightness", "value": 120},
            {"type": "status"},
            {"type": "stop"},
        ]
        
        print("\n--- Enviando comandos de prueba ---\n")
        
        for cmd in test_commands:
            # Enviar comando
            cmd_str = json.dumps(cmd)
            print(f"TX: {cmd_str}")
            ser.write(f"{cmd_str}\n".encode('utf-8'))
            
            # Esperar respuesta
            time.sleep(0.5)
            
            if ser.in_waiting > 0:
                response = ser.readline().decode('utf-8').strip()
                print(f"RX: {response}")
                
                try:
                    response_json = json.loads(response)
                    if response_json.get('status') == 'ok':
                        print("✓ Comando exitoso")
                    else:
                        print("✗ Error en comando")
                except json.JSONDecodeError:
                    print("⚠ Respuesta no es JSON válido")
            else:
                print("⚠ Sin respuesta")
            
            print()
            time.sleep(1)
        
        # Cerrar puerto
        ser.close()
        print("\n=== Prueba completada ===")
        
    except serial.SerialException as e:
        print(f"✗ Error de serial: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


def interactive_mode(port='/dev/serial0', baudrate=115200):
    """Modo interactivo para enviar comandos"""
    
    print(f"=== Modo Interactivo UART ===")
    print(f"Puerto: {port}")
    print(f"Baudrate: {baudrate}")
    print()
    print("Comandos disponibles:")
    print("  ping, status, start, stop")
    print("  zoom <valor>, brightness <valor>")
    print("  quit - Salir")
    print()
    
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=1
        )
        
        print("✓ Conectado\n")
        
        while True:
            # Input del usuario
            cmd_input = input("CMD> ").strip()
            
            if not cmd_input:
                continue
            
            if cmd_input.lower() == 'quit':
                break
            
            # Parsear comando
            parts = cmd_input.split()
            cmd_type = parts[0]
            
            if len(parts) > 1:
                command = {"type": cmd_type, "value": parts[1]}
            else:
                command = {"type": cmd_type}
            
            # Enviar
            cmd_str = json.dumps(command)
            ser.write(f"{cmd_str}\n".encode('utf-8'))
            print(f"TX: {cmd_str}")
            
            # Leer respuesta
            time.sleep(0.2)
            if ser.in_waiting > 0:
                response = ser.readline().decode('utf-8').strip()
                print(f"RX: {response}\n")
            else:
                print("Sin respuesta\n")
        
        ser.close()
        print("\nDesconectado")
        
    except KeyboardInterrupt:
        print("\n\nInterrumpido por usuario")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test de comunicación UART')
    parser.add_argument('--port', default='/dev/serial0', help='Puerto serial')
    parser.add_argument('--baudrate', type=int, default=115200, help='Velocidad')
    parser.add_argument('--interactive', '-i', action='store_true', help='Modo interactivo')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode(args.port, args.baudrate)
    else:
        test_uart(args.port, args.baudrate)
