# Sample   Paper   for  IEEE Sponsored Conferences & Symposia

## Authors

- Derong   Liu
- MengChu   Zhou

## Abstract

— The   abstract   goes   here.   What   you   need   to   do   is   to insert   your   abstract   here.   Please   try   to   make   it   less   than   150 words. We suggest that you read this document carefully before you   begin   preparing   your   manuscript.   IEEE   does   not   want conference papers to have keywords so you should remove your keyword   list.   Also,   at   this   time,   IEEE   only   has   some   general guidelines   about   the   format   for   conference   papers.   It   is   up   to each   individual   conference   to   decide   which   format   to   use.   In order   to   have   a   uniform   look   for   all   papers   published   in   the WCCI   2006   Proceeding,   we   require   that   every   author   follow the   format   of   this   sample   paper.   This   sample   paper   is   for   latex users.   Authors   may   use   the   sample   paper   here   to   produce   their own   papers   by   following   the   same   format   as   this   sample   paper.

## Sections

### I.   I NTRODUCTION
If   you   have   an   introduction   for   your   paper,   put   it   here. This   sample   ﬁle   is   intended   to   serve   as   a   “starter   ﬁle.”   You need   to   cut   out   our   text   and   then   insert   your   text   into   this ﬁle.
A.   Subsection   Heading   Here
Note   that   you   need   to   use   \ subsection.   Subsection   text goes   here,   if   applicable.   You   may   or   may   not   have   any subsections.   That   is   OK.
1)   Subsubsection Heading:   Insert subsubsection text here. Same   thing,   you   may   or   may   not   have   any   subsubsections. That   is   ﬁne.
2)   About   This   Template:   This   sample   paper   is   for   latex users.   Authors   may   use   the   sample   paper   here   to   produce their   own   paper.   WORD   users   can   also   download   the   tem- plate   ﬁle   for   WORD   posted   on   the   WCCI   06   website.
B.   Page   layout
•   IEEE   now   only   accepts   100 %   Xplore   compliant   papers prepared   in   PDF   format.   Please   make   sure   that   you follow   these   guidelines   in   preparing   your   PDF   ﬁles. Violations   of   any   of   these   speciﬁcations   may   result   in rejection   of   your   papers.
•   Paper   size:   US   letter   format   ( 8 . 5  ×  11   in)   or   216  ×  278 mm.
•   File   size   limitation:   2.0   MB.
•   Paper   length:   Maximum   6   pages,   including   ﬁgures, tables   and   references.   In   exceptional   circumstances   up
Derong Liu is with the Department of Electrical and Computer Engineer- ing,   University   of   Illinois,   Chicago,   IL   60607-7053,   USA   (phone:   312-355- 4455;   fax:   312-966-6465;   email:   dliu@ece.uic.edu). MengChu   Zhou   is   with   the   Department   of   Electrical   and   Computer Engineering,   New   Jersey   Institute   of   Technology,   Newark,   NJ   07102,   USA (email:   zhou@njit.edu).
to   two   additional   pages   will   be   permitted   for   a   charge of   $150   per   additional   page.
•   Paper   formatting:   Double   column,   single   spaced,   10pt font.
•   Text   width:   7.0   in   (178   mm)   and   text   height:   9.375   in (240   mm). All   text   and   ﬁgures   must   be   contained   in   the   178  ×  240 mm   image   area.
•   The   left/right/bottom   margin   must   be   0.75   in   (19   mm).
•   The   top   margin   must   be   0.75   in   (19   mm),   except   for the   title   page   where   it   must   be   1   in   (25   mm).
•   Text   should   appear   in   two   columns,   each   3.4   in   (86.5 mm)   wide   with   0.2   in   (5   mm)   space   between   columns.
•   Do   NOT   page   number   your   manuscript.
•   Unix   LaTeX   users   please   use   the   following   command: –   latex   mypaper –   dvips   -Ppdf   -G0   -tletter   mypaper.dvi –   ps2pdf   mypaper.ps   mypaper.pdf The   page   size   and   margin   settings   in   IEEEtran.cls   are set   for   IEEE   Transactions   papers.   We   have   made   some adjustments   to   produce   this   sample   paper.
Also,   please   note   that   IEEE   PDF   eXpress   will   be   made available to assist you in creating the IEEE Xplore compliant PDF   ﬁle   for   the   camera-ready   submissions.
### II.   M AIN  R ESULTS
The   main   results and   ﬁndings   go   here.   You   may   also   have a   section   for   Preliminaries   before   this   section.
First,   if   you   do   not   want   to   number   an   equation,   do   not use   \ begin– \ end.   You   can   either   use   \ [   – \ ]   or   $$–$$.   For example,   we   have
˙ x  =  f ( x, u ) +  g ( x, u )
or
¨ s  =  G ( s, t )
where  f, g,  and  G  are functions. It is recommended that you do   not   number   an   equation   if   it   will   not   be   cited   in   your paper.
Equation   (1)   is   numbered!   The   following   equation   is   pro- duced   using   \ begin { equation } – \ end { equation } .   The   main objective   function   for   each   unit   can   be   represented   by   a quadratic   cost   function   given   by
F i ( P i ) =  a i  +  b i P i  +  c i P   2
i (1)
where   a i ,   b i ,   and   c i   in   (1)   are   the   fuel   consumption   cost coefﬁcients of unit  i , and  P i  represents the value of the power to   be   determined   for   unit   i .
Recently,   it   is   popular   to   use   \ begin { align } – \ end { align } instead   of   \ begin { eqnarray } – \ end { eqnarray } .   Equation   (2) is produced using  \ begin { align } – \ end { align } .   The objective function   for   each   unit   can   be   represented   by
c P xi e k xi  ¯ x i   +  c N xi  e − k xi  ¯ x i
m 
˙ x l   =
e k xi  ¯ x i   +  e − k xi  ¯ x i
i =1
q 
+   1
( c P u j   +  c N uj  )
2
j
y   =   A 0  +  A 1  tanh( K x ¯ x ) +  B  tanh( K u ¯ u )
=   F ( x ) , (2)
where   F ( x )   is   a   function.
Well,   the   same   equation,   when   it   is   produced   using \ begin { eqnarray } – \ end { eqnarray }   becomes   (3):
c P xi  e k xi  ¯ x i   +  c N xi  e − k xi  ¯ x i
m 
˙ x l =
e k xi  ¯ x i   +  e − k xi  ¯ x i
i =1
q 
+ 1
( c P u j   +  c N uj  )
2
j
y = A 0  +  A 1  tanh( K x ¯ x ) +  B  tanh( K u ¯ u ) = F ( x ) , (3)
where   F ( x )   is   a   function.   You   get   the   idea!
A.   Example   of   a   Figure
An   example   of   a   ﬂoating   ﬁgure   using   the   graphicx package.   Note   that   \ label   must   occur   AFTER   (or   within) \ caption.   For   ﬁgures,   \ caption   should   occur   after   the \ includegraphics.   You   also   need   to   know   how   to   cite   your ﬁgure.   Here   is   an   example:   Figure   1   show   our   simulation results.
2 A typical angle trajectory
### 1.5
1
### 0.5
Degrees
0
−0.5
−1
−1.5
0 50 100 150 200 250 300 350 400 450 500 −2
Time steps
Fig.   1. Simulation   results
B.   Figures   and   Tables
Please   follow   the   style   in   the   sample   paper   when   generat- ing   your   ﬁgures   and   tables.
TABLE   I P AGE  L IMIT
Page   limits 6
Excess   page   charge $150/page
### C.   Page   Limit   and   Overlength   Page   Charges
A   paper   submitted   to   this   conference   should   be   prepared in   a   single-spaced,   two-column   format   and   its   length   must be   kept   to   6   pages   and   below.   In   exceptional   circumstances up   to   two   additional   pages   will   be   permitted   for   a   charge   of $150   per   additional   page.   Table   I   shows   the   page   limit   and page   charge   schedule.
Another   example   of   table   is   shown   in   Table   II.
TABLE   II C OMPARISON   RESULTS   WITH   METHODS   IN  [2] (40   UNIT   SYSTEM   WITH
VALVE - POINT   EFFECTS )
Method Mean Best Mean Maximum Minimum time time cost cost cost CEP 928 . 36 926 . 20 124793 . 5 126902 . 9 123488 . 3 FEP 646 . 16 644 . 28 124119 . 4 127245 . 9 122679 . 7 MFEP 1056 . 8 1054 . 2 123489 . 7 124356 . 5 122647 . 6 IFEP 632 . 67 630 . 36 123382 . 0 125740 . 6 122624 . 4 TM 94 . 28 91 . 16 123078 . 2 124693 . 8 122477 . 8
### III.   C ONCLUSIONS
The   conclusion   goes   here.   This   sample   paper   is   for   latex users.   Authors   may   follow   the   sample   paper   here   to   produce their own papers by following the same format as this sample paper.
A PPENDIX
Put   your   appendix   here   if   you   have   any.
A CKNOWLEDGMENT
The authors would like to thank Mr. XYZ for his/her help. This   work   was   supported   in   part   by   the   National   Science Foundation   under   grant   no.   XXXXX,   etc.

## References

No References Found