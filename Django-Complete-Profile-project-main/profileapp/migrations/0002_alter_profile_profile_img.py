# Generated by Django 3.2.4 on 2021-08-12 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profileapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_img',
            field=models.ImageField(blank=True, default='media/default.jpg', null=True, upload_to='media'),
        ),
    ]
