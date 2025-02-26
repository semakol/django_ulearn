import humanize
from django.shortcuts import render
from datetime import datetime, timedelta
from .tasks import *


def home(request):
    return render(request, 'home.html')


def statistics(request):
    stats = Statistics.objects
    avg_salary_by_year = stats.get(name='avg_salary_by_year')
    vacancies_by_years = stats.get(name='vacancies_by_year')
    avg_salary_by_city = stats.get(name='avg_salary_by_city')
    city_percentages = stats.get(name='city_percentages')
    top_20_skills_by_year = stats.get(name='top_20_skills_by_year')
    top_20_skills_by_year_sorted = [
        (key, dict(sorted(value.items(), key=lambda item: item[1], reverse=True)))
        for key, value in sorted(top_20_skills_by_year.data.items(), key=lambda item: item[0],
                                   reverse=True)
    ]

    context = {
        "avg_salary_by_year": sorted(avg_salary_by_year.data.items(), key=lambda item: item[0], reverse=True),
        "vacancies_by_years": sorted(vacancies_by_years.data.items(), key=lambda item: item[0], reverse=True),
        "salary_by_city": sorted(avg_salary_by_city.data.items(), key=lambda item: item[1], reverse=True),
        "city_percentages": sorted(city_percentages.data.items(), key=lambda item: item[1]['per'], reverse=True),
        "top_20_skills_by_year": top_20_skills_by_year_sorted,
        "avg_salary_by_year_graph": avg_salary_by_year.graph,
        "vacancies_by_years_graph": vacancies_by_years.graph,
        "salary_by_city_graph": avg_salary_by_city.graph,
        "city_percentages_graph": city_percentages.graph,
        "top_20_skills_by_year_graph": top_20_skills_by_year.graph,
        "title": 'Статистика'
    }
    return render(request, 'statistics.html', context)


def demand(request):
    stats = Statistics.objects
    avg_salary_by_year = stats.get(name='avg_salary_by_year')
    vacancies_by_years = stats.get(name='vacancies_by_year')
    context = {
        "avg_salary_by_year": sorted(avg_salary_by_year.data.items(), key=lambda item: item[0], reverse=True),
        "vacancies_by_years": sorted(vacancies_by_years.data.items(), key=lambda item: item[0], reverse=True),
        "avg_salary_by_year_graph": avg_salary_by_year.graph,
        "vacancies_by_years_graph": vacancies_by_years.graph,
        "title": 'Востребованность'
    }
    return render(request, 'demand.html', context)


def geography(request):
    stats = Statistics.objects
    avg_salary_by_city = stats.get(name='avg_salary_by_city')
    city_percentages = stats.get(name='city_percentages')

    context = {
        "salary_by_city": sorted(avg_salary_by_city.data.items(), key=lambda item: item[1], reverse=True),
        "city_percentages": sorted(city_percentages.data.items(), key=lambda item: item[1]['per'], reverse=True),
        "salary_by_city_graph": avg_salary_by_city.graph,
        "city_percentages_graph": city_percentages.graph,
        "title": 'География'
    }
    return render(request, 'geography.html', context)


def skills(request):
    stats = Statistics.objects
    top_20_skills_by_year = stats.get(name='top_20_skills_by_year')
    top_20_skills_by_year_sorted = [
        (key, dict(sorted(value.items(), key=lambda item: item[1], reverse=True)))
        for key, value in sorted(top_20_skills_by_year.data.items(), key=lambda item: item[0],
                                 reverse=True)
    ]
    context = {
        "top_20_skills_by_year": top_20_skills_by_year_sorted,
        "top_20_skills_by_year_graph": top_20_skills_by_year.graph,
        "title": 'Навыки'
    }
    return render(request, 'skills.html', context)


def get_recent_vacancies():
    url = "https://api.hh.ru/vacancies"
    params = {
        'text': '"бэкeнд" OR "backend"',
        'search_field': 'name',# Профессия
        'professional_role': 96,
        'date_from': (datetime.now() - timedelta(days=1)).isoformat(),  # За последние 24 часа
        'per_page': 10,
    }
    response = requests.get(url, params=params)
    vacancies = response.json().get('items', [])

    return sorted([{
        'title': vacancy['name'],
        'description': vacancy['snippet']['responsibility'],
        'company': vacancy['employer']['name'],
        'salary': vacancy['salary']['from'] if vacancy['salary'] else 'Не указано',
        'region': vacancy['area']['name'],
        'published_at': humanize.naturaltime(datetime.fromisoformat(vacancy['published_at'])),
    } for vacancy in vacancies], key=lambda x:x['published_at'])


def recent_vacancies(request):
    vacancies = get_recent_vacancies()
    context = {
        'vacancies': vacancies,
        'title': 'Последние вакансии'
    }
    return render(request, 'vacancies.html', context)
