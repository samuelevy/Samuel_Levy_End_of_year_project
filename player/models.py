from django.db import models
import math
from django.http import JsonResponse
from user.models import AppUser
from decimal import Decimal

# Create your models here.
class Player(models.Model):
    # Link to AppUser (one-to-one relationship)
    user = models.OneToOneField(
        AppUser, 
        on_delete=models.CASCADE,  # If user deleted, delete player too
        primary_key=True,
        related_name='player_profile',
        db_column='user_id',
    )
    
    # Elo ranking
    elo = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=1500.00,
        help_text="Elo rating"
    )
    
    # Glicko-2 ranking
    glicko = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=1500.00,
        help_text="Glicko rating"
    )
    
    glicko_rd = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=350.00,
        help_text="Rating Deviation"
    )
    
    volatility = models.DecimalField(
        max_digits=10, 
        decimal_places=8, 
        default=0.06,
        help_text="Volatility"
    )
    
    # Game statistics
    tries = models.IntegerField(
        default=0,
        help_text="Total number of games played"
    )
    
    last_game_date = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Date of last game played"
    )
    
    gamecount=models.IntegerField(
        default=0,
        help_text="Total number of games played"
    )
    
    _tau = 0.5
    
    class Meta:
        db_table = 'player'
    
    def __str__(self):
        return f"Player: {self.user.name} (Elo: {self.elo}, Glicko: {self.glicko})"
    
    #Rating methods
    #Update elo ranking
    def update_elo(self, exp, result): #Arguments: exp=expected score, calculated in "games" class; result=actual score (1=win, 0=loss, 0.5=draw)
        #Use FIDE rating for k, found in https://ratings.fide.com/calc.phtml?page=change
        
        exp = Decimal(str(exp))
        result = Decimal(str(result))
        
        if self.gamecount < 8 : #placement period of 8 games
            k=Decimal('40')
        elif self.elo < 2400:
            k=Decimal('20')
        elif self.elo>=2400:
            k=Decimal('10')
        #New ranking
        rprime=self.elo + k*(result-exp)        
        self.elo = rprime
        self.gamecount+=1
        return self.elo
    
    #Update glicko ranking
    #These methods are a tweaked version of the algorithm found in https://github.com/ryankirkman/pyglicko2/blob/master/glicko2.py.
    #Rating formulas are updated to handle only one opponent at a time, providing real-time updates.
    
    def _v(self, opp_rating, opp_RD):
        # expected variance of the player’s rating based on game outcomes
        tempSum=0
        tempE=self._E(opp_rating, opp_RD)
        tempSum= math.pow(self._g(opp_RD), 2) * tempE * (1 - tempE)
        return 1 / tempSum
    
    def _E(self, opp_rating, opp_rd):
        # expected score against an opponent
        #Convert to glicko scale:
        mu=self.rating(self.glicko)
        opp_rating=self.rating(opp_rating)
        #Compute expected score:
        return 1 / (1 + math.exp(-1 * self._g(opp_rd) * \
                                 (mu - opp_rating)))
    def _g(self, opp_rd):
        #The Glicko2 g(RD) function.
        opp_rd=self.phi(opp_rd)
        return 1/math.sqrt(1 + 3 * math.pow(opp_rd, 2) / math.pow(math.pi, 2))
    
    def preRD(self):
        phi= self.phi(float(self.glicko_rd))
        sigma=float(self.volatility)
        phiprime = math.sqrt(math.pow(phi, 2) + math.pow(sigma, 2)) #Compute new RD
        self.glicko_rd = Decimal(str(phiprime * 173.7178)) #convert back to original scale
    
    def update_glicko(self, opp_rating, opp_RD, outcome):
        #Calculates the new rating and rating deviation of the player.
        
        #Convert variables
        opp_rating=float(opp_rating)
        opp_RD=float(opp_RD)
        outcome=float(outcome)
        
        v=self._v(opp_rating, opp_RD)
        newvol=self.newvol(opp_rating, opp_RD, outcome, v)
        self.volatility=Decimal(str(newvol))
        self.preRD()
        
        phi = 1/math.sqrt((1 / math.pow(self.phi(float(self.glicko_rd)), 2))+ 1/v)
        
        mu=self.rating(float(self.glicko))
        tempsum=self._g(opp_RD) * (outcome - self._E(opp_rating, opp_RD))
        mu+= math.pow(phi, 2) * tempsum
        
        self.glicko_rd = Decimal(str(phi * 173.7178))
        self.glicko = Decimal(str(mu * 173.7178 + 1500))
        
        return self.glicko
        
    def newvol(self, opp_rating, opp_RD, outcome, v):
        #Calculates the new volatility of the player.
        i = 0
        delta = self._delta(opp_rating, opp_RD, outcome, v)
        a = math.log(math.pow(self.volatility, 2))
        tau = self._tau
        x0 = a
        x1 = 0
        
        while x0 != x1:
            # New iteration, so x(i) becomes x(i-1)
            x0 = x1
            d = math.pow(self.rating(self.glicko), 2) + v + math.exp(x0)
            h1 = -(x0 - a) / math.pow(tau, 2) - 0.5 * math.exp(x0) \
            / d + 0.5 * math.exp(x0) * math.pow(delta / d, 2)
            h2 = -1 / math.pow(tau, 2) - 0.5 * math.exp(x0) * \
            (math.pow(self.rating(self.glicko), 2) + v) \
            / math.pow(d, 2) + 0.5 * math.pow(delta, 2) * math.exp(x0) \
            * (math.pow(self.rating(self.glicko), 2) + v - math.exp(x0)) / math.pow(d, 3)
            x1 = x0 - (h1 / h2)
            
        return math.exp(x1 / 2)
    
    def _delta(self, opp_rating, opp_RD, outcome, v):
        #the estimated improvement in rating by comparing the pre-period rating to the performance rating based only on game outcomes
        sum=self._g(opp_RD) * (outcome - self._E(opp_rating, opp_RD))
        return v*sum
    
    #helpers for glicko scale:
    def rating(self, r):
        return float((r- 1500)) / 173.7178
    def phi(self, RD):
        return float(RD / 173.7178)
    
class Meta:
    db_table = 'player'
    managed = False  # DB handled in xampp