set PRODUCTS := {1..7};
set MONTHS := {1..6};
set MACHINES := {1..5};

param profit[PRODUCTS] := <1> 10, <2> 6, <3> 8, <4> 4, <5> 11, <6> 9, <7> 3;

param grinding[PRODUCTS] :=
  <1> 0.5, <2> 0.7, <3> 0.0, <4> 0.0, <5> 0.3, <6> 0.2, <7> 0.5;

param vdrill[PRODUCTS] :=
  <1> 0.1, <2> 0.2, <3> 0.0, <4> 0.3, <5> 0.0, <6> 0.6, <7> 0.0;

param hdrill[PRODUCTS] :=
  <1> 0.2, <2> 0.0, <3> 0.8, <4> 0.0, <5> 0.0, <6> 0.0, <7> 0.6;

param milling[PRODUCTS] :=
  <1> 0.05, <2> 0.03, <3> 0.0, <4> 0.07, <5> 0.1, <6> 0.0, <7> 0.08;

param planing[PRODUCTS] :=
  <1> 0.0, <2> 0.0, <3> 0.01, <4> 0.0, <5> 0.05, <6> 0.0, <7> 0.05;


param demand[MONTHS * PRODUCTS] :=
  <1,1> 500,   <1,2> 1000, <1,3> 300, <1,4> 300, <1,5> 800, <1,6> 200, <1,7> 100,
  <2,1> 600,   <2,2>  500, <2,3> 200, <2,4>   0, <2,5> 400, <2,6> 300, <2,7> 150,
  <3,1> 300,   <3,2>  600, <3,3>   0, <3,4>   0, <3,5> 500, <3,6> 400, <3,7> 100,
  <4,1> 200,   <4,2>  300, <4,3> 400, <4,4> 500, <4,5> 200, <4,6>   0, <4,7> 100,
  <5,1>   0,   <5,2>  100, <5,3> 500, <5,4> 100, <5,5>1000, <5,6> 300, <5,7>   0,
  <6,1> 500,   <6,2>  500, <6,3> 100, <6,4> 300, <6,5>1100, <6,6> 500, <6,7>  60;

param maint_grind[MONTHS] :=
  <1> 1, <2> 0, <3> 0, <4> 0, <5> 1, <6> 0;

param maint_vdrill[MONTHS] :=
  <1> 0, <2> 0, <3> 0, <4> 1, <5> 1, <6> 0;

param maint_hdrill[MONTHS] :=
  <1> 0, <2> 2, <3> 0, <4> 0, <5> 0, <6> 1;

param maint_milling[MONTHS] :=
  <1> 0, <2> 0, <3> 1, <4> 0, <5> 0, <6> 0;

param maint_planing[MONTHS] :=
  <1> 0, <2> 0, <3> 0, <4> 0, <5> 0, <6> 1;

param max_stock := 100;
param end_stock := 50;
param storage_cost := 0.5;

param hours_per_month := 2 * 8 * 24;

param machine[MACHINES] := 
  <1> 4, <2> 2, <3> 3, <4> 1, <5> 1;

var produce[MONTHS * PRODUCTS] integer >= 0;
var sell[MONTHS * PRODUCTS] integer >= 0;
var stock[MONTHS * PRODUCTS] integer <= max_stock;

maximize profit_total:
  sum <m,p> in MONTHS * PRODUCTS: profit[p] * sell[m,p] - sum <m,p> in MONTHS * PRODUCTS: storage_cost * stock[m,p];

subto inventory_balance_initial:
  forall <p> in PRODUCTS:
    stock[1,p] == produce[1,p] - sell[1,p];

subto inventory_balance:
  forall <m,p> in (MONTHS \ {1}) * PRODUCTS:
    stock[m,p] == stock[m-1,p] + produce[m,p] - sell[m,p];

subto final_stock:
  forall <p> in PRODUCTS:
    stock[6,p] == end_stock;

subto demand_limit:
  forall <m,p> in MONTHS * PRODUCTS:
    sell[m,p] <= demand[m,p];

subto grinding_capacity:
  forall <m> in MONTHS:
    sum <p> in PRODUCTS:
      grinding[p] * produce[m,p] <= (machine[1] - maint_grind[m]) * hours_per_month;

subto vdrill_capacity:
  forall <m> in MONTHS:
    sum <p> in PRODUCTS:
      vdrill[p] * produce[m,p] <= (machine[2] - maint_vdrill[m]) * hours_per_month;

subto hdrill_capacity:
  forall <m> in MONTHS:
    sum <p> in PRODUCTS:
      hdrill[p] * produce[m,p] <= (machine[3] - maint_hdrill[m]) * hours_per_month;

subto milling_capacity:
  forall <m> in MONTHS:
    sum <p> in PRODUCTS:
      milling[p] * produce[m,p] <= (machine[4] - maint_milling[m]) * hours_per_month;

subto planing_capacity:
  forall <m> in MONTHS:
    sum <p> in PRODUCTS:
      planing[p] * produce[m,p] <= (machine[5] - maint_planing[m]) * hours_per_month;
