# -*- coding: utf-8 -*-
import requests, re, json
from bs4 import BeautifulSoup
import http.cookiejar

base_headers={
    'Host': 'www.zhihu.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:44.0) Gecko/20100101 Firefox/44.0',
    'Referer': 'http://www.zhihu.com/',
    'Connection': 'keep-alive',
    'Origin': 'www.zhihu.com',
    'Pragma': 'no-chache',
    'X-Requested-With': 'XMLHttpRequest',
}

base_data={
    'remember_me': 'true',
}

def get_xsrf():
    url = 'http://www.zhihu.com'
    s = html.get(url, headers=base_headers, stream=True)
    xsrf = re.search(r'(?<=_xsrf" value=")[^"]*(?="/>)', s.text)
    if xsrf == None:
        return ''
    else:
        return xsrf.group(0)

def login():
    login_url = 'http://www.zhihu.com/login/email'
    email = input('Email: ')
    password = input('Password: ')

    base_data['email'] = email
    base_data['password'] = password
    c = html.post(login_url, headers=base_headers, data=base_data)
    html.cookies.save()

def get_user():
    global num

    user_url = 'http://www.zhihu.com/people/'           # 获得用户的关注者数
    id = input('Input the user id in url: ')
    user_page_url = user_url + id
    base_headers['Referer'] = 'http://www.zhihu.com/people/' + id + '/followers'
    user_page = html.get(user_page_url, headers=base_headers)
    soup = BeautifulSoup(user_page.text)
    followers_num = int(soup.find("div", "zm-profile-side-following zg-clear").find_all("a")[1].strong.string)

    if followers_num == 0:
        output.write('Followers\' number is 0\n')
        exit()
    else:
        followers_url = user_url + id + '/followers'          # 访问关注者页面
        base_headers['Referer'] = 'http://www.zhihu.com/people/' + id
        page = html.get(followers_url, headers=base_headers)
        html.cookies.save()
        soup = BeautifulSoup(page.text)

        url_list = soup.find_all("h2")          # url_list是包含当前页面所有关注者主页链接的list
        for item in url_list:
            num = num + 1

            href_p = re.findall(r'(?<=href=")[^"]*(?=" title)', str(item))      # 提取url
            href_p = str(href_p[0]) + '/about'                                  # 详细资料页面
            targt = html.get(href_p, headers=base_headers)
            soup = BeautifulSoup(targt.text)

            output.write(str(num) + '.' + ' ')
            try:
                output.write(soup.find("a", "name").string + '\n')
            except:
                pass
            output.write(href_p + '\n')

            bio = soup.find("span", "bio")              # 获取用户的biography
            b2 = soup.find("span", "content")
            try:
                if bio != None: output.write(bio.string + '\n')
            except:
                pass
            try:
                if b2 != None: output.write(b2.string.strip() + '\n')
            except:
                pass
            output.write('\n')

        if followers_num > 20:
            sum_ = int((followers_num - 1) / 20)        # 需要发包的总数

            next_url = 'http://www.zhihu.com/node/ProfileFollowersListV2'
            hash_id = re.search(r'(?<=data-id=")[^"]*(?=")', page.text)
            hash_id = hash_id.group(0)
            base_headers['Referer'] = followers_url

            for i in range(0, sum_):
                offset = 20 * (i + 1)
                params = json.dumps({"offset": offset, "order_by": "created", "hash_id": hash_id})
                next_data={
                    '_xsrf': xsrf,
                    'method': "next",
                    'params': params,
                }
                next_page = html.post(next_url, headers=base_headers, data=next_data, timeout=60)
                html.cookies.save()
                follower_list = next_page.json()["msg"]
                for one in follower_list:
                    num = num + 1

                    person = re.findall(r'(?<=href=")[^"]*(?=" class="zg-link")', str(one))
                    person = str(person[0]) + '/about'
                    targt = html.get(person, headers=base_headers, timeout=60)
                    soup = BeautifulSoup(targt.text)

                    output.write(str(num) + '.' + ' ')
                    try:
                        output.write(soup.find("a", "name").string + '\n')
                    except:
                        pass
                    output.write(person + '\n')

                    bio = soup.find("span", "bio")
                    b2 = soup.find("span", "content")
                    try:
                        if bio != None: output.write(bio.string + '\n')
                    except:
                        pass
                    try:
                        if b2 != None: output.write(b2.string.strip() + '\n')
                    except:
                        pass
                    output.write('\n')

if __name__ == '__main__':
    html = requests.session()
    html.cookies = http.cookiejar.LWPCookieJar('Cookie')
    # html.cookies.load(ignore_discard=True)
    email = None
    password = None
    id = None

    xsrf = get_xsrf()
    if xsrf == '':
        print('Try again..')
        exit()
    base_data['_xsrf'] = xsrf.encode('utf-8')
    num = 0
    login()
    path = input('Input output file path(eg:/Users/xx/Documents/xxx.txt): ')
    output = open(path, 'w')
    get_user()
    print('Program finished successfully.')
    output.close()
