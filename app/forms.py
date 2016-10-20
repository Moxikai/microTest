#coding:utf-8
"""
表单模型
"""
from flask_wtf import Form
from wtforms import StringField,SubmitField,SelectField,HiddenField,RadioField,TextAreaField,IntegerField
from wtforms.validators import DataRequired,Length,ValidationError

from .models import User,Answer

class RegisterForm(Form):
    """注册表单"""
    username = StringField('昵称',validators=[DataRequired()]) # 用户名，昵称
    submit = SubmitField('提交')

    def validate_username(self,field):
        """验证用户名、微信号是否重复"""
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('微信号已注册')


class AnswerForm(Form):
    """答题表单"""

    id = HiddenField() # 答题id
    answer_choice = RadioField(u'答案') # 单选项
    submit = SubmitField('下一题')


class QuestionForm(Form):
    """试题提交表单"""
    title = TextAreaField('题目描述',validators=[DataRequired()])
    choices_A = TextAreaField('A.',validators=[DataRequired()])
    choices_B = TextAreaField('B.',validators=[DataRequired()])
    choices_C = TextAreaField('C.')
    choices_D = TextAreaField('D.')
    score_right = IntegerField('满分')
    answer_right = SelectField(label='答案',
                              validators=[DataRequired()],
                              choices=[('A','A'),('B','B'),('C','C'),('D','D')])
    answer_description = TextAreaField('答案解析',validators=[DataRequired()])
    submit = SubmitField('提交')




