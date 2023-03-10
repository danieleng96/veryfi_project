# Generated by Django 4.1.2 on 2022-10-24 00:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images')),
                ('ocr_json', models.FileField(upload_to='ocr_json')),
                ('input_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
