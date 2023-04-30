from django.db import models


# Create your models here.

class AiModel(models.Model):

    objects = models.Manager()

    version = models.CharField("AI模型版本",max_length=100)
    class_names = models.CharField("模型分类信息",max_length=100)
    filename = models.CharField("模型文件名称",max_length=100)
    file_md5 = models.CharField("模型的md5编码",max_length=100)
    file_path = models.CharField("文件保存路径",max_length=100)

    class Meta:
        db_table = "ai_model"
