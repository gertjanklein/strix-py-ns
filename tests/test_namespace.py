import pytest
import namespace as ns

def test_set_in_path():
    cfg = ns.Namespace()
    ns.set_in_path(cfg, 'Testing.One.Two.Three.name', '42')
    assert cfg.Testing.One.Two.Three.name == '42'


def test_set_in_path_section_is_value():
    cfg = ns.Namespace()
    cfg.Section = ''
    with pytest.raises(ns.ConfigurationError):
        ns.set_in_path(cfg, "Section.name", '42')


def test_set_in_path_section_exists():
    cfg = ns.Namespace()
    cfg.Section = ns.Namespace()
    ns.set_in_path(cfg, "Section.name", '42')
    assert cfg.Section.name == '42' # pylint: disable=no-member


def test_del():
    cfg = ns.Namespace()
    cfg.attr = ''
    assert 'attr' in cfg
    del cfg.attr  # type: ignore
    assert 'attr' not in cfg


def test_get_in_path():
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
    

def test_add_section():
    """ Tests adding a section if not present
    """
    cfg = ns.Namespace()
    section = ns.get_section(cfg, 'test')
    assert section is None
    assert 'test' not in cfg
    assert ns.get_in_path(cfg, 'Section.value') is None
    section = ns.get_section(cfg, 'test', True)
    assert section is not None
    assert 'test' in cfg
    assert cfg['test'] is section


def test_value_as_namespace_error():
    """ Tests getting a value as a section raises
    """

    cfg = ns.Namespace()
    cfg.value = '42'

    with pytest.raises(ns.ConfigurationError) as e:
        ns.get_section(cfg, 'value')
    assert "not a section" in e.value.args[0], f"Unexpected error msg: {e.value.args[0]}"

    with pytest.raises(ns.ConfigurationError) as e:
        ns.check_section(cfg, 'value')
    assert "not a section" in e.value.args[0], f"Unexpected error msg: {e.value.args[0]}"

    
def test_value_not_oneof_raises():
    """ Tests that a value outside the allowed range raises
    """

    cfg = ns.Namespace()
    cfg.value = '42'

    with pytest.raises(ns.ConfigurationError) as e:
        ns.check_oneof(cfg, 'value', ("a", "b"))
    assert "must be one of" in e.value.args[0], f"Unexpected error msg: {e.value.args[0]}"


def test_value_not_present_raises():
    """ Tests that a missing value raises
    """

    cfg = ns.Namespace()

    with pytest.raises(ns.ConfigurationError) as e:
        ns.check_notempty(cfg, 'value')
    assert "must be present and non-empty" in e.value.args[0], f"Unexpected error msg: {e.value.args[0]}"

    cfg.value = ''
    with pytest.raises(ns.ConfigurationError) as e:
        ns.check_notempty(cfg, 'value')
    assert "must be present and non-empty" in e.value.args[0], f"Unexpected error msg: {e.value.args[0]}"


def test_check_encoding():
    """ Tests errors on invalid encoding values
    """

    cfg = ns.Namespace()
    cfg.enc = 'CP900000'

    with pytest.raises(ns.ConfigurationError) as e:
        ns.check_encoding(cfg, 'enc', 'dummy')
    assert "is an unrecognised encoding" in e.value.args[0], f"Unexpected error msg: {e.value.args[0]}"


def test_check_missing_attribute():
    """ Tests missing attribute raises KeyError
    """

    cfg = ns.Namespace()
    with pytest.raises(AttributeError) as e:
        value = cfg.value
    assert e.value.args[0] == 'value', f"Unexpected error attribute: {e.value.args[0]}"


def test_flattened_empty():
    """ Tests the _flattened method on empty namespace.
    """

    cfg = ns.Namespace()
    seen = False
    for n, v in cfg._flattened():
        seen = True
    assert not seen, "Flattened returned a value where it shouldn't."


def test_flattened():
    """ Tests the _flattened method.
    """

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

