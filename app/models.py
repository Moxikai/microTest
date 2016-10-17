#coding:utf-8
"""
数据模型
"""
from app import db

class Question(db.Model):
    """测试题目模型"""
    __tablename__ = 'questions'

    id = db.Column(db.Integer,primary_key=True) # 试题id
    title = db.Column(db.Text) # 题目，试题描述
    type = db.Column(db.String(32)) # 题目类型
    choices = db.Column(db.Text) # 试题选项，以换行符分隔
    score_right = db.Column(db.Integer,index=True) # 标准得分
    answer_right = db.Column(db.String(32),index=True) # 答案
    answer_description = db.Column(db.Text) # 答案解析
    answer_list = db.relationship('Answer',backref="question") # 定义反向关系

class Answer(db.Model):
    """答题"""
    __tablename__ = 'answers'

    id = db.Column(db.Integer,primary_key=True) # 答题
    order_id = db.Column(db.Integer,index=True) # 显示题号
    answer = db.Column(db.String(32),index=True) # 答案
    is_right = db.Column(db.Boolean,index=True) # 是否正确
    score = db.Column(db.Integer,index=True) # 得分
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))  # 外键，题目id
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 外键，人员id

class User(db.Model):
    """用户"""
    __tablename__ = 'users'

    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(128),index=True,unique=True) # 用户名
    phone = db.Column(db.String(11),index=True,unique=True) # 用户手机号
    scores = db.Column(db.Integer,index=True) # 总得分
    answer_list = db.relationship('Answer',backref='question') # 定义反向关系




