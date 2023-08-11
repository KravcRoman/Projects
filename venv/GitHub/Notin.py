import json
import requests
from datetime import datetime, timedelta

api_key = "1325a1187397ac9acc691f6f6ed03501"
campaign_id = []
#token = "secret_y1ZaHWAI3mt6HKCYPca77eJg9MWmkJQBbvONb7ZFiSi"
token = 'secret_fNY94BddqsYeT3wHPfxFciP3fDNWL05bkXt5zQQHDLx'
#DATABASE_ID = "38d85cfe199f44a3bff514ef94f5a11b"
DATABASE_ID = 'ae6fc36661594af88e7690a61f93eee7'
#Page_id = ['4f803ab7-dc6e-4d27-be37-66ff0ef538f1', '0473334a-f6af-49da-b0dc-169accf9f05f']
#Page_id = ['b17583e3-6f08-4bc2-9973-2691e94ff047', '0a3bd4df-664e-42ff-8a41-7fa2755ba235', '05e020d2-c8b1-4c53-9c52-932c967564b7']
page_id = []
a = 0
from_date = []
to_date = datetime.now().date()


headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "Notion-Version": "2021-05-13"
    }

# Получаем страницы
def get_pages(num_pages=None):

    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    payload = {"page_size": 100}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()

    results = data["results"]
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        results.extend(data["results"])

    return results

pages = get_pages()

for page in pages:
    #page_id = page["id"]
    props = page["properties"]
    #id = props["campaign_id"]["title"][0]["text"]["content"]
    id = props["campaign_id"]["number"]
    fd = props["Date"]["date"]["start"]
    from_date.append(fd)
    campaign_id.append(id)
    page_id.append(page["id"])

# Получаем id кампаний
def get_campaign_stats(campaign_id):
    # Создаем API request
    global a
    #dateFormatter = "%Y-%m-%d"
    #tomorrow = (datetime.strptime(from_date[a], dateFormatter)) + timedelta(days=2)
    tomorrow = to_date + timedelta(days=1)
    url = f"https://zvonok.com/manager/cabapi_external/api/v1/phones/camp_stats/?public_key={api_key}&campaign_id={campaign_id[a]}&from_date={from_date[a]}&to_date={tomorrow}"
    #print(url)
    response = requests.get(url)
    todos = json.loads(response.text)

    # Парсинг запроса статистики
    for item in todos['data']['call_statuses']:
        # if item['status'] == 'all':
        #     total_calls = item['count']
        if 'all' in item['status']:
            total_calls = item['count']
            break
        else:
            total_calls = 0
    for item in todos['data']['dial_statuses']:
        if len(todos['data']['dial_statuses']) > 5:
            if item['status'] == 'all':
                 completed_calls = item['count']
        else:
            completed_calls = 0
    for item in todos['data']['call_statuses']:
        if 'in_process' in item['status']:
            in_process_calls = item['count']
            break
        else:
            in_process_calls = 0
    for item in todos['data']['call_statuses']:
        # if item['status'] == '1':
        #     ivr1_calls = item['count']
        if '1' in item['status']:
            ivr1_calls = item['count']
            break
        else:
            ivr1_calls = 0
    for item in todos['data']['call_statuses']:
        # if item['status'] == '2':
        #     ivr2_calls = item['count']
        if '2' in item['status']:
            ivr2_calls = item['count']
            break
        else:
            ivr2_calls = 0

    # Вторая ссылка для вывода 1 дня
    url2 = f'https://zvonok.com/manager/cabapi_external/api/v1/phones/cost/?campaign_id={campaign_id[a]}&public_key={api_key}'
    #print(url2)
    response2 = requests.get(url2)
    todos2 = json.loads(response2.text)

    if 'daily_cost' in todos2:
        daily_sum = float(todos2['daily_cost'])
    else:
        daily_sum = 0

    if 'forever_cost' in todos2:
        total_sum = float(todos2['forever_cost'])
    else:
        total_sum = 0

    # Расчет дополнительной статистики
    cpl = total_sum / ivr1_calls
    ctr = ivr1_calls / completed_calls * 100
    progress = completed_calls / total_calls * 100
    quality = ivr1_calls * 100 / (ivr1_calls + ivr2_calls)

# # Создание файла для чтения таблицы
# def readDatabase(DATABASE_ID, headers):
#     readUrl = f'https://api.notion.com/v1/databases/{DATABASE_ID}/query'
#
#     res = requests.request("POST", readUrl, headers=headers)
#     data = res.json()
#     print(res.status_code)
#
#     with open("./db.json", 'w', encoding='utf8') as f:
#         json.dump(data, f, ensure_ascii=False)
#
# readDatabase(DATABASE_ID, headers)


## Создание новых страниц в таблице
#     def createOage(DATABASE_ID, headers):
#
#         createUrl = 'https://api.notion.com/v1/pages'
#
#         newPageData = {
#             "parent": {'database_id': DATABASE_ID },
#             'properties': {
#                 # 'campaign_id':{
#                 #     'title': [
#                 #         {
#                 #             'text': {
#                 #                 'content': campaign_id[a]
#                 #             }
#                 #         }
#                 #     ]
#                 # },
#                 # "from_date": {
#                 #     "type": "str",
#                 #     "date": from_date
#                 # },
#                 # "to_date": {
#                 #     "type": "str",
#                 #     'date': to_date
#                 # },
#                 "Всего звонков": {
#                     "type": "number",
#                     "number": total_calls
#                 },
#                 'Совершенных': {
#                     "type": "number",
#                     'number': completed_calls
#                 },
#                 'В процессе звонков': {
#                     "type": "number",
#                     'number': in_process_calls
#                 },
#                 'ivr 1': {
#                     "type": "number",
#                     'number': ivr1_calls
#                 },
#                 'ivr 2': {
#                     "type": "number",
#                     'number': ivr2_calls
#                 },
#                 'Сумма за день': {
#                     "type": "number",
#                     'number': daily_sum
#                 },
#                 'Сумма всего': {
#                     "type": "number",
#                     'number': total_sum
#                 },
#                 'CPL': {
#                     "type": "number",
#                     'number': cpl
#                 },
#                 'CTR': {
#                     "type": "number",
#                     'number': ctr
#                 },
#                 'Прогресс': {
#                     "type": "number",
#                     'number': progress
#                 },
#                 'Качество': {
#                     "type": "number",
#                     'number': quality
#                 }
#             }
#         }
#
#         data = json.dumps(newPageData, indent=4, sort_keys=True, default=str)
#         # with open("./db.json", 'w', encoding='utf8') as f:
#         #     json.dump(data, f, ensure_ascii=False)
#         res = requests.request("POST", createUrl, headers=headers, data=data)
#
#         print(res.status_code)
#         print(res.text)
#     createOage(DATABASE_ID, headers)

    # Обновляем значения ячеек в таблице
    def updatePage(page_id, headers):

        # Id кампаний в таблице
        #Page_id = ['4f803ab7-dc6e-4d27-be37-66ff0ef538f1', '0473334a-f6af-49da-b0dc-169accf9f05f']
        #Page_id = ['b17583e3-6f08-4bc2-9973-2691e94ff047', '0a3bd4df-664e-42ff-8a41-7fa2755ba235', '05e020d2-c8b1-4c53-9c52-932c967564b7']
        updateUrl = f"https://api.notion.com/v1/pages/{page_id[a]}"

        updateData = {
            "properties": {
                "Всего звонков": {
                    "type": "number",
                    "number": total_calls
                },
                'Совершенных': {
                    "type": "number",
                    'number': completed_calls
                },
                'В процессе звонков': {
                    "type": "number",
                    'number': in_process_calls
                },
                'ivr 1': {
                    "type": "number",
                    'number': ivr1_calls
                },
                'ivr 2': {
                    "type": "number",
                    'number': ivr2_calls
                },
                'Сумма за день': {
                    "type": "number",
                    'number': daily_sum
                },
                'Сумма всего': {
                    "type": "number",
                    'number': total_sum
                },
                'CPL': {
                    "type": "number",
                    'number': cpl
                },
                'CTR': {
                    "type": "number",
                    'number': ctr
                },
                'Прогресс': {
                    "type": "number",
                    'number': progress
                },
                'Качество': {
                    "type": "number",
                    'number': quality
                }
            }
        }


        data = json.dumps(updateData)

        response = requests.request("PATCH", updateUrl, headers=headers, data=data)
    updatePage(page_id[a], headers)
    a += 1

for i in range(len(campaign_id)):
    get_campaign_stats(campaign_id)











