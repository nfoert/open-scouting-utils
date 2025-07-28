import ast
from pathlib import Path

from textual.app import ComposeResult
from textual.widgets import Label, Select, Button, Collapsible
from textual.containers import VerticalScroll, HorizontalGroup, VerticalGroup

from components.messages import LoadData, NewFile, OpenFileSectionScreen

class WizardView(VerticalScroll):
    def compose(self) -> ComposeResult:
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

        self.file_sections = list_names

        self.query_one("#select_file_section").set_options(
            [(name, name) for name in list_names]
        )

        try:
            self.query_one("#select_file_section").value = list_names[0]
            self.current_section = list_names[0]
        except IndexError:
            print(f"No sections found in {path}")
            self.app.notify("No sections found in file.", severity="warning")

        self.app.notify(f"Loaded {path}")

    async def add_data(self, data):
        target_item = self.adding.get("item")

        if not target_item or "fields" not in target_item:
            print("Invalid target for adding data:", self.adding, "(will be added to the root)")

            self.data.append(data)
            await self.build_tree(self.tree_data)
            return

        # Append new field data to the target item's "fields"
        target_item["fields"].append(data)

        # Re-render the full tree using the source of truth
        await self.build_tree(self.tree_data)

    async def build_tree(self, data):
        top_level_buttons = HorizontalGroup(
            Button("Add", variant="success", id="add-top-level"),
            classes="button-row-field"
        )

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

        await tree_container.mount(top_level_buttons)

        # Store the tree data so you can redraw it later
        self.tree_data = data

    def get_closest_collapsible(self, widget):
        while widget is not None:
            if isinstance(widget, Collapsible):
                return widget
            widget = widget.parent
        return None
    
    async def edit_data(self, data):
        parent_list = self.editing.get("parent_list")
        original_item = self.editing.get("item")

        if not parent_list or original_item not in parent_list:
            print("Cannot find item to edit in parent list")
            return

        index = parent_list.index(original_item)
        parent_list[index] = data

        await self.build_tree(self.tree_data)

    def on_mount(self) -> None:
        self.data = []
        self.path = ""
        self.file_sections = []
        self.current_section = None

        self.adding = {}
        self.editing = {}

        self.saved = True

    async def on_select_changed(self, event: Select.Changed) -> None:
        selected_value = event.select.value

        if not self.path or not self.saved:
            self.query_one("#select_file_section").value = self.current_section
            print("No file selected")
            self.app.notify("Sections cannot be changed until a file is saved or loaded.", severity="warning")
            return

        self.current_section = selected_value
        self.data = []  # Reset regardless

        try:
            with open(self.path, "r") as file:
                source = file.read()

            tree = ast.parse(source, filename=self.path)
        except Exception as e:
            print(f"Error reading or parsing {self.path}: {e}")
            self.app.notify(f"Failed to parse file: {e}", severity="error")
            await self.build_tree([])
            return

        # Look for the section assignment
        found_section = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == selected_value:
                        if isinstance(node.value, ast.List):
                            try:
                                self.data = ast.literal_eval(node.value)
                                found_section = True
                            except Exception as eval_err:
                                print(f"Failed to evaluate AST list: {eval_err}")
                                self.data = []
                            break
            if found_section:
                break

        # If section not found, self.data will remain []
        await self.build_tree(self.data)


    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "select_file_new_section":
            self.app.post_message(OpenFileSectionScreen())
            return

        collapsible = self.get_closest_collapsible(event.button)

        if not collapsible:
            if button_id != "add-top-level":
                print("No collapsible found for button press.")
                return
        else:
            item = collapsible.json_data
            parent_list = collapsible.parent_list

        self.saved = False

        if button_id == "add":
            self.adding["parent_list"] = parent_list
            self.adding["item"] = item
            self.app.push_screen("add_screen")

        elif button_id == "add-top-level":
            self.adding["parent_list"] = None
            self.adding["item"] = None
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

    def save_file(self):
        """Saves the currently loaded file section back into the source file."""
        if not hasattr(self, "path") or not self.path:
            print("Showing file picker to select save location")
            self.app.post_message(NewFile())
            return

        section_name = getattr(self, "current_section", None)
        if not section_name:
            print("No section selected to save.")
            return

        file_path = Path(self.path)
        source = file_path.read_text()

        try:
            tree = ast.parse(source, filename=str(file_path)) if source.strip() else ast.Module(body=[], type_ignores=[])
        except Exception as e:
            print(f"Error reading or parsing file: {e}")
            return

        # Create a new AST node from the current section's data
        try:
            new_data_node = ast.parse(repr(self.data)).body[0].value
        except Exception as e:
            print(f"Failed to convert data to AST: {e}")
            return

        # Find and replace or append the assignment
        section_updated = False
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == section_name:
                        node.value = new_data_node
                        section_updated = True
                        break

        if not section_updated:
            assign = ast.Assign(
                targets=[ast.Name(id=section_name, ctx=ast.Store())],
                value=new_data_node
            )
            tree.body.append(assign)

        # Fix missing line/column locations before unparsing
        tree = ast.fix_missing_locations(tree)

        try:
            new_source = ast.unparse(tree)  # Requires Python 3.9+
            file_path.write_text(new_source)
            print(f"Saved section '{section_name}' to {file_path}")
            self.saved = True
        except Exception as e:
            print(f"Failed to write file: {e}")


    def add_file_section(self, name):
        if not self.saved:
            self.app.notify("Please save the current section before adding a new one.")
            self.save_file()

        self.file_sections.append(name)

        select = self.query_one("#select_file_section")
        select.set_options(
            [(name, name) for name in self.file_sections]
        )
        self.current_section = name