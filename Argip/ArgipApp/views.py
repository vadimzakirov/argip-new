from django.shortcuts import render
from django.views.generic import TemplateView
from .workers import ShopScriptWorker, ArgipWorker, GoogleWorker
from .models import Category
from .models import Product


# Create your views here.

class TestWorker(TemplateView):
    template_name = 'test.html'

    def get(self,request):
        list = []
        AWorker = ArgipWorker()
        SSWorker = ShopScriptWorker()
        SSWorker.make_products()
