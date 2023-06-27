from ner_telhub.model.data_models import DataModelManager


class DataUtils():
    """
    Utility methods for data converstions
    """

    @staticmethod
    def text_to_data(input_text: str) -> int:
        """
        Converts a textual type of data to the internal data ID.
        """
        parts = input_text.split(' ', 1)
        if len(parts) > 1:
            return int(parts[0])
        return None

    @staticmethod
    def data_to_text(data_id: int) -> str:
        """
        Converts a data ID to the textual type of data recognizable by the user.
        """
        if data_id is not None:
            return f"{data_id} {DataModelManager.getDataType(data_id)}"
        else:
            return "None"
