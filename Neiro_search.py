import os
from fuzzywuzzy import fuzz


class Neiro_search:
    def __init__(self):
        self.mas = []

        if os.path.exists('phrase_list.txt'):
            f = open('phrase_list.txt', 'r', encoding='UTF-8')
            for x in f:
                if (len(x.strip()) > 2):
                    self.mas.append(x.strip().lower())
            f.close()

    def answer(self, text):
        try:
            text = text.lower().strip()
            if os.path.exists('phrase_list.txt'):
                a = 0
                n = 0
                nn = 0
                for q in self.mas:
                    if ('u: ' in q):
                        aa = (fuzz.token_sort_ratio(q.replace('u: ', ''), text))
                        if (aa > a and aa != a):
                            a = aa
                            nn = n
                    n = n + 1
                s = self.mas[nn + 1]
                return s
            else:
                return 'Круто!'
        except:
            return 'Круто!'



if __name__ == "__main__":
    bot = Neiro_search()
    bot.answer("привет")