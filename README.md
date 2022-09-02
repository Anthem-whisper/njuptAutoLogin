# njuptAutoLoginScript

南京邮电大学校园网（NJUPT、CMCC、ChinaNet）自动登录脚本

## 使用方式

```bash
pip install -r  requirements.txt
python njuptAutoLogin.py <action> [http proxy]
```

参数：
- action，必须项
  - login: 根据data.json里面的账号进行登陆，白天登陆本科生账号，晚上登陆研究生账号
  - logout: 从配置文件或server获取当前登录账号并注销
  - loop: 每隔一定时间(30s左右)检测网络情况，如果未连接互联网则调用login，如果检测到白天黑夜变化(9:40-11:00)则切换用户
- http proxy，可选项
  - 可以设置为类似`http://127.0.0.1:8080`的URL，login和logout的请求会走这个http代理，可用于debug

示例: 
```
python3 njuptAutoLogin.py loop http://127.0.0.1:8080
```

  > 首次运行的时候，需要保证是连接到校园网并且处于**未登录**的状态，脚本会自动获取网络信息并写入配置文件

## 配置文件

第一次运行会自动在同级目录生成`data.json`

如果账号是CMCC，就直接在账号后面加@cmcc，ChinaNet就加@njxy，保证每个账号的键和account值一致

```json
{
    "users":{
        "bachelor":{
            "Bxxxxxxx@njxyc":{
                "account":"Bxxxxxxx@njxy",
                "password":"123456"
            }
        },
        "master":{
            "123456@cmcc":{
                "account":"123456@cmcc",
                "password":"123456"
            }
        }
    },
    "netinfo":{
        "serverip":"10.10.244.11",
        "redictip":"6.6.6.6",
        "clientip":"",
        "wlanacip":"",
        "wlanacname":"",
        "selected_user":{},
        "selected_group":""
    }
}
```

## 其他说明

1. 为啥要搞一个白天晚上登陆不同账号的功能呢？
   经检验，对于一个账号申请到的IP地址而言，本科生网络带宽比较大但是晚上断网，研究生晚上不断网但是网络带宽小

2. 在json文件里可以设置多个用户的账号以达到负载均衡（不是） 的目的。比如某账号终端设备超限了，导致无法登陆的问题
   
3. 本脚本只提供程序，不提供上网账号，上网账号还需自行通过**合法**手段获取
