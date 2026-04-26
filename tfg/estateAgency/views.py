from django.shortcuts import render
from django.views import generic
from .services import propertyService, locationService

# Create your views here.
class IndexView(generic.TemplateView):
    template_name = "estateAgency/index.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        locations = locationService.get_all_locations()
        context["locations"] = locations

        return context
    
class PropertiesView(generic.TemplateView):

    template_name = "estateAgency/properties.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        flag = self.request.GET.get("type")
        city = self.request.GET.get("city")


        if flag not in ["sale", "rent_short", "rent_long"]:
            flag = "sale"

        properties = propertyService.get_properties_by_operation(flag, city=city)

        context["properties"] = properties
        context["selected_type"] = flag

        return context