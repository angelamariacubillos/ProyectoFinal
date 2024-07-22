import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.ticker import FuncFormatter
import pandas as pd
import numpy as np
from scipy import stats
import math

archivo_dat = "datosabril.txt"
mes = archivo_dat[5:-4]
df = pd.read_csv(archivo_dat, sep=';', skiprows=42, header=None)
horaUTC = df[0]
T = df[2]
V = df[3]
brillo = df[4]

horas_utc = [datetime.strptime(hora, '%Y-%m-%dT%H:%M:%S.%f') for hora in horaUTC]
horas_bogota = [hora - timedelta(hours=5) for hora in horas_utc]
horas_nocturnas = [hora for hora in horas_bogota if hora.hour >= 17 or hora.hour <= 6]
horas_nocturnas.sort()

noches_separadas = []
noche_actual = []

for hora in horas_nocturnas:
    if not noche_actual:
        noche_actual.append(hora)
    elif (hora - noche_actual[-1]).seconds > 6 * 3600:
        noches_separadas.append(noche_actual)
        noche_actual = [hora]
    else:
        noche_actual.append(hora)
noches_separadas.append(noche_actual)

minutos_bogota = []

for hora in horas_bogota:
    ange = 24 if hora.hour <= 7 else 0
    minutos_bogota.append((hora.hour + ange) * 60 + hora.minute)

plt.figure(figsize=(10, 6))
noche_sumadas = np.zeros(180)
noche_sumadas_morado = np.zeros(180)
noche_sumadas_azul = np.zeros(180)
inter = np.linspace(1020, 1920, 180)
cantidad = np.zeros(180)
cantidad_morado = np.zeros(180)
cantidad_azul = np.zeros(180)

for idx, noche in enumerate(noches_separadas):
    brillo_noche = [brillo[horas_bogota.index(hora)] for hora in noche]
    juan = [minutos_bogota[horas_bogota.index(hora)] for hora in noche]

    brillo_noche_filtrado = [b for b in brillo_noche if b > 18]
    horas_noche_filtrado = [minutos_bogota[horas_bogota.index(noche[i])] for i, b in enumerate(brillo_noche) if b > 18]

    desviacion_estandar = np.std(brillo_noche_filtrado)

    MAD = stats.median_abs_deviation(brillo_noche_filtrado)
    mediana = np.median(brillo_noche_filtrado)
    promedio = np.mean(brillo_noche_filtrado)

    brillo_noche_filtrado = [b for b in brillo_noche if b > 6]
    horas_noche_filtrado = [minutos_bogota[horas_bogota.index(noche[i])] for i, b in enumerate(brillo_noche) if b > 6]

    color = 'mediumpurple' if not math.isnan(mediana) and float(mediana) >= 19.0 else 'skyblue'
    plt.plot(horas_noche_filtrado, brillo_noche_filtrado, color=color, linewidth=1)

    for idx, minuto in enumerate(horas_noche_filtrado):
        
        intervalo = (minuto - 1020) // 5
        
        if 0 <= intervalo < len(noche_sumadas):
            noche_sumadas[intervalo] += brillo_noche_filtrado[idx]
            cantidad[intervalo] += 1
            
            if color == 'mediumpurple':
                noche_sumadas_morado[intervalo] += brillo_noche_filtrado[idx]
                cantidad_morado[intervalo] += 1
            else:
                noche_sumadas_azul[intervalo] += brillo_noche_filtrado[idx]
                cantidad_azul[intervalo] += 1

noche_promedio = noche_sumadas / cantidad
noche_promedio_morado = noche_sumadas_morado / cantidad_morado
noche_promedio_azul = noche_sumadas_azul / cantidad_azul

plt.plot(inter, noche_promedio, color="crimson", label="Brillo Promedio General")
plt.plot(inter, noche_promedio_morado, color="darkgreen", label="Brillo Promedio Noches Despejadas")
plt.plot(inter, noche_promedio_azul, color="darkorange", label="Brillo Promedio Noches Nubladas")
plt.gca().invert_yaxis()



plt.xlabel('Hora Local', weight='bold',fontsize=14)
plt.ylabel(r'$\mathbf{Brillo\ (mag/arcsec^2)}$', weight='bold',fontsize=14)

def nombre(m,c):
    ho = m//60
    guayaba = m%60
    
    if m > 1440:
        m = m - 1440
        ho = m//60

    if ho < 10:
        ho = "0"+str(ho)
        
    if guayaba < 10:
        guayaba = "0"+str(guayaba)   
    
    ho=str(ho)
    ho=ho[:2]
        
    guayaba=str(guayaba)
    guayaba=guayaba[:2]

    return (ho+":"+guayaba)

formatter = FuncFormatter(nombre)
plt.gca().xaxis.set_major_formatter(formatter)
plt.xticks(fontsize=14)  
plt.yticks(fontsize=14)
plt.grid(True)

plt.legend(fontsize=14)
plt.tight_layout()
plt.show()

# Calcular la mediana en el intervalo de 19:00 a 04:00
inicio = 1140  # 19:00 en minutos
fin = 240  # 04:00 en minutos del día siguiente

# Filtrar los datos dentro del intervalo
noche_promedio_intervalo = noche_promedio[(inter >= inicio) | (inter <= fin)]
noche_promedio_morado_intervalo = noche_promedio_morado[(inter >= inicio) | (inter <= fin)]
noche_promedio_azul_intervalo = noche_promedio_azul[(inter >= inicio) | (inter <= fin)]

# Calcular las medianas
mediana_noche_promedio = np.nanmedian(noche_promedio_intervalo)
mediana_noche_promedio_morado = np.nanmedian(noche_promedio_morado_intervalo)
mediana_noche_promedio_azul = np.nanmedian(noche_promedio_azul_intervalo)

print("Mediana de la noche promedio:", mediana_noche_promedio)
print("Mediana de la noche morada:", mediana_noche_promedio_morado)
print("Mediana de la noche azul:", mediana_noche_promedio_azul)
