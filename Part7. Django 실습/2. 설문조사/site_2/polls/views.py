from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from .models import Question, Choice

# Create your views here.

def index(request):

    latest_question_list = Question.objects.order_by('-pub_date')
    context = {'latest_question_list': latest_question_list}

    # return HttpResponse('Hello World!);
    return render(request, 'polls/index.html', context)


def detail(request, question_id):

    ## django.http.Http404
    # try:
    #     question = Question.objects.get(pk=question_id)
    #
    # except Question.DoesNotExists: # error 종류
    #     raise Http404("Question {} does not exist".format(question_id))

    ## django.shortcuts.get_object_or_404
    q = get_object_or_404(Question, pk=question_id)

    return render(request, 'polls/detail.html', {'question': q })


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    # choice = get_objects_or_404(Choice, fk=quiestion_id)

    return render(request, 'polls/results.html', {'question': question})


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id) # 설문조사 주제

    # print(request.POST) # 'choice_select': ['8'] dict형태로 넘어옴

    try:
        selected_choice = question.choice_set.get(pk = request.POST['choice_select']) # <input name="choice_select">

    except: # 에러 발생, request.POST['choice_select']값이 없을 경우
       context = {'question': question, 'error_message': "You didn't select a choice."}
       return render(request, 'polls/detail.html', context)

    else: # try 문에서 에러가 발생하지 않았을 경우에만 실행
        selected_choice.votes += 1
        selected_choice.save() # 실제 DB 저장
        return redirect('polls:results', question_id = question.id)

    # finally: 항상 실행
