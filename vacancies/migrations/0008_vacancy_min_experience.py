# Generated by Django 4.1.6 on 2023-02-23 05:02

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0007_vacancy_likes'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacancy',
            name='min_experience',
            field=models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
