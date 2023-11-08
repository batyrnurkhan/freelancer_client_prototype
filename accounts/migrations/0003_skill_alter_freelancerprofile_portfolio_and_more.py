# Generated by Django 4.2.7 on 2023-11-06 03:04

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_freelancerprofile_ratings_freelancerprofile_reviews_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.AlterField(
            model_name='freelancerprofile',
            name='portfolio',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='freelancerprofile',
            name='ratings',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AlterField(
            model_name='freelancerprofile',
            name='reviews',
            field=models.TextField(blank=True),
        ),
        migrations.RemoveField(
            model_name='freelancerprofile',
            name='skills',
        ),
        migrations.AddField(
            model_name='freelancerprofile',
            name='skills',
            field=models.ManyToManyField(blank=True, related_name='freelancers', to='accounts.skill'),
        ),
    ]