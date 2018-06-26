from tkinter import *
import random
import tkinter.font as tkFont
import json
import codecs
import configparser
from reset import reset

LIMIT = 3


class App:
    def __init__(self, window):
        self.window = window

        cfg = configparser.ConfigParser()
        cfg.read('config.ini')

        self.data_filename = cfg.get('path', 'filename')

        self.questions = json.load(codecs.open(self.data_filename, 'r', 'utf-8'))
        if not self.candidate:
            reset()
            self.questions = json.load(codecs.open(self.data_filename, 'r', 'utf-8'))

        self.hav_show = False

        question_ft = tkFont.Font(family='Fixdsys', size=14, weight=tkFont.BOLD)
        entry_ft = tkFont.Font(family='Fixdsys', size=20, weight=tkFont.BOLD)
        answer_ft = tkFont.Font(family='Fixdsys', size=60, weight=tkFont.BOLD)

        self.question = Label(window, text="question...", font=question_ft)
        self.entry = Entry(window, font=entry_ft)
        self.answer = Label(window, text="answer...", font=answer_ft)

        self.question.pack(side=TOP, fill=BOTH)
        self.entry.pack(ipady=10, pady=40)
        self.answer.pack(side=TOP, fill=BOTH, expand=YES)

        self.entry['justify'] = CENTER

        self.entry.bind('<Return>', self.enter)

        self.cur = None
        self.next_question()

    @staticmethod
    def set_color(widget, color="black"):
        widget["foreground"] = color

    @staticmethod
    def set_text(widget, text):
        res = []
        step = 50
        for i in range(0, len(text), step):
            res.append(text[i:i + step])
        widget["text"] = '\n'.join(res)

    def make_correct(self):
        self.cur['count'] = self.cur.get('count', 0) + 1

    def set_title(self, done):
        title_string = "({done}/{total})".format(done=done, total=len(self.questions))
        self.window.title(title_string)

    def update_title(self):
        done = len(self.questions) - len(self.candidate)
        self.set_title(done)

    def enter(self, e=None):
        # 在输入框按下回车后
        if self.hav_show:  # 如果已经显示了答案
            self.next_question()
            self.entry.delete(0, END)
            App.set_color(self.answer)
        else:
            if self.cur:
                self.set_text(self.answer, self.cur['answer'])
                if self.entry.get().replace(' ', '') == self.cur['answer'].replace(' ', ''):
                    self.make_correct()
                    App.set_color(self.answer, 'green')

        self.hav_show = not self.hav_show

    def save(self):
        """
        保存文件
        """
        json.dump(self.questions, codecs.open(self.data_filename, 'w', 'utf-8'), ensure_ascii=False, indent=4)

    def next_question(self):
        candidate = self.candidate
        if candidate:
            self.cur = random.choice(candidate)
            count = self.cur.get('count', 0)

            App.set_text(self.question, self.cur['question'] + '(have done {} times)'.format(count))
        else:
            self.cur = None
            App.set_text(self.question, '全部题目已经复习完成！')
        self.save()
        App.set_text(self.answer, '')
        self.update_title()

    @property
    def candidate(self):
        return [question for question in self.questions if question.get('count', 0) < LIMIT]


root = Tk()
root.geometry('600x400+50+50')
root.title("Pack - Example")
display = App(root)
root.mainloop()
