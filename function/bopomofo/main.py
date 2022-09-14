import sys
from .loader import words

def trans_word(text):
    if text in words:
        return words[text]
    else:
        return text

def trans_sentense(text):
    ret = ""
    buf = ""
    for x in text:
        if x not in words:
            ret = ret + ' ' + trans_word(buf)
            buf = ""
            ret = ret + ' ' + trans_word(x)
            continue
        if buf + x not in words:
            ret = ret + ' ' + trans_word(buf)
            buf = x
        else:
            buf = buf + x
    ret = ret + ' ' + trans_word(buf)
    return ret[1:]

def in_string(substring, string):
    return trans_sentense(substring) in trans_sentense(string)

def listofstr_in_string(list_, string):
    return any(trans_sentense(s) in trans_sentense(string) for s in list_)

if __name__ == "__main__":
    w1 = '馬力歐賽車'
    w2 = '[NS] 售 瑪利歐兄弟U 3D狂怒世界 瑪莉歐賽車8'
    print(f'trans_sentense("{w1}"):', trans_sentense(w1))
    print(f'trans_sentense("{w2}"):', trans_sentense(w2))
    print(in_string(w1, w2))