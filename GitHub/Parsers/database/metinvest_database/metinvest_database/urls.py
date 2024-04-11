"""metinvest_database URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from metinvest_database.views import *
from metinvest_database.view_classes import *
from metinvest_database.csv_views import *

urlpatterns = [
    path('', index, name='index'),
    path('upload/', upload, name='upload'),
    path('admin/', admin.site.urls),
    path('upload-raw', upload_raw),

    path('get_csv/', get_csv),

    path('search/', search),
    path('count/', count),
    path('get_categories/', get_categories),

    path('create-supplier/', create_supplier, name='create_supplier'),
    path('create-warehouse/', create_supplier_warehouse, name='create-warehouse'),
    path('create-office/', create_supplier_office, name='create-office'),

    path('all_suppliers/', all_suppliers, name='all_suppliers'),
    path('update_supplier/', update_supplier, name='update_supplier'),
    path('all_suppliers_query/', all_suppliers_query, name='all_suppliers_query'),

    path('sites/', sites, name='sites'),
    path('categories/', categories, name='categories'),
    path('suppliers/', suppliers, name='suppliers'),
    path('cities/', cities, name='cities'),
    path('products/', products, name='products'),

    path('site/<id>', site, name='site'),
    path('category/<id>', category, name='category'),
    path('supplier/<id>', supplier, name='supplier'),
    path('city/<id>', city, name='city'),
    path('product/<id>', product, name='product'),

    path('login/', MyLoginView.as_view(),name='login'),
    path('generate_pdf/', generate_pdf, name='generate_pdf'),
    path('filter_cities/', filter_cities, name='filter_cities'),

]
