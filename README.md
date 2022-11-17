# Dinner with friends 

In Denmark a rather substantial amount of work and effort has gone into reducing bullying in the danish public schools ("Folkeskolen"). Many initiatives, which purposes are to strengthen the unity and solidarity in the individual classes, have been introduced - and this with remarkable results (see e.g. [this link at sdu.dk](https://www.sdu.dk/da/sif/ugens_tal/17_2019)). 
	
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

In `main.py` a simple exmple showing how to use the code is implemented. A data example is provided in the file `exampleData.json` and this file is read using functionality from the `json`library.

The format of the data file is as follows

```
"Girls": [List of names for the girls in the class],
"Boys": [List of names for the boys in the class],
"numOfEvents": integer specifying the number of events that should be planned,
"minNumGuests": integer specifying the minimum number of kids in each group,
"maxNumGuests": integer specifying the maximum number of kids in each group,
"timeLimitInSeconds" : float spefifying the number of seconds which should be allocated to the solution,
"shuffle_kids" : boolean spcifying whether the lists of boys and girls should be shuffled before building the model
```

## Mathematical model

Here, a mathematical description of the model is given. First we define sets and parameters, next the variables, the objective funciton, and finally we provide the consrtaints. This section is concluded with a full description of the model.

### Sets and parameters

$$
\\begin{align}
  G =& \text{List of names for the girls in the class}\\
  B =& \text{List of names for the boys in the class}\\
  P =& G\cup B\\
  \Pi =& \text{List of all ordered pairs of kids}\\
  E =& \text{All events}\\
  K =& \text{All possible groups}\\
  u =& \text{maximum number of kids in a group}\\
  l =& \text{minimum number of kids in a group}
\\end{align}
$$

### Variables

$$
\\begin{align}
  x_i^{ge} &=\begin{cases}1&\text{if kid $i$ is in group $g$ at event $e$}\\\ 0,&\text{otherwise} \end{cases}\\
  \tilde{x} _{ij}^{ge} &=\begin{cases}1&\text{if kids $i$ and $j$ are in group $g$ at event $e$}\\\ 0,&\text{otherwise} \end{cases}\\
  {y} _{ij}^{e} &=\begin{cases}1&\text{if kids $i$ and $j$ are in the same group at event $e$}\\\ 0,&\text{otherwise} \end{cases}\\
  \tilde{y} _{ij} &=\begin{cases}1&\text{if kids $i$ and $j$ meet each other at least once}\\\ 0,&\text{otherwise} \end{cases}\\
  z _{ge} &=\begin{cases}1&\text{if group $g$ is used at event $e$}\\\ 0,&\text{otherwise} \end{cases}\\
  \alpha _{ij}^e&=\begin{cases}1&\text{if kid $j$ visits kid $i$'s home at event $e$}\\\ 0,&\text{otherwise} \end{cases}\\
  \beta _{i}^e&=\begin{cases}1&\text{if kid $i$ is one of the hosts at event $e$}\\\ 0,&\text{otherwise} \end{cases}
\end{align}
$$

### Objective function

$$
\begin{equation}
  \max \sum_{ (i,j) \in \Pi } \tilde{y}  _{ij}
\end{equation}
$$

### Constraints

Here all constraints are formulated and described. First of all, the model should ensure that each kids $i\in P$ is in exactly one group at each event.
This is ensured by the constraints

$$
\begin{align}
  &\sum _{g \in K} x_i^{ge} = 1,&& \forall i\in P, e\in E
\end{align}
$$

Next, we ensure that at most $u$ and at least $l$ kids are in each utilized group:

$$
\begin{align}
  &\sum_{i \in P} x_i^{ge} \leq uz_{ge}, &&\forall g\in K, e\in E\\
  &\sum_{i \in P} x_i^{ge} \geq uz_{ge}, &&\forall g\in K, e\in E
\end{align}
$$

The next rule to enforce is the "if one girl/boy in a group, then at least two gilrs/boys in the group". This can be done using the following linear constraints

$$
\begin{align}
  &\sum_{i \in G} x_i^{ge} \geq 2x_j^{ge},	&& \forall j\in G, e\in E, g\in K\\
  &\sum_{i \in B} x_i^{ge} \geq 2x_j^{ge},	&& \forall j\in B, e\in E, g\in K
\end{align}
$$

Now we formulate the logic linking the $x_i^{ge}$ and $x_{ij}^{ge}$ variables. Note, that $x_{ij}^{ge}=x_i^{ge}x_j^{ge}$ stating the $x_{ij}^{ge}$ equals 
one, only if both $x_i^{ge}$ and $x_j^{ge}$ equals one. To formulate this as linear relations, the standard linearization of a product of binary variables
is used

$$
\begin{align}
  &x_{ij}^{ge} \leq x_i^{ge},	&& \forall (i,j)\in \Pi, g\in K, e\in E\\
  &x_{ij}^{ge} \leq x_j^{ge},	&& \forall (i,j)\in \Pi, g\in K, e\in E\\
  &x_{ij}^{ge} \geq x_i^{ge}+x_j^{ge}-1,	&& \forall (i,j)\in \Pi, g\in K, e\in E
\end{align}
$$

The next step is to link the $x_{ij}^{ge}$-variables to the $y_{ij}^e$-variables. Note here, that kids $i$ and $j$ meet each other at event $e$ 
$(y_{ij}^e=1)$ if at least one $x_{ij}^{ge}$ equals one for the pair $(i,j)$ and the event $e$. Hence, we have

$$
\begin{align}
  &y_{ij}^e=\sum_{g \in K} x_{ij}^{ge},&&\forall (i,j)\in \Pi, e\in E
\end{align}
$$

The equality is given by the fact that $i$ and $j$ cannot meet each other in *more* than one group. Hence the right hand side sum is either equal to $ or 0.

Next, we enforce final definition of the $\tilde{y} _{ij}$ variables. Since $\tilde{y} _{ij}$ should only be allowed to take the value of one if there exists an event $e$ where kids $i$ and $j$ meet, we have the relation

$$
\begin{align}
  &\tilde{y} _{ij}\leq \sum _{e \in E} y _{ij}^e , && \forall (i,j) \in \Pi
\end{align}
$$

THe next part of the model, focuses on the practical rules for a feasible solution. First, the rule that kids $i$ and $j$ cannot meet each other at two consecutive events is modelled as 

$$
\begin{align}
  &y_{ij}^e + y_{ij}^{e+1} \leq 1, &&\forall (i,j)\in \Pi, e\in E: e\neq \vert E\vert 
\end{align}
$$

Next, the rule that each kid $i$ should be the host at an event at least once is modelled as

$$
\begin{align}
  &\sum_{e\in E} \beta_i^e \geq 1, && \forall i\in P
\end{align}
$$

As there should be as many hosts at event $e$ as there are groups in use, we require that
$$
\begin{align}
  &\sum_{i \in P} \beta_i^e = \sum_{g\in K} z_{ge}, && \forall e\in E
\end{align}
$$
This is however not enough to enforce the logic, as there my now be two hosts in the same group and no host in another group, which is rather meaningless. Hence, we enforce that if kids $i$ and $j$ are in the same group, they cannot both be hosts

$$
\begin{align}
  & \beta_i^e + \beta_j^e \leq 2 - y_{ij}^e,&& \forall (i,j)\in \Pi, e\in E
\end{align}
$$

It should also be the case, that a kid $i$ cannot be the host at two consecutive events, hence constraints 

$$
\begin{align}
  & \beta_i^e + \beta_i^{e+1}\leq 1, && \forall i \in P, e\in E
\end{align}
$$

must be included as well.

The last part of the model concerns the definition of the $\alpha_{ij}^e$-variables. Note that $\alpha_{ij}^e=1$ if and only if pupil $j$ visits pupil $i$'s home at event $e$. This means that $\alpha_{ij}^e=1$ if and only if $i$ and $j$ meets each other at event $e$ $(y_{ij}^e=1)$ *and* $i$ is the host at that event $(\beta_i^e=1)$. Hence, $\alpha_{ij}^e= y_{ij}^e \beta_i^e$. Again the standard linearization of a product of binary variables is used to arrived at constraints

$$
\begin{align}
  & \alpha_{ij}^e \leq \beta_i^e, &&\forall i,j \in P, e\in E,\\
  & \alpha_{ij}^e \leq y_{ij}^e, && \forall i,j\in P, e\in E\\
  & \alpha{ij}^e \geq y_{ij}^e + \beta_i^e - 1, && \forall i,j\in P, e\in E\\
\end{align}
$$

Finally, it should be ensured that pupil $j$ visits pupil $i$ at least once:

$$
\begin{align}
  & \sum_{e \in E} \alpha_{ij}^e \leq 1, &&\forall i,j\in P
\end{align}
$$

### The full model

The full linear integer programming model is then described as follows 

$$
\begin{align}
  \max		&\sum_{ (i,j) \in \Pi } \tilde{y}  _ {ij}\\
  \text{s.t.:}	&\sum _ {g \in K} x _ i^{ge} = 1,&& \forall i\in P, e\in E \\
  		&\sum _ {i \in P} x _ i^{ge} \leq uz_{ge}, &&\forall g\in K, e\in E\\
  		&\sum _ {i \in P} x _ i^{ge} \geq uz_{ge}, &&\forall g\in K, e\in E\\
		&\sum _ {i \in G} x _ i^{ge} \geq 2x_j^{ge},	&& \forall j\in G, e\in E, g\in K\\
		&\sum _ {i \in B} x _ i^{ge} \geq 2x_j^{ge},	&& \forall j\in B, e\in E, g\in K\\
		&x_{ij}^{ge} \leq x_i^{ge},	&& \forall (i,j)\in \Pi, g\in K, e\in E\\
		&x_{ij}^{ge} \leq x_j^{ge},	&& \forall (i,j)\in \Pi, g\in K, e\in E\\
		&x_{ij}^{ge} \geq x_i^{ge}+x_j^{ge}-1,	&& \forall (i,j)\in \Pi, g\in K, e\in E\\
		&y_{ij}^e=\sum_{g \in K} x_{ij}^{ge},&&\forall (i,j)\in \Pi, e\in E\\
		&\tilde{y} _ {ij} \leq \sum _ {e \in E} y _ {ij} ^ e , && \forall (i,j) \in \Pi\\
		&y_{ij}^e + y_{ij}^{e+1} \leq 1, &&\forall (i,j)\in \Pi, e\in E: e\neq \vert E\vert \\
		&\sum_{e\in E} \beta_i^e \geq 1, && \forall i\in P\\
		&\sum_{i \in P} \beta_i^e = \sum_{g\in K} z_{ge}, && \forall e\in E\\
		&\beta_i^e + \beta_j^e \leq 2 - y_{ij}^e,&& \forall (i,j)\in \Pi, e\in E\\
		&\beta_i^e + \beta_i^{e+1}\leq 1, && \forall i \in P, e\in E\\
		&\alpha_{ij}^e \leq \beta_i^e, &&\forall i,j \in P, e\in E,\\
		&\alpha _{ij}^e \leq y _{ij}^e, && \forall i,j\in P, e\in E\\
		&\alpha _{ij}^e\geq y _{ij} ^e + \beta_i^e - 1, && \forall i,j\in P, e\in E\\
		&\sum_{e \in E} \alpha _{ij}^e \leq 1, &&\forall i,j\in P\\
		&\text{all variables are binary}
\end{align}
$$

