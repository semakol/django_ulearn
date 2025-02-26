import base64
from collections import Counter
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import requests
import xmltodict
from django.db.models import Count

from .models import Vacancies, ExchangeRate, Statistics


def calc_salary_by_city():
    vacancies = Vacancies.objects.all()
    salary_by_city = {}
    for vacancy in vacancies:
        city = vacancy.area_name
        if city not in salary_by_city:
            salary_by_city[city] = []
        salary_by_city[city].append(vacancy)
    avg_salary_by_city = {city: calculate_average_salary(vac_list) if len(vac_list) > 10 else 0 for city, vac_list in salary_by_city.items()}
    avg_salary_by_city = dict(sorted(avg_salary_by_city.items(), key=lambda x: x[1], reverse=True)[:10])
    stat = Statistics.objects.filter(name='avg_salary_by_city')
    graph = plot_dict(avg_salary_by_city, graph_type='bar', label='Средняя зарплата по городам')
    if not stat:
        stat = Statistics(name='avg_salary_by_city', data=avg_salary_by_city, graph=graph)
        stat.save()
    else:
        stat.update(data=avg_salary_by_city, graph=graph)
    print('Сохранение статистики зарплат по городам')

def calc_vacancies_by_year():
    vacancies = Vacancies.objects.all()
    count_by_years = {}
    for i in range(2024, 2010, -1):
        count_by_years[i] = 0
    for vacancy in vacancies:
        year = vacancy.published_at.year
        if year not in count_by_years:
            continue
        count_by_years[year] += 1
    vacancies_by_years = {year: count for year, count in count_by_years.items()}
    stat = Statistics.objects.filter(name='vacancies_by_year')
    graph = plot_dict(vacancies_by_years, graph_type='line', label='Количество вакансий по годам')
    if not stat:
        stat = Statistics(name='vacancies_by_year', data=vacancies_by_years, graph=graph)
        stat.save()
    else:
        stat.update(data=vacancies_by_years, graph = graph)
    print('Сохранение статистики количества вакансий по годам')

def calc_salary_by_year():
    vacancies = Vacancies.objects.all()
    salary_by_years = {}
    for i in range(2024, 2010, -1):
        salary_by_years[i] = []
    for vacancy in vacancies:
        year = vacancy.published_at.year
        if year not in salary_by_years:
            continue
        salary_by_years[year].append(vacancy)
    avg_salary_by_year = {year: calculate_average_salary(vac_list) for year, vac_list in salary_by_years.items()}
    stat = Statistics.objects.filter(name='avg_salary_by_year')
    graph = plot_dict(avg_salary_by_year, graph_type='line', label='Средняя зарплата по годам')
    if not stat:
        stat = Statistics(name='avg_salary_by_year', data=avg_salary_by_year, graph=graph)
        stat.save()
    else:
        stat.update(data=avg_salary_by_year, graph=graph)
    print('Сохранение статистики зарплат по годам')

def calc_city_percentages():
    vacancies = Vacancies.objects.all()
    total_vacancies = vacancies.count()
    city_distribution = (
        Vacancies.objects.values("area_name")
        .annotate(count=Count("area_name"))
        .order_by("-count")
    )[:10]
    city_percentages = {entry["area_name"]: {"per": (entry["count"] / total_vacancies * 100), "count": entry["count"]}
                        for entry in city_distribution}
    stat = Statistics.objects.filter(name='city_percentages')
    city_percentages_graph = {city: data['per'] for city, data in city_percentages.items()}
    graph = plot_dict(city_percentages_graph, graph_type='bar', label='Средняя зарплата по городам')
    if not stat:
        stat = Statistics(name='city_percentages', data=city_percentages, graph=graph)
        stat.save()
    else:
        stat.update(data=city_percentages, graph=graph)
    print('Сохранение статистики доли вакансий по городам')

def calc_skills_by_year():
    vacancies = Vacancies.objects.all()
    skills_by_year = {}
    for i in range(2024, 2014, -1):
        skills_by_year[i] = []
    for vacancy in vacancies:
        year = vacancy.published_at.year
        if not vacancy.key_skills:
            continue

        skills = vacancy.key_skills.split(", ")  # Предполагаем, что навыки разделены запятыми
        if year not in skills_by_year:
            continue

        skills_by_year[year].extend(skills)

    top_20_skills_by_year = {year: dict(Counter(skills).most_common(20)) for year, skills in skills_by_year.items()}
    stat = Statistics.objects.filter(name='top_20_skills_by_year')
    graph = plot_top_skills(top_20_skills_by_year)
    if not stat:
        stat = Statistics(name='top_20_skills_by_year', data=top_20_skills_by_year, graph=graph)
        stat.save()
    else:
        stat.update(data=top_20_skills_by_year,graph=graph)
    print('Сохранение статистики топ-20 навыков по годам')

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

    return rate.currency.get(currency)

def calculate_average_salary(vacancies):
    salary_data = []

    for vacancy in vacancies:
        if not vacancy.salary_from and not vacancy.salary_to:
            continue

        avg_salary = (vacancy.salary_from or 0 + vacancy.salary_to or 0) / (
            2 if vacancy.salary_from and vacancy.salary_to else 1)

        exchange_rate = get_exchange_rate(vacancy.salary_currency, vacancy.published_at)
        if exchange_rate:
            avg_salary *= exchange_rate

        if avg_salary < 10_000_000:
            salary_data.append(avg_salary)

    return sum(salary_data) / len(salary_data) if salary_data else 0

def plot_dict(data_dict, graph_type='line', label='Data'):

    x = list(data_dict.keys())
    y = list(data_dict.values())

    plt.figure(figsize=(10, 6))

    if graph_type == 'line':
        plt.plot(x, y, marker='o', linestyle='-', color='b', label=label)
    elif graph_type == 'bar':
        plt.bar(x, y, color='g', label=label)
    elif graph_type == 'scatter':
        plt.scatter(x, y, color='r', label=label)
    else:
        return

    plt.xlabel('Метки')
    plt.ylabel('Значения')
    plt.title(f'{graph_type.capitalize()} Graph')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)

    img_buf = BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)

    return base64.b64encode(img_buf.read()).decode('utf-8')


def plot_top_skills(trends_data):
    df = pd.DataFrame(trends_data).T.fillna(0)
    df = df[list(df.max().nlargest(10).index)]

    plt.figure(figsize=(12, 6))

    for skill in df.columns:
        plt.plot(df.index, df[skill], marker="o", linestyle="-", label=skill)

    plt.xlabel("Год")
    plt.ylabel("Частота")
    plt.title(f"Топ-10 навыков по годам")
    plt.legend(title="Skills", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.xticks(df.index, rotation=45)
    plt.tight_layout()
    plt.grid(True)

    img_buf = BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)

    return base64.b64encode(img_buf.read()).decode('utf-8')