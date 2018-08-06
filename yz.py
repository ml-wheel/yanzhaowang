# -*- coding:utf-8 -*-
# import pymysql
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
import importlib, sys

# importlib.reload(sys)  #PY3

reload(sys)  # PY2
sys.setdefaultencoding("utf-8")

# 学校
school_dict = {}
# 专业
ch_dicy = {}
# 考试科目
exam_dict = {}


# conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='yzw', charset='utf8')
# cursor = conn.cursor()

# 学科类别存库
# def save_db(id, name):
#         try:
#             sql = "insert into ch_info values(" + id + ",'" + name.encode("utf-8") + "')"
#             cursor.execute(sql)
#             conn.commit()
#         except Exception as e:
#             print(str(e))

# 学校类别存库
# def save_db(id, name,provinceid,province,feature):
#         try:
#             sql = "insert into school_info values(" + id + ",'" + name + "'+,"+provinceid+",'"+province+"','"+feature+"')"
#             cursor.execute(sql)
#             conn.commit()
#         except Exception as e:
#             print(str(e))

''' 获取 ID和名称  (085212)(专业学位)软件工程  ==> {085212 (专业学位)软件工程}'''
def getIdAndName(name):
    strs = name.split("(")[1].split(")")
    id=strs[0]
    name=strs[1]
    return id,name

def parse(url):
    # browser = webdriver.PhantomJS()#executable_path='D:\\phantomjs-2.1.1\\bin\\phantomjs.exe'
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(chrome_options=chrome_options,
                               executable_path="/Applications/Google Chrome.app/Contents/MacOS/chromedriver")
    browser.get(url)
    # time.sleep(1)
    # print(browser.page_source)
    for id in get_ch_info(browser):
        print("============id:" + id + "==============")
        # 单独调试专业
        # if id!='0351':
        #     continue
        Select(browser.find_element_by_id('yjxkdm')).select_by_value(id)
        for item in browser.find_elements_by_name("xxfs"):
            if item.get_attribute("class") == 'ch-select':
                Select(item).select_by_value("2")
        browser.find_element_by_class_name('blue-btn').click()
        # time.sleep(1)
        # 获取学校,所在地,院校特性,研究生院,自划线院校,博士点
        # yield scrapy.Request(browser.current_url, callback=self.parse_school)#这丫不行
        parse_school(browser, id)


# 获取学科类别
def get_ch_info(browser):
    ch_list = []
    sel = browser.find_elements_by_xpath('//select[@id="yjxkdm"]/option')
    for each in sel:
        ch = each.text
        if ch == "--选择学科类别--":
            continue
        ch_id = ""
        ch_name = ""
        chs = ch.split("(")[1].split(")")
        if len(chs) == 2:
            ch_id = chs[0]
            ch_name = chs[1]
        else:
            ch_id = chs[0]
            ch_name = ""
        ch_list.append(ch_id)
        # self.save_db(ch_id,ch_name)
    return ch_list


# 解析学校
def parse_school(browser, chid):
    for item in browser.find_elements_by_xpath('//table[@class="ch-table"]/tbody/tr'):
        school = item.text
        if school == '很抱歉，没有找到您要搜索的数据！':
            return
        school_id = school.split("\n")[0].split("(")[1].split(")")[0]
        school_name = school.split("\n")[0].split("(")[1].split(")")[1]
        school_province_id = school.split("\n")[1].split("(")[1].split(")")[0]
        school_province = school.split("\n")[1].split("(")[1].split(")")[1].split(" ")[0]
        school_feature = ""
        if len(school.split("\n")[1].split("(")[1].split(")")[1].split(" ")) > 1:
            school_feature = school.split("\n")[1].split("(")[1].split(")")[1].split(" ")[1]

        if not school_dict.has_key(school_id):
            school_dict[school_id] = {"school_province_id": school_province_id, "school_province": school_province,
                                      "school_feature": school_feature}
        # 学校信息存库
        # self.save_db(school_id,school_name,school_province_id,school_province,school_feature)
        # print(school_name + " " + school_feature)
        # 获取学校详细的专业信息，用不着翻页，直接传url
        url = item.find_element_by_tag_name('a').get_property("href")
        parse_subject(url, chid, school_id)
    # 处理翻页
    try:
        # print(browser.find_element_by_xpath('/html/body/div[2]/div[3]/div/div[4]/ul/li[7]/a').get_property('onclick'))
        browser.find_element_by_xpath('/html/body/div[2]/div[3]/div/div[4]/ul/li[7]/a').click()
        parse_school(browser, chid)
    except Exception as e:
        print("已到达最后一页!")


# 解析学校专业
def parse_subject(url, chid, school_id):
    # browser = webdriver.PhantomJS()#executable_path='D:\\phantomjs-2.1.1\\bin\\phantomjs.exe'
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(chrome_options=chrome_options,
                               executable_path="/Applications/Google Chrome.app/Contents/MacOS/chromedriver")
    browser.get(url)
    for item in browser.find_elements_by_xpath('/html/body/div[2]/div[3]/div/div[2]/table/tbody/tr'):
        tds = item.find_elements_by_tag_name('td')
        # #院系所
        # yxs=tds[0].text
        #专业
        zy=tds[1].text
        zyid,zyname = getIdAndName(zy)
        if not ch_dicy.has_key(zyid):
            ch_dicy[zyid]=zyname
        # #研究方向
        # yjfx=tds[2].text
        # #学习方式
        # xxfs=tds[3].text
        # #指导教师
        # zdls=tds[4].text
        # 考试范围
        examScopeUrl = tds[6].find_element_by_tag_name('a').get_attribute('href')

        parse_scope(zyid, school_id, examScopeUrl)


# 解析考试范围
def parse_scope(zyid, school_id, examScopeUrl):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(chrome_options=chrome_options,
                               executable_path="/Applications/Google Chrome.app/Contents/MacOS/chromedriver")
    browser.get(examScopeUrl)
    item = browser.find_element_by_xpath('/html/body/div[2]/div[3]/div[1]/div[1]/table/tbody')
    trs = item.find_elements_by_tag_name('tr')

    #拟招生人数
    studentsCount = trs[4].find_element_by_class_name('zsml-summary').text
    #招生源
    resouse = studentsCount.split(",")[0].split("：")[0]
    #总招人数
    totalCount = studentsCount.split(",")[0].split("：")[1]
    #推免人数
    tmCount = studentsCount.split(",")[1].split("：")[1]

    # 考试范围
    scopes = browser.find_elements_by_xpath('/html/body/div[2]/div[3]/div[1]/div[1]/div/table/tbody')
    for scope in scopes:
        examInfos = scope.find_elements_by_xpath('tr/td')
        if len(examInfos) != 4:
            continue
        # 政治
        zz = examInfos[0].text.split("\n")[0]
        zzid, name = getIdAndName(zz)
        if not exam_dict.has_key(zzid):
            exam_dict[zzid] = name
        # 英语
        yy = examInfos[1].text.split("\n")[0]
        yyid, name = getIdAndName(yy)
        if not exam_dict.has_key(yyid):
            exam_dict[yyid] = name
        # 业务一
        yw1 = examInfos[2].text.split("\n")[0]
        yw1id, name = getIdAndName(yw1)
        if not exam_dict.has_key(yw1id):
            exam_dict[yw1id] = name
        # 业务二
        yw2 = examInfos[3].text.split("\n")[0]
        yw2id, name = getIdAndName(yw2)
        if not exam_dict.has_key(yw2id):
            exam_dict[yw2id] = name


if __name__ == "__main__":
    parse("http://yz.chsi.com.cn/zsml/queryAction.do")
