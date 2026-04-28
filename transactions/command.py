# Pattern: Command (Abstract + Invoker)
from abc import ABC, abstractmethod

class Command(ABC):

    @abstractmethod
    def execute(self) -> dict:

        pass

    @abstractmethod
    def undo(self) -> dict:

        pass

    @abstractmethod
    def get_description(self) -> str:
        pass

class CommandInvoker:

    def __init__(self):
        self._history: list = []

    def execute(self, command: Command) -> dict:
        result = command.execute()
        self._history.append(command)
        return result

    def undo_last(self) -> dict:
        if not self._history:
            return {"success": False, "message": "No commands to undo."}
        return self._history.pop().undo()

    def get_history(self) -> list:
        return list(self._history)
