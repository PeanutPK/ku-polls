# Generated by Django 5.1 on 2024-08-30 07:45

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("polls", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="end_date",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="ended date"
            ),
        ),
        migrations.AlterField(
            model_name="question",
            name="pub_date",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="date published"
            ),
        ),
    ]
