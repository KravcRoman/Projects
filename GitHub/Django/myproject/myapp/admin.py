# from django.contrib import admin
# from .models import Article
#
# admin.site.register(Article)

from django.contrib import admin
from .models import Article

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title',)  # Добавляем id в список отображаемых полей

admin.site.register(Article, ArticleAdmin)
