# Generated by Django 4.2.7 on 2023-11-07 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_clientprofile_profile_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientprofile',
            name='profile_image',
            field=models.ImageField(blank=True, default='static/img/images.png', null=True, upload_to='profile_images/'),
        ),
        migrations.AlterField(
            model_name='freelancerprofile',
            name='profile_image',
            field=models.ImageField(blank=True, default='static/img/images.png', null=True, upload_to='profile_images/'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='profile_image',
            field=models.ImageField(blank=True, default='static/img/images.png', null=True, upload_to='profile_images/'),
        ),
    ]
