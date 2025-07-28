import asyncio
import os
from pathlib import Path

from textual.app import ComposeResult
from textual.widgets import DirectoryTree, Input, Select, Label, Rule, Button
from textual.containers import VerticalGroup, HorizontalGroup
from textual.screen import ModalScreen

from components.messages import LoadFile

class FilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths):
        return [p for p in paths if (p.is_dir() or p.suffix in {".py"}) and not p.name.startswith(".")]

class FilePicker(ModalScreen[bool]):
    def compose(self) -> ComposeResult:
        yield VerticalGroup(
            Input(placeholder="Path", id="file_input"),
            Label("Filter the tree's file path", classes="hint"),
            Select(options=[], prompt="Found on device",id="files_found"),
            Label("Select a path if any season_fields.py files were found on your device", classes="hint"),
            Rule(),
            FilteredDirectoryTree("~", id="tree"),
            HorizontalGroup(
                Button.success("Confirm", disabled=True, id="confirm"),
                Button.error("Cancel", id="cancel"),
                Button("Create new", id="new"),
                classes="button-row"
            ),
            classes="dialog"
        )

    def on_mount(self) -> None:
        self.selected = ""

        self.query_one("#tree").path = "~"
        asyncio.create_task(self.find_files(Path.home()))

    async def find_files(self, root: Path):
        select = self.query_one("#files_found")
        found = []

        async def walk(path: Path):
            try:
                for entry in os.scandir(path):
                    # Skip symlinks
                    if entry.is_symlink():
                        continue

                    if entry.is_file() and entry.name == "season_fields.py":
                        file_path = str(Path(entry.path))
                        found.append((file_path, os.path.dirname(file_path)))
                        select.set_options(found)

                    elif entry.is_dir() and not entry.name.startswith("."):
                        await asyncio.sleep(0)  # Yield to event loop
                        await walk(Path(entry.path))
            except (PermissionError, FileNotFoundError, OSError):
                pass  # Skip directories we can't access


        await walk(root)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "file_input":
            path = Path(event.input.value).expanduser()
            if path.exists():
                self.query_one("#tree").path = str(path)
        
    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "files_found":
            selected = event.select.value
            if isinstance(selected, str):  # Only update if a real selection is made
                self.query_one("#file_input").value = selected

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self.selected = event.path

        if self.selected.suffix == ".py":
            self.query_one("#confirm").disabled = False
        else:
            self.query_one("#confirm").disabled = True

    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        self.selected = event.path

        if self.selected.suffix == ".py":
            self.query_one("#confirm").disabled = False
        else:
            self.query_one("#confirm").disabled = True

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            self.post_message(LoadFile(self.selected))
            self.dismiss(True)
        elif event.button.id == "cancel":
            self.dismiss(False)
        elif event.button.id == "new":
            file_input = self.query_one("#file_input")
            path = Path(file_input.value).expanduser() / "season_fields.py"

            if not path.exists():
                path.touch()
                self.app.notify(f"Created new file {path}")
            else:
                self.app.notify(f"{path} already exists!")

            self.query_one("#tree").path = str(path.parent)
