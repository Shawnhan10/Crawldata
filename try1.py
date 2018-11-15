import requests
from bs4 import BeautifulSoup
import json
import time
import redis
import jieba
import wordcloud
# 第二次思路：定义一个函数，爬取以"http://leetcode-cn.com/problems/"为base_url的网页
#       余下的字符串由正则表达式进行匹配


# 第三次思路：定义一个函数，用于在"https://leetcode-cn.com/problemset/all/"网页中爬取
# 每个题目的href，然后在定义一个next_url = 'https://leetcode-cn.com/problems/'+'href'+
# /description/'即可，然后再爬取每个next_url里面的题目描述。

# 第四次思路：定义一个函数，用于在'https://leetcode-cn.com/api/problems/all/'网页中获取
# 或者用正则表达式去匹配每个问题的名字与id存储在两个list里面
# 再定义一个函数去将'http://leetcode-cn.com/problems/'与之前爬取的每个问题的名字经行连接
# 就可以进入这个题目的描述了

# this is a test

# 函数意义：获得url的源码并返回，以便于下一步解析
def get_html(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        }
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            print('error!'+response.status_code)
    except Exception:
        print('error!!!!!!!!')

# 函数意义：用jsoon解析源码并存储到data列表中，
# 并将解析出来的data按顺序放到urls中并返回urls，以便下一步调用
def get_data(html):
    parse_html = json.loads(html) #将html页面的json数据进行解析
    data = [] #定义一个data列表
    urls = [] #定义一个url列表
    for i in range(667):
        #从json数据中提取出我们需要的题目名称，放入列表
        data.append(parse_html['stat_status_pairs'][i]['stat']['question__title_slug'])
        #将名称与基础url经行组合，放入列表
        urls.append('https://leetcode-cn.com/problems/'+data[i])
    return urls

# 函数意义：利用循环将urls中的每个url都解析出来，
# 并将title和description放到data字典中，并在下一步将数据放入数据库中
# 本来想用yield，但是不会用，就放弃啦
#
def save_data(url_list):
    # 构建一个list
    data_list = []
    for i in range(667):
        resp = requests.get(url_list[i])
        # 休眠一秒，减少服务器压力
        time.sleep(1)
        soup = BeautifulSoup(resp.text,'lxml')
        # 获取title
        title = soup.title.string
        # 获取description
        description = soup.find(attrs={"name": "description"})['content'].replace('&quot;','').\
            replace('&nbsp;','').replace('&lt;','<')
        # 将title和descripton放入list中
        dict = {title+'\n',description}
        data_list.append(dict)
    return data_list

def save_file(data):
    filename = '爬取的数据.txt'
    f = open(filename, 'w', encoding='utf-8')
    for i in data:
        f.writelines(list(i))
    f.close()
    f = open('爬取的数据.txt', "r", encoding='utf-8')
    t = f.read()
    f.close()
    ls = jieba.lcut(t)
    txt = " ".join(ls)
    w = wordcloud.WordCloud(font_path='simsun.ttc', width=1000, height=700, background_color="white")
    w.generate(txt)
    w.to_file("crawldatacloud.png")
    return None


# def main():
r= redis.Redis(host='127.0.0.1',port=6379,db=0)
url = 'https://leetcode-cn.com/api/problems/all/'
html = get_html(url)
url_list = get_data(html)
data = save_data(url_list)
save_file(data)
for i in range(5):
    r.set(i,data)
print('successful!')

# if __name__ == '__main__':
#     main()
