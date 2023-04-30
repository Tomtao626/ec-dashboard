from rest_framework.generics import ListCreateAPIView
from .serializers import SvcDataSerializer
from .models import SvcData
from rest_framework.permissions import AllowAny
from rest_framework.authentication import BaseAuthentication
from rest_framework.parsers import BaseParser
import json


class PlainTextParser(BaseParser):
    """
    Plain text 解析器。
    """
    media_type = 'text/plain'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        只需返回一个表示请求正文的字符串。
        """
        text = stream.read()
        print(text)
        return json.loads(text)


class MyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        return None


class SvcDataView(ListCreateAPIView):
    # 数据解析，kubeedge上传的为text/plain
    parser_classes = [PlainTextParser]
    # 数据上传权限放行，否则边缘数据无法上传，在实际工作场景中，小伙伴需要考虑数据安全性校验
    authentication_classes = [MyAuthentication]
    permission_classes = [AllowAny]
    serializer_class = SvcDataSerializer
    queryset = SvcData.objects.all()
