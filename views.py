from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from .models import Player
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.http import require_POST
import json
from .Badminton_Round_Robin import roundRobin

def index(request):
    all_players = Player.objects.all().order_by('peg_name')
    context = {'players': all_players}
    return render(request, 'roundRobinWrapper/index.html', context)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def player_search_api(request):
    query = request.GET.get('q', '')
    results = []
    if len(query) >= 2:
        players = Player.objects.filter(Q(peg_name__icontains=query))[:10]
        results = [{
            'peg_name': p.peg_name,
            'peg_colour': p.peg_colour,
            'gender': p.gender,
            'id': p.id,
        } for p in players]
    return Response(results)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_active_player_api(request):
    results = roundRobin.getActivePlayers()
    return Response(results)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def player_search_id_api(request):
    query = request.GET.get('id', '')
    try:
        player_id = int(query)
    except ValueError:
        return Response({'error': 'Invalid ID format'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        player = Player.objects.get(id=player_id)
    except Player.DoesNotExist:
        return Response({'error': 'Player not found'}, status=status.HTTP_404_NOT_FOUND)

    result = {
        'peg_name': player.peg_name,
        'peg_colour': player.peg_colour,
        'gender': player.gender,
        'id': player.id
    }

    return Response(result)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def generate_game_api(request):
    return Response(roundRobin.main())

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def reset_game_history_api(request):
    return Response(roundRobin.reset())

@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def add_active_player_api(request):
    active_players = [player['peg_name'] for player in json.loads(roundRobin.getActivePlayers())]
    if request.data.get('peg_name') in active_players:
        return Response({'res':'player already added', 'code':1})
    peg_name = request.data.get('peg_name')
    peg_colour = request.data.get('peg_colour')
    gender = request.data.get('gender')
    try:
        roundRobin.addActivePlayer(peg_name, peg_colour, gender)

        return Response({'res':'player added to queue successfully.', 'code':0})

    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON array string', 'code':2}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def remove_active_player_api(request):
    peg_name = request.data.get('peg_name')
    print(peg_name)
    try:
        roundRobin.removeActivePlayer(peg_name)
        #jsonData = json.loads(data)

        return Response({'hey':'mate'})

    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON array string'}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def set_config_api(request):
    nCourts = request.data.get('nCourts')
    minutes = request.data.get('minutes')
    try:
        roundRobin.updateConfig(nCourts, minutes)

        return Response({'update':'success'})

    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON array string'}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_config_api(request):
    return Response(roundRobin.getConfig())

@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def set_timer_api(request):
    currentTime = request.data.get('currentTime')
    try:
        if currentTime < roundRobin.getTimer()['endTime']:
            print("current game not over")
            return Response({'res':1})

        roundRobin.setTimer(currentTime)

        return Response({'res':0})

    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON array string'}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_timer_api(request):
    return Response(roundRobin.getTimer())




