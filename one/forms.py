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
    birth_year = SelectField('연도', choices=[], validate_choice=False, validators=[DataRequired()])
    birth_month = SelectField('월', choices=[], validate_choice=False, validators=[DataRequired()])
    birth_day = SelectField('일', choices=[], validate_choice=False, validators=[DataRequired()])

    # 성별
    gender = RadioField(
        '성별',
        choices=[('M', '남자'), ('F', '여자')],
        validators=[DataRequired()]
    )

class FindIdForm(FlaskForm):
    name = StringField('이름', validators=[DataRequired()])
    phone = StringField('휴대전화', validators=[DataRequired()])

class ResetPasswordForm(FlaskForm):
    email = StringField('이메일', validators=[DataRequired(), Email()])
    user_id = StringField('아이디', validators=[DataRequired()])

    password1 = PasswordField('새 비밀번호', validators=[DataRequired()])
    password2 = PasswordField(
        '비밀번호 확인',
        validators=[DataRequired(), EqualTo('password1')]
    )