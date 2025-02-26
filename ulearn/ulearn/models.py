
from django.db import models

class Vacancies(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=True)
    key_skills = models.CharField(max_length=1000, null=True)
    salary_from = models.FloatField(null=True)
    salary_to = models.FloatField(null=True)
    salary_currency = models.CharField(max_length=10, null=True)
    area_name = models.CharField(max_length=100, null=True)
    published_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.name

class ExchangeRate(models.Model):
    id = models.AutoField(primary_key=True)
    currency = models.JSONField(null=True)
    date = models.DateField(unique=True)

    def __str__(self):
        return self.currency

class Statistics(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    data = models.JSONField()
    graph = models.TextField(null=True)
