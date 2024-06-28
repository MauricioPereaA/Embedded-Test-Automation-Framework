How-To install DTAF.
--------------------------------------

Welcome!
This may be the first time you interact with DTAF, as you may have seen in the
demo, you already know we have 2 installation modes, (beside the profiles).

For this we have 2 ways to install DTAF into your machine, depending on what
are you aiming to do.

* If you're going to join our DTAF development, we suggest you to install DTAF in
  developent mode. this will download and install mutlitple libraries we use
  internally and allow you to explore the source code.

* If you're going to use DTAF to test some client device, we suggest you use
  one of our release packages. they're pre-compiled and packaged in a single
  file.

.. note::
    **Third Party Licenses.**

    Please keep in mind that your team will need to agree to the licenses
    provided by third party software used in our redistribuitable packages.

    All licenses will be available at the package installation directory.

.. warning::
    **For Source Code installs.**

    Keep in mind that if you're about to install DTAF from source code (for
    any reason). you may need to download third party software, such as
    compilirs, providers and akin.

    You will need a network connection for it to work and some may require
    some level of privilege.

    If you face any issue regarding autorative rights, please get in touch with
    your IT department/representative.


How-To install DTAF in development mode.
-----------------------------------------

First, you will need to assign a folder where we're going to be working, we
suggest you to use a folder in your documents folder named 07-Internal
(``~/documents/07-internal/``), we're going to refer to this address as ``internal/``
from now on.

1.- Inside ``internal/`` you will need to clone DTAF repository, please use
``git clone http://www.github.com/address``

2.- **Optional** Depending on your team requirements, you may find usefull
changing the current branch of the clone, you can use the web browser
to see all remote branches or use `git branch -v -a` in a terminal
interpreter. then you can use the command `git checkout -m remote_branch`
to switch to a remote branch (this only work with http clients, for ssh
you can use switch instead of checkout).

3.- You will need a C/C++ compiler installed, depending on your OS version,
you will need some extra headers, this will enable the compiler to generate
the bytecode necessary for third party libraries.

* **For Windows:**
  You may need to install a C/C++ redistribuitable package
  and **Windows SDK** for your OS versions (Windows 7, 8, 8.x, 10, 11).


* **For Linux:** you may need to install build-essetial, gcc or any C/C++
  compiler.

  **libbluetooth-dev** is also a requirements for the bluetooth interface
  to work. (libbluetooth-dev provides ``bluetooth.h`` required by pybluez).

 .. note::
    We recommend you to use your distribution official package manager, it will
    make sure to install all the necessary packages and make it easy for your
    system to find.

    The name of some libraries/headers/symbols may change, please check in
    your OS help documentation pages the alternative package name.


4.- Initialize a virtual environment.
Inside ``internal/../`` create a folder named ``"env"`` then using your
virtual enviroment tool of your preference create a new virtual env.
Name your virtual envirnoment depending on the versionof python you're using.

* Name it ``"python-AMD64"`` if you're running python's ``64-bits`` compilation.
* Name it ``"python-x86"`` if you're using the ``32-bit`` version of the compiler.
* Use the same pattern if you're using any other version. (change ``python``
  if you're using one of the interpreter flavors)

**For this example;** we will be using ``virtualenv``.

.. code-block:: bash

    # at `internal/`
    cd ..
    mkdir env
    cd env
    # make sure you're using the latest packages of the following in your python's global installation.
    python -m pip install --upgrade pip setuptools cython virtualenv
    virtualenv python-AMD64

5.- Activate your virtual environment and make sure it's workign properly,
for venv and virtualenv you will see that the title's propmpt have changed,
showing at the beggining the name of the virtual environment.
for virtualenv, you may use the activate script inside the ``scripts/`` folder
for windows and ``bin/`` folder for Linux and mac OS.

* **For Bash** -- you can use either ``./activate`` or ``./activate.sh`` with
  ``chmod +x``.
* **For Windows' CMD** -- you must use ``./scripts/activate.bat``.
* **For Windows's PowerShell** you must use ``./scripts/activate.ps1``.

  .. warning:: When using Windows.
    You must have enabled the directive to run PS1 files, if you haven't,
    powershell will tell you the appropiate command to do so. otherwise, you
    can look it up in MS Windows' powershell official documentation.

    Depending on your security scope, you may require to request assistance
    from your IT department.

6.- You're almost ready, now you need to update the installation libraries
distribuited within python, use
``python -m pip install --upgrade pip setuptools cython`` to make sure you're
using the latest version of pip and that python is able to use the C++
compiler.

7.- Now you should be ready to install DTAF into your Virtuan environment,
you can easily install it using pip:
``python -m pip install ./internal/TAF-Test-Automation-Framework[dev]``

.. note:: Using installation profiles.
    Note that we parsed the value ``[dev]`` as installation profile, this
    profile will install some custom libs that we may find helpfull if
    we're going to do development in DTAF, such as pre-commit, linters,
    type-checks and such.

    If you're going to only use DTAF as a tool, you can call said
    command without the ``[dev]`` profile modifier.

8.- **Optional** -- Initialize the pre-commit framework in your clone.

Inside your DTAF clone folder, please run ``pre-commit install`` to Initialize
the ``pre-commit`` environment.


.. _pre-commit: <https://pre-commit.com/>

.. note::
    This step is only for those who will work in DTAF adding new features,
    fixes and reviews.
