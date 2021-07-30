from django.shortcuts import render, redirect
from .forms import SimpleUploadForm, ImageUploadForm
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .cv_functions import cv_detect_face

# Create your views here.

def first_view(request):
    return render(request, 'opencv_webapp/first_view.html', {})


def simple_upload(request):

    if request.method == 'POST': # POST request
        # request.POST['name'] # input 태그의 name
        # request.Files # 제출된 파일의 원본 <MultiValueDict: {'image': [<InMemoryUploadedFile: ses.jpg (image/jpeg)>]}>

        form = SimpleUploadForm(request.POST, request.FILES)

        if form.is_valid():
            myfile = request.FILES['image'] # 이미지 이름이 아닌 이미지 객체 (image.jpg)

            # DB 사용하지 않을 때
            fs = FileSystemStorage()

            filename = fs.save(myfile.name, myfile) # 이미지 이름, 저장된 파일 객체 반환
            uploaded_file_url = fs.url(filename) # '/media/image.jpg'

            context = {'form': form, 'uploaded_file_url': uploaded_file_url}
            return render(request, 'opencv_webapp/simple_upload.html', context)

    else: # GET request
        form = SimpleUploadForm()
        context = {'form': form}
        return render(request, 'opencv_webapp/simple_upload.html', context) # input & label tag


def detect_face(request):

    if request.method == 'POST':
        # 비어있는 form에 입력받은 값을 받아 검증
        form = ImageUploadForm(request.POST, request.FILES) # filled form

        if form.is_valid():
            # 실제로 저장하기 전 변경하거나 추가 가능
            post = form.save(commit=False)
            ###
            ### 필요한 작업 추가
            ###
            post.save() # DB에 실제로 form 객체('form')에 채워져 있는 데이터를 저장

            # post는 save() 후 DB에 저장된 ImageUploadModel 클래스 객체 자체를 갖고 있게 됨 (record 1건에 해당)
            imageURL = settings.MEDIA_URL + form.instance.document.name # 실제로 db에 저장되어있는 경로 '/media/images/2021/07/30/image.jpg'
            # document: ImageUploadModel Class의 document 필드
            # print(form.instance, form.instance.document.name, form.instance.document.url)

            cv_detect_face(settings.MEDIA_ROOT_URL + imageURL)

            return render(request, 'opencv_webapp/detect_face.html', {'form':form, 'post':post})

    else:
        form = ImageUploadForm() # empty form
        return render(request, 'opencv_webapp/detect_face.html', {'form':form})
