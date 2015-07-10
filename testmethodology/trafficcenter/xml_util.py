from lxml import etree


def validate(xml_str, xml_schema_file):
    try:
        schema = etree.XMLSchema(etree.parse(open(xml_schema_file, 'r')))
        return schema.validate(etree.fromstring(xml_str))
    except Exception as e:
        print 'Error in validating xml schema: %s' % e
        return False
