set PRACOWNICY	:= {"A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N"};
set ATRYBUTY	:= {"Koordynator", "Umowa zlecenie", "Max dyżury", "Nadwyżka"};

set DNI			:= {1..30};
set SOBOTY		:= {3..max(DNI) by 7};
set NIEDZIELE	:= {4..max(DNI) by 7};
set SWIETA		:= {8};
set DNI_WOLNE	:= NIEDZIELE + SWIETA;
set ZMIANY		:= {"D", "N"};
set TYGODNIE_POCZATEK := {1..31 by 7};

# w weekend i święta musi być MIN 4 pracowników
param min_prac_weekend := 4;
# w dzień powszedni musi być od 3 do 4 pracowników
param min_prac_roboczy := 3;
param max_prac_roboczy := 4;
# normy czasu pracy
param zmiana := 12; # h
param tydzien := 36; # h
param miesiac := 159.25; # h


param dane_pracownikow[PRACOWNICY * ATRYBUTY] := 
			|"Koordynator"	,"Umowa zlecenie"	,"Max dyżury"	,"Nadwyżka"	|
|"A" 		| 1				, 0					, 999			, -3.33		|
|"B"		| 1				, 0					, 999			,  8.67		|
|"C"		| 0				, 0					, 999			, -3.33		|
|"D"		| 0				, 0					, 999			,  8.67		|
|"E"		| 1				, 0					, 999			,  8.67		|
|"F"		| 0				, 0					, 999			,  8.67		|
|"G"		| 1				, 0					, 999			,  8.67		|
|"H"		| 0				, 0					, 999			, -3.33		|
|"I"		| 0				, 1					,  10			,  0		|
|"J"		| 0				, 1					, 999			,  0		|
|"K"		| 0				, 1					, 999			,  0		|
|"L"		| 0				, 1					, 999			,  0		|
|"M"		| 0				, 1					, 999			,  0		|
|"N"		| 1				, 0					, 999			,  0		|;

set ZLECENIOBIORCY := {<p> in PRACOWNICY with dane_pracownikow[p, "Umowa zlecenie"] == 1};
set ETATOWCY := {<p> in PRACOWNICY with dane_pracownikow[p, "Umowa zlecenie"] == 0}; 

# pracownik preferuje pracę w dzień/noc - D/N bez ramki w Excelu
set PREFERENCJE[] := 
	# praca w dzień:
	<"A", "D"> {3, 8, 18},
	<"C", "D"> {10, 11, 18, 24},
	<"N", "D"> {16},
	# praca w nocy:
	<"C", "N"> {12}
;

# pracownik musi pracować w dzień/noc - D/N z ramką w Excelu
set OBLIGACJE[] := 
	# praca w dzień:
	<"B", "D"> {3, 4},
	<"E", "D"> {2, 4},
	<"F", "D"> {8, 25},
	<"J", "D"> {2, 7, 9, 23, 26, 30},
	<"L", "D"> {3, 4, 17, 18},
	<"M", "D"> {8, 9, 18, 24, 25},
	<"N", "D"> {18, 22, 23},
	# praca w nocy:
	<"B", "N"> {5, 8, 22},
	<"E", "N"> {24},
	<"F", "N"> {11},
	<"N", "N"> {19, 20}
;

# urlopy - U w Excelu
set URLOPY[] := 
	<"A"> {15..30},
	<"B"> {30},
	<"E"> {26..30},
	<"G"> {1..3},
	<"H"> {1..8} + {28..30},
	<"N"> {1..15}
;

# pracownik preferuje wolne - W bez ramki w Excelu
set PREFERENCJE_WOLNE[] := 
	<"A"> {4}
;

# pracownik musi mieć wolne - W z czerwoną ramką, oraz puste komórki dla pracowników z zielonymi ramkami
set OBLIGACJE_WOLNE[] := 
	<"A"> {10, 11},
	<"B"> {1, 10, 11, 24, 25},
	<"D"> {3, 4},
	<"E"> {3, 23},
	<"F"> {15, 17, 18},
	<"G"> {18, 19},
	<"I"> {3, 4, 20},
	<"J"> DNI - OBLIGACJE["J", "D"],
	<"K"> {2, 3, 4, 10, 11, 12, 16, 17, 18, 23, 24, 25},
	<"L"> DNI - OBLIGACJE["L", "D"],
	<"M"> DNI - OBLIGACJE["M", "D"]
;

var praca[PRACOWNICY * ZMIANY * DNI] binary;
var praca_w_dniu[PRACOWNICY * DNI] binary;
var naruszone_preferencje[PRACOWNICY * ZMIANY * DNI] real >= 0;
var naruszone_preferencje_wolne[PRACOWNICY * ZMIANY * DNI] real >= 0;
# różnice w liczbach nocek poszczególnych pracowników:
var naruszone_nocki[<p1, p2> in ETATOWCY * ETATOWCY with p1 < p2] real >= 0;
var naruszony_weekend_min[(SOBOTY + DNI_WOLNE) * ZMIANY] real >= 0;
var naruszony_roboczy_min[(DNI \ (SOBOTY + DNI_WOLNE)) * ZMIANY] real >= 0;
var naruszony_roboczy_max[(DNI \ (SOBOTY + DNI_WOLNE)) * ZMIANY] real >= 0;
var naruszony_czas_tydzien[PRACOWNICY * TYGODNIE_POCZATEK] real >= 0;
var naruszony_czas_miesiac[PRACOWNICY] real >= 0;

minimize naruszenia:
	sum <p, z, d> in PRACOWNICY * ZMIANY * DNI: naruszone_preferencje[p, z, d] +
	sum <p, z, d> in PRACOWNICY * ZMIANY * DNI: naruszone_preferencje_wolne[p, z, d] +
	sum <p1, p2> in ETATOWCY * ETATOWCY with p1 < p2: naruszone_nocki[p1, p2] +
	sum <d, z> in (SOBOTY + DNI_WOLNE) * ZMIANY: (if z=="D" then 2 else 1 end) * naruszony_weekend_min[d, z] +
	sum <d, z> in (DNI \ (SOBOTY + DNI_WOLNE)) * ZMIANY: (if z=="D" then 2 else 1 end) * naruszony_roboczy_min[d, z] +
	sum <d, z> in (DNI \ (SOBOTY + DNI_WOLNE)) * ZMIANY: (if z=="D" then 2 else 1 end) * naruszony_roboczy_max[d, z] +
	sum <p, d_start> in PRACOWNICY * TYGODNIE_POCZATEK: naruszony_czas_tydzien[p, d_start] +
	sum <p> in PRACOWNICY: naruszony_czas_miesiac[p]
	;

# czy pracownik pracuje na dowolnej zmianie w dniu d?
subto praca_w_dniu:
	forall <p, d> in PRACOWNICY * DNI:
		praca_w_dniu[p, d] == sum <z> in ZMIANY: praca[p, z, d];

# pracownik może pracowac dokładnie na jednej zmianie w dniu d:
sub to jedna_zmiana:
	forall <p, d> in PRACOWNICY * DNI:
		sum <z> in ZMIANY: praca[p, z, d] <= 1

# pracownik nie może pracować w dniu d+1 na dziennej zmianie jeśli w dniu d pracował na nocnej zmianie:
subto przerwa:
	forall <p, d> in PRACOWNICY * (DNI \ {max(DNI)}):
		praca[p, "D", d+1] + praca[p, "N", d] <= 1

# odchylenie w dół od tygodniowej normy czasu pracy
subto tydzien_pracy_min:
	forall <d_start, p> in TYGODNIE_POCZATEK * PRACOWNICY:
		sum <z, d> in ZMIANY * {d_start..min(d_start+6, max(DNI))}: zmiana * praca[p, z, d] +
		(if <p> in indexset(URLOP) then (
			sum <d> in URLOP[p] with <d> in {d..d_start}
		)

		)