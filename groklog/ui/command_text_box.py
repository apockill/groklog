from textual import events
from textual_inputs import TextInput

from groklog.process_node import ProcessNode


class CommandTextbox(TextInput):
    def __init__(self, to_process_node: ProcessNode):
        """A textbox for sending data to a process node
        :param to_process_node: The process node to write to
        """
        super(CommandTextbox, self).__init__()
        self.to_process_node = to_process_node

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            write_text = self.value.encode("utf-8")
            write_text += b"\n"
            self.to_process_node.write(write_text)
            self.value = ""
