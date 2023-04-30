from django.shortcuts import render
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from kubernetes.client.exceptions import ApiException
from apps.base.wrap import delete_cusobj,get_cusobj
# dm操作
class DeviceModelView(APIView):
    group = "devices.kubeedge.io"
    version = "v1alpha2"
    namespace = "default"
    plural = "devicemodels"

    # 创建DeviceModel
    def post(self, request):
        name = request.data.get("name")
        # 字段 ['version','file_md5',...]
        properties_arr = request.data.get("properties")
        print(name,properties_arr)
        if not (name and properties_arr):
            return Response({"detail": "参数缺失"}, status=status.HTTP_400_BAD_REQUEST)
        properties = []
        for i in properties_arr:
            properties.append({
                "name": i,
                'type': {
                    'string': {
                        'accessMode': 'ReadWrite',
                        'defaultValue': ''
                    }
                }
            })
        apiserver_client = settings.APISERVER_CLIENT
        cus_obj_api = apiserver_client.CustomObjectsApi()
        # 构造DeviceModel的结构
        body = {
            'apiVersion': 'devices.kubeedge.io/v1alpha2',
            "kind": 'DeviceModel',
            'metadata': {
                'name': name
            },
            "spec": {
                "properties": properties
            }
        }
        # CustomObjectsApi	create_namespaced_custom_object
        try:
            ret = cus_obj_api.create_namespaced_custom_object(
                group="devices.kubeedge.io",
                version="v1alpha2",
                namespace="default",
                plural="devicemodels",
                body=body
            )
        except ApiException as e:
            return Response({"detail": e.body}, e.status)
        return Response(ret, status=status.HTTP_200_OK)

    # 更新DeviceModel
    def put(self, request):
        name = request.data.get("name")
        # 字段 ['version','file_md5',...]
        properties_arr = request.data.get("properties")
        if not (name and properties_arr):
            return Response({"detail": "参数缺失"}, status=status.HTTP_400_BAD_REQUEST)
        properties = []
        for i in properties_arr:
            properties.append({
                "name": i,
                'type': {
                    'string': {
                        'accessMode': 'ReadWrite',
                        'defaultValue': ''
                    }
                }
            })
        # 查询DeviceModel
        apiserver_client = settings.APISERVER_CLIENT
        cus_obj_api = apiserver_client.CustomObjectsApi()
        try:
            body = cus_obj_api.get_namespaced_custom_object(
                group="devices.kubeedge.io",
                version="v1alpha2",
                namespace="default",
                plural="devicemodels",
                name=name
            )
            body['spec']['properties'] = properties
            # 更新
            res = cus_obj_api.replace_namespaced_custom_object(
                group="devices.kubeedge.io",
                version="v1alpha2",
                namespace="default",
                plural="devicemodels",
                name=name,
                body=body
            )
        except ApiException as e:
            return Response({"detail": e.body}, e.status)
        return Response(res, status=status.HTTP_200_OK)

    # 查询DeviceModel（单个/列表）
    @get_cusobj
    def get(self, request, name=None, namespace=None):
        pass

    # 删除dm
    @delete_cusobj
    def delete(self, request):
        pass


class DeviceView(APIView):
    group = "devices.kubeedge.io"
    version = "v1alpha2"
    namespace = "default"
    plural = "devices"

    # 创建Device
    def post(self, request):
        name = request.data.get("name")  # Device名称
        dm_name = request.data.get("dm_name")  # DeviceModel名称
        node_name = request.data.get("node_name")  # 节点名称
        if not (name and dm_name and node_name):
            return Response({'detail': "参数缺失"}, status=status.HTTP_400_BAD_REQUEST)

        apiserver_client = settings.APISERVER_CLIENT
        cus_obj_api = apiserver_client.CustomObjectsApi()
        # 字段信息
        twins = []
        dm = cus_obj_api.get_namespaced_custom_object(
            group="devices.kubeedge.io",
            version="v1alpha2",
            namespace="default",
            plural="devicemodels",
            name=dm_name
        )
        # 获取DeviceModel的定义字段
        properties = dm['spec']['properties']
        for i in properties:
            twins.append({
                'propertyName': i['name'],
                'desired': {
                    'metadata': {
                        'type': 'string'
                    },
                    'value': ''
                },
                'reported': {
                    'metadata': {
                        'type': 'string'
                    },
                    'value': ''
                }
            })
        # Device结构
        body = {
            'apiVersion': 'devices.kubeedge.io/v1alpha2',
            'kind': 'Device',
            'metadata': {
                "name": name
            },
            'spec': {
                'deviceModelRef': {
                    'name': dm_name
                },
                'nodeSelector': {
                    'nodeSelectorTerms': [
                        {
                            'matchExpressions': [
                                {
                                    'key': '',
                                    'operator': 'In',
                                    'values': [
                                        node_name
                                    ]
                                }
                            ]
                        }
                    ]
                }
            },
            'status': {
                'twins': twins
            }
        }

        try:
            ret = cus_obj_api.create_namespaced_custom_object(
                group="devices.kubeedge.io",
                version="v1alpha2",
                namespace="default",
                plural="devices",
                body=body
            )
        except ApiException as e:
            return Response({"detail": e.body}, e.status)

        return Response(ret, status=status.HTTP_200_OK)

    @delete_cusobj
    def delete(self, request):
        pass

    # 查询Device（单个/列表）
    @get_cusobj
    def get(self, request, name=None, namespace=None):
        pass

    # 更新Device
    def put(self, request):
        name = request.data.get("name")
        #期望值
        desired = request.data.get("desired")
        if not (name and desired):
            return Response({"detail": "参数缺失"}, status=status.HTTP_400_BAD_REQUEST)
        apiserver_client = settings.APISERVER_CLIENT
        cus_obj_api = apiserver_client.CustomObjectsApi()
        #查询Device
        body = cus_obj_api.get_namespaced_custom_object(
            group=self.group,
            version=self.version,
            namespace=self.namespace,
            plural=self.plural,
            name=name
        )
        twins = body['status']['twins']
        for i in twins:
            key = i['propertyName']
            if desired.__contains__(key):
                i['desired']['value'] = desired[key]
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
