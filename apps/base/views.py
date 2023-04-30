from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Create your views here.

#测试接口
class TestView(APIView):

    def get(self,request):
        return Response(
            {'detail':'test'},status=status.HTTP_200_OK
        )
