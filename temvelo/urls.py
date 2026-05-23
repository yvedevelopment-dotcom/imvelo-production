"""
URL configuration for temvelo project.

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
from django.conf import settings
from django.conf.urls.static import static
from ind_trees.views import Index, TreeListView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('ad/', admin.site.urls),
    path('', Index.as_view(), name='index'),
    path('select2/', include('django_select2.urls')),
    path('ind-trees/', include('ind_trees.urls')),
    path('stakeholders/', include('stakeholder.urls')),

    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('api/', include('ind_trees.api_urls')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
