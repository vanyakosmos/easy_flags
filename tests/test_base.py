from unittest import TestCase

import easy_flags as ef


class ExampleSimpleConfig(ef.SimpleConfig):
    a = 1
    aa = 1
    b = 2.3
    c = True
    d = False
    e = 'fds'
    f = 5.0, 'some int field'
    t = None, int, ''
    v = 5  # type: str

    def resolve_v(self, value: int):
        return str(value * 42)


class ExampleConfig(ef.Config):
    _desc = "example config"

    a = ef.IntField(1)
    aa = ef.Field(1)
    b = ef.FloatField(2.3)
    c = ef.BoolField(True)
    d = ef.BoolField(False)
    e = ef.StringField('fds')
    f = ef.FloatField(5, 'some int field')
    t = ef.Field(type_=int)
    v = ef.MethodField(ef.IntField(5), 'get_v')

    # shouldn't be called
    def resolve_a(self, value: int):
        return str(value * 42)

    def get_v(self, value: int):
        return str(value * 42)


class TestBaseConfig(TestCase):
    def setUp(self):
        self.conf = ExampleSimpleConfig(desc='simple example')
        self.conf._setup_arguments()
        # [] is crucial because w/o it argparse will try to catch
        # sys.argv with test fixture arguments
        self.conf._parse_arguments([])
        self.conf._fill_attributes()

    def tearDown(self):
        self.conf._parse_arguments([])
        self.conf._fill_attributes()

    def test_int(self):
        self.assertEqual(self.conf.a, 1)

        self.conf._parse_arguments(['-a', '2'])
        self.conf._fill_attributes()
        self.assertEqual(self.conf.a, 2)

        self.conf._parse_arguments(['-a', '4325'])
        self.conf._fill_attributes()
        self.assertEqual(self.conf.a, 4325)

    def test_float(self):
        self.assertAlmostEqual(self.conf.b, 2.3)

        self.conf._parse_arguments(['-b', '5'])
        self.conf._fill_attributes()
        self.assertAlmostEqual(self.conf.b, 5.0)

        self.conf._parse_arguments(['-b', '3.1415'])
        self.conf._fill_attributes()
        self.assertAlmostEqual(self.conf.b, 3.1415)

    def test_boolean(self):
        self.assertEqual(self.conf.c, True)
        self.assertEqual(self.conf.d, False)

        self.conf._parse_arguments(['--c', '--d'])
        self.conf._fill_attributes()
        self.assertEqual(self.conf.c, True)
        self.assertEqual(self.conf.d, True)

        self.conf._parse_arguments(['--no-c', '--no-d'])
        self.conf._fill_attributes()
        self.assertEqual(self.conf.c, False)
        self.assertEqual(self.conf.d, False)

    def test_str(self):
        self.assertEqual(self.conf.e, 'fds')

        self.conf._parse_arguments(['-e', 'hurma'])
        self.conf._fill_attributes()
        self.assertEqual(self.conf.e, 'hurma')

        self.conf._parse_arguments(['-e', 'multi word text'])
        self.conf._fill_attributes()
        self.assertEqual(self.conf.e, 'multi word text')

    def test_tuple(self):
        self.assertAlmostEqual(self.conf.f, 5.0)

        self.conf._parse_arguments(['-f', '7'])
        self.conf._fill_attributes()
        self.assertAlmostEqual(self.conf.f, 7.0)

        self.conf._parse_arguments(['-f', '3.1415'])
        self.conf._fill_attributes()
        self.assertAlmostEqual(self.conf.f, 3.1415)

    def test_tuple_with_type(self):
        self.assertEqual(self.conf.t, None)

        self.conf._parse_arguments(['-t', '2'])
        self.conf._fill_attributes()
        self.assertEqual(self.conf.t, 2)

        self.conf._parse_arguments(['-t', '4325'])
        self.conf._fill_attributes()
        self.assertEqual(self.conf.t, 4325)

    def test_resolver(self):
        self.assertEqual('210', self.conf.v)

        self.conf._parse_arguments(['-v', '2'])
        self.conf._fill_attributes()
        self.assertEqual('84', self.conf.v)

        self.conf._parse_arguments(['-v', '10'])
        self.conf._fill_attributes()
        self.assertEqual('420', self.conf.v)

    def test_multiletter_flag(self):
        self.assertEqual(self.conf.aa, 1)

        self.conf._parse_arguments(['--aa', '2'])
        self.conf._fill_attributes()
        self.assertEqual(self.conf.aa, 2)

        self.conf._parse_arguments(['--aa', '4325'])
        self.conf._fill_attributes()
        self.assertEqual(self.conf.aa, 4325)

    def test_short_flag_with_two_dashes(self):
        self.assertEqual(self.conf.a, 1)

        self.conf._parse_arguments(['--a', '2'])
        self.conf._fill_attributes()
        self.assertEqual(self.conf.a, 2)

        self.conf._parse_arguments(['--a', '4325'])
        self.conf._fill_attributes()
        self.assertEqual(self.conf.a, 4325)


class TestConfig(TestBaseConfig):
    def setUp(self):
        self.conf = ExampleConfig()
        self.conf._setup_arguments()
        self.conf._parse_arguments([])
        self.conf._fill_attributes()


def main():
    ExampleConfig().define().print()


if __name__ == '__main__':
    main()
