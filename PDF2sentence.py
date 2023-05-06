import io
import re
from nltk.tokenize import sent_tokenize
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import time
def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()  # 存储共享资源，例如字体或图片
    retstr = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr,laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)  # 解析 page内容
    password = ""  # 密码，若无则初始化为空
    maxpages = 0
    caching = True
    pagenos = set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages,
                                  password=password,
                                  caching=caching,
                                  check_extractable=True):
        interpreter.process_page(page)
    text = retstr.getvalue()
    fp.close()
    device.close()
    retstr.close()
    txt_path = path.rstrip('pdf') + "txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(text)
    return txt_path
def change(path):
    word=[]
    pinjie=[]
    with open(path,'r',encoding='utf-8') as f:
        data=f.readlines()
        word.append(data)
        true_word=word[0]
        for i in range(len(true_word)):  # i是一行话
            if true_word[i] != '\n':
                pinjie.append(true_word[i].rstrip())   #把每一行的最后的换行符删除
            else:
                pinjie.append(true_word[i])    #保留句与句之间的换行符
    #print(pinjie)
    return pinjie

#change('pdf/old1.txt')

def find_index(src, key):
    start_pos = 0
    position=[]
    for i in range(src.count(key)):
        if start_pos == 0:
            start_pos = src.index(key)
        else:
            start_pos = src.index(key, start_pos+1)
        position.append(start_pos)
    #print(position)
    return position


def zuihou(path):
    txt=[]
    txt_path=convert_pdf_to_txt(path)
    true_word = change(txt_path)
    position = find_index(true_word, key='\n')
    for i in range(0,len(position)-1):
        start = position[i]
        end = position[i + 1]
        if position[i + 1] - position[i] > 2:
            lastword = ''
            for t in range(start, end):
                if true_word[t].endswith('-'):
                    lastword=lastword+true_word[t].rstrip('-')
                else:
                    lastword=lastword+true_word[t]+' '
            txt.append(lastword)
        else:
            for t in range(start, end):
                txt.append(true_word[t])
    for i in txt:
        if i =='\n':
            txt.remove(i)
    for i in range(0,len(txt)):
        txt[i]=txt[i].lstrip()
    return txt
def zuihou_gai(path):
    txt=[]
    txt_path=convert_pdf_to_txt(path)
    true_word = change(txt_path)
    position = find_index(true_word, key='\n')
    for i in range(0,len(position)-1):
        start = position[i]
        end = position[i + 1]
        if position[i + 1] - position[i] > 2:
            lastword = ''
            for t in range(start, end):
                if true_word[t].endswith('-'):
                    lastword=lastword+true_word[t].rstrip('-')
                else:
                    lastword=lastword+true_word[t]+' '
            txt.append(lastword)
        else:
            for t in range(start, end):
                txt.append(true_word[t])
    sentences=[]
    pattern = re.compile(r'^fig. \.|^figure \.|^fig.\.', re.IGNORECASE)  ##后期再加
    for i in txt:
        sentence = sent_tokenize(i)
        pinjie=""
        for j in sentence:
            split_array=j.split()
            result_start = re.findall(pattern, split_array[0])
            result_end = re.findall(pattern, split_array[-1])
            if len(result_start)!=0:
                pinjie=split_array[0]
                continue
            if len(result_end)!=0:
                pinjie=split_array[-1]
                continue
            else:
                j=pinjie+j
                sentences.append(j)
                pinjie=""
    for i in range(0,len(sentences)):
        sentences[i]=sentences[i].lstrip()
    return sentences

#time_start = time.time()  # 记录开始时间
#zuihou_gai('pdf/new1.pdf')
# time_end = time.time()  # 记录结束时间
# time_sum = time_end - time_start  # 计算的时间差为程序的执行时间，单位为秒/s
# print(time_sum)
#convert_pdf_to_txt('pdf/old1.pdf')
#split2sentence('pdf/2.pdf')
