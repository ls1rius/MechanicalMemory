from tkinter import *
import random
import tkinter.font as tkFont
import json
import codecs
import configparser
from functools import partial

LIMIT = 3


class App:
    def __init__(self, window):
        ft = tkFont.Font(family='Fixdsys', size=14, weight=tkFont.BOLD)

        self.window = window
        self.question = Label(window, text="question..", font=ft)
        self.buttons = [Button(window, font=ft) for _ in range(5)]
        # 初始化控件

        cfg = configparser.ConfigParser()
        cfg.read('config.ini')
        self.data_filename = cfg.get('path', 'filename')

        self.questions = json.load(codecs.open(self.data_filename, 'r', 'utf-8'))
        # 读取题目

        events = [partial(self.judge, button) for button in self.buttons]
        # 初始化事件

        self.question.pack(fill=BOTH, expand=YES)
        [button.pack(fill=BOTH, expand=YES) for button in self.buttons]
        # 给控件布局

        [button.bind('<Button-1>', event) for button, event in zip(self.buttons, events)]
        [window.bind(char, event) for char, event in zip("12345", events)]
        # 绑定事件

        self.cur = None

        self.update_title()
        self.next_question()

    @staticmethod
    def set_color(widget, color="SystemButtonFace"):
        """
        设置控件背景颜色，SystemButtonFace为默认颜色
        :param widget:控件
        :param color: 颜色
        """
        widget["background"] = color

    @staticmethod
    def set_text(widget, text, step=50):
        """
        设置控件文本
        :param widget:控件
        :param text: 文本
        :param step:最大字符数，超过这个字符则换行
        """
        res = []
        for i in range(0, len(text), step):
            res.append(text[i:i + step])
        widget["text"] = '\n'.join(res)

    def save(self):
        """
        保存文件
        """
        json.dump(self.questions, codecs.open(self.data_filename, 'w', 'utf-8'), ensure_ascii=False, indent=4)

    def set_title(self, done):
        """
        设置标题为（已完成题数/总题数）
        :param done:已经完成题目个数
        """
        title_string = "({done}/{total})".format(done=done, total=len(self.questions))
        self.window.title(title_string)

    def update_title(self):
        """
        计算已完成题目数，更新标题
        如果一个题目的正确次数达到了LIMIT次，则视为已完成
        """
        done = len(self.questions) - len(self.candidate)
        self.set_title(done)

    def mark_correct(self):
        """
        设置当前题目完成次数+1
        """
        self.cur['count'] = self.cur.get('count', 0) + 1

    def mark_wrong(self):
        """
        设置当前题目完成次数-1
        """
        self.cur['count'] = self.cur.get('count', 0) - 1

    def complete_question(self):
        """

        :rtype: 已选择正确选项的数量是否等于答案选项数量
        """
        done = [button for button in self.buttons if button["background"] == "green"]
        return len(done) == len(self.cur['correct'])

    def miss(self):
        """

        :return:选择错误答案的数量
        """
        wrong = [button for button in self.buttons if button["background"] == "red"]
        return len(wrong)

    def judge(self, button, e=None):
        """
        判断选择的选项是否正确，有以下几种情况：
        1.选择的是错误的
            对应选项背景颜色设置为红色
        2.选择的是正确的且已被选择过
            如果选完了全部选项则进行判断是否选择过错误的选项，选择过就让本题count-1，否则+1，并进入下一题
            如果没有选完全部选项，则无操作
        3.选择的是正确的且没被选择过
            对应选项背景颜色设置为绿色

        :param button: 用户按下的按钮
        :param e: event类
        """
        text = button["text"].replace('\n', '')
        result_color = 'red'

        choose_correct = text in self.cur['correct']
        next_question_condition = choose_correct and self.complete_question()

        if next_question_condition:
            if self.miss():
                self.mark_wrong()
            else:
                self.mark_correct()
                self.update_title()
            self.save()
            self.next_question()
        else:
            if choose_correct:
                result_color = 'green'
            App.set_color(button, result_color)

    def empty_button(self):
        """
        清空所有按钮文字
        """
        [App.set_text(button, '') for button in self.buttons]

    def restore_color(self):
        """
        清空所有按钮颜色
        """
        [App.set_color(button) for button in self.buttons]

    def next_question(self):
        """
        进入下一题，从所有count值小于LIMIT值的题目中随机抽一道，打乱选项并依次放入按钮中
        如果没有题目则设置为已完成，并返回
        """
        candidate = self.candidate

        if candidate:
            self.cur = random.choice(candidate)
            count = self.cur.get('count', 0)
        else:
            App.set_text(self.question, '全部题目已复习完成！')
            self.restore_color()
            [App.set_text(button, '') for button in self.buttons]
            return

        options = self.cur['options'].copy()
        random.shuffle(options)

        self.empty_button()
        self.restore_color()

        App.set_text(self.question, self.cur['question'] + '(已完成{}次)'.format(count))
        [App.set_text(button, option)
         for button, option in zip(self.buttons, options)]

    @property
    def candidate(self):
        return [question for question in self.questions if question.get('count', 0) < LIMIT]


root = Tk()
root.geometry('600x400+50+50')
root.title("Pack - Example")
display = App(root)
root.mainloop()
