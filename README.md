#Dinner with friends 

In Denmark a rather substantial amount of work and effort has gone into reducing bullying in the danish public schools (``Folkeskolen''). Many initiatives, which purposes are to strengthen the unity and solidarity in the individual classes, have been introduced - and this with remarkable results (see e.g. [this link at sdu.dk](https://www.sdu.dk/da/sif/ugens_tal/17_2019). 
	
One of these initiatives is the so-called ``Spis med venner'' (Dinner with friends) initiative. The idea is that the kids in a class should visit each other for dinner in small groups of four to five kids. These visits to each other's homes should happen a number of times during a year ( for example three times in the fall and three times in the spring) and each time the groups are different such that the kids get to visit and dine with as many of their class mates as possible. The reasoning behind the initiative is that you don't bully those with whom you have dined. And furthermore, this is an effective way to strengthen the bonds between the kids, leading to a more stable social community in the class.
	
However, for the parent untrained in combinatorial optimization and mathematical modeling, producing a plan for the visits, which makes the groups as diverse as possible each time, ensures that the same two kids do not go to the same dinner arrangement several times, that the hosts are not the same all the time and so forth is difficult! Really, difficult! Thus, this program is made to help the parents in charge of making the plans.
	
## The program and the logic behind it

This file `DinnerWithFriends.py` implements a group forming problem referred to as "Dinner with friends". 

The concept works as follows:
A specific number of times a year (these are referred to as "events"), smaller groups are formed in the class.
Each group should visit one from the group's home (the host) and dine there
At each event, the groups are recreated, so that each kid meets as many of their classmates as possible during the
year. This is to strengthen the "large social community" in the class, as the smaller communities consisting of good
friends and cliques, will be formed anyway.

The implemented model is based on the following rules

1. The aim is to have as many meetings between the kids as possible
2. Each kid should be in a group at each event
3. Each group should consist of at least `minNumGuests` and at most `maxNumOfGuests`
4. If a girl/boy is in a group, then at least 2 girls/boys must be placed in that group
5. If two kids are in the same group at an event, they cannot be the same group at the next event
6. Each kid must be the host at least once during the events
7. A kid cannot be the host two events in a row
8. A kid "i" can vist another kid "j"'s home at most once during the planning horizon

Note, that the model does not have any "memory" in the sense that it cannot take its outset in "last year's plan".
This means that you might end up creating the same plan two years in a row (especially if it is assumed that you use the same
computer and the same data-file as input).
What you can do is to set the "shuffle_kids" entry in the data file to "true". This will randomize the order of the
lists of boys and girls before building the model. Hence, different runs of the model will most likely result in
different plans.

In `main.py` a simple exmple showing how to use the code is implemented. A data example is provided in the file `exampleData.json` and this file is read using the function implemented in `readAndWriteJson.py`.

The format of the data file is as follows

``
    "Girls": [List of names for the girls in the class],
    "Boys": [List of names for the boys in the class],
    "numOfEvents": integer specifying the number of events that should be planned,
    "minNumGuests": integer specifying the minimum number of kids in each group,
    "maxNumGuests": integer specifying the maximum number of kids in each group,
    "timeLimitInSeconds" : float spefifying the number of seconds which should be allocated to the solution,
    "shuffle_kids" : boolean spcifying whether the lists of boys and girls should be shuffled before building the model
``

## Mathmatical model

Here, a mathematical description of the model is given. First we define sets and parameters, next the variables, the objective funciton, and finally we provide the consrtaints. This section is concluded with a full description of the model.

### Sets and parameters

$$
\\begin{align}
  G=&\text{List of names for the girls in the class}\\
  B=&\text{List of names for the boys in the class}\\
  P=& G\cup B\\
  \Pi=& \text{List of all ordered pairs of kids}\\
  E=& \text{All events}\\
  u=& \text{maximum number of kids in a group}\\
  l=& \text{minimum number of kids in a group}
\\end{align}

### Variables

$$
\\begin{align}
  x_i^{ge} &=\begin{cases}1&\text{if kid $i$ is in group $g$ at event $e$}\\\ 0,&\text{otherwise} \end{cases}\\
  \tilde{x}_{ij}^{ge} &=\begin{cases}1&\text{if kids $i$ and $j$ are in group $g$ at event $e$}\\\ 0,&\text{otherwise} \end{cases}\\
  {y}_{ij}^{e} &=\begin{cases}1&\text{if kids $i$ and $j$ are in the same group at event $e$}\\\ 0,&\text{otherwise} \end{cases}\\
  \tilde{y}_{ij} &=\begin{cases}1&\text{if kids $i$ and $j$ meet each other at least once}\\\ 0,&\text{otherwise} \end{cases}\\
  z_{ge} &=\begin{cases}1&\text{if group $g$ is used at event $e$}\\\ 0,&\text{otherwise} \end{cases}\\
  \alpha_{ij}^e&=\begin{cases}1&\text{if kid $j$ visits kid $i$'s home at event $e$}\\\ 0,&\text{otherwise} \end{cases}
\end{align}
$$
$$
