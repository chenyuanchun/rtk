import xml.etree.ElementTree as ET

from copy import copy


def to_dict(node, root=True) -> dict:
    if root:
        return {node.tag: to_dict(node, False)}
    d = copy(node.attrib)
    if node.text:
        d["_text"] = node.text
    for x in node.findall("./*"):
        if x.tag not in d:
            d[x.tag] = []
        d[x.tag].append(to_dict(x, False))
    return d


def xml_to_dict(xml_str: str) -> dict:
    root = ET.fromstring(xml_str)
    return to_dict(root, True)


def simply_xml_dict(xml_dict: dict):
    """
    xml_to_dict generates dict with list as value always, and leaf node shown as key-value pair of '_text'

    >>> test_dict = {'Credential': [{'_text': 'GOLDENEYE'}], 'Host': [{'_text': '$(GE_SOLACE_HOST)'}]}
    >>> simply_xml_dict(test_dict)
    >>> test_dict
    {'Credential': 'GOLDENEYE', 'Host': '$(GE_SOLACE_HOST)'}
    """
    for key, value in xml_dict.items():
        if isinstance(value, list) and len(value) == 1 and isinstance(value[0], dict):
            if len(value[0]) == 1 and '_text' in value[0]:
                xml_dict[key] = value[0]['_text']
            else:
                xml_dict[key] = value[0]
                simply_xml_dict(value[0])
        elif isinstance(value, dict):
            simply_xml_dict(value)


def load_xml_file(path: str):
    root = ET.parse(path).getroot()
    return to_dict(root)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
