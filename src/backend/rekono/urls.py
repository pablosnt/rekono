'''rekono URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/

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
'''
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)
from rest_framework.urlpatterns import format_suffix_patterns

# Register your views here.

urlpatterns = [
    path('admin/', admin.site.urls),                                            # Admin site
    path('api/', include('authentications.urls')),                              # Rekono API Rest
    path('api/', include('executions.urls')),
    path('api/', include('findings.urls')),
    path('api/', include('parameters.urls')),
    path('api/', include('processes.urls')),
    path('api/', include('projects.urls')),
    path('api/', include('resources.urls')),
    path('api/', include('security.urls')),
    path('api/', include('system.urls')),
    path('api/', include('targets.urls')),
    path('api/', include('tasks.urls')),
    path('api/', include('tools.urls')),
    path('api/', include('users.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),           # Download OpenAPI specification
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),   # Swagger-UI
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc')        # Redoc
]

urlpatterns = format_suffix_patterns(urlpatterns)
