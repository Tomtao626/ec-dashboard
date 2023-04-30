from django.test import TestCase, Client
from django.contrib.auth import get_user_model


# Create your tests here.
class RouterTest(TestCase):
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

    # ruleendpoint创建
    def _ruleendpoint_create(self,name,rule_endpoint_type):
        res = Client().post(
            path="/router/ruleendpoint/",
            data={
                "name": name,
                'rule_endpoint_type': rule_endpoint_type
            },
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['metadata']['name'], name)

    # 查询集群下的ruleendpoint
    def _ruleendpoint_getClusterList(self):
        res = Client().get(
            path="/router/ruleendpoint/",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        self.assertNotEqual(len(res.data), 0)

    # 查询命名空间下的ruleendpoint
    def _ruleendpoint_getNamespaceList(self):
        res = Client().get(
            path="/router/ruleendpoint/default/",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        self.assertNotEqual(len(res.data), 0)

    # 查单个ruleendpoint
    def _ruleendpoint_getItem(self,name):
        res = Client().get(
            path=f"/router/ruleendpoint/default/{name}/",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['metadata']['name'], name)

    # ruleendpoint删除
    def _ruleendpoint_delete(self,name):
        res = Client().delete(
            path=f"/router/ruleendpoint/",
            data={
                'name': name
            },
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['details']['name'], name)

    # 更新rep
    def _ruleendpoint_update(self,name,rule_endpoint_type):
        res = Client().put(
            path="/router/ruleendpoint/",
            data={
                "name": name,
                'rule_endpoint_type': rule_endpoint_type
            },
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        # print(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['metadata']['name'], name)
        self.assertEqual(res.data['spec']['ruleEndpointType'], rule_endpoint_type)

    #################分割线#######################
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
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['metadata']['name'], name)

    # 查询集群下的rule
    def _rule_getClusterList(self):
        res = Client().get(
            path="/router/rule/",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        self.assertNotEqual(len(res.data), 0)

    # 查询命名空间下的rule
    def _rule_getNamespaceList(self):
        res = Client().get(
            path="/router/rule/default/",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        self.assertNotEqual(len(res.data), 0)

    # 查单个rule
    def _rule_getItem(self, rule_name):
        res = Client().get(
            path=f"/router/rule/default/{rule_name}/",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['metadata']['name'], rule_name)

    # ruleendpoint删除
    def _rule_delete(self, rule_name):
        res = Client().delete(
            path=f"/router/rule/",
            data={
                'name': rule_name
            },
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['details']['name'], rule_name)

    # 更新rule
    def _rule_update(self, name, source, sourceResource, target, targetResource):
        res = Client().put(
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
        # print(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['metadata']['name'], name)
        self.assertEqual(res.data['spec']['targetResource'], targetResource)

    def test(self):
        self._gettoken()
        # 路由规则
        rule_name = "imooc-rule-test"
        # 路由起点
        source_ruleendpoint = "source-ruleendpoint"
        source_ruleendpoint_type = "rest"
        source_resource = {"path":"/source"}
        # 路由终点
        target_ruleendpoint = "target-ruleendpoint"
        target_ruleendpoint_type = "eventbus"
        target_ruleendpoint_type_updated = "servicebus"
        target_resource = {"path": "/target"}
        target_resource_updated = {"path": "/target2"}

        self._ruleendpoint_create(source_ruleendpoint,source_ruleendpoint_type)
        self._ruleendpoint_create(target_ruleendpoint,target_ruleendpoint_type)
        self._ruleendpoint_update(target_ruleendpoint,target_ruleendpoint_type_updated)

        self._rule_create(rule_name,
                          source=source_ruleendpoint,
                          sourceResource=source_resource,
                          target=target_ruleendpoint,
                          targetResource=target_resource)
        self._rule_update(
            rule_name,
            source=source_ruleendpoint,
            sourceResource=source_resource,
            target=target_ruleendpoint,
            targetResource=target_resource_updated)

        self._ruleendpoint_getClusterList()
        self._ruleendpoint_getNamespaceList()
        self._ruleendpoint_getItem(source_ruleendpoint)

        self._rule_getClusterList()
        self._rule_getNamespaceList()
        self._rule_getItem(rule_name)

        self._rule_delete(rule_name)
        self._ruleendpoint_delete(source_ruleendpoint)
        self._ruleendpoint_delete(target_ruleendpoint)
