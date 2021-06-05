from django.db import connection
from django.db.utils import IntegrityError
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
    def get(self,request,username):
        user=request.user
        # profile of an another person is requested
        x = dict()
        if not username == user.username:
            try:
                requested_user = User.objects.get(username=username)
                requested_profile = Profile.objects.get(user=requested_user)
                x['mine'] = False
                x['username'] = requested_user.username
                x['first_name'] = requested_user.first_name
                x['last_name'] = requested_user.last_name
                x['email'] = requested_user.email
                x['gender'] = requested_profile.gender
                x['profile_picture'] = requested_profile.get_profile_pic_url()
            except User.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            except Profile.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            #---- checking if connection exists
            connection_exists = False
            connection_status = ''
            connection = Connection.objects.filter(user=request.user,connection=requested_user) | Connection.objects.filter(connection=request.user,user=requested_user)
            if len(connection) > 0 :
                connection_exists = True
                connection_status = connection[0].status
            x['connected'] = connection_exists
            x['connection_status'] = connection_status
            
            #---- mutual friends
            requested_user_connections = set(all_connection_users(requested_user))
            user_connections = set(all_connection_users(user))
            mutual_connections = user_connections.intersection(requested_user_connections)
            y = list()
            for i in mutual_connections:
                z = dict()
                pr = Profile.objects.get(user=i)
                z['username'] = i.username
                z['first_name'] = i.first_name
                z['last_name'] = i.last_name
                z['email'] = i.email
                z['gender'] = pr.gender
                z['profile_picture'] = pr.get_profile_pic_url()
                y.append(z)
            x['mutual_connections'] = y
            
            # ----- all connections
            y = list()
            for j in list(requested_user_connections):
                z = dict()
                pr = Profile.objects.get(user=j)
                z['username'] = j.username
                z['first_name'] = j.first_name
                z['last_name'] = j.last_name
                z['email'] = j.email
                z['gender'] = pr.gender
                z['profile_picture'] = pr.get_profile_pic_url()
                y.append(z)
            x['all_connections'] = y
        
            # ---- all posts
            all_posts = Post.objects.filter(user=requested_user).order_by('-datetime')
            posts_to_show = []
            if x['connected']:
                posts_to_show = all_posts
            else:
                posts_to_show = all_posts.filter(visibility='everyone').order_by('-datetime')
            y = list()
            for post in posts_to_show:
                z = dict()
                z['content'] = post.content
                z['image'] = ''
                if post.image:
                    z['image'] = post.image.url
                z['datetime'] = post.datetime
                y.append(z)
            x['posts'] = y
                
        else:
            profile = Profile.objects.get(user=request.user)
            x ={'mine' : True,
                'username':user.username,
                'email':user.email,
                'first_name':user.first_name,
                'last_name':user.last_name,
                'gender':profile.gender,
                'picture':profile.get_profile_pic_url()
                }
            # ----- all connections
            connections = all_connection_users(user)
            y = list()
            for j in list(connections):
                z = dict()
                pr = Profile.objects.get(user=j)
                z['username'] = j.username
                z['first_name'] = j.first_name
                z['last_name'] = j.last_name
                z['email'] = j.email
                z['gender'] = pr.gender
                z['profile_picture'] = pr.get_profile_pic_url()
                y.append(z)
            x['all_connections'] = y
        
            # ---- all posts
            all_posts = Post.objects.filter(user=user).order_by('-datetime')
            posts_to_show = all_posts
            y = list()
            for post in posts_to_show:
                z = dict()
                z['content'] = post.content
                z['image'] = ''
                if post.image:
                    z['image'] = post.image.url
                z['datetime'] = post.datetime
                z['visibility'] = post.visibility
                y.append(z)
            x['posts'] = y
        
        return Response(x)   
            

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
    
class SignUp(APIView):
    def post(self,request):
        username = request.data.get('username')
        try:
            x = User.objects.get(username = username)
        except User.DoesNotExist:
            newuser = User.objects.create_user(username=username,
                            email= request.data.get('email'),
                            first_name=request.data.get('first_name'),
                            last_name = request.data.get('last_name'),
                            password = request.data.get('password'),
                            )
            newuser.save()
            x = Profile(user = newuser, gender= request.data.get('gender'))
            x.save()
            return Response(status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(status=status.HTTP_200_OK)
        
        else:
            print('inside else')
            return Response(status=status.HTTP_400_BAD_REQUEST)

class CheckUserAvailability(APIView):
    def get(self,request):
        username = request.data.get('username')
        email = request.data.get('email')
        x = User.objects.filter(username=username) | User.objects.filter(email = email)
        available = True
        if x.exists() :
            available = False
        print('available---',available)
        return Response({'available':available})

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
            action = request.data.get('action')
            print(request.data.get('connection'))
            if action in ['accept','reject']:
                request_sender=User.objects.get(username=request.data.get('connection'))
                request_reciever = request.user
                connection_obj = Connection.objects.get(user=request_sender,connection=request_reciever)
                if connection_obj.status == 'requested' and request.data.get('action')=='accept':
                    connection_obj.status = 'accepted'
                    connection_obj.save()
                    return Response(status=status.HTTP_200_OK)
                elif connection_obj.status == 'requested' and request.data.get('action') == 'reject':
                    connection_obj.delete()
                    return Response(status=status.HTTP_200_OK)
            elif action == 'cancel':
                user = request.user
                print(request.data.get('connection'))
                other = User.objects.get(username=request.data.get('connection'))
                connection_obj = Connection.objects.get(user=user,connection=other)
                connection_obj.delete()
                return Response(status=status.HTTP_200_OK)
            elif action=='request':
                user = request.user
                other = User.objects.get(username=request.data.get('connection'))
                new_connection = Connection(user=user, connection=other,status='requested')
                new_connection.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)