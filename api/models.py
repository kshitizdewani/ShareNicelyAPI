from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static
# Create your models here.

class Profile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='profile_pics',blank=True,null=True)
    gender = models.CharField(max_length=10,choices=(('male','male'),('female','female')))
    default_pic_mapping = { 'male': 'male.jpg', 'female': 'female.jpg'}

    def get_profile_pic_url(self):
        if not self.picture:
            if self.gender:
                return static('default/{}'.format(self.default_pic_mapping[self.gender]))
        return self.picture.url
    

    def __str__(self):
        return self.user.username

class Connection(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='sender')
    connection = models.ForeignKey(User,on_delete=models.CASCADE,related_name='reciever')
    status = models.CharField(max_length=15,choices=(('requested','requested'),('accepted','accepted'),('rejected','rejected')))
    datetime = models.DateTimeField(blank=True,null=True,auto_now=True)

class Post(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    image = models.ImageField(blank=True,null=True,upload_to='posts')
    visibility = models.CharField(max_length=15,choices=(('everyone','everyone'),('connections','connections')))
    datetime = models.DateTimeField(auto_now_add=True,null=True, blank=True)
