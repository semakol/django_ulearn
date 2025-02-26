from django.urls import path
from .views import *
from django.contrib import admin

urlpatterns = [
    path('', home, name='home'),
    path('statistics/', statistics, name='statistics'),
    path('demand/', demand, name='demand'),
    path('geography/', geography, name='geography'),
    path('skills/', skills, name='skills'),
    path('vacancies/', recent_vacancies, name='vacancies'),
    path('admin/', admin.site.urls),
]