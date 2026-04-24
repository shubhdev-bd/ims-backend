
# """
# URL configuration for Inventory Management System
# """
# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# from rest_framework import permissions
# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi

# # urlpatterns = [
# #     path('admin/', admin.site.urls),
# #     path('api/auth/', include('apps.authentication.urls')),
# #     path('api/inventory/', include('apps.inventory.urls')),
# # ]

# from django.urls import path, include, re_path  # 👈 add re_path

# urlpatterns = [
#     path('admin/', admin.site.urls),

#     # Your APIs
#     path('api/auth/', include('apps.authentication.urls')),
#     path('api/inventory/', include('apps.inventory.urls')),

#     # 🔥 Swagger URLs
#     re_path(r'^swagger(?P<format>\.json|\.yaml)$',
#             schema_view.without_ui(cache_timeout=0)),

#     path('swagger/',
#          schema_view.with_ui('swagger', cache_timeout=0),
#          name='swagger-ui'),

#     path('redoc/',
#          schema_view.with_ui('redoc', cache_timeout=0),
#          name='redoc'),
# ]

# # Serve media files in development
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# schema_view = get_schema_view(
#     openapi.Info(
#         title="Inventory API",
#         default_version='v1',
#         description="API documentation for Inventory Management System",
#         contact=openapi.Contact(email="admin@example.com"),
#     ),
#     public=True,
#     permission_classes=(permissions.AllowAny,),
# )

"""
URL configuration for Inventory Management System
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from apps.inventory.views import home  # or wherever you added it



from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# ✅ DEFINE FIRST
schema_view = get_schema_view(
    openapi.Info(
        title="Inventory API",
        default_version='v1',
        description="API documentation for Inventory Management System",
        contact=openapi.Contact(email="admin@example.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# ✅ THEN USE
urlpatterns = [
    path('', home),  # 👈 THIS LINE ADDS HOMEPAGE

    path('admin/', admin.site.urls),

    # APIs
    path('api/auth/', include('apps.authentication.urls')),
    path('api/inventory/', include('apps.inventory.urls')),

    # Swagger
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0)),

    path('swagger/',
         schema_view.with_ui('swagger', cache_timeout=0),
         name='swagger-ui'),

    path('redoc/',
         schema_view.with_ui('redoc', cache_timeout=0),
         name='redoc'),
]

# Media
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)