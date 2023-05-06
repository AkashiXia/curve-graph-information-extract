import os
import fitz
import shutil

def mkdir(path):
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录创建目录操作函数
        os.makedirs(path)
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        shutil.rmtree(path)
        os.makedirs(path)
        return False
def pdf_to_image(pdf_path,zoom_x,zoom_y,rotation_angle):
    # 打开PDF文件
    pdf = fitz.open(pdf_path)
    size = pdf.pageCount
    #print("开始将pdf转化为jpg图片")
    # 创建相应的文件夹
    # extract/输入pdf文件名           每个pdf处理结果单独一个文件夹
    # extract/输入pdf文件名/pdf       文件夹保存的是pdf转jpg的图片
    # extract/输入pdf文件名/table     提取出的表格图片
    # extract/输入pdf文件名/curve     提取出的曲线图片
    # extract/输入pdf文件名/formula   提取出的公式图片
    # extract/输入pdf文件名/image     提取出的其他图片
    pdf_name_type=os.path.basename(pdf_path)
    pdf_name=os.path.splitext(pdf_name_type)[0]
    save_root_path="extract/"+pdf_name
    mkdir(save_root_path)
    pdf_img_save_path = save_root_path+"/pdf"
    curve_save_path = save_root_path + "/curve"
    mkdir(pdf_img_save_path)
    mkdir(curve_save_path)
    #逐页读取PDF
    for pg in range(0, pdf.pageCount):
        page = pdf[pg]
        # 设置缩放和旋转系数
        trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotation_angle)
        pm = page.getPixmap(matrix=trans, alpha=False)
        # 开始写图像
        pm.writePNG(pdf_img_save_path+"\\"+str(pg+1)+".jpg")
    pdf.close()
    return pdf_name_type,pdf_img_save_path,size,save_root_path
pdf_to_image("../pdf/sllgraduationthesis.pdf",5,5,0)
def get_img_list(file_path):
  L=[]
  for root, dirs, files in os.walk(file_path):
    for file in files:
      if os.path.splitext(file)[1] == '.jpg' or os.path.splitext(file)[1] == '.JPG' or os.path.splitext(file)[1] == '.png' or os.path.splitext(file)[1] == '.PNG':
        L.append(os.path.join(root, file))
  return L


def get_pdf_list(file_path):
  L=[]
  for root, dirs, files in os.walk(file_path):
    for file in files:
      if os.path.splitext(file)[1] == '.pdf' or os.path.splitext(file)[1] == '.PDF' :
        L.append(os.path.join(root, file))
  return L