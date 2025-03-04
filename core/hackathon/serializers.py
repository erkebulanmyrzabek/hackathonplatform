from rest_framework import serializers
from .models import Hackathon, Tag, PrizePlaces
from user.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'telegram_id', 'xp', 'level']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'created_at']

class PrizePlacesSerializer(serializers.ModelSerializer):
    winner = UserSerializer(read_only=True)
    
    class Meta:
        model = PrizePlaces
        fields = ['id', 'place', 'prize_amount', 'winner']

class HackathonSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    prize_places = PrizePlacesSerializer(many=True, read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    is_registration_open = serializers.BooleanField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Hackathon
        fields = [
            'id', 'name', 'description', 'type',
            'start_registation', 'end_registration',
            'anonce_start', 'start_hackathon', 'end_hackathon',
            'image', 'created_at', 'status', 'status_display',
            'participants', 'tags', 'prize_places',
            'prize_pool', 'number_of_winners',
            'participants_count', 'is_registration_open'
        ] 