from django.shortcuts import render
from user.models import User
from feed.models import Post
from django.shortcuts import render, get_object_or_404

def feed_view(request):
    hash_code = request.GET.get("hash")  # Получаем хэш-код из параметра URL

    user = get_object_or_404(User, hash_code=hash_code)

    posts = Post.objects.all().order_by('-created_at')

    context = {
        'user': user,
        'posts': posts
    }
    return render(request, 'feed.html', context)
