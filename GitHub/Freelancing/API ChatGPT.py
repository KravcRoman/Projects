import openai
import requests

# Устанавливаем ключ API GPT-3
openai.api_key = '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'

def fetch_content(url):
    """
    Получает содержимое веб-страницы по указанному URL-адресу.
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Не удалось получить содержимое страницы {url}. Статус код: {response.status_code}")
            return None
    except Exception as e:
        print(f"Произошла ошибка при получении содержимого страницы {url}: {str(e)}")
        return None

def answer_question(content, question):
    """
    Отвечает на вопрос, используя модель GPT-3.
    """
    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo",
            #engine="davinci-codex",
            #engine="davinci",
            #model="gpt-3.5-turbo",
            prompt=f"Контент: {content}\nВопрос: {question}\nОтвет:",
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Произошла ошибка при получении ответа на вопрос: {str(e)}")
        return None

if __name__ == "__main__":
    # Вводим 5 URL-адресов
    urls = []
    for i in range(5):
        url = input(f"Введите URL-{i+1}: ")
        urls.append(url)

    # Получаем содержимое каждой страницы и отвечаем на вопросы
    for url in urls:
        content = fetch_content(url)
        if content:
            question = input("Введите ваш вопрос относительно содержимого страницы: ")
            answer = answer_question(content, question)
            print(f"Ответ на ваш вопрос: {answer}\n")
        else:
            print("Не удалось получить содержимое страницы.")






# def fetch_content(url):
#     """
#     Получает содержимое веб-страницы по указанному URL-адресу.
#     """
#     try:
#         response = requests.get(url)
#         if response.status_code == 200:
#             return response.text
#         else:
#             print(f"Не удалось получить содержимое страницы {url}. Статус код: {response.status_code}")
#             return None
#     except Exception as e:
#         print(f"Произошла ошибка при получении содержимого страницы {url}: {str(e)}")
#         return None
#
# def answer_question(content, question):
#     """
#     Отвечает на вопрос, используя модель GPT-3.
#     """
#     try:
#         response = openai.Completion.create(
#             engine="davinci",
#             prompt=f"Контент: {content}\nВопрос: {question}\nОтвет:",
#             temperature=0.7,
#             max_tokens=150
#         )
#         return response.choices[0].text.strip()
#     except Exception as e:
#         print(f"Произошла ошибка при получении ответа на вопрос: {str(e)}")
#         return None
#
# if __name__ == "__main__":
#     urls = [
#         "https://vk.com/",
#         "https://www.youtube.com/",
#         "https://www.python.org/",
#         "https://docs-python.ru/tutorial/generatory-python/ispolzovanie-send-throw-close/",
#         "https://selectel.ru/blog/tutorials/how-to-develop-fastapi-application/?section=about"
#     ]
#
#     for url in urls:
#         print(f"Обработка URL: {url}")
#         content = fetch_content(url)
#         if content:
#             question = input("Введите ваш вопрос относительно содержимого страницы: ")
#             answer = answer_question(content, question)
#             print(f"Ответ на ваш вопрос: {answer}\n")
#         else:
#             print("Не удалось получить содержимое страницы.")
