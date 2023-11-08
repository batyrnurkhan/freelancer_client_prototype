from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Order(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    description = models.TextField()
    technology_stack = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return f"Order by {self.client.email} - {self.created_at}"

# listings/models.py

class Job(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
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

    def __str__(self):
        return self.title

    # Optionally, override the save method to handle notifications or other logic

