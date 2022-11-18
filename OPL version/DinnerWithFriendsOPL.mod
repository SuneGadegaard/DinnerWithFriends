/*********************************************
 * OPL model for the "Dinner with friends" problem
 * Author: Sune Lauth Gadegaard
 * Updated last : November 18, 2022
 *********************************************/

using CP; // Use the constraint programming solver

tuple pair // A pair of pupils
{
  string p1;
  string p2;
}

{string} Girls = ...;   // Set of girls in the class
{string} Boys = ...;    // Set of boys in the class
{string} Pupils = Girls union Boys; // All pupils in the class
int numOfStudents = card ( Pupils ); // Number of pupils in class
int numOfEvents = ...;  // Number of times the dinner with friends should happen
int minNumGuests = ...; // Minimum number of pupils in a group
int maxNumGuests = ...; // Maksimum number of pupils in a group
range Events = 1..numOfEvents; // Range over all events

string firstGirl = first ( Girls); // First girls in class. Used to break a bit of symmetry

{pair} pupPairs = {<i,j> | ordered i,j in Pupils}; // All unique pairs of pupils in the class

int numOfGroups = ftoi ( ceil ( card(Pupils) / minNumGuests ) ); // number of potential groups 
range Groups = 1..numOfGroups; // Range over all groups

//Set a time limit on the solution process (in seconds)
execute
{
   cp.param.timelimit = 600;
}


// Decision variables used in the model
dvar int+ x[Pupils][Events] in 1..numOfGroups;  // x[j][e]=g if pupil j is in group g at event e
dvar boolean y[pupPairs];                       // y[i][j] = 1 if pupils i and j meet each other during at least one of the events
dvar boolean z[Groups][Events];                 // z[g][e] = 1 iff group g is in use at event e
dvar boolean beta[Events][Pupils];              // beta[e][i] = 1 iff pupil i is a host at event e


// Decision expressions used to ease modelling
dexpr int meetings[i in Pupils ] = sum ( p in pupPairs : p.p1==i || p.p2==i ) y[p]; // meetings[i] totale number of classmates met by pupil i
dvar int minMeetings in 0..numOfStudents-1;// Equals the number of meetings for the pupil who meets fewest of their classmates
dexpr int totalMeetings = sum ( p in pupPairs ) y[p];  // Total number of meetings created in the class


// Break some symmetry by placing "firstGirl" in group 1 all the time
execute break_some_symmetry
{
  for ( var e in Events )
  {
    x[firstGirl][e].UB = 1;
  }
}

// Maximize total number of meetings in the class
//maximize totalMeetings;

// Maximize the number of meetings for the pupil who meets the fewest
 	maximize minMeetings ;

// Constraint section starts here:
subject to
{
  // Make sure the totalMeetings and minMeetings are referenced
  totalMeetings >= 0;
  minMeetings >= 0;

  // Definition of the "minMeetings"-variable. If this variable is maximized, it will equal the smallest of the meetings[i]-variables
  // Hence, it will equal min_{i\in elever}meetings[i] in an optimal solution
  forall ( i in Pupils ) minMeetings <= meetings[i];
  
  // Group composition rules
  forall (e in Events, g in Groups ) 
  {
    // No more than maxNumGuests in each group
    sum ( j in Pupils ) ( x[j][e] == g ) <= maxNumGuests*z[g][e];
    // No les than minNumGuests in each group
    sum ( j in Pupils ) ( x[j][e] == g ) >= minNumGuests*z[g][e];
  }
  
  // If there is one girl in a group, then there should be at least two
  forall ( e in Events, g in Groups )
  {
    sum ( i in Girls ) (x[i][e]==g)>=1 => sum ( i in Girls ) (x[i][e]==g)>=2;
  }
  // If there is one boy in a group, then there should be at least two
  forall ( e in Events, g in Groups )
  {
    sum ( i in Boys ) (x[i][e]==g)>=1 => sum ( i in Boys ) (x[i][e]==g)>=2;
  }

  // These two constraints could also be formulated as follows:
  //forall ( i in Girls, g in Groups, e in Events  )
  //{
  //	sum ( j in Girls ) (x[j][e] == g) >= 2*(x[i][e]==g);
  //}
  // and
  //forall ( i in Boys, g in Groups, e in Events  )
  //{
  //  sum ( j in Boys ) (x[j][e] == g) >= 2*(x[i][e]==g);
  //}
  
    
  // If pupils i and j are in the same group at event e ( x[i][e] == x[j][e] )
  // then they cannot be in the same group at the next event (event e+1) ( x[i][e+1] != x[j][e+1] )
  forall (e in Events , i,j in Pupils : (e != numOfEvents) &&  (i!=j) )
  {
    x[i][e]==x[j][e] => x[i][e+1]!=x[j][e+1];
  }
    
  // Definition of the y[p]-variables for at pair p
  forall ( p in pupPairs )
  {
    // If there exists at least one event where the pair p=(i,j) are in the same group, then y[p] can take a value of one
    sum ( e in Events ) ( x[p.p1][e] == x[p.p2][e] ) >= y[p];
  }
  
  // Ensure we use the groups with lowest index first. Not necessary, but may help
  forall ( e in Events, g in Groups : g!=numOfGroups )
  {
    z[g][e]>=z[g+1][e];
  }    

  // Definition of the beta-variables
  forall ( j in Pupils )
  {
    // Each pupil i should try to be host at least once
    sum ( e in Events ) beta[e][j] >=1;
        
    //If pupils i and j are in the same group at event e, then at most one of them can be a host
    forall ( e in Events, i in Pupils : i!=j )
    {
      x[i][e]==x[j][e] => beta[e][i] + beta[e][j] <= 1;
    }
  }
  
  // At each event, there shold be as many hosts as there are groups in use
  forall ( e in Events )
  {
    sum ( j in Pupils ) beta[e][j] == sum ( g in Groups ) z[g][e];  
  }
  
  // If pupil i is a host at event e, then pupil i cannot be the host at event e+1 (for the sake of the parents)
  forall ( i in Pupils , e in Events : e < numOfEvents )
  {
    beta[e][i] + beta[e+1][i] <= 1;
  }

  // Pupil j can visit pupil i at most once during the planning horizon.
  // Notem that if x[i][e]==x[j][e], and beta[e][i]=1 then i and j will be in the same group, and i will be host.
  // Hence, j visits i's house. 
  forall (  i,j in Pupils : i!=j )
    {
       sum ( e in Events ) (  ( x[i][e]==x[j][e]) + beta[e][i] == 2 ) <= 1;
    } 

}




// Print out the plans to a file called "SolutionFile.txt"
execute
{
  var outfile = new IloOplOutputFile("SolutionFile.txt");
  for ( var e in thisOplModel.Events )
  {
    outfile.writeln ( "Arrangement number ", e);
      // Find the hosts for the event e
      for ( var i in thisOplModel.Pupils )
      {
        if ( thisOplModel.beta[e][i] >= 0.5 )
        {
          outfile.write ( "Host: " , i,"\t Guests : ");
          var thisGroup = thisOplModel.x[i][e];
          // Find the others in the same group
          for ( var j in thisOplModel.Pupils )
          {
            if ( thisOplModel.x[j][e] == thisGroup && j!=i )
            {
              outfile.write ( j,", ");
            }
          }
        outfile.write ("\n");
      }        
    }
    outfile.writeln ("--------------------------------------------------");
  }
  
  // Print some info about the solution to the file as well  
  var minNumMeetings = thisOplModel.numOfStudents;
  for ( var i in thisOplModel.Pupils )
  {
    outfile.writeln ( i, " møder ", thisOplModel.meetings[i] , " andre i løbet af året" );
    if ( thisOplModel.meetings[i] <  minNumMeetings ) minNumMeetings = thisOplModel.meetings[i];
  }
  outfile.writeln ( "Totale meeting number of meetings : " , thisOplModel.totalMeetings );
  outfile.writeln ( "Smallest number of meetings       : " , minNumMeetings );
}


 