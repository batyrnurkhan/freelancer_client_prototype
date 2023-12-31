# Generated by Django 4.2.7 on 2023-11-07 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_remove_freelancerprofile_ratings_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientprofile',
            name='additional_notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='clientprofile',
            name='company_description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='clientprofile',
            name='company_website',
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='clientprofile',
            name='contact_email',
            field=models.EmailField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='clientprofile',
            name='contact_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='clientprofile',
            name='contact_phone',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='clientprofile',
            name='industry',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='clientprofile',
            name='preferred_communication',
            field=models.CharField(choices=[('email', 'Email'), ('phone', 'Phone'), ('message', 'In-app Messaging')], default='email', max_length=100),
        ),
        migrations.AlterField(
            model_name='clientprofile',
            name='company_name',
            field=models.CharField(max_length=255),
        ),
    ]
