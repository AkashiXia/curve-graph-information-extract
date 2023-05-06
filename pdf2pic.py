from picture.pdf_extract import pdf_to_image, get_img_list , get_pdf_list
from picture.yolo_pdf import YOLO_PDF
from PDF2sentence import zuihou
from sentence_transformers import SentenceTransformer, util
import os
import time
from bert_ner.bert import Ner
import glob
import csv
def convert_img(pdfPath):
    imgList=[]
    _, pdfImgSavePath, pageNum, saveRootPath = pdf_to_image(pdfPath, 5, 5, 0)
    print("转换成功，共计" + str(pageNum) + "张图片！")
    for i in range(1, pageNum + 1):
        path = pdfImgSavePath + "/" + str(i) + ".jpg"
        imgList.append(path)
    pageCount = pageNum
    print(imgList)
    print("转化成功",pageCount)
    return imgList,saveRootPath

def detect_chart(pdfpath):
    imgList,saveRootPath=convert_img(pdfpath)
    yolo = YOLO_PDF()
    for num in range(0, len(imgList)):
        print("开始识别 " + imgList[num])
        yolo.detect_image(imgList[num], saveRootPath)
        print("处理完成！")
    return yolo.name

def delete_spare(words):
    i=0;
    while i < len(words):
        if words[i] == '':
            words.remove(words[i])
            i -= 1
        i += 1
    return words


def find_similiar_sen(path):
    pic_sen_list=detect_chart(path)
    txt=zuihou(path)
    score=[]
    model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
    for i in pic_sen_list:
        pic_path,pic_sentence=i
        b=pic_sentence.split(" ")
        b = delete_spare(b)
        sentence1_representation = model.encode(pic_sentence)
        max_single_score=0
        single_sen=''
        single_score = []
        for j in txt:
            same_word = 0;
            txt_sen=j
            c=txt_sen.split(" ");
            c=delete_spare(c)
            while 1:
                if (b[same_word] == c[same_word]):
                    same_word += 1
                else:
                    break
            sentence2_representation = model.encode(txt_sen)
            cosin_sim = util.pytorch_cos_sim(sentence1_representation, sentence2_representation).item()
            cosin_sim=cosin_sim*0.5+0.5*same_word
            single_score.append((cosin_sim,txt_sen))
        max_single_score,single_sen=max(single_score)
        score.append((pic_path,pic_sentence,single_sen,max_single_score))  ##1.截取的图片路径  2.图片中识别的文本   3.txt中找到的句子
    #print(score)
    return score


def find_similiar_sen1(path):
    pic_sen_list = detect_chart(path)
    txt = zuihou(path)
    score = []
    ##model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
    for i in pic_sen_list:
        pic_path, pic_sentence = i
        sentence1_representation = model.encode(pic_sentence)
        max_single_score = 0
        single_sen = ''
        single_score = []
        for j in txt:
            txt_sen = j
            ##sentence2_representation = model.encode(txt_sen)
            ##cosin_sim = util.pytorch_cos_sim(sentence1_representation, sentence2_representation).item()
            single_score.append((cosin_sim, txt_sen))
        max_single_score, single_sen = max(single_score)
        score.append((pic_path, pic_sentence, single_sen, max_single_score))  ##1.截取的图片路径  2.图片中识别的文本   3.txt中找到的句子
    # print(score)
    return score

def named_entity_recognize(path):
    score = find_similiar_sen(path)
    ner_information=[]
    model = Ner("../bert_ner/out_base/")
    for i in range(0,len(score)):
        X, Y = '', ''
        output = model.predict(score[i][2])
        for t in output:
            if t['tag'] == 'B-X' or t['tag'] == 'I-X':
                X=X+t['word']+' '
            if t['tag'] == 'B-Y' or t['tag'] == 'I-Y':
                Y=Y+t['word']+' '
        ner_information.append((path,score[i][0],score[i][1],score[i][2],X,Y))##1.截取的图片路径  2.图片中识别的文本   3.txt中找到的句子  4.X  5.Y
    print(ner_information)
    with open("./2018.csv", "a",newline='',encoding='utf-8') as f:
        writer = csv.writer(f)
        for i in ner_information:
            if i:
                writer.writerow(i)
    return ner_information

##starttime = time.time()
def pdf_list(path):
        file=glob.glob(os.path.join(path, "*.pdf"))
        for i in file:
            named_entity_recognize(i)


##pdf_list(r"C:\Users\86182\Desktop\papers\2018")
##endtime = time.time()
##print(endtime - starttime)
#named_entity_recognize('../pdf/Mesostructure-and-porosity-effects-on-the-thermal-conductivi_2018_Additive-M.pdf')