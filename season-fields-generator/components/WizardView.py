import ast

from textual.app import ComposeResult
from textual.widgets import Label, Tree, Select, Button
from textual.containers import VerticalScroll, HorizontalGroup, VerticalGroup

class WizardView(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Label("Use Ctrl+A to add a new element", id="instructions")
        yield HorizontalGroup(
            Select(options=[], prompt="File sections", id="select_file_section"),
            Button("Create section", id="select_file_new_section"),
            classes="button-row"
        )
        yield VerticalGroup(
            id="tree"
        )
        yield HorizontalGroup(
            Button("Add", variant="success", id="add"),
            Button("Edit", variant="primary", disabled=True, id="edit"),
            Button("Delete", variant="error", disabled=True, id="delete"),
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
                            if isinstance(target, ast.Name) and target.id == "simple_name":
                                self.simple_name_nodes.append(target.id)
                            list_names.append(target.id)
        except Exception as e:
            print(f"Error parsing {path}: {e}")

        self.query_one("#select_file_section").set_options(
            [(name, name) for name in list_names]
        )
        self.query_one("#select_file_section").value = list_names[0]

    def add_data(self, data):
        self.data.append(data)

    async def build_tree(self, data):
        tree_container = self.query_one("#tree")
        await tree_container.remove_children()

        for item in data:
            # Section case: contains 'fields' key
            if "fields" in item:
                section_name = item.get("section") or item.get("simple_name", "Unnamed Section")

                # Create and mount a container for the section
                section_group = VerticalGroup(classes="section")
                await tree_container.mount(section_group)

                # Mount the section label
                await section_group.mount(Label(section_name, classes="section-label"))

                # Mount all fields within this section
                for field in item["fields"]:
                    field_name = field.get("name", field.get("simple_name", "Unnamed Field"))
                    await section_group.mount(Label(f"• {field_name}", classes="field-label"))

            # Top-level field case: direct field definition
            elif "name" in item and "type" in item:
                field_name = item.get("name", item.get("simple_name", "Unnamed Field"))
                await tree_container.mount(Label(f"• {field_name}", classes="field-label"))

            # (Optional) log or skip unknown structures
            else:
                print(f"Unknown item structure: {item}")


    def on_mount(self) -> None:
        self.data = []
        self.path = ""

    async def on_select_changed(self, event: Select.Changed) -> None:
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
                                    self.data = list_data

                                    await self.build_tree(self.data)
                                    break
            except Exception as e:
                print(f"Error parsing {self.path}: {e}")