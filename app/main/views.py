#coding:utf-8
"""
main蓝本视图
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time

from flask import redirect,url_for,render_template,request,current_app,\
    flash,session,abort
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
    if user.create_test():
        """测试项创建成功"""
        running_test = Test.query.filter_by(finished=False).first() # 获取测试对象
        if running_test.create_questions():
            """测试题目创建成功"""
            return redirect(url_for('main.answer',user_id=user_id))
        else:
            db.session.delete(running_test)
            db.session.commit() # 删除测试项
            flash('未测试题目数量不满足要求，请联系管理员')
            return abort(500)
    else:
        flash('挑战机会不足，分享链接可以增加机会哦')
        return '<h1>管理员，这里转向个人资料页面</h1>'


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
            ('pre_page' in session and int(session['prev_page']) < page):

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
            obj = Answer.query.filter(Answer.user_id==user_id)
            pagination = obj.order_by(Answer.order_id.asc()).\
                paginate(page,current_app.config['ANSWERS_PER_PAGE'],False)
            count = obj.count()
            print '本次测试题目:------------------%s个----------------' % (count)
            answer = pagination.items[0]

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
            flash('对不起，内部错误：%s'%e)
            return abort(500)
    else:
        flash('对不起，不支持返回上一题')
        return abort(403)


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


@main.route('/compelete')
@login_required
def compelete(user_id):
    """提交测试"""
    user = User.query.filter_by(id=user_id).first() # 加载用户
    running_test = Test.query.filter_by(user_id=user_id).\
        filter_by(finished=False).first() # 加载当前运行测试
    if not running_test is None:
        """提交测试"""

        running_test.end_time = time.time()
        running_test.finished = True

        db.session.add(running_test)
        db.session.commit()
        """计算分数、时间"""
        if running_test.show_score != -1 and \
                        running_test.show_spend_time != -1:

            return '<h1>这里转到结果页面</h1>'
        else:
            flash('计算测试分数及时间失败！')
            return abort(500)
    else:
        flash('没有正在运行的测试，请管理员检查！')
        return abort(500)

@main.route('/result/<int:user_id>')
@login_required
def result(user_id):
    """查看测试结果"""





@main.route('/result/<int:user_id>/detail')
@permission_required(Permission.READ_RESULTS)
@login_required
def result_detail(user_id):
    """答案解析"""
    user = User.query.get_or_404(user_id)
    return render_template('result_detail.html',user=user)


















