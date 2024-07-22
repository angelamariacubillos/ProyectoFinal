import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from scipy import stats
import math

archivo_dat = "datosliterales.txt"

mes = archivo_dat[5:]
mes = mes[:-4]
df = pd.read_csv(archivo_dat, sep=';', skiprows=42, header=None)
horaUTC = df[0]
T = df[2]
V = df[3]
brillo = df[4]

horas_utc = [datetime.strptime(hora, '%Y-%m-%dT%H:%M:%S.%f') for hora in horaUTC]
horas_bogota = [hora - timedelta(hours=5) for hora in horas_utc]
horas_nocturnas = [hora for hora in horas_bogota if hora.hour >= 17 or hora.hour <= 7]
horas_nocturnas.sort()

noches_separadas = []
noche_actual = []

ventanas_todas = []
brillo_todas = []
duracion_todas = []
brillo_promedio_todas = []

ventanas_por_mes = {}

noches_por_mes = {}
lista_noches_contador = []
noches_con_ventana = 0

umbral_variabilidad = 0.05

for hora in horas_nocturnas:
    
    if not noche_actual:
        
        noche_actual.append(hora)
        
    elif (hora - noche_actual[-1]).seconds > 6 * 3600:
        
        noches_separadas.append(noche_actual)
        noche_actual = [hora]
        
    else:
        noche_actual.append(hora)

noches_separadas.append(noche_actual)

duracion_todas = []


noches_en_mes = {}

intervalosvent = {}

for idx, noche in enumerate(noches_separadas):
    
    mes_actual = noche[0].strftime('%Y-%m')
    
    if mes_actual not in noches_en_mes:
        noches_en_mes[mes_actual] = set()
    noches_en_mes[mes_actual].add(noche[0].strftime('%Y-%m-%d'))
    
    noches_en_mes[mes_actual].add(noche[0].strftime('%Y-%m-%d'))

    plt.figure(figsize=(10, 6))
    
    brillo_noche = [brillo[horas_bogota.index(hora)] for hora in noche]
    
    brillo_noche_filtrado = [b for b in brillo_noche if b > 18]
    horas_noche_filtrado = [hora for i, hora in enumerate(noche) if brillo_noche[i] > 18]
    
    desviacion_estandar = np.std(brillo_noche_filtrado)
    
    ventanas_noche_actual = []
    brillo_noche_actual = []
    duracion_noche_actual = []
    
    MAD = stats.median_abs_deviation(brillo_noche_filtrado)
    mediana = np.median(brillo_noche_filtrado)
    promedio = np.mean(brillo_noche_filtrado)
        
    brillo_noche_filtrado = [b for b in brillo_noche if b > 6]
    horas_noche_filtrado = [hora for i, hora in enumerate(noche) if brillo_noche[i] > 6]
    
    
    if not math.isnan(mediana):
        
        if float(mediana) >= 19.0:
                       
            valoroscu_datos = [dato for dato in brillo_noche_filtrado if dato >= 19.0]
            valoroscu_horas = [hora for hora, dato in zip(horas_noche_filtrado, brillo_noche_filtrado) if dato >= 19.0]
            
            plt.scatter(valoroscu_horas, valoroscu_datos, color='r')
            
            intervalos_consecutivos = []
            temp_intervalo = [valoroscu_datos[0]]
            temp_horas_intervalo = [valoroscu_horas[0]]
            
            for i in range(0, len(valoroscu_datos)):
                
                diferencia = valoroscu_horas[i] - valoroscu_horas[i - 1]
                
                if abs(diferencia) <= timedelta(minutes=5):
                    
                    temp_intervalo.append(valoroscu_datos[i])
                    temp_horas_intervalo.append(valoroscu_horas[i])
                    
                else:
                    
                    intervalos_consecutivos.append((temp_intervalo, temp_horas_intervalo))
                    temp_intervalo = [valoroscu_datos[i]]
                    temp_horas_intervalo = [valoroscu_horas[i]]
                    intervalos_consecutivos.append((temp_intervalo, temp_horas_intervalo))
            
            for intervalo, horas_intervalo in intervalos_consecutivos:

                if len(intervalo)>=5:

                    plt.scatter(horas_intervalo, intervalo, color='green')                            
                    
                    mes_actual = horas_intervalo[0].strftime('%Y-%m')
                    
                    brillo_promedio_conjunto = np.mean(intervalo)
                    brillo_promedio_todas.append(brillo_promedio_conjunto)
        
                    ventanas_todas.append(intervalo) 
                    brillo_todas.append(intervalo)    
            
                    duracion_intervalo = (horas_intervalo[-1] - horas_intervalo[0]).total_seconds() / 3600.0
                    duracion_todas.append(duracion_intervalo)
                    
                    if mes_actual not in intervalosvent:
                        intervalosvent[mes_actual] = []
                    
                    intervalosvent[mes_actual].append(duracion_intervalo)


                    
                    if mes_actual not in ventanas_por_mes:
                        ventanas_por_mes[mes_actual] = set()
                    ventanas_por_mes[mes_actual].add(tuple(horas_intervalo))
        
        else:
            
            valoroscu = mediana + MAD
            valoroscu_datos = [dato for dato in brillo_noche_filtrado if dato >= valoroscu]
            valoroscu_horas = [hora for hora, dato in zip(horas_noche_filtrado, brillo_noche_filtrado) if dato >= valoroscu]
    
            plt.scatter(valoroscu_horas, valoroscu_datos, color='r')

            intervalos_consecutivos = []
            temp_intervalo = [valoroscu_datos[0]]
            temp_horas_intervalo = [valoroscu_horas[0]]
            
            for i in range(0, len(valoroscu_datos)):
                
                if abs(valoroscu_horas[i] - valoroscu_horas[i - 1]) <= timedelta(minutes=5):
                    
                    temp_intervalo.append(valoroscu_datos[i])
                    temp_horas_intervalo.append(valoroscu_horas[i])
                    
                else:
                    intervalos_consecutivos.append((temp_intervalo, temp_horas_intervalo))
                    temp_intervalo = [valoroscu_datos[i]]
                    temp_horas_intervalo = [valoroscu_horas[i]]
                    intervalos_consecutivos.append((temp_intervalo, temp_horas_intervalo))
            
    
            for intervalo, horas_intervalo in intervalos_consecutivos:
                
                if len(intervalo)>=5:
                    
                    diferencias_brillo = np.diff(intervalo)
                    
                    if any(abs(diff) <= umbral_variabilidad for diff in diferencias_brillo):

                        
                        plt.scatter(horas_intervalo, intervalo, color='green')
                                
                        mes_actual = horas_intervalo[0].strftime('%Y-%m')
                        
                        brillo_promedio_conjunto = np.mean(intervalo)
                        brillo_promedio_todas.append(brillo_promedio_conjunto)
            
                        ventanas_todas.append(intervalo) 
                        brillo_todas.append(intervalo)    
                
                        duracion_intervalo = (horas_intervalo[-1] - horas_intervalo[0]).total_seconds() / 3600.0
                        duracion_todas.append(duracion_intervalo)
                        
                        if mes_actual not in intervalosvent:
                            intervalosvent[mes_actual] = []
                        intervalosvent[mes_actual].append(duracion_intervalo)

                        
                        if mes_actual not in ventanas_por_mes:
                            ventanas_por_mes[mes_actual] = set()
                        ventanas_por_mes[mes_actual].add(tuple(horas_intervalo))

        

    plt.plot(horas_noche_filtrado, brillo_noche_filtrado, color='teal')
    formatoho = mdates.DateFormatter('%H:%M')
    plt.gca().xaxis.set_major_formatter(formatoho)
    plt.xlabel('Hora Local (Bogotá)', weight='bold') 
    plt.ylabel(r'$\mathbf{Brillo\ (mag/arcsec^2)}$', weight='bold')  
    
    plt.title('Brillo Nocturno', weight='bold', fontsize=20, y=1.06)
    fecha_noche = noche[0].strftime('%d-%m-%Y')
    dia=fecha_noche[:2]
    plt.suptitle(f'{fecha_noche}', weight='bold', fontsize=14, y=0.87)

    plt.grid(True)
    plt.tight_layout()
    plt.gca().invert_yaxis()
    plt.show()
    
        
meses = list(ventanas_por_mes.keys())
ventanas = [len(ventanas_por_mes[mes]) for mes in meses]
duracion_horas = np.array(duracion_todas)
brillo_promedio = np.array(brillo_promedio_todas)

duracion_total_por_mes = {}

for mes, ventana in intervalosvent.items():
    duracion_total_mes_minutos = sum(ventana) * 60  
    duracion_total_por_mes[mes] = duracion_total_mes_minutos

duracion_por_mes = {}

for mes, noches in noches_en_mes.items():
    duracion_total_mes = 0
    
    for noche_fecha in noches:
        
        noche = [hora for hora in noches_separadas if hora[0].strftime('%Y-%m-%d') == noche_fecha][0]
        
        duracion_noche = (max(noche) - min(noche)).total_seconds() / 60
                
        duracion_total_mes += duracion_noche
    
    duracion_por_mes[mes] = duracion_total_mes

ventanas_normalizadas = [duracion_por_mes[mes] / duracion_total_por_mes[mes] for mes in meses]



plt.figure(figsize=(10, 6))
plt.hist(duracion_horas, bins=30, color='lightseagreen', edgecolor='teal')

plt.xlabel('Duración (horas)', weight='bold')
plt.ylabel('Frecuencia', weight='bold')

plt.title("Duración Ventanas", weight='bold', fontsize=16)

plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 6))
plt.bar(meses, ventanas_normalizadas, color='lightseagreen', edgecolor='teal')
plt.xlabel('Año-Mes', weight='bold', fontsize=14)
plt.ylabel('Número de Ventanas Normalizadas', weight='bold', fontsize=14)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.grid(True)
plt.tight_layout()
plt.legend()
plt.show()

plt.figure(figsize=(10, 6))
plt.scatter(duracion_horas, brillo_promedio, color='lightseagreen', edgecolor='teal')
plt.xlabel('Duración(horas)', weight='bold', fontsize=14)
plt.ylabel('Brillo Promedio', weight='bold', fontsize=14)

plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

plt.grid(True)
plt.tight_layout()
plt.legend()
plt.show()
