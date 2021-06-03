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
    return connections

def all_connection_users(user : User):
    # requests sent by user, and accepted by the connection
    c1 = Connection.objects.filter(user=user,status='accepted')
    # requests sent by connection, and accepted by user
    c2 = Connection.objects.filter(connection=user,status='accepted')
    # combining the queries
    connections = c1 | c2
    users = list()
    for connection in list(connections):
        if connection.user == user :
            users.append(connection.connection)
        elif connection.connection == user :
            users.append(connection.user)
    return users

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
        return Response({'username':user.username,'email':user.email,'first_name':user.first_name,'last_name':user.last_name,'gender':profile.gender,'picture':profile.get_profile_pic_url()})

class ConnectionsView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        user = request.user
        connections = all_connections(user)
        
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
            if request.user.first_name:
                obj['first_name'] = request.user.first_name
            else: obj['first_name'] = ''
            if request.user.last_name:
                obj['last_name'] = request.user.last_name
            else: obj['last_name'] = ''
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

                            )
            new_user.save()
            x = Profile(user = new_user, gender= request.data.get('gender'))
            x.save()
            return Response(status=status.HTTP_201_CREATED)
        
        
class FeedView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        objects = all_connection_users(request.user)
        posts = Post.objects.filter(user=request.user)
        print(all_connection_users(request.user))
        objlist = list()
        for user in objects:
            x = Post.objects.filter(user=user)
            posts |= x
        posts = posts.order_by('-datetime')
        # print(posts)
        for post in posts:
            obj = dict()
            if post.user.first_name:
                obj['first_name'] = post.user.first_name
            else:
                obj['first_name'] = ''
            if post.user.last_name:
                obj['last_name'] = post.user.last_name
            else:
                obj['last_name'] = ''
            # obj['last_name'] = post.user.last_name
            profile = Profile.objects.get(user=post.user)
            obj['profile_picture'] = profile.get_profile_pic_url()
            obj['username'] = post.user.username
            obj['content'] = post.content
            obj['visibility'] = post.visibility
            obj['datetime'] = post.datetime
            if post.image:
                obj['image'] = post.image.url
            objlist.append(obj)
        return Response(objlist)

class SearchView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,request,term=''):
        # term = request.data.get('term')
        print(request.data)
        print('term',term)
        if term in ['',None]:
            # empty data
            return Response([])
        #searching by name
        by_name = User.objects.filter(first_name__contains=term) | User.objects.filter(last_name__contains=term)
#        searching by phone
        by_phone = User.objects.filter(username__contains=term)
#         searching by email
        by_email = User.objects.filter(email__contains=term)
        searchresults = by_email | by_name | by_phone
        searched_connections = list()
        searched_non_connections = list()
        user_connections=all_connection_users(request.user)
        for user in searchresults:
            if user == request.user:
                # to ignore self
                continue
            x = dict()
            x['username'] = user.username
            if user.last_name:
                x['first_name'] = user.first_name
            else:
                x['first_name'] = ''
            if user.last_name:
                x['last_name'] = user.last_name
            else:
                x['last_name'] = ''
            if user.email:
                x['email'] = user.email
            else:
                x['email'] = ''
            profile = Profile.objects.get(user=user)
            x['gender'] = profile.gender
            x['profile_picture'] = profile.get_profile_pic_url()
            x['isConnection'] = False
            if user in user_connections:
                x['isConnection'] = True
                searched_connections.append(x)
            else:
                searched_non_connections.append(x)
        return Response(searched_connections+searched_non_connections)


class ConnectionRequests(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        user = request.user
        requests = Connection.objects.filter(connection=user,status='requested')
        objlist = list()
        for connection in requests:
            profile= Profile.objects.get(user = connection.user)
            connection_user = connection.user
            x = dict()
            x['profile_picture'] = profile.get_profile_pic_url()
            x['first_name'] = connection_user.first_name
            x['last_name'] = connection_user.last_name
            x['username'] = connection_user.username
            x['email'] = connection_user.email
            x['gender'] = profile.gender
            objlist.append(x)
        return Response(data=objlist)
    
    def post(self,request):
        user = request.user
        if request.data.get('connection'):
            print(request.data.get('connection'))
            request_sender=User.objects.get(username=request.data.get('connection'))
            request_reciever = request.user
            connection_obj = Connection.objects.get(user=request_sender,connection=request_reciever)
            if connection_obj.status == 'requested' and request.data.get('action')=='accept':
                connection_obj.status = 'accepted'
                connection_obj.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)