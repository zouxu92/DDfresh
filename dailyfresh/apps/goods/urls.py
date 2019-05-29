from django.conf.urls import url
from goods import views
from goods.views import IndexView

urlpatterns = [
	url(r'^index$', IndexView.as_view(), name='index'), # 首页

]