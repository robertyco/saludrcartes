import json, sys

d = json.load(open('data/expediente.json', encoding='utf-8'))
docs = d['documentos']
for doc in docs:
    print('=====', doc['id'], '| cat:', doc['categoria_id'], '| fecha:', doc['fecha'], '| afeccion:', doc.get('afeccion_id'))
    print('DESC:', doc['descripcion'])
    print('FOLIOS:', doc['paginas_originales'], doc['formato'])
    print()