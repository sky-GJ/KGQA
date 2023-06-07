# 医疗百科数据获取 寻医问药网（https://www.xywy.com）
import json
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from lxml import etree
from tqdm import tqdm

def get_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/51.0.2704.63 Safari/537.36'}
    req = urllib.request.Request(url=url, headers=headers)
    res = urllib.request.urlopen(req)
    html = res.read().decode('gbk', errors='ignore')
    return html


def main_parser(html):
    # 页面
    soup = BeautifulSoup(html, 'html.parser')

    # 疾病的名称
    # 获取网页标签里的疾病名称
    symptom = soup.find(attrs={"class":"jb-name fYaHei gre"})
    symptom_name = symptom.get_text()

    # 疾病的百科介绍
    jieshao = soup.find(name='div',attrs={"class":"zz-articl fr f14"})
    jieshao_value = jieshao.get_text()
    jieshao_value = [jv.strip() for jv in jieshao_value.split('\n') if len(jv) > 10]
    jieshao_value = jieshao_value[0]

    # 相关症状
    xiangguan_zz_tag = soup.find(attrs={"class":"other-zz mt10"})
    xiangguan_zz_list = [xg_sym.get_text() for xg_sym in xiangguan_zz_tag.find_all('li')]

    return symptom_name, jieshao_value,xiangguan_zz_list,

def attributes_parser(html):
    soup = BeautifulSoup(html, 'html.parser')
    attribute_tag = soup.find(name='div',attrs={"class":"zz-articl fr f14"})
    attribute = attribute_tag.find_all('p')[-1].get_text()
    return attribute.strip()

# 食疗
def food_parser(html):
    soup = BeautifulSoup(html, 'html.parser')
    food_tap = soup.find_all('p', attrs={'class':'fl diet-good-txt'})
    for i in range(len(food_tap)):
        if i == 0:
            good_food = [ft.strip() for ft in food_tap[i].get_text().split('\n')]
        else:
            no_food = [ft.strip() for ft in food_tap[i].get_text().split('\n')]
    
    return good_food, no_food


def dump_json(symptom_tuple,all_attr_value_list,food_list):
    symptom_name,jieshao_value,xiangguan_zz_list = symptom_tuple
    do_eat, not_eat = food_list
    data_format = {
        "name":symptom_name,
        "jieshao":jieshao_value,
        "xiangguan_zz":xiangguan_zz_list,
        "do_eat":do_eat,
        "not_eat":not_eat
    }
    for item in all_attr_value_list:
        # print(item.items())
        for attr, attr_value in item.items():
            data_format[attr] = attr_value

    with open('./data/medical_data.json','a+') as f:
        f.write(json.dumps(data_format, ensure_ascii=False))
        f.write('\n')


def run(num_page):
    base_url = 'https://zzk.xywy.com/{page}_{attr}.html'
    attri_list = ['yuanyin','yufang','jiancha','zhenduan']
    for page in tqdm(range(1, num_page)):
        all_attr_value_list = []
        for attr in attri_list:
            # attri_list类别的页面
            url = base_url.format(page=str(page),attr=attr)
            # 请求头
            html = get_html(url)
            # 爬取的文本
            attr_value = attributes_parser(html)
            # 字典形式存储数据{类别:值}
            all_attr_value_list.append({attr:attr_value})
            # print(all_attr_value_list)


        url = base_url.format(page=str(page),attr='jieshao')
        html = get_html(url)
        symptom_tuple = main_parser(html)

        url = base_url.format(page=str(page),attr='food')
        html = get_html(url)
        food_list = food_parser(html)
        
        dump_json(symptom_tuple,all_attr_value_list, food_list)


if __name__ == '__main__':
    run(10)