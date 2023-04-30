from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import yaml
from yaml.scanner import ScannerError
from kubernetes.client.exceptions import ApiException


# Create your views here.

class PodView(APIView):

    # 创建Pod
    def post(self, request):
        # yaml形式
        declare = request.data.get("declare")
        namespace = request.data.get("namespace", "default")
        if not declare:
            return Response({'detail': "参数缺失"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            podyaml = yaml.safe_load(declare)
        except ScannerError as e:
            return Response({'detail': str(e.problem_mark)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # CoreV1Api	create_namespaced_pod
        apiserver_client = settings.APISERVER_CLIENT
        v1 = apiserver_client.CoreV1Api()
        try:
            ret = v1.create_namespaced_pod(
                namespace=namespace,
                body=podyaml
            )
        except ApiException as e:
            return Response({"detail": e.body}, e.status)
        return Response(ret.to_dict(), status=status.HTTP_200_OK)

    # 删除Pod
    def delete(self, request):
        pod_name = request.data.get("pod_name")
        namespace = request.data.get("namespace", "default")
        if not pod_name:
            return Response({'detail': "参数缺失"}, status=status.HTTP_400_BAD_REQUEST)
        # CoreV1Api	delete_namespaced_pod
        apiserver_client = settings.APISERVER_CLIENT
        v1 = apiserver_client.CoreV1Api()
        try:
            ret = v1.delete_namespaced_pod(
                namespace=namespace,
                name=pod_name
            )
        except ApiException as e:
            return Response({"detail": e.body}, e.status)
        return Response(ret.to_dict(), status=status.HTTP_200_OK)

    # 查看Pod的列表信息
    def get(self, request, namespace=None, name=None, node_name=None):
        apiserver_client = settings.APISERVER_CLIENT
        v1 = apiserver_client.CoreV1Api()
        # CoreV1Api	list_pod_for_all_namespaces
        if namespace:
            if name:
                # 查看单个Pod
                ret = v1.read_namespaced_pod(
                    name=name,
                    namespace=namespace
                )
                return Response(ret.to_dict(), status=status.HTTP_200_OK)
            else:
                # 查看命名空间下的Pod
                ret = v1.list_namespaced_pod(
                    namespace=namespace
                )
        else:
            # 查看所有的Pod
            ret = v1.list_pod_for_all_namespaces()
        return Response(ret.to_dict()['items'], status=status.HTTP_200_OK)
