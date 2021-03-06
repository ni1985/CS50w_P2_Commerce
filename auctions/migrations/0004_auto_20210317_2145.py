# Generated by Django 3.1.6 on 2021-03-17 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_auto_20210315_2110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='winner',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='listing',
            name='finished',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='listing',
            name='url',
            field=models.URLField(blank=True),
        ),
    ]
