"""
URL configuration for companion project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from companion.modules.models.connect_to_db import connect_to_db
from . import views
from . import chains
from . import chain
from companion.modules.documents import documents
from companion.modules.databases import databases
from dotenv import load_dotenv


load_dotenv()
connect_to_db()

urlpatterns = [
    path("", views.index, name="index"),
    path("chains/<path:chain_id>", chain.index, name="chains"),
    path("chains", chains.index, name="chains"),
    path("documents/<str:document_id>/<str:file>", documents.index, name="documents"),
    path("documents/<str:document_id>", documents.index, name="documents"),
    path("documents", documents.index, name="documents"),
    path("databases/<str:database_id>", databases.index, name="databases"),
    path("databases", databases.index, name="databases"),
    path('admin/', admin.site.urls),
]
