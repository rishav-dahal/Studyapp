from django.contrib.auth.models import User
from django.shortcuts import render ,redirect
from django.contrib.auth import login , logout , authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from .models import Room , Message , Topic
from .forms import RoomForm 

# queryset = ModelName.objects.all()  # This will return all the objects in the database 
# other methods are filter(), get(), exclude(), order_by(), etc. use are similar to SQL queries
# get() will return a single object that matches the query, if there are multiple objects that match the query, it will raise an error
# filter() will return a queryset that contains all the objects that match the query
# exclude() will return a queryset that contains all the objects that do not match the query
# order_by() will return a queryset that is ordered by the field(s) passed to it
# all() will return all the objects in the database
 
# rooms = [
#     {'id': 1, 'name': 'Lets Chat'},
#     {'id': 2, 'name': 'Python Chat'},
#     {'id': 3, 'name': 'Django Chat'},
#     {'id': 4, 'name': 'React Chat'},
#     {'id': 5, 'name': 'Vue Chat'},

# ]
# def room(request,pk):
#     room = None
#     for i in rooms:
#         if i['id'] == int(pk):
#             room = i
#     context = {'room': room}
#     return render(request, 'base/room.html', context)

def loginPage(request):

    page = 'login'
    if request.user.is_authenticated: # is_authenticated is a boolean attribute that will return True if the user is authenticated
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'user does not exist') # messages.error() will display an error message in the template
        
        user = authenticate(request, username=username, password=password) # authenticate() will check if the user exists and if the password is correct

        if user is not None:
            login(request, user) # login() will log in the user
            return redirect('home')
        else:
            messages.error(request, 'Username or Password is incorrect')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request) # logout() will log out the user
    return redirect('home')

def registerPage(request):
        form = UserCreationForm()

        if request.method == 'POST':
            form =  UserCreationForm(request.POST) # UserCreationForm() is a built-in form that will create a new user
            if form.is_valid():
                user = form.save(commit=False) # commit=False means that the form will not save the data to the database yet
                user.username = user.username.lower()
                user.save()
                login(request,user) # login() will log in the user
                return redirect('home')
            else:
                messages.error(request, 'An error has occurred during registration')
        context = {'form': form}
        return render(request, 'base/login_register.html', context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else '' # q is the name of the input field in the form
    rooms = Room.objects.filter(
                                Q(topic__name__icontains=q) | # __icontains is a field lookup that performs a case-insensitive containment test and  topic__name is a lookup that follows the relationship to the topic field and then to the name field
                                Q(name__icontains=q) | # | is the OR operator
                                Q(description__icontains=q) 
                                ) 
    topics = Topic.objects.all()
    room_count = rooms.count() # count() will return the number of objects in the queryset
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q)) # This will return all the messages in the database

    context = {
        'rooms': rooms, 
        'topics': topics, 
        'room_count': room_count,
        'room_messages': room_messages
        }
    return render(request, 'base/home.html',context)


def room(request,pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all() # message_set is the related name of the Message model in the Room model message is model name _set is the related name of the model and this room.message_set.all() will return all the messages that are related to the room
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user) # add() will add the user to the participants field of the room after the user sends a message
        return redirect('room', pk=room.id)
    
    context = {
        'room': room,
        'room_messages': room_messages , 
        'participants': participants
        }
    
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all() 
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {
        'user': user, 
        'rooms': rooms , 
        'room_messages': room_messages, 
        'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login') # login_url='login' means that if the user is not logged in, they will be redirected to the login page
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name) # get_or_create() will get the object if it exists or create it if it does not exist
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
        return redirect('home')
    
    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html',context)

@login_required(login_url='login')
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room) # instance=room means that the form will be pre-filled with the data from the room object
    topics = Topic.objects.all()
    if request.user != room.host : # this will check if the user is the host of the room
        return HttpResponse('You are not allowed here!')
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        
        # form = RoomForm(request.POST, instance=room) # instance=room means that the form will update the room object
        # if form.is_valid():
        #     form.save()
        return redirect('home')
    context = {'form': form , 'topics': topics , 'room': room}
    return render(request, 'base/room_form.html',context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host : # this will check if the user is the host of the room
        return HttpResponse('You are not allowed here!')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {'room': room}
    return render(request, 'base/delete.html', context)

@login_required(login_url='login')
def deleteMessage(request,pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user : # this will check if the user is the host of the room
        return HttpResponse('You are not allowed here!')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    context = {'obj': message}
    return render(request, 'base/delete.html', context)