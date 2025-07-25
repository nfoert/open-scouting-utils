from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from components.AddScreen import AddScreen
from components.FilePicker import FilePicker
from components.WizardView import WizardView
from components.messages import AddData, LoadFile

class SeasonFieldsGenerator(App):
    """A Textual app to generate season fields for Open Scouting."""

    CSS_PATH = "style.tcss"

    SCREENS={
        "add_screen": AddScreen,
        "file_picker": FilePicker
    }

    BINDINGS = [
        ("l", "load_file", "Load file"), 
        ("n", "new_file", "Create file"),
        ("ctrl+a", "add", "Add element")
    ]

    add_open = False

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield WizardView()

    def action_add(self) -> None:
        """Show the add dialog screen."""
        self.push_screen("add_screen")

    def action_load_file(self) -> None:
        self.push_screen("file_picker")

    def on_add_data(self, message: AddData) -> None:
        self.query_one(WizardView).add_data(message.data)

    def on_load_file(self, message: LoadFile) -> None:
        self.query_one(WizardView).load_file(message.path)

if __name__ == "__main__":
    app = SeasonFieldsGenerator()
    app.run()