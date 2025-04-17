from django.db import models
from django.contrib.auth.models import User

class Game(models.Model):
    PLAYER_CHOICES = [
        ('R', 'Rock'),
        ('P', 'Paper'),
        ('S', 'Scissors'),
    ]
    
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    player_choice = models.CharField(max_length=1, choices=PLAYER_CHOICES)
    computer_choice = models.CharField(max_length=1, choices=PLAYER_CHOICES)
    result = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.player.username} - {self.get_result_display()}"