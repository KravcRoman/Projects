"""
ТЗ:
1. К нам приходит 1 документ -> мы его обрабатываем под нужную логику из TDocument -> отдаем обратно
2. Храним все сообщения с уникальными URL
3. Поле `Text` и `FetchTime` должно быть таким, каким было у `Text` и `FetchTime`
в сообщения с наибольшим `FetchTime`
4. Поле `PubDate` должно быть таким, каким было у `PubDate` в сообщении с наименьшим `FetchTime`
5. Поле `FirstFetchTime` должно быть равно минимальному значению `FetchTime` из всех файлов
Дублирующие документы тоже отправляем
"""

from typing import Optional

class TDocument(BaseModel):
    """
    Валидация данных
    """
    Url: str
    PubDate: int
    FetchTime: int
    Text: str
    FirstFetchTime: Optional[int]

class TProcessor:
    def __init__(self):
        self.document: Dict[str, List[TDocument]] = {}

    def process(self, input_doc: TDocument) -> TDocument:
        url = input_doc.Url
        fetch_time = input_doc.FetchTime

        if url not in self.document:
            # Если url поступил впервые
            self.document[url] = [input_doc]
            input_doc.FirstFetchTime = fetch_time
        else:
            # Добавляем в историю
            self.document[url].append(input_doc)
            # Сортируем по FirstFetchTime
            self.document[url].sort(key=lambda x: x.FirstFetchTime)

            # Получаем самый первый документ для PubDate и FirstFetchTime
            first_doc = self.document[url][0]
            input_doc.PubDate = first_doc.PubDate
            input_doc.FirstFetchTime = first_doc.FetchTime

            # Получаем самый последний документ для Text и FetchTime
            last_doc = self.document[url][-1]
            input_doc.Text = last_doc.Text
            input_doc.FetchTime = last_doc.FetchTime

        return input_doc

processor = TProcessor()


def test_process_single():
    input_doc = TDocument(Url='doc1', PubDate=1, FetchTime=10, Text='qwe')
    process_doc = processor.process(input_doc)
    assert process_doc.Url == 'doc1'
    assert process_doc.PubDate == 1
    assert process_doc.FetchTime == 10
    assert process_doc.Text == 'qwe'


def test_process_queue():
    doc1 = TDocument(Url='doc1', PubDate=1, FetchTime=20, Text='qwe')
    doc2 = TDocument(Url='doc2', PubDate=2, FetchTime=15, Text='qwer')
    doc3 = TDocument(Url='doc1', PubDate=3, FetchTime=10, Text='qwert')

    process_doc1 = processor.process(doc1)
    assert process_doc1.Url == 'doc1'
    assert process_doc1.PubDate == 1
    assert process_doc1.FetchTime == 20
    assert process_doc1.Text == 'qwe'

    process_doc2 = processor.process(doc2)
    assert process_doc2.Url == 'doc2'
    assert process_doc2.PubDate == 2
    assert process_doc2.FetchTime == 15
    assert process_doc2.Text == 'qwer'

    process_doc3 = processor.process(doc3)
    assert process_doc3.Url == 'doc1'
    assert process_doc3.PubDate == 3
    assert process_doc3.FetchTime == 10
    assert process_doc3.Text == 'qwert'

































