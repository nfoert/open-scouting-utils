from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from components.AddScreen import AddScreen
from components.FilePicker import FilePicker
from components.WizardView import WizardView
from components.SectionScreen import SectionScreen
from components.messages import AddData, LoadFile, LoadData, EditData, NewFile, SetFilePath, OpenFileSectionScreen, AddFileSection

class SeasonFieldsGenerator(App):
    """A Textual app to generate season fields for Open Scouting."""

    CSS_PATH = "style.tcss"

    SCREENS={
        "add_screen": AddScreen,
        "file_picker": FilePicker,
        "add_file_section": SectionScreen
    }

    BINDINGS = [
        ("ctrl+l", "load_file", "Load file"), 
        ("ctrl+n", "new_file", "Create file"),
        ("ctrl+s", "save_file", "Save file")
    ]

    add_open = False

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield WizardView()

    def on_mount(self) -> None:
        # Have to do this, or else when editing the add_screen won't mount fast enough
        self.push_screen("add_screen")
        self.pop_screen()

    def action_save_file(self) -> None:
        """Asks the WizardView to save the currently loaded file. If there is no file loaded, prompt the user to choose where to save it instead."""
        self.query_one(WizardView).save_file()

    def action_load_file(self) -> None:
        self.push_screen("file_picker")

    def action_new_file(self) -> None:
        self.push_screen("file_picker")
        self.get_screen("file_picker").new_file = True

    async def on_add_data(self, message: AddData) -> None:
        await self.query_one(WizardView).add_data(message.data)

    def on_load_file(self, message: LoadFile) -> None:
        self.query_one(WizardView).load_file(message.path)

    def on_load_data(self, message: LoadData) -> None:
        self.get_screen("add_screen").load_data(message.data)

    async def on_edit_data(self, message: EditData) -> None:
        await self.query_one(WizardView).edit_data(message.data)

    def on_new_file(self, message: NewFile) -> None:
        self.push_screen("file_picker")
        self.get_screen("file_picker").new_file = True

    def on_set_file_path(self, message: SetFilePath) -> None:
        print("set file path", message.path)
        self.query_one(WizardView).path = message.path
        self.query_one(WizardView).save_file()

    def on_open_file_section_screen(self, message: OpenFileSectionScreen) -> None:
        self.push_screen("add_file_section")

    def on_add_file_section(self, message: AddFileSection) -> None:
        self.query_one(WizardView).add_file_section(message.name)

if __name__ == "__main__":
    app = SeasonFieldsGenerator()
    app.run()