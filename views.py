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

def index(request):
    all_players = Player.objects.all().order_by('peg_name')
    context = {'players': all_players}
    return render(request, 'roundRobinWrapper/index.html', context)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) # AllowAny if public
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
@permission_classes([IsAuthenticated]) # AllowAny if public
def get_active_player_api(request):
    with open("active_players.txt", "r") as file:
        content = file.read()
        results = {
            'active_players': content,
        }
        return Response(results)

@api_view(['POST'])
@permission_classes([IsAuthenticated]) # AllowAny if public
def save_active_player_api(request):
    array_str = request.data.get('data')

    try:
        # Parse the string back into a Python list
        number_list = json.loads(array_str)

        # Optional: Validate it's a list of numbers
        if not all(isinstance(n, (int, float)) for n in number_list):
            return Response({'error': 'Invalid number list'}, status=400)

        # Respond or process as needed
        with open("active_players.txt", 'w') as file:
            file.write(str(number_list))

        return Response({'received': number_list, 'sum': sum(number_list)})

    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON array string'}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) # AllowAny if public
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





