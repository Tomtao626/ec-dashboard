from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.contrib.auth import get_user_model


# Create your tests here.


class PodTest(TestCase):
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
    #创建Pod
    def _pod_create(self):
        with open("./crds/nginx-pod.yaml",'r')as f:
            declare = f.read()
        res = Client().post(
            path="/pod/pod/",
            data={
              'declare':declare
            },
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        print(res.data)
        self.assertEqual(res.status_code,200)
        self.assertNotEqual(res.data['metadata']['name'],None)

    #删除Pod
    def _pod_delete(self):
        res = Client().delete(
            path="/pod/pod/",
            data={
              'pod_name':"nginx-pod"
            },
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        print(res.data)
        self.assertEqual(res.status_code,200)
        self.assertNotEqual(res.data['metadata']['name'], None)

    #查看所有的Pod
    def _get_podList(self):
        res = Client().get(
            path="/pod/pod/",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        self.assertNotEqual(len(res.data),0)


    #查看命名空间下的Pod
    def _get_podNamespacedList(self):
        namespace = "default"
        res = Client().get(
            path=f"/pod/pod/{namespace}/",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        self.assertNotEqual(len(res.data),0)

    # 查看单个Pod
    def _get_podItem(self):
        namespace = "default"
        name = "nginx-pod"
        res = Client().get(
            path=f"/pod/pod/{namespace}/{name}/",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['metadata']['name'], name)


    def test(self):
        self._gettoken()
        # self._pod_create()
        # self._pod_delete()
        self._get_podList()
        self._get_podNamespacedList()
        self._get_podItem()