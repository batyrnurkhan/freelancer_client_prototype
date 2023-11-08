# Generated by Django 4.2.7 on 2023-11-07 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_clientprofile_additional_notes_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientprofile',
            name='profile_image',
            field=models.ImageField(blank=True, default='path/to/default/image.jpg', null=True, upload_to='profile_images/'),
        ),
        migrations.AlterField(
            model_name='freelancerprofile',
            name='profile_image',
            field=models.ImageField(blank=True, default='path/to/default/image.jpg', null=True, upload_to='profile_images/'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='profile_image',
            field=models.ImageField(blank=True, default='path/to/default/image.jpg', null=True, upload_to='profile_images/'),
        ),
    ]