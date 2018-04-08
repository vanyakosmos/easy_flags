easy_flags
==========

The goal of this nano-project is to provide sane alternative for ``tensorflow.flags`` by adding some additional features that ``tensorflow.flags`` currently lacks:

#. typechecking
#. autocompletion
#. configuration reusability
#. full config print out

Of course ``easy_flags`` doesn't depend on ``tensorflow`` and can be used w/o it.


Basic example
-------------

configs.py

.. code-block:: python

    from easy_flags import BaseConfig

    class ModelConfig(BaseConfig):
        layers = 4
        dropout = 0.4, 'this is docstring for this field'  # type: float
        leaky = True, 'use leaky relu'  # type: bool
    
    class TrainingConfig(ModelConfig):
        lr = 0.001, 'learning rate'  # type: float
        e = 100, 'number of epochs'  # type: int

    class PredictConfig(ModelConfig):
        load_path = 'path/to/model/checkpoint'


train.py

.. code-block:: python

    from configs import TrainingConfig

    conf = TrainingConfig()  # instantiate config object

    def train(epochs: int, lr: float, layers: int, dropout: float, leaky_relu: bool):
        # or use `conf` directly inside function
        ...

    def main():
        train(conf.e, conf.lr, conf.layers, conf.dropout, conf.leaky)

    if __name__ == "__main__":
        conf.define()  # read flags from sys.argv and fill `conf` with default or new values
        conf.print()  # pretty-print all flags and their values
        main()

.. code-block:: bash

    python train.py --layers 2 --lr 0.1 -e 42 --no-leaky


predict.py

.. code-block:: python

    from configs import PredictConfig

    conf = PredictConfig()

    def predict(load_path: str, layers: int):
        ...

    def main():
        predict(conf.load_path, conf.layers)

    if __name__ == "__main__":
        conf.define()
        conf.print()
        main()

.. code-block:: bash

    python predict.py --layers 2 --load_path "not/default/path/to/model" --no-leaky



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


In example above pre-defined ``conf.lr`` is obviously not a float and some IDE/linters after typechecking will make a warning that they expected a float as argument for some function but got tuple instead. Fortunately we can help IDE by adding special comment with proper after-define type:

.. code-block:: python

    class ExampleConfig(BaseConfig):
        lr = 0.001, 'learning rate'  # type: float



Global FLAGS
------------

Globally available ``easy_flags.FLAGS`` is pointing to the latest defined config or to ``None`` if no config was defined. You can specify type after import:

.. code-block:: python

    from easy_flags import FLAGS
    from configs import ExampleConfig

    FLAGS: ExampleConfig = FLAGS


.. code-block:: python

    # or just import config object from script that defines it
    from train import conf
