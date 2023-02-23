"""
This script generates a list of preprocessed data, taken from the test_data.csv file.
Use the generate_data function to use in other parts of the code.
Example usage:
    from tests.test_data import generate_data
    data = generate_data() # now have access to example data to test with
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Any


def generate_data() -> List[Tuple[str, str, str]]:
    """
    Returns a list of data, each formatted as a tuple of the form (timestamp, id, value).
    NOTE: You may have to update the file path for test_data.csv
    """
    data = pd.read_csv("test_data.csv")
    data_array = np.delete(data.values, 2, axis=1)
    return data_array.tolist()
