from django.db import models

# Create your models here.

class ImageUploadModel(models.Model):
    # blank=True: 빈 값으로 저장 허용 (views.py에서 활용한 .is_valid() 함수가 검증 진행 시)
    description = models.CharField(max_length=255, blank=True)

    # upload_to: 저장될 파일의 경로를 지정 (ex. ‘images/2020/02/21/image.jpg’)
    document = models.ImageField(upload_to='images/%Y/%m/%d')

    # auto_now_add: 자동으로 저장 시간을 현재 시간으로 세팅
    uploaded_at = models.DateTimeField(auto_now_add=True)
