from log_aggregator.models import ApacheLog
from rest_framework import serializers


class ReadOnlyApacheLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApacheLog
        fields = (
            'id',
            'host',
            'time',
            'request_method',
            'request_path',
            'protocol',
            'status',
            'size',
            'agent',
            'referrer',
        )
        read_only_fields = fields


class ReadOnlyTopHostSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    host = serializers.CharField(read_only=True)


class ReadOnlyListApacheLogSerializer(serializers.Serializer):
    distinct_hosts_count = serializers.IntegerField(read_only=True)
    logs = ReadOnlyApacheLogSerializer(many=True, read_only=True)
    get_methods_count = serializers.IntegerField(read_only=True)
    post_methods_count = serializers.IntegerField(read_only=True)
    general_size = serializers.IntegerField(read_only=True)
    top_hosts = ReadOnlyTopHostSerializer(many=True, read_only=True)
