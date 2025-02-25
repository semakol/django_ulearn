from django.contrib import admin
from .models import Vacancies
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