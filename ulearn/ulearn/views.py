import requests
from django.shortcuts import render
from datetime import datetime, timedelta


# Главная страница
def home(request):
    context = {
        'description': 'Текст о профессии (не менее 2000 знаков)...',
        'image_url': 'path_to_image.jpg',  # путь к изображению
    }
    return render(request, 'home.html', context)


# Общая статистика
def statistics(request):
    # Пример данных (замените на реальные данные из API или базы данных)
    salary_data = [
        {"year": 2020, "avg_salary": 50000},
        {"year": 2021, "avg_salary": 60000},
    ]
    job_count = [
        {"year": 2020, "count": 1000},
        {"year": 2021, "count": 1200},
    ]

    context = {
        'salary_data': salary_data,
        'job_count': job_count,
    }
    return render(request, 'statistics.html', context)


# Востребованность
def demand(request):
    # Пример данных для выбранной профессии
    salary_data = [
        {"year": 2020, "avg_salary": 55000},
        {"year": 2021, "avg_salary": 65000},
    ]
    job_count = [
        {"year": 2020, "count": 800},
        {"year": 2021, "count": 950},
    ]

    context = {
        'salary_data': salary_data,
        'job_count': job_count,
    }
    return render(request, 'demand.html', context)


# География
def geography(request):
    # Пример данных по городам
    salary_by_city = [
        {"city": "Москва", "avg_salary": 75000},
        {"city": "Санкт-Петербург", "avg_salary": 65000},
    ]
    vacancy_share_by_city = [
        {"city": "Москва", "share": 40},
        {"city": "Санкт-Петербург", "share": 30},
    ]

    context = {
        'salary_by_city': salary_by_city,
        'vacancy_share_by_city': vacancy_share_by_city,
    }
    return render(request, 'geography.html', context)


# Навыки
def skills(request):
    # Пример данных по навыкам
    top_skills = [
        {"skill": "Python", "frequency": 1500},
        {"skill": "Django", "frequency": 1200},
    ]

    context = {
        'top_skills': top_skills,
    }
    return render(request, 'skills.html', context)


# Получение последних вакансий из API HH
def get_recent_vacancies():
    url = "https://api.hh.ru/vacancies"
    params = {
        'text': 'IT',  # Профессия
        'date_from': (datetime.now() - timedelta(days=1)).isoformat(),  # За последние 24 часа
        'per_page': 10,
    }
    response = requests.get(url, params=params)
    vacancies = response.json().get('items', [])

    return [{
        'title': vacancy['name'],
        'description': vacancy['snippet']['responsibility'],
        'skills': ', '.join(vacancy['key_skills']),
        'company': vacancy['employer']['name'],
        'salary': vacancy['salary']['from'] if vacancy['salary'] else 'Не указано',
        'region': vacancy['area']['name'],
        'published_at': vacancy['published_at'],
    } for vacancy in vacancies]


# Последние вакансии
def recent_vacancies(request):
    vacancies = get_recent_vacancies()
    context = {
        'vacancies': vacancies,
    }
    return render(request, 'vacancies.html', context)