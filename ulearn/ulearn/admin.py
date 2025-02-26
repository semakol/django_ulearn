from .tasks import *
from django.contrib import admin

from .models import Vacancies, Statistics
from django import forms

class VacancyAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

@admin.register(Vacancies)
class VacanciesAdmin(admin.ModelAdmin):
    form = VacancyAdminForm
    list_display = ("id", "name", "salary_from", "salary_to", "salary_currency", "published_at", "area_name")
    list_filter = ("area_name", "salary_currency", "published_at")
    search_fields = ("name", "area_name")
    ordering = ("-published_at",)
    date_hierarchy = "published_at"

@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)
    actions = ['reload', 'all_reload']

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    @admin.action(description="Reload")
    def reload(self, request, queryset):
        for item in queryset:
            if item.name == 'avg_salary_by_city':
                calc_salary_by_city()
            elif item.name == 'vacancies_by_year':
                calc_vacancies_by_year()
            elif item.name == 'avg_salary_by_year':
                calc_salary_by_year()
            elif item.name == 'city_percentages':
                calc_city_percentages()
            elif item.name == 'top_20_skills_by_year':
                calc_skills_by_year()

    @admin.action(description="All reload")
    def all_reload(self, request, queryset):
        calc_salary_by_city()
        calc_vacancies_by_year()
        calc_salary_by_year()
        calc_city_percentages()
        calc_skills_by_year()