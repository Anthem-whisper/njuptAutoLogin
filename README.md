# njuptAutoLoginScript

南京邮电大学校园网（NJUPT、CMCC、ChinaNet）自动登录脚本

## 使用方式

```bash
pip install -r  requirements.txt
python njuptAutoLogin.py <action> [http proxy]
```

参数：

- action，必须项
  - login:  根据data.json里面的账号进行登陆，白天登陆本科生账号，晚上登陆研究生账号
  - logout：注销当前账号
  - loop：每隔一定时间检测网络情况，如果未连接互联网则调用login，如果检测到白天黑夜切换则调用logout
- http proxy，可选项
  - 可以设置为类似`http://127.0.0.1:8080`的URL，login和logout的请求会走这个http代理

## 配置文件

第一次运行如果没有配置文件，会自动在同级目录生成data.json

需要分别在登陆和注销时候抓取http请求包，把相应的字段填上去

```json
{
    "users":{
        "bachelor":{ 		# 本科生账号
            "user1":{
                "login":{ 		# 登陆时候抓包
                    "cookies":{}, 	# Cookies请求头
                    "data":"", 		# POST参数
                    "url":"" 		# 请求的URL
                },
                "logout":{ 		# 注销时抓包
                    "cookies":{},
                    "params":{}
                }
            }
        },
        "master":{ # 研究生账号
            "user1":{
                "login":{
                    "cookies":{},
                    "data":"",
                    "url":""
                },
                "logout":{
                    "cookies":{},
                    "params":{}
                }
            }
        }
    }
}
```



## 其他说明

1. 为啥要搞一个白天晚上登陆不同账号的功能呢？
   经检验，对于一个账号申请到的IP地址而言，本科生网络带宽比较大但是晚上断网，研究生晚上不断网但是网络带宽小

2. 在json文件里可以设置多个用户的账号以达到负载均衡（不是） 的目的
   比如某账号终端设备超限了，导致无法登陆的问题
3. 本脚本只提供程序，不提供上网账号
   上网账号还需自行通过合法手段获取
