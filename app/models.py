#coding:utf-8
"""
数据模型
"""
import random,hashlib,math,time,datetime

from werkzeug.security import generate_password_hash,check_password_hash
from flask import current_app
from flask_login import UserMixin,AnonymousUserMixin

from app import db
from . import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class Question(db.Model):
    """测试题目模型"""
    __tablename__ = 'questions'

    id = db.Column(db.Integer,primary_key=True) # 试题id
    title = db.Column(db.Text) # 题目，试题描述
    choices = db.Column(db.Text) # 试题选项，以换行符分隔
    score_right = db.Column(db.Integer,index=True) # 标准得分
    answer_right = db.Column(db.String(32),index=True) # 答案
    answer_description = db.Column(db.Text) # 答案解析
    answer_list = db.relationship('Answer',backref="question") # 定义反向关系

    def transStrToList(self):
        """单选项字符串转换成列表"""
        choice_list = self.choices.split(';')  # 注意是以英文下分号分隔
        choice_list = [(item.split('.')[0],item.split('.')[1]) for item in choice_list]
        return choice_list

    @staticmethod
    def transListToStr(*args):
        """单选项列表转换为字符串"""
        return ';'.join('.'.join(item) for item in args)

    @staticmethod
    def count():
        """返回整体试题数量"""
        total = Question.query.count()
        return total

    @staticmethod
    def is_meet_Min_count():
        """是否满足最低数量要求"""
        if Question.count() < current_app.config['QUESTIONS_COUNT_PER_TEST']:
            """"""
            return False
        else:
            return True

    @staticmethod
    def total_set():
        """返回所有题目对象集合"""
        total_questions = Question.query.all()
        return set(total_questions)




class Answer(db.Model):
    """答题"""
    __tablename__ = 'answers'

    id = db.Column(db.Integer,primary_key=True) # 答题
    order_id = db.Column(db.Integer,index=True) # 显示题号
    answer = db.Column(db.String(32),index=True) # 答案
    is_right = db.Column(db.Boolean,index=True,default=False) # 是否正确
    score = db.Column(db.Integer,index=True,default=0) # 得分
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))  # 外键，题目id
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'))  # 外键，测试id

    def calculate_score(self):
        """计算得分"""
        print '当前答案是：----------%s------------当前标准答案是：------------------%s'%(self.answer,self.question.answer_right)
        if self.answer == self.question.answer_right:
            self.score = self.question.score_right
        db.session.add(self)
        db.session.commit()


class Share(db.Model):
    """分享模型"""
    __tablename__ = 'shares'

    shared_id = db.Column(db.Integer,
                          db.ForeignKey('users.id'),
                          primary_key=True)
    accepted_id = db.Column(db.Integer,
                            db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime,default=datetime.datetime.utcnow)


class User(UserMixin,db.Model):
    """用户"""
    __tablename__ = 'users'

    id = db.Column(db.Integer,primary_key=True)
    open_id = db.Column(db.String(128),index=True) # 微信open_id
    nick_name = db.Column(db.String,index=True) # 微信昵称
    username = db.Column(db.String(128),index=True) # 用户名,用于密码登录方案
    email = db.Column(db.String(128),index=True) # 电子邮件,用于密码登录方案
    password_hash = db.Column(db.String(128)) # 密码签名,用于密码登录方案
    sex = db.Column(db.String(32),index=True) # 性别
    city = db.Column(db.String(32),index=True) # 城市
    province = db.Column(db.String(32),index=True) # 省
    test_list = db.relationship('Test',backref='user') # 定义反向关系
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    """分享和接受的自引用关系"""
    accepter_list = db.relationship('Share',
                               foreign_keys=[Share.shared_id],
                               backref=db.backref('sharer',lazy='joined'),
                               lazy='dynamic',
                               cascade='all,delete-orphan')
    sharer_list = db.relationship('Share',
                              foreign_keys=[Share.accepted_id],
                              backref=db.backref('accepter',lazy='joined'),
                              lazy='dynamic',
                              cascade='all,delete-orphan')
    chance_list = db.relationship('Chance',backref='user') # 定义反向关系

    def __init__(self,**kwargs):
        """初始化方法,定义默认角色"""
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMINISTRATOR_MAIL']:
                self.role = Role.query.filter_by(permissions=0xff).first() # 定义管理员
            else:
                self.role = Role.query.filter_by(default=True).first() # 定义普通用户


    @property
    def password(self):
        """密码属性"""
        raise AttributeError('不能直接读取密码')

    @password.setter
    def password(self,password):
        """设置密码,只写属性"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        """验证密码"""
        return check_password_hash(self.password_hash,password)

    @staticmethod
    def randomUserName():
        """为游客生成随机昵称,确保不重复"""
        username = random.randint(0, 10000000000)
        sha1 = hashlib.sha1()
        sha1.update(str(username))
        return sha1.hexdigest()

    def create_account(self,**kwargs):
        """创建账户"""
        if current_app.config['LOGIN_MODE'] == 0:
            """非微信验证模式下"""
            self.nick_name = self.randomUserName()
            db.session.add(self)
            db.session.commit()
        else:
            """微信验证模式下,获取用户基本信息"""
            pass

    def create_test(self):
        """创建测试项目"""
        if self.has_chance:
            """测试机会不为0"""
            new_test = Test(user_id=self.id,
                            start_time=time.time())
            db.session.add(new_test)
            db.session.commit()
            return True
        else:
            return False

    @property
    def has_finished_test(self):
        """检测是否有已完成的测试"""
        test_list = Test.query.filter_by(user_id=self.id).filter_by(finished=True).all()
        if test_list:
            return test_list # 返回已完成的Test对象列表
        else:
            return False



    @property
    def tested_questions(self):
        """获取已测试过的题目,
           返回题目对象列表
        """
        if not Question.is_meet_Min_count():
            return set([-1]) # 不满足最低数量要求
        finished_test = self.has_finished_test # 获取已完成测试
        if not finished_test:
            return set([None]) # 没有已完成的测试

        tested_questions = [answer.question for test in finished_test for answer in test.answer_list]
        tested_questions = set(tested_questions)
        return tested_questions


    def can(self,permissions):
        """验证权限"""
        return self.role is not None and  \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        """验证管理员权限"""
        return self.can(Permission.ADMIN)

    @property
    def is_newUser(self):
        """判断是否新用户
        1、没有机会记录,新注册用户;
        2、有机会记录,没有闯关记录,新用户;
        3、有机会记录且有闯关记录,老用户
        """
        test = Test.query.filter_by(user_id=self.id).first()
        chance = Chance.query.filter_by(user_id=self.id).first()
        if chance is None:
            return 1
        elif not chance is None and test is None:
            return -1
        elif not chance is None and not test is None:
            return 0

    @property
    def has_chance(self):
        """判断是否还有挑战机会"""
        chance = Chance.query.filter_by(user_id=self.id).first()
        if chance.left_chances > 0:
            return chance.left_chances # 挑战机会大于0，返回数量
        else:
            return False

    def init_chance(self):
        """初始化闯关机会"""
        chance = Chance(user_id = self.id)
        db.session.add(chance)
        db.session.commit()

    @property
    def best_result(self):
        """计算最好的闯关结果
        按照分数由高到低，时间由低到高
        """
        result = Test.query.order_by(Test.score.desc()).\
            order_by(Test.spend_time.asc()).first()
        return result

class AnonymousUser(AnonymousUserMixin):
    """定义匿名用户"""
    def can(self,permissions):
        return False

    def is_administrator(self):
        return False
login_manager.anonymous_user = AnonymousUser # 定义游客，统一权限检查

class Role(db.Model):
    """角色模型"""
    __tablename__ = 'roles'

    id = db.Column(db.Integer,primary_key=True)
    role_name = db.Column(db.String(64),unique=True,index=True) # 角色名称
    default = db.Column(db.Boolean,index=True) # 默认标记
    permissions = db.Column(db.Integer,index=True) # 权限集
    user_list = db.relationship('User',backref='role') # 定义反向关系

    @staticmethod
    def insert_role():
        """插入角色"""
        roles = {
            'User': (Permission.WRITE_ANSWER |
                     Permission.READ_RESULT, True),
            'DataAdmin': (Permission.WRITE_ANSWER |
                          Permission.READ_RESULT |
                          Permission.READ_RESULTS |
                          Permission.WRITE_QUESTION, False),
            'Administrator': (0xff, False),
        }
        for r in roles:
            role = Role.query.filter_by(role_name=r).first()
            if role is None:
                role = Role(role_name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
            db.session.commit()


class Permission:
    WRITE_ANSWER = 0x01 # 答题
    READ_RESULT = 0x02 # 读取个人测试结果
    READ_RESULTS = 0x04 # 读取他人测试结果
    WRITE_QUESTION = 0x08 # 创建、修改题库
    ADMIN = 0x80 # 管理网站




class Test(db.Model):
    """测试模型"""

    __tablename__ = 'tests'

    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id')) # 定义外键
    start_time = db.Column(db.Float,index=True) # 开始时间
    end_time = db.Column(db.Float,index=True) # 截止时间
    spend_time = db.Column(db.Float,index=True) # 花费时间
    finished = db.Column(db.Boolean,default=False) # 是否完成,默认状态为未完成
    score = db.Column(db.Integer,index=True) # 测试得分
    answer_list = db.relationship('Answer',backref='test') # 定义反向关系

    def create_questions(self):
        """创建测试题目"""
        if -1 in self.user.tested_questions:
            """题库数量不满足要求"""
            return False

        set_untested_questions = Question.total_set() - \
                                 self.user.tested_questions # 整体与已完成做差集
        if len(set_untested_questions) < current_app.config['QUESTIONS_COUNT_PER_TEST']:
            return False # 未测试题目数量不满足要求

        selected = random.sample(set_untested_questions,
                                 current_app.config['QUESTIONS_COUNT_PER_TEST']) # 随机选择指定数量
        order_id = 1 # 初始显示序号
        for question in selected:
            answer = Answer(question_id=question.id,
                            test_id=self.id,
                            order_id=order_id)
            db.session.add(answer)
            db.session.commit()
            order_id += 1
        return True

    @property
    def show_score(self):
        """计算分数"""
        if self.finished:
            if  not self.score:
                try:
                    score_list = [answer.score for answer in self.answer_list]
                    self.score = sum(score_list)
                    db.session.add(self)
                    db.session.commit()
                except:
                    return -1
            return self.score
        else:
            return -1

    @property
    def show_spend_time(self):
        """计算花费时间"""
        if self.finished:
            if not self.spend_time:
                self.spend_time = self.end_time - self.start_time
                db.session.add(self)
                db.session.commit()
            show_time = time.strftime('%Y-%m-%d %H:%M:%S',
                                      time.localtime(self.spend_time))
            return show_time
        else:
            return -1



    def during_to_string(self,during_time):
        """浮点格式时间间隔,转化为可读性更好的时分秒"""
        day = 24 * 60 * 60
        hour = 60 * 60
        min = 60
        if during_time < 60:
            return "%d 秒" % math.ceil(during_time)
        elif during_time > day:
            days = divmod(during_time,day)
            return "%d 天,%s"%(int(days[0]),self.during_to_string(days[1]))
        elif during_time > hour:
            hours = divmod(during_time,hour)
            return "%d 小时,%s"%(int(hours[0]),self.during_to_string(hours[1]))
        elif during_time > min:
            mins = divmod(during_time,min)
            return "%d 分,%s"%(int(mins[0]),self.during_to_string(mins[1]))

    def set_finish(self,end_time):
        """设置完成标识"""
        if not self.finished:
            self.finished = True
            self.end_time = end_time
            db.session.add(self)
            db.session.commit()

    @property
    def is_complete(self):
        """检查是否完成,用于可修改题目模式"""
        if not self.answer_list:
            return False
        else:
            answer_list = [answer.answer for answer in self.answer_list]
            if None in answer_list:
                return False
            else:
                return True

class Chance(db.Model):
    """测试资格模型"""
    __tablename__ = 'chances'

    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    left_chances = db.Column(db.Integer,default=1) # 当前测试资格
    start_chances = db.Column(db.Integer,default=1)
    awarded_chances = db.Column(db.Integer,default=0)
    used_chances = db.Column(db.Integer,default=0)













