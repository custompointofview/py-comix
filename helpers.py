import random
import sys

PROXY_TEMPLATE = {
    "http": "http://{proxy}",
    "https": "http://{proxy}",
}


PROXIES_ANON_HIGH = [
    # Taken from: https://hidemy.name/en/proxy-list/?type=hs&anon=4#list
    # BAD
    "46.250.171.31:8080",
    "15.206.199.74:80",
    "138.197.157.32:8080",
    "185.134.23.198:80",
    "167.71.5.83:8080",
    "67.71.5.83:3128",
    "191.96.42.80:8080",
    "138.68.240.218:8080",
    "138.68.240.218:3128",
    "162.243.108.129:3128",
    "162.243.108.129:8080"
]

PROXIES_ANON_HIGH_FREEPROXYCZ = [
    # Taken from: http://free-proxy.cz/en/proxylist/country/all/http/ping/level1
    "54.156.164.61:80",
    "169.57.1.85:25",
    "200.52.141.162:53281",
    "207.157.220.8:8080",
    "80.48.119.28:8080",
    "167.172.125.148:3128",
    "181.118.167.104:80",
    "144.217.101.242:3129",
    "40.121.198.48:80",
    "82.200.233.4:3128",
]

PROXIES_ANON_HIGH_HIDE = [
    # Taken from https://www.hide-my-ip.com/proxylist.shtml
    "176.101.89.226:33470",
    "163.172.189.32:8811",
    "114.5.64.49:8080",
    "103.101.17.170:8080",
    "79.115.245.227:8080",
    "118.185.252.132:8080",
    "193.86.229.230:8080",
    "5.58.95.179:8080",
    "190.202.22.129:3128",
    "103.46.233.230:83"
]

PROXIES_FREE = [
    # Free proxies from free-proxy-list.net",
    # Updated at 2020-06-07 11:52:01 UTC.",

    "12.139.101.100:80",
    "62.106.122.90:36244",
    "159.138.22.112:443",
    "180.232.77.107:56392",
    "119.204.70.145:80",
    "12.139.101.96:80",
    "46.8.247.3:46285",
    "182.253.31.82:8080",
    "189.5.224.17:3128",
    "191.103.254.125:51869",
    "202.152.38.77:52740",
    "185.44.229.227:34930",
    "179.27.83.222:57096",
    "81.16.10.141:38132",
    "185.198.1.29:8080",
    "159.203.44.118:8080",
    "190.103.178.13:8080",
    "78.130.145.167:39825",
    "109.121.207.165:48834",
    "47.91.105.34:80",
    "115.240.134.44:3128",
    "200.89.178.156:80",
    "211.25.18.104:8080",
    "186.42.186.202:56569",
    "64.188.3.162:3128",
    "105.27.238.161:80",
    "82.200.233.4:3128",
    "105.29.64.217:80",
    "91.134.232.63:3128",
    "201.151.79.30:8080",
    "213.98.67.40:41005",
    "209.41.69.101:3128",
    "104.215.73.3:8080",
    "1.20.99.44:32119",
    "65.152.119.226:39408",
    "103.212.92.253:30138",
    "47.52.231.140:8080",
    "105.27.237.27:80",
    "103.233.198.156:8081",
    "91.226.5.245:49576",
    "45.165.131.12:8080",
    "117.121.211.170:8080",
    "87.140.113.225:3128",
    "186.159.2.241:43459",
    "103.143.196.26:8080",
    "136.228.128.6:41399",
    "3.249.236.176:3128",
    "118.69.140.108:53281",
    "51.158.123.250:8811",
    "204.15.243.233:58159",
    "51.158.98.121:8811",
    "103.194.242.254:60025",
    "85.21.63.219:53281",
    "78.140.7.239:51884",
    "27.50.18.42:23500",
    "103.122.248.45:8080",
    "103.251.57.23:60083",
    "189.127.106.16:53897",
    "105.29.64.222:80",
    "161.117.251.194:80",
    "46.175.185.239:36853",
    "190.103.178.14:8080",
    "45.230.8.20:51200",
    "36.68.208.93:8888",
    "47.244.50.83:80",
    "45.236.88.42:8880",
    "130.180.196.43:60540",
    "104.154.143.77:3128",
    "185.200.182.91:47868",
    "213.230.18.251:8080",
    "3.105.184.70:3128",
    "114.5.195.226:8080",
    "173.212.202.65:80",
    "201.55.164.31:3128",
    "176.62.185.72:59368",
    "40.121.198.48:80",
    "202.166.207.218:56576",
    "206.189.82.151:8080",
    "85.196.183.162:8080",
    "163.172.180.18:8811",
    "194.8.146.167:50510",
    "119.82.252.25:56874",
    "119.15.82.222:37790",
    "103.69.220.2:45155",
    "12.139.101.98:80",
    "197.89.175.235:8080",
    "51.158.123.35:8811",
    "46.229.67.198:47437",
    "193.188.254.67:53281",
    "181.168.206.106:38024",
    "94.244.28.246:31280",
    "197.211.238.220:54675",
    "95.168.96.42:34273",
    "91.211.172.104:55218",
    "186.159.8.218:48300",
    "182.75.59.66:55021",
    "79.129.117.118:32281",
    "185.32.165.78:8080",
    "45.151.169.254:8080",
    "178.213.130.159:60253",
    "27.147.210.35:8080",
    "41.215.134.139:8888",
    "182.74.174.107:80",
    "14.161.44.149:80",
    "181.102.86.103:7071",
    "79.230.56.173:8080",
    "37.135.50.75:53281",
    "103.216.82.198:6666",
    "200.106.55.125:80",
    "87.251.228.114:31793",
    "176.98.95.105:37783",
    "103.235.199.46:31611",
    "41.160.40.2:37741",
    "103.31.227.27:8080",
    "176.98.76.203:36651",
    "89.251.70.153:43716",
    "195.189.71.187:49495",
    "125.25.165.106:43730",
    "144.76.214.156:1080",
    "190.152.213.126:44523",
    "193.68.200.85:52825",
    "194.213.43.166:36683",
    "157.245.63.182:8118",
    "195.4.164.127:8080",
    "178.213.0.207:35140",
    "190.15.195.25:50630",
    "12.218.209.130:53281",
    "103.106.238.230:50941",
    "197.242.206.64:34576",
    "103.105.212.106:53281",
    "175.139.218.221:44454",
    "213.154.0.120:53281",
    "124.41.211.40:58720",
    "154.73.109.84:53281",
    "103.241.227.106:6666",
    "103.221.254.44:56471",
    "125.26.99.186:34577",
    "78.8.188.136:32040",
    "85.194.250.138:25834",
    "202.77.120.38:57716",
    "190.167.215.170:52479",
    "191.241.226.230:53281",
    "84.53.238.49:23500",
    "71.183.100.76:42413",
    "109.183.189.238:53959",
    "182.176.228.147:57472",
    "77.252.26.71:57348",
    "201.234.185.147:42226",
    "110.44.117.26:43922",
    "216.169.73.65:49627",
    "140.227.175.225:1000",
    "112.78.170.26:8080",
    "81.95.131.10:44292",
    "175.106.17.62:45864",
    "195.182.152.238:38178",
    "193.242.151.44:8080",
    "103.94.171.134:46276",
    "109.122.80.234:44556",
    "85.175.216.32:53281",
    "43.225.67.35:53905",
    "134.90.229.118:52972",
    "192.140.42.83:36124",
    "176.110.121.90:21776",
    "177.37.240.52:8080",
    "41.242.143.126:41632",
    "176.103.40.198:48892",
    "181.112.40.114:58123",
    "200.206.50.66:42515",
    "103.142.110.130:33405",
    "113.53.83.210:39695",
    "31.40.136.134:53281",
    "194.67.92.81:3128",
    "187.120.253.119:30181",
    "36.89.193.109:61737",
    "212.24.53.118:3128",
    "51.255.103.170:3129",
    "209.97.150.167:8080",
    "188.40.183.185:1080",
    "213.79.122.82:8080",
    "103.139.9.179:8080",
    "192.117.146.110:80",
    "188.40.183.187:1080",
    "94.73.234.169:55443",
    "89.36.195.238:39131",
    "188.40.183.190:1080",
    "5.59.141.152:61981",
    "88.198.24.108:8080",
    "210.48.204.134:46669",
    "188.226.141.211:3128",
    "169.57.157.146:8123",
    "119.81.199.80:8123",
    "118.175.207.25:38325",
    "159.8.114.37:8123",
    "159.8.114.34:8123",
    "77.222.152.137:54710",
    "85.10.219.101:1080",
    "185.204.208.78:8080",
    "41.164.247.250:38460",
    "91.241.152.125:53281",
    "36.83.26.76:8080",
    "45.12.110.174:31282",
    "1.20.97.122:44279",
    "47.75.90.57:80",
    "113.161.207.105:60626",
    "217.23.69.146:8080",
    "116.202.23.170:8080",
    "182.52.238.52:50619",
    "36.67.27.189:47877",
    "177.73.188.110:54459",
    "34.216.89.174:53281",
    "117.197.47.2:59823",
    "180.179.98.22:3128",
    "185.21.217.20:3128",
    "5.23.102.194:52803",
    "36.92.178.100:55443",
    "122.176.65.143:39059",
    "110.164.91.50:51065",
    "173.249.30.197:8118",
    "41.190.147.158:37010",
    "103.22.248.59:61661",
    "103.212.92.201:48111",
    "12.139.101.101:80",
    "91.226.35.93:53281",
    "103.221.254.2:44195",
    "195.138.73.54:59224",
    "46.35.249.189:32422",
    "180.178.102.174:55443",
    "213.96.26.70:53018",
    "187.73.68.14:53281",
    "1.10.189.107:33376",
    "129.226.50.76:8088",
    "103.15.140.139:44759",
    "36.89.194.113:38622",
    "183.87.153.98:49602",
    "114.199.111.162:80",
    "91.220.166.148:39915",
    "51.158.111.229:8811",
    "212.129.1.218:5836",
    "190.152.157.91:80",
    "187.177.139.8:8080",
    "95.65.73.200:60952",
    "96.9.77.71:8080",
    "103.129.192.218:41451",
    "182.53.197.87:53515",
    "155.0.181.254:31359",
    "156.67.117.66:8080",
    "36.66.235.147:57550",
    "177.136.168.13:49171",
    "197.98.180.89:39442",
    "200.229.236.114:37739",
    "31.173.94.93:31504",
    "178.252.80.226:35566",
    "185.23.128.180:3128",
    "103.220.207.17:42670",
    "118.27.1.165:60088",
    "171.103.139.126:43115",
    "178.134.208.126:50297",
    "180.250.153.129:53281",
    "45.235.163.35:33265",
    "12.139.101.97:80",
    "159.138.20.247:80",
    "194.228.129.189:61866",
    "103.42.253.210:38797",
    "109.232.106.236:35423",
    "95.143.8.182:57169",
    "93.185.96.60:41003",
    "202.79.56.90:23500",
    "109.238.222.5:45313",
    "36.89.10.51:34115",
    "105.27.238.160:80",
    "118.174.232.128:45019",
    "89.216.29.136:80",
    "1.20.100.227:57396",
    "103.74.70.142:35754",
    "159.138.1.185:80",
    "175.100.16.20:37725",
    "113.130.126.2:56605",
    "202.166.196.28:50153",
    "49.248.154.236:80",
    "196.216.220.204:36739",
    "91.108.136.219:53281",
    "175.212.226.57:80",
    "206.81.13.169:8080",
    "103.78.75.163:8080",
    "185.140.100.219:53281",
    "207.157.220.8:8080",
    "81.95.226.138:3128",
    "119.82.252.29:34661",
    "94.153.169.22:59177",
    "190.84.232.87:47295",
    "103.57.70.248:52000",
    "5.189.133.231:80",
    "89.189.172.88:8080",
    "118.70.12.171:53281",
    "185.134.23.198:80",
    "103.250.157.34:44611",
    "209.194.208.82:3128",
    "105.27.237.28:80",
    "12.139.101.102:80",
    "167.71.165.106:8080",
    "142.93.117.149:3128",
    "165.227.202.9:80",
    "140.82.61.218:8080",
    "192.241.137.194:8080",
    "161.35.114.60:8080",
    "107.191.41.188:8080",
    "64.227.25.67:8080",
    "159.203.44.177:3128",
    "34.86.63.83:3128",
    "50.206.25.104:80",
    "50.206.25.106:80",
    "50.206.25.108:80",
    "50.206.25.109:80",
    "50.206.25.111:80",
    "50.206.25.110:80",
    "50.206.25.107:80",
    "35.169.156.54:3128",
    "198.98.51.240:8080",
    "146.148.59.22:80",
    "68.188.59.198:80",
    "191.96.42.80:8080",
    "40.121.152.234:3128",
    "157.245.251.117:8080",
    "18.224.39.7:8080",
    "144.121.255.37:8080",
    "34.75.10.193:3128",
    "104.247.51.10:8080",
    "52.179.18.244:8080",
    "71.13.131.142:80",
    "34.95.11.2:8080",
    "54.156.164.61:80",
    "136.53.58.105:3128",
    "34.71.181.76:3128",
    "64.235.204.107:8080",
]


class HelperProxy:
    PROXY_LIST = PROXIES_ANON_HIGH_HIDE + PROXIES_ANON_HIGH_FREEPROXYCZ + PROXIES_ANON_HIGH

    def __init__(self):
        self.index = -1
        self.current_working = None
        random.seed(sys.maxsize)

    def get_next_index(self):
        self.index += 1
        if self.index == len(self.PROXY_LIST):
            self.index = 0
        return self.index

    def get_rand_index(self):
        self.index = random.randint(0, len(self.PROXY_LIST))

    def get_proxy(self):
        if self.current_working is not None:
            return self.current_working
        return self.get_rand_proxy()
        # return self.get_next_index()

    def get_rand_proxy(self):
        return random.choice(self.PROXY_LIST)

    def get_next_proxy(self):
        return PROXIES_FREE[self.get_next_index()]

    def reset_current_working_proxy(self):
        self.current_working = None

    def set_current_working_proxy(self, proxy):
        self.current_working = proxy


def print_error(msg):
    print("-" * 75)
    print("# Error:")
    print(str(msg))
    print("-" * 75)