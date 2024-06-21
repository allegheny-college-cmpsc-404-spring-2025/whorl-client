from .views import *
from django.urls import path

app_name = "persona"

urlpatterns  = [
    path('search/<str:persona_name>', PersonaSearchView.as_view, name = "persona-search"),
    path('create/<str:persona_name>', PersonaCreateView.as_view(), name = "persona-create"),
    path('generate/<str:persona_name>', StreamPersonaGenerateView.as_view(), name = "persona-generate"),
]
