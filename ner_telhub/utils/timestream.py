import boto3
from botocore.config import Config
from dotenv import load_dotenv
import os
from typing import List, Tuple
from PyQt6.QtCore import pyqtBoundSignal, QDateTime

from ner_processing.data import Data
from ner_telhub.model.data_models import DataModel, DataModelManager
from ner_telhub.utils.threads import Worker

load_dotenv()

DATABASE_NAME = os.getenv("TIMESTREAM_DATABASE")
TABLE_NAME = os.getenv("TIMESTREAM_TABLE")
REGION_NAME = os.getenv("TIMESTREAM_REGION")
ACCESS_KEY = os.getenv("TIMESTREAM_ACCESS_KEY")
SECRET_ACCESS_KEY = os.getenv("TIMESTREAM_SECRET_ACCESS_KEY")
BATCH_SIZE = 100 # WARNING: Do not change to more than 100 (max allowed by timestream)

MAX_QUERY_SIZE = 1000000; # In data points (used to prevent overflowing user)
ONE_GB_IN_BYTES = 1073741824
QUERY_COST_PER_GB_IN_DOLLARS = 0.01 

DATE_TIME_FORMAT = "yyyy-MM-dd HH:mm:ss.zzz"

class TimestreamIngestionService:

    @staticmethod
    def getIngestionWorker(models: List[DataModel], test_id: int) -> Worker:
        """
        Returns a worker to upload the given models' data to the database.

        The test ID argument is the identifier this data will have in the database,
        grouping all the data together as a sort of "session".
        """
        return Worker(TimestreamIngestionService._uploadData, models=models, test_id=test_id)

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
        except:
            raise RuntimeError("Internal processing error - thread configuration invalid")
        
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
                    max_pool_connections = 5000, 
                    retries={'max_attempts': 10})
            )
        except:
            raise RuntimeError("Could not connect to the database. Credentials may be invalid.")

        for model in models:
            id = model.getDataId()
            for data in model.getData():
                if type(data[1]) is int or type(data[1]) is float:
                    measure_type = 'DOUBLE'
                else:
                    measure_type = 'VARCHAR'

                record = {
                    'Dimensions': [{'Name': 'TestId', 'Value': str(test_id)}],
                    'MeasureName': str(id),
                    'MeasureValue': str(data[1]),
                    'MeasureValueType': measure_type,
                    'Time': str(data[0].toMSecsSinceEpoch())
                }
                records.append(record)
                total_counter += 1
                if len(records) == BATCH_SIZE:
                    success_counter += TimestreamIngestionService._submit_batch(client, records)
                    records = []
            if len(records) != 0:
                success_counter += TimestreamIngestionService._submit_batch(client, records)
                records = []
        
        message_signal.emit(f"Finshed database export. Ingested {success_counter} records. Failed {total_counter-success_counter} records.")

    @staticmethod
    def _submit_batch(client, records):
        """
        Writes the given records to the database, returning the actual write count
        """
        try:
            response = client.write_records(DatabaseName=DATABASE_NAME, TableName=TABLE_NAME,
                                            Records=records, CommonAttributes={})
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
        except:
            raise RuntimeError("Could not connect to the database. Credentials may be invalid.")
        self._paginator = self._client.get_paginator('query')

    SELECT_AVAILABLE_TEST_IDS = F"""
        SELECT DISTINCT TestId FROM {DATABASE_NAME}.{TABLE_NAME}
    """
    
    SELECT_MIN_TIME_FOR_SESSION = F"""
        SELECT time FROM {DATABASE_NAME}.{TABLE_NAME}
        WHERE TestId = '?'
        ORDER BY time ASC
        LIMIT 1
    """ 

    SELECT_MAX_TIME_FOR_SESSION = F"""
        SELECT time FROM {DATABASE_NAME}.{TABLE_NAME}
        WHERE TestId = '?'
        ORDER BY time DESC
        LIMIT 1
    """ 

    SELECT_DATA_COUNT = F"""
        SELECT COUNT(*) FROM {DATABASE_NAME}.{TABLE_NAME}
        WHERE TestId = '?'
        AND time >= '?'
        AND time <= '?'
    """ 

    SELECT_DATA_COUNT_WITH_DATA_ID = F"""
        SELECT COUNT(*) FROM {DATABASE_NAME}.{TABLE_NAME}
        WHERE TestId = '?'
        AND measure_name = '?'
        AND time >= '?'
        AND time <= '?'
    """ 

    SELECT_ALL_FOR_SESSION = f"""
        SELECT * FROM {DATABASE_NAME}.{TABLE_NAME}
        WHERE TestId = '?'
    """
    
    SELECT_ALL_WITH_DATA_ID_FOR_SESSION = f"""
        SELECT * FROM {DATABASE_NAME}.{TABLE_NAME}
        WHERE TestId = '?'
        AND measure_name = '?'
    """

    SELECT_ALL_WITHIN_TIME_RANGE_FOR_SESSION = F"""
        SELECT * FROM {DATABASE_NAME}.{TABLE_NAME}
        WHERE TestId = '?'
        AND time >= '?'
        AND time <= '?'
    """

    SELECT_ALL_WITH_ID_AND_WITHIN_TIME_RANGE_FOR_SESSION = f"""
        SELECT * FROM {DATABASE_NAME}.{TABLE_NAME}
        WHERE TestId = '?'
        AND measure_name = '?'
        AND time >= '?'
        AND time <= '?'
    """

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

    def getTestIds(self) -> List[str]:
        data = self.run_query(TimestreamQueryService.SELECT_AVAILABLE_TEST_IDS)
        test_ids = [d['TestId'] for d in data]
        return test_ids

    def getStartTimeForSession(self, session_id: str) -> QDateTime:
        data = self.run_query(TimestreamQueryService.SELECT_MIN_TIME_FOR_SESSION, session_id)
        time = data[0]['time']
        time = time[:-6] # Get rid of precision after milliseconds
        return QDateTime.fromString(time, DATE_TIME_FORMAT)

    def getEndTimeForSession(self, session_id: str) -> QDateTime:
        data = self.run_query(TimestreamQueryService.SELECT_MAX_TIME_FOR_SESSION, session_id)
        time = data[0]['time']
        time = time[:-6] # Get rid of precision after milliseconds
        return QDateTime.fromString(time, DATE_TIME_FORMAT)

    def getDataCount(self, session_id: str, data_id: int = None, time_range: Tuple[str, str] = None) -> int:
        if time_range is None:
            min_time = self.getStartTimeForSession(session_id).toString(DATE_TIME_FORMAT)
            max_time = self.getEndTimeForSession(session_id).toString(DATE_TIME_FORMAT)
        else:
            min_time = time_range[0]
            max_time = time_range[1]

        if data_id is None:
            result = self.run_query(TimestreamQueryService.SELECT_DATA_COUNT, session_id, min_time, max_time)
        else:
            result = self.run_query(TimestreamQueryService.SELECT_DATA_COUNT_WITH_DATA_ID, 
                                    session_id, data_id, min_time, max_time)
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
        except:
            raise RuntimeError("Internal processing error - thread configuration invalid")

        try:
            total_data_count = service.getDataCount(test_id, data_id, time_range)
        except:
            raise RuntimeError("Invalid test ID")
        running_data_count = 0
        current_progress_pct = 0

        message_signal.emit("Fetching data from database...")

        if (time_range is None) and (data_id is None):
            data = service.run_query(TimestreamQueryService.SELECT_ALL_FOR_SESSION, test_id)
        elif time_range is None:
            data = service.run_query(TimestreamQueryService.SELECT_ALL_WITH_DATA_ID_FOR_SESSION, test_id, data_id)
        elif data_id is None:
            data = service.run_query(TimestreamQueryService.SELECT_ALL_WITHIN_TIME_RANGE_FOR_SESSION, 
                test_id, time_range[0], time_range[1])
        else:
            data = service.run_query(TimestreamQueryService.SELECT_ALL_WITH_ID_AND_WITHIN_TIME_RANGE_FOR_SESSION, 
                test_id, data_id, time_range[0], time_range[1])

        message_signal.emit("Entering data into the model...")

        data_list = []
        for d in data:
            try:
                test_id = d['TestId']
                data_id = int(d['measure_name'])
                time = QDateTime.fromString(d['time'][:-6], DATE_TIME_FORMAT)
                if 'measure_value::double' in d:
                    value = float(d['measure_value::double'])
                else:
                    value = d['measure_value::varchar']
                data_list.append(Data(time, data_id, value))
                running_data_count += 1
            except:
                raise RuntimeError("Error while querying data point: ", d)
            progress_pct = int(100 * running_data_count / total_data_count)
            if progress_pct != current_progress_pct:
                current_progress_pct = progress_pct
                progress_signal.emit(progress_pct)
            if len(data_list) >= 10000:
                manager.addDataList(data_list)
                data_list.clear()
        if len(data_list) > 0:
            manager.addDataList(data_list)

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
