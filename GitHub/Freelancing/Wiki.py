from lxml import html
import requests
import wikipedia
language = "ru"
wikipedia.set_lang(language)
first =[]
second = []
third = []

n = 'Nintendo 3DS'
page = requests.get('https://ru.wikipedia.org/wiki/Xbox_360_S')
tree = html.fromstring(page.content)
links = tree.xpath('//p/a/@href')
title = tree.xpath('//p/a/@title')

for link in links:
    first.append('https://ru.wikipedia.org/' + link)

if n in title:
    exit()
else:
    for i in first:
        print('1------------------------')
        content = wikipedia.page('Xbox 360 S').content
        a = (content.find(title[first.index(i)][1]))
        b = (content[a:].find('.')) + a + 1
        c = (content[:a].find('.'))
        f = (content[a::-1])

        if c >= 0:
            print(content[c:b])
        else:
            c = 0
            print(content[c:b])

        s = title[first.index(i)]
        print(i)

        page = requests.get(i)
        tree = html.fromstring(page.content)
        links = tree.xpath('//p/a/@href')
        title = tree.xpath('//p/a/@title')

        for link in links:
            second.append('https://ru.wikipedia.org/' + link)
            if n in second:
                exit()
            else:
                continue

        if n in title:
            print('2------------------------')
            content = wikipedia.page(s).content
            a = (content.find(n))
            b = (content[a:].find('.')) + a + 1
            f=(content[a::-1])
            f = f.index('.')
            f = a-f + 31
            print(content[f:b])

            for link in links:
                third.append('https://ru.wikipedia.org/' + link)
                if n in second:
                    print(third)
                    exit()
                else:
                    continue

            print(third[title.index(n)])
            exit()
