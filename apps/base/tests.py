from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
# Create your tests here.

class BaseTest(TestCase):

    username = "imooc"
    password = "123"

    def setUp(self):
        print("初始化逻辑...")
        User = get_user_model()
        User.objects.create_user(
            username=self.username,
            password=self.password
        ).save()


    def _testview(self):
        path = "/test/"
        res = Client().get(path=path,HTTP_AUTHORIZATION="Bearer  "+ self.token)
        # print(res.status_code)
        self.assertEqual(res.status_code,200)
        self.assertEqual(res.data['detail'],'test')

    def _gettoken(self):
        path = "/api/token/"
        res = Client().post(
            path=path,
            data={
                'username':self.username,
                'password':self.password
            },
            content_type="application/json"
        )
        self.assertEqual(res.status_code,200)
        token = res.data['access']
        self.assertNotEqual(token,None)
        self.token = token
    def _test_k8s_apiserver(self):
        from django.conf import settings
        v1 = settings.APISERVER_CLIENT.CoreV1Api()
        print("Listing pods with their IPs:")
        ret = v1.list_pod_for_all_namespaces(watch=False)
        self.assertNotEqual(len(ret.items),0)
        # for i in ret.items:
        #     print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
    def test(self):
        self._gettoken()
        self._testview()
        self._test_k8s_apiserver()
