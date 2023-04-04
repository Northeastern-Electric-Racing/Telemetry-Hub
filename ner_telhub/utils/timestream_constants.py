import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_NAME = os.getenv("TIMESTREAM_DATABASE")
TABLE_NAME = os.getenv("TIMESTREAM_TABLE")
REGION_NAME = os.getenv("TIMESTREAM_REGION")
ACCESS_KEY = os.getenv("TIMESTREAM_ACCESS_KEY")
SECRET_ACCESS_KEY = os.getenv("TIMESTREAM_SECRET_ACCESS_KEY")
DATE_TIME_FORMAT = "yyyy-MM-dd HH:mm:ss.zzz"

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
