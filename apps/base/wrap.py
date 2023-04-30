from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from kubernetes.client.exceptions import ApiException
from functools import wraps
# 删除自定义资源注解
def delete_cusobj(f):
    @wraps(f)
    def wrap_func(self, *args, **kwargs):
        name = self.request.data.get("name")
        apiserver_client = settings.APISERVER_CLIENT
        cus_obj_api = apiserver_client.CustomObjectsApi()
        try:
            ret = cus_obj_api.delete_namespaced_custom_object(
                group=self.group,
                version=self.version,
                namespace=self.namespace,
                plural=self.plural,
                name=name
            )
        except ApiException as e:
            return Response({"detail": e.body}, e.status)
        return Response(ret, status=status.HTTP_200_OK)

    return wrap_func


# 获取自定义资源注解
def get_cusobj(f):
    @wraps(f)
    def wrap_func(self, *args, **kwargs):
        name = kwargs.get("name")
        namespace = kwargs.get("namespace")
        apiserver_client = settings.APISERVER_CLIENT
        cus_obj_api = apiserver_client.CustomObjectsApi()
        if namespace:
            if name:
                # 查询单个的dm
                ret = cus_obj_api.get_namespaced_custom_object(
                    group=self.group,
                    version=self.version,
                    namespace=self.namespace,
                    plural=self.plural,
                    name=name
                )
                return Response(ret, status=status.HTTP_200_OK)
            else:
                # 查询指定的namespace下面的dm
                ret = cus_obj_api.list_namespaced_custom_object(
                    group=self.group,
                    version=self.version,
                    namespace=self.namespace,
                    plural=self.plural,
                )
                return Response(ret['items'], status=status.HTTP_200_OK)
        else:
            # 查询cluster
            ret = cus_obj_api.list_cluster_custom_object(
                group=self.group,
                version=self.version,
                plural=self.plural,
            )
            return Response(ret['items'], status=status.HTTP_200_OK)

    return wrap_func
