import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import json
from tqdm import tqdm


# 请求头
def headers_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/51.0.2704.63 Safari/537.36'}
    req = urllib.request.Request(url=url, headers=headers)
    res = urllib.request.urlopen(req)
    html = res.read().decode('gbk', errors='ignore')
    return html


# 疾病名称，疾病所属科目(科室)、百科介绍、相关的疾病症状
def attr1_parser(html):
    # 页面
    soup = BeautifulSoup(html, 'html.parser')

    # 疾病的名称
    # 获取网页标签里的疾病名称
    symptom = soup.find(attrs={"class":"jb-name fYaHei gre"})
    symptom_name = symptom.get_text()

    # 所属科目(科室)
    category_list = []
    category_div = soup.find_all('div', attrs={'class': 'wrap mt10 nav-bar'})
    for a in category_div:
        category_a = a.find_all('a')
    for i in range(len(category_a)):
        category = category_a[i].text
        category_list.append(category)
    category_list = category_list[1:-1]

    # 疾病的百科介绍
    jieshao = soup.find(name='div',attrs={"class":"zz-articl fr f14"})
    jieshao_value = jieshao.get_text()
    jieshao_value = [jv.strip() for jv in jieshao_value.split('\n') if len(jv) > 10]
    jieshao_value = jieshao_value[0]

    # 相关的疾病症状
    xiangguan_zz_tag = soup.find(attrs={"class":"other-zz mt10"})
    xiangguan_zz_list = [xg_sym.get_text() for xg_sym in xiangguan_zz_tag.find_all('li')]

    return symptom_name, category_list, jieshao_value, xiangguan_zz_list

# 病因
def yuanyin_parser(html):
    yuanyin_soup = BeautifulSoup(html, 'html.parser')
    yuanyin_tag = yuanyin_soup.find_all(name='div', attrs={"class":"zz-articl fr f14"})
    yuanyin = []
    for p in yuanyin_tag:
        yuanyin_p = p.find_all('p')
    for i in range(len(yuanyin_p)):
        for yy in yuanyin_p[i].get_text().split('\n'):
            yy = yy.strip()
            if len(yy)>4:
                yuanyin.append(yy)
    return yuanyin

# 预防
def yufang_parser(html):
    yufang_html_soup = BeautifulSoup(html, 'html.parser')
    yufang_tag = yufang_html_soup.find(name='div',attrs={"class":"zz-articl fr f14"})
    yufang_p = yufang_tag.find_all('p')
    yufang = []
    for i in range(len(yufang_p)):
        for zd in yufang_p[i].get_text().split('\n'):
            zd = zd.strip()
            if len(zd) > 1:
                yufang.append(zd)
    return yufang

# 检查科目
def jiancha_parser(html):
    jiancha_soup = BeautifulSoup(html, 'html.parser')
    # print(xiangguan_zz_html.text)
    jiancha_zz = jiancha_soup.find_all('p', attrs={'class':'f12 mt5'})
    jiancha = []
    for i in range(len(jiancha_zz)):
        for jz in jiancha_zz[i].get_text().split():
            jiancha.append(jz)
    return jiancha

# 诊断
def zhenduan_parser(html):
    zhenduan_soup = BeautifulSoup(html, 'html.parser')
    zhenduan_tag = zhenduan_soup.find_all(name='div', attrs={"class":"zz-articl fr f14"})
    zhenduan = []
    for a in zhenduan_tag:
        zhenduan_a = a.find_all('a')
    # zhenduan_ = zhenduan_p[2].get_text()
    for i in range(len(zhenduan_a)):
        for zd in zhenduan_a[i].get_text().split('\n'):
            zd = zd.strip()
            if len(zd)>2:
                zhenduan.append(zd)
    return zhenduan


# 食疗
def food_parser(html):
    food_soup = BeautifulSoup(html, 'html.parser')
    do_food_tap = food_soup.find_all('div', attrs={'class':'diet-item clearfix'})
    do_eat = []
    for p in do_food_tap:
        food_p = p.find_all('p', attrs={'class':'diet-opac-txt pa f12'})
    for i in range(len(food_p)):
        for de in food_p[i].get_text().split('\n'):
            de = de.strip()
            do_eat.append(de)
    
    not_food_tap = food_soup.find_all('div', attrs={'class':'diet-item none'})
    not_eat = []
    for p in not_food_tap:
        food_p = p.find_all('p', attrs={'class':'diet-opac-txt pa f12'})
    for i in range(len(food_p)):
        for ne in food_p[i].get_text().split('\n'):
            ne = ne.strip()
            not_eat.append(ne)

    return do_eat, not_eat


# 药品
def drug_parser(html):
    drug_soup = BeautifulSoup(html, 'html.parser')
    drug_tap = drug_soup.find_all('a', attrs={'class':'gre mr10'})
    drug = []
    for i in range(len(drug_tap)):
        for dt in drug_tap[i].get_text().split('\n'):
            dt = dt.strip()
            drug.append(dt)
    
    return drug


# ------------------------------------------------------------ #
def save_json(symptom_tuple,yuanyin_list,yufang_list,jiancha_list,zhenduan_list,food_list,drug_list):
    symptom_name,category_list,jieshao_value,xiangguan_zz_list = symptom_tuple
    do_eat,not_eat = food_list
    data_format = {
        "name":symptom_name,                # 疾病学名
        "desc":jieshao_value,               # 疾病的百科介绍
        "cure_department":category_list,    # 科目（科室）
        "cause":yuanyin_list,               # 病因
        "prevent":yufang_list,              # 预防
        "check":jiancha_list,               # 检查科目
        "symptom":zhenduan_list,            # 症状（鉴别诊断）
        "accompany":xiangguan_zz_list,      # 相关症状
        "do_eat":do_eat,                    # 易食用的食物推荐
        "not_eat":not_eat,                  # 忌食用的食物列举
        "common_drug":drug_list             # 药物
    }

    with open('./data/medical_data.json','a+') as f:
        f.write(json.dumps(data_format, ensure_ascii=False))
        f.write('\n')
    

def spider_main(number):
    base_url = 'https://zzk.xywy.com/{page}_{attr}.html'

    # 循环爬取
    for page in tqdm(range(1, number)):

        # 疾病名称、疾病所属科目（科室）、疾病百科介绍、相关的疾病症状
        url = base_url.format(page=str(page),attr='jieshao')
        html = headers_html(url)
        symptom_tuple = attr1_parser(html)

        # 病因
        url = base_url.format(page=str(page),attr='yuanyin')
        html = headers_html(url)
        yuanyin_list = yuanyin_parser(html)

        # 预防
        url = base_url.format(page=str(page),attr='yufang')
        html = headers_html(url)
        yufang_list = yufang_parser(html)

        # 检查
        url = base_url.format(page=str(page),attr='jiancha')
        html = headers_html(url)
        jiancha_list = jiancha_parser(html)

        # 诊断
        url = base_url.format(page=str(page),attr='zhenduan')
        html = headers_html(url)
        zhenduan_list = zhenduan_parser(html)

        # 食疗
        url = base_url.format(page=str(page),attr='food')
        html = headers_html(url)
        food_list = food_parser(html)

        # 药品
        url = base_url.format(page=str(page),attr='yao')
        html = headers_html(url)
        drug_list = drug_parser(html)

        # 以json格式进行数据存储
        save_json(symptom_tuple, yuanyin_list, yufang_list, jiancha_list, zhenduan_list, food_list, drug_list)


if __name__ == '__main__':
    # 要爬取的疾病数量
    spider_main(50)