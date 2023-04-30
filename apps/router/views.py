from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from kubernetes.client.exceptions import ApiException
from apps.base.wrap import get_cusobj, delete_cusobj
import json


class RuleEndPointView(APIView):
    group = "rules.kubeedge.io"
    version = "v1"
    namespace = "default"
    plural = "ruleendpoints"

    # ruleendpoint创建
    def post(self, request):
        name = request.data.get("name")
        rule_endpoint_type = request.data.get("rule_endpoint_type")
        properties = request.data.get("properties")
        if not (name and rule_endpoint_type):
            return Response({"detail": "参数缺失"}, status=status.HTTP_400_BAD_REQUEST)
        # 对ruleendpint 的类型校验
        rule_endpoint_types = ['rest', 'servicebus', 'eventbus']
        if rule_endpoint_type not in rule_endpoint_types:
            return Response({"detail": "参数错误，rule_endpoint_type仅支持" + ",".join(rule_endpoint_types)},
                            status=status.HTTP_400_BAD_REQUEST)

        if not properties:
            properties = {}
        # 构造RuleEndpoint结构
        body = {
            "apiVersion": "rules.kubeedge.io/v1",
            "kind": "RuleEndpoint",
            "metadata": {
                "name": name
            },
            "spec": {
                "ruleEndpointType": rule_endpoint_type,
                "properties": properties
            }
        }
        apiserver_client = settings.APISERVER_CLIENT
        cus_obj_api = apiserver_client.CustomObjectsApi()
        try:
            ret = cus_obj_api.create_namespaced_custom_object(
                group=self.group,
                version=self.version,
                namespace=self.namespace,
                plural=self.plural,
                body=body
            )
        except ApiException as e:
            print(e)
            return Response({"detail": e.body}, e.status)
        return Response(ret, status=status.HTTP_200_OK)

    @get_cusobj
    def get(self, request, name=None, namespace=None):
        pass

    @delete_cusobj
    def delete(self, request):
        pass

    # 更新ruleendpoint
    def put(self, request):
        name = request.data.get("name")
        rule_endpoint_type = request.data.get("rule_endpoint_type")
        properties = request.data.get("properties")
        if not (name and rule_endpoint_type):
            return Response({"detail": "参数缺失"}, status=status.HTTP_400_BAD_REQUEST)
        # 对ruleendpint 的类型校验
        rule_endpoint_types = ['rest', 'servicebus', 'eventbus']
        if rule_endpoint_type not in rule_endpoint_types:
            return Response({"detail": "参数错误，rule_endpoint_type仅支持" + ",".join(rule_endpoint_types)},
                            status=status.HTTP_400_BAD_REQUEST)

        if not properties:
            properties = {}

        apiserver_client = settings.APISERVER_CLIENT
        cus_obj_api = apiserver_client.CustomObjectsApi()
        try:
            # 查询rep
            body = cus_obj_api.get_namespaced_custom_object(
                group=self.group,
                version=self.version,
                namespace=self.namespace,
                plural=self.plural,
                name=name
            )
            spec = body['spec']
            spec['ruleEndpointType'] = rule_endpoint_type
            spec['properties'] = properties
            # 更新
            res = cus_obj_api.replace_namespaced_custom_object(
                group=self.group,
                version=self.version,
                namespace=self.namespace,
                plural=self.plural,
                name=name,
                body=body
            )
            return Response(res, status=status.HTTP_200_OK)
        except ApiException as e:
            return Response({"detail": e.body}, status=e.status)


class RuleView(APIView):
    group = "rules.kubeedge.io"
    version = "v1"
    namespace = "default"
    plural = "rules"

    @get_cusobj
    def get(self, request, name=None, namespace=None):
        pass

    @delete_cusobj
    def delete(self, request):
        pass

    # 创建Rule
    def post(self, request):
        name = request.data.get("name")
        source = request.data.get("source")
        sourceResource = request.data.get("sourceResource")
        target = request.data.get("target")
        targetResource = request.data.get("targetResource")
        if not (name, source, sourceResource, target, targetResource):
            return Response({"detail": "参数缺失"}, status=status.HTTP_400_BAD_REQUEST)
        # 构造Rule结构
        body = {
            "apiVersion": "rules.kubeedge.io/v1",
            "kind": "Rule",
            "metadata": {
                "name": name
            },
            "spec": {
                "source": source,
                "sourceResource": sourceResource,
                "target": target,
                "targetResource": targetResource
            }
        }
        apiserver_client = settings.APISERVER_CLIENT
        cus_obj_api = apiserver_client.CustomObjectsApi()
        try:
            ret = cus_obj_api.create_namespaced_custom_object(
                group=self.group,
                version=self.version,
                namespace=self.namespace,
                plural=self.plural,
                body=body
            )
        except ApiException as e:
            return Response({"detail": e.body}, e.status)
        return Response(ret, status=status.HTTP_200_OK)

    # 更新Rule
    def put(self, request):
        name = request.data.get("name")
        source = request.data.get("source")
        sourceResource = request.data.get("sourceResource")
        target = request.data.get("target")
        targetResource = request.data.get("targetResource")
        if not (name, source, sourceResource, target, targetResource):
            return Response({"detail": "参数缺失"}, status=status.HTTP_400_BAD_REQUEST)
        apiserver_client = settings.APISERVER_CLIENT
        cus_obj_api = apiserver_client.CustomObjectsApi()
        try:
            # 查询rule
            body = cus_obj_api.get_namespaced_custom_object(
                group=self.group,
                version=self.version,
                namespace=self.namespace,
                plural=self.plural,
                name=name
            )
            spec = body['spec']
            spec['source'] = source
            spec['sourceResource'] = sourceResource
            spec['target'] = target
            spec['targetResource'] = targetResource
            # 更新
            res = cus_obj_api.replace_namespaced_custom_object(
                group=self.group,
                version=self.version,
                namespace=self.namespace,
                plural=self.plural,
                name=name,
                body=body
            )
            return Response(res, status=status.HTTP_200_OK)
        except ApiException as e:
            return Response({"detail": e.body}, status=e.status)
