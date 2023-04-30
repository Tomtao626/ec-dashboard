from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.contrib.auth import get_user_model


# Create your tests here.
class SvcDataTest(TestCase):
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

    def _svc_data_create(self):
        res = Client().post(
            path="/svc_data/svc_data/",
            data={
                "image_base64": "ttt",
                'detect_result': "fanqie"
            },
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 201)

    def _svc_data_getList(self):
        res = Client().get(
            path="/svc_data/svc_data/",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data),1)

    def test(self):
        self._gettoken()
        self._svc_data_create()
        self._svc_data_getList()