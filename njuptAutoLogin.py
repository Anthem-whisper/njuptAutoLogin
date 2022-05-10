#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : wh1sper
# @Time    : 2022/04/22 12:00
# usage: Capture HTTP packets, convert it to: curl command ->  python -> json, see https://curlconverter.com/
# you only need to change 3 params to login and 2 params to logout in json file

import requests
import datetime
import time, sys, random, json


def login() -> None:
    if currentSelectedUser != {}:
        userInfo = currentSelectedUser.copy()
    else:
        selectUsers()
        userInfo = currentSelectedUser.copy()
    userInfo = currentSelectedUser.copy()

    cookies = userInfo["login"]["cookies"]
    headers = {
        'Host': '10.10.244.11:801',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'Origin': 'http://10.10.244.11',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Referer': 'http://10.10.244.11/',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6',
        'Connection': 'close',
    }
    data = userInfo["login"]["data"]
    url  = userInfo["login"]["url"]
    
    try:
        r = requests.post(url, headers=headers, cookies=cookies, data=data, verify=False, allow_redirects=False, proxies=proxy)
        if r.status_code == 302 and "3.htm" in r.headers['Location']: 
            print("[!] Login Success, current user: {}".format(userInfo["logout"]["params"]["account"]))
        else: 
            print("[!] Login fail, use account: {}".format(userInfo["logout"]["params"]["account"]))
    except Exception as e:
        print("[!] Login fail, use account: {}".format(userInfo["logout"]["params"]["account"]))
        if sys.argv[1] != "loop":
            print(str(e))
            exit(-1)

def logout() -> None:
    global currentSelectedUser
    if currentSelectedUser != {}:
        userInfo = currentSelectedUser.copy()
    else:
        selectUsers()
        userInfo = currentSelectedUser.copy()

    cookies = userInfo["logout"]["cookies"]
    headers = {
        'Host': '10.10.244.11:801',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Connection': 'close',
        'Referer': 'http://10.10.244.11/',
    }
    params = userInfo["logout"]["params"]
    url    = 'http://10.10.244.11:801/eportal/'

    try:
        requests.get(url, headers=headers, params=params, cookies=cookies, verify=False, proxies=proxy)
        print("[!] Logout Success, current user: {}".format(userInfo["logout"]["params"]["account"]))
        currentSelectedUser = {}
    except Exception as e:
        print("[!] Logout fail, current user: {}".format(userInfo["logout"]["params"]["account"]))
        if sys.argv[1] != "loop":
            print(str(e))
            exit(-1)

def loop() -> None:
    urls = ["https://www.baidu.com/","https://www.qq.com/","https://www.sogou.com/"]
    lastcheck = checkNight()
    while 1:
        if lastcheck != checkNight():
            print("[!] Day-night change detect, now logout.")
            logout()
            time.sleep(2)
        url = random.choice(urls)
        second = random.randint(20, 40)
        # second = random.randint(1,3) # for debug
        print("[!] checked for {}  {} , sleep {}".format(url, time.asctime(time.localtime(time.time())), second)) 
        try:
            r = requests.get(url, timeout=1.5)
        except:
            print("[E] check failed, now login.")
            lastcheck = checkNight()
            login()

        time.sleep(second)


def checkNight() -> bool:
    d_time  = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '9:40:01', '%Y-%m-%d%H:%M:%S')
    d_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '23:00:01', '%Y-%m-%d%H:%M:%S')
    n_time  = datetime.datetime.now()  

    if d_time < n_time and n_time < d_time1:
        return True
    else:
        return False

def selectUsers() -> None:
    global currentSelectedUser
    try:
        with open("data.json", "r") as f:
            users = json.load(f)
    except FileNotFoundError as e:
        print("[!] data.json is not fond, now create.")
        default_json = {
            "users":{
                "bachelor":{"user1":{"login":{"cookies":{},"data":"","url":""},"logout":{"cookies":{},"params":{}}}},
                "master":{"user1":{"login":{"cookies":{},"data":"","url":""},"logout":{"cookies":{},"params":{}}}}
            }
        }
        with open("data.json", "w") as f:
            json.dump(default_json, f, indent=4, separators=(',', ':'))
        exit(-1)

    if checkNight():
        currentSelectedUser = users["users"]["bachelor"]["tcc"] 
        # randomuser = random.choice(list(users["users"]["bachelor"].keys()))
        # currentSelectedUser = users["users"]["bachelor"][randomuser]
    else:
        currentSelectedUser = users["users"]["master"]["yan"]
        # randomuser = random.choice(list(users["users"]["master"].keys()))
        # currentSelectedUser = users["users"]["master"][randomuser]
    

currentSelectedUser = {} 
proxy = {
    "http": "" # command line param
}


if __name__ == "__main__":
    selectUsers()
    if len(sys.argv) < 2:
        print("[!] usage: python3 njuptAutoLogin.py <action>(login/logout/loop) [http proxy](http://127.0.0.1:8080)")
        exit(-1)
    if len(sys.argv) > 2: 
        proxy['http'] = sys.argv[2]

    if   sys.argv[1] == "login":  login()
    elif sys.argv[1] == "logout": logout()
    elif sys.argv[1] == "loop":   loop()
