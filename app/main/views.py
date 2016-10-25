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
            return redirect(url_for('main.answer',user_id=user_id,test_id=running_test.id))
        else:
            db.session.delete(running_test)
            db.session.commit() # 删除测试项
            flash('未测试题目数量不满足要求，请联系管理员')
            return abort(500)
    else:
        flash('挑战机会不足，分享链接可以增加机会哦')
        return redirect(url_for('main.result',user_id=user_id))


@main.route('/test/<int:test_id>',methods=['GET','POST'])
@login_required
def answer(test_id):
    """答题视图"""
    test = Test.query.get_or_404(test_id)
    print '进入答题页面,当前用户是----------------%s------------------'%(test.user.username)
    form = AnswerForm()
    page = request.args.get('page')
    page = int(page) if page else 1
    """处理页码,防止回退修改答案"""
    if ('prev_page' not in session and page == 1) or \
            ('prev_page' in session and int(session['prev_page']) < page):

        if request.method == 'POST':
            """处理提交数据"""
            answer = Answer.query.filter(Answer.id==request.form['id']).first()
            answer.answer = request.form['answer_choice']
            answer.score = answer.calculate_score() # 计算分数
            db.session.add(answer)
            db.session.commit()
            session['prev_page'] = page # 设置前一页码
            if page < current_app.config['QUESTIONS_COUNT_PER_TEST']:
                return redirect(url_for('main.answer',page=page+1,test_id=test_id))
            else:
                del session['prev_page'] # 清空，防止下次登陆时出错
                return redirect(url_for('main.compelete',test_id=test_id)) # 最后一道题目提交后

        try:
            obj = Answer.query.filter(Answer.test_id==test_id)
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
            start_time = time.localtime(test.start_time)
            return render_template('answer3.html',
                                   start_time=start_time,
                                   test=test,
                                   answer=answer,
                                   count=count,
                                   form=form)
        except Exception as e:
            flash('对不起，内部错误：%s'%e)
            return abort(500)
    else:
        flash('对不起，上一页是%s，当前页码是%s，不支持返回到上一页码'%(session['prev_page'],page))
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


@main.route('/compelete/<int:test_id>')
@login_required
def compelete(test_id):
    """提交测试"""
    running_test = Test.query.get_or_404(test_id)
    if not running_test is None:
        """提交测试"""
        running_test.end_time = time.time()
        running_test.finished = True

        db.session.add(running_test)
        db.session.commit()

        """已使用机会+1，剩余机会-1"""
        if running_test.user.use_chance:
            """计算分数、时间"""
            if running_test.show_score != -1 and \
                            running_test.show_spend_time != -1:

                return redirect(url_for('main.result',
                                        test_id=test_id,
                                        user_id=running_test.user.id))
            else:
                flash('计算测试分数及时间失败！')
                return abort(500)
        else:
            flash('闯关机会设置失败，请管理员检查数据！')
            return abort(500)


    else:
        flash('没有正在运行的测试，请管理员检查！')
        return abort(500)

@main.route('/result/<int:user_id>')
@login_required
def result(user_id):
    """查看测试结果"""
    user = User.query.get_or_404(user_id)
    test_id = request.args.get('test_id')
    if test_id:
        test = Test.query.get_or_404(int(test_id))
        return render_template('result.html',user=user,test=test)
    else:
        return render_template('result.html',user=user,test=None)


@main.route('/result/<int:user_id>/detail')
@permission_required(Permission.READ_RESULTS)
@login_required
def result_detail(user_id):
    """答案解析"""
    user = User.query.get_or_404(user_id)
    return render_template('result_detail.html',user=user)


















