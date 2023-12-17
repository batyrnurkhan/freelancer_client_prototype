from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator


class Rating(models.Model):
    order = models.OneToOneField('listings.Order', on_delete=models.CASCADE, related_name='rating')
    freelancer = models.ForeignKey('accounts.FreelancerProfile', on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['order', 'freelancer']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        average = Rating.objects.filter(freelancer=self.freelancer).aggregate(Avg('score'))['score__avg']
        self.freelancer.ratings = average
        self.freelancer.save()


class CustomUserManager(BaseUserManager):

    def create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        if not username:
            raise ValueError(_('The Username must be set'))
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)

    def get_freelancers(self):
        return self.get_queryset().filter(user_type='freelancer')
from django.utils.crypto import get_random_string


class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ('freelancer', 'Freelancer'),
        ('client', 'Client'),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    username = models.CharField(_('username'), max_length=150, unique=True)
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    activation_token = models.CharField(max_length=50, blank=True, null=True)
    email_verified = models.BooleanField(default=False)


    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def save(self, *args, **kwargs):
        if not self.activation_token:
            self.activation_token = get_random_string(50)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(
        upload_to='profile_images/',
        null=True,
        blank=True,
        default='static/img/images.png'  # Set the default path
    )

    # Add additional fields as needed

    def __str__(self):
        return self.user.email


# models.py
from django.core.validators import MaxValueValidator, MinValueValidator


class Skill(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


from django.db.models import Avg


class FreelancerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='freelancer_profile')
    skills = models.ManyToManyField(Skill, related_name='freelancers', blank=True)
    skill_desc = models.TextField(blank=True)  # New field for skill descriptions
    portfolio = models.URLField(blank=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    reviews = models.TextField(blank=True)
    profile_image = models.ImageField(
        upload_to='profile_images/',
        null=True,
        blank=True,
        default='profile_images/images.png'
    )
    video = models.FileField(
        upload_to='profile_videos/',
        null=True,
        blank=True,
        help_text="Upload a video showcasing your work."
    )
    def update_ratings(self):
        self.average_rating = self.ratings.aggregate(Avg('score'))['score__avg']
        self.save()

    def __str__(self):
        return f"{self.user.username}'s freelancer profile"


class ClientProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_profile'
    )
    company_name = models.CharField(max_length=255)
    company_website = models.URLField(max_length=255, blank=True, null=True)
    profile_image = models.ImageField(
        upload_to='profile_images/',
        null=True,
        blank=True,
        default='static/img/images.png'
    )

    contact_name = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(max_length=255, blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    company_description = models.TextField(blank=True)
    industry = models.CharField(max_length=255, blank=True)
    preferred_communication = models.CharField(max_length=100, choices=[('email', 'Email'), ('phone', 'Phone'),
                                                                        ('message', 'In-app Messaging')],
                                               default='email')
    additional_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s Client Profile"


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Check the user_type and create the respective profile.
        if instance.user_type == 'freelancer':
            FreelancerProfile.objects.create(user=instance)
        elif instance.user_type == 'client':
            ClientProfile.objects.create(user=instance)
        # You may want to handle the case where user_type is not set.
        else:
            # Handle the case or raise an error if user_type is not set.
            print("User type is not set for the user: {}".format(instance))


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
