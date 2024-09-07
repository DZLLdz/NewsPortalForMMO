from django.urls import path
from .views import NewsList, NewsCreate, NewsDetail, NewsUpdate, NewsDelete, NewsSearchList, NewsComment


urlpatterns = [
    path('', NewsList.as_view(), name='news_list'),
    path('create/', NewsCreate.as_view(), name='create_news'),
    path('<int:pk>', NewsDetail.as_view(), name='news_detail'),
    path('<int:pk>/update', NewsUpdate.as_view(), name='news_update'),
    path('<int:pk>/delete', NewsDelete.as_view(), name='news_delete'),
    path('<int:pk>/comment', NewsComment.as_view(), name='news_comment'),
    path('search/', NewsSearchList.as_view(), name='news_search'),
]
