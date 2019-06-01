import pybgpstream


def main():
    stream = pybgpstream.BGPStream(
        from_time="2015-01-05 20:00:00", until_time="2015-01-05 20:00:10 UTC",
        collectors=['route-views.kixp'],
        record_type="ribs",
    )

    # Creamos un archivo csv para la salida: { ip_addr, isn }
    fd = open('full_rib.csv', 'w')
    for entrada in stream:
        origen = entrada.fields['as-path'].split(' ')[0]
        prefijo = entrada.fields['prefix']
        fd.write('%s,%s\n' % (prefijo, origen))
    fd.close()
    print("Fin del procesamiento")

if __name__ == '__main__':
    main()
