from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse # 反向解析
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View
from django.http import HttpResponse
from django.conf import settings

from user.models import User, Address
from goods.models import GoodsSKU
from celery_tasks.tasks import send_register_active_email
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from utils.mixin import LoginRequiredMixin
from django_redis import get_redis_connection
import re
# Create your views here.

def register(request):
	'''注册'''
	if request.method == 'GET':
		# 显示注册页面
		return render(request, 'register.html')
	else:
		'''进行注册处理'''
		# 接受数据
		username = request.POST.get('user_name')
		password = request.POST.get('pwd')
		email = request.POST.get('email')
		allow = request.POST.get('allow')

		# 进行数据校验
		if not all([username, password, email]):
			# 数据不完整
			return render(request, 'register.html', {'errmsg': '数据不完整'})
		# 效验邮箱
		if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
			return render(request, 'register.html', {'errmsg': '邮件格式不正确'})
		# 效验协议是否勾选
		if allow != 'on':
			return render(request, 'register.html', {'errmsg': '请同意协议'})
		# 校验用户名是否重复
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			# 用户名不存在
			user = None

		if user:
			return render(request, 'register.html', {'errmsg': '用户名存在,请重新输入'})
		# 进行业务处理:进行用户注册
		user = User.objects.create_user(username, email, password)
		# 用户是否激活,默认为0 未激活
		user.is_active = 0
		user.save()

		# 返回应答,跳转到首页 -->反向解析
		return redirect(reverse('goods:index'))

def register_handle(request):
	'''进行注册处理'''
	# 接受数据
	username = request.POST.get('user_name')
	password = request.POST.get('pwd')
	email = request.POST.get('email')
	allow = request.POST.get('allow')

	# 进行数据校验
	if not all([username, password, email]):
		# 数据不完整
		return render(request, 'register.html', {'errmsg':'数据不完整'})
	# 效验邮箱
	if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
		return render(request, 'register.html', {'errmsg':'邮件格式不正确'})
	# 效验协议是否勾选
	if allow != 'on':
		return render(request, 'register.html', {'errmsg':'请同意协议'})
	# 校验用户名是否重复
	try:
		user = User.objects.get(username=username)
	except User.DoesNotExist:
		# 用户名不存在
		user = None

	if user:
		return render(request, 'register.html', {'errmsg': '用户名存在,请重新输入'})
	# 进行业务处理:进行用户注册
	user = User.objects.create_user(username, email, password)
	# 用户是否激活,默认为0 未激活
	user.is_active = 0
	user.save()

	# 返回应答,跳转到首页 -->反向解析
	return redirect(reverse('goods:index'))


class RegisterView(View):
	'''注册'''
	def get(self, request):
		return render(request, 'register.html')

	def post(self, request):
		'''进行注册处理'''
		'''进行注册处理'''
		# 接受数据
		username = request.POST.get('user_name')
		password = request.POST.get('pwd')
		email = request.POST.get('email')
		allow = request.POST.get('allow')

		# 进行数据校验
		if not all([username, password, email]):
			# 数据不完整
			return render(request, 'register.html', {'errmsg': '数据不完整'})
		# 效验邮箱
		if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
			return render(request, 'register.html', {'errmsg': '邮件格式不正确'})
		# 效验协议是否勾选
		if allow != 'on':
			return render(request, 'register.html', {'errmsg': '请同意协议'})
		# 校验用户名是否重复
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			# 用户名不存在
			user = None

		if user:
			return render(request, 'register.html', {'errmsg': '用户名存在,请重新输入'})
		# 进行业务处理:进行用户注册
		user = User.objects.create_user(username, email, password)
		# 用户是否激活,默认为0 未激活
		user.is_active = 0
		user.save()

		# 发送激活邮件，包含激活链接:
		# 链接中包含用户身份信息， 并且要把身份信息加密

		# 加密用户的身份信息，生成token
		serializer = Serializer(settings.SECRET_KEY, 3600)
		info = {'confirm':user.id}
		token = serializer.dumps(info)  # 返回的是bytes信息
		token = token.decode()

		# 发送邮件
		send_register_active_email.delay(email, username, token)

		# 返回应答,跳转到首页 -->反向解析
		return redirect(reverse('goods:index'))

class ActiveView(View):
	'''用户激活'''
	def get(self, request, token):
		'''进行用户激活'''
		# 进行解密，获取要激活的用户信息
		serializer = Serializer(settings.SECRET_KEY, 3600)
		try:
			info = serializer.loads(token)
			# 获取待激活用户的id
			user_id = info['confirm']

			# 根据id获取用户信息
			user = User.objects.get(id=user_id)
			user.is_active = 1
			user.save()

			# 跳转到登录页面
			return redirect(reverse('user:login'))
		except SignatureExpired as e:
			# 激活链接已过期
			return HttpResponse('激活链接已过期')

# /user/login
class LoginView(View):
	'''登录'''
	def get(self, request):
		'''显示登录页面'''
		# 判断是否记住了用户名
		if 'username' in request.COOKIES:
			username = request.COOKIES.get('username')
			checked = 'checked'
		else:
			username = ''
			checked = ''

		# 使用模板
		return render(request, 'login.html', {'username':username, 'checked':checked})

	def post(self, request):
		'''登录校验'''
		# 接受数据
		username = request.POST.get('username')
		password = request.POST.get('pwd')

		# 效验数据
		if not all([username, password]):
			return render(request, 'login.html', {'errmsg': '请将数据填写完整'})

		# 业务处理：登录校验
		user = authenticate(username=username, password=password)
		if user is not None:
			# the password verified for the user
			if user.is_active:
				# 用户已激活
				# 记录用户的登录状态
				login(request, user)

				# 获取登录后所要跳转的地址
				# 默认跳转首页
				next_url = request.GET.get('next', reverse('goods:index'))
				# 跳转到next_url
				response = redirect(next_url)

				# 判断是否记录用户名
				remember = request.POST.get('remember')
				if remember == 'on':
					# 记住用户名
					response.set_cookie('username', username, max_age=7*24*3600)
				else:
					response.delete_cookie('username')

				# 返回response
				return response
			else:
				# 用户未激活
				return render(request, 'login.html', {'errmsg': '请先激活用户'})
		else:
			# 用户名或密码错误
			return render(request, 'login.html',  {'errmsg': '用户名或密码错误'})

# /user/logout
class LogoutView(View):
	'''退出登录'''
	def get(self, request):
		'''退出登录'''
		# 清除用户的session信息
		logout(request)

		# 跳转到首页
		return redirect(reverse('goods:index'))

# /user
class UserInfoView(LoginRequiredMixin, View):
	'''用户中心-信息页'''
	def get(self, request):
		'''显示'''
		# Django 会话给request对象添加一个属性request>user
		# 如果用户未登陆->user是AnonymousUser类的一个实例
		# 如果用户登录->user是User类的一个实例
		# request.user.is_authenticated()

		# 获取用户的个人信息
		user = request.user
		address = Address.objects.get_default_address(user)
		# 获取用户的历史浏览记录
		con = get_redis_connection('default')

		history_key = 'history_d' %user.id

		#

		# 出来你给模板文件传递的模板变量之外，Django框架会吧request.user也传给模板文件
		return render(request, 'user_center_info.html', {'page': 'user', 'address': address})

# user/order
class UserOrderView(LoginRequiredMixin, View):
	'''用户中心-订单页'''
	def get(self, request):
		'''显示'''
		return render(request, 'user_center_order.html', {'page':'order'})

# user/address
class AddressView(LoginRequiredMixin, View):
	'''用户中心-地址页'''
	def get(self, request):
		'''显示'''
		# 获取用户的user对象
		user = request.user
		# 获取用户的默认收货地址
		# try:
		#	address = Address.objects.get(user=user, is_default=True)
		#except Address.DoesNotExist:
		#	# 不存在默认收货地址
		#	address = None

		address = Address.objects.get_default_address(user)
		return render(request, 'user_center_site.html', {'page':'address', 'address':address})

	def post(self, request):
		'''添加地址'''
		# 接收数据
		receiver = request.POST.get('receiver')
		addr = request.POST.get('addr')
		zip_code = request.POST.get('zip_code')
		phone = request.POST.get('phone')

		# 校验数据
		if not all([receiver, addr, phone]):
			return render(request, 'user_center_site.html', {'errmsg':'数据不完整'})

		# 校验手机号码
		if not re.match(r'^1[0-9][0-9]{9}$', phone):
			return render(request, 'user_center_site.html', {'errmsg':'请输入正确的手机格式'})

		# 业务处理：地址增加
		# 如果用户已存在默认收货地址，添加的地址不做默认地址
		# 获取登录用户对应的User对象
		user = request.user
		#try:
		#	address = Address.objects.get(user=user, is_default=True)
		#except Address.DoesNotExist:
		#	# 不存在默认收货地址
		#	address = None

		address = Address.objects.get_default_address(user)

		if address:
			is_default = False
		else:
			is_default = True
		# 添加地址
		Address.objects.create(user=user,
							   receiver=receiver,
							   addr=addr,
							   zip_code=zip_code,
							   phone=phone,
							   is_default=is_default)
		# 返回应答
		return redirect(reverse('user:address'))  # 反向解析默认get请求