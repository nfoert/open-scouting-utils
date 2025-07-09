from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, TextArea, Placeholder, Collapsible, Label, Tree, Button, OptionList
from textual.containers import VerticalScroll, VerticalGroup
from textual.screen import ModalScreen

class AddScreen(ModalScreen[bool]):  
    """Screen with a dialog to quit."""
    def compose(self) -> ComposeResult:
        yield VerticalGroup(
            Label("Add Element...", id="add-title"),
            id="dialog")

class FileView(Collapsible):
    def compose(self) -> ComposeResult:
        with Collapsible(title="View output"):
            yield TextArea.code_editor(language="python", read_only=True)

class WizardView(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Label("Use Ctrl+A to add a new element", id="instructions")
        yield Tree(label="Season Fields")

class SeasonFieldsGenerator(App):
    """A Textual app to generate season fields for Open Scouting."""

    CSS_PATH = "style.tcss"

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"), 
        ("l", "load_file", "Load file"), 
        ("n", "new_file", "Create file"),
        ("ctrl+a", "add", "Add element")
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield WizardView()
        yield FileView()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_add(self) -> None:
        """Action to display the quit dialog."""

        def add_quit(quit: bool | None) -> None:
            """Called when QuitScreen is dismissed."""
            if quit:
                self.exit()

        self.push_screen(AddScreen(), add_quit)


if __name__ == "__main__":
    app = SeasonFieldsGenerator()
    app.run()