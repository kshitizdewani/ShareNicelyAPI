from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import *
from rest_framework import status
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
        