import datetime
import re
import time
import json
import datetime
import pyperclip
import requests
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--from", help="yyyy-mm-dd")
parser.add_argument("--to", help="yyyy-mm-dd")
parser.add_argument("--update", action="store_true")
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

def __locale_change(string: str):
    return string.replace("Januar ", "January ")\
        .replace("Februar ", "February ")\
        .replace("März ", "March ")\
        .replace("Mai ", "May ")\
        .replace("Juni ", "June ")\
        .replace("Juli ", "July ")\
        .replace("Oktober ", "October ")\
        .replace("Dezember ", "December ")\

def parse_time(time_str):
    time_str = __locale_change(time_str)
    return int(datetime.datetime.strptime(time_str, r"%B %Y" if time_str.count(" ") == 1 else r"%d. %B %Y").timestamp())


if args.update:
    blacklist_pid = ["120073", "119095", "124509", "115478", "109314"]
    clipboard = pyperclip.paste()
    clipboard_dict = {}
    for i in clipboard.splitlines():
        i = i.split("\t", 3)
        clipboard_dict[i[2]] = {"datum": i[0], "id": i[2], "name": i[1], "comment": i[3], "unix": parse_time(i[0])}
    for i in data:
        if i["id"] in blacklist_pid:
            continue
        if i["id"] in clipboard_dict:
            clipboard_dict[i["id"]]["datum"] = i["datum"]
            clipboard_dict[i["id"]]["name"] = i["name"]
            clipboard_dict[i["id"]]["unix"] = parse_time(i["datum"])
        else:
            clipboard_dict[i["id"]] = {"datum": i["datum"], "id": i["id"], "name": i["name"], "comment": "FALSE", "unix": parse_time(i["datum"])}

    sort_dict = {}
    for i in clipboard_dict:
        if clipboard_dict[i]["unix"] not in sort_dict:
            sort_dict[clipboard_dict[i]["unix"]] = []
        sort_dict[clipboard_dict[i]["unix"]].append(i)


    copy = ""
    for i in sorted(sort_dict):
        for j in sort_dict[i]:
            copy += f'{clipboard_dict[j]["datum"]}\t{clipboard_dict[j]["name"]}\t{clipboard_dict[j]["id"]}\t{clipboard_dict[j]["comment"]}\n'
    pyperclip.copy(copy)
    print("FALSE/TRUE zu Checkboxen umwandeln: https://infoinspired.com/wp-content/uploads/2018/10/convert-true-false-to-tick-box.gif")