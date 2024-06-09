
from django.contrib import admin
from django.urls import path, include # 追加
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('account.urls')),  # 追加
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)