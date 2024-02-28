# parser_saturn #
____
Процесс работы программы:

1. Парсятся ссылки на все каталоги внутри городов, их 217(на момент 5.11.2023). (по времени быстро, около минуты)
```python
all_catalogs_urls = collect_all_catalogs_url()
```
_____

2. Далее необходимо спарсить все ссылки на товары в каталогах, для полученияя ссылок на товары:
- Все каталоги делятся по 10 штук, и запускаются в цикле:
```python
splitted_catalog_urls = split_list(all_catalogs_urls, 10)
    for catalog_urls in tqdm.tqdm(splitted_catalog_urls, total=len(splitted_catalog_urls)):
```
этот цикл состоит из 3х частей: 

- Асинхронный парсинг html-страниц,
```python
        for catalog_url in catalog_urls:
            pages_texts_catalog_url = asyncio.create_task(parse_catalog_pages_texts(catalog_url))
            tasks.append(pages_texts_catalog_url)
        await asyncio.gather(*tasks)
```
  - Многопроцессорная обработка html страниц,
```python
with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
```

 - Запись результата.
```python
write_and_save_json('url_products.json', all_product_urls)
```

Время выполнения 2-го шага около 3х часов.

_____
3. Парсинг данных со страниц товаров.
Как и 2-ой шаг состоит из частей:
- Разделение всех ссылок на куски по 100 шт, запуск в цикле.
```python
splitted_urls = split_list(product_urls, 100)
    for product_urls in tqdm.tqdm(splitted_urls, total=len(splitted_urls)):
```
- Асинхронный парсинг html-страниц.
```python
        for product_url in product_urls:
            tasks.append(asyncio.create_task(parse_response_text(product_url)))
        await asyncio.gather(*tasks)
```
- Многопроцессорная обработка полученных страниц.
```python
        with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
            future_to_url = (executor.submit(parse_product, response_text.result()[0], response_text.result()[1]) for response_text in tasks)
```

Время работы этого шага около 10 часов.

Основная информация:
1. Время работы около 14 часов на момент последнего теста. Итоговый результат сохраняется в файле `result_saturn.json`
