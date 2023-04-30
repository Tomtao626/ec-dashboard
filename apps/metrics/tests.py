from django.test import TestCase,Client
from django.contrib.auth import get_user_model

# Create your tests here.


class MetricsNodeTest(TestCase):
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
    #获取节点的运行状况
    def _get_nodeMetrics(self):
        name = "testing123"
        res = Client().get(
            path=f"/metrics/node/{name}/",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        print(res.data)
        # {'cpu': '31988358n', 'memory': '3030036Ki'}
        # 1m = 1*10^6n 1c = 1000m
        # 1M = 1024Ki
        self.assertEqual(res.status_code,200)
        self.assertEqual(res.data['metadata']['name'],name)

    # 获取Pod的运行状况
    def _get_podMetrics(self):
        name = "nginx-pod"
        namespace = "default"
        res = Client().get(
            path=f"/metrics/pod/{namespace}/{name}/",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        # print(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['metadata']['name'], name)
    def test(self):
        self._gettoken()
        self._get_nodeMetrics()
        self._get_podMetrics()


