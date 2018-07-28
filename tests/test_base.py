from unittest import TestCase

from easy_flags import BaseConfig


class ExampleConfig(BaseConfig):
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


class TestBaseConfig(TestCase):
    def setUp(self):
        self.conf = ExampleConfig()
        self.conf._setup_arguments()
        # [] is crucial because w/o it argparse will try to catch
        # sys.argv with test fixture arguments
        self.conf._parse_arguments([])
        self.conf.fill_attributes()

    def tearDown(self):
        self.conf._parse_arguments([])
        self.conf.fill_attributes()

    def test_int(self):
        self.assertEqual(self.conf.a, 1)

        self.conf._parse_arguments(['-a', '2'])
        self.conf.fill_attributes()
        self.assertEqual(self.conf.a, 2)

        self.conf._parse_arguments(['-a', '4325'])
        self.conf.fill_attributes()
        self.assertEqual(self.conf.a, 4325)

    def test_float(self):
        self.assertAlmostEqual(self.conf.b, 2.3)

        self.conf._parse_arguments(['-b', '5'])
        self.conf.fill_attributes()
        self.assertAlmostEqual(self.conf.b, 5.0)

        self.conf._parse_arguments(['-b', '3.1415'])
        self.conf.fill_attributes()
        self.assertAlmostEqual(self.conf.b, 3.1415)

    def test_boolean(self):
        self.assertEqual(self.conf.c, True)
        self.assertEqual(self.conf.d, False)

        self.conf._parse_arguments(['--c', '--d'])
        self.conf.fill_attributes()
        self.assertEqual(self.conf.c, True)
        self.assertEqual(self.conf.d, True)

        self.conf._parse_arguments(['--no-c', '--no-d'])
        self.conf.fill_attributes()
        self.assertEqual(self.conf.c, False)
        self.assertEqual(self.conf.d, False)

    def test_str(self):
        self.assertEqual(self.conf.e, 'fds')

        self.conf._parse_arguments(['-e', 'hurma'])
        self.conf.fill_attributes()
        self.assertEqual(self.conf.e, 'hurma')

        self.conf._parse_arguments(['-e', 'multi word text'])
        self.conf.fill_attributes()
        self.assertEqual(self.conf.e, 'multi word text')

    def test_tuple(self):
        self.assertAlmostEqual(self.conf.f, 5.0)

        self.conf._parse_arguments(['-f', '7'])
        self.conf.fill_attributes()
        self.assertAlmostEqual(self.conf.f, 7.0)

        self.conf._parse_arguments(['-f', '3.1415'])
        self.conf.fill_attributes()
        self.assertAlmostEqual(self.conf.f, 3.1415)

    def test_tuple_with_type(self):
        self.assertEqual(self.conf.t, None)

        self.conf._parse_arguments(['-t', '2'])
        self.conf.fill_attributes()
        self.assertEqual(self.conf.t, 2)

        self.conf._parse_arguments(['-t', '4325'])
        self.conf.fill_attributes()
        self.assertEqual(self.conf.t, 4325)

    def test_resolver(self):
        self.assertEqual(self.conf.v, '210')

        self.conf._parse_arguments(['-v', '2'])
        self.conf.fill_attributes()
        self.assertEqual(self.conf.v, '84')

        self.conf._parse_arguments(['-v', '10'])
        self.conf.fill_attributes()
        self.assertEqual(self.conf.v, '420')

    def test_multiletter_flag(self):
        self.assertEqual(self.conf.aa, 1)

        self.conf._parse_arguments(['--aa', '2'])
        self.conf.fill_attributes()
        self.assertEqual(self.conf.aa, 2)

        self.conf._parse_arguments(['--aa', '4325'])
        self.conf.fill_attributes()
        self.assertEqual(self.conf.aa, 4325)

    def test_short_flag_with_two_dashes(self):
        self.assertEqual(self.conf.a, 1)

        self.conf._parse_arguments(['--a', '2'])
        self.conf.fill_attributes()
        self.assertEqual(self.conf.a, 2)

        self.conf._parse_arguments(['--a', '4325'])
        self.conf.fill_attributes()
        self.assertEqual(self.conf.a, 4325)
