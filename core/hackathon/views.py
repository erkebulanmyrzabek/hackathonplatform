from django.shortcuts import render
from user.models import User
from hackathon.models import Hackathon
from django.shortcuts import render, get_object_or_404

# Create your views here.
def detailed_hackathon_view(request, pk):
    hash_code = request.GET.get("hash")
    user = get_object_or_404(User, hash_code=hash_code)
    hackathon = get_object_or_404(Hackathon, pk=pk)

    context = {
        'user': user,
        'hackathon': hackathon,
    }

    return render(request, 'hackathon_detail.html', context)

def hackathons_view(request):
    hash_code = request.GET.get("hash")
    user = get_object_or_404(User, hash_code=hash_code)
    hackathons = Hackathon.objects.all()

    context = {
        'user': user,
        'hackathons': hackathons,
    }

    return render(request, 'hackathons.html', context)