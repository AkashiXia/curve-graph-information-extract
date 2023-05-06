import cv2 as cv
from skimage import morphology
import numpy as np
from paddleocr import PaddleOCR
import pandas as pd
def pixel(img):
  image=cv.imread(img)
  gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
  ret, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
  ls=[]
  for y in range(binary.shape[0]):  # 图片的高
      for x in range(binary.shape[1]):  # 图片的宽
          pixel = binary[y][x]
          if pixel == 0:
              ls.append((y, x))
  return ls,binary

def pixel_1(img):               #白色为直线   黑色为背景
    ls = []
    for y in range(img.shape[0]):  # 图片的高
        for x in range(img.shape[1]):  # 图片的宽
            pixel = img[y][x]
            if pixel == 255:
                ls.append((y, x))
    return ls

def detect_origin_location(image):
    yuandian=[]     #原点的备选集合
    yuandian_1=[]
    startPoint=[]
    img_gray_binary =pixel(image)[1]    #获取二值化图像
    # 保留垂直线
    kernel_y = cv.getStructuringElement(cv.MORPH_RECT, (1, 100))
    img_gray_binary_open_save_y = cv.morphologyEx(img_gray_binary, cv.MORPH_OPEN, kernel_y)
    # 保留水平线
    kernel_x = cv.getStructuringElement(cv.MORPH_RECT, (100, 1))
    img_gray_binary_open_save_x = cv.morphologyEx(img_gray_binary, cv.MORPH_OPEN, kernel_x)   #白色线
    ls_x=pixel_1(img_gray_binary_open_save_x)   #获取横线的像素点
    ls_y=pixel_1(img_gray_binary_open_save_y)    #获取竖线的像素点
    for i in ls_x:
        for j in ls_y:
            if(i==j):
                yuandian.append(i)    #交点
                yuandian_1.append(i)
    for i in range(len(yuandian)-1,-1,-1):   #删除一些左上角的点
        if (yuandian[i][0]<(img_gray_binary.shape[0]/2))&(yuandian[i][1]>(img_gray_binary.shape[1]/2)):
            yuandian.remove(yuandian[i])
    height=max(yuandian[i][0] for i in range(len(yuandian)))    #找y
    for i in range(len(yuandian)-1,-1,-1):
        if yuandian[i][0]!=height:
            yuandian.remove(yuandian[i])
    width = min(yuandian[i][1] for i in range(len(yuandian)))     #找x
    for i in range(len(yuandian)-1,-1,-1):
        if yuandian[i][1]==width:
            startPoint=yuandian[i]
    for i in range(len(yuandian_1)-1,-1,-1):   #删除一些左上角的点
        if (yuandian_1[i][0]>(img_gray_binary.shape[0]/2))&(yuandian_1[i][1]<(img_gray_binary.shape[1]/2)):
            yuandian_1.remove(yuandian_1[i])
    if yuandian_1:
        height_1 = min(yuandian_1[i][0] for i in range(len(yuandian_1)))
        for i in range(len(yuandian_1) - 1, -1, -1):
            if yuandian_1[i][0] != height_1:
                yuandian_1.remove(yuandian_1[i])
        width_1 = max(yuandian_1[i][1] for i in range(len(yuandian_1)))  # 找x
        for i in range(len(yuandian_1)-1,-1,-1):
            if yuandian_1[i][1]==width_1:
                startPoint_1=yuandian_1[i]
    else:
        startPoint_1=startPoint
    print(startPoint)
    print(startPoint_1)
    return startPoint,ls_x,ls_y,startPoint_1

def cutMainPicture(img):
    height_plus = width_plus = 0
    image=cv.imread(img)
    (startPoint,ls_x,ls_y,startPoint_1)=detect_origin_location(img)
    for i in ls_x:
        image[i]=255
    for j in ls_y:
        image[j]=255
    if startPoint_1!=startPoint:
        height_plus = startPoint_1[0]
        width_plus = startPoint[1]
        height=startPoint[0]
        width=startPoint[1]
        height_1 = startPoint_1[0]
        width_1 = startPoint_1[1]
        MainPicture=image[height_1:height,width:width_1]
        xPicture=image[height:image.shape[0],width:image.shape[1]]
        yPicture=image[0:height,0:width]
        #cv.imwrite('MainPicture.png',MainPicture)
        #cv.imwrite('xPicture.png', xPicture)
        #cv.imwrite('yPicture.png', yPicture)
    else:
        height_plus = 0
        width_plus = startPoint[1]
        height = startPoint[0]
        width = startPoint[1]
        MainPicture = image[0:height, width:image.shape[1]]
        xPicture = image[height:image.shape[0], width:image.shape[1]]
        yPicture = image[0:height, 0:width]
        # cv.imwrite('MainPicture.png', MainPicture)
        # cv.imwrite('xPicture.png', xPicture)
        # cv.imwrite('yPicture.png', yPicture)
    return MainPicture,xPicture,yPicture,height_plus,width_plus

def rgb2gray(img):
    (MainPicture,xPicture,yPicture,height_plus,width_plus)=cutMainPicture(img)
    gray = cv.cvtColor(MainPicture, cv.COLOR_BGR2GRAY)
    ret, binary = cv.threshold(gray, 127, 255, cv.THRESH_BINARY)
    #cv.imwrite('beijing.png',binary)
    return binary,height_plus,width_plus

def paddle_orc(img_path):
    ocr = PaddleOCR(use_angle_cls=True,lang='en',use_gpu=False)
    result = ocr.ocr(img_path, cls=True)
    return result


def delete_char(img_path):
    (binary,height_plus,width_plus)=rgb2gray(img_path)
    result=paddle_orc(binary)
    weizhi=[]
    for i in result:
        weizhi.append(i[0])
    for t in weizhi:
        x1=t[0][0]
        x2=t[1][0]
        y1=t[0][1]
        y2=t[2][1]
        x_cha=(int(x2)-int(x1))/2
        for i in range(int(x1)-x_cha,int(x2)+x_cha):
            for j in range(int(y1),int(y2)):
                binary[j][i]=255
    return binary,height_plus,width_plus

def sk(img):
    (img,height_plus,width_plus)=delete_char(img)
    _, binary = cv.threshold(img, 0, 255, cv.THRESH_BINARY_INV)
    binary[binary == 255] = 1
    skeleton0 = morphology.skeletonize(binary)
    skeleton = skeleton0.astype(np.uint8) * 255
    #cv.imwrite("skeleton.png", skeleton)
    return skeleton,height_plus,width_plus

def getColorName(img_path):
    (img_gai,height_plus,width_plus)=sk(img_path)
    img_raw=cv.imread(img_path)
    #print(height_plus,width_plus)
    index = ['colors', 'color-names', 'hex-value', 'R-value', 'G-value', 'B-value']
    df = pd.read_csv('colors.csv', names=index, header=None)
    img_new_list=[]
    width = img_gai.shape[1]
    height = img_gai.shape[0]
    #print(width,height)
    img = img_gai[30:height - 30, 30:width - 30]
    #cv.imwrite('img.png',img)
    most=[]
    color_list=[]
    for y in range(img.shape[0]):  # 图片的高
        for x in range(img.shape[1]):  # 图片的宽
            minimum = 10000
            if (img[y][x]):
                color1=int(img_raw[y + height_plus+30][x + width_plus+30][0])
                color2=int(img_raw[y + height_plus+30][x + width_plus+30][1])
                color3=int(img_raw[y + height_plus+30][x + width_plus+30][2])
    #  calculate a distance(d) which tells us how close we are to color and choose the one having minimum distance.
                for i in range(len(df)):
                    d = abs(color1-int(df.loc[i,'R-value']))+abs(color2-int(df.loc[i,'G-value']))+abs(color3-int(df.loc[i,'B-value']))
                    if d<=minimum:
                        minimum = d
                        colorName = df.loc[i,"color-names"]
                most.append((x,y,color1,color2,color3,colorName))
                color_list.append(colorName)
    spot_sum_all=[]
    i = len(most) - 1
    while i >= 0:
        spot_sum = []
        #print("i是", i)
        spot_sum.append(most[i])
        color=most[i][5]
        most.pop(i)
        i=i-1
        for j in range(i, -1, -1):
            #print(i)
            if most[j][5]== color:
                #print(j)
                spot_sum.append(most[j])
                most.pop(j)
                i = i - 1
        if len(spot_sum)>800:
            spot_sum_all.append(spot_sum)#((x,y),(color1,color2,color3),colorName)
    print(spot_sum_all)

def aix_cal(x_img,y_img):
    x_result=paddle_orc(x_img)
    y_result=paddle_orc(y_img)


    # for i in range(len(spot_sum_all)):
    #     colorR = spot_sum_all[i][0][2]
    #     colorG = spot_sum_all[i][0][3]
    #     colorB = spot_sum_all[i][0][4]
    #     print((colorR,colorG,colorB))
    #     img_new = np.zeros((img_raw.shape[0], img_raw.shape[1], 3), np.uint8)
    #     img_new.fill(255)
    #     for j in range(len(spot_sum_all[i])):
    #         x=spot_sum_all[i][j][0]
    #         y=spot_sum_all[i][j][1]
    #         img_new[y + 140][x + 376][0] = colorB
    #         img_new[y + 140][x + 376][1] = colorG
    #         img_new[y + 140][x + 376][2] = colorR
    #     cv.imwrite(spot_sum_all[i][0][5]+str(color_list.count(spot_sum_all[i][0][5]))+'.jpg',img_new)
    #     print(i)
getColorName('curve_04.jpg')
#detect_origin_location('curve_04.jpg')
#sk("curve_04.jpg")
