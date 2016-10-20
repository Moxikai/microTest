#coding:utf-8
"""
数据模型
"""
import random,hashlib,math,time

from flask import current_app

from app import db


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

class Answer(db.Model):
    """答题"""
    __tablename__ = 'answers'

    id = db.Column(db.Integer,primary_key=True) # 答题
    order_id = db.Column(db.Integer,index=True) # 显示题号
    answer = db.Column(db.String(32),index=True) # 答案
    is_right = db.Column(db.Boolean,index=True) # 是否正确
    score = db.Column(db.Integer,index=True,default=0) # 得分
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))  # 外键，题目id
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 外键，人员id

    def calculate_score(self):
        """计算得分"""
        print '当前答案是：----------%s------------当前标准答案是：------------------%s'%(self.answer,self.question.answer_right)
        if self.answer == self.question.answer_right:
            self.score = self.question.score_right
        db.session.add(self)
        db.session.commit()

class User(db.Model):
    """用户"""
    __tablename__ = 'users'

    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(128),index=True,unique=True) # 用户名,微信号
    phone = db.Column(db.String(11),index=True,unique=True) # 用户手机号
    scores = db.Column(db.Integer,index=True,default=0) # 总得分
    is_finished = db.Column(db.Boolean,default=False) # 测试完成标记
    start_time = db.Column(db.String(32),index=True) # 测试开始时间
    end_time = db.Column(db.String(32),index=True) # 截止时间
    answer_list = db.relationship('Answer',backref='user') # 定义反向关系


    def createQuestions(self):
        """创建随机题库"""
        question_list = Question.query.all()
        random_list = random.sample(question_list, current_app.config['QUESTION_COUNT'])
        order_id = 1
        for question in random_list:
            new_answer = Answer(order_id=order_id,
                                question_id=question.id,
                                user_id=self.id,
                                )
            db.session.add(new_answer)
            db.session.commit()
            order_id += 1

    def deleteQuestions(self):
        """删除答题记录"""
        for answer in self.answer_list:
            db.session.delete(answer)
            db.session.commit()

    def calculate_scores(self):

        """计算总得分"""
        for answer in self.answer_list:
            answer.calculate_score()
        score_list = [answer.score for answer in self.answer_list]
        self.scores = sum(score_list)
        db.session.add(self)
        db.session.commit()
        return self.scores

    def calculate_scores_right(self):
        """计算标准得分"""
        score_right_list = [answer.question.score_right for answer in self.answer_list]
        scores_right = sum(score_right_list)
        return scores_right

    def calculate_spend_time(self):
        """计算花费时间"""
        start_time = time.mktime(time.strptime(self.start_time,'%Y-%m-%d %H:%M:%S'))
        end_time = time.mktime(time.strptime(self.end_time,'%Y-%m-%d %H:%M:%S'))
        spend_time = User.changeTime(end_time - start_time)
        print '本次测试开始时间是：------------%s------------结束时间是-----------%s-----------花费时间：---------%s'%\
              (start_time,end_time,spend_time)
        return spend_time

    @staticmethod
    def changeTime(allTime):

        day = 24 * 60 * 60
        hour = 60 * 60
        min = 60
        if allTime < 60:
            return "%d sec" % math.ceil(allTime)
        elif allTime > day:
            days = divmod(allTime, day)
            return "%d days, %s" % (int(days[0]), User.changeTime(days[1]))
        elif allTime > hour:
            hours = divmod(allTime, hour)
            return '%d hours, %s' % (int(hours[0]), User.changeTime(hours[1]))
        else:
            mins = divmod(allTime, min)
            return "%d mins, %d sec" % (int(mins[0]), math.ceil(mins[1]))

    @property
    def is_completed(self):
        """检查是否全部完成"""
        if self.answer_list:
            answer_list = [answer.answer for answer in self.answer_list]
            if None in answer_list:
                return False
            else:
                return True
        else:
            return False



    @staticmethod
    def randomUserName():
        """游客生成随机用户名"""
        username = random.randint(0, 10000000000)
        sha1 = hashlib.sha1()
        sha1.update(str(username))
        return sha1.hexdigest()




