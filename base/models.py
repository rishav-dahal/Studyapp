from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)

    def generate_filename(instance, filename):
        extension = filename.split('.')[-1]
        unique_filename = f'{instance.email}_{instance.id}.{extension}'
        return f'avatars/{unique_filename}'

    avatar = models.ImageField(null=True, blank=True, upload_to=generate_filename, default='avatars.svg')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.name

class Topic(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name
    

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.CASCADE , null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)                 # max_length=200 means that the field can only contain up to 200 characters
    description = models.TextField(null=True, blank=True)   # null=True means that the field is allowed to be empty in the database and blank=True means that the field is allowed to be empty in forms 
    participants = models.ManyToManyField(User, related_name='participants') # related_name='participants' means that the field can be accessed using the participants attribute of the User model as user is already in host field
    updated = models.DateTimeField(auto_now=True)           # auto_now=True means that the field will be automatically set to now every time the object is saved
    created = models.DateTimeField(auto_now_add=True)       # auto_now_add=True means that the field will be automatically set to now when the object is first created.

    class Meta:
        ordering = ['-updated', '-created']                 # ordering = ['-updated', '-created'] means that the objects will be ordered by the updated field in descending order and then by the created field in descending order

    def __str__(self):
        return self.name
    
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE) # on_delete=models.CASCADE means that if the room that the message is associated with is deleted, then the message will also be deleted
                                                             # on_delete=models.PROTECT means that if the room that the message is associated with is deleted, then the message will not be deleted
                                                             # on_delete=models.SET_NULL means that if the room that the message is associated with is deleted, then the message will still exist but the room field will be set to NULL
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']    

    def __str__(self):
        return self.body[:50] + '...' if len(self.body) > 50 else self.body