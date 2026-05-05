from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from player.models import Player
from django.db.models import Q
from django.db import transaction
from .models import Game
import datetime

# Create your views here.

class SearchPlayers(LoginRequiredMixin, View):
    def get(self, request):
        #IF ABLE TO, IMPLEMENT CHECK THAT USER IS ADMIN. ELSE, SHOULDN'T BE AN ISSUE AS THEY ARE THE ONLY ONES WHO HAVE ACCESS TO IT
        #if not hasattr(request.user, 'admin_user'): #Only valid if user is an admin
            #return JsonResponse({'error': 'You need to be an admin to access this!'}, status=403)
            
        query = request.GET.get('q', '').strip()
        if len(query)<2: #Make sure that the search is long enough so we can actually have a result
            return JsonResponse({'players':[], 'message': '2 chars or more'})
        #Search engine (by name or id)
        q_filter = Q(user__name__icontains=query)
        if query.isdigit():
            q_filter |= Q(user__user_id=int(query))
        
        players = Player.objects.filter(q_filter).select_related('user')[:20]

        player_list=[]
        for i in players:
            player_list.append({'id': i.user_id,
                                'name': i.user.name,
                                'elo': i.elo})
        return JsonResponse({'players':player_list,
                             'count': len(player_list)}) 
        
        
class RecordGame(LoginRequiredMixin, View):
    
    def get(self, request):
        return render(request, 'games.html')
    
    def post(self, request):
    ###############################################
    #IF ABLE TO, IMPLEMENT CHECK THAT USER IS ADMIN. ELSE, SHOULDN'T BE AN ISSUE AS THEY ARE THE ONLY ONES WHO HAVE ACCESS TO IT
    ########################################################  
        #if not hasattr(request.user, 'admin_user'):
            #return JsonResponse({'error': 'Admin access required'}, status=403)
            
        try:
            player1_id = request.POST.get('player1_id')
            player2_id = request.POST.get('player2_id')
            outcome = request.POST.get('outcome')
            
            if not all([player1_id, player2_id, outcome]):
                return JsonResponse({'error': "Missing required field, please enter players and results"}, status=400)
            
            try:
                outcome = int(outcome)
            except ValueError:
                return JsonResponse({'error': "Outcome must be 0, 1, or 2"}, status=400)
            
            valid=[0, 1, 2] #1: player 1 wins, 2: player 2 wins, 0: draw
            if outcome not in valid:
                return JsonResponse({'error':"Please enter valid outcome"}, status=400)
            
            try:
                p1=Player.objects.get(user_id=player1_id)
                p2=Player.objects.get(user_id=player2_id)
            except Player.DoesNotExist:
                return JsonResponse({'error':"Player(s) not found"}, status=404)
            
            if player1_id==player2_id:
                return JsonResponse({'error': "Cannot record game between same player"}, status=400)
        except Exception as e:
            return JsonResponse({'error': "Invalid data"}, status=400)
        
        try:
            with transaction.atomic():
                if outcome == 0:  # Draw
                    db_outcome = None
                elif outcome == 1:  # Player 1 wins
                    db_outcome = p1.user_id
                else:  # outcome_code == 2, Player 2 wins
                    db_outcome = p2.user_id
                
                game = Game.objects.create(player1=p1,
                                           player2=p2,
                                           outcome=db_outcome)
                
                self.updateRating(game, p1, p2)
                
                return JsonResponse({'success':True,
                                     'game_id': game.game_id,
                                     'message': 'Game recorded successfully',
                                     'details':{
                                         'player1': p1.user.name,
                                         'player2':p2.user.name,
                                         'outcome': outcome,
                                         'new_ratings':{
                                             'p1_elo':float(p1.elo),
                                             'p2_elo':float(p2.elo)
                                         }
                                     }}, status=201)
        except Exception as e:
            return JsonResponse({
                'error': f'Failed to create game: {str(e)}'
            }, status=500)
            
    def updateRating(self, game, p1, p2):
        result1=game.resp1()
        result2=game.resp2()
        
        p1_glicko = float(p1.glicko)
        p1_glicko_rd = float(p1.glicko_rd)
        p1_elo = float(p1.elo)
        
        p2_glicko = float(p2.glicko)
        p2_glicko_rd = float(p2.glicko_rd)
        p2_elo = float(p2.elo)
        
        #Expected values for elo
        exp1=1/(1+10**(float(p2_elo - p1_elo)/400))
        exp2=1/(1+10**(float(p1_elo - p2_elo)/400))
        
        p1.update_elo(exp1, result1)
        p2.update_elo(exp2, result2)
        
        #Update Glicko
        p1.update_glicko(p2_glicko, p2_glicko_rd, result1)
        p2.update_glicko(p1_glicko, p1_glicko_rd, result2)
        
        #Save data
        p1.tries += 1
        p2.tries += 1
        p1.last_game_date = game.played_at
        p2.last_game_date = game.played_at
        
        p1.save()
        p2.save()