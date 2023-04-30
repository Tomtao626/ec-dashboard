from django.test import TestCase, Client
from django.contrib.auth import get_user_model


# Create your tests here.


class NodeTest(TestCase):
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

    # 获取节点列表
    def _get_nodeList(self):
        res = Client().get(
            path="/node/node/",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        # print(res)
        self.assertEqual(res.status_code, 200)
        self.assertNotEqual(len(res.data), 0)

    # 获取单个节点
    def _get_nodeItem(self):
        name = "imooc-edge01"
        res = Client().get(
            path=f"/node/node/{name}/",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        # print(res)
        self.assertEqual(res.status_code, 200)
        # self.assertNotEqual(len(res.data), 0)
        # 返回的节点信息与查询的节点信息一致
        self.assertEqual(res.data['metadata']['name'], name)

    # 获取纳管节点token
    def _node_join(self):
        res = Client().get(
            path=f"/node/join/",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        token = res.data['detail']
        self.assertNotEqual(token, None)
        # print(token)

    # 添加节点label
    def _node_addLabel(self):
        label_key = "test"
        label_value = "123"
        node_name = "testing123"
        res = Client().put(
            path="/node/label/",
            data={
                "label_key": label_key,
                "label_value": label_value,
                "node_name": node_name
            },
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['metadata']['labels'][label_key], label_value)

    #删除节点的label
    def _node_deleteLabel(self):
        label_key = "test"
        node_name = "testing123"
        res = Client().delete(
            path="/node/label/",
            data={
                "label_key": label_key,
                "node_name": node_name
            },
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['metadata']['labels'].get(label_key, None), None)

    def test(self):
        self._gettoken()
        self._get_nodeList()
        self._get_nodeItem()
        self._node_join()
        self._node_addLabel()
        self._node_deleteLabel()
