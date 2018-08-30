import requests
from requests import post, get
from bs4 import BeautifulSoup as bs


def busca_tabelas(linguagem):
    url = "https://www.cvedetails.com/vulnerability-search.php"

    payload = {'bidno': '',
               'cveid': '',
               'cvssscoremax': '',
               'cvssscoremin': '',
               'cweid': '',
               'f': '1',
               'msid': '',
               'pem': '',
               'pey': '',
               'product': linguagem,
               'psm': '',
               'psy': '',
               'uem': '',
               'uey': '',
               'usm': '',
               'usy': '',
               'vendor': ''}

    response = requests.post(url, data=payload)

    pagina = bs(response.content, 'lxml')

    return pagina
