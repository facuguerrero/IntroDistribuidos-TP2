import os
os.environ['LD_LIBRARY_PATH'] = '/usr/local/lib'
import pybgpstream
import random

def crear_stream(objetivo):
    return pybgpstream.BGPStream(
        from_time='2012-01-05 19:59:00 UTC', until_time='2012-01-05 20:01:00 UTC',
        collectors=['route-views.saopaulo'],
        record_type='ribs',
        filter='path %s' % objetivo
    )

def parsear_entradas(stream, objetivo):
    proveedores = set()
    caminos = set()
    prefijos = set()

    for entrada in stream:
        as_act = entrada.fields['as-path']
        caminos.add(as_act)

        prefijo = entrada.fields['prefix']
        prefijos.add(prefijo)

        lista_as = as_act.split(' ')

        #Si no termina en el ASobjetivo, lo ignoramos
        if lista_as[-1] != str(objetivo):
            continue

        #El proveedor se encuentra en la anteultima posicion del as-path
        if lista_as[-2] != str(objetivo):
            proveedores.add(lista_as[-2])

    return {'proveedores': proveedores,
           'caminos': caminos,
           'prefijos': prefijos}

def main():
    objetivo = 16814 # Telecom Argentina
    #objetivo = 34795 # AS objetivo
    stream = crear_stream(objetivo)
    resultado = parsear_entradas(stream, objetivo)

    print 'Cantidad de caminos: ', len(resultado['caminos'])
    print 'Cantidad de prefijos: ', len(resultado['prefijos'])

    print 'Cantidad de proveedores: ', len(resultado['proveedores'])
    print 'Proveedores: '
    for proveedor in resultado['proveedores']:
        print '  ' + proveedor

if __name__ == '__main__':
    main()
