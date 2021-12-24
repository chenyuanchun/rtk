import os
import re

from abc import ABC, abstractmethod
from datetime import datetime
from collections import namedtuple, UserList


class Predicate(ABC):
    @abstractmethod
    def __call__(self, record):
        """apply predicate"""


class PropPredicate(Predicate):
    """Predicate that applies to record property"""
    def __init__(self, prop: str, value):
        self.prop = prop
        self.value = value

    def __call__(self, record):
        value = getattr(record.props, self.prop)
        return self.value == value


class RegexPredicate(Predicate):
    """Predicate that applies regex to the log text"""
    def __init__(self, pattern: str):
        self.pattern = re.compile(pattern)

    def __call__(self, record):
        return bool(self.pattern.search(record.original))


class TimeRangePredicate(Predicate):
    """Predicate that deals with time range on timestamp prop"""
    TIME_FMT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, time_range: str):
        start, end = time_range.split(',', 1)
        self.start = datetime.strptime(start, TimeRangePredicate.TIME_FMT) if start else None
        self.end = datetime.strptime(end, TimeRangePredicate.TIME_FMT) if end else None

    def __call__(self, record):
        start_ok = record.props.timestamp > self.start if self.start else True
        end_ok = record.props.timestamp < self.end if self.end else True
        return start_ok and end_ok


RecordProp = namedtuple('RecordProp', 'seq timestamp severity pid')


class LogRecord:
    """Single log record, can be multiple lines"""
    TIME_FMT = "%d %b %Y, %H:%M:%S.%f"

    def __init__(self, seq: int, timestamp, severity, pid: int, line):
        self.props = RecordProp(seq, timestamp, severity, pid)
        self.original = line

    def __str__(self):
        return f'{self.props.seq:5d} {self.props.timestamp.isoformat(timespec="milliseconds")} {self.original}'


class Filter:
    """Help turn where args into predicates"""
    def __init__(self, **kwargs):
        self.predicates = []
        for k,v in kwargs.items():
            if k == 'keyword':
                p = RegexPredicate(v)
            elif k == 'time_range':
                p = TimeRangePredicate(v)
            else:
                p = PropPredicate(k, v)
            self.predicates.append(p)

    def __call__(self, record):
        for p in self.predicates:
            if not p(record):
                return False
        else:
            return True


class RecordSet(UserList):
    """Set of log records, with particular columns"""
    LOG_PATTERN = re.compile(r'^(\d{2} \w{3} \d{4}, \d{2}:\d{2}:\d{2}\.\d{3}): (\w+) +: \[(\d+)\] : (.+)$')

    def __init__(self, instance, data=None):
        """
        init the RecordSet with calc instance name and optional data (log records)
        :param instance: calc name
        :param data: existent log records
        """
        super().__init__(data) if data else super().__init__()
        self.instance = instance

    @classmethod
    def from_file(cls, filepath: str):
        """
        Create instance from one log file
        :param filepath: file path to load
        :return: list of log records
        """
        instance = os.path.basename(filepath).split('_')[3]
        records = cls(instance)
        records.load_file(filepath)
        return records

    def load_file(self, filepath: str):
        """
        load log file into current record set
        :param filepath: file path to load
        :return: None
        """
        count = len(self)
        with open(filepath, errors='ignore') as file:
            record = None
            for line in file:
                line = line.strip()
                if not line:
                    continue
                m = RecordSet.LOG_PATTERN.match(line)
                if not m:  # continue line
                    if record:
                        record.original = '\n'.join((record.original, line))
                    continue

                timestamp = datetime.strptime(m.group(1), LogRecord.TIME_FMT)
                record = LogRecord(count, timestamp, m.group(2), int(m.group(3)), m.group(4))
                count += 1
                self.append(record)

    def where(self, **kwargs):
        """
        filter current record set by criteria
        :param kwargs: criteria, including properties of LogRecord, 'keyword' to do regex match against log content
        :return: subset of current record set
        """
        _filter = Filter(**kwargs)

        results = RecordSet(self.instance)
        for rec in self:
            if _filter(rec):
                results.append(rec)
        return results

    def count(self, **kwargs):
        """
        number of records that satisfies the criteria
        :param kwargs: criteria, including properties of LogRecord, 'keyword' to do regex match against log content
        :return: number of records
        """
        _filter = Filter(**kwargs)
        ret = 0
        for rec in self:
            if _filter(rec):
                ret += 1
        return ret

    def select(self, group_pattern, multi_line=False):
        """
        extract data from matching log
        :param multi_line: target is multiple lines
        :param group_pattern: extract data as multiple fields
        :return: list of tuple (data record)
        """
        p = re.compile(group_pattern, re.DOTALL) if multi_line else re.compile(group_pattern)
        ret = []
        for rec in self:
            m = p.search(rec.original)
            if m:
                ret.append(m.groups())
        return ret

    def select_first(self, group_pattern):
        """
        similar with select(), only returns the first record
        :param group_pattern: regex pattern
        :return: the first match
        """
        p = re.compile(group_pattern)
        for rec in self:
            m = p.search(rec.original)
            if m:
                return m.groups()
        else:
            return None

    def select_multi_lines(self, patterns):
        """
        extract data from consecutive multiple lines
        :param patterns: group patterns that match each line
        :return: list of tuple (extracted data record)
        """
        ret = []
        compiled_patterns = list(map(re.compile, patterns))

        section_started = False
        section_count = len(patterns)
        section_index = 0
        new_rec = []
        for rec in self:
            m = compiled_patterns[section_index].search(rec.original)
            if m:
                if section_index == 0:
                    new_rec = list(m.groups())
                else:
                    new_rec.extend(m.groups())
                section_index += 1
                section_index = 0 if section_index == section_count else section_index

                if section_index == 0:
                    ret.append(new_rec)
            else:
                section_index = 0
        return ret

    def __add__(self, other):
        """merge 2 record set in time order"""
        assert isinstance(other, RecordSet)
        ret = RecordSet(self.instance)

        index = 0
        for rec in self:
            while index < len(other) and other[index].props.timestamp < rec.props.timestamp:
                ret.append(other[index])
                index += 1
            ret.append(rec)

        while index < len(other):
            ret.append(other[index])
            index += 1

        return ret
