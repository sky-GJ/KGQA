# 医疗百科数据获取 寻医问药网（https://www.xywy.com）
import json
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from tqdm import tqdm

def get_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/51.0.2704.63 Safari/537.36'}
    req = urllib.request.Request(url=url, headers=headers)
    res = urllib.request.urlopen(req)
    html = res.read().decode('gbk', errors='ignore')
    return html

# 疾病名称，疾病所属科目(科室)、百科介绍
def attr1_parser(html):
    # 页面
    soup = BeautifulSoup(html, 'html.parser')

    # 疾病的名称
    # 获取网页标签里的疾病名称
    name = soup.find('div', attrs={'class':'jb-name fYaHei gre'})
    symptom_name = name.get_text()

    # 所属科目(科室)
    category_list = []
    category_div = soup.find('div',attrs={'class': 'wrap mt10 nav-bar'})
    category_a = category_div.find_all('a')
    for i in range(len(category_a)):
        category = category_a[i].text
        category_list.append(category)
    category_list = category_list[1:-1]

    # 疾病的百科介绍
    jieshao = soup.find('div', attrs={'class':'jib-articl-con jib-lh-articl'})
    jieshao = jieshao.find('p')
    jieshao = jieshao.get_text()
    jieshao = jieshao.strip()
    return symptom_name, category_list, jieshao

# 病因
def cause_parser(html):
    cause_soup = BeautifulSoup(html, 'html.parser')
    cause_tep = cause_soup.find('div', attrs={'class':'jib-articl fr f14 jib-lh-articl'})
    cause_p = cause_tep.find_all('p')
    cause = []
    for i in range(len(cause_p)):
        for cs in cause_p[i].get_text().split('\n'):
            cs = cs.strip()
            if len(cs) > 7:
                cause.append(cs)
    return cause

# 预防
def prevent_parser(html):
    prevent_soup = BeautifulSoup(html, 'html.parser')
    prevent_tag = prevent_soup.find(name='div',attrs={"class":"jib-articl fr f14 jib-lh-articl"})
    prevent_p = prevent_tag.find_all('p')
    prevent = []
    for i in range(len(prevent_p)):
        for yf in prevent_p[i].get_text().split('\n'):
            yf = yf.strip()
            if len(yf) > 1:
                prevent.append(yf)
    return prevent

# 并发症
def neopathy_parser(html):
    neopathy_soup = BeautifulSoup(html, 'html.parser')
    neopathy_tep = neopathy_soup.find('div', attrs={'class':'jib-articl fr f14 jib-lh-articl'})
    neopathy_a = neopathy_tep.find_all('a')
    neopathy = []
    for i in range(len(neopathy_a)):
        for a in neopathy_a[i].get_text().split('\n'):
            bfz = a.strip()
            neopathy.append(bfz)
    return neopathy

# 症状
def symptom_parser(html):
    symptom_soup = BeautifulSoup(html, 'html.parser')
    symptom_div = symptom_soup.find('div', attrs={'class': 'jib-articl fr f14 jib-lh-articl'})
    symptom_a = symptom_div.find_all('a', attrs={'class': 'gre'})
    symptom = []
    for i in range(len(symptom_a)):
        for sy in symptom_a[i].get_text().split('\n'):
            sy = sy.strip()
            symptom.append(sy)
    return symptom

# 检查科目
def inspect_parser(html):
    inspect_soup = BeautifulSoup(html, 'html.parser')
    inspect_div = inspect_soup.find('div', attrs={'class':'jib-articl fr f14 jib-lh-articl'})
    inspect_p = inspect_div.find_all('p')
    inspect = []
    for i in range(len(inspect_p)):
        for it in inspect_p[i].get_text().split('\n'):
            it = it.strip()
            if len(it)>2:
                inspect.append(it)
    return inspect

def food_parser(html):
    food_soup = BeautifulSoup(html, 'html.parser')
    # 宜吃食品
    do_food_tap = food_soup.find_all('div', attrs={'class':'diet-item none clearfix'})
    do_eat = []
    for p in do_food_tap:
        food_p = p.find_all('p', attrs={'class':'diet-opac-txt pa f12'})
    for i in range(len(food_p)):
        for de in food_p[i].get_text().split('\n'):
            de = de.strip()
            do_eat.append(de)

    not_food_tap = food_soup.find('div', attrs={'class':'diet-item none'})
    nf_p = not_food_tap.find_all('p', attrs={'class':'diet-opac-txt pa f12'})
    not_eat = []
    # for p in not_food_tap:
    #     nf_p = p.find_all('p', attrs={'class':'diet-opac-txt pa f12'})
    for i in range(len(nf_p)):
        for ne in nf_p[i].get_text().split('\n'):
            ne = ne.strip()
            not_eat.append(ne)
    
    return do_eat, not_eat

# 药品
def drug_parser(html):
    drug_soup = BeautifulSoup(html, 'html.parser')
    drug_tap = drug_soup.find_all('div', attrs={'class':'city-item'})
    drug = []
    for p in drug_tap:
        drug_p = p.find_all('div', attrs={'class':'fl drug-pic-rec mr30'})
    for a in drug_p:
        drug_a = a.find('a', attrs={'class':'gre mr10'})
    for i in range(len(drug_p)):
        for dt in drug_p[i].find('a',attrs={'class':'gre mr10'}).get_text().split('\n'):
            dt = dt.strip()
            if len(dt)>4:
                drug.append(dt)
    
    return drug


# ------------------------------------------------------------ #
def save_json(symptom_tuple, cause_list, prevent_list, neopathy_list, symptom_list, inspect_list, food_list, drug_list):
    symptom_name,category_list,jieshao_value = symptom_tuple
    do_eat,not_eat = food_list
    data_format = {
        "name":symptom_name,                # 疾病学名
        "desc":jieshao_value,               # 疾病的百科介绍
        "cure_department":category_list,    # 科目（科室）
        "cause":cause_list,                 # 病因
        "neopathy":neopathy_list,           # 并发症
        "prevent":prevent_list,             # 预防
        "check":inspect_list,               # 检查科目
        "symptom":symptom_list,             # 症状
        "do_eat":do_eat,                    # 易食用的食物推荐
        "not_eat":not_eat,                  # 忌食用的食物列举
        "common_drug":drug_list             # 药物
    }

    with open('./data/medical_data.json','a+', encoding="utf8") as f:
        f.write(json.dumps(data_format, ensure_ascii=False))
        f.write('\n')

def run(num_page):
    base_url = 'https://jib.xywy.com/il_sii/{attr}/{page}.htm'

    for page in tqdm(range(1, num_page)):
        # 疾病名称、疾病所属科目（科室）、疾病百科介绍
        url = base_url.format(page=str(page),attr='gaishu')
        html = get_html(url)
        symptom_tuple = attr1_parser(html)

        # 病因
        url = base_url.format(page=str(page),attr='cause')
        html = get_html(url)
        cause_list = cause_parser(html)

        # 预防
        url = base_url.format(page=str(page),attr='prevent')
        html = get_html(url)
        prevent_list = prevent_parser(html)

        # 并发症
        url = base_url.format(page=str(page),attr='neopathy')
        html = get_html(url)
        neopathy_list = neopathy_parser(html)

        # 并发症
        url = base_url.format(page=str(page),attr='symptom')
        html = get_html(url)
        symptom_list = symptom_parser(html)

        # 检查
        url = base_url.format(page=str(page),attr='inspect')
        html = get_html(url)
        inspect_list = inspect_parser(html)

        # 食疗
        url = base_url.format(page=str(page),attr='food')
        html = get_html(url)
        food_list = food_parser(html)

        # 药品
        url = base_url.format(page=str(page),attr='drug')
        html = get_html(url)
        drug_list = drug_parser(html)

        # 以json格式进行数据存储
        save_json(symptom_tuple, cause_list, prevent_list, neopathy_list, symptom_list, inspect_list, food_list, drug_list)



if __name__ == '__main__':
    run(10)