from textual.app import ComposeResult
from textual.widgets import Label, Select, Input, Rule, Checkbox, Button
from textual.containers import VerticalGroup, HorizontalGroup
from textual.screen import ModalScreen

from components.messages import AddFileSection

class SectionScreen(ModalScreen[bool]):  
    """Screen to add a new file section."""
    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        yield VerticalGroup(
            Input(placeholder="Section name", id="section-name"),
            HorizontalGroup(
                Button.success("Add", id="add-section-confirm"),
                Button.error("Cancel", id="add-cancel"),
                classes="button-row"
            ),
            classes="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add-section-confirm":
            name = self.query_one("#section-name").value
            self.app.post_message(AddFileSection(name))
            self.dismiss(True)
        elif event.button.id == "add-cancel":
            self.dismiss(False)