
"""Provide a Namespace supporting both ns.value and ns['value'].

Expected use is to represent configuration files. To that end,
a few functions are also present to ease checking configuration
validity.

Nested namespaces have their name in a property "_name".
"""

import codecs
from typing import Iterable, Mapping, Optional


class Namespace:
    """Namespace that also supports mapping access."""

    def __init__(self, **kwargs):
        """Allow initializing with keyword arguments."""
        
        self.__dict__.update(kwargs)
    
    # ns['key']
    
    def __getitem__(self, key):
        """Add support for value = ns['key']."""

        return self.__dict__[key]
    
    def __setitem__(self, key, value):
        """Add support for ns['key'] = value."""
        
        # Don't allow overwriting methods with data
        if key in self.__class__.__dict__:
            raise ValueError(f"Setting key {key} is not allowed.")
        self.__dict__[key] = value

    def __delitem__(self, key):
        """Add support for del ns['key']."""
        
        del self.__dict__[key]

    # ns.key
    
    def __getattr__(self, key):
        """Add support for value = ns.key."""
        
        if key in self.__dict__:
            return self.__dict__[key]
        raise AttributeError(f"{key}")

    def __setattr__(self, name, value):
        """Add support for ns.key = value."""
        
        if name in self.__class__.__dict__:
            raise ValueError(f"Setting attribute {name} is not allowed.")
        self.__dict__[name] = value

    # key in ns
    
    def __contains__(self, key):
        """Add support for in operator."""
        
        return key in self.__dict__

    # for key in ns
    
    def __iter__(self):
        """Add support for iteration."""

        return iter(self.__dict__)

    # repr(ns), str(ns)
    
    def __repr__(self):
        """Can be used to re-create objects."""
        
        attrs = []
        for key, value in self.__dict__.items():
            if isinstance(value, Namespace):
                attrs.append(f"{key}={value.__repr__()}")
            else:
                attrs.append(f"{key}={value!r}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"

    def __str__(self):
        """Simplified dictionary-form representation."""
        
        attrs = []
        for key, value in self.__dict__.items():
            if isinstance(value, Namespace):
                attrs.append(f"{key!r}: {value!s}")
            else:
                attrs.append(f"{key!r}: {value!r}")
        return f"{{{', '.join(attrs)}}}"

    # ----- Helper methods

    def _get(self, key, default=None):
        """Retrieve a value, or default if not found."""

        return self.__dict__.get(key, default)

    def _flattened(self, _prefix=None):
        """Yield (dotted name, value) pairs for all values."""
        
        for key in self:
            if key == '_name':
                continue
            value = self[key]
            key = f"{_prefix}.{key}" if _prefix else key
            if isinstance(value, type(self)):
                yield from value._flattened(key)
            else:
                yield key, value

    @staticmethod
    def _from_dict(input:Mapping) -> 'Namespace':
        """Create a namespace from a dictionary."""
        
        ns = Namespace()
        for k, v in input.items():
            if isinstance(v, dict):
                ns[k] = dict2ns(v)
                ns[k]['_name'] = k
            elif isinstance(v, list):
                ns[k] = v
                for i, v2 in enumerate(v):
                    if not isinstance(v2, dict):
                        continue
                    v[i] = dict2ns(v2)
                    v[i]['_name'] = f'{k}[{i+1}]'
            else:
                ns[k] = v
        
        return ns

    def _to_dict(self) -> dict:
        """Convert a Namespace to a dict."""

        d = {}
        for k, v in self.__dict__.items():
            if isinstance(v, Namespace):
                d[k] = ns2dict(v)
                if '_name' in d[k]:
                    del d[k]['_name']
            else:
                d[k] = v
        
        return d


# Backwards compatibility code

def dict2ns(input:Mapping) -> Namespace:
    """Convert a dict to a namespace for attribute access."""
    return Namespace._from_dict(input)

def ns2dict(input:Namespace) -> dict:
    """Convert a Namespace to a dict."""
    return input._to_dict()


# =====

def set_in_path(ns:Namespace, path:str, value):
    """Set a value in a sub-namespace, assuring it exists."""

    parts = path.split('.')
    # Add sub-namespaces, if not present
    for name in parts[:-1]:
        if not name in ns:
            ns[name] = Namespace()
            ns[name]['_name'] = name
        elif not isinstance(ns[name], Namespace):
            raise ConfigurationError(f"Configuration error: {name} in configuration should be a section")
        ns = ns[name]
    # Set value
    value_name = parts[-1]
    ns[value_name] = value

def get_in_path(ns:Namespace, path:str, default=None):
    """Get a value in a sub-namespace, if present. Never raises."""

    assert '.' in path
    parts = path.split('.')
    # Add sub-namespaces, if not present
    for name in parts[:-1]:
        if not name in ns:
            return default
        ns = ns[name]
        if not isinstance(ns, Namespace):
            return None
    value_name = parts[-1]
    return ns._get(value_name, default)


# =====

class ConfigurationError(ValueError):
    """Exception to signal detected error in configuration."""

def get_section(config:Namespace, name:str, create=False) -> Optional[Namespace]:
    """Return a section if it exists; optionally creates if not."""
    
    section = config._get(name)
    if section is None:
        if not create:
            return None
        
        section = Namespace()
        config[name] = section
        config[name]['_name'] = name
        return section
        
    if not isinstance(section, Namespace):
        raise ConfigurationError(f"Configuration error: {name} not a section")
    return section

def check_section(config:Namespace, name:str) -> Namespace:
    """Check that a section with the specified name is present."""

    section = config._get(name)
    if section is None:
        raise ConfigurationError(f"Section {name} not found in configuration")
    if not isinstance(section, Namespace):
        raise ConfigurationError(f"Configuration error: {name} not a section")
    return section

def check_default(section:Namespace, name:str, default) -> bool:
    """Check if a value is present, setting default if not."""

    value = section._get(name)
    if value is None or value == '':
        section[name] = default
        return True
    return False

def check_oneof(section:Namespace, name:str, oneof:Iterable, default=None):
    """Raise if value not in supplied list of options."""

    value = section._get(name)
    if (value is None or value == '') and not default is None:
        section[name] = default
        return
    if value in oneof: return
    disp_name = f'{section._name}:{name}' if '_name' in section else name
    raise ConfigurationError(f"Configuration error: {disp_name} must be one of {str(oneof)}")

def check_notempty(section:Namespace, name:str):
    """Raise if value not supplied or empty."""

    value = section._get(name)
    if value: return
    disp_name = f'{section._name}:{name}' if '_name' in section else name
    raise ConfigurationError(f"Configuration error: {disp_name} must be present and non-empty")

def check_encoding(section:Namespace, name:str, default):
    """Raise if specified encoding is unknown."""
    
    if check_default(section, name, default):
        return
    encoding = section[name]
    try:
        codecs.lookup(encoding)
    except LookupError:
        disp_name = f'{section._name}:{name}' if '_name' in section else name
        msg = f"Configuration error: {disp_name}: '{encoding}' is an unrecognised encoding"
        raise ConfigurationError(msg) from None
