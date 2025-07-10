from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, TextArea, Collapsible, Label, Tree, Button, Select, Input, Checkbox, Rule
from textual.containers import VerticalScroll, VerticalGroup, HorizontalGroup
from textual.screen import ModalScreen

class AddScreen(ModalScreen[bool]):  
    """Screen with a dialog to quit."""
    def compose(self) -> ComposeResult:
        yield VerticalGroup(
            Label("Add Element...", id="add-title"),
            Select(
                options=[("Section", "section"), ("Field", "field")],
                value="field",
                id="add-type",
            ),
            VerticalGroup(
                Label("Add a section..."),
                Input(placeholder="Name", id="section-name"),
                Label("The name of the field", classes="hint"),
                Input(placeholder="Simple name", restrict=r"[A-Za-z_\-]*", id="section-simplename"),
                Label("The simple name of the field, used in the backend", classes="hint"),
                HorizontalGroup(
                    Button.success("Add", id="add-section-confirm"),
                    Button.error("Cancel", id="add-cancel"),
                    classes="button-row"
                ),
                id="add-section",
            ),
            VerticalGroup(
                Label("Add a field..."),
                Select(
                    options=[("Large Integer", "large_integer"), ("Integer", "integer"), ("Boolean", "boolean"), ("Multiple Choice", "multiple_choice"), ("Choice", "choice")],
                    value="large_integer",
                    id="add-field-type",
                ),
                Rule(),

                Input(placeholder="Name", id="field-name"),
                Label("The name of the field", classes="hint"),
                Input(placeholder="Simple name", restrict=r"[A-Za-z_\-]*", id="field-simplename"),
                Label("The simple name of the field, used in the backend", classes="hint"),
                Checkbox("Required", id="field-required"),
                Label("Weather or not the field is required", classes="hint"),
                Select(
                    options=[("Score", "score"), ("Miss", "miss"), ("Auton score", "auton_score"), ("Auton miss", "auton_miss"), ("Capability", "capability"), ("Other", "other"), ("Ignore", "ignore")],
                    value="score",
                    id="field-stattype",
                ),
                Label("The type of the field when tracking stats", classes="hint"),
                Input(placeholder="Game piece", restrict=r"[A-Za-z_\-]*", id="field-gamepiece"),
                Label("The game piece that this stat corresponds to", classes="hint"),

                HorizontalGroup(
                    Button.success("Add", id="add-field-confirm"),
                    Button.error("Cancel", id="add-cancel"),
                    classes="button-row"
                ),
                id="add-field",
            ),
            id="dialog"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add-cancel":
            self.dismiss(False)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.value == "section":
            self.query_one("#add-section").display = True
            self.query_one("#add-field").display = False
        else:
            self.query_one("#add-section").display = False
            self.query_one("#add-field").display = True

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.value != "" and event.input.value != "":
            self.query_one("#add-section-confirm").disabled = False
        else:
            self.query_one("#add-section-confirm").disabled = True

        if event.input.id == "section-name":
            self.query_one("#section-simplename").value = "".join(c if c.isalnum() or c == " " else "" for c in event.input.value).replace(" ", "_").lower()

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
        yield FileView()

    def action_add(self) -> None:
        """Show the add dialog screen."""
        self.push_screen("add_screen")

if __name__ == "__main__":
    app = SeasonFieldsGenerator()
    app.run()