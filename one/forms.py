from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo


class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])


class UserCreateForm(FlaskForm):
    # 기본 정보
    name = StringField('이름', validators=[DataRequired()])
    email = StringField('이메일', validators=[DataRequired(), Email()])
    phone = StringField('휴대전화', validators=[DataRequired()])

    # 비밀번호
    password1 = PasswordField('비밀번호', validators=[DataRequired()])
    password2 = PasswordField(
        '비밀번호 확인',
        validators=[DataRequired(), EqualTo('password1')]
    )

    # 생년월일
    birth_year = SelectField('연도', choices=[], validators=[DataRequired()])
    birth_month = SelectField('월', choices=[], validators=[DataRequired()])
    birth_day = SelectField('일', choices=[], validators=[DataRequired()])

    # 성별
    gender = RadioField(
        '성별',
        choices=[('M', '남자'), ('F', '여자')],
        validators=[DataRequired()]
    )
