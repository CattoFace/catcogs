import requests
from bs4 import BeautifulSoup

baseURL = 'http://maplestory.nexon.net'
site = requests.get(baseURL + '/news/update#news-filter')
soup = BeautifulSoup(site.content, 'html.parser')
news = soup.find('ul', class_='news-container rows').find_all('div', class_='text')
for entry in news:
    title = entry.find('a')
    if ('Patch Notes' in title.text):
        entryPage = requests.get(baseURL + title['href'])
        entrySoup = BeautifulSoup(entryPage.text, 'html.parser').find('div', class_='component component-news-article').find(lambda tag: tag.name == 'span' and '2x EXP & Drop' in tag.text).find_next('p')
        for time in entrySoup:
            print(time.text)
        break
