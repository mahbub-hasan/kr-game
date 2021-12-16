include "globals.mzn"; 

int: size;

%input validation for size 
constraint assert(size>0, "Value Error: Size cannot be negative and it's must be grater then zero");

%define row and col of the matrices
set of int: indices = 0..size-1;

%define array
var int: adjacentMatrixSize = 3;

array[1..size] of opt int: clue_h; %left clue
array[1..size] of opt int: clue_v; %top clue
array[indices, indices] of var bool: assign;



% constraint no more then 2 black cell in the row

constraint forall(i in indices)(
     count([assign[i,j] | j in indices],true) == 2
);


% constraint no more then 2 black cell in the col

constraint forall(j in indices)(
     count([assign[i,j] | i in indices],true) == 2   
);


% constraint adj must be white in a black cell

function var bool: adj(var int: rowIndex, var int: colIndex) = 
  forall(ai, aj in 0..adjacentMatrixSize-1)(
    let {var int: index_of_i = rowIndex + (ai - (adjacentMatrixSize div 2)),
         var int: index_of_j = colIndex + (aj - (adjacentMatrixSize div 2))} in 
     (index_of_i>=0 /\ index_of_i < size /\ index_of_j >= 0 /\ index_of_j < size /\ (index_of_i != rowIndex \/ index_of_j != colIndex)) -> not assign[index_of_i, index_of_j]
  );
  
constraint 
  forall(i, j in indices)(
    assign[i,j] -> adj(i,j)
  );
  

% gaps in row 
constraint forall(i,j1, j2 in indices where j1 < j2)(
  if(occurs(clue_h[i+1])) then
    assign[i,j1] /\ assign[i,j2] -> abs(j2-j1)-1==clue_h[i+1]
  else true endif
);

% gaps in col
constraint forall(j,i1,i2 in indices where i1 < i2)(
  if occurs(clue_v[j+1]) then
    assign[i1,j] /\ assign[i2,j] -> abs(i2-i1)-1==clue_v[j+1]
  else true endif
);


% solve satisfy
solve satisfy;

%output
output [
  if fix(assign[i,j]) then " B " 
  else if fix(not assign[i,j]) then " W " else " " endif 
  endif ++ if j==size-1 then "\n" else " " endif | 
  i in indices, j in indices
  
];


