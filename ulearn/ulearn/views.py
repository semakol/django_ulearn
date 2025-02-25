from collections import Counter

import requests
from django.db.models import Avg, Count
from django.shortcuts import render
from datetime import datetime, timedelta
from .models import Vacancies, ExchangeRate
import xmltodict


# Главная страница
def home(request):
    return render(request, 'home.html')


# Общая статистика
def statistics(request):
    vacancies = Vacancies.objects.all()  # Получаем все вакансии

    # Динамика уровня зарплат по годам
    salary_by_years = {}
    count_by_years = {}
    skills_by_year = {}

    salary_by_city = {}

    for i in range(2024, 2010, -1):
        salary_by_years[i] = []
        count_by_years[i] = 0
        skills_by_year[i] = []

    for vacancy in vacancies:
        year = vacancy.published_at.year
        city = vacancy.area_name
        if year not in salary_by_years:
            continue
        if city not in salary_by_city:
            salary_by_city[city] = []
        salary_by_city[city].append(vacancy)
        count_by_years[year] += 1
        salary_by_years[year].append(vacancy)


    avg_salary_by_year = {year: calculate_average_salary(vac_list) for year, vac_list in salary_by_years.items()}
    avg_salary_by_city = {city: calculate_average_salary(vac_list) if len(vac_list) > 10 else 0 for city, vac_list in salary_by_city.items()}

    # Динамика количества вакансий по годам
    vacancies_by_years = {year: count for year, count in count_by_years.items()}
    avg_salary_by_city = dict(sorted(avg_salary_by_city.items(), key=lambda x: x[1], reverse=True)[:10])

    # Доля вакансий по городам
    total_vacancies = vacancies.count()
    city_distribution = (
        Vacancies.objects.values("area_name")
        .annotate(count=Count("area_name"))
        .order_by("-count")
    )[:10]

    city_percentages = {entry["area_name"]: {"per":(entry["count"] / total_vacancies * 100), "count": entry["count"]} for entry in city_distribution}

    # Топ-20 навыков по годам


    for vacancy in vacancies:
        year = vacancy.published_at.year
        if not vacancy.key_skills:
            continue

        skills = vacancy.key_skills.split(",")  # Предполагаем, что навыки разделены запятыми
        if year not in skills_by_year:
            continue

        skills_by_year[year].extend(skills)

    top_20_skills_by_year = {year: dict(Counter(skills).most_common(20)) for year, skills in skills_by_year.items()}

    context = {
        "avg_salary_by_year": avg_salary_by_year,
        "vacancies_by_years": vacancies_by_years,
        "salary_by_city": avg_salary_by_city,
        "city_percentages": city_percentages,
        "top_20_skills_by_year": top_20_skills_by_year,
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


# Функция для получения курса валюты на определенную дату
def get_exchange_rate(currency, date):
    if currency == "RUR" or not currency:  # Если валюта рубли или не указана
        return 1

    date = date.date().replace(day=1)

    rate = ExchangeRate.objects.filter(date=date).first()

    if not rate:
        url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={date.strftime('%d/%m/%Y')}"
        response = requests.get(url)
        if response.status_code != 200:
            return None
        data = xmltodict.parse(response.text)
        curr_data = {}
        for item in data.get('ValCurs').get('Valute'):
            curr_data[item['CharCode']] = float(item['Value'].replace(',', '.')) / int(item['Nominal'])
        rate = ExchangeRate.objects.create(
            date=date,
            currency=curr_data
        )
        rate.save()
        print('Сохранение валют за ', date)

    return rate.currency.get(currency, None)

    # if response.status_code != 200:
    #     return None  # Если запрос не удался, пропускаем валюту
    #
    # data = response.text
    # if currency in data:
    #     start = data.find(f'<CharCode>{currency}</CharCode>')
    #     nominal = int(data[data.find("<Nominal>", start) + 9: data.find("</Nominal>", start)])
    #     value = float(data[data.find("<Value>", start) + 7: data.find("</Value>", start)].replace(",", "."))
    #     return value / nominal  # Курс с учетом номинала
    #
    # return None


# Функция расчета средней зарплаты с учетом конверсии
def calculate_average_salary(vacancies):
    salary_data = []

    for vacancy in vacancies:
        if not vacancy.salary_from and not vacancy.salary_to:
            continue  # Если нет зарплаты, пропускаем

        # Берем среднее значение вилки
        avg_salary = (vacancy.salary_from or 0 + vacancy.salary_to or 0) / (
            2 if vacancy.salary_from and vacancy.salary_to else 1)

        # Конвертируем в рубли
        exchange_rate = get_exchange_rate(vacancy.salary_currency, vacancy.published_at)
        if exchange_rate:
            avg_salary *= exchange_rate

        # Исключаем слишком большие значения (некорректные данные)
        if avg_salary < 10_000_000:
            salary_data.append(avg_salary)

    return sum(salary_data) / len(salary_data) if salary_data else 0