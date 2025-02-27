from django.shortcuts import render
from user.models import User
from feed.models import Post, Webinar, Casecup
from django.shortcuts import render, get_object_or_404
from hackathon.models import Hackathon


def feed_view(request):
    hash_code = request.GET.get("hash")

    user = get_object_or_404(User, hash_code=hash_code)

    posts = Post.objects.all().order_by('-created_at')
    hackathons = Hackathon.objects.all()
    webinars = Webinar.objects.all()
    casecups = Casecup.objects.all()

    context = {
        'user': user,
        'posts': posts,
        'hackathons': hackathons,
        'webinars': webinars,
        'casecups': casecups
    }
    return render(request, 'feed.html', context)

