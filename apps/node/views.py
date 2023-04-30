from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import base64


# Create your views here.

class NodeView(APIView):

    # 获取节点列表/单个节点信息
    def get(self, request, name=None):
        apiserver_client = settings.APISERVER_CLIENT
        v1 = apiserver_client.CoreV1Api()
        # print("Listing pods with their IPs:")
        if name:
            # 单个节点
            ret = v1.read_node(name=name)
            return Response(ret.to_dict(), status=status.HTTP_200_OK)
        else:
            # 节点列表 只展示边缘节点
            ret = v1.list_node(watch=False,label_selector='node-role.kubernetes.io/edge')
            return Response(ret.to_dict()['items'], status=status.HTTP_200_OK)


class NodeJoinView(APIView):

    # 获取边缘节点纳管的Token
    def get(self, request):
        # CoreV1Api	read_namespaced_secret
        apiserver_client = settings.APISERVER_CLIENT
        v1 = apiserver_client.CoreV1Api()
        ret = v1.read_namespaced_secret(
            name="tokensecret",
            namespace="kubeedge"
        )
        tokendata = ret.data['tokendata']
        token = base64.b64decode(tokendata)
        return Response({
            'detail': token
        }, status=status.HTTP_200_OK)


class NodeLabelView(APIView):

    # 添加/更新label
    def put(self, request):

        label_key = request.data.get("label_key")
        label_value = request.data.get("label_value")
        node_name = request.data.get("node_name")

        if not (label_key and node_name):
            return Response({'detail': "参数缺失"}, status=status.HTTP_400_BAD_REQUEST)

        # CoreV1Api	replace_node
        apiserver_client = settings.APISERVER_CLIENT
        v1 = apiserver_client.CoreV1Api()
        body = v1.read_node(name=node_name)
        labels = body.metadata.labels
        labels[label_key] = label_value
        ret = v1.replace_node(
            name=node_name,
            body=body
        )
        return Response(ret.to_dict(), status=status.HTTP_200_OK)

    # 删除label
    def delete(self, request):
        label_key = request.data.get("label_key")
        node_name = request.data.get("node_name")
        if not (label_key and node_name):
            return Response({'detail': "参数缺失"}, status=status.HTTP_400_BAD_REQUEST)
        # CoreV1Api	replace_node
        apiserver_client = settings.APISERVER_CLIENT
        v1 = apiserver_client.CoreV1Api()
        body = v1.read_node(name=node_name)
        labels = body.metadata.labels
        if labels.__contains__(label_key):
            del labels[label_key]
            ret = v1.replace_node(
                name=node_name,
                body=body
            )
            return Response(ret.to_dict(), status=status.HTTP_200_OK)
        else:
            return Response({'detail': "该label不存在"}, status=status.HTTP_400_BAD_REQUEST)
