from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid
from django.utils import timezone
from accounts.models import Skill

class Order(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    description = models.TextField()
    skills = models.ManyToManyField(Skill, related_name='orders')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_request', 'In Request'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    freelancer = models.ForeignKey('accounts.FreelancerProfile', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='taken_orders')
    taken_at = models.DateTimeField(null=True, blank=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            # Use UUID to generate a unique slug
            self.slug = slugify(f"{self.title}-{uuid.uuid4()}")
        if self.status == 'in_progress' and not self.taken_at:
            self.taken_at = timezone.now()
        super(Order, self).save(*args, **kwargs)

    def is_completed(self):
        # Assuming you have some criteria to check if an order is completed
        return self.status == 'completed'

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

# listings/models.py

class Job(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_request', 'In Request'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )


    freelancer = models.ForeignKey('accounts.FreelancerProfile', on_delete=models.SET_NULL, null=True, related_name='jobs')
    client = models.ForeignKey('accounts.ClientProfile', on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    deliverables = models.TextField()  # This can be more structured if needed
    is_active = models.BooleanField(default=True)
    def save(self, *args, **kwargs):
        # Call the "real" save() method.
        super(Job, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Soft delete method
        self.is_active = False
        self.save()

    def restore(self, *args, **kwargs):
        # Restore soft-deleted job
        self.is_active = True
        self.save()

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

