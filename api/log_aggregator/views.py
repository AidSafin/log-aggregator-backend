from django.db.models import Count, Q, Sum

from core.viewsets import BaseGenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from log_aggregator.models import ApacheLog, RequestMethodsTypes
from log_aggregator.paginations import ApacheLogNumberPagination
from log_aggregator.serializers import ReadOnlyListApacheLogSerializer
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class ApacheLogViewSet(BaseGenericViewSet):
    permission_classes = (AllowAny,)
    queryset = ApacheLog.objects.all()
    filter_backends = (
        DjangoFilterBackend, SearchFilter,
    )
    search_fields = [
        '=host',
        '=request_method',
        '=status',
    ]
    pagination_class = ApacheLogNumberPagination
    actions_serializer_class = {
        'list': ReadOnlyListApacheLogSerializer,
    }
    top_hosts_count = 10

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        aggregate_data = queryset.aggregate(
            get_methods_count=Count('id', filter=Q(request_method=RequestMethodsTypes.GET)),
            post_methods_count=Count('id', filter=Q(request_method=RequestMethodsTypes.POST)),
            distinct_hosts_count=Count('host', distinct=True),
            general_size=Sum('size'),
        )
        page = self.paginate_queryset(queryset)
        data = {
            'logs': page or queryset,
            'top_hosts': queryset.values('host').annotate(
                total=Count('host'),
            ).order_by('-total')[:self.top_hosts_count],
            **aggregate_data,
        }
        serializer = self.get_serializer(data)
        return Response(serializer.data)
