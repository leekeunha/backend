from django.shortcuts import get_object_or_404
from healthdiary.models import MainMenu,BodyPart, Sport, SportHistory
from healthdiary.api.serializers import MainMenuSerializer,BodyPartSerializer, SportSerializer,SportHistorySerializer, SportHistoryDetailSerializer,MaxWeightAndCountSerializer
from rest_framework import generics, permissions
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_datetime
from rest_framework.pagination import PageNumberPagination
from collections import defaultdict
from rest_framework.exceptions import ValidationError
from django.utils.dateparse import parse_datetime
from datetime import datetime
from django.db.models import Max, OuterRef, Subquery, Count, F
class MainMenuListView(generics.ListAPIView):
    queryset = MainMenu.objects.all()
    serializer_class = MainMenuSerializer

class BodyPartListView(generics.ListAPIView):
    queryset = BodyPart.objects.all()
    serializer_class = BodyPartSerializer

class SportListCreate(generics.ListCreateAPIView):
    serializer_class = SportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        body_part_id = self.request.query_params.get('body-part-id', None)

        admin_id = 1

        queryset = Sport.objects.filter(Q(createdBy_id=user) | Q(createdBy_id=admin_id))

        if body_part_id is not None:
            queryset = queryset.filter(bodyPart_id=body_part_id)
        
        return queryset.order_by('-created')
    
    def perform_create(self, serializer):
        body_part_id = self.request.data.get('bodyPartId')
        instance = serializer.save(createdBy=self.request.user,bodyPart_id=body_part_id)
        return Response({
            'id': instance.id,
            'name': instance.name,
        },status= status.HTTP_201_CREATED)

class SportRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Sport.objects.filter(createdBy=user)
    
    def delete(self, request, *args, **kwargs):
        isinstance = self.get_object()
        isinstance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CustomPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 100
        
class SportHistoryListCreate(generics.ListCreateAPIView):
    serializer_class = SportHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        body_part_id = self.request.query_params.get('body-part-id', None)
        queryset = SportHistory.objects.filter(user=user).order_by('-sport_date')
        if body_part_id:
            queryset = queryset.filter(sport__bodyPart_id=body_part_id)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        grouped = defaultdict(list)
        for history in queryset:
            grouped[history.sport_date].append(history)

        results = []
        for date, histories in grouped.items():
            serializer = self.get_serializer(histories, many=True)
            results.append({
                'sport_date': date,
                'bodypart_names': set(),
                'body_part_sport_names': defaultdict(set)
            })
            for data in serializer.data:
                results[-1]['bodypart_names'].update(data['bodypart_names'])
                for item in data['body_part_sport_names']:
                    results[-1]['body_part_sport_names'][item['body_part']].update(item['sport_names'])

            results[-1]['bodypart_names'] = list(results[-1]['bodypart_names'])
            results[-1]['body_part_sport_names'] = [{ 'body_part': k, 'sport_names': list(v) } for k, v in results[-1]['body_part_sport_names'].items()]

        page = self.paginate_queryset(results)  # 페이지네이션 적용
        if page is not None:
            return self.get_paginated_response(page)

        return Response(results)

    def perform_create(self, serializer):
        user = self.request.user
        request_data = self.request.data
        sport_date_str = request_data.get('sport_date')
        sport_date = parse_datetime(sport_date_str)
        histories = request_data.get('history', [])

        created_histories = []
        for entry in histories:
            sport_id = entry.get('sportId')
            sets = entry.get('sets', [])
            
            for set_entry in sets:
                set_number = set_entry.get('setNumber')
                count = set_entry.get('count')
                weight = set_entry.get('weight')
                
                count = int(count) if count.isdigit() else 0
                weight = float(weight) if weight.replace('.','',1).isdigit() else 0.0
                
                created_histories.append(
                    SportHistory(
                        user=user,
                        sport_id=sport_id,
                        set_number=set_number,
                        count=count,
                        weight=weight,
                        sport_date=sport_date
                    )
                )
        
        SportHistory.objects.bulk_create(created_histories)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        created_instances = SportHistory.objects.filter(
            user=request.user, 
            sport_date=parse_datetime(request.data.get('sport_date'))
        )
        new_serializer = SportHistorySerializer(created_instances, many=True)
        headers = self.get_success_headers(new_serializer.data)

        return Response(new_serializer.data, status=status.HTTP_201_CREATED, headers=headers)



class SportHistoryDetail(generics.ListAPIView):
    serializer_class = SportHistoryDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        sport_date_str = self.request.query_params.get('date')
        if not sport_date_str:
            raise ValidationError({'date': 'This field is required.'})
        
        date_formats = ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S.%fZ']
        sport_date = None
        
        for fmt in date_formats:
            try:
                sport_date = datetime.strptime(sport_date_str, fmt)
                break
            except ValueError:
                continue
        
        if sport_date is None:
            raise ValidationError({'date': 'Invalid date format.'})
        
        return SportHistory.objects.filter(
            user=user, 
            sport_date=sport_date
        ).order_by('id').first()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        if queryset:
            serializer = self.get_serializer(queryset)
            return Response(serializer.data)
        else:
            
            return Response([])

class MaxWeightAndCount(generics.ListAPIView):
    serializer_class = MaxWeightAndCountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.id
        sport_id = self.request.query_params.get('sportId')

        # 최대 중량을 찾기 위한 Subquery
        max_weight_subquery = SportHistory.objects.filter(
            user_id=user_id,
            sport_id=sport_id,
            sport_date=OuterRef('sport_date')
        ).annotate(
            max_weight=Max('weight')
        ).values('max_weight')[:1]

        # 최대 중량과 해당 중량의 반복 횟수를 포함하는 쿼리셋
        queryset = SportHistory.objects.filter(
            user_id=user_id,
            sport_id=sport_id,
            weight=Subquery(max_weight_subquery)
        ).values(
            'sport_date',
            'weight',
            'count'
        ).annotate(
            max_weight=Max('weight'),
            max_weight_count='count'
        ).order_by('sport_date')

        return queryset

from django.db.models import Max, F

class MaxWeightAndCount(generics.ListAPIView):
    serializer_class = MaxWeightAndCountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.id
        sport_id = self.request.query_params.get('sportId')

        # 해당 사용자와 스포츠에 대한 최대 무게와 해당 무게에서의 운동 횟수를 추출
        max_weight_data = SportHistory.objects.filter(
            user_id=user_id, sport_id=sport_id
        ).values(
            'sport_date'
        ).annotate(
            max_weight=Max('weight')
        )

        # 최대 무게와 해당 무게에서의 운동 횟수를 결합
        queryset = SportHistory.objects.filter(
            user_id=user_id, sport_id=sport_id
        ).annotate(
            max_weight=F('weight'),
            max_weight_count=F('count')
        ).filter(
            sport_date__in=max_weight_data.values('sport_date'),
            weight__in=max_weight_data.values('max_weight')
        ).order_by('sport_date')

        return queryset