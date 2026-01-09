# Automatización de Biosistemas - Portafolio de Proyectos

Este repositorio documenta las prácticas y proyectos desarrollados para la asignatura de **Automatización de Biosistemas** en el Departamento de Ingeniería Mecánica Agrícola de la **Universidad Autónoma Chapingo**.

**Estudiante:** Eduardo Cano García  
**Grupo:** 7° 6  
**Enfoque:** Psicrometría, Instrumentación Meteorológica y Análisis de Datos Climáticos.

---

## 📂 Contenido del Repositorio

El trabajo se divide en el desarrollo de algoritmos para el cálculo de propiedades del aire húmedo y la validación experimental de sensores de temperatura bajo distintas condiciones de radiación.

### 1. Psicrometría Computacional (Tarea 1 y 2)
Desarrollo de herramientas de software para el análisis termodinámico del aire, fundamentales para el control de invernaderos y sistemas de almacenamiento poscosecha.

* **Algoritmos de Cálculo:** Implementación de modelos matemáticos para determinar propiedades como:
    * Razón de humedad ($W$) y Humedad Relativa ($\phi$).
    * Entalpía ($h$) y Volumen Específico ($V_{eh}$).
    * Presión de Vapor ($P_v$) y Temperatura de Punto de Rocío ($T_{pr}$).
* **Generación de Cartas Psicrométricas:** Scripts para graficar el estado del aire ajustado a diferentes altitudes ($Z$).
* **Análisis de Datos EMA:** Procesamiento de 90 días de datos de Estaciones Meteorológicas Automáticas (Teziutlán y Tecamachalco) para visualizar el comportamiento climático local sobre la carta psicrométrica.



### 2. Instrumentación y Medición de Temperatura (Proyecto 2)
**"Comparación de Métodos de Medición de Temperatura del Aire"**

Este proyecto experimental evalúa el error de medición introducido por la radiación solar y la falta de ventilación en sensores electrónicos. Se diseñó y construyó un prototipo para comparar tres configuraciones simultáneas:

1.  **Sensor Expuesto:** Sometido a radiación directa (simulando error máximo).
2.  **Sensor Protegido (Pasivo):** Dentro de una protección contra radiación pero sin ventilación forzada.
3.  **Psicrómetro (Aspirado):** Sensor protegido con ventilación forzada constante (Estándar de referencia).

**Resultados Clave:**
* Cuantificación del sesgo térmico debido a la carga de radiación de onda corta y larga.
* Cálculo experimental de la Temperatura de Bulbo Húmedo ($T_{bh}$) mediante el método de aspiración.


---

## 🛠️ Tecnologías y Herramientas

* **Lenguajes:** Python (Procesamiento de datos `.csv` y `.xls`).
* **Librerías:** `Matplotlib` (Visualización de cartas), `Pandas` (Manejo de series de tiempo de estaciones EMA).
* **Hardware (Proyecto 2):** Sensores de temperatura, microcontroladores (Arduino/ESP32) y sistemas de ventilación forzada DC.

---

## 📄 Referencias Teóricas
* **ASAE Standards:** Ecuaciones para el cálculo de propiedades del aire húmedo.

---
*Eduardo Cano García | Universidad Autónoma Chapingo*
