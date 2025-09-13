from functools import partial
from typing import Callable, Any
import inspect

class AgentFactory:
    def __init__(self) -> None:
        self._registry = {}

    def register(self, name, constructor) -> None:
        if name in self._registry:
            raise KeyError(f"Agent '{name}' is already registered")
        self._registry[name] = constructor

    def register_decorator(self, name):
        """@factory.register_decorator('astar') on a class or function."""
        def _wrap(ctor: Callable[..., Any]):
            self.register(name, ctor)
            return ctor
        return _wrap

    def names(self):
        return sorted(self._registry.keys())

    def create(self, name, **kwargs) -> Any:
        if name not in self._registry:
            raise ValueError(f"Unknown agent type '{name}'. Known: {self.names()}")
        ctor = self._registry[name]

        sig = inspect.signature(ctor)
        accepted = {k: v for k, v in kwargs.items() if k in sig.parameters}

        return partial(ctor, **accepted)

factory = AgentFactory()
