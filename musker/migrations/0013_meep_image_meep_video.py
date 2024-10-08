# Generated by Django 4.2.4 on 2024-08-25 01:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musker', '0012_meep_hashtags'),
    ]

    operations = [
        migrations.AddField(
            model_name='meep',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='meep_images/'),
        ),
        migrations.AddField(
            model_name='meep',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to='meep_videos/'),
        ),
    ]
