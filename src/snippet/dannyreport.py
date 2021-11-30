#!/usr/bin/env python3

import csv
import os
import sys

if __name__ == '__main__':
    task_duration_file, prod_tfrm_file, report_file = sys.argv[1:4]
    # task_duration_file = 'TaskDuration.txt'
    # prod_tfrm_file = 'prod_tfrm.csv'
    # report_file = 'report.csv'
    work_dir = os.getcwd()

    with open(os.path.join(work_dir, task_duration_file)) as f_task, \
        open(os.path.join(work_dir, prod_tfrm_file)) as f_prod, \
        open(os.path.join(work_dir, report_file), 'w') as f_report:
        prod_reader = csv.reader(f_prod)
        task_reader = csv.reader(f_task, delimiter='|')
        report_writer = csv.writer(f_report)

        task_duration_lookup = {}
        header = next(task_reader)
        for record in task_reader:
            _key, *_value = record
            task_duration_lookup[_key.strip()] = _value

        report_writer.writerow(header + ['prod_start', 'prod_end', 'duration'])
        for record in prod_reader:
            _key = record[0].split('.', 1)[1]
            if 'simulation' in _key:
                _key = '.'.join((_key.split('.', 1)[0], 'sensitivity'))
            else:
                _key = _key.replace('extract', 'submitBatchToGrid_extract')
            _task_duration = task_duration_lookup[_key]
            report_writer.writerow(record + _task_duration)
