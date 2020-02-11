from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup

import time
import requests


def init(id, pwd):
    import pickle
    with open('./auth/user.dat', 'wb') as f:
        pickle.dump([id, pwd], f)


def load(dat_path):
    import pickle
    with open(dat_path, 'rb') as f:
        account = pickle.load(f)
    return account[0], account[1]


def login():

    library_url = 'https://library.hanyang.ac.kr/#/login'
    id, pwd = load('./auth/user.dat')

    #driver = webdriver.Chrome('./chromedriver')
    driver = webdriver.Safari(executable_path = '/usr/bin/safaridriver')

    # 백남학술정보관 접속
    driver.get(library_url)

    # 백남학술정보관 로그인
    driver.find_element_by_name("userid").send_keys(id)
    element = driver.find_element_by_name("password")
    element.send_keys(pwd)
    element.send_keys(Keys.RETURN)

    time.sleep(3)
    driver.get('https://library.hanyang.ac.kr/')
    driver.implicitly_wait(10)
    return driver


def getURL(target_url, driver=None, selinum=False,  hyu=False):

    if hyu and selinum:
        driver.implicitly_wait(5)
        base_url = "https://access.hanyang.ac.kr/link.n2s?url="
        driver.get(base_url+target_url)
        html = driver.page_source
        return html

    elif selinum:
        driver.get(target_url)
        html = driver.page_source
        return html

    else:
        html = requests.get(target_url)
        return html


def getDriver():
    driver = webdriver.Chrome('./chromedriver')
    #driver = webdriver.Safari(executable_path='/usr/bin/safaridriver')
    return driver


def parsing(html):
    return ""


if __name__ == '__main__':
    import time
    driver = getDriver()

    idx = 0
    target_url = 'https://scholar.google.co.kr/scholar?q=%22chb-mit%22%2C+%22seizure+detection%22&start={}&as_ylo=2019'
    target_url = target_url.format(idx)
    html = getURL(target_url, driver, selinum=True, hyu=False)
    print(html.status_code, html)
    soup = BeautifulSoup(html.text, 'html.parser')

    nop = soup.find_all('div', attrs={'class': 'gs_ab_mdw'})
    print(nop)
    nop = nop[-1].text.replace('검색결과 약 ', '').split('개')[0]

    title = []
    link = []
    author = []
    for idx in range(0, int(nop), 10):
        target_url = 'https://scholar.google.co.kr/scholar?q=%22chb-mit%22%2C+%22seizure+detection%22&start={}&as_ylo=2019'
        target_url = target_url.format(idx)
        html = getURL(target_url, selinum=False, hyu=False)

        soup = BeautifulSoup(html.text, 'html.parser')

        h3s = soup.find_all('h3', attrs={'class':'gs_rt'})
        divs = soup.find_all('div', attrs={'class': 'gs_a'})

        for num, (h3, div) in enumerate(zip(h3s, divs)):
            title.append(h3.text)
            link.append(h3.a['href'])
            author.append(div.text)

        time.sleep(1)

    import pandas as pd

    df = pd.DataFrame({
        '제목':title,
        'URL':link,
        '저자':author
    })
    df.to_excel('./검색결과.xlsx')
