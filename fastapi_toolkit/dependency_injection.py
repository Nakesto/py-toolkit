"""Dependency Injection utilities for FastAPI applications."""

import inspect
from typing import Any, Callable, Dict, Type, TypeVar, get_type_hints
from functools import wraps

T = TypeVar('T')


class DIContainer:
    """Simple dependency injection container."""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._singletons: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
    
    def register_singleton(self, interface: Type[T], implementation: T) -> None:
        """Register a singleton instance."""
        self._singletons[interface] = implementation
    
    def register_transient(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """Register a transient service with a factory function."""
        self._factories[interface] = factory
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """Register a specific instance."""
        self._services[interface] = instance
    
    def get(self, interface: Type[T]) -> T:
        """Get an instance of the requested type."""
        # Check singletons first
        if interface in self._singletons:
            return self._singletons[interface]
        
        # Check registered instances
        if interface in self._services:
            return self._services[interface]
        
        # Check factories
        if interface in self._factories:
            return self._factories[interface]()
        
        # Try to auto-wire if it's a class
        if inspect.isclass(interface):
            return self._auto_wire(interface)
        
        raise ValueError(f"No registration found for {interface}")
    
    def _auto_wire(self, cls: Type[T]) -> T:
        """Automatically wire dependencies for a class."""
        try:
            # Get constructor signature
            sig = inspect.signature(cls.__init__)
            type_hints = get_type_hints(cls.__init__)
            
            # Build constructor arguments
            kwargs = {}
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                param_type = type_hints.get(param_name)
                if param_type:
                    kwargs[param_name] = self.get(param_type)
            
            return cls(**kwargs)
        except Exception as e:
            raise ValueError(f"Failed to auto-wire {cls}: {e}")


# Global container instance
_container = DIContainer()


def get_container() -> DIContainer:
    """Get the global DI container."""
    return _container


def inject(interface: Type[T]) -> T:
    """Dependency injection decorator for FastAPI dependencies."""
    def dependency():
        return _container.get(interface)
    return dependency


def injectable(cls: Type[T]) -> Type[T]:
    """Mark a class as injectable (auto-registration)."""
    _container.register_transient(cls, lambda: _container._auto_wire(cls))
    return cls