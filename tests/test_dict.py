""" Tests converting from/to dicts """

import namespace as ns


def test_ns2dict():
    """ Tests the ns2dict helper
    """

    cfg = ns.Namespace()
    ns.set_in_path(cfg, "Section.value", 42)
    d = ns.ns2dict(cfg)

    assert 'Section' in d, "Section missing"
    assert isinstance(d['Section'], dict), "Section should be dict"
    assert d['Section']['value'] == 42, "Value property set incorrectly"
    

def test_dict2ns():
    input = {
        'l1name': 'l1name_value',
        'l1sec': {
            'l2name': 'l2name_value'
        },
        'vlst': ['a', 'b'],
        'olst': [{'n':'v'}]
    }
    
    cfg = ns.dict2ns(input)
    
    assert 'l1name' in cfg, "Top level name should be present"
    assert cfg.l1name == 'l1name_value', "Top level value should be correct"
    
    assert 'l1sec' in cfg, "Section should be present"
    assert isinstance(cfg.l1sec, ns.Namespace), "Section should be namespace"
    
    assert 'l2name' in cfg.l1sec, "Subname should be present"
    assert cfg.l1sec.l2name == "l2name_value", "Sub level value should be correct"
    
    assert 'vlst' in cfg, "Value list should be present"
    assert len(cfg.vlst) == 2, "Two items in list"
    assert cfg.vlst[0] == 'a', "List item 0 should have proper value"
    assert cfg.vlst[1] == 'b', "List item 1 should have proper value"

    assert 'olst' in cfg, "Object list should be present"
    assert len(cfg.olst) == 1, "One item in list"
    assert isinstance(cfg.olst[0], ns.Namespace), "Object in list should be namespace"
    assert 'n' in cfg.olst[0], "Name in object in list should be present"
    assert cfg.olst[0].n == "v", "Value in object in list should be correct"
    
