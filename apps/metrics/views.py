from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
# Create your views here.
class MetricsNodeView(APIView):
    #获取节点的运行状态
    def get(self,request,name=None):
        if not name:
            return Response({'detail': "参数缺失"}, status=status.HTTP_400_BAD_REQUEST)
        group = "metrics.k8s.io"
        version = "v1beta1"
        plural = "nodes"

        # CustomObjectsApi	get_cluster_custom_object
        apiserver_client = settings.APISERVER_CLIENT
        cus_obj_api = apiserver_client.CustomObjectsApi()
        ret = cus_obj_api.get_cluster_custom_object(
            group=group,
            version=version,
            plural=plural,
            name=name
        )
        return Response(ret, status=status.HTTP_200_OK)

class MetricsPodView(APIView):
    #获取节点的运行状态
    def get(self,request,namespace=None,name=None):
        if not (name and namespace):
            return Response({'detail': "参数缺失"}, status=status.HTTP_400_BAD_REQUEST)
        group = "metrics.k8s.io"
        version = "v1beta1"
        plural = "pods"

        # CustomObjectsApi	get_cluster_custom_object
        apiserver_client = settings.APISERVER_CLIENT
        cus_obj_api = apiserver_client.CustomObjectsApi()
        ret = cus_obj_api.get_namespaced_custom_object(
            namespace = namespace,
            group=group,
            version=version,
            plural=plural,
            name=name
        )
        return Response(ret, status=status.HTTP_200_OK)