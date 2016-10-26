#coding:utf-8
"""
question表相关资源请求处理
"""
from flask import jsonify,request,url_for

from app import db
from app.models import Question
from . import api

@api.route('/questions')
def get_questions():
    """获取题库题目列表"""
    question_list = Question.query.all()
    return jsonify({'questions':[question.to_json() for question in question_list]})

@api.route('/question/<int:id>')
def get_question(id):
    """获取单篇文章"""
    question = Question.query.get_or_404(id)
    return jsonify({question.to_json()})

@api.route('/question',methods=['POST'])
def new_question():
    """新增题目"""
    question = Question.from_json(request.json)
    db.session.add(question)
    db.session.commit()
    return jsonify(question.to_json()),201,\
           {'Location':url_for('api.get_question',id=question.id,_external=True)}

@api.route('/question/<int:id>')
def edit_question(id):
    """修改、更新题目"""
    question = Question.query.get_or_404(id)
    question.title = request.json.get('title',question.title) # 如果title不存在,默认值为question.title
    question.choices = request.json.get('choices',question.choices)
    question.answer_right = request.json.get('answer_right',
                                             question.answer_right)
    question.answer_description = request.json.get('answer_description',
                                                   question.answer_description)
    db.session.add(question)
    db.session.commit()