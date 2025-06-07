set PROD := {1..7};
set MONTH := {1..6};
set MACH := {"Grind", "VDrill", "HDrill", "Borer", "Planer"};

set profit := {10, 6, 8, 4, 11, 9, 3};

set time[PROD][MACH] :=
  # PROD1 PROD2 PROD3 PROD4 PROD5 PROD6 PROD7
     <1, "Grind"> 0.5, <2, "Grind"> 0.7, <5, "Grind"> 0.3, <6, "Grind"> 0.2, <7, "Grind"> 0.5,
     <1, "VDrill"> 0.1, <2, "VDrill"> 0.2, <4, "VDrill"> 0.3, <6, "VDrill"> 0.6,
     <1, "HDrill"> 0.2, <3, "HDrill"> 0.8, <7, "HDrill"> 0.6,
     <1, "Borer"> 0.05, <2, "Borer"> 0.03, <4, "Borer"> 0.07, <5, "Borer"> 0.1, <7, "Borer"> 0.08,
     <3, "Planer"> 0.01, <5, "Planer"> 0.05, <7, "Planer"> 0.05;

set demand[PROD][MONTH] :=
  <1,1> 500, <2,1> 1000, <3,1> 300, <4,1> 300, <5,1> 800, <6,1> 200, <7,1> 100,
  <1,2> 600, <2,2> 500,  <3,2> 200, <5,2> 400, <6,2> 300, <7,2> 150,
  <1,3> 300, <2,3> 600,  <5,3> 500, <6,3> 400, <7,3> 100,
  <1,4> 200, <2,4> 300,  <3,4> 400, <4,4> 500, <5,4> 200, <7,4> 100,
  <2,5> 100, <3,5> 500,  <4,5> 100, <5,5> 1000, <6,5> 300,
  <1,6> 500, <2,6> 500,  <3,6> 100, <4,6> 300, <5,6> 1100, <6,6> 500, <7,6> 60;

set machine_count[MACH] := <"Grind"> 4, <"VDrill"> 2, <"HDrill"> 3, <"Borer"> 1, <"Planer"> 1;

set maintenance[MACH][MONTH] :=
  <"Grind", 1> 1,
  <"HDrill", 2> 2,
  <"Borer", 3> 1,
  <"VDrill", 4> 1,
  <"Grind", 5> 1, <"VDrill", 5> 1,
  <"Planer", 6> 1, <"HDrill", 6> 1;

param hours := 2 * 8 * 24;

var produce[PROD][MONTH] >= 0, integer;
var sell[PROD][MONTH] >= 0, integer;
var store[PROD][0..6] >= 0, <= 100, integer;

# Initial and final storage
subto initial_storage:
  forall p in PROD:
    store[p][0] = 0;

subto final_storage:
  forall p in PROD:
    store[p][6] = 50;

# Inventory flow
subto inventory_balance:
  forall <p, m> in PROD * MONTH:
    store[p][m-1] + produce[p][m] = sell[p][m] + store[p][m];

# Demand limit
subto demand_limit:
  forall <p, m> in PROD * MONTH:
    sell[p][m] <= demand[p][m];

# Machine capacity with maintenance
subto machine_capacity:
  forall <mach, m> in MACH * MONTH:
    sum<p in PROD> (if exists <p,mach> in time then produce[p][m] * time[p][mach] else 0) <=
      (machine_count[mach] - (if exists <mach,m> in maintenance then maintenance[mach][m] else 0)) * hours;

# Objective function: maximize profit
maximize total_profit:
  sum<p in PROD, m in MONTH> (sell[p][m] * profit[p]) -
  sum<p in PROD, m in MONTH> (store[p][m] * 0.5);
