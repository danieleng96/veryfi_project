# Generated by Django 4.1.2 on 2022-10-24 02:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='upload',
            name='slug',
            field=models.SlugField(max_length=200, null=True, unique=True),
        ),
    ]
