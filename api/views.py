from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import *
from rest_framework import status
from django.contrib.auth.models import User
# Create your views here.


def all_connections(user:User):
    # requests sent by user, and accepted by the connection
    c1 = Connection.objects.filter(user=user,status='accepted')
    # requests sent by connection, and accepted by user
    c2 = Connection.objects.filter(connection=user,status='accepted')
    # combining the queries
    connections = c1 | c2
    connections = connections.order_by('-datetime')

class PostsView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        posts = Post.objects.filter(user=request.user)
        serializer = PostSerializer(posts,many=True)
        return Response(serializer.data)

    def post(self,request):
        new = Post(
            user=request.user,
            content=request.data.get('content'),
            visibility=request.data.get('visibility'),
            # image= request.data.get()
        )
        try:
            new.save()
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_201_CREATED)


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        user=request.user
        profile = Profile.objects.get(user=request.user)
        return Response({'username':user.username,'email':user.email,'firstname':user.first_name,'lastname':user.last_name,'gender':profile.gender,'picture':profile.get_profile_pic_url()})

class ConnectionsView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        user = request.user
        print(all_connections(user))
        return Response(status=status.HTTP_200_OK)
        

class UserView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            obj = dict()
            obj['username']=request.user.username
            obj['email'] = request.user.email
            obj['first_name'] = request.user.first_name
            obj['last_name'] = request.user.last_name
            obj['gender'] = profile.gender
            obj['profile_picture'] = profile.get_profile_pic_url()
            return Response(data=obj,status=status.HTTP_200_OK)
    
    def post(self,request):
        username = request.data.get('username')
        try:
            x = User.objects.get(username = username)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            new_user = User(username=username,
                            email= request.data.get('email'),
                            first_name=request.data.get('first_name'),
                            last_name = request.data.get('last_name'),
                            password = request.data.get('password'),
                            password2 = request.data.get('password2')
                            )
            new_user.save()
            x = Profile(user = new_user, gender= request.data.get('gender'))
            x.save()
            return Response(status=status.HTTP_201_CREATED)