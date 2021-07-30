from django.urls import path, include
from . import views # from polls import views

app_name = 'polls'

# base_url/polls **
urlpatterns = [
    path('', views.index, name='index'),
    # /polls/3 해당 설문조사 상세정보
    path('<int:question_id>/', views.detail, name='detail'),
    # /polls/3/results 해당 주제 결과
    path('<int:question_id>/results/', views.results, name='results'),
    # /polls/3/vote 설문조사 투표 -> post 요청 처리
    path('<int:question_id>/vote/', views.vote, name='vote'),
]
