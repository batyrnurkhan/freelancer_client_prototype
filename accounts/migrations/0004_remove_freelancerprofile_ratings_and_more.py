# Generated by Django 4.2.7 on 2023-11-06 08:25

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0001_initial'),
        ('accounts', '0003_skill_alter_freelancerprofile_portfolio_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='freelancerprofile',
            name='ratings',
        ),
        migrations.AddField(
            model_name='freelancerprofile',
            name='average_rating',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=3),
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('review', models.TextField(blank=True, null=True)),
                ('freelancer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='accounts.freelancerprofile')),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='rating', to='listings.order')),
            ],
            options={
                'unique_together': {('order', 'freelancer')},
            },
        ),
    ]
