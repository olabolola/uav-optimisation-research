import cv2
import numpy as np
import glob
def make_video():
    img_array = []
    # i = 0
    # while i < 150:
    #     filename = r'images\hind' + str(i) + '.png'
    #     img = cv2.imread(filename)
    #     print(filename)
    #     height, width, layers = img.shape
    #     size = (width,height)
    #     img_array.append(img)
    #     i += 1
    
    filenames = list(glob.glob('images\*.png'))
    filenames.sort()
    for filename in filenames:
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width,height)
        img_array.append(img)
    
        

    # for filename in glob.glob('images/*.png'):
    #     if i == 0:
    #         print(filename)
    #         i = 1
    #     img = cv2.imread(filename)
    #     height, width, layers = img.shape
    #     size = (width,height)
    #     img_array.append(img)


    out = cv2.VideoWriter('project.avi',cv2.VideoWriter_fourcc(*'DIVX'), 15, size)
    
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()