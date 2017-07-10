# -*- coding: utf-8 -*-
"""
Created on Sun Jul  9 08:47:29 2017

@author: nyan101
"""

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import  urllib.request
from PIL import Image
from operator import add, sub
from time import sleep

# load images
imgSet = {}
imgList = [num+col for num in ['9', '8', '7', '6', '5', '4', '3', '2', '1', '0']
                    for col in ['r', 'g', 'b']]
imgList += [op+col for op in ['add', 'mult', 'sub']
                    for col in ['r', 'g', 'b']]

numMap = {(10, 10, 10): '7', (11, 13, 15): '1', (18, 22, 26): '4',
 (20, 21, 21): '3', (29, 35, 39): '9', (32, 39, 45): '6',
 (33, 37, 41): '2', (38, 50, 58): '8', (39, 44, 45): '5', (58, 63, 67): '0'}

opMap = {(10, 10, 10): 'add', (11, 11, 11): 'sub', (22, 27, 32): 'mult'}

yOffset = {'0': 8, '1': 13, '2': 4, '3': 0, '4': 39, '5': 4, '6': 33, '7': 0, '8': 11, '9': 10, 'add': 21, 'mult': 0, 'sub': 0}

for f in imgList:
    img = Image.open('./img/'+f+'.png')
    imgSet[f] = (img.size, img.load())

def normalize(img):
    X, Y = img.size
    raw = img.load()
    for x in range(X):
        for y in range(Y):
            t = []
            for i in range(4):
                t.append(((raw[x,y][i])//85)*85)
            raw[x,y] = tuple(t)
    return

def comp(t1, t2):
    return all(map(lambda x:x[0]<=x[1], zip(t1,t2)))

def check(typ, img, prev_xSt):
    X, Y= img.size
    raw = img.load()
    
    xSt = -1
    bFlag = False
    for x in range(prev_xSt, X):
        flag = False
        for y in range(Y):
            if(raw[x,y]!=(255,255,255,255)):
                flag = True
                break
        if(flag and bFlag):
            xSt = x
            break
        else:
            bFlag = True
        
    off = [+1, -2, +3, -4, +5, -6, +7, -8, +9, -10, +11, -12]
    oi = 0
    while True:
        cnt1, cnt2, cnt3 = 0,0,0
        try:
            for y in range(Y):
                if(raw[xSt+3, y]!=(255,255,255,255)):
                    cnt1 += 1
                if(raw[xSt+5,y]!=(255,255,255,255)):
                    cnt2 += 1
                if(raw[xSt+7,y]!=(255,255,255,255)):
                    cnt3 += 1
            if(typ=="num"):
                cand = numMap[(cnt1,cnt2,cnt3)]
            else:
                cand = opMap[(cnt1,cnt2,cnt3)]
            break
        except KeyError:
            xSt += off[oi]
            oi += 1

    ySt = -1
    for y in range(Y):
        if(raw[xSt+3, y]!=(255,255,255,255)):
            ySt = y
            break

    col = ''
    if(raw[xSt+3, ySt]==(255,170,170,255) or raw[xSt+7, ySt]==(255,170,170,255)): col='r'
    if(raw[xSt+3, ySt]==(170,255,170,255) or raw[xSt+7, ySt]==(170,255,170,255)): col='g'
    if(raw[xSt+3, ySt]==(170,170,255,255) or raw[xSt+7, ySt]==(170,170,255,255)): col='b'
    
    ySt -= yOffset[cand]
    
    cx, cy = imgSet[cand+col][0]
    craw   = imgSet[cand+col][1]
    
    for x in range(cx):
        for y in range(cy):
            raw[xSt+x, ySt+y] = tuple(map(add, raw[xSt+x, ySt+y], map(sub, (255,255,255,255), craw[x,y])))
    
    return cand, xSt+1
    
    return -1


browser = webdriver.Chrome()
browser.get("http://asm.eatpwnnosleep.com/")

print("start")
browser.find_element_by_id("start").click()


for lv in range(1, 101):
    while True:
        try:
            urllib.request.urlretrieve(browser.find_element_by_id("img"+str(lv)).get_attribute("src"), "./level_"+str(lv)+".png")
            break
        except NoSuchElementException:
            pass
    
    img = Image.open("level_"+str(lv)+".png")
    
    normalize(img)
    n = (img.size[0]-110)//40 + 1
    
    ss = ""
    px = 0
    for c in range(n):
        if(c == n//2):
            s, px = check("op", img, px)
        else:
            s, px = check("num", img, px)
        ss += s
    #print(ss)
    if "add" in ss:
        ans = int(ss[:ss.find("add")]) + int(ss[ss.find("add")+3:])
    elif "mult" in ss:
        ans = int(ss[:ss.find("mult")]) * int(ss[ss.find("mult")+4:])
    elif "sub" in ss:
        ans = int(ss[:ss.find("sub")]) - int(ss[ss.find("sub")+3:])
    
    browser.find_element_by_id("ans").send_keys(str(ans))
    browser.find_element_by_id("submit").click()
    img.close()
    sleep(0.1)

print("done")
