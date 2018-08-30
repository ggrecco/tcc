import nmap
import os
from app.models import Servidor, Usuario
from app.scrapy import scraper
from flask_login import current_user


# site pra teste -> 'testphp.vulnweb.com'
# site pra teste -> 'scanme.nmap.org'
def portScan(site, user):
    a = nmap.PortScanner()
    s = str(site)
    # scaneia as portas
    d = a.scan(s, '21, 22, 23, 25, 53, 63, 70, 79, 80, 110, 119', '-sV')
    # Busca servidor no banco de dados
    ser = Servidor.query.filter_by(url=site, usuario_id=user)
    ip = ser.value('ip')
    nome = ser.value('nome')
    lista = [21, 22, 23, 25, 53, 63, 70, 79, 80, 110, 119]
    i = 0

    while i < len(lista):
        j = d['scan'][ip]['tcp'][lista[i]]['product']
        if j in '':
            pass
        else:
            print(j)
            scraper(j, nome, lista[i], user)
        i = i + 1


def busca_ip(site):
    # captura apenas o campo de ip e salva em um arquivo txt
    s = str(site)
    # os.system("host " + s + " | awk '{print $4}' > ip.txt")
    os.system('ping -c1 ' + s + " -4 | awk '{print $3}' > ip.txt")
    arq = open('/home/ggrecco/Documentos/python/flask/tcc-teste/ip.txt', 'r')
    ip = arq.read()
    b = ip.split("(")
    c = b[1].split(")")
    ip = c[0]
    arq.close()

    return ip
