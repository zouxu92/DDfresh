from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse

from goods.models import GoodsSKU
from django_redis import get_redis_connection
from utils.mixin import LoginRequiredMixin

# Create your views here.
# 添加商品到购物车
# 1）请求方式，采用ajax post
# 如果涉及到数据的修改（新增、更新、删除）采用post
# 如果只涉及到数据的获取，采用get
# 2） 传递参数： 商品id(sku_id)) 商品数量(count)


# /cart/add
class CartAddView(View):
    '''购物车记录添加'''
    def post(self, request):
        '''购物车记录添加'''
        user = request.user
        if not user.is_authenticated():
            # 用户未登录
            return JsonResponse({'res':0, 'errmsg':'请先登录'})
        # 1.接受数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # 2.数据效验
        if not all([sku_id, count]):
            return JsonResponse({'res':1, 'errmsg':'数据不完整'})

        # 效验添加的数量
        try:
            count = int(count)
        except Exception as e:
            # 数目出错
            return JsonResponse({'res':2, 'errmsg':'商品数目出错'})

        # 效验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            # 商品不存在
            return JsonResponse({'res':3, 'errmsg':'商品不存在'})

        # 3.业务处理：添加购物车记录
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id
        # 先尝试获取sku_id 的值 -> hget cart_key 属性
        # 如果sku_id 在hash中不存在，hget返回None
        cart_count = conn.hget(cart_key, sku_id)
        if cart_count:
            # 累加购物车中商品的数目(存在的情况时，需要)
            count += int(cart_count)

        # 效验商品的库存
        if count > sku.stock:
            return JsonResponse({'res':4, 'errmsg':'商品库存不足'})

        # 设置hash中sku_id 对应的值
        # hset->如果存在更新数据，不存在则添加数据
        conn.hset(cart_key, sku_id, count)

        # 计算用户购物车商品的条目数
        total_count = conn.hlen(cart_key)

        # 4.返回应答
        return JsonResponse({'res':5, 'total_count':total_count, 'errmsg':'添加成功'})

# /cart/
class CartInfoView(LoginRequiredMixin, View):
    '''显示购物车页面'''
    def get(self, request):
        '''显示购物车'''
        # 获取登录的用户
        user = request.user
        # 获取用户购物车中的商品信息
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id
        # {'商品id'：商品数量}
        cart_dict = conn.hgetall(cart_key)

        skus = []
        # 保存用户购物车中商品的中数目和中价格
        total_count = 0
        total_price = 0
        # 遍历获取商品的信息
        for sku_id, count in cart_dict.items():
            # 根据商品的id获取商品的信息
            sku = GoodsSKU.objects.get(id=sku_id)
            # 计算商品的小计
            amount = sku.price*int(count)
            # 动态个sku添加一个属性amoun，保存商品的小计
            sku.amount = amount
            # 动态个sku添加一个属性count，保存购物车对应的商品数量
            sku.count = count
            skus.append(sku)

            # 累加计算商品的总数目和总价格
            total_count += int(count)
            total_price += amount

        # 组织上下文
        context = {
            'total_count':total_count,
            'total_price': total_price,
            'skus':skus
        }

        # 使用模板
        return render(request, 'cart.html', context)