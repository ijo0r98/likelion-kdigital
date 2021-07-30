from django.contrib import admin
from .models import Question, Choice

# Register your models here.

# class ChoiceInline(admin.StackedInline):
class ChoiceInline(admin.TabularInline): # Choice 필드들 옆으로 나열
    model = Choice
    extra = 2


class QuestionAdmin(admin.ModelAdmin):

    # fields = ['pub_date', 'question_text']  # 순서 변경

    # 해당 테이블의 row 추가 페이지에서 순서 변경 & 소제목 추가
    fieldsets = [
        # ('소제목'. {'fields': ['포함될 필드 리스트', ...]})
        ('Question title', {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    # collapse: 소제목 안의 항목들이 많을 때 감추기/펼치기 기능

    # Choice 함께 추가
    inlines = [ChoiceInline] # 섹션명(소제목)은 테이블명

    # 테이블에 저장된 row 보여주는 페이지에서 보여질 컬럼들
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    # 필터 추가
    list_filter = ['pub_date', 'question_text']
    # 검색기능 추가
    search_fields = ['question_text']


admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
