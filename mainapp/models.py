from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f'Tag - {self.name}'


class Photo(models.Model):
    user = models.ForeignKey(User, related_name='photos', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='static/photos/')
    upload_date = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name='tag')

    STATUS_CHOICES = [
        ('PENDING', 'В ожидании'),
        ('APPROVED', 'Одобрено'),
        ('DISAPPROVED', 'Не одобрено')
    ]

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return self.title
