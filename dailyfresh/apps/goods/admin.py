from django.contrib import admin
from goods.models import GoodsType,Goods,GoodsSKU,IndexGoodsBanner,IndexTypeGoodsBanner,IndexPromotionBanner,GoodsImage
# Register your models here.

'''抽出一个父类进行重写新增、修改、删除数据后，添加任务到celery里面生成新的模板'''
class BaseModelAdmin(admin.ModelAdmin):
	def save_model(self, request, obj, form, change):
		'''新增或更新表中的数据时调用'''
		super().save_model(request,obj,form,change)

		# 发出任务，让celery worker 重新生成静态页面
		from celery_tasks.tasks import generate_static_index_html
		generate_static_index_html.delay()

	def delete_model(self, request, obj):
		'''删除表中的数据是调用'''
		super().delete_model(request,obj)
		# 发出任务，让celery worker 重新生成静态页面
		from celery_tasks.tasks import generate_static_index_html
		generate_static_index_html.delay()

class IndexPromotionBannerAdmin(BaseModelAdmin):
	pass

class GoodsTypeAdmin(BaseModelAdmin):
	pass

class GoodsAdmin(BaseModelAdmin):
	pass

class GoodsSKUAdmin(BaseModelAdmin):
	pass

class IndexGoodsBannerAdmin(BaseModelAdmin):
	pass

class IndexTypeGoodsBannerAdmin(BaseModelAdmin):
	pass

class GoodsImageAdmin(BaseModelAdmin):
	pass

admin.site.register(GoodsType, GoodsTypeAdmin)
admin.site.register(Goods, GoodsAdmin)
admin.site.register(GoodsSKU, GoodsSKUAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)
admin.site.register(GoodsImage, GoodsImageAdmin)