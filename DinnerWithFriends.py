# This file implements a group forming problem called "Dinner with friends". The problem arises in Danish public schools
# where each class is encouraged to implement the "Dinner with friends" concept.
# The concept works as follows:
# A specific number of times a year (these are referred to as "events"), smaller groups are formed in the class.
# Each group should visit one from the group's home (the host) and dine there
# At each event, the groups are recreated, so that each kid meets as many of their classmates as possible during the
# year. This is to strengthen the "large social community" in the class, as the smaller communities consisting of good
# friends and cliques, will be formed anyway.
# The implemented model is based on the following rules
# (1) The aim is to have as many meeting between the kids as possible
# (2) Each kid should be in a group at each event
# (3) Each group should consist of at least minNumGuests and at most maxNumOfGuests
# (4) If a girl/boy is in a group, then at least 2 girls/boys must be placed in the group
# (5) If two kids are in the same group at an event, they cannot be the same group at the next event
# (6) Each kid must be the host at least once during the events
# (7) A kid cannot be the host two events in a row
# (8) A kid "i" can vist another kid "j"'s home at most once during the planning horizon
#
# Note, that the model does not have any "memory" in the sense that it cannot take its outset in "last year's plan"
# This means that, you might end up creating the same plan two years in a row (especially assuming you use the same
# computer and the same data-file as input).
# What you can do is to set the "shuffle_kids" entry in the data file to "true". This will randomize the order of the
# lists of boys and girls before building the model. Hence, different runs of the model will most likely result in
# different plans.

from ortools.sat.python import cp_model
import json as js
from math import ceil
from random import shuffle


class DinnerWithFriendsSolver:
    def __init__(self):
        self.model = None  # The CP model is stored in this member variable
        self.solver = None  # The solver is stored in this member variable
        self.meets = None  # meets[i, j] == 1 iff pupils i and j meet each other at least once during the events in E
        self.meetsAtE = None  # meetsAtE[i, j, e] = 1 if pupils i and j meet each other at event e
        self.meetsAtEInG = None  # meetsAtEInG[i, j, g, e] = 1 iff pupils i and j meets in group g at event e
        self.isInGroupAtE = None  # isInGroup[i, g, e] = 1 iff pupil i is in group g at event e
        self.groupInUse = None  # groupInUse[g,e] = 1 iff group number g is in use at event e
        self.visits = None  # visits[i,j,e] = 1 iff j visits i at event j
        self.groupInUse = None  # groupInUse[g, e] = 1 iff group number g is used at event e
        self.isHost = None  # isHost[i, e] = 1 iff kid i is host at event e
        self.status = None  # Status of the solver is stored in this variable
        self.Events = range(-1)  # Range storing the events: 0..numOfEvents - 1
        self.Kids = []  # List of all children in the class
        self.Groups = range(-1)  # Range of possible groups: 0..numGroups - 1
        self.Pairs = []  # List of all distinct pairs of children (i,j)
        self.Girls = []  # List of all girls in the class
        self.Boys = []  # List of all boys in the class
        self.numKids = 0  # Total number of kids in the class
        self.numGroups = 0  # Maximum number of groups available at each event
        self.minNumGuests = 0  # Minimum number of guests in a group
        self.maxNumGuests = 0  # Maximum number of guests in a group
        self.numOfEvents = 0  # Number of events in the planning horizon
        self.timeLimit = 0  # Sets a timelimit of the solver

    def readData(self, filename: str):
        # Read the data from the Json file
        with open(filename) as f:
            classData = js.load(f)
        # Copy data to class members
        self.Girls = classData['Girls']
        self.Boys = classData['Boys']
        if classData['shuffle_kids']:
            shuffle(self.Girls)
            shuffle(self.Boys)
        self.Kids = self.Girls + self.Boys
        self.numKids = len(self.Kids)
        self.minNumGuests = classData['minNumGuests']
        self.maxNumGuests = classData['maxNumGuests']
        self.numOfEvents = classData['numOfEvents']
        self.numGroups = ceil(self.numKids / self.minNumGuests)
        # Set ranges for Events and Groups
        self.Events = range(0, self.numOfEvents)
        self.Groups = range(0, self.numGroups)
        self.timeLimit = classData['timeLimitInSeconds']
        # Create all unique pairs of kids
        for i in range(0, len(self.Kids) - 1):
            for j in range(i + 1, len(self.Kids)):
                self.Pairs.append((self.Kids[i], self.Kids[j]))

    def initializeModel(self):
        # Initialize the constraint programming model object
        self.model = cp_model.CpModel()

    def createVariables(self):
        self.meets = {}  # meets[i, j] = 1 iff pupils i and j meet each other at least once during the events in E
        self.meetsAtE = {}  # meetsAtE[i, j, e] = 1 if pupils i and j meet each other at event e
        self.meetsAtEInG = {}  # meetsAtEInG[i, j, g, e] = 1 iff pupils i and j meets in group g at event e
        self.isInGroupAtE = {}  # isInGroup[i, g, e] = 1 iff pupil i is in group g at event e
        self.groupInUse = {}  # groupInUse[g, e] = 1 iff group number g is in use at event e
        self.visits = {}  # visits[i, j, e] = 1 iff j visits i at event e
        self.groupInUse = {}  # groupInUse[g, e] = 1 iff group number g is used at event e
        self.isHost = {}  # isHost[i, e] = 1 iff kid i is host at event e
        for (i, j) in self.Pairs:
            self.meets[(i, j)] = self.model.NewBoolVar('meets_' + str(i) + '_' + str(j))
            for e in self.Events:
                self.meetsAtE[(i, j, e)] = self.model.NewBoolVar('meetsAtE_' + str(i) + '_' + str(j) + '_' + str(e))
                for g in self.Groups:
                    self.meetsAtEInG[(i, j, g, e)] = self.model.NewBoolVar(
                        'meetsAtEInG' + str(i) + '_' + str(j) + '_' + str(g) + '_' + str(e)
                    )
        for i in self.Kids:
            for g in self.Groups:
                for e in self.Events:
                    self.isInGroupAtE[(i, g, e)] = self.model.NewBoolVar(
                        'isInGroupAtE' + str(i) + '_' + str(g) + '_' + str(e)
                    )
        for g in self.Groups:
            for e in self.Events:
                self.groupInUse[(g, e)] = self.model.NewBoolVar('groupInUse' + '_' + str(g) + '_' + str(e))

        for i in self.Kids:
            for j in self.Kids:
                for e in self.Events:
                    self.visits[(i, j, e)] = self.model.NewBoolVar(
                        'groupInUse' + '_' + str(i) + '_' + str(j) + '_' + str(e)
                    )
        for g in self.Groups:
            for e in self.Events:
                self.groupInUse[(g, e)] = self.model.NewIntVar(0, 1, 'z_' + str(g) + "_" + str(e))
        for e in self.Events:
            for i in self.Kids:
                self.isHost[(i, e)] = self.model.NewBoolVar('isHost_' + str(e) + '_' + str(i))

    def buildModel(self):
        # Add objective function to the model: Maximize number of pairings
        self.model.Maximize(sum(self.meets[i, j] for (i, j) in self.Pairs))
        # Add constraints saying each kid should go to a group at each event
        for i in self.Kids:
            for e in self.Events:
                self.model.Add(sum(self.isInGroupAtE[i, g, e] for g in self.Groups) == 1)
        # Ensure that each group at each event has no more than 'maxNumGuests' and no less than 'minNumGuests'
        # if the group is in use (groupInUse[g, e] = 1)
        for g in self.Groups:
            for e in self.Events:
                self.model.Add(
                    sum(self.isInGroupAtE[i, g, e] for i in self.Kids) <= self.maxNumGuests*self.groupInUse[g, e]
                )
                self.model.Add(
                    sum(self.isInGroupAtE[i, g, e] for i in self.Kids) >= self.minNumGuests*self.groupInUse[g, e]
                )
        # If one girl/boy in group, at least two girls/boys must be in the group
        for g in self.Groups:
            for e in self.Events:
                for j in self.Girls:
                    self.model.Add(sum(self.isInGroupAtE[i, g, e] for i in self.Girls) >= 2*self.isInGroupAtE[j, g, e])
                for j in self.Boys:
                    self.model.Add(sum(self.isInGroupAtE[i, g, e] for i in self.Boys) >= 2*self.isInGroupAtE[j, g, e])
        # Linearize relation isInGroupAtE[i,g,e] == isInGroupAtE[j,g,e] * meetsAtEInG[i,j,g,e]
        for (i, j) in self.Pairs:
            for g in self.Groups:
                for e in self.Events:
                    self.model.Add(self.meetsAtEInG[i, j, g, e] <= self.isInGroupAtE[i, g, e])
                    self.model.Add(self.meetsAtEInG[i, j, g, e] <= self.isInGroupAtE[j, g, e])
                    self.model.Add(
                        self.meetsAtEInG[i, j, g, e] >= self.isInGroupAtE[i, g, e] + self.isInGroupAtE[j, g, e] - 1
                    )
        # Enforce that if i and j meets at a group g at event e, then i and j meets at event e
        for (i, j) in self.Pairs:
            for e in self.Events:
                self.model.Add(self.meetsAtE[i, j, e] == sum(self.meetsAtEInG[i, j, g, e] for g in self.Groups))
        # Enforce, that i and j only meets at least once if there is an event where they meet
        for (i, j) in self.Pairs:
            self.model.Add(self.meets[i, j] <= sum(self.meetsAtE[i, j, e] for e in self.Events))
        # Use groups from the lower index end of the list
        for g in range(1, self.numGroups):
            for e in self.Events:
                self.model.Add(self.groupInUse[g, e] <= self.groupInUse[g - 1, e])
        # Enforce that each kid, at least once will be the host
        for i in self.Kids:
            self.model.Add(sum(self.isHost[i, e] for e in self.Events) >= 1)
        # Enforce that at each event, there is the same number of hosts as there is number of groups in use
        for e in self.Events:
            self.model.Add(sum(self.isHost[i, e] for i in self.Kids) == sum(self.groupInUse[g, e] for g in self.Groups))
        # Ensure, that there is at most one host in each group.
        # That is, i and j in same group, they cannot both be hosts
        for (i, j) in self.Pairs:
            for e in self.Events:
                self.model.Add(self.isHost[i, e] + self.isHost[j, e] <= 2 - self.meetsAtE[i, j, e])
        # Ensure no one is host in succeeding events:
        for e in self.Events:
            if e > 0:
                self.model.Add(self.isHost[i, e - 1] + self.isHost[i, e] <= 1)
        # Linearize the relation visits[i, j, e] = isHost[i, e] * meetsAtE[i, j, e] as the standard
        # visits[i, j, e] <= isHost[i, e], visits[i, j, e] <= meetsAtE[i, j, e], and
        # visits[i, j, e] >= isHost[i, e] + meetsAtE[i, j, e] - 1
        for e in self.Events:
            for i in self.Kids:
                for j in self.Kids:
                    self.model.Add(self.visits[i, j, e] <= self.isHost[i, e])
                    if (i,j) in self.Pairs:
                        self.model.Add(self.visits[i, j, e] <= self.meetsAtE[i, j, e])
                        self.model.Add(self.visits[i, j, e] >= self.isHost[i, e] + self.meetsAtE[i, j, e] - 1)
                    elif (j,i) in self.Pairs:
                        self.model.Add(self.visits[i, j, e] <= self.meetsAtE[j, i, e])
                        self.model.Add(self.visits[i, j, e] >= self.isHost[i, e] + self.meetsAtE[j, i, e] - 1)

    def solveModel(self):
        self.solver = cp_model.CpSolver()
        self.solver.parameters.max_time_in_seconds = self.timeLimit
        self.status = self.solver.Solve(self.model)
        print('Model is solved!')

    def printSolution(self):
        # Check if there is a solution available
        if self.status == cp_model.OPTIMAL or self.status == cp_model.FEASIBLE:
            # Print the number of pairings created
            print(f'Maximum of objective function: {self.solver.ObjectiveValue()} out of {len(self.Pairs)} possible\n')
            # For each event, print the plan. Mark the host with and asterix and with green color in the terminal
            print('Plans for the', self.numOfEvents, 'events follow:')
            for e in self.Events:
                print('Event number', e + 1)
                # Find hosts for this event
                groupNumber = 1
                for i in self.Kids:
                    if self.solver.Value(self.isHost[i, e]) >= 0.9999:
                        print('Group', str(groupNumber) + ':', i, 'is host for', end=': ')
                        groupNumber += 1
                        # Find the group number for kid i
                        thisGroupNumber = -1
                        for g in self.Groups:
                            if self.solver.Value(self.isInGroupAtE[i, g, e]) >= 0.9999:
                                thisGroupNumber = g
                                break
                        # Find all other kids in this group number at this event
                        for j in self.Kids:
                            if i != j and self.solver.Value(self.isInGroupAtE[j, thisGroupNumber, e]) >= 0.9999:
                                print(str(j) + ',', end=' ')
                        print('')
                print('====================================')

        else:
            print('No solution found.')

        # Statistics.
        print('\nSolution statistics')
        print(f'  status   : {self.solver.StatusName(self.status)}')
        print(f'  conflicts: {self.solver.NumConflicts()}')
        print(f'  branches : {self.solver.NumBranches()}')
        print(f'  wall time: {self.solver.WallTime()} s')

    def getPlan(self, filename: str):
        print('Reading data')
        self.readData(filename)
        print('Data read. Initializing model')
        self.initializeModel()
        print('Model initialize. Creating variables')
        self.createVariables()
        print('Variables created. Building model')
        self.buildModel()
        print('Model build. Starting to solve.', self.timeLimit, 'seconds allocated for solving')
        self.solveModel()
        self.printSolution()


if __name__ == '__main__':
    dwf = DinnerWithFriendsSolver()
    dwf.getPlan('exampleData.json')
