from django.db import models

# Create your models here.

class UserInput(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    gender = models.CharField(max_length=10)

    birth_date = models.DateField()
    birth_time = models.TimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"