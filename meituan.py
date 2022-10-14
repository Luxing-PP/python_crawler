import json
import time

import requests
import sys

import excel

api = {
    "queryFeedback": 'https://ecom.meituan.com/emis/gw/rpc/TFeedbackEcomService/queryFeedback?_tm={}',
    "getFeedbackSummary": 'https://ecom.meituan.com/emis/gw/rpc/TFeedbackEcomService/getFeedbackSummary?_tm={}',
    "getCityPoiIndex": 'https://ecom.meituan.com/meishi/gw/rpc/home/-/TEcomOperationDataService/getCityPoiIndex?_tm={}'
}

ONE_DAY_IN_MS = 86400000


def date2TimeStampMS(date: str = None):
    if date is None:
        return int(time.time() * 1000)
    t1 = time.mktime(time.strptime(date, "%Y-%m-%d"))
    time_in_s = t1 * 1000
    return int(time_in_s)


class MeiTuanCrawler():
    def __init__(self, cookie):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
            "Cookie": cookie
        }

    def getAllTimeSummary(self):
        print("执行 总的评价获取")
        header = ['店名', '均分', '口味', '环境', '服务', '好评率', '总评论数', '好评数', '中差评数']
        res = [header]

        data = self.getCityPoiIndex(date2TimeStampMS())
        for name, poiId in data:
            print('获取 {} 信息中...'.format(name))
            row = [name] + list(self.getFeedbackSummary(date2TimeStampMS(), poiId))
            time.sleep(0.1)  # 避免反爬
            res.append(row)

        excel.create(rows=res)
        print("完成")

    def getPeriodSummary(self, s, e):
        print("执行 {} - {} 的评价获取".format(s, e))
        header = ['店名', '总评论数', '好/差评数']
        res = [header]
        data = self.getCityPoiIndex(date2TimeStampMS())
        for name, poiId in data:
            print('获取 {} 信息中...'.format(name))
            # good bad
            total, good, good_comment, bad, bad_comment = self.queryFeedback(s, e, poiId)
            row_g = [name + '好评', total, good] + good_comment
            row_b = [name + '差评', total, bad] + bad_comment
            res.append(row_g)
            res.append(row_b)
            time.sleep(0.1)  # 避免反爬

        excel.create(res, s, e)
        print("完成")

    def queryFeedback(self, s, e, poiId):
        url = api[sys._getframe().f_code.co_name]
        url = url.format(date2TimeStampMS())

        good, bad = 0, 0
        good_comment, bad_comment = [], []
        # platform 0 美团 1 点评
        body = {
            "pageInfo": {
                "limit": 50,
                "total": 0,
                "offset": 0
            },
            "platform": 1,
            "queryPara": {
                "platform": 1,
                "startTime": date2TimeStampMS(s),
                "endTime": date2TimeStampMS(e) + ONE_DAY_IN_MS - 1,
                "starTag": -1,
                "referTag": 0,
                "poiId": poiId,
                "poiIdLong": poiId
            }
        }
        response = requests.post(url, headers=self.headers, json=body, verify=False)
        data = json.loads(response.content)['data']
        if data['feedbacks'] is None:
            return 0, good, good_comment, bad, bad_comment

        total, feedbacks = data['total'], data['feedbacks']
        if total > 50:
            print("没爬全，呆滞没有想到你真的能碰到这么多评论，可以申请一个返工")

        for f in feedbacks:
            if f['score'] <= 3.5:
                bad += 1
                bad_comment.append(f['content'])
            else:
                good += 1
                good_comment.append(f['content'])

        return total, good, good_comment, bad, bad_comment

    def getCityPoiIndex(self, timeStamp):
        """
        :return (店铺名，poiId)
        """
        url = api[sys._getframe().f_code.co_name]
        url = url.format(timeStamp)

        response = requests.get(url, headers=self.headers, verify=False)
        data = json.loads(response.content)['data']
        data = list(filter(lambda d: d['cityName'] == "深圳市", data))[0]
        pois = data['pois']
        poi_info = list(map(lambda p: [p['poiName'], p['poiId']], pois))

        return poi_info

    def getFeedbackSummary(self, timeStamp, poiId):
        url = api[sys._getframe().f_code.co_name]
        url = url.format(timeStamp)

        # platform 0 美团 1 点评
        body = {
            "platform": 1,
            "queryPara": {
                "platform": 1,
                "startTime": -1,
                "endTime": -1,
                "starTag": -1,
                "businessTag": "-1",
                "poiId": poiId,
                "poiIdLong": poiId
            }
        }

        response = requests.post(url, headers=self.headers, json=body, verify=False)
        data = json.loads(response.content)['data']
        avg, sub_score, total, bad, good = data['avgScore'], data['subScores'], data['totalCount'], data['badCount'], \
                                           data['goodCount']
        sorted(sub_score, key=lambda score: score['name'])
        return avg, sub_score[0]['score'], sub_score[1]['score'], sub_score[2][
            'score'], good / 1.0 / total, total, bad, good


if __name__ == '__main__':
    crawler = MeiTuanCrawler('sda')
    crawler.getFeedbackSummary('203131')
