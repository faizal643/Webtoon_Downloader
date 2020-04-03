import json
import time

import requests
from bs4 import BeautifulSoup as bs4

import module.shared as shared
from module.gethtml import getHtml
from module.makeurl import makeUrl


def getImgNo(op, webtoonId, viewNo, cookie):
    if (op == 'naver' or op == 'nbest' or op == 'nchall') and (not viewNo in shared.html):
        getHtml(op, webtoonId, viewNo, cookie)
    if (op == 'daum') and (not viewNo in shared.html):
        getHtml(op, webtoonId, viewNo, cookie)
    if op == 'naver' or op == 'nbest' or op == 'nchall':
        soup = bs4(shared.html[viewNo], 'html.parser')
        for img_tag in soup.select('.wt_viewer img'):
            if not viewNo in shared.imgUrl:
                shared.imgUrl.update({viewNo: list()})
            shared.imgUrl[viewNo].append(img_tag['src'])
        shared.imgNo.update({viewNo: len(soup.select('.wt_viewer img'))})
        return len(soup.select('.wt_viewer img'))
    if op == 'daum':
        if shared.htmlLst[viewNo] == -1:
            shared.imgNo.update({viewNo: 0})
            return 0
        js = json.loads(shared.htmlLst[viewNo])
        for img_tag in js['data']:
            if not viewNo in shared.imgUrl:
                shared.imgUrl.update({viewNo: list()})
            shared.imgUrl[viewNo].append(img_tag['url'])
        shared.imgNo.update({viewNo: len(js['data'])})
        return len(js['data'])


def downImgWorker(op, webtoonId, viewNo, cutNo, cookie):
    if not viewNo in shared.imgUrl:
        getImgNo(op, webtoonId, viewNo, cookie)
    cookies = dict()
    if cookie != None:
        if op == 'naver':
            cookies = {'NID_AUT': cookie._auth, 'NID_SES': cookie._sess}
        if op == 'daum':
            cookies = {'HM_CU': cookie._hm_cu, 'HTS': cookie._hts, 'PROF': cookie._prof, 'TS': cookie._ts,
                       'LSID': cookie._lsid}
    else:
        cookies = None
    headers = {'Referer': makeUrl(op, webtoonId, viewNo)}
    try:
        image_file_data = requests.get(shared.imgUrl[viewNo][cutNo], headers=headers, cookies=cookies).content
    except:
        image_file_data = -1
    return image_file_data


def downImg(op, webtoonId, viewNo, cutNo, cookie):
    while True:
        td = downImgWorker(op, webtoonId, viewNo, cutNo, cookie)
        if td == -1:
            time.sleep(0.5)
            continue
        return td


def saveImg(op, webtoonId, viewNo, cutNo, saveName, cookie):
    with open(saveName, 'wb') as out:
        out.write(downImg(op, webtoonId, viewNo, cutNo, cookie))