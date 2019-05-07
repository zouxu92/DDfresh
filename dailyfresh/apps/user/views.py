from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse # 反向解析
from django.views.generic import View
from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings
from user.models import User


from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
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
		subject = '天天生鲜欢迎信息'
		message = ''
		sender = settings.EMAIL_FROM
		receiver = [email]
		html_message = '<h1>%s,欢迎您成为天天生鲜注册会员</h1>请点击链接激活您的账号<br /><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' %(username, token, token)

		send_mail(subject, message, sender, receiver, html_message=html_message)
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
		return render(request, 'login.html')