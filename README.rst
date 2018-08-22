easy_flags
==========

The goal of this nano-project is to provide simple alternative for ``argparse`` by adding some new features:

#. easy definition
#. type checking (with static type checking tools)
#. reusability


Installation
------------

.. code-block:: bash

    pip install easy_flags


Basic example
-------------

foo.py

.. code-block:: python

    from easy_flags import SimpleConfig

    class MyConfig(SimpleConfig):
        int_val = 4
        bool_val = True
        with_doc = 0.4, 'some docs'  # type: float
        without_default = None, int, 'another docs'  # type: bool

    if __name__ == '__main__':
        # command line arguments will be parsed after ::define call
        c = MyConfig().define().print()
        print('bool_val:', c.bool_val)


Run:

.. code-block::

    $ python foo.py

    + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    |  bool_val        : True
    |  int_val         : 4
    |  with_doc        : 0.4
    |  without_default : None
    + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    bool_val: True

    Process finished with exit code 0


    $ python foo.py -h

    usage: foo.py [-h] [--bool_val | --no-bool_val] [--int_val INT_VAL]
                         [--with_doc WITH_DOC] [--without_default WITHOUT_DEFAULT]

    optional arguments:
      -h, --help            show this help message and exit
      --bool_val            bool, default: True
      --no-bool_val
      --int_val INT_VAL     int, default: 4
      --with_doc WITH_DOC   float, default: 0.4 - some docs
      --without_default WITHOUT_DEFAULT
                            int, default: None - another docs


Alternative definition
----------------------

.. code-block:: python

    from easy_flags import Config, IntField, BoolField, FloatField

    class MyConfig(Config):
        int_val = IntField(4)
        bool_val = BoolField(default=True)
        with_doc = FloatField(0.4, 'some docs')
        without_default = IntField(doc='another docs')


Reusabillity
------------

.. code-block:: python

    from easy_flags import Config

    class ModelConfig(Config):
        layers = 4
        time_steps = 256
        cell_size = 256
        dropout = 1.0

    # same as model config + additional parameters
    class TrainingConfig(ModelConfig):
        lr = 0.001
        epochs = 10000
        dropout = 0.9  # change parent arg


Docstrings
----------

If you want to add help message for field (which will be displayed if you run script with ``--help`` flag), then you need to add it  after flags' default value:

.. code-block:: python

    class ExampleConfig(BaseConfig):
        foo = 5.0, 'Some float field.'
        bar = 'field with only default docstring'

.. code-block:: bash

    ./script.py --help
    usage: test_base.py [-h] [--bar BAR] [--foo FOO]

    optional arguments:
      -h, --help  show this help message and exit
      --bar BAR   String field, default='field with default docstring'.
      --foo FOO   Float field, default=5.0. Some float field.



Booleans
--------

Boolean flag with spefied in config name will set destination value to ``True``, and the same flag prefixed with 'no-' will set value to ``False``

.. code-block:: python

    class ExampleConfig(BaseConfig):
        cache = True
        f = False


.. code-block:: bash

    ./script --cache -f
    # cache=True, f=True

    ./script --no-cache --no-f
    # cache=False, f=False



Short flag names
----------------

If flag name consists only from one letter then it can be specified with one dash instead of two.

.. code-block:: python

    class ExampleConfig(BaseConfig):
        e = 100, 'number of epochs'
        b = True


.. code-block:: bash

    ./train.py -e 42 -b
    # also valid with two dashes
    ./train.py --e 42 --b
    ./train.py --e 42 --no-b



Specify type for tuples
-----------------------

.. code-block:: python

    class ExampleConfig(BaseConfig):
        lr = 0.001, 'learning rate'
    conf = ExampleConfig()
    conf.define()


In example above pre-defined ``conf.lr`` is obviously not a float and some static checkers after typec hecking will make a warning that they expected a float as argument for some function but got tuple instead. Fortunately we can help IDE by adding special comment with proper after-define type:

.. code-block:: python

    class ExampleConfig(BaseConfig):
        lr = 0.001, 'learning rate'  # type: float
