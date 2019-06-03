# Agregación de Full RIB

En primer lugar, abrir una consola y pararse en esta carpeta.
Para descargar la Full RIB se debe ejecutar:

    $ python descarga_full_rib.py

Dicho script genera un archivo full_rib.csv en donde se deposita la salida, y utiliza los siguientes parámetros:

* from time: 2015-01-05 20:00:00
* until time: 2015-01-05 20:00:10
* collector: route-views.kixp

En caso de querer modificar alguno de los mismos, hacerlo en dicho script.
Una vez obtenido el archivo full_rib.csv, se puede ejecutar el algoritmo de agregación y obtener una salida mas completa:

    $ python agregacion_full_rib.py
