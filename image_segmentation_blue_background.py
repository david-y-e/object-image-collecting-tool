import cv2
import numpy as np

def Background_Removal_Blue(img,threshold):
    # img = cv2.imread('/home/irobot/images/test_white%d.jpg'%num_img)
    rows, cols, channels = img.shape
    grayimg = img[:,:,0]

    interval = 1

    set1 = list()
    set2 = list()
    set3 = list()
    set4 = list()

    row_temp, col_temp = 0, 0

    ############  step 1  ############
    min_temp = cols - 1
    while col_temp < cols:
        while row_temp < rows:
            row_val = grayimg[row_temp][col_temp]
            row_val = row_val.astype(np.int64)
            row_val_pre = grayimg[row_temp - interval][col_temp]
            row_val_pre = row_val_pre.astype(np.int64)
            # print(row_val,row_val_pre)
            if row_temp > 1:
                if abs(row_val - row_val_pre) > threshold:
                    set1.append((row_temp, col_temp))
                    # print(row_temp, col_temp)
                    if min_temp > col_temp:
                        min_temp = col_temp
                    # print(row_temp,col_temp,row_val)
                    break
            row_temp = row_temp + 1
        row_temp = 0
        col_temp = col_temp + 1
    xmin = min_temp

    # print("==========================\n     step 1 finished\n==========================")

    row_temp, col_temp = rows - 1, 0

    ############  step 2  ############
    max_temp = 0
    while col_temp < cols:
        while row_temp > 0:
            row_val = grayimg[row_temp][col_temp]
            row_val = row_val.astype(np.int64)
            row_val_pre = grayimg[row_temp - interval][col_temp]
            row_val_pre = row_val_pre.astype(np.int64)
            # print(row_val,row_val_pre)
            if row_temp < rows - 2:
                if abs(row_val - row_val_pre) > threshold:
                    set2.append((row_temp, col_temp))
                    # print(row_temp, col_temp)
                    if max_temp < col_temp:
                        max_temp = col_temp
                    break
            row_temp = row_temp - 1
        row_temp = rows - 1
        col_temp = col_temp + 1
    xmax = max_temp

    # print("==========================\n     step 2 finished\n==========================")

    row_temp, col_temp = 0, 0

    ############  step 3  ############
    min_temp = rows - 1
    while row_temp < rows:
        while col_temp < cols:
            col_val = grayimg[row_temp][col_temp]
            col_val = col_val.astype(np.int64)
            col_val_pre = grayimg[row_temp][col_temp - interval]
            col_val_pre = col_val_pre.astype(np.int64)
            # print(col_val,col_val_pre)
            if col_temp > 1:
                if abs(col_val - col_val_pre) > threshold:
                    set3.append((row_temp, col_temp))
                    # print(row_temp, col_temp)
                    if min_temp > row_temp:
                        min_temp = row_temp
                    break
            col_temp = col_temp + 1
        col_temp = 0
        row_temp = row_temp + 1
    ymin = min_temp

    # print("==========================\n     step 3 finished\n==========================")

    row_temp, col_temp = 0, cols-1

    ############  step 4  ############
    max_temp = 0
    while row_temp < rows:
        while col_temp > 0:
            col_val = grayimg[row_temp][col_temp]
            col_val = col_val.astype(np.int64)
            col_val_pre = grayimg[row_temp][col_temp - interval]
            col_val_pre = col_val_pre.astype(np.int64)
            # print(col_val,col_val_pre)
            if col_temp < cols - 2:
                if abs(col_val - col_val_pre) > threshold:
                    set4.append((row_temp, col_temp))
                    # print(row_temp, col_temp)
                    if max_temp < row_temp:
                        max_temp = row_temp
                    break
            col_temp = col_temp - 1
        col_temp = cols - 1
        row_temp = row_temp + 1
    ymax = max_temp

    # print("==========================\n     step 4 finished\n==========================")
    img_check = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    for i in set1:
        img[0:i[0],i[1],3] = 0
        img_check[0:i[0],i[1]] = (0,0,255,255)

    for i in set2:
        img[i[0]:rows-1,i[1],3] = 0
        img_check[i[0]:rows-1,i[1]] = (0,0,255,255)

    for i in set3:
        img[i[0],0:i[1],3] = 0
        img_check[i[0], 0:i[1]] = (0,0,255,255)

    for i in set4:
        img[i[0],i[1]:cols-1,3] = 0
        img_check[i[0],i[1]:cols-1] = (0,0,255,255)

    img[0:ymin,0:xmin,3] = 0
    img_check[0:ymin,0:xmin] = (0,0,255,255)

    img[0:ymin,xmax:cols-1,3] = 0
    img_check[0:ymin,xmax:cols-1] = (0,0,255,255)

    img[ymax:rows-1,0:xmin,3] = 0
    img_check[ymax:rows-1,0:xmin] = (0,0,255,255)

    img[ymax:rows-1,xmax:cols-1,3] = 0
    img_check[ymax:rows-1,xmax:cols-1] = (0,0,255,255)

    ############  Bounding Box  ############

    # img[ymin,xmin:xmax] = (0,0,255)
    # img[ymax,xmin:xmax] = (0,0,255)
    # img[ymin:ymax,xmin] = (0,0,255)
    # img[ymin:ymax,xmax] = (0,0,255)

    # print(xmin, xmax, ymin, ymax)
    crop_img = img[ymin:ymax,xmin:xmax]
    # print(crop_img)
    return(crop_img,img_check)

    # cv2.imwrite('/home/irobot/new%d.png'%num_img,crop_img)
# cv2.imshow('image',new_img)
# c = cv2.waitKey(0)
# if c == 27:
#     cv2.destroyAllWindows()