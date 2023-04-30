from django.test import TestCase, Client
from django.contrib.auth import get_user_model


# Create your tests here.


class DeviceTest(TestCase):
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

    # DeviceModel创建
    def _devicemodel_create(self):
        name = "imooc-dm-test"
        self.dm_name = name
        res = Client().post(
            path="/device/devicemodel/",
            data={
                "name": name,
                'properties': ['propertyName1', 'propertyName2']
            },
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        # print(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['metadata']['name'], name)

    # DeviceModel更新
    def _devicemodel_update(self):
        name = self.dm_name
        res = Client().put(
            path="/device/devicemodel/",
            data={
                "name": name,
                'properties': ['propertyName1', 'propertyName2', 'propertyName3']
            },
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        # print(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['metadata']['name'], name)

    # 查询集群下的dm
    def _devicemodel_getClusterList(self):
        res = Client().get(
            path="/device/devicemodel/",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        self.assertNotEqual(len(res.data), 0)

    # 查询命名空间下的dm
    def _devicemodel_getNamespaceList(self):
        res = Client().get(
            path="/device/devicemodel/default/",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        self.assertNotEqual(len(res.data), 0)

    # 查单个dm
    def _devicemodel_getItem(self):
        name = self.dm_name
        res = Client().get(
            path=f"/device/devicemodel/default/{name}/",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['metadata']['name'], name)

    def _devicemodel_delete(self):
        name = self.dm_name
        res = Client().delete(
            path=f"/device/devicemodel/",
            data={
                'name': name
            },
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['details']['name'], name)

    # 创建Device
    def _device_create(self):
        name = "imooc-device-test"
        self.device_name = name
        res = Client().post(
            path="/device/device/",
            data={
                "name": name,
                'dm_name': self.dm_name,
                'node_name': 'testing123'
            },
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        # print(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['metadata']['name'], name)

    # Device删除
    def _device_delete(self):
        name = self.device_name
        res = Client().delete(
            path=f"/device/device/",
            data={
                'name': name
            },
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['details']['name'], name)

    # 查询集群下的device
    def _device_getClusterList(self):
        res = Client().get(
            path="/device/device/",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        self.assertNotEqual(len(res.data), 0)

    # 查询命名空间下的device
    def _device_getNamespaceList(self):
        res = Client().get(
            path="/device/device/default/",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        self.assertNotEqual(len(res.data), 0)

    # 查单个device
    def _device_getItem(self):
        name = self.device_name
        res = Client().get(
            path=f"/device/device/default/{name}/",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['metadata']['name'], name)

    #更新Device
    def _device_update(self):
        name = self.device_name
        propertyName = 'propertyName3'
        value = 'hhh'
        res = Client().put(
            path="/device/device/",
            data={
                "name": name,
                'desired': {
                    propertyName: value
                }
            },
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer  " + self.token
        )
        # print(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['metadata']['name'], name)
        for i in res.data['status']['tiwns']:
            if i['propertyName'] == propertyName:
                self.assertEqual(i['desired']['value'],value)

    def test(self):
        self._gettoken()
        self._devicemodel_create()
        self._devicemodel_update()
        self._devicemodel_getClusterList()
        self._devicemodel_getNamespaceList()
        self._devicemodel_getItem()
        self._device_create()
        self._device_update()
        self._device_getClusterList()
        self._device_getNamespaceList()
        self._device_getItem()
        self._device_delete()
        self._devicemodel_delete()
