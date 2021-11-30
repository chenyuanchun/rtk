import csv
import logging
from abc import ABC, abstractmethod

from contextlib import ExitStack

from .log import with_logger

_logger = logging.getLogger(__name__)


def process_csv(input_file_path, *, output_file_path=None, record_parser=None, multiple_header=False):
    with open(input_file_path) as input_file:
        _reader = csv.reader(input_file)

        _writer = None
        with ExitStack() as stack:
            if output_file_path:
                _output_file = stack.enter_context(open(output_file_path, 'w'))
                _writer = csv.writer(_output_file, lineterminator='\n')

            _header = []
            for row in _reader:
                if record_parser:
                    if not multiple_header:
                        assert not (_header and row[0])
                    if row[0]:
                        record_parser.section_done()
                        record_parser.header = _header = row
                    else:
                        record_parser(row)

                if _writer:
                    _writer.writerow(row)


@with_logger
class RecordParserBase(ABC):
    """
    Base class of Record Parser
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.col_lookup = None

    @abstractmethod
    def process_record(self, record, col_lookup):
        """
        Process one record
        :param record: list of columns
        :param col_lookup: column name -> index
        :return:
        """

    def section_done(self):
        """
        indicates one section finished, and a new header found
        :return:
        """
        pass

    def __call__(self, record):
        self.process_record(record, self.col_lookup)

    def set_header(self, value):
        self.col_lookup = RecordParserBase.build_column_lookup(value)

    @staticmethod
    def build_column_lookup(header):
        return {
            name: index for index, name in enumerate(header)
        }

    header = property(None, set_header)
