import csv
import socket

def crear_direcciones_agrupadas_por_asn():
    """ Creamos un diccionario { asn: [prefijos] }
    Nos sirve tenerlo de esta forma ya que 2 prefijos son agregables
    Si tienen el mismo asn """
    direcciones_agrupadas_por_asn = {}
    with open('full_rib.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            asn = row[1]
            dir_ip = row[0]
            # Solo queremos los prefijos que sean IPv4.
            # Por lo que solo lo aniadimos si cumple esta condicion
            dir_ip_sin_mascara = dir_ip.split('/')[0]
            if validar_ipv4(dir_ip_sin_mascara):
                agregar_clave_valor(direcciones_agrupadas_por_asn, asn, dir_ip)
    return direcciones_agrupadas_por_asn

def agregar_clave_valor(dict, key, value):
    if key not in dict.keys():
        dict[key] = set()
    dict[key].add(value)

def validar_ipv4(dir_ip):
    """
    Para saber si una direccion ip es ipv4:
    https://stackoverflow.com/questions/319279/how-to-validate-ip-address-in-python
    """
    try:
        socket.inet_pton(socket.AF_INET, dir_ip)
        return True
    except AttributeError:
        try:
            socket.inet_aton(dir_ip)
        except socket.error:
            return False
        return dir_ip.count('.') == 3
    except socket.error:
        return False

def crear_direcciones_agrupadas_por_mascara(direcciones):
    """ Como ya tenemos las direcciones agregadas por asn
    Agrupamos las direcciones ip por tamanio de mascara
    Para luego chequear si son contiguas """
    direcciones_agrupadas_por_mascara = {}
    for direccion in direcciones:
        direccion_separada = direccion.split('/')
        dir_ip = direccion_separada[0]
        mascara = direccion_separada[1]
        agregar_clave_valor(direcciones_agrupadas_por_mascara, int(mascara), transformar_a_binario(dir_ip))
    return direcciones_agrupadas_por_mascara

def transformar_a_binario(dir_ip):
    """
    Para transformar una dir ip en binario
    https://stackoverflow.com/questions/2733788/convert-ip-address-string-to-binary-in-python
    """
    return ''.join([bin(int(x)+256)[3:] for x in dir_ip.split('.')])

def limpiar_resultado_final(direcciones_a_borrar, direcciones_a_agregar, direcciones_agrupadas_por_mascara):
    for mascara, direcciones_ip in direcciones_a_borrar.iteritems():
        for dir_ip in direcciones_ip:
            direcciones_agrupadas_por_mascara[mascara].remove(dir_ip)
    for mascara, direcciones_ip in direcciones_a_agregar.iteritems():
        for dir_ip in direcciones_ip:
            agregar_clave_valor(direcciones_agrupadas_por_mascara, mascara, dir_ip)

def obtener_prefijo_de_direccion(dir_ip, mascara):
    return dir_ip[:mascara] + '0'*(32-mascara)


def son_contiguas(dir_ip_1, dir_ip_2, mascara):
    """ Se le suma los bits que la mascara nos permite modificar, para alcanzar
    el limite de la direccion ip. """
    final_dir_ip_1 = bin(int(dir_ip_1, 2) + 2**(32-mascara))[-32:]
    if dir_ip_2 == final_dir_ip_1:
        return True, dir_ip_1
    final_dir_ip_2 = bin(int(dir_ip_2, 2) + 2**(32-mascara))[-32:]
    if dir_ip_1 == final_dir_ip_2:
        return True, dir_ip_2
    return False, None

def main():

    direcciones_agrupadas_por_asn = crear_direcciones_agrupadas_por_asn()
    # Datos para la salida
    prefijos_iniciales = 0
    asn_iniciales = 0
    prefijos_finales = 0

    for asn, direcciones_ip in direcciones_agrupadas_por_asn.iteritems():
        # Incrementamos los datos para la salida
        asn_iniciales += 1
        prefijos_iniciales += len(direcciones_ip)

        # Organizamos las direcciones ip pertenecientes a un mismo AS, por mascara
        direcciones_agrupadas_por_mascara = crear_direcciones_agrupadas_por_mascara(direcciones_ip)

        # Estructuras auxiliares para python.
        # Python no deja modificar un diccionario mientras que se lo esta iterando
        # Por eso necesitamos estructuras para luego modificar el resultado.
        direcciones_a_agregar = {}
        direcciones_a_borrar = {}

        # Ahora comparamos todas las direcciones dentro de una misma mascara.
        for mascara, direcciones_ip in direcciones_agrupadas_por_mascara.iteritems():

            lista_direcciones_ip = list(direcciones_ip)
            agregaciones = []
            for i in xrange(len(lista_direcciones_ip)-1):
                for j in xrange(i+1, len(lista_direcciones_ip)):
                    dir_ip_1 = lista_direcciones_ip[i]
                    dir_ip_2 = lista_direcciones_ip[j]

                    #Si ya fueron agregadas, no hacemos nada
                    if dir_ip_1 in agregaciones or dir_ip_2 in agregaciones or dir_ip_1 == dir_ip_2:
                        continue

                    result = son_contiguas(dir_ip_1, dir_ip_2, mascara)
                    if result[0]:
                        nueva_dir_ip = obtener_prefijo_de_direccion(result[1], mascara-1)
                        agregar_clave_valor(direcciones_a_agregar, mascara-1, nueva_dir_ip)

                        # Las agregamos a la lista de agregaciones
                        agregaciones.append(dir_ip_1)
                        agregaciones.append(dir_ip_2)

                        # Las agregamos al diccionario para modificar el resultado final
                        agregar_clave_valor(direcciones_a_borrar, mascara, dir_ip_1)
                        agregar_clave_valor(direcciones_a_borrar, mascara, dir_ip_2)


            print 'Se agregaron %d direcciones para la mascara %d' % (len(agregaciones)/2, mascara)

        limpiar_resultado_final(direcciones_a_borrar, direcciones_a_agregar, direcciones_agrupadas_por_mascara)

        # Obtenemos la cantidad de direcciones finales
        for prefijos in direcciones_agrupadas_por_mascara.values():
            prefijos_finales += len(prefijos)
        print 'Agregacion finalizada para el ASN: %s' % asn

    print 'Cantidad de entradas iniciales: %d' % prefijos_iniciales
    print 'Cantidad de entradas finales:: %d' % prefijos_finales

if __name__ == '__main__':
    main()
