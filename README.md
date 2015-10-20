#AUACM

Welcome to the Auburn ACM programming competition source code.

You're probably wondering how to set up your environment, so here we go:

##Mac

0. Install Homebrew 
    ``$ ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" ``

1. Install git
    ``brew install git ``

2. Clone the repo. (Or install git if you have not)

    ``git clone https://github.com/AuburnACM/AUACM.git ``

3. Navigate to ``/../AUACM/auacm/`` and set up your virtual environment.
Do this by executing the following commands: 

    ``$ pip install virtualenv``
  
    ``$ virtualenv flask``
    
    ``$ CFLAGS='-std=c99' ./flask/bin/pip install -r requirements.txt``

4. Install npm with

    ``$ brew install npm``
    
5. Install Bower with

    ``$ npm install -g bower``
    
6. Install local components using Bower

    ``$ bower install`` 

7. Now you can run the server on ``localhost:5000`` by running

    ``$ ./run.py``
    
More steps to come.

##Ubuntu

0. Install git
    
    ``$ sudo apt-get install git ``

1. Clone the repo.

    ``git clone https://github.com/AuburnACM/AUACM.git ``

2. Navigate to ``.../AUACM/auacm/`` and execute this to setup the environment:
    
    ``source ubuntu_setup.env``
    
    Follow all the setup instructions.

3. Now you can run the server on localhost:5000 by running
    ``$ ./run.py``


## Everyone

1. Navigate to the setup folder.

2. Copy data.zip to auacm/app/data.zip and extract the contents
   there. You should now have two folders inside auacm/app/data/,
   problems and submits.
   
# Need test solutions or competitions?
## We've got you covered.

1. Navigate to /setup in terminal and type

    ``$ chmod +x create_competition.sh``
    
    ``$ ./create_competition.sh <<< "Your Mock Mock Competition Name"``
     
2. When prompted for your passwords, simply enter them there. If you
   don't have one, just press enter.
   
3. Have fun with your Mock Mock Competition. All of the solitions
   should be located in the /testing/testSolutions folder.
