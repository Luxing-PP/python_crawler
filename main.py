import argparse
import os
import time
import excel
import warnings

from meituan import MeiTuanCrawler

warnings.filterwarnings('ignore')

parser = argparse.ArgumentParser()
parser.add_argument("--cookie", "-c", type=str)
parser.add_argument("--mode", "-m", type=str)
parser.add_argument("--start", "-s", type=str)
parser.add_argument("--end", "-e", type=str)

COOKIE_PATH = "./cookie.txt"

if __name__ == '__main__':
    if not os.path.exists(COOKIE_PATH):
        print("Error cookie.txt not exist 确认是否和cookie.txt在同一目录下")
        exit(1)
    cookie = open(COOKIE_PATH, 'r', encoding='utf-8').readline()
    crawler = MeiTuanCrawler(cookie)

    args = parser.parse_args()
    if args.start is None or args.end is None:
        mode = int(input("输入你想要的模式 1.全量查询 2.时间段查询 :"))
        if mode == 1:
            crawler.getAllTimeSummary()
        elif mode ==2:
            s = str(input("输入起始日期 格式类似于 2022-09-24 :"))
            e = str(input("输入结束日期 格式类似于 2022-09-26 :"))
            crawler.getPeriodSummary(s, e)
        else:
            print("谜之输入:"+mode)
    else:
        crawler.getPeriodSummary(args.start, args.end)

