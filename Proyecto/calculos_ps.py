from calculos_vec import *



# Ejemplo vectorial directo:
z = 2250  # msnm
tbs_ej = [13.76]   # °C
hr_ej = [100]          # % (puede ser 0-100 o 0-1)

# calcular la hr con tbs  y h
# Calcular resultados
resultados = calcular_vectorial(z, tbs_ej, hr_ej)

# Encabezados de la tabla
print("\n" + "="*170)
print(f"{'Muestra':^8} | {'Tbs (°C)':^8} | {'HR (%)':^8} | {'Patm (kPa)':^10} | {'Pv (kPa)':^10} | {'Pvs (kPa)':^10} | {'DPVa (Pa)':^10} | {'W (kg/kg)':^10} | {'Ws (kg/kg)':^10} | {'μ':^8} | {'veh (m³/kg)':^12} | {'h (kJ/kg)':^10} | {'Tpr (°C)':^9} | {'Tbh (°C)':^9}")
print("-"*160)

# Filas de la tabla
for i, r in enumerate(resultados):
    print(f"{i+1:^8} | "
          f"{r['Tbs_C']:^8.2f} | "
          f"{r['HR_frac']*100:^8.2f} | "
          f"{r['patm_kPa']:^10.4f} | "
          f"{r['pv_Pa']/1000:^10.4f} | "
          f"{r['pvs_Pa']/1000:^10.4f} | "
          f"{r['dpva_Pa']:^10.4f} | "
          f"{r['W_kgkg']:^10.6f} | "
          f"{r['Ws_kgkg']:^10.6f} | "
          f"{r['mu']:^8.6f} | "
          f"{r['veh_m3kg']:^12.6f} | "
          f"{r['h_kJkg']:^10.3f} | "
          f"{r['Tpr_C']:^9.3f} | "
          f"{r['Tbh_C']:^9.3f}"
          )

print("="*170)
