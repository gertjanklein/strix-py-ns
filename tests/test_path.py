
"""Test the get/set in path helper code."""

import pytest
import namespace as ns


def test_set_in_path():
    """Test creating a deep path."""
    
    cfg = ns.Namespace()
    ns.set_in_path(cfg, 'Testing.One.Two.Three.name', '42')
    assert cfg.Testing.One.Two.Three.name == '42'


def test_set_in_path_section_is_value():
    """Test error when existing value accessed as section."""
    
    cfg = ns.Namespace()
    cfg.Section = ''
    with pytest.raises(ns.ConfigurationError):
        ns.set_in_path(cfg, "Section.name", '42')


def test_set_in_path_section_exists():
    """Test setting value in existing section works."""
    
    cfg = ns.Namespace()
    cfg.Section = ns.Namespace()
    ns.set_in_path(cfg, "Section.name", '42')
    assert cfg.Section.name == '42' # pylint: disable=no-member


def test_get_in_path():
    """Test retrieving values using path string."""
    
    cfg = ns.Namespace()
    assert ns.get_in_path(cfg, 'Section.value') is None
    assert ns.get_in_path(cfg, 'Section.value', '') == ''
    cfg.Section = ns.Namespace()
    assert ns.get_in_path(cfg, 'Section.value') is None
    assert ns.get_in_path(cfg, 'Section.value', '') == ''
    cfg.Section.value = '42'
    assert ns.get_in_path(cfg, 'Section.value') == '42'
    cfg.Section = ''
    assert ns.get_in_path(cfg, 'Section.value') is None
    


