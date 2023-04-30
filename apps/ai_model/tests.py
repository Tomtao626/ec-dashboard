from django.test import TestCase
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.conf import settings
import hashlib, time
from .models import AiModel

# Create your tests here.
class AiModelTest(TestCase):
    username = "imooc"
    password = "123"

    def setUp(self):
        print("初始化逻辑...")
        User = get_user_model()
        User.objects.create_user(
            username=self.username,
            password=self.password
        ).save()

    def _gettoken(self):
        path = "/api/token/"
        res = Client().post(
            path=path,
            data={
                'username': self.username,
                'password': self.password
            },
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        token = res.data['access']
        self.assertNotEqual(token, None)
        self.token = token

    # 模型上传
    def _ai_model_upload(self):
        path = "/ai_model/ai_model/"
        client = Client()
        with open("./temp_dir/vegetable_model_v2.h5", 'rb')as f:
            res = client.post(
                path=path,
                data={
                    'file': f,
                    'version': "vegetable_model_v2",
                    "class_names": 'yumi, fanqie, qiezi, luobo'
                },
                HTTP_AUTHORIZATION='Bearer  ' + self.token
            )
        self.assertEqual(res.status_code, 200)

    # 获取单个模型
    def _ai_model_getItem(self):
        version = "vegetable_model_v2"
        path = f"/ai_model/ai_model/{version}/"
        client = Client()
        res = client.get(
            path=path,
            HTTP_AUTHORIZATION='Bearer  ' + self.token
        )
        self.assertEqual(res.status_code, 200)

    # 获取模型列表
    def _ai_model_getList(self):
        path = "/ai_model/ai_model/"
        client = Client()
        res = client.get(
            path=path,
            HTTP_AUTHORIZATION='Bearer  ' + self.token
        )
        self.assertEqual(res.status_code, 200)

    # 模型下发
    def _ai_model_distribute(self, version, node_name, rule_name):
        path = "/ai_model/distribute/"
        client = Client()
        res = client.post(
            path=path,
            data={
                "version": version,
                "node_name": node_name,
                "rule_name": rule_name
            },
            content_type="application/json",
            HTTP_AUTHORIZATION='Bearer  ' + self.token
        )
        self.assertEqual(res.status_code, 200)
        return res.data['detail']

    def _get_distribute_status(self, serialize_id):
        path = f"/ai_model/distribute/{serialize_id}/"
        client = Client()
        while True:
            res = client.get(
                path=path,
                HTTP_AUTHORIZATION='Bearer  ' + self.token
            )
            if res.status_code == 200:
                if res.data['detail'] == "done":
                    print("模型下发完毕")
                    break
                else:
                    print(res.data)
            else:
                print(res.data)
                break
            time.sleep(1)

    # ruleendpoint创建
    def _ruleendpoint_create(self, name, rule_endpoint_type, properties=None):
        res = Client().post(
            path="/router/ruleendpoint/",
            data={
                "name": name,
                'rule_endpoint_type': rule_endpoint_type,
                'properties': properties
            },
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertIn(res.status_code, [200, 409])
        # self.assertEqual(res.data['metadata']['name'], name)

    # rule创建
    def _rule_create(self, name, source, sourceResource, target, targetResource):
        self.rep_name = name
        res = Client().post(
            path="/router/rule/",
            data={
                "name": name,
                "source": source,
                "sourceResource": sourceResource,
                "target": target,
                "targetResource": targetResource
            },
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        print(res.data)
        print(res.status_code)
        self.assertIn(res.status_code, [200, 409])
        # self.assertEqual(res.data['metadata']['name'], name)

    def test(self):
        # 路由规则
        rule_name = "imooc-rule-test"
        # 路由起点
        source_ruleendpoint = "source-ruleendpoint"
        source_ruleendpoint_type = "rest"
        source_resource = {"path": "/receive_model"}
        # 路由终点
        target_ruleendpoint = "target-ruleendpoint"
        target_ruleendpoint_type = "servicebus"
        target_properties = {
            "service_port": "5000"
        }
        target_resource = {"path": "/receive_model"}

        version = "vegetable_model_v2"
        node_name = "imooc-edge02"

        self._gettoken()
        self._ai_model_upload()
        # 路由规则创建
        self._ruleendpoint_create(source_ruleendpoint, source_ruleendpoint_type)
        self._ruleendpoint_create(target_ruleendpoint,
                                  target_ruleendpoint_type,
                                  properties=target_properties)
        self._rule_create(
            rule_name,
            source=source_ruleendpoint,
            sourceResource=source_resource,
            target=target_ruleendpoint,
            targetResource=target_resource
        )
        self._ai_model_getItem()
        self._ai_model_getList()
        serialize_id = self._ai_model_distribute(
            version=version,
            rule_name=rule_name,
            node_name=node_name
        )
        self._get_distribute_status(serialize_id)
