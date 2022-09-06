#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : wh1sper
# @Time    : 2022/09/01 12:00

from pickle import TRUE
import turtle
import requests
import datetime
import re
import time, sys, random, json


class NetManager:
    def __init__(self) -> None:
        self.config_file    = "data.json"
        self.config         = {}
        self.proxy          = {}
        self.selected_user  = {}
        self.selected_group   = ""
        self.url_check_list = ["https://www.baidu.com/","https://www.qq.com/   ","https://www.sogou.com/"]
        self.http_url       = ""
        self.http_header    = {}
        self.http_body      = {}
        self.http_params    = {}
        self.http_cookie    = {}

    def action(self, action) -> None:
        try:
            if action == "login" and self.check_login() == False :
                redict_page = "3.htm"
                self.select_user()
            elif action == "logout" and self.check_login() == True:
                redict_page = "2.htm"
                self.select_user(1)
            else:
                raise RuntimeError("Already login or logout")

            self.__gen_httpinfo(action)
            r = requests.post(self.http_url, params=self.http_params, headers=self.http_header, cookies=self.http_cookie, data=self.http_body, verify=False, allow_redirects=False, proxies=self.proxy, timeout=3)
            if r.status_code == 302 and redict_page in r.headers['Location']: # success
                print("[!] {} success, user: {}".format(action, self.selected_user["account"]))
                if action == "login":
                    self.config["netinfo"]["selected_user"]  = self.selected_user
                    self.config["netinfo"]["selected_group"] = self.selected_group
                    self.__write_config()
                if action == "logout":
                    self.config["netinfo"]["selected_user"]  = {}
                    self.config["netinfo"]["selected_group"] = ""
                    self.__write_config()
            else: # fail
                print("[!] {} fail, user: {}".format(action, self.selected_user["account"]))
                if action == "login":
                    if r.status_code == 302 and "2.htm" in r.headers['Location'] and "bGRhcCBhdXRoIGVycm9y" in r.headers['Location']:
                        res = self.config["users"][self.selected_group].pop(self.selected_user["account"])
                        print("[!] password error, delete user: {}".format(res))
                        self.__write_config()
                    self.selected_user  = {}
                    self.selected_group = ""
        except Exception as e:
            print(str(e))

    def loop(self) -> None:
        lastcheck = self.check_night()
        while 1:
            if self.config["netinfo"]["if_check_night"] and lastcheck != self.check_night():
                print("[!] detect day-night exchange, now change user.")
                self.action("logout")
                time.sleep(5)
                self.action("login")
                lastcheck = self.check_night()
            if self.check_login() == False:
                print("[E] check failed, now login.")
                lastcheck = self.check_night()
                self.action("login")
            second = random.randint(20, 40)
            time.sleep(second)

    def check_login(self) -> bool:
        url = random.choice(self.url_check_list)
        print("[+] checking url: {} | {}".format(url, time.asctime(time.localtime(time.time()))))
        try:
            r = requests.get(url, headers=self.http_header, timeout=1.5)
            return True
        except:
            return False

    def check_night(self) -> bool:
        d_time  = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '9:40:01', '%Y-%m-%d%H:%M:%S')
        d_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '23:00:01', '%Y-%m-%d%H:%M:%S')
        n_time  = datetime.datetime.now()
        if d_time < n_time and n_time < d_time1:
            return False
        else:
            return True

    def select_user(self, flag=0) -> None:
        if self.__read_config() == False: exit(-1)
        if flag: # when logout, get user from netinfo or server. if can't, exit
            if "account" in self.config["netinfo"]["selected_user"]:
                self.selected_user = self.config["netinfo"]["selected_user"]
            elif self.__get_current_user_from_server() == False:
                exit(-1)
            return
        if self.config["netinfo"]["if_check_night"] and self.check_night():
            self.selected_group  = "master"
        else:
            self.selected_group  = "bachelor"
        randomuser = random.choice(list(self.config["users"][self.selected_group].keys()))
        self.selected_user = self.config["users"][self.selected_group][randomuser]

    def __get_current_user_from_server(self) -> bool:
        url = "http://{}:801/eportal/?c=ACSetting&a=checkScanIP&callback=&wlanuserip={}&_=".format(self.config["netinfo"]["serverip"], self.config["netinfo"]["clientip"])
        try:
            r = requests.get(url, proxies=self.proxy, timeout=3)
            c_account = re.search('"account":"(.*?@.*?)"', r.text).group(1)
            for i in self.config["users"]:
                for j in self.config["users"][i]:
                    if self.config["users"][i][j]["account"] == c_account:
                        self.selected_user = self.config["users"][i][j]
                        return True
        except Exception as e:
            print("[E] can't get current login user from server.")
            print(str(e))
            return False

    def __read_config(self) -> bool:
        try:
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
            return True
        except FileNotFoundError as e:
            print("[!] {} is not fond, now create.".format(self.config_file))
            self.__write_config(1)
            return False

    def __write_config(self, flag=0) -> bool:
        try:
            if flag:
                default_config = {
                    "users":{
                        "bachelor":{"Bxxxxxxx@njxyc":{"account":"Bxxxxxxx@njxy","password":"123456"}},
                        "master":{"123456@cmcc":{"account":"123456@cmcc","password":"123456"}}
                    },
                    "netinfo":{
                        "if_check_night": True, "serverip": "10.10.244.11", "redictip": "6.6.6.6", "clientip": "",
                        "wlanacip": "", "wlanacname": "", "selected_user":{}, "selected_group":""
                    }
                }
                with open(self.config_file, "w") as f:
                    json.dump(default_config, f, indent=4, separators=(',', ':'))
                    return
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4, separators=(',', ':'))
        except Exception as e:
            print("[E] can't write file.")
            print(str(e))

    def __gen_httpinfo(self, action) -> None:
        if action == "login":
            r = requests.get("http://{}/".format(self.config["netinfo"]["redictip"]), allow_redirects=True, proxies=self.proxy)

            self.config["netinfo"]["clientip"]    = re.search("wlanuserip=.*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", r.text).group(1)
            self.config["netinfo"]["wlanacip"]    = re.search("wlanacip=.*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", r.text).group(1)
            self.config["netinfo"]["wlanacname"]  = re.search("wlanacname=(.*?)\"", r.text).group(1)

            self.http_url    = "http://{}:801/eportal/".format(self.config["netinfo"]["serverip"])
            self.http_header = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0",
                # "Origin": "http://{}".format(self.config["netinfo"]["serverip"]),
                # "Referer": "http://{}/".format(self.config["netinfo"]["serverip"]),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Accept-Encoding": "gzip, deflate"
            }
            self.http_params = {
                "c": "ACSetting",
                "a": "Login",
                "protocol": "http:",
                "hostname": self.config["netinfo"]["serverip"],
                "iTermType": "1",
                "wlanuserip": self.config["netinfo"]["clientip"],
                "wlanacip": self.config["netinfo"]["wlanacip"] ,
                "wlanacname": self.config["netinfo"]["wlanacname"],
                "mac": "00-00-00-00-00-00",
                "ip": self.config["netinfo"]["clientip"],
                "enAdvert": "0",
                "queryACIP": "0",
                "loginMethod": "1"
            }
            self.http_body = {
                "DDDDD": ",0,{}".format(self.selected_user['account']),
                "upass": self.selected_user['password'],
                "R1": "0",
                "R2": "0",
                "R3": "0",
                "R6": "0",
                "para": "00",
                "0MKKey": "123456",
                "buttonClicked": "",
                "redirect_url": "",
                "err_flag": "",
                "username": "",
                "password": "",
                "user": "",
                "cmd": "",
                "Login": "",
                "v6ip": ""
            }
            self.http_cookie = {
                "program": "2",
                "vlan": "0",
                "ip": self.config["netinfo"]["clientip"],
                "ssid": "null",
                "areaID": "null",
                # "PHPSESSID": "9f1jc2ph85oo14sh4cqktu4011",
                "ISP_select": self.selected_user['account'].split("@")[1],
                "md5_login2": ",0,{}|{}".format(self.selected_user['account'], self.selected_user['password']),
            }
        if action == "logout":
            self.http_url = 'http://10.10.244.11:801/eportal/'
            self.http_params = {
                "c": "ACSetting",
                "a": "Logout",
                "wlanuserip": self.config["netinfo"]["clientip"],
                "wlanacip": self.config["netinfo"]["wlanacip"],
                "wlanacname": self.config["netinfo"]["wlanacname"],
                "port": "",
                "hostname": self.config["netinfo"]["serverip"],
                "iTermType": "1",
                "session": "",
                "queryACIP": "0",
                "mac": ""
            }
            self.http_cookie = {
                "program": "2",
                "vlan": "0",
                "ip": self.config["netinfo"]["clientip"],
                "ssid": "null",
                "areaID": "null",
                # "PHPSESSID": "9f1jc2ph85oo14sh4cqktu4011",
                "ISP_select": self.selected_user['account'].split("@")[1],
                "md5_login2": ",0,{}|{}".format(self.selected_user['account'], self.selected_user['password']),
            }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[!] usage: python3 njuptAutoLogin.py <action>(login/logout/loop) [http proxy](http://127.0.0.1:8080)")
        exit(-1)

    net_manager = NetManager()
    net_manager.select_user()
    if len(sys.argv) > 2:
        net_manager.proxy['http'] = sys.argv[2]

    if   sys.argv[1] == "login":  net_manager.action("login")
    elif sys.argv[1] == "logout": net_manager.action("logout")
    elif sys.argv[1] == "loop":   net_manager.loop()
