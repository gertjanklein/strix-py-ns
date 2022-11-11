"""Various namespace tests."""
import pytest
import namespace as ns

def test_del():
    """Test that del works."""
    
    cfg = ns.Namespace()
    cfg.attr = ''
    assert 'attr' in cfg
    del cfg.attr  # type: ignore
    assert 'attr' not in cfg


def test_add_section():
    """Tests adding a section if not present."""
    
    cfg = ns.Namespace()
    section = ns.get_section(cfg, 'test')
    assert section is None
    assert 'test' not in cfg
    assert ns.get_in_path(cfg, 'Section.value') is None
    section = ns.get_section(cfg, 'test', True)
    assert section is not None
    assert 'test' in cfg
    assert cfg['test'] is section


def test_get_existing_section():
    """Tests retrieving an existing section."""
    
    cfg = ns.Namespace()
    cfg.section = ns.Namespace()
    cfg.section.name = "value"
    
    section = ns.get_section(cfg, 'section')
    assert section, "Section should be found"
    assert section.name == 'value', "Section should have expected property/value"
    

def test_check_section():
    """Tests the check_section method."""
    
    cfg = ns.Namespace()
    cfg.section = ns.Namespace()
    cfg.section.name = "value"
    
    # Retrieving a non-existing section should raise
    with pytest.raises(ns.ConfigurationError):
        ns.check_section(cfg, 'zection')
    
    # An existing section should be returned
    section = ns.check_section(cfg, 'section')
    assert section, "Section should be found"
    assert section.name == 'value', "Section should have expected property/value"
    

def test_check_default():
    """Tests the check_default method."""
    
    cfg = ns.Namespace()
    cfg.name = "value"
    
    assert not ns.check_default(cfg, 'name', 42), "Property should not be set"
    assert cfg.name == 'value', "Property unaltered"
    
    assert ns.check_default(cfg, 'name2', 42), "Property should be set"
    assert 'name2' in cfg, "Property should be present"
    assert cfg.name2 == 42, "Property should have expected value"
    

def test_check_oneof():
    """Tests the check_oneof method."""
    
    cfg = ns.Namespace()
    cfg.namea = "v"
    cfg.nameb = "x"
    allowed = ['v', 'w']
    
    # Existing property, value allowed
    ns.check_oneof(cfg, 'namea', allowed)
    assert cfg.namea == 'v', "Property unaltered"
    
    # Existing property, value not allowed
    with pytest.raises(ns.ConfigurationError):
        ns.check_oneof(cfg, 'nameb', allowed)
    assert cfg.nameb == 'x', "Property unaltered"
    
    # Non-existing property, default specified
    ns.check_oneof(cfg, 'namec', allowed, 'w')
    assert 'namec' in cfg, "Property set"
    assert cfg.namec == 'w', "Property should have default value"
    

def test_value_as_namespace_error():
    """Tests getting a value as a section raises."""

    cfg = ns.Namespace()
    cfg.value = '42'

    with pytest.raises(ns.ConfigurationError) as e:
        ns.get_section(cfg, 'value')
    assert "not a section" in e.value.args[0], f"Unexpected error msg: {e.value.args[0]}"

    with pytest.raises(ns.ConfigurationError) as e:
        ns.check_section(cfg, 'value')
    assert "not a section" in e.value.args[0], f"Unexpected error msg: {e.value.args[0]}"

    
def test_value_not_oneof_raises():
    """Tests that a value outside the allowed range raises."""

    cfg = ns.Namespace()
    cfg.value = '42'

    with pytest.raises(ns.ConfigurationError) as e:
        ns.check_oneof(cfg, 'value', ("a", "b"))
    assert "must be one of" in e.value.args[0], f"Unexpected error msg: {e.value.args[0]}"


def test_value_not_present_raises():
    """Tests that a missing value raises."""

    cfg = ns.Namespace()

    with pytest.raises(ns.ConfigurationError) as e:
        ns.check_notempty(cfg, 'value')
    assert "must be present and non-empty" in e.value.args[0], f"Unexpected error msg: {e.value.args[0]}"

    cfg.value = ''
    with pytest.raises(ns.ConfigurationError) as e:
        ns.check_notempty(cfg, 'value')
    assert "must be present and non-empty" in e.value.args[0], f"Unexpected error msg: {e.value.args[0]}"


def test_check_encoding():
    """Tests errors on invalid encoding values."""

    cfg = ns.Namespace()
    cfg.enc = 'CP900000'

    with pytest.raises(ns.ConfigurationError) as e:
        ns.check_encoding(cfg, 'enc', 'dummy')
    assert "is an unrecognised encoding" in e.value.args[0], f"Unexpected error msg: {e.value.args[0]}"
    
    # Default provided in code is not checked; this hould not raise
    del cfg.enc  # type: ignore
    ns.check_encoding(cfg, 'enc', 'dummy')
    assert cfg.enc == 'dummy', "Property must have unchecked value"
    


def test_check_missing_attribute():
    """Tests missing attribute raises KeyError."""

    cfg = ns.Namespace()
    with pytest.raises(AttributeError) as e:
        _ = cfg.value
    assert e.value.args[0] == 'value', f"Unexpected error attribute: {e.value.args[0]}"


def test_flattened_empty():
    """Tests the _flattened method on empty namespace."""

    cfg = ns.Namespace()
    seen = False
    for _ in cfg._flattened():
        seen = True
    assert not seen, "Flattened returned a value where it shouldn't."


def test_flattened():
    """Tests the _flattened method."""

    # A few flattened key, value pairs to test against
    tests = {
        "Key": 42,
        "Section.Key": 43,
        "Section.SubSection.Key": 44,
        "Section.SubSection.SubSubSection.Key": 45,
    }

    # Populate the namespace
    cfg = ns.Namespace()
    for k, v in tests.items():
        ns.set_in_path(cfg, k, v)
    
    # Check the keys returned by _flattened
    for k, v in cfg._flattened():
        # The key should be found
        assert k in tests, f"Unexpected or duplicate key '{k}'"
        # The value should be correct
        assert v == tests[k], f"Unexpected value '{v}' for key '{k}'"
        # The key should only be found once
        del tests[k]

    # All test keys should have been returned
    assert not tests, "Not all keys returned by _flattened."

