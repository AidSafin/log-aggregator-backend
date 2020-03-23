from rest_framework.pagination import PageNumberPagination


class ApacheLogNumberPagination(PageNumberPagination):
    page_size = 20
