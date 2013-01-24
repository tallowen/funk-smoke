# README FOR JAMES

## Instalation on UBUNTU (I'm looking at you james)
    sudo apt-get install python-dev python-setuptools python-webunit python-docutils gnuplot
    sudo apt-get install tcpwatch-httpproxy

    git clone git://github.com/nuxeo/FunkLoad.git

    cd FunkLoad/
    python setup.py build
    sudo python setup.py install

## Running Stuff

    cd fixtures/
    fl-run-test test_Smoke.py
