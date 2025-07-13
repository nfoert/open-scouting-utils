import ast

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Label, Tree, Select, Button
from textual.containers import VerticalScroll, HorizontalGroup

from components.AddScreen import AddScreen
from components.FilePicker import FilePicker
from components.messages import AddData, LoadFile

class WizardView(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Label("Use Ctrl+A to add a new element", id="instructions")
        yield Select(options=[], prompt="File sections", id="select_file_section")
        yield Tree(label="Season Fields", id="tree")
        yield HorizontalGroup(
            Button("Edit", variant="primary", disabled=True, id="edit"),
            Button("Move up", disabled=True, id="move_up"),
            Button("Move down", disabled=True, id="move_down"),
            classes="button-row",
        )

    def load_file(self, path):
        self.path = path

        with open(path, "r") as file:
            source = file.read()

        list_names = []

        try:
            tree = ast.parse(source, filename=path)
            for node in ast.walk(tree):
                # Only grab top-level assignments
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(node.value, ast.List):
                            # Convert the list node back to source
                            if isinstance(target, ast.Name):
                                list_names.append(target.id)
        except Exception as e:
            print(f"Error parsing {path}: {e}")

        self.query_one("#select_file_section").set_options(
            [(name, name) for name in list_names]
        )
        self.query_one("#select_file_section").value = list_names[0]

    def on_mount(self) -> None:
        self.data = []
        self.path = ""
        self.query_one("#tree").show_root = True
        self.query_one("#tree").add_json(self.data)
        self.query_one("#tree").get_node_at_line(0).expand_all()

    def on_select_changed(self, event: Select.Changed) -> None:
        selected_value = event.select.value
        if selected_value:
            with open(self.path, "r") as file:
                source = file.read()
            
            try:
                tree = ast.parse(source, filename=self.path)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id == selected_value:
                                if isinstance(node.value, ast.List):
                                    list_data = ast.literal_eval(node.value)
                                    self.query_one("#tree").clear()
                                    self.query_one("#tree").add_json(list_data)
                                    self.query_one("#tree").get_node_at_line(0).expand_all()
                                    break
            except Exception as e:
                print(f"Error parsing {self.path}: {e}")

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
        wizard_view = self.query_one(WizardView)
        wizard_view.data.append(message.data)

        wizard_view.query_one("#tree").clear()
        wizard_view.query_one("#tree").add_json(wizard_view.data)
        wizard_view.query_one("#tree").get_node_at_line(0).expand_all()

    def on_load_file(self, message: LoadFile) -> None:
        self.query_one(WizardView).load_file(message.path)

if __name__ == "__main__":
    app = SeasonFieldsGenerator()
    app.run()