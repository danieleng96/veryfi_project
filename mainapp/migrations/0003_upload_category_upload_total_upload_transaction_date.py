# Generated by Django 4.1.2 on 2022-10-24 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_upload_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='upload',
            name='category',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='upload',
            name='total',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='upload',
            name='transaction_date',
            field=models.DateTimeField(null=True),
        ),
    ]
