from django_filters import FilterSet, CharFilter, DateTimeFilter
from .models import News, Response


class NewsFilter(FilterSet):
    class Meta:
        model = News
        fields = {
            'title': ['icontains'],
            'content': ['icontains'],
            'category': ['icontains'],
       }


class ResponseFilter(FilterSet):
    class Meta:
        model = Response
        fields = {
            'responseType': ['icontains'],
            'responseMessage': ['icontains'],

        }
