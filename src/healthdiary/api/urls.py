from django.urls import path
from . import views
app_name = 'healthdiary'
urlpatterns = [
    path('main-menus/',views.MainMenuListView.as_view()),
    path('body-parts/',views.BodyPartListView.as_view()),
    path('sports/', views.SportListCreate.as_view()),
    path('sports/<int:pk>', views.SportRetrieveUpdateDestroy.as_view()),
    path('sport-history/', views.SportHistoryListCreate.as_view()),
    path('sport-history-detail/', views.SportHistoryDetail.as_view()),
    path('max-weight-and-count/', views.MaxWeightAndCount.as_view()),
]
