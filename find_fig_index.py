from paddleocr import PaddleOCR, draw_ocr
import cv2 as cv
import re


def paddle_orc(img_path):
    ocr = PaddleOCR(use_angle_cls=True,lang='en',use_gpu=True)
    result = ocr.ocr(img_path, cls=True)
    txts = [line[1][0] for line in result]
    #print(txts)
    return txts

def cut_img(img):
    #img = cv.imread(img)
    img = img[int(img.shape[0]/2):img.shape[0],0:img.shape[1]]  # 裁剪坐标为[y0:y1, x0:x1]
    return img

def check_figure_name(img):
    figure_sentence=''
    flag=0
    #img = cv.imread(img)   #检测单函数的时候需要
    ocr_result=paddle_orc(cut_img(img))
    pattern = re.compile(r'^fig. \d|^figure \d|^fig.\d', re.IGNORECASE)      ##后期再加
    for i in range(len(ocr_result)):
        result = re.findall(pattern,ocr_result[i])
        if len(result)!=0:
            figure_sentence=ocr_result[i]
            break
    if figure_sentence!='':
        flag=1

    return flag,figure_sentence

#print(paddle_orc(cut_img('./extract/1/curve/5cb1ff305a864d68adde2b65701c8639.jpg')))