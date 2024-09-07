from django_filters import FilterSet, CharFilter, DateTimeFilter
from newspages.models import Response


class PersonalFilter(FilterSet):
    news_category = CharFilter(
        field_name='responseNews__category', lookup_expr='exact', label='News Category'
    )
    news_title = CharFilter(
        field_name='responseNews__title', lookup_expr='icontains', label='News Title'
    )
    news_date_start = DateTimeFilter(
        field_name='responseNews__publicationDate', lookup_expr='gte', label='News Start Date'
    )
    news_date_end = DateTimeFilter(
        field_name='responseNews__publicationDate', lookup_expr='lte', label='News End Date'
    )
    comm_author = CharFilter(
        field_name='responseAuthor__username', lookup_expr='icontains', label='Comment Author'
    )
    comm_type = CharFilter(
        field_name='responseType', lookup_expr='exact', label='Comment Type'
    )
    comm_date_start = DateTimeFilter(
        field_name='responseDate', lookup_expr='gte', label='Comment Start Date'
    )
    comm_date_end = DateTimeFilter(
        field_name='responseDate', lookup_expr='lte', label='Comment End Date'
    )
    comm_message = CharFilter(
        field_name='responseMessage', lookup_expr='icontains', label='Comment Message'
    )

    class Meta:
        model = Response
        fields = ['news_category', 'news_title', 'news_date_start', 'news_date_end',
                  'comm_author', 'comm_type', 'comm_date_start', 'comm_date_end', 'comm_message']
