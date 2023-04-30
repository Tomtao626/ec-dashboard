from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import AiModel
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .serializers import AiModelSerializer
import hashlib
import requests
from pathlib import Path
from kubernetes.client.exceptions import ApiException
import threading
import os, time

# 模型下发处理状态 key=serialize_id value=具体处理状态
DISTRIBUTE_MODEL_STATUS = {

}


# Create your views here.
class AiModelView(APIView):
    # 查看AI模型
    def get(self, request, version=None):
        if version:
            try:
                ai_model = AiModel.objects.get(version=version)
                serializer = AiModelSerializer(ai_model)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response({"detail": "该版本的模型不存在"}, status=status.HTTP_404_NOT_FOUND)
        else:
            ai_models = AiModel.objects.all()
            serializer = AiModelSerializer(ai_models, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    # 删除AI模型
    def delete(self, request):
        version = request.data.get("version")
        if not version:
            return Response({"detail": "模型版本必传"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            ai_model = AiModel.objects.get(version=version)
            # 移除文件
            p = Path(ai_model.file_path)
            if p.exists():
                p.unlink()
                # p.unlink()
            # 删除数据库字段
            ai_model.delete()
            return Response({"detail": "模型删除成功"}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"detail": "该版本的模型不存在"}, status=status.HTTP_404_NOT_FOUND)

    # 上传AI模型
    def post(self, request):
        # 接收参数
        file = request.FILES.get("file")
        class_names = request.data.get("class_names")  # 分类信息（分类神经网络）
        version = request.data.get("version")  # 模型版本
        if not (file and class_names and version):
            return Response({"detail": "参数缺失"}, status=status.HTTP_400_BAD_REQUEST)
        # 参数校验
        try:
            AiModel.objects.get(version=version)
            return Response({"detail": "该版本的模型已经存在"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ObjectDoesNotExist:
            pass

        # 保存模型
        fs = FileSystemStorage(location=settings.MODELS_PATH)
        filename = fs.save(file.name, file)
        with open(settings.MODELS_PATH / filename, 'rb')as f:
            content = f.read()
            my_hash = hashlib.md5()
            my_hash.update(content)
            file_md5 = my_hash.hexdigest()
        serializer = AiModelSerializer(data={
            "version": version,
            "class_names": class_names,
            "filename": filename,
            "file_md5": file_md5,
            "file_path": str(settings.MODELS_PATH / filename)
        })
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "模型上传成功！"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": serializer.errors}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DistributeAiModelThread(threading.Thread):

    def __init__(self, version, node_name, rule_name, serialize_id):
        super(DistributeAiModelThread, self).__init__()
        self.version = version
        self.node_name = node_name
        self.rule_name = rule_name
        self.serialize_id = serialize_id

    def run(self):
        global DISTRIBUTE_MODEL_STATUS
        version = self.version
        node_name = self.node_name
        rule_name = self.rule_name
        serialize_id = self.serialize_id
        DISTRIBUTE_MODEL_STATUS[serialize_id] = Response({"detail": "模型下发准备中..."}, status=status.HTTP_200_OK)
        # 模型存在性校验
        try:
            ai_model = AiModel.objects.get(version=version)
        except ObjectDoesNotExist:
            DISTRIBUTE_MODEL_STATUS[serialize_id] = Response({"detail": "模型版本不存在"}, status=status.HTTP_404_NOT_FOUND)
            return

        apiserver_client = settings.APISERVER_CLIENT
        cus_obj_api = apiserver_client.CustomObjectsApi()
        # 查询rule
        try:
            rule = cus_obj_api.get_namespaced_custom_object(
                group="rules.kubeedge.io",
                version="v1",
                namespace="default",
                plural="rules",
                name=rule_name
            )
        except ApiException:
            DISTRIBUTE_MODEL_STATUS[serialize_id] = Response({"detail": "路由规则不存在"}, status=status.HTTP_404_NOT_FOUND)
            return

            # 云端路由起点
        source_path = rule['spec']['sourceResource']['path']
        src = Path(ai_model.file_path)
        tmp_dir = Path('./tmp_dir')
        tmp_dir.mkdir(exist_ok=True)
        # 切分分片大小
        buf_size = 1 * 1024 * 1024
        total_size = os.path.getsize(ai_model.file_path)
        cur_size = 0
        index = 0
        with open(src, 'rb')as f1:
            while True:
                buf = f1.read(buf_size)
                if buf:
                    save_path = tmp_dir / f'{version}${index}.part'
                    index += 1
                    with open(save_path, 'wb') as f2:
                        f2.write(buf)
                    try:
                        CLOUD_ROUTER_HOST = settings.CLOUD_ROUTER_HOST
                        print(f'{CLOUD_ROUTER_HOST}/{node_name}/default{source_path}')
                        res = requests.post(
                            url=f'{CLOUD_ROUTER_HOST}/{node_name}/default{source_path}',
                            files={
                                'file': open(save_path, 'rb')
                            }
                        )
                        print(res.text)
                        if res.status_code != 200:
                            raise Exception
                    except Exception:
                        DISTRIBUTE_MODEL_STATUS[serialize_id] = Response({"detail": "模型下发报错！"},
                                                                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                        return

                    cur_size += len(buf)
                    save_path.unlink()  # 删除当前切片
                    DISTRIBUTE_MODEL_STATUS[serialize_id] = Response({"detail": round(cur_size / total_size, 2)},
                                                                     status=status.HTTP_200_OK)
                else:
                    DISTRIBUTE_MODEL_STATUS[serialize_id] = Response({"detail": "done"},
                                                                     status=status.HTTP_200_OK)
                    tmp_dir.rmdir()
                    break


class DistributeAiModelView(APIView):
    # 下发AI模型
    def post(self, request):
        # 模型版本
        version = request.data.get("version")
        # 节点名称
        node_name = request.data.get("node_name")
        # 路由规则名称
        rule_name = request.data.get("rule_name")
        if not (version and node_name and rule_name):
            return Response({"detail": "参数缺失"}, status=status.HTTP_400_BAD_REQUEST)

        serialize_id = str(time.time())

        distribute_aimodel_thread = DistributeAiModelThread(
            version=version,
            node_name=node_name,
            rule_name=rule_name,
            serialize_id=serialize_id
        )
        distribute_aimodel_thread.start()

        return Response(
            {
                "detail": serialize_id
            }, status=status.HTTP_200_OK
        )

    # 查询模型下发处理状态
    def get(self, request, serialize_id=None):
        if DISTRIBUTE_MODEL_STATUS.__contains__(serialize_id):
            return DISTRIBUTE_MODEL_STATUS[serialize_id]
        else:
            return Response({"detail": "无效的序列号ID"}, status=status.HTTP_200_OK)
