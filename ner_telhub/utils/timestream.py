import multiprocessing

import boto3
from botocore.config import Config
from typing import List, Tuple
from PyQt6.QtCore import pyqtBoundSignal, QDateTime

from ner_telhub.model.data_models import DataModel, DataModelManager
from ner_telhub.utils.thread_timestream import thread_timestream
from ner_telhub.utils.threads import Worker
from ner_telhub.utils.timestream_constants import *

# WARNING: Do not change to more than 100 (max allowed by timestream)
WRITE_BATCH_SIZE = 100

PROCESSORS = 8
THREAD_LINES = 300000


def process_rows(
        rows,
        manager,
        progress_signal,
        current_row,
        total_data_count):
    with multiprocessing.Pool(PROCESSORS) as p:
        out = p.map(thread_timestream, rows)

    current_row += len(out)
    progress_pct = int(100 * current_row / total_data_count)

    manager.addDataList(out)
    out.clear()

    progress_signal.emit(progress_pct)

    return current_row


class TimestreamIngestionService:

    @staticmethod
    def getIngestionWorker(models: List[DataModel], test_id: int) -> Worker:
        """
        Returns a worker to upload the given models' data to the database.

        The test ID argument is the identifier this data will have in the database,
        grouping all the data together as a sort of "session".
        """
        return Worker(
            TimestreamIngestionService._uploadData,
            models=models,
            test_id=test_id)

    @staticmethod
    def _uploadData(*args, **kwargs) -> None:
        """Uploads the data in the models to the database.

        CAUTION
        -------
        This is a worker function meant to be called from a thread (see Worker).
        Is expecting the following external arguments:
            - kwargs["models"] : List[DataModel]
            - kwargs["test_id"] : int
        """
        try:
            models: List[DataModel] = kwargs["models"]
            test_id: int = kwargs["test_id"]
            message_signal: pyqtBoundSignal = kwargs["message"]
        except BaseException:
            raise RuntimeError(
                "Internal processing error - thread configuration invalid")

        records = []
        total_counter = 0
        success_counter = 0
        try:
            client = boto3.client(
                'timestream-write',
                region_name=REGION_NAME,
                aws_access_key_id=ACCESS_KEY,
                aws_secret_access_key=SECRET_ACCESS_KEY,
                config=Config(
                    read_timeout=20,
                    max_pool_connections=5000,
                    retries={'max_attempts': 10})
            )
        except BaseException:
            raise RuntimeError(
                "Could not connect to the database. Credentials may be invalid.")

        for model in models:
            id = model.getDataId()
            for data in model.getData():
                if isinstance(data[1], int) or isinstance(data[1], float):
                    measure_type = 'DOUBLE'
                else:
                    measure_type = 'VARCHAR'

                record = {
                    'Dimensions': [{'Name': 'TestId', 'Value': str(test_id)}],
                    'MeasureName': str(id),
                    'MeasureValue': str(data[1]),
                    'MeasureValueType': measure_type,
                    'Time': str(int(data[0].timestamp() * 1000))
                }
                records.append(record)
                total_counter += 1
                if len(records) == WRITE_BATCH_SIZE:
                    success_counter += TimestreamIngestionService._submit_batch(
                        client, records)
                    records = []
            if len(records) != 0:
                success_counter += TimestreamIngestionService._submit_batch(
                    client, records)
                records = []

        message_signal.emit(
            f"Finshed database export. Ingested {success_counter} records. Failed {total_counter-success_counter} records.")

    @staticmethod
    def _submit_batch(client, records):
        """
        Writes the given records to the database, returning the actual write count
        """
        try:
            response = client.write_records(
                DatabaseName=DATABASE_NAME,
                TableName=TABLE_NAME,
                Records=records,
                CommonAttributes={})
            return response['RecordsIngested']['Total']
        except client.exceptions.RejectedRecordsException as err:
            return len(records) - len(err.response['RejectedRecords'])


class TimestreamQueryService:
    """
    Service for running queries on the database
    """

    def __init__(self):
        try:
            self._client = boto3.client(
                'timestream-query',
                region_name=REGION_NAME,
                aws_access_key_id=ACCESS_KEY,
                aws_secret_access_key=SECRET_ACCESS_KEY)
        except BaseException:
            raise RuntimeError(
                "Could not connect to the database. Credentials may be invalid.")
        self._paginator = self._client.get_paginator('query')

    def run_query(self, query_string: str, *args):
        """
        Example formats of results are as follows:
        - Get all test IDs = [{'TestId': 'test1'}, {'TestId': 'test2'}, {'TestId': 'test3'}]
        - Get sessions start time = [{'time': '2022-08-01 00:04:07.004000000'}]
        - Get data = [{'TestId': 'test1', 'measure_name': '1', 'time': '2022-08-01 00:04:07.005000000',
            'measure_value::double': '2931.0'}, {...}]
        """
        for arg in args:
            query_string = query_string.replace("?", arg, 1)
        try:
            page_iterator = self._paginator.paginate(QueryString=query_string)
            data = []
            for page in page_iterator:
                column_info = page['ColumnInfo']
                for row in page['Rows']:
                    data.append(self._parse_row(column_info, row))
            return data
        except Exception as err:
            raise RuntimeError("Exception while running query:", err)

    def thread_query(
            self,
            query_string: str,
            progress_signal: pyqtBoundSignal,
            manager: DataModelManager,
            total_data_count,
            *args):
        """
        Example formats of results are as follows:
        - Get all test IDs = [{'TestId': 'test1'}, {'TestId': 'test2'}, {'TestId': 'test3'}]
        - Get sessions start time = [{'time': '2022-08-01 00:04:07.004000000'}]
        - Get data = [{'TestId': 'test1', 'measure_name': '1', 'time': '2022-08-01 00:04:07.005000000',
            'measure_value::double': '2931.0'}, {...}]
        """

        current_row = 0

        for arg in args:
            query_string = query_string.replace("?", arg, 1)
        try:
            page_iterator = self._paginator.paginate(QueryString=query_string)
            data = []
            for page in page_iterator:
                for row in page['Rows']:
                    data.append(row)

                    if len(data) >= THREAD_LINES:
                        current_row = process_rows(
                            data, manager, progress_signal, current_row, total_data_count)
                        data.clear()

            if len(data) > 0:
                process_rows(
                    data,
                    manager,
                    progress_signal,
                    current_row,
                    total_data_count)
                data.clear()
        except Exception as err:
            raise RuntimeError("Exception while querying datapoint: ", err)

    def getTestIds(self) -> List[str]:
        data = self.run_query(SELECT_AVAILABLE_TEST_IDS)
        test_ids = [d['TestId'] for d in data]
        return test_ids

    def getStartTimeForSession(self, session_id: str) -> QDateTime:
        data = self.run_query(
            SELECT_MIN_TIME_FOR_SESSION,
            session_id)
        time = data[0]['time']
        time = time[:-6]  # Get rid of precision after milliseconds
        return QDateTime.fromString(time, DATE_TIME_FORMAT)

    def getEndTimeForSession(self, session_id: str) -> QDateTime:
        data = self.run_query(
            SELECT_MAX_TIME_FOR_SESSION,
            session_id)
        time = data[0]['time']
        time = time[:-6]  # Get rid of precision after milliseconds
        return QDateTime.fromString(time, DATE_TIME_FORMAT)

    def getDataCount(self, session_id: str, data_id: int = None,
                     time_range: Tuple[str, str] = None) -> int:
        if time_range is None:
            min_time = self.getStartTimeForSession(
                session_id).toString(DATE_TIME_FORMAT)
            max_time = self.getEndTimeForSession(
                session_id).toString(DATE_TIME_FORMAT)
        else:
            min_time = time_range[0]
            max_time = time_range[1]

        if data_id is None:
            result = self.run_query(
                SELECT_DATA_COUNT,
                session_id,
                min_time,
                max_time)
        else:
            result = self.run_query(
                SELECT_DATA_COUNT_WITH_DATA_ID,
                session_id,
                data_id,
                min_time,
                max_time)
        count = int(result[0]['_col0'])
        return count

    def getQueryWorker(self, manager: DataModelManager, **kwargs) -> Worker:
        """
        Returns a worker to query data from the database, storing results in the given
        data model.

        Pass in filter parameters in kwargs:
            - test_id:    REQUIRED - identifier for the testing session (type: str)
            - time_range: OPTIONAL - time range to query (type: Tuple[min_time, max_time])
                (returns entire session if blank)
            - data_id:    OPTIONAL - ID to query (type: int)
                (returns all IDs if blank)
        """
        return Worker(self._queryData, service=self, manager=manager, **kwargs)

    @staticmethod
    def _queryData(*args, **kwargs) -> None:
        """
        Queries data from timestream and stores it in the data model.

        CAUTION
        -------
        This is a worker function meant to be called from a thread (see Worker).
        Is expecting the following external arguments:
            - kwargs["service"] : TimestreamQueryService
            - kwargs["manager"] : DataModelManager
            - kwargs["test_id"] : str
        And optionally:
            - kwargs["time_range"] : Tuple(int, int)
            - kwargs["data_id"] : int
        """
        try:
            service: TimestreamQueryService = kwargs["service"]
            manager: DataModelManager = kwargs["manager"]
            test_id: str = kwargs["test_id"]
            if "time_range" in kwargs:
                time_range: Tuple[int, int] = kwargs["time_range"]
            else:
                time_range = None
            if "data_id" in kwargs:
                data_id: int = kwargs["data_id"]
            else:
                data_id = None
            progress_signal: pyqtBoundSignal = kwargs["progress"]
            message_signal: pyqtBoundSignal = kwargs["message"]
        except BaseException:
            raise RuntimeError(
                "Internal processing error - thread configuration invalid")

        try:
            total_data_count = service.getDataCount(
                test_id, data_id, time_range)
        except BaseException:
            raise RuntimeError("Invalid test ID")

        message_signal.emit(
            "Fetching data from database and entering it into the model...")

        if (time_range is None) and (data_id is None):
            service.thread_query(
                SELECT_ALL_FOR_SESSION, progress_signal, manager, test_id)
        elif time_range is None:
            service.thread_query(
                SELECT_ALL_WITH_DATA_ID_FOR_SESSION,
                progress_signal,
                manager,
                total_data_count,
                test_id,
                data_id)
        elif data_id is None:
            service.thread_query(
                SELECT_ALL_WITHIN_TIME_RANGE_FOR_SESSION,
                progress_signal,
                manager,
                total_data_count,
                test_id,
                time_range[0],
                time_range[1])
        else:
            service.thread_query(
                SELECT_ALL_WITH_ID_AND_WITHIN_TIME_RANGE_FOR_SESSION,
                progress_signal,
                manager,
                total_data_count,
                test_id,
                data_id,
                time_range[0],
                time_range[1])

    def _parse_row(self, column_info, row) -> List[Tuple[str, str]]:
        data = row['Data']
        row_output = {}
        for j in range(len(data)):
            if data[j].get('NullValue', False):
                continue
            datum_name = column_info[j]['Name']
            datum_value = data[j]['ScalarValue']
            row_output[datum_name] = datum_value
        return row_output
