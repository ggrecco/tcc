from flask import render_template, flash, redirect, url_for, request, g, json
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.models import Usuario, Servidor, Dados
from app import app, db
from app.forms import LoginForm, RegistrationForm, \
        ServidorForm, EditProfileForm, DeletarForm, \
        AlteraServidorForm, NotaServidorForm
from app.portscan import busca_ip
from celeryF import *
from datetime import datetime
import unidecode
from flask_babel import get_locale
from flask_weasyprint import HTML, render_pdf


# atualiza data de ações, traduz conforme local
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


# página inicial
@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')


@app.route('/qr', methods=['GET', 'POST'])
def qr():
    return render_template('qr.html', title='Código QR')


# página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = unidecode.unidecode(form.username.data)
        usuario = Usuario.query.filter_by(nome=username).first()
        if usuario is None or not usuario.check_password(form.password.data):
            flash('Usuário ou Senha Inválido, tente novamente.')
            return redirect(url_for('login'))
            login_user(usuario, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
        login_user(usuario, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Entrar', form=form)


# logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# cadastro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        username = unidecode.unidecode(form.username.data)
        if username.isalpha():
            user = Usuario(nome=username, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Parabéns, você foi registrado com suceso!')
            return redirect(url_for('login'))
        flash('Por favor, não utilize caractéres especiais como "/ $ #" ' +
              'ou palavras acentuádas.')
    return render_template('register.html', title='Registro', form=form)


# edição de perfil
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.nome = unidecode.unidecode(form.username.data)
        current_user.email = form.email.data
        db.session.commit()
        flash('Suas alterações foram salvas(e automaticamente removido as ' +
              'acentuações ;) )')
        return redirect(url_for('index'))
    elif request.method == 'GET':
        # busca do banco os dados para exibir ao usuário o que está salvo
        form.username.data = current_user.nome
        form.email.data = current_user.email
    return render_template('editar.html', title='Editar Perfil', form=form)


# exclusão de perfil
@app.route("/deletar", methods=['GET', 'POST'])
@login_required
def deletar():
    form = DeletarForm()
    if form.validate_on_submit():
        user_id = current_user.id
        u = Usuario.query.filter_by(id=user_id).first()
        d = Dados.query.filter_by(usuario_id=user_id)
        s = Servidor.query.filter_by(usuario_id=user_id)
        d.delete()
        s.delete()
        db.session.delete(u)
        db.session.commit()
        return redirect(url_for('logout'))
    return render_template('deletar.html', title='Deletar usuario',
                           form=form)


# perfil do usuário
@app.route('/usuario/<username>')
@login_required
def user(username):
    user = Usuario.query.filter_by(nome=username).first_or_404()
    dados = Dados.query.filter_by(usuario_id=current_user.id)
    servidores = Servidor.query.filter_by(usuario_id=current_user.id)
    return render_template('user.html', title='Perfil de usuário',
                           user=user, dados=dados, servidores=servidores)


# Pesquisar servidor
@app.route('/servidor', methods=['GET', 'POST'])
@login_required
def servidor():
    form = ServidorForm()
    if form.validate_on_submit():
        flash('O servidor foi registrado,alguarde alguns ' +
              'minutos antes de consultar.')
        u = Usuario.query.filter_by(id=current_user.id).first()
        p = busca_ip(form.url.data)
        s = Servidor(nome=form.servidor.data, url=form.url.data,
                     ip=p, rel_usuario=u)
        db.session.add(s)
        db.session.commit()
        url = form.url.data
        user = current_user.id
        scaneando.delay(url, user)
        return redirect(url_for('index'))
    return render_template('servidor.html', title='Pesquisar servidor',
                           form=form)


# refazer analise
@app.route('/refazer_<nome>_<url>_<ip>_<user>', methods=['GET', 'POST'])
@login_required
def refazer(nome, url, ip, user):
    i = 0
    flash('Refazendo teste, alguarde alguns minutos antes de consultar.')
    s = Servidor.query.filter_by(nome=nome, url=url, ip=ip)
    result = scaneando.delay(url, user)
    return redirect(url_for('index'))


# botão visualizar dados escaneados
@app.route('/dados_<nome>', methods=['GET', 'POST'])
@login_required
def dados(nome):
    servidores = Servidor.query.filter_by(usuario_id=current_user.id,
                                          nome=nome)
    servidor_id = servidores.value('id')
    dados = Dados.query.filter_by(usuario_id=current_user.id,
                                  servidor_id=servidor_id)
    return render_template('dados_servidores.html', title='Vulnerabilidades',
                           dados=dados, servidores=servidores)


# detalhes da vulnerabilidade
@app.route('/vul_<cveid>_<nome>', methods=['GET', 'POST'])
@login_required
def vul(cveid, nome):
    servidores = Servidor.query.filter_by(usuario_id=current_user.id,
                                          nome=nome)
    servidor_id = servidores.value('id')
    dados = Dados.query.filter_by(cveid=cveid, servidor_id=servidor_id)
    return render_template('vul.html', title='Detalhes', dados=dados)


# servidores pesqusiados
@app.route('/ver_servidor<username>', methods=['GET', 'POST'])
@login_required
def ver_servidor(username):
    lista = []
    d = {}
    dados = Dados.query.filter_by(usuario_id=current_user.id)
    tamanho = len(list(dados))
    servidores = Servidor.query.filter_by(usuario_id=current_user.id)
    for servidor in servidores:
        dados_servidor = Dados.query.filter_by(usuario_id=current_user.id,
                                               servidor_id=servidor.id)
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
        while i < len(list(dados_servidor)):
            if dados_servidor[i].check == '0':
                k = k + 1
                if dados_servidor[i].nota < 4:
                    verde = verde + 1
                elif dados_servidor[i].nota >= 4 and dados_servidor[i].nota < 7:
                    amarelo = amarelo + 1
                elif dados_servidor[i].nota >= 7 and dados_servidor[i].nota < 9:
                    laranja = laranja + 1
                else:
                    vermelho = vermelho + 1
            else:
                pass
            i = i + 1

        j = 0
        while j < len(list(dados_servidor)):
            if dados_servidor[j].nota < 4:
                tverde = tverde + 1
            elif dados_servidor[j].nota >= 4 and dados_servidor[j].nota < 7:
                tamarelo = tamarelo + 1
            elif dados_servidor[j].nota >= 7 and dados_servidor[j].nota < 9:
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


#  deletar servidor
@app.route("/deleta_servidor<server><serverid>", methods=['GET', 'POST'])
@login_required
def deleta_servidor(server, serverid):
    form = DeletarForm()
    if form.validate_on_submit():
        user_id = current_user.id
        d = Dados.query.filter_by(usuario_id=user_id, servidor_id=serverid)
        s = Servidor.query.filter_by(usuario_id=user_id, nome=server)
        d.delete()
        s.delete()
        db.session.commit()
        flash('Alterações realizadas com sucesso.')
        return redirect(url_for('index'))
    return render_template('deleta_servidor.html', title='Excluir',
                           form=form, servidor=server)


# alterar servidor
@app.route("/altera_servidor<server><serverid>", methods=['GET', 'POST'])
@login_required
def altera_servidor(server, serverid):
    form = AlteraServidorForm()
    user_id = current_user.id
    servidor = Servidor.query.filter_by(nome=server,
                                        usuario_id=user_id)

    if form.validate_on_submit():
        servidor[0].nome = form.servidor.data
        db.session.commit()
        flash('Atualizado com sucesso')
        return redirect(url_for('index'))

    elif request.method == 'GET':
        form.servidor.data = servidor.value('nome')
    return render_template('altera_servidor.html',
                           title='Alterar Servidor', form=form)


@app.route('/baseimprimir')
@login_required
def baseimprimir():
    servidores = Servidor.query.filter_by(usuario_id=current_user.id,
                                          nome=servidor)
    return render_template('baseimp.html')


# imprime todos os dados em pdf
@app.route('/imprimir_todos/<nome>.pdf')
@login_required
def imprimir_todos(nome):
    servidores = Servidor.query.filter_by(usuario_id=current_user.id,
                                          nome=nome)
    servidor_id = servidores.value('id')
    dados = Dados.query.filter_by(usuario_id=current_user.id,
                                  servidor_id=servidor_id)
    html = render_template('imprimir_todos.html', title='Vulnerabilidades',
                           dados=dados, servidores=servidores)
    return render_pdf(HTML(string=html))


# imprime todos os checkbox
@app.route('/imprimir_todos_checkbox/<nome>.pdf')
@login_required
def imprimir_todos_checkbox(nome):
    servidores = Servidor.query.filter_by(usuario_id=current_user.id,
                                          nome=nome)
    servidor_id = servidores.value('id')
    dados = Dados.query.filter_by(usuario_id=current_user.id,
                                  servidor_id=servidor_id)
    html = render_template('imprimir_todos_checkbox.html',
                           title='Vulnerabilidades',
                           dados=dados, servidores=servidores)
    return render_pdf(HTML(string=html))


# imprimir por faixa de valores
@app.route('/imprimir_faixa/<nome>', methods=['GET', 'POST'])
@login_required
def selecionar_faixa_imprimir(nome):
    form = NotaServidorForm()
    servidores = Servidor.query.filter_by(usuario_id=current_user.id,
                                          nome=nome)
    if form.validate_on_submit():
        minimo = float(form.minimo.data)
        maximo = float(form.maximo.data)
        if minimo <= maximo and minimo >= 1 and maximo <= 10:
            return render_template('confirma_faixa.html', nome=nome,
                                   minimo=minimo, maximo=maximo,
                                   servidores=servidores)
        flash('- O valor mínimo deve ser maior que 1')
        flash('- Mínimo deve ser menor que o valor máximo.')
        flash('- Valor máximo não pode ser superior a 10.0')
        return render_template('imprimir_faixa.html', servidores=servidores,
                               form=form)
    return render_template('imprimir_faixa.html', servidores=servidores,
                           form=form)


# confirma impressão por faixas
@app.route("/confirma/<minimo>/<maximo>/<nome>", methods=['GET', 'POST'])
def confirma(minimo, maximo, nome):
    servidores = Servidor.query.filter_by(usuario_id=current_user.id,
                                          nome=nome)
    servidor_id = servidores.value('id')
    dados = Dados.query.filter_by(usuario_id=current_user.id,
                                  servidor_id=servidor_id)
    html = render_template('impressao_faixa.html',
                           minimo=float(minimo), maximo=float(maximo),
                           dados=dados, servidores=servidores)
    return render_pdf(HTML(string=html))


# marcar todos os checkboxes
@app.route("/marca_todos<servidor><selecao>", methods=['GET', 'POST'])
@login_required
def marcaTodos(servidor, selecao):
    servidores = Servidor.query.filter_by(usuario_id=current_user.id,
                                          nome=servidor)
    dados = Dados.query.filter_by(usuario_id=current_user.id,
                                  servidor_id=servidores.value('id'))
    i = 0
    if selecao == '1':
        while i < len(list(dados)):
            dados[i].check = '1'
            i = i + 1
    elif selecao == '2':
        while i < len(list(dados)):
            if dados[i].check == '1':
                dados[i].check = '0'
            else:
                dados[i].check = '1'
            i = i + 1
    else:
        while i < len(list(dados)):
            dados[i].check = '0'
            i = i + 1
    db.session.commit()
    return render_template('dados_servidores.html', title='Home',
                           servidores=servidores, dados=dados)


# marcar um checkbox
@app.route("/marcas_<cveid>_<servidor>", methods=['GET', 'POST'])
@login_required
def marcas(cveid, servidor):
    servidores = Servidor.query.filter_by(usuario_id=current_user.id,
                                          nome=servidor)
    dados = Dados.query.filter_by(cveid=cveid,
                                  servidor_id=servidores.value('id'))
    if dados[0].check != '1':
        dados[0].check = '1'
        db.session.commit()
        flash('Marcado {}'.format(cveid))
    else:
        dados[0].check = '0'
        db.session.commit()
        flash('Desmarcado {}'.format(cveid))

    dados = Dados.query.filter_by(usuario_id=current_user.id,
                                  servidor_id=servidores.value('id'))
    return render_template('dados_servidores.html', title='Home',
                           servidores=servidores, dados=dados)


# quantidade de Notas
@app.route("/quantidadeNotas<nome>", methods=['GET', 'POST'])
@login_required
def quantidadeNotas(nome):
    servidores = Servidor.query.filter_by(usuario_id=current_user.id,
                                          nome=nome)
    dados = Dados.query.filter_by(usuario_id=current_user.id,
                                  servidor_id=servidores.value('id'))
    site = servidores[0].url
    ip = servidores[0].ip
    verde = 0
    amarelo = 0
    laranja = 0
    vermelho = 0
    tverde = 0
    tamarelo = 0
    tlaranja = 0
    tvermelho = 0
    i = 0
    while i < len(list(dados)):
        if dados[i].check == '0':
            if dados[i].nota < 4:
                verde = verde + 1
                tverde = tverde + 1
            elif dados[i].nota >= 4 and dados[i].nota < 7:
                amarelo = amarelo + 1
                tamarelo = tamarelo + 1
            elif dados[i].nota >= 7 and dados[i].nota < 9:
                laranja = laranja + 1
                tlaranja = tlaranja + 1
            else:
                vermelho = vermelho + 1
                tvermelho = tvermelho + 1
        else:
            if dados[i].nota < 4:
                tverde = tverde + 1
            elif dados[i].nota >= 4 and dados[i].nota < 7:
                tamarelo = tamarelo + 1
            elif dados[i].nota >= 7 and dados[i].nota < 9:
                tlaranja = tlaranja + 1
            else:
                tvermelho = tvermelho + 1
        i = i + 1
    # j = 0
    # while j < len(list(dados)):
    #     if dados[j].nota < 4:
    #         tverde = tverde + 1
    #     elif dados[j].nota >= 4 and dados[j].nota < 7:
    #         tamarelo = tamarelo + 1
    #     elif dados[j].nota >= 7 and dados[j].nota < 9:
    #         tlaranja = tlaranja + 1
    #     else:
    #         tvermelho = tvermelho + 1
    #     j = j + 1

    html = render_template('quantidadeNotas.html', nome=nome, site=site,
                           verde=verde, amarelo=amarelo, laranja=laranja,
                           vermelho=vermelho, tverde=tverde, tamarelo=tamarelo,
                           tlaranja=tlaranja, tvermelho=tvermelho, ip=ip)
    return render_pdf(HTML(string=html))


@app.route("/grafo<nome>", methods=['GET', 'POST'])
@login_required
def grafo(nome):
    servidores = Servidor.query.filter_by(usuario_id=current_user.id,
                                          nome=nome)
    dados = Dados.query.filter_by(usuario_id=current_user.id,
                                  servidor_id=servidores.value('id'))
    lista = []
    dicionario = {}
    verde = 0
    amarelo = 0
    laranja = 0
    vermelho = 0
    tverde = 0
    tamarelo = 0
    tlaranja = 0
    tvermelho = 0
    i = 0
    while i < len(list(dados)):
        if dados[i].check == '0':
            if dados[i].nota < 4:
                verde = verde + 1
                tverde = tverde + 1
            elif dados[i].nota >= 4 and dados[i].nota < 7:
                amarelo = amarelo + 1
                tamarelo = tamarelo + 1
            elif dados[i].nota >= 7 and dados[i].nota < 9:
                laranja = laranja + 1
                tlaranja = tlaranja + 1
            else:
                vermelho = vermelho + 1
                tvermelho = tvermelho + 1
        else:
            if dados[i].nota < 4:
                tverde = tverde + 1
            elif dados[i].nota >= 4 and dados[i].nota < 7:
                tamarelo = tamarelo + 1
            elif dados[i].nota >= 7 and dados[i].nota < 9:
                tlaranja = tlaranja + 1
            else:
                tvermelho = tvermelho + 1
        i = i + 1
    #
    # dicionario["COR"] = "Verde"
    # dicionario["NOTA"] = verde
    # dicionario["TNOTA"] = tverde
    # lista.append(dicionario)
    # dicionario = {}
    # dicionario["COR"] = "Amarelo"
    # dicionario["NOTA"] = amarelo
    # dicionario["TNOTA"] = tamarelo
    # lista.append(dicionario)
    # dicionario = {}
    # dicionario["COR"] = "Laranja"
    # dicionario["NOTA"] = laranja
    # dicionario["TNOTA"] = tlaranja
    # lista.append(dicionario)
    # dicionario = {}
    # dicionario["COR"] = "Vermelho"
    # dicionario["NOTA"] = vermelho
    # dicionario["TNOTA"] = tvermelho
    # lista.append(dicionario)
    # dicionario = {}

    # return render_template("grafo.html", dados=json.dumps(lista), nome=nome)
    return render_template("grafo2.html", nome=nome,
                           verde=verde, amarelo=amarelo,
                           laranja=laranja,  vermelho=vermelho,
                           tverde=tverde, tamarelo=tamarelo,
                           tlaranja=tlaranja, tvermelho=tvermelho)
