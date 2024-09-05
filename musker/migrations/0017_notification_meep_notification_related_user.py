# Generated by Django 4.2.4 on 2024-08-27 03:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('musker', '0016_remove_polloption_poll_remove_polloption_votes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='meep',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='musker.meep'),
        ),
        migrations.AddField(
            model_name='notification',
            name='related_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='related_notifications', to=settings.AUTH_USER_MODEL),
        ),
    ]
