from django.db import models
from django.utils import timezone


# Create your models here.
class SvcData(models.Model):
    objects = models.Manager()

    image_base64 = models.TextField("图像的base64")
    detect_result = models.CharField("识别结果", max_length=10)
    # 上报时间
    upload_time = models.DateTimeField("上报时间", default=timezone.now)

    class Meta:
        db_table = "svc_data"
