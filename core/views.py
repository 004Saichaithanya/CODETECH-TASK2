from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile,Post,LikePost,FollowerCount
from itertools import chain
import random
# Create your views here.


@login_required(login_url="signin")
def index(request):
    user_object=User.objects.get(username=request.user.username)
    user_profile=Profile.objects.get(user=user_object)

    user_following_list=[]
    feed=[]

    user_following=FollowerCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)
    
    for usernames in user_following_list:
        feed_lists=Post.objects.filter(user=usernames)
        feed.append(feed_lists)
    
    feed_list=list(chain(*feed))

    #User suggestions
    all_users=User.objects.all()

    user_following_all=[]

    for users in user_following:
        user_list=User.objects.get(username=users.user)
        user_following_all.append(user_list)



    user_suggestion_list=[x for x in list(all_users) if (x not in list(user_following_all))]
    current_user=User.objects.filter(username=request.user.username)
    final_user_suggestion=[x for x in list(user_suggestion_list) if (x not in list(current_user))]
    random.shuffle(final_user_suggestion)

    username_profile=[]
    username_profile_list=[]

    for users in final_user_suggestion:
        username_profile.append(users.id)
    
    for ids in username_profile:
        u_profile=Profile.objects.filter(id_user=ids)
        username_profile_list.append(u_profile)
    
    suggestions_username_profile_list=list(chain(*username_profile_list))
    


    
    return render(request, "index.html",{'user_profile':user_profile,'posts':feed_list,'suggestions_username_profile_list':suggestions_username_profile_list[:5]})

@login_required(login_url="signin")
def search(request):
    user_object=User.objects.get(username=request.user.username)
    user_profile_current=Profile.objects.get(user=user_object)
    if request.method == 'POST':
        username=request.POST['username']
        user_profile=User.objects.filter(username__icontains=username)
        user_profiles=[]
        user_profile_list=[]
        
        for users in user_profile:
            user_profiles.append(users.id)
        
        for ids in user_profiles:
            profile_lists=Profile.objects.filter(id_user=ids)
            user_profile_list.append(profile_lists)
        
        user_profile_list=list(chain(*user_profile_list))



    return render(request,"search.html",{'user_profile':user_profile_current,'username_profile_list':user_profile_list})

@login_required(login_url="signin")
def follow(request):
    if request.method == "POST":
        follower=request.POST['follower']
        user=request.POST['user']

        if FollowerCount.objects.filter(follower=follower,user=user).first():
            delete_follower=FollowerCount.objects.get(follower=follower,user=user)
            delete_follower.delete()
            request.session['flag']=False
            
        else:
            new_follower=FollowerCount.objects.create(follower=follower,user=user)
            new_follower.save()
            request.session['flag']=True
        return redirect('/profile/'+user)
    else:
        return redirect('/')


@login_required(login_url="signin")
def like_post(request):
    username=request.user.username
    post_id=request.GET.get('post_id')
    post=Post.objects.get(id=post_id)

    like_filer=LikePost.objects.filter(post_id=post_id,username=username).first()

    if like_filer is None:
        new_like=LikePost.objects.create(post_id=post_id,username=username)
        new_like.save()
        post.no_of_likes=post.no_of_likes+1
        post.save()
        return redirect('/')
    else:
        like_filer.delete()
        post.no_of_likes=post.no_of_likes-1
        post.save()
        return redirect('/')

@login_required(login_url="signin")
def profile(request,pk):
    user_object=User.objects.get(username=pk)
    user_profile=Profile.objects.get(user=user_object)
    user_posts=Post.objects.filter(user=pk)
    no_user_posts=len(user_posts)
    user_followers=len(FollowerCount.objects.filter(user=pk))
    user_following=len(FollowerCount.objects.filter(follower=pk))

    follower=request.user.username
    user=pk

    if FollowerCount.objects.filter(follower=follower,user=user).first():
        button_text="Unfollow"
    else:
        button_text="Follow"

    context={
        'user_object':user_object,
        'user_profile':user_profile,
        'user_posts':user_posts,
        'no_user_posts':no_user_posts,
        'user_followers':user_followers,
        'user_following':user_following,
        'button_text':button_text,
    }
    return render(request,"profile.html",context)



@login_required(login_url="signin")
def upload(request):
    if request.method == 'POST':
        user=request.user.username
        image=request.FILES.get('image_upload')
        caption=request.POST['caption']
        new_post=Post.objects.create(user=user,image=image,caption=caption)
        new_post.save()
        return redirect('/')
    else:
        return redirect('/')

@login_required(login_url="signin")
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        if request.FILES.get("image") == None:
            image = user_profile.profileimg
            bio = request.POST["bio"]
            location = request.POST["location"]

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        if request.FILES.get("image") != None:
            image = request.FILES.get("image")
            bio = request.POST["bio"]
            location = request.POST["location"]

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        return redirect("settings")

    return render(request, "setting.html", {"user_profile": user_profile})


def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm = request.POST["confirm"]
        print(username)

        if password == confirm:
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email Already Exists")
                return redirect("signup")
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username is already taken")
                return redirect("signup")
            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password
                )
                user.save()
                print(f"sucessfully created User:{username}!")
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                user_model = User.objects.get(username=username)
                user_profile = Profile.objects.create(
                    user=user_model, id_user=user_model.id
                )
                user_profile.save()
                return redirect("settings")
        else:
            messages.info(request, "Password does not match!")
            return redirect("signup")

    return render(request, "signup.html")


def signin(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("/")
        else:
            messages.info(request, "Credentials Invalid!")
            return redirect("signin")

    return render(request, "signin.html")


@login_required(login_url="signin")
def logout(request):
    auth.logout(request)
    return redirect("signup")
