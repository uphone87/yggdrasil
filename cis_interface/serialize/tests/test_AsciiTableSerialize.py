import numpy as np
import nose.tools as nt
from cis_interface import backwards
from cis_interface.serialize import AsciiTableSerialize
from cis_interface.serialize.tests import test_DefaultSerialize as parent


def test_serialize_nofmt():
    r"""Test error on serialization without a format."""
    inst = AsciiTableSerialize.AsciiTableSerialize()
    inst._initialized = True
    test_msg = np.zeros((5, 5))
    nt.assert_raises(RuntimeError, inst.serialize, test_msg)

    
def test_deserialize_nofmt():
    r"""Test error on deserialization without a format."""
    inst = AsciiTableSerialize.AsciiTableSerialize()
    test_msg = b'lskdbjs;kfbj'
    test_msg = inst.str_datatype.serialize(test_msg, metadata={})
    nt.assert_raises(RuntimeError, inst.deserialize, test_msg)


class TestAsciiTableSerialize(parent.TestDefaultSerialize):
    r"""Test class for AsciiTableSerialize class."""

    def __init__(self, *args, **kwargs):
        super(TestAsciiTableSerialize, self).__init__(*args, **kwargs)
        self._cls = 'AsciiTableSerialize'
        self.attr_list += ['format_str', 'field_names', 'field_units', 'as_array']

    def test_field_specs(self):
        r"""Test field specifiers."""
        super(TestAsciiTableSerialize, self).test_field_specs()
        # Specific to this class
        self.assert_equal(self.instance.format_str,
                          self.testing_options['kwargs']['format_str'])
        field_names = self.testing_options['kwargs'].get('field_names', None)
        if field_names is not None:
            field_names = [backwards.as_str(x) for x in field_names]
        self.assert_equal(self.instance.field_names, field_names)
        field_units = self.testing_options['kwargs'].get('field_units', None)
        if field_units is not None:
            field_units = [backwards.as_str(x) for x in field_units]
        self.assert_equal(self.instance.field_units, field_units)


class TestAsciiTableSerializeSingle(parent.TestDefaultSerialize):
    r"""Test class for AsciiTableSerialize class."""

    def __init__(self, *args, **kwargs):
        super(TestAsciiTableSerializeSingle, self).__init__(*args, **kwargs)
        self._inst_kwargs['format_str'] = b'%d\n'
        self._cls = 'AsciiTableSerialize'
        self._empty_obj = []
        self._objects = [(1, )]

    def get_testing_options(self):
        r"""Get testing options."""
        out = {'kwargs': {'format_str': b'%d\n'},
               'empty': [],
               'objects': [(1, )],
               'extra_kwargs': {},
               'typedef': {'type': 'array',
                           'items': [{'type': 'int', 'precision': 32}]},
               'dtype': None,
               'is_user_defined': False}
        return out


class TestAsciiTableSerialize_asarray(TestAsciiTableSerialize):
    r"""Test class for AsciiTableSerialize class with as_array."""

    testing_option_kws = {'as_array': True}