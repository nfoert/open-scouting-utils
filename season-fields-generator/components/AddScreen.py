from textual.app import ComposeResult
from textual.widgets import Label, Select, Input, Rule, Checkbox, Button
from textual.containers import VerticalGroup, HorizontalGroup
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
                Label("The game piece that this stat corresponds to", classes="hint", id="field-gamepiece-hint"),

                VerticalGroup(
                    Rule(),
                    Input(placeholder="Default", type="integer", id="field-integer-default"),
                    Label("The default value of the field", classes="hint"),
                    Input(placeholder="Minimum", type="integer", id="field-integer-minimum"),
                    Label("The minimum value of the field", classes="hint"),
                    Input(placeholder="Maximum", type="integer", id="field-integer-maximum"),
                    Label("The maximum value of the field", classes="hint"),
                    id="field-options-integer"
                ),

                VerticalGroup(
                    Rule(),
                    Input(placeholder="Choices (comma separated)", id="field-choices"),
                    Label("Enter the choices for the field, separated by commas", classes="hint"),
                    id="field-options-choice"
                ),

                HorizontalGroup(
                    Button.success("Add", disabled=True, id="add-field-confirm"),
                    Button.error("Cancel", id="add-cancel"),
                    classes="button-row"
                ),
                id="add-field",
            ),
            id="dialog"
        )

    def validate_add_field(self):
        if self.query_one("#add-field-type").value == "large_integer" or self.query_one("#add-field-type").value == "boolean":
            if self.query_one("#field-name").value != "" and self.query_one("#field-simplename").value != "":
                self.query_one("#add-field-confirm").disabled = False
            else:
                self.query_one("#add-field-confirm").disabled = True
        elif self.query_one("#add-field-type").value == "integer":
            if self.query_one("#field-name").value != "" and self.query_one("#field-simplename").value != "" and self.query_one("#field-integer-default").value != "" and self.query_one("#field-integer-minimum").value != "" and self.query_one("#field-integer-maximum").value != "":
                self.query_one("#add-field-confirm").disabled = False
            else:
                self.query_one("#add-field-confirm").disabled = True
        elif self.query_one("#add-field-type").value == "choice" or self.query_one("#add-field-type").value == "multiple_choice":
            if self.query_one("#field-name").value != "" and self.query_one("#field-simplename").value != "" and self.query_one("#field-choices").value != "":
                self.query_one("#add-field-confirm").disabled = False
            else:
                self.query_one("#add-field-confirm").disabled = True

    def clear_fields(self):
        self.query_one("#section-name").value = ""
        self.query_one("#section-simplename").value = ""

        self.query_one("#add-field-type").value = "large_integer"

        self.query_one("#field-name").value = ""
        self.query_one("#field-simplename").value = ""
        self.query_one("#field-required").checked = False
        self.query_one("#field-stattype").value = "score"
        self.query_one("#field-gamepiece").value = ""
        self.query_one("#field-integer-default").value = ""
        self.query_one("#field-integer-minimum").value = ""
        self.query_one("#field-integer-maximum").value = ""
        self.query_one("#field-choices").value = ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # TODO: Return added data in dismiss
        # https://textual.textualize.io/guide/screens/#returning-data-from-screens
        if event.button.id == "add-cancel":
            self.clear_fields()
            self.dismiss(False)

        elif event.button.id == "add-field-confirm":
            self.clear_fields()
            self.dismiss(True)

        elif event.button.id == "add-section-confirm":
            self.clear_fields()
            self.dismiss(True)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.value == "section":
            self.query_one("#add-section").display = True
            self.query_one("#add-field").display = False
        else:
            self.query_one("#add-section").display = False
            self.query_one("#add-field").display = True

        if event.select.id == "field-stattype":
            if event.select.value == "score" or event.select.value == "miss" or event.select.value == "auton_score" or event.select.value == "auton_miss":
                self.query_one("#field-gamepiece").display = True
                self.query_one("#field-gamepiece-hint").display = True
            else:
                self.query_one("#field-gamepiece").display = False
                self.query_one("#field-gamepiece-hint").display = False

        if event.select.id == "add-field-type":
            self.validate_add_field()

            if event.select.value == "integer":
                self.query_one("#field-options-integer").display = True
            else:
                self.query_one("#field-options-integer").display = False

            if event.select.value == "choice" or event.select.value == "multiple_choice":
                self.query_one("#field-options-choice").display = True
            else:
                self.query_one("#field-options-choice").display = False

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "section-name" or event.input.id == "section-simplename":
            if event.input.value != "" and event.input.value != "":
                self.query_one("#add-section-confirm").disabled = False
            else:
                self.query_one("#add-section-confirm").disabled = True

        if (event.input.id == "field-name" or event.input.id == "field-simplename" 
            or event.input.id == "field-required" or event.input.id == "field-stattype" 
            or event.input.id == "field-gamepiece" or event.input.id == "field-integer-default" 
            or event.input.id == "field-integer-minimum" or event.input.id == "field-integer-maximum" 
            or event.input.id == "field-choices"):

            self.validate_add_field()

        if event.input.id == "section-name":
            self.query_one("#section-simplename").value = "".join(c if c.isalnum() or c == " " else "" for c in event.input.value).replace(" ", "_").lower()

        if event.input.id == "field-name":
            self.query_one("#field-simplename").value = "".join(c if c.isalnum() or c == " " else "" for c in event.input.value).replace(" ", "_").lower()