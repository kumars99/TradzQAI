import cv2
import numpy as np
import pandas as pd
from mss import mss
from PIL import Image, ImageEnhance,ImageFilter
import time 
import pytesseract
import PIL.ImageOps


area = {'top': 250, 'left':78, 'width':200, 'height':820}


#def check_is_valid(data):
def save_to_xls(daily):
    date = "EUR_USD.csv"
    daily.to_csv(date)

def add_new_daily_data(daily, last, c):
    is_new = 0
    new_data = pd.DataFrame()
    time = []
    price = []
    i = len(last) - 1
    if c > 0:
        while i > 0:
                if last['Time'][i] in daily['Time'][len(daily['Time']) - 1] and last["Price"][i] in daily['Price'][len(daily['Price']) - 1] and is_new == 0:
                     is_new = 1
                     break
                i -= 1
        if is_new == 0:
            daily = daily.append(last, ignore_index=True)
        else:
            daily = daily.append(extract_new(last, i + 1), ignore_index=True)
    else:
        daily = last
    c += 1
    #print(daily)
    return daily, c

def extract_new(data, index):
    time = []
    price = []
    while index < len(data) - 1:
        time.append(data['Time'][index])
        price.append(data['Price'][index])
        index += 1
    tmpt = pd.DataFrame(time, columns=['Time'])
    tmpp = pd.DataFrame(price, columns=['Price'])
    tmpp = tmpp.join(tmpt)
    return tmpp

def extract_by_row(rows):
    price = ""
    time = ""
    new = []
    count = 0
    name = ['Time', 'Price']
    for row in range(len(rows)):
        if count > 5 and (',' in rows[row] or '.' in rows[row]):
            price += '.'
            count += 1
        if count < 5 and ':' in rows[row]:
            time += ':'
        if count > 5 and (rows[row] >= '0' and rows[row] <= '9'):
            price += rows[row]
            count += 1
        elif rows[row] >= '0' and rows[row] <= '9':
            time += rows[row]
            count += 1
    if len(time) != 8:
        time = None
    if len(price) != 7:
        price = None
    return time, price

def extract_new_data(data):
    new = data.split('\n')
    tmpt = []
    tmpp = []
    i = len(new) - 1
    while i > 0:
        Time, Price = extract_by_row(new[i])
        if Time and Price:
            tmpt.append(Time)
            tmpp.append(Price)
        i -= 1
    tmpt = pd.DataFrame(tmpt, columns=['Time'])
    tmpp = pd.DataFrame(tmpp, columns=['Price'])
    data = tmpt.join(tmpp)
    return data


def parsing():
    with mss() as sct:
        daily_data = None
        sec = 0
        frames = 0
        c = 0
        start_time = time.time()
        while True:
            buff = ""
            last_time = time.time()
            sct_img = sct.grab(area)
            img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
            #cv2.imshow('Row_img', np.array(img))
            im = cv2.resize(np.array(img), None, fx = 4, fy = 2, interpolation = cv2.INTER_CUBIC)
            im = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2GRAY)
            gray = Image.fromarray(im)
            gray = gray.convert('L')
            gray.point(lambda x: 0 if x < 128 else 255, '1')
            gray = PIL.ImageOps.invert(gray)
            #cv2.imshow('Mod_img', np.array(gray))
            buff = str(pytesseract.image_to_string(gray))
            data = extract_new_data(buff)
            daily_data, c = add_new_daily_data(daily_data, data, c)
            print("Daily len :", len(daily_data))
            #print(daily_data)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
            #time.sleep(5)
            sec += time.time() - last_time
            frames += 1
            if sec > 1:
                #print("Frames :", frames)
                frames = 0
            if sec > 60:
                save_to_xls(daily_data)
                sec = 0
            #time.sleep(0.2)
            print ("Loop time :", round(time.time()-last_time, 5), "s", " Time since start :", round(time.time()-start_time, 5), "s")

parsing()
