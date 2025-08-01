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

class EditData(Message):
    def __init__(self, data):
        self.data = data
        super().__init__()

class NewFile(Message):
    def __init__(self):
        super().__init__()

class SetFilePath(Message):
    def __init__(self, path):
        self.path = path
        super().__init__()

class OpenFileSectionScreen(Message):
    def __init__(self):
        super().__init__()

class AddFileSection(Message):
    def __init__(self, name):
        self.name = name
        super().__init__()