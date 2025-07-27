import ast

from textual.app import ComposeResult
from textual.widgets import Label, Select, Button, Collapsible
from textual.containers import VerticalScroll, HorizontalGroup, VerticalGroup

from components.messages import LoadData

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

    async def add_data(self, data):
        target_item = self.adding.get("item")

        if not target_item or "fields" not in target_item:
            print("Invalid target for adding data:", self.adding)
            return

        # Append new field data to the target item's "fields"
        target_item["fields"].append(data)

        # Re-render the full tree using the source of truth
        await self.build_tree(self.tree_data)

    async def build_tree(self, data):
        tree_container = self.query_one("#tree")
        await tree_container.remove_children()

        async def build_collapsible(item, parent_list=None):
            title = item.get("section") or item.get("name") or item.get("simple_name", "Unnamed")
            children = []

            field_buttons = HorizontalGroup(
                Button("Edit", variant="primary", id="edit"),
                Button("Delete", variant="error", id="delete"),
                Button("Move up", id="move_up"),
                Button("Move down", id="move_down"),
                classes="button-row-field",
            )

            section_buttons = HorizontalGroup(
                Button("Add", variant="success", id="add"),
                Button("Edit", variant="primary", id="edit"),
                Button("Delete", variant="error", id="delete"),
                Button("Move up", id="move_up"),
                Button("Move down", id="move_down"),
                classes="button-row-field",
            )

            if "fields" in item:
                for child in item["fields"]:
                    children.append(await build_collapsible(child, parent_list=item["fields"]))

                children.append(section_buttons)
                collapsible = Collapsible(title=title, *children, classes="section")
            elif "name" in item and "type" in item:
                for key, value in item.items():
                    if key != "name":
                        children.append(Label(f"{key}: {value}", classes="field-attr"))
                children.append(field_buttons)
                collapsible = Collapsible(title=title, *children, classes="field")
            else:
                print(f"Unknown item structure: {item}")
                collapsible = Collapsible(title="Unknown Item", classes="field")

            # Attach data and parent reference
            collapsible.json_data = item
            collapsible.parent_list = parent_list
            return collapsible

        for item in data:
            collapsible = await build_collapsible(item, parent_list=data)
            await tree_container.mount(collapsible)

        # Store the tree data so you can redraw it later
        self.tree_data = data

    def get_closest_collapsible(self, widget):
        while widget is not None:
            if isinstance(widget, Collapsible):
                return widget
            widget = widget.parent
        return None

    def on_mount(self) -> None:
        self.data = []
        self.path = ""

        self.adding = {}
        self.editing = {}

    async def on_select_changed(self, event: Select.Changed) -> None:
        selected_value = event.select.value
        if selected_value:
            with open(self.path, "r") as file:
                source = file.read()
            
            # try:
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
            # except Exception as e:
            #     print(f"Error parsing {self.path}: {e}")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        collapsible = self.get_closest_collapsible(event.button)

        if not collapsible:
            print("No collapsible found for button press.")
            return

        item = collapsible.json_data
        parent_list = collapsible.parent_list

        if button_id == "add":
            self.adding["parent_list"] = parent_list
            self.adding["item"] = item
            self.app.push_screen("add_screen")

        elif button_id == "edit":
            self.editing["parent_list"] = parent_list
            self.editing["item"] = item

            self.app.push_screen("add_screen")
            self.app.post_message(LoadData(item))

        elif button_id == "delete":
            if parent_list and item in parent_list:
                parent_list.remove(item)
                await self.build_tree(self.tree_data)

        elif button_id == "move_up":
            if parent_list and item in parent_list:
                index = parent_list.index(item)
                if index > 0:
                    parent_list[index], parent_list[index - 1] = parent_list[index - 1], parent_list[index]
                    await self.build_tree(self.tree_data)

        elif button_id == "move_down":
            if parent_list and item in parent_list:
                index = parent_list.index(item)
                if index < len(parent_list) - 1:
                    parent_list[index], parent_list[index + 1] = parent_list[index + 1], parent_list[index]
                    await self.build_tree(self.tree_data)


