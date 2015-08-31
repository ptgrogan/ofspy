# ofspy: Orbital Federates Simulation - Python

## Introduction

This project develops an integrated simulation for Orbital Federates, a simplified model of Federated Satellite Systems (FSS). It demonstrates a multi-actor system value model by mapping input design decisions to initial cost and total value measured by revenue accumulated over a system lifecycle.

## Installation

### Prerequisites
This project has several dependencies based on its intended usage.
 * Basic installation to execute OFS:
  * Python 2.7 (32- or 64-bit) with NumPy and lpsolve55 modules
  * Tkinter with Pillow module to use the graphical user interface (GUI)
 * Optional to cache batch results in a database:
  * MongoDB server
  * PyMongo module
 * Optional to distribute batch executions across multiple threads or hosts:
  * SCOOP module (Scalable COncurrent Operations in Python) with ZeroMQ library
  * Password-less SSH access to each host
  * Identical Python interpreter and OFS executable paths on each host
 * Optional to execute genetic algorithms:
  * DEAP (Distributed Evolutionary Algorithms in Python)
  
While it is possible to use any platform to run OFS, this author recommends Linux/Unix to avoid issues with C/C++ dependencies on Windows and other challenges with SSH for distributed simulation. For convenience, partial guides are included for both platforms below; however, they may need to be adjusted for specific platforms.

### Installation on Windows

This installation guide was developed on Windows 7 and does not consider multi-host execution in detail.

#### Basic Installation

 - Download and install [Python 2.7](https://www.python.org/download/releases/2.7/), select x86 or x86-64 MSI installers depending on your platform (32- or 64-bit)
  - Configure [Windows environment variables](https://docs.python.org/2/using/windows.html#configuring-python): set `PYTHONPATH` to the installation directory, e.g. `C:\Python27`, and also add it to the system `PATH`.
  - Install [PIP package manager](https://pip.pypa.io/en/latest/installing.html) by downloading  the `get-pip.py` file and running with `python get-pip.py`
 - Download and install [Microsoft Visual Studio C++ 2008 Express Edition](http://download.microsoft.com/download/A/5/4/A54BADB6-9C3F-478D-8657-93B3FC9FE62D/vcsetup.exe) - Python 2.7 specifically requires this version
   - For 64-bit Python, also download and install [Microsoft Windows SDK for Windows 7 and .NET Framework 3.5 SP1](http://www.microsoft.com/en-us/download/details.aspx?id=3138)
     - Can uncheck everything **except** ``Developer Tools >> Windows Headers and Libraries`` and ``Developer Tools >> Visual C++ Compilers``
     - After installation, copy file `C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\bin\vcvars64.bat` to `C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\bin\amd64\vcvarsamd64.bat`
 - Download and install NumPy module:
  - For 32-bit Python, use the official [NumPy repository](http://sourceforge.net/projects/numpy/files/), look for the win32 superpack installer for Python 2.7
  - For 64-bit Python, use the unofficial [NumPy repository](http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy), look for the cp27-none-win_amd64 installer, and install downloaded WHL file using PIP, e.g.: `python -m pip install "numpy-1.9.2+mkl-cp27-none-win_amd64.whl"`
 - Download and install lp_solve library and bindings:
   - Download and extract source code for lp_solve Python bindings: [lp_solve_5.5.2.0_Python_source.tar.gz](http://sourceforge.net/projects/lpsolve/files/lpsolve/5.5.2.0/lp_solve_5.5.2.0_Python_source.tar.gz/download)
   - Download Windows libraries for lp_solve: [lp_solve_5.5.2.0_dev_win32.zip](http://sourceforge.net/projects/lpsolve/files/lpsolve/5.5.2.0/lp_solve_5.5.2.0_dev_win32.zip/download) for 32-bit or [lp_solve_5.5.2.0_dev_win64.zip](http://sourceforge.net/projects/lpsolve/files/lpsolve/5.5.2.0/lp_solve_5.5.2.0_dev_win64.zip/download) for 64-bit
     - Extract files into `lp_solve_5.5\extra\Python` directory from expanded Python bindings source code
   - Run `lp_solve_5.5\extra\Python\build.bat` to build the Python bindings for lp_solve
   - Copy the `lpsolve55.dll` file to Python `site-packages` directory, e.g. `C:\Python27\Lib\site-packages\`
   - Check if lpsolve55 module is successfully installed by opening Python command line (interactive mode) and entering `import lpsolve55`
 - Install Pillow for imaging in Tkinter: run command ``python -m pip install pillow``

#### Optional Installation

 - Dependencies required to cache batch results in a database:
   - Download and install [MongoDB](https://www.mongodb.org/downloads) on one host
   - Install PyMongo module using PIP: ``python -m pip install pymongo``
 - Dependencies required to distribute batch executions across multiple threads or hosts:
   - **Note: this installation guide does not cover multi-host execution on Windows in detail. SCOOP will default to multi-thread execution without multi-host configuration.**
   - Download and install [ZeroMQ library for Microsoft Windows](http://zeromq.org/distro:microsoft-windows)
   - Install SCOOP module using PIP: ``python -m pip install scoop``
   - Install a SSH client on each host, authorize each host key for password-less SSH
 - Dependencies required to execute genetic algorithms:
   - Install DEAP module using PIP: ``python -m pip install deap``

### Installation on Linux/Unix
This installation guide follows syntax for RedHat/Scientific Linux flavors. Adapt as necessary for your distribution.

#### Basic Installation

Low-level dependencies install Python, its development headers, and C/C++ compilers: ``sudo yum install python python-devel gcc gcc-c++``

Manually download and install lp_solve_55 Python bindings:
```
# download and unpack lp_solve source code
wget http://downloads.sourceforge.net/project/lpsolve/lpsolve/5.5.2.0/lp_solve_5.5.2.0_source.tar.gz
tar -xvf lp_solve_5.5.2.0_source.tar.gz
# download and unpack lp_solve Python binding source code
wget http://downloads.sourceforge.net/project/lpsolve/lpsolve/5.5.2.0/lp_solve_5.5.2.0_Python_source.tar.gz
tar -xvf lp_solve_5.5.2.0_Python_source.tar.gz
# change to nested directory and install bindings
cd lp_solve_55/extras/Python
sudo python setup.py install
```

Finally, install dependencies required for GUI usage:
```
# add epel repository for extra packages (python-pip and eventually zeromq)
sudo yum install epel-release 
# install python package manager (pip) and tkinter
sudo yum install python-pip tkinter
# install pillow module
sudo pip install pillow
```

#### Optional Installation

Dependencies required to cache results in a database:
 * Install [MongoDB server](https://docs.mongodb.org/manual/tutorial/install-mongodb-on-red-hat/) on one host.
 * Install PyMongo driver on every host: ``sudo pip install pymongo``

Dependencies required for distributed execution:
 * Install ZeroMQ library: ``sudo yum install zeromq zeromq-devel``
 * Install SCOOP module: ``sudo pip install scoop``

Password-less SSH (required for distributed computing using SCOOP) requires authorized keys on each remote machine with permissions following local security policies. This can be accomplished with the following steps:

```
cd ~
# generate a public/private key
ssh-keygen
# set permissions on .ssh directory and private key
chmod 700 .ssh
chmod 600 .ssh/id_rsa
# create file to store authorized keys and set permissions
touch authorized_keys
chmod 600 .ssh/authorized_keys
# authorize public key on remote machine at address RMT_ADDR (i.e. replace with address, e.g. 192.168.0.101)
cat .ssh/id_rsa.pub | ssh RMT_ADDR 'cat >> .ssh/authorized_keys'
```

You may also consider creating a ``.ssh/config`` file to save settings for hosts, addresses, user names, and ports:
```
Host host01
    HostName 192.168.0.100
    Port 22
    User testuser
Host host02
    HostName 192.168.0.101
    Port 22
    User testuser
```

Dependencies required for genetic algorithm execution:
* Install DEAP module: ``sudo pip install deap``

## Usage

### OFS Executable

The main OFS executable ``ofs.py`` runs one Orbital Federates simulation. Its basic syntax is:
```
python ofs.py <DESIGN...> [OPTION...]
```
where `DESIGN` specifies one or more space system elements and `OPTION` sets zero or more options.

Standard outputs return a list of initial cost-final value pairs (`:` delimiter) for each player separated by newlines, e.g.
```
1150.0:1500.0
1100.0:1700.0
```
for a two-player game specified with designs ``1.GroundSta@SUR1,pSGL 1.SmallSat@MEO6,pSGL,VIS 2.GroundSta@SUR2,pSGL 2.SmallSat@MEO1,pSGL,SAR`` and seed 0.

Each design is specified with the following syntax: ``P.SysType@LOC,SubType,...`` with
 * `P` = player number `{1, 2, ...}`
 * `SysType` = system type:
   * `GroundSta`: Ground station with capacity for 3 subsystem modules. Costs 500 to design and 0 to commission on the surface.
   * `SmallSat`: Satellite with capacity for 2 subsystem modules. Costs 200 to design and 0 commission in LEO, 100 to commission in MEO, and 200 to commission in GEO.
   * `MediumSat`: Satellite with capacity for 4 subsystem modules. Costs 300 to design and 0 commission in LEO, 150 to commission in MEO, and 300 to commission in GEO.
   * `LargeSat`: Satellite with capacity for 6 subsystem modules. Costs 400 to design and 0 commission in LEO, 200 to commission in MEO, and 400 to commission in GEO.
 * `LOC` = location:
   * `SUR1`-`SUR6`: Surface locations in sectors 1--6.
   * `LEO1`-`LEO6`: Low-Earth orbital locations above sectors 1--6. Spacecraft propagate 2 sectors per turn.
   * `MEO1`-`MEO6`: Medium-Earth orbital locations above sectors 1--6. Spacecraft propagate 1 sector per turn.
   * `GEO1`-`GEO6`: Geostationary Earth orbital locations above sectors 1--6. Spacecraft propagate 0 sectors per turn.
 * `SubType` = subsystem type:
   * `pSGL`: Proprietary space-to-ground link. Can transmit 1 bit of data between spacecraft and ground stations (same owner) per turn. Takes up 1 module and costs 50.
   * `oSGL`: Open space-to-ground link. Can transmit 1 bit of data between spacecraft and ground stations (any owner) per turn. Takes up 1 module and costs 100.
   * `pISL`: Proprietary inter-satellite link. Can transmit 1 bit of data between spacecraft (same owner) per turn. Takes up 1 module and costs 50.
   * `oISL`: Open inter-satellite link. Can transmit 1 bit of data between spacecraft (any owner) per turn. Takes up 1 module and costs 100.
   * `VIS`: Visual light sensor. Can sense and store 1 bit of visual light data per turn. Takes up 1 module and costs 250.
   * `SAR`: Synthetic aperture radar. Can sense and store 1 bit of radar data per turn. Takes up 1 module and costs 250.
   * `DAT`: Data storage unit. Can store 1 bit of data per turn. Takes up 1 module and costs 50.
   * `DEF`: Debris defense. Protects a spacecraft from debris events. Takes up 1 module and costs 100.

Options include the following flags (view with ``python ofs.py --help``):
 * `-d` or `--numTurns`: sets the simulation duration (number of turns), defaults to `24`
 * `-p` or `--numPlayers`: sets the number of players, defaults to `None` to interpret from designs
 * `-i` or `--initialCash`: sets the initial cash amount, defaults to `None` to adapt to initial designs
 * `-s` or `--seed`: sets the RNG seed, defaults to `0`
 * `-o` or `--ops`: sets the federate operational strategy from `{n,d}` for none (`n`) or centralized (`d`), defaults to `d6`
  * Additional centralized options set `dH` or `dH,s,i` where:
    * `H` is the planning horizon (default `6`)
    * `s` is the storage opportunity cost (default `100`; `a` estimates based on expected demand), and
    * `i` is the ISL opportunity cost (default `10`)
    * Defaults to `d6,100,10`
 * `-f` or `--fops`: sets the federation operational strategy from `{n,d,x}` for none (`n`), centralized (`d`), or opportunistic fixed-cost federated (`x`), defaults to `n`
  * Additional centralized options set `dH` or `dH,s,i` where:
    * `H` is the planning horizon (default `6`),
    * `s` is the storage opportunity cost (default `100`; `a` estimates based on expected demand), and
    * `i` is the ISL opportunity cost (default `10`)
    * Defaults to `d6,100,10` if selected
  * Additional federated options set `xG,I` or `xG,I,H,s,i` or `xH,s,i` where:
    * `G` is the fixed SGL service cost (default `50`),
    * `I` is the fixed ISL service cost (default `20`),
    * `H` is the planning horizon (default `6`),
    * `s` is the storage opportunity cost (default `100`; `a` estimates based on expected demand), and
    * `i` is the ISL opportunity cost (default `10`)
    * Defaults to `x50,20,6,100,10` if selected
 * `-l` or `--logging` sets the logging level among `{debug, info, warning, error}`, defaults to `error`
 * `-g` or `--gui` launches the graphical user interface where the spacebar advances time and escape resets the simulation


### OFS Batch Executable

The OFS executable ``ofs-exp.py`` runs a batch of Orbital Federates simulations as an experiment. Its basic syntax is:
```
python ofs-exp.py <EXPERIMENT> -s [START] -t [STOP] --dbHost [DBHOST] --dbPort [DBPORT] [OPTION...]
```
where `EXPERIMENT` specifies an experiment, either by name or by design specification. Hard-coded experiments include:
 * `bvc` - evaluates a symmetric 2-player tradespace of 530 designs using a centralized strategy
 * `bvc2` - evaluates a symmetric 2-player tradespace of 530 designs using a federated strategy
 * `bvc3` - evaluates a symmetric 2-player tradespace of 530 designs using an independent strategy
 * `masv` - evaluates a 2-player tradespace of 530x1 designs using a centralized strategy
 * `masv2` - evaluates a 2-player tradespace of 530x1 designs using a federated strategy
 
`START` and `STOP` set the first (inclusive) and last (exclusive) RNG seed values (defaults are `0` and `10`), and `DBHOST` and `DBPORT` set the MongoDB host and port number to cache results (default is `None` and `None`). Other options replicate those in `ofs.py` including `-d` or `--numTurns`, `-p` or `--numPlayers`, `-i` or `--initialCash`, `-o` or `--ops`, `-f` or `--fops`, and `-l` or `--logging` with same defaults.

Standard outputs return a JSON list of initial cost-final value pairs for each player with each seed separated by newlines, e.g.
```
[(1150.0, 1500.0), (1100.0, 1700.0)]
[(1200, 2100.0), (1100.0, 1650.0)]
```
for a two-player experiment with designs ``1.GroundSta@SUR1,pSGL 1.SmallSat@MEO6,pSGL,VIS 2.GroundSta@SUR2,pSGL 2.SmallSat@MEO1,pSGL,SAR`` and seeds between 0 (inclusive) and 2 (exclusive).

A batch experiment can be executed with SCOOP for distributed execution. For example, for multi-thread simulation use
```
python -m scoop ofs-exp.py <EXPERIMENT> -s [START] -t [STOP] --dbHost [DBHOST] --dbPort [DBPORT] [OPTION...]
```
or for multi-host simulation use
```
python -m scoop --hostfile hosts --python-interpreter python --path /path/to/ofspy/bin --external-hostname 192.168.0.100 ofs-exp.py <EXPERIMENT> -s [START] -t [STOP] --dbHost [DBHOST] --dbPort [DBPORT] [OPTION...]
```
where ``hosts`` is a text file specifying host names and number of processes, all hosts use a common interpreter `python` (may mask platform dependencies) and have a common path `/path/to/ofspy/bin` to the executable, and the primary host has external address `192.168.0.100`. All remote hosts must be accessible via password-less SSH from the central host and firewall rules must allow the required traffic. For more information, see the [SCOOP documentation](http://scoop.readthedocs.org/en/latest/usage.html).

Note that while the `DBHOST` and `DBPORT` arguments are optional for general experiments, the `bvc` and `masv` experiments require a database connection to save results for each design. Similarly, the post-processor introduced below queries results in a database.

### OFS Genetic Algorithm (GA) Executable
The OFS executable ``ofs-exp-ga.py`` executes a genetic algorithm experiment. It is separated due to configuration requirements of the GA library. Its basic syntax is:
```
python ofs-exp-ga.py -d [NUMTURNS] -o [OPS] -f [FOPS] -s [SEED] -N [NUMEXE] -g [NUMGEN] -n [MAXSATS] -c [MAXCOST] -x [PROBCROSS] -m [PROBMUTATE] -p [INITPOP] --dbHost [DBHOST] --dbPort [DBPORT]
```
where `NUMTURNS` sets the simulation duration (default 24), `OPS` and `FOPS` set the federate and federation strategies (defaults `n` and `d6,a,1`), `SEED` sets the initial RNG seed (default `0`), `NUMEXE` sets the number of executions per evaluation (default `10`), `NUMGEN` sets the number of population generations (default `20`), `MAXSATS` sets the maximum number of satellites per player (default `2`), `MAXCOST` sets the combined cost limit (default `4000`), `PROBCROSS` and `PROBMUTATE` set the probability of crossing and mutation in the GA (defaults `0.5` and `0.2`), `INITPOP` sets the initial population size (default `200`), and `DBHOST` and `DBPORT` set the database host and port.

### OFS Batch Post-Processor
The OFS executable ``ofs-exp-pp.py`` post-processes data from a batch experiment. Its basic syntax is:
```
python ofs-exp-pp.py <EXPERIMENT> --dbHost [DBHOST] --dbPort [DBPORT]
```
where `EXPERIMENT` specifies an experiment from `{bvc, bvc2, bvc3, bvcP, masv, masv2, ga}`. All experiments match the corresponding entry above, except for `bvcP` which combines results from `bvc`, `bvc2`, and `bvc3`.

## Acknowledgement

This project was funded by a MIT-Skoltech Faculty Development Plan (FDP) grant on Federated Satellite Systems (FSS). All source code is Copyright (c) 2015 Paul T. Grogan and Massachusetts Institute of Technology.

For more information on the FSS project, please see the following publications:
 * Grogan, P.T., K. Ho, A. Golkar, and O.L. de Weck, 2015. "Bounding the Value of Collaboration in Federated Systems," Working Paper.
 * Grogan, P.T. and O.L. de Weck, 2015. "Interactive Simulation Games to Assess Federated Satellite System Concepts", *2015 IEEE Aerospace Conference*, Big Sky, Montana.
 * Grogan, P.T., S. Shirasaka, A. Golkar, and O.L. de Weck, 2014. "Multi-stakeholder Interactive Simulation for Federated Satellite Systems", *2014 IEEE Aerospace Conference*, Big Sky, Montana.