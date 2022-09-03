import datetime
import re
import time
import json
import requests
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--from", help="yyyy-mm-dd")
parser.add_argument("--to", help="yyyy-mm-dd")
parser.add_argument("--days", type=int, default=365)
args = parser.parse_args()

s = requests.session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; x64; rv:105.0esr) Gecko/20010101 Firefox/105.0esr"})
anisearch_regex = r"""<a class="merchandise-item pointer" href=".*?" data-id="(.*?)" data-bg=".*?" title="(.*?)" rel="nofollow" target="_blank"><span class="gradient"><span class="details"><span class="title">.*?</span><span class="company">(.*?)</span>"""
anisearch_url = r"https://www.anisearch.de/merchandise/page-{page}?char=all&sort=date&order=asc&text=&date=99&startDate={dateFrom}&endDate={dateTo}&category=1&medium=2,4" # bd
#anisearch_url = r"https://www.anisearch.de/merchandise/page-{page}?char=all&sort=date&order=asc&text=&date=99&startDate={dateFrom}&endDate=2{dateTo}&category=1&medium=1" # dvd
dateFrom = datetime.date.today().strftime("%Y-%m-%d")
dateTo = (datetime.date.today() + datetime.timedelta(days=args.days)).strftime("%Y-%m-%d")
data = []

print("From:", dateFrom)
print("To:", dateTo)
print("Days:", args.days)

page = 1
while True:
    resp = s.get(anisearch_url.format(page=page, dateFrom=dateFrom, dateTo=dateTo))
    reed = re.findall(anisearch_regex, resp.text, flags=re.M)
    print(len(reed))
    for j in reed:
        data.append({"datum": j[2], "id": j[0], "name": j[1]})
    if len(reed) != 40:
        break
    page += 1
    time.sleep(5)

with open("data.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(data, indent=2))

with open("bds.txt", "w", encoding="utf-8") as f:
    for j in data:
        f.write(f"{j['datum']}\t{j['name']}\t{j['id']}\n")