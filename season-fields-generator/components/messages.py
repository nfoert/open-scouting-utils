from textual.message import Message

class AddData(Message):
    def __init__(self, data):
        self.data = data
        super().__init__()
