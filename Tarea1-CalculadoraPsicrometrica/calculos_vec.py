# Eduardo Cano García
# 7° 6
import math
import csv
import os
import numpy as np
import matplotlib.pyplot as plt

class CalculadoraPsicrometrica:
    """
    Clase para realizar cálculos psicrométricos del aire húmedo (por muestra).
    RA en J/kg*K.
    Nota: el código original se ha preservado; las funciones devuelven valores escalares.
    """

    RA = 287.055  # J/kg*K, Constante del Gas para el Aire Seco

    def __init__(self, z, tbs, hr):
        """
        Args:
            z (float): Altitud sobre el nivel del mar (m)
            tbs (float): Temperatura de bulbo seco (°C)
            hr (float): Humedad relativa (0-1) o (0-100)
        """
        self.z = float(z)
        self.tbs = float(tbs)
        # Normalizar hr: si viene mayor a 1 se asume porcentaje 0-100
        self.hr = float(hr) / 100.0 if float(hr) > 1.0 else float(hr)
        self.patm = None
        self.tbsk = None
        self.pv = None
        self.pvs = None
        self.dpva = None
        self.w = None
        self.ws = None
        self.mu = None
        self.veh = None
        self.h = None
        self.tpr = None
        self.tbh = None  # Temperatura de bulbo húmedo

    def calcular_presion_atmosferica(self):
        """Calcula la presión atmosférica en kPa en función de la altitud (msnm)."""
        self.patm = 101.325 * (1 - (2.25577 * 10 ** -5) * self.z) ** 5.2529
        return self.patm

    def convertir_temperatura_kelvin(self):
        """Convierte la temperatura de Celsius a Kelvin."""
        self.tbsk = 273.15 + self.tbs
        return self.tbsk

    def calcular_presion_vapor_saturado(self, temperatura=None):
        """
        Calcula la presión de vapor saturado.
        Devuelve pvs en Pa (como en tu versión original).
        """
        if temperatura is None:
            temperatura = self.tbs
            temp_k = self.tbsk if self.tbsk is not None else 273.15 + self.tbs
        else:
            temp_k = 273.15 + temperatura

        if -100 < temperatura < 0:
            pvs = math.exp(
                (-(5.6745359 * 10 ** 3) / temp_k) + 6.3925247 -
                ((9.6778430 * 10 ** -3) * temp_k) +
                ((6.2215701 * 10 ** -7) * (temp_k) ** 2) +
                ((2.0747825 * 10 ** -9) * (temp_k) ** 3) -
                ((9.484024 * 10 ** -13) * (temp_k) ** 4) +
                (4.1635019 * math.log(temp_k))
            )
        elif 0 <= temperatura < 200:
            pvs = math.exp(
                (-(5.8002206 * 10 ** 3) / temp_k) + 1.3914993 -
                ((48.640239 * 10 ** -3) * temp_k) +
                ((41.764768 * 10 ** -6) * (temp_k) ** 2) -
                ((14.452093 * 10 ** -9) * (temp_k) ** 3) +
                (6.5459673 * math.log(temp_k))
            )
        else:
            raise ValueError(f"Temperatura {temperatura}°C fuera del rango válido (-100 a 200°C)")

        # Guardar en self.pvs solo si se calculó para la temperatura principal
        if temperatura == self.tbs:
            self.pvs = pvs

        return pvs

    def calcular_presion_vapor(self):
        """Calcula la presión de vapor Pv en Pa usando hr * pvs."""
        if self.pvs is None:
            self.calcular_presion_vapor_saturado()
        self.pv = self.hr * self.pvs
        return self.pv

    def calcular_deficit_presion_vapor(self):
        """Calcula el déficit de presión de vapor (Pvs - Pv) en Pa."""
        if self.pvs is None:
            self.calcular_presion_vapor_saturado()
        if self.pv is None:
            self.calcular_presion_vapor()
        self.dpva = self.pvs - self.pv
        return self.dpva

    def calcular_razon_humedad(self, presion_vapor=None, presion_atmosferica=None):
        """
        Calcula la razón de humedad W (kg_vapor/kg_aire_seco).
        presion_vapor en Pa (si no se pasa, usa self.pv).
        presion_atmosferica en kPa (si no se pasa, usa self.patm).
        """
        if presion_vapor is None:
            if self.pv is None:
                self.calcular_presion_vapor()
            presion_vapor = self.pv
        if presion_atmosferica is None:
            if self.patm is None:
                self.calcular_presion_atmosferica()
            presion_atmosferica = self.patm

        pv_kpa = presion_vapor / 1000
        return 0.621945 * (pv_kpa / (presion_atmosferica - pv_kpa))

    def calcular_grado_saturacion(self):
        """Calcula mu = W/Ws."""
        if self.w is None:
            self.w = self.calcular_razon_humedad(self.pv, self.patm)
        if self.ws is None:
            if self.pvs is None:
                self.calcular_presion_vapor_saturado()
            self.ws = self.calcular_razon_humedad(self.pvs, self.patm)
        self.mu = self.w / self.ws if self.ws != 0 else None
        return self.mu

    def calcular_volumen_especifico(self):
        """Calcula el volumen específico del aire húmedo (m3/kg_as)."""
        if self.tbsk is None:
            self.convertir_temperatura_kelvin()
        if self.patm is None:
            self.calcular_presion_atmosferica()
        if self.w is None:
            self.w = self.calcular_razon_humedad()

        # patm en kPa -> convertir a Pa multiplicando por 1000
        self.veh = ((self.RA * self.tbsk) / (self.patm * 1000.0)) * ((1 + 1.6087 * self.w) / (1 + self.w))
        return self.veh

    def calcular_entalpia(self, temperatura=None, razon_humedad=None):
        """Calcula la entalpía en kJ/kg (valores aproximados)."""
        if temperatura is None:
            temperatura = self.tbs
        if razon_humedad is None:
            if self.w is None:
                self.w = self.calcular_razon_humedad()
            razon_humedad = self.w

        self.h = (1.006 * temperatura) + razon_humedad * (2501 + 1.805 * temperatura)
        return self.h

    def calcular_temperatura_punto_rocio(self):
        """Calcula temperatura del punto de rocío Tpr en °C (aprox.)"""
        if self.pv is None:
            self.calcular_presion_vapor()

        # Estas fórmulas usan ln(pv) con pv en Pa
        if -60 < self.tbs < 0:
            self.tpr = -60.450 + 7.0322 * math.log(self.pv) + 0.3700 * (math.log(self.pv)) ** 2
        elif 0 <= self.tbs < 70:
            self.tpr = -35.957 - 1.8726 * math.log(self.pv) + 1.1689 * (math.log(self.pv)) ** 2
        else:
            # Si está fuera de rango, lo dejamos None pero no rompemos
            self.tpr = None
        return self.tpr

    def calcular_temperatura_bulbo_humedo(self, tolerancia=0.001, max_iteraciones=100):
        """
        Calcula la temperatura de bulbo húmedo (Tbh) por bisección.
        Devuelve °C.
        """
        if self.patm is None:
            self.calcular_presion_atmosferica()
        if self.w is None:
            self.calcular_presion_vapor()
            self.w = self.calcular_razon_humedad(self.pv, self.patm)

        def funcion_objetivo(tbh_prueba):
            pvs_tbh = self.calcular_presion_vapor_saturado(tbh_prueba)
            ws_tbh = self.calcular_razon_humedad(pvs_tbh, self.patm)
            # Ecuación psicrométrica aproximada (unidades SI)
            numerador = ((2501 - 2.326 * tbh_prueba) * ws_tbh - 1.006 * (self.tbs - tbh_prueba))
            denominador = (2501 + 1.86 * self.tbs - 4.186 * tbh_prueba)
            w_calculada = numerador / denominador
            return w_calculada - self.w

        tbh_min = -50.0
        tbh_max = self.tbs
        f_min = funcion_objetivo(tbh_min)
        f_max = funcion_objetivo(tbh_max)

        if f_min * f_max > 0:
            # fallback empírico si no cambia de signo
            self.tbh = self.tbs - (1 - self.hr) * (self.tbs - 14) / 3
            return self.tbh

        iteracion = 0
        while iteracion < max_iteraciones:
            tbh_prueba = (tbh_min + tbh_max) / 2.0
            error = funcion_objetivo(tbh_prueba)
            if abs(error) < tolerancia:
                self.tbh = tbh_prueba
                return self.tbh
            if error > 0:
                tbh_max = tbh_prueba
            else:
                tbh_min = tbh_prueba
            iteracion += 1

        self.tbh = (tbh_min + tbh_max) / 2.0
        return self.tbh

    def calcular_todo(self):
        """
        Ejecuta todos los cálculos en orden y devuelve un diccionario de resultados.
        """
        try:
            self.calcular_presion_atmosferica()
            self.convertir_temperatura_kelvin()
            self.calcular_presion_vapor_saturado()
            self.calcular_presion_vapor()
            self.calcular_deficit_presion_vapor()

            self.w = self.calcular_razon_humedad(self.pv, self.patm)
            self.ws = self.calcular_razon_humedad(self.pvs, self.patm)

            self.calcular_grado_saturacion()
            self.calcular_volumen_especifico()
            self.calcular_entalpia()
            self.calcular_temperatura_punto_rocio()
            self.calcular_temperatura_bulbo_humedo()

            return {
                'patm_kPa': self.patm,
                'pv_Pa': self.pv,
                'pvs_Pa': self.pvs,
                'dpva_Pa': self.dpva,
                'W_kgkg': self.w,
                'Ws_kgkg': self.ws,
                'mu': self.mu,
                'veh_m3kg': self.veh,
                'h_kJkg': self.h,
                'Tpr_C': self.tpr,
                'Tbh_C': self.tbh
            }

        except Exception as e:
            raise RuntimeError(f"Error en los cálculos: {e}")

# -----------------------
# Funciones auxiliares para procesamiento vectorial y archivos
# -----------------------

def _ensure_list(x):
    """Si x no es iterable (o es str), lo convierte en lista de un elemento."""
    if x is None:
        return []
    if isinstance(x, (list, tuple)):
        return list(x)
    # strings considered single scalar
    return [x]


def calcular_vectorial(z, tbs_list, hr_list):
    """
    Calcula propiedades psicrométricas para listas de tbs y hr.
    Args:
        z (float): elevación msnm
        tbs_list (iterable): temperaturas bulbo seco (°C)
        hr_list (iterable): humid relativa (0-1 o 0-100)
    Returns:
        list of dicts: resultados por muestra
    """
    tbs_l = _ensure_list(tbs_list)
    hr_l = _ensure_list(hr_list)

    if len(tbs_l) != len(hr_l):
        raise ValueError("tbs_list y hr_list deben tener la misma longitud.")

    resultados = []
    for tbs, hr in zip(tbs_l, hr_l):
        calc = CalculadoraPsicrometrica(z, tbs, hr)
        res = calc.calcular_todo()
        # añadir datos de entrada para referencia
        res['Tbs_C'] = float(tbs)
        res['HR_frac'] = float(hr) / 100.0 if float(hr) > 1.0 else float(hr)
        resultados.append(res)
    return resultados


def leer_csv_o_txt(filepath, delim=None, encabezados_esperados=None):
    """
    Lee un CSV o TXT delimitado y busca columnas para Tbs y HR.
    delim: si None, intenta detectar por coma o tab.
    encabezados_esperados: lista de posibles nombres para Tbs y HR:
       {'tbs': ['Tbs','tbs','T_bulbo_sec','Tbulbo'],'hr': ['HR','hr','humedad','phi','phi%']}
    Devuelve (tbs_list, hr_list)
    """
    if encabezados_esperados is None:
        encabezados_esperados = {
            'tbs': ['Tbs', 'tbs', 'T_bulbo_sec', 'Tbulbo', 'T'],
            'hr': ['HR', 'hr', 'Humedad', 'humedad', 'phi', 'phi%','hum%']
        }

    with open(filepath, 'r', newline='', encoding='utf-8') as f:
        sample = f.read(2048)
        f.seek(0)
        # detectar delimitador sencillo
        if delim is None:
            if ',' in sample:
                delim = ','
            elif '\t' in sample:
                delim = '\t'
            else:
                delim = ','

        reader = csv.reader(f, delimiter=delim)
        rows = list(reader)
        if not rows:
            return [], []

        header = [h.strip() for h in rows[0]]
        # intentar identificar columnas por nombre
        col_tbs = None
        col_hr = None
        for i, col in enumerate(header):
            low = col.lower()
            for candidate in encabezados_esperados['tbs']:
                if candidate.lower() == low:
                    col_tbs = i
            for candidate in encabezados_esperados['hr']:
                if candidate.lower() == low:
                    col_hr = i

        data_rows = rows[1:] if col_tbs is not None and col_hr is not None else rows  # si no hay header, leer todo
        tbs_list = []
        hr_list = []
        for r in data_rows:
            # proteger si fila corta
            if col_tbs is not None and col_hr is not None:
                try:
                    tbs_list.append(float(r[col_tbs]))
                    hr_list.append(float(r[col_hr]))
                except Exception:
                    # intentar saltar filas corruptas
                    continue
            else:
                # si no hay encabezado, intentar tomar las primeras 2 columnas como tbs,hr
                if len(r) >= 2:
                    try:
                        tbs_list.append(float(r[0]))
                        hr_list.append(float(r[1]))
                    except Exception:
                        continue

    return tbs_list, hr_list


def procesar_archivo(filepath, z, delim=None, encabezados_esperados=None, guardar_salida=None):
    """
    Lee un archivo (CSV/TXT). Devuelve resultados vectoriales.
    Si el archivo es .xls/.xlsx intentará usar openpyxl/xlrd si están disponibles.
    guardar_salida: ruta de archivo CSV donde escribir resultados (opcional).
    """
    ext = os.path.splitext(filepath)[1].lower()
    if ext in ['.csv', '.txt']:
        tbs_list, hr_list = leer_csv_o_txt(filepath, delim=delim, encabezados_esperados=encabezados_esperados)
    elif ext in ['.xls', '.xlsx']:
        # intentar usar librería si está instalada
        try:
            if ext == '.xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
                ws = wb.active
                rows = list(ws.values)
                # asumir primera fila header si strings
                header = rows[0]
                tbs_list = []
                hr_list = []
                # intentar detectar columnas por nombre
                headers = [str(h).strip().lower() if h is not None else '' for h in header]
                col_tbs = None
                col_hr = None
                for i, col in enumerate(headers):
                    if col in ('tbs','t','t_bulbo_sec','tbulbo'):
                        col_tbs = i
                    if col in ('hr','humedad','phi','phi%'):
                        col_hr = i
                for r in rows[1:]:
                    try:
                        if col_tbs is not None and col_hr is not None:
                            tbs_list.append(float(r[col_tbs]))
                            hr_list.append(float(r[col_hr]))
                        else:
                            tbs_list.append(float(r[0]))
                            hr_list.append(float(r[1]))
                    except Exception:
                        continue
            else:
                import xlrd
                wb = xlrd.open_workbook(filepath)
                sh = wb.sheet_by_index(0)
                rows = [sh.row_values(i) for i in range(sh.nrows)]
                # reusar lector csv logic:
                # escribir temporal csv-like in memory is possible but por brevedad:
                tbs_list, hr_list = leer_csv_o_txt(filepath, delim=delim, encabezados_esperados=encabezados_esperados)
        except Exception:
            raise RuntimeError("No se pudo leer archivo Excel: instala 'openpyxl' (xlsx) o convierte el archivo a CSV.")
    else:
        raise ValueError("Extensión no soportada. Use .csv, .txt, .xls o .xlsx (o convierta a .csv).")

    # ahora calcular vectorial
    resultados = calcular_vectorial(z, tbs_list, hr_list)

    # si se solicita guardar salida, escribir CSV con columnas ordenadas
    if guardar_salida:
        campos = ['Tbs_C', 'HR_frac', 'patm_kPa', 'pv_Pa', 'pvs_Pa', 'dpva_Pa',
                  'W_kgkg', 'Ws_kgkg', 'mu', 'veh_m3kg', 'h_kJkg', 'Tpr_C', 'Tbh_C']
        with open(guardar_salida, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            for r in resultados:
                # filtrar sólo campos en 'campos'
                fila = {k: (r.get(k) if k in r else None) for k in campos}
                writer.writerow(fila)

    return resultados


