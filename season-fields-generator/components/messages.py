from textual.message import Message

class AddData(Message):
    def __init__(self, data):
        self.data = data
        super().__init__()

class LoadData(Message):
    def __init__(self, data):
        self.data = data
        super().__init__()
        
class LoadFile(Message):
    def __init__(self, path):
        self.path = path
        super().__init__()
