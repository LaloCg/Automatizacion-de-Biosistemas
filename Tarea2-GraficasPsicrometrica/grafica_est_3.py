# -*- coding: utf-8 -*-
# Eduardo Cano García - Carta psicrométrica extendida
# Usa la clase CalculadoraPsicrometrica ya definida

import math
import matplotlib.pyplot as plt
import numpy as np
from calculos_vec import *

# ========= CONFIGURACIÓN DE LA CARTA =========
Z = 2451  # Altitud (msnm)
Tbs_vals = [t for t in range(-10, 41, 5)]   # -10 a 60°C
phi_vals = [i / 100 for i in range(10, 101, 10)]  # 10% a 100%


# ========= FUNCIÓN PARA CALCULAR LA CARTA =========
def generar_carta_psicrometrica(z, Tbs_vals, phi_vals):
    datos = {
        "W": [],
        "H": [],
        "Veh": [],
        "Tbh": []
    }
    for hr in phi_vals:
        Ws, Hs, Vhs, Tbh = [], [], [], []
        for T in Tbs_vals:
            calc = CalculadoraPsicrometrica(z, T, hr)
            resultados = calc.calcular_todo()
            Ws.append(resultados["W_kgkg"])
            Hs.append(resultados["h_kJkg"])
            Vhs.append(resultados["veh_m3kg"])
            Tbh.append(resultados["Tbh_C"])
        datos["W"].append(Ws)
        datos["H"].append(Hs)
        datos["Veh"].append(Vhs)
        datos["Tbh"].append(Tbh)
    return datos

# ========= CALCULAR DATOS =========
carta = generar_carta_psicrometrica(Z, Tbs_vals, phi_vals)

# ================= LEER DATOS DESDE EXCEL =================
# Archivo Excel con columnas "Tbs" y "HR"
archivo_excel = "estacion_3.csv"
tbs_medidos, hr_medidos = leer_csv_o_txt(archivo_excel)  # tu función detecta Excel si es xlsx

# Calcular W de cada punto usando la clase
W_medidos = []
for Tbs, HR in zip(tbs_medidos, hr_medidos):
    calc = CalculadoraPsicrometrica(Z, Tbs, HR)
    res = calc.calcular_todo()
    W_medidos.append(res['W_kgkg'])


# ========= GRAFICAR =========
plt.figure(figsize=(12, 8))
plt.title("Carta Psicrométrica - Aire Húmedo", fontsize=14)
plt.xlabel("Temperatura de Bulbo Seco (°C)")
plt.ylabel("Razón de Humedad W (kg vapor/kg aire seco)")

# ----------  LÍNEAS DE HUMEDAD RELATIVA ----------
for i, hr in enumerate(phi_vals):
    etiqueta = f"{int(hr * 100)} % HR"
    plt.plot(Tbs_vals, carta["W"][i], color='blue', alpha=0.4)
    plt.text(Tbs_vals[-1] + 0.5, carta["W"][i][-1], etiqueta, fontsize=8, color='blue')

# ----------  LÍNEAS DE ENTALPÍA (h) ----------
H = np.array(carta["H"])
W = np.array(carta["W"])
T, PHI = np.meshgrid(Tbs_vals, phi_vals)
niveles_h = np.arange(np.nanmin(H), np.nanmax(H), 50)
cs_h = plt.contour(T, W, H, niveles_h, colors='black', linestyles='--', alpha=0.5)
plt.clabel(cs_h, fmt='%d', fontsize=7)
plt.text(55, np.nanmax(W)*0.85, "h [kJ/kg]", color='black', fontsize=9)

# ----------  LÍNEAS DE BULBO HÚMEDO (Tbh) ----------
Tbh = np.array(carta["Tbh"])
niveles_tbh = np.arange(np.nanmin(Tbh), np.nanmax(Tbh), 5)
cs_tbh = plt.contour(T, W, Tbh, niveles_tbh, colors='green', linestyles=':', alpha=0.6)
plt.clabel(cs_tbh, fmt='%d', fontsize=7)
plt.text(55, np.nanmax(W)*0.75, "Tbh [°C]", color='green', fontsize=9)

# ----------  LÍNEAS DE VOLUMEN ESPECÍFICO (Veh) ----------
Veh = np.array(carta["Veh"])
niveles_v = np.linspace(np.nanmin(Veh), np.nanmax(Veh), 6)
cs_v = plt.contour(T, W, Veh, niveles_v, colors='purple', linestyles='-.', alpha=0.5)
plt.clabel(cs_v, fmt='%.3f', fontsize=7)
plt.text(55, np.nanmax(W)*0.65, "v [m³/kg]", color='purple', fontsize=9)

# Puntos de medición desde archivo
plt.scatter(tbs_medidos, W_medidos, color='red', s=60, edgecolors='black', zorder=5)

# ---------- ESTILO GENERAL ----------
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.tight_layout()
plt.show()
