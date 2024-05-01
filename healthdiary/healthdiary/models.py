from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class MainMenu(models.Model):
    title = models.CharField(max_length=200)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.title
    
class BodyPart(models.Model):
    name = models.CharField(max_length=200)
    # slug = models.SlugField(max_length=200, unique=True,blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name
    
class Sport(models.Model):
    bodyPart = models.ForeignKey(BodyPart,related_name='sport_bodyPart',on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    image = models.ImageField(upload_to='sports/%Y/%m/%d',blank=True)
    created = models.DateTimeField(auto_now_add=True)
    createdBy = models.ForeignKey(User,related_name='sport_createdBy',on_delete=models.CASCADE)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['id','slug','createdBy']),
        ]
    def __str__(self):
        return self.name

class SportHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_sport_history')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_sport_history')
    set_number = models.PositiveIntegerField()
    count = models.PositiveIntegerField()
    weight = models.FloatField()
    sport_date = models.DateTimeField()

    class Meta:
        ordering = ['-sport_date']

    def __str__(self):
        return f'{self.user.username} - {self.sport.name} on {self.sport_date.strftime("%Y-%m-%d %H:%M")}'
