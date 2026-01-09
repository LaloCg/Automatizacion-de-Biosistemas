#include <math.h>              // Para pow(), log(), exp()
#include "DHT.h"              
#include <LiquidCrystal_I2C.h> 
#include <ThreeWire.h>  
#include <RtcDS1302.h> 
#include "FS.h"     
#include "SD.h"     
#include "SPI.h"    

// --- Objeto SPI personalizado en el bus HSPI ---
SPIClass spi = SPIClass(HSPI);

// --- Pin Chip Select (CS) para la SD ---
const int chipSelectPin = 15;

// --- Constante de Altitud ---
const float ALTITUDE = 2250.0; // Altitud en metros (msnm)

// --- Configuración de pines del RTC ---
ThreeWire myWire(18, 19, 5); // (DAT, CLK, RST)
RtcDS1302<ThreeWire> Rtc(myWire); 

// --- Configuración de la LCD ---
LiquidCrystal_I2C lcd(0x27, 20, 4); // 20 columnas, 4 filas

// --- Pines y Constantes NTC 1 (Bulbo Seco) ---
const int ntcPin_1 = 35;
const float referenceResistor_1 = 10000.0;
const float nominalResistance_1 = 10000.0;
const float STEIN_A_1 = 0.001129148;
const float STEIN_B_1 = 0.000234125;
const float STEIN_C_1 = 0.0000000876741;

// --- Pines y Constantes NTC 2 (Bulbo Húmedo) ---
const int ntcPin_2 = 34;
const float referenceResistor_2 = 10000.0;
const float nominalResistance_2 = 10000.0;
const float STEIN_A_2 = 0.001129148;
const float STEIN_B_2 = 0.000234125;
const float STEIN_C_2 = 0.0000000876741;

// --- Pines y Constantes DHT11 ---
const int dhtPin = 32;
const int dhtType = DHT11;
DHT dht(dhtPin, dhtType);

// --- Constantes Globales ---
const float referenceVoltage = 3.3;
const int SAMPLES_COUNT = 20;

// --- Constantes de Tiempo ---
const unsigned long READ_INTERVAL = 2000;
unsigned long lastReadTime = 0; 

// --- Acumuladores y bandera ---
float sum_NTC1 = 0, sum_NTC2 = 0, sum_DHT_T = 0, sum_DHT_H = 0;
int sampleCount = 0; 
bool hasLoggedThisInterval = false;


// --- Función 'setup' ---
void setup() {
  Serial.begin(115200);
  dht.begin();
  lcd.init();
  lcd.backlight();
  Rtc.Begin();
  
  //Rtc.SetDateTime(RtcDateTime(__DATE__, __TIME__)); 
  
  // --- Iniciar el módulo SD con pines personalizados ---
  lcd.setCursor(0, 3);
  lcd.print("Iniciando SD...");

  // 1. Inicia el NUEVO bus SPI ('spi') con TUS pines:
  //    (SCK=14, MISO=25, MOSI=13)
  spi.begin(14, 25, 13); 

  // 2. Inicia la biblioteca SD pasándole el pin CS y el NUEVO bus 'spi'
  if (!SD.begin(chipSelectPin, spi)) { // Usamos 'spi', no 'SPI'
    Serial.println("Error al iniciar la tarjeta SD");
    lcd.print("Error SD!");
    while (true); // Detiene el programa
  }
  
  // Si llegas aquí, funcionó
  lcd.print("SD OK.");
  Serial.println("Tarjeta SD iniciada.");

  // --- Escribir el encabezado COMPLETO del CSV ---
  File dataFile = SD.open("/datalog.csv", FILE_READ);
  if (!dataFile) { 
    Serial.println("Creando archivo datalog.csv con encabezado...");
    dataFile = SD.open("/datalog.csv", FILE_WRITE); 
    if (dataFile) {
      // --- CAMBIO: Se agregaron Tbh y Tbs_DHT al encabezado ---
      dataFile.println("timestamp,Tbs,Tbh,HR,Tbs_DHT,pv,pvs,dpva,w,ws,mu,veh,h,tpr");
      dataFile.close();
      Serial.println("Encabezado escrito.");
    } else {
      Serial.println("Error al crear datalog.csv");
    }
  } else {
    Serial.println("Archivo datalog.csv ya existe.");
    dataFile.close();
  }
  
  delay(2000); 
}

// --- Función 'loop' ---
void loop() {
  unsigned long currentTime = millis();
  RtcDateTime now = Rtc.GetDateTime();
  if (!now.IsValid()) { Serial.println("Error al leer el RTC!"); }

  // --- TAREA 1: Escaneo de Sensores (Cada 2 segundos) ---
  if (currentTime - lastReadTime >= READ_INTERVAL) {
    lastReadTime = currentTime; 

    float tempC_NTC1 = readNTC(ntcPin_1, referenceResistor_1, STEIN_A_1, STEIN_B_1, STEIN_C_1);
    float tempC_NTC2 = readNTC(ntcPin_2, referenceResistor_2, STEIN_A_2, STEIN_B_2, STEIN_C_2);
    float humidity_DHT = dht.readHumidity();
    float tempC_DHT = dht.readTemperature();

    updateLCD(now, tempC_NTC1, tempC_NTC2, tempC_DHT, humidity_DHT);

    if (!isnan(humidity_DHT) && !isnan(tempC_DHT)) {
      sum_NTC1 += tempC_NTC1;
      sum_NTC2 += tempC_NTC2;
      sum_DHT_T += tempC_DHT;
      sum_DHT_H += humidity_DHT;
      sampleCount++; 
    }
  } 

  
  // --- TAREA 2: Cálculo y Guardado (Cada 10 minutos) ---
  if (now.Minute() % 10 == 0 && !hasLoggedThisInterval) {
    
    if (sampleCount > 0) { 
      // 1. Calcular Promedios
      float avg_NTC1 = sum_NTC1 / sampleCount; // Tbs
      float avg_NTC2 = sum_NTC2 / sampleCount; // Tbh
      float avg_DHT_H = sum_DHT_H / sampleCount; // HR
      // --- CAMBIO: Se agregó el cálculo del promedio de Tbs2 (DHT) ---
      float avg_DHT_T = sum_DHT_T / sampleCount; // Tbs2 (DHT)

      // 2. Formatear la Fecha y Hora (Timestamp)
      char timestamp[20]; 
      snprintf(timestamp, 20, "%04d-%02d-%02d %02d:%02d:00",
               now.Year(), now.Month(), now.Day(),
               now.Hour(), now.Minute());

      // --- 3. Calcular Propiedades Psicrométricas ---
      float pv, pvs, dpva, w, ws, mu, veh, h, tpr;
      float hr_fraction = avg_DHT_H / 100.0; 
      calculatePsychrometrics(ALTITUDE, avg_NTC1, hr_fraction,
                              pv, pvs, dpva, w, ws, mu, veh, h, tpr);

      // 4. Imprimir TODO en Serial (para depuración)
      Serial.println("\n--- REGISTRO 10 MIN ---");
      Serial.printf("Timestamp: %s\n", timestamp);
      Serial.printf("  Tbs: %.2f C, Tbh: %.2f C\n", avg_NTC1, avg_NTC2); // Tbh agregado
      Serial.printf("  HR: %.1f %%, Tbs_DHT: %.1f C\n", avg_DHT_H, avg_DHT_T); // Tbs_DHT agregado
      Serial.printf("  w: %.6f, ws: %.6f\n", w, ws);
      Serial.printf("  h: %.3f, tpr: %.3f\n", h, tpr);


      // --- 5. Guardar la LÍNEA COMPLETA en la SD ---
      File dataFile = SD.open("/datalog.csv", FILE_APPEND);
      if (dataFile) {
        String dataString = "";
        // --- CAMBIO: Se agregaron Tbh (avg_NTC2) y Tbs_DHT (avg_DHT_T) ---
        dataString += String(timestamp) + ",";
        dataString += String(avg_NTC1) + ",";    // Tbs
        dataString += String(avg_NTC2) + ",";    // Tbh (NTC2)
        dataString += String(avg_DHT_H) + ",";    // HR
        dataString += String(avg_DHT_T) + ",";    // Tbs2 (DHT)
        dataString += String(pv) + ",";
        dataString += String(pvs) + ",";
        dataString += String(dpva) + ",";
        dataString += String(w) + ",";
        dataString += String(ws) + ",";
        dataString += String(mu) + ",";
        dataString += String(veh) + ",";
        dataString += String(h) + ",";
        dataString += String(tpr);
        
        dataFile.println(dataString); 
        dataFile.close(); 
        Serial.println("¡Línea completa guardada en SD!");
      } else {
        Serial.println("¡Error al abrir datalog.csv para guardar!");
      }
      
      // 6. Resetear acumuladores
      sum_NTC1 = 0; sum_NTC2 = 0; sum_DHT_T = 0; sum_DHT_H = 0;
      sampleCount = 0;
      hasLoggedThisInterval = true;
      
    } else {
      Serial.println("\n--- REGISTRO 10 MIN: No se tomaron muestras válidas --- \n");
    }
  } 
  
  if (now.Minute() % 10 != 0) {
    hasLoggedThisInterval = false;
  }
} // Fin del loop

// --- Función updateLCD (Sin cambios) ---
void updateLCD(RtcDateTime now, float tbs, float tbh, float dht_t, float dht_h) {
  lcd.clear(); 
  char buf[21]; 
  snprintf(buf, 21, "%02d:%02d:%02d  %02d/%02d/%04d",
           now.Hour(), now.Minute(), now.Second(),
           now.Day(), now.Month(), now.Year());
  lcd.setCursor(0, 0); lcd.print(buf);
  lcd.setCursor(0, 1); lcd.print("Tbs (NTC1): "); lcd.print(tbs, 2); lcd.print(" C");
  lcd.setCursor(0, 2); lcd.print("Tbh (NTC2): "); lcd.print(tbh, 2); lcd.print(" C");
  lcd.setCursor(0, 3); lcd.print("DHT H: ");
  if (isnan(dht_h)) { lcd.print("ERR"); } else { lcd.print(dht_h, 1); lcd.print("%"); }
  lcd.setCursor(11, 3); lcd.print(" T:");
  if (isnan(dht_t)) { lcd.print("ERR"); } else { lcd.print(dht_t, 1); lcd.print("C"); }
}

// --- Función readNTC (Sin cambios) ---
float readNTC(int pin, float refResistor, float A, float B, float C) {
  float totalVoltage = 0;
  for (int i = 0; i < SAMPLES_COUNT; i++) {
    totalVoltage += analogReadMilliVolts(pin); delay(2); 
  }
  float voltage = (totalVoltage / SAMPLES_COUNT) / 1000.0;
  float resistance = (voltage * refResistor) / (referenceVoltage - voltage);
  float logR = log(resistance);
  float tempK = 1.0 / (A + (B * logR) + (C * logR * logR * logR));
  float tempC = tempK - 273.15;
  return tempC;
}

// --- Función de Cálculo Psicrométrico (Sin cambios) ---
void calculatePsychrometrics(float z, float tbs, float hr,
                             float& pv, float& pvs, float& dpva,
                             float& w, float& ws, float& mu,
                             float& veh, float& h, float& tpr) {

    float patm = 101.325 * pow(1.0 - (2.25577e-5 * z), 5.2529);
    float tbsk = 273.15 + tbs;
    const float ra = 287.055; 

    pvs = 0.0; 
    if (tbs > -100 && tbs < 0) {
        pvs = exp( (-5.6745359e3 / tbsk) + 6.3925247 - (9.6778430e-3 * tbsk) + 
                   (6.2215701e-7 * pow(tbsk, 2)) + (2.0747825e-9 * pow(tbsk, 3)) - 
                   (9.484024e-13 * pow(tbsk, 4)) + (4.1635019 * log(tbsk)) );
    } 
    else if (tbs >= 0 && tbs < 200) {
        pvs = exp( (-5.8002206e3 / tbsk) + 1.3914993 - (48.640239e-3 * tbsk) + 
                   (41.764768e-6 * pow(tbsk, 2)) - (14.452093e-9 * pow(tbsk, 3)) + 
                   (6.5459673 * log(tbsk)) );
    }

    pv = hr * pvs;
    dpva = pvs - pv;
    w = 0.621945 * ( (pv / 1000.0) / (patm - (pv / 1000.0)) );
    ws = 0.621945 * ( (pvs / 1000.0) / (patm - (pvs / 1000.0)) );

    mu = 0.0;
    if (ws > 0) { mu = w / ws; }

    veh = ((ra * tbsk) / (patm * 1000.0)) * ((1.0 + 1.6087 * w) / (1.0 + w));
    h = (1.006 * tbs) + w * (2501.0 + 1.805 * tbs);

    tpr = 0.0; 
    if (pv > 0) { 
        if (tbs > -60 && tbs < 0) {
            tpr = -60.450 + 7.0322 * log(pv) + 0.3700 * pow(log(pv), 2);
        } else if (tbs >= 0 && tbs < 70) {
            tpr = -35.957 - 1.8726 * log(pv) + 1.1689 * pow(log(pv), 2);
        }
    }
}