# puzzled-platypus

#### What?

Doing a qualitative reasoning project for the *Knowledge Representation* lecture
of the *Universiteit van Amsterdam*'s Master AI programme, winter term 2017/2018.

It models the inflow and outflow of water as well as the current volume of different, interconnected
containers.

#### How to?

To download the project from _GitHub_, use the following command:

    git clone https://github.com/Kaleidophon/puzzled-platypus.git

Afterwards, install the requirements for this project using _pip3_:

    cd puzzled-platypus
    pip3 install -r requirements.txt

You can now run the project. There are different way, the easiest being just
running the main module of the project with _Python3_, in which case the
minimal graph with verbosity setting 1 will be visualized:

    python3 visualization.py

You can also specify which state graph to visualize. The two options
are _minimal_ and _extra_. You can either use the _--graph_ or _-g_ flag
to do this:

    python3 visualization.py --graph minimal
    python3 visualization.py -g extra

You can also choose between four different verbosity setting using the numbers
between 0 and 4 with the _--verbose_ or _-v_ flag:

    python3 visualization.py --graph minimal -v 3
    python3 visualization.py --verbosity 1

 The different setting will have the following effects:


 | Verbosity value | Information displayed |
 | ---:| :--- |
 | 0 | No information |
 | 1 | Transition table & state table |
 | 2 | New-found transitions & states and everything from 1 |
 | 3 | Current state, stack size, current # of transitions and states, possible branches, rejected branches due to discontinuities and everything from 2 |

You can always get information about possible command line arguments using the flags _-h_ or _--help_.