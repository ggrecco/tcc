from flask import render_template
from app.models import Dados, Servidor


def listarServivor(dados, tamanho, user):
    servidores = Servidor.query.filter_by(usuario_id=user)
    for servidor in servidores:
        dado = Dados.query.filter_by(usuario_id=user,
                                     servidor_id=servidor.id)
        lista = []
        d = {}
        k = 0
        i = 0
        verde = 0
        amarelo = 0
        laranja = 0
        vermelho = 0
        tverde = 0
        tamarelo = 0
        tlaranja = 0
        tvermelho = 0
        while i < len(list(dado)):
            if dado[i].check == '0':
                k = k + 1
                if dado[i].nota < 4:
                    verde = verde + 1
                elif dado[i].nota >= 4 and dado[i].nota < 7:
                    amarelo = amarelo + 1
                elif dado[i].nota >= 7 and dado[i].nota < 9:
                    laranja = laranja + 1
                else:
                    vermelho = vermelho + 1
            else:
                pass
            i = i + 1
        j = 0
        while j < len(list(dado)):
            if dado[j].nota < 4:
                tverde = tverde + 1
            elif dado[j].nota >= 4 and dado[j].nota < 7:
                tamarelo = tamarelo + 1
            elif dado[j].nota >= 7 and dado[j].nota < 9:
                tlaranja = tlaranja + 1
            else:
                tvermelho = tvermelho + 1
            j = j + 1
        d[servidor.nome] = {'verde': verde, 'amarelo': amarelo,
                            'tverde': tverde, 'tamarelo': tamarelo,
                            'laranja': laranja, 'vermelho': vermelho,
                            'tlaranja': tlaranja, 'tvermelho': tvermelho}
        lista.append(k)
    return render_template('ver_servidor.html', title='Perfil de usuário',
                           dados=dados, servidores=servidores,
                           tamanho=tamanho, lista=lista,
                           dici=d)
