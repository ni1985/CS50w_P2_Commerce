# Generated by Django 3.1.6 on 2021-03-17 21:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_auto_20210317_2212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='winner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='winner', to=settings.AUTH_USER_MODEL),
        ),
    ]
