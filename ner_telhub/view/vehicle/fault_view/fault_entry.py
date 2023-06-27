from ner_telhub.model.data_models import DataModelManager

class FaultEntry():
    def __init__(self, data_id: int, name: str, model: DataModelManager):
        self.data_id = data_id
        self.name = name
        self.model = model
        self.value = None
        self.time = None
        self.last_time_high = None

    def update(self):
        try:
            self.value = self.model.getDataModel(
                self.data_id).getLastestValue()
            self.time = self.model.getDataModel(self.data_id).getLastestTime()
            if self.value == 1:
                self.last_time_high = self.time
        except BaseException:
            self.value = None
            self.time = None
            self.last_time_high = None
