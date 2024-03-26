from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Article

class BlogTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.article = Article.objects.create(title='Test Article', text='This is a test article.', author=self.user)

    def test_article_list_view(self):
        client = Client()
        response = client.get(reverse('article_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)

    def test_create_article_view(self):
        client = Client()
        client.login(username='testuser', password='12345')
        response = client.post(reverse('create_article'), {'title': 'New Article', 'text': 'This is a new article.'})
        self.assertEqual(response.status_code, 302)  # Redirects after successful form submission

    def test_article_detail_view(self):
        client = Client()
        response = client.get(reverse('article_detail', args=[self.article.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)
        self.assertContains(response, self.article.text)
