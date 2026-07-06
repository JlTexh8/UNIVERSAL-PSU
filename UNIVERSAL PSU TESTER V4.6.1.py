import sys
import os
import time
import json
import csv
import threading
import socket
import http.server
import socketserver
import urllib.request
import urllib.parse
import webbrowser
import warnings
import numpy as np
import serial
import serial.tools.list_ports
from collections import deque

# Importaciones directas para PyQt6
import cv2
import pyqtgraph as pg
from PyQt6 import QtWidgets, QtCore, QtGui

# --- MOTOR RHI NATIVO DE QT6 (MÁXIMA EFICIENCIA, COMPATIBILIDAD .EXE) ---
pg.setConfigOptions(useOpenGL=False, antialias=False) 
warnings.filterwarnings("ignore")

# --- CONSTANTES ---
COLOR_BG = '#0A0A0A'
COLOR_GRAPH_BG = '#0D0D0D'
COLOR_V = '#00FF9C'
COLOR_A = '#FF00FF'
COLOR_W = '#FFEA00'
COLOR_BTN = '#1A1A1A'
COLOR_GRID = '#222222'
COLOR_LABELS = '#666666'
COLOR_CURSOR = '#00E5FF'
FONT_VALUES = 'Consolas'
FONT_LABELS = 'Verdana'

# 👇 CONFIGURACIÓN DE NUBE Y COMUNIDAD 👇
URL_DISCORD = "https://discord.gg/QvqQ6JQ88" 
URL_GITHUB_API = "https://api.github.com/repos/JlTexh8/UNIVERSAL-PSU-Reference-Measurements/git/trees/main?recursive=1"

web_data = {"V": 0.0, "A": 0.0, "W": 0.0, "Title": "UNIVERSAL PSU V4.6", "TimeWindow": 15}
user_lang = 'ES'

TEXTS = {
    'ES': {
        'menu_title': "UNIVERSAL PSU OPENSOURCE GITHUB",
        'port_avail': "👉 Puertos COM disponibles:",
        'port_sel': "👉 Selecciona el número de tu dispositivo USB: ",
        'connecting': "📡 Abriendo puerto ",
        'connected_usb': "✅ ¡Conectado por USB! Iniciando motor de gráficos...",
        'err_connect': "❌ Error al conectar al puerto: ",
        'web_ready': "🌐 ¡SERVIDOR WEB PRO LISTO!",
        'web_link': "👉 Link para navegador:",
        'web_pause': "|| PAUSA",
        'web_play': "▶ PLAY",
        'btn_snap': "FOTO",
        'btn_cloud': "☁ CLOUD",
        'diag_ok': "🟢 ESTADO: ÓPTIMO\nSecuencia idéntica a la referencia.",
        'diag_warn': "🟡 ESTADO: ACEPTABLE\nHay variaciones menores (ruido).",
        'diag_anom': "🟠 ESTADO: ANOMALÍA DETECTADA\nPosible fuga o consumo errático.",
        'diag_short': "🔴 ESTADO: PELIGRO - POSIBLE CORTO\nConsumo excesivamente alto.",
        'diag_open': "⚫ ESTADO: LÍNEA ABIERTA\nNo hay paso de corriente.",
        'diag_crit': "🔴 ESTADO: FALLA CRÍTICA\nSecuencia de arranque irregular.",
        'hotkeys_title': "--- ATAJOS DE TECLADO (INTERFAZ PRINCIPAL) ---",
        'hk_e': "[E]        : Editar el texto seleccionado",
        'hk_c': "[C]        : Cambiar el color del texto seleccionado",
        'hk_wasd': "[W][A][S][D] : Mover el elemento seleccionado",
        'hk_pm': "[+] / [-]  : Aumentar / Reducir tamaño del texto",
        'hk_zx': "[Z] / [X]  : Mover curva de Referencia (Izq / Der)",
        'hk_esc': "[ESC]      : Deseleccionar elemento",
        'hk_arrows': "[Flechas]  : Ajustar tamaño y posición de la gráfica",
        'set_title': "⚙️ Configuración",
        'set_time': "Ventana de Tiempo (Buffer de Memoria):",
        'set_warn': "* Cambiar este valor reseteará la gráfica actual.\n* La web se sincronizará automáticamente.",
        'save_title': "Modo de Guardado",
        'save_lbl': "Selecciona una opción para guardar la Referencia:",
        'save_prep': "1. REFERENCIA DE ENCENDIDO\n(Borra gráfica, cuenta 3-2-1 y grabas.\nTe pedirá dónde guardar al poner PAUSA)",
        'save_norm': "2. REFERENCIA NORMAL\n(Guarda instantáneamente la gráfica que\nestás viendo en pantalla ahora mismo)",
        'load_title': "Cargar Referencia",
        'load_lbl': "INSTRUCCIONES DE SINCRONIZACIÓN:",
        'load_inst': "1. DESCONECTA la placa de la corriente ahora.\n2. Presiona el botón de abajo y elige el archivo.\n3. Iniciará un cronómetro 3, 2, 1...\n4. CONECTA la placa exactamente cuando diga ¡GO!",
        'load_btn': "ENTENDIDO - ELEGIR ARCHIVO CSV",
        'trig_title': "Configuración de Disparo",
        'trig_mode': "Modo de Disparo:",
        'trig_opt1': "1. Post-Trigger (Grabar el futuro del pico)",
        'trig_opt2': "2. Pre-Trigger (Cortar y pausar inmediatamente)",
        'trig_lvl': "\nNivel de Disparo (A):",
        'trig_time': "\nTiempo Post-Trigger (s):",
        'edit_title': "Editar",
        'edit_prompt': "Texto:",
        'ref_title': "Nombre de Referencia",
        'ref_prompt': "Ingresa el modelo de la placa (Ej: iPhone 12 Pro):",
        'cloud_title': "Nube GitHub",
        'cloud_prompt': "Selecciona una firma oficial:",
        'cloud_msg_title': "¡Únete a la comunidad de reparaciones!",
        'cloud_msg_body': "Descarga las firmas oficiales de la nube o entra a nuestro Discord para compartir tus propios diagnósticos y añadirlos a esta base de datos global.",
        'btn_discord': "Ir al Discord",
        'btn_cloud_load': "Cargar Nube",
        'btn_cancel': "Cancelar",
        'msg_cloud_err': "No se pudo conectar a GitHub. Verifica la red.",
        'msg_cloud_empty': "El repositorio está vacío o no tiene CSVs.",
        'msg_vid_ok': "Video guardado en tu carpeta de Usuario.",
        'msg_save_ok': "Firma guardada correctamente.",
        'msg_load_err': "No se pudo cargar la firma.",
        'msg_exp_ok': "Datos exportados.",
        'msg_diag_err': "Falta cargar una Firma Base (LD REF).",
        'load_opt_title': "Modo de Visualización",
        'load_opt_msg': "¿Cómo deseas visualizar la firma de referencia?",
        'load_opt_live': "1. Live Sync (Diagnóstico)",
        'load_opt_replay': "2. Reproductor (Replay)",
        'load_opt_static': "3. Estático (Fijo)",
        'console_breakdown': "\n--- DESGLOSE DE BOTONES ---"
                             "\n[SNAP]   : Tomar captura de pantalla."
                             "\n[SV REF] : Guardar curva actual como Firma (Save Reference)."
                             "\n[LD REF] : Cargar una Firma base (Load Reference)."
                             "\n[☁ CLOUD]: Descargar firmas de la base de datos global."
                             "\n[CSV]    : Exportar datos a Excel."
                             "\n[DIAG]   : Diagnóstico automático (Compara actual vs Referencia)."
                             "\n[TRIG]   : Configurar disparador automático (Osciloscopio)."
                             "\n[⚙ SET]  : Ajustar ventana de tiempo (Buffer)."
                             "\n[●]      : Grabar video de la gráfica.\n"
    },
    'EN': {
        'menu_title': "UNIVERSAL PSU OPENSOURCE GITHUB",
        'port_avail': "👉 Available COM Ports:",
        'port_sel': "👉 Select your USB device number: ",
        'connecting': "📡 Opening port ",
        'connected_usb': "✅ Connected via USB! Starting graphics engine...",
        'err_connect': "❌ Connection error on port: ",
        'web_ready': "🌐 PRO WEB SERVER READY!",
        'web_link': "👉 Browser link:",
        'web_pause': "|| PAUSE",
        'web_play': "▶ PLAY",
        'btn_snap': "SNAP",
        'btn_cloud': "☁ CLOUD",
        'diag_ok': "🟢 STATUS: OPTIMAL\nSequence identical to reference.",
        'diag_warn': "🟡 STATUS: ACCEPTABLE\nMinor variations (noise) detected.",
        'diag_anom': "🟠 STATUS: ANOMALY DETECTED\nPossible leakage or erratic draw.",
        'diag_short': "🔴 STATUS: DANGER - POSSIBLE SHORT\nExcessively high current draw.",
        'diag_open': "⚫ STATUS: OPEN LINE\nNo current flow detected.",
        'diag_crit': "🔴 STATUS: CRITICAL FAILURE\nIrregular boot sequence.",
        'hotkeys_title': "--- HOTKEYS (MAIN INTERFACE) ---",
        'hk_e': "[E]        : Edit selected text",
        'hk_c': "[C]        : Change selected text color",
        'hk_wasd': "[W][A][S][D] : Move selected element",
        'hk_pm': "[+] / [-]  : Increase / Decrease text size",
        'hk_zx': "[Z] / [X]  : Move Reference curve (Left / Right)",
        'hk_esc': "[ESC]      : Deselect element",
        'hk_arrows': "[Arrows]   : Adjust graph size and position",
        'set_title': "⚙️ Settings",
        'set_time': "Time Window (Memory Buffer):",
        'set_warn': "* Changing this value will reset the current graph.\n* Web server will sync automatically.",
        'save_title': "Save Mode",
        'save_lbl': "Select an option to save the Reference:",
        'save_prep': "1. BOOT REFERENCE\n(Clears graph, counts 3-2-1 and records.\nWill ask where to save when PAUSED)",
        'save_norm': "2. NORMAL REFERENCE\n(Instantly saves the graph currently\nvisible on your screen)",
        'load_title': "Load Reference",
        'load_lbl': "SYNC INSTRUCTIONS:",
        'load_inst': "1. DISCONNECT the logic board from power now.\n2. Press the button below and select the file.\n3. A 3-2-1 countdown will begin...\n4. CONNECT the board exactly when it says GO!",
        'load_btn': "UNDERSTOOD - CHOOSE CSV FILE",
        'trig_title': "Trigger Setup",
        'trig_mode': "Trigger Mode:",
        'trig_opt1': "1. Post-Trigger (Record the future of the spike)",
        'trig_opt2': "2. Pre-Trigger (Cut and pause immediately)",
        'trig_lvl': "\nTrigger Level (A):",
        'trig_time': "\nPost-Trigger Time (s):",
        'edit_title': "Edit",
        'edit_prompt': "Text:",
        'ref_title': "Reference Name",
        'ref_prompt': "Enter board model (e.g. iPhone 12 Pro):",
        'cloud_title': "GitHub Cloud",
        'cloud_prompt': "Select an official signature:",
        'cloud_msg_title': "Join the repair community!",
        'cloud_msg_body': "Download official signatures from the cloud or join our Discord to share your own diagnostics and add them to this global database.",
        'btn_discord': "Go to Discord",
        'btn_cloud_load': "Load Cloud",
        'btn_cancel': "Cancel",
        'msg_cloud_err': "Could not connect to GitHub. Check network.",
        'msg_cloud_empty': "The repository is empty or has no CSV files.",
        'msg_vid_ok': "Video saved to your User folder.",
        'msg_save_ok': "Signature saved successfully.",
        'msg_load_err': "Could not load the signature.",
        'msg_exp_ok': "Data exported successfully.",
        'msg_diag_err': "Missing Base Signature (LD REF).",
        'load_opt_title': "Viewing Mode",
        'load_opt_msg': "How do you want to view the reference signature?",
        'load_opt_live': "1. Live Sync (Diag)",
        'load_opt_replay': "2. Reproductor (Replay)",
        'load_opt_static': "3. Static (Fixed)",
        'console_breakdown': "\n--- BUTTON BREAKDOWN ---"
                             "\n[SNAP]   : Take a screenshot."
                             "\n[SV REF] : Save current curve as Signature (Save Reference)."
                             "\n[LD REF] : Load a base Signature (Load Reference)."
                             "\n[☁ CLOUD]: Download signatures from the global database."
                             "\n[CSV]    : Export data to Excel."
                             "\n[DIAG]   : Automatic diagnostics (Compares current vs Reference)."
                             "\n[TRIG]   : Setup automatic trigger (Oscilloscope mode)."
                             "\n[⚙ SET]  : Adjust time window (Buffer)."
                             "\n[●]      : Record video of the graph.\n"
    }
}

def t(key): return TEXTS[user_lang].get(key, key)

def mostrar_atajos():
    print(t('console_breakdown'))
    print(f"\n{t('hotkeys_title')}")
    print(t('hk_e'))
    print(t('hk_c'))
    print(t('hk_wasd'))
    print(t('hk_pm'))
    print(t('hk_zx'))
    print(t('hk_esc'))
    print(t('hk_arrows'))
    print("-" * 50 + "\n")

# ==========================================
# MENÚS Y DIÁLOGOS DE CONFIGURACIÓN
# ==========================================
class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, current_time, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t('set_title'))
        self.setStyleSheet(f"background-color: {COLOR_BG}; color: white; font-family: {FONT_LABELS}; font-size: 13px;")
        layout = QtWidgets.QVBoxLayout(self)

        layout.addWidget(QtWidgets.QLabel(t('set_time')))
        self.time_combo = QtWidgets.QComboBox()
        self.time_combo.addItems(["5", "10", "15", "30", "60", "120", "300"]) 
        self.time_combo.setCurrentText(str(int(current_time)))
        self.time_combo.setStyleSheet(f"background: {COLOR_BTN}; color: white; padding: 5px; font-weight: bold;")
        layout.addWidget(self.time_combo)
        
        info = QtWidgets.QLabel(t('set_warn'))
        info.setStyleSheet("color: #FF3333; font-size: 11px;")
        layout.addWidget(info)

        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def get_values(self):
        return int(self.time_combo.currentText())

class SaveModeDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t('save_title'))
        self.setStyleSheet(f"background-color: {COLOR_BG}; color: white; font-family: {FONT_LABELS}; font-size: 13px;")
        layout = QtWidgets.QVBoxLayout(self)
        lbl = QtWidgets.QLabel(t('save_lbl'))
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)
        self.btn_prep = QtWidgets.QPushButton(t('save_prep'))
        self.btn_prep.setStyleSheet(f"background: #FF3333; color: white; padding: 15px; font-weight: bold; border-radius: 5px; margin-top: 10px;")
        self.btn_save = QtWidgets.QPushButton(t('save_norm'))
        self.btn_save.setStyleSheet(f"background: #00FF9C; color: black; padding: 15px; font-weight: bold; border-radius: 5px; margin-top: 10px;")
        layout.addWidget(self.btn_prep)
        layout.addWidget(self.btn_save)
        self.mode = None
        self.btn_prep.clicked.connect(self.select_prep)
        self.btn_save.clicked.connect(self.select_save)
        
    def select_prep(self):
        self.mode = 'PREP'
        self.accept()
    def select_save(self):
        self.mode = 'SAVE'
        self.accept()

class LoadModeDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t('load_title'))
        self.setStyleSheet(f"background-color: {COLOR_BG}; color: white; font-family: {FONT_LABELS}; font-size: 13px;")
        layout = QtWidgets.QVBoxLayout(self)
        lbl = QtWidgets.QLabel(t('load_lbl'))
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #00FF9C;")
        layout.addWidget(lbl)
        info = QtWidgets.QLabel(t('load_inst'))
        info.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        self.btn_ok = QtWidgets.QPushButton(t('load_btn'))
        self.btn_ok.setStyleSheet(f"background: {COLOR_A}; color: black; padding: 15px; font-weight: bold; border-radius: 5px; margin-top: 10px;")
        self.btn_ok.clicked.connect(self.accept)
        layout.addWidget(self.btn_ok)

class TriggerDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t('trig_title'))
        self.setStyleSheet(f"background-color: {COLOR_BG}; color: white; font-family: {FONT_LABELS}; font-size: 12px;")
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel(t('trig_mode')))
        self.mode_combo = QtWidgets.QComboBox()
        self.mode_combo.addItems([t('trig_opt1'), t('trig_opt2')])
        self.mode_combo.setStyleSheet(f"background: {COLOR_BTN}; color: white; padding: 5px;")
        self.mode_combo.currentIndexChanged.connect(self.update_ui)
        layout.addWidget(self.mode_combo)
        layout.addWidget(QtWidgets.QLabel(t('trig_lvl')))
        self.amp_spin = QtWidgets.QDoubleSpinBox()
        self.amp_spin.setRange(0.001, 20.0)
        self.amp_spin.setDecimals(3)
        self.amp_spin.setValue(1.500)
        self.amp_spin.setStyleSheet(f"background: {COLOR_BTN}; color: {COLOR_A}; padding: 5px; font-weight: bold;")
        layout.addWidget(self.amp_spin)
        layout.addWidget(QtWidgets.QLabel(t('trig_time')))
        self.time_spin = QtWidgets.QDoubleSpinBox()
        self.time_spin.setRange(0.5, 9.5)
        self.time_spin.setDecimals(1)
        self.time_spin.setValue(5.0)
        self.time_spin.setStyleSheet(f"background: {COLOR_BTN}; color: {COLOR_V}; padding: 5px; font-weight: bold;")
        layout.addWidget(self.time_spin)
        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
        
    def update_ui(self):
        if self.mode_combo.currentIndex() == 1: self.time_spin.setEnabled(False)
        else: self.time_spin.setEnabled(True)
    def get_values(self):
        return self.amp_spin.value(), self.time_spin.value(), self.mode_combo.currentIndex()

# ==========================================
# SERVIDOR WEB (BaseHTTPRequestHandler)
# ==========================================
class WebHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = f"""
            <!DOCTYPE html>
            <html translate="no" class="notranslate">
            <head>
            <title>JlTexh Monitor Web Pro</title>
            <meta name="google" content="notranslate">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
            <style>
                :root {{ --col-v: {COLOR_V}; --col-a: {COLOR_A}; --col-w: {COLOR_W}; --f-size: 4.5rem; }}
                body {{ background-color: {COLOR_BG}; color: white; font-family: '{FONT_LABELS}', sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; overflow: hidden; }}
                .container {{ position: relative; background-color: {COLOR_GRAPH_BG}; padding: 30px; border-radius: 20px; text-align: center; border: 2px solid #333; box-shadow: 0 0 20px rgba(0,0,0,0.8); width: 90%; max-width: 900px; }}
                h1 {{ color: {COLOR_LABELS}; font-size: 1.8rem; letter-spacing: 2px; margin-bottom: 20px; text-transform: uppercase; }}
                .vals-container {{ display: flex; justify-content: space-around; margin-bottom: 20px; }}
                .val-box {{ font-family: '{FONT_VALUES}', monospace; font-size: var(--f-size); font-weight: bold; text-shadow: 0 0 10px rgba(255,255,255,0.1); transition: font-size 0.2s; }}
                .graph-container {{ position: relative; width: 100%; height: 250px; background-color: {COLOR_GRAPH_BG}; border-radius: 5px; overflow: hidden; border: 1px solid #222; margin-bottom: 20px; }}
                canvas {{ display: block; width: 100%; height: 100%; }}
                .controls {{ display: flex; justify-content: center; gap: 15px; background: #111; padding: 15px; border-radius: 10px; align-items: center; font-size: 0.9rem; color: #888; border: 1px solid #333; flex-wrap: wrap; }}
                .action-btn {{ background: {COLOR_BTN}; color: white; border: 1px solid #333; padding: 10px 15px; border-radius: 5px; font-weight: bold; cursor: pointer; transition: 0.2s; font-family: 'Verdana'; }}
                .action-btn:hover {{ background: #333; }}
                #btn-plus-web {{ color: {COLOR_V}; }}
                #btn-minus-web {{ color: {COLOR_A}; }}
                #btn-pause-web {{ color: #00E5FF; }}
                #btn-snap-web {{ color: #FF3333; }}
                input[type="color"] {{ border: none; width: 30px; height: 30px; border-radius: 5px; cursor: pointer; background: none; padding: 0; }}
                .control-group {{ display: flex; align-items: center; gap: 8px; }}
                .watermark {{ position: absolute; bottom: 15px; right: 20px; color: #444; font-size: 0.9rem; font-weight: bold; pointer-events: none; }}
            </style>
            </head>
            <body>
                <div class="container" id="main-container">
                    <h1 id="web-title">UNIVERSAL PSU V4.6</h1>
                    <div class="vals-container">
                        <div class="val-box"><span style="color: var(--col-v)">V</span> <span id="val-v" style="color: var(--col-v)">0.000</span></div>
                        <div class="val-box"><span style="color: var(--col-a)">A</span> <span id="val-a" style="color: var(--col-a)">0.000</span></div>
                        <div class="val-box"><span style="color: var(--col-w)">W</span> <span id="val-w" style="color: var(--col-w)">0.000</span></div>
                    </div>
                    <div class="graph-container">
                        <canvas id="graph"></canvas>
                    </div>
                    
                    <div class="controls" data-html2canvas-ignore="true">
                        <button class="action-btn" id="btn-plus-web" onclick="zoomInWeb()">+</button>
                        <button class="action-btn" id="btn-minus-web" onclick="zoomOutWeb()">-</button>
                        <button class="action-btn" id="btn-pause-web" onclick="togglePauseWeb()">{t('web_pause')}</button>
                        <button class="action-btn" id="btn-snap-web" onclick="takeSnapWeb()">📷 {t('btn_snap')}</button>
                        <span style="margin: 0 10px; border-left: 1px solid #333; height: 30px;"></span>
                        <div class="control-group">V <input type="color" id="in-v" value="{COLOR_V}"></div>
                        <div class="control-group">A <input type="color" id="in-a" value="{COLOR_A}"></div>
                        <div class="control-group">W <input type="color" id="in-w" value="{COLOR_W}"></div>
                        <span style="margin: 0 10px; border-left: 1px solid #333; height: 30px;"></span>
                        <div class="control-group">Tamaño: <input type="range" id="in-size" min="1" max="8" step="0.1" value="4.5"></div>
                    </div>
                    <div class="watermark">Youtube JlTexh8 Tester V4.6</div>
                </div>
                <script>
                    const root = document.documentElement;
                    const canvas = document.getElementById('graph');
                    const ctx = canvas.getContext('2d');
                    let graphColorA = '{COLOR_A}';
                    let isWebPaused = false;
                    let webZoomFactor = 1.0; 
                    
                    let currentTimeWindow = 15;
                    let targetHistoryLength = currentTimeWindow * 20; 
                    let historyData = new Array(targetHistoryLength).fill(0); 

                    document.getElementById('in-v').addEventListener('input', e => root.style.setProperty('--col-v', e.target.value));
                    document.getElementById('in-a').addEventListener('input', e => {{
                        root.style.setProperty('--col-a', e.target.value);
                        graphColorA = e.target.value;
                        if(isWebPaused) draw(); 
                    }});
                    document.getElementById('in-w').addEventListener('input', e => root.style.setProperty('--col-w', e.target.value));
                    document.getElementById('in-size').addEventListener('input', e => root.style.setProperty('--f-size', e.target.value + 'rem'));

                    function zoomInWeb() {{ webZoomFactor += 0.2; if(isWebPaused) draw(); }}
                    function zoomOutWeb() {{ webZoomFactor = Math.max(0.2, webZoomFactor - 0.2); if(isWebPaused) draw(); }}

                    function togglePauseWeb() {{
                        isWebPaused = !isWebPaused;
                        document.getElementById('btn-pause-web').innerText = isWebPaused ? '{t("web_play")}' : '{t("web_pause")}';
                        document.getElementById('btn-pause-web').style.color = isWebPaused ? '{COLOR_V}' : '#00E5FF';
                    }}

                    function takeSnapWeb() {{
                        const btn = document.getElementById('btn-snap-web');
                        const originalText = btn.innerText;
                        btn.innerText = '...';
                        html2canvas(document.getElementById('main-container'), {{ backgroundColor: '{COLOR_BG}', scale: 2 }}).then(canvasExport => {{
                            const link = document.createElement('a');
                            link.download = 'JlTexh_Web_Panorama_' + new Date().getTime() + '.png';
                            link.href = canvasExport.toDataURL('image/png');
                            link.click();
                            btn.innerText = originalText;
                        }});
                    }}

                    function resizeCanvas() {{
                        canvas.width = canvas.parentElement.clientWidth;
                        canvas.height = canvas.parentElement.clientHeight;
                        if(isWebPaused) draw();
                    }}
                    window.addEventListener('resize', resizeCanvas);
                    resizeCanvas();

                    function hexToRgb(hex) {{
                        let bigint = parseInt(hex.replace('#', ''), 16);
                        return {{ r: (bigint >> 16) & 255, g: (bigint >> 8) & 255, b: bigint & 255 }};
                    }}

                    function draw() {{
                        ctx.fillStyle = '{COLOR_GRAPH_BG}';
                        ctx.fillRect(0, 0, canvas.width, canvas.height);
                        
                        let actualMax = Math.max(...historyData);
                        if (actualMax < 0.5) actualMax = 0.5; 
                        let maxA = actualMax / webZoomFactor; 
                        
                        let leftMargin = 50; 
                        let drawWidth = canvas.width - leftMargin;

                        ctx.strokeStyle = '{COLOR_GRID}';
                        ctx.fillStyle = '{COLOR_LABELS}';
                        ctx.font = '12px Verdana';
                        ctx.textAlign = 'right';
                        ctx.textBaseline = 'middle';
                        ctx.lineWidth = 1;

                        for(let i=0; i<=5; i++) {{ 
                            let val = maxA - (maxA / 5) * i;
                            let y = (canvas.height / 5) * i;
                            if(i===0) y += 10;
                            if(i===5) y -= 10;
                            ctx.beginPath(); ctx.moveTo(leftMargin, y); ctx.lineTo(canvas.width, y); ctx.stroke();
                            ctx.fillText(val.toFixed(2) + 'A', leftMargin - 5, y);
                        }}

                        for(let i=1; i<10; i++) {{ 
                            let x = leftMargin + (drawWidth / 10) * i;
                            ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
                        }}

                        ctx.beginPath();
                        ctx.strokeStyle = graphColorA;
                        ctx.lineWidth = 2.5;
                        ctx.lineJoin = 'round';
                        
                        let firstX = 0;
                        let lastX = 0;

                        for(let i=0; i<historyData.length; i++) {{
                            let x = leftMargin + (i / (historyData.length - 1)) * drawWidth;
                            let y = canvas.height - (historyData[i] / maxA) * canvas.height;
                            y = Math.max(2, Math.min(canvas.height - 2, y)); 
                            
                            if(i===0) {{ 
                                ctx.moveTo(x,y); 
                                firstX = x; 
                            }} else {{ 
                                ctx.lineTo(x,y); 
                            }}
                            lastX = x;
                        }}
                        
                        ctx.stroke();

                        ctx.lineTo(lastX, canvas.height);
                        ctx.lineTo(firstX, canvas.height);
                        ctx.closePath();

                        let rgbColor = hexToRgb(graphColorA);
                        ctx.fillStyle = 'rgba(' + rgbColor.r + ', ' + rgbColor.g + ', ' + rgbColor.b + ', 0.2)';
                        ctx.fill();
                    }}

                    setInterval(() => {{
                        if(isWebPaused) return; 
                        fetch('/data?t=' + Date.now(), {{ cache: 'no-store' }}).then(response => response.json()).then(data => {{
                            document.getElementById('web-title').innerText = data.Title;
                            document.getElementById('val-v').innerText = data.V.toFixed(3);
                            document.getElementById('val-a').innerText = data.A.toFixed(3);
                            document.getElementById('val-w').innerText = data.W.toFixed(3);
                            
                            if (data.TimeWindow !== currentTimeWindow) {{
                                currentTimeWindow = data.TimeWindow;
                                targetHistoryLength = currentTimeWindow * 20;
                            }}
                            
                            historyData.push(data.A);
                            
                            while (historyData.length > targetHistoryLength) {{
                                historyData.shift();
                            }}
                            
                            draw();
                        }}).catch(e => console.log('Esperando datos...'));
                    }}, 50); 
                    draw();
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
        elif self.path.startswith('/data'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(web_data).encode('utf-8'))
        else: 
            self.send_response(404)
            self.end_headers()
            
    def log_message(self, format, *args): pass 

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer): daemon_threads = True

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))
        return s.getsockname()[0]
    except Exception: return '127.0.0.1'

def start_web_server_thread(port=8080):
    ThreadedHTTPServer.allow_reuse_address = False 
    try:
        httpd = ThreadedHTTPServer(("0.0.0.0", port), WebHandler)
        print(f"\n{t('web_ready')}\n{t('web_link')} http://{get_local_ip()}:{port}", flush=True)
        httpd.serve_forever()
    except OSError:
        if port < 8100: 
            start_web_server_thread(port + 1)

# ==========================================
# LECTURA USB SERIAL OPTIMIZADA CON COLAS FIFO
# ==========================================
class SerialStream:
    def __init__(self, port, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.data_queue = deque(maxlen=2000) 
        self.new_data_ready = False 
        self.running = True

        print(f"\n{t('connecting')}{self.port}...")
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0.05)
            print(t('connected_usb'))
        except Exception as e:
            print(f"{t('err_connect')}{e}")
            sys.exit()

        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()

    def _listen_loop(self):
        while self.running:
            try:
                if self.ser.in_waiting > 0:
                    linea_bytes = self.ser.readline()
                    try:
                        txt = linea_bytes.decode('utf-8').strip()
                        if txt.count(",") == 2:
                            t_esp, v, i = map(float, txt.split(","))
                            self.data_queue.append((t_esp / 1000.0, v, abs(i) if abs(i) > 0.015 else 0.0))
                            self.new_data_ready = True 
                    except ValueError:
                        pass
                else:
                    time.sleep(0.001) 
            except serial.SerialException:
                pass
            except Exception:
                time.sleep(0.01)

    def flush_buffers(self):
        # 1. Vacía nuestra cola interna en Python
        self.data_queue.clear()
        # 2. Vacía el buffer a nivel de sistema operativo para eliminar el lag acumulado
        try:
            self.ser.reset_input_buffer()
        except:
            pass

# ==========================================
# INTERFAZ GRÁFICA Y LÓGICA PRINCIPAL
# ==========================================
class OverlayLabel(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal(object)

    def __init__(self, text, color, font_size, rel_x, fixed_y, parent=None):
        super().__init__(text, parent)
        self.base_color = color
        self.font_size = font_size
        self.relX = rel_x     
        self.fixedY = fixed_y 
        self.offsetX = 0      
        self.offsetY = 0
        self.selected = False
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setMinimumWidth(350)  
        self.setMinimumHeight(60)  
        self.update_style()
        self.show()

    def mousePressEvent(self, event): self.clicked.emit(self)

    def update_style(self):
        border = "2px dashed #00E5FF" if self.selected else "none"
        self.setStyleSheet(f"color: {self.base_color}; font-family: {FONT_VALUES}; font-size: {self.font_size}px; font-weight: bold; border: {border}; background: transparent; padding: 8px;")
        self.adjustSize()

class JlTexhMonitor(QtWidgets.QMainWindow):
    def __init__(self, stream):
        super().__init__()
        self.stream = stream
        self.setWindowTitle(t('menu_title'))
        self.resize(900, 650)
        self.setStyleSheet(f"background-color: {COLOR_BG}; color: white; font-family: {FONT_LABELS};")

        # --- GESTIÓN DE MEMORIA POR PUNTERO CÍCLICO ---
        self.time_window = 15 
        self.hz_margin = 150 
        self.max_puntos = self.time_window * self.hz_margin 
        
        self.ptr = 0 
        self.tiempos = np.zeros(self.max_puntos)
        self.voltajes = np.zeros(self.max_puntos)
        self.corrientes = np.zeros(self.max_puntos)
        self.ref_data = (np.array([]), np.array([]))
        self.ref_mode = 'live'

        self.is_paused = False
        self.trigger_threshold = None
        self.trigger_mode = 0 
        self.is_recording = False
        self.video_writer = None
        
        self.post_trigger_active = False
        self.post_trigger_target_time = 0
        self.custom_post_trigger_time = 5.0 
        
        self.pending_save_active = False
        self.pending_save_name = ""
        self.temp_ref_data = (np.array([]), np.array([]))
        self.temp_ref_name = ""
        
        self.ref_time_offset = 0.0  
        self.graph_margin_h = 0
        self.graph_margin_v = 0
        self.selected_label = None
        self.dynamic_labels = []
        
        self.replay_active = False
        self.replay_start_time = 0

        self.init_ui()

        # REFRESH A 30ms (~33 FPS) para rendimiento extremo en Pantalla Completa
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(30)
        
        self.countdown_timer = QtCore.QTimer()
        self.countdown_timer.timeout.connect(self.process_countdown)
        self.countdown_step = 0
        self.countdown_mode = ""

        self.start_time_hw = None
        self.pause_time_accum = 0

    def init_ui(self):
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QtWidgets.QVBoxLayout(main_widget)
        self.main_layout.setContentsMargins(15, 130, 15, 15)

        self.lbl_title = OverlayLabel("UNIVERSAL PSU V4.6", "#FFFFFF", 22, 0.5, 10, main_widget)
        self.lbl_v = OverlayLabel("V 0.000", COLOR_V, 38, 0.2, 50, main_widget)
        self.lbl_a = OverlayLabel("A 0.000", COLOR_A, 38, 0.5, 50, main_widget)
        self.lbl_w = OverlayLabel("W 0.000", COLOR_W, 38, 0.8, 50, main_widget)
        
        # Etiqueta LD REF centrada (Ajuste de coordenada Y)
        self.lbl_ref_name = OverlayLabel("", "#00FF9C", 24, 0.5, 300, main_widget)
        self.lbl_ref_name.hide() 
        
        self.dynamic_labels = [self.lbl_title, self.lbl_v, self.lbl_a, self.lbl_w, self.lbl_ref_name]
        for lbl in self.dynamic_labels:
            lbl.clicked.connect(self.label_selected)

        self.lbl_countdown = QtWidgets.QLabel("", main_widget)
        self.lbl_countdown.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lbl_countdown.hide()

        btn_layout = QtWidgets.QHBoxLayout()
        def create_btn(text, color, callback):
            btn = QtWidgets.QPushButton(text)
            btn.setStyleSheet(f"background-color: {COLOR_BTN}; color: {color}; font-weight: bold; padding: 8px; border: 1px solid #333; border-radius: 4px;")
            btn.clicked.connect(callback)
            btn_layout.addWidget(btn)
            return btn

        self.btn_pause = create_btn("||", "#00E5FF", self.toggle_pause)
        create_btn("<<", "#FFFF00", self.move_left)
        create_btn(">>", "#FFFF00", self.move_right)
        create_btn(t('btn_snap'), "#FF3333", self.take_snap)
        create_btn("SV REF", "#FFFFFF", self.save_ref)
        self.btn_lref = create_btn("LD REF", "#00FF9C", self.load_ref)
        create_btn(t('btn_cloud'), "#FFD700", self.load_from_github) # Color Dorado Premium
        create_btn("CSV", "#FFFFFF", self.export_csv)
        create_btn("DIAG", "#FF3333", self.auto_diagnostico)
        self.btn_trig = create_btn("TRIG", "#FFFFFF", self.set_trigger)
        self.btn_set = create_btn("⚙️ SET", "#FFFFFF", self.open_settings) 
        self.btn_rec = create_btn("●", "#FF0000", self.toggle_record)
        self.main_layout.addLayout(btn_layout)

        graph_container = QtWidgets.QWidget()
        self.graph_layout = QtWidgets.QVBoxLayout(graph_container)
        self.graph_layout.setContentsMargins(0, 0, 0, 0)
        
        self.graph = pg.PlotWidget()
        self.graph.setBackground(COLOR_GRAPH_BG)
        self.graph.showGrid(x=True, y=True, alpha=0.3)
        self.graph.setYRange(-0.02, 0.5)
        self.graph.setXRange(-self.time_window, 0)
        self.graph.setLimits(xMax=0)
        self.graph.setMouseEnabled(x=False, y=False)
        
        # --- CONFIGURACIÓN DE CURVAS PARA PYQT6 ---
        color_fill = QtGui.QColor(COLOR_A)
        color_fill.setAlpha(50) 

        self.curve_ref = self.graph.plot(pen=pg.mkPen(color='#555555', width=2, style=QtCore.Qt.PenStyle.DashLine))
        self.curve_live = self.graph.plot(
            pen=pg.mkPen(color=COLOR_A, width=2.0),
            fillLevel=0.0,
            fillBrush=pg.mkBrush(color_fill)
        )
        self.curve_live.setClipToView(True)
        self.curve_live.setDownsampling(auto=True, method='peak')
        
        # --- CROSSHAIR PARA INSPECCIÓN ---
        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(color='#FFFFFF', width=1, style=QtCore.Qt.PenStyle.DashLine))
        self.hLine = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen(color='#FFFFFF', width=1, style=QtCore.Qt.PenStyle.DashLine))
        self.graph.addItem(self.vLine, ignoreBounds=True)
        self.graph.addItem(self.hLine, ignoreBounds=True)
        self.vLine.hide()
        self.hLine.hide()
        
        self.cursor_label = pg.TextItem(text="", color=COLOR_CURSOR, fill=pg.mkBrush(0, 0, 0, 180))
        self.graph.addItem(self.cursor_label, ignoreBounds=True)
        self.cursor_label.hide()
        
        self.proxy = pg.SignalProxy(self.graph.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

        self.graph_layout.addWidget(self.graph)
        self.main_layout.addWidget(graph_container)

        watermark = QtWidgets.QLabel("Youtube JlTexh8 Tester V4.6", graph_container)
        watermark.setStyleSheet("color: #444444; font-size: 11px; font-weight: bold; background: transparent;")
        watermark.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignBottom)
        self.graph_layout.addWidget(watermark, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

    def mouseMoved(self, evt):
        if self.is_paused:
            pos = evt[0]
            if self.graph.sceneBoundingRect().contains(pos):
                mousePoint = self.graph.getViewBox().mapSceneToView(pos)
                self.vLine.setPos(mousePoint.x())
                self.hLine.setPos(mousePoint.y())
                self.cursor_label.setPos(mousePoint.x(), mousePoint.y())
                self.cursor_label.setText(f" T: {mousePoint.x():.3f}s\n I: {mousePoint.y():.3f}A")
                self.vLine.show()
                self.hLine.show()
                self.cursor_label.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_labels_position()
        self.lbl_countdown.setGeometry(0, 0, self.width(), self.height())

    def update_labels_position(self):
        for lbl in self.dynamic_labels:
            new_x = (self.width() * lbl.relX) - (lbl.width() / 2) + lbl.offsetX
            new_y = lbl.fixedY + lbl.offsetY 
            lbl.move(int(new_x), int(new_y))
            lbl.raise_()
        self.lbl_countdown.raise_()

    def label_selected(self, label):
        for lbl in self.dynamic_labels:
            lbl.selected = False
            lbl.update_style()
        label.selected = True
        label.update_style()
        self.selected_label = label

    def _get_ordered_data(self):
        if self.tiempos[self.max_puntos - 1] > 0: 
            t_ord = np.concatenate((self.tiempos[self.ptr:], self.tiempos[:self.ptr]))
            v_ord = np.concatenate((self.voltajes[self.ptr:], self.voltajes[:self.ptr]))
            c_ord = np.concatenate((self.corrientes[self.ptr:], self.corrientes[:self.ptr]))
        else: 
            t_ord = self.tiempos[:self.ptr]
            v_ord = self.voltajes[:self.ptr]
            c_ord = self.corrientes[:self.ptr]
        return t_ord, v_ord, c_ord

    def force_redraw_ref(self):
        if len(self.ref_data[0]) > 0:
            t_data_full = self.ref_data[0]
            c_data_full = self.ref_data[1]
            
            # Anclaje dinámico dependiendo del modo (Scrolling o Estático)
            if getattr(self, 'ref_mode', 'live') == 'live':
                t_ord, _, _ = self._get_ordered_data()
                anchor = t_ord[-1] if len(t_ord) > 0 else 0
            else:
                anchor = t_data_full[-1]

            # Modo Reproductor (Replay)
            if getattr(self, 'replay_active', False):
                elapsed = (time.time() - self.replay_start_time) * 1.0 # Modificador de Velocidad
                idx = np.searchsorted(t_data_full, elapsed, side='right')
                t_plot = t_data_full[:idx]
                c_plot = c_data_full[:idx]
                if idx >= len(t_data_full):
                    self.replay_active = False # Finaliza reproducción
            else:
                t_plot = t_data_full
                c_plot = c_data_full

            # Pintar
            if len(t_plot) > 0:
                ref_t_relative = t_plot - anchor + self.ref_time_offset
                self.curve_ref.setData(ref_t_relative, c_plot)
            else:
                self.curve_ref.setData([], [])

    def keyPressEvent(self, event):
        step = 10 
        key_val = event.key()
        
        if key_val == QtCore.Qt.Key.Key_Left:
            self.graph_margin_h += step
            self.graph_layout.setContentsMargins(self.graph_margin_h, self.graph_margin_v, self.graph_margin_h, self.graph_margin_v)
        elif key_val == QtCore.Qt.Key.Key_Right:
            self.graph_margin_h = max(0, self.graph_margin_h - step)
            self.graph_layout.setContentsMargins(self.graph_margin_h, self.graph_margin_v, self.graph_margin_h, self.graph_margin_v)
        elif key_val == QtCore.Qt.Key.Key_Down:
            self.graph_margin_v += step
            self.graph_layout.setContentsMargins(self.graph_margin_h, self.graph_margin_v, self.graph_margin_h, self.graph_margin_v)
        elif key_val == QtCore.Qt.Key.Key_Up:
            self.graph_margin_v = max(0, self.graph_margin_v - step)
            self.graph_layout.setContentsMargins(self.graph_margin_h, self.graph_margin_v, self.graph_margin_h, self.graph_margin_v)
            
        elif key_val == QtCore.Qt.Key.Key_Z:
            self.ref_time_offset -= 0.05
            self.force_redraw_ref()
        elif key_val == QtCore.Qt.Key.Key_X:
            self.ref_time_offset += 0.05
            self.force_redraw_ref()
            
        elif self.selected_label:
            text = event.text()
            
            if key_val == QtCore.Qt.Key.Key_W: self.selected_label.offsetY -= step
            elif key_val == QtCore.Qt.Key.Key_S: self.selected_label.offsetY += step
            elif key_val == QtCore.Qt.Key.Key_A: self.selected_label.offsetX -= step
            elif key_val == QtCore.Qt.Key.Key_D: self.selected_label.offsetX += step
            elif key_val == QtCore.Qt.Key.Key_E:
                new_text, ok = QtWidgets.QInputDialog.getText(self, t('edit_title'), t('edit_prompt'), text=self.selected_label.text())
                if ok: 
                    self.selected_label.setText(new_text)
                    if self.selected_label == self.lbl_title: web_data["Title"] = new_text
            elif key_val == QtCore.Qt.Key.Key_C:
                color = QtWidgets.QColorDialog.getColor()
                if color.isValid(): 
                    self.selected_label.base_color = color.name()
                    if self.selected_label == self.lbl_a:
                        c_fill = QtGui.QColor(color.name())
                        c_fill.setAlpha(50)
                        self.curve_live.setPen(pg.mkPen(color=color.name(), width=2.0))
                        self.curve_live.setBrush(pg.mkBrush(c_fill))
                self.setFocus()
            elif text == '+' or key_val in [QtCore.Qt.Key.Key_Plus, QtCore.Qt.Key.Key_Equal]:
                self.selected_label.font_size += 2
            elif text == '-' or key_val in [QtCore.Qt.Key.Key_Minus, QtCore.Qt.Key.Key_Underscore]:
                self.selected_label.font_size = max(8, self.selected_label.font_size - 2)
            elif key_val == QtCore.Qt.Key.Key_Escape:
                self.selected_label.selected = False
                self.selected_label.update_style()
                self.selected_label = None

            if self.selected_label:
                self.selected_label.update_style()
            self.update_labels_position()

    def open_settings(self):
        was_paused = self.is_paused
        if not self.is_paused: self.toggle_pause()
        
        dialog = SettingsDialog(self.time_window, self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            new_time = dialog.get_values()
            if new_time != self.time_window:
                self.time_window = new_time
                web_data["TimeWindow"] = self.time_window 
                self.max_puntos = self.time_window * self.hz_margin
                
                self.ptr = 0
                self.tiempos = np.zeros(self.max_puntos)
                self.voltajes = np.zeros(self.max_puntos)
                self.corrientes = np.zeros(self.max_puntos)
                
                self.curve_live.setData([], [])
                self.graph.setXRange(-self.time_window, 0)
                
                self.start_time_hw = None
                self.pause_time_accum = 0
                
        if not was_paused: self.toggle_pause()

    def update_data(self):
        if self.is_paused:
            self.handle_recording()
            # Mantiene el redibujado de la firma constante si estamos en modo Replay
            if getattr(self, 'replay_active', False):
                self.force_redraw_ref()
            return

        self.graph.setXRange(-self.time_window, 0, padding=0)

        if self.stream.new_data_ready:
            self.stream.new_data_ready = False
            
            # --- VACIADO DE COLA FIFO EN BATCH ---
            items_procesar = []
            while self.stream.data_queue:
                items_procesar.append(self.stream.data_queue.popleft())
                
            if not items_procesar: return

            ultimo_t, v, a = items_procesar[-1]
            if self.start_time_hw is None:
                self.start_time_hw = items_procesar[0][0]

            w = v * a
            web_data["V"], web_data["A"], web_data["W"] = v, a, w
            if "V " in self.lbl_v.text(): self.lbl_v.setText(f"V {v:.3f}")
            if "A " in self.lbl_a.text(): self.lbl_a.setText(f"A {a:.3f}")
            if "W " in self.lbl_w.text(): self.lbl_w.setText(f"W {w:.3f}")
            self.update_labels_position()

            # --- LLENADO DE RING BUFFER ---
            for item in items_procesar:
                t_sec, iv, ia = item
                t_now = t_sec - self.start_time_hw - self.pause_time_accum
                
                self.tiempos[self.ptr] = t_now
                self.voltajes[self.ptr] = iv
                self.corrientes[self.ptr] = ia
                
                self.ptr += 1
                if self.ptr >= self.max_puntos:
                    self.ptr = 0

            # --- PLOTEO UNIFICADO ---
            t_ord, v_ord, c_ord = self._get_ordered_data()
            
            if len(t_ord) > 0:
                t_relative = t_ord - t_ord[-1]
                
                window_mask = t_relative >= -self.time_window
                t_plot = t_relative[window_mask]
                c_plot = c_ord[window_mask]

                self.curve_live.setData(t_plot, c_plot)
                
                # Renderizar referencia si está cargada
                if len(self.ref_data[0]) > 0:
                    self.force_redraw_ref()

                if len(c_plot) > 0:
                    max_a = np.max(c_plot)
                    target_lim = max(0.1, max_a * 1.1)
                    current_range = self.graph.getViewBox().viewRange()[1][1]
                    if target_lim > current_range or target_lim < current_range * 0.7:
                        self.graph.setYRange(-0.02, target_lim)

            if self.trigger_threshold is not None:
                if self.trigger_mode == 1: 
                    if a >= self.trigger_threshold:
                        self.toggle_pause()
                        self.trigger_threshold = None
                        self.btn_trig.setText("TRIG")
                        self.btn_trig.setStyleSheet(f"background-color: {COLOR_BTN}; color: #FFFFFF;")
                else:
                    if not self.post_trigger_active and a >= self.trigger_threshold:
                        self.post_trigger_active = True
                        self.post_trigger_target_time = time.time() + self.custom_post_trigger_time 
                        self.btn_trig.setText("WAIT")
                        self.btn_trig.setStyleSheet(f"background-color: #FFFF00; color: #000000; font-weight: bold;")
                    
                    elif self.post_trigger_active and time.time() >= self.post_trigger_target_time:
                        self.toggle_pause()
                        self.trigger_threshold = None
                        self.post_trigger_active = False
                        self.btn_trig.setText("TRIG")
                        self.btn_trig.setStyleSheet(f"background-color: {COLOR_BTN}; color: #FFFFFF;")

        self.handle_recording()

    def handle_recording(self):
        if self.is_recording:
            # En PyQt6 se usa el método grab() nativo del widget
            pixmap = self.grab()
            img = pixmap.toImage().convertToFormat(QtGui.QImage.Format.Format_RGB888)
            width, height = img.width(), img.height()
            
            # Conversión segura y rápida de memoria a numpy para OpenCV
            arr = np.frombuffer(img.bits(), dtype=np.uint8).reshape((height, width, 3)).copy()
            
            w_even, h_even = width - (width % 2), height - (height % 2)
            arr = arr[:h_even, :w_even, :]
            
            if self.video_writer is None:
                temp_path = os.path.join(os.path.expanduser("~"), f"Video_USB_{time.strftime('%Y%m%d_%H%M%S')}.mp4")
                self.video_writer = cv2.VideoWriter(temp_path, cv2.VideoWriter_fourcc(*'mp4v'), 30.0, (w_even, h_even))
            self.video_writer.write(cv2.cvtColor(arr, cv2.COLOR_RGB2BGR))

    def start_countdown(self, mode):
        self.countdown_mode = mode
        self.countdown_step = 3
        self.lbl_countdown.setText(str(self.countdown_step))
        self.lbl_countdown.setStyleSheet("color: #FFEA00; font-family: Consolas; font-size: 150px; font-weight: bold; background: rgba(0,0,0,180);")
        self.lbl_countdown.show()
        self.lbl_countdown.raise_()
        self.is_paused = True 
        self.countdown_timer.start(1000)

    def process_countdown(self):
        self.countdown_step -= 1
        if self.countdown_step > 0:
            self.lbl_countdown.setText(str(self.countdown_step))
        elif self.countdown_step == 0:
            self.lbl_countdown.setText("¡GO!")
            self.lbl_countdown.setStyleSheet("color: #00FF9C; font-family: Consolas; font-size: 180px; font-weight: bold; background: rgba(0,0,0,180);")
            
            self.ptr = 0
            self.tiempos.fill(0)
            self.voltajes.fill(0)
            self.corrientes.fill(0)
            self.curve_live.setData([], [])
            
            self.start_time_hw = None
            self.pause_time_accum = 0

            if self.countdown_mode == 'load_ref':
                self.ref_data = self.temp_ref_data
                self.ref_time_offset = 0.0 
                self.lbl_ref_name.setText(f"REF: {self.temp_ref_name}")
                self.lbl_ref_name.show()
                self.btn_lref.setStyleSheet(f"background-color: {COLOR_BTN}; color: #FF3333; font-weight: bold;")
            elif self.countdown_mode == 'save_boot':
                self.pending_save_active = True
            
            self.is_paused = False
            self.btn_pause.setText("||")
            self.btn_pause.setStyleSheet(f"background-color: {COLOR_BTN}; color: #00E5FF; font-weight: bold;")
            self.graph.setMouseEnabled(x=False, y=False)
            
        elif self.countdown_step < 0:
            self.countdown_timer.stop()
            self.lbl_countdown.hide()

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        
        if self.is_paused and getattr(self, 'pending_save_active', False):
            path, _ = QtWidgets.QFileDialog.getSaveFileName(self, t('save_title'), f"Firma_{time.strftime('%Y%m%d_%H%M%S')}.csv", "CSV (*.csv)")
            if path:
                self.execute_save_ref(path, self.pending_save_name)
            self.pending_save_active = False

        if self.post_trigger_active:
            self.trigger_threshold = None
            self.post_trigger_active = False
            self.btn_trig.setText("TRIG")
            self.btn_trig.setStyleSheet(f"background-color: {COLOR_BTN}; color: #FFFFFF; font-weight: bold;")

        if self.is_paused:
            self.pause_start = time.time()
            self.btn_pause.setText("▶")
            self.btn_pause.setStyleSheet(f"background-color: {COLOR_BTN}; color: #00FF00; font-weight: bold;")
            self.graph.setMouseEnabled(x=True, y=True)
        else:
            self.vLine.hide()
            self.hLine.hide()
            self.cursor_label.hide()
            self.pause_time_accum += (time.time() - self.pause_start)
            
            # FIX CRÍTICO: Previene que la gráfica se ponga una sobre otra al reanudar
            self.stream.flush_buffers() 
            
            self.graph.setXRange(-self.time_window, 0)
            self.btn_pause.setText("||")
            self.btn_pause.setStyleSheet(f"background-color: {COLOR_BTN}; color: #00E5FF; font-weight: bold;")
            self.graph.setMouseEnabled(x=False, y=False)

    def move_left(self):
        if self.is_paused:
            x_min, x_max = self.graph.getViewBox().viewRange()[0]
            self.graph.setXRange(x_min - 2.0, x_max - 2.0, padding=0)

    def move_right(self):
        if self.is_paused:
            x_min, x_max = self.graph.getViewBox().viewRange()[0]
            self.graph.setXRange(x_min + 2.0, x_max + 2.0, padding=0)

    def take_snap(self):
        was_paused = self.is_paused
        if not self.is_paused: self.toggle_pause()
        self.vLine.hide()
        self.hLine.hide()
        self.cursor_label.hide()
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, t('btn_snap'), f"FOTO_{time.strftime('%Y%m%d_%H%M%S')}.png", "PNG (*.png)")
        if path:
            pixmap = self.grab()
            pixmap.save(path)
        if not was_paused: self.toggle_pause()

    def set_trigger(self):
        dialog = TriggerDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            amp_val, post_time, mode = dialog.get_values()
            self.trigger_threshold = amp_val
            self.custom_post_trigger_time = post_time
            self.trigger_mode = mode
            self.post_trigger_active = False 
            self.btn_trig.setText("TRIG")
            self.btn_trig.setStyleSheet(f"background-color: {COLOR_BTN}; color: #00FF00; font-weight: bold;")
        else:
            self.trigger_threshold = None
            self.post_trigger_active = False
            self.btn_trig.setText("TRIG")
            self.btn_trig.setStyleSheet(f"background-color: {COLOR_BTN}; color: #FFFFFF; font-weight: bold;")

    def toggle_record(self):
        if not self.is_recording:
            self.is_recording = True
            self.btn_rec.setText("■")
            self.btn_rec.setStyleSheet(f"background-color: #CC0000; color: #FFFFFF; font-weight: bold;")
        else:
            self.is_recording = False
            self.btn_rec.setText("●")
            self.btn_rec.setStyleSheet(f"background-color: {COLOR_BTN}; color: #FF0000; font-weight: bold;")
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
                QtWidgets.QMessageBox.information(self, "OK", t('msg_vid_ok'))

    def save_ref(self):
        was_paused = self.is_paused
        if not self.is_paused: self.toggle_pause()
        
        dialog = SaveModeDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            if dialog.mode == 'PREP':
                ref_name, ok_text = QtWidgets.QInputDialog.getText(self, t('ref_title'), t('ref_prompt'))
                if ok_text and ref_name.strip():
                    self.pending_save_name = ref_name.strip()
                    self.start_countdown('save_boot')
                else:
                    if not was_paused: self.toggle_pause()
            
            elif dialog.mode == 'SAVE':
                ref_name, ok_text = QtWidgets.QInputDialog.getText(self, t('ref_title'), t('ref_prompt'))
                if ok_text and ref_name.strip():
                    path, _ = QtWidgets.QFileDialog.getSaveFileName(self, t('save_title'), f"Firma_{time.strftime('%Y%m%d_%H%M%S')}.csv", "CSV (*.csv)")
                    if path:
                        self.execute_save_ref(path, ref_name.strip())
                if not was_paused: self.toggle_pause()
        else:
            if not was_paused: self.toggle_pause()

    def execute_save_ref(self, path, ref_name):
        t_ord, v_ord, c_ord = self._get_ordered_data()
        if len(t_ord) > 0:
            t_rel = t_ord - t_ord[-1]
            window_mask = t_rel >= -self.time_window
            save_t = t_rel[window_mask]
            save_c = c_ord[window_mask]
            
            if len(save_c) > 0:
                t_offset = save_t[0]
                t_rel_save = save_t - t_offset 
            else:
                t_offset = 0.0
                t_rel_save = np.array([0.0])
        else:
            t_offset = 0.0
            t_rel_save = np.array([0.0])
            save_c = np.array([0.0])
            
        custom_header = f"REF_TITLE:{ref_name}\nTiempoRelativo(s),Corriente(A)"
        np.savetxt(path, np.column_stack((t_rel_save, save_c)), delimiter=",", header=custom_header, comments="# ", fmt="%.4f")
        QtWidgets.QMessageBox.information(self, "OK", t('msg_save_ok'))

    def load_ref(self, *args, filepath=None):
        was_paused = self.is_paused
        if not self.is_paused: self.toggle_pause()

        try:
            if len(self.ref_data[0]) > 0 and filepath is None:
                self.ref_data = (np.array([]), np.array([]))
                self.curve_ref.setData([], [])
                self.lbl_ref_name.hide()
                self.btn_lref.setStyleSheet(f"background-color: {COLOR_BTN}; color: #00FF9C; font-weight: bold;")
                self.ref_time_offset = 0.0 
                
                if getattr(self, 'replay_active', False): self.replay_active = False
                if not was_paused: self.toggle_pause()
                return
                
            if filepath is None:
                dialog = LoadModeDialog(self)
                if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                    filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, t('load_title'), "", "CSV (*.csv)", options=QtWidgets.QFileDialog.Option.DontUseNativeDialog)
                    if not filepath:
                        if not was_paused: self.toggle_pause()
                        return
                else:
                    if not was_paused: self.toggle_pause()
                    return

            ref_title_extracted = "Firma Cargada"
            with open(filepath, 'r', encoding='utf-8') as f:
                primera_linea = f.readline()
                if "REF_TITLE:" in primera_linea:
                    ref_title_extracted = primera_linea.split("REF_TITLE:")[1].strip()

            data = np.loadtxt(filepath, delimiter=",", comments="#")
            if data.shape[1] >= 2:
                t_data = data[:, 0]
                c_data = data[:, 1]
                if t_data[-1] <= 0.0: t_data = t_data - t_data[0] 
                
                self.temp_ref_data = (t_data, c_data)
                self.temp_ref_name = ref_title_extracted
                
                # --- NUEVO: MENÚ DE MODO REPRODUCTOR ---
                msg_box = QtWidgets.QMessageBox(self)
                msg_box.setWindowTitle(t('load_opt_title'))
                msg_box.setText(t('load_opt_msg'))
                
                btn_live = msg_box.addButton(t('load_opt_live'), QtWidgets.QMessageBox.ButtonRole.ActionRole)
                btn_replay = msg_box.addButton(t('load_opt_replay'), QtWidgets.QMessageBox.ButtonRole.ActionRole)
                btn_static = msg_box.addButton(t('load_opt_static'), QtWidgets.QMessageBox.ButtonRole.ActionRole)
                msg_box.addButton(t('btn_cancel'), QtWidgets.QMessageBox.ButtonRole.RejectRole)
                
                msg_box.exec()
                
                if msg_box.clickedButton() == btn_live:
                    self.ref_mode = 'live'
                    self.start_countdown('load_ref')
                elif msg_box.clickedButton() in [btn_replay, btn_static]:
                    self.ref_mode = 'static'
                    self.ref_data = self.temp_ref_data
                    self.ref_time_offset = 0.0 
                    self.lbl_ref_name.setText(f"REF: {self.temp_ref_name}")
                    self.lbl_ref_name.show()
                    self.btn_lref.setStyleSheet(f"background-color: {COLOR_BTN}; color: #FF3333; font-weight: bold;")
                    
                    if msg_box.clickedButton() == btn_replay:
                        self.replay_active = True
                        self.replay_start_time = time.time()
                        if not self.is_paused: self.toggle_pause() # Fuerza pausa para ver el Replay
                    else:
                        self.replay_active = False
                        if not was_paused: self.toggle_pause()
                        
                    self.force_redraw_ref()
                else:
                    if not was_paused: self.toggle_pause()

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"{t('msg_load_err')}\n{e}")
            if not was_paused: self.toggle_pause()

    def load_from_github(self):
        was_paused = self.is_paused
        if not self.is_paused: self.toggle_pause()
        
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(t('cloud_title'))
        msg_box.setText(f"<b>{t('cloud_msg_title')}</b><br><br>{t('cloud_msg_body')}")
        
        btn_discord = msg_box.addButton(t('btn_discord'), QtWidgets.QMessageBox.ButtonRole.ActionRole)
        btn_cloud = msg_box.addButton(t('btn_cloud_load'), QtWidgets.QMessageBox.ButtonRole.ActionRole)
        msg_box.addButton(t('btn_cancel'), QtWidgets.QMessageBox.ButtonRole.RejectRole)
        
        msg_box.exec()
        
        if msg_box.clickedButton() == btn_discord:
            webbrowser.open(URL_DISCORD)
            if not was_paused: self.toggle_pause()
        elif msg_box.clickedButton() == btn_cloud:
            self.execute_cloud_fetch()
            if not was_paused: self.toggle_pause()
        else:
            if not was_paused: self.toggle_pause()

    def execute_cloud_fetch(self):
        req = urllib.request.Request(URL_GITHUB_API, headers={'User-Agent': 'JlTexh-Monitor'})
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                tree = data.get('tree', [])
                
                csv_files = [f for f in tree if f['path'].endswith('.csv')]
                
                if not csv_files:
                    QtWidgets.QMessageBox.information(self, t('cloud_title'), t('msg_cloud_empty'))
                    return
                    
                nombres = [f['path'] for f in csv_files]
                
                item, ok = QtWidgets.QInputDialog.getItem(self, t('cloud_title'), t('cloud_prompt'), nombres, 0, False)
                if ok and item:
                    item_encoded = urllib.parse.quote(item)
                    raw_url = f"https://raw.githubusercontent.com/JlTexh8/UNIVERSAL-PSU-Reference-Measurements/main/{item_encoded}"
                    
                    temp_path = os.path.join(os.path.expanduser("~"), "temp_cloud_ref.csv")
                    urllib.request.urlretrieve(raw_url, temp_path)
                    
                    self.load_ref(filepath=temp_path)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"{t('msg_cloud_err')}\n\n{e}")

    def export_csv(self):
        was_paused = self.is_paused
        if not self.is_paused: self.toggle_pause()
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export Log", f"Log_{time.strftime('%Y%m%d_%H%M%S')}.csv", "CSV (*.csv)")
        if path:
            t_ord, v_ord, c_ord = self._get_ordered_data()
            if len(t_ord) > 0:
                t_rel = t_ord - t_ord[-1]
                window_mask = t_rel >= -self.time_window
                
                t_exp = t_rel[window_mask]
                v_exp = v_ord[window_mask]
                c_exp = c_ord[window_mask]
                p_exp = v_exp * c_exp
                
                np.savetxt(path, np.column_stack((t_exp, v_exp, c_exp, p_exp)), delimiter=",", header="Tiempo(s),Voltaje(V),Corriente(A),Potencia(W)", comments="", fmt="%.4f")
                QtWidgets.QMessageBox.information(self, "OK", t('msg_exp_ok'))
        if not was_paused: self.toggle_pause()

    def auto_diagnostico(self):
        was_paused = self.is_paused
        if not self.is_paused: self.toggle_pause()
        
        if len(self.ref_data[0]) == 0:
            QtWidgets.QMessageBox.warning(self, "Error", t('msg_diag_err'))
            return
            
        x_ref, y_ref = self.ref_data
        
        t_ord, _, c_ord = self._get_ordered_data()
        if len(t_ord) == 0: return
        
        t_rel = t_ord - t_ord[-1]
        window_mask = t_rel >= -self.time_window
        y_curr = c_ord[window_mask]
        
        if len(y_curr) == 0: return

        max_amp = max(np.max(y_ref), 0.5)
        
        compare_len = min(len(y_ref), len(y_curr))
        error_medio = np.mean(np.abs(y_ref[-compare_len:] - y_curr[-compare_len:])) if len(y_curr) >= compare_len else 0.5
        porcentaje = min(100.0, max(0.0, 100.0 - ((error_medio / max_amp) * 100.0 * 2.5)))

        if porcentaje >= 90: diag_txt = t('diag_ok')
        elif porcentaje >= 75: diag_txt = t('diag_warn')
        elif porcentaje >= 40: diag_txt = t('diag_anom')
        else: diag_txt = t('diag_crit')

        QtWidgets.QMessageBox.information(self, f"Match: {porcentaje:.1f}%", f"Match: {porcentaje:.1f}%\n\n{diag_txt}")
        if not was_paused: self.toggle_pause()

    def closeEvent(self, event):
        self.stream.running = False
        if self.video_writer: self.video_writer.release()
        event.accept()

# ==========================================
# PUNTO DE ENTRADA Y SELECCIÓN DE PUERTO
# ==========================================
def configurar_puerto():
    puertos = list(serial.tools.list_ports.comports())
    if not puertos: return None
    print(f"\n{t('port_avail')}")
    for i, puerto in enumerate(puertos): 
        print(f" [{i}] {puerto.device} - {puerto.description}")
    sel = input(f"\n{t('port_sel')}").strip()
    try: 
        return puertos[int(sel)].device if sel.isdigit() else sel.upper()
    except Exception: 
        return None

def main():
    global user_lang
    print("\n" + "="*40 + "\n 🌍 LANGUAGE / IDIOMA\n" + "="*40)
    user_lang = 'EN' if input(" 1. Español\n 2. English\n👉 Select (1/2): ").strip() == '2' else 'ES'

    print("\n" + "="*50 + f"\n  {t('menu_title')}\n" + "="*50)
    
    port_target = configurar_puerto()
    if not port_target:
        print(f"\n❌ Error: No se ha detectado ningún dispositivo COM o la selección fue inválida.")
        input("\n👉 Presiona ENTER para salir...")
        sys.exit()

    mostrar_atajos()
    
    threading.Thread(target=start_web_server_thread, args=(8080,), daemon=True).start()
    
    app = QtWidgets.QApplication(sys.argv)
    try:
        stream = SerialStream(port_target, baudrate=115200)
        window = JlTexhMonitor(stream)
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"\n❌ [ERROR CRÍTICO] {e}")
        input("\n👉 Presiona ENTER para salir y cierra esta ventana...")

if __name__ == "__main__":
    main()