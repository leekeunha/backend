from rest_framework import serializers
from healthdiary.models import MainMenu,BodyPart,Sport, SportHistory
from collections import defaultdict
from django.db.models import Prefetch

class MainMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainMenu
        fields = ['id','title']

class BodyPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyPart
        fields = ['id','name']

class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = ['id','name']
    
class GroupedSportHistorySerializer(serializers.Serializer):
    sport_date = serializers.DateTimeField()
    bodypart_names = serializers.ListSerializer(child=serializers.CharField())
    body_part_sport_names = serializers.ListSerializer(child=serializers.DictField(child=serializers.ListSerializer(child=serializers.CharField())))

class SportHistorySerializer(serializers.ModelSerializer):
    bodypart_names = serializers.SerializerMethodField()
    body_part_sport_names = serializers.SerializerMethodField()

    class Meta:
        model = SportHistory
        fields = ['sport_date', 'bodypart_names', 'body_part_sport_names']

    def get_bodypart_names(self, obj):
        body_parts = set(SportHistory.objects.filter(sport_date=obj.sport_date).values_list('sport__bodyPart__name', flat=True))
        return list(body_parts)

    def get_body_part_sport_names(self, obj):
        body_part_sports = defaultdict(set)
        sport_histories = SportHistory.objects.filter(sport_date=obj.sport_date)
        for history in sport_histories:
            body_part_sports[history.sport.bodyPart.name].add(history.sport.name)
        return [{'body_part': bp, 'sport_names': list(sports)} for bp, sports in body_part_sports.items()]

class SetDetailSerializer(serializers.Serializer):
    set_number = serializers.IntegerField()
    weight = serializers.FloatField()
    count = serializers.IntegerField()

class SportDetailSerializer(serializers.Serializer):
    sport_name = serializers.CharField()
    sets = SetDetailSerializer(many=True)

class SportHistoryDetailSerializer(serializers.ModelSerializer):
    sport_detail = serializers.SerializerMethodField()

    class Meta:
        model = SportHistory
        fields = ['sport_date', 'sport_detail']

    def get_sport_detail(self, obj):
        queryset = SportHistory.objects.filter(sport_date=obj.sport_date, user=obj.user)
        sport_detail = []
        for sport_history in queryset:
            detail = {
                'sport_name': sport_history.sport.name,
                'sets': [
                    {
                        'set_number': set_instance.set_number,
                        'weight': set_instance.weight,
                        'count': set_instance.count
                    }
                    for set_instance in queryset.filter(sport=sport_history.sport)
                ]
            }
            if detail not in sport_detail:  # 중복 제거
                sport_detail.append(detail)
        return sport_detail

class MaxWeightAndCountSerializer(serializers.Serializer):
    sport_date = serializers.DateTimeField()
    max_weight = serializers.FloatField()
    max_weight_count = serializers.IntegerField()