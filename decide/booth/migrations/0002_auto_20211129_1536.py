# Generated by Django 2.0 on 2021-11-29 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booth', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sugerenciavoto',
            name='campos_preguntas',
            field=models.PositiveSmallIntegerField(),
        ),
    ]
