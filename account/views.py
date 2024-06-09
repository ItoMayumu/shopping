from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.shortcuts import redirect, resolve_url
from django.urls import reverse_lazy
from .forms import LoginForm, SignupForm, UserUpdateForm, MyPasswordChangeForm
from .models import Item,Order,OrderItem
from django.views.generic import View
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView,DetailView,View
from django.utils import timezone


@login_required
def addItem(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order = Order.objects.filter(user=request.user, ordered=False)

    if order.exists():
        order = order[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
        else:
            order.items.add(order_item)
    else:
        order = Order.objects.create(user=request.user, ordered_date=timezone.now())
        order.items.add(order_item)

    return redirect('order')



'''トップページ'''
class TempView(View):
    def get(self,request,*arges,**kwargs):
        item_data= Item.objects.all()
        return render(request,'account/top.html',{
            'item_data':item_data
        })


class ItemDetailView(View):
    def get(self,request,*args,**kwargs):
        item_data = Item.objects.get(slug=self.kwargs['slug'])
        return render(request,'account/product.html',{
            'item_data':item_data
        })











# ここからはログイン等ユーザー情報のため変更不可
class Login(LoginView):
    form_class = LoginForm
    template_name = 'account/login.html'

class CustomLogoutView(LogoutView):
    template_name = 'account/logout_done.html'

'''自分しかアクセスできないようにするMixin(My Pageのため)'''
class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        # 今ログインしてるユーザーのpkと、そのマイページのpkが同じなら許可
        user = self.request.user
        return user.pk == self.kwargs['pk']

'''マイページ'''
class MyPage(OnlyYouMixin, generic.DetailView):
    model = User
    template_name = 'account/my_page.html'
    # モデル名小文字(user)でモデルインスタンスがテンプレートファイルに渡される

'''サインアップ'''
class Signup(generic.CreateView):
    template_name = 'account/user_form.html'
    form_class = SignupForm

    def form_valid(self, form):
        user = form.save() # formの情報を保存
        return redirect('account:signup_done')

    # データ送信
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["process_name"] = "Sign up"
        return context

'''サインアップ完了'''
class SignupDone(generic.TemplateView):
    template_name = 'account/signup_done.html'

'''ユーザー登録情報の更新'''
class UserUpdate(OnlyYouMixin, generic.UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'account/user_form.html'

    def get_success_url(self):
        return resolve_url('account:my_page', pk=self.kwargs['pk'])

    # contextデータ作成
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["process_name"] = "Update"
        return context
    
'''パスワード変更'''
class PasswordChange(PasswordChangeView):
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('account:password_change_done')
    template_name = 'account/user_form.html'

    # contextデータ作成
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["process_name"] = "Change Password"
        return context

'''パスワード変更完了'''
class PasswordChangeDone(PasswordChangeDoneView):
    template_name = 'account/password_change_done.html'
