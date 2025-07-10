from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Label, Tree
from textual.containers import VerticalScroll

from components.AddScreen import AddScreen
from components.messages import AddData

class WizardView(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Label("Use Ctrl+A to add a new element", id="instructions")
        yield Tree(label="Season Fields", id="tree")

    def on_mount(self) -> None:
        self.data = []
        self.query_one("#tree").show_root = True

        self.query_one("#tree").add_json(self.data)

class SeasonFieldsGenerator(App):
    """A Textual app to generate season fields for Open Scouting."""

    CSS_PATH = "style.tcss"

    SCREENS={
        "add_screen": AddScreen,
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

    def on_add_data(self, message: AddData) -> None:
        wizard_view = self.query_one(WizardView)
        wizard_view.data.append(message.data)

        wizard_view.query_one("#tree").clear()
        wizard_view.query_one("#tree").add_json(wizard_view.data)

if __name__ == "__main__":
    app = SeasonFieldsGenerator()
    app.run()