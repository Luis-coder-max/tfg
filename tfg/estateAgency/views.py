from django.shortcuts import render
from django.views import generic

# Create your views here.
class IndexView(generic.TemplateView):
    template_name = "estateAgency/index.html"
    
class patata(generic.TemplateView):
    template_name = "estateAgency/patata.html"