from django.shortcuts import render
from shop.models import Product

# Create your views here.
def shop_view(request):
    product = Product.objects.all()

    context = {
        'product': product,
    }

    return render(request, 'shop.html', context)