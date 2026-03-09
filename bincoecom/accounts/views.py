from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from store.models import Order, Wishlist


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('register')

        user = User.objects.create_user(
            username=username, email=email,
            password=password,
            first_name=first_name, last_name=last_name
        )
        messages.success(request, 'Account created! Please log in.')
        return redirect('login')
    return render(request, 'accounts/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    context = {
        'orders': orders,
        'wishlist': wishlist,
        'total_orders': Order.objects.filter(user=request.user).count(),
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='login')
def profile_edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()

        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        profile.city = request.POST.get('city', '')
        profile.postal_code = request.POST.get('postal_code', '')
        profile.bio = request.POST.get('bio', '')
        if request.FILES.get('profile_pic'):
            profile.profile_pic = request.FILES['profile_pic']
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('dashboard')
    return render(request, 'accounts/profile.html', {'profile': profile})


@login_required(login_url='login')
def become_seller(request):
    profile = request.user.profile
    if profile.is_seller:
        messages.info(request, 'You are already a seller.')
        return redirect('seller_dashboard')
    
    if profile.is_seller_pending:
        messages.info(request, 'Your request to become a seller is already pending approval.')
        return redirect('dashboard')
        
    profile.is_seller_pending = True
    profile.save()
    messages.success(request, 'Your request to become a seller is pending approval from an admin. 🎉')
    return redirect('dashboard')