import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .Badminton_Round_Robin import roundRobin


class SessionConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.send(text_data=json.dumps({"message": "connected"}))

    def disconnect(self, close_code):
        pass

    def receive(self, data):
        self.send(text_data=json.dumps({"message": "received"}))

class PlayerListConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = "playerList"
        self.room_group_name = f"session_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()
        results = roundRobin.getActivePlayers()
        self.send(text_data=json.dumps(results))


    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        jsonData = json.loads(text_data)
        if jsonData['action'] == "add":
            active_players = [player['peg_name'] for player in json.loads(roundRobin.getActivePlayers())]
            if jsonData['peg_name'] in active_players:
                print('player is already added')
                return
            peg_name = jsonData['peg_name']
            peg_colour = jsonData['peg_colour']
            gender = jsonData['gender']
            try:
                roundRobin.addActivePlayer(peg_name, peg_colour, gender)
                print('player successfully added')
                results = roundRobin.getActivePlayers()
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name, {"type": "playerList.update", "players": results}
                )
                return
            except json.JSONDecodeError:
                print('error')
                return
        elif jsonData['action'] == "remove":
            peg_name = jsonData['peg_name']
            try:
                roundRobin.removeActivePlayer(peg_name)
                results = roundRobin.getActivePlayers()
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name, {"type": "playerList.update", "players": results}
                )
                return
            except json.JSONDecodeError:
                print('error')
                return

    def playerList_update(self, event):
        activePlayers = event["players"]

        # Send message to WebSocket
        self.send(text_data=json.dumps(activePlayers))

class CurrentGameConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = "currentGame"
        self.room_group_name = f"session_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()
        currentGames = roundRobin.getCurrentGames()
        self.send(text_data=json.dumps(currentGames))

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        currentGames = roundRobin.getCurrentGames()
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "currentGames.update", "currentGames": currentGames}
        )
        return

    def currentGames_update(self, event):
        currentGames = event["currentGames"]
        self.send(text_data=json.dumps(currentGames))

