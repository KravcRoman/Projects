import requests
#import json


def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data from {url}, status code: {response.status_code}")


def main():
    # Получаем данные по этим ссылкам
    posts_url = 'http://jsonplaceholder.typicode.com/posts'
    comments_url = 'http://jsonplaceholder.typicode.com/comments'

    posts = fetch_data(posts_url)
    comments = fetch_data(comments_url)

    # Создаем словарь для хранения количества постов каждого пользователя
    user_post_counts = {}
    for post in posts:
        user_id = post['userId']
        user_post_counts[user_id] = user_post_counts.get(user_id, 0) + 1

    # Создаем словарь для хранения количества комментариев для каждого поста
    post_comment_counts = {}
    for comment in comments:
        post_id = comment['postId']
        post_comment_counts[post_id] = post_comment_counts.get(post_id, 0) + 1

    # Создаем словарь для хранения суммы комментариев для каждого пользователя
    user_comment_counts = {}
    for post in posts:
        user_id = post['userId']
        post_id = post['id']
        comment_count = post_comment_counts.get(post_id, 0)
        user_comment_counts[user_id] = user_comment_counts.get(user_id, 0) + comment_count

    # Вычисляем среднее количество комментариев на пост для каждого пользователя
    user_avg_comments = {}
    for user_id in user_post_counts:
        total_comments = user_comment_counts.get(user_id, 0)
        total_posts = user_post_counts[user_id]
        avg_comments = total_comments / total_posts
        user_avg_comments[user_id] = avg_comments

    # Выводим результат
    for user_id, avg_comments in user_avg_comments.items():
        print(f"user_id: {user_id}, average_comments_per_post: {avg_comments:.2f}")

if __name__ == "__main__":
    main()
