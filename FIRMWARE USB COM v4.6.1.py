from machine import I2C, Pin
import time
import struct

# 1. HARDWARE I2C: Mucho más rápido y estable. (Pines 8 y 9)
# Frecuencia a 400kHz (Fast Mode)
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)

# 2. PRE-ASIGNACIÓN DE MEMORIA: Evita picos de lag en el microcontrolador
v_buf = bytearray(2)
i_buf = bytearray(2)

# 3. TEMPORIZADOR ESTRICTO (10ms = 100Hz exactos)
interval_ms = 10
next_read = time.ticks_ms()

while True:
    try:
        current_ms = time.ticks_ms()
        
        # Ejecución NO bloqueante
        if time.ticks_diff(current_ms, next_read) >= 0:
            next_read = time.ticks_add(current_ms, interval_ms)
            
            # Leer voltaje directamente al buffer pre-asignado
            i2c.readfrom_mem_into(0x40, 0x02, v_buf)
            v_raw = struct.unpack('>H', v_buf)[0]
            voltaje = (v_raw * 1.25) / 1000.0
            
            # Leer corriente directamente al buffer pre-asignado
            i2c.readfrom_mem_into(0x40, 0x01, i_buf)
            i_raw = struct.unpack('>h', i_buf)[0]
            amperaje = abs((i_raw * 1.25) / 1000.0)
            
            # Enviar por USB (Timestamp, Voltaje, Corriente)
            print(f"{current_ms},{voltaje:.4f},{amperaje:.4f}")
            
    except Exception:
        # Fail-safe en caso de desconexión del cable I2C
        print(f"{time.ticks_ms()},0.0000,0.0000")
        time.sleep(0.1)