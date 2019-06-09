from django.conf.urls import url
from cart.views import CartAddView, CartInfoView

urlpatterns = [
    url(r'^add$', CartAddView.as_view(), name='add'), # 购物车添加
    url(r'^$', CartInfoView.as_view(), name='show'), # 显示购物车页面
]