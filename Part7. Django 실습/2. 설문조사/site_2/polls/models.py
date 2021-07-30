from django.db import models
from django.utils import timezone
import datetime

# Create your models here.

class Question(models.Model): # 설문조사 주제
    question_text = models.CharField(max_length=200) # 주제명
    pub_date = models.DateTimeField('date published') # ‘date published’ : 관리자 페이지에서 보여질 항목명
    # pub_date = models.DateTimeField('date published', auto_now_add=True)
    ## auto_now_add: 생성일자, 최초 저장 시에만 현재날짜 적용
    ## auto_now: 수정일자, 저장될때마다 날짜 갱신

    def was_published_recently(self): # 현재기준 하루 이내에 올라온 설문조사인지
        now = timezone.now()
        return now >= self.pub_date >= now - datetime.timedelta(days=1)

    # 해당 함수의 리턴값이 boolean임을 확정해줌 -> 관리자페이지에서 아이콘으로 보여짐
    was_published_recently.boolean = True
    # 해당 컬럼에 대한 정렬순서
    was_published_recently.admin_order_field = 'pub_date'
    # 함수 명 대신 컬럼명으로 나올 내용 지정
    was_published_recently.short_description = 'Published Recently?'

    def __str__(self):
        return self.question_text


class Choice(models.Model): # 설문조사 주제별 선택지, 득표 수
   # 자동으로 Question table의 pk를 fk로 세팅
   # on_delete=models.CASCADE Question(질문) 항목 삭제 시 연관된 선택지들도 모두 자동 삭제
   question = models.ForeignKey(Question, on_delete=models.CASCADE) # 설문조사 주제 id (fk)
   choice_text = models.CharField(max_length=200) # 선택지
   votes = models.IntegerField(default=0) # 해당 선택지의 득표 수

   def __str__(self):
       return self.choice_text
