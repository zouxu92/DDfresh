from django.contrib import admin
from goods.models import GoodsType,Goods,GoodsSKU,IndexGoodsBanner,IndexTypeGoodsBanner,IndexPromotionBanner,GoodsImage
# Register your models here.

admin.site.register(GoodsType)
admin.site.register(Goods)
admin.site.register(GoodsSKU)
admin.site.register(IndexPromotionBanner)
admin.site.register(IndexGoodsBanner)
admin.site.register(IndexTypeGoodsBanner)
admin.site.register(GoodsImage)