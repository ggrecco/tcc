from requests import get
from app import db
from app.payload import busca_tabelas
from app.models import Dados, Usuario, Servidor
from flask_login import current_user


# retirar nota minima e máxima nas pesquisas
def scraper(procura, nome, porta, user):
    i = 0
    lista = []

    # captura o id do usuario logado
    u = Usuario.query.filter_by(id=user).first()
    s = Servidor.query.filter_by(nome=nome, usuario_id=user).first()

    tabelas = busca_tabelas(procura).findAll('tr', {'class': 'srrowns'})
    coment = busca_tabelas(procura).findAll('td', {'class': 'cvesummarylong'})

    while i < len(tabelas):
        coluna = tabelas[i].find_all('td')
        produto = coluna[2].text
        cveid = coluna[3].text
        tipo = coluna[6].text
        datacorrecao = coluna[8].text
        nota = coluna[9].text
        acesso = coluna[10].text
        comentario = coment[i].text.split('\t')[6]
        check = '0'
        if '\n\t' in tipo:
            tipo = tipo.split('\t')[6]
            d = Dados(autor_usuario=u, autor_servidor=s,
                      produto=produto, cveid=cveid, tipo=tipo,
                      datacorrecao=datacorrecao, nota=float(nota),
                      acesso=acesso, comentario=comentario, porta=porta,
                      check=check)
            db.session.add(d)
            db.session.commit()

        elif '\n' in tipo:
            tipo = tipo.split('\n')[0]
            d = Dados(autor_usuario=u, autor_servidor=s,
                      produto=produto, cveid=cveid, tipo=tipo,
                      datacorrecao=datacorrecao, nota=float(nota),
                      acesso=acesso, comentario=comentario, porta=porta,
                      check=check)
            db.session.add(d)
            db.session.commit()

        lista.append(produto)
        i = i + 1

    return lista
