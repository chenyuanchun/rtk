import csv
import logging.config
import os
import sys

from datetime import datetime

from rtk.common.log import with_logger, DEFAULT_LOG_CONFIG
from rtk.common.csvutil import RecordParserBase, process_csv

FI_RESET_DATES = 'FI Reset Dates'
ASSET_RESET_DATES = 'Asset Reset Dates'
FI_PERIOD_DATES = 'FI Period Dates'
FI_APPLIED_PERIOD_DATES = 'FI Applied Period Dates'
ASSET_RETURN_DATES = 'Asset Return Dates'
NEXT_BUSINESS_DATE = '2019/11/01'

DATE_DELIMITER = ', '
DATE_FORMAT = '%Y/%m/%d'


@with_logger
class EpsilonRecordProcessor(RecordParserBase):
    """
    modify deal file
    """

    def __init__(self, oet_path):
        super().__init__(oet_lookup=[])
        with open(oet_path) as config_file:
            dict_reader = csv.DictReader(config_file)
            for row in dict_reader:
                self.oet_lookup.append((row['swapid'], row['OET Date'], row['Next Reset Date']))

    def process_record(self, row, row_dict):
        row_type, row_id = row[row_dict['ID']].split()
        assert row_type == ':EPSILON.EpsilonTRS', 'non-TRS trade found: {}'.format(row_type)

        for oet in self.oet_lookup:
            swap_id, oet_date, next_reset_date = oet
            assert swap_id and oet_date
            if swap_id == row_id.split('-')[0]:
                self.logger.info('processing swap id: %s ...', row_id)
                end_date_index = row_dict['End Date']
                if oet_date == 'Daily':
                    row[end_date_index] = NEXT_BUSINESS_DATE  # next_business_day(current_business_date)
                elif oet_date == 'Monthly':
                    row[end_date_index] = next_reset_date
                else:
                    row[end_date_index] = oet_date

                # Remove any dates that are after the post-modified End Date
                end_date = row[end_date_index]
                self.logger.info('End Date: %s', end_date)
                end_date = datetime.strptime(end_date, DATE_FORMAT)
                for to_modify in (ASSET_RETURN_DATES, FI_APPLIED_PERIOD_DATES, FI_PERIOD_DATES):
                    to_modify_index = row_dict[to_modify]
                    modify_dates = row[to_modify_index].split(DATE_DELIMITER)
                    row[to_modify_index] = DATE_DELIMITER.join(
                        EpsilonRecordProcessor.truncate_dates_after(end_date, modify_dates))
                    self.logger.info('%s -> [%s]', to_modify, row[to_modify_index])

                # adjust reset dates
                asset_end_date = end_date
                asset_return_dates = row[row_dict[ASSET_RETURN_DATES]]
                if asset_return_dates:
                    max_asset_return_dates = asset_return_dates.split(DATE_DELIMITER)[-1]
                    asset_end_date = min(asset_end_date, datetime.strptime(max_asset_return_dates, DATE_FORMAT))
                else:
                    self.logger.warning('%s: %s is empty', row_id, ASSET_RETURN_DATES)
                _index = row_dict[ASSET_RESET_DATES]
                row[_index] = DATE_DELIMITER.join(
                    EpsilonRecordProcessor.truncate_dates_after(asset_end_date, row[_index].split(DATE_DELIMITER)))
                self.logger.info('%s -> [%s]', ASSET_RESET_DATES, row[_index])

                fi_end_date = end_date
                fi_applied_period_dates = row[row_dict[FI_APPLIED_PERIOD_DATES]]
                if fi_applied_period_dates:
                    max_fi_applied_period_dates = fi_applied_period_dates.split(DATE_DELIMITER)[-1]
                    fi_end_date = min(fi_end_date, datetime.strptime(max_fi_applied_period_dates, DATE_FORMAT))
                else:
                    self.logger.warning('%s: %s is empty', row_id, FI_APPLIED_PERIOD_DATES)
                fi_period_dates = row[row_dict[FI_PERIOD_DATES]]
                if fi_period_dates:
                    max_fi_period_dates = fi_period_dates.split(DATE_DELIMITER)[-1]
                    fi_end_date = min(fi_end_date, datetime.strptime(max_fi_period_dates, DATE_FORMAT))
                else:
                    self.logger.warning('%s: %s is empty', row_id, FI_PERIOD_DATES)

                _index = row_dict[FI_RESET_DATES]
                row[_index] = DATE_DELIMITER.join(
                    EpsilonRecordProcessor.truncate_dates_after(fi_end_date, row[_index].split(DATE_DELIMITER)))
                self.logger.info('%s -> [%s]', FI_RESET_DATES, row[_index])

                break

    @staticmethod
    def truncate_dates_after(end_date, dates):
        return list(filter(lambda x: datetime.strptime(x, DATE_FORMAT) <= end_date, dates))

if __name__ == '__main__':
    assert len(sys.argv) == 4

    work_dir = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]

    logger_cfg = dict(DEFAULT_LOG_CONFIG)
    logger_cfg['handlers']['file']['filename'] = os.path.join(work_dir, 'epsilon.log')
    logging.config.dictConfig(logger_cfg)
    processor = EpsilonRecordProcessor(os.path.join(work_dir, 'OET_Date.csv'))

    process_csv(os.path.join(work_dir, input_file),
                output_file_path=os.path.join(work_dir, output_file),
                record_parser=processor)
