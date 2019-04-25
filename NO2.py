#Importar librerías del proyecto
import folium
import numpy as np
import pandas as pd

#Carga de datos
datos = pd.read_csv('https://datos.madrid.es/egob/catalogo/212531-7916318-calidad-aire-tiempo-real.txt', sep=",", header=None)
informacion = pd.read_excel("Estaciones.xlsx")
informacion.columns = ['ESTACION', 'NOMBRE', 'DIRECCION', 'LONGITUD', 'LATITUD', 'ALTURA']
headers = ["PROVINCIA", "MUNICIPIO", "ESTACION", "MAGNITUD", "tecnica", "dato diario", "ANO", "MES",
          "DIA", "H01","V01", "H02","V02", "H03", "V03", "H04", "V04", "H05", "V05", "H06", "V06",
          "H07", "V07", "H08", "V08","H09", "V09", "H10", "V10", "H11", "V11", "H12", "V12", "H13", "V13",
          "H14", "V14", "H15","V15", "H16", "V16", "H17", "V17", "H18", "V18", "H19", "V19", "H20", "V20",
          "H21", "V21","H22", "V22", "H23", "V23", "H24", "V24"]
datos.columns = [headers]

#Recortes de los datos originales
df1 = datos[['ESTACION', "MAGNITUD",]] #https://stackoverflow.com/questions/14940743/selecting-excluding-sets-of-columns-in-pandas
df1.columns = ["Station", "Magnitude"] #Renombradas por problemas con es español

df2 = informacion[["ESTACION", "LONGITUD", "LATITUD", "DIRECCION"]] #https://stackoverflow.com/questions/14940743/selecting-excluding-sets-of-columns-in-pandas
df2.columns = ['Station', 'Longitude', 'Latitude', 'Direction'] #Renombradas por problemas con es español

#Selección de los datos validados
validados = list()
for i in range(10, len(headers), 2):
   x = datos[headers[i]]
   y = datos[headers[i - 1]]
   if np.equal([x.loc[0]], ["N"]):
        break
   else:
       validados.clear()
       for j in range(0, len(x)):
            z = x.loc[j]
            validados.append(float(y.loc[j]))

#funcion para las coordenadas
def hexa(x):
    latitud = x.split('º')
    a1 = int(latitud[0])
    latitud2 = latitud[1]
    latitud3 = latitud2.split("'")
    b2 = int(latitud3[0])/60
    latitud4 = latitud3[1]
    latitud5 = latitud4.split(',')
    if len(latitud5)==2:
        latitud6 = [int(latitud5[0]),int(latitud5[1])/100]
        latitud7 = latitud6[0]+latitud6[1]
        c3 = latitud7/(60*60)
        datofinal = round(a1+b2+c3,6)
    else:
        latitud6 = int(latitud5[0])
        c3 = float(latitud6/(60*60))
        datofinal = round(a1+b2+c3,6)
    return(datofinal)

#Transformación de las coordenadas a coordenadas decimales en df2
LAT = list(df2['Latitude'])
latitud = list()

for ij in range(0, len(LAT)):
  n1 = hexa(LAT[ij])
  latitud.append(n1)

LON = list(df2['Longitude'])
longitud = list()

for ik in range(0, len(LON)):
    n2 = hexa(LON[ik])
    longitud.append(-1*n2)

#Creación del dataframe que se usará para dibujar el mapa
df2 = df2.assign(Latitud2 = latitud)
df2 = df2.assign(Longitud2 = longitud)
#https://www.reddit.com/r/Python/comments/b3gfz0/merging_with_pandas_trouble/
df3 = pd.merge(df1, df2, on='Station', how='left')

#Recorte del dataframe a plotear en función del contaminante deseado (Dióxido de Nitrógeno NO2)
df3 = df3.assign(Contaminacion = validados)
df4 = df3.loc[df3['Magnitude']==8]
df5 = df4.sort_values(by='Contaminacion', ascending=True)

niveles = list(df5['Contaminacion'].quantile([0, 0.25, 0.5, 0.75, 1]))

#Creación del mapa
m = folium.Map(location=[40.427340,-3.707134],min_zoom=12 ,zoom_start=12)
#https://python-visualization.github.io/folium/quickstart.html
#https://medium.com/the-artificial-impostor/visualizing-air-quality-data-2ec16268711e
#https://www.kaggle.com/daveianhickey/how-to-folium-for-maps-heatmaps-time-data
#El símbolo _, realmente sólo vale para que la variable row que hace de contador en el bucle no se quede guardada.
for _, row in df5.iterrows():
    if row['Contaminacion'] <= niveles[1]:
        color = 'green'
        nivel = 'Buena'
    elif row['Contaminacion'] <= niveles[2]:
        color = 'orange'
        nivel = 'Regular'
    elif row['Contaminacion'] <= niveles[3]:
        color = 'red'
        nivel = 'Mala'
    else:
        color = 'darkred'
        nivel = 'Muy mala'
    folium.CircleMarker(location=[row['Latitud2'],row['Longitud2']], tooltip='Nivel de NO2',popup=str(row['Contaminacion'])+' µg/m3', radius=10,fill=True,color=color, fill_opacity=0.8).add_to(m)
    folium.Marker(location=[row['Latitud2'], row['Longitud2']],popup='Dirección:' + row['Direction'],tooltip='Ubicación' ,icon=folium.Icon(color='lightblue')).add_to(m)

m.save('NO2 AQ.html')
