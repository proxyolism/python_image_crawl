# -*- coding: utf-8 -*-
import json
import os
import urllib.request
import socket
import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from datetime import datetime

# 다운로드 소켓유통기한 설정.
socket.setdefaulttimeout(100)

# 이미지 카운트
getlink_succounter = 0  # 이미지 링크 따오는 것이 성공한 횟수
getfile_succounter = 1  # 해당 이미지 링크에서 다운로드 하는 것이 성공한 횟수

# 최대 수집할 이미지 갯수 정의, 수집하지 않을 이미지 사이즈 정의
maxcollectnum = 3000
maximagewidth = 100
maximageheight = 100

# input.txt에서 크롤링할 인물 명단 가져오기
fin = open("input1.txt", mode='r', encoding='utf-8-sig')

# 저장할 PATH설정
now = datetime.now()
nowstr = str(now.year) + str(now.month).zfill(2) + str(now.day).zfill(2) + '_' + str(now.hour).zfill(2) + str(
    now.minute).zfill(2) + str(now.second).zfill(2)

PATH = "Z:\\collectionadd20200227\\" + nowstr + "\\"

'''
#인물검색어정의는 매개변수로 받음.
#실행방법 : python test.py "안정환"
searchterm = sys.argv[1]
'''

# 화면로그 출력과 파일로그 출력을 동시에 수행하기 위한 print정의
def customprint(fout, *data):
    now = datetime.now()
    out = str(data)
    out = out.replace('\'', '')
    out = out.replace(',', '')
    out = out.replace('(', '')
    out = out.replace(')', '')
    print('[' + str(now.year) + '-' + str(now.month).zfill(2) + '-' + str(now.day).zfill(2) + ' ' + str(now.hour).zfill(
        2) + ':' + str(now.minute).zfill(2) + ':' + str(now.second).zfill(2) + ']' + out)
    fout.write(
        '[' + str(now.year) + '-' + str(now.month).zfill(2) + '-' + str(now.day).zfill(2) + ' ' + str(now.hour).zfill(
            2) + ':' + str(now.minute).zfill(2) + ':' + str(now.second).zfill(2) + ']' + out + '\n')

# 크롤링 작업 전체에 대한 로그 파일 기록
if not os.path.isdir(PATH):
    # os.mkdir(searchterm)
    os.makedirs(PATH)
    fout = open(PATH + "crawler_log.txt", 'a')

# 구글 이미지 크롤링
def googlecrawl(searchterm, imgdirname, imgname):
    global getlink_succounter, getfile_succounter, PATH

    # 로그용 파일 생성.
    # fout = open(searchterm + "\\" + searchterm + "_result.txt", mode='a', encoding='UTF-8')
    fout = open(PATH + imgdirname + "\\" + "debug_result.txt", mode='a', encoding='UTF-8')
    fout_ = open(PATH + imgdirname + "\\" + "dbinput_result.txt", mode='a', encoding='UTF-8')

    customprint(fout, '------------------------google crawls starts!--------------------------')
    if getfile_succounter > maxcollectnum:
        customprint(fout, 'number of crawl images overs number of max collect numbers. stop crawls.')
        customprint(fout, '------------------------google crawls completed!--------------------------')
        fout.close()
        fout_.close()
        return

    ################################################################################################################
    ################################################################################################################
    url = "https://www.google.com/search?q=" + searchterm + "&source=lnms&tbm=isch"
    # chrome webdriver 사용하여 브라우저를 가져온다.
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    browser = webdriver.Chrome('./chromedriver', chrome_options=options)
    #   browser = webdriver.Chrome('./chromedriver')
    #   browser.set_page_load_timeout(15)
    browser.get(url)

    # User-Agent를 통해 봇이 아닌 유저정보라는 것을 위해 사용
    header = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}

    customprint(fout, os.path)
    customprint(fout, "Selenium started!")
    for _ in range(500):
        # 가로 = 0, 세로 = 10000 픽셀 스크롤한다.
        browser.execute_script("window.scrollBy(0,10000)")

    # 스크롤 로딩을 기다린 후, 결과더보기(id는 smb)버튼이 활성화 될 때까지 기다린 후, 뜨면 클릭
    try:
        wait = WebDriverWait(browser, 20)
        # element = wait.until(EC.element_to_be_clickable((By.ID, 'smb')))
        element = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@type="button"]')))
        element.click()
    except:
        customprint(fout, "there is no click element!")

    for _ in range(500):
        # 가로 = 0, 세로 = 10000 픽셀 스크롤한다.
        browser.execute_script("window.scrollBy(0,10000)")
    ################################################################################################################
    ################################################################################################################

    # div태그에서 class name이 rg_meta인 것을 찾아온다
    for x in browser.find_elements_by_xpath('//div[contains(@class,"rg_meta")]'):
        if getfile_succounter > maxcollectnum:
            customprint(fout, 'number of crawl images overs number of max collect numbers. stop crawls.')
            customprint(fout, '------------------------naver crawls completed!--------------------------')
            fout.close()
            fout_.close()
            browser.close()
            return

        getlink_succounter += 1

        googleimgurl = json.loads(x.get_attribute('innerHTML'))["ou"]  # 이미지 url
        googleimgtype = json.loads(x.get_attribute('innerHTML'))["ity"]  # 이미지 확장자
        googleimgwidth = json.loads(x.get_attribute('innerHTML'))["oh"] # 이미지 세로길이
        googleimgheight = json.loads(x.get_attribute('innerHTML'))["ow"] # 이미지 가로길이

        # 특정 이미지 사이즈 이하 다운로드 스킵
        if googleimgwidth <= maximagewidth or googleimgheight <= maximageheight:
            continue

        customprint(fout, "")
        customprint(fout, "Total Count:", getlink_succounter)
        customprint(fout, "URL : ", googleimgurl)

        # 확장자가 jpg나 png인 것 만 수집하도록 한다.
        if googleimgtype == "jpg" or googleimgtype == "png" or googleimgtype == "jpeg":
            try:
                # 이미지 저장 시도
                # urllib.request.urlretrieve(googleimgurl , searchterm + "\\" + str(getfile_succounter) + "." + googleimgtype)
                # urllib.request.urlretrieve(googleimgurl , PATH + searchterm + "\\" + str(getfile_succounter) + "." + googleimgtype)
                urlopen(googleimgurl)
                urllib.request.urlretrieve(googleimgurl,
                                           PATH + imgdirname + "\\" + imgname + str(getfile_succounter).zfill(
                                               4) + "." + googleimgtype)
            except HTTPError as e:
                customprint(fout, 'Error! Error code : ', e.code)
                continue
            except URLError as e:
                customprint(fout, 'Error! Error Reason : ', e.reason)
                continue
            except socket.error as e:
                customprint(fout, 'Error! Socket remotely disconnected. work continues..')
                continue
            except UnicodeEncodeError as e:
                continue
            except Exception as e:
                continue
            else:
                customprint(fout, "Succsessful Count:", getfile_succounter)
                fout_.write(
                    imgname + str(getfile_succounter).zfill(4) + '.' + googleimgtype + '\t' + googleimgurl + '\n')
                fout_.flush()

                getfile_succounter = getfile_succounter + 1

    customprint(fout, '------------------------google crawls completed!--------------------------')
    browser.close()
    fout.close()
    fout_.close()

def navercrawl(searchterm, imgdirname, imgname):
    global getlink_succounter, getfile_succounter, PATH

    # 로그용 파일 생성.
    # fout = open(searchterm + "\\" + searchterm + "_result.txt", mode='a', encoding='UTF-8')
    fout = open(PATH + imgdirname + "\\" + "debug_result.txt", mode='a', encoding='UTF-8')
    fout_ = open(PATH + imgdirname + "\\" + "dbinput_result.txt", mode='a', encoding='UTF-8')

    # 네이버 이미지 검색 추가 ----------------------------------------------------------------------------------
    customprint(fout, '------------------------naver crawls starts!--------------------------')
    if getfile_succounter > maxcollectnum:
        customprint(fout, 'number of crawl images overs number of max collect numbers. stop crawls.')
        fout.close()
        fout_.close()
        return

    client_id = "####################"
    client_secret = "#######################"
    encText = urllib.parse.quote(searchterm)

    beforequerytotal = 0

    # json 출력 유도. 쿼리 당 이미지 100개 추출 가능하므로, 1000장 수집시 10번 요청해야함. 좀 넉넉히 20번 쿼리 요청... 어차피 1천장 채워지면 그만둠.
    for val in range(0, 9):
        # query1 -> 1~100 , query2 -> 101~200 ... query 10 -> 901~1000
        startidx = val * 100 + 1
        if startidx == 1001:
            startidx = startidx - 1
        # print("startidx --------- " + str(startidx))

        # start 매개변수 범위 : 1 ~1000, 1000을 넘으면 400 request가 return 된다. 1000 넘지 않도록 주의!
        url = "https://openapi.naver.com/v1/search/image?query=" + encText + "&display=100&start=" + str(startidx)
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        try:
            response = urllib.request.urlopen(request)
        except Exception:
            continue

        rescode = response.getcode()
        response_body = response.read()

        jsonin = json.loads(response_body.decode('utf-8'))

        if jsonin["display"] == 0:
            customprint(fout, 'naver crawls completed!')
            fout_.close()
            fout.close()
            return

        # 이전 토탈값과 동일하다면 startidx는 다르지만 같은 이미지의 json리스트를 가져오므로, 수집을 중단한다.
        print("jsonin_display----" + str(jsonin["display"]))
        if (jsonin["display"] != 100) and (beforequerytotal == jsonin["display"]):
            customprint(fout, 'naver crawls completed!')
            fout.close()
            fout_.close()
            return

        beforequerytotal = jsonin["display"]

        for val in range(0, jsonin["display"] - 1):
            if getfile_succounter > maxcollectnum:
                customprint(fout, 'number of crawl images overs number of max collect numbers. stop crawls.')
                customprint(fout, '------------------------naver crawls completed!--------------------------')
                fout.close()
                fout_.close()
                return

            getlink_succounter += 1
            naverimageurl = jsonin["items"][val]["link"]

            customprint(fout, "")
            customprint(fout, "Total Count:", getlink_succounter)
            customprint(fout, "URL : " + naverimageurl)

            # 확장자만 추출
            naverimgtype = naverimageurl[-4] + naverimageurl[-3] + naverimageurl[-2] + naverimageurl[-1]
            naverimgtype = naverimgtype.replace(".", "")

            # 확장자가 jpg나 png인 것 만 수집하도록 한다.
            if naverimgtype == "jpg" or naverimgtype == "png" or naverimgtype == "jpeg":
                try:
                    # 특정 이미지 사이즈 이하 다운로드 스킵
                    image = Image.open(urllib.request.urlopen(naverimageurl))
                    imgwidth, imgheight = image.size
                    if imgwidth <= maximagewidth or imgheight <= maximageheight:
                        continue

                    # 이미지 저장 시도
                    urllib.request.urlretrieve(naverimageurl,
                                               PATH + imgdirname + "\\" + imgname + str(getfile_succounter).zfill(
                                                   4) + "." + naverimgtype)
                except HTTPError as e:
                    customprint(fout, 'Error! Error code : ', e.code)
                    continue
                except URLError as e:
                    customprint(fout, 'Error! Error Reason : ', e.reason)
                    continue
                except socket.error as e:
                    customprint(fout, 'Error! Socket remotely disconnected. work continues..')
                    continue
                except UnicodeEncodeError as e:
                    continue
                except Exception as e:
                    continue
                else:
                    customprint(fout, "Succsessful Count:", getfile_succounter)

                    fout_.write(
                        imgname + str(getfile_succounter).zfill(4) + '.' + naverimgtype + '\t' + naverimageurl + '\n')
                    fout_.flush()

                    getfile_succounter = getfile_succounter + 1

    customprint(fout, '------------------------naver crawls completed!--------------------------')
    fout.close()
    fout_.close()


def daumcrawl(searchterm, imgdirname, imgname):
    global getlink_succounter, getfile_succounter, PATH

    # 로그용 파일 생성.
    # fout = open(searchterm + "\\" + searchterm + "_result.txt", mode='a', encoding='UTF-8')
    fout = open(PATH + imgdirname + "\\" + "debug_result.txt", mode='a', encoding='UTF-8')
    fout_ = open(PATH + imgdirname + "\\" + "dbinput_result.txt", mode='a', encoding='UTF-8')

    # 다음 이미지 검색 추가 ----------------------------------------------------------------------------------
    customprint(fout, '------------------------daum crawls starts!--------------------------')
    if getfile_succounter > maxcollectnum:
        customprint(fout, 'number of crawl images overs number of max collect numbers. stop crawls.')
        customprint(fout, '------------------------daum crawls completed!--------------------------')
        fout.close()
        fout_.close()
        return

    #client_ak = "KakaoAK ####################"
    encText = urllib.parse.quote(searchterm)

    beforequerytotal = 0

    # json 출력 유도. 쿼리 당 이미지 80개 추출 가능, 최대 50페이지까지 제한.
    for page in range(1, 50):
        url = "https://dapi.kakao.com/v2/search/image?query=" + encText + "&sort=accuracy&size=80&page=" + str(page)
        request = urllib.request.Request(url)
        header = {'authorization':'KakaoAK ####################'}
        r = requests.get(url, headers=header)
        jsonin = json.loads(r.text)

        finalpage = jsonin["meta"]["is_end"] # False or True
        print("finalpage : " + str(finalpage))
        for inpage in range(1, len(jsonin["documents"])):
            if getfile_succounter > maxcollectnum:
                customprint(fout, 'number of crawl images overs number of max collect numbers. stop crawls.')
                customprint(fout, '------------------------daum crawls completed!--------------------------')
                fout.close()
                fout_.close()
                return

            getlink_succounter += 1
            daumimageurl = jsonin["documents"][inpage]["image_url"]

            # 특정 이미지 사이즈 이하 다운로드 스킵
            if jsonin["documents"][inpage]["width"] <= maximagewidth or jsonin["documents"][inpage]["height"] <= maximageheight:
                continue;

            customprint(fout, "")
            customprint(fout, "Total Count:", getlink_succounter)
            customprint(fout, "URL : " + daumimageurl)

            # 확장자만 추출
            daumimageurlsplit = daumimageurl.split('?')
            newdaumimageurl = daumimageurlsplit[0]

            daumimgtype = newdaumimageurl[-4] + newdaumimageurl[-3] + newdaumimageurl[-2] + newdaumimageurl[-1]
            daumimgtype = daumimgtype.replace(".", "")
            # 확장자가 jpg나 png인 것 만 수집하도록 한다.
            if daumimgtype == "jpg" or daumimgtype == "png" or daumimgtype == "jpeg":
                try:
                    # 이미지 저장 시도
                    urlopen(daumimageurl)
                    urllib.request.urlretrieve(daumimageurl, PATH + imgdirname + "\\" + imgname + str(getfile_succounter).zfill(4) + "." + daumimgtype)
                except HTTPError as e:
                    customprint(fout, 'Error! Error code : ', e.code)
                    continue
                except URLError as e:
                    customprint(fout, 'Error! Error Reason : ', e.reason)
                    continue
                except socket.error as e:
                    customprint(fout, 'Error! Socket remotely disconnected. work continues..')
                    continue
                except UnicodeEncodeError as e:
                    continue
                except Exception as e:
                    continue
                else:
                    customprint(fout, "Succsessful Count:", getfile_succounter)

                    fout_.write(
                        imgname + str(getfile_succounter).zfill(4) + '.' + daumimgtype + '\t' + daumimageurl + '\n')
                    fout_.flush()

                    getfile_succounter = getfile_succounter + 1

        if finalpage:
            customprint(fout, '------------------------daum crawls completed!--------------------------')
            fout.close()
            fout_.close()
            return;

    customprint(fout, '------------------------daum crawls completed!--------------------------')
    fout.close()
    fout_.close()

for searchterm in fin:
    searchterm = searchterm.replace("\n", "")
    # KPC0000001 쥬리 로켓펀치
    searchterm = searchterm.replace("\t", "_")
    # KPC0000001_쥬리_로켓펀치
    splitword = searchterm.split("_")
    # splitword[0] : KPC0000001
    # splitword[1] : 쥬리
    # splitword[2] : 로켓펀치

    searchterm = splitword[1] + " " + splitword[2]
    # searchterm : 쥬리 로켓펀치

    imgdirname = splitword[0] + "_" + splitword[1] + "_01";
    # imgdirname : KPC0000001_쥬리_01

    imgname = splitword[0] + "_o_";
    # imgname : KPC0000001_o_

    # 소스코드가 있는 경로에 '검색어' 폴더가 없으면 만들어준다.(이미지 저장 폴더를 위해서), 그리고 폴더가 있다면 루틴을 수행하지 않는다.
    # if not os.path.exists(searchterm):
    if not os.path.isdir(PATH + imgdirname):
        # os.mkdir(searchterm)
        os.makedirs(PATH + imgdirname)
        customprint(fout, searchterm + "-------------- Crawling start!------------")

        googlecrawl(searchterm, imgdirname, imgname)
        navercrawl(searchterm, imgdirname, imgname)
        daumcrawl(searchterm, imgdirname, imgname)

        customprint(fout, searchterm + "-------------- Crawling completed! number of crawled images : " + str(getfile_succounter - 1) + "------------------")

        getlink_succounter = 0  # 이미지 링크 따오는 것이 성공한 횟수 - 초기화
        getfile_succounter = 1  # 해당 이미지 링크에서 다운로드 하는 것이 성공한 횟수 - 초기화
    else:
        customprint(fout, searchterm + "has already its folder! skipped and work goes on...")
        continue

customprint(fout, "All of Crawling job Completed!")
fin.close()