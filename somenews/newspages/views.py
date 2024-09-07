from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.core.cache import cache
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import NewsForm, ResponseForm
from .models import News, Response
from .filters import NewsFilter
from .tasks import notify_about_new_post, notify_about_comment


class NewsCreate(LoginRequiredMixin, CreateView):
    form_class = NewsForm
    model = News
    template_name = 'newspages/create_news.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        news = form.save(commit=False)
        if self.request.user.is_authenticated:
            news.author = self.request.user
            news.save()

        get_post_inf = News.objects.get(title=news)
        post_json = get_post_inf.toJSON()
        notify_about_new_post.delay(post_json)
        return super().form_valid(form)


class NewsList(ListView):
    model = News
    ordering = '-publicationDate'
    template_name = 'newspages/news_list.html'
    context_object_name = 'newss'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = NewsFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['next_post'] = None
        context['filterset'] = self.filterset

        return context


class NewsDetail(DetailView):
    model = News
    template_name = 'newspages/news_detail.html'
    context_object_name = 'news'

    def get_object(self, *args, **kwargs):
        obj = cache.get(f'news-{self.kwargs["pk"]}', None)
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'news-{self.kwargs["pk"]}', obj)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['next_post'] = None
        context['news_comments'] = self.object.news_comments.all()
        context['form'] = ResponseForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ResponseForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.news = self.object
            comment.save()
        return redirect('news_detail', pk=self.object.pk)


class NewsUpdate(LoginRequiredMixin, UpdateView):
    form_class = NewsForm
    model = News
    template_name = 'newspages/news_update.html'
    success_url = reverse_lazy('news_list')


class NewsDelete(LoginRequiredMixin, DeleteView):
    model = News
    template_name = 'newspages/news_delete.html'
    success_url = reverse_lazy('news_list')


class NewsSearchList(ListView):
    model = News
    ordering = '-publicationDate'
    template_name = 'newspages/news_search.html'
    context_object_name = 'news_search'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = NewsFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['next_post'] = None
        context['filterset'] = self.filterset
        return context


class NewsComment(LoginRequiredMixin, CreateView):
    form_class = ResponseForm
    model = Response
    template_name = 'newspages/news_comment.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        comment = form.save(commit=False)
        news_id = self.kwargs.get('pk')
        news = get_object_or_404(News, id=news_id)
        if self.request.user.is_authenticated:
            comment.responseAuthor = self.request.user
            comment.responseNews = news

            comment.save()

        comm = Response.objects.get(id=comment.id)
        comm_json = comm.toJSON()
        notify_about_comment.delay(comm_json, news.author.email, news.title)
        return super().form_valid(form)
