import urllib.request
import csv
import re
from bs4 import BeautifulSoup
from datetime import datetime, date, time

import sys
import fileinput


baseUrl = 'https://coinmarketcap.com/currencies/<cryptoCurrency>/historical-data/?start=<startDateAsString>&end=<endDateAsString>'
reqheaders = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'
}


# def selectCrypto(url, crypto):
#     return url.replace("<cryptoCurrency>", crypto)


# def selectTimeInterval(url, start, end):
#     return url.replace("<startDateAsString>", start).replace("<endDateAsString>", end)

def convertDateTimeToString(date):
    day = '0' + str(date.day) if date.day < 10 else str(date.day)
    month = '0' + str(date.month) if date.month < 10 else str(date.month)
    year = str(date.year)
    return year + month + day


def createUrl(baseUrl, crypto, start, end):
    return baseUrl.replace("<cryptoCurrency>", crypto).replace("<startDateAsString>", start).replace("<endDateAsString>", end)


def accessWebsite(url, reqheaders):
    cryptoCurrency = "bitcoin"
    startTime = convertDateTimeToString(datetime(2019, 1, 1))
    endTime = convertDateTimeToString(datetime.now())
    site = createUrl(url, cryptoCurrency, startTime, endTime)
    req = urllib.request.Request(site, headers=reqheaders)
    try:
        page = urllib.request.urlopen(req)
        soup = BeautifulSoup(page, 'html.parser')
        tableHeader = soup.find("thead").find_all("tr")
        tableData = soup.find("tbody").find_all("tr")
        header = []
        data = [[]]
        for row in tableHeader:
            cells = row.find_all("th")
            for cell in cells:
                header.append(cell.get_text())
        for row in tableData:
            cells = row.find_all("td")
            rowData = []
            for cell in cells:
                rowData.append(cell.get_text())
            # convert first field from string date Nov 4, 2019 to yyyy/MM/dd
            rowData[0] = datetime.strptime(
                rowData[0], '%b %d, %Y').strftime('%Y/%m/%d')
            rowData[1:] = convertToFloat(rowData[1:])
            data.append(rowData)
        filename = cryptoCurrency+'_price_'+startTime+'_'+endTime+'.csv'
        with open(filename, 'w', newline='') as file:
            csvFileWriter = csv.writer(file, delimiter=',')
            csvFileWriter.writerow(header)
            for row in data:
                csvFileWriter.writerow(row)
        removeSymbolFromFile(filename)

    except Exception as e:
        print("An exception occurred")
        print(e)


def convertToFloat(listOfNumbers):
    return [float(i.replace(',', '')) for i in listOfNumbers]

# replace all occurrences of '"' with ''


def removeSymbolFromFile(filename):
    for i, line in enumerate(fileinput.input(filename, inplace=1)):
        sys.stdout.write(line.replace('\"', '').replace(
            '*', '').replace(
            ',', ', '))  # replace '"' and write ''


accessWebsite(baseUrl, reqheaders)
