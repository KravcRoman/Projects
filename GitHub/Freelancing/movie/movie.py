import pandas as pd

# Загрузка данных из файла 'movie.xlsx'
data = pd.read_excel('movie.xlsx')

# 1. Вывести количество недостающих значений в поле 'duration'
missing_duration_count = data['duration'].isnull().sum()
print("1. Количество недостающих значений в поле 'duration':", missing_duration_count)

# 2. Заменить недостающие значения в поле 'duration' медианой
median_duration = data['duration'].median()
data['duration'].fillna(median_duration, inplace=True)

# 3. В столбце 'genres' перечислены жанры, к которым относится фильм.
#    Необходимо посчитать среднее количество жанров у фильмов
data['num_genres'] = data['genres'].apply(lambda x: len(x.split('|')))
average_genre_count = data['num_genres'].mean()
print("3. Среднее количество жанров у фильмов:", average_genre_count)

# 4. Найти фильм/фильмы с максимальным количеством жанров.
max_genre_count = data['num_genres'].max()
movies_with_max_genres = data[data['num_genres'] == max_genre_count]
print("4. Фильм/Фильмы с максимальным количеством жанров:")
print(movies_with_max_genres[['movie_title', 'genres']])

# 5. Найти самый часто встречаемый жанр.
all_genres = '|'.join(data['genres']).split('|')
most_common_genre = max(set(all_genres), key=all_genres.count)
print("5. Самый часто встречаемый жанр:", most_common_genre)

# 6. Построить сводную таблицу (pivot).
#    В ней должна содержаться информация о том, какой суммарный бюджет фильмов в разрезе стран за год,
#    в 2014-2016 годах включительно.
budget_pivot = pd.pivot_table(data[(data['title_year'] >= 2014) & (data['title_year'] <= 2016)],
                              index='country', columns='title_year',
                              values='budget', aggfunc='sum')
print("\n6. Сводная таблица по суммарному бюджету фильмов в разрезе стран за год:")
print(budget_pivot)
