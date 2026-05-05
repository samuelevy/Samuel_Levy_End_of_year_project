import json
from time import timezone
from urllib import request
from django.shortcuts import get_object_or_404, render
from django.views import View
import math
from django.http import Http404, JsonResponse
from player.models import Player
from user.models import AppUser
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

from game.models import Game #To display profiles

# Create your views here.
class PlayerView(View):
    
    #Glicko constant
    _tau = 0.5
    
    #PARAMETERS AND CLASS FUNCTIONS
    #Getters and setters
    def setlastgame(self, date):
        self.last_game_date=date
    def getElo(self):
        return self.elo
    def getGlicko(self):
        return self.glicko
    def getLastGame(self):
        return self.last_game_date
    
    def get(self, request, user_id=None, **kwargs):
        if kwargs.get('action') == 'leaderboard':
            return self.leaderboard(request)
    
        if user_id:
            player = get_object_or_404(Player.objects.select_related('user'), user_id=user_id)
            return JsonResponse({
                'user_id': player.user.user_id,
                'name': player.user.name,
                'role': player.user.role,
                'elo': float(player.elo),
                'glicko': float(player.glicko),
                'glicko_rd': float(player.glicko_rd),
                'volatility': float(player.volatility),
                'tries': player.tries,
                'gamecount': player.gamecount,
                'last_game_date': player.last_game_date.isoformat() if player.last_game_date else None
            })
        else:
            players = Player.objects.select_related('user').all()
            
            players_data = [{
                'user_id': p.user.user_id,
                'name': p.user.name,
                'elo': float(p.elo),
                'glicko': float(p.glicko),
                'tries': p.tries
            } for p in players]
            
            return JsonResponse({
                'count': len(players_data),
                'players': players_data
            })
            
    def post(self, request):
        data = json.loads(request.body)
        app_user = AppUser.objects.create(
            name=data['name'],
            role='PLAYER'
        )
        # Create Player
        player = Player.objects.create(
            user=app_user,
            elo=data.get('elo', 1500),
            glicko=data.get('glicko', 1500),
            glicko_rd=data.get('glicko_rd', 350)
        )
        
        return JsonResponse({
            'message': 'Player created successfully',
            'user_id': player.user.user_id,
            'name': player.user.name,
            'elo': float(player.elo),
            'glicko': float(player.glicko)
        }, status=201)
        
    def patch(self, request, user_id):
        data = json.loads(request.body)
        try:
            player = Player.objects.select_related('user').get(user__user_id=user_id)
        except Player.DoesNotExist:
            return JsonResponse({'error': 'Player not found'}, status=404)
        
        # Get both players
        player = get_object_or_404(Player, user_id=user_id)
        opponent = get_object_or_404(Player, user_id=data['opponent_id'])
        
        result = float(data['result'])
        rating_system = data.get('rating_system', 'glicko')
        
        if rating_system == 'elo':
            # Calculate expected score
            expected = 1 / (1 + 10 ** ((float(opponent.elo) - float(player.elo)) / 400))
            
            # Update Elo
            new_rating = player.update_elo(expected, result)
            
            return JsonResponse({
                'message': 'Elo updated successfully',
                'user_id': user_id,
                'new_elo': new_rating,
                'expected_score': round(expected, 4)
            })
        
        elif rating_system == 'glicko':
            # Update Glicko-2
            new_rating = player.update_glicko(
                opp_rating=float(opponent.glicko),
                opp_rd=float(opponent.glicko_rd),
                outcome=result
            )
            
            # Update game statistics
            player.tries += 1
            player.last_game_date = timezone.now()
            player.save()
            
            return JsonResponse({
                'message': 'Glicko-2 updated successfully',
                'user_id': user_id,
                'new_glicko': float(player.glicko),
                'new_rd': float(player.glicko_rd),
                'new_volatility': float(player.volatility),
                'total_games': player.tries
            })
            
    #Get top 20 by glicko
    def leaderboard(self, request):
        limit = int(request.GET.get('limit', 20))
        min_games = int(request.GET.get('min_games', 0))
        players=Player.objects.select_related('user')
        
        if min_games > 0:
            players = players.filter(tries__gte=min_games)
        players = players.order_by('-glicko')[:limit]
        
        leaderboard_data =[]
        for rank, player in enumerate(players, start=1):
            leaderboard_data.append({
                'rank': rank,
                'name': player.user.name,
                'elo': float(player.elo),
                'glicko': float(player.glicko),
                'last_game_date': player.last_game_date.isoformat() if player.last_game_date else None
            })
        return JsonResponse({
            'leaderboard': leaderboard_data,
            'limit': limit,
            'min_games': min_games
        })
  
#FOR THE HTML VIEW      
class LeaderBoardView(View):
    def get(self, request):
        limit = int(request.GET.get('limit', 20))
        min_games = int(request.GET.get('min_games', 0))
        players=Player.objects.select_related('user')
        
        if min_games > 0:
            players = players.filter(tries__gte=min_games)
        players = players.order_by('-glicko')[:limit]
        
        #For the HTML view
        leaderboard_data =[]
        for rank, player in enumerate(players, start=1):
            leaderboard_data.append({
                'rank': rank,
                'user_id': player.user_id,
                'name': player.user.name,
                'elo': int(player.elo),
                'glicko': int(player.glicko),
                'last_game_date': player.last_game_date.isoformat() if player.last_game_date else None
            })
            
        isAdmin=request.user.is_authenticated and request.user.role=='ADMIN'
        template='admin_home.html' if isAdmin else 'homepage.html'
        return render(request, template, {
            'players': leaderboard_data,
            'limit': limit,
            'min_games': min_games
        })
        
class ProfileView(LoginRequiredMixin, View): #class to display profile
    def get(self, request, user_id=None):
        if user_id is None:
            if not hasattr(request.user, 'player_profile'):
                raise Http404("No player profile found")
            player = request.user.player_profile
        else:
            player=get_object_or_404(Player.objects.select_related('user'),user_id=user_id)
        p1_games=Game.objects.filter(player1=player)
        p2_games=Game.objects.filter(player2=player)
        wins_as_p1 = p1_games.filter(outcome=player.user_id).count()
        wins_as_p2 = p2_games.filter(outcome=player.user_id).count()
        total_wins = wins_as_p1 + wins_as_p2
        draws_as_p1 = p1_games.filter(outcome__isnull=True).count()
        draws_as_p2 = p2_games.filter(outcome__isnull=True).count()
        total_draws = draws_as_p1 + draws_as_p2
        
        losses=player.gamecount - total_wins - total_draws
        if player.gamecount > 0:
            winrate = total_wins / player.gamecount * 100
        else:
            winrate=0
            
        rank = Player.objects.filter(glicko__gt=player.glicko).count() + 1
            
        context={
            'player':player,
            'profile_data':{
                'user_id': player.user.user_id,
                'name': player.user.name,
                'rank': rank,
                'elo': int(player.elo),
                'glicko': int(player.glicko),
                'game_count': player.gamecount,
                'winrate':winrate,
                'last_game_date': player.last_game_date
            }
        }
            
        return render(request, 'profile.html', context)