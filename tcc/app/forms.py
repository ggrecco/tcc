from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import Usuario, Servidor
from flask_login import current_user


class RegistrationForm(FlaskForm):
    username = StringField('Usuario:', validators=[DataRequired()])
    email = StringField('Email:', validators=[DataRequired(), Email()])
    password = PasswordField('Senha:', validators=[DataRequired()])
    password2 = PasswordField('Repita a senha:',
                              validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')

    def validate_username(self, username):
        user = Usuario.query.filter_by(nome=username.data).first()
        if user is not None:
            raise ValidationError('Indisponível, por favor ' +
                                  ' use outro nome de usuário.')

            def validate_email(self, email):
                user = Usuario.query.filter_by(email=email.data).first()
                if user is not None:
                    raise ValidationError('Já cadastrado,' +
                                          ' por favor use outro e-mail.')


class DeletarForm(FlaskForm):
    submit = SubmitField('Deletar')


class LoginForm(FlaskForm):
    username = StringField('Usuário:', validators=[DataRequired()])
    password = PasswordField('Senha:', validators=[DataRequired()])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')


class EditProfileForm(FlaskForm):
    username = StringField('Nome de Usuario:', validators=[DataRequired()])
    email = StringField('E-mail:', validators=[DataRequired()])
    email2 = StringField('Repita o e-mail:', validators=[DataRequired(),
                                                        EqualTo('email')])
    submit = SubmitField('alterar')


class ScrapyForm(FlaskForm):
    linguagem = StringField('Linguagem:', validators=[DataRequired()])
    submit = SubmitField('Pesquisar')


class ServidorForm(FlaskForm):
    servidor = StringField('Nome para o servidor:',
                           validators=[DataRequired()])
    url = StringField('Url / IP (site do servidor):',
                      validators=[DataRequired()])
    registro = SubmitField('Pesquisar')

    def validate_servidor(self, servidor):
        servidor = Servidor.query.filter_by(nome=servidor.data).first()
        if servidor is not None:
            raise ValidationError('Indisponível, por favor ' +
                                  ' use outro nome para seu servidor.')

    def validate_url(self, url):
        url = Servidor.query.filter_by(url=url.data,
                                       usuario_id=current_user.id).first()
        if url is not None:
            raise ValidationError('Site já cadastrado.')


class AlteraServidorForm(FlaskForm):
    servidor = StringField('Novo nome para o servidor',
                           validators=[DataRequired()])
    submit = SubmitField('alterar')


class NotaServidorForm(FlaskForm):
    minimo = StringField('Mínimo: ',
                         render_kw={"value": "1"},
                         validators=[DataRequired()])
    maximo = StringField('Máximo: ', render_kw={"value": "10"},
                         validators=[DataRequired()])
    submit = SubmitField('Filtrar', render_kw={"onclick": "clickLoad()"})
