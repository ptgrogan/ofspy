# ofspy: Orbital Federates Simulation - Python

## Introduction

This project develops an integrated simulation for Orbital Federates, a simplified model of Federated Satellite Systems (FSS). It demonstrates a multi-actor system value model by mapping input design decisions to initial cost and total value measured by revenue accumulated over a system lifecycle.

## Installation

This package requires two dependencies: Gurobi and Tkinter. The easiest way to use `ofspy` is via [Anaconda](https://www.continuum.io/downloads), a Python distribution which bundles many of the most useful packages including Tkinter and makes it easy to install [Gurobi](http://www.gurobi.com/downloads/get-anaconda).

Gurobi is a commercial optimization library with bindings for Python with a free license available for academic use. [Download and install](http://www.gurobi.com/downloads/get-anaconda) the Anaconda distribution for Python 2.7 for your machine. Follow the instructions above to install Gurobi into Anaconda and install a Gurobi license.

Once the dependencies are set, you can configure the path variables by running (from a command or terminal window) at the root of the project:
```shell
pip install -e .
```

## Usage

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

## Acknowledgement

This project was funded in part by a MIT-Skoltech Faculty Development Plan (FDP) grant on Federated Satellite Systems (FSS) with Massachusetts Institute of Technology. Source code is Copyright (c) 2015-2019 Paul T. Grogan.

For more information on the FSS project, please see the following publications:
 * Grogan, P.T., K. Ho, A. Golkar, and O.L. de Weck, 2016. "Multi-actor Value Modeling for Federated Systems," *IEEE Systems Journal*, vol. 12, no. 2, pp. 1193-1202.
 * Grogan, P.T., K. Ho, A. Golkar, and O.L. de Weck, 2015. "Bounding the Value of Collaboration in Federated Systems," IEEE Systems Conference, Orlando, FL.
 * Grogan, P.T. and O.L. de Weck, 2015. "Interactive Simulation Games to Assess Federated Satellite System Concepts", *2015 IEEE Aerospace Conference*, Big Sky, Montana.
 * Grogan, P.T., S. Shirasaka, A. Golkar, and O.L. de Weck, 2014. "Multi-stakeholder Interactive Simulation for Federated Satellite Systems", *2014 IEEE Aerospace Conference*, Big Sky, Montana.
