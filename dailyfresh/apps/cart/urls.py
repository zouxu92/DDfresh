from django.conf.urls import url
from cart.views import CartAddView, CartInfoView , CartUpdateView

urlpatterns = [
    url(r'^add$', CartAddView.as_view(), name='add'), # 购物车添加
    url(r'^$', CartInfoView.as_view(), name='show'), # 显示购物车页面
    url(r'^update$', CartUpdateView.as_view(), name='update'), # 更新购物车记录
]