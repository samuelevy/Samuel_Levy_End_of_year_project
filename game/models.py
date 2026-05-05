from django.db import models
from player.models import Player

# Create your models here.

class Game(models.Model):
    #Define model
    game_id=models.AutoField(primary_key=True, db_column='game_id')
    player1=models.ForeignKey(Player, on_delete=models.CASCADE, db_column='player1', to_field='user', related_name='play1')
    player2=models.ForeignKey(Player, on_delete=models.CASCADE, db_column='player2', to_field='user', related_name='play2')
    outcome = models.IntegerField(null=True, blank=True, db_column='outcome')
    played_at = models.DateTimeField(auto_now_add=True, db_column='played_at')
    
    class Meta:
        db_table='game'
        managed=False
        
    def __str__(self):
        if self.outcome==None:
            result="Draw"
        elif self.outcome==self.player1.user_id:
            result=f"{self.player1.user.name} wins"
        else:
             result=f"{self.player2.user.name} wins"
             
        return f"Game {self.game_id}: {self.player1.user.name} vs {self.player2.user.name} - {result}"
    
    def resp1(self): #Player 1 results for rating model
        if self.outcome == None:
            return 0.5
        elif self.outcome == self.player1.user_id:
            return 1.0
        else:  # DRAW
            return 0.0
        
    def resp2(self): #Player 2 results for rating model
        if self.outcome == None:
            return 0.5
        elif self.outcome == self.player2.user_id:
            return 1.0
        else:  # DRAW
            return 0.0
        
    def get_winner(self):
        if self.outcome is None:
            return None
        elif self.outcome == self.player1.user_id:
            return self.player1
        else:
            return self.player2
    