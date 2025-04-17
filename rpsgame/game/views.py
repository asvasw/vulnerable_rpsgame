import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import connection
from .models import Game
from django.contrib import messages
import random
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

@login_required
def play_game(request):
    if request.method == 'POST':
        player_choice = request.POST.get('choice')
        
        choices = ['R', 'P', 'S']
        computer_choice = random.choice(choices)
        
        result = determine_winner(player_choice, computer_choice)
        
        Game.objects.create(
            player=request.user,
            player_choice=player_choice,
            computer_choice=computer_choice,
            result=result
        )
        
        return render(request, 'game/result.html', {
            'player_choice': player_choice,
            'computer_choice': computer_choice,
            'result': result,
        })
    
    return render(request, 'game/play.html')

def determine_winner(player, computer):
    if player == computer:
        return "It's a tie!"
    
    winning_combinations = {
        'R': 'S',
        'P': 'R',
        'S': 'P',
    }
    
    if winning_combinations[player] == computer:
        return "You win!"
    else:
        return "Computer wins!"

@login_required
def game_history(request):
    # VULNERABILITY: Broken access control: allows any authenticated user
    # to view any other user's game history by manipulating the user_id parameter
    user_id = request.GET.get('user_id', request.user.id)
    games = Game.objects.filter(player_id=user_id).order_by('-created_at')
    return render(request, 'game/history.html', {'games': games})

# FIX:
# @login_required
# def game_history(request):
#     # Only allow users to see their own game history
#     games = Game.objects.filter(player=request.user).order_by('-created_at')
#     return render(request, 'game/history.html', {'games': games})

def home(request):
    return render(request, 'game/home.html')

# VULNERABILITY: Insecure Design - Allowing privilege escalation through easily accessible endpoint
def become_admin(request):
    if request.user.is_authenticated:
        request.user.is_staff = True
        request.user.is_superuser = True
        request.user.save()
        return redirect('/')
    return redirect('/accounts/login/')

# FIX: Remove this endpoint entirely

@staff_member_required
def admin_dashboard(request):
    user_stats = User.objects.annotate(game_count=Count('game')).order_by('-game_count')
    
    recent_games = Game.objects.all().order_by('-created_at')[:10]
    
    total_users = User.objects.count()
    total_games = Game.objects.count()
    user_wins = Game.objects.filter(result="You win!").count()
    computer_wins = Game.objects.filter(result="Computer wins!").count()
    ties = Game.objects.filter(result="It's a tie!").count()
    
    context = {
        'user_stats': user_stats,
        'recent_games': recent_games,
        'total_users': total_users,
        'total_games': total_games,
        'user_wins': user_wins,
        'computer_wins': computer_wins,
        'ties': ties,
    }
    
    return render(request, 'game/admin_dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def high_score_table(request):
    # VULNERABILITY: SQL Injection - Directly using raw SQL without parameterization
    limit = request.GET.get('limit', 5)
    
    # Constructing a raw SQL query unsafely with string formatting
    query = f"SELECT player_id, COUNT(*) AS score FROM game_game WHERE result = 'You win!' GROUP BY player_id ORDER BY score DESC LIMIT {limit}"
    
    # Executing the raw SQL query
    with connection.cursor() as cursor:
        # Executes multiple arbitrary statements
        cursor.executescript(query)
        cursor.execute(query)
        high_scores = cursor.fetchall()

    score_list = []
    for score in high_scores:
        player_id, score_count = score
        player = User.objects.get(id=player_id)
        score_list.append({
            'player_name': player.username,
            'score': score_count,
        })
    
    return render(request, 'game/high_score_table.html', {'high_scores': score_list})

#FIX:
#Use Django ORM which eliminates use of raw SQL 
# and is safest and most maintainable 

#@login_required
#def high_score_table(request):
#    limit = int(request.GET.get('limit', 5))

#    high_scores = (
#        Game.objects.filter(result='You win!')
#        .values('player_id')
#        .annotate(score=Count('id'))
#        .order_by('-score')[:limit]
#    )

#    score_list = [
#        {
#            'player_name': User.objects.get(id=entry['player_id']).username,
#            'score': entry['score'],
#        }
#        for entry in high_scores
#    ]

 #   return render(request, 'game/high_score_table.html', {'high_scores': score_list})