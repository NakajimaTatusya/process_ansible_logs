
import random

class Hoge:
    def __init__(self):
        self.number = 0
        self.name = ""

    def __str__(self):
        return "number:{0}  name:{1}".format(self.number, self.name)

if __name__ == "__main__":
    names = ['hanako', 'tarou', 'mituo', 'satou', 'koda', 'hayano', 'ichikawa', 'torisima', 'iino', 'okabe', 'moriya', 'zadako', 'kayako']
    foo = list()
    
    nct = 0
    while nct < 100:
        hoge = Hoge()
        hoge.number = nct
        hoge.name = names[random.randrange(len(names))]
        foo.append(hoge)
        nct += 1

    tmp = filter(lambda x: x.number % 2 == 0, foo)
    for w in tmp:
        print(w)
    