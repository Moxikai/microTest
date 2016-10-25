#coding:utf-8
"""
main蓝本视图
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time

from flask import redirect,url_for,render_template,request,current_app,flash,session
from flask_login import login_required
from .. import db
from . import main
from ..forms import AnswerForm,RegisterForm,QuestionForm
from ..models import Answer,Question,User,Permission,Test
from ..decorators import permission_required,admin_required

@main.teardown_request
def teardown_request(func):
    """请求结束后关闭数据库连结，解决sae平台连结问题"""
    db.session.close()

@main.route('/welcome',methods=['GET','POST'])
@login_required
def welcome():
    """欢迎页，游客首页"""

    return render_template('welcome.html')


@main.route('/create_questions/<int:user_id>')
@login_required
def start_test(user_id):
    """创建随机题目"""
    user = User.query.get_or_404(user_id)
    test = Test(user_id=user.id)
    db.session.add(test)
    db.session.commit()


@main.route('/answer/user/<int:user_id>',methods=['GET','POST'])
@login_required
def answer(user_id):
    """答题视图"""
    user = User.query.get_or_404(user_id)  # 查询用户
    print '进入答题页面,当前用户是----------------%s------------------'%(user.username)
    form = AnswerForm()
    page = request.args.get('page')
    page = int(page) if page else 1
    """处理页码,防止回退修改答案"""
    if ('prev_page' not in session and page == 1) or \
            ('pre_page' in session and int(session['prev_page']) <= page):

        if request.method == 'POST':
            """处理提交数据"""
            answer = Answer.query.filter(Answer.id==request.form['id']).first()
            answer.answer = request.form['answer_choice']
            db.session.add(answer)
            db.session.commit()
            session['prev_page'] = page # 设置前一页码
            if page < current_app.config['QUESTION_COUNT']:
                return redirect(url_for('main.answer',page=page+1,user_id=user_id))
            else:
                return redirect(url_for('main.result',user_id=user_id)) # 最后一道题目提交后

        try:
            pagination = Answer.query.filter(Answer.user_id==user_id).order_by(Answer.order_id.asc()).paginate(page,
                                                                                                               current_app.config['ANSWERS_PER_PAGE'],False)

            answer = pagination.items[0]
            count = Answer.query.filter(Answer.user_id==user_id).count()
            print '本次测试题目:------------------%s个----------------'%(count)
            """初始化部分表单"""
            form.id.data = answer.id
            form.answer_choice.choices = answer.question.transStrToList()
            if answer.answer:
                form.answer_choice.data = answer.answer
            return render_template('answer2.html',
                                   page=page,
                                   user=user,
                                   answer=answer,
                                   count=count,
                                   form=form)
        except Exception as e:
                return '出错了,%s'%e
    else:
        return '对不起,不允许返回上一题'


@main.route('/question/add',methods=['GET','POST'])
@permission_required(Permission.WRITE_QUESTION)
@login_required
def question_add():
    """临时视图，新增试题"""
    form = QuestionForm()
    if form.validate_on_submit():
        """处理post"""
        try:
            choice_list=[('A',form.choices_A.data),('B',form.choices_B.data),
                         ('C',form.choices_C.data),('D',form.choices_D.data)]
            choice = ';'.join(item[0]+'.'+item[1] for item in choice_list if item[1])

            new_question = Question(title=form.title.data,
                                    choices=choice,
                                    score_right=form.score_right.data,
                                    answer_right=form.answer_right.data,
                                    answer_description=form.answer_description.data,
                                    )
            db.session.add(new_question)
            db.session.commit()

            flash('题目%s已保存'%(form.title.data))
            return redirect(url_for('main.question_add'))
        except TypeError:
            return '<p>choices:%s</p>'%(form.choices_A.data)

    return render_template('question_add2.html',form=form)


@main.route('/question/edit/<int:id>',methods=['GET','POST'])
@permission_required(Permission.WRITE_QUESTION)
@login_required
def question_edit(id):
    """题目修改"""
    question = Question.query.get_or_404(id)
    form = QuestionForm()
    if request.method == 'POST':
        form_ = request.form
        choice_list = [('A', form_['choices_A']),('B', form_['choices_B']),
                       ('C', form_['choices_C']),('D', form_['choices_D'])]
        choice_str = ';'.join(item[0] + '.' + item[1] for item in choice_list if item[1])

        question.choices = choice_str
        question.title = form_['title']
        question.score_right = form_['score_right']
        question.answer_right = form_['answer_right']
        question.answer_description = form_['answer_description']
        db.session.add(question)
        db.session.commit()

        return redirect(url_for('main.question'))

    form.title.data = question.title
    choice_list = question.transStrToList()
    for item in choice_list:
        if item[0] == 'A':
            form.choices_A.data = item[1]
        elif item[0] == 'B':
            form.choices_B.data = item[1]
        elif item[0] == 'C':
            form.choices_C.data = item[1]
        elif item[0] == 'D':
            form.choices_D.data = item[1]

    form.answer_right.data = question.answer_right
    form.score_right.data = question.score_right
    form.answer_right.data = question.answer_description

    return render_template('question_add2.html',form=form)

@main.route('/question',methods=['GET','POST'])
@permission_required(Permission.WRITE_QUESTION)
@login_required
def question():
    """题库题目列表"""
    page = request.args.get('page')
    page = int(page) if page else 1
    questions = Question.query
    pagination = questions.paginate(page,
                                         current_app.config['QUESTIONS_PER_PAGE'],False)
    question_list = pagination.items
    count = questions.count()
    return render_template('question_list.html',
                           count=count,
                           pagination=pagination,
                           question_list=question_list)

@main.route('/question/delete/<int:id>')
@permission_required(Permission.ADMIN)
@login_required
def question_delete(id):
    """删除题目"""
    question = Question.query.get_or_404(id)
    db.session.delete(question)
    db.session.commit()

    flash('序号为%s的题目删除成功！'%(id))
    return redirect(url_for('main.question'))


@main.route('/retest/<int:user_id>')
@permission_required(Permission.ADMIN)
@login_required
def retest(user_id):
    """重新测试，仅用于测试"""
    user = User.query.get_or_404(user_id)
    user.deleteQuestions()
    return redirect(url_for('main.answer',user_id=user_id))


@main.route('/result/<int:user_id>')
@login_required
def result(user_id):
    """完成测试"""
    end_time = time.time()
    user = User.query.filter(User.id==user_id).first()
    if user.is_completed:
        user.is_finished = True # 更新完成标记
        user.end_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(end_time))
        db.session.add(user)
        db.session.commit()

        """计算测试时间"""
        spend_time = user.calculate_spend_time()
        """计算总得分"""
        scores = user.calculate_scores()
        scores_right = user.calculate_scores_right() # 计算标准得分
        flash('您已成功提交测验，请查看本次测验结果')
        return  render_template('result.html',
                                scores=scores,
                                scores_right=scores_right,
                                spend_time=spend_time,
                                user_id=user_id)
    else:
        flash('还有题目没有做完，请检查！')
        return redirect(url_for('main.answer',user_id=user_id))

@main.route('/result/<int:user_id>/detail')
@permission_required(Permission.READ_RESULTS)
@login_required
def result_detail(user_id):
    """答案解析"""
    user = User.query.get_or_404(user_id)
    return render_template('result_detail.html',user=user)


















