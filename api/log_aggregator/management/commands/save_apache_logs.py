from django.core.management import BaseCommand
from django.db import transaction

from log_aggregator.downloaders import ApacheLogDownloader
from log_aggregator.models import ApacheLog
from log_aggregator.parsers import ApacheLogParser
from tqdm import tqdm


class Command(BaseCommand):
    help = 'Save Apache logs from url'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str)

    def handle(self, *args, **options):
        with SaveApacheLogCommandExecutor(options['url']) as executor:
            executor.execute()


class SaveApacheLogCommandExecutor:
    def __init__(self, url: str):
        self.data = ApacheLogDownloader.download(url)
        self.content_length = next(self.data)
        self.parser = ApacheLogParser
        self.log_model = ApacheLog

    def __enter__(self):
        self.progress_bar = tqdm(desc='Processing', total=self.content_length)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.progress_bar.close()
        if exc_val:
            raise

    @transaction.atomic
    def execute(self):
        for chunk_data, chunk_len in self.data:
            parsed_data = self.parser.parse(chunk_data)
            if not parsed_data:
                continue
            self.log_model.objects.create(**parsed_data)
            self.progress_bar.update(chunk_len)
