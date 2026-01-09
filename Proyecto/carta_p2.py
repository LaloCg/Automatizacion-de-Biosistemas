# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D  # Necesario para la leyenda personalizada
import numpy as np
import csv
import os
from calculos import CalculadoraPsicrometrica  # Asegúrate de importar la clase correcta

# ========= CONFIGURACIÓN DE LA CARTA =========
Z = 2250  # (msnm)
Tbs_vals = [t for t in range(0, 45, 5)]  # Rango eje X
phi_vals = [i / 100 for i in range(10, 101, 10)]  # Curvas de HR


# ========= FUNCIÓN GENERADORA DE LA CARTA (FONDO) =========
def generar_carta_psicrometrica(z, Tbs_vals, phi_vals):
    datos = {"W": [], "H": [], "Veh": [], "Tbh": []}
    for hr in phi_vals:
        Ws, Hs, Vhs, Tbh_lineas = [], [], [], []
        for T in Tbs_vals:
            calc = CalculadoraPsicrometrica(z, T, hr)
            res = calc.calcular_todo()
            Ws.append(res["W_kgkg"])
            Hs.append(res["h_kJkg"])
            Vhs.append(res["veh_m3kg"])
            Tbh_lineas.append(res["Tbh_C"])
        datos["W"].append(Ws)
        datos["H"].append(Hs)
        datos["Veh"].append(Vhs)
        datos["Tbh"].append(Tbh_lineas)
    return datos


# ========= FUNCIÓN DE LECTURA (Tbs y Tbh) =========
def leer_tbs_tbh(filepath):
    tbs_list = []
    tbh_list = []
    nombres_tbs = ['tbs', 't_seca', 't_bulbo_seco', 'temp', 't']
    nombres_tbh = ['tbh', 't_humeda', 't_bulbo_humedo', 'wet', 'tw']

    if not os.path.exists(filepath):
        print(f"Error: El archivo {filepath} no existe.")
        return [], []

    with open(filepath, 'r', newline='', encoding='utf-8') as f:
        sample = f.read(1024)
        delim = ';' if ';' in sample and ',' not in sample else ','
        f.seek(0)
        reader = csv.reader(f, delimiter=delim)
        rows = list(reader)
        if not rows: return [], []

        header = [h.strip().lower() for h in rows[0]]
        idx_tbs = -1
        idx_tbh = -1

        for i, col in enumerate(header):
            if col in nombres_tbs: idx_tbs = i
            if col in nombres_tbh: idx_tbh = i

        if idx_tbs == -1: idx_tbs = 0
        if idx_tbh == -1: idx_tbh = 1

        for row in rows[1:]:
            try:
                if len(row) > max(idx_tbs, idx_tbh):
                    val_tbs = float(row[idx_tbs])
                    val_tbh = float(row[idx_tbh])
                    tbs_list.append(val_tbs)
                    tbh_list.append(val_tbh)
            except ValueError:
                continue
    return tbs_list, tbh_list


# ========= PROCESAMIENTO PRINCIPAL =========
print("Generando carta psicrométrica...")
carta = generar_carta_psicrometrica(Z, Tbs_vals, phi_vals)

archivo_datos = "datos_temperatura_p2.csv"
tbs_exp, tbh_exp = leer_tbs_tbh(archivo_datos)

w_calc = []
hr_calc = []

print(f"Procesando {len(tbs_exp)} puntos experimentales...")
for t_seca, t_hum in zip(tbs_exp, tbh_exp):
    calc = CalculadoraPsicrometrica(Z, t_seca, 0)
    hr_reales = calc.calcular_hr_psicrometrica(t_hum)
    w = calc.calcular_razon_humedad()
    w_calc.append(w)
    hr_calc.append(hr_reales)

# ========= GRAFICAR =========
plt.figure(figsize=(14, 10))
plt.title(f"Carta Psicrométrica (Z={Z}m)", fontsize=16, fontweight='bold')
plt.xlabel("Temperatura de Bulbo Seco (°C)", fontsize=12)
plt.ylabel("Razón de Humedad W (kg vapor/kg aire seco)", fontsize=12)

# --- 1. Dibujar líneas de HR (Fondo) ---
for i, hr in enumerate(phi_vals):
    color_linea = 'blue' if hr < 1.0 else 'red'
    grosor = 1.5 if hr == 1.0 else 0.6
    alpha_val = 0.3 if hr < 1.0 else 0.5
    plt.plot(Tbs_vals, carta["W"][i], color=color_linea, alpha=alpha_val, linewidth=grosor)

    if len(carta["W"][i]) > 0:
        plt.text(Tbs_vals[-1], carta["W"][i][-1], f"{int(hr * 100)}%",
                 fontsize=7, color=color_linea, alpha=0.7, verticalalignment='center')

# Preparación para contornos
H = np.array(carta["H"])
W = np.array(carta["W"])
T, PHI = np.meshgrid(Tbs_vals, phi_vals)

# --- 2. LÍNEAS DE ENTALPÍA (h) ---
niveles_h = np.arange(np.nanmin(H), np.nanmax(H), 20)
cs_h = plt.contour(T, W, H, niveles_h, colors='black', linestyles='--', alpha=0.3, linewidths=0.8)
plt.clabel(cs_h, inline=True, fmt='%d', fontsize=7, colors='black', manual=False)

# --- 3. LÍNEAS DE BULBO HÚMEDO (Tbh) ---
Tbh = np.array(carta["Tbh"])
niveles_tbh = np.arange(0, 35, 5)
cs_tbh = plt.contour(T, W, Tbh, niveles_tbh, colors='green', linestyles=':', alpha=0.5, linewidths=1)

# CORRECCIÓN AQUÍ: Eliminamos "fontweight='bold'" que causaba el error
plt.clabel(cs_tbh, inline=True, fmt='%d', fontsize=8, colors='green')

# --- 4. LÍNEAS DE VOLUMEN ESPECÍFICO (Veh) ---
Veh = np.array(carta["Veh"])
niveles_v = np.linspace(np.nanmin(Veh), np.nanmax(Veh), 6)
cs_v = plt.contour(T, W, Veh, niveles_v, colors='purple', linestyles='-.', alpha=0.4, linewidths=0.8)
plt.clabel(cs_v, inline=True, fmt='%.2f', fontsize=7, colors='purple')

# --- 5. LEYENDA PERSONALIZADA ---
from matplotlib.lines import Line2D

leyenda_elementos = [
    Line2D([0], [0], color='black', linestyle='--', linewidth=1, alpha=0.6, label='Entalpía (h) [kJ/kg]'),
    Line2D([0], [0], color='green', linestyle=':', linewidth=1.5, alpha=0.8, label='T. Bulbo Húmedo (Tbh) [°C]'),
    Line2D([0], [0], color='purple', linestyle='-.', linewidth=1, alpha=0.6, label='Volumen Esp. (v) [m³/kg]'),
    Line2D([0], [0], color='blue', lw=1, alpha=0.3, label='Humedad Relativa (HR)'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='yellow', markeredgecolor='black', markersize=10,
           label='Datos Medidos')
]

plt.legend(handles=leyenda_elementos, loc='upper left', fontsize=9, framealpha=0.9, edgecolor='gray')

# --- 6. Graficar tus puntos experimentales ---
if len(tbs_exp) > 0:
    sc = plt.scatter(tbs_exp, w_calc, c=hr_calc, cmap='viridis',
                     s=60, edgecolors='black', linewidths=0.8, zorder=10)

    cbar = plt.colorbar(sc, pad=0.02)
    cbar.set_label("Humedad Relativa Calculada (%)", rotation=270, labelpad=15)
else:
    print("Advertencia: No se encontraron datos para graficar.")

plt.grid(True, linestyle='--', alpha=0.4)
plt.tight_layout()
plt.show()