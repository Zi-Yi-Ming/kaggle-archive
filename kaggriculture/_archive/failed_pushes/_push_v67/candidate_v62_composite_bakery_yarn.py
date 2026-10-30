# Modified by mohui666 in 2026; see NOTICE for the change summary.
"""v51: current-meta capital-flow hybrid.

The 719-step route is an offline proposal prior.  Runtime decisions use only
the public observation to repair drift and control market timing/quantity.
"""

import base64
import json
import sys
import types
import zlib


_V51_BASE_SOURCE = zlib.decompress(base64.b85decode(
(
    'c-'
    'lm}SKG2cvn71Kf5m324C>`v1{D1WqKIGs1B%E2K_sY15=B7$?c@8+<2@dk=+#YkRjpN3{LlaV&!b)c|Ni^t=#hD>1(9i;p8u_T@u'
    '}vXJX5#L|GwR=|9t19hv;<t-~aPJ|MOq}b-'
    'D(A6#w@@znLBQ_vw7|z2Ey=di%YN)4=@ukh!PBfBn~gsbagX4hI6Q3XAQUqW>HJ|9|=4N7L}H-#OfF(ElC#e;>N-'
    '|9p8gq5p#Z>%YIR|7FwyZX&%AX$M^fHN^D1J${akX|pbLp-ua;dz`r`GXBgIsmwIY;0@QRcm92-'
    '{jdLfz38qF%oV^V>fIZ$m(%Xmovy?Rx6Gs!`YErawlOI#r}t1KOC5wbJ!ff970-8H)78*rm(%f5t!=1Ni--'
    'rasGnSgim}WE3C-IQ`r@#d$iaV5N!cFk*xR`u>RrzqN-soTt<v?8JtIY>WwOsBGSjKrXDy7X_ihBJ#BKL6oT`ma`heM*&bKGw3D@'
    '4D(yet?(}A%*6Bc=1ns>7ITh654q}w^0yzLiVJv3eoVTR=k<#m}??fE(f#qv^^KNWelLhZ5I=I@e5YTezL2?alUbq`4}#IIYv`7n'
    'zYwgGB+VLR&2uF}iI_~b<`BboaxCr1S(j752B#e5gQW%4(N=0HN<a(P?8glw67Cbw66FM^lPxcIh)-TrnGb0vBE+)-'
    'S1qocc!T?01V!spS8L)PT%I&%#toNJEPfIYN<4bD-'
    'gFvPeQ*P|PzLL@@#^!^8>N~j-*=j{1{Hlzw2ycbmnk_dzB9nQ{2_IlAR`mLf}{b--l(TPj*hi!h=z{(mzZe9l4#$kDw0cRe16~{N'
    'T@Fb0fzMkeE1nM6YXSlk;?SD`~@`9nIy~N(Lr}qJ)M+WEH#eH{%f=qv#U|x7;zdMk?(^n%WnQ2$a<dU-tcU6}NgY=o-'
    '3LCh{r=cB2ST>pWRPnA-k8718l6K>?4rREzRzk494?Wm>%?2f{-;Q4G(r@H!?|Z>UBRb|mQ}of}*7^N1RdTaiPsS{|FAps)uQb-'
    'f$A=v62>7^Bv}*e`Ln)3-'
    'Ho~DJgd6(BuSC1Ms{86`k?O$H#6yCw5TEifC}_cB?7x=ld7JqSzg^%XZ~oHd?=iV1H6XTY(Nl`vpW&pqI7N$Kj2#A_$w$=s19N@p'
    'PdZ|IiDT(xSpbSHk2PnTl+iovkUM0n9&v^u#-'
    'h5~qw<PR&Bt@s8?U2(P}&^MP6Dt?u2fRVb|$mzc+53Mf$JK75u}24j+GDIoJ>v_(J&y1o0N9bq!9r|@ze|>DXyXs6VM;_WYF21n%'
    '>9)k|_Y%psD$g-aNqayYdgJu@&Jq-'
    'T|@W%6xXFjYEhXpcA}Pf%P5vEq#P6t9meg!*gKT9W9i|jc_#rkN4^+&d$*55`B;5op*NGh$#i#EkbA=uX5S%lqu$)I;|MxFQo-On'
    'TdtG6SIZQP#ax2am#p$;a)sP?c<N%d7cEZ(OK)_GxuQPVvg$`SHX`16x~O;I7as!5x;5MdDc!^9(ovq_s+h-'
    ')6{ROpThy(5VOfcmCA^Q4I5@@nOZy;4%%_yS~)8ZsCs?$`q^U?=hh|%de?>By3E*5TwsK*N}QvbQ(vsr;=X!q|3)o~`Ux5brIp%H'
    '4&}I#Y+w`=7e@jjV6ZVyhYeM}FX{F?&nqnY>h_c0m78k&*?3NNdeVzaDzf1_TLn$xR<^taED&5u6Xo7p50}2g&(0F0+3VMCeO7U7'
    'iqtn_3|XF%dKQ@SB&{3(xS>>fZ|3U}c8#@HtY;ETGhqE6R8;|=`>XA5E9<a(otDyGP?=v5xlaWQc?B==kr~hZTU8x<J6%S%21QTU'
    'ygl`r^Yy2j8U=B3A*;1}j`IdfALg6n*`O5fQ{xw}_z1m`^KVhoetvMm&2+-'
    'xD+C4!OsRy=Ovaz+yRn=4&Bx(9uDyQ$o{#W%QWZd?k31-Ic8DS!FIgxF3DN=sZpI8J4)yZs)q2)vUR-'
    '@xNvF^=i26R54zksuwMj0$ahm88s1idoEnRl^`fg)AbFLfoq^e8fIrk3=UAp=V0(wGKK86LzkZM~Cl-'
    '25K_VL?V`3fMN3M7Rk6=H7%T@o*%6!*L5Y4be5$!VkM;UF_}cuHXO>bzsVe@meEgEJLh7iIqI^2wGtgao)dD%lI{CCJ_VoFlOhen'
    '#%YOP%f+IdJIL>REmAc^m}~Go!iiPFR@e74#*+E~ExbXf5I~9sT(hwmOsNuddsT1G`h=+z-we-'
    'kzYUMfrt>O+<D_=9uuu)+97%eZO+>hdWB*hMN-bqJ=XXlpFg`bGlr#=6jT!tM|@)ISh8q45kgyCXXNGn*D>a4!2c(-'
    '<WEHp_TR!RtF38VGwXMv~Th~X>b+M0C<UI0xoh;TsSUBbE}D6kjZzaLUlMJ3fyK~?yQ}6z>e25!r8ux1+vg_`0|_VgpKLY5C1_8*'
    '59~rf36hlnLEctX@8RP2U5Mh(c<fpl^$tVYxg)Z&qvh8Q)hXGbolAhnXQtMzi1TuA#TyScpUZ?+ZkoR1I+SIez*P#FX^ULf7x>5r'
    '2foI(t8!0YZdSqKjc;R)xK!ac%qMb4!^**W2}B&yNs|6*Z#B8v}+7#B6X~58t`?mJN31#nZLcDi1bx>Fze45n~?och8+;23tW2ab'
    'r1J4W^yDmrk?ExU6WpOvrD!gT#u|Cf?1glUbxwtI@fb{fo&!zPt(m?C>tBp8u)^83a(@&7Xw?0|3M+=`*v}aBzJg!H!nMoKK29Xc'
    '&rR~L*ls89J$An`BLf0+|}&lb2%8xz8BJ3Lj<~~$f6$uYpNaM2Qug2uOVHBg=|+ySIa42wnvOt^Zl3ii(dWyqi)O_ethY#xz7pFQ'
    '&oLULy(^tLvyiy9Mx7h6Q(B8#p6kx-ni;<I|mxnqjY&TNc(+6nrz#eZH+b!tq-(vSIt{z=wPRCgU1Q$;m6{Sfq5(7`n}R7t-'
    '<Vexh>ptyQQ5EEe7-^(NpPyo?O{JAK><J=f8%~-J+7gTFY9w)=mp7S=iiud$EQEP6X~-'
    'rV5n(OYicv+BLMCFK2hJ&}irx5A+WD=IkxZ?kMzzUjmBk@#ShMce2XHn=B^{#<GYKlXUj8)_ir{UKBZC4h23Ml@6Kw>U!PHKd2(r'
    '8Y{b|0LI)tD@4$0eKv;Ui(-'
    '{+&sg4#G6tGkMc(p%e8U+uCjOU=LweUQGDNv9CV`;(C3LH)V%~FS0^0%=41oA#^91J$Ob`mA{&o3kP2@6^B0^!W&OWz8C6U_grj0'
    '0|b#FGML(%yt^E$s!j1v5t9KO0PPv!NjpG?UCX^v;lC|pN7tC~jcuDfTEcvIS!w3R#C59pqi5d1KFO{`Xtl{%$eI@uhGC_6s`?0b'
    '|bsdC^c?V*n3wtg><hTsIRK7XXPkh;4?^M(!78n{9{H6jq8Lp=I+`x~bKk&Mvr^1B09K;JeHEWfAlVsNnRMyK~2!}HMszEn)9#5X'
    '&>zW3_7c%d5Q4=Mw)Eo<FDR1s%tC-'
    'vpSkb8|MG-^(g8+Gq@a64$>tERdmXmY@O-Tvt|`3F^Rv)UD?110;x&4XN_@6FrPoKr4yPFScyNW_^KIjb-El??3pZhG6<*U@epSe'
    'p(eX3ifD8dnsyZqMsyFsH)()iVL)a%PQFgVCeY*KM7D&RFgQ4(jFp!hYp*XQ5zmqokc1ojRzEM^LHv786n-'
    'Yz)1AwNKx2h5aCOV@4J(q2HM<FbP=&52oPU$(E{}dyo^ljUhBcH@5>am~zSF@eA3nLKLa_3GEih=bfAfr(`Oq-IM(vWwL`6cFM5z'
    'MS8`r^7-!a5NV&edvP(^s>o9LjN7RONn((XCd<>!G$-dsElRmTLL#(%@3-0`VKS@q<IU!MP(h?^Htqh&l=m!_PgTXGc3t-'
    'Eo#utp4bdOQ=e2g?N4ayBcA6rERHqeI@~*W!PuDE6>wCbiS9L}kq4buIs(nMlZM1w*UFU<iA5oHBe1dnLVewYFP{Kc`n#QAji$AX'
    '278`eS?mm>pWS3pPT97aG`dp52o!7Si++w@SnEp+$^uRV-;{@RFv-62z0>dB@tCqwiT-'
    '<JD8X~s4YOC3)h7C}nhnGu=Jg&sMo}>3<u%YzHVm8Gwj&@57=qx!tN~$AeWHoO|lcg=#DYPoxAMZp2{SFKE5)Q8oNU#lvTJ%{d5C'
    'CW(uKCpoB=*JUk?N$CvOrg<kVR*sERZ${hES{dTPqX_XLJv=P&O!hP0f-|u5c`r-'
    '_A9g?Q!JsSqJlfP=MOKCLN1K?Q{9E>S~lYZ2FX2RGrC*>W*)<JRb+UOD&CwmuOC=ij6PE%jtR5dTQrewOGf$+;`Mpsm5JUf<3U@t'
    'fq-jMa4n&j7SHWSH;dhC^J}M{o~R)44Gk%8&hOid<>1SeLTJo{(SYSmmx**ziM=NO0tF9gY)*M*J?lFq=JuD?-'
    'Lz+>}Utg76Ga=xIcV8&}xCLZf2`S$Qtnmy>9ORpjtz^JF1V1qthleB>AoglUieegQwqScAxG5YA<&I(XiygH|QE+G93<%ORC%i5u'
    'x7@3Fo6~%95N(^MNQvB+nJPxU?UTpwT@|>%~5nGVZ7MnF&^<M7i^_DK|$#9TX&8sPH-'
    'N%KxAq`s=lw);M2hZ!5VL3&hQ6zlz{~;J=U4GOo%COWFig7_T@W`M9JNb3e{^8?C-'
    'FInXO*)7wr#7l&7wD2&}VUKP$@+tu#jzCx~!q`o1a*I$I{ZN5%N;Tt8JTcW*r*f>&#JSrp2-i^;%F4L9ydPj;@*G-'
    'yG&0gC_Prwl*gbqOXLE)8A<v4pHV5zy9+pm=JQEY4lEk3xzpZ)NP%$WJ~=WVg5cX)TU%M7`>=KYdj>&_HsP^W2q#PJ}u^Hv>6<4c'
    't+_EqjdhZiots**MUDs!VxQT^6&<D9;;O2k?J>nH$*q`usUue7+3Ewyh)OSJw$@jPii@#7q#UU#X8PeQxpN2Av{VBryt@ig-'
    '|+~=aUb6UlZen73waYbvE?P#R9s0H01FLFIX9fz&eZ})MZsS_KKj;qx4SlKr#^ex<J#M*#M=X!n_1_)buGACU+E633esM03~x65('
    '0dexGBc^Su){Z>v{a%0w6+-g>ktMrCvD}4?$@vqGlZ<81P4@ypmz26-%^op8uFAg*D_`o8=>oamkk9FUKd)AG!-'
    '0w{~tBG7XXZj5P;N*IKf98cQ@Z|@u#^O9*Tvl0kx{!SFQZ+hYwKOR#^Gcy!2dTOL4@!}z^RDX2z@i%Mv~sWAD{@VzxVl3#f1Opm;'
    '<{Jz(t|n5Ko_1|@`Z_-{xG#SAWvFr7qh0NVsNh9vAW%n7tCO`y`x3hpygYwmRc38$qPTPagm;BXyulQ<}rJ_O*f@Y4f?=-'
    'O@ZgIidNmzQ)-Tf^FQI)6t5h%zz4ljr}`}JiuMt2g2tf1-aq-'
    '!B~E^W@Z>Rhq0PRA6#4oUZ5aa9S%eotJ1)wbN>*agmfa_&cxkt~R8=tC<V3gZmRAt2pu+;K{DT7NSjo1V$R{v#CnDsBE@+P_VD!@'
    'QXLBD4fFO=nkL3CRS~}y&sqZD*&%^E|<ehBRi#)8P`lfMMktXh5K|s2JlY}beNrE5uK?$}NUE`Oo*l|gZr-oBl_8zyZyk>X9>OL4'
    'Eji__99p^4qM|?05PZ%VQL1gKc#--8y=>Tuuvj~f2rX@}$Ti9ebRZH>+t~6#s4`OBJd|k;t?e5L8Q2qx6OM6cC-bB3L9h%grUBYf'
    '0XH?u^W=fRv!rp~r=6-$F`T$^I?{kw%9r?W2BJ<j~Pw&AB(h<NzwPQ8w-'
    'nBgY+7dCm&jzDGZ^kbb=+7>Spd4>uUR9CkI;cUbU2+8Fs)3EyTr#?B!98kV8gcN6VIA6C2Iek(4jr#`E*;Gr_8VKm##tdV``3^qm'
    'gxJi!tiKOMIglaLEK|6uauYJVkb`En}~8Zr_{nO#Wadl0RIdu6s%mTx41C=3UDE4^NRt$f+%XUkGQuo;LI3MKg{{k?($tcSvNlV5'
    'U%i4@uNI@z0#+v{(z9JKDid;`z)$S7~&K4OWC<T)8VL_P5^CLaOUr2dnVpRNg}+RdOy6IeMu6S+^$2GU3G!i<vD&xaycLRgG1J6)'
    'Jug2+#fkG^8kypC0m<3f84vPYdi4R)KM^mH2Yi$I`#XjI$A7=Mg%@6zx$FG&l?~eVnuUiv?EsoPTRt7maf9Cx{*elu~~#fv;G;22'
    'kLtRO7oj?donh{tt+L%*D3#0?1C;#T5HBIrWNvjKegk1!?l(9<T?|?LaEe=i6@&k*}gGQR5|GReCsr%Yvd($z%h!DvUf@sjP|$TS'
    'f&85&}}f#(45zStXQY|J2s6Sep5O!3L*Jv79dArfKZ@xSV5Dhi%y`sJ@RLL?@-'
    'ue8?>n5<C6X5To+<RjyqL}_}hVTQ#`iNI{(;DDR((e#_xypu0TPFv}xqzMV-gjk*%A>T`uFaOb;q-92e>;GEC-'
    '=1ewD2t9c7MdQ6ZPZ8Yt1J0FlD@QzwGw=%l)<K!SeOH9(QF98s+dR@bA<?@LGm&)$~*#~9dxYasq&JzdZL3WY4mzAi|5%F#g{Edp'
    '8^%6a9wDe8$ub$=gJ-yekG(gi^4bZMn^Qr#WG)bp;wtrBU?L6bf_DjvqGkDo|d4R=a?Snr3u{7!JGradSB=3+znAQ>a(<@Pm70<<'
    '&Hy%rlQl>w!WA!>(@2FKiv5Kg4ZdEpoa=Uq5k%c`^v4p|@gR+bBh2A?{{JT;Ytv5GXj!WC8lmX^4y|<y}<^Eu%^pGRApl86}Klxv'
    'd&ZYDN2pJwmSNMr}fh=ECY@kv?tRa)7Ml%1>EH$;<GLf#){Kw5I@S;g(ZKgV39hvt+u-Le5yN~l&)5KSzK?uW-'
    'd<BeS6Q4F1Eis?asx^svLBH}`mfRqQwUAm(Yi~NAgb&2~oq_QRx!g}H^U)a@bkgWGIsh{>+izow-'
    ')fK3$}zTA?8~36^+^b8_;9K+-tjK(g)nu*@^6%sWvm88_NxH4H4cSiz^ZGzK5Vuvy?fB>kUcrqCt6WVi>Ka^m<^=;-'
    'uS2$9kYzvo;`*0Q%OwVy@0mQ3%K*@?$<hc<MdJ3-$J$N4`ncq@A!-0k1e4+K(qV#*o~{^`E@*Z*jgnx#;=dza9>rlHKfLHMS$Qw-'
    '7T5tdSBJAa-$4kw`-%Nd?oAk&kLDvEc5qkXXAX?VO7-U$~ahyFL@3&nkkaJi(<`scJ4hF+a-'
    'RjaF|vgv*fIvt>w<ND@`Kn4Hg+(|9{C}-MLpIYh5O{m8jlusv66KpfZryha<hcB^h6?MasT5)*0HF(LI&n#>lh7E)Dcm-'
    '>KyFNEYH0*?(5pqmGW+4=lLHMIZe%e*i@*kzh4wy-t4_Rt4v;+ZQ}tz|b=-'
    '5O}gQ9!0tdTnl|WZ7}2Zp?L7n=<ztwqvC&#%xKcfD0**#ZpmeA^&E5P4R%^(>o8zZp>I5i8@DSps%vgruEKUv?EJaXRb|}PTTrVR'
    '0$bJDq8n-6xHGeJIVfXO0P;;KxF5isJT>Tb49w5h>2Q>r)&Z($7zwcCc~e3p)`-'
    '$}1(Q|@i_S4Jh><=vYId#}odMBLBXHBT1zu{klRO!$(w7F622JC$?!y!y6aFW-'
    '9Th^g%AfJ0<$#yL2Cug>bG{K;JNP+kU)@)0Y_1>cG|h%@ds!j(pDRfk%ur1h-'
    'PufYmmT#7wSB#J?t@;5jqYcY@qgiV>Qskf2FwxjHeMf3Rm9ESa+<QCnQfOx47Rf7JGRBIO1G`SI4xY6eonlmt44(>JIjqTZSR5ek'
    'v^%bclv5o908xTDq}eAOgfcI@iaBj^*^XieGWq}K0Jd=5!=NUy%%FCTJN8)#x&T4dz<YpPX~|01(qJ|Z^5S8eXE+MJIMa8?m}GME'
    '(h)7hMi>%-'
    'RT2F!9R2Ac@C|6CT8S|%M%RPWxWXy)ps@(H}1tSCFwO_*t%>1{SS@5H)6zPufJ@(`stRJZDnb(NvGL9Hj+<E>6|!ejjZ-'
    'g2|#ujRT##fk7x9rz2HSgOS3UxsjWIvD~;E%4%Tk5JQImsS;juT(fW<MLnv}k6bK7cJ{4ci>tGNysZJT(4%91A#IW*Xk<7cDObPo'
    'Cy1Z4Yz4<7!?~M|r^?}cFdE;&~qCI_F?^BY;S*<{<Xtv?JnPe)g1>Pg-KY3T$4LBNTBJ(neUD$&r>&4~u9KE*n%g3MJ!+D-'
    'eMsd*AC08u;@2?@fANAit8Q(MVU!CY9$ore-N+<j|#jHz{c1p{Myo*+JhsoypTU}lNE{i83x?L+P{coL*9WfwbY-'
    '@HeqxLwgvY@h?Z)Su)dW*;7#yxzA0R1>-d!sR+CMG#roomSY{vs8%`atq^AQ!59b72%hF?BsW^^x-'
    '0eekl{N>U?0H$R+eU3bMUFCx}UpH!;!8UZ-H-'
    '*&bW|A@aQRLjF*L0z=KLM>SSF6v~iAc0vqUM<Cs@0){k_?=xcVDs;xxrdX7TC9G&vlYFC^M&i(!nYO=oMX3M&?v#IlwlXG4%Eb<Q'
    '~ZywR9_>jClwE^3V%Hbt`b!iV{s`8Rj+3>+~41r{`dTU@8du@_tW_V2C-'
    'Jid&?(3b>?&81Pdeiw(8!`*sAncQm3#4?jSHOCJ$$Hf8o`B7_1-'
    'nAT36XBU%|flm$j|cxxGb6)2+B#mQ$(oPPBrq?WV?oux$d>C3jiXqiD(?teqs`682gmr{2|WY;U^>RMNV;?d~8&w0I;jB&wBE$6R'
    'MfC}7lRxeZq9KN6VXyoKk>!YUdb=NLe!RHCqpTvyl0hb3vx^IN6iPkP7lSbtmE4ER*gJ(^c-'
    'm$kUS3A4UcKtela`F^9A^r9>3xLG8{Y&#TM8$V6igR0$<>TVz=GMR*?kKO=xn8C-'
    'o5HjNDVCONmxkl3GNJ}G;sP0;_o|C!t)t_ol>8ui+wzAcPxMjRgUY!3vR|KmeY6SiUS9jHiOi3l*BK1KLAtdIWh1G8bpoFd;ATe@'
    'vkv!e@WQUDVf;bK$>RJBmq9A*pzZPBK9<V;WV8{i_g%$vm^^Lv(wrKJt&6s4-B5qF$x?7^b~+Hb=7t-'
    '3xPYFZU<#it)G9ee@~R|C<u5&K<?T4T2=RU(O~7lFOTyWV(UHd!@O&mXCxDn2!Y9`lD}jeL%S$k=3JH?{EiikXw#YELV~v~9lW@x'
    'Z21vWSDv<5RB>WPvp1=<adyEZ!70LQeVKOmOT0X_Ndf`@DvCoM~jdNs6!JoHV+xEuLv1GaO(D<_Z>XJf-'
    'm)k&Z{U_fE$iN)y<x>%}8wcci)5gzF`BubG=oH`nEI(hi+@-y8m(d)-'
    'ixvSOUEZmisoozYc=>jOutcg)?BZvb@L)y3E(h&4@yk0aJ>D${tFOk&5IYWeshLby<Kg9<WqPb0XVLK^#>zRq6xko+C6b_h7I3_d'
    '3(;^YcOOMY`H)d1@bT|ax;B@{raa@FX%<b8uS^FD*i-K-ZWC{#bGo`ITOZxK{^tEQqoyLxPoCvav%o{*SJSnua91$~-'
    'A}VV9Guto!Xct+_6f5-'
    'g!%oJv!;(_bb|$WIFcHJc6;7aMnlE;#AZ_~roWNH_L#!SXWjzIa%?PGqxVq^SXUTwCp%o!jy$Awi_K|5x%2&s0{gUYELP#8KSPg_'
    'V~jT^jTIH^(T6HSxV~<fU!&ph!jtNS1$cFEnlkApzjQ`FK3~?5EpTH^udu%vH0ImcCpsn|jBMzYUx@kwmtY~bn4Z_q3p8IC&`=Y1'
    '$0?(pu#SljLa6h$%Sx5K%6)$3RNM1KK~O#m6GXTL0dQsVvEN&6Qw6*C!;<43P4k!KXc5~_=LH#Dq$N-'
    'KSZs^~?*f6<`XoLt8{OyhtIPf(cOTqHE!ZjHSz~`I(yzmN&1;9=vwvAQ;ig_h>W5+Lgid&5z}#aWRoO!{k&O)#R9Krigo6bbeJ?h'
    'Rii-'
    '`}#mok8Lv${*&`BgvkC#54QvaZimvTrzp=Lao`v4X9AUL9cH_>{_Kpx`$((0}O?O;V7rG2h&Ug<>5ZQd<YC(7K`cg;}XyJWZ}8#6'
    '9$bu%xGxhZzIc2?eDHy~cycrSi_wPSN3z6Il}XB!9iOti*TPb4S<V8QvJ4W2rBsI*1@^ogn+@Ccq;Jz++_q04q-'
    '91NkY4%9pKpEj5Bpt#Q)<>(G2WJ{ihFV9JcPyA&>yV3dw6<t_qgYnxfl5wC_g(^XD$u1wj2_R6QP!$z^#b;4}e^W0*pTYJT4S>&`'
    '$^fF6KRyRO`$~(;Yo}L_(vzd*cVRU{sOO(8g9dE1Q>ETo4~J}RuurL?KkA<RBe$ErCaZ4G&He5P86BJLoX8i&^S&`!e)g>;)m{oP'
    'Pyd+!2HaMnP2zj#m3I{jXwj4Hc8&7&*SPHo=GKYRMTu!*W?E`J#`Qy4^CU5b&)6EK5tUA+;?9_~w#=g|n!c&RdJCKD>G)Vay;V*='
    'oR_x!YxP<#Ps{1>FOiUs>zvA|_r7N|79Pvzi^(FOb*>t5vm$>#?KSkaf%UVXw2Uq@oVK6arBfi(+wSw8j#P(Oj$nQSX}834(;YiL'
    'H|qF972qbfsGJw4Bh8`1A8VFR*KDetfbL~}@dYPpUtDY4e+KFGw3wHccMc*;HoU>BI3YH1kTtGl?KEFl`<MuTQ&nlD0+SRwb3<EE'
    'a6M{PuOC0SK4l18V$Y&e$1XqKj#KH&9v6k|N^KYi*zko513|pDob(}!g^)lM*V`9IiqZ2uE)*8~LmQegL$6eXyQjKGmNQ=?CB4&{'
    '82eLVpAQ4_5t2rml~|k-a#?Oe%U_q(WQ*o|gvJ~x@rl<><?F+^k9B&ySRA9hX>mB-HVR!`@Aa}(9m0#pi7ehWdSuLPztA>=Q}SIh'
    'M{Cucf~&ckh!7=p<VQ&?R(KxUq|e8%sCuA`?cs#+%?Z_ZtF<SSu=?TeFe;x&s8GaZa_T;Zr_F4@kGc5d8rfCb_0+8NHQ42LznO2v'
    'o)+kRM;m<@w2sX#lZ?^dV%(|gOtzP4+UrZ6&I<r{n(CVd(v3&zo}?<4lmBk-SoOv`rkXvaS)xa)PuXep1NiQ?qF{*Mt@eG{e~-'
    '7XYA(9ozy}6&KdQT#X%il)3-'
    'e<c+IUM`NrukVx$?_3zT{YacK;OJ`)O7hrl)4|pnnY8+3!Z!xXh~&O(iT#>iz3#1T*WsHM}pY!v4niBkg6B#zH?Bl0~1(JYjp7NQ'
    '^foz%VYirroiKVC})65}q_82M>H{$*&OMP;o!E4&I>MUwhV(YLQaCaBN%jt~{{=?GezEnFTamY0?jgsV6%R+C6r+{nd*IeQeYL*A'
    ';#KxqPV?XZ`l!spWe4_SEOaI;k=wbtA52&(t$$`SGGfqp`4Kg>Up87vV%*OPfz0g<6X8WeWlz?yKEQ*6PUf5e`JL94*ugD)rD^{D'
    'J!0rZsrk=wmqoTR*pP7)aRm)54GCtFScv?tX1~cC!TpmDF)iNo{3eXU%q+4)Or<(fli_J6&kB9=^fAJ|Kq_KIt^J@yU_|jV@9=aB'
    ';DsPwLJs2xr^BERJ6<Pofv=wwYke>yTgY#f5NK{5AHWtINi(yD*DX*i^`jIbF&t2pi|)f?MA{liRA%>X5Jy%`xB@bUU;d6?V#+Jx'
    'yVv=K))c5c9zqJne$q-}GOF)Gqq(952U}Lq5fWAI$Axai>XV@rpz|Gj2dO7#nNWI8xo_^mMLJBW)S1sLBK^Lu^-'
    'puC1gkk545at#sOh`*n{qr1U@`7aiOBnnFMRAW5R@gL|tkI@gl)ZcKl1<0Cbhg>`$@!^m*4zi>R}2iJ18t&E~U;I{H;fA7ZlV9}`'
    'r*A=_y;pE65idA-*FcEi;LohFHR#7EMG1^@OWAw!~l`9bmewnUTxEq3>P3)`<$g23+>Q{;kj-}5(sD5KGd7a`NuW514-'
    ')c<IzwLGJY*+Z!qf=Dy!tQB_!1&3_=Yb}*wpXKOa$~2$0C0r2dq#-8nqr(lcZ^>U0R#D>Kg}la>Tw75{HZ7y>z`M-'
    'M{*^fRi@Q|)Tq<@>fP*Uly%49yPei=I*HWnQZnryC7v*4ahF%@V<IYD7g^q>SJI&{W^o8%Q2jXaffnF_u5WIK+`l*FcX}F8T{3C?'
    '3W6`)H!riLaPbY~S>sn{D)@Z4a#oTCEg?&UE>aPFQSZ~;`I@q3j5u4>>1kZZgXg4K^a-'
    'e&at*aqXm75q(K48_N>a;huQhTux_rN{b>pvjS^*x78N%wZR_S<?<_NY^uhDAKVqDoIes$%~=q`xldTUu;**)+X3RnA+fA0GXD|E'
    'uoHAwrXWw?-}VKD7G?k2kLST`-5Lmxdj+A%0zqMsF-kC$K0TVqfD?5-*@j6WTSzsV*dhW<pZ0MD?z=%~}7-'
    'LG`TPovsd)lV~UJiR)F?n!??d!qqcZr62ZWakekRS+j0)YJMndo?sB*YMDs{3?Zwa|@VywZWR5Mp&mZd|sBT-'
    '7*6AfOC<tlR^<>sndHKIv2T-VQ<S5*L$G{Z-UpRZn7V!0<OGg7*^$+N@cg14e#+E!SDFtx{8osqb|mTG!sm@O9ABi_jA41JG$c)-'
    '10-'
    'pT#RPXB4_S1dbhVp)>~wKa>o~6xX=V2>r3Ib9iaQpiki2cU8hf4=r_{kycKb2aPMds*M&bb>gGV<OpzOH;4a8v2a$fc#N|MqA2tw'
    'mtB!M`+HX``e0N5Y@HOm-'
    '&7wk#pDOweeaR}F`1+hYJWpqLr=Z8%=2NN9;gC5>?XtOh&!0WW*`$*blr@s57+BDy_u}kpGFN{6EV8~i%n$55Z&lNUqef~ETyFfB'
    '(N9kdMUE_Vnt6HV<YdPg(FLV=#`1k+>=#pRV*&<E&XWOghfeI^PbSTW$y|U{Rd}uaCw(~YjMl7NF$Z#W@`MN4hc5X!{)D#|<2=L$'
    'ukLV`*wbFimsXL04$^)o*^7&%)#Y$A4iDRsGdmFWRnN_D(D-'
    'X;E8yA$t@$m8+E^(zOvWasJzC|GAxtnYc}COt(ets62srfVoJnY(9nFVT<~V8#7O%k-d^Ekzt>`l>-'
    'oQ}^Q6JIU)9xVJ#j_$xsB8W&ZA~CCjCBv*eIyovv993D&%=zIxJMjH(~7n(Sy%JHEr8o%+pCRNt#(IQ7ZRBQ6!RPA_O;n#H%Lm^f'
    'VFmIap?bswbFVe>k`xk0t}~JgdJ=18r(|g1|AS-sa9=0r+ZnY3yvDD_LT?bkA%1G8gQU=RvYlqW}n=8f79!1IT2kT_l*uLqy6Z6a'
    'Mkst=BL$^Lw{R*`WW((8=gT|Qy=UosrqI9%r*0insZf2PZNVK7(+cTv~T+pTP)vE`4Kk?93K^gb-'
    '<dFTJvr9p_Umt$X5GLR(m+<+^=r;xF7|;5dVeAQt^zw??7Hkk?wK6-h`icyE|T|=`K-'
    'dtg+fQF0DG=b77Fb?PaV|tgyng*c_Ddw^><j*M1;B%5TjzhS)es$5_Ag`D`CuS8w&B-'
    'J7w{`%kTf0Zv<1bsV#eomLtK;XU1HM}HBGXUNScRM*?TssO1Ko{iN^f;wdJgOPG#Nz{tE`*?C)F9yRe3#ZoyXF#l)Xf|ORM&2nno'
    '>kO^<eZ{sttZwkep9FLJvjA{!sup=ECnwXcYhj4zfr!`5Zz`?I`2!fw2lf5U$aTs=FMY91WvEBRsw?VImROG=Df_e#Q&F^o?no+c'
    'd;mZwC$`pCc3}frJ<M00m$YH^IG95@qwM)tE7leUj4b*<EPbi1DcVuMTPt<Ki5YzK*kf`8-'
    'XRHF}>JENAS^bQhwiVXJO?v@MZOvs(WZ_McIpHNMd7DkeTK3J}hH~LgeKNzoANpW28{lUC1c6+uLnSyR`D-'
    'vfO1+o3tFTc=+sjbZ1YB5BQWfo0SPa8(2nfZ|wWXVYI}Z`Y)ymNQFEz14*dKWw2m8taSM{TUQw{X4&Bgz-n;Y)>c^tQ;6Ujd-'
    '%^Tn4T3Lh{sSm(Cu+z_KxSRg0ofbTwI8-'
    '<bCw>MYuf(&VCoOrz@uED4nDWpQ#JOSuofMU<LK!$JF#R&rI_X7GpMhHMayW*wRFR)Jb&sHMm^Uy{SPFkDOov&37ij4fc`?w+dfQ'
    'WKT9iqI%QaY_{NoYQ{aEvQA($vTrp+>^Kkyw;e7NiZoK|j?uB_wA5n)#XL9ga|nK#!@qVdaUKR~ci|=@e>obGk5*hPCjHYJ1nxE1'
    '$G3p=Cq=W0*wo&NW^G}rzKD7tb6P0P)w0Q^17^3Fo(Jt>hu%SYrmx~j<!NqD0Si?t&f(l?RBx3lLxj+SAJ*P|LOvD$(%F|ju&hp<'
    '3mTW)G_NG}9e&ecp!vp#i5^s5t<CN+b$T>3XgJ#EN_cIXPV=L(MXuZ}q(j&z?XK#c?fBAN?R#O`UYt7pWm2sB%ZY+_r_c4Tk83Fr'
    '$(FC!F55DyP`_Au;ti70q&=6efMTdpT_T!3sKOcO#h<_vOW+Bm2u$KdaP?wJ=MP#OY~DJinAfi#k%4h(pG+`$*y;?QtY4sT9{8Q+'
    'TJsgcYBwUBo(MI-Nj<HMkG|>crqFf8&)~G&j>K<ls6mCW3e#HNSy+5whzwNa(Tj$+3s5M{d(oLCyoJRSn0-'
    '_K%m1z#QT?j`E(fRujr3)5hZ0m6rWtBJ`DF>&J2hMB3=JCXSw_zKRn&OerBWQf$>MC;9t~5gJ&NpS<FA@}YlI{<dznuXux<qe=u7'
    'zhP12wCaIRi2J$~Oi)QZjIq?Yvkgw%#}mJ)5I_AK3`L+M#sFpNCOpG_@d&Q9+BIS-ucl}s;=sbMk4<7nP=c3cfx1}b5iB7Iu8dm('
    'nKjmb%-t0Uj5T~xI=z&n$jc{tF-'
    '<Km!y6SPw(8;QfNNtJI?Sa^t1Gk9pr$8$S?N$MoX5!6`Bi_Kv;YW2=Vbg2U+c~~vSg;$R%ybV82xueqAedLGl0nMjkZJOQn8JR5A'
    'jose{a^Xig(Af|4m_PQQxO=x2N*7$WMmMGGwzJD?mgDfzT~d@<g(~CnstG#Myy0YBYFY12w6CWD18i;x^gx)A^*#cg<K~f>^Mjto'
    '%@FV7%S+(|KmE5`Ui`KcZ+22HFMC(;)SpkgR3G^(93P|UT_$r!rFd+wUX%h)0v_=hVrgz>)^WNTpo61}T)T8@#Z>H1_3G(~2XL6Z'
    'D_5EMekA4{a1L{~x_?v?ij?_8Au7k?R4z33$9XOE!N0r=lY<Vcw)|;ND3$i==lmSj)nK}d%z5}JWm92nopaj?+DB%Kk8TkBiLa{o'
    'I2g}Yt5XH~_xom7<@xOxk94$G*?R1HT8!Sac2~LV4_)8fV88xYTI&-=MKNg);h0z5Qd`q}Vkwq2hV;^>C0y%Q4LEJnrG3*8+-'
    '5!}5}T0B3u^|8NjLe*EN<6=FU+|yI?SjY!<;eRF@Sv|CFgf5`6S2Qk2&-'
    '3Q!CMr_NE<hByPTpUJ}T|n|7a=t(HLgl?J25D^^%wcjBCd`*tVSfrTCd7es+mqPoTV;?)XN=x*l3p-'
    '~ND=Q8fvAbnju&}rO6@WF3Y`@MdtG{$*#(BZE}JspP8dhiskP8c{(Oq<edonB6B;dRK9Z@Zl+S9M(*zGVAxr~aOP3?I+7RzUaTOW'
    'e9lUiO_!O|RXE9x*nBxp7Y~^@cuus%k(*nO|5q$&QE1gjMRZJrM7suW^F~3cYV_Cu&Z{Y$=L@ccUGG*Fvn?5ij*W(_gEdcdg{rvi'
    'zER*c7_s;^^KKIwTGD59{^y+~%A?_7z&Y>A@X8+c|>~Fqa|lv|L#{LmhKm2YNVH8)pu!TXiO7q<bj`)ff;*<3IP_`Ff0Guz66$v`'
    '|uamUnh8PA3}^J@4bXymC#Q+><-'
    'y%fXv%Dds7I^@8N|k24R%<K0Ao4a=QBp8>h^lr=H^T!(i+elyr`(%t!Zy?w6#o~Q&%6J?sFbwMJ-pmJhH&g8ZwQ)3$~$UYZ8_Kp@'
    'HA0%E$3l$hRK_wR<O3lrY#Q}W54&YwAd3vA4j5?MvW#8QIa(b}W9v2mZ&(xzdDv5``7R9X9xw@0%ahOjtNh1zvqj3)_P#8Qe0#!p'
    'UZEDr3HcuQPn#YAYu3VMfJVNe&eff7&CfiJh|2&s`xEKB2DBgCO@#KM`lGF?8=LIze6`-^R-'
    'Z#~FUFtN=fFnupDV*r6d2hlEu1Jexk99ReI;Vk=0sWBS+Ly^q*if!aSCalOiF|7Mp%v0xX(-'
    '%~9%r|UaY&C`y;sjJWZPTFtr3GFjc3H_^QAYq41;I!6iM~2I-'
    'nAFde++R$L@RVkRJ9WTQ2R4!lVEGdmQsB5Ho%nDf{}1GFh9|vywPlH0sO#A`(7#$>z-'
    'M^Sp}JKzAf7zRfSl7Q_e=7K`Qs#WaP29>Au;z36DgB(nN!j<mlHSLjd&Iv6b|IOoU3OVg<1W9B}T(qpl3BEpmPbzys*91cs<a8TS'
    'vzW=C<57pstSBL2iJ;W;?L|9J4TyK8$*1W0G-Hn-z_)7Nlfk($|_kO(`Kt2Rkt4n?mrpuc-'
    '5n4j!UOd!H=3u_M+xLJSm+b1M)bxPcX!z;$*Ks1=>W8ALfviI3lG%wWQzEEEXGgCVM)Yijr9dl2|8!w}YxdlhOU;{u7%qV!y8PTh'
    'p_nhc{k;|T!Ah2}E$i0Z-'
    'PbHYXp6NMSlo>4Vb>3Zo`lUH)n?(0cvi<%3fPNymDG>r1Ci$YQiYb_P0HKMk4)d0lD{kG&U8K;)N9_eu{oce1iO1S)si>5JpSB{?'
    'p<4_@L+3B5S|8_tx!`Hpbr*xX9%uQ{oqadw<V`8^j^QTcnn7NxU#m{tcm=sh_BlWrw+4c2Yc;5y6o`w{L)!c;KkUhym}rBPZefg;'
    'z@VDVY4|}nQOM)Xkb^HLq}Sdd%`y<>-'
    'T;0c`g8*((&9s7ABPEmqy%$bya1YNcoSmZwFVuF*z>JtM+v14}wtJs(o}{9~XC8q^I1B4Mc>%W?iq%Y=&?0NEG-'
    '+Z;ZdLBj_zX&O0Fbqw)T1uvu0jRgaZz1hClPKDv&WLV2^9gCaJul|K$MSz3*?<z@YcL|l7iYLON3qxk7@I5LD!X&pn>7w+&#`h9c'
    '|dypZXCR|6=^my{7+`>KEkd5JOtRt6jq*nDs+3p<q-U1(eJP4ZEpF$=eKg!sd6hpWWZoWz^Z!Ehu<KK>zijTVq-`Vv364-'
    '7PNZYAw1?5=-R!p#jZ?JYb>ZiJ12KQk_#@kf>VV%{rP_@ZcQXdw)q~!IdoRmq`eVN9Fad-'
    '884Yu&uoM#sqw65^0H6W*OW8@uG{_)uU3JGTDZ1Hi>a_hTeztFI~+j!}IZ+W_D0_`^w51Fw`<ma9tTYK)MRiw1gFX9b;VX&-'
    'bK~~ghiDYGyU~!_T+l&2oaBh8SofuYOb*R?ENCF+|P?Jwlxx|wB9hAnWDTO=asD7U1q`)hDD=ZhE^Z91I@>Mb`Jm-aN^<3|a%Rx)'
    '*&N*as2GWYS!l|!&b5OiG>9W6P{>oQ(^_N9Mj!C;x4neMDZ9JJDQVI|K=b3s|hkUfuI+W|h^^_Us!W0@uQG==WL((PL;rhGU$3Sl'
    'J_tjmXPxNhF*%tQgg+xW}Gv3zc9Rj)L`mE{2jbEYR{zgu>tXWXa)Z*`I%0Ml+v_03((Ti${GYS)=)9luDv!{7<vCC)QUwQS;+!F7'
    '^=6bptE|QR^hY=bl+A{N=-7Jr>*I5O25>JjbyTSbyH5=~P18LQxUN7e-'
    'wXIU<ojN!ic=q5mCZC1<<$;t5&mhNDeS4bA2rd}J>7f4ArqE9V*cec|*_$_(SvqNWmc19AFomt4Q~h?t3vaYZ?1r$Ztm0R}TTVA4'
    'jlhdlv*x)}b!-o4*FJ2He~njo&&9#?r2unI)8<a>-'
    '^W#&V<1N`M<uD;5!J@do;BWsa9!J)wKBR%v3qB8yonDepDMX{>bhFiX_aNepr|fPuRW02axKyWm~(t+{I$K4zQEtxLshT-bqlnq^'
    '#(1DN7_V+s$kpa-|7d5nw>i^Xg_A%_<fkR-<e@-'
    '<cvDEjR`yr#;~Z~j?=Zh?Q((k6?s0;7}Cm=MJKs2>8Z;nZ1hYS5+64Rg3edqm+$>6Dis2KEBIFSa<c<tDwEDssdpOBrhk3_UN^No'
    '%N=^048@kwGNAbxT{*(1g@Qt~XlYhP#bI3wB#Mt-'
    'b=Kt>@aBWDjl2Jcs4H7imRW+&Vz`7t7$Jfvfq)8vY~qf30mvqxhzlZu`s`=Eh@=1YI5S9hRcBUZWuq_0FSeYdbX_;UG(5iP#z5!@'
    'aO@zH+Y8EzJ^FaM)V$dmKc7`)dl=R9i<xwU9Q|>bhOTx@LEp(qkzF9=kGYP^K(U};oe9?(3WGAQqv`o%-H6`V^3MB8@6ds(<dFQ-'
    '%H0gindf<eth^TWx|`dNv-CPo+zbC8&f^Zg$!=>ea@8-S{1KPJQoJI1b<@pdJ8%DS_krNwkX_Q<oj~d|6poY-'
    'q<D4o3@iN67$TBWYKj=WQ@P5ziu9P1v2qo?UpP;RE7Fk<O)!z@HtE34ZtW;DXzeF&-'
    'FYE=?;aBv#kYK~89$TvL3XdN8#{MY9ogNCO2c(t1SOZ`;t6GoT*F@!`_E;|-'
    'wbwbxqIz3gR^tmG>c|`H<?`1D9O0nVES$y><5{N4fES1v4@-'
    'rNP~i5%vwrFLCS38v?ziL>42kxZKx=>_q4c!hDEpBxactN#q&8z?qJ=RT$WTdpW%G?9MVPn;`YNl=lKK11v0T*5Jhl0?ZZX?OUFK'
    '?-B6g#6vGn>-VPg=x&t!c?B}B+V3mvy$))c}OG!0`86>INBH?eJW*cuk02BXE-'
    '(@Ha*qW2x6deZA;Y_WtRZ{G}4)Ab`f<UkE5=4x@hr9grDhkLDLlA&(zg~Al-He}aEb|KC#4S`-'
    'y|KM+`2|7no$Zm%<2#ldLL#dctlsUr^oK#XGEUljw>`DGdCM`EBX$|TYD1Ch9?*ETUuVeF?x5G(=Qi42c0huM`6a)a#Soa%D|XRB'
    'c}mx^<g}P7>ub50AWd_6e`xFDj=nTK5&qfo2v8eth7gT5fulNlFta=0fX53pqA{VSCF<dUznaFOtTT)BS8T<z=hPM3TSm5~wV|&@'
    '?Ud)yLIo6HqPdtS#f{zCQ-FiBdJ=t{saz`?#~OCI+MR^u2)yZV&*E&%_QzK71#olmJVRAKLN4lWUi@7!rb!mL!TFV~<Mz;oPHJHf'
    'N0zS$$31~PYXa!4*8qMh)KZ8@f^C!^=YdwJofoFr>Y>QAIv5<6zv=iXkq#WJ@es$n<ur?V%Yt5S9}1xcRSCtC2{5JUSf8!cXX$E8'
    ';i?0#*uw2Kt?%VV_y9hcwy=vU#=KVjZFdMV&x0_0gI;MWy@oTH-'
    '2aL|<*{?P)Bfy9t*Kgk8|!{3X^MyXj}rc9p3B%Mus1E%o$HdNGsms{9CbW#z}`@|h@&-'
    'eH}x*#`{q<I&%Lwn@;Sk8`|M_;vi0zsszv~$tN;Hi%$%IEq#!XhV0V4yf;rn}==mqwJk27S1?@RV)458S6yK_D;3_qA_@37s$`6@'
    '85P&2;kjiu3f}wnw+_w7YH7i`u6Y-Lz(Y6S8s?%58gTT!ccDd2Apg_1gV~+MV2`W~j-'
    '1$yG$gBBubzA30Z@IldZC@tG8)v_t%rxN*EAKh&7hk9Llx6q)gah}qgRV>4QhS@!(P-'
    'nNjUP@tP^s41rR1)`q+T$lRqwnE!ZBz@hwa75Mh~&sdU)HM@~7!zt#&$$u&fDv(IcA^Zc`f8Y3EM2U>8HafAS2Bp&OCVT_LLa!vc'
    'KltSZMOq-yQ``brJ$9`cT`b3A^RU$M7)oF4QnI}2c~a~*Kybu-3FPlWxQ@gO-kUvEPQR;Hb&kXNUr&!@N?><Wu83~mGGsU45bF<6'
    'GEu5Yd5f<GKEzbL(oz1CMcJ=BNnPJc9j@0V@Aye2NONF^fw(Kn)lSDa11<Q%@Ef?bKkB0#|KnfzAv(<>Y|md99pm?+l5tWPMK6t`'
    'cLd}<oLMAFw5O~0eRjN^n)0{2coN+ND}X_VgW=4-'
    'bI5ous<2XXniIgg2fR~#qZP4zdylH+2#S&kbusac!~E$+@PMwNxQWANG1I5*^|DC5;}%M7^Jy4-'
    'W4&4)7W2u2!4ZK?Io<O>pkQ=6=&LZF@liT^QAiLUb7%ei={6prAm+F`KuRyXqcfn8F9KFRItmSy(Wf?8Qn*ZD8qN*GgRCct7#*y='
    '{D0ZGBob4T8HAD=5#t&YxnrgC<DVC8}4gER^+a(GjfsKtiDGQVtY<q25u9-'
    'DENs*$o{$wpB=+7JJ<+9kJ&*i6tr*8A1N9<X?AA!NaQL~7n4Pqlgou_O%6SAXm{$`_MO%UDYv@HR;?`SO#qox|Q{^a$s-'
    ');KCgA7N(~TkYB!lUF5XAIc<*$Jgn$UJmxl?)pS(&tYO;cSE*o*TZ3ROfV`Sgcr~OZzTUqu9IVcD5V$G8YJy(?4e%Y?jmKG>#)sR'
    'gzNP-P+v~`<x(-'
    'UQgtY{u<Vs8t%R$ul*S7~u;L|s_s*qv;c`>hCbh9{;F)fTW32%*wRk!3xYaj(H1?};vANx2Gs4+k8$uy+%96}U(`Qitj)-'
    '<0Uk?MDtVH7r+2&Vx)(NsCUjm)OC}&M<PLJDh?E)I7U7Ud`(L6KcXofYDCRF_l%jJW6s)*kc%@dOmiGj;q3mic5wN{%)ujEte*-'
    'W9><;R7V=F+uEi3c3jyBPHGVRB{eUg|77e`f5$rBY4&$}ZXl?Bl$*^NBufRkYez+t2K-'
    'eLPuV_LWj8tx_+LmFD0jyxYuBiDO6qJB3AVRxPj7wqK}k^CLMw^mTtkcj4*cmwPmk3eQ8qd5k(Rm$Z80%FxM(r+t#O(XyQpNNK{a'
    'Aw+IBL#d4lOKaaOASdxPtaMJ{LJIob;zQsGd#m2YqtK)uFYo*k!HJ%q3imLWL`UXZOXct9<~32b_TXKx%6|(*h8gXKq0R8!JH_Bi'
    'R<N@59=_%CRb!%o=@o8-'
    'RyDP0k6%46aw!CMCv#P6Ptz%}zoGD%5Rf?8q@xz#ZXJWW4i3L&jqJ<KZm(SFYsu+X98HtZ+E(ojJ7D3i;<hCUk4blQ-IUD4;f72D'
    ')7y4Z5#Sd${urY8iRi8v9fENFJiD{D93?$zf)Sm47A^4=%+-'
    'XM37pDTXExA(%HCwZb2<4o$S>R|sVD2HGA=&k#vJ#d@p=3d>{{+YXL8o<btR1djbrageKor6LEMuL6o<E#fPe4$$4ppo=V~!OWZP'
    '#2uO18C>gaIHcTf<`)XDXEEc!P}D%7O7=Y7tt41<eDKz<cVwKO+!y!iYDS*tY+cf^Lo#t-'
    'q*aWZc@)M&CS0gzqY_MA#SM)Af)Z1uq_KTb-QWq9A{DLzJFD+Rn6wEIicBU0&A&30>*^nN3ycaEk?Ro|pR?o2%V1fVPPN^i3JFs$'
    '9X(7;l%m1-PZMO?kkM@K?nTFBz^{cS*rscPku2_pkLWF2kRDMM75XW1Aa>{_!^G6^<WET-KXR=l<t?a4h+0oeq0b9QQ`ZWd1A1i4'
    'pN7Tf|y?MrQ1o8%jJLOSLqzN}Ysr?vUktBD=6^iX}MX5^Z>r_D+cjHdfu=X88W0J$EUZ4Xko!fd&DOd?{iV<#n3-'
    'j!#cYDP7#`fwZ5+D$KeMxMXoKfXWNO&7LxkgFOc4+^Z^j_zMO9t%1pVeg=_{R0TixfgYMF4KM+5^x7dhRW?SLjIsT`W)TS<<1bi^'
    'm8b)KVe4obWVHtoR!VZP*47l;H+a*i{%4LY??#9O%d3;^a%KkMD4F9oh2C>-'
    'aVyW!{x1xlvX#<qdK%IeyjM<Z{Y&Ci$u|P4!A?#q|x6;FPflzXH2U|KqQ(xRM-'
    '8L)G1Z#sJGb_?_6+$qS4v?6v@t@!Nv*s+oy#)vj)hqd3~}QUq{?ob@J|lyJN1WBWSl+%?!2~Dk{_e3&>DExBDOf-'
    '6+3=z7DAKy0oUfFg(V1AAA68|L^TNzKkTd&iNBE&|Ge}t~=~2g&@TvL;Sp6%pUDbw$Cxz$fVKjaw2sI&bS%lix@YNqt(=^1(~YNs'
    'tn}hF}R%j!LE$SE#bb6MEoI;@~l>4pbNIj&h4coRM4DH#lomxHQi3J)jhqzZ!6}Gl7eWmNgdyZgmptOad5FN{j!5CwCu8@M?otLN'
    '>`1uJGfDRG*|0iUPCWGKOJvgAQN|s__v|AdL&UanGq$DxaM|L=OZr}qX#0X-'
    'rU=F0Vocb*3a6x&H><V44@Yx=Q`7~snb<hF61+#duUwd&otNJhG@4%_`F$d+@u5^h3&Z~z~s@X><fvqy!QxWGkgD9z1WMZe26Yw2'
    '&-^=e{NnD)T=gyMq>9&qlW1gYgAtx-5<hbfBeHCz9b4lbt%$ZOG@rUk{-M#sfyJ~W3?bQMd;)|^0wZt5oj6P_WcG}_-'
    'QAbj*7gEWa*wxiL5QVq8!_(s%Lg{II6u)=uN-*?g^=)gDsCOg3oC=4K`X8I|+>=)4m68nit`K8xqF)Wgx4nbSN4t;!2+V0Ic-'
    '=8EJj>cww*6Ki7Ip<JJb~X@cfM848H|Tt3tyJb%^t&;8+$s>0g|`3#?N`zKSTcI2uN_#f@sE#gLneeP`Y#c<KfkOvp2_2{O2nwp1'
    'VB=ifZ-'
    '1}yW_MuEDGiTnM$U5)Y;87pRF*jT@?I(Vq*VB?$Yk<^LTt?Q0RKYds)ZQ)aI(+a#ZFglhI3<;^i74#n?dfcDRbJX+hh!k$GyMO`P'
    '3%WmI#(w1|DY|CFN)tE3?@>;a;<qYrt@;7P3?so-3jL3)XPe1*YbFw*A{Fy-OZrV@)1w>OpA&bKOx)%;+rsiz6Omoi2{F_=k>U``'
    '^v30Dw&&tP<TEQPS~(&^Xp!)>%O&dt)(){WuZ1bt|uY0mEbB!*C(L=SjIS>ti)-'
    'MW)H&Ijf@KilyA1!D%8Lw<PB9x)hf%vHko=a<1@?K)_Pf2c44mr#5&AF7tmzd-'
    '&bl{P%AZyso&FL#~SVC!Q~JrSaV*ESt1&3cUiwXy#vL_UO68O;79%P3F6w(kXUF|a0(X0BPy2N+N0SNh}v5#Bp5=owfocUlA(ClP'
    'bu;(psKa~$gMNj#gl+Ph|T|3%d+=QxYJq~lCR1&@IZ-Bxj9Z|k%g|h*FmA_k^%iuwoT=3zUf0ehLc(8fQ2I!Zcqnj=Y)H1fRC)SF'
    'T_6BN(1gnzpJB47!2}ljb8?bFVdu}cGHUI(J)z~{d=LctxN|)j(_u<Q8X-mkqr)Ss(saqL%M^U`;y;*qiuSK1-5-Eo{hW^Jx-'
    'O=tf4MVOf6Q2*CO(8dRv2S5c+Lzm%Rb`mA5;8feeM+U{i>vTdX)+Pc5t(pGT{Q=$ExdUino7dY5Wp+gR}XUY^~Nc}qgwt$oZdo_b'
    'pnc4<lMM&*9>eFyN}9~XHq&VMu@wJ13h&?k9|@quKKFYm_e<Ht1}AxrPoD>Yk)Kab#9nc*DmtbcV0`n;g$HItrZGh8Z6T2fR^Z(X'
    'BjxSbl^;!r{3%;hNE3a5dxZ}IRFv+RClwPdC3R+c;IXu}qoGg8SFhaQhN2p+}KAE3h~CMN|-'
    '?BMt37ygoUHLes~v=!Cb@GZ0+gNl(QcTkAl_Yz=hhH5xt>AIF~r<42Wy^P(VA7gPc9`6=|u&*py>*=*O95|~qXAN^#f$!;N-'
    'I%nVzccyGuRpbSw9|X%m-'
    'WP#5ybU|tx^N|<=diE3xOP)Y8<r3N0Sn?>ni#m8|#QL=4K*bnP=n;H}B<1B~ATk^oK=Tv|a^WGmnw=Y%g^9gY=w;fohv?e*!HqI2'
    'j>*bo|^tmch9?yK`R+`@VxsuQ##b!TEDo9Wr5m%vhCpa2_uh$`@xXeK470#PKGk%wuC6+s&$Sa9b<%ewFWyQE@#lyr50!noa?F(H'
    'T}-RW?`o+>+np`-h)pl%jqmEf01J?{9OveqxG-'
    '&FqNPwd$T1=lKFVlPPlO3R?(owr;(5B`w?(wbIOj9=a9rPosHNiCX2zytE#*jUkPDQ~GGXATEA`0)$i0pNy5A-}!t`-'
    'GS<ur<jL6T4hqoB%#1<%$Hnqm5%Sjjl~@nZ-phii+tlgcrc9*T09Q-<=3{+-0!l#^Y+SMliA$ZlvQp=)ez-uZkv||f6<9z$d1OQL'
    'X>*nwc?sD5`_qAn6CkY?QMUp_2sZ({5z}s_JxC!=S98ys&wokdbir68^sRlW%=R{9$3ui@osJveL;)qD+RKh7pq77)EZIKzUpk#^'
    'Ptb|@%y^$?pHnbZkBC;1+n>A-F}Crj3ei%joqi-?Poh_DnH~I2^lLzW_{4woT=7rW<VEp1tHq@Cqk~}L|*j!@J{oPWpZ7vmc0w-'
    'v5$Wy4cfN6yv*N^*P0xLgV{y@WBpeIdEBkK-o^i*U67-6yP~7g6ade^uUy$I8bf7|8{#Tke`e3-'
    '*qMac8m|p&Y_18?J(sP0Td9xwWMN@!?j?cUz()CnB`G+A2_4ZJ<Oy#U2JtV=$mtOwR?C87PVxcOn@=-wk-'
    'c4xAHCGu)?Po`0{cXv@^Wh5O4i~MHgz7E4yoqm^m7Owaj2(J_-YQ?)bK*QOY5z+&Z6u9@A%ELw%OEf{nfF_UXlj7;!zS^#dX;~LC'
    'qt`@;7{L0^7W1zd&SIiSoZ7G)Kwm_EYqhKPl8D{Bv`h4a<71YzPvg-EPCF303(;5!pSPt960eEHh896bX`8)jMo&Xpi=<!xQ}NmL'
    ';`mT#mg<&l9$*Bcz`F_7PxTr$g+v=HgPjUgKYNC+N1uz1HlCOi^cDf#KckBamenS#DKc)(nq5g*z4+PywV0z3KLlSyoHbz-wN~@|'
    'L{speJXaGKG9FA4flB<#Iz7NPVKLORgkkZex8*9yin6c^Zi7@>Z&^-'
    'FnFeL`@aTefNp}gcsNNGiZ;mi;O(Zy<S?X_~|uB02PR5om{NFhW0|}8mmKAtMma$RR(PSBW+F*qRd_*+psJGY%Dh$(|LX^8)&b&+'
    'S-'
    'Qqi5}Ud@FY#NwkYp)?$N7FlFj7JOfNk1#=P4=${yp%A6(kWjbWvlk4J|#a?SnebGV#69#yIK^|ZSUw%U<oIudGB?X9ze2XNeVXl1'
    '5x%U*&v_vI3gz1NG*{*JXr7C3E68(YUhvKu2hTyQoek#EHVtX|u6fvP`wQUUvu$GzvZ_|wLKw8d7m^oD=@b4{&H2E(j*{VbK)?2o'
    '}M>?=JzGAmSYy~?MhRFcC?<cjC8>|^1UC98|mR@p(L?Fm^~*vTn=-'
    'j_wpWTSlc94X_kH@+o|M#NFuEWnU&OD%fzV$fxm9l4cKUwjEOrk_*S1ncqL`Vz@c^MOsw4<qbq`4{<lf4qSBcw|4L4)OQyaP7yv;'
    'a(WSOkn|MkiDCr`t06{b*^2f<8+evY}OR_(fkM$Ue=`U!yzUCjkXxEjqEtOH@ZpMTNCW1K90Qx!gRDkgE_0EETEf<?!~u<tMjAtZ'
    'JNln>6ytXR;=#UP+1*yU<=#WM7_DG+%<Pdh?1Z7+`^7ntnY8kOk=vR`=yx6L9W@o3y=fSBeECWu6h>;HN?#l;t1DdX)V=1#GfN?V'
    'T;azxpyNr-BziWmAGkG$5W90bekvZp}ZSSYP>6~`QKLbE<UZnqGGWOfGItyzC!L;wKk?|5`TNQQMPkHj?@x?B<Vw-0BPJ0Bv-'
    '<5a{0OF^~8BT%UZmWcw&VOO4FMb@_7CJ$%cVdA5J3nSnkfgT)6?tInb*&yV-aG%p$r&mUQ$$mCoy9T`u{h*G0QAs~!OF*r2`iDrS'
    'o*w>YN=BEX<jycl~9Rjfw|VpN|lFEqbB`gMLrh97&|KXO}$AG1As?+kn=!E?TQ5Ns*DO#f(@!yd+^^J%(#v7Z4EGLPPKm+r`EK`9'
    'FJ^{e{8II%v=xP!Wx+HwWJFPQ=$7En>+Rbl=UZNKq=YTW5zZqU{1k_UWIZLFdFdhpO@#N_eG9<QL1+(02l#Ls^0AQa!ETSv?keo#'
    'mjKfP1=v|I*Q6{p~sHV@iH+XDNPYLK-UHs~>f<N0TRN(2b~nh1naYZ!&Fm%+N5Mq917QgV5`wx!mqg-'
    'y#UBS4P=E9LS8oD8bvB^wAL9oj^dl-'
    'U}o+}rEMZdi(WcXXzhHvqRd>{T4!!v`(UjZI^*qE_GLr#syBOXQ+|xg^B?C0_717ZgGNNOG4b-'
    'S>+*#xsqyRaE*5$*hf^KwEi@aJCFq7w2fvLCayfkRO4w#@44!+h&?kcD})*YS9V6+?NK69s1oA`@Ilirxz>i3&rU=YM+`sVPM5%h'
    'W3JCoOStGMAdKQ8rLj&U}-)3)cvq}iOS`@36fH*1;-}Z@apPfJE3V_A%9LCTsdQBh1TRO?zQ)1ROMg$tN>Fv2ey>|`m=!-'
    'ot%`@g^zm&@v&N6C1bc~&9|AHE0zBAu_Mo#&1KSiH@imk=%#-'
    '<<TWd5yay+h=((aNQMsp>$ZC5xTf%srWH!B31{|5ZywP&I?tSeg*)Rp2Kcv?qNGz>}zBO#cqS%0F!SK=RO*et0paum-'
    '7ZzmR$M4z|PVL%6@Ou1WcJOO0(6E=M2LEBMeDA!67RLrSEK^Gzj7Noq?2VycOe+R^CYOa923;qXZ6GE6^oLzXQy2#n@!;f&)zHDF'
    'AinI;yk!_|Pc0vp^La(4a%gA1PmKDzy9UAb>q~Fcc%*}!?OmJ$)W{dsFf|D-)F#0Bp4@?7Z{yY05mC47wRHZ-'
    '&ids)Yp}63guPZiUB~GM>@M11wYR*qfYArJC@RU2MRF@rnadSczgSMAgwFTt;P%*YCcaVUtNvJ?u9!!-'
    '&?}D`$}e!W(MHKzpWsE{MS9Ji4UzC-vR~DNX)obcm(SW64$hSO3=`cl$=G<g^vEQb?jUC5ZueUb8O%Kv<C{JB$U(XhXhPvMarU+1'
    'QOjs2l&^jcrm73wmg^#ZRYE@nJAY?N59!I^v(mkCl?T1KQo8+G@r5>h)igYw`T5OQAZA4}&b0zk_?8LOPU$&Kj)FRS#XUo=#hXl-'
    'H(+eYyeFkXCx@u&Vf(plHeOICLij}q#o1+nw~l^))$TU7CxC{Q&`8gLA=SQ(u3lJl@bq@w#C4vL<C0GHci-'
    '^`1Wk$Q$iD#u950K}pz3z9k|R|d^mtN^S8yj&vt3dfK2}E^V5%ZX4xHTPghTI9cBs~sDT*k|U*GM4+K-'
    'bWACyiMe7J~FOHo*v=O5JQyFI#@gMM!7%@uNudZXN?eO54n%HIQo*oJ0Dv^3#rq)BeB%wII(F?7jPWo6w@`?SN>+JNuyi=ggAgtD'
    '{!%)8{r0d1xGgYI^gLV%CD?zbheX?m5?<`EdSMj2~|*o(EXaXsS`K7>5;(x*TJ{Pa4}Xku48(zw$^a4w}P;Q6-'
    '1Unv<*B`bn^sYp((;yY?}3)A2SW)}<Yuo8PZQU~!sNh+sOH>`VFZP1XsKm>Qg^Vt&d^ip5M#qGP(<DRxyI1zNpe|}=c<W?I=#|qL'
    'LmpVs`y7Nf2r?Bp=s_z<IjVsie^LFX}#L5fEnU0YKwRtkYA6Q%JJduC6Qb`%|;O4Q-D7yBrSkK12%i!dhD@^%h0M-'
    '7@><pW2)6nK&xtDuHD8Ta()KMh5W9Vmhcs)Jp*?K5x$3Q+HGa?o@eFtkT3)K2OQkfyYR`1rt+38PY>t6c6`$^6>p4l*)@(&Uho!k'
    '7J?k2P|l8_HJ*vzJfN7cBb0hSF#q>4hGMibB`J8d?CrH;D^Xi$@x_Zl3-'
    ')Or#3)3vr_oY%!H^ALzToEoH~+qF6Ao5kkw#aoBwx1xn*I&>&X%j8Y8M%6=SFqWd}bdV+M=HR_5O~xk=6qwBhv`F@FqK^e<Bm_y8'
    '&y+z}nEb`rAF2jjmmHVM`1^SkhXe9hJ5rm>mAjwfn14Mg>i4ywFgBgHVG%y?-Lh-'
    'Z9!rKSCM+MbpeilJj#DA#KbNK^d>8xZlPz{(d1l)B>2s*|M91AOr-!X35@N8tjA6F((C&}3Iu-'
    '~0DYPW3HLNWb_ctM25@pbs_qAxocEr*enc2!2C_SpNdz%R9R9jo>S3l)etFw~rYn;|Oef;~e4~=-'
    'DHR*6=yVHtMrgZD{N7thO?3Gp9`6XLduVJNetyx`O_o6zyEo^=^UNsjp@cPt`W1AK#$Su8W9Un}wLb-'
    'n7iWA^OJ`mXRUI&3HMo4obU+7}0K-FlH6ztyE?>p;dEq|TJl-l0w-'
    '#&tV*Q1cz@Q65GM>?3CM(b?~{Td4p1U6xOj`1u!udKV{#OljEj1kw`)3XZ5yb9|X28!Lzpt{=a{_rDceP|Ut?V57Zn20WOv?I;C#'
    ';>x}4<=KLx~)Wq_#*{T{I{(Je;|ba-a>-5vNv>CsQty#+OFNe)E~Vp)xFWUc3@c+K5BA#*{-'
    '(ZQ!DSh1_N17@rZKICHmYcfyh<IUx!Okx~0xCjIMwMhjZ&_A2rl#EZ97lognY4HS3Y@HZnJB)k|Ee1sM7O*|htSIUwHA=1fWb)jq'
    '7J{v4=uRXg7g3LJWpovaZRXYru)yjdE0z?7yxnLKZ2iLI)4i3a9ERo_T#vx>9LruEa@Q2kfST}cmFT$L)_g*~!*t-'
    'tJzek4#c>@_275Y0lOBEPR;tZ;SX$4D4u^m=`_OThCL-g^tyTubTc7%3m^6a^EUS#4%sd(+9vof*;qzC}gIyE;NX0Y9yINO-'
    '(#bhIL|+*OHXaoWAS<)nFA_4pG!+a69Vciwo1-e)xE#S@Oal;y&ZimIa<Wdyy_aOj?!D70ub?q1f7a#OZIn;ZS5^RKXV-'
    '>D<PfYy?Q<@Gx5M>)qHIeqV5)!S&r=0ZRmtfCO_0<GQKaqPI?YA!xZfP`Q`%3iUu@%PSu!qNdfd*AwYsi02nVPy|<bND&lrY8<4L'
    '`zVs9*>98s9ssb5O_CAaXo9ky+00ZKk?#9o@J<n&W;)!!>AGrySZrpC?H<hH4gh)Hw}j1sz0PAQ@d}Eu2tPEqRR2G>?j-'
    'kqbDn>_ID1tr$Mm2Om(JRJ}lzqAJUdO2G3?PutmU2v^+96-'
    'v*ZO_|u)<@Ad|QuafnR^f2C#sIuziW1gxj=0bqrUU}yCC+p)b#haDlTPa|-'
    'nNgdE&+Q=P7_?s}v*U^hYr`3V>r(Lv@b>$9?*O9N`FyPENOF8?K{tYmS9YViGV#9h#pDlLU;sWHUts%wJFuod$UyPb2h5zcDksF8'
    'uaK9D^1!)w*dG8``^kE5>+2eky3w22wTjlWh<>76+gvA&d7}`=!&lhwTv$?MUFj+1HdK*sR>dE3ZQKRPgQHw1^Y2s1bGezDr6wU}'
    '>nkZ9YVM=g|67PwpKnx*;<tB#sLkqWn_NZzdcmvDqx-gGK`^u8YO=vxsm7z~`>x#e`^VbuCHWAaQPFFst_TQ()3vPEc(K|7V5w@`'
    'M4D$m+m%kxjjko(Bp+Uf3|=WSQ=T#3A5z#K*tfWl+35Cm@ARJ^6e`RDk~#iCp><<;F9D}RL^R=OZ=U)zNsJB`XM4T}3(<#awA6&R'
    'loDk~H9^q+*yKjPoQ%wbUO_tCufs4JMW=W5CL+#s4my`shIfB8$Q+ZDCAKpo7au>t>QKEjsAb#ir0I6FdS=%<+tdi&US_?C)oqq{'
    'iJPgM?E%ppz3#*#5*L(?$Ft6{Bvr$71){=p!QSFUUb7!uN7qi5hx{`QeRG}8PGow}W51m)<4$V#q*<Xke`C_>e7WEBXQ?qPYsfqD'
    'i{q#?#@{a7;6)lOC+Mmz-l9$f&PFKenqt^^5o&E@ZysUbvzIP*+R-'
    '}w9ibqfvsz~R44KSy;Hii!wrYgkmN5a7`?MhKn7=%|CHqwHioEc?JjAY;h|R8lIE<M+1)cWPdmS_fPfYu9IH2;B)r$`vl9KcM<Fs'
    '?-'
    's0?>=m_nq^b>PDswm`cB&!QU!=7JgqhlNwIZtl)kHLwzuetHCL`l@bqepS)(=9yQ5=BS$jwiK+(WNJ9HoZ9z$<pKXa*(NEO4P^_J'
    'RdegQ3nBHImn&<FeXllH<xTJeYWa`voVy_UkSkpZ1E!r7x^%k*Z9TvVp1Wb@{84d+-'
    'uxZyxMq#Oh@@N*hqOX%tA#!Q;MEnWpN5^$AMk3ovLMs=$3Btb$1LT&Rs@8s4{~GuJ4SY(4-'
    'nI$UgzDUKqVU)Q;BidDUypU*E{ZlI&qwWpVuj{@qR^Qrh-x+GE5KSX={o~94p31x}TbzM&)C4K)<zIhmLyI*5DCC7h#C<wyNR-'
    '0v(fS03XWFVSHi{>Juc8sT{mmJ0#&+e`X>2Qpi`~sW6@I?K7>{yn{4ndJAq%nF_7CMrm2v;RXDmc1XH*<g~dg4?}aG^dC>1md@Bg'
    '%|~2-Yg}u&dJAN-qTO<~t3NI?bo@FFlDIZoY0IXKpALaNc!I|FN-'
    'x}KtI*(;^fddlm6iE45vR}@OJ)m{H&F5~iL?szZ1N;+@BmCU0l(iLj4KB-'
    '(z^Q_MLC`oty`1(j}{4T+_SqM#rVO1i?zaPju~u@>iIe!4L>vkoEKr?jutK}pt~S?Y{o(B)@9JkY%KT-zogrj#rW7o4PxD<0IWYs'
    '4{xdOt%$FUy8*Y&;_<vGMeA$3-x@BqUCt|B@JFDW>r?qobQ^NtH5bNYQyHe3*{?U-'
    '9_E*Z4hW@;RB2rZG@NzS*%%GIeq~d8uKMd)IR0Jyv8~kdDYPLUCfS_E)5crOq4`g40(Caq<LmJd^xX>pDhSWD^>*W?&$#v2ug0Pr'
    'NSNy!ZO@tTg?MaG=k>>-$yv?rZ6lU`U#IBAD6AiMEqnwb1>V#sF$*NCQbu2HUk7Ne{6=AN(`n>KHdNDHVb#Wsx5-'
    '{9yaL`&MjVgRK_$%fxm}%CpUfYYHLn{IFuSeFv3dO!xmt($en?~a`V14D2~WIhvsnfSJ3)Bs`&#Xe8Gs4DH=c1h_d<6z%qOLTus7'
    'JcwW5cnJb7%~5j<50q0}4OIDI|=(gmU`?Db9j24qGXVomh~=^c|u8LPl0N9OLWwDZB7hABS_xtnB@YkxaV>)O#QWUIPn7~a@Kt;z'
    '$E?;e-b#idNO<NX^N84KC27_4=-HaKE3xR?X;`}ymDXCE!>q*$<7Mt0M|VapIPDI2!$-'
    '~tUZ1KZZS`egs<SVGk4$fXx{0EJKR0XNMLU&5wq)HM1yZO$c`2zw)8%l0d8rO$(Db~l>A5yn>C?^!x1vLzA%(X&aHZ*iyknDkm$<'
    'zf%SeP=w~<Jll6J?^|#{JjSt>c|n^dYXF}xOWZ*mrRz}k&LP3`+x*!rS@pXNHFOb#i71D^fO-'
    'e2FSUhb#`p)4?pzJ(X=I(dF0{b`+O$NR-'
    ')CF{uO;5@AclQp<Yw{dUl!JlRRzikS(x|9&@hO=`$V7x+3G|D}$e6;5Ok}CoF98C(2lQ^U`K$Q5wWr@$!^=w{4p(%AV!+M&p**Iu'
    'sqe64dsa;K$b1m6;xs!bEOHvyZ&;o@J75uJ~yEIJ!r24EgZ9igjP*TEG-'
    'K@or|aGxI+q=!g<@A#=F5|AEy%$S@@$N~*w@ClRjCL;Iuc$$i{Kj`8BvY(ImoeXv*f?yw(itl9gw`xp5(XsD+<L!^iOS+zi;+IJ('
    'VofL|*{es_jO~K9J$@$dhgyMKzC>+3QW9wJ+X+=8HIak4NQ3)KETT>DpEtXHar{~^z-~oB}xl>-'
    'ka?zfCE5Voiwphy7oknw_PAFyv)7icZ>(9mRA$X0)@j+`eFO_xnQ#$=K2CQ{iAD^tVpn;V@id|W!+tf*|Z0g$O#-'
    '(b4*TssFs8R7Yi|u0=+mD~?bmlCnQU5W=(@oCQsSdTjE!c5<1b02<69mUakbom<Dz@Idxf-wjaC(a}1Qk}NQ!d^8=HwKAOzNN=cI'
    '|V)c%<Cn%o8D*@HQE2DGK9-'
    'DM%GlS2=7RRb1OQGF64D<}2~k`uXpr6sm^vEELHSVldq{$Fw6tW=h<{m~|qC=<^l&wffEyZ)^j+wta={KBm<rTN-UY;R?tmf&NN~'
    'YYx2nEwp~4r)xR)I+d0X>a1~Nl)XD-O?|npAD>3^F++!klVtqC(H38@p8K-'
    'N05UF5AnnnwKfhHytB_yY743sOi8Wt=fZ41}Q@T(~Sme3-'
    '`2bmM7|HM5R!yXXWWlr>omDlr7N4v+d+d}1+McF<aju~|v0pyH1h^k!;~V9imnZ3YL$AlB4sf>@PZcl~zX9_!bE{@ywH7q|CT<an'
    'iq_@t1093=DNV|{S=+jU$I%Qy$<rRIyEPZB!?h`I4@!B0b-'
    'O!^8}|8@+uS{1vA1tIjn6`hkomRyNiTIT5r58pt@pl@o|Z}Jyq=}!bfc7BHGmiacEzi$EYISoxpNQb#s^jGR$2(bzLM-'
    'j;9WulD<1{L!TA+-'
    '9CG(k8cnS_4XsUUDikdR2W5}Bk=TTD&7a4#popBb`gF%}_emBL$pl}5Pu~Gub%CmT_EQyMTw>p+B4*Ex=j4TGL<pHVbG0V*KGpe9'
    '68NM0vkU@yH11W;^4u})8(y4Va&iJ{4eClF_e~O7GCWO3)}*4(*ZxrQ(WL_}C(hHK(~AU9^XYK(>MN7joj`J@qZ1y+hwURg(<5<q'
    'LwoC}2W-B9g3_BrBC1QjbAg7bV&jF>Q?>PkI*migyI3e^)MX86`y3`#nfJt9rDxyZz}95kQ`7-'
    'fnNc!F;9Yf|mG^6@FWNJVaf&`62_E8cm#gwCkY8^&aARbCn(TyE+L;DN^v-'
    '@hF0FH*04^Mik*B>mwWx{HL*wFo`f5;rm!?0)Ym<^}{T+En0HhvLbzWwlYn_~DX9m4IE4?a0G|R-'
    '~VJrq+IXu0>V`X?=I5*_NBV8ws+Q}ZTY}qb;y_dzpgnFQ(4xLp8mCDbT+<xvy6W=f{dvg)L+7o93g~xOSP{QAeqM{y`m0m*}{^hX'
    'y!d1W~F^(o@-z4V)*`59RWJ9mCqc*u6hutUPM6cU%8sqr2nJbzd-'
    'PyTQv<9C6bG;FMtFRtVXW4SsisCnYvmC30PPdosXUG|>sQ)T0S=oyBjZK#~H&r3NAelrE4yNx~4b{3gnpd-'
    'cRAD|oga?H>VL`t?2=o%sp#>WJ=QT24qVE)j-$!`8ZL1o)oY;p-aQ={FRonzK+?<xL!tX-HBCe^^Q7N<O2_SX0k!^p{u|}Qp`i5_'
    'd``tUbsqCP=bZVOf%9_^$l!8yK^nKR3q+K@?Es#2$V(U0uc-'
    '&Ikbo%I<N2Mf<vSDiBLY!0(C6%^~HG=}z&nJR~k~MhVar!i!kyz<CnGF2ws%+nlGh)0wbTycrHnu>lU%dSIVh3O~>|FGRlrzYlwF'
    '#3uT0UAzMpQSOG#_C2w+pvm8;2&TyD#!;*UCossEqu9fl}Yw&rBe0wcPV=yn49GCB{GlT}iq`(d#GnX&B05iiY2^S~RfE;Udr|sM'
    '8vlQ*ta^5DKZ4ik-xIR#Yi!1j~G+RQGEI^@7uppLCv&+k3KFojVk3o>w_ROX=OHnDa^y6(S@A|M)M#H)Xe4(Icbtf?wZnWp|mGsx'
    'bm;@$22EsGa*+)ry7BkHFy#ZR1@H96R0d##t2#OGqW|<S<)rv*@+Tj#=bx#V5?&p7V{5`VoS_=%PIzUCzO05s6+h)`8c=-'
    'FRkkc+d$5;*QW32WF*1)@h1|)h7PZfc2tIr@Q#Z3&8wiS?Q;7+)hO0+9Mz3vU{1)!LtU%vm^}J1~xtgPlsmrg3*Cr_$TG&TV0wPI'
    'Jmsyp1v{qO-'
    'O5FcJ4nWVK93Qm<C8*t6xcUeFnBruVkS06FX8&TJJF#h)<F6LiY64iyL3dpGGvhSvlN1Hu^eVISY=aPIgD6OM=>bJsH?9s7qZ<Xc'
    'Km=xM}~c6Dowv*_E;*<*bnkqjulU2Qb+6d3<(52RDWfavN30D^lu#bA47_l^xVy81_}NaPX$IUmR>hP{r|0oGSy|9Oxf>Xrp6;X0'
    'VH6pdGcN^7o>sN#^Yz0oXe=rf<=YVwM<8S8B4RMEf!CQ!RU56tEGVZ;(NAa?o%^Pbv>aDfO5)lHUSh-'
    '>P2ZM#W~CiE)g|2R>I=r1*D?tGz;h=^m4Q`VG}xW4_%k8Mvsfz}x9OGJP~A*Co5*-'
    'qro`4@Q)YX`xU&u$`HFQ=rvrqMB3CQM*#r&W?AkHc{uum7=0KAlXnc%h9IbQ>{@0Ud~f&mc#P$d&{mm6HU16ctF3EpPKufF&+Rv^'
    '7F8)k?J&-&U4*}p%Y_lve8&RJE}d$2FqqPeT3|IYjkpAP76nY99->be<Sy^{(0heyvZ0vpI2nG++@1<IqkX5u{3N&7}=F-'
    '0<dl~EsOcqfy+TrTwtMNp~?$tmhJ=-)UAQ}JOkqMrrhaTrI4J2w|3HUuhiDv77ra8`^>-'
    'APyRBUt=MXD*`&%F+|^Y!bj3w=3lxcNid}9^L!Z_!-iG<o!tLF1!`{@ahz%iRU(nntPEJ|gGujX2I2^J_DOtGH)ns)T-'
    'CZ2M>ob$1^9e!iu8nCYDZ71hNIdBBV)ulG<=ScUj9SHYLhlyG)L#vQVPbtPQRHr6kO%wI-5-'
    '#~t^VEs5*K$o%c2L1gX^zG_PE%^K6rOA?`c)neH-'
    '1`<S^>*b{oKiZiOIY_d}d>dd3O3%|&keJ2?oobRwA6LAAsiU$ZZFZ_*+_7F4k8^ZO8O<z=xV#8-{iXranG#aCN)L34!-'
    '1WSDR)aYgnZ%U;YukYDoJg9EH{{5-'
    'oJ+duMxp0DZl5xo`40oOCGL0+<ZTGi8w@|Vd6WNHRm2X7fubPd)Ea>hk!SQ$i`{(yPE>6Ju)GhpWQ>N|n0Dld%+(30je|D>Pd<>|'
    'QhG(z!UTmt{w+pbtJ$>nM7vbVz-DjI*=&qySmbUAS4Zc|}Z8H(d!1lJc<AE!5=WZmuVAKDq3+nEij9w`VZDX+x9>jASbSvxn9dxt'
    'mp|3V<?%sCM<6!ZC`-'
    'x?^ZyPzLuq6ql;U9mZHhR?X&g)y3I`8|^OrJ#X^U~eCRdu_IVjEEAzpi9s*I^~o@ARSuFZDUG>p=dF?g(6Iu*Q*c_^1pO1zIbi0s'
    'f&g4PQ=%;=dW3P$-lu9KE<j{B@=SGYVx2#{M$)-'
    'iPA6YAMV9eZzo*i@U6S{n2u+F|CwJe$40*OQh7jVw(fEMZe;L0q~SR&gI=zJTvt{dOh^XE#_Z?M>XTyeRH|MKNdQJuRwc_^H?y9I'
    '!3LwXqEL6y}y0N=~4S3>vcaHH4)|JFT+K;O0BmgVQ_!aFgkrPu^ef)wtEoHKXoWO)gORKp3BGHt}H>Z_nCb1Q#grBJIrca!4{HN?'
    '$B>~HnNK4hCeuG$ay-'
    'S0K?~P@v_a<MOwGy6m!k+cV+PHBR!|gu~vGI(Al%pZ9?7W(=Q3rSy1uB)f>LhC8Fkl(WgHO+;dYsZM!@_4%Fte<z79VTwXFc+83G'
    '78ZW1+dvTw81g;s?8uqhDKjfG(SW#D@+8b0~ks(rs!xyvDbF}ARs?R4q)eH66Acp(hZS^tVS45aBkC?qp{N=hE)(42;9~rXwn;k#'
    'ODfuE6Eor|?`W0R7LGr)RpYM_Jd{pY?b~mt36}}FEyW+D9t%A)5&4S8xk+5MIvY<9W+kP!Y^m!2oCzo1zzQPwe$q)kmbi^g8Hkx2'
    'lR93%{cngVYau+cy>t@-J4@p9E9}m64#QQMmNP1a%gNB1x01fwXnUQko4|v4QTptf#BV^ZLiU+M2(>;@umU<aHl1N-(_P6{DYQQ-'
    '&CLXfCe(NNvdrL0_Wj^8_x+yQtbTyeMsV|(sp5w~fsw~#|QI4!qy!ZI*Dm875n5RB=tW1Sx2csQ(@X%>mkQ5B>^<JxDtky3a{!F`'
    'C>E~fI?R1p^S<UFFR0|C!wH-_jv&nGe^ku?WG8Nm8D$`+bs@XDhdU50-xaT~u+}dq@-'
    '9n$+{&sJib8L7Z^|llwT_*GxX|lR9H`E)|I?$W>iZ&m_Yb|oGbg@dn6dIJo5~FY&TYQg=@I0)RuFKIAR5k<O%BcgfI$u@~iGW@C3'
    'E&*q{tH17V?T3YLsn~jgw$_H-jKCb`LbG6mPT+?-mm4?On@M`fJr5Pu)|Bkh3Pg*VORFluzS9ApR;-'
    'k02CmEFU@DYTE86z>(kk+PXQNVl%pKdRSAkRl$!|U^4>lNqw9+tS2VWpv5A`dpJA{W_cmonfWg81$sgca^LpQwZ`QSO3F>*8Up`R'
    'YL2FOv+|lG-uO11&dmAgYDN&!=ceLDR2gPMz%isvMTZ_Z8r~?J>*RxXO9MWC9dgZD0W<$ty%?Ku^iOmVzNZuz|TFZt{fLLScogL@'
    'hem#aZCjg(=H}@C$G<R9gdXqGDYvf_I>cD)q;K%{z0Yy+Q2Cq(VET8h~mQF{_Cph8M{}FYq%j>aG^jaD+Vwy?kCQ>Ph3K8)^$)V8'
    'MF&(b`{k<RRe+7#D?7i3CYpus-TDxQH1=oaHXoCYuB=?${t}Cy>v>yEBjbaXqSEyqP%(M@O`)MYMKikYXCe(6z2zQ88!nX>a$Q-'
    '@a$}@AHE;8)8TB}OcK`Wp0#BYsTw<hM3Mrwb30vL^LnmtT6l&9=H?i?1Ghn%3R`f;?X$!!v4ARo^c=D;(|f#CqXs`g;TcRjweq*z'
    '23t;&ec!*pD#=a}5A%UGkO3q)7{YFcDHQt;HspYb!9?mp$PUw><_qOMxxo?S}Q#vapD(oZAfGAWw(lK$FaWwcygPHR&<-'
    '~2xM9;z*?Alx0jgtPLfkKH)67?fpN;Mq!9szNg;JRLXM&W{g)I`F<NW&2ODx?4{c2fwt!lh+5wX?jC&{I>gm$9<6ZO#J;S)jFe|6'
    'gHY4@x?qI=#j0zM>4xVx0v26S`bWL<Hp1V%~{lxY6QkEriJP;`kI7o7TeO`(Ww^21yV;{96F`@!`-'
    'F%aoo?yGph~v8Qbr653(+J)V_F~VA`zi4-(Wz9;4%RAkrUa{uo_DHT(-2<TY`@Es2v2^lZw7=Vn-'
    'XebptBpdEW-@qJ1!Jr5edr)Us8;U&#2DDeufZ--lJ1&WBR9fI4Z4!0atCHn6nTdgpXyi{k^TNkvb<}x-'
    's3OFBSq8k?_IHWrPZ<o&-INOBZ&?2`*Z~Cm9$y*$Vt;U0-'
    '&2dJVzNU%waRQ;$30u0TyXtbJtl9F?koeNu4z^jsP5j!g{~5a!LSS{ZzpA%7C;}XgIx#qnnmw5ZkZZ5?;4`0Xmc0erDNFC&oh(h4'
    '$r&6HqSCK54B|AU)siZme!_IIM<@+*<>(?tBmF`FJGHX6+i)W%g<=wVYin-PCnjh1@;2>oZu=|B?=e^(ZxnkVTQD-'
    'J8$1dy9a^cl`*=3|mrfM7-Z=8w(FKot2Qk0j)k8CA{P*)5q`)O@q<-'
    '^_`2cq7&TlyKTAW;Rc`s1fykf;o`dKG*JEZjqzV)Wleo!BE#)wxu?Xz+3UAmZsXQtO-+&?0h-'
    'JET}i`jz^`bkDU$?{|>$Ki5PsqfP>Yrv<S^-t!JPR07AYOH}Jwq7#vpgMb&OX}_Y=$w!-'
    'qQ7px{1pwEebqbA{ZrofJnb6{VpA<16wwvQ)5ER!T>AJ!rk*IcR`xDC7&zu;;oQP4=0MhF1hgOUvJGU(9qL4lQY|>&^m09K3kVn}'
    'HK_mFo*&6|pRT?Vhr2Mu;Zttj-'
    '=qYus69Hw7qX(3iL!Ic<NJH84WQvC<$@jw?DWnN1BZk8!=iuc6EB!frQsf*HtG~bVc062^{Tb*b69M~VzoVpqS=1zpLEv46lga~3'
    'SRhnOtz#ro(^jteZAc}`)$RynxR$iepUo=$%5Awy{z<j=cq2Nfg1Q#eC$tC0l(gv#`eRWU-'
    '=&LpUJryY_ai*OACE(ytot|8(ViFEG<45#xNu7vGzAyl_38x^jJ2uS2sAZ_JgdV(g8ibsUt$P-'
    'U(QRU94M(e;!~*d$b3v<v1cTxyMY7=S!>8Mw->pxuYDFDKi<e$8$~D3)+3LABged-adAA2VGtzc?*19N2hwX@>#LH>U5I54y)<|J'
    'T5{GUeHQKCtkH%WBS$6k>E8op+^nhTgBwv1{;d<R#|US!beoSHxH>%yWgqx<~32N#&&Db%`UTN3=L%BAay@nE!ZHZe0`fZXdzTS9'
    'dcfvSM3DuiE{=Ohbqd@^Do|E?v-nyN<*jhU$xVYtJ~)VU2u!;x=8CWDNw}#ESDEn{ENmr<WFWpb23!;agi#w+66-<Aq-csfMbZ)9'
    ';xO0c752Kk`G^aH5yIOXcgOIWHIY43VY(p;JUb57JH8e<!vTH*`wyA&Z=7(8=K^(S-'
    'e!6QB!70Z&G=g^<pjRvpsdbH|nRzew^V(uj3zJ<OMXcay{yw-hGf50ONxAh%}on*2OKI@9?#X9+*S6eEv*DkSHJaI)c`Nyyt7gAk'
    '1Ybj|S&`exMG?-'
    'r>nufc<N=xf_pCEW@_U0*!~=(=&MdHry~r6C3{mGq<}bU9ll#cPa0f4pVM;?(n;u6)Cw7L66ALhW@l$FJzx<VK)=9om7A1ORMz+1'
    '9qHQjk|DXls?mxESrM5acA9Ez@(C1!_BwLTho;;dtb~(fqmM4Ak$b%-SKP!k*x3x5#FEUiy_V4?E#KHXZMF!7u-'
    'E*{!XE5v^?UpDpp^eL6C>%+?*dRc%1s`<bhxd^2vyGDMa^>8g0=XxL4BwfKPN-3-'
    'N<9W!gQ1+7Ww&vyM>E|2*E+=k3Oij>W?hwm$u??aJuaj*@*U(RBAPYwsy~BiZy&9a|+g1loO)Qr5-'
    'Vv^i*%uKgNZ7(jTh(OB_tbqg-'
    '=`ktyzmoqa{8oYn<_()<V;nqX*+aL}42m4yt?!@2?zJuGB{igdKx)R~2ESOy@p@kl~E>yJDX!dEr4)oKLOhFMng2K?amw>>rh-'
    'r>Vjf-ZsEeM4)e5B24xLreLMj}=G%9E7#J#t*U&V8d%x#vU?k?mBX>}I$)QDhHBrIKn~Bj6;z_akjJu0O>f`8p3xZiRUco<Ci&!o'
    'R~eNB4Goak>&G?rUD+c%WJtv^LHDg?q3sb@JIiqU``5J9|QekyeMiEzzwt9ZfgGBS2DKUyDTsxRA?3Zz9beS$jLRzTS+JhMCkyd{'
    'p?TaG{1W*UT*(9w2uO2<M=2^?4aPhOCFs-Ep~c8x9^R;KaeL9Mvacs9*4j+SrilJh2Zz&8gnGN13m7=K!P*eVh9+uB)D0OYz4z^*'
    'E&gbReE$rIX9KNwB(U{YUK9j=&S)X2YsqaE7;8B2P4}xf`987mK7IFG1|QPc8etwxQN?Rs%u{9CkIOv`)$3?zvm&^5waMF+KUi_!'
    'PamHL&Tm4U?cypTZpVYz@x$N%>}RYcyrwk$W8Z=s<drU1Y&*{~7{dR4kXmdHS<@14sBn+sxrd5}5OrcSl_oL9A|cxIq|IHLF#g^X'
    'qTEVp!2*v_SgHBfDExrtg^|zl&JqwgtiMOt!1ZNGY2aU^y37K}JJOuMMIl>^$<yp8chs)G>Jv{FTTrv0LRrZP36%l_CLSCV1z4Rj'
    'O_K_R%M`zIqQIl=|xRuV71aqY2!(9ctjEdl__*G;R+q@8FMoO!9iG-tb=E2h``zPaa&nZdr06-l1G$pMEdoJ<yQr-__R`Y?#G;%1'
    '+N4a6P*5Wt|ksqJWo%5&zF;n%g}|@9(7DM!Pmz>5Y-G@l-xt9BWQ4#pCSoK$dWKc*&xhb3bQk^04D6bwBy%ZA(r}WMLca(^y-'
    'J`k@i{+Z>&qpDN)D70l!Hn6Oi|_T6+G9I9^6HhtX*#Rlfpn7OjXkS1Wy^kTc{mGm1PJ8BOK%Apv&Y8M9W&4nYWC#7;%b0x3il>0p'
    'Lp0&8Tw<z=44WQM*Tg&M1b#0iUREhiF3oo)>ZTWn0!$n%IUFMBP4tA&~VVyg=i><h-'
    '67$CRtPi7OxEtj?wuy#bm7n1UpS@AQtch7hyT)7lwB(A9<ac?O^9lrpz;H|R8rJUPx`BJ}7_u_s*X48XFLh%dpqpR9)`X_j{<{5I'
    '=F%AwCSds@5clJgC~}RT7xQTISEB}>eWh}#pX{04QPiD%+})v7M;W64r^@m{k6MdV0IIuY)WMbNd&1An;!%0OcGE+7>UU(J`LWw;'
    '8=&)7jFxKm;|PL;haPK|YLdd&VgXPF<VkmV+sU=v#=3;wHfRq@XKI*ZHE(9*6M>7B<a0fT$7&TR4+VnV1>Ts(zzy{rY3Xa|C`lG<'
    'Tz<K^$nIIq+vH(l{v?3hrT#fDkTvwwYts)7EyuF0`cTc+)8?!FsI`n_vTr{utv#RfWR)2g#$i3b9}a%8`CeVSYunrs$`Tk3bfXXM'
    '`4ya2?&j(`J9a1I&x7)>^{*ZFxwhVSritS+*M%3qJML08lm;vOJ&Cpp#$qw3Z&uJ4Vxz#y+;J>7tAbt0lUlcCo$JMC!7(mwR_d+X'
    '9X>|vJ%%=q1z-0sP5kQJl7^ph-$&IBR`bDD!CtwWwU(`0eXFOBtzbVH!Uk5UY67P^-Q)Ks27%jIHBXN;-'
    'K_5_;!Q(|PO#hLbD6=ml4sX#yV=IaRGGPNcQf<#3D35uPT24(u=$A14Of(!vqz3|O@>_=_oPnuFEqF&L3G~^OZ%>YRu5v_GLy!Bz'
    'a8lQsquPt%ZJ{&r`*QK^_Cglp#JMYibD~*oT5JNwcQ<S@-Jg<ds0zd-WqWdjN@JV^MsHY)SrMK=5;?$o;kg-'
    '9%Niar1SBwf)+>?<rjMQ1o4RYIdc=ec6#S<bFHQ5@k6i0;PLH2j8^GAoOOP5oOCSl&nALCFSIl`I$`wyJWr^C0*ldjoAHZIPYz(9'
    '@AP<4zCOKT^;$DVPYNg4mDCS<r+S6m;GeN?$4FQjFMHClx9n%TQ_Qry)lWZc=(MbiZ?$JDmZ4MStVICX=h4HFyi4wU(;uhPR@3aw'
    't>6+)-fg`5e{)_LHt0R9eR!Q^yX9$J+shj&As6+PD3+tRrsH#|Wly6|a%{obcQn|H1Fhd$ou)1|#-'
    '!Acnc)z}E0lP?#OHT)8C~9_(G;;70&q{)mq)KoQgAzPcYXYjWtM)Qe(pGXA$2uU?auo=r<si8=_^SXI?ig3dy7&pI~9=9t^ana<K'
    '=q`M(uU=pskl0<pj%WgcQJi-gQ0W4<aFyliwu<^sgn{d(efdI~k3}et^BcCNATMTbB>B8C2Y_4o6~<VPMjh((S4Tv<9PjC!DXz38'
    'UAsm1|`Cq<{f_w0xqyhCN=rxGE0XzAcXaIz~N*^hTh9%HnD~fWoxeR{O2H(G!_3)miDTDJSi6@hbi_RsuThg1&*fF_J%wXY*N9-'
    'gD#1Xrw<GPkgFp5@Krytk97#%R#+X#Zre1+m^Z$xr<xY*8BB|nr)(Bc&i{2e@DKGjm-PXmXz8Uj_AkYu!vM^SO5q3b)MsAb+a&s`'
    '>n-+t3>JZbfG|eRIEA~^F`^=+GS7l0BPd*e#EM3C`iL)FL_OTdOSpK?7|tKn=LfJw&`ceZ@(spi-mGdh7lw_;Ep05OBFLX%9+twy'
    '{jjB0+gy58e!Y|Y$mw1C3sCpI6jBc^1ggDMpJnvDuv=cLq_8YzF~H|Cf=E!hP1dF#27%V3-'
    'Be)r0*5)Gma>zEPW^Cp;Mri5uL3{_LY0C<_*6OflISvhW$GozWMX6zpvZ5rku|#GOd6Eo|B8iYGv;|TJ_I0!asN})hY|z-'
    '&6+h2HWidU{xqAT>b09!6(^LZ7}Oaz8MxLi#qxtit;O#R+4$x40)-'
    '6?zR~Vqj8t&_qAt)pxD$p@P4k$|KLD4QX{m+f|cNX7){H<Wbvw!VsG=Np9+l!%rk6cU*<GTR;(K&XcRwLI1*9gN@f8bY)RkVjXAY'
    'ZelX(to}W)*!OxC$g<x-3L2K*fN~4B)W!Ko3i7|{Y=nLK5x<AuCf@tXS7<czIIWw7uh%oN!XZZabdOa_M-Kd2z*^}JIg$&jjFQPE'
    'e8EcWX8aNQP4=no9kkxFcb`Mcqmch;qhugZfv+d<)Em>B+_c?3OIdy^R#YMU~ncZHyLu=3wh5q16D^Q1OfY;~N<>JT<bM!7@J4kV'
    'F6yGJfK&>Gv_ZIIJ;`zv*(OYxKd0UtrAu~|1g8ojgs84Cm!3`7`L*bdIZj}vQ*~@Qb?~iM{r#@f*RmU%)QHs}A<<tfQwdKwS@q#R'
    '#R#RtS4zbT<CJmn-`WBSDMQX(NJ8Ah7G&a*YqK|=<4tB2|3mEu8$~QcP>+6-'
    'jYH*cyK5zABTctNg6mI<}%)WH;%oy6(;rLhGQa2;wd`Gb2?7H+qrhX}o7p-nj`K#w7wYgkt;Cs3|ZKAa7dX5f);XPaJ-'
    'x%~E#uNCF7qRK;2|`abNfvaMCi0QnLyuIcz5YTKJ>sMhqZt4D+pF}Q&#Wmpe=bjd(IV0td#yv}D{@wJ6gG&z>^7y55`Qvwlbce(W'
    'aAKCgqL=d5Y8|v!BZgL_rLy35Y4<=SxFAlSl*cLP;W9PPsGvxG%JjJ-pn0oscZMgD>-tTv|6k5rg!|fcmhQ-'
    'y6>9nXi*(kJtF0^aEcVhq?NAm{cJ|R;kD&quP8V-'
    '(BkYKcf`0`oNe*r#D&E#1*8|Q<s%$ZIdtnaS{bcPcSfQhxAEv&4b9I57+0m^G9GQOt#uo@F}l!SlSGO5{4<bGkzO(22e+mZe|j>1'
    '2lxQm7Fxynixf`@VAN@=XJx3oo%Bxq-3cy+)#J*c23u~`SDK;MMIgmMVYj0dv{V0nmIGto4VZb4V&A&@BeMyBcI!m@7IT|jj>eD-'
    'yJx|tFU}SGkofa>aJ;$S1csHUPfEs8I%UJ?wg1fy0JA!5UEOw1*6P*2W=eh5Hn;1hb*Y;~A%*7C$vT**DhD5kLbNiUhu15rM~1{s'
    'mRFs%5VPeEI<2=ivpif_q!6N_9mWA`9QSXH?&{fL*rS@T&Xxvhz@8fKct*8T+!%_8B+WW+r<O>#^p~K3j&OTmm1`Y5f(q+)TKxt$'
    'j+(*oNq5i@tYcufWK6EM=@JXkE7aqu%+ZeYC1pf;TPHe1x-'
    'K7k*=8aQo_CgBLESmMBGvMi;g_1#h+pM{P~VmYI6RY=$*l4!;0iK*5H*~AI7`)_4#d05{RImxV%u}+AnzuF<L|E8oohDT$+_&P>?'
    'n2c%rpaXYT^R2i0XBg$Mwo9ww@>aeNX-wPb{^0a$#c~_`Ki_)FCKXA0?|+0{2Ehl{!FrWIOk4p?~moQ-ayrk!B10W_egcwq`l~HP'
    '4U#I(K*?6z@M$tXIV91lKz!kIyQtov$g%5;KkKi<E=tHRV0*wNBt^SbVPkx}3u#S{wIR#-'
    'r<~Jvf*|PLVfa;8nKWzt>Bm`)gbfM~@TIob)XD!48J@K#;#4TxA!6tLtKjhW%S@@ao7hhf1xY^RTJHU+O$<3m2pqWok!%oL>~#(r'
    '>A<3J`2}epCXUOLKg+n}w91Gzw#7xDj-~mDAn$nI+-Ss{_8c)4u#3@RYqZN}91viu^4O!iR5R64f;>&}^cHc?y{}JD-'
    'f5CfObbatYX1)WK5KV7Yy_t*iocZ%S{U>35=8%(9wyhSsrBtWN?EHF|d)y5I4OBf?nywDL>tSu}U+@0fI4?4PdfmpW0InLdgh$H;'
    'ikNsQ>i<Hvb%+y{QX7Oi#1nYN?j$<f;t=J=Y7Vn*}(nMDSyC&Pl@39pOiHk||wDeDllY_qewR{YuiR0gLHyL@JMzJ`{d1K01Ww_#'
    'iZE4+nxU2VwDf&nm3Xz#kFA!s&IIbnF*Uh4Pd#F{4Up8z4-'
    'k17G?Jhx*y7G18ks&1S8La;gxEH@C8Fg+<<JD!Oc6aA>ALZ3PJ9qgR8v(jd@`ulIa#NP<-$xXOnli=Ag--'
    'XqC{oc&?l`9iGo&~d3Xt-6b{#u=Y=_xPag$<RG1)jt=73aoXR|S25ixqo1S<qG-tgP?AY}RP4{I}3L5zX_Z)34SG{Z^*Cp1VL_*R'
    'ZXvFvDuDu2g!vtAW2%>fp;G7Zz6OWwYJWyHj#+Xo1n{FT=KM?>VGzw|OoxZf5B|CeAKvl>WjzxswbABf~qxr^&T(8(r?x$hAw0aW'
    'E@>;P+M$n{e43*0P(J-^q0epk;)apR4x>+*rx`#$w8=R{o{M%UUNI!l<4*uhRLGoiZ)((phm@s;I!_LUprfqd&{@GY{@pn-'
    'S|c;$m11Lv|gQ?S^^_r+;}Qy#OO?o>cIMN3y_zO`Xz#(*Ka|>%spJUe9Ie>ZyUu?UBq}-'
    '^BgxNksXYbM?y)iB;uO<@C5&%XPK|f@WBi>h!~;g(WkE+SmH$FPX#uavUyRu4nJH(&75*+~?vTri7=~U|eP+Z6}AHxrx2qCew9K+'
    '8-'
    'K?K_lFx(wTZPDs}8`Pk40&<n7(%peV0U?1RN)pp4VoFwbA7^070k6rsyc9{1N{Zo^fzx1HO8ygzgcbQiw}oY*A8q)1`(xp?XEXm9'
    'xRJi*j~$`kZV=ai|<_1THh#?yP8ch{_#Up|rA2EAFbU*0gD-'
    'p)|#^SZ?|az}peS+2GEs}e(3BP|s)tUcD2kFCDfSz3Bd%1P1&74&`n@q+3}Fmw`zFTve$XOcS2robPaQ*~=AN`5fIi+Aj`*Bx>W8'
    '$@P9e$8Lzj#&Uz3b5MFa>NufxLu;@Mz+9X;xjJa*1vsT4UEXBh`C3T368egx!OH9u&`cqN2$-'
    'OiDzyJ%o{|Xs9^Uym2XRzj#rB+1xjyJ`YtH(54>TsvAE3XX3Pb(`QU+TX$^elsq`+rmz&;iwCzjq6CTxgE`yu4kxzV~89b`@^L|m'
    '_uGOFdjHC5rZN~H3Og0O#lJY5hx#`)!H5C`V9uE2DFdZ39j-'
    'EaBFbL5pvG5wL;+&2bMgZUXo%B1N6&=6m?3lYprt0e82Ord%rjJvbTbkq+N!00mP+W1ZjfmZnpA5La8&=2X)dqMD<{IC=c$FqsSD'
    'rqIz3QdQ`r>uL&NQ10s%gHo*SR#%IT-Uc)zK`7_f0vG`7zsS3&gy$Ioa0XuC=;dfu0lw$l<TXc<im&{w}mbTW#s5XZQT{na7e#PV'
    'BW^@OOD}`jq!M-e_2*!R(~oQ8_j8Lwg?@D_+PRhcLdASCZw8jt7MY;nkR-MXtzjL0H?TT_oUUUXO)#C#jHp3(#0E#nCjG3@b}K@u'
    ';qHjl*$^XLpU#iI{zqQq3Ab*V2%w2I2lJHC%Jeg~R5iIU~|(v3Gf@f8D`-'
    'Yu?iU>vZkwqG*3wtz>L#@^I&6@dy}wQ7~PPH=K;Babt}v|9S5ciBQ^mUSSnxG10{LyD4m}KeZAyt^4?8w5$Ocz)!6z^qEZ5aetxG'
    'Iv?TauCcnk@4M;q092xzt!M4R1bWmw;a%%%xKj%cv@)UlR0*8u-+P)%?b%ERtg{B?BK-i;OV?~5Td%dCk3)Ukn+L-'
    '+iA)nUo2{Y#eSNM~xsu;#OXI)r$u<XATJnhENrQ*W^@s7q#QXPN*TsvaOY&CbQ3};&-'
    '%I`WQ((|Mpi0UTIGCG@B3>L|R}Ax<U0UZ7xha-b**b6*F0aM#PZ2(6p;bxS9_vVFY2MsLoj7eCmuO!ZgRHZ8bYNZ2Pms{=kkjd7-'
    'H+ZRw4ICbQkx)!&by>N)^_T_xw>4@Keb!Y%Yn^?bs`O%o{NgqLeA%4RH8oJB)UFrQSH)52;B`K$d^o<sMg`blx(GKc`aT%AEJusI'
    '9`MC{jjhkW{%L+D9CAU+m%8)pr370A~5<JO&4CgO|Bm!kay#T4oFk*UbMFge_8Ce8|}uhYgyqGXPg{X6T3r6eSjRn?qWKJ#-'
    '#W}ou*v7lm=jYrRzKJj9sV6d_7nmlIvl;ZqW%-'
    'fxo+Ci8$gEyBji3D}a3HlWzQ3?%<Kt3W@wB>!gS!uD;az!EiHE7A20mkNE%ZDtsU(VSa-;D-'
    'hd`!k$#v>XVDK?uTQtzQP9M0bOV9o|61LjN1+9i8U`qyTu>&?3(8Nb(XrHzy3O|ho+aD$=J-*0rVg$-'
    'C+B2%=0xK3hRx17(rw>rpVRq`LIwEgg~>gd-Xr>WxaRQNBV^4=H*LyA+5jYa@ik~r*g|2?xd+2z2-'
    's3E`2h<*bkbzybl>pn$%iBi=X`5eYUy%G*2%oyN`z<ganl-a9{Uq72Aw9-d$VsqJ-NELA+V|K#8d<csll~R(i?ak7xom+2SBGq4S'
    'lY<AS%ft3`$ZS8Z#f|A5_=`|FnFU2%h#b5gBPMsp||B;5Gy<JrL*wzjX0zZv{2w(%#<1?0m1U}N+BSymgZAxt&L%-'
    'J=`HmM^Ox7W8AOUk9wn(wF@&CShiaeq-UUq?-'
    'zJ3o%WY~v8m6_KyTuXPnK1Zwpe>aQVo*>pB(^!XmK&$9}cvm0g{kt(rn5e?(+yw^|La4DxQb)U`ABztzQZdp3R(<9|;H!1{B?H!L'
    'Qduzo$RwJMxw%w<1&tK2ul2aeb%byvSZ7qH+&i?o{BfeR3e%}*OoIXk>TMItB&#U?&+8f$WO~_a`c8*K5qkwxinr;ifKWz#+Tr5H'
    '+y4}xD(Ae3>P!V8JKu`TK95&caH~f19J}Gf0Vb#7ELGeLDIlFI8-'
    '}7Quf?5~xP=~Kop;n6jaQ|n&+5a8U*I?6XW@>|c7s)^cJDuY2EPkLuQa>NQ*UlADW&07@#JO5s3<>niIRd?S-UlV2-'
    ';}wPvOz}q_Mq;^oW0AT@@oSOo?M3WeC+F=LbE@WOl`Ad2Rt)R#OsHIo;*3057pm^P`xAMqu5p5E+r#vZ=U<=>!f3QZEiI;3P2qB_'
    'R}TY)55DqXu%^s%YsheY8oQbw6&}`-'
    'Pm+i!!eMy6Y#VtwhP<2i|3XwTk4^ThmE{?{W?A!brUVOIlRZW>z9w_16EUAgIU#mID4vs7PaMk=}v#xvk<`R!XzEJKue1)l)0nfh'
    'cMgcWS)1D$i~|hczYsx(XuP-CJo;qmMTn{=N;UTwP<2yw4=WJ8_2LC`PC1&V;5bqH@A*>eANwaj3H+FcZFcdl~+p%%0|Nz1Whk9T'
    ')VAGb(CXw&zluaxB@>A3#c_Jx%<j1GL%bE^=FxpK~Q$8tXn34OE?BHLaO#BiREhs4n*Tq*t#pkRTv3{2llO7v(?O&YtLDH8C95aE'
    '{Dp@3(&24`>W1gIE){i{`on#%}reE{yx&i?Jjvv&!taf&1$C9ddh!&i?S4vt@EH(7L4wIMZXW1{=QIgx2j$7{eVW80$2cw>o{Kyc'
    '954hHod$P*UFDLJ&c&fkH}(YO6;$ITj9vv*s57=_9jVy4v&G!ME9_9C&HnFAyfN$9KF^O6X<q0I+?d^95aZpmEIH1q(7bJRl6jKw'
    'OnS@1$Nur8xw7BN`AQ*6(RqcOO`9XuWX6A5pXfVJZrsot=`h#+6ioRF%+|GQL;br{x2^2wbaUOk8gNgn(d$Nw%Q>nhrYkk?5etlQ'
    '9z^f`VrCYFkk=2>SA{V?*Zpq`>4Kf^Jc&QaI@&(#a%&ulf<|Y7Xdo2Uq-Lyf{Mk_VkEb7b4ik0_B9^ypWom|6LiRELD&1Dj}3(2o'
    'G|;RwwdX*srrtyQEoJmXAh0{<bcx-'
    'n7I8}jQHY?06H}J<Qu6WEefXJ8vQ{kg|Y%gQmQbI8UDs9JS(huQ`@{Ztx9G3_?TVfVl%goy9{~nR@UC}I#hlB1HNw-'
    'y4~+r^$i#9G0d%AlVS1D4~ljh9c;uy>$VlSU@^!Y7xH?TQhLZnRGnMw_^<cb{q-~|Q39M>*GP%Pt%J5cx=g!2vJ_&^(OSVEHC<W-'
    '%V0hOZ}f4I)hCyn3}2;Ve3=AJN<~D%BAb$FM}t&$w+`Kr>Je`cM9aR%2E+DB5Nx<lsqSOZc#~c=P#Kj67li-'
    '4n{ET%J@WAM9G(uF4Xzy0-l2t=e$3}<N}$(7!p)nefOOiN+goX~YUgIH+PB=&_IrKNj#6*12@O!i<}y+-'
    'tN0V0%z?X>C><J_RHvKvWcVcjSIMAF(L=d0=sSHtPO)qb<O_$H!}C%_^e!WKrhHBl9BXKezlvlljDlk#*~Fe!oq_wM-'
    'n4VocTJ*6I32fBXzwsP2oIAD@JgmVwCKdg<JXqVnHKYfR-'
    'w9iV_PbQ`A9BO=IatzMTK8XJ4<ZR8eH+*9q+k$asupL?IX`CTUX|o80hp<@4_yeHDGfpEdCwTbS|GhlWU{jdwHAsf!l|(>UT*4&7'
    's~d(V_!2tW)cU&{J-^ldCL#)UlKl-x%DjOvHYEwA+xsWsIm8U^lL}&<{DwE-#`?`IF|_>)wEKV-'
    '|s<VmsJ5q5Wc^GdG=J#Y&sBYUhI8s)_PvrryT0Y*wgL)Y{ZWPw2NfWP9g8F(%9;m=xvn^!e!8)tU0!g23TSdR0l=X;cgQE`~U|_O'
    '6X@sI(tdy?3*k4QwM;C6+V%$y)F3hhe;!$K#sE;2cck7_HNzKV;PE7|0(4+3nTcqA$zHF^`~UyORtSjpEnakGk?}F9kZ#DEXo2@c'
    '05IvgS&LGVWm8^XINI3U+btl!j?e;-'
    '@8KR{$$@h1he_|2|;^STrlgCaLf{APT6&nAO16Wj0*6LR4!+dK27_?h^Vi<4#D@!v6aCZbm%TPI414AGf3kVwoHRQi5iEs5v4+a)'
    '@vG6>wi!fdZ?Kk8s~R+TJdXhGxqMniTWy4oi(fvvgXyDfyiI$U35h+?W*L@lxB(Fg=*8M-'
    '7>$jY>&7awb?t2R^IUH~Xo%tlzp*HJ(APC%7suNPpoz`N=)ZX6wXeKzBW=r~~5NtBqZ+R1s#YQVJkdG$@|q8{Z_C?HzX-'
    'cB0#7CXB$B_g=?G>o&09_Z@?G+wksXTXB{{r5iZUR`Jb!gjbM24QsO%-d{D?dA-~fhbTn@-R0CfAl-Mr6#@7ILa-W7lM^-'
    '`)N>civ3?YQMbLp-'
    'J&Jtx*QnO<cfEi;bS@5Z2JXmmi>+0(a1z2@=Y<^TsgpoIPulgm8m>AZzVh~)1GbJ9O&d_9wNA;wrZzRMouG07m*s=I?3N44G9I=Z'
    'mVG3Fz97?qEx5HcO@_8P^L{qKDg6Y!-'
    'LTMzHYFAsUtiQYmUfGY@;IILffG!t@M836q?=7uf(H%mCM2%hRUwCX;TK9ff)4Y~P#ZYjI?dVjzKZL*3|dcBy&mSf-'
    'm~pYoQ)}@6J7!NH|zrE(&xsrOzE#l@P^6;D8B2e7Bv`Us`9PD6uFm`ZlA$=Md--n!b-'
    '{_gLyp;zupMizJTAkf03>Bb4ed+=w%d9_VgX05McgQ3oYEvB;L0=CqV0;t32gITkX~v9p1}A%w6dJd7Ty@@WJ1afR}Lt{?r+*9Y3'
    'Spk+-Iu>G7o6$n?(N+FzT7GUKPDUC(@*e|Kj=xxUVFd6U9=^KlgFjMy<6t6qGx*OHIO>ddvx(tBhqC&0?DHi|+iewJVwaius--UD'
    '2`Yhv!tE!0l{MggvA`M%4)oRqZZo+`iHg;l8)lRJOHp|Mv?*lsHg)<tIAWyKdDY=Ye=z`8d(>20rY{cHxe2tvjBcA+>KeAbvAy*O'
    'MEUp24ib)nYy^z~uk9W<{DBxL4r#1yN9%6vnaC>U}YPM2?HRiANjN$WT-'
    ')f9?#Z1K*eA$r86Qe(2D7loicINvW}bsPVE0NnDEdS<ZALdUjfV`FdWERqk;DN(;`$ln{W3_2*7$E(A<zRalU2iU1iJDqN|^<M}V'
    'PueNGUaAdbORw^be^tZjg_L0i5!GWRejL@v;ZNM{T`S|yxy?@46$W$A|I|tKmdZe3Gfqfn|Gp)M$Ggz_5MC$wQY3=Nu)#pf)@Y8*'
    'KMY=TlzpDCjl#JJM}r3jEJL6q54=QPIJa&2cHcSO%U#~77X+CImjS54T>@^}><0Ey#TP0Lcc7plzSDnhRNLh!dyk#weM*G;N)Rg7'
    '&24xkioIUeYQJ9cLN=e&ID)m<9WZ;c+MZ&TwXId&_vf|pU_&FH*~jp0wvOp9gRx?zRYJM#Uu~^=+~Ud?lj4DP7eZ(85sXH0E_7y-'
    'c7*BSCpShlAt<kBMXSP(PI0_l-'
    ';RpjhnL+|cI~{D#3W?L*kHlEWi%`N<*wWHr&QG9M1<aKFojE6&Br{`DqS3bKhBrzMVd3a@UvD={f^h)n6+M)ayV#jOU)UxC`K^n4'
    '@xk0SR5_4F1po1WOacvC|_?gMv|#Ur4|5#cKiNiCH&HSNgcGvWfD_Jh3Mg<P3mX!=bph?^f2aEvZCH!pR=>QtrES96+KQrxuh0~='
    'hNZITD^J44Q3&c<DwK%4nWTJE?tDLyqrRb=DXmmhar<MCv*6UmC^DkTfU(-3lzOp7n`@MG8Ga%RJHegGA=*+`TY;wX@-'
    '3(vZ8ZpgZox`FxON_MDzDxgHyBdxGZq{H1tk@WSKq(^*fIp-'
    'S$?Kr8EETGoA+VIo)5$tvFRz+e{`qRH>TFyiOHvakcXaQ1akT8Lzc@4dx5O*SefoVq2waOR(a}Oq7a-h#dJ0x-'
    'HF{ym*qcQSV6EP^FIt@ml9XWAq)d=#BlOJ>!rKLhxl_7{phjK6>0C?z#-7-BnAvc-;#AGHf4=-'
    '!DU7H$RV6;Pt0e0WC1|hZD4)lh<Ki`_0G;h>#nu^Hi%ftYFKpqZcj&Hm-'
    '@yWm*4#@pw3)qcgKu4*oFpr@Ze{^TME9Hs<l@+^qvEs?Up)F;t5GS&sR09=y<-bVS$I#e(pM(wgUBB~M<=@xZ-'
    'VHT?T<MS0vMA=c{!xYKI@$XZ{c7etCzubQ?{0BFC#j{0NU?#e#>#{1a9C@rF-Gf}H4H_?AS$E?(jKNa1YCxj8Nr=B_z>!s2CuE_^'
    'p92d&K1~P#Hjb#NR8P3{NHJu|^PLK%~+vXMNe~wmq)oZ=^s4)USi2g&&s&#WQ6S0O!C;h41JQxYkTa!YBdv`}TXlQlqu22(BtC2#'
    '?@)O0>UQ>;^ybH5ENtRxv&SUmoT`zdU_6THJZ>+#BzlePQr|W4h9;L%k?Py!4c$HprtgG0v*`*d!woRKlzP#4q-'
    'w@QRy|FIOsaC(R`ScUo|1^v310CqmcH1c>(se<$`aZgV#b*N`MK^90K+WuPPE4Nio;j?K;0Kl8F1`>Nw7l3KAMYQjVEQ24;#}dat'
    'SV6el?KH--9(w%-rC@&`5`RJ3~{=m>AFL%Uz_S;6kfN&<@6i+-'
    'ZQ_aE&wS$h$pMin$6oBJu|2*mUwi&L(s!twa^Ba(T30US*>BGq`#|m_fxQ5f^68l&>l7{XocZ05D^&@b~q1`*Yfocm2aEZC?&AX^'
    '9yn=*VWb;_a}#vPxQ)2%8f42vdV?@s&jNpbSr!j1+lRx!k5bKJO<}cE<_)!<Hd6VofGef64hO@=&jdwJDpk|!-'
    'Z05DHQF>FLYtK361V(w5*_^a`a}&;UrmVa8?(@I;_9@q=L5Q59A;_a`d*w#ryk!7RaDpQl~~Bi}bi&!{Sq%?cqNVUHwDER_pwN7r'
    'oMJ(d#||Bc{UdrE~31i+5b~9dD4+R+&44I~UN;L$SQdyXmnx`|A#dA3XsFkNMfZwyqv`a<3OTABJ`(Uc4s;JKA2?@8Tsny>AQeaq'
    '||Gqld?-|HMuP{%ar!Ir@zDn<Z-W^3F6LHE{ASv^$+^Yf4YU*s7D4DeejeBoS+C)TH--'
    '+7x2i%#_kT*>yTp9tCo^#_4_AY1OOyi5;4)B_aPksyJv$(4q={{}O<_zy?zuEvx<G@n|m~?(yo1*THA7p_#|ZixxKN<cJpRyfw<B'
    'kzcb$&SLgaOHaPEo9u=BM{thkHBhi*#*rI5w>1DoB1X&Jt2!(Qcge1uk84C3U&IplPk8TFBOiQpFQ(p}wO;nbo#7~YC=_bl58t?M'
    '^HpZ-pv%0;aF>32U}A#}H0WONKprEfaT^~W_r>aYg{z&h{<#es7kDur$74V`wM`*DZoT}AfZ~|M>cOmB`fLGpKIS&KclW$7y6o!9'
    'C)a#DPV^Wo4xqwcSxplQM0U}j?!_Y0_mK*88A<yCB@f!y0`&I}Zzz6%9V&rFhDo1)lX0aKH-@D*t-'
    'l2=2DP=dM@~^qyMtTu>7G4!Xg@pkCg1EVwiP*5Qyb5ctskGe5;<(mpjxL?>hMlU?bB)NxfV=!+$dF9_WfiV7$*evBI$fx)Y8_iD!'
    'ht6AF&5S_{pdrYiG5#FM)nnFz)pP;lyIL7>KyA+?}i%P2X)_g$uj8dN~Nvdfso7>HfG@E}gh#9y}x-'
    'RN5FLt%}W3;WSe;e%W8n32S<~73bD>K3W*ui!))6DB5Wpc*-Op&TFy5-'
    'YPCOS_t?1p>YU5)%I@iB&^ZFi`NgbR>h4j1}`Q;hQF!ft2iM=-k$DG(dX=QgjhdxeM&}`40Z-c&-'
    'g9ox0q&`!2KnU&+>Hy9V<tn3^;=#t^}padQzE}aL{ioYsseM^qz`U27xy6I1TEfUgfW~V;8`E6E|M4z_kJ$ogm9b<gI@RIxiXhi&'
    'z)Iqe+Ul`{Z(%nS)hEUIcO-'
    '9Z$`3T7U6vT30hpv)eZUZue$bEq>2hgL_honAOxfkH!!8dN_4`eSGakTpAxvN*e`;`=HPn?|$RdvU}`5;#X<02zpP<*%;{*b~R_W'
    '`asX14Pm9~0&$!3nOHJdyn3G%jPY~X@{pRw%P$bx-AfHe51fU88D}J(RLq+4KYHzl;E`OOR*zRHzkesUvDs@a<pi6SkZk=J51hsQ'
    'jM|GPtHRA8gYG`&eCPZ3KAyj3!$Th^lxr3|#PB|{GJms)cVJ5G(Sg&uwW@knTa-'
    '~e+;;D+kWKjG7RwX(ZfRN5=+%?o@junW9={dPW5L|{?BgnBV~uo>qb9mLeLCvz;^%gBJ{Hwi4moM&bd*pVyU}Sg9&A`-'
    'w79nqkqC(L)wHdKU}F1v={&+KEndsnMPQjYn|$S4aHnLr-'
    'g?>)R8x`R)~);3BPJ}5>=#{Kt||MYGX{A@xi{{PjJ#N_u$U)YFQ=>*WaQ6nZ?%h+Lvt|z@tL<(qpY&lz}DFY>e{Ed$FS0+_TBmge'
    'GM+vE5nB|Ba@dOpWa|24+2rxSx=YsCKs1kSo?Eak)d%_eVc9e;Ggdg!nnQGA-'
    'kS2G&B+H_u4GCe5_^eD_D#72aO+37h~??W@z>U_5?=Th}IXoy5}v(GyN0PblSpsfmJDZlU>KL_pW9)t<vz{^XTFjmvNU-lPz|>Cu'
    '{`eeQn$3&aH}f;@`yi)$9#wOG@~A;yPT;`euJ)RZTCYP<GgWv^PdR4zI=e2V|n;mz#I`tl;VM({(W0Mu+1<5TjMg)Kh5Jb0&mEtn'
    'F;5v=)slYtnPDxxmg(`I=|dk)+ATqN!)W=V7?+Bbo3oyMInbys<PTf?8ebvyq=QTie_BbeMbkSgO~SA9$8YAYKJYQw$0$I;{Ty)('
    'wL{o55@71xnPD-M3&aM6nZT?$p_iFF<47)RI+nUvzsLb~hzEotnu}D3e^yYxr^c=<_xOZCHpUH(aGgLHif$-'
    'nqs@FTmM8o5*R?`ii0+)M+^7%I)aNQ2p@M0Cj0%j}ds-uSN9xT!RC1QXu>7&vtjQ%jZi8Vd~wj;}#90g=qMxtg6`rrsb6P%>4>~v'
    'P*5)kt%DeIcnUneNt}x(44fGYpZA24q651XuykOEb<izyv43bPEQEb8Lxl|qPU=9nQx0V@4n#-'
    'C;jF>JEvh@j}#wh1OxdfSduE9(YsUy?{>mohNrb2uBa<G+hFs2*S21ndiE0&$Zxko1-'
    '4$bLHBl8w}&`1FHC#{Y>_i`TBHME^{LU@%eA%H%^l|JY8|Z%UwjC!$_EGU$vHADOQ=d$`=|}wJLDI;pm&_hnpr)H3@e|s;*q8ROW'
    '_@1P!)PRQsMr>2?e7HJw0XJ`L_BfGVpqLPgziZQ=bpS{3wF^a20Vkanh>-P@GQFan-'
    '1I?x@+0y*<dl_u3fK+lnjkEaMeFBlHS++y3EFctFhFhz>^aTo{S;N1IF?tU@(-'
    'cKD0xI&eXcy0=A#FWqu4NAfx(!+pz6co7)Q`|xI*FhYU^e#KT;<d#?EzfaV9pslW~Yuv2&800;>u=RI@al8!<V04u}DmaP`)=pe='
    'ka&;YU-C(|&4+mVbRKu-'
    'yLbW>E8b)^O0s$6k?t@Cts=TZ{l8ACJRUS#p-7f&(xi;iwYQ$myM|R0ehC29iCAC>VIb-P)M#k6O>&m!>18FwIpsI-wQRyvZ8-'
    '?9Q9;@gd}=&X!g@mOHgU0~JRbnOc=-F#8)w@t&@D-'
    'K`!*Gvk_5S2>zi{@tyaG3L#SShQDTpkU~C@uOO}&Douoe<F!ZQ^(%nnB_DaIMRW{rAeuU1r<YRt*-'
    'g_{DM9*>YJk8j1CwnyLcP4c*+bAY`=ehHj?X9PcuD4_aBbS%Nq^s?IHO)DZDLKq%P~TKU;Au8e?hJgeE0Do8c|k4l6J>Lb#aqC1i'
    '~!#zMDBOfgK%2*<0|5&6tOI!-V3EJ<u%?z8|%cFtyQef=#1l-'
    'w`+l*G@yH*ucQ^j2$10omHDet%IB5UZ|{TNS>V?Bt3{<tKB>XcY`1~0)Ua|2MG)#VC)DglzoSC<RzAk3IVug0<Ras*#;bLF=5bKZ'
    '?qkaCwDxDBwCsA>>oi!_M1hgVX^lPFlx*5{^EU}S_FFe)((J5!^wKGpJgxa3Q`g#kuKRRfODkHcWi2_RmX3tVp&TMTs3aokfJEW7'
    '-=E)uumAl99O}AeX7AavN3??JeP0G2;OVfptw#)S;nLZIZ@LH4Qoe%x6Cv}#8TNkrJ>P~<&`_%7_$57b@#6(5(Xc~5Jb2Na*p<GR'
    '@%FLop%+UHx6AFDwu5m@oKnh^H=Z|mhw}zfkA>3w7Uia47$4x#yuY~JwzzaO%5pq~`qw_Xtdm2YR95T`)}QCJ04?O#^%X5~yQB*@'
    'eQFspcs-we%bo}q%Hm13@ytbAFVkYi^k2B-'
    'Y8@pBk0;s5c{>D+!3t}3!qd#OK`q#3cafI<N}!{vaGwac4d$2Y_K9mt_TMVLy!pNll+|u{@h`-'
    'rz0v@T(<d<LbirEQA(~g>GDxW%yeQ7$J&45x9#uM?a+*SR{ec1EeUY6b=$*t4I%_S)-'
    'es9*Vh$?V^N>eEG4wkf``0iV9?BOii;!XTm|r&!Z?@0YA*vqk5(?-'
    'w$~GXY^*XmIi=PqC9Ai3iXu9QL+}=(%GdMe<fpv~Ilg~$KGa9dakf1dX3W}w+bhA~`tcpo(K2&YI=yi61X_cZ7FX-'
    'O&@&{BG)n(L(+VZPXy9<ks-'
    '9ORc^55WeaV*WVK{y>uuWouddBPTfdG^>F%i?vodoQeK`K5F5b&IV6wKeOt7}499(Wer;@pY}JspXl5#oT67n{qd1^BR{#YLs7(@'
    '~4wE<%y=T_CK#V<dxnlJ)1wk;~aq1QoDhdk9FA$U>jCG3j|@d2mvtUclSi;ZO$xTFCW%trIlr2OS64%h7I48*EO^W-'
    '|_pflQTJnDW^QI>%GsK31VIUheh|BUNI(biqh^+Yh*?Kxxh8f`Fb@xbw}q|iHbVf7Hs{oJGJ}4b6&f_c&FRa2NMR&x)aN%AIGc3#'
    'M6<c_C9|<$9{HEm)jK4A1+??h|H}?`5J||S=|gALK6-qb9&|f>|ad__w=-'
    'M0T{kEuA{?=M*x4(u1Wo6u__NzWRaKYvB>Q36UI}rwP$0<EZWHJT<!dU?ql;X#7|=!ev9u(=h|R{&aa6L$EGp#btE|UqwC7+Dd+j'
    'w^$g^`0(f-kKi?KUEv+}*+az91`;(%v(4dvmFZ6Ps-m6~@36Gt@`9C9Du9XJO{_$E~%5*Sj9>%(@b)^)4{q|$B6LUC&_0j@l;V0-'
    'RI9>YDhX|8EQP8(!tR?v2XiGDFN7Gl$X1R5MugOfS<72GU#otXK;VBXKgT%Spg;8GBMp%0@rjmfv7Jn!k9lpNKDVNGe7APHKLE1^'
    'HXK+K@*T4OR&#v6pfniRiihTpoMpBzHcT-gG^wL`|T>Uy9P9Yc+xS0B^6lA*B8}-BZ#K4at+IRz_Q`X?gq-mahte&9EHs}`J(8W6'
    'oI@tbDf@iBvli3{NLTubj{dP9q*ZS@B;&J#<ULDW}b)zZL!AI^~wAk(9K$VYIc+juhj)M(FlsRN9&Y(?!JcPYg4Uh7__AwNopaC_'
    'W3!Y@q6_pvr%#KE1qxtI1y{@?1C)Vf!z|W^bEf+qgzB`jGI__jZZ`@TG*5Fuxj+Q4vU$@_E8M`xI?>Cow*zE}zQ<@j0XfzMA8q<N'
    'y_jP#5h7IlA1<oe9<M*6oW^KSQGp2Jje3T$+BR_Km{<Cei8v3qec<lq7wJQ5Kp-'
    'zo$O*TGor(ynb+GHI#rG0-l>fG&Se;Y5z;i7)|7^uDw##~^h*7W(>>eJcv@$7c<#PqYFNVBi@kc1|Mid_f-mN?pwXyvA^1U#BuQK'
    'p97R9#Ju%~4}!kpE~t7dM|!ISB87=4n}JhD)$DB3pFNyTY5g6S}RScI+)W0p2zG)6ZmlG@a64z<zL5n(#)|g&#PA1o;nDQ<@Je1u'
    '6z_o|klIF@Wf!K?FaU$!%dgJHg@EnOVhiK(W{N?U4CfaoS2IEu&{^Ou;zw4q9`;O1o)aM&ka&oNv`y^+2~T9w%J^dc3Nd@-'
    'yoC_u;O=mCe-opM_T1&<j2;|2>X&e0m~swwD=iakW3jD*o=@c?3LFW8Oz`wql-&EvX%cim~69%A55Hex!QM39F-'
    'rcLE0S`S&8;q;Z9NGDeG>G<5a7x-C)SPESX~q^lb}Ooabl=C=cH&)vxq+^*hf>1_(ry$rpZ*@-'
    'c4NhKZv^QT`?`&%y^=z1rpEaA+bwZe?JQ>*pALpx}#M=|hP$_Tnn<FNE0EU%>gq4sbyfW2A7uNC(8YEk0(K}Kp|kVk9-k{T4~-'
    'F+qOiM2x(!;3|K$NA{-'
    '{2j6(coPf>g`@lAytkaYSZ99!3YiVt@+dmnLMcYCx=X!>d|X>p4DzJc$d6Nf{*~UNdPQAxCVd@mmkhlLFme5=-n-'
    'ueM!YT^aoTMN^8w$XDu?9(G?}s}kBPnJ%_o}4{~M6HzpLos*pNi7nqD$`u`KqfPT`1v+(%^u%4VOGKG3c6=I$?ovAZUB*XZ$@tdy'
    '_)?#>Q++T;bZ?P^dG9CSiZ$LvogX>q|}2v@{0e|{wQZ%6Bpiy6I$A9hysQVY#y!^X|tk}Yrz0NIoCo{8A?hNq&F##wu2@<7GeMfL'
    '>Rwo)K&0R6$w?z6#+pZ&m=3Q>rZ_Oqy8lf{<Ws+F0K;J9H`(Wn}X)%&Jd!K`d~`36Y1UEzP1l^HtIR8rYtBkvNmVr7Ywp!ppq&T1'
    '2EHRL)NPx*TPXU8-XaD8$Z%;U<g-FN4U@25oqUw?lwPe`MR5AAJmjnR%B9}fIRx>uECnN{Z}=%b8XX8IGRdE;o<Hm(s}X-'
    '|U2dD8Fk)Nb1i<wHZ_tmo<(Gq&Mz8jpA#^?AIsNId;JyaCSJx!9Z}&DDVJlT!Ja?vFtCmV2K=chK*7?&rBWIm-Ha`;qo>+xQ%j#y'
    '2}MiFc1zU_2q9WM1`V&R5{a#wV|N$+t_&&c)ikr9F>uttHVuis-'
    '3WwxoE15EVDlf?g@&$#pqLqM|*uzSeRKw@Knvt~vI<u40`Di?LAdzjQ`?MOgnEl&^9sd)$0BZQjcjc!Sp$2DfkF$E(`A>HEv|1$O'
    'f=Iu+;H;T~rD=?jkqnKQ1f|Fwd&qcPZ2+8*xj(xG$SFLyg#&Ud9|v+yU>UnrcOk(#GH3LP?!+oQ86DSOU#F8f=sLts5P?ti(UsTQ'
    '5m3;c)=x$!36`-T#iteQD*`18Z)CiH5<-'
    '2%WPS5=Jrv~{RQkOane)dA|u>tEUGFoP;TT;A`{aNQa^qn7?Z4e)(y`S3hYg_MA@<zDz)UCt@Z#d~^wdhuPJ$>Ywwu`ogm8%@+pN'
    't1W@(&5YXd+<<=hz}rR{Y|UfAC4t>X42)h-sOzf=kMo_z&eOf3yTx8-ti|o)mYE=2XSqB9dMZl>z6oeIu-'
    '}OsEN=Ub^Ew!udD8>zsW=44dy_=?|L=8py+tob$QOVSkipRO%*zG;X9?o>->~$m@;ym4q0^-'
    'qZAC<;&DBwFFo|fh1hT~N;!Zm3~z&v&H1?Qjz-H4e3JwhO}7J%FxV3-'
    'v$c8AFe(t1UdaQs=pk9~`A(4`x0sTA@S1u!n^>ENYqSOtAi=B5xhgj$(crK8{O6TN)z6{^?_O49@<*M;5WM`h_D7Mw7Gxjk8P?7Q'
    'I>M&Ed5KRSYGN$bZ9<CN6QNyGjW6@-{t!*e=4E8MgthvdYrR41QhGlpW#Ie0K1};8Z2r-'
    '34f4%~qiF*NHu#ZTzaz7gnXwbzE1lD|XK;Pg;YE68++REqKR}z#^wGMq>8iq)KU~-'
    '{>#0+CxfTb`Ga|8aRG)rMlb62++pWPGJS&>=FNFi!_5Rqo0J%LA#M8GwWiETEGVwgdo6n@bDxH3bX4Gi`rG4@RTU%kiwC4oWOc92'
    'Xqw^L0D^C^!t_`>e*P)+ng^5C>7k{;6_*e{j%|fmJ6R+F`a&K_1^Rz<0^3h3ybKz!0;+$j4NwU)W@a1V#TJ5mFR*~GewUi$*eWD('
    '8r1i%;<}c2dX2xv&=32Hc4&G|5Uhy(IAv-'
    'l1FUEv0cdRmTJb|=*1>$h~HLjO}9WR4P2~WYU7){_#J$Y~CTJtz8bo^6c)7|oYGX6dKvjr`*7QWlG0=4m->V6BMs!EYm-'
    'g8}vfT+*e%RN?N6SE>hhZAME+KM1}Q8s>bQ*a!YUKYN%F1C{axH~CDi5SI=8Di|#0jhpArQPX4^H;spKe@0ORW3@#mrcA^0lNBxm'
    '~;Yrp;YbEpBPOv$Hgs$>o0RFm0qjrmtP*MJN_Rdf+~~o^4;^(36A*Fbo&Qh#KraAW){;|v!|usExMSGiw^7dCq9AoxUDhDzT1wrN'
    'anNvS4_tZIf9O0U|!o_daZ7|O(h3?rWpFROAhuZT>dw9+U&WF$p_*e6Hki1>e2g4FbE=8)yc$i0RAYI<>{(&w4FT+m(TK?*w#PN<'
    'FRA6;g&vU%&YP&Aa&Pv5cMVRK&4IV$MX7GSMA{7mfBy#8vHXCk<K9S!jP{~_A7Qi(EbYk3SwL3Dz<~LTJ)*9`Q_9!&HAQ+HU)hZ5'
    'v(<2=LdsqoDRnlv%-JviFO6pvwo)BDZ6gK#ES6w0T+p8ADCd4Ufw|aSDKA5O-'
    'b&{&aNj^;~P@0Uk@_+KFjA;@=)g#v%ipS&+BXA6?y%1*w2zMY>+x))!mog8g09gdkLBHoosRE&bpZ?6>mMGXT4`LsT5Jb4%hJXg~'
    'i5X!+Uy|>HUqzZrc0fYyD(3@u@o>cY0+uTjS0(d8g@r#mhhH=+O@Cj!BrO2{Kxu&#}1V>9Z_4gBu%UC;l5>zumCSd8cYT7mdHef^'
    '-=8FWe$NBWc$;Q=xM|JBH;iewaZ|nE{yjlA_ygjqHb{OR-8u|NE*=Wfdp`=ox6X7HYh^{N~19&lq*PZ{2~?B8F2wIdbQKb-'
    'CG>Sggz`jaFD`V23mCa<ipHa^<o!r*vX>@+n^CXt=`atZbje=CNN0C#CeyY-QkZtMzX0%g%t?-'
    'SWe9wEIiM@oJt8KynBkYyH~2mi8U-'
    'acqM3Ewi_Q;)^dBeF_3n4>oT<kztE1pSscWG1e;nYuM3mE%mBxKi%HBziy#z=p{R&znj1BW+j-'
    '+@JXN?1T%h%L{vuN3bWlI{Y6zx0@XWCBF)2F59FN|Kk(TB3#eZDyQrV%qMN_4WV)s9+2$@mGr7%!%O1VGtfo<Iqki0@8BLb1#%~b'
    'U@1f_mv&4J#rZ8?*qAPxI!14N(d!(K#!6V)#G;A$eVWn^UdnOcL3!C7cfz7i#&BW=07?7}UL{hdNB(^*5cN~445XT%5*tNWinWNc'
    '!mTSlv7-'
    'Q7HjY_<I>aX{o=47~?6K!zaZjbWgJi*c%fjnj%Y&ZND_#bp)7n|SC8PT@lOGm?=@KkWSfl;t+HsX=ebXBzccj=+5EPL0!ExO}b{;'
    '>ju8l)>nsiUTP6wIg7A73YKX%nB&XJgz7hwR3`Gt>iLB1uGz{*J{t<^MGmgcf_sHBCk?)L)uc9yD+=PMpHH`aPsJ0{QYDV*S3@+k'
    'auU8%TA5d?eC&G0K42O1^H(wp-'
    'G>yj?np2hN*X^Yi#)77IiTplyloy#VMlhyQ7EZ&NSl_KvypmNEOK58P4TTCd%DSbg|4gv7eDqZ(A-'
    '_7_v$3(#HFr+kY;#f4uc=?749-'
    's7qO6~8I9^zF37rg>wXaedo=);qLcNbSKrReY^J7#)1;2}{=z(+<_!DVNTJ8QXGy+^uc~9+3S(>BO<8(ql89<>vkPcv8>BD>uHNl'
    'NmzoGGHx8|0_J5*=WO&MH%VUK-BZT`Ift_IM4lg$)dfMTJ8j8Ff@mkDZ@TqpEEdb-pcc9<@?hwF*&@4gi9RP%Rsw0F1+W>YKhy*4'
    'NlJrKjV}O^wRR4z_#xb*3w*1PL_{vpIw3?HXaIWJ<YQ>eW-'
    'Q&PYHJfQX#c|si$;D9*R6RTx1{Yf4q;|HHQu7v$3_$egdxtOKg~EgYGWRNz!`M$@8P#Clq$sBRv6!Jd`wmf$Ac8t9l1Zg2mxbEh@'
    'doVVPVmIj%2_^;EBdzgTW)^=u7g<M(dO90g)q4c1QK)XsPg${;X28{-SVv|8KKRsjDV*C~h2{+<`MgUu`%5Nz-'
    '>is%H6s?fl}YSi`bdT3>K8L4#7;B>rGnaL!+@3EbCCfNIMa!Uf{LUf22nPo|9_0-'
    '}}8pyS@R^g@iJAFq!GKME8V3+Q&M;6rL@1UZP{r)%6ce>xo(;lL2@96F`8qTly-'
    'q{A@&!^d8nl5_d(FAP|X8v55>UhmvPA7`uXvg;B9&5{~sRbt`zQ_E#`&8w1X}EN59s0gm>z2C>>JdthSiJj>uE(1A<K25T=w|)39'
    'HUdduPtlsu-Y@u8#mmKDw-65YgH+P)c|a%6K)jR#0K_~%}f6^fZyj`?%(Q@@@!D7+F-Hs+wn$;Ki|vZggUGTHmv8-'
    'Sos{f9J`Ue=)KG3Xvcr&uHA8yC{bIlW2@onPx_p*vh-'
    'b&?Noa?*8BeVpBh~N7XG;pOo2tZpF%YaSRPr~<=zvq|3#boD}O%Nb3N!~3d0X$t+cW=b2aESCVvoInl3*3BRV<ms^vM*hyLO`gnE'
    '&_?=N=`s5$5-_ot;c%0GI(zsO}!Z8q5eWMEmTC0{dU=HBWn3M(|JxBW{Nok|_5c3SV?6Ddi(V%V@&in--h<4Bjf0qS(dLiGJB_Z^'
    '3sopsPw)^C~(Z2WX9r`DCc{4DvgFc72F{k#Y%JVg5dZ*^TJo0MIET}Q*Md0DHG-'
    '!fYPIyM#pxi$*asL)x5oH3yS0L}Vh^o_ib>Jh*x%irovPD<ZV(738UxlyAv!BA<L)yB+D`A)aUVT2aybiFrw7o1w$^D?@g%N4s>o'
    '9sXgt*cU0f0C^a7z`-'
    'k6OAgQS?PCRh2@@z!amg7&Xuhks_ZcUZicP#vm*VoB}NAkhv@YvGnnStO}Y4DIB)>0Ow2u=A`5#`nd0y3*vpT{X+i_h!nv%F&Bu2'
    '-cpA-`sM)KfsgrbBVFK+HiUsU}K=zF~!9$;Is&}5k{$JiR!NdMKRg<(YTjnxvzN=W@RisNUVeLBWvg-;RJBtw*B@wRG-'
    '*GbB6mx#m8=s??3sXnCkGssS%2nxc{yp&FIIOx+G1=m`WG@Uku|)opc4UOu-TKg`Qt81*Vj=Zwi{Z*XP?fA87Fn=wgLwb9V<iz1A'
    '6tSDuxPlu?%f~_n7cMIssJtb9kq4?9SWCM3%onSF>vjxx2xIr;_psIdw2P<sw1<%%1bcz`ENRcSk?EB`-'
    '<cE8sZ5hyG72oTVdmurNL3Ri5FV}7jmUGtuyB2FvwlRv0mW|quSpNnGEhY+u_C?)JeVCWzRQ{lfyV;D`${_AYkZVhmSIr{@In8Om'
    '`?4#!zV*Rz=!luz*=LF;NBg9!j@-pLI|D{h|wk5wRtjCv^FqUQILo{rS4Eh<iN*AlC1rfN&{Mm-FRU)wbtKWagrFxlfgK|MhZ8d;'
    '4A&LeqGaI%_-LG{((_$h`oXUBtCCTbr-'
    '1w*)FGSTgj+>tcDU9pBNp9hv{@Z0!)P*|Ey(s2D8SlBZpQeRZa5Zh1#W1<f0T+U(SBjI=+>mm78MDNE|Z)d^JCl-'
    'X;S504{!>hET+UTHy=xKdYpipOk>Y%Ze%NVfB4C@lXSH3tv7x7M=Tm#gP8uC<TX<0bVf*B@=WHD22($U*Z5(r?f_$YOTyO{iBkUm'
    'gJn|2|q|p8+<z8}()y)~4?cueMOG#duJzJN@n8+$SVNzEDsrT>eP;@z(h4*3XX67Ki2Pa)^@i@35?^VP3~4C2KM#yIYt6W+e#@4Z'
    '7spo3y$+Cgb^Knr)M9YkN77h|M><cT#u>2=;3SPg+_Ey8_Ot+&MmFZF?_Y8Tq<MFD6hT_X_HDptc#nucoOfi_h1dF)!f>PAB)?c)'
    'lCBn|_1=I}*z<Pg>PMU|s7zYqQYm<_?k|lh>>G_uy6oXHoB9$VM7uavO5h%ec6{gf4D}eq*=8uPZ=4ZOZFgKw4m|fwx`})r<c7Dg'
    'Awxf>EU--yW3klH;uU@{|>Yd?!sYzd2>mhCVpqdf)sf7LWOAYVTVSeEUxMPU_#i31!lJ)!3z!Zg^TWV~02f9?xElFLiv2aNkXET9'
    '{VleV??<Es+S{>$-o-'
    'hz*{MO5LM;9sW4T&(zku(4JVET}iuo?HL3=Jn`H<z4QF2Q<5W63^tXo^)u;~4`kHrggBkt#A2C#ZoNgbRFKeNDkRIP`}~aYnf-'
    'o7;?|Z9<rSDqdr%7h={2<>V6W(Vm%Au);xyX~X1P@9ZaX}O|Dm-fF;?ctX-jO63uHYf7q4{wicOIb0_J>aLXWY1k*&3H<W}71KNF'
    '~#Z3(QJl+qzdO-'
    '=@pO0Dw0$%ZB&5VAIl1}ib7)B5_%D`$YDB<8T#0o~CBcgzQCF3iSTE4?1q3ye&5w*dV5^ko7F@aN7hMRaz#VpN|Ue)D`-'
    'ijP_IP#@_=w0auJK>Qg<U&ai>taD+6y<=D|W1b=nFk;kK3upSR`K9`4{RzNSn4aK*U<M|Yr~7)1<N^TI^iUj_3W^ZU)L6)rLyCOo'
    'V#{}Fb>UqIQ6}f{ux8BvISdfY>C<bZNm8X$pFUaY`Z;0Kbnjk!of&s+f6_H03zg&V?s8OQjPtm{F_@o7DeK%H3q5jaM0w|Dq}L41'
    '_&jjCH2{m{AQ$3Ow4dn%@p4%o__?x^mY$02PRVyy+{=XToWjf>eJb|oeO8!vZ(PA*3;7X6^hENkJswA|oH~e~hV0|^;8uGSHEn(R'
    'lzuuk#om>d7^e2<vXZ`XvRu%sY%cmAx_NJEAGY_>p4aT_kFnM&rl-'
    '?WJoO<|`?UHBB!`Vm?>6W6kK3~E+19Bf;gZHNj;N^`2a3dimHU39`LEf`z#T9?QA&3uxa>q>bcHrQ0t^i0#%-mj-EtK2UG-'
    'i)NX7ag&Fwk{)uG}qO@*v<J4YW#Vk?3dr{W~|T8&l-'
    'xy@lXFJ0S&=09(zH~yPrE=3V)b}(*IA6QNIqVU4RH(K|dZZz(vxxUyAQDrR*H`|J+)oaJG6VB4={dnVq7vvlS8ToB!AzQaFW2U#A'
    'DoWkqYNQ?UN`bW27ddSoQW3>;DP3!|um7F&TxHX4^U%w?-Jan7^A+!t%UX~m2s0Altb+OdP?Kwmi`CYpX6yQqZ?-'
    '6pAOCJ73`~x+eVh)kOau7fq1Z2U7|7u#ZhjxY@f`OCle(U*+@dm~4aBsgzQLUwLmUP3j(MFR)0KCkeBvA<$x?pt;KCOSYxUALU4>'
    '{B;;Q9pzh%ScUh6qq?H^CD(=qS77z5eHn%7FwbKNO3mYi@mVbzL^Ap)FU5?!u6ZSe*^^G1JT!|8x9xlIvpL5Z+YcK0oljmu=v7Wv'
    'qjeT)A#_B#JiuBGIc2D86eP``ZXEwo+3Q8;Gj(bS~kUo&^xKUU^PcG-7ZmlIlK@eLVBuu*PYvtR-'
    'w)g85BQ)XsK`;^`X9TNMcm(nvI4wR<}p*ca~2S9gc!po^V>h$?kJ`c5C?VO}MZmHZUN|MV{-WdAquiyZwlR-P-ZJoYP;o+MT4{CA'
    'Q%m_s_HDlW#2rj8>i^llXo&Sqq*V=xynXt;hh$W^ZZoAfODai?m8**{`oa(jDn0>4o$h=oYv6&|y+MChM{SB<`9`M;Pr1^sTj<&C'
    'zbt4<-'
    'lS{hC!If53P?;dT*f)TivuVlVo9E+)RE<DCNs+(zQaH$}lZ3m&@^>bsgj@Q<`!jWpR*T!r=a;nB&jw_dZUvL*ap`p=?b09SzFh9P'
    'AiU~RH!H~-yAJsGV1Wk$hy%d7XH!DYEpx#TmRpx{+MZ>v+2gT!z~8~;cl-'
    'q$6Y1nHn{egxit#QG92PbCk?YiuswOicTZ683yQz%hhS`omU;Is)VC3!)-'
    '`(Q$(`0?u$JH&EH{4(kzrz0HfKcOtpwBAC>Pk)1lTcy%f8nqvE>{m_VAYUya>_&dQR^w2e!o21KzGY>rx3I{b)O`K-'
    'zaU`t{cI07PC4tfwlcVDfat1oSqnzNt-7zDuULCE;H8@td2iVALL~|`-zLoV}nIY>(RJ#Y-'
    'OsgY7OS;nIjOIel~~YYzvl8`{y9rH}yBT??<XLU)vC2FhSCm8gq&`J&MD4{^q@>BjFanb51*}JyS)dI!v#X#3(TSw=Xv>Vzi;5_m'
    'PY@LWDES;I^io{oX=IU11I9?_=xGxs>4(4AlJiq;T<8O17r~t(UPa)FU4Ut`4x6I7j6YF5R&6-'
    'DkuA%2%IRI~e*|Z&&<tc57d9&cbo<EXo^#B;~a=4CBFQHcWV_e(wf*w*h7b<z2mJ%N;O$cf7rc3cX6jbk&tcK;_1Ve|L%>S6*U|v'
    'E5|YvSRD_x&%F-4DRUAZQp*Isb4L3dZAeCKCYuqmeyr5yy8+fRx3+Q*i^I0hzzJc-'
    '5r56aECxPI2~#IHJ@!OrBGP!zua=S<MhvcMjgw)7Tjgjfw|l1O8W9Px7+ND#_BqOy=t@GA0{#<Nv#2GyIK&NO)(LhotHbUw4S}j;'
    'GKr{bI}q9SXFQTx|!=q{kZ39?flxeSj6%4@1Q@%w&RODFY8S#$&y9`H5d+``0t?sYUP#^F%1(Rnl+S4Y<`C}@cm;7&Xxl}+MGw~t'
    'TFV#^R(k;r4ihnW2@&ss|lIKZ@rtyRLGOLLhuP&?~RflDK;UK@O}W5<$-'
    'VJo5Z<Nt^uA*ZqaIj8sP_TWW(>1z~T4@VvOT1>p<9f`G+yk=KXsb=W6ddwz_j%Ii$o-'
    '!!`H!VVq)>_M81~oF2RNC98pl$3<HvjYZ!W0k+sN6EFQsu(eIS(Ew0vtOEyPO*c3i6Da0IHW=$T-(A<eWD5FQ+M$_jFA-'
    '%8MC;v|#s6!P?YT1T`AMU1);F~UCD%mUb9Xcp)Rky=1q`Jab^h|<_;}<-'
    'yu^0Y>=JsXajCkLNA77_lJ~@K3jj!52_+bOo9w~P_*Q8}p7y7$3me3}gcY+|e!<TBzj_*ToqAlXx1ATEu3N&M=CNUeP8GW$(eTXm'
    'N`bn2O_z6D*8VaF7fkveS!SZM-'
    '&X&z$IlRq%hT{oLo$7Pj=pF|Mz<$et&Y^ojkYvk1od8raha&}4vOTrdy|4TND#Y3xV(Rr`y<CR>tshiwWX0xd=KT{F5lMmQRxe5w'
    '`(mYmxZ^=@4{t~jIKWRD<Ig)4hAz(`1{$5fMeVHL%ohA$hYq2<%Yb#+wI=!pzM;6bDxmSXLXAH98`<Hgipv%*Q!o6hK;a|#Ix73R'
    'gVs(ht<H~3;Jlly)zEH#@X#R*w|6kw08N9Zchg~n0iEq!fLbreEq>U^m}aWc=1Dv+~bcMaz9(ar}NYrvCV`^Ol9%~$~tSjW=Z~Z-'
    'Pfr8^<cKyqkG^R9@(4=!j09n($99e+Sx5BgE*fu-'
    'T9Osx|D&Pv_{T)hszFjFZUKOct1Z(k(k#HrI+X>#)$vV@bG$)>S&3*&#slHVj63OGyO?8+G-h|V!}vz-Rd2_JwLj9?nG=<3o25in'
    'rGlI;Cl!Ef($F=a=g6WhtT<b-'
    'PIVMIqXOaz|q=`l`Q$Tdr$t=!ryXvbyaFJgPAuVeWB9$YLs=gOlpMcFiSw5V$J`Y2XMULi7mznu)w6H1Q=fi^{msQ+8>10jrKZLg'
    '%cX>jvh{v*98J@yc+y`Oln_o`R}X7!P>nz4-Zy(ZIC<(^7-'
    'J^onMOH|7mG!4fyq__W)J^+xFqsZRA06Y(wx}$)tAVSLjAr>z!+xM!3>;J5~n0+jJ(x!|-'
    'XeXJnY`FJNjEKSGsy&irQ4UEMf*vDfzBczhlQ*LsC%Hy3yJqe@=b0{uTQ7j}>*lU82xtT+d&&kktZ!sNU*yh?M7w3x*hJ?|NjHeV'
    'H`qz2{3Wr#0_++gre1Dn;C_)6A+l|pn&q1?ZgCqQsI2<B(OcV~Xzj0tqtz&FeDcq4vE>)H^<v&|K_h?8q~qqTuHU|EOF#6O``E)2'
    'a(^%5XHTzl?Zm&ermGSB~MoOds#0l}N~zS!rRs7{m`6o41c-70EX5;Plod~8P?3LX~$%$!y4hJev-bva8OD~sfA*;OLr&Q{c5V~4'
    'e)lr@wq5(VTW%D>dGbKW~4^pE@&!_uY4n3OgcK00X-V?s`>J-t)vgQB<$Md=PJwISs+k<*$c-'
    'tVjVDl1eoQ=+j`fh*?AaT9h6Efi{Ej9XXr(s`XP@q`%e_ZHSPonOcOz<o?7SaQFrV;WiVl54}EXKxC~A9y+50pu~Y;>Sk`x`p>gZ'
    'zS9<4Aw7yWA`vlmQ>p>t)XsCjEy1N`i$YB2s;GGr@WWfW|!I<J&%T6fgv;CM<v|)9o`qFmy-bxo9j1vZ=W5ToM7GC4IR$M{1c-'
    'T)#_GfF=;&SLm_#f-|6VyfFAkUFo0j6PSaVrET*1(N{p@QlxKqxp3>j7H7Wn4VE^Wi$c)ObnEaQhPL;}`I_x-'
    'T*Z2!9_^8(cI=fV<^!9T@_;ebhh90zdIYGJGtAG6MXM&5p9L-Kd$jGT}&QFJYJuG=>UN!IH-'
    'R>acYq(uz4OP3Q0NKUI;23yZMFThM<*XDUmuC04^#f*HSvD)(-Y+-'
    '<ipm^Zs;}iGw+}j~&47rTmy!Eovwm4@r+tTqH2plU?SdopP4cKI@lhWekWD}PFs7N-'
    'Qmn0&wLEXu#Q5)x?&`t$;i%qFTrQW$Na;@gCC0zH^2v_n#k=(l-E=S4Kg`5V%EMNv=?){)|5}fSg2(I}4SI_-b-'
    'IUi|AjoV4b&)%>DsK-dXK?0RFTPcG0R02?{3m`4)^xS%Ao4APb`xEZlgE7S7fnda;Iy@Zn76FZn7d-2C8S2>|-'
    '<nPiLO;Kt>g;POweB83lbO`Y8k81RXgB@$fT~H<pLRNfs_PG~|Kd>+*(A$r%waFnssU=Pq^T50A=s`CRoi&6k+DI|SZxiM$Ms_f^'
    'mWmpATytu^i&+n~r2B$aGp%_{M4O$324pjTJV?wJ$K<{)U*%S&gY;o|9NkA96avO6)|qdq+k6ow+bPp{ug{<7F|=k1jl$Y_Z8SDC'
    'EZ!n#hEP)#~t0;5(5gD<kFUuas=ZAD??R96UPGRnavwGY_Ey!BTC5g92{j%{{-Q+?^^9$WdrRFrDIe<n{hEsi_-'
    'K8CHPx0@MdZyJ+-SnJBQ(p!o0wISD<?-8r;cU$^$a~nl3Lptw--ekhi8>#K>9^eML>X&N-'
    '+DR|iyy*RtDp;>?s|8dU8M7+$jA&{ox;|*;hIVcV_oRT;xKUd*G183hH%C0IAFC)g^X0j9gSx6ls$d_M6Xzz+z~6<Aigj)6f>!9%'
    '@9X6pIaX$`(;WNUSom6+h7BxlxN6y(jqpolv+1eIbx<|*#aIx$5kVjyMyw*!m4iz24QN+FdAsQ0Kbs)6dB*z^vcJLXqq*b7{bg5+'
    'o2TztBTK+8^XAD!@-'
    '_`@j~)7b<9l9&Z*J98y+EBLZGJqvZYq5P^{3nnr&~uaD;k87x#RDQ8by>IHKk_!PpVeEE=r=)DUlUfP^DS7t1h-'
    'Ky)y@cEx&jI)xOR2UUPM|DK_|1!uLL@OF`MKoz|o$<M&dnB9DC7^5RDv6u&SPRUD~kt|G;J*!`^;mS5Os*9x@B{4ZE6{-'
    '6$MM#}!&8c!CTvps%_+ilkw%=_xsC?*pDX#d*i#KGl6K;QQ0TbEPz+Ty0npvmA>fE|6U8IH>sg|?OqF@;`9XN#TKNm?3=zw?0wdS'
    '1Fu9}4o5hQI${*SEguG8Jo_q$io;n3=W=6twIX!ire6HsSt?-~k@R?IRS7Z)nd!C;Dzs9aVFtzo;x^oc7}zFs{<`O-(-4SwDF-'
    'bP1HzL-{A_diSTS57yn=vNZk+uA6w7?U2!Hv#5hkn@c~lg<I)0j*FP?m4gA^`dr|d=KW<wcRLjP-CTEb^&o`HRi0J|`a#?M@Ue%I'
    'QLx6_5OC|a#L}-t6t729e|W0nLs_nn_xSKs<81TI=Upbc<(-'
    '9joKNV^QI8615uG+rerf5w!`n_&d>=Dg5FMg1ws|e=3FF*>y5bCO$HT4<txYtj559HyUk|oU9{Kaw=aqsbONCTu!^hvbX3hH>xxJ'
    'KLK8<c<-!a*c?h=G{CeZ$Lxa%92Q(i*uhZ-'
    '!CfQ45MK;}1U2HW^7^WGGf^<N8VpkwlA;5nbQIWK*=${e1tRT*j8!}<gC+aR@ES&9up;B{iVC3tM1JvS<1&v+*#dy~f1!C*ldQ}l'
    'xjZtvS*=2^`n*B(s&vhcH1=_c;W{^#{jU|DDT7qAvwUXR90FU<QX;jfk(=yLrOFJaZ(&ZdMKFYRt1c0-'
    'QJE}Nv$ep8`y8=b?b9tw0XoSj<i^ew@fyZhphb+#E%WBv1PdPvJ>;$J6Z8*F<-`t@_Er_RHb!vx;*o?-'
    '=&^(%6y;o!55b;0QEYp|9W$Mypt)_>(kMbi8*s7J3!tG`lTaJM{rPYRp`>K!~Uuj*OrjmII=NbI5T?<}NmW>U0}uXsqS#%pz`_$m'
    '9S9R6@D+@nS>N+$#P(s7pP_|3=q+c}R1gVk$BUsouO5^!lDE}K)LoHu#WUF~<Db0;ya$MQUfv-ScQU{v}~y%DThLx1knl2n<czE~'
    '7<&D*S6i{$naIsiDjR9@8awQQ@i>il_a>kdCgr_KDx_Xd<tk!=?vzOkZ~pKhPKcYd=KW54Ja{<aj3;uk~=f%@|^2$IV2r#Lu$7gs'
    'U;V(OK1+U>U2(|bYib>kVdyJAoCwSQfGbvL=_@k-'
    'z6i)YIm7MJ~Hu>(P==PU(bnOkl!gl~2{ondo1uMbqdp5D7z^ZV>5E3E!c+X+(cGZ@_LqSLzGYbE*b;AQ$YMXx%rZd}}-'
    'fgO##*z+}yvdb2+jN)=!L?Kwhr(HRarUZ)|X#X)pxNdwx8og(7KU6Z&I%Pt?yPgVUOpe8DRDEnnyP{PSk)qR)LuP(GeChM&>udiA'
    'yGC>D0N#ol=ATuhpRn-'
    'f^|R}q?AtcQ*JF9J5a%!8dLou?D?Xu;!J*uvz#?!b?hW`>7=%Z)Gkfp$JDgTNrw?t?n3VTWsZ8#uX?BJO?xg!93$9eYO67zmpxY('
    'imBN3ky7cRGS5n2s<1D+U5!X&CFJ{HKstBa(u_wj)(D^m5nR{geH;|BF9=%dm2Zf%FebPES)yZ2w1*Kf!>)+AUOoqeGp+!Pey|*&'
    'E(S9MfueZZIUd>dmJLl>x-'
    '9O8p^hV$b$H?gUkwcf%;%N%E{#op;Mw+QX1Y7FFl|7O>r^S_nirXbPF+Uwo3pIt#q4L>@Q+ie2QCMG-PJC;A*-'
    'la1T&(Ma^h(~*va(IH_3IA=^G<p6DoZm^9c<9jL0{PXq)kCB?+@z;wrw<k$Ea<NbRA*~jNR+a_@4{&`pEv}r<%X3-'
    'h|g@xO|NasrBKdTZ2LCT|<!uuc=f8+l>u3Qj~=8{tmz#?{!NZSePz*YFrB-XJxxm<L-'
    'OAD_U;ApG1vk%UzeP*y^U$FaNuT)ZBlH^gLRPs4aqu$c#DkjFu;}jsB*aTa?khfGkhJo%#9#e+Gw<iNf@nYCngQrY_;;9fUrPflW'
    'c;@Lx76Dy@KhqJ*F?%2EEQtQL&$58;jz`$1m}idr}Q^Qh>0$NOM#DYS88=n3`E9cjI3`}(-72tPcx-f!_$xl-Jo?;Hq?T*n8t)~o'
    'FfZDe>0ygmzUH|n~SM?Sbm!&3v=G=JNLFYu}(J)0M>QG*{@{0C8vPyW?HFrKWocDEtv6+IJVTx)kgDrjG;Qdd+j*0Xd*{UA&o@U8'
    '@5Jt?}`Qhg^2TI~)bZ|~j%+(K45Y1-=TTag*Km`zm{f<^Ntal5VGqZ@148H~yYuxCVvZo)>e0m);yJI-Hi5U-q<*Ulyrr?u-'
    'pFM=uGY>nNIO`aO%30<PQUX+dKJ)CE|GyAP->I&-'
    'LA%2@QVcQsKzGj}(6I#krzxK@&g}DFdNcp`)>?@0Sih2TYn&KlJ)HO(f3w|gi2|zFdWBGYi;2V0U+Q8R2^y?9_YR<Ph)8tirc^o#'
    '%b6*T5t~u;KTc9DVR=cd!s?oyVF~9eZwSV<+giYq@1JHYmy<Vg`IazpXFaoqYu$X&=V-CIg!!fE!m-)}cM^CWs0>h`er-'
    'y4TJ=(A5jOy2F`rtX)W!CsfeF4c~@w~KU_OS>*4m^ON|BPbZ)*oI3VqB_mOFUx!E<qN>SLM5VS4?mCqM=p0-'
    '^BQqHf^r8PDQkUWP<c+BTDSy@PZr)Qx1$ujPdkV`8iQFF)FoIOXwnKMT0$YeZC9*qh9sTOp(*^z?jgLF;;rj(-'
    'Z&ZUWf5}20V*BxYxVacWq-A-'
    'Ps53W(BntHpk;_gd@|JyM2y@R|5uZqF$Y$xGo$&vhhFX6D%t>i{4Y&JQveN?p<3!Wd~r4%b4taZCmMe`C=;5MkU-'
    'zNKbRYvFbeJc5{}xyECmd3F^ezY+ZW~=l}D=2Cx&>FWv3A!KBPN#8B+2SM)X1KXBIa22b9S>Jyy-'
    'TTvs;PM7V(p=a}hO^I?aEZXl))Yu--RcG`#w|3`SN^4O+(KemE_!?0TJ?*Wre^i)WCl`&nL6~E^g{`_nk>n558E1wj*I>`9_14(Z'
    'TVc9-`nB2&dim4<U>1-7;Ug6w^j2{{?q8Ku-!NVuhVgy*MG+IJKj`h-'
    'Fo`9vAH9l@2XV=aX4G(>w%6vew{`}nPrBYk$q`ML>R)XXp2NvB66cd6y3)9g_MDF;iW;t;({@j-'
    'voX$v{qh6GeLdYyX0|c7>j?j{j<o#@zT55dpA+czd=O_!LWI-'
    '9sxCs)rdE_s+)yE(i;8a04&J;8=vK?uwZk)J4uf)kjXfkN<KG)NKhOLcbKm*No@3goG-'
    'y9kT_5$exrDr_YnOb^<PfB$|F$K&n+H|e4w^r^U0}VIMc}>cJ$kz<@IhVqVARm{68XCem-JlO_zxYe_v7jHfv2@|SVMu*TbtIFtX'
    'a&!&FFIb+E1bmt?OG6tn?PU=NOB;L%HT1wO?j`b4`0~;fvXW39Ct;N&IH%zA7tB1@AsPqdlccSx_DGs7#+x#m}7u^vJKoelu32OR'
    '(7X`lGYFn)K^BgdSZIUd+gHBc9q!h>dQBel#oJ<G(SArL%BJfbi7=x_4ZygZHp*eg7yfJh{td!TPHY`_nfgG!JXO@9W@Gd~KBNy<'
    '91a{=SV$uM7PQdZMz|4U%W?8U#w?%bsv_A^1$YUog7<qs5)5bveP+1x55;2^9W)-'
    'F?b4K<sH~bJ2g7US+w()832h$TmREh0`_zXHOU;tZ!ZqY9@5QfEVko?6#@ewc_RGY>&#j@aJ@9FjHbIJ0fOly6pN-JulLhb{{JnZ'
    '5r0q<8ALklrf>&9@7lkRIMO<NgjEV7K8~oUkOKjyDRlyNV}G~S8EcQ;Uuuu{PA&S_!jxv+=i`xefzkniOY<8+^ehphH4IzR#+jeV'
    'r@6#6+C{PDpF1dIH_@3MaY$38LKrW(+si$sOVXQ2iC&o$~})>MejH@I_`-YZtsdkVPZ+3g$XPf`|_<-'
    '!ICiTL>C6nj?eA8$JehC10wie)_M!?tls6@$T~iiChwn`6?f*_-'
    '7<de%XJQqW)Z6sYS_$A?`BoQnaX`oZhpI;>uotYZ)#91mHU;x2UHKz3KFK%I#(JLFcQCuM{N-'
    '^{bAXo=*{<DPHt7Y0g%Q2{9jwwb#vp>W4BDb5u$d6XIBWt5D6k<KPX?U?zvkaZuaqv@^(5eV_@+cKkV207J1JG`l{c12ntq;p7zc'
    '%S`BHfWaa0}U(Lc}bbL2UD3<SX>?EHV>M^`*-'
    'jfMmdBdyG>eG9IGxGx+PL;Ix<dvT%1ew=PrRZ=S?X*+OP9_sDon7U__3n;o%PM#Ou#40aTlAa5zF*)+2OqSxwaUj!4jjPk=w8SQn'
    'jFnLuNu(s)%qx{=OCxKRVr_nlf^QPK|P(6#L`^dmQH=tgCvhGL*xB*y)SmkodH+N%FkK*-'
    '5~Yk45c)EKYYnIVty_Is`2iXuQju}8?6O!(LFPm8cW}9nc03%mF|umOn}pNara;6(qsy;=l-'
    'JxWcZ^@mBg&@Q@UF8J7;@7jufa4Re#Ba`f3NeD$Gv-'
    '=q&e;o(9+B>TPyV?{*SCG+~9n7d4!z*^!HA!=+vFF`fQ|NHueMJZ`uP)EUKcM%?U)t1OW{SRU}2lCBl$Yo|O!++DUq4|-'
    'Fvoo%*!RxLn%ojZ5vy&Qei8U=gC;VV7%;x+eg%h~@Cb@j{Zd0q5c8fwrqqf%)iMHC_=(H|mu6-'
    'uP{Yk&IAJfD77fa9FA*V=pSwVj_6klbbu*`1w#NMKX-!k`STD-ts7wC%;Zbed@Qs-EwWR{%gA>deAl3gRy}aknL@Kb%PDvO>&0{0'
    '@R%<58O_w9eDUG2ad*=MDa9Hg-#ioMK|nU!vnlgCy(!&DYo|{WjCv)DY61TV%FPXY=mZlU7%%j-'
    ')p*TXEZH=I8JnZ%+Wk{kfv@tqyrYpGUHA-tQt}v=`K7gG+Fr6pChDi=NBPyE@@zxllV4o$z#p@AE$V*w(UUAdisNIlm|818+Yoz3'
    ';Bt{nuB0cnIef<u<*D-'
    '?WSsZAT!REC)0@rvknNmwd7(;R;6I74S=M%N_SDH$msrehdZ9BQ^Mxid$imk0hwy>ptR`ZYW2ogCi#Mknm<{IY9e=0wCAhl)rE=#'
    'nthoI9`=krFY^q>+-0hocmhRB{HsL#TpHjeQBk)s?^VHaizus&|N4+_*onp4+@$2ooqP!EcpyFbu(@8&*FB4$9PV-'
    'R=9Q@Qb)I+40+e7jQ$isZMpdDA1R0p$HC_iJWuZlxiDv=g5QtR6*mLd#9soxEuB^VAQp>fbl(Winqy$}KHp4FrNav;bP7&dC)c8g'
    'CCYDBAMBl&<FTaOeA_2({2F)r>Eh1hrJ`Y_bu<P}5kFc_<E3peb$?r^v1ep+M$3eMY%U9RwLW)#rxe&d;jRk_mNJ=~0>KW&?(})Q'
    '8O`&f?w~UuA2VTtIlhl_;)u^8bOY%oKCg$H$X={=`59TW@JS>t!`_qv!aeT>-N{MidS4FTx{S+a!-'
    '#$&v)U%q*^w%9gs4h9Qh*KDdCB{}*H^E@=}CC!<w<Mjs&Zf2^1YsXJRgn1c6sXe!(~^KA3XSLwB8O7-'
    '+m9z!<vg5v*N;Q%k<+s%O*AZMADhUG9#at19Vi{!?QCrTo6ptn#2%UuWP{Zx*tpK^{{qUqIoPYdxUeUI?0>tauV)r#I;1ss@=c7E'
    'O&IP>?SYvNPh&gIoP2i%4#a(`##4D(+`(sx8`WPDow`7n*Ii%_r-jOt|z^jUJShUmpdLHCvdyeXO)Q$bh>#J+N1CopL$NeP)M@{K'
    '+XPI3*r@aY1`1$Zf;zzX5__Af7P0?CH!Q?&r(`g<|@1{A|yYZ%vOf@zK?zAehseKhc!N8Vi@4FUW-ZH&o`)`6|TjSp*X|}za4taj'
    'C;R6Xy;GzSCv)`@Z*g~FU`P6Rh)f<!=%ceT1DW}95tQCvcFO@NmZ9Gm5J8p%}{r55wv3By_B~)qXU~9woB;sJRL5|h%{VUoZcAHk'
    'b7{G4fJ~v!TuiQEF|E_eXrBIZuTHTga>SVSk6x4dIgD^YgM3_{9_r9xD@GRL+`cs@n)gW^n2`i2#~F`bhTS+u=9Gn*jUM|4H7oc-'
    '%wNMdYXs+p60X@`Rji_VkIn7nRW7>gd~g$-'
    'MsG9qpZ5P6Eh7u<8v0zqn0!I=%(}n^L5+)9^rK|`EK&%JXs27T}xi&fB`M)YMSGTs<_p9x%j|JWF%tqmeHR74FoWI=!&M$5aRWEh'
    '1_UltL6pEQ|1%*@*FMGcV^EtlgfHMw~@jehZ`KV+7<2vU9txrZ$Dn5KUq&$qeR{-'
    'TPAWdvB+TY%b^MUXL@(bvLIR&4X$=w7Jv0C4x04+>8_3UKakU<nG@7#4HC|d#-'
    'KbmF~Z1#L5i5fRDXfW${o><1g&q^@&>zR8v;H(#ASQ}oLY#k^YOU5h+DN}U`(gC(P}O_9M}wm+h4vFHM(H8Hq&<M&^e^dCdSH_@H'
    'KIJ^XUs^X37*63~s8CD;aE*-'
    '1Vg)FDF79%8z0su=jSk`Gq01Pe^`Wl4o>KU!OL$X#QNE;s+btsNSnb{ZyOg0?E(`mm|j%R|?M&7|WY#lPYJqA*Vs+)H>Z>LOqam2'
    '9E3Xot=LI!)jF)!IfC`{SiR-_o=uX=c7sf6tD5_8`Je#>r)a-6M6D8-'
    '59<{;&R1Dk63=KutM2|xodoX)OUwE?d_)h=jV_Sn{KbHR9j8v1(J1;fqSzoZq`4?-'
    'f9ObLGB@@x#_HEy)>AAsuRi3%}WOc!+3Z@t>^yFhUO8ag0<g!!@2P8*@*HMOB6??;&nlvLIJ>_4X--CpWVB%^etIL%td_<i_rXGQ'
    'di|6g1g1{>$@H3%X0*5!`?r0YCx8m(!pb@Df}5951VDVE;p8o!VFm5PK|N<&816~ZlcHyD5hX0FMMOcjh5R#y&n96^VM;imC?v55'
    '>M_hYai9^X0yk&buJF;OJyBHgI?eo?+#tpgPPK@IBh7_-tnA-xD=$f|J?b!+o_PfvBhN?&Ryct;});o+Zpd#dF}9b3Cz3lWG40(z'
    '2j%Qk-24IwFbJ;&YPIm(e!qLtM^i4&+n$Ei!?t2JxdLC$6_lz1J|{Fm~-'
    '=w*!*<v0>)jWi0%usyt3SR{^!j{xjfO8+xzAJ6<hPtcovULTwL{oA|>V5{)X920dai$Y${I_--xd~xl&2i|4Gqn*WSuW2a}!N0p)'
    'JZr!WaZO;XyPTP=5Q>}#3ncXpxf<DTqp&9wmxKoB_+ZLv+i>(3P?JEMyiRcq~qQmRbc`*l$`9M03xFI!+-'
    '!O2i=jHa9INL1JsGN$%i(O(Jc01ZxH8(Kq-_Hk=kT#u2w-VBrGYSg*#x>Kw!H^k^(fWH(K$f5G-'
    'U2~k*xuu%9JHHG&CTE=9mO94%QrA9<t}njIb~R=%5Y8_0j`lnr_qzzmag##lo~ks7li|P=RvcV?m497<+3+;EMK#RFSH1jYHl*A6'
    'bK&~Kh9gMx<59|rJF-'
    '8BZ;yLZUDqGpsGQr^dq3)4S46SUnCWvSW60Nn{!H;D$b9Lt+eotHG5ak8_ee}v*lHa285IZR;MOSmqPHtQP&6CJ8nlQWckR;*suX'
    'mug6-mgwR_kW>_^xKc-$L}ad}l)dGr{ZrIE^vydNNFZ`$`&>gC5_qLj{4>}(uhRojfgx?eh<Mj8^13-'
    'uU>`y?V<w5K1%r^?i3QW8wu5ue9J>l}xKFW6p`7gzI%n9=8*Hu^y3m+_v!>U=c&E2(XN=&4lz>rhw7KRenLvJQ$*hh+G@?RWb6PC'
    'ey<Q7DudQ-|`jIg`QC<v8}UaK76+U`HoXY~ZS=+5BejSq4&ECY~iTnlFBzdg+legWnyj;QhhG-'
    'Z`64U=D?)L*^T${t}9QQ(UH0Vx>;)X;XK4w~&H&ymAGS&8(T0)VGb}VS?K@7f-'
    'y6gg(f%J?boO<#>gv#Grn>cw}dO%IVs!%IT6d?cd@?=hUaVMYs6s72j+8Nu}k#OjM86E2Y*+e)ON|?((^!ShSU~zTfkc@&c1OUtC'
    'u$tfZ}yGRf5<5aNunhFKwe{+C^B_O9(+Cz9q7)Jv)6`t`Y?Fb-'
    'UgDJH$Yc&Y{F&K<Ylb~UDmCn4;-N2fG&2Z}x4W_$XCf~(~S8Nc08H^Je<a_PS*_V-IBRb4Se{4_hiI?G(_w2t?|h^lkCTMF&%uyM'
    'q<i@w8doN_*lXU7jlB=y<7KG^S&W{Jdg9c`ju>(MoVSA85<ka?YJ`wi{Qr=@gHFP?Jb|M|o6$adi``AGtr<LZ4@N#2;fd-czDHkH'
    '@qJnZi(zrn1>>fr+@RkgkBUq_|>tN|%Ey=T3msI#sePNV#bB9fj6mbd1+{p!Vh@cqX@%#L;TL2ZQN#aX)x_+ng^i|#POP{1CQHP6'
    'O7htU*itOWdfVEzEnI32*WDb?Ve&;T?EvAhpGY8SjgaYYrDa^)Z>z5GBjUBGU(3$|)m^8$Bk`8#fnd!Os`Q)(896ub5o>nZHIeAt'
    'Jb&U0iG`yvkYT3n6!TY>2?yXv|`wP`7FZ;((q^Mz89(Z?O-'
    'R7z&ITWRJ)z7b@`0xwq$rN|*uJPlV|yPy8D5aU+bU2QKUGQ%42dRM6H`FvgPyRHi10`y^HK^h<l$?o26Evc4?J2d1D>woq|AUJPC'
    '*C}<|m@Rj^g*!}$Ns?}Ee_T`ia?@I1T)Ez!t$vZ^)Mkb1q?bfA`UVF9SesS2@*$CwcWf1FurnYaG0MmL+UOdM2j7b%F9;1{A}%We'
    '*Hm6%Vcw=2PWs$J&HMQix01(SD8&vjJs@F5ZXSEVsm2mPpQLsWJk%GhW+&-'
    '|iXeaV(x*KavZRP_w{z{8omhb0x!;pVW(9<KeNqEP8vd~2uFR;>p;{?xjH2O%$gaC<`1(^7EB=Dk$mRL?WhApZyr{hvj}ayW#3f#'
    '|=FS{Qy3V9iV1z|4!gGv!T^ZTC`Yk=DDX_EoRIiU+%*+KIv;Ujt(kic~-~}$_6JSp7zl`}w^{&kx8M6oLet1_VBe+1W`rp^&-'
    'y8;n7w(mq_Y=6<zwq9vf_l|rgX&Jat5+X4%7mar7vI0<&TBvXReh?IQ37s3y~i<pusucL>=O&YH|V63MTk4<mA#h{vs_-'
    'M0WldAl=gZyj%Rn_+zg9IPn=!O8gUO3=YUmXb^kkCO`>Q|NvNEB;pyyi8!K9TX)%_U-'
    '#!a1%g}Z<eZAU7T(#1yBk$+0verp^(<G4BqsFcgKV({~-'
    '5BebA1aTvc_|p7KW%vDOG_>_<{LU)bAOe=gEpAAd0Ckzi&M1$02DvI!TtLPv4)r1;Cl)``LU=jhV{>`et^)QAg~;x#cZS|W^*}Gx'
    'w9vI!#ejxwdH|QdyTsj@HNaMxu7Q@AzsM+sy&<ZYSu{;wEFs3Vn3&q!+MP;8E_XJ-72o!X7F2sx-'
    'Q!fM<DbkAQk@FJqoO<7ClQeIwQ87;g?$U25+aK%0{#9{aGM4Ku>(xi`R0eB<CcYv<bK|Q?wh4w<l9%-'
    '+O^gzT?H$^t8IIr_y?czjtE^S#ON>lz+9+_&WPz#?R~Q$i%))`Gln(I$fa+@=-'
    'c1lmBI|nsa(&O5<?Xtq#bogrMeUKG&aNJM)9(_6eD`(=ybtP1645M$rDJ`(%2|(%4mtQpl%Vm6|Q<WEv$?LOFDb$6I|^X_cmZNBF'
    '5+`SAT*-'
    'Me34P}~h$acEtmo)gfbrC?RVdg8NQlEQOR|8IUOy}GdW0c5IJQ`^7Hq)4NIFswyc!9?wW*ro7nb<SV#C_0W@teiH!Ann>IUWaaHq'
    '&^CT>t$r)X|>a?cN`uP3B53%*KOCFtEHL11E&G{M-'
    'IQ2h_`38dJ%f3=UvaGO*uWD13}wd$mwveK|rQfBlfbN3I(nF9_feHAfxY`UGLQnJ-'
    'K~Til0%ZWkvj~HbUvUI|a&}&EuE(yg<=6(#vEi#tPQ(yhlTK5lJ;t>BBYa=*(Z}Md?=(Yw?oen|+CPRr?|-'
    'w~O^~)|s^W#(to=nQUvdN@Wb3LcfuWeu=tky(MTd)=<LD<~qY6_@Rzzd;A+htk&=%dbv@dR$X?+xtEIC3_rBM-WYuWtLcPr2yj7&'
    'sQ10?H}kunuBEYaxohCG>`s8e(|B|7I{4gr{rd5I6}0}m)}n=i9c;H|daP~@z3^wQxqAcW%}$vW_3|cIgrwJHiu~RL4(AXnKPJ^x'
    'NV+*ayhrRxyaG3CWXoRl(LE2tUdC7M`Jp$u%?~?+4J3RDqI!+>yixDkU6J`{7*dM^Uh4mmhyJNHVn2CSFYj@2umf~!?i?#ayV{<r'
    '$^LSN%br$x{B%4;f1PBtHnN1~1%rA$)ly1<qf%!bz3!%?`tTE)H*4%|Lp{c;=O&xdbv*3ik~6q+&+r;IP3zD+JQg(Py^n}(G#IhJ'
    'Wq;NEE;s#<$htZmANKM%MZ!iU-'
    '7Zg+d?FX*{ovS;=$p4_DQxk>y`Nqf|7hfa97e}_JoU$i(PVW;&bw*!wo2tX)y&p6A}YT#Jlk=@e(TE>$x>rr-'
    'QOB06<^!DDt^i*qO<8y%oA!qZV>iv-QxH;*qO_fn~KQo2nM`UfBpYa{VVmUf6m?FeLMnd46Gc_8r%%}HhZET0}t6hx~@8Ue)nOhB'
    'bG~-'
    '2U}zindal+k<qjFD;AwL{(HDg6Yn%1?TgHsdr#5PtbcEQ`6t4$fvbG4WqvzT@Z;#QCA1Z6Eyeagf5m=$u1z^$Iqt#}xgQQ@up*=V'
    'k1~wr<Z#(!H_+@fUq!XnUkmjMn<UtdMtOL%vzKV8uDM6G{pvP@9%?%i46Bovtf05=pRxK6ggeOBo2f^kw<YpNbkR$_{CpHUI`D;_'
    'ugh6J70(#9jy}qKd#cY`7pD98E7doeuC}LM<?(>mc$$9wQzkukb5<R9weIPQ>u)n?L3X9*gniX7X{c>yVibjq<qKyHij5|73o3Q^'
    'xL;`b>OU)g>xcUxM_#pr_Q^T)`<IeqDvfm=DcsrKUFcz}L1!meNq%OjHk#ya2bX~Led6%rQ@AbFFFSQX9om{S?`ORyc{n@#5}>NT'
    '{UgK$J8!INy`mu&u#KL$YqjtaE=0Pz8`tXraLeZ_y*{aQ$LDUxr)yfPPcDryy1PEr#1=YLPF48!r1a(^Eb83&1GXB4PrntnFUV&7'
    'xRrj6DvIAGhTEw1A(}HiFoH?*vZKh(qgj@-'
    'PMdmyN+A?l@^U&JIYJgbjN#~sE|BSHbPcdw9|Vkd>$xPt$wJ!ldfKo~rEuPT>mfO{{jR27>l^#82)74mwDf+af({)q9vwXh!Y!6K'
    'HAIs726||<pJZWW7Zw=E%-'
    '_dyCnsH5Rt_FwT1jLAWmQeb^ZRAP(`#!rliq~ze!f#v(7^()_H0XWrU*b}?!?^~x6U*H#`Ec?$mF#PTiq_$tuEPDP)z^y>cQs?R|'
    '-{-IW_pG<2RqJlHjVn+qU{$mEn<K-&xZ=EY-5y9@qvk+9peR=uBjT-'
    'J4VYRqoio_9n<MMp8OV3eQICcw9XXi@D0@&0d^wR{hYXcS;>pr<uHM3&ow-'
    '8!n+^GnzkQ{W#BBS2yNoGT(HLCi&cd3R{79igH5)>H-g$#~IO>Oj7r6vaHgYa^>gjg-xCI2)fnho1s#7&tN%yyzTlm+RFjRzmU;f'
    'wWr{+CLG@0skX$a>Z|JDhwJ>gUreta^h<I=ipKJqDji{RQa?G3>*ytErzYe@&}So9!3%#xFn|=3f%3pL{(k*r$B{XMe>JNfc0Td&'
    '<DCK48U5VnJ<Y9cmXh2#9M9FG0XAAi-LT|Bb8CHSYa0X6JMwx6+Lwl=E{}W$do6`5Ph{*)qou>;mbh>p#21rOBHv|RDXU9=mHpd#'
    '-05<boo&4JFBFtkJ3)HSvApNA&O~XH7B`c7$b+=o1N%3J1+HMWO^3ZJysT>SGDI$sev6p6wm39H)a{Mda@sNm$1xJt+L5Nl<g4D+'
    'EoElt>iu2sUg19*-}3D-;?~qclcw-+$4|c-jplZ688A|Vg!-'
    '3_AGY}CJY371jBKf=cGtQzU9jP>y5Yy*jhPqbhtgZg`bC`_!`)L2gXcwQ!g82VwHS}s)c$&!2h3J$)t5_*0egm6ZM;}-'
    'QE(GgJ%A8Y^*4y1EqVrV?=;uN&_2a2fwJro;T|+_6-'
    'k}Zq&kI5pJWsJ9k%UA@n<<N=ch&DT=6ZwUYsha`DfHW=U8ny>eU8CrcXHqrqrn_bZI(0?)vevrbC{=WCf}p909BeA8_sgHZ5g;I8'
    'r+?y&l@qD?MHbVb77F<&B*l&yB{PZKJr(<+gc$KdUW~_{%cSTh>wDZ9#eJ&ddL%xH<mP>E4HnD~{TyC~;?pcazh&OnWY0;#@&-'
    'cx&$V;_;~!=Usrh9c*BE9|z|G$C0YNu&eC)v=3`3`>OW(Shl^nf37V=kqRH1l2&BZXSvS1I-^%xX?1#-'
    'bbSRaXAO}rOp9J3Zjz_7Q~RYElkW?QN~tiLdqnXErPWnWe`h0tK3^>?Y%BLAR_$F|h#+y(7b9=>`T8?sZqEJvI}pZlldO1nd=CQ^'
    'JTCb+Db}+oQqVn+QD4xg7Je3YN{K#B=608>jT4|PoPfdVpkezxnIh)}Pby+2!?KJ-RKvy5<Mg{n^<}(pqv#0!^#72qr_LAeW&wRw'
    '3ymrsZ>{zI5luSFy=y4A**GU~zW88P4gq4j-'
    'uFabJo}SFY|HFEqngmq$SW5cF?Q^8Wf63?oO(zGX@7`kh1wxZ1q(j~aVEmIIi}ysu}q4CMZ5;bLN}P+&i-'
    'Yw`>szL=nOBzHpG0;6<klbikre*2~tLH!W~_+SMP5+T=Cj~+f~8pkC(-'
    'G)l@3)*?xHvonF<)<!_uhaaY`L?SaoA)h0r@d=o)A3ah24vEHaIv2W$oB^YVDv0YzGe1LtxsDB;jh6kA=iQkA&?Wdh~_t`G!drR6'
    'WV>wv-hA?@<&5axTG#g&&8OF>R|8CfI9O~B~VYBBE3<uA9dvGXO_`XK<B7ku?$-'
    '5|Z|NS%GE^tq2z1rSbdye4ov6OCbZ3C5CFv<8o`4(K|Frs4-<!*UsoRi~xeH>@z-'
    'kn+|)2?o*!zFF_^ky@>IBQb(T><o{)NUECDj!X5t-g1iEf>9no=wn4`$Or<v}hluci`o!-'
    'PK`R<Lc0#8aTY@W^s<c#^l?}^Q+5JB`=^Cq$U-&*eW3)b)P+*cQ~qO%_<#SUx&wIpS7vSu$7M=9+A?U&axmbC(}wv5H>5#-'
    '1o3X2RZ!e^84pZ?oZ1KLuW#z+1d~X`oWtGAEdmXVLwmW;ytT;Ec7TYE1@y5p{KzQ9`TRU+;tW0Y0vKAwA|4jrG21=co{%eC0OeYh'
    '|Yvc<g8px8S-Ro&!nEj%<kgcsrqb55Yl{*wcou>)S-'
    'SEjrao0CSjwW0{o=0E$i~x@=4e8gVlY3gO{?_vk}2jbnl4?$rsc%c&hLz(B*0mxO};Ga{#H4qq2mv8htUWnHaqSsE4~#wOQyKx(l'
    'fwLx1AZA}6`~oN{P^W(U^5^t(N^T!@#gJ;Ro^r~p7UNqd!Bl`d-'
    ')C`EpF_jd)Q+{WwZCh6h}t?zu9m{bn|^7{FC+*Vwu<d>(cYx7v1UlmY;qs?{^2+u$U(E(?6ZOvI1q!ol^+Ut4ZF7^GmMj;I#SPfl'
    '7wP`=*%K~iI*Qj-WVlVwol?Ngb73anZw2AfNPmGbkKA+E3ur2D@MMk4QsFE9h@o86By3$>juM=ZW)?Q-'
    'gH!+}10`UyJv@Q#YafO;UR#f3Qxt{w|?%ujU<q>8L+~EU6Hudih#F6*M++=z^8S|$Orsiep(Qo&5V!vmlltL{wb!9UoNPV#NZqWw'
    'c$LGuTZ>H1GfTVPMgPHkqP693NQ{Ym$Tft5lcBx!VH$cwEICz@QIZYQ;IQHAVcqtR6M(3hSrsRvz4<6TQr`h&=5L&i22B1arDcI<'
    'yGCFR5vk3+*(9t^#bytH7s^1@s>Z5e_9^YcKK|Yq^61m?6@FnTD@RXP5oh*JfFRfq!STE_fiBT6uzISX<nC_<fnNSy2u>a&Q4O>Y'
    'aapqrM)*$f3M*|h8C+>4(mol8A;mzxLBpQWxaP^wOoqpPnwKciUTBl;QH3AQ3D18PaX^0ZG3iSRM##r`dT5GSf!M%=oy+%>F$}Zc'
    'N8~n8}9(U;auaB>LzlcG)@uQL{Apm)<-}z+HM18tFZx6|Cx3Iig_l2~V-'
    'VRP+qy2g+KK;R)FKKro$O_HCZM1XcxV$(c>RsM8$<W;=M2CKiiZ`Oge^HtL2ja_XkBz<QeMwOf)83jGjSY^B8*>06yaVR?>$BqPi'
    'U2u!7>3aMqtpfJ)0OC1d^z*au6w`hFIRA0)$(p``x4|PaID_TfQEg@vfs<+#oM}#Pach9QcUULK*;r+VZo!RNWTE<bS>B<xj4_|6'
    'l1}G-'
    'c63c>g3fv<H1>;OnRB41$$>4pNAP#7+2N7*c?3Uj6)WIzBV{!S|T9+wJVSJS$~^hj#%c&SIW1FBRzh2TjOE<wLEDVvMynFWf;JLT'
    '{=sPg9H}11es#B8=Hh%KP3jG?Kbpx&5kdRtzFR{Pm1|<+$x2X^Tnw-zde*OP5R<_8d%)YhBSS)&D&2)T8H)ZYF3_70zb<J$KK==_'
    'Rw;vswE|1It*0kGBkih6{EsyF_XNezOR=avL7FhQXy(@B$1g^273oV;Y96s@_y94h!db@!}EN^VAgDA|NTG3!}5&88)xHq-'
    '4B=gXLYj)V7{rJZ$0*VvC*%hUAyKK^^0_6>3}nD2f;)7B;ON_PtIJ<BxDbsb?0ig5KIt%v^X%VZZfVhvRA@wcpo>VF7e66=4;>ju'
    'FhMId$pSLc|J{RZtAmgbvkz$s*CAwc!2^x18BayoY4~0<|M1v$Z&&e^=~w5-'
    'crf$1;A)~Gu5Wp=^)3r)P%P>RYcFw`iwoV*?50w90a0A_8Y!>Z9%BFlSN+^yqds{k86jz0Aa08YK^}oxAfMj0eA|EaD=_nqR|R-'
    '!7U;Vrz0oAw@{*cM$sIGO9EVh>M9zLlbKai;j*>+6#W&<JXZsitsna}V*`HT@sbm+-'
    'PWGh=KR7x?(et5`bUkT_l1b7uMyy>$Y;fhK1!D3#koFd7J@_l5!YGhuqYpt(Sht4Iq~Wef_%yiCMi7bpnXD%KS5(g!d0tGgDfgMC'
    'JW6k>dN`pYGqM#I79bpNnlJ_a2wMaws_GXw)5aqp_vb<nCB~fpmTJ?4^sSDK&F?EJR%VFV?tvRqL8({MF%7q8gl3SxY<sSQA%Sqw'
    'nRuemBrH)9rhpS$rScB0q!iZ)`ipR>U;DXs|cGT0-{dx&K{T_<HzcpZ$2}x3H+tT?fv-87uQFyPpT`kI$`*N-E@!o8J-'
    ';KwUtfj!xwlAUX>0wBACl>BuT42?p^6V6|M~<DZ=GJyS2mn!)hW379XfgKr9h|c;3EWB>Zo-3sx)nB-nds594`Tl?%X!#?Q1en_R'
    '&DN4?H2zH~zTSt*hSN5k@7_12#@ojcd+*<P<74xb@WM!s;qavundwY>u#=n;@9HVD2fm)h^E+~8T2n(UzR4QKb;BIVZU3&Mf`!-'
    'GD&{;y5JUJ{Gu&WP9n{yu%kc!-'
    '9>hlz>!#+bi4OZ?cG9AT9nw|aVx&!#vTmBz~L+SN)sa~Nxnj}?w5g+keoqk5xL<Z*VqLcuNe{B*4;_d`OT^0Pq}^ov|u-'
    'qNxw_GX)Og*k<tN_P+an@^oSFqxQ9bpv=4ot#$mWZShk@1C%PG|`30K7HACUX-'
    '}^5gC*NW10N2+)&kop?h&rI4QFlg1|rBhQE<`AT^I|?^^vFwf-US4#TiEs*+1Fj%r@Sh4<IOndA!&_tzt1;FJUWMpj={ab70}2Us'
    'l22-'
    '1rld3NBoim{f`c8siUjWZ6w<W!E6od0=gG$<`4$0Az3_*srPKXXOA?VqL;I6U^kW>@sCc<cE9htsZGq;2T2|3K|Th27MU+)1oy8)'
    'ax<;-^y_iG!E0-7rs_g@D4gQz~uvq+35P)b(D7(ZyR`;veC@Ju|2MU-w_3>44K_{d6eLjCJTgzodt_sOO<4PE2~fTDxQuwShwc4q'
    'ZE>jl<D6M0;iv*N)f<<oXtuSFPM!Ifo}`-'
    'd}5DmYsF$(7Wr(9A0$W4!(yczXqe!bf7^jA1CV|9p|8TTFTrpV(nLj2M;%Kis4mi;|YQ)Hp>OrKF%-'
    'bDw8C)V65Uj(xZyaf+jz{SNuToK54UQ*3;j(aeV(IH#z5vW3vO&jfu_fUz7WTeP?W!^~vx-J!>KSLA+UdUv^Xb2C+Pb;D;q-'
    '1?yj~t21&Pd9)=i`*iT^UG!~T=cHn1p0v<&$1zD1JG%f{!|ioJu$LgyXw-fR!2r`5QqjK%W<0OAPtjfRC*u_`p7yf>oLl+xW3wTi'
    'dF_ju4XVg%Too^>vdf3jJR6w!$-_6u;0+DGZ{F(i@6)`^yj@RwhP85flB3>+{QUJrpPHe-VgN1p(d`XP-'
    '*{_)%XNdTkEHBe@2!J(chRzXlW`BO)(&ZF-p{U^_eR?k-'
    'dT}t>;}<ufsRJydzkhbU7XTg?sTg)kl}itqFMO(0<*u!3d1d@omLjGWglFOtT2!~VY}q2{83&7Nf+_r@_Mz$%{hAIaPIQJo>0BC7'
    '0l|*`tFz6EbjaUGN<8XSM}EZn7&PF#i~y1fcA!7VsJ1`LnE&-oiwkoCGY2v-'
    'mcoxqE6`a!0es**}S$5h|VlyXUoU;;;S|~t9WtXJ^{EQ6Q$K1**;UOrsnO~Tu4>_uvFs_+8;OWKX9ct?$vzo1|gbiQT)NpkeD9ac'
    'FLirp9dX9CJF_98;O4K9%R*FB`)tI<2>frC`yUh;CD$pUuU)2(z3ieNtMxRKe5N<BWD#R^itcWkM20nQ6WzESFb}1l<F#!`d%M?K'
    'baS9Zjizgh#?Tv+8<<D<9U63+8-t4uy>Mz7@P*l1^#X7@zZZA%hRUJJy<-'
    ';`(gP(<z3?pTFP$oj*E9nHdj=>JEQ8oxaNuI*p)iD3`7#RBm3jhx?rEG%cOIcK382W$>vS3?dZ9&boTgGQQ2ys|CznTvangJExr2'
    'rVyP|Z(mpBXecU@<{6lev@AN~tl@`&iEGdlt80IfaI)+d8(%L}GjP(Sl$2O6uLDbYyw@*5!EZ@(!T{C1#rzK#6<Usr6e_r24^@et'
    '5qF8JJhHbdVl(+6a_^O>uEPRZ6?iB_UaMWOHhcCOrZxmQMSYS5zTa^f0%d}uYSYZdWhDzK|3~eXXz}u&E;CyIBt~;l^DFt=o27DI'
    '4JXx-jbCfMql<A{IJh;R71$=~zY&`AGy^U>IoM5-W&0ssb-'
    '9l;^&*ZNj&D&e7{VJ7?jz7FY?fR8dr%kZb59%nq;4CFdhfNT6*lwv&DC;)QRfU;2?NE?6&ei1K*zkQ718&a^w>41=Hm?CZs;8OH&'
    'mR5UidX%_{=13g(U=%p*Fy7hYI)m}UW(k~!UREXcHo{XCPKXGjRgC_eNmMMYX@(>)-%nd`}A5Lfz>bcLaYteMzZI1-'
    '@H`42yQrzmU97<P^D>~9^!lQ@2isQSW?o8R2+EhbCArY+fkU`sfd<#fi)o-'
    '>dlDtoaTp%sxxuIFT4z&X+^nx$&H3p+a+8vi+i#jEU)jIWhdgh(_dDuztq%=r#|BP>I(Nc+i0+T^TeS$%{@=Yy99kl3%dVv@KHW{'
    'En@)9Ev?L8Uqq#`j=sj1l3db;ou0&4Vv#3pd|j2PZW-QhC6P+4d?GPXH;NN(w_vn~Ri0%AH7u<rqe-pHhS9m3@sN;~{7q?tw*Iot'
    '6Y%3c^>Zyt93@*Xmj-'
    '04kkU}v!h6HCCZ8$RY>SpU{eI=3xUCIl(SMCr9MySzM)@GXnghivhd~=dH*pxTUbWsD9O<>|y(kF6Fwvv98R8T-d~c@C+v)}5-'
    'Vk${oKN^CXBMg!0L~?-jyF@<uRXMMlG6adf=ZM8GblTD%gJt*PwZo~Mo*s1kIo8WC;NhX8-*?u8m)BPmwFUfJSJ1_yX6Tfg-UE^!'
    ';{}of+_eZAP8tcjUEHX4~zuGyS#O?FmV^w%-'
    'f*TXiI<1*U@aKobQWuJwdCaeqQP%TF8H;(+$Wy5Da`HjRGHawO(Xu$^1D#tjh8NVvj;MU$w28JLl+fIy6huHX#blO(9*N(|<{~c5'
    'zO>l`y!DiowmxtV3E{;~QqR?dtgkEY=t2!t$>X|1^YB#6s0%nYI8yEZy_FA#bwIOC%;v?#2i$G4+R8Qo_Z!IK92)-'
    'q8pv2)Nz05_VGBY%SJ-Q}Z$>ETJpq2O7|~!g*Wr^`8R-v;$b)i5AcOT{_ce7+*YlK<opzl>oVb)Qx(p^ORU+FCdXo_3Giul-hF>Z'
    '%9kRf}H3<U$kzo{cL;oT>>ud@~8Q^tg}6NzOJDH<S!ZbPt4gkRYn2JzIF%Xwta-'
    '+%0FXi!%FTmm**x$I}PC4@H7yW8#EaVi^k|9c5noKJsGj0U1w-'
    'kT@KNMUN2K2_!uiSOJv@h7C;H~1<$zEGwtJFaJD<l8olH$kfP}p7}R%Bhfk@t7>hht-Xxd7%#4R>Vr(utDiZaZp?mB8lA7&Yt%a~'
    '-d|#NK9yo-}ud|UG0++cOHXPti?W;|3JUoqh-r}#k(R+;7cznVuk7}1Y(2-Co$wbtb5GXhDMn5j#S-'
    '+($v>x|4y*vtUl}0$!)2t_Ysh0|$5dpYCJV2Yf^>DY}zRXf;Eg{0K$moCLF`e_g@ZoCbQNz!%Q4a=Xx%(x5ceA-'
    'X4Hy0Q{`M9*s8KK3YPzMy)4bk1sg!(CYFy1>ds3Gp(bkt&cKJ>8Ha5}mwnUC8Gqut?UCj|iH2w-'
    'G*0u~`jT1MnR+g5PmJiIji1dpVpQ1KBHGtN=orG7`e+t;vZzl~QCGMqxB;Tl3aD7NSA#UwLyKShAbo%Na=UQcO2rJC=H~`FZU23r'
    'WU%tyae;{c7UWJ*i)T7I4tu9MHsmEhLm+Dkk0PBy*a=P{<Z62pNWt`m4l~Z2A7s5~SR?7ti+Bq3md()hQ__DK~T!>2>mcldTbhp!'
    'T)ed{XqUUGcwIxuGgcwaDjJ-Kq$No)~+eyH{K%!@7hAn}!5U6w@V~J%xT7F=G<=ICKYn^FPD_^>I$F2A~HWgM%P;By>*MR-'
    'y<S2XNkSIrsBL^C{-D6dsG+!S{^9X(;ER7qg4~bpr_Bfqmvx|12ebkS!Aq9iIDhq!%xk_C1aow+#TMPF1160J~-'
    'FK9E!y~w6yJJqpL<g&*;I}pM2tI#?V0R!~#mD(oy}ZTp-7D6?@xWdTOFa12FL!WsWWLY~)5aHL8&R{>IXrDkISs<da%0F6raZhf-'
    'QEPTP@aUE>7=QToT5v%$dyU?Z<dG7kJ<X53Ml(&H#}Jzlo|y)Toq5`XY^YI=UFf>*LvnwwJSNlP-'
    'F(R@<A6)#kQf(vQfd@pGyh>tWzae5Vd_y)ycRQY15|iNwJ-)k5k!|wfOGPQe)P@&6F-@^R-'
    'z$P8NI#<k>#m{LAP_B`lx2(*w<3s<pMpm$r0aa1gpH2AZ1AnZEZz^`4VM8)}cTsMDo;NUcenD7?NHwc1`$d(kxl%IE7b)I~0KBDI'
    'Oy?6|O{pW~L>KtOr?#h%#b;OK)>i_Sk4RA<aqy=J@j*=s5!zZAOETsyOU^~+0SB{-'
    'L6DC)wzV$9p$&+*>_WW`e0t~JM5DxU3;%!5mCJiR|tQ9tg=Y;U%`zfE$iIzx>5wH?_dn!E*5a<=PDPx~o-6ar`PA)bxxskjC-'
    '<}TBRgaRcrj@QfW+ZC$y=7JaB2e1&sYS%30xP9NX0I^I(r?XJ#X@w5JmF9kkS<4%y5%B1*Ae;%~wIway8ExOhZ}1(pF1yEpO5Shj'
    '9M=z3+4ZST@|)ELJELJ^yI>o4fY=Z7unwO#6Pto;zqn}42BmJ3H@r;m^c7<DOr$Dx`Vuc~IYS1ul*zo3wX%2sss&hZmdd^`H}{EK'
    'Lv9Y5W>T-S+QBpJ@Am89E<21Nk3Ca@G7g?0d{b+Bch2r+HOij!sN=LoP{r_u!h?^~*PPmffJBODe-'
    '69PW!POsZREOnDs6mpypw>q4URj8-'
    '@ZIx1Pz%lJ0AQM)n;vGs4HIG>R!9Ui|em(2}0Ipal1tM66urJ#x)m>#2zINRjGF&Dp#5sP)G2=tIxjAXzUPVfr+38TVhaP$y%SY*'
    'qGAB#Uu{epxs^b==iUG*U6~1)$Qd*TVQldrG#DI!)TqIf^$_AgiW{HOsT+8J3{RV@de`|Pb$X+#Z}#v^z*zP=A~`{I<T#%@U$1>H'
    '-zsV%y357+hS-Kd!*D}z{G@vzD#{*(ysr|vL$EiPU`tm%0>V&#;e6Dl7+38WYxBSFe^)~-'
    'jQpeg3D#%;c&ILf4SOMW?q(^I{kPMca`>B|2Pv`NZ||*!Qr)eUx0#J$iKwDK<>q3pW;?}?woF1Ulkt})hpnqqFdVRM?xRRYL28-'
    'n(N1JxN1K;OGIt62KFuM@o8x5=yd|Yb=iyU`(}O{A0eEQ2L18{ibAHAK=U?Ld+5ZVYus^nYn7A!IHIR|rh595U)u+Zzgc>8%BJ$A'
    'c%5}0cD3|}A}6yq72oRRqnt67z^0s9{%px!zz#5^H|^Jym3tL$o5BshP-bPRHeD&Nll}zo{JryY57b|!#=9dEAp16&g^hyRo`<e`'
    'OKRhU=wyOCLSLUA#WwL6c=mIIo+g+A^ogD9sOErd`ih3M{mp|SdK<Nu7S;CZP2_8y-'
    'QOsFF4X{j(fNZH^;`4H@XIgrcCvGwTD+Lc&JfBq->V?mB=yNnvEE11-'
    'btXsiF^QC;8iioi|P7&TwYz)uLkWk15wU4ugl#zk%#WtPm_^ydzim0v+Mb6HSU9xT4WTPMC-'
    'w7Q8^f<(==B%ovn2}RhlqbyKW#v{UT$CIdzt`)$qo0`_fsT4BaC29Oz=3Zp7u6P0z8R;v9oc_$ZXGrJge5Ds$!!(ORR%RVO*#KiV'
    'NUHSR0EW!FZaS@#DHi@|TI+H!mB3%~L0_PXYf3q6}%UPAHm)K^RT=myisH}SVvoPc#cYHx<m>X!w_Ra$e^#%Wp{F8^%n*F=w707-'
    '@MuvyJNz*v85TqNa`?H}!WiOj8nk=&m7=7@%9vuy9?tCqC+<#I8VR7gwTpv&DGT551%B3{+@-sp&)g5h~w=O-O<lBn^Cm~W~B-'
    'eZ6gm`o!nDp{sH%z;Itxd|C_cdkSXF#(z<e{`v>T@zX%C_`<rPVrA+^yF^Wt;ILNMa>5HtnRkA_`Mb64G1qan#Vm3Od8ew4!aL#l'
    'j##Bw5`*=Uz};F{NY>AG#aR7ZofV68vR$0h}Fj9gEF+)VTy)CMVCte7tVi^9#&UVt_1Pt<r<l^hn6wsBCQ*vbopL_@3GnNic*Pi0'
    'a^WhOg3YlnotXVTTC{k)lJy;=KDnh;2j2Ugb#>S0HWW@gMB<Kco+T%KcIS9$o_@_-'
    'eJsZ6A2>2Gds#w1^P%=3oCJ_p5WpL|FSrD6ypQA3zdG^qm*Uw{wjWL7sMW8mt{_=U5Cyj>}hvhE({CJaUczh{r*^cWMzmPRd<+fq'
    '+NL?)j_JCA;19{_FFyuH9XPC1}KyVKjVocHIFdo0tXVyHnZVu)WAiK8Lqp#?PFbBPkl{MRYwZVk3HPBTj3=3jGRdVWBX~pi(0}q&'
    'EcnytdVIUDUPXnZ;{6V91C2P?ITTqTa`+G=9$gC``P&NFh&yK@EjL2$X~#%-'
    'LuSmnSM~}QSLgqvZvZPH?@W$mhnxAZsgGmCd3(3932-'
    'OKS|!17+G#Bnjt4~1z1vf6Rhi4U&;j3!P1}R{fi{P!KcIa%mJ2^i_5{u<H7RMj<Z<3k&ESeFLSiJ^Dg%^V6OZCV+SNCb=>BqFGK|'
    '(^qx<XJXh7hR;e<*dm-o_$sv8wO5QacG#-'
    'tf_UB04j@YTqI;U5fJ1us=#8>sv=0LkR<FjoE5L^%|rLNW!WeJBbJNwyuK2GGbVTRD`v=vf}HfaNCcI724%PI6c8@{<ug+xIEVKk'
    'YU`eyjo!+W?5zC7Yo{jAhkncD&39rkJA%d7j-MyOskeVN})!{kv&QMI42>j%ZW)(=Uz1JS)%TroF=ERrbe^h24M%e4mC>JP<O-'
    ';}H3JNw4UmPP&PDmj0CZA_-aXQX!L#_HWFmOhJ_FflcsSG87Kju~ZN?P4O$L<7Kfx(E<oD5JKsuGMon%zp{V<#lCkSnD>~U{q4!k'
    'F|JTilK!gRG*UzJV2J=fTub;R*i?cT0HJwHSShXS(QCO_6j4i=Ep$hZinC_e2Szc**o$oC@5rWHJn4ww>A&Af83UG?}tTuvN@Wt<'
    ';T*-Y*fH|m9Hbpxa3N-+wL_-'
    '>)K?}rdGShyBn;zhrhhp$EET~&H*o6^s+6Kg9Ip0Xxo#$dqUL$e$^9Z*7{yCXTLtr2!FwWbsen^DGJ)F12VYupF7Ee4T<w3>NHZX'
    'PyJ^OK-A1fx8d(T>5<y+R|}uly?Q*ycPG8N-y*_z%jE|nZMvE^1zy7=`lw&cb^)ng%r*F)5D2@Bqy3kfJ<Cw-eDZo!&}jWCKWu+|'
    '>iff*7|f-'
    '!cB~n@6;*mk@6mGeXr`ISU&m_`g)yu&PUj8t`Fzwv_HgEJ5B`SdgJd+?;W4mk_Hc~Dw@vcCz1C)e8SbCARSXOlSAFs)k*;{XN7~u'
    'WP}Scj=n+-P<L4f1&={E79@2b~k=1W4nBo!Iq-2MDOzgRX%*CTDA+;-'
    'il99u`(w^$$!F;8c>PV4+esi3Q)3YV)y~Q)!!0>!^E#nsk;%3OhVJ=BByO7!T1Hf=7{1R-'
    'Y6EeH<a>W#Y$#Q3nfd|A1x`fQWj6s_sYK?8t=5P!=3E>Md`6*-'
    'BJY?Z#I~nG)88IaH2VaSR?%>^o3lGNpA5&Mht1Pz!pM@X<Bql025E-2il^IdEP@EA(6h#@-'
    'XFvWI+wWZO#I3MacU5<FHR2hUzOnvKin#vVAnK%<f1A6QDlsgeOOIP9Up87j_L%Ny<js44-$ORkx<~J>i>L$cr(T)-'
    'bUS^{XV+2AT+Dgp)DJ75E6H|SK7F*=;y$`<?82&d1!g0b-4H9Q(L3&IZRfZ8Wy=-'
    'qs60^nZvSG%qt!Vdbv_lzpR0W40?+Z%(sbd1tp%J<M5=RM6i$I1KeqZy62xPxeB5O2urYlj>Cv?EyfW58vMlaT#X4sS_XLIi@Dti'
    'q+f3_H%Wl+MeUy>Lj3<0_9GtgtE45}BonNJdbZD)fANw&XoF<D)-#MV41TuP_I|%qCKd}$y{$U{tZ+Y1@%l-'
    'WFg?}HVe91arI&=H{<(O+nrQqm-zH??fCdSKn1Drb;XGIsbtb02Yks3p=gKb}XQ*Ro}fV=kc$*QGV44{}bOto%;27n(MLh3sj8a+'
    '~>8Ir@5{AM)zi@LoO|C<KwTw*Y%JrJlV#mT6{Hq9GWYOK2N34FOJjWDZhr7}@PFy6I*b^81_9Iy4@0igR&=H}n)+Gu}Ty0$MpiY?'
    'zURtFhg2j8^SmarF>%C=uF5B#0`4KBbcl<V84-'
    'XXFEC|9~rbW{zyKZstr+iJH&o&B#sb#OK|EB;kh?xC!a53CjWUF8E|KTn;xFfMELLYc6F0-'
    'bVR+5kRf(Z0ojz7}k9b}ww5OCVDYu1OE%%Jri%)WDq>Bt_7;&v%_#vwc{N4~V9>)^WW~P7Xp8gEBk$mCx5Vi>uAMxBe9$kHOAG-w'
    'YUrjTELMi^f^S;hl87r<-'
    'L_UP#z>oDOatxHzr`w&KXK6^#?V=#F4+m%SIvGs6qxmC}Zjo<Hcgia+j|mznXGt>|Jo#){1K9ZeemZgo#1`6)N+f^h773RfFtZ<+'
    '}6y*co3S7WMKKhYhGp!ex6lY`m^BU9s+G6(M_^XGu*yy*$k2BTgkqTPwrU704_D{Ov4fGTEb8t_IDq+Y}V<x*JOg2>D$aS|<>7+h'
    '#q@~U7ri#~E1ThnARDn9&Ce|vq@mhsyC+~1-'
    'e4w;WoA8l<lHY5%YZZVJ?g!4pg`jtW9uN**}1_$7N+Fm?Hts>XO$5yVB?bN#ux3AKRpJwgOJXmz*PB7@>!-{jR%2cy<V0-'
    'W;C^}sQS5taBmBY45J5+U0zJ406JsbKWNRuu!`pwl;CS6iX!jd&I;)3)2U9S`0-'
    '_n+CVmePg)NSWfPsgs7B9&X9l{<C^TeY)wqCSe1!O3S-N1K2hslk8~k*y5lw44H1eQb3}|KfEEWN3E&B0-'
    '13IqbNpUDUkym_g$AFuz*%a9V+GTQwS5R9@Ngb&BmEV^UmSdw#Yyt6R}ZIlS(><0)+YbiPHZSl(Rd8Su%osiMxb&Q<TmDDU+Nd1`'
    'A@cx<h>6}OcUk!*Ovkl8NS!ZbBAEedra9<zxBnDsPAA*KGM@IH4RG%BGBuZHti=$K*V|JBTar2Gnj{V0{`{M64ANE&s@_PBJxNpy'
    '0nn)p^P!6ofW5mpTzejFQ1Cfs+RaDiQKzrK@#Mjh|o*&IfThdD=6Zer9vblfDuswH&M|18LXqDbLU4K)tq>S|e-'
    'mR5zZ(kHIV(;nXm#Ea^jo_B;q6Fq<q`>EiA#R&rVzehsv3tByULnW|ZsBGIqdzPbjvlEwwhatkg^iYeLXw()SB1^6LZvS)TNe66A'
    '!TV68Bjz{QQ7x#P1u0Q`%=B92+M#g-<+8bJif_G-'
    '$PqWF<Jfr&x9u8z>cn%S;TQMF*6i=j0K3+lp(e#=dK;J{9)V{icuz;I^)&lJj@Mbf|Lc@0_wi<Z1%}fi@W?L{A>q7@vwCNZ+?m!j'
    '-vQM=W<`R*XR_<!v;;g}I(J4~kD0;lBxu#b-'
    's_}3T!xSY78_+eI4kGE!646Yf5`Vsv)yknUe}4&MZYe7wQYB?m?Y>1>5nArEXaL(2)7*KJ{-'
    '+oomcr|>u*AC1TxmvCi~TGHEU%!_Rz<fUw!#G)?^TqQ&8nSmx{;fz0f_^>Xn2QuiFZ!N}|+pnGycy&&o?0*WZ)}FL{Qh;{sbR0QZ'
    'P#8_Akz7sqR@Oq9E&vS$(~VNVJ2ZX~1l3K$mDukK%qn{+63gg%MMd!t4Ih23Q6TB8hLs#Cvqm22nNvY&s+?|!`mQGS@m9*rS&BQ~'
    '%$Iy;V?_8nX-hVx}%USkHY*5%#L8vXsC23L6JWfP8;$iLC;DeiTiI6Uua0p6;z9ZP*|*Oyl9w376BCoeqHFZ7yhrlj8q&jds6+Lb'
    '$CR>IqSxM`l><rN6`&dUVb;uvlnATAkd9Zafas^#KD<Khi&l|P9m^ja&Gp>}QdH@DV?HObm-p&eKC=dDuhWQ+PGWNANg!GnHH-'
    '#FXf9KVloK`9;ex<fA(09?ll6etWJZ8Pk;{-'
    '8bB>$^?(V3j?(iOvqte*8U|TA$XQsJgD*P>W428PRy2r2<mxP7cnOSLfbfnHSdO(b8SRTK)=|Bw_O*??`pa<cMXkrGnA3aE2yDX0'
    'tfiYd$;2g((!+C{sHg>cW<;{nhB7b+LFDtVaS#kW9M~#}`{TueV~Z&dV%txmRpmT=?6EJ6z}YQg0Hvxg4FT-m|&j?bE-'
    'd2~x9$506Gdt(2NpJF^}84!~d|@15OI%SICJ(H+*WL}&b<o|}cB4FbGpb|wTr3%M#_Wm~w<R9epN8IBNU*{DuGRTB|)HAO|l$?8t'
    'r#r`T1B0XL%fLcc{&;6IBDQMn|sKx1y6**>%$L)+8^@c5i{-VU~q(?O_TwJ-3=f{-Qx<|v^W!y~N++y^x-'
    '^G2_xnr&5@nv(}XMNzwt54e5{F*7iVabz2dAy7gsq+OS<#eG2>gf0p&EF(qbSkt?5yg$mNx&SY3~_%5R19vH{Sm~+exm1Q%$M=QG'
    'K6;D8^yT<pLC@IevjSQ0bldtdJ$n&uPF_ho{D*|Pu);}7-'
    '{sta{bWDYgdo|8&*|E=M5|cyUE%dmpQ_mU=N;NuIzN7T>W7m#pCW~Hvq1ql$}`oA}P=LGg^kHM{$IIv4y|LHWnb9#{B$paYWBOlF'
    '4p8PbKZ)T?We?tJA|jM<_d=O^JGU5VRVkk>1#QwS^c!CWFbw+8Nym>DP(|z^y3oxL2SAyPkw|Hkdy^V^sFVBX}>sfCxuWp>jX<VR'
    'b(YpRRDi!IRo(j}G<U%*a5LJyzQ8>c^uOPJwwAufm!#YWCj9Kyf=hT!1{TE)ruFnN(?PQg%#wahm)FVeg(cCk|ZUO^i!<zgH<hdt'
    '7ZDG-'
    'C9!k4hh8&KnQUnU`~u!OLuwv+rhkmBr;!KcRDZK=G&T?`;c)|D4rlzOAwT=#<NMM2L&$25M9(SPUnF8LIOf@<g`}W|?&>AX_8r_O'
    'o<ZOgcVLmVjhYA)gr5dEXaW@W?ZF6$E!QoKW3Qaizx7Pk8xLs5H<Uir-aN=2xZ9QFgHDe7Ubr#jVn>i#w@!l3zHGuQf1RY}-'
    'T%%p71?ITS^DR|)#@<TvJzl|9Gr<kmviO`C>qddEWBJ#MjSyS~zo;}HyLOQ~gtnsHVR3zgQB-'
    '<sTdbH9Lwz}>i3pL5rpERMEjVm$t+x8H)kI?1iNR#??0uSRpeRKP0G(6jCLVil%NL!%>*N*GA4siIB5yIVQ*@>h+^y$Mm1^6`F2{'
    '`lzb2A|22JQp|EQ5|m9VQ&W9dvLNlE6wide14mSA%uhjy&vu|9!^}hw_pa8Jp47)EMQN6Rt0Y}q#}_rp0<=!kzKn=r@h0VMnI?{o'
    '{kik4M4cMSW?vxb25z^1n{uYP<r5MG2ERhnmNiQ1+I$}{9;{sEjK?P!n#}hyysK=P{CS_-SZfQo3SnXZf0eNo?5c{_=UackZn1)&'
    '0#WGy?e@2z03JEqPmi?gj@P`5Ber0$4Q;NzY^xUpWbQj(jMVi32gt9DqBTJ(sd+MKBe?katmrUXLFxVcRG7ruP;8(Y$GHovMqK5_'
    '3lf$B_{tpwSP;4Ca&D?i*5KaQ7NeD!iNz;ev|x~O=l02icM)b&oJI3n9t-9sGm=y@y-<7prT}MX9)@R=x7}LKJV-'
    '%*{nD7eRKJ$+l&fShx?$<cD7@si!kd^^SORhtq=UF-FvlJL+xfQ536|1;U?VlJH_xih?^?@d(mbvaw0?WyXpz<^rua&XyIRyaBDf'
    'aI@l+E>G?h6;OY#`WB7^^e0YPyN0%wr$4hDtP98qrr>3x(YyIbSyse&)40S44Q_}N{J#`PLjV_?SKv+1W!##U~@$tk0TVr~#nVd9'
    't00c|(SzZUvu{jwmD+^PoM@;8A@U(jku=WkSejV+%(B=^g9?(hZu*JZsbr<#O?J;xoN3&s5qwPYJltcJel;);>vGGu$7yAmYO-'
    'y`F<oYc{%lmj(>#+p+6p7tDtL{BzNNys{NH+x&-LWnZaZ*oem)Gz)q+14RFDQ-'
    '%8l7M5+Pl>Y{VJqBoEx%*ikrYoAFPT2eYEKHaA~Nj&tYTmO=6$w?~Uaox}{gU)#`n*>*Zx8SST$Yy|%};7yR3F-'
    's*Ae3AID9pg9yL9O@NgAF6gVeVlvF_`NzRyj;(nw$`Xs2lBn&GmcYI=;eWh<owAf%bnn_7m^HZVbeNr=ruFexKXqZ=pCsBc?Ew69'
    'sE{J7IW$jS<<m^-'
    'T}B|p7`TCuE`{AmCZJ)@27C(V2Gt?DBUOIGF4_NSuOq`Zg#42?c<67c#jA>HEpxA?s(SR#neD~MA_)=2MzaqyAeIAkCsf?&q)VYU'
    'Jywi$>HngE`#*0Wd3;G;xahGHLXdVtogoa8;8)Mi-K7@9m3Hq17gQ(G8f{AYdBubM{?*)`Sdfjs-'
    ';$VsLqd7Nefyx^DY0{i=(7c7YDxF+E<lo-cG}u=xh+5Xv~A{%9zAe<q7NB<Rso?Sm5Qs+KjDZR;{f0>W3Hgwcdt*3Wu#q4IysHHC'
    '&Dl7vscemdE`?&BE&dBDVXE=7W3@39}!fsQCQ*nMaGbR|R((CXQxNzc(Y_P|azSM};VO_4}0Z@UBf)865^ggX;`idau8lJn-fGV}'
    'ss2T@Ny4fiq8s*c|}8j!ioMiYcES%2Ya}B&+!#yyyOIJ70j&;ocneD$;8FG=gDafvM23&DQ&iVE&sz0;(eydz90pfNu4+!Jw&|)N'
    'WaQx8-b|H?D&m9-'
    'YY5>pA7b<oV`orepFF<c|(FYKadwLl5ZLT>d^N^ypIWSRei;4_JL@*G{#D#bDq((qwzs+Pnv2(V5J`$!TaH&7`^RpZPX8s_sxFzc'
    '1aWcG2j3b^HY&rh4OMlM_*4Hqnwa$3~#hwHG#TJzJ#QdF*V$ADdRcxDYR6wvxt1x%2+#r*qj0Q)^g2=!P<B5}SH3H2Nu9o{zG(VC'
    'A^AWv%KM-XF$6P;f_|YVrY<JKVbxE>8h{6?nqIwHmF!q1yeWXYl^Hu4XE`>ceJ;>)yHoI8keU*2a$`Qx4ohBi~nfmW`t8kRb;gJ+'
    '7f5R8bm)u$g<0a&6!tPh0F6lePpnk3JY}7}1YIwK1o52Xs}uIDZy|7wXvWovbFZncj~HzH~qIBlpvrepxR2!D>*c)_>jGFL!Hu(V'
    'S=Q%vmssSR>JzZ(BL-qi4~t4m1Gu+rCk~?0RT0*p!_%pf|5dQX!J-'
    '#;VM&MmAl;9%m2wA0jF(C!=%XT|d8konM%6uMuPXG9NAupZNu)OF3F}S>*0RAJ|{^>yz;d%m>it#)zy77h5NbB}bWd87qexQ0@fF'
    'v9h2>%{E&#`j+GO(f;ZqPe3yKwNJ`ndF7jItCx${U|AU=;gWADhq<`qfT?2)lZbpb+f><yQC9=763=cr%39h<#3ZK*(cySooEK5X'
    '{fwuU)B5<%`=`rVbTO;Cadej7z~e^k@jkE{cM0^Iw(L~D^sWX^WbWuO_Sot6&y8kvHtyw1qEMYiW8=KWG|U*iZIm`&jGS-Bd<*%R'
    'L0-D|v-'
    '(l2+dC;B0krMWGk5apm9LM7&wR#2)4|I@DLEhDch4=gJ>=ol{NiBl;(KA$^^E<e@k!SAqSBA$U|>A9X(aTKX=}%h;2+MQn$T=NFY'
    'muc3wd=gv(~bn46%FO^iu<7@5?@H?+<(L^xtj~4*y636ZyJ7Ii2ywXwX<k)^Q)b?2ned+iw55OU~DePtS_(XvWMah6=Nw_-AK0U0'
    'ZYdwW`tAilAG}$?8<~QW?#R)j32Sw)CI}SKhxS>!aT-'
    '71QE3XM4ix+}=Ii0e6$k{5PNQ;BCcBMm@KJ?WKnhrL=~KkGtjA`VQH4Lm)6R1=wZ&5e3riWLS5^C;U*}==0^PMW?mHzy#bs-'
    'y?TA>dV*Mr-)hgwbXAr>T?h2f8NuL9-'
    '^!M=k<~rz2|;oQI9&xd>)NLy*SX1s`9V((uHm(9~phDF~nD*+gJv!>z0tfc7J)?_l?PLHYk>*ZBk!1<>hlx?09BU`O;-'
    'OP*UbqO^^HxmCd=Rq_7MXml4rOhIp4-'
    'NDqZ)zu3@|{%UsRoyUJs+8{1U%h_^P%T0?PF86~vMb^a^rl<!0Z?5Lm9}Lg@2i{Y)rqbLthjllbb1Inhju4$@g~rZ7@gjIZLz3jX'
    'pXHWv`cR>;IdM-aWKwY5%8nqv5zWGL)8D>kiC);c)x(o$oXSK!9I?Qks@bp-'
    'Z@x`?vh<lsmHGJ`KAyO<MMr)M4fSQ?K!fmmuGQ<U!a9_|-}sKZ@7BvVO)H|yD%jfzaFGox-GKqG8$aQU9KLOYYo1n{ZTY%;f1&aL'
    '%-'
    '1FC_AWMuYu+FloB^L)8(|;q<!3KWmQM`#U_Cgn)<F7!p+c8eEN%3Xh2JT1XFL6(vi`NdfCer}*1&{Q;(h%K`Jh4AEV4{*1JNIA)J'
    'jP<XZm%yJK5`rf)|B2wN5tH+`fjr^Yl`wL9IaSLS#;Haj1m{y^4d6ZJi|lR#M-'
    ';C(!b$byC7ME*vk?(_vm~7fNXv9jPL49h%EQX+3AIU!tiUiw|<}&Wq!tvpP5Q@7wO*117S%HKr=gji4={h2IO_mxEEn6+=>KOqwq'
    'm<1S{4hC5?WIgEkAykF=Z=e=5Laogy{H7K>8-'
    'eq?0!iIN=2IuCw8HUvH6k8$?I(YjPjYUI8JO6F!Rkp8PWfWfqe}kt3OVkGdJw*J?GC#oNjCPyXy;Ki4gx$3@*P5WR+U|fh2T|4W7'
    'a^0`usWSCj=&S0wx{pM3crnfarNKA?O(qLLh~Rz@9+iyw~l%J)PKw8%fdjS>in#%Z*1fF@fRE8LX}2ooeuBk!$vGMoz%F$I=^{m$'
    '0U!?ssWlvui2-sio+d($;cI9ApIU}Xmn<*x~-'
    'y2!p8gV?&f5d5lKEm>3i@~wBD?3m=i>01pb&Z6n8r0?apdMx2mAL#><{hwOQozTSttsa7#T#+A_sViMov~pAO1C9Zv_ByE45hOI*'
    '8rZ*6&qopicB9wYpwDwVew76h*)m)FW9xP0MBvDar%`n-'
    'eAMShjsIu(XG*@r;{?EVZYc_wu&YN0@3vNl*MYzLLLOF8FiC19=Gx#Ga#_$j7g)+F%K45IG|-'
    'r!@s*douPOfP&NP;=FPaCt?#JWpm_p0UY4duTjf>dd_-!j-`XF^Xg`Y0hRJRUf{qn<P+Ef)i<#o-'
    'ixf@5e!uxnlwN^ss$hJ%vGQRK5dH7%7FzOJ{`RdY7MCcvdbh@hvN7bQAg<BvSiBkjOKMy#3=zS09>1ZJ%6gS4_9<UYjVFZ=nWHuF'
    '0jl-9W>kreuJ!%I0ZvJZO=9^r+urfgfX=4SYML1>!@e>z;aToELqC-'
    'oX{FDO7sx)#LAkwh-{y?#Qyeno8j$msEO4F+#a_g5Zm}D&6m`NcC(Mzdr2CsQd-Fal06e6I2u~Z9+5p!j>^QZlUN}cPT39?O5tat'
    'NKiGu<LXFpl_9Y@#i|n&j6Y?&dI~UzEF<PUO413$_pb7d8-'
    '@lMs)jozT%};uf8Uvg{51Pt2N)p##30U<fHYLt7C~|2K8cu)E6{`&l>$@aDRUZ=TR(FE^~Wb`|D;W$!|MS*HIZIz8Y>VrFCF}Jjp'
    '$`tB}UHYVy;ZIfGK`vbr}54brF;h}E`M5X9ZMZGzN$C#>Dn!hsWfp51{%ZGI@u)nlWL8>1t_!Le$WVMS)ezyB($0+A-'
    '2_T8RLlkt8k4L>x}z!f{UCp|K^7hl3K87+3VTcv3g39dJpi^K?Rq33-'
    'xG3>NQZHOAUIV~bTdDX+PJ#+c>XufyOwZeOTZXealUnAG|VW9j(J}&z+g1wM$Y9+L4!bt_9VqaVqAB9n0Y`vx$>Zsi73?KK6mAW9'
    'MD+ER(VI&8YSGx#6+niA*jH~nJaoDubeo#1__OF3lzN9U8+d@xm-MdN^czU@0{G6+!ay!U;x-qEI$2NZ=-'
    'A;1pHPomwN=)5zRe*+fm5Vt7PO0h$&@5|aVo_Nb^#%V~ks1GNuj?1{x!Yfh+GW}w{x>j1V!LD*VGRGS{rsHOCC$z-'
    '%IDGT8pNt5;KWVLt3F=Tp%pxl0l?o2hKzYEuirZ75xr5}zMi&`Inmi)%rC078*fxIc8{gA9(+3Dm8iHKxxDQv_U4JL6QZ{NTl0X|'
    'uJr5OHMvzUDrPm@=c(5)$U0V~Vm7%D?~r?;wNfX1s@d1>arD&XYWNeNvUoX^0gK~^X)>SGbcYMeOS^^u^>wc<9a?JCNSb#H8Y`!U'
    '-mkd~LB8@%?Tiog1+l3#ELEkRPHWwRFSi=np0cyS3HSEdTJQOH-'
    'S&4{@2|MI={6ClH5Z!`SaGnuyzM0Dc_UY%nZE&>%?Tj%AZUNBEuC}&WMwxE=eBONI1WdH{guVyD!SuVPh;7+>2IfiUb1#4B)=(DB'
    'i7UV{Y+crpW8Chc2Y)*6oDhli<Rm|Nm$tJ8o+AOeqA8sa6LhI`Rtv=R^O<0J{~lGX1CT0JJ`sKj^jOJd<kOXeulEJETj#t16(-'
    'txkMI9?^hOP4(oP=Y|9V*Va(dtX`2w|Fh(}rt?%`Qe1%<Yx6;~+g$K|`2cPp=<)~*Hje1Nl(xOpiTbZ|5I9cjV6fg*<zZ2Qw-W-'
    '(Gx||`}j18gAU(u!EJ%#t)dfH7BNB`+cfrP)%#*M13+Z8ad?nZqNbv{}bIz48By|BH?d_Hnd@IdNp;P1^CTJZ77tK13-'
    '!k{}Q*7x(IHq{xqEPn2VFGz2X@_doK5Tx79LUSPhB`9Y;Zx794V?S>w#22KkaqYHYKf#dz;In(L`%(Kr6b)CPmSy}^+i?<#E{S%^'
    'AnB#XM6&lmcHAW;%837^ht3Cp3ANp=GH$R=DW}}*ot}TEnJjDt!*=%!)(;*2@w}~=<Z4Afq59`E6(ttS#m8z6@p4;{DbXs7J}P6p'
    'ZT8{0K3F{%i&mqRaMMAi7!%k*y&hHRO)urDqdpF|P`{3V`Bd<?<<@iAsY}H<@iSLy(_{7iQeM4f3b3kP+BpRbiuU7++biNw#-'
    'DV)UZ302K9E;Vz^-'
    'rM&l7zSRC<;BrQKQ`uEDNTIBaPYfwt8xy0Fb=<d^xjq7?S?sNZOTH{UpqiBqep)A2bnNMky*W|bOqB9D9jQ1*VTISE&Rd6IpVJU}'
    'Bd-#on$8TJ>;vQm^*;xl{IeGTJ`vh|c7-'
    'E)+B)qZ%VSkO+)a*BsGcR=pJOiBBXN{MY9)>UUfS=a&vfX(<$^8T@u{MiS@`ezM=c?&t3j9a{Sy2K7Gn=voHPZb=i?rNW^&duzaU'
    'q~AHmfr`)KXA$-'
    'OyiP$8Jt0Nz4N0`wnt5*T{n>PFle~pj^O;9^@ac}8$EWto^{&1AOUdHy2~z|94EL`y~pB<i=W=H%v1SIupgLuGH>ntb$ZCLIruYR'
    'X@FDi)kNy+bz#&f^(ReA=o~%_mrd690-'
    '=cW+3{A%bi3<>^`zPJd&~ErTRio~++|ZT)BI;*(wpa7Vk?AJL0GOwbq5D^f_^M6=z57C^MJF6wE4d3>>{q+b}|Ayn+`c9+lPcsKN'
    'a@Iz25k$aJSGw$VNSdt&T_hq(F}iQ!77=Vso-!)_>c&D<rcQ^heR#SNFAc)Qd&i&^qp*Y6|O3C-'
    'dj&!<@rQ`<USoaX59W`<F7Btmycg^1ZnYbn5-'
    'XL6iE&h?<=b_tVmTFEYX4@&1{;5u4L{ko}1c8(H&t3!z=lAo8p~SxxVoVvBvD4ALQD7ksaUw^}F{F5AR>yms#U`sLt^Pj{17!Mnu'
    '%zL}O?4U1daPvSr?kV(Vn=;o9^htT|W_szIm@eeGyUFjRs{>IMJe4SQrs$Jb2np~+^{w?eY`%>_%U8~+V;*|@ll@ZT7jrR1Cu&w#'
    '%EUlNKePACfW-&QE*Dn^P0g}sF1!4|k9o7q7H7+$$=T`%*uSeTKyfe+Px?G12JDyiZo!1j+56RaTaC2Ec-}Pz+v0jad-'
    '7_ck+k7?A#>ses&NU*MEXzeKLD(0`)US?h4p&rh$`sakr%;qL-Hk=K^JkEpD-'
    'gDL&bFsdC~~;CQ-`}oTUqudh#<_67i<@=3t?s2OKVfOq#hIP^N13w`_G8g$eW#D<s_tGxqU7w>*isex2Gk3azzZWeUfGyBHh-zf0'
    'F24MGe#5C!b=z{ZJb0#Vh9#2OlOQ?yT!>S{&wq1XA}0soXkQYt^n!l`90RpTR=6uV9lZcaGz+vb4ulqGp6J%C?RBuP`tvZ?yQ-dj'
    'UC!)_vU0!Be+mPq(4~WR+;4uNyt6I;1s0IL|ZlWhn-'
    '*=mT=b=nL~kOs%atD7;pdQk?SOvkS%W9^6s872pfGpj|nR+5e3_ouoyXwixZ8dYuczET(Ip!}xM9ZN!fViuZ$eN6)Zwt#v=bQ*g0'
    '(jF{0?-3W$r`V_3|A{$<lGS)HEwwRo@y{+$83IZ#hLb!bS6;JD8(t+MQA`IWqz-Z8qp%X8%)ur%W$_b*{q%#y-'
    'D;C?Kvw2P4y4C9t!3!T}z{L7Bn-Px#(#?8`G_NDXBd)tIFkDV#n}^pe;Y{?PUxHmU+|jyTJn%gp0yn9xo!k9SAFh^wPdp<6v8QI6'
    '%0?~&{**ahy-8i&WfkpM8g?%QXITZt-N81MYj$1QQ*We+XD6OcwPsK=x0~y^@+BdMKU|zA>Xo)i&p4Fre6e<KedPL(r-'
    'M6p6^Dr?+=O}+!uN!nLLU)Me<6%6w(J5Itp#@%UWl9Pk`?$%+M4Eem}Qns-'
    '4>1ew3hc0r`a@$Aa@fgKvB7f?mz|9a4l`KdN(|$LtuB|TC)wQZB<DgCp{ZJ_m4Aljjpgibz;KK?#(q~kFl`zj27LbQ3@Z&iE>PM_'
    'IBFbPhPgUb!D+p#J<_Xml)}14~k`1c<!!GkeF(X#bdmBaS_x4v$K>YDL;RAb|&o2J66qtfx@%jtm@-'
    'tLB|S%1=_pp!I2E1E1`7g+-'
    'k2IPb`pq&)TQOBENrkf~HNq))M_kLCq0sl&fJC#_d@QU0dA~U3<`@(>O`b3HbEFadBi(MBKcB`<7=VO|JXOj07K=T>aU64{@yA@j'
    '_&lls{&D5NbQSPZ8;h_sBzBsYPO&U;NFnQESB0Zi~H4d=_*L41*a-'
    '8QltyO<pU(9c`7id~Q6>V&AqLZt&5Uxf2BE`rH7s#p!bRFWorokg|=%SqVYo#pvp`m$@x{Iz0=m`2xWof6xB(8Dc@ztyIzL?zyqX'
    '{(8|5ah0h$9=`A`A|PJZ+w-'
    '1QNP4T&(Eh0B9+A)6qsNR*J%8h4e7@+79`j!4CxT?VVoQ8HufY5RWg=SmreyW+S5?ayoW=L0NL%(C4SHJ@hbbDX2i~#9z6P~=g{v'
    '>bV`m3(%Z+LB6xj7^TLN-(Z!cYF_e~u%Q#DbfBZ+|bAcZsSaa~<Cr~{oKevbn8KkatBKbY9*-'
    'x46<C0g=4Ro80@8UuIofDNERt*L$UqTb?ajoZ?oTpE3?PLpZjorO^I%(@~b>;_*XcTS5R8~k21vA5Zr8$49)>IZgH7+Vr>4=&TFe'
    'Tx6KT85*_j;)FJ9B%tgb{a^w&`4!$m$v5bympGtp?R!1k*m{+6OJ~xV?s+Nmgk+OK5QsYuyAk(>}J2**DuTEQP^&>yJUsE)=|E&y'
    '$4EP?Oy`)>u}H$k5&`3^1|pF@}{74OZE`V4Kw?-'
    'e;0QL!k%fJ%0dwy$U4?KtAbi7$eY(SHxURdd?}1fsVaSv=$3K@H`NMoZjP7w9mLU{6iGSz7evVQL3W=zLe{}rgYnsiX!X-'
    '}dEMKN^G2&~DrJvinL*$-'
    'e6zjo?OWRhG4ifMBX5UZZPwkbaKwlvkam+R`&^3qQ*1bqVpn9)+xdJQzJl|g)@n10RtNUIR1f#{|CxVY$V@|C*5kb+jbk=Z+JzS2'
    'eI(!;r$uaanAWid|3zyIi7jK*XeTG|qJ_?WaQsA?-(;EAF-Tg2Lr2Q)lrgv(i9;r*vrljLWp7plia=%fx6_J=;FtZ}bx(swCb*l!'
    'W5#E*ZnIs#w|lG6WG~Azs#u}9#VI;ItDEsg8_ef*skUF;+pCHscsgC_2-53xrrB&U9^lO=h;NoR&k8-'
    'pnW|=Q+WO1Rui0XLoQ)2VfZw<JNx!y<_%)W>DBYIu-rE16llP!<{eGE=H?A=qb$dIGvlX!;_QTZ$TBGx0zeOmD9<Le1jp5Gc^dZC'
    's^(8^{dop~Nr)lfrZ`&zH*X3bg9!->N%}%@4wu)>lc|>r=thS~8YVfm}C#^ss5AKVGkI$~-'
    'a}Ymz^Tv6Swx^96l9#LXMW}J|ea8~WI}fmEd9B2c&gWhanagB6-s{-'
    'm{ybFFZWJ`1+D*L^9K~I5zy|g7hHw6SR%`gpLWVZGjf&;VQ+c1Sl%tV*?23JYcE<(E@aa+IEbV?49$s*FGH>M~7;r3d_0{T}KBj8'
    'ZJ6zq_ZhhPE2HGLp%k>smHF}$)LlO(<_7VSxZXH<pezm!;pQ(w64Y@+|978WDzfO&?a+?7@EQA<T7Nx?XnK=4T4{P!~rpZ}|R?hZ'
    '9P3HsZ3&XW6=$f-iq5h7lK*280J+i|-'
    'hnjrv4gS30s`RVQ&R+iY=sgF3G(k?MCUgY#2KRWwoj}@E;+_Xiy;H`0coeN1k4gX^Ij*dzvi3dOg;(g^Z(8L|0Aa2tUkuQZ)(hvj'
    'sqsq^Zc_u;{WD(~dTR&l%xbRnZaAO0q0@&D&kw$TEnJHBP&|&=d}J2bx(KbWq5aDJaN6vhN85F+BG~_$7&EmVDX8RDGJl`02N&<E'
    'Q*c}C`rSrrA^E#oQ_GawQ5#Q2$ekNG$!7nE)|Ih#8ui6kfA8%PB7-}!JL_SEMVb4U(tZ_&vKJ6Uk0rTS_#?r>yrR%TFFqZQ2-'
    'P&{qW7docvTx21SdDh@%6DdVEJt*k%Pu5Do~xt?mtBwSz(@q>3N~qS`S3;)8>RPI=ez^0zcHoo^kd;7~_}Od<l;Kw2LKF+8#0lT7'
    'h+Bu4h7UPoQLC4T5VWC)66ZJ}XP5Wmr<9Roldf-'
    'Fj5Q#(qe%^lfU4)MRH1^Q7rqC9yQ!t9qYo+)l);{Mtqg*WalOTQL4=##*UX?F-+ic_G@chA-ieTp7h{W(taArPhYKh=<LfdhgFmT'
    'YEk%OUD3y>gj@les*b<%N`P9lx`kfcUEyY9^0#vTc>rZ;YK-)9km@kE@5mi(#T*RbN4{sok<jNOO-'
    'f56U*9ywS#zAZ7bJvuB?`#)<{O1fz>WzBk~);Zn(#VfASFaZB|P&=<`|@rvsGqYX*ePrs?$q)Cd|!7Iu1dC5t&%h$lP1%~rB#tR?'
    'Gi_3%SY@5+yEh|BS8AC_KcuXZ*+tMQ1Wok?JpD!p{#|N5DWN((AJ2mrF*R>ffn!x)#A&7JsMvOw-'
    '7oH;2qA9c0kcQ55}#}X_h$Ywn64eOvDzo;m-'
    'W|kK4gWeY3m`b5LdoV#M$fWzv3Q}&|;9*~?Zc;dz6}GX*FY=hGOa^lil{;diT0dR2($&7{?n%W;zN1IXq*M$`)-'
    'Ia)dAWi6=()BX6-'
    'tkvpK|j;UhG+ObGw1e2yNbd7kJkEaZu+VE)WDS81}=`?d4_bpQhB^l3jB*l#0v%Wl?$Q#lxi~GDoi2br$Q5puzK~jsRxFZOaN@7@'
    'eEfs<`6#@v?KRC1~M!>z1MROT8J*mye3)<3JirFKNa#eukQ&g!|OJj%Wj8-0vK*i9cTH&1DhlqT^-'
    'sfkP4QkI8TV4EvNrU3Wx!Tk@0~7cUjzDrz5i&X(6=-'
    'OsPyh*Fue+HUbQE>%bYp_moIC7a8io80M8F;D*YBCp=@gA~{Bc5>>B6m6ytd3y^c<Lu|{!tLnIs=J){P=}o~$x65A7Gm#E+ruu5G'
    '}7kYnx~T94v)^3P=nfvLdURl=c}^YrY11Eb}EN(f;9m^QSJRUU-'
    'n#aSlPX9qP46TK&HOllfO+&uv!1ff=KZkQXhJZ&awBTO|+*c2ocj)Mm<`9@l5(R{3&?@WLoSN_pq%rMS1HFjqxsni<?c?<HK6Z;h'
    'BwcIF_Mld@f4WCf&HSsV;d+=V`A(z83sXxpF+M1?Ihvt{EjLvVkM$qxsgtiY7Bf6G4hpkJ@%waU@m?yI<{FHjul_7anD(r(dM0wl'
    'y%J-gJkx9#68%vfl#V=t{Y<TzpKvz(AV<#>g=01B(;j);T(y2yW|cPcbl1IHk=*Pba+Z^XaaG^~2x_-<jmk4-'
    'Q+J`|&2&zCZ10#`oq&yI4^~BWIAu)a$?r1dH#9;^RW2{xr@dg!y8>V$NdyA>yqoFhFDE$sN>q^QUoBHTVu#HuVK>%j^7zi^}w%$K'
    '(}#T)NGr^7#I>3ZKc(%=feNXr<#99qx^)#fG6!U_RR-Q}TTPY0X@|Q8bY28#&yp)-'
    'spaA<QUpcmT(L)pT|`pB>c>F%x#jOw$swT^5}Mcwsu3$)sa+Mcn(u<uw$5{Mp<DlzhcJyPA&Y6bPQ0i{*`f#@o+06pq7Re{1tr_<'
    '=P!jw8K1zJZkoncp7k@Eg<&=hK_+29wsi(?%VNrS<DEKa9)xXZl$b%by{=lwU28wW?g#b8O>Tklb$S=*!PqX9aIkb#`|iS)Jd1qu'
    'C3XDp|{pTC5d>V}Nx9dEf9-frtCxva24`xZBke7$l^7V;RQ4;?lvjtbyf0-'
    '2q*%#G%z)x;S=x^C@f|LrI;Ns@UV_tn+2(%S|Vkqp_v>W+TNVKAlf}VmiEu4lQ+}%l(@Hes$6>%KGG2IVj6mqk|47i;dbk-qgcbm'
    'h{4ql^3<bL``ZrdEK`v$HIhugzK%J*l#cgKz`mWW>C{=K3?f(u_6oNr$n*KW2v<1!x8&DoKbxAR|u?a`Nz>tL)S2%k1`RfMZ}qBW'
    'ezEI?J%W(ylbP~G_p_Q6cS6_bNm1-ua`j9tzayL*|D`Z3nHyO-'
    'u`KpF8iy_p1MriT0A(1n4OOF<79>{Ak`Qu=_8t7w&*h7=ylfgmQ{am+M}^jio(Ao&qGP7OpHud^yp<JWNpI<N^sq&iv1y)DoRF|B'
    '|65uO{bhS9EgMV1E&U{M@T>5&zZG>it&qIVbI`XGSr$1x&I`FI^A`quYm>dj?*};{-iU~M7ph8ik+@kV(d_Bc}f(DmmoRr-'
    ';ULb#16tu4#lU;6?On|@g(d;pK9%EJUvHhS%Qa&R6O$2upEhbiE-;-'
    'V}})w!>ug$@Wy(yT9)+9U)emjr;D43*EZI%Tu)n(Xxz$(T&dS;rS|gVd{(pQq9wf0E3_7=QoEu*sftVYeF5AwciRijy_lWn^$3<p'
    '1GF=HHf!*3G#&B+#v}f#8u#e!s@Z3%l@U6>{n{bU$!)EQ0XpoOK!xj26Q_O0%Di6h_ovlsfq&TiV<9*|TrYs!ZaV0X!S$3TY$cwp'
    'GoXQ`g*~TDnExi#?tT}lD7Dg$y2hN+Z_rg{y@S|0IFP=OKksk0#=BZ!S_97a{mpF?-'
    'hutL)n!M$uAI}iK?G;dNz}$>124om+p(HmkoNG-'
    '8c3DGW7}DjUQC~5eu|E3H9amVQoo*`G^*ZFi>kTc)3}3ZRP2;c6T^TM_DjeedybTLKe_@`@>#DTG4)>n#mQdD@dtLj(?cdgj|7Wq'
    '*7ZK-iL7H^0BBO|9)bQE`8Tl)L09$;oaty60`;Pec{=j)gW{n{Gd;hh_^WVyk+o53##+}APY;m4?-TF7EVpLhgM2KA2-'
    '1@IhV5_qTccBCh2Co6vmD7wT+cm8<X^}+U9_SQWw&qo+DcYeN-v-'
    '02NATx`<$ZvAX!WE?n4+KZgu<ToXhyP9pbWU0Pc~GRi!H=5L7?B+ieJ6);)7=f^$l2o!%hvoI;b3*UQ0XWsr>mx=pBL>};-'
    'sr|{bhi`>+~t5My)EE0HD{7JFbjh{?IF^+Yq;H}`@)wAh9U-'
    'RQVSe|U8<>7Q%YQsl=&PeQlR)%ftb1NUu$C|mBbq@20mP%XX`SzWk6AE!|UAgD6_lqR&=VYpz=i+cg0d%#gi6qsW+m&&|k-'
    'dsCGMszeNX+cxLVnSB2b`E26iI!yWU&!|`$gwn%#Z3s+Jv2WI9Y94X17MJCXN0q&RfC~h<x<^hvnmb53j#ceLTGnw<CPU)s^>hWy'
    '-A$CA#>By#-;G^jm@jUf0`JS@QV@eBO3y&-'
    'NtR$Ke!x&tA)<bnR~XtxJCwVCY+W42Bg|GsAUyXz@X5_eUFGqd&SsH)y?HtMmQm;H}u}{9Ut!1DOnyE!{9Tb-'
    'A)5?V|dP>IyTjGy<TXqm^gVRX;{0aXw^9U_TYPFD-Zd)-9V7%?*TtZ58b)+gz<>>QLM*j-'
    'mo0wYMbnd9fT7pp@3ISnqg5(cLSEQ!7k)q01h&I=l;;!UZuyW%`>0v9~>ZF&91)&|yPpb0{@leXcc%iv3|?g2wyb`Jmmxbm((kC*'
    'Krw_t<TpT=7*qLs!TMr(;05dRvka)?IeVR<trlEgH_=+iUoB2}%+?*lno7t$Ha<WaFGv2h=Ye-Vw0vI(WRT16A+_nYRy>rn$Q_ug'
    'gYpA0ii$`v&C~{QD-'
    '!T!EyCEY{%S+~#jy@#;6v6?dwu&*fVpUssXPIJHtY!F#cHUiRNo&Mo#qwbjb2x$ZId)oaAe;%81RLAAUj@@Nyo=6V-Q-'
    '^^07Wif*P-lU!j`+H^k2(-m(`0I~YSP$F?I=x};K#B~n+<!(c-0-?w;ssD)0-'
    '3%?M|#7D)B59;XzpA9I<p3C#m|fyanC{JFk+1_a)Z5M*mS@N!?bTJBkU(a_q;3cco|;)6>TO!*qjWk4mOB;smg)Yu%x4=1Etdj2o'
    'DY>+yxIs7+AWmTK%I*feEkm=QfL#({94!+RIdL6+B$S4m<CyLFm>BX{>W!C~GZiI>Y0lRN9aJFk3WOoXosj#V?x|;S}!i{e`U74d'
    '+;cOWv%zvgR|am~wYm2Kg?!GEN{6cRFLB*{&aVNA=V6s6+RcXC!C1OPhrm5*ho^eEu9wQlSQL){q0DV%QkX3y3xCR)8P2?(kgnDl'
    'GQQdI2fhwyhUI_h>3{?UCH4wQ<sjr))mHU1}o%tB2inBes?>%Svr6;HK}b6x7C_8@(FXDyTJ`=awoLjx|mg|8&`qz@hTE%24GoZd'
    'W7;%8J1PhY{@!jwNQ5SFTZr(rGbW(mROvivVV>`VZaD2cZx80h>D|h@ciJ7qdZ63w|<1^Lnl|=A_qv)%A_U<>J%xNS)?YMV1b`)1'
    'F!Yjbd6!6a0qW-8xfUPtE(LdFtLzRY(>u@Gyop%B!*(Z9HavyaJl}-'
    'VTSZ*|U6j@S^rU{I}WyBD*y|z)L#;IoEa;PhGIWDGZROwr>4!{+-@!K;7M47;bH^;vsW)RI0o8QDR9)r-'
    'Mk$CuZg*jv6z`q+C%$>Y%m2?sMKkzWGA#oS@dF>OZzYdK7aVe@JIwCQt6}d3G*!Gj9Ti-M^vVe$z6ME4QpdUF>0AVSl-'
    'x6I*#Mcw)3o>)zBqZdWItTaCvJes#?9LYshQl2;?&?{@7qnuE-d-XVSwzaGeAT_^fg5BCoR=2+&p5r8U9?r%A8Iu|*q3kOap%gn-'
    'PUo;dxWv7L01w`-x6FMJMbQmY}d66f^j$P@yJ|9O-a<%+T`0M1<6R%OGPkK5{><}^_n{zDfQ>TU8ZA-h1FL>Zq;9d^|v-'
    'X3JpHKqbxt#pyd9aGQK18N9ZYO|%sP70+8dZ8Vdc8SWMbHxt+fX2|>7U7Bp)r7V!<teyql9eP_O>qoaqO007H^VtHSWwON0S_8<u'
    'aXIrpb^!Tn>)>KhEB?TR~*m7X4noqAZ&yx~*YDBUcfWMpQ%v1>}qaD2-'
    'wR3IYo1Z+}+pTGrn8?EA(Y@6%dJrX)dT<cy4n8O}08=rrmI6tw`^QR6|y_l_VxFGhe7_M3KCAWe4g2fZK4<DbJq;4t5pS@l-'
    'fW3#(b$*+g+(otlnMq*lmGEW9ExxE)MG%TTsy{vR4px3Z-'
    'vp1G@>$a_^q{k8`DFWgMIIEO6_IkZaZ(2F1MbBlf07G}in;$@g+at8VmeyqZQGkeIS?lfG2@s0VuyUWkOXc{Cog9*IRpnG_n`b$n'
    'hNl$?*kj>nPw)m#u|YwRx$=;hBqw+L>W(tGns~TU)voT_mCMVYsm_=C4MAv9&|R9cr^e!%2&gKi^6Qyv$W!<BD4e^K&B(psL;=7i'
    'O(KtB;0K1CB)(~y=yb7J1N6CR4=M<}Z4_pD(YC4Etxa#c$f`41u9N1M=!n{v3!U<WZ9$Jtt=Xj9MbiPYm(*zV6m-'
    'be=9IKQsBzMO&EsS=!){3Qddz^i>ps2kGyoVE_tdUiJXYVzu`(SGCR(Ey<r}+#fS;g4$-'
    'VxRM}wwM#Wtd959XyXc2U@P9(G2uWMyHu*-tNz{x}$4lEr#=oQ}`!_%kKoq@cg#LVZ_iK=NW9&a3az+_)-'
    'K2kpP$AYcqb1J~W_TmZu_Q8@G*cgwA|SOuosO68=U+^P@S<eU(atQwQ6)j=88D#uY>xp@2pYSpeW!zmf}O@XS)&Lx@L%v@v_DD1o'
    '=m%Q7h^Mmnt?N^&;!)sh5Wm2kwboF}W&=*g%@Y5v8ZBET<<(!#y<Jh9GHJU?Z&Rwbd!F^3!<`XU8U`?$@8PTZxFhxk4@MGpnPYsh'
    'Fw^M&QE?}G9)QabE8#8E*Z#mTK!Rki7RjHn*+qC!a=b+5v4ASM-Jrl1Vk?Ezy_S*#46vjc>$3Dv0#7~PZx@^Cbs24VV!VNx%?UGP'
    'FLsFB6c(zkd07%ZkmH`c|@4#do+A&js_YG^^o(DbY$#?ByJv21sICU0B;%yCXP_<h|WJ-ISLB2(X<5Q@R*$Bz?q#WN&FTf9=*ShI'
    ';l|e+laf}cOTafR^+bK*Zg(M$T4IEQlSZ;>XMO~GTfMf(V<F%TJ)j(q)|FZ6=`y~{j?dW>5D%q(3OsmeekUV2jPoIT}9FBabc^+{'
    '6Z9hX#7z&_w9CR5%rX}MW&i#0Uz0ia6`15KfNREH;(JoXJSTlCx#=GCr;4^JF(?dOVx6`;->?VYsT|_%7nD^D%>3<Z1A-'
    'mANK?0Mcg?q~c;rB0T_#Gcu=$wr>r;<6?N+0OU7%(DJtIv2ekFM9kq+DhD`DTTDft$kAkER#1t{U;?o$gxa&GU7YhMf`pQO3ZwWh'
    'pDYk?Ln6o5y4!mm{{p^jrkL`DPDa$cNe5oNm1;Re-c5eLE;lfno0sSNF~ppfsM=w(-fbB6GApOOr`yR4Z4!%wBCp*ph>~x9g-'
    'BR6mS6*e$ycP|N3w*%{j(|0WW6@hz{5Zr^wC4AnI<OXNPa%{4!pd8vGlx7S8n&bf_`;-'
    'UzOHZz>Lbbv{*GQ3Uc4F_M*Df@RWSc12*{H32Dy<-'
    '!S_DiQvUyAyQbZ=FQ10rh>jVC4ZUY=Gckt#8#c4@0gozVxZfirtjvP!d*$lez_8zqy=eVhjLHX2w&^)YKX)6%=z7QUrfv1)u*c7U'
    'fL{c$ssusGP3k(JvuCYpF_?T2t#Kc;FdovMxFjJ|W%0WJhz^wr7Fd!w?o%!IN$*^64K*`B1G{D|o)&dyE?8hFUeEpz$U*!=psA0t'
    'a2LAtfh@ckv1>E7=VvAfzzUSn05){eOe)Gg^**e~(h{iqG-'
    'SfxKF1$L>vH)XW5+DPNI%&ge{TU_Ep)`g!;6n?7%e3T2{=?+tU37rPm8SY!j=1DAoO(8K%h>gP@zl)OxXRskQBb-K#9wS%OF-'
    'Jl+SivKU-vK1Mh-xIkxL<oS-99eX?4CJP?=H?tmNVQ_1#YkGBJ71%=+FT;=OX1}M55f%f-KQQ2*ht$csxH^*+0*L>eDwmQ-'
    '8d?AQLGN`T&v3Yme+uF82oC1VDd4)A&VzpYJ|z14eoB^cqy?D_S2EplnG|W1qn=CqL<^jcT8dI|s9Gv~RP4INc`PL1x+>*|!BQE6'
    '`J5B#W{p=*o1stz+nszgHf!-tI>?SZK<QeRS7-'
    '1{pi(2%9!Quv($^9x48PU&zZdOg!ePCJfP|rYMc?HHNvM1^Ik5u1vZclM`ME=5w$yD<?C@(%sCk@=Co~cS~Nx;hISQ<Z#&|>h<J9'
    'RVi$fJ$w-4U~(94Bm#JEL^Yr4GIHX^71o-'
    ';TgXQ5)Xk@djYavix(%)`^Zwo(VeeKvOr)LZW4LyF)%ADEj5D3d8MCjytQ@VourD6FgkQx0WOjNTDELP9Mh6OkuTU1w%EbtEf?)+'
    'ZxK)olen}vm`X*RJpqcCCz+o}pV-4<|bNq5BZw^vdp+KYe*(D*!iesVL^sXr7!#N-'
    '7MNbs3?ddgeuJ$d{3OBvr3mDtVVGgVtSg*7<<KDF=%{+oNG;KB$D`u-TBQDkoYcV54!Mgsz-Yj1Gxrmph28aw_=UxRlTxX+EbJl`'
    '$)T&#5V;<uzHq>YP$lYX8nA?f*L)|(7)bs1@6rJIVm_?)f$aBno8lQ@jm6bdd%}e6+Hfk{YL|_bl8?#D#$TOrtu5GX}-'
    'z2R)<#zYy$SSSd?5Ib$m9&o-'
    '>87#lg$jFgkskO1Lf~0(o9O`<ZJ$!DUQfbuba|uNDyLSKLKkPW)?ny*iO^YNH6z<r9Q6#o^?9F17v2j-fv3mi^<woK_U1BS<-'
    'xw{$izt#K49&)W%kGc#LX!~og}MV7}UtexxgOtg`97^*T!8EihOzPqVENn;+GiWq;mD}m{pDTCK*i;ktDK1%ON`buj;R^7SO7F>X'
    'O4-($J-jaed+tkSkN3ta-'
    'V)x~H|3%Hk#_A$8Kh26QoKlI&1kl1yLGH*P$t9Ps#kAGeKdedy^lLPX)SzO9RW>~uO_`}ggSGaI?R>Quizlfw1w-'
    'k=L~^mMjuuEk~_8x*-z;U2j-cF@Bc3o-'
    'bqyo>uX)GKZZ25}^3$Mx=%@53hQ*4>XK%D$HAtNxfk#dF*V^Vaek`qJ7#O8H#`y4qcO6^Ql6R&MwK$2GXkoG*2he8--47TQ+auJ6'
    'hCq7<4Ur3r(bJM6^7r4I#Ky9jI>?5sR|!$n8N`q*w<jI!Wyn)la*V>Q&iaZ{_gzRV+Lxqu?_Dd*#_3UeHZL5-Wu-z|UKn>fX-ug>'
    'S}%Dm@KD6Uzg9o_FFn{ZqqQlg+-I^R9uo^%vJtd1AcG+jy<@t9u6d!xs}kIoOvMGxuWv*W3<>gn`m*;@=P**-'
    '5g050gpX1Ig9?QrekP5;_q#RZwu?ufRstNb--^ea&D%D=9|>mj$Uk~9!7oP$z3pj4Jtku3Cy+&Mui(6^eeS7Ju*d-'
    '|4OL$fepy&B$N)mtcTD{3X2Y#h{0F|YYAoluhbY%<E)K97*-'
    'YfF#OzBD|5yHof&b*XFO)gn%!&Y$h9Qad)t$KZR!3P|ka{<;f6qL0YE@nFA^JC_^Zd(2dE9_BA}Zpbtlg-'
    'B69sD!UNxda)PUW3nbRxqbG<Ics!w+$7h$9eUPQ#XAhpswmJfn4c0%ay~!g#Z<<HqQ*L%H(HXatnwsZQ(Yu{6O0${pzsQq{V)%#a'
    '_hYVCN0SBvsr`!^sPJJX>VxGz^qw6xiX-GINWdm3Q1zxGy8!Vp!w9#ts~-H;x2Gn63=5LdBUu@ha&!WqZ_L7uTQVP>iW*BP{0m!-'
    'jm9x4BWg!|Nvm*^A3tyzJ9bd-#E;oK(R(E4;cHh4+gp@gD3z^OGtR&gd-tIlM~JZg`8B@WElI=jZmfZCx#?rDJi>8jQ?r#FT(m*#'
    '?T^;p_@W%LjSnOOW{$elAuqwdj+j?Vh;9d#$drD=nF9#<#(#b-pD~IRzJ`x6zK3)r?-sd!eW^i-}>*KEH3|Yzg6%TM-sEne$DKnA'
    'evM@Ub*H7jQ=<RuE>ho)0tw3yCjor$1}iF$WCh&62ORJ~r92RKGo#xMRt^^{qqO#V^@U=`qE%fxWk>%e^&*_|gY)5b6oRPLJ6X4i'
    'vpFoMd=?cZjUl9VT@kZrIf7bSa6$*<`nku!=D(5y&aiH~ezQ-Ws>M#$pTz!i1gkZ{1~n@lz9=^0dM#-'
    '*WQmvc%vwW)>R8RGbxxAr!#bAZu4QgO??vN77S{gZuulDyPMBBM<PyCVbz_!?*H;^W$uEPjrnfllB&8c2e%nD062iT6waSDL;<?$'
    '!D)#4>w+(T|(RJCMSc6eR>CRKcTm9aw#j(6#!R-'
    '{pEvOH|@rNmH2LE8RPEKiRhS*LOtV0cb}h>q3sE5;4Uc8;|Jp;6>WcOw1fKlCvJ4-'
    't%j_EYeeEcqWr$Il^kRHf_KBAI6{Zu>rvP1)XKZB#;Z2%H*(DZ6Tl08yn4C2+18@-'
    '$LHK6pw%ws0rS?!Do8mSmbmIo9b;Wn=?AL%Ls?4zyAd@yi&?nT<4vd6^9)cd&;V1y?q)9VUAuRAe$T|yR}(tiAxi*C+K3NnMVET<'
    '1wAwvMJ@8z7jE>J<wk>!Oy}LuK&n4U(7k%`m5Vk3n*41J3h+t1rnBHVk8d#Wgx-s9iQ~RKyEL)=b6JXnRX5DH==r<~_V;A7_p-'
    'Y5##9Gr^;|J?KmfLhDvEG5QCfV&_6@#iV&zcrKils$8WAN=GzJ4ty;b>2^O{KSa4g?;a238z)2&@bXRlK^SNS5-'
    'I}jI|b(NGF&qfKNIj&5dr6r<j<#xD<taI`P&5l_NK3g=fyJh(r7RW`hXU)zmVqO>)PcFUkta``F%T~V!E+@z~u_`B8>V16``GPit'
    'vpcy*O>1YzBQXs@vW{M?tB4JQeAz7b2Z!`rzh7@-'
    'ef5Cnb2L%=TBItqi8Eu&!g=4?r2ImDMGOSn{?>ELi27;aMddxdAB?!`5BOb~(;YhSIDTbPcI(n*oA7+C3s3R0=%)qWv>&&qQxDc%'
    '?JIt&l)vxxaV8g|xg&UkcJWr;jK&qBY*db1R>V|6YjzaNy5xD(KDYW;j^3(zn|eEfQ5NQ>4K2*B@pUr3PH649a}mlS0O)bRq|`;w'
    'hKMeHj_x7d+ttiqbgXS;elwuG7B)agOuiwr-Vkxui!v>NIzc@8z1a)CSm0)EO7|DOu#}fM)lSPzIIQ-cP1x-2=BIn%NlANe-'
    '>#o?)U1?K*MY(R0J@l$x&mrkgu$!xVz6QQ>Kx<obb!m(`%<0`3b*P?MS6)o<TkiNmer<yzzb4cW8~?zdK^DDu9M6Ky!$M7HVb8$r'
    'mVJKEibcnQ0zi(1!*pRLR%>*1C&wmQ~~mx+8EmSPxYmhu7%zTaon3&xvw0&sZf{A{Ltgym&~R3qQ7V?*Qfj(aRRb6%5nCyeXBjVh'
    'Ww)Yq?&#}MN#|g&p^YGM%UW;rzE96*Zc5|avmGl*Qn}YDIw}j>e-EgXfaLJF-'
    '~t_SRXCgX32>z#jR2tvi)1suM7s}wK$xM_bt={V&_ZE6RM54t4)g4(>0cg9NQW!;(cBjwgC|JUi@Ox5^{AH953*-J-n3cNg-yJtD'
    'e|Mf%CD~$aN*#IeNG|TF$@u6mvGr6ztG?3_-~#-'
    '>2YAJbTuyJ>^}_9<T9*H@^;cVv{GxWrywBtCCc2Vz)fj#&<hcu1d<vsabbUCFd3)g4E;&)2!h6v(e&k(==>l!jo_DKfO)%utp&tZ'
    '3)QGi#_#76ac8OJFLb2bl7OP`IK-VIQ$@lMlq#PJEYrC&K;ofZ8#V;)Iz6jcv7zX<uH+sg=D(vVQm^v@TAyPL@~0qjpf6R7tVI3j'
    'nW5$N`3`-8>`~H+G{RUfcR1-'
    'BIDlW2p+Iyff1X_XljMNK3@on^TC``IJ<x@IWG<i<5Fi1OCjxxAxY?WWyBt&MIF|iT3G8~mx{;SfP+>2=68=novl=Qp}nfMPP1J~'
    'NJ2F3y_yRdtXGG_<MKvaDx)xeusf3mu3aACPUPy$Oam^JW^nJeE5%{otNP!l1kEp>=I!TVe6{mo3?1)ER3XpZe7>iW+eq3&o>Bm2'
    'zFX87y{(^$Ub^`@Q<xHYHlgMvP~Kc)&hN(eMf(=?5Wn0<)os{3#N#%uwb7CDC^jd|_;@+Y{-`l_2j?J{Rox5q28-'
    '`lQYhQ4<VS<)vn4KD*j%j2&C`UM0uS?t7goSqysIv#!GW9)EbD<4Odc6SPv$nmx6)YL%rmPCcQvZn_+wIGOQ~4aKlb@ODosAqi;}'
    'w@GP#4N_(V!Z3a;$Ib%`Aoy|zko4A8)|KK_Hu2;sN^&B69LDlnJINju#D!!sE=&2mTX_?WY$!IM}Y@1sM3%WpQFlDe^0?d|~CY5d'
    '`PxW#%ib%!+UZowXu^)t-'
    'fOrX?9((@{_=l(~(DG~X;KKJmYBZEqxzxrQ(6&@hzbEAX3ZB`P=f&UtDtwv?l+<Y*(fD!2Dq1!FUv&#{^8*Nx{cA2-'
    'xS3@W^$2ia$oWs-DqDQwvfcLmMcJ~FWhuwxjX!47gTT_G5wf`g5@Jh&!@LZCU(gT{zPLaShCH+gJ<f}QR;e%#ygb#ZDvZERj3-'
    '8!tSrYP_C5f~hT2CQnSwWixzFhBimB&6<c4@lRR+m(`Z1GZ6bGrl#nZoQwZe9G*8(eWCc^7)|V)6~U34yEX(`0$THEK1bFq*uZFK'
    'L(OR<6GsfFnGDme(vT2uo4lPP%ACp0(y~HEI)iJEsnj&8;+M-'
    'RF6mAJVyUwVg68Li?U;eL(Sb^HB3L4<2*_Y)LGxNkYaCw~yClw=TTL=S#{WlkGE$7<GAW%a3#T=tTbeve`$^{o7XzZGxgUbPs@hZ'
    '~(^}uM1w&y?UjM9l3$b^d~V@oy31Qb3EmwjH5<je0!Hx$SrvcF7k-V4vk%@HlU&jkm%;~5M#Jogp}?YgBWN~`zQ%-'
    'R>5}0*N6hGdCE^0ccwagHzBI%Q`}*nbfKmG$~Bbfd$B%pLN5?)!m1#|xO(3f&IQ<Nzr~z$A}%%JOG{uGLPA{0J%lVb=$i<oyfn=+'
    '&A7g2p#Rv&<Kk+oB)4zwb=@3;GlhAUwwHzVobw#1_E~aEPF-'
    'l%$FWKX@4BJGfw{%PAx1mkb;3}t`KH~I+#wdai&d+$Or#HU#HjDt*5X;m#QHHD3|cz2pLg8(X5jvWZy>$a4J4pZ?uB0E4OZ*VnN_'
    'nKJl{FAT741C#{q;UK;O+}5zL?~=3_{VH`5EVhK5aLQS3}hjmBvgXyAPiiO+r`E`4(wQ#W`&>8{WLU4g?!OprGEgTnTz6vRV<)%W'
    'w|>>z6KIlt+u=QqwTnSEhiop(6*#ubm9;gLH7!9oM4aET5&+{d7<FUJoRVMU^WbZ8u}RDMz|Uci=Lrn$2?Di5pELljLs1QY10b{r'
    'J~^9jO*gJUgKVR)>Vn8;2gC0Dg%zDNnvZf81ix3}uR>wn%OJN^33-Lg%{>mXFb4fC-'
    'B`e8V4%YB}>Z^_Zcb33$j4K@>1nvA1KcsaFJZqc4hb2IL3RjyNAZxD6KfApfa79P83ck{ZPSCLLnfQq*?3QZaE;ve6oJBs&9T1$+'
    's(w_}-37dDYMdS3ap-FMS+&#0Q^QeO`Ub@1bq*3t3e4OM3kMphWi2#EF;B;OC8p@Tz*10+^Az{T{mr$&|3vOzCzqqH)<_DPik8P!'
    'beYPVmeKxaupWzu6C>pi<X|X9x(CmoA!(zPi_Gnd3sC(?2Mjs=pm**2g-'
    'vxxtueG^8t_VK%cdgv5Q5`XDB%;pg;tbJ3nRzlU7FuBYwQf3<L&vqv_X33hTdfwm&P=YZ2i_%@@cq`keQ6uhW_SENqNSVCXlvWe#'
    '%vv@lfEx4+!3`0F1!A>+#Y?aO)WfvRXw<2)pd3REy3R{zJv!Gm`?gmHy2EgrB=He(%p6=LAyv9z9)YBps&|XXm%78EG3I+g&sTO#'
    '(7l)$=0ztXWzp|Z-S>QWd}p_6>)ZKBV_q0Xr(pZy%qaQK^LOck07=FaWH=pt8LzSOPwSc#_N-'
    'y&D4IKZ?g$bhk!YH4cMI3kD48_=`_&ux`}^~LxrOTbE>dh9m3DzdXueToIf`k+;y)aByHqNP=k9Iw5YrC4{xMD=u`+Z+V5(sv;Ua'
    'kNoy<JD7F1AZ?)$A12CY~03Uf`DaUr`#~mo17P7Y=V1rOUD8P1owa&r74FG%{cT{^FnSAmsXGCb%E0=3)0I2Z9%|W~T?D(iXo_mQ'
    '}zLc#y99^RMUaPV?Sg2iM4X&0-'
    '7<Red$#+*0L3*F+v)QmWN>*<7?arc_DT$^hlp$X{ChFI6J=fD={W2?@edsnWT~ziERt^Z$nb<^YaHt=e9jWJT#Kqnoc~dX9t%h}v'
    'A5Jqhk7RSX(IUjlx>S}si@x+!Rv)EyCg>i+Jo4E*kjT+E*sqiCB!DQ^@(`O&M?UA>e8Cibci%=BBz%>Ihgt9vx>Q@dN^f?NUT&vS'
    'd?=T$=bqEH_Qib<n`i`}rtYX!DCf(GCQbs8Vk-6Hq8}|Q=UjAr{{-'
    'f)&Hb`g0~s+!qESWJiT8|L&Cb{BYd@?jg_La|7dXuY(9lmuZ(rPh6bf)zd=Q6<){m5EM9hQi8Fab>kRD%DH+l2<tS=^e>)l=@q>('
    'OjKXr(z$qqesdGQ;Z78Arq1(4;8YTxQiYyW_Opo=@>ik8xL*iIINax4<^RtA0F6Xd)YZx_c(kCvD5K!B`*{;~VmqEvdGjN@fD6X8'
    'PtzNn1thFOd#|C{)*Hrgn#3A=~FxxQ3t?pxSp!{&kSP|fkof?`$xup<b~!Z9)H9`D&n4Yf<!o(P-'
    '9a*M2kcWG|+ae;lR)jurQTKT>qkek&ezRwZa+sUP?v~+pd&Bk!0sv^n`HKQ2cwVu0z#{rdX1;0_gRm3f(hvbB5t79)@>`a7Ozj3D'
    '8aEET&P#4lhS@~S5;7kCz2E%Rt4o;q4+q(nhN%`)zb+2b+bDHy$_}tqB(t3r3U{YgJ`DC0a@NVsI#S$w>heS~be3Cp-'
    'i5V9b?P0q)EET%fp8hDwZ-'
    '`wQzM9me)uUF!;NIbT%JB7WL(JoN*h7H>j#A4tOC*3SZ0o|JLtbfZuEpM9+2~x&YDey|7MOFhV>r_te^#)%(WNaeS#3S`<}Lbk%2'
    '4NC%60S8#Ur>~`=@A04i_$*lz$woEJWXs{oS)Me03=;cbbK&$yVq!?Xx#`vUD-2)V$g?J#qGDZm@w)-'
    'u$QE%5*#~udwUUk~CyRk1TMu>LOvXthYMouxK*TdeyKt?EC8j>uddG#2V)Lz|sSTK-'
    '4pKD@>R9)?~nV^MHOQ%xQHUlzXKOYkr=o#)FNX%2C+SYF&hRv(_>7uF&LiM}0W1mXFe!+dS|F1QxdF{OeHZRYMRgZ=#GdE6L)iRt'
    'mv+6-HSKuf@D}*2@?3nI~Jw;?b&_(u5+d{>pjI${Tt!-'
    'TCF=Ov$W3tdoWzJa02=Sh{b{^Vulw`LUnTI8cP^Kg!}lh{NQvdftm=f8VL-xQDm&(mOx&gMv4Fz=>+&{&^j-{kJ-lm$~=-'
    'qKnfRKxK;;&XuOpP{RtzOc)Cf^b(u^Bq=W!esQ^4`dH@e4*M<L{@F2L1@FkiQyy|7Y=yoaY;|OoK1dXhDzg<9cVjTVAGJ*8I#azT'
    'KRQ|6`|_3uO<;P=2`Iex-1D@n9I$z>J?vuY+4g979hXkat#CV!*-N2XpCzdI#zvj=qq=iY9y+93%r1>yle&-'
    '{#uW=_hx<;V^;?dAvD5Kw)yxNJ@h3j4g9fRK^{IAm*hUrkeW^R+1TR>f;{-'
    'j5t6XJ@6^(d_aHQWTiD<V**U#sj+4I$qSdZ+|uHqkXF6WnM_K|&0x9Q_r%@>^JeW8zcIKd72^?H7oKQ`V>-'
    'B1vvx9oJtHM0(9jXppf`W<&a^!7qr)SU!>KMRj}B@>&(M{%BwIn%H2pZ3>ZRoNVs{P@(j?N-Te2vO_3*eiTRE-'
    '7F*era0||GF4D;BtxbjUhC=Q^i&MSWNPF^<%1D)s8tT&Cv?Mo&0REXu)(uf7V2QwT>$1L3d}FrB_#dYF0xrjst35c$;OgZl~)9Qj'
    '(*gQ+z5^-zRAP=V*MXM&&ob!&INR>3S5Ic5XU4Y4>Tnes~n1h_u^BZ#IXH&oq+ndRH&@i56fX(sbW0u-'
    'wsiAmK7KJGnif>m#QSk=UtMnl?D+)wYEj@I+fb_30mCHWeNTUSdNnhS09MFGG#hX`#;Q7VG*5To1{KVv5YbORj-'
    '7pvxEeC`i?uUp*&-#TD^|bt|093uu{5wnk^3o_3?-'
    'IpHtke754IqZh;eq&VC=Zs;epyDQ}1HCA+S{adj3a?Gv^`@Y|aq7yGj1NGii&!P*$5Vhwod%f&VmX*oEG|~I;&Aw>0I>U_Vu@krY'
    '#qgdLk;>w;cE|S|!S=UVwW{ZM!RPUuznD88%{hCs%^%*Ro^P5pw^}F<`cWs|^Q}mfPupspldmf9fGp#shR0cCBE#FAx}a64F^5Wk'
    '(8zKhv&~ocffW>M#oDgVv8RYoCeca{+)br&H{YG%DVA%F_!CGvD9z@tL4m(%N7_b@Dy^T_t>eeCe9L|0{Xl1Ne*<Keerk?xK?~S2'
    'ix}0VO1<kJgmqy8I~(9o%#DNK3HP{c%@$E!ou3xyZoTq(JN_;ZH{DWTk4DVOW0-3S<OPn%>>Y%adP@$gT?7z-'
    'o7Qex=yQWta$c%B5VbKbt7G3;3fDF6>ZzS1LI3V(_w#NMjOx3E30IT;rv8X6?38=1f1D1u1QTz=oE1c9Fq^+^AKq<?t9l6raMNnm'
    '*te#S(5TgyO4K!9$y%({D|K=s^-X8CT4;-%=5e(C2E7w~rP*r5WTTuTsmB`ehFRZ#%zImve;2Cqjd7TCy2rrxF-'
    '*SBOKvqVH!Fh~$#1z*d2PwVvGuGs^Lrq@yJ#|Au&qw+)-?wv05`Ku;lLHN5JJ!F>b5z8uJ*v$na<^u-'
    'JKoh*;EeO>x?MRvp^^bF#9nV!5_a7NpA{4(%jzchpG+FWiotF>ENkkJ>vYfp9F~yomMmpk(eSOFc(%c*N#4b-'
    '`V&Y&qXC&N`U+#(<_4ZHWLEQb*zd}eP2MyYugTx2a@RL1bPwZP;KMx&(YfNs43jgiSBrHQPatE{Itt^vC;HvkHwMYy%SWaa!h6Du'
    '~BPz8sj=gZ40@?uN-hqlJ~WnbMBPsR=<R97V~i@Tj_1%Np9&MevDE3D5F7#lIpJk&t&Iv?L~aUoz!B7bS5u*Hra!Z{!5>?R_$z+e'
    '@BPMty<RfxH3d`x%Z6kk=X)h><B1t<TCc5`z6jPK5Rovb*xk(okLl)^v1s7;JBDSDFi%B;ty^*nCQ=DLFDvx?P8+2z1WTRB?O9UM'
    'PIJu#I^t|yD1->M#d7F$I+mMqw_nVSB~ZM?EgQ%0KWjh@0M-)mR<fWx;eG>Z@@3Q1l9FHU!;G<e!V>|cKG|$x1y81{QO`3O^-'
    'iUoxo3RPme+LU)%q#>yCS}b^X)vx9&FbtdnikK8<?6{ad5U#yoCzf3^GVm+%q(e*W_g;eY*WGjDVLwE6E(qwlxB*mv73oBsLoxlj'
    '4~wJy$90!jbl*Z(<`fBgE}AANoU{{7+y3V!wj;Fn*1v25qpKcDHZQI-'
    'F=E%3ko6zo4o^%=mw4Dt7!efwvdKbyGDPb)Y4mG?dSpFRJr_x}*$-'
    '`)Ri_n(FL*P#B_Z@*T5{iE0C&u<@T{*SKzD$+mN{ihbU{hycr>%YGj|5fsT^!h{A|NQ)Clfb@3f%o&xzliGOZ>&Eb;vc_;eiWEL^'
    '15sS+q-=v{f}SGy?e6$8qDv(=fcgsxxQEa?f2ilg8OIlzXkShui>8;fnWY_CHem$#s4I||0ubC-'
    't(9L3(@@BJp88&{_(#L;a{fS_sY+_`#(q^v~Qc+Ehzu%-'
    'T&F<zyA{H&u;<$@eTbs#iuiB#nIwtz=zQHe*fcTh2`|*ZvR~A=SyIRVR^d=Z5aH0+lKyH{=by}Do<MTH-+^9%t~-'
    'xIh`ggQQ=9a#1E#|=>RBS#kz!0ShoI%c5+m%sk#Xh6pNdfg*}-eAfkosKrE0@&Rv@+xvm{g_JQ^bD-9}<@Ha(D-'
    'YUDE7uT2QLTYtprq1uq{F3c5eA!(b9?b#VY!>3KfOHA04dxZt9oA7W70i5a9#*tQseyEbQyZr%ammkkj-'
    '6fMn|>}Z_`F~w{qxjHeyB#Nb7h`xuS`J9JGWM@Se>jlpitYZ*otX;bq1hvlT)y5ev=N1CF4{I$WygKO?u~1gh$56+ag6go=OzJ5k'
    'S9N7-OyipsSU}SAgig0(fJ&;)h=8bd~wNSdz=CRBVxVVX>!YuNYkry~zrl_be=)EFakQ2cBMPtA}=-'
    '3{;If<^id9Li&CfgDqq`>d<6%zt<ldd0V93Q*2!~+Eu<+A@Ysxan=Oum9L*I5691u0PWLuWvX){$%z|4<F+X^&*UvQpVdwCCK*?|'
    'v548+UHXRQwU@1W+sw~RVgpwd>M~m7w#T4Z;qcD#;n{JLyDlSjF6FuX3s_I9ud7#1qf@b1`?_hchs+^XxpNMKkIh^nt4`4wsh)g+'
    'nhkAwKFRmeWqYyEii;VurD`eO<cvjlXS&|s*QdC3MjyEqXPkn0=P9?^Zx>x@3$v}MgSp61L;HNQaz9?W^wO)zh00=J7UF=fPeGl3'
    'G1sdk(jSvhyXu_XIe_e>X7ja23j`#fN8RVf{eUgSj3LlsmC?W6C1?gb>ZfzlZwF)xM;l|Ycf{bjlWbG|v{)2rEDv|O15fY<t1*J@'
    'J>8ng&z3QaW-'
    '^PKYM*>_PV&GoZ6E{62at8^H>up8rjt|xH0mICf1I)}qdZNG+!W|eAy*K1P3^uYE9tWLY}y<aPYHk_Uaft99rN|c&MVRTMcHYQrm'
    'uu{TxnN;gwoD&`NcOjS*^er8)o0=%$E=Fo63QmgY;f5V3S@Xoo+OQpS+mvG>~P}nR?r6b{JXb7c?V@QTn9c(-`LJe#b-'
    '~O)%LDU0ZP^zIs~m$HMsQ2=B&~9oW!%u@4UFkNO*>CfOwgz+<^weBSp`#7_qmM?=^9N$9k7wAtm`G{nXGv8)rf6Bk%13sl=V=4~4'
    'bUa1y|<EF#!^HUnMO#J$iO7IV-'
    'z&o$?>f$4yqNz4FnD!#v?}1RabBp?P`g;53Y17Tu8!uu11VFqxnNM_jC22?>2`jhN*=7Ykn@+@Ryt2}!1C_SfoPMSV%wETRwcp>g'
    'iP6tuJH!V`!xzn7Z-_B>?NI6yp+r5IM-'
    'z7|{oJnlXid4SBF4ks_YkCRBy4`%olmXyTD&$66S#6HHu3$rVcixxC=QG(Xa^>KxliO`IL);SDizBaf@mYF0GAt!0!t`10VLbK(;'
    '@t8y||wahxO={gR`0B&21b1NkE3{g^(g}XR^@p-UUr8a9|2~wSBwW=>TX4R&B*Rj;%-'
    'TQJTm6_$aqgW@w4qc~0IP2SnP2YYWS)vDbn5*pG9yXJub(e$B!GBUK>D!t~|&=GPa+KImz=O2`zZ`hL+)xLSK&*IBUX!_xja`6$|'
    'I`%%Z`;lA=-?l*bHId36Zz^{;Yo148CUfe>R*lm7!Y9{vyc|YDQsjx-'
    'rx1z5Wiyv#;*%0wJAWk-&vzAL>W&L)j=G0FTZsV_J$2}_rhjEV#t6_7Qvt6)tqFLCPZ%Z>|QX-aj+zpj{G=(@~SX!S{zOPh-WAQ;'
    'Y<!x|md@HUf&@dW}=EEbUyMrE^+&a^eaO^WHsn_n7vVC)l<-VGWgSuq2v*)U{ic5pEU%w1Dtt!jg+Huw&ayirKR`J4P-'
    ';>K$qkOzywcBCLEP$7~TnUuv<jsYkJ27*&d(uRFFQZx1*Z8JzlToEy&s(RZrv0!vco*l;sW)mvJ>m|g-'
    '7ieIu~%0j?A6RzYx3m7&J%x%xOtC9m-'
    'y;O`N@h3zOU|Mt?TpBWtLtP<1}e*mKQaKwei8As7>06%Oh04l$%8;swK5ch>uGrtl9GG<N7zKGw!zZ?7_1^<=UCD5dS)BkH!SA_V'
    'lfy_Y~(~Z0XJ`L2CBSP)R&L?LejU=*(_c@5+xnuXF5*gi*Vc@`cg!Zg=0gc9tbmC)XVRXCngm#qooG0=hqem+Spn{_XSW_x)oVxY'
    'lnUZ1l&cFmfFCt_OZ}vxDFMLXm$%%y0j{!24gw=D)t*|2Oa#<{6H7U6`$w^#5<v6CAs<34pve+0-'
    '*i#R{L14ZweI5pj47PUNn@CZju9nA0C?G08Qy{ma%DN8W1K7CfU>Etji3P4dowQ^RM5aign$vjX*0eqfBwS328uy{U0Kbo*i*4!!'
    '{`$g)CrInoyIgBz=K7T1!MEyRz_pMk5XGkDZtk04HL53Dp5wSe?EvmC*^z3yu6lhfKCNI)~RnoV|d+8AAk2ie%o*w?F_*2GHE(|3'
    'QD$UJQ(R>giAeE=wm^`}*{YW;~&a0azytS@uSQm@`;r!x_q`*wbRZ(!rJg}Bi}c_~w<od|i{QD5N72^hd~$IUyWV9Isdz&D%ExVk'
    'w#me)UCnJP5AF%lO%Z|U*ynMe}51#9wK+Y>it>=}{f>Kp8G=yi#f`Z^f<Z2kG|#Pd5HDC-iF1mr(Rbevj&pYOCm=Vk8D=F9LTPpC'
    'ZFm2YH2kYAhQRgf=i+?*CSCX=_qUQzKeafLP-s8~X0Sd6JE*wQ8G#oU_N#2tDALEdjs`j(Wl;B;*-'
    '(7r~Q(z6W4*L&LMvGVod9*c8%6U3<cgFuiN+Eik*GR?!w=L@}_=IreR8#gX2PxA`IWWMkSuy^;GK3aD)W4fy(YY2>NjlYb0#MYih'
    '(=Gon?0cMB2cvG^be~?}&kE|K?Qz*>tMB=mH#?l_a122`GoMbI$F*T>S1q00#R>w`h@)=DIkeQok3*w=9J22XyALQLHDZ;o{Dc<{'
    'KbzI~GFxoR&qpt3JO$kXoyT#pdx9_R0U7>iQQdDG4C@NTbP69@-D$hm8`-B7=l9-'
    '&@P1rv*xNH<)}0GnnLj2c%BsCZ>fG`lDCK^gI@|Mblxrk}dN$EK)t*25wQiK%cC|@zmU4n+O-'
    '#>{5_m_<bWIm~*V9lzA4$ksEAQH!`^~wYumhpp(=Y4c2<`|Z)*YR`A!tR0)|QHF3h+CK^ecaNZX8%DzIF`wwz2oCJ*wjlP$g}s3V'
    '>oGBp35=HGklX>goE9>^cn$oC9^a7N+gI6{0G*e7BISw_Oz%5+j>C)~OIbdX^~-'
    '59l?{jYmuqqf^Y*S{ReJur1n|AFgz$jpUNOytIXUqPD*&W48+^^bSOeZlA!VtF*Blfq7(acU6q-'
    '<v0WA^3ZH&ofyO6#dFWd#;GAK_r#(VMZ0t5AOxM6HN2kbiQU9VhvP``G@9jl<AEVd+_{;qDnEHAGst@usVrN8Q?yMNU-'
    '#!|@pzOD&$dD{#REz=9dmS<gWQ>H^q%3isgCP45ni>4ft8(Y2TB$OK@sxw_K0Ek3|>#XR(`ZrK)%!pdj-V$1}%nD-'
    '97o<bcwIJrI|M!z3Q?Y4s)k`-'
    'Yf3K3u&$xMOlM3Ug#l(qE`?0OH<)n$F_giVZ>Y{@Aie!BXvAGb&P}#B%|rw3A4&~zh+kRj9<cjNT{!Ds*{p+V;_qODGq>~TSM|j3'
    '*5a|erE#V)pCmZRRnaw$DUzLuJo1tSPrE>Ot9dMeHP{He&C5QBgVPn+&W!@BA5E>i`sjP2{|n1TL>htD$+_|3G^|t_`|)qhECCy!'
    'zYQXV_ogZT}>G<df0R|XO4Ni73}xJA9S{sHi(?y{o<2Iketbass3nCn@zNkjWRnCBTUdtPGT+;)bFUl8+UInv?$I>y)$TD1hV6em'
    'uZyWP@Z`r8{s0?Inr0`6**StOqP7^JTLqNqR0aB;!EyiI=~0l<!ziJXUD}^Y3%u{hUdKysko1!Ay%tGgRdQ;1q&RDX)db#O=HmYP'
    '9OjubQ}lw=@#G*VFxBh=fw<jSBh|bh!}zU{OPusUDC>A)0iZiqfx%D;WeM@675}kr&$JtNP={QxcUe`!W}62hV?a@RByIExv;_^('
    '|vK-T>u<*!B4Y65+{XHL2fpM=adk0Q^*-VXNiCm-'
    '}^%TI8qAf87wi{jeB)Z^a(uNInT!H(`MV0SiXG6bT&{oVwfX;NbWG~2p!i6Fm1{*7`ef{)|aQ3voO#kdWuk<QJK4^Z3~Hkd}{$uw'
    'y$Qfcx`hhojRF^3Ng7(srtant)$?#Pd9XHHN3TaV2DOc`xt=Mu~?1wKS*DGs8JIO+1vqo)T9G5770_Fj8}TUVYn=Zw8c4$nwnff@'
    'nvNKNX(HkR;p<pkg;o0MZe_rt+rjxvGTQFwUTRhdEj=!Go6$ddZ(t&=-Lmr;D&p?S+h4W?+FZ8qsPttD1=c-'
    '@%&`h8R)AeTi$N{o!V}`tGvwbn1PRq%|Tbbe73AM>NR>=t>qOJ!i0H9i=1uHe-'
    'E2Te@Jaf?hCgUEzn9g3zwYeD|^#FG)H+HYjlp6hq6Y^*`?sdgxU2pUYn<t$1T4kutASGMta&>M!CvcrRteHdFSoXgKolAw=^3M!D'
    '@FUI&YA-?pXW%qd2QR-'
    '9)YG!1Jl&oIG6mM|ISyKkF~JddavAMfJIw0hgMomP>gZHeU!+9naI!$L=TER5%|Gu5Z6c_dh0C+1mD%zvKU^-'
    'N=_3Qi}#{caM?P)n(=3n?bd@mOxHk%U#;P3m1~X*5|&u-'
    '^Zcc4T}0ax$}csEKD4zEaX;EHStyFxF_*$G4$ZkKGT#9r|#)^$Oo_JhmfPdTM%>axR0r)G_5yWQ#b(!=-'
    'AZB(G9#i*O@ae6uwoJ^F9mF#0Hq_@BA6LYoECV@+p}<$|rq(spPNikpv&)bD4<ejRuDtP>$T=t@5F_oGtr3F^?$Lw~iq=oL`+?b+'
    'FHw3pvfmi?!2YdhIM!e=f;vK)p}!$U(2jFyyXK?Nyu9wyF*1*%x(F_J_y-'
    'eS0*ZNNp8U1@0uyp>tz*wY$;2$31sxu&xO|Zpt*<d$+MLMw-VdfLd&U+c3J!l*`MrHW6K!Yi^~WqZZHTENYc@Fuq4XfIgSPbyfTW'
    'ygu*eg3G;9MdI`9XF!HI=tAJiC`_2@%pD>0WcX9L5LyUBuHm5>JBp{VTDfUw@!3*OqG*N)ZcGo<ncJrq3~eT@5mwc#_kH9X7EoYD'
    '3(R!J#mv1%eh=QsTAc<<!l<5~t%h+^Xn?tsg;^>xTm2}CQ?@Y+=+JEF2C#2wGzXnKb9B%xf!*a$OQQ|ecRXd?s(%drt4=&D?OS%q'
    'zkMM8NnTi6Yaxziq}X)0Rl3is0U6GNGwv~dar&a9p6<hi3z}<C!|8fL%f!lRRQdF#zPHPn&LJOLnHI6p4k=y)XuxZ`{?5brdk@=*'
    'KcKinRd_FYF>0!{^h=!@ioJ$8@v2sJgnH*ft&VD0w@&pbB3ttPyyp<WVW76y@>^YzNu~w8I!zfej@sF_4}MJeUL{w5n)R_2z(80V'
    'd>2kTq~F4AT<+rM@zKHR!!Sw8Vy9Y=cHI54*D>*SOaZ90$#2{Hc5e7Gj~v&QBU_Ybr_rr^?HvF%=Qv{6EgNx1C}La0Hd9Wii2KD_'
    'P-#Q@p}v=3NY&i1@d|}rN_w)|ExOTRIKXhJnCB22e`xf$+t=V#wPMC@?He!vKKyCNuuPXeQia(Ib+i$+;f-'
    'f*<h$kh_>C+=jOv04O^U{#`CRJKV@h1SSi&3BOoi>CrwMW_jlxrp6JumPdxAzaT}OjLdp;-'
    '%x81=03Em5kdchJK9Gj8@=IR|&_Jp1QtgO$wt-Cs?FjPH!EsYA_xMqQKoz6D&qmX6?^e~qf)Dc?we7?KAPtI4!{f1oL%d51Sd-wV'
    'I^kyy9!`k0X<B2<6PRF~hoe1Z}lj0Qwg<GGUPwhf<Mlx#iA<g(#r6Sg?;o|I)jYe?I9q(bImI&kU@QsnMTgEu^R^3T*x3c}SH-'
    '2cVZ2Ioe1ISBSuzV`i&V*>Z{G=u9tA{jQDYO)oBEhRbWA>KmpH<oGy^hp&Gx$3nW6_yPg-fg3c%eHswNLx8-'
    ';h?b$vOb(%I0xdC~s~~v?o3w<FR-'
    '79+>VyO`VwTqcSU{%*QgRKlZ67(Q9G?arr2yGo9;GKpq=$Mei;Qt0m;MD#X6pXgj;z7?*N6c*AeD)uJoMWD-BjqelX_Muib&qH#6'
    'wQ4#-'
    'Pd%@NoNE!%Rr01nv6dg9@;dxUs=k5Crg0L*VE9S<YbDEB(E&fyv&a;`}@sN8=^BV~HOxX34bgJK^e@UDSFN$Dl1@@T@n1Rhh*W&Y'
    '<jr-1soiOhC-WAHL4Rap}!{9jy*4cPL^h(9|sd<UE%V+&e+I?mSCuNUXG+bFJlC900KIFf2lR3|Vg=N07_7Mtf*+L=$(BW`675T='
    'Wby7(?l-'
    'iR_TOE`>IALo?rRIJRw{mV?UO8;O0n0s`(J#j7QJ;=hY}g$KF&3Z1<@`FDe)QO`_kMm8n!6&k9L#apj@|_w|9=bnvZhs$ZQJ+rE6'
    'Pwgg8RE6hz(b<Lq!n~5CwfuP!N$;dfVTAT~$kK*J<KL7-'
    '2*vWG0Z!m^pKdDFF5Pk3GP8@|C<yJgd(cFzrTFiTm#4R>e(MsZINbF%dw8wdkJ?EzP5x&B>c`xERbX&E~RpT@L!k%Ywd+4(Dr3Sg'
    'z-iwa4_nv2Hl7-DLZVxc3XLuSi456T(J2%*<umWN6sh7J!j3(C7<t@y(=K2wC&h>pQANQ1<{e!=5IP-DFne4u$=}-'
    '=82*sh=Zwj!kCp%Rls!pKJFT246M=R~&-'
    'uwRgZ8fHu09>zBrCio<JW(@hBMjq~c;ffa){Y^)Eer@2yR9uhH69&GK<PL|Awed0!LWYks)iUmu#Z?+Dp>~yAc7`|$lk={+_@;S9'
    'P?w^<nQfS-7)x6!i8~(d5cBq-o3W8ZLlV=5g+h>I))czu?WvkeIO0Ob;fd)`oNJ~4o-n(_DyJ`oCh|6brJ!^9-'
    'drvf!d<_~64Qo=po0NLoy@3`aqMH<KBk3$<<sN^Pmt*ECY0Pb{3-'
    '=bcy6BtN;d9=!2d902A3mS6i7!w^=;iE2rE=v#))(E|q(Fhhb6wgLPc<_~HP0e}&DgvBT;|y7F<_^P{(jjIQf7!nuWE~HVcpO6R&'
    'J?}HB2L@GKTn*)`u-$r=PXz{s;qp#gR58ojDv|;W55~+T)c;mznX9v9}3PGt?K*oOVmwA+=0%qhUchz~dTv8K&v_TKFE7Gfta>k-'
    'zviI(-3$1M{|uEjkg9t^vC}PD$}XdLo0=t4|p{n{NkE8D1@#r@Ik&JPm(^Euq0k$Jx@1KTdAdQ|gpk<z|Lfmp3tf8f-'
    'Q^g;2V8Lz`BkSx@Trt45OS>FaI}FLUC~)hn%`#+|sZbk@g}#w=W5KK2dkyhtwz-=bMOOOhHs8*ArElc+bL-czvwVK@}*d>cO>VD5'
    ';n!sPj!q*>6cj@EcKq@BWbVmz<23IP15&bI5F@dJDsD>wVAaL9S;VMNv5C<MV|;-@`sj0fwrDBjhfrLyw-Q<yy(UsT-dK`m(5+k|'
    'F$kEy*u{-n8qAGsWcG}7-'
    'zNH}?~MME@xB513n6DiYBY7xZ^n#Jz4=8emTN_2LrxkgMh8c1;PCA#!F)%juBg(}B0a?Psi3_|w@fo*MEu)WQ#A$}z&!APiqL?y('
    'UcJ_&cB85`@GPRDc{&MDmOaCOEJhU2UewrM@fgcd#S-'
    '0I<upMr$v$^xM%cS{y$!_e5JDwxY)y6ol?eT;hEaSQtg>$4lp7~sh8Qh&C>freKrhY~r(V2pH0rSf;DBfOo;%$kV#w^Z{m7n-'
    'J)Se*FuRq2redy^%|7(E~rK0j`tSZ9FnG{)cfdiEmH))i5h7Wc(8b9t26Pu*UD3HCe&#IB1{0bD%xlq-'
    'P;I%rP$FW2Td3_VQomX!MTArHq(2KY)?RWKhbAspw^qF&yxADGzWYyj!S162k%4<hI&gh_6EJg7)q$ZBoO?)J%+#Y`6bU`YW@IBQ'
    'Ul`C^YD4_aYHX<f(P}Yp(<k(XZlT_K_Ld0;$$aJZU8xs8bZ1327r4d&~&9S$6&!t8$m{N7^uFMu&(SrHeHmf~p=?xs`_a-zFD!Ls'
    'M@nTR_X52P!>}t#HW;dC}Si3og($!_4#`?(&BA5vKR@vnWwsl57UP)tpRZ2_o+I*1nUd7nGUsuIAEUex-C-'
    '&+3LN0o>e3#`<`Q5VWKIw&QPeNH)yp0ZFK!P^Vt_sY(^4xzHTD2utBQkZFWA##ws_zwf8jE)1x2COLgzm9a4E1f2g?p))Xj)tq2J'
    'c1RuFT+(ypcL`HXiLs%Ny2pVRb~eINM)QrC?h;Yvb7y@#uYiTK|L!0-'
    'Tl7b9VW5uU&zA_d_^(rt<~vVGu)a@_L>@mZg+vZyWbo)1swq8Xd?Hk1bCb0ANB+&@k^ka=nX8KFR*(Sr*eQL>R~K?k(l|b*uLD6;'
    '<`mE$QG|l&|Fm{QF(b8o(R4r$$(=Pl&Zyrbk8~Ya5jIi*BXYS-'
    'vLksiM`I9+hNadSm^$Z$v~+s039MEsbLkskf(Hf+Wtj+^Et19Ov{dlr#vut`<0rX4VbZ@HXz%h{IZA`i-1LPVXpvziqllAz-LZ+N'
    '7Yu#{0P?NO5ptd%FSh^|2M&+s!45b`_mO=7bbl<bcAL6wg3rwUa$2M=PF&H-'
    'ZLHRC+A%0h!&J?KroYTqnSYWBu#oysui9Way!Dp<j5Ic`ISdlV_>DINRgz*4;$CwucJS5Kh*vS3l~AM!OG0noWm~dOI}D!gw-'
    'tU12!?NlHd;e&}81i$acD%0HG-dnn^gp9*(@+A)pZIGG$LK9F>J`hy%}_Juz*%=&5d31mnx7cO_Fmb(mbL52e}PPDl^6$KVTPO&I'
    '7R~V~JmC^~L>n8}#RaSEP;)i~VrL$~yc}+$2VHIaU{?Qs0YexiicID!1r_S{-^b;R|3w-eLAI{ilf2+j3*|d8qIn7-'
    '??)Er)sW2%x$!{zZ<VP1Pz_<#^UZ1T#)SSbohiVk+C8r!TOa0|*=cub^@*Y&kym47(cYik3&QPzcEPOzJ&2FFYYjU1FlHfW2#T55'
    '5@f_VB<*4cS$$&yvzJ?)8y}r1U{I~*_HUKo~!&}nUvy`z(Ef3(8E7k8Z1^uK_#dr(vi{)Z+(@j+cB_=+=nbR=D`5wzd`Pk~=weL<'
    'QxtSa3<RzYzi-~E?-'
    'V;rtXbEvPSzYQ@ep=M#`Ll<uJ(x`E&aj5G*XV}S{oGztZ@q47^kQuSu5*31JsRfQIkhsqcFaZZJ<}DkT>0^JYn|$w)UnSMa8W$BQ'
    'sy!TG6W6@nYbCPF69u?Yk%xKfBMSLs+#egJdo>P{T&mQsL-'
    '5`CbJ#I<;Id}nxF>PL&2ilGjLh|P{&s+8IEVwht5X~^ozy;z`WML*8Eo7Q#q}l3bLXO_@{I|3scI$^jyP6K@I76w;&x3JEbM!4d`'
    'N33}UpJwK09Zo88@UHo0xC&*`a-'
    'Tfn@qEmk7zJ^Qlo7)l8DbI$aLk)w80DFE+vze}IV@~eN`7OF2H=OnA!vEF0V5yXR&#5~>yHk@-CI!MbT_$qcPw@vGpTB7*#-'
    'A=l;1LS32n_=)!C$4v85KTUfhRKi$NGuo0u8V({zdTWCbRH(M@CSTy7O1YesQ7}2qT=b^I?zU(#{AHJO163KAKj_KxfW<VBXRr?w'
    '`J3exPWCS`Dhh3s>M_<*rqrhEk;^|u8xPlRZsbQQ{7@Pey0m=u$Wp@6w%e53Wcq4JT$7aTf@B6tZKOvanLI_@k9lVqkHYF_LSD^f'
    '_cq=V<|WFQTf&Va_t!-'
    'uS%uI)QA=uR7a)BTwHFw`!$QZqx5>rz({}i>lU?Mz#C~4cwuHJ+Od$9Tf>S<BP{o9Q)O96Tqa^85`b%rSDO?k4Bwx`$Rh4usK#fn'
    'B}WgAT5+`YCi|)i_MEm>W5KtL`{<RSb)j9PIZf<~d|zod@mdkTjiE{?wMQhp=3VzT64W4vU$q{Bq+|z3wi>~o#EY};$9B%)m$Hc9'
    '{73pOa^=mnqCcU*klD)DJ5mVCgMPY?4FJszcbDa?A&>~-'
    'wG%(3=GHC`GZ<eH?~p~OYkY3sil?b<KAdv%2$ov|<uDsxCrJbb!<S~{H-'
    '$kVSN!ZCt<0sP(Ya~}PG$uID<sX@ax}=VXVY2lG0#7>vNF8UuV%H@IfF;n*(%sBH}+or(*16GO+gf2q|>UmGU?zCN`rM5@81RTIp'
    'QApR)Ua;J|jMXv|dc3vAB>eJ@acLG?#z|#WgZqe66fNq;nX2f&HA)pI}8c)|b^3<%PYuS<xU_U4)HIfruT)xtb|N&I_+jp|W@`>%'
    ';gOzwH}<{S}*;`;6b^2ssR$q*(eDRe35buU%Vj+5;bI*dt@SXqm*lwN=*w;0%Yzu7PLG>U7@QhhEY$k%xVz@t!Cpgpm~ZVyw^&@z'
    'TF=ypl?d5UK=A#JpcVRk@t(FXfz#u(kNK8a~9I;zM{1m<H<NFrYA(QnX_W5=c8?DiXk;a#BgU>Jk<*D&r`u3kUW`z?+2^b31Xzvc'
    'ZaH>pNytTs@tK<(7!PVHjN$TVA)~H``um!k4yn<)^`v`Yp{h!|Aj@m5sl5lJeW*^yv&0zedA3VUzC{c76gy;VV}yo_dc~iglBT{2'
    'u0OF4(A4&n*l1gc2se4tLvm(w$`c)~xpurAo7w`pZOWJE_S<jl3lIl{vI{)j#~F{cyBjWV@{j?Y+}^t)2PG6=Lc~cqb0_oV4$T<G'
    '98WryNPEF<(CAW5unjHSx3qx7CGuJ&z7b)ICh%iNHU*&{)Rno>OfVjf1tJd8FOVKDyI%3pyarJ~|fWwI|#pc&9{90R;m}ELcHB(3'
    'Z)ZR2+O2(||dHSbUx6J#PF~K){g-H0SfOT7%ub6+(-dacUKNHMgsJ&Q0C<d;dNv+bba(A9P1|Vbvq4-'
    'T^=6Ftqn9?~u3Aaf)^L5sEO=ZQdUNmH$wf^8*lX#K5u$q)#!fGu#**B<K#`o#mXz)brxkj=h`e5cQeP=>=MW|Bx(wNF`&lJ%EEkW'
    'k0Ex7Meb;akXV8@dY6saFC2a)4Z#VFgt1L*IHmKv8NFUYR8VpWux>MwHlpWCAf3<M(M?|-S&qNGG(vhbEVROo72Kb-lI5bl7_TB3'
    'xH7UG?xPLu4cZ*cinz-'
    '7dOo393{Hmm3$h0+sRYsDTxI0YE1}gi`_WCGA(<t?=Bt)7Ai@RUOzy&ntUw0=}*&AR_CP@J7AiiVA4#32j<=3PNeFXv9<6vf9?)8'
    '5%~?dR-brBS-'
    '67JfFkTmP`&msPuE}ZJeT{a%c};*_t{(vU*0#;tN9F$3e_ni!C5j$&hFs@yN@=vhhDu~6^7;xo6KjZ+3N>vv=s{XKAafT&sqJ3lE'
    '@2ly^LSClWOP=TIGN&<ySc>7g-'
    '$#miJK2@2?L#D6(^3E=$V1E!kkO5%$P(wXniGJrMHwT5I}>b6{V1=*x*@*q8lnluQYBicqWd9OmcSpb73D5*^Uh{o5)jy1hfb+aB'
    'UGP5ANbYWY1<pC0fiq65Et`G7YKF$_exP8rSVH1ptQGXY0a1|~HkvIhIXHSa!Z)EiEnTux&c;|j1)I5?PscE!<XLzbqK73UQC6Z$'
    'F)4v=Wmr@0Yqw3Sb_+ge@e%HI&lBn?f8ut`g&>MgyFChes*tosGeq+eEVMMC4!zQ3TzAF&_yO#|E{HcA$C-'
    'Vz?A`D+a!m}xw^bF+4uG(<J4jLr>rZ)wEwpvO2Wp(&FFrH`u(IM&ZO+P}Cf7|qyv&;~m4Jh+BUXWKdqn%Y4Wir~Tw#eQ#HporpaP'
    'oCJ7W>1*iXnaI_x5p;G%~>4XKklSA-XsEG*jlo@$m_@ZuzDiKA1TvQv$HF0a2#$x+`2!`0$yPsLqAx}hf#W-'
    '4710y1Ae*Bm+^hqgc)}QB13^xETFeoV#2Be6`p-'
    'WcVgFWgHv$U>U9!0KY)zd898&?z3lCbb74nCr@(!t{^)+JH*4xK%m&2Q1EFu#P%+yx{H1WCaUM&S-'
    '_89;9a|R9M*gx=k_M3~%OX>{AESB;*tHhh#i4PVhyj-jA?JkVmQAEC`BR|0G;8fSdLuW9N1a=kqs8$#W}WvO_$=p_&ft7)mRv!tu'
    'iq;(`WcKwrZ8Y>X5q)S4U_HrsWeXx>(yaCM2j|(v<oM@RGg;s4)9>9RL|MOdouaTn%K#CFBC4lEIAe``O^Uzs%l!=*Sd9uszJ4)s'
    '8AOJJ9(&=+5Tj6+12IJJ-uyKo>{r{g!!})^Fimd-'
    '_$vBHE0$<>OGH@dd1=MSG4A8ctt)a$5GGbV=U~4vuwI3k6%xyH5z2tRqQ^_DLLfYW+z{T^TN~t?mHx#k(Xe+<l96lbILI9Ci>fAO'
    '=_ALpeG5~zAb+4LXF*4z<Uml%#iVb9DkeuqO?PHPlF=ygLRZE8zyJDZy;9aXlSYJ3OqA^TR-xG>J2K4lZ3^*xv_E)_B|2b?R1~PR'
    'IX`Hx&L%0?0NGF+lpbG*^BUKm^slR&ATer8Vy;0VoMWaF8UJiXuKnF1yA%AVF&I<X|bL@<`(g|^P7Cb?wPHHT$dIr3D%!n_G#*kY'
    'H2|8?nEP$Yp-'
    '2SDLx2Vb{DWN&sx7uvYzeay3dzl(BQ=kJdJAV)_n%`3nRD3{Lifp<=W>0?==K|4sU*JpUIxr!uc!OU^h3F#opGZ(WUpCrsZy>!)T'
    ';6)JC3v%}l~QhD`}G;iZGI2Z`PikMr6*7H&PS#S@r+R#k0l4V696wc1H94Ex7CS!#pw<H*k$dg<oe_!G~n+bxo8hq>!QYHZN%?7r'
    '#9F4A}8CY333!W3Ft_P#^!TPNu()i$?(^7+|*j~}RJgcM?MYd6UGD+NdKPZXq9Gk1<h?XQy3Ep)8Lb&Ac`7gMWN?wX5L<LvznaE5'
    '>y-7Tb)u6%h3<%dSST`f4ngccqH3g=u%dLs)|%VoDU-`i5{E&-u8@v-'
    '*nubbfKZsmnoDqayO`#8DX&|j`PXw2y~u6ZDl%Vx=)UXFRb@0Q54pio}FEz`9oNKj>NKNNEv9qWo{y-'
    'I$SXLPj@ptIB4W|Sv%_2r&B#9~wCdag9?B-RZLBD+>Q;m<U1xQmi5-'
    'ZK!6RL94mmz!29l|nE&=aXn!+RO8XD_^5>Q4*F@`t0#7rWU08g$aHzy#m5VesQ^lN9O(9+HIn#yV?L-'
    'ZzfB<G~Q%enzuFK1{|(377-h}o7zmp9PV5^o~oOhD^cY$MBu{{!dT%d#-'
    'hb{Kj>Jg_sVgVskKc5s!2WaQm;OU9V(2X!8KWqOroQ9T3@ODfmDGG&!~GH)A?1l?*)s&EbAxipu1y%twL)LeTI(}1f4)5Kx?iZn-'
    ';7FhLYXe@?&>?_SHwK$0pro@Z*dCETcg4Akk%8C9DE6#yxA)g)dZ2TJ~)9GiEorJ~XPuom+AALJc6bIE(jrwO}6TP)07!k)l@uiF'
    'fu?yjVSsEE$4ieNWNyK!{uEtv#9;+;Z|`CF8k3ZEcQ|k<thrUFsk2@6X~XmxNH9sx_(m%C`z4#8im+K0(VoYyu2dkuv?BI^AU}In'
    'gk6SC|9e$jusLO-'
    '<Wi<G8x*kcnT0%54E*BQPB;iH`Kh1z;~X!2$#?`k%AjgCQ(v{LirpHPw3lt3sjXPX^+{*m~;tbA>t`73Ek>kDXqnyoGl3_L9yK2s'
    's~u=4IbMo_8mSEL@k_pbSpOIEwO57w5oWV)}SMKFubm$Fho(kJEK~(`Pc#{hN_<75txdq3MJyk4r|B==Nse8`*G|Eb_{|?}B%0@{'
    '=?}DYc4**?9F+K$P6F%S-'
    'RI{=$zs7$=^{UHEWkK+cs+<%YkUnEi1l2Q(r3;d)Q8AJ18iotK*PlyLG}4qqNl>s#}6@(Bp3T}NHOxE|ID9KhJ-'
    'Ff<lTdDIm4Y-iQl)v9WApj@OFtcv-S4_XZHxb3q(jun-THXv^uPR{Pb0_#hk&a(cYmd;|gBQ=cZ&QvhzSSGBQ@X;>JFRk9@wLTrn'
    'fUNE~HjDS^dLIuPXB*G8x%>hbo&^R5{YY4si$6ICo+&^5uT1Z=jg&SJVXx&pJT8TXP<Ei=cyyR^=N6k?o2%|me<GyVP>wW<y?bB9'
    'l)1@-nVGQ-'
    'x417tZf8@aD_!0z*sFWjP}g>rT3xT+x|c5|Gefv&9U_6%nbqoHDZEY}`$Ys?K!lZL|K4kijM1|@t7bucI}N`F|E*UUGWkX|e=}AX'
    'yBe7Gm+P>0=>r{%Mu`~Z*n3&2J&gIgi$>@hI)zDt%2&PI;i8vV3)H|>-)mqr?6UPjI0qWd+x;<A+-'
    'b9TpA(aX)vFj>7bGFxVZv_(8QpUE*4sdU%%)a9o`4)WR{FqBtofw8WDTCrh|b2jp9S2aW_#l*_gg3I8vi^o|7FwQaW<!rxL)8I8Q'
    'lD-'
    '%xtdBR@C5P{#2PWSFVr0M^y&<v|mbYSxxNjGI<$F##x(!7Y$7<l$OT*A3FNk^yMS7naY|Yo}ZijD?h%yk<xy!yy{4`Nvy&t(LYT$'
    'VpYRj;l$+N-mAFhN#I&2m&T*w=S;LxS9`H$jl0pZE8(joukU5*5Q2pgF?RADt-'
    'A!{2likf3z&@7g$j2O`HOP&s&NG{@N;vq)klqCYWQ@z&YuROZm<_xG_=XTCLDGlh0fO<GO3deT<8FQhrTS_7M*eXtPExBcnF4ER|'
    '3*BP*KjOigCRvj31%(YzvZJ#j80E323KT3|kaE18C88B`LupAX}_`Z3<nbjhKdONACxff{#wlNGv_j_D9XVmEh@YOR+Qbv2eVVP^'
    'w5FlRrdfW$^xK?k#=gLP~x85H8!4d3*E2EL7lGES4;ACF`20=@<kwuxhP1tOl2Bm}h`PVWD*zh3clHc?3QDRK+i5C_N#p+FBOyjJ'
    'TJ|r!;ao=J7Pk*3jL*EzaX)z2^2gNC%6NAb8#g=ndP$qY-zm;n-'
    'MqhA)FJjY)ah1NuL$!B6Xp7odk&tl{k(Y}PuEM)rb$u2s?+ukrVs_!D_R+<Y62>#j9YW%5v{QYp<RoP<6&KELgdlbl^<f6$+)AKn'
    '_kP<fs&>b;W{wi=0ob$PL$v<sX6jlJ?8$G~&`NKowm1bS#{v1;!Qo*M<8ZR^1wrsI1-'
    '^oQ^}i}2i|Y5bvvf3j5mnfkk+FZ1Pd?>;td?JwfXE>Z1R-~G=2Rmv}V%U>6$cBBWc8kvdyzm*iKM}4OrezB{+H~(AO-'
    '?#mPZ1c}{{4?vHP53MCH_t{GEvCa|pWYF3c0472bMycC$R!B6|L40_H`?i$8AhgS>_XkP!~guhe~3Y>|Lc$6xt_aobv5{}$&Tmh*'
    'PW&x&4U@eGtpY5@_#Dd>@fCy`?`DEb$WR6Z0&tT_0McS&~?XuSL&*7xUBtM>?h;o1?J6jf8FqJsg9bNPVDUV?^Wsa&V!M6=C5|`!'
    'ox}bMXc67b*8#$oPIS4{<A_=Q~h6GX7`V)|GsLh+Tp*~|KA?0^6SB#zZDevv^WyjzBpa|A~F5Xec&&)(mxqb|N1-'
    'azkHp4{m1X3xj8*0*8eQ^uh05#1^%gwpc=mj{C_9@TciF;wN+=YsegF;@b~NeGxa@w%<$dWc44IZI9#j$s`@X%fImwty|4e*ABR7'
    '?M;xfX`X&BLEa5lfD+;cEbKrk-+W)QL|HIwjZx;SR_oF{XfBwBw|9c_-'
    'Wib3I=_~qRsfO|XTw%O-%<#|Fzgrqyeb4;=Hu!h(|J$>H|MC9-mDq~9'
)
)).decode("utf-8")
_V51_BASE = types.ModuleType("_v51_frozen_v50")
_V51_BASE.__file__ = "<bundled-v50>"
_V51_BASE.__package__ = ""
sys.modules[_V51_BASE.__name__] = _V51_BASE
exec(compile(_V51_BASE_SOURCE, _V51_BASE.__file__, "exec"), _V51_BASE.__dict__)


_V51_ROUTE = json.loads(zlib.decompress(base64.b85decode(
(
    'c-qxn%Whm*a{L#qxlp|*(mS<OGcAm|Dd;i8xIr`;@E8V+@uKaWG5>B!B&%-'
    'SjEsoPbBk=RL{P<B=jM53Mn*>d^1m<s{kPx$@%P_f{L3#dKD_?)>BZf}i~soTzy9sNzy9LukN^1X_y7F+|9t!TpBK}Q{(STC^N-'
    'nQe|ho4m%sh`;p5HQFK<4-xOj2<<No#6e|L8m_y6;0zkhrD^{d&hf7-'
    'vl`T51gYW?l^Kfe38f8qY{?IEv!e)rSs_g^3L=H~Xr#X9`@(~tZ8hj0Hed!gI?r_a;(`D%@KZ~pS-!{d`y-'
    '=6gFq2udMel`C%F<$(x<MR%Wc^K&G^y`j4{qW`8`?tS-'
    'owCngzP&#Ax)1MP|NQx2*pu&_J!Ja*53@7-emK0ZU+`v+-~5*spZ4$H&mIR?$12Ro>(Bd-vne_KB0MAT4c@$-'
    '8!3)V&eHuuE}+?FHlB>^{)e7X!ZIaud0dGPR+>)HqcP*s?G0?ZHm2+NRR_x*1{qB_GMq4Z^P>#S(4W4YH>Z0TSZ?-'
    'rXB%HWLnlMM|I|{eDUO1iaI;B#!kL<E?uY-of7*QVvWY4fA8ceaF>xAv)1n84pGuFeSuB2f_L(!7F8nlVy8Y`<^ZEb&XDz!OZF6{'
    'RZnnv9>fczkR_CSee*=wm_`i|o9)CzIvefhEW>{?8$q($YGpAycy1vp;ojv*CXonNHpHG`U93Bqo#U6L_{{8;V=U@M{|M>ac`*;5'
    'uJhIuNrcW<<sNe71$+vvFLeTdB*X#8C;I%Y+aB??o?o^Z$+&cdKda9AHYR%L9#tnCSTnNZlw#Tj(!rVgv`?wSlv4zz!G&xiB@W`e'
    'D!;^=Jy{Q@p)x%Mbp4PYpKHYqoZ-Ajw6zubL|LJghuhZ>)dFQXX(${CM?K$U}EXie8%|g?>T6mhBIAY`#{>V?8T^d^o!<~X{I}1x'
    '|xF`hfXm}`<aLC?e-'
    'qYp9T3FpEnkE4}UEjbL0hdt4aB*5eoK*?j$jlz@9tJ<PC$=?O%jfWywdHe6ej3;&Xn1;Z8rFP#`j4+a{#A{axeCW%J%qm+a<B}07'
    '~$wbeS8fR-7a|+wU#WorVn#<u(dO3=q%f)liry_c&2S|k|ti|^UTX)j=Xn>&em=7d0>DKi_4f0_U0*2@@yVRj)u(d(u=-'
    'Rl6fcb9M7DR!Sg&mq;pS@xP0un;^-kh0{H6Mnzs<`QJ*CEPzXw|8J-'
    'S%dZmn?{KtC*!n`r9(YOqf>o6YN&eg!MuXMO9^H7_0U?gI~VLu95P9N8e`<^)%`fV&gh8S-'
    '#tf!O<^SuoEG9JF`dKq<e1_d##msb}%TIpR}!~u#XYtr@snCo-'
    '=A#!NW36n<Te3{p1JlD*h&FCzB7i?DmfwnU@?CTQwc=P#T=Qw_tv+f-KX<4tSz_?jY-lB`%4h>*s41nFhmWOyU$)7%de0}@F{^Q5'
    'L)h5gI<6O!~oJi=7R{Xjl$Jc)qgCI8gDxM#7I|6h}{hR5}hm*(g4duyflP5}UBJfZwKe1%-'
    '!zGU{VF?JZAmjMJ`F%TJY6Pv>mk0=*31>vUJTaz+*35U_$p!QBu4QX7e4RsY1a<uV<TVt=z{0#mGJRQExSQ$QopNT83EjM3a(%56'
    'A7ra@f(H)ccz)TrSN&8SBdVNwZ=1w>;{&UCcG+UI2r<iIY)|MTR^deoq}?_WCYGx*>`4qeT*1!Ab5H?k<9R9q{!N^T$>Q&$n#fP;'
    'C2rVsBtr)9V~-'
    'a?l5exGEYMDEw?tuV*|D$P?|73XcMZedW)^6We89pvTr$A)1sjvZCvZ|{*LahFk+1GW5gX)W+dOUtREpDK<k7&?6`pn>(;9tn_6i'
    '&Xjg>nU|D_JW$vxQN(bc(b&qx)YI}H9@o%(s}#Lrui3EUL&rU?0@bY$t#9M5%_G>V92&r1STQLT|3{ybZ=>Z#xcdOZ0{^*j$p!|l'
    'z@`}?|AeWxA9P8n>62d3!U0wKdm`R&(h^=(><>xZI|&Ei$#rXP1vhP7X~2KEoVmg(L?eslZ_BRDlSIZjAH3cnkWkW!Cg4TkduwYp'
    'Mcyu60FG$48Xg`AHJUJgs>eu6rv`y751F(*LJkRKnd7|X16mGJR-'
    'U;!Q{I66hM9}K%}iC3gyx1<gh7b7O|1^#utmLE*y#As>}X2sWu18v*aDGCQiWBh@-'
    'z`nH@zKt#o9f_x;&@nURUejSu0NbEFnWtW+Z`IwQF|suf{w5pyxZm({K0>+1v?VoAT{|Gai<a9iQ9BGGQH8G4Nf`=|a5#$qb~q1J'
    ')P1Xv^;J3II`Lb91H8>XG`&pPtW}aLWA5zKc@$DDIl_HG^K6B~363CMhIKB1LogwVJ=h>=4T_eJF<tS8|GhF9XpBG*&;7%1=CR*J'
    '{JYXYdyIo)^m_OeaKz@Hs`<>vCnskZKGn0!fQ9fEBG#|n0?AiFcIrOAC8yUHh{qNw5Ie!UanJ_?PyOL+(rDQ21gu2$DGWz>+l8=<'
    '@!!3HJGD9a-'
    'k}cOU_}tB+#$tYB{i?YaG1UktrRl=<BOq@iDd+o9)Q&bO02z#fSQdu<Zc*GPzL)l`T^MNDTQY_Cl>g`hS~iX!ujq}0Chg)o*1*-'
    '?gN;)u(9bI)6iyc2*|?*!PRLfv$)BP;Oy*5O1%`9Q2$gxlNE5mAaEq&f;k|Vlme_R9-'
    'dJo(i|Q*Dx=2_29fIHTqFz@N#lHU0DgM+{x9EDQ?S<_+!i_{=4Rf1&rWbOC!eweU2S?u^6Of?B>qon>NrUED~=m_rpUVPlz66sSO'
    'a)@l-'
    'HzK8D$JL#=ebCp)u&gvIe;bOatR;t2wSdXnyc=_FVZvEkFcRk}76L(s+0%W3##(vH{z9I$C7uiTdO(IgtPyg2lk`7(NlbWl@_Z(p'
    'O$#ueYG2E3yQISv9=uD~R31Bvu4$WHG^(c!%SLR`(-|o>0w8E5;vsmv|M?O-'
    'k!<YZFk&T1?i*@q6)|143i)D{kKIF{ubiGMY!R2*lhoVU`kQ7KC%WW{k)sR@SQ^UAZ4NWbQl~n^@_ojOFq#%e2AAK3q5>NM#TuZ3'
    '9r`xbpu{mK!q$UP@70s)Q)iOmkK7epeMcZlBDKJOQ(nl?Y6mVJw|qFxRWff%UA*HYrCO1i~8j-'
    'BnDsU1sfWpVjiY$z*+LsT_218~q^+%4-'
    'G^#k68=K%LOd0ZWIzO?cd~3P5pINS`NQ{j0O>s&#F}lxZtlZ6`vM&ulM)tD%>yx^(S!F@WU|Ve)8|qmxGJ2nrS}j2Pw}0I(JZ4O~'
    ')Vs5-'
    'A;)|5C53X1;Au|d<&M<VV3VbphYUM>sJwn4?ZU{yhl`k*TjwZO@<KBY^Eu7+A?EV%4=nWv%ZUAUW>ViCm@Vrm01$uX$uW(VB2y1M'
    'K3^GIeO(-'
    'G2A&svFcAfrRzWG1`_e}h_8D8hG95qV2C)cHKsE`AMiVzg4{4AA?<vJE9;O;5aPC9D>g0TA2tUve{obgNNA7&hfsf^KVdJxbi&wK'
    '6%BTAPdE!#xk%IC@ta$t$F%g<G{_mCTsDc#z!<MH#@5DA#M0%^2rbSPyawXMaIo-1l^8g2z-'
    'aC?;4O8#HH^B`Scv24&||Uqrgf48C;KMuyHDx5CBaoNtr2P(@~H|MZm1EXm|<A=n~jHF|^(Ra7-'
    'FtD1gUs_Io#6uYnruda*}vosym$BoI)LKMrln<<|g48}XnH%v3Kzy)cKG2%>;VZX=aISjy@Hi|>Ix)OlqIGti2)Y%PeqJlxN0uBW'
    '$3J3@K^J(mDiNZX^GN~C2_-z@w03wp?qgX#LVyguK=$E5MDtJ@CQ-'
    'f1V#1hck(M45{DZGIb;F_|(z?)QXq1{mGt@>&L2S<dr8SHmYdcTi@FTo^Z`uqLoUybE$!<WM_0t^ue9z=4(^e@ow(k$SqbO3`-'
    '9v-*eE}Cz}!=+>&@Of}^gZPUhGwh{T>xEyMR%J|HEaC_BRRN-JyxnC<`3Xd^D%huEhOFaLLzD&|1GecYK)RU6;PL*$Z*Fcrq#IC5'
    'q`0un?o1^Ij2cDf1z{8^SdTZOT}c=x^?cNl(sBVAl;9xL3Js%QQQ!za{SsktC9PFB9u9GTFUdLQ^A{l^DcnQ2y7kR&6X))W?C$Rw'
    '@Xd~}5u}Ey%a85FhblxL5Q8H?Ws*+Sx7V~IuxHkHB`u}w+i7tp+0}(bUa_nREbc#LHRZ8<^sFkq?j+YLL(9Fnq&5}u?@r>eEv}|s'
    'tr|SQ^=b%0HTi21)$<XYG1b|&tW|{PX!eA^SVq|zkVf6qm}NByO5n4rPdcwSuGtS51_&Rdg?}!Ru<3AIr5BEz7gbZ&?qd;(>XUSJ'
    'VQC~0KmVxNqc<z>*B%#>6hmK5$t$2hknyyNN@s#VA{P)?(%@AWAe2=C@Y)(8-'
    'Qzuhw_d9n#unyffaLp<zj*uZ&rMzlA#5P`6TAWV&y17SP=s~)Vcs{v!`l8}M@QkRLZW~-'
    'PvMgCd(d=xAE5O>sx8v?Fa%VnsUe0tMUW~*-yz#M8PgV~H-'
    '%FCV4CFmNNOocrneH(p;q@zr|&q?2Uuj{k&od?kryPt`A;AVWk}f6E+5wSh~GHq!uLB{UJkG@4QX-8?DnzPNYk`-'
    '6bys7CrXeBgQiwOD_F(pP&H~_pDh9jS7&El6;!0RNlOKzau8r=I^bUURMkr>1m_9-'
    '+l;Q^zJ(v7Qoao<K`V8GMk1dlB}?0)%$g1X_K9jEsa;Bw;fFC2NNeL3PpLL439mtnG#)Bp4SkP3CjZhfhncOQH!??>*u`-'
    '8@N{#y2J*!_#yxc_eRhhnTr)^xwQkF80Ai1)rDvUihq0^CF;RNvE9EjXgX@i#AL$(OqDu=B(fpdB!`K3RFf7u-GUh1U-'
    'HQmZ=JxEh{+dt=WS!Itx#Pq7;Tc(`T{cT?Eq+{9Amn8>Rp-'
    'E@T5dy=<*($EO~%fH!3zbwp%dq#9JGX9nj_;O&dBvPw&5tB2OS5g2sc$=STzYGSZrTZ`z&OnW#otalASD}yjH@5n?mq-'
    '&63bh6HAVyps6M#tLgFDE<4k)Qp)G6bROyVZOf07dWwhZ3?Num0zHD%e#@0cfz;`tajnH2ie9FWa;@lmC`kq%CYJF8_?tYsZ9<&9'
    'ZiR{~=Bmmi?N7EIbB;1*wto+nHsvWL%gahEPzq!Pm^}O90`ty9RU1G)&k?wVWGJYX)?>{X(4#5(!s@l9S>h^($O>3gF#K_p%xml0'
    'b~_a%lsKx~2iBmL+6?pzW1%yPKbm<qnkixlDvLQ!>oV@~tBUA+nYQI<0W|vxmJ(3(&`R^_i==tIg>L1HDyHMwYxGc~qT~C7dNA75'
    'nv(vQbxaka7DdEQY!VgJLVqn(aW2>jTE?6mV70NZlZKXVX`>9cY&OM47RkSYz4iPV*x<@?&BYirM|7kYb#DY4dg5yvvKiB;@cu8?'
    'y&!zOw4O#^XCv=MoFu&of3+m9F)`r6=*CkRc38awChnsFK@3O!iqzbXuh%Eiiy4)`K*Z&JS!ge}KXYRXdpw>c&umN~jbU4i$`iPZ'
    'YqEr2?K+F}3`dEj#}cCg6i`x{buQQA75H@4rfw*F!f3g#CIfiw;i&{4h?No6drrUE!Iyau!l76<nt~}q{x<c6S&|hoBz1)tQl!_I'
    'X<YX`w|7mc?l`p5<;JPpnFQOC2RqM$ofbl0;n(d8;Z`MakK-71p$-mYr4eE*L+P}I17{GSEHCWS6`-'
    'FS8n&4SPw_^%;BeS&7L7px`sQ4%9a+s#sa`JCBYUZYt48K`RMrC51??-'
    'T5ehO4e|1)Bj4~W(IP)?&45uqD8nLJ%UBPq!xtijI*u^RI7v$%Qt_yMrXG<B#&()cbypMs!d*zmhau9e_f2d|1Plvemse&fN<^NN'
    'HO%4Kv|6%gE>HpbE5Ovnewii@ZdgY#;g&ZG+uqed)c-T4Ph6~PI%{1Eqe$g@(rCua}-9-'
    'IaIa=Q?i?VGO0yfwk9dR;1dtrR}bD68KB4FYEX&iY1Vkq{C&v*W#uA8pXFxW|cxe0A=Zz$(xJu$trr{a9Y*qmZ|k>Pa@UF~?6k$M'
    'mW=P7ZSfdfg4U-'
    'I66x|NrK0~A6J7#uhHQCnG)`xjW>6}X6r(5V*)gOgQsymD#|M4p6m$?|j)3%mTX1Jv?vx@1{vIVw_PoGe}XgLNaIou%#$7ScAW(`'
    'kSX3~0u;6<ew)ra*^m5Voh4JGGs{PNoE0#zm%JJ(?=3{?1{zKO!y>@|RqgR(VTptYA6%s%B_BXtWj#{Md0)kD2lcK|ePnK6Fye%a'
    'O-ngVHul?6ijrUd`Zq1sF0(+GDB{dF2}!ypa_8aO8@a7cd*Dd_z);#RzGvf0e;H><OEmK{LckGA)Q%ouAL9WM4cUS`J^C<zo@#>9'
    '>G7$=7{9|2Ag;X6kv+jcsG6AGz$;O&00GK-G2}mSEOkdI|A9%GFx@to@?E=(<RmBTOx7fRg&M*XH>d)`rWFXcSV>6!m!wQn%N-'
    'NM7RsOcrkfPbsIANK0J1B;A2(2~IqZyMHt|;>A%crLA0k1N`v=C8?a{ha#tI#p(_3${@~}ZFd!kPOnl7VoBhRoIRs5%7U$FjWAU%'
    'A=j9eO$q%c&^E)Tha(PJUenClG8Mx?1%RDN(oXy#-'
    'n%6YD!Oh5b#1{B9fiZkRA)tt56bWbXJJnDEe8AhJj9<kg~@59{GqIJyhsko+ZFR-'
    '^M>BN#wNB`1+hB{oX~?SmM#K>u+=eV3ParUo}I!&wIDS~NMa(Zb*G0k8egY)Ab;Rss~3E0xu(wNX0!thxf!WuH<BJ&jrQptn)t;^'
    'CJQFD7*J2FPs>8LYS-%u^mJ|p)N-g%y9la4W~mlHwn%3_$r-'
    'e`+a$kwb~~?^uz$qpL_H0a*cr3?8E91|l))?%{jyGt1XE+?`LgG;3Qfl=_6KDG><4m>OO=)kZYmcJgpB%P<sk`kMk}XQ6`Bp@Ub%'
    '&a8S>}#ky^Z36drf*{oH~?ufDN9lhxN{&|!%t*+cCxltGlR7RgayLJIZuR0vOIxJeI+8;X1fBi*<Hs2#cx<<-'
    '!Fe^S4LBBVx9j!`6E2xe(N776Ec)M5mRoNYe8Df(DZR$L5FIRoYf87PkCgxq(%>LbRz+UI?<;PO>@haLyZ_I^;?W@}HO>EGLD78^'
    '6O9AI8~h+e5y`lTiVu@?Z&S7$TrJrz_f#p5?y35+P{ak08Op8T;?=1hLps?I=@z0-3w_5pA!hP^z`a*-Ion8p&-'
    '%i^W!F4#>4yyABb64jP2rF>3Wn$bUcBluGlLAHg##7U9NtQg}W<e&#-'
    '(L4s42@eu$TD26ivhsRWut0@W7Dr{lYD6o`d8?=c7vG5sWUcRdrSoCjoM3iqd->$G%P@efHnjVhSW;aT$CoDdl_o-'
    'ko<-EJU3_NK@21D|z8H;$s#mxBMoo{?at}ng%DfHmw5juJtY)lt!(kMTNDeOJp&CBYe_Se6^#VJ8EhqXU99?q--W~B}gL*||8<FR'
    'JDKIOA4U*8j(Kx`7OicT8D?Jy6XGl7G8Zcb;h=$^<L~x+wo)v_=1yhTlnE+Ym><**DLid&gN4W1@Af>dZQtmHiZc)EtnGV&LF~1#'
    'YW#CFpFl;g@QcY2fCOHl`+5B>=i?6r3>(Esyo1A55YTi_^%QEzRVSoU5*cmXXh0*K`wIf9C+cvNnOMKsH3y3LxySt9um4(^V(3^V'
    'x$Oa~QKOp2MgOO(N1Xl_+;h0^WICeg$=JXF9wV;Y1&f(7r`k^K|!}=WiSPo;wr0={%Z|G3Gwy9ya6$^2CRc^_x-Cb|cO6ji_G62D'
    '+sB90f|FCp$TCbLGr_iYD=%|zkQqg%xpbJW}88C*sC<-'
    'fpxmsYPzGhVcJTVi=lJ#|FQz25F1%Jih8hfW!qr9apQeqCW1uiif1nZDck-LnGyjcl4t~BwB{~b?#$EU0>Qa{N>l%E!B73gV6dC3'
    '@2w46$rU-+H5Z&}r4m-'
    'bffq>v%w+#^v7wZ+V_<%(&|6s4f^wh%3vj;jGzW0=uC0vV!OU*;z5FrFs~{*q;pd^mo|9UIp@Bj&K;)RZ2D7TiM9P{2;2a1|qwd+'
    'emKCZ)87G;w6Px_;yzDTwF#t}tNQw7lW0=OXT2-'
    '_TO;EQmd<6HkEFrDiOzS~CNHo9#?BMojw0y7}Qtw$k#Xc5<?N0LXSdz*MuaO>}Ru`f=x#DEG{&XFWFRIH9_i$X(B(lYdrnm)EN?m'
    'l87-'
    '#2f(ZIm<+A(Ev@~Ih`wYso1mC4_0UkO7)p>QW#cRHpcF0jG+Yj>`Ea&%UP`M8DBP~!U*a^G9H1W`c*))u9n!}S^NlqS>|FXB2hg+'
    '*ezT9UTw=5eDZ?i5)%XC4g)pgxlYG+pWs6KkG+co7YLxD*F#MhY~npGe$%e|_366iQAu-'
    '~l&D6<<}w@Y;Z!lMS^^2vI&9Wzp}@d=*v#@AV8T>XLxz!j91TIZb<l3~l>$9FS4tfmYF;29c&?=;j}hja0o8G{Lh3R-'
    'O698O*o&yL=5=>1))HUtOzwb)+bIr^xb=z)UboW(3!Dj=*ZKf<pci?hsE!RRJwclTiVPa=Hsh6$!WwPT69Z=_;;!`1lDOTdc~nyo'
    'f%+6G7)u+F6$?gos>oh3ZTiuhh7QzLnj^4VM;QP5uBQgL#a{@QrXHXvw1$a-'
    '+aU~avD(gZ>)Ah|E}W_TmUFi@it`pxLL2N$$!+&b`I0smNJ)R&zLFRzugnOToD0UtFn)??OvZ`P*8u)O>+6vxVZTO6%1yeqw3RU&'
    'yLzI3Gsto&p#ohXeepWM`8BAMx-Uz$I&4+=J~~sWSfVB{I9VCU$C{&Y{fVBsy^1`AxEPD=6<5LG=`SY&#~MCTAbEh4kAkv<ab{Sb'
    'OhYQP(Y9q=vGBkk<TAManQ}_A3tVa8@?fl7{aSbhZf>dxjeZjKQ62sPGqU<(xV$ZqwX{^KTOb9nNLF^s;KGFt0ip0(kT<pO>9liS'
    'u^Z^Vv&poUp(xSjciPOqzN|35y>8T^)`${gSPRAn@BhkcK21F}<VdD=Csmk(?gQ2Vh_U<1kk-'
    '2;MC=*^Y5LV`t2yJfgda9lxDivt3~am)OKd`by15(blE^T53ujwE%ie=RxJ$g4(0({uo*z+(o6=`R8IS>2(_+26X&c%Ll<=LyF0m'
    'QN{1ZRz-'
    '{1U90F{^VvzbJMqp%by7&FaEM<YMx>n0e=t<i+&bkyMmfvA*I73Gm7s9F~752i)GUcr}f?#f~_Dyx+>bqYL^5SWmYC0(LJidfL^e'
    'puFmb>GJ;qOq_8PRmn%q?sgM8GJL)(~3ktl#Q3aQ#EXq9j&Ntv=<B)#wdz;{F;@H{K{e)UcB7ymTbMZ@BXaUvB{9UHr8akg<RBtX'
    '_mwxe}Av?+N@n8UXQe1OH8mX`<*zkew*1bYZOb4I1%u<UG(ZW)W?O(y=YdAb??r-G7x({<8kgekVL|-'
    'QCl;z7=`I*{N&@Zw~HM2IN}6pnJB5F=lil!5LUxy+2v$Js<qP~x+1);mEAf_N!sq$IuCfzvP2CA2nNCI81_GN{$@ynjM^*8fY6Og'
    '3)7r-ffgU-^vUv#Fn)#9sVaa-tE$UEaR%EBo~g_XMd{m2V(Q5t6H+84=q6d6Rh44$5UFq6STQo`Anb#y>i15A0%DU6YnAAMQ~EeF'
    '^|CZoMm{<G-{YAnG#B^vHXtDQRPoT`U~K6Rp{X%HdM6Af`)atX6c)Ixz1=4C<o$Y!l@?q2OcR=ST4Kp2EFMSmqApBQOCl;{N-'
    'Saq6EVkUexj9F$?giZIwBaN2Foo@9#Hc-'
    '24B;^wJu4EHKp?cgg;yS7GLoQY#lR7;4HfyeW=75;)gtwR_+Kry9B(5lF<^e`7le{SLl1O+C;qm@NrmcdLK8kyx&y~uXp~ji6K#b'
    ';OYC-2JW>^vlH6pa=G#ZL>6_+Ac|j@d2O3^p4OE_9jGu7XoV>^=9u<=JL|=)duGA2L08uDg&=tlvoY|-VNSOT-fVFpL3Im0kh<lV'
    '+`?!Ra^-F$1pNF=iA-4<%V|i7>5Z<w*mTrtXzF!c(W1d+EU)}d-'
    'CWA)1gt35u~6+a22WUe7;<YRYQk21%&C4Qrt!xt*x0_OP2E{>xMYe-AEePBhF<Fxsyh{SDGV{0ZWX^L!3*wE8<%77es%WO5PCj<_'
    'IWT`c`qWDROoGqr0epOM6}r{6Y7<SwwiPw9cxRGaawUkH47cKF>zpC87qSWVsfMVx<j)Jat#gwYzg7@QI5Wbxa#vQ)NS{U_Nl>u8'
    'DFnR2fpZ{CLCF#*Vvd!F`r%{G|c!{BrRVoeBi+zr3=Pt69m|K^v>0_*$2U$MxTu3EMVYy>>ELiGsjkcgMu)$#%uVpU_4O}li^N<d'
    'j}7m(_}C23jU&(>ZA3Nd!upPye{5ghzMK8iLVt=JUA4Q*v?i!yTLHVUASf^$GmcoY;<#(_1YN|E0}esYI~%GFE#g~-e|s~s9Rt-'
    '>=eV{ekWWhrMgoP<mwri4o(iMsF7;`6tQ>IWdbvx_UOK>5IF6Gln4{2+gG(k(vD#Cgo&vFaSB=;ur<0t#=fd%11Lj^wwp3Ec@Gy<'
    'WyH)0Rb~Y^4*yBrQBE$vTrDhpjV>9HaOVeXF?y{obB_r8^$$PZP^^Q*XwelLNObekVJDtZi-'
    '#=up2M1U6`)!fmR`c}qTlJYEvuaUdV1=*2REsd+I9H(w;?r7YD=UH$iN~NjbY=aL+wQ3r*wG1!ko>n<ID(o3hsU5Z70@oL5Y!xly'
    'SxkiV%F(25^s9#aEeCC}curyq|%EDrq)+t$JF_5$IWb=kxnn_QNi(QN`@Q0u-iJx^3V*-'
    'tA?VRGNdyH_K8vxmI1xSX1qrB}{tmKmvgvHbFugaaE7;R%Ak>bzhOmLZBTtNhe*}91aeC&}AExAr}(f5E>S#&{GQ57!4oV(8n174'
    'GD4RLWr#@FLl~v>vqpUd_S%AI0^HvfM`pG8R@j^?A2FX<%5DFR%3C7rO1``O3$U&>%=V-Agt#aansTf^Qy-'
    '!Fs4es_KCrz>Xk}bsNP78%3ox(3-_l)ARH$NiatMEwq{j3=WH_tx!%I1WI>O-5l_uUkrlslgmy}ZOxYBBo>4l+Dxd-'
    'P)9Q@sak^cGN0ZBcYk7k_amOk-dTf3-'
    'WoUJr@w~Z*%WMr)yw`VKf`1mq@(WE#eiA$==|jGDUP@s{`+_0`s{vung2_Qx!$T<$1i%AI>7v<*+FoQdf5yDw=d$4oEmF!yYabNV'
    '=$177uJih-G^|@M#{e6XL)9)yQTx3j0@@PSC6y6a#+haTEN%~!Dk?Nij&p89m(^M-'
    'S6fo@pup}bOUabP9E_Py`>+JMM?*crVq&zrQA*IF()f7u3~f+&_mfnOV&|z*IA`f<3y2mB#%Q*@d~CI0(?c@7%VJWzCO{#Qu}|JQ'
    'x!TUr0WB!KK}DxUjZcdEG-JWrM&A<A_aw(<YG=9lnxvR_5|M7b5?IUjGkuQO*T~;H(Srwio@k(?Y=yVJD_|O&kAR#PlE_wx7*+bv'
    'UDI{)Hi%oa1i!B&*cZ|?fda<WBcV<yH^;>MM8ix@Nh;_RAU#ShR3PMC%C#FhZ?(SGhe5IoA9uLN&dzyURPooXO@4$kuJyfG($o}~'
    '1fC~GPte&1TXlgJ(y&%D7INN?XsdGDBJI2%l2idTD^0CRN<cxk$AS`IoM}O~7sFeCzcEBG(27zNkmK1hX4m2Niu4-'
    'J%AOoaFdrvkOfu9R&R;1^|AxgqwZWq0v6XtdydjWNc4b6h&iSP>WC<_=XpqG;uvs*-'
    'GcbixJ6wJrFubeXfp&ITU;a^Wm#DBvfR$7_llDL^mdk8#H(C!s$$tN^NGn)O_dI1sPKk$;eMWam$x5+kiB_;wA;+XoWRjFbUXz)9'
    'StO?u$M(1t!Y=}k9bAwNp@3F1T2n!`PU|~muE;)HbX^>@3p!19gVoayEs`=()t@Vs*EN%);mzvqoZB5%tcS;8JpKz%Qs2--'
    ')3MO^gq3p(wME%=X^Z-k_mnBkx*?N?FMSKr8AVAba;);?vI;AH-'
    'HSffNgw!0`YG#q)d&kYBa)H@qHS{VqK910%a^4*yhgJ)(TO6AJz-cTNz0qXs+mZY&KBuhQ=CaV`(Zj&SF5{1)apmc@f8H{*0O0Dp'
    '}KP8*5wGA_c;AFXspM2HLGF{N^5Zb(}08?{pFo%Ctc|p9DCM8i<02^aZJds-'
    'xXkDltbZ4tQ<<Pn{0?GEz}ssn%2znBmGEjoxZEh{;a(bIsR?2zwF2WE5OL^Ie-xsoRW*>))14Q=bYA6G-S<45*g^h0FD-'
    'r5jQ<)3k52EnHIh0PS!D-'
    'riIo^SqLS?_~H5X<IRVPVO9$fXjmKhT5niULNz1$j?Vo0t|Agh1=d_x1$1XHq4?^%z$;KHLhxV+z0qOO#S4JNL0xj3jQ41(1nona'
    'ljaiGD!L=CiobML!Lia28?;Ns75jiGp0&eJMV1#)kf?Y+Hvap*ylF1R5Z@4UEW{wpfTW|AEer8ody3wfO=d)=nx6M@>mFAHu#z6I'
    'oVX=>Wj66sk`m&aEixj9_rQX0<|FeVB;8Z&^8}0v+-JOlttA#}og&{;lvfe*4AkF;kxd1nAIHkw4=$Q1vu4h%_gF-'
    '~E8Tb!%|{~#FHPHs=uuzx1^duXhXEdb(A^2eC+i9!heZ?-9H*L`ejz+Y;|Uu-W0l&3HTBBYf)vxXcqxuOEqDLC`#*6bX1V'
)
)).decode("utf-8"))

from v49.residual_controller import ResidualConfig as _V51ResidualConfig
from v50.hybrid import build_route_value_hybrid as _v51_build_policy
from v50.hybrid import safe_action as _v51_safe_action

_V51_RESIDUAL_CONFIG = _V51ResidualConfig(**{'front_existing_sells': True, 'front_on_near': True, 'front_money_deficit': 4500.0, 'front_supply_threshold': 3.0, 'preempt_enabled': True, 'preempt_horizon': 2, 'preempt_maximum_batch': 8, 'near_scheduled_supply_weight': 1.0, 'adaptive_near_schedule_weight': False, 'preempt_money_deficit': 4000.0, 'near_distance': 8.0, 'near_streak_required': 12})
_V51_POLICY = None


def agent(obs, configuration=None):
    try:
        return _V51_POLICY(obs, configuration)
    except Exception:
        return _v51_safe_action(obs)


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)


# v54 train-only route residual override: r025-1-evidence-h2q8
_V54_ROUTE = json.loads(zlib.decompress(base64.b85decode(
(
    'c-qxn!ERhha{L#bc~Cc-Ey*{I)Vm`rXDCpT8|wiv7+}{hV5|>g-wgk|r6Jk<`ekH9WY%lW>`4UGd|j_9t12@xGV-'
    'VYz4-TEe*MSaf4%sZpDsS$eEM|paCz|`zx>zV{`>1MzW(@+Uw-}1zyHs-pa1W2`q3Zn?mvH@efFn|@4o!?=a2Vy@4vkJd~tcP|9*'
    'G#_227<%g6uuwA;Nu{`&Ro*FWrT?|!_vT&=(T{`(L2y9@V+Zx6Zo@xu={w_hLg?rwi^xemYn^!;x4@!NmQUTDAj^m+O|UuWaPyT5'
    '$-`23{Rw<kS)==l1RU(G*GCNF;1@p*^GJPmYp`gO;jzWegw_WjRam+bSGZ?8|j?&IyvkDm_{d-'
    'A=rhfKf!X?14b4~O^l3*PPUoBwq2X?J@&dmOZmRalXm&%68ClAL}KUJ>{P?{4Ok6h|gk>G2_#aN1^bJQ>;J54}kVW=hubXo*j=G+'
    'm<S$&9Ak8`x%TEZ6a?4l{QcWSqj0;e^GTA7yBT{`Bp<Io-ox=4O9)w(;dFbTZV(Pc3ClaTMf)n=RrCuGD06KmFh1)8>npEmUFh!A'
    '3?46PLlCTJ*s1Q|ZyQ8H=BuedY{P7k(O@y4}sE`TGC%XRUcV&duSm`Ls=bQ~$>5Y;|7h@i%a?4*xgu+~W_)j4bv1`7|sx?&Jsd*q'
    'KvtmAbytQJp>c>1c-'
    'wxSKDVJ{+D7>BSy*cYC{g_xa~P?e0H+xc%^N!6TbJYWnn&hx*&SJNcGxR|xtZ;Ch|DAH0@k4^Hl;s|OY31h<ZVzg}wOt6J+czj4F'
    'e9t{Ec%J$fmA<R7#u#Za-'
    '5i_jLM3XZ`507jrFg$sf*qf?xP(2;>=xL2x;M3ig`34v|MZrE__n!{8_d4C)+Xvt3N?)J3w&z@DVv@^R%|gq(T6meAIAY`#{>V?8'
    'T^bt-'
    '!<~X{*A|x6a8U@{(eO|z;gG${yr;{HwP4*SnkE4}wQt~yfJ>+{adBBeoK*?j$jTn>9tJ<P7q&H8%jfXT+VVLjKMiaXG(5dHjoEyD'
    '`u8{Y|Ek8zT!mw>9>QM@Iam{W7~!a)KEDQvZkIfZS|&@b>BCwb=Gs{_be3JIlipcFc&1(9Bu%`^=b4wq9C_~$o!M>kd0>D~#$_xB'
    'd-'
    'D`1`Q1E_91WS@rKOafJg_tGWANaP53w$Uk&wLhO~q4(xCh{?Yvyi&*`w}AaGwy0UOMmju&1{PbP=OtT@L<^7Y)RHW1gdNJ0$mGJj'
    'tEAf`MV_a9Jv%Jf*-'
    'wz|@h69d@_ieCkuZ;TAAIM88eZ84F)K`sjS_mT^Yn7ctLz$QiNM?zmzo*lE4}N_`Wu^)7&7ImHvRw7mu9Bu$<d={9FTRNvp<eN5o'
    '{MIg7vW6ez4!7Utf)vjMOakVTew46so5t`kA)1Nz7^$kfT*z~X(9x1)`&XO;jpO$5}zyfjv0@w0BXf*G*RAl;rgHb|F{M<uuFW{e'
    '!dL74!InapG^#-J&%h4q|SXsC-n}-'
    'tc)Zmi4JScm?rW6(AG1PIH%8p7sug*J@^#YED;b&X89(ms4i`9A!0`r0A4a`6JqJyI}miD_|IPJF?A{H(PdDZ=>Hk#!zTFTB^%py'
    '`8t>GRYI3X#hW#!e^)!jG0VG_c=dLcjn$2a5H*TkjaaM#&Z#3vm#79i#)(85pd_)nkjZ}#8q?(hE!EFd0S+-'
    'd2uE93WIkPrZd%Mc|F3-)}cPo{<Zx`75<rnB#)qL1A09H4Dt1<A@DZ$h+PI$uPy-'
    '|QWRW)8qcAem{MSFr*EvGTCROuw^pGCr?AM5GeiZM=}&<}G80+nfQ61#<=wQHr1qFE%<&Hpv$mx9{m=Mx3i<=<Flj+uUG_$d?a_A'
    '#BLw_{KuQDP^lga)u*3ZgeunD>23q7Btuspb{&5rTh%}O8CyPCM|v`aAf>%wVf33@JZ=h^=}M+V}Ez|)nHby<ngh}-'
    'aUGwfbKvM$-@weB>e-w_v@wdUX}eG|C-_*%*{L81o4N1NoJqv)FN<_D`CdO(SVmY81#}up0A8R>A-'
    '=Aw&n2(j+vq3`>5SPUa#$XM&}^TCW;Bs3|n|7jfLhFG0=)**-ZRRe2J6-S2}GTlU6(mohP_pg*85&2$f^WTA&!FA1pQTZ{vo{-'
    'ytuHMh_nh=ioLqazoPjCI#}egwsYa*Buls+BKtHX}gZ!iGrR;dzr`Rl2BQo%uE;f$~=eTdqf`#EF`N_FY&KIbQe(scCzkcf=r(BH'
    'mDc4O;zMY$G?rWb?;a(xxo6tSOo~tq18`zM*;$3kJ7)oQQ{GkiELORgAy7`35(Q>a2}<CbJlZZ$>s?A+lq@u-'
    '1#;0=Es9;a@ZqxiwEA&MQ}8QRt4#x={NhoOrZedPe$m@$EgDz8u-'
    'r<b`SW5!|8wczrzn{LScy{#qnG4O>p?&@dp)kEQbwDolNXIW`Br(ZAAGd#55jct0;~Iew1zLyZ?0(W;TCdKqtH%{8s~mPYJArOb$'
    '~bi=#iV4`mpWbBvcDqr|W=Zi;{+07zi(a{P_($w~F3Afgy2cQtD+Hqulf+l(hxI<XQ3JAtYXes_x!H@t@4{1K9&U+L%XS>WsfWrx'
    '|8&C7iR1G6<F=(<)ev{_czifc3Fi+nU-12DLvx9^BhQ!9-blV{|`K`chlK9Th9$lO`;u#hGeGk{2~>u9>v-'
    't@RrQZMbS%35F`5qcSx<PajU?Ksd%VP2zHX)~Vss1BB;J876jD!NPH$n#b3!-'
    'w0yd=tTeF%YH9VVC6ep^C@<G@Xy1U#$u5uA*;O(U-}j5Z&HO2v{*+#nQGIkQ@VfgqaHOT4s@HUaEl^0DA#nF+LD?+U#V-+%fV-'
    'U9N5R(|3OHc7OsNS6{+{+=us*FIR&c!Dz>aH-aY{E&q-M%{}{VL>#o*rxdO&Zry?hN0CD_++3s#3_v98;uF!-'
    'uAE1_Du7cbfysQ|?JB87%DQtmR<z}K5dmi|18r>|yKk#`kutt(nE+9Z|L$s5dJHGz7Kqethak#4ah@5VtgJ%(1ddCagcf%MT7E~p'
    '*;Cmdk}B*@gg0SzLkyOwq$x@^tq7lm+oT%3T^WIkH@7OELir9u)n=PoVxJV%aXx#wXl+~%M2liyI*`N5NL-sgG)qxYpbrid6#APU'
    'P*p-C%YY3+8jR6-'
    'EDS=gWU*#wnPJy$Vu=??KFx0WLa2I5ao&{ZoRV}c3BT^3XS|7xPeWu06&hQ!g#lN|m~t1YGqmpq6q3(Z)y_xtXBq@u1oU9jYeEa-'
    '8lIY$aHMJq3(w1)sQ1)>5ef-ZmL&Bo-KbztKIr<vH-'
    'F?w`tA|9&N0QyS2CzrIRs@WP>lUgl2$sK$umK^%Dm?eswe8Z#IcUHB8O2~j#{&>#lE!aw-'
    'E5a?An1XJM&7AKM;+^lCVtAE5$4unlhOQ1L+(Q(NO<iOEeB_Lo!cDJkBeE<)-RH579qm-|Xn>U2-'
    'KwnT@NBC@tyD<XIM)$g4?sR?)#<cMFnBKjes#e6i32<Y^)&qjsj&`Jp9HJyQSN`{AEuFpH51`ryQ-KuCuuMM3Vl7N1W?`DS4yZOT'
    'os{?3F`^4RQp;Yxt(N_LkoX^%3;21`jH+})f1snwL(L87=^HgKu9_d0c*m>i(IJ88vB?l9p$!@o64jXP6Kl8#zj2*?gfu23cLB7*'
    '}|_k-nu|8pwnE7FPA6-F!=55V??kNQk@dhATT1t0?^J3W6sV`Lqk$47qrNopbSK?9tRKasr_A#oY!H5witazq0=pNrs-'
    '@v7@hyQCIGl3-M%B7XWY3dPO0V0-O`>PMnp3uA?|<}2WSNpUWL(9L6COs^7QxN(=vx|F`Vn@19{oLbP-jz<VRVBEzl6gni-hO|o#'
    'j_T>U&Ocv<qG&&oXn^syal09Z|C&AAy0wy}xb)KTo(<p3o8p4Y&dV;(9#xhi^F*avyNd}nv9Bqg8++mi$3Z0I=*P3xF|)K`x1>^^'
    'LN(h8l>^vC+&Ro-rb|S&g>TMm3r7QIKSV1WF=`mK$V!e9QdBVC!JeoC!|lO2zEe@|E_UM7pm|yGa)V@G*UM-Wa3m-'
    'PDK<9ZvswV|Ix4C)+M{tw4x)Gp0%c@V46BnFnNKCQ3%qogGGJ0i<@f2T8srTZ%9=J7C#Rxsc2&_g^L5#j7r@JN75^R5WeSD725*2'
    '?=~6~AFPLPTY#Gvky>-'
    '+q0|4V#V&=Rr@s+j}vm4oHg+<u!id7fIe0brFZD}ltM{#Aaouw_%YBwWKIMRtYHAK2Amsph{ViDtB=onsoz#w5PD=`?uRj{jgE!M'
    'eegchSBxr%cWszzRCM6&}6M7&_fP*;bl2w3WAy>4A&9tFr>#En%qyRoivL0}XFvfjkAbcioYlBztQWi9E3`n)FhL_;*ECEEHjVMR'
    'K*PV4s+@M@?o29FGYmy~)$s$-}cJ;yjR#X(OERI60Dh^{}is6<Z?*X_!qS_w~!Ye3{(3Ux!5i}#=R=%CA?PcJH1vaGnJ(-Gpb-qF'
    'j2AXXMdguuYCjRWlo7HXP$M1_dbvd#|P4EZS>hdB)jTO=LWM>#U7FIpf|D5!#MLqN(8#ZvD-{8><-'
    'Dx+lWoT4=XCy)6J^ZTdf#YGWQmTePEE3oA4z9-'
    '7i?CY%3>p;XGjmwr=8OIph{q0OED$OLd(VBv$Z+ljWK@w#otUxj*A)Yv!!KvgFi*<aULh;!jvBI}a{e!rBa>KJg%eN+$0z9nz0F0'
    '?#v{6K7V>tkT;Sg)&w)cEpjEY0XQL1{p0nt9gU`rFq$Q-'
    'mfB3HmzBB?B4Vm3(73Lvq9CDbR4E#Y(yNMm_VHTyIcUcIWwW|FORs9YgBAicT|pC#9e!nL}}ptR_yR>m;j;@ssi^C)Q1$aRk0nDG'
    'wlnXP&bRtsrrH8LB64KWv(TosrR=nN(bT#PjD%fb6eT96k3rLQbUULIaQzl!Ek0>(?u?CN2GCdG_5fjllV!`SO39(!tnwYIVyy`C'
    'Sa4gtA=q9Ui>GhvA=zqCT9*Pf*mzeK%rCw3=H7Y3O1n$DmHQ@borT}7a9R}n4ZSPd(~7_vz^I~8HjotD?^N*C@dfhWAb({>Px0kO'
    '8gA=Pgo9W)20mYFEd_qVOIn+H`!nl|WgtQAy2{f32HweBTlD$mcBXDL68P|kOz)4g(3eHLlpr4YxRY=|)@pOnm%`i=yDB;#T#J6*'
    '97uw?om*y)xUdWX}>CFFw<4gRAXF`G4T9qHsTht%^7$>{V9r;7_EEHya$<y9x%a-'
    'jOEP;3wz2!x=R<cmo&4T4`^r5SIQvm=BzddYU=3t7&Ns(90UJIFESwI1t!Qbl<NDCmm2HOd7n!ib?vK@{Qd%#<U_5F1Gnk-'
    '1})D*nZQo);6xmX{TM5a9fuX6Uy#xsF|JU>qvNJj=vyA4=AWoe)x9OGu5OAI4+?B+p^n&pZ>i#jFLWTX)Tl5%1aESxm^bX~na8*f'
    '%yPbQq(qaY3GnZOX@iHB}x=jym+k=|!<zKXVmpGq0RkwHzVSagE<Kk%pPBy*zyjH7SE00bOAZo#mj{5<KKo+5{@@P&jy)CGA?J*u'
    'e1GFwWR+l#|_(hAEO;!Ngz}gSUYBGC0N~t5fke-C{l_xv^|S(pZ>epeXU-*%9)g>gaME(&`jaW6IJ7xv-'
    'S`MpMUD?9_l$VtKM37tx8Vs{eMv^?6jaeet;6FROwP__eP=NSektIrK#m<&|E~PB)H?NFA6Znf_kiJ1ow4D@GXQu<mI<PRH3O?*W'
    '%2m1d{1a+;Jcvsl+wk)3gmO84#bDIk1c>XPoQMeo;!L?(qw%VLuqb=6XT1=gX~uW~vG%irh;VHwlOL%Iy@nfZ}z!>c5NyPTd>_1r'
    'H@I@LBz=DzZL5UoSdDTHFr4u+d>a=I!CFnVKjOb8sAAfS>vgy_Pw`pqMlklXrcwbt~r=H+2EJ+36ZYSwKO0N}}_<Ow~~&?;!REq*'
    'PKOg?Bcuxpj8DC>x(>=wHFwBYd~b9yoc`=$x{l!8LKeYdJ{Bq&wF>R2^Fv~O?for<EVt&kq5RCfRZb-AT4jffxtL@**jcVhxf=id'
    'ORdX&{HtfVJn$e@!QA%WimKVhQ9@dl6o0I@`@g_i|IaskyjWiJ2eFh`jEUY%N4yr(S0b@moJTNCtpnZg8%Y4Ohv+0X_b@VXb>BvN'
    '!><CU8)Tg*`4j#Nu7C@zx&Rnh02Un--B4T;bIH!qx-=>lGN`c5Y7Lf{M2h8oaw2e)x_1W0v3JwD~bUQm|NX*}4d`E|PvgPtvo-'
    'X>(v$hoK$-};gqAcU<^g?YZ9Egl7gpo#1i@FFq&N#cgU=8|S4&i<f=)0I<n-'
    'BQl7=_<|=NjSQ5)q3dQG0&(vTVn6+2XG5v>c*+{C}N6DrX$k}tevBGv|ItaDCxRWrym&b957Xf-$`o|>-'
    'pS0>5Ehf$o;>^(N*`zr1^bzu!%we9OyIZz@i3(BtIoJMN=CS0OgdCCTU@(30|YYkv!E=BFK@`jK>4+L@Uq7oPRM5g*Qb@C$$y2&w'
    '&h=W#qmwV3PyLKuKL_G9FtDFlGC+C#?Sp$L34}h!C|YquH|P=_UhvIyRpR7SWF?6|CFArmL$$Fe+PcYhlLC(h$$@B}2iX4RX=fDK'
    '(qH5}0Ms8uCh56VhxoQs~+`$eoK9IP_rIw_1vko!c(@m(eSwmc!$%k!h3Htjd4$aoc}9G`}hU1hu_cDjFe-{C7sVV~PAl-'
    '5FX?V~(!t`9ro70Lw_AC1}>=VXrHq*~`$t8uTQZWUa9nC}*N5a==roFm+uUEJQ&FmkBts(Mg`rv#2YSE4tMxoT8;qBVZiJg6+-'
    'T)*xmZ9i0tSq=5Q~^u;EDRy;0OSD=*<b#b-'
    '=Ks@3~B9pNQDvokT5aOd+G5EcGI5`$cu<4F_0JKcPmlQ<8VPn?H7Di;v6DY;2$8BB>B-'
    's+D%xd6Kavqq{7~jgBc1pAFAn?`e3RJ~djeAsEu9$;E5-'
    'k;sjob%LKOm8OY@qmE?iU+I{0)peXn#6ill}ygdX+>7ysZg7OpSg&1+?tdgTXu6s$wY%2r*yV(Gfiz-'
    '0!P9Qs9VqNJ>OUIGPfCn3pM7VsZE0;aKc<g&znw)5Hcmtr6Oy6nuW>3N^>(=cn1Z0pi&C6)v5sZOut9+{?74O1ZX9y0pFkRB(m1i'
    'j(w@JnLT$B1BY5eGc(Kqu6C`^UZ!rwxWu%c1CJxX%%qFEQfsv>7tY+=dSD$>0(~A+zP5Qe>Sv+C{^buYv&skN6;$g?b!NozdMi1T'
    '1sW-'
    'Z9m&gA8scVInr()!)BWqN|6BGW?X&dXrJ1;wlWQ<^LrKcB=A(n^P0F)GwxLSGlmdF1r3?mHVC1yaEI?*fkZwEU&sp<h%=IuAgfZd'
    '{IUcFA{<aK3Lx^BMy&djS4sKGMTW!E%kFMx)D5DuN$Vd$RbjX5E9v)xH@n+9gw<Nd#n*L6WT0d(v-'
    'UNDgi_lST<kM4J&>_)%u*b)F-'
    'vn(u(J2raL?2^rPTxGkI84r6k^H*7YBif3M`Ha!#D(EX}~(7Hx4GF>UnIkLruAsE)F5cz~Rywp218t?*PG)uQ}~Oo_L!m&VRg~#m'
    'L>}75yYE2uv1?q_kES&lk~^lM!&YQ6hyTMN4zWDqx~BmE2rnKw?0gYXRn*?1GY>zhF+qaiJiP=K7l^-'
    '|1QC*+wU~?!!>!nly*xVAtE|qIz0^=WBu`W^N`6@!=TvVl-'
    '}6d!y?l*ddrvc&dGBQCe8oI>ofxIER^e_7e>qi!YiDZ8@Rvcv5XzQM)6Uqbbb6Lda;+1q~yr@`7PUHhTbBwrzHtQIXgJmp`NW$0|'
    'ZpmOR6wx;nn_$cv3rP6+}KV}gmJh^Dx3(AEGS8D2r$6)*aa?n{JLbY$V75?ikz3QxRbfd#O|6?fSJUfQK>*88+t1>k}z(O9o;<1w'
    'ujo9oYns=p%6azX`O*P)jg$}pY$Ff@TD|4ynhH4Za`HMUxTgm>}TYJf+vYfhG7vmDst5sQ-GARfM~TMH5G?VvjpQU^|CmPn31NE+'
    '$12k1(T*bO0EAfcc|`|6=ur=W<Yoj_4RMO}cT>c1u|6^sLU^||^&klc7C&ML&@fSKog9=L*BmKRL=gw&KA@(@xPe~W7?kRD!*odw'
    '4x`yj1++6^$9$+;_NTHQ#oyZ@ZS1Yo_C;fDe-ds?xE_^z&*ph2DEZq!czt+ceKwk_oIg(iLiMnR9D%3tdiU9!x4wig9UP~FXz;!|'
    'nUDyWh;OpG?17eTf8S|r3px-c`KFhnwId?690vJ4<oeGaV?Ly1MOL!)98H9WVTwmSt}k}b-#9xHP0l%U<cyjb~mF8-'
    '3dDR9elpFmRzhAT;$IzFj%O$wy+#8zw$$hsnDQ`j2dZ`|g9ZYE~F%{RRUO%}d_F=bkR)L=wetS2Bv9N}yBdV;HYV&|KOKMobgY~Q'
    'r;x&&=(<&_dpvsy-'
    '2#;H1_jhOZWN+<yDLSq!2j&o^WG;rQ3x!49NA{$Q+<yZ~4yJfcm8o1DL8$R#TBhx+r2pkXxD$`mhw2xLM1Rv$oK#*PN5Q|sajrGj'
    '|(`8oqk-'
    'o|U>Mkp7;m~%0z2YfWPDe+yCE7DB&QI(yLk>FJlsHH9Y%f~5GF}=#P#FoeL41i9#uf5PE4l6#>&)cPYw~m3Rvcy5V>IXnHBU#J>L'
    'e#388l&@_H!#q;5r&cy%XKPnDi;c=>%@>|4l{QMQt<iLF?dWY$@Hw;I%&c^SUwt{i*E*qE7HZ(Suk5H*~?`UZP^q^gw7x>e6mho?'
    '9ojl5{$S+CG&7qv3;d3j!hLt2bFohjJS<2%2my8ivEg!C-'
    '5Ct!e;et2ZMH#wmY}6bVJVNUWmoinY26l`x@Me<@m|h!2IU>YieV3IcR?X{8>Srw#!K7U@BI^?%6>uBBJ_GEJbUf_TwS?MU>34H!'
    'V9b12{l+6AlhC(?O2{xX6M(bS2j(+grqD-'
    'S)WvZ;h{M|JKf{^K^eepS=vtCwRTN7dIrYiQx<CE!w!IC3^x&sWp_hP((bJW4X<JRoh<IqYe0)YNT6a3H~YY?SIU$=#NS7?cVkA~'
    'S8~yL#0Rh#AE&bW%Kgbi({(WS>Wk38P?mqvNjWS@gO{q@}{Lq(qgF(wgOOjCUdQ?)?H(re#&kkBf<=ax0~NPmIfv28eYf7o#tas>'
    'xFv9vfe>878CRAWqE_q&<))Ja288O2)@0(J%$XgXlp5P}LDNW8hCo$+}ad$LN5%rq-'
    '5;%HmQ>JDTfT4$;#JT%!d$V8@nTk@F%5Z$h=4OImtscI8xkq4BQ-PQoBxR=LZ}@O0~2*IvXH%w|(+E9qkD_$JTeXGEl|ZfHz}#)b'
    'z8x@N3Vy@lr))pf?&e{)U`4pYx9w*#psoWlcZx?sVUgL<@~o$SQ`Dr~6GIeI#dm`q*&1tly~ZZhd3%E2Lb#D3JWt^&g%m*O`A=qm'
    'VDuB}L=qGhoF5mVv+^SSLy`4o|-'
    '1&A#c<zc#wW|t9nw$tB~vMH=(mF0(~slANNykuY4^K2TLrnP#3sLm&7_eeagP+3X0z2q%G__9HP5zVuL*`vfp>aYRxH*HA50CAVF'
    'b}eL=h>C>LCNVa**bJhVqQ4m|FaewpT@=;|R%t62x3XmKad?V*d#$euqu36HqpB>M@+mxmeL#Xwk&><6J?<6JVKd_iumLH_7Gt{L'
    '@<8^~*npBp1+l8<E1>lV-7hLAn92k<Ge@CC8B?zn^kE@03~qR7H1_rd$V-'
    'e)TtWnu^RM4}TQ}teXl!8?Su)Ncq#TGgg;ns0o{)Qz!!L7A8r~2D_^^qFPv0T&7eM@BFp<@RT>h{ef@ji&dPDPQSHWQ*K;QKlC_^'
    '-1nJM$woxH368&s=a7GV;Ky)h&eh#AW|lL9qPnyRTpaMxwR77-'
    ';OQii(@=Qf%Rvh<r*t`LX+I0yCNC*~r=6OEJJjGI%2*rLsGNRMGH_H2$COhesmSR2)@@d_0+Tp;J<OWiDi++hi5uRE2{<z&$S@=_'
    'zdfp*Ry3t&3Cr|^kIv!n8!>^0-g>2%6v-@pzf71{8}Zh5^_%D7`abr~M(NZ5@xl%mQgxlXdxx2(b5(_BOqw8w2%peQg<16)q-'
    'hQ6$~$hHNCxk|RJU#?eEZh0xd55t%oYju^(U73$M=pwXl2nUZ9p|VY%6SkJ!I}7Z3;9Js-fqTh_<cX3kFI;h@0#&MjJ<Av{`q`U`'
    '@5r%g5ci}xl{!(o2@;S3Q{fk~BfzLu?V%fKhc3~TlD9igdx3Yln3FLJY_i78CAev(NG)T&^|=^GUf=cl^cU5JAO>_MVp2T5O+leT'
    '{n@SnO`M`~R2+IWR*JSav>iZnz|((b8+H%M0D}f(X41`^2Ko_8(45At!P%j%4r1<*`Z6QUsZx8u;m`@@uOGd?tFW<rMiOm9WHmoF'
    'OZv-M=FrrY_co^Ne_M^A8?rs$-A^l}^OYbLrLBmShGV0Ogu|}UW3%{Fp6sp}yA5p?q$X)@p9tfW+-'
    'S60oPemYlhmF8gb}WnG64dw>r{o24!dLr3ABp{wG;U5@I_|x>1xcZwtYvy9M+=vTcb==0vjPe1Q^Rq@Ev4iyA(IBv9qZXog^cgy#'
    'U&DC6U;}8KoEo)>bo`cCAd*Ih1@YXjPAVO6h3GjJ>Vwb_$(PVk;;}_V3j~LGsa?bl6scgG|*K6{V?Ojo@qV+x1Dn$%tq=5U~NSCt'
    'nT9@Bk)-'
    '{9WlHfZGkSRiHq{=|x&oOJK$hPD4Tf>hyyc?$Sz|YZLrvpUG7ZG{N;?HxDK%)Te>%|1yF^T$+V7(&DI3fCRWob)j|qH7ke3@X)%W'
    'yq&ii$Ei}5h_!mZ!!^08z$Vo(m>C!?*Lc+jL7Ic9HQQRS!4?`*2?yVM1>fK%FFAUomeI$_M6p1-'
    '(M|5@P<Tl<x)7yj6*X9d!YCY%_iP%p7wH*Lp^3_uqYRD1P7pSWY-'
    '3aL@4Yf27Cq*%VdZq=&UzwXudC?xBuJE6#%J=`qwd8dolZ7p1E*xhcIt?H(_CGElcaRl>^*Gc?z?(}g^SPHwfIEOkC?_q&q&zjez'
    'lM;=9Wa(Q#%*sK>sy0w*1wFsPqCi6gy)WVwiEHWVHQOU;cFa$Txz9Tva3tlbtHbRp2Pr;f_{Z(u!0>H86ZxR`|;MfQn{Oe)VrBIx'
    'jU9=55b&*n{=HBB!B4rXe{eBE^i1!V~iuDZuK<?pXilF+8}|$Npsz5)&ujKm~3C?D1;O2Z31N&z=Z2^8SUjx+GS&)z?C1ToMvcz('
    ';tR`4c&JKly)EYTQ{O!5|nVh8iYSy?ousw%=!Lq`pvl^^nmgNjRY^ghLGmY-laKJeFf+R2CWGIB>-'
    '8W#MU^fxT*V9^LO6%8|9)s|vG<QXZ?qRigTuReYjk&lOY_WSetRmO!ZE>|o}d<8^4n`rN^+Ds|C|A!<cf!O0CX2EVU$Zq<qQu7lZ'
    'XT-Ox-)lm-'
    'D3;$8Rii>ihcqdQUBZj!|w204)xGkVSOfN@l%r){fYghgDD5X+uirzG`{AGom&2VLo3lJNSP6IXDmRwb)wOzbfx$9m~vu+-'
    '?DW6GcW72!0asx|e+Rq|o$p@IkDoBgbQh~zRy00BUw4NEa9K~)(&Hn*q`zkT)iZxYx-'
    '6uXXDTGP{u3P0%6`9AEC%Iq&<|?Vh1Y}s4%}Fo61zA1i93zZnzHpR{osV>-'
    '7+S0;3b|`ez^PY}__=yrNj2q#sUSLW>RLPEZa(QnRHGmS0R`f@_A;FE=R5DJ;)q0f5uGWfo2Vh7d}<k+no?mjait`~qGdYL*|@&@'
    '^5ORV&+qPj6R6{5Zoyh(w2BO%)uP<y;m4Va<sQnF69g2wrwB+A+Cvr8n)qb;U9uQ571VL4Yy<5-'
    'UL%8%erhxvG8{^N3Q?HA=&?flJiD`5=rJ~N(d>rKg;f>?o?9zPtvid%+sRQ`1{S1o1&;oiN2-'
    ';<7Km|{*(s+3ju0}Un=UDEJ}B9tNA)c5Ov3Is`UG6Po!7my9C_MDYV!NkGXbYW7E|%N+;Rge!3^`6sKyNgaX5&eci%GH8ehGRYKO'
    '@wWPyn)U-'
    'IgF?LF29QbFYy2($s3E4bC1BuY!ptX8m8SXT+ZsQ=e`DyFi;>48z=gUpIISHCAUgeZ*pzoA&k$XIAu%g&IYa8*sV#kSz)#%F`ARo'
    '>7tL3Ui3Bc;ExhFZ9Vc-L98=45CJ-'
    '&jY{LBU;Bqo}$SdhBcF&Z^S5Q}kz1L={~OU|jYrt0#nwxehC<KiA_Dy?&`cgw9TIp*cM|zkNIPpOLNYWbtitCl?wpsVJ0aK~$I2>'
    'z2bcC*a<vsl7B+dDNbfE8eJ*XH|63DC%_-'
    '+$?E$4)7wsuPzyK1+d`+JT^jFK+E!8R6^;=uFx&RE@P_5RbpMSkw3Yluj`CwjLSd28Tb|Gj$&R-l;N{>_MPmor)-'
    'lU_cAo~D`AWTaJ~%DtRxl`7l+y3<A)lnVTz44SLxV)=V_4+FLQu3jtn^wHUa~-'
    ')s&B%vxfeV6|d&`ae(cfP68Y8+nDmauCC2Uuju{<iA7Gt%Mz`(hyMrX@sP#'
)
)).decode("utf-8"))
_V54_CONFIG = _V51ResidualConfig(**{'front_existing_sells': True, 'front_on_near': True, 'front_money_deficit': 4500.0, 'front_supply_threshold': 3.0, 'preempt_enabled': True, 'preempt_horizon': 2, 'preempt_maximum_batch': 8, 'near_scheduled_supply_weight': 0.0, 'adaptive_near_schedule_weight': True, 'adaptive_confidence_alpha': 0.35, 'adaptive_confidence_negative_alpha': 0.55, 'adaptive_confidence_decay': 0.99, 'adaptive_confidence_minimum_events': 2, 'adaptive_confidence_activation_threshold': 0.3, 'preempt_money_deficit': 4000.0, 'near_distance': 8.0, 'near_streak_required': 12})
_V51_POLICY = None


# v55 train-only live candidate: e103819410-islet-full
_V55_LIVE_ROUTE = json.loads(zlib.decompress(base64.b85decode(
(
    'c-'
    'rM%(QX_`a{L!Q^FbUADamhIY0fL0b}3NO4bBT<v4GDoV4NS;elz^<mc(ICPiJIAWLA$>wx2|hqn_%jtg6h&$jD#*>*8O2`~B~K`~'
    'Bh{ez|!6>cfYNhs%q9{q5iX`9D7Y;`5Jx|LymG``dqh`T4&u=O6v~?*8MC*=K*b_~FxEe|>*{_vX{<j~AC0`yY3&KL303aQXO`54'
    '+u)<FB7De*M$#-'
    'QCX@msguFzyI;={qDm3;mbo_{rvW)SMNSQ=JnnF;&Kyy{o%*m?){fPEM928`|xr8KA&gf?dv~(djIsKt1nMFeCYW4vtKPgemWr^c'
    'JJODU-'
    '?RZ`|%s52Ooxhbvl6KPd|Km`|i!JpBM4tr!Ny?tVkHg`**K?{y43{$$%D5pAT$$+NB)#=P!7@J4}+8qDyzs`&S=#_lvcge+^zZIQ'
    'rMG;>`8O6&CgJ@t1Hi7c)N_^WzUI4T`Mr(UcFf_qcFhhj5tUX!++`!{ayo>C3@zG9_{TRvpdmRX7a7@=R+<rfu=R&NjMyc}`~U@l'
    'z{};_&{+e!w6Wv$d8nFD@*!PO}|<_}k;tmP?l{l-'
    '$(E$p?EFElgYny};9103H~AB99)OvH0o5XU;Hn;iu85JA7!q{$Ho1HE+kcnI4-'
    '@+w3>$8^>qsaXht`di)KXtm$u^$vXYNWJcC{{%o?=9e45rdu;SH61Q18x!Oi{OVf@H>hUx!`1gs!1kQYY2pw*u*|VoR3Y}_?e<aU'
    '~R}pcvj?azG-txJ3@80cRfBf}NyZeuC-'
    '@W~(rH2ClPQ4WLKT4<BlaDcbz+xdLyZmtXX}J#5RU7_0yl=0U_I7xrxb&Ysm5p{_L|fp_qWLfuX*wT{!zI3nH@uB@P$tVPM<Vjk$'
    '7}6)84O%-'
    'Z|?8jpWXn|E*&{ZXYakn!MyT0AGgtWG`R13>eh7>{yz<_<5R5rw8aUuO+6HL9G=2@Hx_CqJp<y<#N*lzQ9Zw98JdRkU3mx~60SH('
    'zzd^K)bUZAU=l}KV~mp=##4;p)TDyggrQQ>XGZsCVYtL*!D0;=EgGMEo|;WISo!k6Bb@nD(GU6Y)%{=8h~tD#D+HFx#~<R%qM=SB'
    'T*X$8-*Dm;FG63v%NXX@Gh5_2Z`DyV%|Bd6cs*=!W+q~J%XAALNyh-daf<eqzxwEb42so=%t_vYkCO#@((;M7V3^KXosVmpRqQw!'
    'tH3Az3GO&C*3F>ZkCKB^xPxrB2K}`B>hTTK^Gv*p862J+r-'
    'u)FeyJEww=WemdXVPmz~=ZujK`33qqBoI9WKj6)K(o#5}Cr%vLg=^&YW>bi&Y1{5A!Knz8iD2!q<*I8sHi|x8*uHoZ>ezzZrTj*Q'
    'WO(q2edl@3>^S=@ei8N_w2g+M_R$ME5?}4xQao1g4mBShzTskd@<qg<7TQNfY*I!RifftMgnlt#(3uS-erf4ZEqjVY6R<o`L(jkB'
    '8m!{bNAqaEwy_tG?sF#sFCa{ynqB`S9`n)&7Uw{rz9Tcg4v+ZavcrYj~~TbxPitdvk)TK|h^w^WgLkfpF-'
    ')bzCemslW}X;U+GE6rB*Be5*MS!1r9*O^5QxEPk?*aDfiPOvm3PP>RXIa{Z1uIR$5si9vYh6bYwOPi&nPLw>?4_qF%DwH9maH2_('
    'FJa1tB$rnw2Qvv<~_IT3=mpBFqUhXoz9Iqd~DehHqxVFNv8r-fFld5`eAi21<O9$vf-'
    'n%S4l}q1KvQOSYhzzjE@ufQWJyoZq@aW=#t?2n7$1>bWo$QNb6|F^I#TX*M6D#S396dNvd=B2gY!8rM(|5F319Y#k2#5f<&S8Qcj'
    'n@_hLWMl6nS288ps#-LY~aL#%%)>BpfqDyQji-)Et^UzW{?k^8RM@0Msh#5);w-'
    '!2Cy#aUEQ>M?(JE;^SqiWxK!wya>gNd&A>UZDL7!!^DMmcnTX#@b5>s6CV|oTSy`=;<o;Wk_zhM*I=10sgZD!=`r~m!#(yow52*9'
    '`;Pu9g)obx9<!8uO!gmJMY2ix|71{n)+a&@IpHc9u|Hp7{_IG!mjp^!{$D2p*o>D=?fR6FRG=wsNoSlY;zkR;--'
    'l%%#<CAF&$o$QCRYf9r_L&Zco(`0;gW_nwOGF@Sg(0W3e^T)SF}ax3Iu2ZI5%L~wUpJ0ye)h*HM6oBDRu5oW*3CfkjKwwaHz4Pna'
    'qmh;OrU3hcy^hIgC*ZdEl<uRS+klaM*NdyCZ2WNX}TUMFLj?ke3d-'
    '3^5IEU7_Abuq0&tUV*?>UjioNX6U9!ES_7jf!7Lgn{<W(58Jn^Kte}uDA_(kY+s71|4xL@>E~L<!u#0|zu~KoWfMurj#wpOy3ICV'
    '1c^0Y1yxR|Z_N7ten2?T~X-_#$t)+rT<Hiw0c^U^^8!(slB6`QQUj%*PLvL_#5kn2O>jc8&=tka-RUNIWy$zz-UWT_<>2O3KU;i&'
    '7RA?aYk{5rkpC6h||LJej4{6e1jYP!pTkuUVeen2$3INuN)#v^ncI&eLh<|NF-6k9~9@wgYip5}*wCQ{1<!nqkf0Uw<{;z?-'
    'U$>7ZrVB8!6lD~V^O4u!sl=!)8h!}cK?FWl`M{Fb>|42WSo8FdbO6~HJU=qVt=sR6iB8_VLvy3EVNw3tX<v^nzt}Y1Oc`sy-aF!F'
    '1xL11qesefebWc_$)fq5A+Rq&lhlx7Vqqu<hzPdTNP$t(M?SG4^JZR+`BWGrxz(gHK!9{~k*43IzRy_&uHp{>(D1*~5OnoJuzFI`'
    'F$ycWcY~sqtq=SUy-^_<NP`|yZ(RcXpRSCb-oE?u#pNxINGMSapSh<G<+shWwvV5`+7N(RB)@2!><axdtrPC`05A%`I~qeYfaGf<'
    'Ef2u>h2ri;=3i+7rxD!)TLND(J`i`>>?Fa`x$;Imtes+)6NSheY4ajPloOcj%tp^3VF^kaEnV`e<DMZlLIzrbQ;N4%H&ecx9IP|r'
    '#dRyLAZc>v6d8Mh9PSJgJm@4!S?;Y}B{%2md^i#}z@5v$P+I`DZ;*KjF}@j@_D_*LE^N)?l7sY}IuZQk1dbldE^^47Mq5?^dzOs`'
    '$E1fX!<|4aVr{*vodr1Y2^$u3O4EQTfiBTSg<GO5+**=nrCx$cN>B<wK{rTBPRaB*3H~`%yj(F>w2h-'
    ';0GsH7PW8E^lb)ZGRO}~JVf?O7%5A~lsYrc@?lNZf2_hAYrg$v7sq*bgb#6_f7|0)zY=~r93Rl3nG)}p`+Y+TwvX3RZwJh&24bz='
    '*mKUL+GFupM|E#Xs?%ydW!d|YbomT44v?WGCSj0}%Wl<iYDLap*N?CX#!L=rYWe9Wllim?<BsPs)NZ(IF6N?#DzMeqEb|K(GkzQO'
    '<%5q9)vt%X-SD1PB7&oFCKdx!&kQ*|k8g!D%06zfOf|vI*g%ejGqqA(ZBiM<-'
    '$A*rJicYkZvdFd|h`5GW4~wawavXu2I8|Pt64AS4i54zuhyI%8=}U|`T3(wL$i}KvN0hHXZn7GpY}(bl<OfG3$uF+DUB1U*=1_#)'
    '9cNBZ7*##aWN+XP{)f+0vE2Ki4oCGU1*^ag4N^A*A_{WKMcEt*D7+X_s-_`{_5Vx=;U*2UZdPW~-'
    '&FFhd`WwRI5t>H<=`IP^1oVLlpU~%2X?@<;tuQFg<_(6@*1U8CAs5-{~HrDk;M7VRFf>CR_6hVf0E%d)-'
    '{yz*C)#Ze{(9oE2@Pz4+Xv}7!MT~PC9HnQj{KBiQfVg0aKKoKA-WZrswgIAAgcsLVVD`6Xs83uSKX=#(9l~$A=t&z0T(%`eVH6X4'
    '|<z(btp8?)k?k__y3^=Ub#GC;|?BibF8`t(}-$hP0UCByeKmYM4IzSV{c)ZmHt!b>u{A%+Cvd$)LItVjoZr=InqW3U@j5-'
    ')+eeYvkgEz_APlEiT}x&duUkT0oCb?%1NbFIcn;__!_Df>u!8HFgE@{pr^<yHxX1g&BwV@yxU87;<owbB+s43Fa)(0uKl{7J8=Ur'
    'VBP;q&+aoDg(tA6%Dn(2nGhSG{OKKWJoXqkqnIMEFHnGRWbaDbAXchKCAwTSa8)4o7-'
    'HUk@Nwst;qT)_Dk1{juSDhjNV}us5qS~INycA?XuQwC(2r|Y4o&qluj)0KY3DtPzZ<Hx&XKXY2THkS1bn05C_*+>r%HkFH}{$aOg'
    '#j^|;tMw<yiv$lB92xzDz-tEmLR{;`P4d0*n>+&-+hD+&|6-'
    'xbRW#`46rq>{v7Ji2(ffJS?o^2i}wZc~FY*+;8p=mBMbF%0DSB0n(Jq7ejnz~Fhl@LcsNt1)F<fw398AdeF%kUiRCn|c8baKL4=i'
    's(73XFHBGns?n?2F2-@5{)2`^QMs@?!`vZaXCt|j5b-uK0y$7M)Y8nx^PSv&tRKKyJ*ssh_E6-'
    '*cgX`MI!|u(UV+6E=M5!5NN2S28rsmdgwEuQ_*VNN&^^Tce)&>id~d;zNHz`sd?$aDrLgSi~j|LlWO}USIv53@dzN48NbwOz!Ym+'
    '>cTKg*NtRC*x!cAJVD8VA8z=c<f__>+J{1|3~Y^n{B0Cyym|YNf)i62ChLzA18m@ud35iXrztpsKvjTUWRQ9T*1X-'
    '^!PkaY*Ow>YzQQ#cV=&G<Dv);JT!Ab+SUjA?bX~^+@jj~V#HopfjMOKBOTV@i#kjCh9bAdnPcgBV%|dlrELkI3KMkZoyCBRd(&Ee'
    'P^~-d!t;$SpPfzFiD&p?yKv0(<GpY1%H7#6{`!~f7ywb#j*YoUQg%)&74v$o;`b%nE$7U(SwHpt6HQI~$d?-'
    '*7z*<LMJ``mjea$L}ZzJ=pbOf83dlqlAkS$u?dLoa#f{Mm`EKdOyD86LL^1--Kz)q}9u<C7AjWxZx1uVmN(3}&EowiBJd0WV(qqC'
    'UArtDyJ<*zq|Bq7*Xpj?q9V#~wpHz!7OX+vFSnc2>5$P)0#$+9zJJ=O<JYtuSgE1S@3eSoOs$R89%6>G{H(sXmO=uX=&OPITEnSK'
    '{&BLjP>+A^)uWCJ~z8sIupcU97p+f^iFIJ%-'
    '!leU^%!6s{6s@fTfaEWkT9lViKG5wmnrmw;<O(<#4H>%r4tP7{G+Xgm%=%uX*97_X5C|@y(>oqQqc)sxy0?||!3dC2o6eIy)t{*y'
    'Gg%r3)y8R|e#+ryBbMOe%#|m}*#^bgM1Ol?<-'
    'nQs_Ey@M=iHI2aQL>fVr$Jqbkury>^CW|4kbb`W>huG+%sTDS0et+&XI8@jX!FaXUV4a7+3Aq?7Lb0?OBDDgha3ao2xW`jsU6ujm'
    'Jefb7tdRR{9R7_-'
    '}G}E$`L@}QQXFnnzKq)j56RDEUn^>n0>9K%2*jf=XzMCCrVBTI>b&=+P63vjs0J+;3_4%$Xwq(lq}G!izI1m(gk2P0g@PS`_ML2i'
    '+0tC=2x>=R&{9SH`7SePFh~Qu)&vUG@2ub91z=Rr-'
    '5lAy+?+I?le8m*Xxt4Vp`@{GeealWa5?ayJkt>`6A1svrw}zcyZGe<`7j5E;Y%ZmP`pnQVV2CyCXN>eeiTQj>1}Im<A)+{bpDkIn'
    'PZ<vu1Y;^FSvbExyU(Vmh^6?S0aOlw@eQoZpjEQrG5|UeS~xrN9;4zXoBhwxdC8Irp^Zh8YvQoOQU0AYPlDT!@vIvCC~$lK&gikz'
    'ovc<4dcNUKmaqx|D0KrIc?<eSe+)0$YK;o7H&EX)r~;m*YK+W6wbXg`9jbzH8VUouenS*Qt;m$(o;Db)<}2R{C(KPXWOKlilk~`('
    '_30K#F&kRrrSM;i9LQ1|VK_<Sed!q2HWIVm&>?YYuW^P{iVSwVpvl)fhNS1l4Rk^GkV3hEnPE@QaNG7?i=O*pk~?$U8u*00$Tdh<'
    'tuFd*?#QA;Rdm`JR>$%|B}%<yJG*N`9$k#|E(-PbOE@mop8m!eh9bjY$ZrKu)l-'
    'gJ`sFwX`J6k_UAUwqUe0=bbVwh=yycbVOo8C8&&%=hre?SpPD&3(|s-'
    '7OF#_ET%~q2hq@hqs;`&{(}Vp*uj~l#QQ7hFc`whve$Kk`Tdl&pJ|J|5KQn0c<?Hgm~cnQcnhC99j0tlVA1GlUCVM!4;cQ9q7)D&'
    '{`81d8VOkJgCdY(_O}?oS6-'
    'eSUxD|v5VKEX@U7j7wZYr3VJVvm`=VNPK=G3tXo}7(6Q>Ati#3525_SP@TsWaq3%Kda9|7l=>i<JmomIq9g}>49t*CS7bV2h9_~?'
    'e96;^(81+qKjON$~>&)$6%2oRjsNVFXE?<wUHRV3guVos0*=oq23TZGqDv2$Hh&PQov=<8C*+yLsS%3i57S2W>1|I!{5gJX^91@<'
    'cl&5VQ(UbJbt1`r0U&mk<*YPmWl!6Ncf?Ck%497$2EIMK7G$#ixg2}V2)$621fX(mW(Q4%;bdoMvWPN`Ufd?<PLq6CN|Wf=E1k?S'
    'v};6Y@)EgCPW4bZCWj8l-'
    'iB&WmGsK*2bP(~A)j76^j=HaHexqJny;Q(u9>S+g38uJ(m=I0a`9#LgSb*W@t*GCJ5v3mq8bP!gfrmT&+tgV7@R{VtA-gP?4cCdh'
    '>iJ<te1jBu|H$tJ2V~OoR#vAiF*u8J+19tAa=ro$$;%N>1D$^z}T9rQL<F^0v(EO_S4V0l~`CWwW@!xfXrWx(Y6ygP!X>WAEd54T'
    '1)|rjqSNL`<O&^h#U5C`v;NZ~2WfxHt8C;`2o@XmzI(RhFgHQ!w_5imrI>R$+6ZL~^r7%&M6Rmt6z~VTRi8c<Xhh06J>n&k+7H?T'
    'w+Z3Ypc<Qq-nNdoFS_HYJC<K@cP6gP~eN;TJ$$jBlLKRn0(GmRKd@~=wgjTc{iuq=}VDPmB!D#dXrR}Wx$Z!r)kq?-sH$XV-'
    'G*oEHWHPhoC3tNm(&k7R^AGl#RqVR;CzBoVPQw(Dup64bE??Ctv4<f;rAZbM6hDEJp85S9As2XV5?*&rLeE%?%%Jw%swyE1*f3w)'
    'k)=Ex+_>7s%Rf}@!b3(P+QHG0;FWyS;+@-'
    'vLVUe<_zL@7;Rgc3G%)~A`GWRH1fM4zlM7?>^Tq6#0a5JoDld&sg}1)f=__bBNzM99Q=JdmV@pyg@+^EGm!STI_@Ghdu{7f*K4Hs'
    'yC<A5$krt1M^HMpEL+B2rtTp#iYg5iEb6c@*=B0)f0HwMVW!HT3;b>Rop;xwQkM3E@E$7`1SxEcrp~R%&Hd2wL?6!;3Q34|;Sn?9'
    'gbw0IdZA%?82)`pmDc#P(zImTUX*QdOF);{RhJx&lp}qO2*dQ;)Vj7N>TNQjH!h76v8skx0DhV$2Aw9;)ZA6kR+efv3Sj7rua}}<'
    'dnA4Y%vr^F&M72aTe1VKN$4Uqgkd6QJN5SkkvM37H9cdECT(^?c0ft*YX%r8Ho!^V`o~z=f)<)4#$+>>`?g=89TuGTR;y@r#_Jh{'
    '>U#^USY+I6`jxvh_il|zY5&4XLp<0&nNsd<=8t!TZDKy~bbcP6y=llYy!G64q#Sq=D1O3Ei-'
    'o>w5{*XD+JQqV3Lk6aL$P~~kws5{QwMr^UnZzi>fH-'
    '>r%q}ruF63V07sYYax~}!jc%4RanrZJPqJ6~2)S*ejNsxWA3rcj|I4uwJHP90iH?wm1u#5XJ8g`-'
    'NgdS`e*`?a#6J=Y4RaYS40<_>IbbXw@W7|a|p)CXy$W00#3wF#vKT}kK#f8y;nNW_Rd{7w@9Nx0&1gNfU#2(A*@yVcx9JC8Ap+%)'
    '}mDSpR-w)MN!NV>##W>BuOBN&{+qp2#ZD?#zg9M3_LR|pTPC33+$MH+&l=*p#yC4}<)-mo;8VKY-'
    'MNzErE2N~Nf5fnntg@|GFmpnK-QfQ>m6y3Qz753EO>FIX^M63gL<n=-'
    'YB>wuedSgoF^Y$h5`Txmna7pg_P9AoBoI$0)_j8~xOQ+Dii?8-'
    'C`;Q$HzW;f+5>d;FzglqE<Vs4dQI}M6a6VnXDky<%S`i^TfaJ0^1zvZr;t1YhMVjD_cC)yFNm53K^_+>b8hic1yI9lk+X=`%;5WN'
    '0t+l)a*_%{)A_<b=YU}9hKS#W!X|qHu^9BOE&`wtnB%_FPXN7+Xf6vkJ0d$&h?^(K5xmW-oUT@h-'
    'd>%&f+MGHP)ky%gf#AVPG?cB%)|U6CM41+A~j)iq-'
    'e6h_(I6C!PgEU<I3Qp7GbwKzBl}+Udh^ZsRd553z;%tMZcRekh?b#D>%*tOOiLm93RoEts!4xD$S(gDy~0fiiFtY3#S5-YKACw2-'
    ';WDwX^adjg8S23c-'
    'jjt+Hv5ju_+wMz_5FXW%h=y$W0LHexiJ@1Fu=_VC$yjb664gouf|Jo;Z(>xjNMRd}@P&b}h)kzq#ywoB+oqTy^V2a8^acdWHt{Mb'
    '3&YYre~?`g>5k1zI7U--B?w_SO32K-'
    'j%t&yva>ztE;R$7Nqyl`x+Qwo?avtW%hx9!Q4M5~4N2y75frt&yC>Lbx|X=Qn0c^MASp@hUa8ZcjFl{8eK0td?S9pwVQV8ZMdwx>'
    'lEjFw&Ckh8<smcL|oUbJY6Y045HbvhF*2b!Bs`)rluRk>0J?cvZny!|^!A45E$&lW3f9?L{X)TRR;w9a?NTXLn<UuX(J+&Ovql|c'
    '8@mIHAp_+V{i;y$8fDRkF2bX{pe9xlmsNP=Efw~+K8g(y3fucEPlCC9aS5nl26L$TczL_}`8D(9k605uA`=;~JQEXoGqd^IC$1)g'
    'cSE4jB-'
    'm4Nj_ibxNUD2Un>lzoGsm{8gl@7z>5rG(a;xM1Ol@UQZh47c%b?`sKne~&u0)bZ>n!h(L@0oqwvpe5GfS$K&cN3hy=BJq~vC;I^z'
    'SDHHUgk(V+Y2}ayIVMV}byTR0;yQzkEbCQF$S?IZy&4)WdaAiJAr703KH=3#H6%26ZBLTp=CP-'
    '#!1=s@{lYV%sXNFR!+R^mr~F?|o}ly%5rSz0-'
    '_^@%KyWCAp_AF+qfdNEL27)|T(FxfY=WnLU8Js3EmKmZNw{InA~Hsd5ZdZ~X(kh2TBA#~*{QYEFo=;Y(y(uZiKaCligZ}$bgyB9O'
    '-T>KsS%=TH{c0R`%*?Z`0OK6nt&J(9XtSgI?7rlM3Z4;ouW3zzth#G&Ro-'
    'jdvBR>f%aA4_O$Mt*t{vyNd!Sm=vH&Af|yJk$O4lrc1k^Y-j%JvO%6ifkulRc-Od#{(3P$yGCLNjZKKPI;~PG`m(e$}rMx0L0_74'
    'qw8?YBT^M|UqL|ETorJ(PdHIAooC}#LaW*(92Gl&kf+mk*;=IBNS}_2~H6+s<VHighrQSam<rY&4Fli^r(VBq~mopwBq2cSuceP+'
    '^SdxmIpN?5yQ>KXJtdJ=unaRa1!9CveH%01F-'
    'gn4y2GdMfM)2)*?L3bm)0C#w+M(2iCIU%?`aZhpWXc}Gc@6f5=ztVV8KnSH?+BQ5J;}!UXAp}Pg!+;}8yiuWvuIxDo3j;tgWb%ce'
    'n*OfcG+-iANC&e#NU9?o{icr7|}_|RhIX!lsQHNcTe07F&4j;4YEj%5|d(<XQ8LPwKs~QBnsm-'
    '7=qRyG@htLoYB^}cD*dyH!+n`!B=&+=+f6~sE^v)6zr|&k&Em;+LkVRYSvLwFpnaeiY#?Z`w#}januv#gDpXuRS4M<Ioz-'
    '$LgC%O>TTRbI1Sk(Ln`7EmKJZZee<*y8NyL1qhe5&RZqo<GV+HCUaCr&{s=r}A>LxQIj;USSmGZ5vfMmWMOjnrDXm!RNZs4i9|zA'
    '65(V7lnGqgD1%p&zZj8L%|Ba=hJaT;;{^K0fWeSC$o^dCbF>T6PYD&aty*NuAW?#&5m#Sn_e$4Ft6y-'
    'u7&*H10)L<?w=j*jt5JHR0*GHac1P-EoE6<*#tmjjB3Q1U0E~?ka-cVb-'
    '(>9cS13NWT;KD<;y6qt6ohdX~n3C?2+10hAdKkGPqSe!>As_I}psT4EJMN=GQk`KC;Hr=}kS*+Lb~yJN3-'
    'Pj#hQQ+OLsbkN1{FD2=_*UR!Vld&K`C3T0+DUp9Nl5)<crdNSYa;%H;ov3kl-xJL>F$IQe`5gL@WUGrYpu#To5p%iGn)q)+iq<u<'
    '=MOp>WFBt~Lr22USfNKhfaMo1NL3V-p2UC2A(EJ<RHozA34NwuPQS?_Y7GHCZhQ3iIOIl^L1xE`>UyQBq3|vs?vI-OH@lD62JUbx'
    '2|jm3iSmS2nici%Zkn1aAXqvZVhqjj>}G-x3UAXPc1$RQWOBGVnxd)joU;7~XZ6@TBZc(n-'
    'Ce$uteUD|u5^$_uxv<_*^6;p+Xoe)o4ymJfu3w1=uv)nnlvolxL#S-c%j)YOcx${WB&!b(0YvUDfpXzT)I)_~c-B`Ic@*iAhr-'
    ')nr!tX=>=L@SXXQPUTV_M%pMvLoIMYYRMc&WJI<p7XuQh)W_%FQdb{E_ET!1TKo?qnQ%s%Nc%IObFowMT~-Ks}ZfQQiZv9N-'
    'zPP$JW196`H5)g677fFahN%g33$(S|SteRagq5D3y;>#FzrPnMi%xB^=<^jX*A^LUT*j=7796TS#Vh8z@S4s?uAcLzNn9iz)9&&D'
    'Xs<uYn_NnrnS(362aj$Sgt~%Qi;z^R@a;C9$#|<dHH^NY@<>Z-ii+i{lnLMc-u9yb3H5YYm@g@P~2#<;{i#Cz77qL#ic|Xu-'
    'bBOdqUS{?h#JTGO7En~uJ{gyZhL5?OFXmz-Tv#^qx_f*anc|EC>)3TpbIm}gfIVMTa@LZ^7|mqE+uRHF-pe_txo%6J#8lQ`X8SqB'
    'Tz@&K%Y({Rr^k;B&2N_!HaNfp&$2RqjJ&*)cVvo%mQW<aMt!<XwbUzjKe`JxygLt=otNsXNG%8g+PmzcF%NsoB`3P;`4H4-'
    'HhtEU^=!jpQ=2D1XzEw3VWW;ISuHEKI|5j$fT+?G*p>IS~gHRcLIr6|W~E1@09*##_!^}nLUakNZO`t7XlkaztXc1(x3gr%;a)EO'
    'pqDl9QlVmgq-Nz{DhQ*4QjbTm>-HU<3{tE7=Mj6KC3)&&{-raK%2z}-'
    '7Na>f9>P(c;8`W<n5u~_X`EAVi8vSZBSx+pKp_zA@MhmWX``Khl}B1Ry<A-'
    'eS@ZEK{_?irgDms=NytT4$S3H1`}voi=l3pM2t601M4657XsBg!TV@0x8!D|&IY^q&eZ3cX)|2b&++s(nz!he$R^p|)K11}6M(Lg'
    ';1Z9dE3x=aw~&f>}W7y%vM7){Lq&K5KWy%G)~UZtPp+2D)5ETb;0QW$=H>*Q?3&;tlL%>jkSnMp_IZ1IgO}_BcVBm{|@un9I{h#g'
    '+<2DellnJX=B_{uJ{92N%>dV2G|K$8>9p*Bkdt<uJX%y68EUPvpwoCVfgj8Id8|Fc(sg9xACtkP~iS+xN7r5;xJq7kpiGpLBDc@$'
    'eOnBQ_X?2y|ZL_Q5X`Nt9w+RU{P&H_40mHrPa&31K1)EZpQwiLZf48KOu#%3N36&nWb`9P5>0>}d5UXt;+%;Z(Ee@RiRiDT}-'
    '~55xjaZC_15DubyDtO=x;&dO6fZe8aJ1di;}m+4$3-8`eBrd;+cnz0h6U_oeQTt9qz`|i!JukXHc$9SPnFv}POB8;NdVArNm$C-'
    '<adb?>fOU~BXO{8s43Yso_GX3r^4DAV89JK75HqWh*Ge|2S8m<`LB$~G#a}4z`AWoj$u_yG-nK@#1=h4C{3j@!sl_YKb7JeqM5x!'
    'g?6y8}_S?=sCBxRUjYsBEo>`+naWx^<KZn~hrFQAF_9#ycwX$bq})cK;BQc~k<`*pDi$f;V1J~pyYieK)Q16YY+n9D?kI~exDAq9'
    'i(x(bcM*Uh4WMvTybtB_cDqUv0{I!k-'
    'cc{+v!5SUjISq<q0RhRP<X$ew{s;pZi%7r>AtFCm07Ni&{(xnxV&;Cf(1JhNuf8#g`aI~pLaJ4*wjFpy2><j^b(T=X>@xTUURcs`'
    'Z8-+v794Y-(r?`Y&Uc6bOS?SOm7e9wov4bj$ptk@^HztP;Bk_yY4T{~NdFg|-'
    'FG4Ss%S5s|<R*T@?MikF5XsoW===`G)V)Twwv+Xp!w_Ae#$5nQamuSp>UG)R+5vFylhj_QJh%+eh*8hlsIJyM2TD0fZiO^V2Y8a-'
    '!P1#pDilO<9?o531E+PCnw)zuBXp^-OO|RGmB>y`-'
    'Y&T5&kHPl&~X9$3Up&IZz3AtZ$OB#DYt#|85gc{sPlmweqBRPJsxCxTNx&<8Z*qu1~-'
    '?<6v=8XA8Ho&^g0s&0#aORPWbG(jZqGhaHE^0kO-*iuoHA~F*Tg~Hs0q5;#8_ZvkL$$OrP>3Q<*{tT|E2`WwhN5'
)
)).decode("utf-8"))
_V51_POLICY = None


# v56 sparse public-state router: Islet backbone + shop continuation at step 72.
_V56_BACKBONE_ROUTE = _V55_LIVE_ROUTE
_V56_YARN_ROUTE = json.loads(zlib.decompress(base64.b85decode(
(
    'c-rM%U2hyoa{MoPo(Ih*Nxx~OIj?ZKrJ#=+oEOC60H0yNI6tiYX86Bb(vUOVoskid+0E4+{G<Uz_EcA8Rb@s-'
    'M*jRiFaGVXzyAGizrOgVpI^Lx_3`72ht-RJ|LcGL>wkUu!IzJJ|Ld>+@wfl}`uTrX!(aXB{==sqv)}#s#SfqV^2_@V_isMG{`6w?'
    ';`HP3)t7(w53BS4d^{fCTz`Bs`SG8Q@9uwkv087w{`|+cAC52F4__bh>ZiAVdiCzhV_x5%UaU6Z#~*(@9^ZfckI4(2jvqe_-'
    '{;G0ynX%0&+ng}wEp^}$6va>{@_Q`Ums7%$K$(q*H>QaZ@+%S<-w0bUylcH{q)1<x9{Hk@?{Y}ef~Nj#)^b-'
    'ynpxVr%#tP7!7Fh^x?oRPg}`xfBAyf$Hz$$Q?zmieR}oj_+hek!>_>$2S@+<Rh+s0xWb~IAHRZ=Ihpyvn9m;;8WdUKt0_Ou-'
    'g)7^4dHQ$qvb!}8eYHY4_^<4(UipbTXZzXSK%-'
    'S%X3*vGHsK;dbZK!%QKq2^KUIQipTdy_5%hnnXRRad2(T)bsFsW$NxJ&ZMt;XLdi{ioqVu|(Za-K&<lJy3%~=zC-UgIGZue)@;lE'
    'kb>Y+8seAmT;rf4@me#yo=jQU*eA)&-QQtU!w$9_Jz0~<9aI!A{*O{#G-;x<w>iL7oT6WyY2lm+LX(Vp5baJ(g9H*uo9n|Y-'
    'TJY}^hY6hd`Ve}&kp|Dc+)?OMJO3wnUc8Ekqji05boQpty?^)a`1;c?e>i^l^!DA`f0=qH@c*fog8rg(nmzd#g9l6&;$oK{?>|r1'
    ';d0f6KZp12c4}{rj}({w({E*?oiU;vaA(nc7>jf{AFjhCzKJ)yjdoBjmRXKO<fE_G+VwJ+alyU$aQ}XM16+3LoRf6$-'
    'b)<J3!n3G8~u(3_xql@WgUh8PlN0D6w5wsasusA4}~3vV_0u*p?1<UAP!ADuKf_z^IN8&X*l1NhX5ksilYR)F#1FtAH@kKailfII'
    'LTo=#TZUaDu_)ODkXhpbZ-`hOKcV_)-'
    '0n%<CD)*v&jZ4Umkdb1Ai*|AwRzQ@MksRIH8vn0!!uN4{>JEP%k4~#8$80F!G8gp|9R$4D;)mE%Kaq>ZrNQKU_z6J?wC1CSrNhbP'
    'FFz#{j@_iuRVj`sjfSiq(kBC~v{X$pSrT`NUf=Oy^mhk1fqAcAShw;1mA@cbpjOW{_#anuAlggKW13eVTst{0-'
    'FeOuUO39G)GghYx#rsTfbUFBLR;kmk^dpKT?{G`b?=!Q|ZW>?lrOfaNA?b^xZ0Olt3BMK(5^Ipf$Cb^zj0=4G_Jxfnr{$(#G=eC~'
    '>l%+~!P=14<#W^1}L_S#)n3`H}Yw^!eTEIr=RNv!YNKXiR<uK*<=;*&>CW9<v<1$vrcls3-'
    '4t#Nk)SM2y)xwjEJrthomtG?Rc$6qGk!~Lhhj(Yt0$4?(#oqjle`0$rUZ0R{bq{$R_xKb4OFurF#l;l4g?4~3y0x;&;X_2*FA(R%'
    'GTn5Xm(e>=`zNzh+E&C#Xo`?>9yne*}V?geBBg!RY=(yt&k^^z*Hf0Qgg^v1+lrYbE0#jna&32-'
    'ZEJy0}^wy%gy7n3<sz?djorQCdNsS*CMqw6=4muA9%!4^IS$drILV(A=??0Wxmf$cn()>#TVihNAx3n`gi(<52_|joC`8XQM8}gE'
    '26Ar6&U^_3v{73ZdHR_O`L?g&mjh@KBHMtfP2}DDb1R09<N7Sk~zkIx%WG|(_qq&fCdUcy5jCXMoH1Fu~HXhja==mdG4gK!$%W89'
    'u3q8;`v@)f1NdbnTZ&5H{l)-'
    '#@pj^<Cxtf<J%GG2eOy>6b@Y?Dj@*sk*XH74{i0tXDF@72hJ>nG<C$seIIYjUrJsNvo@}l3*x#*SKvq`We=3Q)O<qi#k^j;(qZOq'
    'jl6+H2;w9WAV8N%4he1a_=%cM$Qsjp4=$_cmyXy(fd!Xj#q>Y%I<c;vLUJAFa6@9*E83vQwB;Uk6Y4QLYbGJq5hd;Fg-'
    'SJImoc~Nip`{CSdbdK|4AmEy2BqUaJ1J`Mj(qEpc2hko%j4IM|!qd?3&7oH6@umli-jX2cl``X1DtPFqbXk?i<xWeiIg_A+^G?5j'
    '*T@WgK3Gzmmhl$Ow&`Q4Wj3*VpvK~xkyKCzSN#5ouX}kxgzI-;)RPE}0Q*n{O!D~YRu!W>aXdvpk<-'
    '(pk&{MmNnq}BxmbRG0ShCWb9h8gQV4iS!FKJCAL6P>69L~-<wew_1~Q}|E5jwBr-'
    '(>9DT5e8=KP422w8c`ZAMKyBDfeKp9}scOqXTKW0zmE-av}$WxF=r0vQI?@5<UYZ4}@2yIKV^hoH}cUGsH8j%SdZwSJUkC;T7Tj&'
    'g^9%0FFh!HM%!ayr0O8lQXlaJkAR_xPMb>8B@=FS&le7Z{BnN|<T(1-$_zKTbk5&e|}-'
    'Mvr~SVBKWE(=upGO$>y)PNpcC1X?!^m3FdNavD_D?>d@{fx$pPjfOb-h;BEt?oSebK$JI0?-(&NzsZF8(ecxWAN<-'
    '<^*EX7u2iPcx)GMc7*1~X?9JPMwlZ}9j6vT^<ZJTm<6K`mZ0U<)o0FfOTedXF{w6W26Ll8ogK-ETPnE-pi5EM=anAE@S>(M)y%?a'
    'd)?<60{%XDV{19(`j&AiEssgZ=`)xFndf#YBk1kmx2=hyzX0ZlkI~mhWm&;X9?TH1wE3UlAT&n~){?prcfBY5-'
    '@{lC_dSv_frGS?SJwJ`4mbP|^xRG))&>dhk)R0omgB3E%deB-MA@B#-03!v%m7cQXj-t<a^>-'
    '&~w43aLYtT9_uZ}knrSORfQ?!u&^wCH_#S`>DQGl|99ZF;yjAiJhPLg35m-lNloRV3m8apB&$%<SZGtFcoiP$W-'
    'W}%3(T(ky+F58r!ixZp%iP#zd#?d8UfdDTK29*0koC9TO8&yNw2VY4=`rA`$8yYC&8qQ)bg7v!&0Fh=CH}RDzf$nG=#)SpbSU8>9'
    'q(8E&xg1PJ{^(T`#(jveF_FsV6QeF+PY;KQ%w|b7R%fYiV+UJgWd}6(*fBB9qGiD`4S<2Beks}Li)ONK@Mp)PvThg2jB5Sl(S`q='
    '<Z}+QtA!THMFROjct92TwUxSM5#*I<wv75jSg>j5jD?(0aEr#Y02yB_7cpZ0GqZD7qh(3DQ$9#5^K%)LJDH8@YeyJ~qOMD%o55uZ'
    'upJKbP8TwGt;<X?$yy_4>te5ro_lm_n(X{FEJX8JhL$9pJ7d1412qFP<K=7EG4}>67d68adg@G=MU3!ltSOaRH?u(ygx8j$7@C0J'
    'J^$p%4E&$m8K1VOF*OBfs0OAGd<{#)lnJATrw<SaU~#mxVwO4?m;#?%OeSkd<7ZF+Rs!kFjnAAVX%X4Q1P^|00~>ls(M+G8Dwe8h'
    'X-dez3t82bsaCU{L7a8<|EPr(^y10^FDqkB)Gxf*b;-'
    'Z`hXvH|SH(PgKk2(jocgSKu`5CTq*3df6y)tgK^KAX*{tT5PH66HEP@uI1xisl7y~WyIzkRucA?7rMW1LKq8J9=gnGcL&1F;YIHM'
    'iZJip<Slv9lVACCpyZf<g6Ur8?5$T`&QpwV(M&G1CTI5*-'
    'wsNwQ~f!~W{JE4z!WpiAH<jy$D(}AJI4=8UZIN!rjP8Nv2RblMtyU<Ws+7XTuQk$l^IQANZYqR&rRbY50Cyk2df}HAnMa4@R@_(@'
    'kJCG#sn89D7KL9tw<t05pakOSkwIlE59mNUP9S&Vif)20Es&=juCZiEh-'
    '0N)8=+Cb!jJvFLG1mQMbJRMI^!`1}+`iP=GBhrPPDl4LyYK+Bq6*xTMP)q0-'
    '^HCsba;H4q7je*%W^W|o~D7?L$g$t0u9DWNnC$DzCygmvpq6H&Iy2Nz-kBujpPTH6NZAUos@F{T}g0K&JmYl+Xn)Ckt?T`HEup~w'
    'ELt<RvN>}Ch6%CQJc7@8n#JG*TIj@Tj=%u{re*Oq-&^L;>&bT)>~X#y<Rs2!8Y54(V^6*-'
    'n#^cB~UIYo3t)+*sY3)eZrT^HDj;GBCW5a@`TUJHqDB$lO&U<<74mEN?!yXv7}3~oC_V^(ayo9+EKR;g>sQv?RCL_;YGc!^bB$7K'
    ')euN9mETK5ZDu)cozk2RAzWHh_i9SNRy0YW8Uu5mv?32gy73)T9$X<@|DTT+r~i@+nYtO{pH%x`XHkTSqUyJ$U>QI-'
    'w+%9*d?2g;%jn^h<0Qw6=NSzI)lQtMdPC5TjaN(rKrq4iQ;*x7}@zzQzJ9W5E(0VnNbN3&B$pjLA0J|-'
    'pqno{8YH!wZjCA<y9(J7smn^yo`hqu8N*P6z$m~h!`3hb7dXeQYdN2vN);L1wGmVZ&nwq!D)uLB3*lX)&S045XmDi#pifM{KXNmJ'
    '5<hvh;INK%vR<kj4<YF+yTG*P^g+!Xb3@rJf_hc2?jYh3ldsHtzk|xo7?Ze=)oia#<Jk>Mnl4TXEgU3vGNaLA4~?hu?zGei-Iux4'
    '@O%{G-Kmne_Nmj<e6X+g>S3vS>ttoJ-!6D5lk<5+vy6@!LP!srzn=A#T8*6Dz7mf>bB9o{Q8Fz#Jw-'
    '#EPV*X?Vr^XowfS}WNHQ)w0fm4Z?a|(Tqr<)X<@~d{b7d@|I|<-jYIQ`8dTgx=-'
    '@28q2uq>42Suo7kqF;=9Ur^5TuNmoZmZ`YjXF{tuvr81nUGEM@$3h30dT>kKk2nTA1;5x?eJFytt=f;b^60yk&Co9{8q`=q6)*Fl'
    'uwVgyBK)9MOW-twKl#+Bo=}=J5<!sP{u*rBi4OF(P)t_vMW+FX<<@tz&ODZF>VrN;^P|A-bXHfNEZD7O+CJU1XD64-'
    'g`q<eJKf70Abqkx{s~#}tUW@2B6ece}%`W_6RrR0p&7(<#?)U~*C9LmFR`m}sByS~g8T8u$gCpI9j5Y_uGqQck}6$R`#flSY9HPw'
    'UPk4tNdFg6!u6nRLn;m_P1HUFVF(niLu%mO!;c=1~?{F_mV3Op1>Ma>HRS*pF$~C56~yAwFi+UMqw4(ts>snHH@##b*U07L-'
    'tU01un7r*U)-Q_hq{>FT3fl}%%^%v?+2jP)F^FKfYjE=}y!P-vi<AZf^NM<tzzgHfT-?jpuokS~|<g*sMI-'
    'D+JkfJ@0?<J|O`+qJ|TSy1Ab<fdSfB+mpdQzj$O=p#g(HxC4jMG?<#kWjOU>?p#+FZiA7imIV6CrS%r)DAMt5v9dTuR@P#OUH3mI'
    '}N@=n@R3McetS=zbmA=@4iE-'
    '8^+_PFa;)XQHq&I9;O`Qx}(2=V~HcHX+H7n5>p)Wu>_F$Wlh*Pov70Bz#&W0JUbwP!o<h)_3Tpq>!08g^rkO(hmBJNN*(x7Caoq%'
    '=}o-sAHPgr4F&ZW24dB9B`uEUm?W@I%$rHbL{oBj9jkz-70?Nih^E;Zq$BU}ITU*%GSCwHX!4xfmM;-'
    'eYW0UwcRh<trIhvAwbQ8ciXbm>clmg9065oTMU>Ks_V>?Ym$JHCaep$=A3EI{UG?k}t+R!B7!CG%_DbV2h`Soi0-'
    'Bb}RHg~e%Co!$likfT*@^~22P~M0vwFH`UQbu8oMoKxMh9mOxiDwg*+PYAjri+8HzF9V+CL4%YU3<0FH)>_Cr&FGIw;m=*Jm~H>k'
    '@?Qv=^qzwX;mW2_6(sgu*ed5Q6pk*&zamV(bg4enFFmG;Tvpa<gRO-;=+DQ?V89sc5EHm-'
    's(a(!Q+igu86;4JtfU<`F=QCaTV83i?hQ8@-'
    'MMn|Tg{pV1Ix=j^RF)prF%g7}hVqx0ch)S4eyuO<5LrLRSC3*smPdjg&a&j5;DLvPK;uQd%W&z`Z}gGNfCR==-'
    ';0}v@BLQ)a2h{?3*>51H%yG9C!Q3WYZQ^(@w&@H?TC`ZO-l!-'
    'w|4^*@dl3*&qt1@w>7E7t_^bRJ%d!E>3WbGGhelW*FJ5h!Y3tLeMu*2=wWe6-'
    'quJw}bI0M)c*t|}sgv6A{yznN<jLu#ZkZ8(ncwuo&RI~jshhgr=aFq1H)B}kyDA}}+BffEX=82i8Aifq)!@Y{73@efq7RY1Kl^GL'
    '6*8I+GfK3T?G@4epkK?Xv3RV4#h6>(-&1y;c$Qq=brD@$P^!)2|5w-'
    'A=dLhap&3?YW@&NHGZP@`HWl`3K(eZSc)1L#lkT*rcNykn@9G>yFWSVeL`O<)3SO<|pdV%zEU`hO%CU?vmrtp7!7jjI_@iV+B_1l'
    'JaZ*gn75ul`e5Zn=l(wcF$j?iaKRjkWkhsw9Nde4fR-75GPd>95oz6L|qE+X~wm0S-'
    'iiE{Gkj=4LkhONG$g=(cTOh;o!uMdEPM}R}cT-'
    'd~DnvEi9tToI}pG8#%n`M`HT?P|hZp586vkWBhfj1x)al~D4<^U(#UV|y$V3%phOYMDYtqM$U5QYEj-pxSwN*d;5oRZA$tx_>+@X'
    'oe8kvkDnQSGj?;0nlkJaI+Z)UXc)c5)rw<^9Ke!ii(v&YMtPGNj!x+AQ2E7W4ql<4I2!G%Th=%^F3qO~Z&~li{_d*Yrb31)vZ}Gl'
    '6d4oMT|PkC=gu?e<1D_<hzpc|uKON7LE|!goH05nmZzd62QL`UMnRr`Q|+BpZ?Nt{%VRx);W?kCiZ!GM|omMap9zKKmx{+jq0t)L'
    'LX4ArYyW+CAzWYdFDo5=D#rv3YFPcuU~Wn7}8z8?#9etVkVrei6Tgyttx95~RS759bh?{i>9*a=T-'
    'D@+=X?%Uu59XW{fyC#GK8L)yrUvIGWS)QhM~X_1>kLf)?q1BMk(3sDoNof@kkEWQSZQeZRMDOfRJw~URcp|D@fz;SJ0#$GJx!&94'
    'c0@SjE466o1Ckbl|1y0_%ebFQ2YzvDB6`tX2;)6+Tic+P6iJjBJ1`89fN{=|vDIpx177Oyof@bJ5PsmY!%5kfVy%d!ks)Qs{LAW4'
    '~$~1&dPUp+KSw>A-ShS}%OG<$vMYBv!pL(ogF#=r<G_8tRO1$2l-<RX>E>Il-MS~0fGNxU^OKHi)LMZDc-k;?-'
    'J?>6R0SE(FFF}g)w!clIq$sf!utzP%$Xu<@s(MI~$MQ@KGk!N{N~a<Sp=>GMVk%3F{82^fDYQV18cpDS0rm~b4#?}*kd}<UvQlLS'
    'Oyc;M=CPCj41+_{;PE$Be~RNMu7WQJwb_)Dh=melnu-%5IRxAd$Nr{-;Hdg0KpL^~U-KF#&_c6L%Z#yOtZM(9K*Ew<gTMr-'
    'PNW62!r{dw_VwNio?L3v&Xu{j%0%hwog7|WhU-CGP3QVqUTT*0)4<s-'
    '=b)+ocCSWD0&@(S=ABe|rqNE9g3EPR5b~L=rb#ulnJ%f?7NuP3`cRT7E)@%LW?RM?B-'
    'dPTV{jf1CGHk>!;C9{O99jN6kyC8=C5dg><i7_XWta8brkIw&JkQkjODhFaP_GTqO>x*A5xsKWc(B{%WgDJ0-'
    '2V^%<8{FL16Ey3X$2ASOh27hpNtxzyZO_1sVwD!?ucLE8-'
    '^RyG{azm;E#y18UiDQ3KyP3{&d}Q!is$sP*eVDp(ZQ!!BaPcsiC)?Vb{?hBn+RfZDaf2429#{vc!sV@9T~Jaf}}iHH)hUt$Hq9g4'
    'HXy`ckYrdJ9f^VZ6VCvp<iM5}B`Q@0D$oMv01SGHLCIYEZW#@QX0Eoct-'
    'k~{=uE{LTnS4=fytBKo<cZ!&)BX@E;cUqN|oKxiM$rZ@~)ct>1vliT@g~1Qfz$<|+rElAWAcn7aly#q{kZ|cn(LZqwnTGo;mb%-'
    '&D`)B4RBEAs8(ZPC;ln@#`$w&~QL=ril)$S-42$C}D2oRs%bjDB0vB@%u9i-6eC<U`=SYSUf#}q-'
    '##$DD{(<U5Wx)_~OEMjb5vZkVHx_?nXdLlHU{y8~&s|adTaw4Nq*YlPo4Sm;M=;i-icF8Vw-6Q)4yH1V7+UY0L&3SlZ-'
    '7qYaGAq|txKRcQI^~2fZsh7v{=9^Z=5YkrF+cAL;hQC9vbp8u=6u!uEk%4M=b$jJZ9SO8=r|dun@pKQ~;X%2}=}9wRk+cN;6n0Qo'
    '+<hFrh$qCEC~A1lmCt9O23PFj@?4I8+&6m^>w>Za1$4V?DonOByWhh#YyayA@LhK+wAxC+Cb<zD!C7w~qR6%&u_mG_r4;mx9oUsp'
    '>O>1?EbOOAY@R850DtCtNc?OB(_y1@#xknP8rB-'
    'l%A=;bAGTh)#f%1;fIx=?TVj)Gh5P1t0L%7PONwU%eW#Lk=sR`1jdMF|6pYkX)KhvPGPJAZ9yRz7c}!V%{V1T*Z+VsjF1`$LKq2?'
    'FcY<amHpyB_hP+JP0I89&D?)CAe%Ey>zKoU_7)?p+LPnjP{K}&ByRPp*)csd~3<Qmku6~e(<bXh?MHv%hIW5?ASc#0Sk9h!ECF@h'
    '-}o!7Zv)Mh_uJiJY0=_=JmY_7K1xC9cngVj&z!eZJUk7&AzHOURt}vD!o6TaqrZnRjQ=5m@n21HW{Q38QJGe??Z7X_#hF=U0+DZ&'
    'xIaIi|5o8F4K~;Sn42A8}%xd0Wrm})U)VO9IN=eAjTHP<Z=;FM;BhJ;tTqUe%GchUqvXVq(V_`((JYGPTxbgT^w9;YLs#YjoI2I-'
    'B(;zniJKT-'
    '`K0AVyR``6TMW#kcz1E6mRNr8pc?Us=^A#7_6?ONu=Ly`s83!;(;;?PEMoKLdqmpbYePC;M`1`xO3*JG<?i^&u~u8&nO+Bj_}K7!'
    'RirOtz#K}k{ZUd^3;V)987LLH@>gXkB9r4?hvny)DjvqJOm}#F)m^0GbKT(z9_XJ#k6%MN{JGAr}uD#Mx8MMtT110240Y~EUN#gm'
    'k1{T87+C^oX)ESUiRrs?fBS|a1@Ci3fB_QRiLl>?G<z|e5fTht8(RZZ$8a(LnP-'
    '$+dp4xG8|i5xYtkb=3z#r(&wpqg}yu;)#~D_s{tW3t_-y31N|SZ=81P?HH)0ul$p`75H)em!1XK+4ReVHSRVq3JX-lFccir`vlE1'
    'rB$)+Q7;q^`+N*PdhA=hYwN9$>U6<RkybTC^;GN`Faj@cg?PAk9i9%lzJoPl6;o(BOD_Q$~=hPCqF&Z)+EX^q>VKY0BJ2t$VbBFt'
    'asGf9kSD>R-emd8%z0%J{kcOwW?4MHCu%kWzESRLY-MD48o^;fFGmGwK66$<`W|mfFC6oFre_1L@5qpga7wJ}CBtE{ao!LNlVi+T'
    '0bc%5{qkH1Eu(_?!MrniZqmgKH)B7|WOLxHSoDJX+lyn~?7z@QOVsBUxp}7n@#KIy&=aSZ>P6g4+B+Z^NpN1VIq;!bYpv*Jx{KnI'
    ';$@Ia7n{w#$^#E0YtJ1MGF=bmg!PqDwLlE1xB*WqYBkj7MD1lIukC{P~c@C|Z5kj!pB?SiS{WCF7dXmFTK;6USoe|EeEn>=5v1|('
    'JDOZ2rY~Z;o^o6k|TDXnTeeV<)`AvPTj1v>4Ef7#{dH~sJ1o5v_`rdcJeH9d=leNiJqJ=beA(v7T&XXZj-Noij@aWAKo_$(TDG^g'
    '{OCzt~yuJV(M#b_czX$gAp;avyk~l);qX1{L`u;LGT_oI5@3+L2n`#<CL_$;%$7t`5Tgj}kpjaMZ_Vhumww#OrWT+*z68RDhNA?3'
    'Qq@=_^Rsfc|lEvZ2?aDyR%Wl=E77H+78p%E|&x7Dw)g1{B8}gHscQPJ*9oKrdYBD(DpR#DUjE+yr0wGV~xQpYYNb7tRnA=JzhnQM'
    'z=hWk?*iCNM3Vl##zWRSDE9{sw{u1D^!x<;=4sUB@D)9Oy%*e<quCmXn2^k`LMv)JW$Zjlsk*p1l2qE2VPxFP@OH0$mmfEc<x+o~'
    '>`*TY&MHL9EQdq!J%H5;|I>y61fTct;x#oY-'
    '3ug_Vg;ERoGu_NO9v8r61K7jh16CAqLjR^VuDp|(iep{##0O69%oP_B5G8%b6HR##Sc@_7*M>wFDn&M!A-'
    'N>N0^FG4_PeVId;n8n!o0$HEwsr<Y@}79%JirKyMxTQVeL01i(rvJ&Ehl3hE54@Nh$Qi^lxZnCd5J_8~eNu@9=ZT&aIz7B(n{>|7'
    'G4Q`5iK9UjIxDO5OrmK#bK(s6rUC!cFwiMfH35y<&xq%wuNCAhn7%`+O25zaBcl$?=BYKusox#lZ&7j0M=$T;+40Il^j58Bk)iUb'
    'FR6lqcIOmOj~FpubH=k>?!{lv|e$9kT_qC~SM$%Trb$=L6MF7HH6qKMEuowl^7Y=di=EL`RmJ!HQj0CnWI3lN-'
    '!IR1CLKny2mIn2<R&ENV1&6#=1C5lYg*e0c#)SdEy9*W;-'
    'r%HrDa#0K2hX_UlWW3tKZ<i}qI_Tm21V>0_WxF>_HjbIO>vrmGx)VU}Iin1w{IWV10!u2RoSBwrbl_9f&9nv|2YHW6JpMqG($xwp'
    'Qomgoxl5<q=trVpTD>PvjDodtIjt|LcfjZIcAN+I$y%u$IVb9F`mP>_OD8^zj%JvivD@iHZkwAoG(eGwrN|N$b2{^sh3J_=bW;u_'
    'SO}FpH(+pVcSvsA$imfBK{?E}*c7plI5N~N(k~qN?dzxLj{2Ty~Lv#Jtd<US7Ss-'
    '4|Nr4umM(8#GHCt8rbLyMFeDHAr0U%Ni7prTV$=+k6RI}T+sG*&Eaz8yYhTJWt{Su_Syvg)tT_#<L2y|fBm<l2!un?fbUU7)$-'
    'hkuWQR4NQG6SUi<W(&L<c4Mgu3r#>>uIOe8>c_djk>%ne}b_Bd#hDZjmb+<@qc1KFvBuiI8DccQ(PW#S5!QTCSC*H%1O)kuRz(l4'
    'gIVFP1IJ(rf3g!8kW?lJ&<A{fZuEvrp^%WK<av!ZKa>Lyl7LX_hd3}G#ei`M=n&e=|ryim?=Mwq*;LjIsH+uF16r!`>Jbnw07U3='
    '=@qLHwwb2iPv&zZWWo9bqKh!n<-'
    ')|#KUIyUoiz=Y&JjRL)3R4G4@(#D{1diJU2@rJGB*uiqI+DgG>p^X)$Ao)T{34hyG4rYC0^RN2jOS#({tZZUY3)t|zd8!-`pTH-'
    '}5anA<U3Fj_1){93rPvS|p)&b+)awMOqpj#Tuz6tFO!Z@H;jNi8&*5f7pn*;WwnJ4I1U*`icXW|O8oZQ`Cds4XQ+#BNV+8Kj|pE('
    'wNPr^K4&oYB4mPX6So9Y8&2kzT|1FG-Cvjb%&njVur=H0;Pf`u%y7m(#E5%3PZnCQeLMC1LRq!0RxZgt7RB2*Qk=%Ne@L7X<AS|G'
    'Z=}E)-'
    '#jrCkE0nV$b`KFzWfNEx02fvPD)uv1);=^q@@9}*r4^ou%(itKD8Tke#KkqT7~<1>7x>OW;83L&Gw`c!DSjVLm_iwD7>AUG2<<`L'
    'r;DOT`qD&J^Igo2{ETALvr5Xh97t5L$}O)zu<i?%NHPZv6EA+xiSK#u62V!v2N)q`QGtdk#Ko_g~l(Ok<{q0J5nH}F|ZVO08APn)'
    '>3FEW<+!1&Hy%AP9;rLV<IpDcf1kDHAjQf1FlFiO#XQrCfNB8G9rIt})8dU(Bl@a>+lI;8KO?oX7LbkvqBbOgV<)rqB5Y13c^AUV'
    '3JPC*BU;-SMK$~^NrSJrQ4XE~(+?+F@W5Qw4lre+3}P)<YqX_IbL?f}iM-'
    '}BZgECjwVO_!@clS9?oj^m)g=A(xpZ&~QnSX=cP=uC(=JR`T$Iu~NF#WFyiMD&kf9i<q&57YAiN&j4Kk)@Vt&{yg^;k56jxRTo{f'
    'c|N-'
    '@=WUr@dPVK>0p_ks+8?PRu?@^|MuB|5!O1X(9P#i=%LI3kdD?0dx@w0lJ6U{%rmE!9Lf|ar%VYr0zsHF?@?If(31LM2sZ!l`R%(m'
    'zr4P`e=nOjbN&T98ogQ{N5jC@Q7NG3D&rg}z?EE}$8L%O0iv-'
    '8%f?<wY*l(6_bY$}Gdb7E{~7q=Q=<yM;T|Qm$}D0|`sy`zxG8x6Vr#k~B&~U<+P3iq`tD63W(;4M1d9Ux!7YXQ-NW$fn@x@xp&_`'
    'eZ9q?oyV&xZ$jrz8vJGN{sULEf;jTi5!uG;beH3}H;`MZ>+_*syD01DrlzEbWu0>_aPIyT&>p~U%fhD~16V3k<R1x$Y;)s}8TFKW'
    'MvF0bDm<jiV$S#l*0<<hnyK<i=?#8LF1ct*9xy#^{Hu2N%rI=@zr;1I6YJsxBv{{7FtVJ(KU>$>iA`H>)re|WgQD=kmyx2;!(V7='
    'tVVr3#=lPTvWbUIG0Bw-b-zD#*UAlcu!FCCGSWe8C$%3U#k6wP)Cd5u};bP;Q@tOJzl`RX8-'
    'W87;xnQ*tKZ+P~jZt)<vEfz{HWXT9VS{pde2J*rV#T?*tLO<Yyh+1ly)6odshUVpicZ)mBJuGQ@*FBPkev98Z=pCuc5QW4bkzDYL'
    'Ju3*sjm%EP)5L3;EsQkp8POE1SKq@98@#n0v1A}vD%ckoM!G{se~d7aT^0u=`Y4iN`_$|3}-8#`#uN7HjaRhZ2yT5q@z_)#8QH-w'
    'q%>d@N6ysE{Ye(vd{)(tkVc96`dRg@I5ZSW1SoWOkhIYE)1C`@F}01g#X%D%)T^_69I>QnIxE&Vj(6?Xpw*?txg*;ioAUg-'
    '!+C!^bO5-'
    'y*#6%@<#Kq8~p+*^#oq<+V42o3{W<z3e}HR@97xc=@(KcavVJgUg;g97a+%#x5m;au7}^Y)`;M#5q547=M8&rK$_~%{xc8%2cZVr'
    '<p'
)
)).decode("utf-8"))
_V56_BACKBONE_POLICY = None
_V56_YARN_POLICY = None
_V56_CONTINUATION_SHOPS = frozenset(('YARN_STORE', 'PET_CAFE'))


def _v56_visible_configuration(configuration):
    if not isinstance(configuration, dict):
        return configuration
    return {
        key: value
        for key, value in configuration.items()
        if str(key).lower() not in {"seed", "randomseed"}
    }


def _v56_first_shop(obs):
    town = (obs or {}).get("town", {}) or {}
    shops = list(town.get("unlocked_shops", []) or [])
    return str(shops[0]) if shops else ""


def agent(obs, configuration=None):
    """Route only on the first publicly revealed shop.

    Both controllers are advanced through the hidden-shop opening so their
    public-flow residual state is valid when the branch becomes observable.
    """
    try:
        visible = _v56_visible_configuration(configuration)
        raw_step = (obs or {}).get("step")
        step = int(
            raw_step
            if raw_step is not None
            else 24 * int((obs or {}).get("day", 0) or 0)
            + int((obs or {}).get("hour", 0) or 0)
        )
        if step < 72:
            default_action = _V56_BACKBONE_POLICY(obs, visible)
            _V56_YARN_POLICY(obs, visible)
            return default_action
        if _v56_first_shop(obs) in _V56_CONTINUATION_SHOPS:
            return _V56_YARN_POLICY(obs, visible)
        return _V56_BACKBONE_POLICY(obs, visible)
    except Exception:
        return _v51_safe_action(obs)


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)


def kaggle_agent_v56(obs, configuration=None):
    """Unique final callable selected by Kaggle's source-file loader.

    ``get_last_callable`` selects by namespace insertion order.  The embedded
    parent artifact already registered ``agent`` and
    ``_kaggle_submission_entrypoint``, so redefining either name does not move
    it to the end of the namespace.  This new name must remain the final
    callable in the generated file.
    """
    return agent(obs, configuration)


# v57 early-floor router: delayed PET decision at the second public shop.
_V57_PET_ROUTE = json.loads(zlib.decompress(base64.b85decode(
(
    'c-rM%U2hyoa{MoRo(Ih*Nxx~OIj?Zsr9eqHI4_9B0zSilaei3)&G3J>q#<W|IwK<@vzsd&{3K#T_Ec48Rb@s-'
    'M*i|YSO50g?|=W>?^ply%hmhWA3j_?F0TIlxBvXt|N8vF=O6$6+wcGJxBvd~^Zzb}zxwn2!^a=9-'
    '~Hw4hfja~_5H*B+fQ#kUM;Q;Kki?D{&)MhIR4Lv{r>Iw<LlAKKke`Cf4*8QS6@E=@!iAz%KhQXLtg*<?x)vxpC9w){&2Neg^xe{x'
    'Zl73@*krK9rhnS4(IcEHQv4X^QZUEPg;I?($g=Ur$6{;{Ogws@?n2>cb@W6fBX3xP7i(>`touB=bwJ~^zQEMub*Gy$4_4t#CRiN9'
    'PjU5|NQav4lV{Xdiro+r>8CCxIcfvoBh)wi6vUNgFd|exPKVEyW!X17Y9fG=5<`T{<y+RJwAQ`7jv}ogE1d}m}yYt4WCW<Y4wgT?'
    '&}bqmN;7e%e}+%H~s0$!Emu8as6f;&Hi;b48rR<y-TueqrZBw(dDn_V)c%{HPa}b=8x<L3}Uoea~bpK!b0z9u;ZWp@A$OwtIJ-'
    'L+|=jA2YVR3nD`p>3qG9%;DO;M^60567Jqy6J1?+w;isuf_w-'
    'A{_y2WSTI+URo6}?SWgC2=zH$0$9mi9f)bSIzSf~H%EY{`Uk`<Zj`GdupcihPj?6J|)NZe-W<Z2t)k4-'
    'x|sOQtP;NK?>6FBqrA@p=34W50vqtK~#{7>?{coh*x>-^m4?2Vs$e|NWk^YPa|?H@kAyL<O9V-'
    'E%XKlM`3UzAR>XCGtmfYFOM+2x1(PviG+x@yCp!~1qUwzsE8icA0bx3bYr7|{l}vuHhxmvlNG&ch|Xi8s8Jc2G{1S&l^HqtDmc`7'
    ')Sr!M%OBe}8!coObDylXNieIS%HT&-u8GzN5i?-%B^IqwxP}a2=mw-lvUDpiSzbu;cI&*4tXBo%9TdLlci{KScHXmT_nr&UfV@fJ'
    'nIFC;=~wK2gU<ae+x3X^k;1au`oBhEt0QViSf+NuL?rn}y*Ln*}dxlF_2^$>*unWP_EH2Oi<TpNf9SkFOv8qDCAS^z??ntMc)OxU'
    'y)drxDI#tLJaH@QO#Fuij-0^Xr){@|-'
    'v7s5z}ae2?&Y*x<}e#PY`J7Cw@W0f6Ha?JfW9qX#l5RwFVOc?&*H7U)UKC*Fc#Ixp&ctZ7!U<7CVNpZF)Z<HT4ugLXek4o=|?vfU'
    'c=)A*~WZ=jxM;$6((@a#A}eAvTF#dx}Xsi4t=G)D(E#}{HehMXIn9lYsqStg?P*1;l?B`m#m<blGKGY)C-'
    ')`9QCe2SLu#vHBiwNoDraE+eZvQ7@C_)W}jhThBC^j;)X{0#e@Us-NC#py4l$BC>x`XWhm?}P2o*}X(yiYbSYi?e{N9RDlSTRJ`I'
    'gne4Ddc)i5Jl9OCT@YVJGb*@Y+o~Hj`1tb*JlubL+CASt2J{k+QR;uycO2LlAdA4iXYg`9e0+F)_+kI>@K^9%aq-Vv&-'
    'B6?UMrYR$s2QTPH;8or!#IIT>eQQ9J+5E7mF+^a6@XiiHjgbCxj>8Y7PYOJ;!#_p*%8+KUqn*KqtdY=g$%-#bjZ*e#elUf-'
    '}g(AiQ&mgwv@fHqRSFe!?vGwfDTaUe>f}0I~pi-'
    'h}lhUv%=D3h)oG$88^6;us{D+#<ak*N=ZF?p1NPHo~!*xLqkGRrTILa&c~#4$z0Zxr{xPh3_fZC+|dv46w-'
    'Yr8@C@s!mDa(Zv@wqvwYl%Wx-kvM-WVG#7mpV~7AxtfUum^x#bKdGZDZdw_gQ=V-'
    'A8=w4$H5CL$V!vsAVzgrXt74ooV@(IjAU;W_Oz=;K!O~+_JX~wvuAUBL!HkDM&ARjt2#(jN8azD4;dECwnU>(!Dx@q^^+p~D*c{N'
    'pVsn9p&j6?34fpcJ0aKNJHS(x(+5x>Xgth~Ba0;6#!bxH=*pm}eFyJo)UWnon3Lj&GSmjh(1&7OY=Hdie6Dt)E)FyNGvLkT!f^9;'
    'hGn<LzXkHA9<+s?uB7!UXNcgM0}=sroW*_r{Zp*syg1)HDmt+!WsX>$1c;o7WpIDRq^aLITXJ~KJAN=ZD=HIQfzB}N6nqVdzv@a;'
    'U7UsX6hVDy#*2y@EsS1InHH`C>Y5*%F=#RyN{Tfy-'
    'c@W^lIBf`Syv>3T?wv8WCEf$JJ5H&7hAKa7&mvo4M6J1GHkQAEl^$!<JI@@SZcd^Ml_dWaplxhX!ypzF3K!<u=jJ7a?g^|rUJfcU'
    'L9Q;bbcI}Wl8u$wMo+{m=CYW&Xk{~T7dW0nmMb^mHf;Jd1gN4aTS*G0puwEJwcW8u_RqYh28|MJ=U*?_l22y-'
    'qwrkTZ^I`G(rmW!8=IgqCSF7x27gUC@YrZUq3JvPst&g%YZvUe$;me}Y@}Ew(;K+HJnlp&cJ^gUH%0~D29LWUoCFdXT1xDkCIkG^'
    '_0VE$Mp<42>8{V%>QYE<6ln*&B=EjW63ld>B4VNqet$v4kL0K%x5>(z@M^%+zFc46qz#H+Gj7F&3gm9F1e)(fRHH(?~O(x8bj-'
    'N*S;MeA=D#}b(W|6ELVLpsOg@~txdHe34Rp5RRiinyEBEo~#C*(U@zINEsC*3*vN&xoQDZT=HIHzDTb7easQZ(g+gqMI9JHc_zi{'
    'i4#dzPxV81Xe?`w`kab>7oMyeVM{ncfR&8?ed!G0IQ9Z!`o{=PY%E`6W<!S%b1a56XA;U@pg>0b>M1iUZS+EO39GkMy73-'
    'TnD%D9A&S@as`=szIecK8>W7)^>`xk#aK79fM-8{xcOSTQ`E%+6aL^zy=rv$y@;~OSCEajAws$q^Y~gF1Ut#)M@H?6P*WRr@-'
    'i+%(Hwn5>W93{ZAC2%wdNW=3tO;jma>K%lq{Z>&JqErX%pG-pJW8le&H^5t{|qEEG|ei{1fIgl>xH5mK0;^nx*tliyJk7z6=c91N'
    '}>iZ}<#(6Xq)T`-'
    '~tBmM2MwJnmmsM9#5Q8Hat@czyNK%^NFiXr1`D>cR!3zo5PI(2Q1?P|`S&d48dCp5^J2pbcrY`!q+682Pmm{e|-'
    'R6}l+`@TGEk<|;(++)YYI>pgu01P?<l#-'
    '3U^e6iUe|7Sj@6qd;Av3B~pf4``ZzKY=>qeOK<|1L86F8uX{Mw2rtqAf;G+Rb}A}rXn|Hn+uD7ZyqT7Zmic%Iw!GDl|Trbf$>bf<'
    'ifR_5n4D0eaK6jn{%iK4D^q?>7}1SeRHkI2EAjl9-*mY8I%k+T(Rn22XHU9LQSU4b556t;6$%&)(qW?*K#d?h}w95Nn_^tV{4-'
    'V7#|13_vyCBfIanGJ#<{B9|Vp$Yii^G}}4!2ijeaZnZKD0k3M4J;ulz9Wg4GGTOGQOGbvIlSytj|$Ww7n8-'
    'B)A$(_0Fj5*+W5>_k`|G@ShQYArwtE1q-'
    'dtkPZdkGxHKhX;DxN}$}EFkPaw{^x`x!k3Nm=*fS2iyB(fjg>bm6L?c)rZ{)=Lsy`S`*B~E=&)!T(2e|o|pjTGd~W1*a0tAKck$L'
    '*wue4U03+s6W>s2q%e#($mO0}vf3Gk?)fG!9V=18+e+VAbZbDR`XG4r-oXCh~!Xh5w&PgNXK5?&>m+)ke-'
    'E5F?7~s%eI2BF3?u@J<bv4-EWXB-'
    ';s<=QEq*G$eP$S)L9IE&hP=c7pRg9OdW*@mUqdj=qZv*v7OY94DkUjdO8q8iZ@J^~hCVcn2qqir0di>imt0N$RZ)s;~n|0*@K|CH'
    'ez!Gn^*r0g4yz4Eli!)ssB-'
    'a$9ydbU6t+Oq*5hoEJ<+BcQm~*`(2*Usf1*Sp#M)1;f^;bsp*cyPLRusk3EhTnL?x?qzo30cJ%NxU-DPct+vYuoH>Owog+u0y1D('
    'PA1&bG*ElUr-9^gI@-'
    'G=C2{`sIE8qRXM4n^91z}Lu0+KtXe2+_w)dRqhuzAUjgGD)I4OPUc$&_q)$(!UMbA+w{SdnxpX2MtM(b*qY?7WX5w(eXs$rY7bRB'
    '$j+(K{e@81{MCtXA35?`i!vRvcZ>gBQ_2)0_!j1Hwf_0}ag%z<)A*`#HW!){eXY!kj*-'
    'dy{9EYkYQke}&QFm@OeSuu8!WD<3JY;LXeMc@%jx+KfF(BbXv9Bir`b@Ny#7pc`=7yK7q)ay#m5SI?b3vucoUf_ekp6JNCa202T;'
    'Y}dU#tkD)GLnsX(^6kjl!+5kO<b^_cpouenXJ5R97M6bSp?f(zB^hUMD_m~aA`pn%4}YT*y#H%*@P5dlWRn@S!1af`+zbeeaW_HT'
    'y#Qb`VXL`sLVcz;(4kV+4){mBQwje+T%1OJTxPx^$Li@H3*Lnq#dH&1ILtH^cAvUtC!JO0E3s2Fe)14#2||H>=8r^jg6_Y4sI!wG'
    '-O$v)avCPZGmclM{97JJT6G@;hr^svlm42$V>4#UJ-wBMC^8zb0Ojz00*;`ISC_-'
    '`5L#tFW(iaW)&Jj&>)X#G)00z4$gvvW>IUH(yQm@8!&n>34pOIIK0u2@ZK1mfi772yRZ*NgIw7K`jACI82&p=vW6>m8SJkM^ng4Q'
    'Orr30wFgnW?$5`U;5LHg1+yK$K|1(FSoIXes&#+~xH>fXi=nO?P1w(WI6~a}BF@r>V2zSmo!x_B(}D#G8noI>&2O@15L_rge`R6C'
    'mi=Le5r1kZk;b9<MGY$MB6M&T-'
    'q7*)YKFsl(hGiCZ%!88`7I+3<Q*Fpx4NC7pSYFRXCrnRfTjcX5xi<m3p2h>uU)2%7xy$Q91T;LYI5=(_^OiVCS!dtYIQS*;X(17)'
    'bP?nni|~A3<n<yk3B_slk&Z)lun^B#E94l-'
    '{&{NyrkdkYna*F_4EeDnlNVQ6B>#RsOIH*1}j9{B_DC+c0;Y(CMqXZARjwMM&aTXQy^}?oqoesWcuCyXk|J?q4(1v*Kc5QQRIg-'
    'z9uozHsQ6bntn9!3p_vZWm~#ZDJS23<O_?DNu$7pr*$V12fPMoLH2WmOgd!^%pZ59u5(6Xu@NjGmO!;c=1~?{F_mV3Op1>Ma>HTI'
    '*pF$`C56~yAwFi+UMqw4(ts>snHH@##b*U07L-tU01sQS=W%ooQ_hq{>FT{(l}%%^%v?+2jP)F^FKfYjE{*KfP-vi<AZf^NM<tzz'
    'gHfT-?jpuokS~|<g*sMI-D+JkfJ@0?<6QNc+qJ|TSy1Ab<f>qjB+mpdQzj$O=p#g(HxC4jMG-'
    'G<kWjOU>?p#+FZi9yimIV6CrS%r)DAMt5v9dTQ=vz+rQ<lMod(~b%_MiBJKU&2yPfL3{RXLS7>}dE6qvw8DP|sdm~xEEj{XLYCHA'
    'bQ`M|SFOmWP|5<upcHDTj)qDsdDhb&3+?0^Ic6CdO0*`@sFKfx#Hbzkrf8>a}AI`E@RT8)m<>v-'
    '8eeVM)*3hFTo#H#B`S{%<ylE5}GZzdrVP08VPECQldKqp8dnr3T|j=aO?Q0$G!KuheS$#ZU7zC=W+)$dB(^(-'
    '=#Qr2hJPNU8%g1p4t<>S!-;8cqhQA#J;-@c4p%Ib2({mDds=yGdx)w56Zo-NG7Xt39_R~nZ=+|_6n(6m&hGEHz+p5-'
    'l=>}HzDRx}VgV8KM3)zdxmdb(=mEaQwfIyiI4g*n5{7Aiz*#9s%x5y5EH{%IgqE9V9CBE@QV;<TcngJP{VeO42{E<wmndts_vJIn'
    'N&;6VXJC>-'
    'MoAy_V793p@y#<q~^7c_ZD<2KYJS92!*J^4$x6l>w0ie`#+iT_<C?aSIuxUUV)pu$sS9s$H?qUwyMpl`&n(d$UCn&vS084W>p&St'
    '%;&J_>|;v~&R=fkzAH9xSXCHn8B)1tTqag>2Q0Z)Wy0L8AMx8~E=ng*9=&)DukBPCI*-'
    '&er_h!hebsfbv_WL)(0OzzEHBZb4Lf)uBzV{von7TyMwBV#kl#2};xD%uB0FqPm{nK)C6rBru%2NU5vPwX<X_6s&YSmU9cD8q+^t'
    '*8Xp;r8n?1ePM#ddYU20c;6uUZ+z+VoGFPcoSttXD<p!H03tDus9~F*?yS9F!y6PO8Q{xfkYUTY}%(0UpqYW#7tBWUyG;VUd2*|7'
    '0C(<<gw_=j0qxZey29Tri3~gO)K2TaaUG_s(wa81+!qQT2el;25Dz$S~m+l|2kbnExe>&h%!sFpKq@`K>SKuc7R7&l(k`WJRRorr'
    'vNTwrf4|n*lCEvGyaxL6Amh084wKXAW}##kX{ZfiC@#?j(Nir{*QAZ$K(`0!&_3nZD{uvx0V|LO3DYp9bqV~8E5MVeb!XPIt_NHe'
    '0!t!thm{&f{(!u!$8Q_V944<q<+4V>tQ8PPCnf+cSqH*)mOAotyG5TXzb|q0g&(raHyCIn;1>AQ6!DEhWY8EsOn&|Y!a`_VB*V-'
    'xUp82fh0cg2E-'
    '!vxC_n{;AGuvFy$NUJS};ty|1me0@E8r;Xk`~Gtj+~hB+9gB(r;~RE!$Dvn>zgPQ+AHyX!2t0<s=YT#+_4>|KGKT!(jg|1qC%;+V'
    'HH6Us}5v^z$dg<Hjf9>94#>gj@p#dN4yqbRm%7_n?Lyw>uXeh8@m6ar}`&<&h(3=H=XGtjZ!-'
    'slFu&zh4b)I@ePt$iST=VKW0h2fP48Oy3)K*4p2z44!9BNE=#<2$Z<VLba-'
    '2{S75>8MwvJoe$UuLHk*GpS9jMYa(Vk(#O9qu#NG6MQF8w8$Tu$7YSU1P+Y}e8Rgin*_m%)Pd(0@mt7?D{3S`3jFwR4x!mEN+~P1'
    'JGLj!5@Ec|<sbemoPO%W)N6Z48<~qNfx#E`BI;6F<hqcM_p8HzVa3xz)Wm70#wrMl)8J4FY(_f<D+cVAOJiy%>=!d|TpO6N7fbr^'
    ')aIN3wJagSs=?4n!Wu(?lXq%g^awfI!XiS2XSka9U{af+ROw)1=d`fF!o;i6BTjTm2#2P{f;_UI8T!l<a?~Gk+$v))MJ0zSA<0w_'
    'F36)Y4WWb6`7&>oQIi%H?di>uQlLoDER)lx9_v_)K$jg&t74WCueay-<>hx5sE&Z5!G(Vr(=OqqwB%wTl=TYl&vKj|cc-'
    'NQgaNEqAjNsp-=<Mgl-LT`qZVUis@7*!J*3EEd7*|G-'
    'wm45sR%+STZ*@s$`Tj;s3P?gTA)UaCUCz1`vzqPWcoFvCF8FwRM`QOINqmuEF}QL;LtR9{Dak>;y8+L!54&Dt;$KnLJ2ZW#R-'
    'ud0`7)me^o+oRDBa5jad1wX^j(Tp;@P8#-(GdYX6)-'
    '!jfKtzyzsIqy@CX;l(BP_1+7fTx!$KmASdfMCtSn4zDi5^&qaMbNwtYHOcyE;B1$3(A0msSED6?c?p{4om6?I(N33w%XL!_@|mor'
    'Nj0>YE~(lUrCjQASCT0%6$^1@TgDkA*IaL7a2^jO?iO~#ge!nc0n_#rV9XrmuV{d53(ejq-xREM6zv$!5nM-'
    '%<))Bu^{EY_v@*LNQk<}4{1h?EZZuB<nU=;(>c2ukVDG95k=dA71Q*zcs*aDq0l}*o8VKdXwu)sd;wI)?M*+jDewvN}wQRVkfo~m'
    '#sda>@mod%M`t=_bEDG#l7cpWy9ZRToONmxP8*UarZCYUiFJNMS5Hf@@BU4wNxo%A&qD1VMSb=bd;%sqm=zyB(l|sn8wsPW$oJ2L'
    'zDqGUj?E*EYS(oUQEtY;xkYTcMcE@E4nghNh4?&p=VyVg%Q_a|F;&$VmA|~p{9o){HR%IpU6#05`MREXj|6kRt1-'
    'EHo@Pjn)N}x;W+cqJH;VT|x-RCJJT)K<spSXrh!+jD<-'
    'R<9%vvjU2wNSu~t?=3KVIYG2y;j^P**;ZD;8i1r#qk!D#RHS&&ap{>i#Y{XOD8$L_M)Y8BtwZnbZS{+Eek;ZKy{+BU<kP-nGVGW)'
    'Kax8i$5|njyMrmmCeL+7gYb2<gqPjRo2F)E~D-'
    'djP<A@(<AOJghhmdsZ1k=)_dzvaBlDn&}kelbC|Go3G^n)auXf!+sA?y3z+iC*`ids$80?0&vNzHke7j-'
    'pD}YS{wh3b2@vBk)4p$fCgQ+C0C!gbX!0k_Q7qNs@oXy1V5vw2Qwza_0^OBpTXPd=2VHQ4C-'
    'Y&n7}{{CGQhBSN=)5uUJ1r}oO??eEbfRLd9b?`QwKoMyBR0vh*-'
    'W#N(a}D`ftpxaPBm+Z=9Ec(1@w(Gl2!>N{mYl{}>q)1hFSvGeAol0x1Rc7si=jo^sx(Xsh92DX@r6fRqKp!msfO#&gsy?I{Hx@YW'
    'WzlQDmLHDrezRy^_VvzKC6(P1IEG@WFNIQ>A(cCvgU1lPs9N8-7PBP~)_srHZ2ch=ewVDRFM&5%k&h{<^nNR&L-'
    'R&h&k*)n?RQmw#vXrV%ZdU+V_8-<#W;d?@PB02chl6x;5JRtqxS+x);)wh?WQ_tA3dCmhC?xcd*R*@0esG~0`^fM7@kG*-'
    'g8vV@cdlkG4?%Z^!*@QXLX)3mEHWoMgs@iyI?Gmf>{(#24QI}S!lGb9rSU1>ckUnH&pEtc9iaWsviBRtPL_&Tk^hjDfr>=0BmYl^'
    '>2Z`FKSFsF;DTbw<MUUcG#peYvwlF4_i-<b9@LCmL&{y=kHg)+bLOCTBifWT)uYGqq58-'
    'xkaLK7r${93fYnOCiaan0jRA+u;ua=6XmU&O~QV~NcqS8~msmEy;W8JF?D;#66x{@Z5e!c3GgH4GC$}BiIjZO<GlU&h>=|F*VGi~'
    'C|nXA(9G4DOYIXOS0bbva-FRK}=M`*Q<W%x;I7_Z867cy}$x%u2UU!fll_cz@kUK^=7G-h}RO0r{I!qR6-'
    'f>M1^YD0=?>r9jqCGuA9;Rua7V**%V{<;}>LDI6Q{-'
    'a(ZoCIXF<c)JW&lY&vrxUf~V@tw|NOV`YmVmATo$A*q=wNtPOKeu<%IV&GUgd^J&b79G{;tVzY;ECQKfUY637JZtr|K2@@^n<Ii?'
    '6N*gw(h)(4r6Yf3%t>-'
    'jUTTa%xj%E{=t$iE{+5Cvj+)OFY2(5J=?F$`83CtxcJoAfzP8EV#meOG(mRof9;KsR6HbQjPDr+?3^QK;Q%KB)5u#71wJQo7PDb`'
    'jX(Kr}+#I7vf#X+V?xBme7sSknvz?PC*Hq*n!-'
    '!;mwpg+!sXkq?5Y>9kue)sfO*9el~(MytHNil)8o;^#NePB*pE<EtB=6qvo4gbT^Su=L<Bmv@$E1)MxptQc;T7YgD*MxB4RS@lEZ'
    '_2D%f&7!jjWjI$Zt6SsxUO@%f}8+`ALM4Ox5r{P$-'
    '18$~l0FR)g`yjzsD1H%}VMT=IH0%%yiwvDhT9Y~zL@$#xd&Ybkc94+LAy$Jj&Ajs)Ps1kT2ODn6uFuy4R0Xa|$KHu4+rkOPMiCi;'
    '*w!T(78e+4*Zo8ZgqnQJ1ftAKXvJJ01glL_V6fc25c8xbIm`sqJxtyi;iTFkrd$=vrl6j3_4myNo|{5n7;B-'
    '0+Zf&VPJxl%)Yr;5F=5&Q0p+>}kR2`{{)I~4`!2Yzf?{;CHn~c)kj5_LQcA*kGK8wT*t`iIz4^kk&u>&p#FX38$SXLnFF=P;vHZ#'
    'JfxUigRSSkBj!^k1z!|N+zf4XS33t@{Epg?hnnn<j5LLu6+WX^1GHWa-mPeR9eNd|{CnEqEYDuj`zC^>3{eTN8DKU^0fTgZvarkk'
    '&G7$5$TQ#c10t}c&vJcGTAox~wN5aE~{3PX_j4!^9YrR`F865FXSu|Wm$0uchkf(6m#c@)kb-'
    'D`7O{J7WEUmV4>hV?VCO2z^KBzNa{lAnIc1#+73GmqAiW7K;w>2^qczqLQWaI@`*=N;+43Rye$U8@5H<rFg)&@s}knXmp`NHg_rR'
    'icz?N$|C6cqLCxh0vR3WQZDEMO_+uF?V><6$1aQlgoh^S@}qS;J?c)I$DDH?xk%1#sB__AvMXD~dRwe^VP*-'
    'pNeGv95XI11GoU8y6A~C4I*OO?ePli!t$+hC~-'
    'CMK+irxg^32+?e6^yR8X)08?SYyux`cw8=<pq*bEI^r!*5gRHn=?bjuXV39!0;xoyHP6=;GDfGbfZ)jvD#6lt)`?wEp@pH(|t)D<'
    '7vkkldW!@|K9WrWO|4a=^-U3=cjMYo1LKw5cP4v-'
    '4^?P_;u|h}YF*9Y5T1A_EK8ccF51ruTc*Ad?CX>VBU;}5y0_<w4^106(VYQ?TD6v|v+4?EUlkF8tA8att-=-'
    'Il=PeMFTb2$Tvjwv#Y<u3zV^$#N1JzCzXwXj|1riP0n+&*f*x^{BBg@TT#V)H85}5Jm26GS<!)=u2X?r*(WKIo>8qIA*Kqys&l5{'
    'X%UO*F8Bc|f@cxs8VxHdep0XKHKNa8Lr+2m&Q@#ld(+<$yZX1@gYWU#dn>|u2FNwAhW7sWtPR;4lrrqfBd9wq9E(P5@CWLB_4I%i'
    'Og%?|EU5DPgNN>I8JD=kKHj_R$IqI6+}ChS6G$#lu_E;%hwC%WyUpRS<SqHZqinVH{msc;L$SS&`_p2A@zDMdRHh>$G$-'
    'AqhLQobqyr`K8m;tXFc=jpQP_T6}10joVrr!!Zvbp+S{+55>(us#{$Elo=jC%9ryvn!XM0|0VpuK$|v0JJd+#Oo<3(1O$m-'
    '3Fj$t15p^ee+k3J}w{tM9Se}b!`*bdyJH7cKa4Jv{O&+=V!){yT!DhgOryynO-'
    'f+q$?4D4h$PpL4*Vr0(96Ehj{KaIL;j<Uau)LK*|qZ)iOYCXg1*d1tGW|cUrx6`tw|?%ggd77%Q;%wkoPIc_}LXPYeiVSY`{S>3D'
    'F8%OmcJibv7JYrw3Ww2VIm%GPb@XBB9owo*1ld#KYer%vsT6bk|TW<4`?hIj{3*TZZp{j%jnt3tgelX;`r__#T8p_)}Ea?Qs~`Ee'
    'x83LMDsN4>h#g6Hk4uF=ujeT$;=YpL8Q2%{!m%cZ$hWLnlC;L2{Mh^-J0o7{iJ6nwGS{EQD#-+jc`Yn`p6y-'
    'V@jEQRdUR_rQ5r*sc8B`BxGj3rX9x~K2@JAtX`uzVg}o@yHh0v5Op5IDP@zy=O0X3^aoE)ipD$8^DHvEcA?;m*RQAt*cZ^2XE}y^'
    'kEJ=w&HjVLab*Q?-&>Xfz`pL^HCjAmDe3qL{Kpsi4dzO?leHJ#kQ5N|uP-'
    '9^5iWL;YM54A)MHHOo1peFvQU(N#NudX6H!hVNgJ8fO~ImgF0GL9EcQBme04=TTlxzosj5Z6=sFF;$g>#YX_I!)y}9;tUal89SFV'
    'bd|plv`_r=lF7JGge8`C36y4h{<rxw^Hv~bcnSon#t^|qaY@F1uuDHAJQU~`br2QV*+{nBDHS6XsvIuQ@Qtefl#M8ai~{RZq2)HB'
    '$nYi}1iOOZOw5=^j9;W!!Q527(Ub@UMRT<_Lp&gmDKl52gwdN|=mcKcveZ9a=(L5*&PD<`qJN4#v5u+-'
    '!&F%(KmK~^&5J~HEnkH;J0#q|XEudV>1RD};?lmzSmFcYJ9;Twt|XLBi<v%o{eeAhHhxHzJxjqTMgK`%2d;@2#udvn*wg9Z<?_+D'
    'd&cUJzI(bqQC`wfTdvR%{O(o<mR6-'
    'rgBgJ2=%zXa9UO{>4u>f7%<EiPznP8YlmfgbXox`|hSHmw8B{_!4e_T<x>30Uw7P!JTdS}T_`)<@t^!RCRckwrg9e+A9)`SSp;Kd'
    'R)oY+LA>Qze+)nFUh`|=i0C^J8KZ13XV(>mp&jTd=bGb#9TBbo?sqci-zMJAoZmR(Lr_IVUtt-'
    'S6tRSU>WqztswmVr}^tAlz7Y9aI>!d<ApIxDcG6z69S}SZ4&-*3cH)fe<PA%D$DN;_E5^w~9FlXMQu*jh$^~Dfu{^8TRySKl-xxa'
    'ren>cg+1w0zPS|3Nlz}8VIpyw*%94Ww+T%gBpiUI+mu?Wk?o=I#~dLQ>IfCV!-*U|qO_~LV;3cukVCAG>dVov(%HFvl!c>rQ-'
    'x*;U3d8pd9F#~<~rVulRuS|kP0sr8ZLjCSx`1RE$FBzdBxU6kJPl~(P@|(!a$N#bo;sR6O<uJo-g${-'
    '7g{S%`@?gd5=}@_GgCJ1kx_K${DF0lG%9Ne(l4RC}D*6L+c;yG0|0k#-=sUy_F|)LiziY&rABkcn+!rFdKu!qIvN-'
    'L^eO$O}r@j&x4nyQlgIC(b&%c*qo?V_QHW{h~$_CSB5k|8Xy&!>g3<8QUM7x`wiRDI}4bJmoZ<>wPyzmO+Olvuhr^Fz0AI$)0gIx'
    'SwGB54YZEFg)bI8MTV#Y)kENy!9>YFwpc6tjJ8|Pe}sV`93GV|zN@u&+ItXASj5ksyqiVie3+)BcRLW?YHP)?685p`3nI2U&nJ>i'
    '8nX}GL6Md2`26Ddm32|Gn3KAuCKU8M$+6QA)d6o<&Jt*(lWdjE{j!v=QfYl9S&5wI1w<G)BxK3pJz5*ASosu^(s3!%|iZOL0sGxx'
    '7lLJ@|zje)837h@(R!!QtrqZQD7pMzp6M?grn|HKE<-l`~KDZy4-'
    'vej&OHWvUF#S7%M&<13z(+DdS9UTU69;e^2PL2U4Frsc3hRhTAluu5=e{C#gUz(?dfI~km5==|65R)dfNWha;r(H0LynPVo8p9?!'
    'LvyaDXLMBFXg+qOC!kVKV1nm<$H``ZvQbs2{^IRDAHy3xA%!Bx(Uahn-'
    'ZA<G<hb(Mcr}Xa;kT_dB6w<qom<42VQ&VcsSfQw^Z0+>I}!i'
)
)).decode("utf-8"))
_V57_BACKBONE_POLICY = None
_V57_YARN_POLICY = None
_V57_PET_POLICY = None
_V57_PET_SECOND_SHOPS = frozenset(('YARN_STORE', 'PET_CAFE'))


def _v57_shops(obs):
    town = (obs or {}).get("town", {}) or {}
    return [str(value) for value in (town.get("unlocked_shops", []) or [])]


def agent(obs, configuration=None):
    """Use only public shop observations; identity and seed are unavailable."""
    try:
        visible = _v56_visible_configuration(configuration)
        step = int((obs or {}).get("step", 0) or 0)
        shops = _v57_shops(obs)
        if step < 72:
            default_action = _V57_BACKBONE_POLICY(obs, visible)
            _V57_YARN_POLICY(obs, visible)
            _V57_PET_POLICY(obs, visible)
            return default_action

        first = shops[0] if shops else ""
        if first == "YARN_STORE":
            return _V57_YARN_POLICY(obs, visible)
        if first != "PET_CAFE":
            return _V57_BACKBONE_POLICY(obs, visible)

        if step < 144:
            default_action = _V57_BACKBONE_POLICY(obs, visible)
            _V57_PET_POLICY(obs, visible)
            return default_action
        second = shops[1] if len(shops) > 1 else ""
        if second in _V57_PET_SECOND_SHOPS:
            return _V57_PET_POLICY(obs, visible)
        return _V57_BACKBONE_POLICY(obs, visible)
    except Exception:
        return _v51_safe_action(obs)


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)


def kaggle_agent_v57(obs, configuration=None):
    """Unique final callable for Kaggle's source-file loader."""
    return agent(obs, configuration)


# v58 public-state known-floor continuations and anti-copy timing.
_V58_RECOVERY_ROUTE = json.loads(zlib.decompress(base64.b85decode(
(
    'c-rM%O>bODa{Mnm^Pv7<lk`n1_3j9(848qSVm%-R19%Ms#`-'
    'Y!&Dj5LX~^z={W3BlGV4(@i#>@TTd(U?WmRQHMn?Yle;5Dp^Dlq<>n|7o^5eya*B?J#JYHV>=g<HB@Bj1V7hit-'
    '+t0uJ*I)nl>(76`oPP9&yZcYyWuN`=;t!wy^3#X=ySJa;e7d;2c=&Gr`pdspkC#t>`MBS|J^lK6_UrHW@9%!NxLmEj{{Fjn_xlU?'
    'hp!KL{lmNOU%&tIm^XJ17nkes>yO{<_aDCgVfI1~`;VWd@AG9g-o5$r=MRS`t-'
    'e0#`9r7IpZse6@$(7!xPSlt^vWy!?Wb=zKKOa)tMdVze)_}bckkc+^kor0ef~Nj#)^b-'
    'e0cx*hfl{fI2+LH>C=H7pLQw7{pAbZ?4Kt|Owpw~=!e&z_V=^3n|=*mI5_$@uj9=1#}yX!>G79vGG{YC8S~Q*3k`~_@X3^)XYXm@'
    'ejUQ|6i3T{xivg}(;vSc3};gk=Wo%`>|ck&AS};uEy=Xa{@06*E?=Ir*?aobLZf(oe`G&k5VP4@%9v*t7Fwstj(`5!)6?clmo1ds'
    ')ThY@dl)TDTn4?s$Fl%DF#JRwJvw9Y)3eXKz|@7GMyKxiL(}#Dby`~UcAA^xWAka7{6>A__-'
    's9mr}k1$zk!o={99+T&i^l&k)@tLnXF~Uo&3Na8$FH0ZI({1wvqkZw4;N1I!z1yec~{IGhZJ<&o|QK*~dEyooY{iB+rXi5plFm&y'
    'CLB{JD4U-|ydi`st7R`%mxQzx%hjhXVgjy%h96N~hVu$Cx}|wh%|V{CM|yz7EH$HvD&Z-'
    ')`pi_WVe3=^s9ojdox}Tj0*3`7jpgcs`tlOMDY=cx&yT94)gPiO5HvuC>!;FmS=Wy}$c#eghnL>BvbsdG93-=7rDsxQ%{CgZq6?-'
    'Lj6tKhxkkKE<+6o1H-0)I(v%;W?~#WubP`GawF4Jg)r^)$?2Cp=mhZm4^T#;fkXKyfFGi9UsLBCUK-S#yH7gJjEDJO)7{@7%C-'
    'wW^`{BhD&S~EY^_GqVdV+so7+Ml`juG!ihf>{gCfo-'
    '~X!`ah%ZO3W25a@rO9GXsE{#E@G>vZ#eUcXQ8j&WeoG{nJx01x9X@l&Ocm7cs*=!W+q~J^K=UzNyh-daf<eqzxwEb42so=%vs)ok'
    'CO#@((;M7V3^K}Iv*RFRqQw!i@+!T3GO&C*3BT(hBXJLa0l6L4f<*R)#Dqe=b3mHGdMguP7fdU^inaNZeJ>B^dQZl6F-'
    '|ulIiS<j0cl*$Frk2eF2u6sM!ISHZrNblNH(6bmoj>Ti5}JN12z=^5$X$O(t*j(fQmJ9hr^$Ma+?g?##w?XY92*tr&`CI&ZJO2U&'
    'W&rIT3Sw}0sR+Fk)lK*T4XIgPb1uovhs!zgW>e_P}32CmrtrE+g)?3li<c2)J&CcpkN0rz*GCOhi+_a8sqzkc|`{{H?i&)CvSfJn'
    '0`?r^0j@L_z<IF#f+9PFkfF9I;;;k3v~uMkR$%r1jv*64J0c;D1^&6a%;Ku<&mKVCoL{xKl;d?U&wWazl#5|RUP>NaHzf`yLyjFd'
    '3uJb@{(;AT6~NR}gYdU|WoU0r((6jh{z?GE7_WK!b~3!^X#MhBgT1LncVOqL#}y%6B>U-'
    'h5PVM}lr8fpF|0kMjcwO!ho8lo6oEqv)PntU9M<PCYruo;KdI<TFWVg4if_8N7_Pofdzszy&_;F??uiUgt|N`eeU`y*;qoL@fPPO'
    '_I$;L%*jIX$^e62?0^37U8Gd>c<}`|SB=z8d=M^vh~<jtf1|H?%UPbV&h*p>I(zV3ff;JWwv^gSnc=C(6}iBTVM@^zhp1A@U%CuZ'
    'N}=VMO-y))+qxh92<>ij!G-_6QL?M~}|EFL}{lja>A~?O7+-'
    '67w!LL%BnPAblkgi8kiyj|!gnC)(!u02#vA%Y1?@9?PUkU#YK6_{s^m1!(5W48kI6pVdKGBk;&+ZFl;JY~S6ze=4|zzK4$#vNxbf'
    '$m0M~JnZ=|U#_IL7kN={`2W+nS?e6<(Llg8%}7YB=mxISI;FoHst3^?N{lMfbHdZm@XeuC>hb0WjNXzU>6J3$RVsMusB~GC$mLE;'
    'tT~gQgY(Y6fY-=OeLh%HoR;wx&bIkus%18@e4xhS8%QdsgDZaj%-'
    '21>Aj0)KFzSN{jR5;l1x)hz=~fk^JaIflK#|j7(#T1pw<Iukxm+y2zkr32%{e`yXDI}{q+q*t$PaPVq=|s<sq!LfQUe)Mkd@(*&{'
    'IUDos>b0A#;Ajr3hJh%59*g9T8lNkk1AG6Q;{D<+01JS#Kc4^|D=?Zh;Jg>bGU>n>LE?`dzJpnO)H5!LIqLAjdOF&RW09vJ?KVY)'
    '836K;=IjZ^4=KRB}4NRT`gr{NZ?&&F=A$Lg~Yk$d{acz!w;eA4-^M_65BGB)?8VHO|^F!bXpM$Y9-'
    'M!1FR_Oic`gyH2JknFLxl4wZJYSaKdz*6%u+jDf*GK#it2`WfABu<lP1e?XKsOYaylGr!4%`O)#yh#!1xsd}8ubT3t=(Yg_q!x$d'
    'i?AhCQf3h-'
    'l0E|K3OXO?v?Bl4f9k%pQvCYX(kCrV>vcE~p>O`Fd`d}Oa$W!I8V&cUPIL>+AEsMMtsTTtj)_QF3(_gLk9uM)xb99&AP!)i^+_%w'
    '8>V2ajJ-TF(Aj~g;n#CHF?PN^XT`pHawI>$zUUKC{=2|7d@%QiE|M}NYkcTAU<B{#-'
    'mjWIq^yz6NwY0HQ#Eq1bf$jjSp@x)d9$X@`tOu>N5dwdJ4KPwLT<IxG?kM_<Cx3UQM!U`~xCX7``098QQ3{`!FhvXLPalm0R6Ifd'
    'hys))>`)@xU@TKFb(RdnxV&GZ;grle)z}dMNmk_Km}w>xNyKKsH48<Q<)SqpblIl-'
    'T%6!ENW|6vFpe$(3j}y^FreHQ;v6VL+o&4aJo-v1(%+t2+tffI*Kmlv2-fd307RNm+{D+W1iGVf7#9{yW8rjalm5uA=5jC@`J-'
    '1&822H<#zZQcPmH>RJv|&IGMgpUSe>Q5jU8-'
    '}l^xLBW5>iai<Sk)Gyn#g`lV!}FPh1|!Ji$E%DP!3GphBI&o2DmNIqvbTrIRnE)vKO!UL+vuQltI*P@5Wsz$P9#3#am1xNwtk<s;'
    '&zzrHx0%UZtRK$q;pIDvS8YN3oo$^6iS)b#e+{tWIUOS>l6meZ5)eJ6Lfa`FGcfOET|CZ_mlYBLDvyRrvh`D>Wn#s;w!xA)~UucQ'
    'JxijXgIZz`ob6viA9dm5Ja#15pL8s1yS(FIR#+o9jbu*iUKX`2^exa%N-P2E=%fR!=-'
    'SByH8dFVx25Ddl!Pl@9OqnWb`1k;O02W7!Du#5)z!dnjVlr7v8b1R8um(tHZhX!xNr=e)C3x_ot!wBZMRR<9l341grO6-'
    'zDP;9lrcTXffHLbU|4|DoD8-dST~@%F=w5iU>(YL&9v9HTzbt0hmrVC=7Yke$(Zry^fETplPM0|2c+;Z(@))}?@J9T-'
    'NkfIJK^imdDr5#}T2G#kn$UMRnd~euBa378U#;mw6ha=3KI4M5`RbIe#_5BUBb<E}XKN!aGBCp=V}(7N<D>xYEz866btz3P7-'
    '5_fl+9uZd9WIt`DA`S8m^)`qn~C1CQqD{r=G++!NfnYP7a^XC^5(9CBhrwTfy7KJmT~}px;Fr_ml)PUtIQP>#cukBdG*1IFO|c*?'
    'ahTmfqzSz}|4Rer$DPK|>`FD@y%<d&?N`ZsKo3;f=f@chnc$KK2OBG8@CLMv(E%Ex?_M^o^b>FyGwWeJBeU0Vf^2SS<0Bn9eLC)H'
    'x!-'
    'LeT(+MYLI?lEloVn?Mv#$cdSe*r5!4Os*9Z!x4Ngtc9)DNy|>j==^P!X4QEkKN+%eUkrS!RafAjAY_Z!qAbs(&{guy43rcqvEtrg'
    '8{jY|UpkX5G10W8oPT2V{=l#n8JiLT7{n??ZMnP0f?U|(4}in>8xiO0g^Ja67ETj(LRK4_fPE;8Uo|wn)|(EV!vt3oUm2xy1;f7w'
    'Kn2kwlW0zAk5PdSh&vsKXIMh0lB$zLWksOP#3C#2_YLyL%wh4~h|@LHK8zX_xBUz>@;xb@XcWKEJ{z|^x?OiGaMH<3**r)CDdUzj'
    'Ur>L;=KJum@eSdpAz>gR-'
    'n+6cmwjB%Pm2Tej^>7~{8%<nat%bs5Cbpl+=;PbYF@1cX?5_VInu)6T2lHFW={&~<iSbHt{T!`4&|NbSrLLqI)SW}Xr~W@JSk8KB'
    'j?DZfLu@C4H+gt&yCJ@OLtGs_rEg9<`sk9vD1Nq>oquCoPE8<N((`hPm22;qNSqLy<>sQj^b~~KDXL<FWk@@9^(F9r&Y3@mUHyck'
    '#1U$DzsYfJs;S&29ja)|GacR#S(cVxP}m`r#-'
    'kCQdFopQ{<7G7blPSdII!v(ur*DaG@xDU8rcq;5#BHoW~WLNG#vUuDOJ0K27x;zM)W$z=FL@H~pCjADPl5r$wpqnsYlBfS$a2tRr'
    'TX_?g_oraH$dp!2Ga6#zI|B>~RGki>Z(njXI@WjU!rj#8YbxwK~U)u(rcut7X3K~kBg$c!#rS!OO~AtHn1R8=e@=Xh5bG0ythxHJ'
    '8Xgl&d8#YmHF*ZM4gS7-'
    'D|6c3kOv0VwTxIZWZ54a%vzL!CTw4&8<@7A}o?V~Rb0(OJ2D{z~u?VxB6ObMiMz*VyArS<eTXT0w;JFqbzR+<6%Dl+(bs2^*q$02'
    'DmWp7kH!>~4Ic>9mKUP4#aRl4b%GKxc!mne9oi@L-'
    'vNL!~Ti3*N$+Gch;XlA5g$xOPOl=ZYKEN+J^P#ro>r{Kma7o_+s#zduZPR{ZT&d=Yn^!$SHGUc;zNdTU?FP2;^qhd}~mYKYaQLH<'
    'Cdk!aEdhrDtK7iFh**2lO&Jfb3ZV-UfnNtoOn>x>b<wO@I2iZ~AVo5}PRnq(Lx>yjxOUIGX8uiJIR#`;XnAA}Ki{*Kk`F|*eMJx-'
    '+N?vJ2y5HZ&fR${m4ek5y%cUuffo@B*S>_$0N%aJ(`u%mw1{b6FLXDKOE8@{;HN4ABxupQIS}kyTR@E9jTd#!=RBj%Kk*J`CSN{d'
    'uX~HxJ0_l{`&5ziwE<dHnQAq%j&h#ZOZc1lNhkuV%Aa#OMTI9`RK^4zzy8v;EIWH^~$*(ZQcp(8eJe}YcJEWZ=US?c6*_OZ>=TCT'
    'nn%!1?E}cZbvQ(1M$Q2bWDuSgXZU-`IMq?W0w6$BmwL}h%k=)er-Ttof)>^jjD!FmbAReMGmB#H`9;J6g0%EQ0DX&SwS4$uO<w_l'
    ')4X+8Np;iEs*fC*W+Zs^(7qS47`);4tkQW51)@_9<TC3TpAx<sFw1vVOL48<OLCg`4vf|D<(u$w|nA6rd=VKi*Msr>RwjvPMYlg*'
    '*=7=zZC*sKvVPw>*A>&^U)M3m=x>ju*u>a~(^l6sp)-)#;83X*z%F2w}J}{M7o(Mr4-'
    '!~&WxdxaJDOjcni=#i9*Z0kM*SF$=;wH(&@&W-'
    'FcI`~_Wkwrs!`gn^+YDjLTmh0NZ&6l1GAPIQI_)HG^1YWWI~lf5)|e#L>T#Tq653451X*R~sF6wm(k!mqbeqOotr9V|xoyn=nG)t'
    'gZ*X^8@QGPSyB;fdw><z#FPCTMW?j%Xa0>1%or6JCV4&!p<?1VkWR=IhTKxuqKy-_P4v|$ipFLrdB*_OQ6W1*Sf!62I(h#fZl%b)'
    ';;g{n0WK=)iA1Rl$63T$Q@Or_HQ@cu7IK5j%-=g!6(voYkG8A0D)bb~`ls9-4odIDbc>oTus#B6+9n`B*8UpPsNxK`CcL7-'
    '!dgSn)BIou4JqQ4dK=n}-KrP?34SCN%yP8y^;%!95RfU{<{!YT7hU?@vU+|?4c$RMNtq(WrA~yqyUX?%2#^-'
    'U**!_{6ys+V@`Y3>poJi|cp#lmUO$I%vU)jZxMv5+u)mFB!T%1C&hw|ve#$^2%wGr^1=YzgGKifI+i+_w%-'
    'W1@DR|U`zh1X|z6{uWk&*OsDdTs(FXp|QuSDkc}u`*>vuc=AekU*7plX`1y!(ePt;vjA5ke*tG6k#hb!W2y?(!>rdoX~DrvNz&}j'
    '$c8y!RcV)H+i3`@ZDhaBw{v29!2^$IMwGP(r2=QRIXnfQ3+uZZ^G_ED58~v$H<<9ZbKyzR^Q|t{Q*Lt;In=M4!0}Hjpfr(xsaIE0'
    'HlLN%3<uJR*ep7xeT{S6Q5&zkgqFS!fYEyNglL&fhIL>()d1BrWKWxd6dr^I7Ya|Ul^gK5orWT2ZL1YfF+<k##JMwh~1BKuW&r)O'
    'eI$RZQy8F@`%Mb=G_3OrnVUcsZ@KG=tpMpn#l6)2en!=F#60!LZLTu!{@yqrmo0Vp`RsNrsRgYXa()5q0Qko7r?)2b*#135^IDvl'
    'c#i5Gj4GA<a9Mz3{)xiur>eEqmP)i>X9>)U4P&*4a$U7ROxaaO>cyZpWS$_t|AE5tz%w>KU>EgK}9-'
    'jZZWf%9@cr5rkMH!=jxO6JjQ8A{~dqu1eBbO!*~JNpwp0)vXUo5(BOJoA(h~%OsijfAjkn!wuQEp_5Lb_bPbz%c|g{BZ2}UERjcx'
    'n#FN|KOCbu&Pk<_vtOCa+oMer+7S@j-8Vg(tgLi`8Cq4A)c{?Ir2-9=9OfHw2WV+XF`X-'
    '{mddgvCp#xJ_LcmObhuM%6Q+NS&#~SDeNVLZ{X9-'
    '|RHYr31tTolS0o2O`c+!`){bOK_+R7EWL%XQ~liD{`x^sN4C2nDAHyhM?LARhmMoZIzr-ym4k5k4NJrUB6y%zNhOb`KrrI|_Y+yz'
    '?F0N<1i!4$&Lr=%&10WCu;qujC?7m=bR<Pc0pAB_c|A^2|hLV7fItpZpnkrGH7v1v-'
    '0D#%d!X<<qp@{v_SZ)iC%A|3UxSCTg>IMn?OYZ_RTg%K}fdZW{D%on@0$QSJ+fTiAjJzhxz0Q?JFTS&Xr#ve>Q+}Xfv$HEt;1v9Y'
    '221-FzUjb6SCt!s;FDU3OO&Z6DKITB(P2-1lFU;Qp4RH%Yh{{GlJRAXxsL{c?+MeaZPx4?xRXSdPNchYw$BZg<-'
    'Qc%6>WGVa<wJWX-DLCm7XVE}`8bseWY<HdrX2dt-1A^YQ_<~m${__DvMZImu*wy|22`7(Za59LGZ&8GswO@-<-'
    '7f8X0xyfjx&chhs$f$BNZu}5UO<QP??Qaq?U~x95N!Ij=XG@mUfdjRSG|sYs_o5ES5G5^M_5`tU5^b{al3&jTfx16L5G_;E-'
    '^Pl~wjZGsAOUEh$S!TZrX7Dgz8T-8Ay-tz|H=uAx(KE@$w=-'
    's;$BrF=Z+iv`j(jRR6KO(nW2KFxa7%_%TX#%fH`ocwg)joM>eLl$WtuS!T3%@S#D$E$(}g1!_;`z8x*jHhe`IO1KkV{Fe5e$pP&C'
    'Rfoe#AG<2e2`EjD&SyFM?W))ZK-cjv7}1@9TxOG8*T${S*lX!9}{HB^h~%y2xn%{UPdW26Cb4{*ee*zw!{e}_ygc2fZ{-'
    '_0%>eS(HR8IV{(ldYYDq8h0$=;CZDneuoyzB^X{Z?Hf3eTa(zLPi&E_%oz(i~v8V7%o5kzIdKz#nLBZfbX8dX%*qD@3+6f&RglZg'
    '+d@*;r0p$foW;RzXi!7Z6+nKv>5x+AdLUN{cy>$U5-'
    'afV@L4cbFc5(D;a$K^$A5`|3v5a}4J}cH}?}8pTgZkg*q0?z4Ku<@KHxUX54c*{U7Xe-nMJ0`iY>E?kS-8)(tq#kW@-'
    'QcxSHZ>is3{&Y08sHy2)jNx{2H}6F%kzy1;yqCtC(s-%=}#Hl)S2IvZhsoad+k%DAB-'
    '4*Zxl11fCD2qUIVGIf%pu%7Q!w2TzvsFDx`YMAsxMXST|G7D{*m`%foW_tdf#%`7EZau&J7mGHi*<}pG)I8TJd5gh4Rqb@Vli;jU'
    'Nbp}i&HvR2!7N7;}D4T3e%~{%Cm0>RuWEm4l+4efYaJVQb|AC)fCwJt-'
    'etGsa@Ww3qjgtwh4G_kXS)RX@?O8CzTqJdZ@CL2#KwH*Lf$z;a*}||w_-hp{kP1H{L)WNY3=#KDfq`DJh3JnrOD=)Sf9+H}8)9fq'
    'e&?!K%EqdL!4*yfOKVDOSCu5Or7p<QzLMD#W7)E8(~=yh`jFYZ+W|lh)Xx91ezZ2LkR`N@?DZ8Bbuww=oE*XI8G{*g!}^+&PFLuf'
    'u`AA}^Fya!2s<uhYQ#YI2lt@BNGPw$6{+w9i^KWf$5T)&kMBNK%GK^0q@k5!p-'
    'e_ca<xH(w$}_zDbO9fO1NAFg}ENp)?!@SBpX8~4j>s~*H3X#pVhk1o!r+AOIao&cOtMzr}NuNYgIM%Wc{ANRxh4{@(-'
    'xJ$`wzX9zmS-DiM=^L@kt^mIfjCh*uV14%RxI*&QNWBagH(=u|&=fj{Z!#;6+0Ins8XBWiyLRY)uSZe}1!JjlQUQXs&GT<4Zd1Ay'
    'BIOJCK>Utn^YnT@MKQ8-muzeNR$U?<<KF@o^LqW-nU_20hxlUDBH!7ju9?dE*6o{IvamO#by4dN^JDOQ{H<ATjCxFI_Pn^8nfHZ{'
    'k<jf!<y%J|piSjgVl)Exfy<rVMm@;Hla2qVqvWcJMJ9)qStdV7WXe%cJyZ0>NJ9H(h?7=dc}z_*Uwm6@8|;SC6@MXUZ_8~2{q<qM'
    'qxhaoDxrdm<X3*0D;VbK;XCvHP_G}zZkRU}&M=E<2sFG^O8ktr$>JG;Uv0j(>@>lp0{dqMhDpVPLnV3eJGFn}lno@eN6Ly|gXCCT'
    'p557_ZVN*i7yYqUsa2iA#Oi*(Z#eK|~`&zCVFtqjCqR&`U9cFCtO?q;ub#xN(Prhn^5+p78fXV8AB6uOXT`^<Pe`Iocg!>bqN#mF'
    '2id9!m6WKGMn43wbd8gUj3b7oT!-'
    'DNa!2~9@`mDZbVnvsE^5~Nuvqc6Z^iF9Lx%uZZGi*oI>x1rxq^@<_liYAo)(YQQ@8`xs(LvV^{pH090;C88Q&ZX3-'
    '+F*<gkU7`!RcM-$37H64nWj|B%cSE?J9gw+3TN;`Tc1iP^#Dz2FS8y9q-K9AHw2?1+#DwG1;SK|ss{&j(N-'
    '%9(UdLwf$_?z>SH7s1|M7S7!|!|?KlUvC$$0^M*$G|JhX96^-YBlgU!XJ0WmLi9-vcaV^c}GTFQ4&>|K?B`3Ax67tV>x=`ZmmqS-'
    '|5#X{_t>l)G6#^!v80i6CBGef@fb&l7+(r^P^t97!o<MPYyJQ>l$BgD<NknvuYT5lrx7Jwa(e^UZYY=P$&lF8*nnJlyZk`PLjH=}'
    'qRLeizuQ~7#m+=R2kxD>G-NOTQSNfmI8^E7tSwwbB-MWAEuu2($|;Q0Bp5dr=(lDFRr_V%%(TM7dS<^=i_5dIEcFXY=15!1u88ww'
    '7Y>wxkg+JdS{wydh6)(|TVt*f?98+S|JE@o*(6V6I8vx7RAIuy*vHLxe2Qc`|^%W#_Wz%DR#h`7>HhXBUh(Q|D4O37<QOLlw3hGe'
    'j1)LyP#7&Q}AvKoM%d`BNMp@J2Z3>LIXAjijGG}Ov1ZkJpUYT<;_>kvFdtuOQIYCY)_c1<bukK5a(XljX_Mdy~CluqH~C_Gpk5=q'
    '}#jmB!GZ3umGXx_AR+CIosW?os>XCXgA2PI8y<|))-'
    '20>7$ce^*S=lJB3Qu8ZMjm02}VXT>4uQ~oHZmNpSP;CQCZzwWJ+EhKS$uVu5EFhOIeI?AH;)vY*9;9o1jg<$hRo}kQN@RY%F0No}'
    'C3|uKl?rr0D}o%keJZcP(mSk;vPpFyx}i&yBNe0%^P5op(a!DMmSt}9E(T_8woyD|cQt6`0$J9F+<x+1&f~*vRnM993l}W`L0i2u'
    'l%>&NKo2)D6jkF~Xnc{Tm@V;}qVTPw<%c9%teCCV%%CT(S(mS{tNST^f%vHn>j|Jkkn*v%Cuca8QABj(c>2*cH^}|TQU9)#^m8az'
    'rdo;91JTL+4zAVoTbdkBWwa6d<5#E~cl1rtCd3{!KE9t5NfaeyRLgQpNpObFbyPh;wnrRm49j(^j`O3hNK)EW#gL_uR8JH3$~AMD'
    'T;`<9D5Ds&K-oBsb59AlOdU8}#lO)VX%(xD1`QyfhxJ+U2UZ?cD|-'
    'g^VKFBnU|&~uZFIa|KaTWR9%}S#F<2r3!MP)`UhvG{U12)O&Ft6DtMDv~_^s4yonFe~u+pN*3_WRcO^9@>C=PLa5_u*+e|@K9#VV'
    'fE8Z;%TXVeJJ6C$zdj&rnWARdedof5xdy2ONLftP}o2XtDWY}UPEEGVlV&u)g}(B8mHSUGl4s~uihzr>Qcvyh?^T&1G*Y(KF&r~I'
    '(Qxt#0v78n84_;Nu|NVL~&SNu_~zrv11#aIO^nePK$4k=N}ET7Dp_LO#jNJF2?JX97M+)Ygu%1za_GZhD%F9t^>Z`e(18%wqBexO'
    '{aXP}W~a#>YCiD=_Y(t#j63UzX7jtVC{7jufNDj^0IqE;uYtXgs$l{~gGL9j`_W3?8A+6*uOnViiS<Yx(QlCzMBq1A{SULlbxWCT'
    'JKektf-rDm!JqHCem5sW*E;R*c8_Vlq<sc1}Q@uC35Y(&h#7MBDLeDhV03I}R$qLnb{hg9mY<4_zgbjGZDAzO!c`OZEWFtYiE$|W'
    '2P$vYzR|F<L=WhdS=XQen%D7syxrU`s!D$(N$+tXCAsaQcjMtc%<*#kbuANy}CDP$G-'
    'XJKWDZzr3}6!@5BMcmF|zAh07xc`WK*s@fcL8Q^ubuoHla3RWr??q;-k%@x#Dq1G7&-'
    'EHsS+}*<Feg!?zHQrgEpts9;VOw4C5vQe4%ID{>usQ8f^cxMHjTzsbbRo$NAkTzn@?M^Ge&xtLMJzcdiQ~ysmd)MytX49o;N6c9^'
    'JJ*U&auvsW%BX`&f&h6BwaaOW4WW8}*)0gO$K>{7&@?j#pNn@R7o!!vC>^%t+tj^qoXSl7xo*>nFZ~eP|v{fR@2piawrE6UJ@#`g'
    'C>Q6R<}8H+u98pe>eSKV{n|eT5NblYN+A=gTBR&6T4$P|Yf`su_JT<&wy4RRy-'
    'jE&2u$D7%F@D-C54(nd#v5f1M11h3q5hRt>*Q9Ut1Ba6(^)?tw8*9i(RrykOv-XGvoQUn&Ysw2r)JrT1wR%l5A4ESw4<6i0lkW*P'
    '&{UMzA;*i7=f`#DEJpJXBjy`YGPN}OEys7E}M}Kp?f3CdHgbXjOlHv8uKAgA;%MiA*d4B`cK*e*sFw3dcxOp7H2_R5PcZ5P0n<WH'
    '3+6-d2KnQuzsnA-KNxg9YDEAVeZd&l*jpi)Gm4|o5jt|W{OLqLo0wsCQZ$K=%mOEGWP=Ry{+G>y-'
    '|2_21?1IwK>o`7otX=~;@LcEZFx`jQg06ptR^KpC;-'
    '(O3J`lwNFRt+;vAi@zV~e$_2zpQyGCdt82uf9e+&l|zX#x}5$(S25tr=0sNCsD-'
    '|GLeWz!^G>U9Ssl+WfQw;*=piXD3?DUKwV}TBI4t<e=#lcw9Bzl6nQvXt_^c6eTDz;hLV^?}3W4Q9N|3a%6TjYy#0_$_qT;J-'
    'dR`3#g*XUn+T}xY1%WMEihaTyFO#))?9!31hWVF<4Z~5|5x(dz*62joZmpH4dVMI?mDQ@S1c_Ubj`X!(ozqT8DDYZ~X_SLx<BC=&'
    '@j%6z{W@EILH%^{#K8l>P;{9=t@r)e1?|fbms?z4ibgCueU74o6!}MURa9YRX<yiQ*-f-'
    '?rI&ULBh)3Vw)Dp>62O^w1MvRXCmasa;@6<$bUQ7Tr1??M(VmcQ7^-+5=1#Blz~W+UbQo9DgUV7a8BP6vXUt*R`rak(*ed-'
    '<9u$h}DV`DtK#TAt8LPgZF%+F_z=#3R{WNjM8|jR!D<npJRZgv2L^M!S2C`8uzHuUQ$6~)^pHPHSKD5Yn0B+MKLA(V#UivbAX}mb'
    'n`t|j#amwqtYS4h+g50MT9tb>(?)?hw5}tvE(h%CSLR)+NA^ITmg$qNk!u=JrOFU%C1@_mtG#ADoT*!atn7k`b_f%EiZt3p+@6UQ'
    'y7in0~CJSl`553=v;fVQre!5$xKaZ*^$xSLMjo>8+X#~xo_|9KF~{Wlc1>ULK@2JyQ>`!Q8rP+Og8Iw4+_z$5&!mSqK#OKtcAlQE'
    'huPkz`?ncI>p<n3MMJ06Aq!CN$iZ?6dQs+>`OacXnh)07dMsCG6r>0y=xl@U<|+~3r}nj+CLcF@pCeYGN4-'
    '^CwXw6wuZ!{9fs1ZhiJ02cR;sRT=hUYMoGB8KzgCO!{xWE*G{w*ZHyKn0<+?d8lNDxQLi%v!AcL%<0y|m04<34Ax|AFcxc=7Y9DG'
    '_dK{Lep>X`PG2mUn=ZIr=#$^q;qM&r+6i@UdG|3OgZc^uKVl--h{QKko1NatMW&'
)
)).decode("utf-8"))
_V58_SMOOTHIE_ROUTE = json.loads(zlib.decompress(base64.b85decode(
(
    'c-rM%(QX_`a{L!Q^I?Y^Qj*`a(wtW~?Q%g$H#jeZ#R5LVfN_3U`_1sbTUwGm-JOvUk=ZreJ@`okHSDRb%BsqYjEwy0e=h#*mtX(>'
    'w_h**>8FbyUw`;;@%i%N-+%effBmm7zxeXw-'
    '+%e_KmPXLUw{7J%lSutxV!)OUG~|ZF24Qr*Pnm9zkB=X&Bu$&i{p2P*I)j<`F#2CKOYW<x2IpfSpE9@!~44*E-'
    'rUhUw{AIyZgh1`@`3Vy#C?c_pjf7dCZ%;<HhAw`1ObH4u>DV{>SQtj)xB)=kN1nHr~DY^QRx5p0xY=q{k1PUVrwh^~aYJ^5O9Q{p'
    'po=`rA+6Fg^Hj=)2_rPCtG7>D~LcKYv-okDtCyh_NDJ96!E){lmv;4Hg4hJ$*i~>1mg8++V)n&Eav9#1vh+gFe3gc(`A!-'
    'TZ6t!oktMc^zl2Kd!K-50AfulewDt*_a=G7&Iud!Y5OHoV|yI`)vr1QyeY-'
    'd~106rayf>7#33!=Wpm}4zI&u5SC|JOEPV%zdGCK^5t2~-ovK`jpFhBk^O){tY&MJF|RHxv`(`f|M-'
    '6oPg^ftwor0YpC%vdVYD!D8T0~AX90L%_=!Av>x{)uuRe2zsS7`Cow~;l&Da08X=%;dX>O*+=F>L&jrzvzv-'
    'L2Z+DkqB22R%Wf1Sx%{w<l2QO}=E*4S|;Kd{F}Pa|=grIV{|<ghmF=%AiX(}I7WI85No*N4#KjWm1qbVs36?cqPk^Ws%R9IexHqq'
    'Dbu?%n(Mhc_R8{?p<9<Gc6o{$=f<!2hRS3i^xEY4+q}%pR~>h{-NL+<jWF!*tb#KZp12_1fMZA1N;Vr%z?0-'
    '7um(aA(nc7>hKW52xW0-^3f<m3B}j%PdDC^3kVj?Q|JzxZvL2-'
    '~G6}0j6EL<s_ZG_lSde@Hrp1(I04Vf9$Cn>nQwx8eGSx82hx<3A9f=6m}dgVZ9p*wUeF!acJUk?T4tI-'
    '?9!(!}+c}1P}>V93|j|(I@KoC{8emBdsyUNe<&F#&Bv<L2SZMDd{t#d$TZHVzXeeHW@7%pM0L0O*UBh^1vgU`BTvk`R?`oU(|@>g'
    'ib32mdeK;;>@C<P9q#*tEX>Rc*U#GSMM^0`Sr{edCq%v)J*da*AZS1dz_hxSl&9_!bj3E0C1e5z2&bydLV;hH6pXfTkvtRKu=me@'
    'fHlzIji$=O|yy}Cu0bF;-BD-'
    '6Jy;BGHqCMa0+*j?be{5)?dAS1NA%;?_vgrXUFN`!=7I%#?$Rf1&to0IdtOZx{_pCT#@l$a_)F`6sIr1auYQ>0MkY$wRf^28=KFZ'
    'acm1a0P!gEGFskTjG)QnZGCh;cST3$+WjKtNJDq#+H_~^wL7gCie@@*uf7Ladc38RSl_pQ==$1T0ZKr`Coi1F+85Xh^fbdLZJd8w'
    '<L(Bo*x_8cw*@<<@2lNZeYM%Izf8dW-N)IEdi?!|kN2;S-'
    'yZJo|N4k6odZN#O>u`SMS&0Fd$vPK{=>m;O7bEAW8Rz=+36KRX_3`sFlLQTXNUJqZP#q<ivW5eI{5MW5%-'
    'S)xyy|xmyn_3j!Q@m#JSs)F$e}7^%*H)oAU&w#DbgcL?c;_)amK1MR#@WHBeNM61KYu=OB|Be;ACy42%vs4+qSHEi+kqoc2P1$A8'
    'm*I)^R6VQ8fJM*?CMCu=|2nc74#x*2@wFq(WEjpPk^$*>iN)jF`9mtp=R`t}-i$WNjX<f=wbWZ;@y3yK7yAxeS_Mf)RaRh(Zw-cG'
    'WYQsB{C$T>Z^O%leNoCM7~dc2Kiw!L`%!dF9|oqt(v&T*j!`i54flrAa2F!U`728=S8PY;v}dNfyadZJuSHo|0XPY<uH9wHAS_<G'
    'ayB8<qM-Wubl!O$aKL2)um&)z}=&(Wi$_a!g-n=Kc8ktXfCH)WnPz~-'
    'X6)&x)B2;m_Pa;9{QB>+tC+gOklzfyjtdU1h*tMH`^Mv~tegA^YloB1WxzcB)x<K5jCgV}xKQNeQv=#mo&C?qirq0EVX{GTtk$=i'
    '#(9yk0w%{#=kI=yvd3q=NV_L&aKNe2q5V9`bbxu2CwHh9oU#FAFpks1~>LRkDu{k}`GghP<+IJWr#ALkZDV`#n;0Ji`itm{OeRmW'
    'nI_?!3=Dc7uY{ybH*@`{~U{|d{Tllm1e3f)@4LNX7DyBoKtuEEL6yXOzzh>gIFd!<nZSr9{tr)V)HN;7!qwF5E%4rq<cEx!}x#Ut'
    'Nj9cfBJB1f>(1->><=J*~~xjdsORtPX420J-'
    'w(MVFpHef=O7EjgUWx=eEABZPZ*4DjsDSp6M;gP3XT~@X`!j@!yrhk>A1RCb{ILpFlSe>N==kwL)0w94`0?b@@$^0_og-'
    'd_MJo@bcwuKXmT1ZAHT|@A%3~8XrC-'
    'pUe=EL!SNoud<pKPHS1L>5!uzF*43iyWU0+{}9`T+#!o0&23>ypc0`rzpY6^M)j4d#9(b|14p#J@Jee-'
    'nG!9($|6jz@!(0qMs8<;w7M2El+-P5ZXNr=-$BxzRZKg+`HxW^(3leO0K?S-LR-ya12_eo54#sNLsEA!dXj**Lk!S@X0}9dcBy1M'
    '7#JqE5&}kx(GBgWo+Rtq)y8Z~kBozFKPM?^@vVf>QMrUzgSZuWfI$MWHKOdD2#OUNgMSO8Jd^vxi#r_8n19f)iIKa+4PaAsGSw5C'
    'zJ?fWwH2^N^=|N6iCB|BeyOU~fuuxX&PU1qKokm<^Q|-'
    'Q;U0k$Hmxqy47j$5m&rEa^#ODpD$40z;n8{O{kr|MSJ=Ee?3V(VS;3F2O_jbumrn!{>Kb1ZU?uygOTmmr0QjwcSeyP%)>((vEP`3'
    'cx=Ed4p9HbR~1iG#AwX2!OqSuh>2iciQaa#M%S$MqMr-_EUC#wN8lpk*Y2NP^q)-'
    'CtI#7L8N8J(;LB)jnY74<#5k_8=(c7S%a(Csg;l!Hs}yiG|&tmhtx0u(1YD?B0BQbGzhM=h$q&&=uk-'
    'v`igjt3=MF!GElYa|9Yx5!0~0$Ca{8kbIB~?1dz-Sy0Ar(RSpsOZOj?w06k?*6_yYjWX0l33`N!yjjb5ZQlA2g3h$_GcCX5tveY1'
    '(L<EV#O;IfuDoLf%nN&#($}{lm(XT$2^`K;mop7(GO-K(fyEbdPP=?lWymX@eA-YCe_{@IZ6^7d2;6TB*>6}zGG_r)#Mo@vVDo+}'
    '=RTiM51hti(2C|7H_aTX)*-'
    'c*vB9|28eTir(Nzsyy>kfLwY1sQS&T<+w>SYT9E|=l@=>Cm?g5~w9+9{#_OcRxMi}VcXB1YO~yudq}DrMo2Qph+;1yrS-'
    '!(@3%&(e(w1LcDnS_WViI}Q_*E>Ln-'
    '1FW3XTN<))M5N*wOrB}7Rpwm^Y;^ZPrBWPhMGkPXG_mGCi+yR;S0Q|X*|h^GcIK5}av&OwC0m)IRf;B#gWtfEsECI8|5~MRgeo&j'
    'Z5j$|-K2MPMA=t3+H#j%OHd}nY9mUb*;!W$t!E-Pw-cJ8fm}%-V{i2wa#P@Jmf>66uHWKu)=+nljibyX@)~-'
    'vp><R5hcoq&8a|j|>HM+eZ-_<|)QeRdp2G_-2aDcN7J&74CXVnjjkRtDv+i#yc~rinJr)`pETvy?_ig>BR@35|s0xJ&ECS}r6<P-'
    'fr7M!wlH?8${xkerv#7T-'
    ')g&P}9}5uIUR;0Bv4p?e)})gW+9%5c|L4@JC;b+@d1NG0Fdl%_3!n3eR`k%h`xbx(m{#=k`HcHCJ&%w4^iyJk?w|o~$Dhbvi_oQR'
    'e0k6L@c57;y4U$!1bd8Ez1p{nRY7D3Mn$U4=O3fc+IkDN*KSi$M$|`PL~GXi4csp&ZY2=6bu5dCOd_l{?vm-'
    'V4+Y6@?$$Ac*D({VK0jdG#jLfMM^pu{P^gH=TG#dG%g_>4G>ZlpZyUE`Z}>0LDstmec(yu`?nnaK%L=a^)sv??P0Yw$#DtL8*Z38'
    'I;@n_*ba8MA4f)}$Eod;u%5zRyE-*7v)i@Wsn6FczU21OAY`;b;_f?d+Wv}s;TjM~4L5r-'
    '7C_zNFRr`R<hH>@a8Q*#E2_(pQK|};W;7<m2b4LCNi1Z@?#YJ{@18}U9Qdy^~1f|#@YNo4{N?OQm<(!a`ekF;7Top<{b>632{SU5'
    'esos<P+9J(V<iM^ga$vrsnY!+I39I6iLq1EP*wskvJKb!VL{Lqtr?6b(_K2EgfJmIGvz+%O&d+Vd?6z#Q!Xg|G#Y%=^!n*Lrwu+P'
    'ln7D}6!K%M+br_K+9O;;w8luy+def?GV*W64gbvEp2Mm_PST(*Fmx5iz%b2QlH}<JFiYw%bvw;?C(PN-'
    '+e;N9++JRG_hF02JLSriPfN_y+9tB89#En%qy8^QqxjAbsP7thm6VLJ+zH~>1LA`zV&s9xLpK0VCVTgDn`plL9wyeQ}H?^GC$GaA'
    '^G&zDp2Ea(l7$VgxvRhy|?cq67B{-'
    '+kmkFtN3KF?p1yn1iv84Sf;yDhCxQVjVm5kZ?^#ce=&qx8Hjh>Cp30XxFA=bDMiQx+nI2ZOhU<{yGaMWWLL~NC{Kk%lfM^gq>B$9'
    'jUBNmyoRkK(Lw#)$OHxvdv-'
    '1m%*)a*kQZ3?(!?80APAGL8rSx%M!6C|fv0~_ArLz$6%8&yR7MWldA%T=cVW>g#vXzo%tt*H8u6dr5#m!_hzq6U(-'
    'A^`x>>Ik0y*$htQi&#|RLkg-'
    'k`vKK^)szy5yC*li7QE<_v&jJ%6R&8a0Cry~{|C?(VvXGPo^FS&QipMrs<dr`1f5~9r3q#H3R;qoi%HbJUm>?_G(gBcS?&>{iH7Y'
    'vy7y^--4r$?8(}K;AQBn9JiJdY>xICY+OXTGb2(Zy;>@)pg_xt#v~EbO$QmE3o_E#4l3LBk-'
    'e3*DmS*rh36%hykVH|6vB?3W;?(#+bx^QWSMsDN$U}fyP?nSS)YQ8vOf=0BqAgDPQmAZ53p1)KK}C*ug^W!LtR(cK3DDAIH`ic}b'
    'yu)fMEggspD2LwW_EklU7GBZLmJuCuBLhUuINSLae%xB*YV)Uob@c1X6dQ^%CJeLQh$eBmxD@eqj_h<@~-'
    'Az!9J<D(zYq2`hTRAoG5amO$~b7d|MQdYMyWj)-'
    '&28&cc({fu?D0R;gD8n>L#$S?&^%x!!t#8SfQOT%Lco{6Iq#XM<iU<@8~=@gRFU0FH<(0x<Y|)EOnPBpGp93o$|$1Z*dLejIcIiN'
    'f(ftBa6hM-=I2{fNjs7Va&Og5@B5o>Lh%VGLNXAck5kimr_@vIozYDh_9=T|5va_CxSa^2Max1U*waDR07Squ2ML-COKsg$zaovu'
    'PS0<Sp}(j;ns6MtLA8sEhkKx=lr&(vHu;m-'
    '|)btH`;WHxk)ER*>RfCg^!F8Qt`8KzOlC^55e8Ja*%Oaj3NQO7GH>1A%r%*sdhiPZ~+gCV-'
    'q)PoHWVHSu}ON`Sg`*X$Uvp52|rbY`1Yyee;fX@gGF7<GjU@?~sOei+zITeHC=s6!8*-V@{ceycE^dGySv<p`O|YW%L5(93-'
    '3<>6Z>NYSV{bqMGRlL|3f_fjX&k}mU>><&evw=$;vZuETr!dt^QV!L5bc1aqhNG=5v2p%D3!LS^UlTIbuI<uR%(<M1BN|1PRZtAl'
    '0(z}}S`V^d_fQIHK){^gNO4+h4tu^J9cVPr49bXmVO@CErCUN^m5p;wR_l>U=NZPkJx&0vt{7Rc+r#r@8WE;#%OJ~FTWo;ltjyGT'
    'gQl>9RV{bZgeT0&MdVMabAe?6AR~;kca+E&V@+lxBU;>b}`EAHmQY5r2{Mb=Cy{YsrV0~Hrs-'
    ';Ct{ZdZ|6Oo%egh_LBsN5_2BO8PlJ_aW^J*7tY84?PR{&KQo;5kGK7QkC=>yyF25YA#(IY!Ue4Balzw7{VW!Y8?-'
    'h}O#>C3>|7mPK3h&zjeV)f%{x469kaQ9*zwlX5YdR|V~e#jg=U4*;D2dX=@xI-)7NX?mZTyuF^Bo|wVDX|_M*tC61At#Td-'
    'L6wj>R*n$uyTyHnB}sEz0f=l&EKqd_V&7fV1F02)Z)Qk{si<^*Ge;$)tm0u;>)_1VOtaoSbq{A^EzCqWUgGzfAeM-'
    '=@T#K7G@#0*3~X5rb4$SifwB?yu}p;AWG`Xxc#<quY4Am|MG>%BWmjH){$nCI@RAq(A5v6c@70=*Ew?DJMyf?26rsr>tLW*juabJ'
    '-APc}DVH{{IACA^^U2pmgA+L?lol=;g8xOAL=oOH<hnnLqUB8y@qSN|sd#Ny$9`U=5ki8+_S=8ow1bui;K{*Z(x0boaBun5+t@ee'
    '>iQE-%E-~>*qKm*3o!V(?P+h%5QRcx917ACqh`Z4(s%BUo5Fux`VJDcXG~n*Rq>QC;K*ovG<Ey*OWGR5HbAXRlM4;%1bkC_14-'
    '5zo7_h_lq$QGva(~1l>2FjD&i%iKJIIt~tR?)}u_o#cl9-'
    '<$5JT+;34KaVN`=xGsge^DjW}+`xg(EtlrM@yemWdMo7fCI?r|{Yaqqrq$X3K#+D#;M3<F+fd7Z{y6U;ylL^MMW-'
    '2qs#$RV<sZ?|((6$~?CMn<bgC|#VqN@Z+51B}&_xLVtt-ZWi#7AOK@D|QX0+zinNsX;qC*{JXt@f>pP*9kcLjRi7e5FPSLSTWLUE'
    'K=yjTB3=N@y7HM4lUxhT9T5T%Q1SJ(MP40!(*~7(<X0azn&b8yHSkZm|qn;g3946NsTTn{yWWXs1d_x4FYvS&CzuO0Z5PnfEo$A1'
    'l_tkYzK-{AX<?*)*w33^lKL;6?te+M<FC#VJf>eM2M6S&JzegqSHL1cL5he{ia{$6zzN-'
    '4&$g6Y;I>yx0_7Y?3(9xa~CDvSl|@zZd;}*4y*#FDFC=*v%N|T`kOv*j?zdF4x}nHcqW|v$|gG6I_QpsuObM3L+zW<TeW$*lUxgf'
    'NXX{V@a#7gw1=5LFHS7v$5vlLSpb)c7jSH{8;_`<TrmibhhdFHDCS0vf2RYGz;qhPlr9B~4I};rh8eUYov&QKfTX_3WOHaM6MS}h'
    'EG!o+`^F(4-'
    'KwG~3p6ob+YuRA4K9dB|HFunctA=7M>v=gyqf2!Zen5g(cxPh4}~8HHq(R#JjD^(j}&}<<qI{(=BKdPNdm&y_4VKO&kL6{t*cUQt'
    '&=3J&otFnp?%>b7bGVJNN38G!58r<^+Lo4jq;ea(brHd5!Z_nHk!`>9!`t3#p$#h_929aQqG+FyCbs4yq>ugXJ;O6=sHoV+fmleH'
    '!zN>h4CF7TklT1#))~iRc4BL@6VDyp5zu7A;ytPY4$d3cCew03E+Un)n~r<($=+=X+WLdw>Vd7Nug6!U%w;wAUO@0*fyA>v3{p;D'
    'TSV!j9uYo`&elj+lq=iL%5z`6hPlGjZgIft}^kJI|>J*fS7XG-'
    'P?@1LF6|nf&{7yo126+4r<XLn3f9J9=h`#87SGztUZoUA+q*~rgk7h-'
    '<#z(CfTF8AsGLAMP)iu50_Tk85yp;3h?PpgEPM)!zELgDN|k?P$nw4D20bHsEnl<>xkw!FpVnr*&>iau78f5=jkap++ig?6awJ9i'
    '-^eQL<lOJe!9NJ5cyAueoP6Q2QkUOAWAEE@q7|pA{qR;lF54$(4jD;C{|{a1Ey$GN!2HYB?iPrOTb!?Z4e{=KAGx?7J{NdTJY7}0'
    'G+;w%p#ENZ#~`a<5HrMt;d9rAa<cLpBC=<3Rj7hn;AuXX2z`;ZM#sL!~4Oz8AJ|PqC~N<a0+#oV2*Mo+Rr}ptXq&|l+9oyjcG+gY'
    '?FySx70<sgdk1*AGAdm<c_EyjK}w*K(lSb+c_7BE%=!X3Qso8dj(^46@H;X$L1^RL_L6}U@9phE-s36TR~cCsw3c6(N&39OQ-'
    '2@I)Ti)V^j;tAPeY=tNRj3Q`ZI9f=bU=FJz-Jt#w!{&V)j`BFeI0`d)1SUS>~7A(x=wx2!h0`bScd5ppTFT6To@^10QpjiS*k)?q'
    '&m!toeHiO(O8RMwn@2={g{8w#caZ!t?4N7o_^VA=z8<w)!X5H4!a9C}TRvJ>Yi{AZw&3=Ojr)(Hl8yb4?wu!#go$%1FHt)eX`F!Q'
    '{|nB8M}k}&BDQqyn9V?|~BEt;)>Z@9*0R>|Ub<UHo8mrYVLId=ses~Z4z_oZ{l0AQCg{7{5tPb*d(r*trF(D-'
    ';e?MD3s&^b#xZy{9SOau-MBpbWUPV1IbIs}DmCkig0x|uEQr#6_zPi&_2XNj<M3T#c39jU>r0KpL3T;cnOFp_1U=n8YNlN0t{RJ@'
    '^vlQvA?J-dEDg(yFb)GbB1*d++l<jDb=WG?=aygYE$bW^|vZvu3e(K<CueOYBAsHRGv|G~so3R?sGjobFmO{FMEh$-'
    '9@MRYNwPK%5htS5`v1eAv(0?l4eurE`jXVFY2IeP!FJRGz4)81<+w6}#=N_ft0jLwWxmq@!f9XAN009Xu-'
    'QS?8~Wq;AYc>`s8=#PKQp&M|&%k~8{j-idR3|Hpyk!fQ9gcXQGmq|+$nn#<R{sQ~~zrv@0AiL0!7_YwD)_4a@qgnMwx-D-IdjVO*'
    'wdIRsGH}*)RfbVHKqffaIW6c<>@))yI?R+fM{M}QsFkhKP=m@#sQuvUMlgbqS8&Nyw^+v}hf0$l->UY?YN;CSw@fp<s-'
    'E6NOoL{^(<X4zs-+N0a9V~O-~R2Sj~q@MaI^d`dm5(pJ(R2d@PnVRryRcSdY9x?Wda&h+Y1D!;DZAk9xC=sH+e%-'
    'mv){)VlU1si7g{NOd+oi#J{Lm7+BdxugL3azcUD!+*$+-'
    'hg*X|)%>2+;K{9aq*x?Q*>9vcC}Kro!F*S$)k&y?2d!F3ZE%?wN`gR|Lt0@+UcbZWfyH&u4E<j+JK~#kZn4(^q<JNad45+tVCrCY'
    'ly$*I3*gQ<lxqaLf)(f!&AS{YDPcJHblaDzu07dZ5CdB2=8fbPrE9xY^N!*=8+(`5OR11U>8qJFq;2$6a}7rv@*4f+N0Dm`wGdu3'
    'l%&RagxRQDIMR5hso{uVK7!SBQ6|o-pv(>tL1{BT)Jt<fY$t}HlicB>Ga@JB?krm}d1-'
    'J=7457M@5_Ej>FEfUgUtyW#cDC3qq22M^$VQgOoFP_ZtX>JzNvUhsh1O@Y^0&!00~f4J*SvCHa=w2Mz%_QIOR!@%s`&7>?&00%!&'
    '_HqEQMc2hpzt7^$OB#`=y_ptDZR9i#l|vRGU4$*D8tnv|QkW(6*hp})PMk5TN?6=^Pl&nEQ9xiTd&IHy(9wIfQq+X;|_;kB&hmYH'
    'E_Fy>N{Ug?r33fxE|6JntJfLIm4Z)~ANey|Zj0<ak?b-'
    'ov9BX6=f73bfe=xKL$T^vXg;d~oVrUh%TJmjMZ?_@6q5MV=7&Jn(GRA1_?x={i$<r|ZRpd1KtM?4@`B2pn*)Sq41Bi_hqGOhykr_'
    '<CI(kWs`MyKD)Cbh(3A<Q=i&`!xc==3+Lj?(D^Og0O{P}l{NChRhX^2i3S=h;g%9m{oB(u-'
    'HsCmY)=f@y{7NqRm=9s&`(D5dH}BdoAvP_`rW%)rhW#Ykk`Sja9Bg$JcgVi3&4W)NKv{mo!O3E+e%F9ZnNX!{knPUPqjZRi#@BI{'
    '`XMwJ|lG*vw{B|}uoNTcby=X-'
    '}uj9)9qlBz^4CdVz$PDWE=DkmjuX%dleP%&r@LRX9G_@z?4&E!sK7siBT1w&Uz{eqj>MO60feF|`s7;Lzt2P$zif>ajfjAh3hD#^'
    'rrVRPOlQ$p5A4u-7xVA%W#Iw5CWv_0D=bwq}YH6Zsm?Xv0lBY!9XK1Ka!P8cc;P1RrppFqV$&!&oeTj-iy{ofF|J})FBBywXADIh'
    'MEDkjxmis|GeEQNprcVlME4^f68b+5<v`eWHKuQ(u%^WkOd+Mhzc(Kz1C05;`mX<WG9GJ#;9ki4xFc#g$H|G0NcNkp?-'
    'Rn$p=)R3<_BQU$Zc;wM*2qm;HStNkm)Cfbw4U|dPZ%F4Ok>;b#s^E&6?8W0w>-4l`-@r~QU;b9_p%E&jlqbhp-'
    '7;v^(U;ra)rsns<Z8uM^RVrlJHQ}RA$;731=0b7IKX9wws;TNO5$CrLoJ9#m6ej)S<2bN=p=_kU14xnbc4hYFGA5kP0xig=UB}r+'
    'uS+BYU~~vu)BeCNjCrnUA!cR(grWwXr)Tg907}1e^WJ_gUuk?Ni!XF?sPNwCpDYG4P<A4Q2^@qw!Vo~t}hDO%8W#cTtV86JZ;t8B'
    'ikqxvc{h!$Y~}R{R|u-uh028IYO_VuNcgf;VD#uZDa`TwiSRK4JicR#q(60*|gjvJb*z1vM}lWO#}6a1+;WlSn-vSF;w|9aNp~c?'
    '3a(;-'
    '<h3DeMueO@tZKl>@Mb72|+MsyyjCug_L*vrM!AurNAxHaH&mC_weId>s%uU8foKRrG?n8(uiJ`#Z~e|YR!Oa)3!3y7fbFd+C@%0v'
    'So+SgEwptK*``5Av0j^rcN6WNxj)~&$NLADn-'
    '=J2~0M9QK@+|*e+^&cjUfdxre_se4Lu>bw<<@)B_n}4jaB7!U8W!a`k$0_#!Qavo|qzs;x-'
    '0!dk(kbENpn$Eq@S$(i7Ep3AP7JPoCp)3lg_b!o1D1v=eYl#2+-OM;3^^#m0|$f_bJc1tH3?RJF@a1kOn4J2QH<7n-'
    'WXims2m3Kb4Z6Lt|$}}u5wwg8oGjwpi5zb7f$w5;%(CfFyfS6;Z%-'
    'lb(O`OVuVHo<d@~HO4S@4|Q%Sl%#j<STHkZUOyx|`pyT3rm&Ty^xJ^KRHUwa5~eR(o<B7+BRpjH<#0VWu)#P0D>8J?Fb?9i#?!jY'
    '4B80mnzLo*CTM)R*w>m-Vt&h?ii{kCTa@-KYwU8${XFp`h4{P!fgI@eV{A4M@5KR8pbx<tWGDr1PZ_N88v}oO-W>h6RFom{-'
    ';3n$`D1xpiG0b|itIp~8C>Cp^kJ%&1mmA2wh^W?M_gW4AjK3ry*b*_+r%e|LNO6s|&R+u|eLK4Vx$h$bcI{<I*eo*TlJkhO2DNaq'
    '!*emb`bJ17`Dmyv}`x(OE^I_8Rnh3HWf7*_T3g22tbe>ix3*Jw2%t+qtLU{7y|`u~)CQF26lc7t!^itdaAeRJ4?wP`AmF-XdX=m{'
    'ee@Kk2DR2cPSVyyo&<&`*uaePMn!Vm8`zJOcNdi0YsAs6zEaHG3eM_Q}1VdY7EJzhrHAl^QFL|waNcWvGZ)G;ejOAy8p;{cOqUA{'
    'A9L+LZN?sgh_J5r^ZLqhUmLNW)(0StD~B4Byw#p;Bt?EY!sh|$WT$)QS^71_dCs#C=`MP-Ry;W|)_uPSa#vctAT3$`XLAwsiLx72'
    '~0bv=U_OX@-wBSX8^-'
    '^{x*^0}{^ZPhjQPWn}BbMv{RBd<<rxL){=@>Og@REPt_`#Q>wBgEmR#bpu$p=kn<sArl#;vt?utx?`mDj}w5Nh2$6>AEb%%(oVax'
    'In9cs!$xV)~Y+#TrOUJ+<A6ojr)gW%JETZiuAm%T$9qj^^+_aSPyeN1vx6iRYXVNv37#ca#-9r61xVq(+|{vtGuZz^HXhZo^&-'
    'L^)`uuajOcaBJcOi)Q({s4-@EMfiCBO{1(*o6j_Y0k-'
    '4l<X>>i(ogyl+4jJSMS%5y@#G1U_i%MxuUit_k2B&h;k_&5dLPU)Oir7)$n~U={D^8<0h0dDN9aEOxEy>zN>s6{FEI9RGwI@Fz(3'
    'HOY^zQxJpWod5CV9q-'
    'wSsNN5E3o7*F}20k@jtZd7R!@g<yA9XKCafi97TPDu@H|>GfMCF|;U%t57un+C^H>O#CKVG|DmjM}7)b2z02!2J!RkHdmqH)XYV*'
    '+wvAxSr~Y3tt4sfEHdvcMhpL0OvZ&B^s;8BASt2+TOfv2W}lSONkW1*d6X2yj~SDuHeR2W5q81p+T!ZmyzIKeqnHa}rk5u;4YJsY'
    'U+k8<S27#oE>VdThQV-bz$m^NLPhaq&#1(doI)0Ws7f8LPPM(q^2mOcngf9|08s^Vm~$d4%xB!slS-'
    '^AVG#BIT82ZP47(alVpW9o;`d}s5DhB-H%cpb;OJ=C#=+20aBDSgi%p-+9nJ=8RhASEAah9cSDi7jdxbX-HH#^l<ASHlB;>8iCsd'
    '&YJ+U=Y;;Pb9Q8d#~Yz|FlZxu<?hDwSYh=Rm4>sno8ZdbBPgGihfM(4NNrmiotwSz1Z-'
    'He<S>g@%%6Q{hoq+ZVxu5JMLK25g8Vuh9af2A|FjaqJ2_7#ny-oKTbC5@l~q~rHOB}1-YDx9UpMo3FOU5%kA_;SC-'
    '2qsHow=NZlDv_1g$R}aI%X%FmLern#4Ezc-$uO@bHu42eIo)@%9h$ODhQQ0H(k}xsa<us}M6;4GPFx&je-'
    '9s`*@7#O;JUJ#@by;d)Q078k*1fK5Q!7lOhkgffNf3Pr}w=v1m&H8Gf!9puyy&$T<4=W?OS^D_CH9BE%4}<_t{sw`uu-zu$n;'
)
)).decode("utf-8"))
_V58_CLONE_ROUTE = json.loads(zlib.decompress(base64.b85decode(
(
    'c-rM%U2hyoa{MoRo(IhrN%@T{%~`^6mjWf-;JhFf3-}BJ#`$6GH^cwkl4dy5(-'
    '|2NncZCN!A~MaWKUIfR#j$XWaQ8PbM<e({`U93{dV<FKVN;g`}pzdX>s-'
    'Mzy9aH{@0fezWn(2Uw`|Lzy0^upZ|9;{MDZx9zVUye)s3AA3p!}mk*B*Z$H2JbhWtJzuVn?`FH!YIQ-AY-'
    'R|xA<D1dPKkn`ye!5yLS6@GW_x^Er<^J&XA$LE$|MBkr%VXX=?5`H9@bSlYyWNMc|1p}-'
    'e)sXya6VsF<NcdIfBx|Nq~+Hq9e?RO{lQ1$U%y<CkGuQ(^OTqR+t1%{dhl`R%gX_rfBNC``}?=Qe0hnVK7U;h<Bf!Ie7L{+>C@>Q'
    'TnuRR^x?oxPg}@wfBAwpyW=8>C0e+H-rs%NJ&xYp@N4jkgQI_Q7gw%7uJBS1k6*yW9IgCd%!eOl8WefMXH!0|-'
    'r>c48^UpkqvgNcJ3N2WpS~Up7fTY?Z`RT5?!sXZUeD=Wl4TqH)r*ZTe?1qgclfQDMsb`!vL7&r(Q3_Q%%ckny{EyBKmOn0Y2#Oyy'
    '(qb<&x;TCFnTfZHRu<7It#!9!%yVVQ&%kh_ULzBVClk7Q<v`eOT+j7ZCP6Dc3zv)WAkMje4@T_`f44<Q=8P`6S!EX|LZK)<=>JOn'
    'd|w3#hQ2A$q($Y(bGuWX6fW=8`+IbJ36T6)3o5<Ck_)h^YtNgypaaaKHX91R6G19d0xDVh@*9WZglp>&waSR-'
    '@W<t%b#|SpWffU|Ch0c0{@?SDd;asr`fZQF?hh}MV##N<HP6idpKRS;m_fHyB^!y@sZ-vfBvm(v=c_O0q!hX591}B&WH1GiErW!Z'
    '>1fSlVz485&7uzwRXM?CR}iDA0Iwk-'
    'T<dvI^`rC%zKW5dFFFIZlgcY;QrW4H?O1c|7ma?pJLvpjZUCV>Y=dX@DkSBTBx1$42VM$k83|f_57A`Xd2FU<spDbxZ)@QFN{7>$'
    '47C2NgQd7F)nf#Pcep5iwa^BhDu4F8Qq(O;S!q#FKd#~qVdV+snukIm6Hb^;lQ7Ye#pDK$G@l%#|1sTA@Hhv{2{I^8tQ3;v)JnS8'
    '!o)!QRu688N>W~W{W)MjXG*h>kr=}ydE|<GZV4Aak_<%q+<Z!I7NHQfBWcx42so=%thXUkCO#@((;M7V3^K}Iv;DARqQw!v%n|*3'
    'GO&C*3BT(hBXJLa0l6L4f<*P)zddn&ol8ZW^j0RoE|>x;iY0c-M&=N=s}u8Cw|tIB-'
    '6ze84o7sj%P=4IsulOsM!HnHnOO_lNH(6aOI3+Ti5}JN12z=^5$X$O%`wJqw}>ZIx=hbi<lz~-I=xN&e-'
    'qn{Kil;)0w^c9%Sk9mQG@Q-~OTNYkLJK0TG{k;WXC1z<xo`D~!^{`L{LhZs3aTUMlx?!H((sYTK%>Hu(6<0z5u^8tka!=N~^k-'
    'tB+bJwE>Rh%LPYh%{Q_4p)i-'
    'AIA4ghm!n<gWZ(mMF7S;IW4l(ZwRGDMwh`n@92DXc;D1^&E}m5peLe(AHP51{xKl;awE!D$k1`eB_s#p&~3^X1T!7=87X0!^8}W}'
    'f}8C`BY7RE)6;tw-'
    'M4GM14R`nVY`!X4zj56hnZ2B8KZ;F!vXVP%1V|Vr@av1@o)Q2=ddL>42?AZoPb!x$=b~AOiiK~ZD+o87)?HoM)HQdWY~zqY8}|lW'
    'SIYmzP&~r@{?!;xvJ3<8Mr3j1w{hU5G6r|qWuxIDy}adZztJHDe!15<eHw{CJE!6oCM7~I^M<u+rD`Ig|CKwclc$sHOGY>=o?y@Q'
    'u;~(hM{j!FkqCye14#Op?mXfo}MV*CL3Y0w&#b}-'
    'X0<kBKUgJ@*<4LUfvqxr@_!8UO{m&OV6G{1kcf<OYciw^xG*Hy>fe23AV(%i}j@3p+S(|ibSG~x%#7mC;pkXc{xCaF!nN^V2j5xs'
    'nS>KYZFd60k;6ne4asAMD2?@C~E{BIj!wZpOEc`hx<dpE%ZHnq>#;kCLvD)Nb#`a|9rWU-'
    'd^QJz2WbNYqQch&Xa+FYnqXeSkVo9Ppg#v@?1TL_E2I}k)9KthK6qrwNj5aK4A2g1WB)y8Lv{oLr0~{szfe#T4K$a1Rb1r`~|#5X'
    '6W<5lH#<Cw{W(NA5$%}iRA+|7T<)Vf;zb3_m6zt(*zN&-'
    '+@v0A~XW*LlrQ|<EL9yjPk_s6ahs}&x=M*8oecfxy#qZ^7}Jb7}=b|BYKoVz^@c+*ADq1zBOqg;CrgPh?>+uh7@FFxFqxx5osr75'
    'M#)kAF&W2D^IyisA)$87bE0z!T*HmGEaHz{O_zckmCEYU7K!!41?-'
    '7W$l|bitqYet%8~BpwEL{^JPJfXONt=KFYEa{ztZ>+##UypH8>n$ayL`9pEaB&prKcy2?iP_>@BF=O>XbIsbq!Fd9FUFw^V{dILy'
    '4PC_-#+AzXKkA28s-DJSyGH6Uq41~K*rYKniS~m`rcCuJ<98}itI+~1u!9YNbhB*2K-'
    'ELytpCtZ(C~uVBF=A$ZlL_;q<EIfn__ev}aWd0gs7#}EBg}^}?A`3y+xP!$W$FMJgT9x@*W}s9slImD(kI0>CqF&4Y-'
    'y1FO=4Cj>MYO);}AfeDu)#lFLr|Coaf!L$a|K0F+gFh$M!z`)tdM85N~>pZt**+0<g*bKAK6rZ#1Mw=PVM0`6W=ZSc9^ijOnV&<t'
    'nK5#Dd-hS6*bURRSFU`2POS-'
    '$Fqil7wH6Y#+ZA@U)<Zr;*gs+D;KSQcecC1FVJ`QmT2dKxSDFT5BT&{s0?bq+qzxQ<mIO^cm0o?nsSxm0fTRTE}VXcoR_ypI9(O3'
    '+XQ(jRaIYLH`p4D0A4MM7F_LhF<C@8HRCrzed9;nRTkMBLb4Vk+Wl_nM@=Rn+4Y_6j7Fo-'
    'T|S@Hs$By0;fSDwg!N4bO~4>z>9+c<-QQ-'
    'KpEOb)zJFMS5lGw_So8n1`4@`lh}*k{hbGZNHdC?cxOtWI~s@a#e!uloK9`hAKBGh4kjai^r{KtK1A4<NM-YdQJ1i%hr>i>v!oiU'
    'v(&e-'
    'gDtYM1Dbp6n3!hKvf!8oz(7;Klx*}xGub!ztK(5w*Ry0swSMx&h5w!8bFL>>3(b;?1oDIMfGYB9D|O2v$Scuo8TE;<VAIYSGdZK+'
    '7L92EGQL<YV#NLjX6L3x%aU}be2`Y==QJpHF&ov_jxZ8MUFS$QgUc3RI~?X6zsTUV&a=cMYmJ<(lf5!}?#``gvh&xl5Y1;9T9R<?'
    'iusxj)C|mwm#<;R+#B$^s2QfvQ)j^}VuWX7O{vtnnGJ#<{B9|Vp$Yii^G}}4!2ije@o|e9Q&WJ3YG4V$*RVuPnJ{X2`T&6d7Dr1f'
    'CaIHwCGg3`WU=Nneg*|#C6LbA_{>?77Li>{@ZhI5u%U+(&Gh-HVyUW@ri2W<kX2ooYBlQ##93GWk6KtkFRmQ$vNG00{lZ&am;AeZ'
    'nn4YJQOvXVlfJXWsV}M*yAb408nsSILEb(UbP*Vz&1!z>gyz1+B4{C6pcIvZG0-'
    'xvBjkW(7plx(^b?Ik6vMz<P!CwOxoip^XS9Qw=Qn(ka*FZ)<FTOI%}p+BE6D{LIfuF(G+HjE8J>w4heo{DYPfu0;P)cgPUs__*&L'
    '@Kxhu}{bYN)l2b8xHobTZ%M=yxasxWr+U1+E*?Fh#SsZHZt9GeE=+H5^?6&T*$Nu%PmAg4NiqhgYV{9mlX4kQUYX7HEj55UcEnxq'
    'FPUc57=+L3qjj^c#N4u>u$L5FFxs-'
    '5$K$!G)=_d1(2`t!>Q<1TAmjCFt68nw<Ny??JKZeQwb85$Qtr=xqBop^v*Q3dYFqB5T0@8V7*Iy^p2(Fn+ZWjUE}Pt!o{p-'
    'C!Bfd*rxB+kDcrx5S)Y>!Nka{^!*uo^-'
    '^Bl*GkgrOj7C*@o~R}!3*Q^cj%_JIIj<jSen8aE#~+I`X_D~;h~lk{|ns7>5c4cnxp>)@lq7JBpW@S(^)=^84R_%hv-'
    '<r>#kFP9BLu+@5IbSU+yw=Th94wOsECM}B`cB>*{oABjw&Dis?Nb4)9JmJf-'
    'O|xR`B*`S|_}JW9>5IT4mUKy$bD_iA**Vx$JL>kSP%cudy)O7Kyr|ceo*^zBh!^72LA<~Rfj!ZYcTvzrWrjC_I2$*NG|5Od=IuUx'
    'c~>S*2)>M_WqAiKUzx1DZ5%|gy;%g?U%oq9A7nHkE5W4&StzsZ8)BpHx?~eld`+$q(T<FzV(bG-XHeL-Xk2uBi~Jt66qVU0Q9Mr-'
    'BRk(|YGh^^B4ed4Gb-Vs89A+25UnSgH?v?CKNYTb?Jxmjxl0A>;#dHKmys~SRnaquqCI;A5kq5Rs;q-'
    's3MCC$7ALj3phsKa&FX?RIL#0jq-'
    '$@_8o=2LB6;Mc_#Cf@zc?ax*OhZ2;u`=5vz0jsBaHbPuYq5FU8tH>Xb3@rJf_hU2?jYh3lf?|tzk+to7?Ze=)oia#<Jk>Mnl4TV>'
    'I`=VC7$jeJ~p2$}Z4{EDFN#zc$)hq7}Og_SXe^K%NOEQTV#ro;6<g=i^Io8^Q8|*^b{J9sDA!dWvE>T3iwKq4FA+LtQu8m!JP|gt'
    '+%boTU$exc!rQqO*3NfK1ImgI2Hf`Ayagf(r%cuPm(CvOnxF;!h1F(l|7~s6oYDgbvQa8#?}8&2U&xdcg-rWNIlv0YS=`$@#s5xh'
    'Ailx^)ILhG3mQ<A`Y>JtB*|?jv~Bnigh!o$i-'
    'R8!zr@SU6f~8E=`Kya&FiB)Z91AB<Yv&S7{^JV&&kb*m84fi@04r+GX>7V7;_Sm_iRLyU-'
    '>@O^$G%uD*oZR^<EP21i;lF|+kV~B1jI-'
    'r`Dn;EPSZ5P?()&qn{C%L9_Vg>TCV`LOAZZQSo_4m_n*t*?e7n8clVyc7L`)Qx+H!!&<@<SS5lbC3m@LE<)KN|Q2o}XAK<ZQGYp;'
    'Au1`^Xm-Ba=pf3s37#Bo25D(1Pse2$^)s8kj%sN?qrS#+nowBbGq5MCMTzSTU7mfJ};y1#-h-'
    '&)AP?(<O!2V<A3f)m|%u_R@eXVVM@KH^pZKBNmiUcmNMuvFCAg4^z&RMd|9DTa`^?vdmmd;*9kiuP<xCdoGRa)lg`lnjmS&Z$~Aa'
    'h=Wm~(C#9}T97Z7@r628QQc}?Gk{CUVdGr&n%lL+99dA}nB=Npk|fUrFH<HX(C8yXoi`5zjYSbJZjey3iR>uC!!P)q%ZjR@FDFV1'
    'W7G~Z%n_x<OH-jow58)XshtMjq0J<Bp*!5rk>3<j-'
    'LJnxsvE}Rs4xX4a8ZhxM;@je<Fcc_fn$jst7+cz>=IKP^RWbw`DIPmIGw1{@xUQV(mXpLfx^VcczSjz|M^ew33}5Pyu-'
    '#R0;LZ8D3eyBqx2?T_Qx;NS3^NPhJjdhT}g}Mc}Wu3Cg#l~WTGiKypBac)C%YXNkr3Z4bqW!_#BG85gBNSeKdK_ZOfO4D7E_QQg='
    'OzOr@0d*|pQC^NJuZad-'
    'K6bO1QjVnvkFiT1ZIW0$hJTycLg(I2|p8eR456TN2(^Dr9h_3V|#We|5Ynguj1m8nb<oRw#J3nsgnX0jCxgbr9R5oh&u&%B<lS~<'
    '%&<Bbl^9CBgKu(O2<(HimBfo?=FTD5-'
    '~h}Ft@!MsSZ+MPJ9Xy~9=t4*KP#IH*bveRCeD%Z|3{U&%&KoJVZxIze)%NK_TAd0aqr1}L-9@4lCHObYSiGNT25-!DBxTm6-'
    'VqN0@x{~%~Z71B<24`UMY`?`et4jC<L7ON;qdDmtagLAyFGB=LT1Bp=`4oQAL-'
    '3)qby!WG{SvVBSIzF|!_}#EOt2;@n)bz)nog9$AH?4VRtOv#o=6m%k6ylb%VkEHC*jzhLn9@@FVQ#~l!2JFE652F5QpSAVs(^pHP'
    'tg~IQO}xR=POdB8wYH_XamGA{q2iiU(m+P&GivuBk-'
    'D%IKL4E#=VD%bi%er=l6l0SY!hSmU9cD8q*pv#7S%DH_oA4J`Mrg_!LC2G|nVyiN;-#FWUo@b1ivCtp;iXzF-'
    ')@pjCBv;8oIy6y*ulug2935nt;yP^&wzHtcbiJ2&LpcbgZy^1vwD_R&9dSvmS8O1~v6Ho1|O__Q$Ojm%CQ|!1Z$OSNdE0_ga)sm!'
    '=HAp-C)4Eyc`PXSrY5_6z3YX#n9}<v~Y4-g!4v3>^3mov!jPgT_-'
    'l|9O<6OSdgm%bG(QwkS(<q2@3oJn>9CyAlpcB@sq>#uUT_YG>pr-yEGn8qfA<l)In@&W$uw4;vk^PpX-'
    'HYCO0jGHmWotJW!BXxE?ovak);NPmD7~gqS28WRyM<F=6`>4%7{*Y(E=1PCA`KCggb*v!a&r8RNA4&swtAfwDyYgRAPqac-UJd^0'
    'lpaXeiNhNWUvd(>C%e;_B%|aAM{_xM+5NVjG}@1$l-'
    '!B*u{tPfUd<3H|&`L#jJb1uzWk7r+YBn25alBz{Cq_Mvz_H8Ps1<HrX48C$oF2s*M`F6PoVHRf$=%c7t4SGi2?kxOi@A*w+Ojbsa'
    'F~t<rpMjAP!;OelpKG6WgJ7j6~*e80|A&WFD=>Pmw~%apWPt1Gsb7&VU0!CQ3GX(1(yLgCE>)PaYO0q8z52U^bC+n*8?zq#`WjdW'
    '(|X-|=zPs=$7h5MLb-SA1(+y{#4Q_zq9#QI?!5uSxgxbjvef8b&tR$LIve@3-U9m$Re_y8B}1_!k5-'
    'n<sWNa$i}dU}s<$hvIsy+(m6e{3FwH(o3__9jRUZ$WLcA}jh1o`=P6E-'
    'yl<F(WDB<l{)BwqQ|8r@1Y`y?`$widpb5{8@w#)bFVmG?Csp7a0tLB<scIrIgK0fh^#c!~w&Kr-dj4)Q*rN8N7Df8IIn-'
    'p1flqWWeURG_OXZfnvUJG~WV=vm}#Gt<VX6%St+|C=Q)1tUnewi>J1Sk0`gTuOh^VhO3E>Dz!~Y1s|)jdz_MWWvE+HU~#Y#LYOoy'
    '7G%8zP15Jdki&nUV`3TCDhgUu=~JeVazQ1QNh$4}2B3M*keb3W7&AWKXk{%B=4e(6x~ZpirJpkbbgpSC7*nmd8i9{EmHM&)o(Y#l'
    'W^}=XTq8$Jkjq;OK6{0?a~TVWo7vJ$$|t3ic>PTsby$fBfgNqJVWtYCRwY-'
    '89GwzKvw51a5y>A0u<2A<A*e5fbZV6p5yu%+LWq{MX0zF-h6S!Luqi-g23e3Ayp!>FBv8o2q<3i=PD$-'
    'Bls1i6e`lSoIF905@TIp_t8xysQ0z@Ji9(LZ0iDxHP}oS7i2*8%mA;$SqJmcNb()i0`rfL_(uq|pkvoWnkUCIWsw{kJEM`#ea^VT'
    'nHtk%Qo2vnpPH*q<3NtVff_a*%z|v)tte?i_c6|$FF0{L1T4JM@NNwJ;mZwDRye_z0HwDS0$-'
    '1Rft(+;qs%>E=eY1&CLFiKT6zA(@Oh|Ig^)?2lAyMLTVK+>;0=VchZ3F_w%ySDBwUs<#Uf#}rQ?Mpov^P5ki5=OS+d`Jt=U|9h)9'
    'ijop~#Z)Q&29u(LAwfS}W8h`;eH0!q46f76P_0FAA=Eg@3ikKgZ$2s~H+Q<+HJBjVq!vr6ow`=qC~xaLh)F`YP8|b83xx>P2A9j='
    'V_Wk=Kd+!@^O4OzmP)jBI2{3~y^oUalwGw4xAR561o=<TPUrsV*6G)0#vCo!Bq20_+aq+u{$=0W}jsg$Ufs;wN$))zq-;B~-'
    'Ty)KzF*B9XRg7IKmg)BCeqWm`xea7}qc%Ul;r4zQRU$5s=!8*lM3Q2=o7wp_IeRXH!p7XmEO8E7=|s%9;?zYaq)q=8rBW=dPPDNG'
    'Em@u>Pfvm)UGUVsV2d1T`Ili2xg<F%YubW^De1CDNmlZOujfgS9$qDjg2sS*XRp)o9u_YN%{m@IvdO$uDhDOOuL$?>%pEu8}+N@S'
    'x`@Vj*COhK)tvS5hdC5aQoVa#p#=+7e;W@WKmhV~NY2CLbb5b}a*8S^Pr%6$pN!<NMNc++}Rk$@7n8^SNbS=D7nhq`8H=&v2Z&@G'
    '-BI=I8V4^zc%y?}|>EECXb6F0!?r-'
    'ED#Sc;Xi%c;7O*>uXE{W_Wb@~NQ=1iOJ_zFz!Qc#8K(NtB`Y$HsyphAm{0uPb0s{)9QI%UT?yO{HZpl?`FKE|?6Vdsl61J_+r!3@'
    '(RcK8(^s+fr2q7#2@S?%OR+!B`J-SG~Dy9q92M$$<~M%Qba21RtI;jA-ZawWI$Wb3&YJjtm|r*&r}u3NlTgw7JUkvh_oZ%L#tj(-'
    's<FwG9oMf<O-=fUpoQ&#i4WI4$Kf(UFi+dRXu`KGJx?y(Jr_zzg0Hg*L$EZ?A?ck+X`k7<?*Lj9@yHDwlJVY!Ro8jM;^lZ-'
    'n5>nAb==S8-'
    '5BDpS?|G1?VdI|2+|oUs{Bir76lsRN172iq!c39c+h?_4VU7!NH}Dp4<|qwU5}&pLchC`TlR{+tT7<<pdd2P8i{s}>TpWYdc39ji'
    'M5qX6fb7+BGi%A{LWS!4rW&a==RN91C5=9!CHhJy*zwlH`X+~?`g&k5nB)1q$OY*TM`>9s-J+TAuZpPOd07-'
    ';hwb;p$ol`SHVb>Ur3*vFvk)2a7EafA366Uwun0N0lSpX5g1G#f69lQVAW7*iWGD^@@;QMc3&DY2Y|=7c9S$J%}BF}cJ_)ZK@d>G'
    ';acqN%#6s8|suDrtOFJAr#W;?sEuCygUfPI*?&_A%T1r2C31igS)W^D=v7WGoFHA=ET}_N~_vq)`e(^{5U*v^!N?h9eSIQq!y<Sg'
    '-n2XH!6fvLN=gZo1Fi<NXv&E~&+YxWGXg??Nq2X;cefu78G-a&AfKKrJPcL-p-'
    '^1va#x$=V=E4jZr5bLTp7fVoQ%=PMcqz;l4^B(L?@97;btf+a~fu0HCsKY^Nos7507#&vd$L$k^8N>GIyc6)?iolyczGB*GQhNyX'
    '|x?{DMlSq!133B4<*(6UJx32kfTPhWW(f4)XngbFQbOpZ6tUd{zRITdP(=GhG_Vq4cQK>C%3T^>pIJTU0uT|sC(}XmsPto;Crg<('
    '*XNwqenbuW83Sb$xaXpPFY`pzPFAL*+g3UUxHq$39b39WVCJ}#_-'
    '#q{r5j5oy@AtX4t}UJ&G^A+DEJ?#K4{w1`JWgofR6~2~Od!AB<+iLR1fnZ=b-'
    '8seOwB+$?6i`k(8mTZJx#87XcTXQ*LDLq{e^CfhHeT=#R?u<vCTKP25iHdDObHOa_b3XcNI};1-'
    'erW+bfQ3gnW2u%Wf?7AT`I|vS5;icY~hEs^L*&&n!!vNc!_dw^@#x6_u(`9KkWKN`*XP_fhRA-'
    '7KzzCp}N8v^{|K$1vu^s2F3QMn}dKM%h$Iu(TQd&PW8htOOe0rF-Re%2x5{R=UF$46foAu^CqMflk8?!L`UBx)eOAT|%TxNn>)%0'
    '%AuFskvgsIMd8KzZ*3UGk&n)&|LS~hk#1K1q0bTF-3AZOd3c34MKVAk{FJQz?2H0c>B1LhR+0gk1yD>oS@G$eh{v!SZ-'
    'g4LemqHW;**`(!d$vq#7$GGZxFoph|Z2_st%%n?ge&YoUcF8Y6;Ep_Sim+DeHrap3}!=B9_a?Jsf*3&lh5y?S4I#^|wblCEg|kX_'
    'KG)S&Y$43*Te2_QTm^u>dp-'
    '>B5(DR(cDcXeJ?fexc$)tBF$ef`v`nhfb9A+1tCNLsC@nItk&OR2Zz;&NH8223%^6W$_DX5&be0^k<t%g5f6ezh9GGJ=z#T-'
    '6dim$*AJD{xOGg%z?M((H1V4L|N;2A7^TvBu9>fC3X%_BnbO1mD5#NO*XWAFzznKKeQ?<8PIs@Z3Vm{^62FKA8-'
    '}Muk%_j+0`#eMO#h{ETxYmR8$2bp$JRlbf|dFVvZ@{$DCaJ0^|41UT|=#R)uQF&Yj)?z$kL>>D+sUoUt|1y*gzFy6s*lt^+c_L0O'
    'AjxiyTbx%%*Sx`$B$CgU2isC2`>-)1>G6@<8)KdJwk}+PTB}vA^JS3(>aXIIn(S);>;zHVn{F!c-'
    '9*+y)!~u|E@B<cHaWI0Wa<ROnnZ{;a5=QrFyY@BG5*rYr86`c=Jx!|+M9h@1$)<*Cv<;d{t|2i4QD?XxU)K~-'
    'fbB3HW#QiznxrHq(kjwr^5KALLRQ>}B5z6-!GeXF!Dkv5og(Ji9xxQ(0oOz{aS}~-'
    'F54}>#?NW+V>jiailo_Lm&nW&Cck6Preb;W{?J-'
    '&tY$<N1DVx;qN6jab;R?ERZ23anrW`os{ibROq54^NC#*B8y*KWnH+fs`#LigU{_NW?R^#ttGi{Oi`AiT6ygy*zh%`c?v<MFZK%='
    'TxQa05$=2kp`4mkIuEg{19<v)cTd8)|KodWH6evDyw=!7JVYy>{lPn>G)zPe8SzyMaE6qtR86KxJPun>%0eNaz)M#E;M43|cElF1'
    'M#Thj5HsUj0yRVj_jTuT^E2C&Ai7uCz@p3!*_{%^aA3kZp-ZlYdu+<TyV)S%MaGW|J#z1IRrSc7?kxB?BCH{=jTc|Q*R)|D;rciy'
    ';4yII)UfCORTe_t$EwbuC?OQ8F>S7j6NQbJyX}@fpoFAawL!2*3m(Yt-_pSB}&u_m~xTj+L76W!qZ?cjUqpc`J7#DqYCRQbxXq6y'
    '!wQ+iCK*-'
    '{o<s7e{ZV#5{6|h?Mbh@;8^JBK|D}JJ(57sBc*QIGm;s#elYIbPzGY&v*&h>Ef9e_4wfjC~^i@lm4(L%QYs7|YD(NpjJ)sv4U2rQ'
    'CP%UA{9L{cH+%9@SjMYZtMll%FZF(_|U1We)z3bCOaqFF7=WH1rC4h$YsRD|>xf`W8bZVM{n7P1Xax(LA0_IiZ_z<%%5b^~0frL='
    'X#_ZJ|fUjz@)XzFyME=0>mVN6H&P19aKRGB9)<i-'
    'DqVaN<qZJ|RQuTb%m#Qjt8Qkp0cn3a<q@~1$F$qg;D0`=9_LZ=uLbwuXW7QQBRQ2-'
    '@czqrz{uZm)JEq~ccs#T!|mPzhW`as+qxya9|6AkBMrVKxl?FCNh_@iE}Zo!-P_3r3sks7-'
    'h30N9I3Kppe4s$hi744Q)9Jr{SDLgC`+9r3{G39dX3I#^jsP8^v?6uZq(%z-'
    'uahA$<>P1Rov~&+L9WAGckkwZ}?1bfYe<v_4B9=v@%cFLINrEA`gxlhR7ZMPJqQpQdZW)&*QrkMbs1m(6D;7PKDEX8KWqn=_o7$-'
    'Nkt6!OEQK+Qzg%vn$0@ARjCjb+NW`MBpi}<EG(bwFb2g>RQ;#M9OD=j-'
    'mpi2jPc@BePuZTaWX`1SOTh`J4xQ!1(cT2%!RV46fJX<(3nOZnrg%@!gy=z$H^!<iJF1(0k0#|F^$Xl=uG@0LE+E#da>V%D;AN^!'
    '##@{rLP>*&6$N?uD?%H`KV+F44h3ssotprB#+OE+)MWzIr47wM%xjD`Y!vxr{0G<RhlDr-ov98uBO6=Ej!UJ=EKfN0cyT5m`w6M%'
    '^|G=LiBO|pZA!Fi$vRw&D??F>==Q`6f6O0<lrWf^nI9d7B%~F|Mu}Ffs_m$FxFJ)2t^^DtZsm(0K2KMLsiz1Xy^v+vNKi?%+p#Cy'
    '5mRCKE^83UUt7KTm1xf9>j`IviW_dtrWGq)x93e?+AkSTeqek9e=ZkrN~gt4pS=FSpEnzQq{^$)Tz{IHAjL1ZaAX*|EYq0NDZTUe'
    '0b{Yq@F3l<C}-;EXjf<!ez&weOZn24)eOecvCfS{l%O@`=wgB{jHsf`%ZTal9k&<2P(j-b;zN|*)lByi&TWW!ZPt-WbfCrcdo2U)'
    'c*Y3dTe*D|%5q#?!<cc<U^mjkk@v)OD%h=(7Ia8N7l85oX(<pf*kbJ@&v^Q0vJQI;l8Wh?0ER*?gURyXG^{MO7<pybCB?Gbt`PK3'
    'o5gur*okL@L81xkEGa1*078g*tK;&oUmSX2&9n+_o30B@x;ezsk+xxzc-}AhzA-Cda~{lfna|}^ZUILi2&U%EEsG>#Qj`q=?jJtC'
    'zkmD7n}>%FvP(E8i@>AND|T{pA8e7D0%C8c$Df&OE5v`Uq%A#qR#aLLePvkU_*|=5<tK7q16Vba-W~lP_f-'
    'dB^lhOnBW2~vglEoL>vin7DR~8AySi~EEd;Uc-JgNJk5gb9V_sD%$a!lPa1?Gl)IA?YY2VEBlI0pg(Au8#l+=r@=Si1<_+Pe-'
    'TwwXRa@p#2h2n)xi02$BVqrz~=}@`7gIG~y;dv4GC^cRS-jtp2Vs6%#EV>PIIPZJPOd#ka=r3g<X|bg=uXD+XR;x|TPEZxWNai$Q'
    '{SfgBa=KJ!dh1lM0+VAH;A!Yeefs(LQk1pJ+Qr63wO!d@>;qD72+>y**v24Y2}86yGn(je)H>n(Huk33Xw9p#FwV4E_He!o$Oq93'
    'fIiE`-zD?X{^7Q!NIZw!FXxun7yRKES@vXRj`8%X@7mwmX<I$Hh0>%lpP9$%>UUlEZa1ZRM~X;tfmn2&vEf$oK@_@VA&Bype3h=-'
    'VoATas^|eP+)(oBFT$148GBpQb5lj5qW+&yY(%o<Jc&Y)DCdCVizyC~-'
    'DF)cBV`kemBa?N?+daN<S4KexZ}S_i9TMSkP>!LKC2nN0Slp_U2Vx*el&NvR1y=$%R6}_I79-'
    'Kg<}k=WMl?{aWD)q_%vK|gq&m>S$szAtST&)nQV2fTg?WmbCGvZ+Cg4RtbG`;qMROftSb#G!5y6;aIUA{u@0PMCY#ELIn{u2>j{d'
    '`EbsGM8y(jNPU*CEFtNsBSelX}5tV4ZyUcBCp}Qc(u#8U7oa*Tr9i6^vDhhPO4U<y&G%)FN7w%-'
    '+Krygtu3<UErBYBoPDo+iar7i$rZ<*$N^%r@?aV|FSp2TZ25LYJvvVgoGwjWPG-jebjGq1vkM>5G'
)
)).decode("utf-8"))
_V58_KNOWN_YARN_ROUTE = json.loads(zlib.decompress(base64.b85decode(
(
    'c-'
    'rM%O^+MNa{Mnk^B{iANaLGU;`0h`c1IXVCY~3A#R7hY0pt0w_Ra8rw<MCyW@ltXWOk3Wwof8vM$PJ~tg6h&$jD#*^Tj{^_WR%d`u'
    'mH&`{l)lHy=N~cv`*qm*4*FpZ@*J559c-+i$=B>tFxl>*xPkjsNuLhsRGpW`Fz3iyuD!<<}375AQy|{q$n>;_&1C&6j^~o>s@-'
    'eBAHfU4Hy(^5dWO_YXh6Sgki-fBxh9$NdZU!`Fwr`T6}%Z|=W5=Iz7b#cC6N{PD;A{=?T_OkU`)|M+SAK3`_z{o6l({&0TM`s<TU'
    'e{^~M(T}Eoemx-{_xJagS6=IHzkI{+;M368*8{kG`r-5Y`***7S;SADzfOp;B4HdK?%(|UX;_1+0ZpDh9@y}-'
    'l^pk%FL=8@O_G?Rl{@Ien@{`4$=Z#-'
    '1}_{O{o6Nj=KA9bi+X(g3Qp!^=0{^bepqNwWQ8xLe44%E!hIXUX^NxeKi?W&zUfb24~DBLiSxJUX!dWyVGx#QSW7Z(lmGQ>qsy1)'
    'YW9wQwa_R|?~m*U3}P}{OBwUz!b0mb+VQ8~9iKK`x@@83roK!**u!XH;xgz39?k;r!0?GYdhU$Hzn=WfGfZ9hG<WJwe>7hIZ`0D6'
    'x69lNkIkoT^b_@s^JnWgp4v+te*!0K_+4kRuKzEYk)@tLnyh8VoqS-Ajh;s0HcKa0+sJ-'
    'u+R;J1oTdf;K5>}9nXeC_(~UHG_Haj`Q|<Um^1OHz5l8Ft-0190pZjoszkmDb*FWtaKfS+y|Bq7-'
    '1^%9TDd>NcPP4O*F?zscAqKnr`0#nU4#QO&{yV&Hw^MsNJyKly=fBEEJ7YvU;Lf7?FcxVzA1=cszKJ)yjdoB5%PdDC^3j)T?Q$8+'
    'xZvJBK76>o0ft>V=Oi7y_Yw#5!smS4Mt`8e{jsNRSx4dj)8INj#j;PEoItzOLt)3^HLQ1Ip?1<UAP!ADuKf_z^IN8&X*l1NhX5ks'
    'ilYR)F#1FtAH@kKailfIILTo=#TZUaDu_)ODkXhpbZ-`hOKcV_)-0n%<CD)*v&jZ4UmkdbBY!ITAwRx({0BASIHAJ|fu-'
    '{Chd8rnsKW>svDM2rTzSQl&{yv=hWYi(7J1G)b<_;=57!Z14?CQhiCEq=-'
    'NHxGF#vF!qP^v>K6)U7Vl^UjmAByIWPzTveBvz_rt_@M$ChRlJ5I(T@QHtdJ5G#sGsv`I&A}<$LAG0iK25)R{s!uKCf>yi4$qF$!'
    '-qY-RE($FmkJs^NOS1K&$g0ey1F9c!Q|ZW>?lrOfaNA?b^xZ0Olt3BMK(5`Ipf$Cb^zj0=4G_Jxfnr{$(#G=eC~>l%+~!P=14<#W'
    '^1}L_S#)m3`H}Yw^!eTEIr=RNv!YNKXiR<uK*<=;*+nO#@ZLy3v`}gls3-4t#Nk)S8V@Wxwk8JOy5_#srqW8AAgyE$A?d&9d-'
    'Ko$4`%M4nOQ4AOCW~mYxqp;#dzGRs{rk2DfXTi<P8AJSdDoe{_!GvVdHO&dHG=KBS-)@v#bn10=#MUuW^Cnpr2d0frMFQQc-Uf1+'
    'o&1TvKocWUki^2cTc5!3s6Hb^=@GPpdoFgV6EnR<PtnL-z~yp|n@V!6w`@Jx`5U-'
    'l_O!c||x;8eM>02v>y18ji8Vedmk&*W|Fmi8)UacyoEzDpTjJdQ>ZXuPb@gv|Lr;yj^muW@MnY!ZQRYNsbdndDkfNDK{8dL<P029'
    '7~(e))JiSx?FZM{^<P^x~FCJZre{Gy&)2m5glr>iOfR!oMAVS#8d7#RK|=R?3hrY0upTBL;v{f%A7T*ONKCg)uI?fQU#(^LecqrU'
    ';CjVKcQmJg~u7OM#*KjMg6Bphi!;GlZvHyJPakznOF6EB|Mcpe@YJ*p@5qpr>SThi@{pw*u4z?}-l!UIG(J<4Vz-BO>R+J77Z%2u'
    'Sug{+0SJg)g1pKa-'
    ';&DVuW!F{{oB<0X@0Mhxzmp{xNCet5V)R;uF4O?H+gnL;lGa`Cr^5u|f|`puUM?A?pJ95(#_@#Jju!d*5JD*L2&eFRkE@eJ2&lX6'
    'Hd-wih#+Ty9@(XmqpVFsp`(_=spiD6*iB|uKP2KY?N8{i&@H4rIj&kw;0#jaNsnb2NC)g~w|r2$x8%-'
    'hLL4^~QRVz7(L7O#))CdNf-Z1Um?ViCQnK448WQ=Jv*EpvT2$=od9tYm%3)*H-'
    '5#V&NLS#@J)notJnY&)FFvJCH21?rhQltk1M{syck4X@RiH!o(UxEP;07|fQoA+;f}$j`ct2@%A=MuuS_bL59Aq=@K+9HL3EkYF^'
    'SY<BW03zy6eql-bWMHx9+^zBo-'
    '64tLXVL<<`8PGOz0MM83SIkmXn{`3F=E}vje@Kdk8_$``(d3_o3vUv(mXeIX*^18{J`5)tk+rDS5(l?0e#zxS;*qg><Pw&uT)x@>'
    '@(VVJ^#y6d2n=aBYwRBi?BXkp`2#)*VPI+5?5MhH?@v5`bQU*~C8SV#L5~#-'
    'x;^FKwhj_MlFqY&`eEKMD@A||LtVyurpcfja04{MR)N_x5HYL5fEQ|df!zcVy8gW2lm-'
    'jZ1@~rwhNC*Uq+IXIE5z`Vk@vIMN>2nzfszeJQ_{VJTU-jTEsYbZ82Z!fIMwe-LI+Z9(V2vlT+BoL7Uc}gMa-yx3I>_h=n=SBNX6'
    '=N3Z-|*>}`!ASGl0+npl*qInh`z#RuvO=_LtsmEa_;W-'
    'HbnBds9017XCd`$unqLgoB<XaDs6{?A{7dkUuyf5hbg+hZH1`1nO61GZHe@1{QN@D3_gPzaqH==zC}?Nc|xo6w*5E#>~U6nY|8DW'
    '2DZz2QWNSIuqDUOaRm%C15K<%&`#%_c(lhC8|pAb3M5fwS)M88fd8mst(?5va)Q3Nl19oJz0aA4y=olTFxGl2t5tWPA%0!^kKK1e'
    '9P>cswNy5@qNo<bX{ntF^6Uwa}>;4b;qiEm`6P>@cdk;XEa#3oN_0Q6e&U?@)L-(OZqN&Lr30$ax_&CBh)BBXi<X%vOfnQe{Y-'
    'o@e<@S5neAeAp~f`T#g)!~1j#!${x+cE{ywCsgl=jXC8KS~pT~_RyNfSUAc9Om@gLXIn}sf}II7MS>Pb5ra9E&>)`*bOCW~6*2{@'
    'u05gtHu%PwhT&>4{o@%*Jh!v!trp400wqJJ_l;uwlID-WLbl>c&PoRELnP<M1D-'
    'YESjKl`0en0L;s_&jVE_+Dvg@wNd{ohS93*qWCJfx2FQVKk5_fc#@X^`MgAp0NykaK_52BdHW!5Ga<}#B^GW_5zKtxR9$@#kB@$0'
    '1H$iWw)FgGWju^DB2bev)$w?C^+1q((EG0n(zrp%&|cvjZbUacG2$UDTVivcw=SG71E$+~xtel9GQtpx`(Ukkp5K`C|0@m3$oC`5'
    '`TNAHh$f@fe7Iyg;BR>QV`7BnUha%Xmcqa^GaT%e@048V>YySBhedQkDBo*K3ab)|e8<NDiZaJ<IbbY9pCD8XJ#p+PP|?JCpxoL|'
    'f=#&ItRI}iIJFm&^@fXKf6yM};ou^-QKvx-X}_!$q3NJOfXL;1Qw>eB_jf<otn={`LXbS5ou0Lwuc@Jc$e7+A!j%9ci-Xgs2%Y`h'
    '8e^vm5`v&>B5WJO2vAWMOuVd3A4I!h+x;?6GfTa}*^CEZ~#g`(!7Lc^IEa_sMWtA@)52L3J*GKB2%g+nq7$(?a<+OeTA2Tn$0apJ'
    '-P@wY0B9eo!XYSPyrA17pCO;Z)@H3-A!+qK|$8<-ykh7FQn{5?Sw7EgP=(&FU}J!MpRAE@hi)U;Xi_`iT#1LQ-'
    'D%|_R=!|O|V_~0#g1ru(xt!iSXus~@~GMZo3?AXd|th3&Hg~LW~&fA%5Nj)jX=;8QtQ!?(F!<fr^WPMyDN+13sEBYt&QptTZ{4iF'
    '%&)$%A)|CEPENPRzS<ZO4WZEg}>Igl=ds=cjRWg7`rBJ#O5vU-'
    '!KwFSZHh>^aRfQuNjXC}banBl}Tx?Gzgr$AzEhbAHC8DIQI^CkZUB-SFftg77Xo#{=LJs<L+(vI7LPfhx^r*@oQY|#(W}tlM7T1%'
    'n*A3;g&30h~h*u*xgoY)MEU6o{E*9Eaj@*s7{o_lIN8_<t7nW<<76h{5sfZFvLOGPWNu4xBxR7PB9!suhFRqjPVg)F*(({6=f_!I'
    '=Q`xq4evb-8F)s~(wYL|ip&$^u1alv}MBD+=#-'
    'bPkZ~p0P+%hpnn*RbDgcG^>OD;6GZS%KlljK2^=dhX?cXx03MZGAyJLfdYD$~hXFB*=qtcZQU6slw?L&Uy~tUU3v@<ddaMnZ0$qf'
    'INwdzuAS^|vECl1q&(%s64iZ>X4w@btkV_}8;h8@<<F4IvK!Vl87tRMgLjK@{!TV{5P)%8mvIRiZ=LF$puuLIhyxC6$DIUhM`pH='
    '*1J3P<YuGO*>YaF>AN7{uks8Sz<IGEX)Nd(Uxo<(!DP1gknz@y1oP&4lvat5;F@1d(i@w|J-LO}X-'
    'ikz&A)n2!B(HspEz9e6Yt0%Y6<4mdQ_rFNRZdCiHx4JJMr<OVyIz^8}Y1;VetHF{J+A^)qmd|OD$=Xq8VFmJ29R^!cnIhkDkU<|E'
    'CZ#!K<I{1~Ebyiu-'
    '6g1)xk6*BDG#o$uN3B+^u6G5hd(5eZq9bMh(;&XpW^;KPGy~Xf4+zJiuuIpKOz=tnDhwi2X%=l%2Fr?0fcwYrsh-lCMYQio%N+JC'
    '4!O;>r=ELUl#3E_9G4%V_>h=c$6<x9ou-'
    '&fua9YM;H0b3=+?0#d0xMJ|M!K=q)V+YcTMNI@j2KdV8O)%a)~B^0+DHcq*t%W#}LCwCmd$(S))!4nqVF+k~?vUqYGr@RP+^-'
    '@NBB)+f^aTEM7P@X+c(jVTr}JLrb(5Zg4LD?)wQ3+_;TlSF;+);+(zN#p#d>4<LBiC_zcXQW9lk>|IYPAzqo_TK8NxYs~Zr_RIg+'
    'u}4$9Dq!s>m+?&I%)IylUV*0=X666^W3(bzXa(oslEqq`nevl$U{`wkF#;S5qQ=9Pwk!#JF0;Y@M$6@^<P8{YfhM_FIxek{Zi=l6'
    'A|~MDdk_fQpb1ySKJhp|6D4E!Zn5t?y=pCvzlc_XuWTOuc&aLqM$6I|_qLx(xWG(+gK~?~Q*(|Z@1r2`>;3BT!pt$%O_<D`g#|8S'
    'Wh4OtZ!sijX^XoM(?Zs6A%Bd)LYt{3+1aMq(QXv9`B;hr%~n$Oy}AN8G%qpFokpZ-MpO(c1=T0y(eA-'
    's%c@oYiXqAyyTQ9ca`o;zBv)OXe4H{wNlos{o3PlrqqD%3^mzvXoERyTwU96z<Qi$?Gs;!*ve!wD)zQC)9vutN!Ry&2+aa4;4Iwi'
    '}6<Vf<NII}xE&Vb)xuceE>2FML?;2DXjqy4OeZyMyiNf8{QXAxeRlt`DAv{To(%b`ZeJoNyLIFrtyGed+8?6KZyM2l*jt$N;=Xv^'
    'G5hh8@6K9i;N5=(oZBPURg@||=Q<DY1iYKC_=8bfUWpb1VO4~G%kfT#`MZ@}NgsRgC=||LRT@WL6f*A5tqmeXRznpglR*KI%G4{+'
    'BZHLsJh2*~0A7V7Fth4yOhDtC`)7dAbG-U1#gX;WXnrfF+dIhk;nF4rYBchqqa2L6jhc0ZkN?Hhlz_-'
    '&h)2u6R$^I2iU=>ua*UuhR!@&QhkXRO6X2`WQg!VQ|rkOouKsXg!;Vd$xua*k>Z6)_eRXfaOgKtnFDzeKQ!Wv9#CZiDV#JQnF+dc'
    'kL<-YgPdckYWUU^e}(alrE9UWuTm-ns-!CS9j7AE0WAWkbV5a2LyJXvf5iq)UK)-<9#+rzd48mW|NE;<xmim7DYprGW;-'
    '^~4&3OvE|q%To)$*irMzM3qv6KhGVfRQ>36%OT+HX`$gLlI*}UL3tW%{kokTQ!a+a%>~Yz=aN|P7OBmv|85H_VCTN5HkQ_G7Dxmc'
    '$h7(mDjUi^wrbMD2s?IQ081AIqt_&lv?1i)ibZQzV<5it;MHsyN!Q%soba(>08){M?Yn94YKx8*4;wj4fp}3o<FOc@atSi5i?^I<'
    '`S(5@1T;rb}N>BHY+^xX*a-<8bjW5fFTX45}@6apvtlP{*~6m|Fg@ic^pGI0~244D5K`Gb|!W~-'
    'V_dJosOP{7d+`~Y0%&x`=x<ruucU9w4G?iv(&PR=!9Nygi2GyJiZ(`I@vxQD?h&OO|aj#uzP)5lW(<{pq?R4PZ3UKPunN%Lvbrxr'
    '2Nr`aUkL+xidle)bm!7Bdk8fN&eQH+E)L;LXAin!fLla$<PMi_%N3;u>&riL0b;cSqCN=<*G-'
    'A%`S1H492xQ$h?D>VGcf&1@c=7tGL$G%#V3!7rZ&mII9-'
    'S8PySm%5Jv|Pd0lpd~=t^m3V1qB;&YaW^GmMP<wWwxdXYyFiX*HKMBtAtj)_je&q}tl(!l3=?@*&xs`M`OY$WOVH8kZH6q{0`gkT'
    '%%bL6x^$79^UK<s<Q~{8C2&CAm!ioS6F2+h1fSY6`U`G)H<)bat7_uWNb)9fqk3r8@m9RV{T34@Tvy-Pu!<as;EzJK1E?Z#a=~&1'
    'xsnY1w?OQDNSAomCo7GLyB7O)>InCkial4F0z=a->AbYo8gcKPMe$i%xctCE`R8t6{QG`ZyRjPjdB6a;807PKge&WWUslKw-'
    'A|ha!+dlp*9CzxI^qM_f$xIq_L@#ok)qq#yS*(;<lp<-'
    '*!|^OR5&;`KPJ{XpGvj*I8xq;2bW&h;nA$6h23Hb(rnclnfNh~e<R76^fKdy;$=OuvvV{|baL9Pd@bRI{zrt)+j%P|>lmTB!VWHR'
    'ao>6*CC2c`ib2i@5<=Z{^r}QDmhcYTn1dwL2V+!huEL(eUn#SdF_Wj1qX2qV}{ZE7UGRwQEbO1$I#x2bZ3NK#NT}h<kw!)yJl~*)'
    'e1}Cu7+QLDCUfLuIw=PJh6*U0#vft__>JLU~LZqo<C#0l=pCuq@0uckZNWJYuc;T7E>;Eu7MW^rs0az)NQLDK>dXb87QfLquWog)'
    '@5!#lI$>`+uYam9(tXL`P0@FR+r>Pz#jlqz{G-O*|RLKMunyautHmy(*O7l%ZB*aHYDcqroQvjdA%J$6DJf|f>9Rd4mH&s<_S-Rw'
    'ofE0uSNL?9aa#kGE*_+GmPRyMXJkvsKr6AoT^V5RTnFX&#m*jf62eES+!P+!`nzn9ppez-'
    '>Yd|sYKFHH;W@d09QFotlMEiCyMuD1r4Wm-'
    '+(o$Inr&489G;$v?!1|_O{G5wIIiCfKpK+jb5m72C55~;V??QWk*@ryq!9p9}a!j)$ws5HD;6<TZdbB%IX^I=qnjQ!jjxRrlj6lR'
    'Xs}l!>P`&#l#6nZz3#^v#A)iQ2X*BD|$A*+e0&HO(JSO9Dz3HpOq56=}wj#F@thg~1wp^@PgWW=~*52WWz5HK<TqbfHKJLPZB$g2'
    '74P^q28Jc6!!~*29d+NCLyg-Hhhal$>QxbKVj#sUhh*%5zBUZ-gj&su*XGD_eIGZ_&c9#p73r>pttGP$nL}I2i%1n}XPS;=(Sxqn'
    't_<KCMV~&EQlvPZp;xz{f?^FkVrf61&*u{A)zG_x6&D}Nt+$w<u>(V&ur7e!P#GF<IV3}mJXjFbCFd=JQ1>7VkWBSgs_|AT3oRw_'
    '0#>!$)1x|r&h4;G%qg!k$kTM<;eQq&<VOTTHJ689q+D-$NmN^|I1gK{cpj0V-'
    'rG)*?NMi$bjoL}@^%9U@vCsDPRz(TLCTY>>h<2{1@Fpv4uhki{Ooywx+~S^sQGuq8`?T7P!T<A!rwEC7jRy)~AJ(X~!Jsw)i%@GG'
    'J6K$Tbnt!~2Na+(8&wSq`AWg5AmSXc#|C}dTl}Y2*HwaT)cH?;Y@~xVvxb5CZ3XJcpRhz-Op8}y&?__IED;%{*fnXN#9z8FQdasc'
    '--ppOyw)H`5bDkq^rUaHPo<8<g(*E2@KVP~Dls4ONZ)sz*&Q#K#F0!gg#umXe#|;}YGj&N4#5ah>x88&Z>xz0SLImgqk))}0B|!S'
    'o0eilL3@Ky0!kS{sVavyZXxNHM@U^Rm5q^d)qC2&lh6MmI@9C`;>m2EjFWEr(pl-'
    '!OA_06ItcjX2GYXgfrtYhQV^%MgrPp^7`Zz4GPuvud}S^SxSfTOm*kr0El5?*Kw-Pn5ThXWYLyvgXSXd^FjH?KKN)m;RfDXPN@g{'
    '6J$=+aE7eHlco}<iN*i;^FIGyYg*7t}>43d?`Y{NT*H_lohr1OWc5k#ku$`P9Zmll5X8XZd7UL`Eb+!St>7BZ3O7)NyTZ3IZcsuM'
    '0;EXy`7<glRC|bJ@$DlxVcLo=p3#XCh&FL0g`yyvv)Zv&mzEms#VaiIWkI<vqRncuh&n%3|rOTn-54@zomldt_N3O_>lr#XUO-'
    'n0-'
    '7TywvVw~!foZsPf7k^dQJY2q()0~+D*sH5y302+<xI~Iil`WRoTa{gtdHG&j2h%8yVBX6<6V)uVry24?tE=G4N}3@Ty<t*0NSZ!t'
    'TwLjE6pb4bsWUi`GY?8<q;X`_sn@h<!!q|IKZ;-'
    'd++9eVFkVtqh)}~FOgDkoBBs>J<eOEM!W3FS$qKMgcH7|%B}@!ZU@hu5NWEm8anW<$B7*3Av(r)PK$YU1V))|D#Iwx{n>e{}M3Fj'
    'g!-|>}t!sm^>uuq(0p;!VRlmK0j!ca@pgF?IboZTSx!|1ygXSwrzSKq-'
    'J2F3&Je$vd^a?b2DyGNvmQ`Pf6QY2OPUqSGZFMlb1EN{@(k6dg?euMcWN+$Zkd^eend>@2*AOh@5tt9T!)vGrkOPDiuDE46YYcLf'
    '<hIq>LF11a*jZ<Sw7ca<kr5D}h&F}XB`nlQQ~G_O0Ro<7ni8l0GVPn0^B<_SH>4C;-'
    'cL}IW;XC$=tA}dA3a^yo=O6(Z<}kAULl`ZOL13oA%W$&J|uPQI%VU)R!QF1jV-'
    '$BxIx)+70{Q}GD0CD^Xn_lvYaccrfbAfmS3xg<VK?(cSX*QOUd{tc#$GSj0F>&47W+f>k7e<M^}3zN9AU}7Z0oaoQ_ZI;C-'
    'GujRZnmTBwH6RI8F(fhz8atcR=qLJCiq;>1iN%`Y|$RZOp{MHptRzSmt;Ee<}>|14G(A+Ty&Qp9lah<4$~daGq4YuX+&7$IcvbNL'
    'jfoBw5Y_1`=b#iFOG%Cw*z0NWekta2456%;FRpk!?I?@3i!aqy@FHJ@nV=0&%=tz=<~@OLYJn0{v`bf(VX`7Y+kZr@+-'
    ';8M69EUU1vi+Ge)YMwfnr%vdJ&-'
    'tR8=Vh8BY2NDqL>TR~o4r>T(<rH@T{x*Zw@`&y3b;@PuHLPM>)g~dS%^}i;ylsT0<SAxX*0{;)J(KG?=fDBp-'
    'wYLbeb!@fqO9V<;Bt5Yk<OlzhSp&6o@(YFl*v4DiSr5<FNRCbjQYB`uqgsDgswu$5p5;sy|1^Q#MGAlU_KcEKa}50sG_+#-R~Yqb'
    '--ZPnC7g%~Hkd>R?vCuS=vlHj2L$c)f552t>kKptQ}DF<Mt#%$q4nX(&F{KS*jplnfEM4O3#HG|Fy;#j*k#pnXWjBn{}!_h(6DDi'
    '^R{6OF4a9nejhtv4R#Aru8XVw~bcFH9;&nR*8KZ=G8WI9eb|AAP{G4o>)7B6G8(sJw}3bMLYgg$tG3nHC_*_)Cg-'
    '2bwJ)I1!b}FzQqdf<s=tz8If_D=&c6XOg4Bu`CQLS@>4PB9qhw`~@<#i!C|x&THnI)!=t3IUAkg4oqr<#!N!KA+mu-'
    'IzT+582W@&4;7NDg-yVu8|q{l;e_u>RwYk$E!)KS_l+_Or(>gPaD`tg7JtY*Uncgj#4#iaJw1Sc^RtasNz^!UL>cVV%q)NfxstL;'
    'X$VjjwOJ6X+K_=4wXRN4`YPwMaEG;5J$tZ`I(M&D?8a=LDoUl!+m*2dRFR7~JD?SxeiR5JY(p}@tT~+|mjOK$ulY(!3272-'
    'lzI6ANgf_et*5E_f}|mg256<S@eX9es1Y+IHEIoYln2L-z)b${_=|{-'
    'yq^5{%Xl9jKAq0e=iph4HZejdj20saEK=uP7=TAj+n$LX5?(`zrm?UbKdT8L-2td9;bAYKXj7w-'
    'iWB*_G7<gJO&mpGOnp6IuFypbn#c*&oziYANfpq$PInjeEUM>N=bYjg0ehlyl~fQFUKb%#^o*J6jpQaZ%Y6xP_H<2jI|ZEI(`pt`'
    '-(hs>xlYU8Pa1-'
    '`$ROnT`~j|`(ro!NC;Mu9nz>D*tyZ7{H)oae1E67p8lS3kbFFcQiNH|~603zOFfVSb>x+>d%`Uy7V$uabYYi}luZq!ciwWMLn(3^'
    'kJ{@>8I5KKXnh-ig2pnNALK`^%chu{$3Q*>QSDy-'
    'C5v{#+7YfW@feiKClhHrqmAZ<o`<@ZnIxF+)siOFimng1ezwv|YQMRxjrD!YS<ga)EP2bANQuyPg+)+ots844UVi>4vFBisMP&5P'
    'TtLOD400!AEOco(`y`jKhHi~`TniQjTDJ!7#lGCiqyn=pu?N*DNFxD3XjM*%iG0Jc0l~+Uu82;MnmSV|~D0HBv_{mj^c>|P&G6{l'
    'dXh10hooedEv|}mP>UIg{j0v!)`PO>pNDG$oqFGM0WX@E;hu*#9n%ALvgZ1GXHxoEv=_@)H)z&@^ZABR=?_?Zr6cWN4tdCW92e|Z'
    'ux&4m?X~QEfp1q@@b$Q8AYJ=X7W`+-'
    'pdRp$cR4T%WcEJNz#`YA%@lHczCQDGNOtOhSo_y;J$pWhKQWK8#gq|hsZClBfqHP1b>dBQi0!-'
    'E$)7fU}<xNF4){@R5i^0m$v;ym0ui+iOQIz|!SOJl5#l#x@E<^Y-'
    '>aso%v^PZkRC?UgB}bO;pJ_}!gTfRSTcxEgxtv#l<1>TB&;}(S+B1!^cZ%0A{SUY44+$p%ZfgsaSS1=1E7?U-'
    'cUf7>1|X$^mjcQD`Uu~t(n2YwFKXtQ);_rw#<T2r$#(^1keD=%V7bUVg7+&W=s*cpt?>zW&SlQX6_{WQoPy+n5WNc7jh%!;L<<K~'
    'Dq#225oKTyB<lgj=e#aeFFN)3DxKLLZw4Ywy@j|fOD3I>jYlRn5_Jv=E(L2QD;g-'
    'rrWSpwUpTib3WdZ;Q2^%8kA45OYURi|rM`7D>VkBq(_M&ibGlvNRoljl&fquHIk1c(Z4}Djmsb5dho<4pFUtM$!bU0}>Ufd>ND1;'
    'x5aFPloM!Hj5E(<%XLCXnl#V9XkW6Oe*MpS~R^c57bLDJ;y+e;M-nPsslkGOf1-'
    'CCFJk$CIVuQ2$;0guLl0LTlT;rtWx^gTRN~0#O76q#kO6}em7HX|$p-Y~T(O@-P*<$hhA;@K5A(pC+=dCO^IqNb#H#ouiw-'
    'j26+!h+8auA{;lfho%yo>VPWY+iP42j!1N!BP^0rz^4Fw6zQn^bfWR1PQQ51-'
    '%Pzx(y=!>PG2>(pv72`+@7nbTKP#HxYMMLq$|jd^68SmZ659vJDyO_~47T?b&OOy6?yyNdsN9lO3RwDzJzOPOWMIZNF;UTiZrfTJ'
    '9Gn<Q|aPWb}*7EM7|j1W~h0=#Pw!zs8?P`7#<Fnu$>YxZJ@25SeLCpKK{>Pu9#<F9NxnNVU@2?Ml1^T9^MGi4MMV9|BSyg}$D(!s'
    'n=b&{fW1nYagxIjJ4zK8MBCkWO}+Z8|1Tsi>+hpb>Lg5^ukvT%8+gQ&bG%RYYRYk+N&Bz|5SwqbCRbW!Q>Mk(CbrBf=6bd*SAqp?'
    'pjZK`%7IoPBzjL~f9C6QE*y#ls8SYtLyexY^Oc-'
    'Y{hba&L~1ey=m|8JeV2RoxOz<{fY4v#*zL}^KO4*wNCxN51EOvTA~UVhi^rA|}QVxy1igYg-PDi$8StMqf_(bh`FDE7xC9MQ>DXk'
    'SEACKMoK@qzMT<gi3NvbcQcfh}A^IW(c%qzdXpp)&8&&Qg%)u*8w6qj#a|!x4wbuAX+<Ml3d?s<44cLPDVw9<Q}K%B$4g;}!f?!h'
    'Fo=2dp`bjAl)u=f!fbN2TOoY}pu?$|*4_PBIK5u8-'
    '~6!cKNXeq@V4e2(m`(iE0VtG5Yi<G)<hSkU3gJQo{V(Uih4*vU?Y?=k$1we7Q*@~$#up3|np=3-'
    '+_*7M=`x^RHQRB(ja9HEt|xB_Va|Ml2nuV*ag>+lyF9@5dWq7l@l0z1$X49EJJg+qOwatYjct<Hz#PR9i{!b<iq)8e;yni;nm4A<'
    'r|5cxJ=1dAG5{rqH!TwpLU;&w`zi@3p8tAF}$;6=@p'
)
)).decode("utf-8"))
_V58_ICE_MINIMAX_ROUTE = json.loads(zlib.decompress(base64.b85decode(
(
    'c-rM%(T*HPa{QNlo(InC?27aoMb25oQCeb2-'
    'ry_{f`B{2fN_41{bt<1o7C?1^mIl>L}v9+^4${`%h{gls;sKa$jHba|M%+OfBxlffBog^Uw*uL_wxPwt52J&|M>a8{_@|SfARUpz'
    'y18nfByA<zWn_6&HST3+}(fpF8l0{SKog8^H1;Y?_Pg=_2FuBb^Pw|^7FqppEeKw^Zsynefsq`i(h|#czgH5)n>c<^84@J+#jyoA'
    'HF=~<qvPZfBE+FV_w}IuQt2z>-XOs4)4DF$Kr*KhxZ@m@AG*!-'
    'n{zb$9GRp+J1S`<A+YKKl|14<L49d{_ytg>6N$o+fUyxJ@|3x+w%dOe){&~o42oj`n-rAK7N@HV@1L^-o1VK!-'
    'r`N&IYu2`g~y1(>8M4pTFSM;c=406m8r=A76er+%MK{{xx{v;OJkyj5F6CS6I}C$8X?dE@pl<=7%3v8WdUKlPN#W-'
    'owKEI)uk5j+TG9H9UROAHEz6XHydAZ`IKpUWUUUEYGx-WZD*gb+OUq%X2n+51(3T6p!zZ><0{DF<WaH^Wwrn>onW(kN@}ZwB^!e3'
    'ne%8Y4X7yMhg>{K`-!h7JvtapU9&}XDoht@tF%uUHEBq>K;EdU;kgHr8RG-xtSiDPuuJ_>Kn&r>tQ^#mwNaOoUG~pI+Jz&w`4}vd'
    'j4#()*W~91AA=rG!nO2I=R|L4olOH4(jPNE%^6|!vxNJeF#0?NV8{8cN99+9{!U&FJ48&(K<ahI(y6K-o1T$c=h3@KOF8qym|ZP-'
    '<BQ<{D11DpuZ@cW=}rG>;a2~nC$ZX-N)rROjm9Ab9mogFYWE|k>b*S`cyXBff4P2JB#MSSfuHEI1QKhCf@LN+CiBtvmA-'
    'YN1v{>(`7Jl!M(n}dv|^VOuKaCB%QtY8VB>r=X~5ozoWtZzNc<oN8z7oa2=mw-KQ;1pndA0u;cI?*1NG#JLwq^hbA7^eu(P%Ez8g'
    '}obSp*0FiLTQ375VeWH$!;sld8(i&r&<S?FM45ua)#3l@tl0GxKHw(ihHVYPO$Y{~{<nz>Qvcbxi2Oi<fpNf9ScQ5b%q(&SkbXp;'
    '>R6hO?XBG{08sRFodisVluXqvq>RrY#zn<A5&v~zonrZ&wI>PH=k25n7%Uh;f_((bi0FG0%xBS&d4`fiRMr6+N7JQs6(36%=yamH'
    '_F6w+-E9Yanj7#~!5$MD}y&VU}x)rqRQF3ky_mAz;pr4jsJ-'
    '&H*UWs=pgM+i<@bF>JFBIrwM&Eh+seR3$cLIrz4v>zo$apY0cRV|a)8Vq*M0rYqg@CCe6Wcp)k@d~z(>Tn9Er2MM`5rAFFUHkm@<'
    'tz>&t1{Ixpu#Zx!2Iixi*~~d+kmuhGLx7+i%r3AzP2PcY*=<I{>=Gwzq&16Y<G_yW@X_y+{*6+CU8*muy`ya-'
    'MoSBggbzwVTy4S(gTWc=GBJ-cjm=)r^~F#_WWJobA)rG5xKEe=7K5B_FH~YAnyuvco_k2DmneZPW5gmIR)%vqjDt;Cj?B75A)+jt'
    '5W7HJygj#4HnS79DcaT%zbpgv+$IKFEhluosiI<u2Hq&4N?T)B|^pA;7tnK3V6T$$9}7WC%|2p11m9wO#|T3&`^Z=AV4g<U$pk5M'
    'YlteKd-LmMsqAieOmX!)oJPUZSt+#(~u0+P)odky0pZ)$AVNa<IYxhj#@y<M^5!1m9R5Fi$fz@iDqU(^qJkSA98R;sPB2vn&7ohx'
    '?buZx8qPe+Kpt&oN0Zf^eKV1mgE#G!Y<+-2-%s7wqYZpG^z-'
    'bptloq_ZCmS`ZwaSmimA+XNMol|^w<VP(w>l=TinGY9Y`kodHC%CT|-'
    '1T2Zg%)hh2h@RFTLRX3HHeN_>^OiBhZO)L$f;rQqyrxRm<|fG_8+exCg^l=Hh1a?e@q1~oMTpEt&&q6Vuq4s(3?Hj_h>H=PHaZ#O'
    'wHPDdwC4lVdm@&V#jli~AzumK8I+BMFGU<-`&(@%1w4Gljj#TV;cp!8?mipL_L)a$NAI3;G{k^Tp8hn1GPC>fe?DI-uT`<}>8~mL'
    '!Q8yac#16S>@yt#I~^#a=ETu}mzWHC%^@#WMu2v#3I~l4q>xVUqjm>*y|(KaM>ap&<IJK65zV#*h0?faS?2;RIu^sk-'
    '^7<lxpJkGC(x-tM7qq1!4mDH_9o|ltXX{%WA@2v6JIxOPF+8gm!{7jJ{a1;Eo-EZq$5rWzi1(-'
    '4Q}o_02|=1)`;lxJ5c}>xiZUmU6LsaJe&CfUz=xgd=IPCpHVC;G#wP_MMQy}tjCx;lPA6n@dZLu6@}5UaAR%V`xZ<tu>Q1cIRzw)'
    'Wo5e~0R*vk>0je0Cy5zIHbjxZ3XP=%=kv}{Q9)T^;Biy(yvJ9vOQg>n`5p7)$HVGk#@{NCW(kNFuB_3vpk6c|jQ>lLz1Vncno)AD'
    'Q4+p>-'
    'e@}hr~jLNNV5xTWGqhKg0F(<gQp)<2(lhfF!wUC^O*f1{<RVEn|RZB#H~U)76np{rtkmPshipSfdQ#n{IS8OwAVsfhe@Bs(NCO38'
    'OP+z<TZ#YF>Z{TB0vfNA2_;|0Y?1f<b6^^QH+!Onl&FARZo*`#<MJ)V2L81KpY6ayG559UPEvG2m#SA5cKyf@OD9g{bI{fYAj=Cw'
    'q^uf*UE>sY6_cyZ6-'
    'jFj|OZ2hFA3V9npJg<ur*Z3CRaqaG%J4`~0lpJhUhrrFj6fyLF^K*qfeqO6sLuRG<qCBw{ZEbs^nkYbSAegMy;{P{L!^87xb38if'
    'QI_~OGLPiOx3Z{Gg#YIBQ&9ZH+SzQ_4P6`B8WIv+m2-4TRch1srpFcVNA8o?U~O);m$QoL{z3as2DW}BvW-'
    '?$!>SF++~Ip|l655%1|J1w#FfV@$cOP~EjonO5aVt%9rjG$BMtovz}>p^B<wBzZG;K@d-!(+X3&wd-'
    'B1ugk0#bv8ow_v|fh|r8HSE&U9SO~lLMA&pFXAG|kDAZX5vfOuvN)nN1j`$nPQQ`q!TZYcsI<<XUrQ$>2u4NKMCFK@ng~0u)j#Xu'
    'GJ4q_Adgz<sW@c=xLZ}1|Oi4cT4i_}Rj`p)B$>Hd95yWc68I)yWStgPtRG^)rJyNZ$Dyhm+XG3L8D6PR5b*kzrrL$y4pA_10QhT|'
    'OZCpJ>%U*6As9_Zes1ee%pXP<}Jvcc~#BZKWRbi1V!!?LxF#6`H3aCmr94j&GdQmLlA{nUJ#b1bA&w0-K5~ou#uO;i(9rS`ivG-'
    '@3B~oap%@zh+E~`t)`!@!P(3h)f=b`#DO$6;NcD2n;F@-DE(Zxs8rmP*gO*BJMfOXnQRF)|9te#1=o5CTxLE#YJc|vP|iC(_cLB-'
    '@DU_(J<c#^Z+(#33^Y1tJfp0qCVM1j{h<ITND<C}a7lmjrUq6>i%X^6G)s&PB>N>D)%o5mtB7CB%*v!ObZ*)R~-'
    '5%CR;2DH568p=;ByJ|?#b@T4gEoEQfi0^H<+@eH%Y9mU^c{8P!`iz;izF;7`Zsl?5ha5JNZ*jYPi^o|*ZB+(GnaAffEMuVbx%b0`'
    '>abTI%xa8+b(!Z7n<z*>tEfB&8=kMMs!fRq*58?^!t*rpx>=d>e^W{2@+IvN;n-'
    'j)1BCl;%RjZcJv;alm(B)05_d=Et`HLdlvgAzWXT;M{Ac*LW;JnVs!4`X>jw$P68>_myD4MTPnHM%&nc3xh$Y@sc&=bP0J#@F=M%'
    'H(q2>84fDJIS>FM(s{c3t1ANlDgDR;yN4NyG(MD|*Qv1OdsXn1_c5$o%GF2X&=tM2ygO4%a<IKrq%q5J$}l#sOCg6*{%stSpcER5'
    '^Tdgg)qB?Ybo=C+JwF_%h&)y7>iefFUm`qkYshVWXAqSfaIjJueH@`Z%P02T^WF<I-'
    'n{CpW(qP<C?0mj?LZFL;}i}ctWTnf)tC*B`PM|(Nq#iPoqVxC-dYZo!?CH6Ibx>lSUthsj_T*8EYIBOj<OS^e<-'
    'gJSd0gNMV6J|H_bt?3k&25_P*J$PJhiHnqWiRoTTjM~4L5nQUC_zNFRr`R<z_@zwjPE>@JBpn-FNl^PY6y~n-'
    'CU530wVoLM{$vz?Fu;7NgS=w+Jh5r5N}hEA|oeaSZK^hSt{LJN&=<qROfxV;sbflgtGRGMWLxtehWHezLuK0?s*lhVy_d5?~rbmk'
    '@9!i12f&Cntsrl%x!z`sM!Zd#i?-2d0*lb-Bwm-WCIo!;dm(4QWP`Ug*UdPtt9ZomAyQob*qz%Jo!iq;?xkGHsC|6GQ<gDtO*^gs'
    '}C6TiFG9cW4y|X92}X1l`4N$BN4fZaeyxrJqelyC_`dae|75XP!Rx2{jArBYs}LCiHf+f>Sj0AJuV1@f*{tLc$W9@RYepwb+)V}-'
    'A|v8<eq4VpR`6VUnY!5CzqDnCgq`iQ*WZhNl;2kB_c&GR9U_^iJm)E0(v^l(NU3|Ae-COLbb9ROL4GZoEE@1L}qG=n~Z+@KR7u^H'
    '+xV`xm@gIXK_9V)C*fLFm_O>xfYZE3%D!m#^B9RkHZY=O(ZYZM>8@WHmzGJ)H%VH9w1kTVx!k@{#9_7RCSG`<;PkuMQa4k9P<yBS'
    '5LFoFR(^-r$OozFokxn5@mq)O;+hiAmWV1Jxi^RV+qau4W|`VSd!vq%_-'
    '9aH&!b_l3^r#Kq4d|Zn&7isVo$&oUs83Rsa2f3BG7H+ljj;H#`fRd|_fHz?I4mz?jZO8$~oHmIDA-'
    '4Y5XUdr#NMsD@)4r7D>l(AF~ywltxPwLuFV^3HR$?^n1l8x7FrPnLTPHAutu9V!1bIIjz0uvmxekEybRsB`p^{yvwj7gcK>#dc8F'
    'b8W$j3m2*sf|yp@=8^D|wWwA-{i;<gwE~sBK~Y#rIc^Jd1$15#tt-Y@cNNy>VNHhFkX$NAUx3<Dmf|i5Gu!!2G>;O%ZO-ZnoqidS'
    '0l7eSYR_rQVm9iI{VKttTG@xXIzF*KR2P7}I8h-}Q3PpZ-K7;ez3VLD^)=dYI4R_f>Iha9=Gj$PUEuquU6!Y=YnOCS6Nw-'
    'WwSY`%R~)clleI2r?bJoMEx2wH-pFZp1;4|K@at_6K`MnpI#Lc!Ewe?Oe{Y*(x$~qFIuyp6_Q7zh7?dUbie+3k?<?bd;z7&LB$SC'
    '=Xku>-'
    'QadsDr&sQ@$x?vfLAIS(azsj2OnpZJAChq~8Jn&c2v|dXJ{)x83cc}ZB@uGXhyeac3z*HCzK%eWmm}hNf@5@ghSR!*Dw7%-'
    '{S_0s;pnr;|52qs1dk-GOFCB2b1HiemRckHGkV7!+Re#cR7hJa#^c#?kRi-VGIsrxi1HUu%oR6ltlnRR%0l^kDDFR)2}6|kHBuZR'
    '@5TyB{CfdCFQ$E)J_!g3&hzfKIAx9<a9|uNLA=PX-+n4ttEs?8lIo-v#cTp3d*Qa9H?~CgI&cE9?wTDVcCx#(m}+d(iWlXn&uvU-'
    '8l$d6L5_-T%BO)fMHfsaIdsM8MX_Gja20_wr<_@}93c}*jo&p>YMHOSJbeq5BP}!-'
    'oVy%Jqg@=zT!RwP)zZzOAn`Dl+3sb}H!!?5j5D?y<Yc#`VT$BdFag^&)F>F};!($`=2~ZV^On3Mt3<g7Pu@*kMP9mBQ?8tXYAGh+'
    '(Ew`+Z8W89+0LysrGF=zZ<Q3c7pohcBnrJDZhtSNYZ!9h_+o#g8;g@KUnMDCX_f3WyV#3VfmssiY<R!^48+Ls28>9`^aW|~O-'
    'J4+xB(X;l{u%1Zkj${b&QP5QTk-(PXRFjQ*f-!Z$odA;+$pW#*S3!O{M(+>+R|n7o7#w&-'
    'H{b6}Z_$1~N`br<ybSBO8QQC<Z4uJ*C$0Gb9!u{pDoGz;lS!2I#y%vDF1bLpWhv5%oP|>*R@{X@Nr%gimru5wVt)q~z5eIIpalf7'
    'ZM{toFi{3|GzS4YEF-OiG|=UKO;#6~9JEHXlg&_bOnObwpEki_d+w?`4zm(Y|SVKBb|MzS^zI83{p^kU7TukM`|Ny;J=&w-'
    'wTClxhJ$ST48pF8+ap2f;TB#v2nqy1b#IN>5f^u$7*Sp*1c$%GX_-iHk6k$9RrkYr<F}*upD#B9VY<k2197e3&CFey^k~tm$LQ;U'
    ';^FgRRGTvrg*{i&gOt0olM?U36?nVSv3?0lsd{LV+hzt*oGsOpZ}S*LHb#)I0rHhz*I`0530`r0KfebQ(G)ggxL1(_R+PZwGgAbO'
    'T7)LCsT_zFtcy(dpJVUWSYMpEUY}ki8+_S=7CHRC-?|0|cryQZP>otVS6ovdlz?3iyzi>LlSrV2Vy%GBv2KlA-IBa_UTjA7HdeHD'
    '*``gLyu5U{4&q4FPT;%*Qx46U8<uYX<v^0j!;4dbD5xygzApQ>PjjpdGMahvG@g5D(>+hDXwps1%O-'
    'e~)7>Q#P@d<7Wq(s0qMfKBEt;YCuSYQ_@g0jWK~w&e><20w%YtJlRo>$WgP5X94cu+PJPzbiOZ|HL01<4FzOqETeQ#@$B^FnlJ`R'
    ';6n5BAnwn^=F_gL{#$L`1O>y1sF^WN24#tpSE-E6=Y2)+qe}bgHkIirpb&`4md09{aI-eT(^j0gD1<{U`Z~#GKUf8`4v0fu39C1n'
    '-9HKqQ%h73GTxYC!qG(hR!iHla{)&GGJ2)da(EavGHvqaRatR9Zu^gi=2wM_po%w3L?hsl|IVmvERnycheL~J%+Yl{e@KD?7#az*'
    '1f{w>>|I4EcpY|FgUm!ztX*VO<eCkc1D;rgiR;>6Avi)9PQa0kPV$V*MO~p>lC4(F6fJ!o0pmaxY;X3q9ny_~ffS%Wk*wG!K#Irb'
    '>I$baqAt!&06<4vKx8r)zxSq(mZRJeME<BO44w&RpR$RLwho#V;mZgj-'
    'mv%S+FP}GzLNw?oDZunhDKzc%}|7yI_iR^TEKwV7U6Y@z9{$NJ4$|z$6-98x^cx5TvL37!ffRHcRKQj9OTfXcG<g*>;a54Xy-UzM'
    'g9zfdX_{4ys-#AJdKV!1$6A0Lo>QnwNV!EVZOGbO?p1K|2L8%9&!@V5RRS%FXro%EU`HI=x{2Ihr$m8jA>#4o{k9Z5(+-'
    'QaDAF%^V8Jq+yHUw^0sgL<AwW{7E38F*2#m`XPT;}(5`Hf?~y0}rSEiW%E*f_lsX;agGSBE(&%e2mI&lUT^cPD1O7~lnZ+rx9Oog'
    'Nj8a;hyRK{Ghk225E3VEQ+R(M3RE(pnoo`?qM5`pXW9!2$=R8hpDV?2n-'
    'Yj|FNiqT0NkxIQ+e)z60furSfV&x2pLyEnwyv#ABk26Tg`EXFMe)1@PWQ=PUn4{2tqpc)EXpZdN)Or=^6mthiX^?q>dn|zT(V<!1'
    'wtnn1`uaV!%=;Ls|<VPlESekAe?Nvo10NHh-4<MZUi-h-'
    '9D?N^A6tIZody!VIA#3Vlix>WH+<^GJ<4cZ4^z}K!(0IOKQxvDa{SRNZyO#UZ~qit3gX$=kqt@t7MumWde(XxJ1nrrOB`k<YLLZI'
    'x;s72BYeAMkGzh-'
    'A)&W5MbbNSF6#X@jYizL~uQ)HIU)WuVyhsw>?EazX}456(c0AxyAE7bctkSTWSzwpfwbO6kWs_ZGdUeRPyeLVTl28G6h%*vJJRce'
    '~lUy$AyAEn%-}2g--iG&o(;Ab02mR#b`ZVgI!RgYw2m}oi9q2n7Nr9#D`|wi_y3X#WnOO%osV<2C*pXD=eEL*=-'
    'cVOf389g`Ry2(u*=1+CD<z@1)FhOc9ixZ#<8G&?a4wD54@R7-'
    'nR%2asgjipMDwi7jx|Gb(1RB1dK03y`WS$_tOY*aYRA5dd)~m?(;HiVG3lR$vt3n|KgF^i?8|(rL+?PM|Jt!m}*tU|AP?4n1zVYr'
    's$-'
    'Fwg9bY^<fB62Z`vtbDHss+<vccLO*}T9|iwvQy3ddlrNdswcNvJ%l&mxz*r}V#=IN`hGni$0G?Pet$eySyvSzxZ6Q)C|nLa#w;fs'
    '-HSAcX%Em<6|oyPxY$8+=rs|^POPU;pcMsSs0*49OEARa)zI3_7oU}R?M!Y}$io3M&-*bjry@@SCjC5WDhzqNsEohGn-'
    'w4qucXc*VUtLZRxKR{Sjyzw6^yHH5ZK+9&LIQfT}t9ZF_t~8SS|cemq5^X&1pC4CxDh$v}gwRydwKn=-'
    'DSY6Z8nGRJ3lvB+I&Idr=Vn)ZJ`}IF&Z7LLrI6#3;ad0aKfLMFLu+>9RltLp-y?7ZPC|%gDsl)}S0A*fvp-gBosHPnw+qC&_+fT8'
    '$Moc1pM|!I<>!VwKmqZcFm+z+2Pp{2UdRo(4~<F_U5>JyjH&<FTvg&J?x=_#3xlpPNxp_=?v@$wE{xG)(J;8q6k(y#y44BMQx4Pf'
    '#rLTFED%;`hU{F?%uXy#_yfTQsGF(`?t#gmDT8X;-D=fQSizyU-'
    'X#L*iVO7Y&?uG`5HS_{SWQ0k^hnCqUy9+PKQ_P#zzd3iTrlKpdq^4x!M^+3dU*U=8>cKEVUog^sXz;oMjw959V$!5(RUJRr;h@`F'
    'puhc*rD7*DZsLppjZ(avdEePX8>aL{3$#5rQa7e=jYl?D)02tw@#U*Um~e!N;qu8_q#C^<Zt{P?!DLD_8>?YB%K+=YZ#`8+2=7&P'
    '&nwrMMA)vjUcGF-'
    '8B$+9zt(*hXae#XHy`hhUP7Paxf2d$HzQKK9>?sA*t6=4GDQ~L|Vo#2B;6P8WW6QUZ;boV#JZ)uAt$XRgSN$e%*dkS5AD%?e*1+L'
    'Wo6ev9h5;{qz$8x(eh??A5TnvY2gQ3;@TGa^3t@gWEI8KRhqzWhkMq(9x&#To2s00cv8bJ+QI}9p8NX;QFr6aHJ+JZsxfyH&uI{j'
    'ZV^J?h`{-(md)cfp6<brJ#kRMl(=4!9r5*-'
    'oW6eTlQO+Hbz%kh;F?1v^xJPBP8BU)+ZLDGuSs2x?WqqxstuhDuT74kQIS+a&|jh<?*#)v~=qaXZQq#8pAgqI8@iEti)Hfk1*G#q'
    'NGF(Md{U^!hBit{NbqeBE(+RP8{oB2H_D<(##Q{LgDGhQd7@;oR;7^S|CmsMP(t8JAMO9fv^At|AkHEYxugF>jz`_-dNV5-'
    '$H?VI9!Q)!e^GbTpXNMphk<UCdNoTB8|2$D@0!TVq-'
    '5Bt2N?cr1`L23he!qfgHO~)RFy7$gnqCpDy2hptr(5j<J))YkU)Z8(`pDu{CHJxg=!qKw%0?(|#BQo@~uXf~e*!0OFu@6_|zX+zA'
    '5Fh8dl-^QaU8gT;b-MoiDGr@5%$HT=GAlhl7`h5h0g^C#N2$H1OQ++zJ-w06#12Z&*pMMX+>AxK+zYg!xWTSY7}LG9Y7V5CaJ~*G'
    '--5MS4g%7ytIA#sK*ENcoFj|lXu{Mxaier)N<${?J~>e2j(CNPib$CF()?ZBUG+vz4{;U9Kb@w&%uW$ol7?hD6^Z-'
    'm=K4t%b#b9^2Rr?Ze$N;{lP$xL7Iw{~$-RueJkY}xEzs`k>@u3qwc3DizDwr+N!YDWUrA32NoauRXM-9e+FylTf>I-'
    '?j|O(jTHHp~U4`rvQJ7HLC<awc7{BO!=o`O<E`U>_ybvIIqa9b=I+CNu*ePz=oxU!NIyx9|s)}n$o~RU>M$>oC_zo`_zg7+}RT*D'
    'QlUtsho-!Ix<S^i-'
    'CDw6k0cFq}g!~rO`%C3|E0soj<DOc!4r8LTf&(mMfWZwd?a1Dz06d9dhf92*>iR3(S&>P?@@NjrWFp0|xm~zuw;77nr{6=0NsgZ^'
    'iDr185J1Bv4?gC!o?mH13lM)8(qlCNmp_!SpP~pfXAO-EE%*Qz;Qlz;$hU<~*wz0%mn8b?(2o$xjbWmIvRH1IREa6llasX+0uJ0s'
    'nK3{_xrS7~UblH4ONV(y1aX`XFIyJ?6(WSjnQVrqDPPM1KWva^TN39Xy?eFxviXu=)-'
    '>ep_JK$_Mzb4Ilv#nKkS|6fAiKV*<k4#dB}6fq`;UCkh&{x8WfELi8h<{&=ir9Lp`+@W>_y{->olTe-'
    '@pzn718iuZhg5@N}FRnY#D~?$jpuRZ=&iYxp1-'
    '7CTyI72MC2KPLCU}z&>C&2DsDwEgf4qclCX_Otmc+u2+xTsY&x`DS!{dlpGv&mBd|nj=nez;nA@oQMSEvZdJ{mB4WZ9iEgPC4g=t'
    'lR`<*GRaHE^aMP8_OQ{a^0_blFi*uwI1Vd?>qfW7w7~V~VgF^~Jg_p=q1Eac>x43??DhGZ^J7|d}k-'
    'YtQ+MByax=|Qpjbuyk(M(kOD{zIp#^#sg3cdJxbz`QSPoZ#ZkSSCV{;`@;u}0rqjDhP`yHz#DpaFZBwEw0NdjthqdM&I-'
    '%g7h1Y#O-Pbwc*@NAK@UVM1S;hd2Eu%rU!>xptSLY?uL~1c)f~MCDz7DbwCoJ8(-'
    'm+#>&{EBA4+b*d4BleBrS(n?%WR@I^_c`CMM*fq4Tb{dx}Ik0FOIdRI!7NaL`*dTzB!L>$a5Zz6kHDGbiZ_=(1;~PleRYVS*0BF+'
    '}l^QsM?V`4KM-LoUg!o&-N36+SXFM&zFpxp!YQy(~Sl~uUs$NeoU*yejdM5@?wH1k0SSzb^juc-QS(WgfQzkf@XVX=ir%^NWn$G5'
    '6S*+_{flfOY<s(Awl3?CaVM0X&sz_|TD4y*=h~6&M0WLy>t$`Q}a2%~263q#@rSi@Pw+*CsKs|@^i>)RizziLnZ-'
    'g<^>4Grac9gb@CP>UN6K)>p>goYi9u8B0U%=M?nmx@)mne>^gcy)(Fc*5B-'
    '>{NT49n~~y3%=%Y@B0c8BD8bIgSIYDj`N)VS_M}6s^|fzRaHU-'
    'L;NVD|V4WV=4i~N3Vz(T+SrW`levNti!!RxCCE*J?#kEovP5sK@?h5<WCVOqL4Y>k!a9>#zYn>UygDbPF`OcakPzn#fSF_W?0;pM'
    '|D-*u31Sxlxf$+U`G=7Nv+-'
    's`P@;<VMb#k`>=r$GTS<LJiZ7t5WxeRs>fYC$cAutv61lZ3hou|LTlgRGu=L9SPF<{A?OCRAgG=n!j_QrbF66USw%hxv7~d)u%m<'
    'Fa~VabQIvGdl?)5Pq9`Y<>gp}QiQT?`Hh68=Xzd`atwhv|o&pi||0&s`<cRoe2H&I=&lxHE<|qYg+EgN6kPHtI7DguEsmtUn9InR'
    '1Xhl8Q80-HEsPZMz3O|_VXaa6T>yb+?gj2{j!d>oSEoiOEh7~9ERe2d9gZTFF5p{)<?e!WxB1^;(glI&s-'
    '=tTUZwT2=`htzSop#;}Nth-'
    '<ge1L$Fb;P58OWfezVbkel>=F+`_sS?VU@*>tG3sz$QIV}m@1elszz)J*MVw}RdHI99ad<KC7WdvIz8bzvs1U!f1LG3gXu`>Fc-'
    'r>yN=&Xsxof5ub*v|FZNFQMI>|csiY>aPHDJa_>b~cYy(n=;KRE=%0?r^y{0u~67Zl&0g;7gdOqSIo~r3Ksc6}KDv9|Q4tKgZb}H'
    'P{a<KsuUKQd3tp<kDXbwc(N~XPBycfAw?dl!(PtTOuqr?>HMNqjvrQ_@8S~AQYrg{n*RE7_U&c<WyXrbk?xbGzP8EVHOr~_B&Q&-'
    '!k+VMQ87A0jiiGXpd_@<)i_mvqQt5H2n1cXJvoC@-'
    '5w9^x6G2%()%SK7j<w&=Rp2WImkelQT4SE(^v0HtmNF@98W+0SsDkeKxU_LcOR7Rjs9!12tHgB`iG>TK`<SE@TW#!$HmR+=7r8>f'
    '*Ru6A`@)H7E>D!NQ-oF0n)!nZ;XS_x$*k+6^(Q<oDs6#``Hmy8PZ>&AA8?&=ya*w(ldIl9VgZT9Nea;w+6vS4jHUMoxE!ZZ0k1ZP'
    'J82%$ag(^Hc)Ln!4d3G19(0FR*qS;M-3#%*)JhxVosdg5bw;rPf|12is$_;v1vr~}N&Vnrv!z!~!O6epa!J9lv3W~>!Ptz$t-'
    'OgLGr`OR?@le=Ar?26P-'
    'n>}5b{u5E6TjIlf3IXW#9yK!C=83?;DAwcwF)K0*FB?}Q*sJf1fmLbyz*3gllh_jta1rN&H!E&3}ViWRK-'
    '(PGbh{#lnSmYr4aT1T9>2EpjZ^fZGTHL1reO`f1{+1R~#L!-'
    '#8co3U1NHZL#~axy9LFtrC;M31kk5{;D%3cCql*qGnY^xg4i)x=gy>s=h*1V$h>plPj)26)FToZw*BN(R}w-'
    '(KPL}q}YQfd`uIy)v$uwn{3)3a;=5Y`F*;nSBq@zAj?LFF||Vdy?}k<lvkJ3Yk|Vm4&dIWX}Cquvg>FOHfp<BU05^<*_U8j%Q(~6'
    '8h|~1`&2UI3fjVnZES?JCe+m&iUKhAOY~r}G<F+P)u<A`NvGRxW5VK_LfOC!3VwPs@GH<W!@QdOUH6!5sdqzDw#l%08E*PjAx8E#'
    'UxsK_65xr8!|d<jLygtgcsr%JN~f+YkBc<D%mh^c6hll1pE?%WZEp;zc_-k^JNf_^_WYIE_-'
    '^77y{N9lNFU$+2Z{X!*@ERefBO5U{{xZp*5U'
)
)).decode("utf-8"))
_V58_BAKERY_YARN_ROUTE = json.loads(zlib.decompress(base64.b85decode(
(
    'c-rM%U2hyoa{MoRo(Ih*Nxx~OIj?Zsr9eqHI4_9B0zSilaei3)&G3J>q#<W|IwK<@vzsd&{3K#T_Ec48Rb@s-'
    'M*i|YSO50g?|=W>?^ply%hmhWA3j_?F0TIlxBvXt|N8vF=O6$6+wcGJxBvd~^Zzb}zxwn2!^a=9-'
    '~Hw4hfja~_5H*B+fQ#kUM;Q;Kki?D{&)MhIR4Lv{r>Iw<LlAKKke`Cf4*8QS6@E=@!iAz%KhQXLtg*<?x)vxpC9w){&2Neg^xe{x'
    'Zl73@*krK9rhnS4(IcEHQv4X^QZUEPg;I?($g=Ur$6{;{Ogws@?n2>cb@W6fBX3xP7i(>`touB=bwJ~^zQEMub*Gy$4_4t#CRiN9'
    'PjU5|NQav4lV{Xdiro+r>8CCxIcfvoBh)wi6vUNgFd|exPKVEyW!X17Y9fG=5<`T{<y+RJwAQ`7jv}ogE1d}m}yYt4WCW<Y4wgT?'
    '&}bqmN;7e%e}+%H~s0$!Emu8as6f;&Hi;b48rR<y-TueqrZBw(dDn_V)c%{HPa}b=8x<L3}Uoea~bpK!b0z9u;ZWp@A$OwtIJ-'
    'L+|=jA2YVR3nD`p>3qG9%;DO;M^60567Jqy6J1?+w;isuf_w-'
    'A{_y2WSTI+URo6}?SWgC2=zH$0$9mi9f)bSIzSf~H%EY{`Uk`<Zj`GdupcihPj?6J|)NZe-W<Z2t)k4-'
    'x|sOQtP;NK?>6FBqrA@p=34W50vqtK~#{7>?{coh*x>-^m4?2Vs$e|NWk^YPa|?H@kAyL<O9V-'
    'E%XKlM`3UzAR>XCGtmfYFOM+2x1(PviG+x@yCp!~1qUwzsE8icA0bx3bYr7|{l}vuHhxmvlNG&ch|Xi8s8Jc2G{1S&l^HqtDmc`7'
    ')Sr!M%OBe}8!coObDylXNieIS%HT&-u8GzN5i?-%B^IqwxP}a2=mw-lvUDpiSzbu;cI&*4tXBo%9TdLlci{KScHXmT_nr&UfV@fJ'
    'nIFC;=~wK2gU<ae+x3X^k;1au`oBhEt0QViSf+NuL?rn}y*Ln*}dxlF_2^$>*unWP_EH2Oi<TpNf9SkFOv8qDCAS^z??ntMc)OxU'
    'y)drxDI#tLJaH@QO#Fuij-0^Xr){@|-'
    'v7s5z}ae2?&Y*x<}e#PY`J7Cw@W0f6Ha?JfW9qX#l5RwFVOc?&*H7U)UKC*Fc#Ixp&ctZ7!U<7CVNpZF)Z<HT4ugLXek4o=|?vfU'
    'c=)A*~WZ=jxM;$6((@a#A}eAvTF#dx}Xsi4t=G)D(E#}{HehMXIn9lYsqStg?P*1;l?B`m#m<blGKGY)C-'
    ')`9QCe2SLu#vHBiwNoDraE+eZvQ7@C_)W}jhThBC^j;)X{0#e@Us-NC#py4l$BC>x`XWhm?}P2o*}X(yiYbSYi?e{N9RDlSTRJ`I'
    'gne4Ddc)i5Jl9OCT@YVJGb*@Y+o~Hj`1tb*JlubL+CASt2J{k+QR;uycO2LlAdA4iXYg`9e0+F)_+kI>@K^9%aq-Vv&-'
    'B6?UMrYR$s2QTPH;8or!#IIT>eQQ9J+5E7mF+^a6@XiiHjgbCxj>8Y7PYOJ;!#_p*%8+KUqn*KqtdY=g$%-#bjZ*e#elUf-'
    '}g(AiQ&mgwv@fHqRSFe!?vGwfDTaUe>f}0I~pi-'
    'h}lhUv%=D3h)oG$88^6;us{D+#<ak*N=ZF?p1NPHo~!*xLqkGRrTILa&c~#4$z0Zxr{xPh3_fZC+|dv46w-'
    'Yr8@C@s!mDa(Zv@wqvwYl%Wx-kvM-WVG#7mpV~7AxtfUum^x#bKdGZDZdw_gQ=V-'
    'A8=w4$H5CL$V!vsAVzgrXt74ooV@(IjAU;W_Oz=;K!O~+_JX~wvuAUBL!HkDM&ARjt2#(jN8azD4;dECwnU>(!Dx@q^^+p~D*c{N'
    'pVsn9p&j6?34fpcJ0aKNJHS(x(+5x>Xgth~Ba0;6#!bxH=*pm}eFyJo)UWnon3Lj&GSmjh(1&7OY=Hdie6Dt)E)FyNGvLkT!f^9;'
    'hGn<LzXkHA9<+s?uB7!UXNcgM0}=sroW*_r{Zp*syg1)HDmt+!WsX>$1c;o7WpIDRq^aLITXJ~KJAN=ZD=HIQfzB}N6nqVdzv@a;'
    'U7UsX6hVDy#*2y@EsS1InHH`C>Y5*%F=#RyN{Tfy-'
    'c@W^lIBf`Syv>3T?wv8WCEf$JJ5H&7hAKa7&mvo4M6J1GHkQAEl^$!<JI@@SZcd^Ml_dWaplxhX!ypzF3K!<u=jJ7a?g^|rUJfcU'
    'L9Q;bbcI}Wl8u$wMo+{m=CYW&Xk{~T7dW0nmMb^mHf;Jd1gN4aTS*G0puwEJwcW8u_RqYh28|MJ=U*?_l22y-'
    'qwrkTZ^I`G(rmW!8=IgqCSF7x27gUC@YrZUq3JvPst&g%YZvUe$;me}Y@}Ew(;K+HJnlp&cJ^gUH%0~D29LWUoCFdXT1xDkCIkG^'
    '_0VE$Mp<42>8{V%>QYE<6ln*&B=EjW63ld>B4VNqet$v4kL0K%x5>(z@M^%+zFc46qz#H+Gj7F&3gm9F1e)(fRHH(?~O(x8bj-'
    'N*S;MeA=D#}b(W|6ELVLpsOg@~txdHe34Rp5RRiinyEBEo~#C*(U@zINEsC*3*vN&xoQDZT=HIHzDTb7easQZ(g+gqMI9JHc_zi{'
    'i4#dzPxV81Xe?`w`kab>7oMyeVM{ncfR&8?ed!G0IQ9Z!`o{=PY%E`6W<!S%b1a56XA;U@pg>0b>M1iUZS+EO39GkMy73-'
    'TnD%D9A&S@as`=szIecK8>W7)^>`xk#aK79fM-8{xcOSTQ`E%+6aL^zy=rv$y@;~OSCEajAws$q^Y~gF1Ut#)M@H?6P*WRr@-'
    'i+%(Hwn5>W93{ZAC2%wdNW=3tO;jma>K%lq{Z>&JqErX%pG-pJW8le&H^5t{|qEEG|ei{1fIgl>xH5mK0;^nx*tliyJk7z6=c91N'
    '}>iZ}<#(6Xq)T`-'
    '~tBmM2MwJnmmsM9#5Q8Hat@czyNK%^NFiXr1`D>cR!3zo5PI(2Q1?P|`S&d48dCp5^J2pbcrY`!q+682Pmm{e|-'
    'R6}l+`@TGEk<|;(++)YYI>pgu01P?<l#-'
    '3U^e6iUe|7Sj@6qd;Av3B~pf4``ZzKY=>qeOK<|1L86F8uX{Mw2rtqAf;G+Rb}A}rXn|Hn+uD7ZyqT7Zmic%Iw!GDl|Trbf$>bf<'
    'ifR_5n4D0eaK6jn{%iK4D^q?>7}1SeRHkI2EAjl9-*mY8I%k+T(Rn22XHU9LQSU4b556t;6$%&)(qW?*K#d?h}w95Nn_^tV{4-'
    'V7#|13_vyCBfIanGJ#<{B9|Vp$Yii^G}}4!2ijeaZnZKD0k3M4J;ulz9Wg4GGTOGQOGbvIlSytj|$Ww7n8-'
    'B)A$(_0Fj5*+W5>_k`|G@ShQYArwtE1q-'
    'dtkPZdkGxHKhX;DxN}$}EFkPaw{^x`x!k3Nm=*fS2iyB(fjg>bm6L?c)rZ{)=Lsy`S`*B~E=&)!T(2e|o|pjTGd~W1*a0tAKck$L'
    '*wue4U03+s6W>s2q%e#($mO0}vf3Gk?)fG!9V=18+e+VAbZbDR`XG4r-oXCh~!Xh5w&PgNXK5?&>m+)ke-'
    'E5F?7~s%eI2BF3?u@J<bv4-EWXB-'
    ';s<=QEq*G$eP$S)L9IE&hP=c7pRg9OdW*@mUqdj=qZv*v7OY94DkUjdO8q8iZ@J^~hCVcn2qqir0di>imt0N$RZ)s;~n|0*@K|CH'
    'ez!Gn^*r0g4yz4Eli!)ssB-'
    'a$9ydbU6t+Oq*5hoEJ<+BcQm~*`(2*Usf1*Sp#M)1;f^;bsp*cyPLRusk3EhTnL?x?qzo30cJ%NxU-DPct+vYuoH>Owog+u0y1D('
    'PA1&bG*ElUr-9^gI@-'
    'G=C2{`sIE8qRXM4n^91z}Lu0+KtXe2+_w)dRqhuzAUjgGD)I4OPUc$&_q)$(!UMbA+w{SdnxpX2MtM(b*qY?7WX5w(eXs$rY7bRB'
    '$j+(K{e@81{MCtXA35?`i!vRvcZ>gBQ_2)0_!j1Hwf_0}ag%z<)A*`#HW!){eXY!kj*-'
    'dy{9EYkYQke}&QFm@OeSuu8!WD<3JY;LXeMc@%jx+KfF(BbXv9Bir`b@Ny#7pc`=7yK7q)ay#m5SI?b3vucoUf_ekp6JNCa202T;'
    'Y}dU#tkD)GLnsX(^6kjl!+5kO<b^_cpouenXJ5R97M6bSp?f(zB^hUMD_m~aA`pn%4}YT*y#H%*@P5dlWRn@S!1af`+zbeeaW_HT'
    'y#Qb`VXL`sLVcz;(4kV+4){mBQwje+T%1OJTxPx^$Li@H3*Lnq#dH&1ILtH^cAvUtC!JO0E3s2Fe)14#2||H>=8r^jg6_Y4sI!wG'
    '-O$v)avCPZGmclM{97JJT6G@;hr^svlm42$V>4#UJ-wBMC^8zb0Ojz00*;`ISC_-'
    '`5L#tFW(iaW)&Jj&>)X#G)00z4$gvvW>IUH(yQm@8!&n>34pOIIK0u2@ZK1mfi772yRZ*NgIw7K`jACI82&p=vW6>m8SJkM^ng4Q'
    'Orr30wFgnW?$5`U;5LHg1+yK$K|1(FSoIXes&#+~xH>fXi=nO?P1w(WI6~a}BF@r>V2zSmo!x_B(}D#G8noI>&2O@15L_rge`R6C'
    'mi=Le5r1kZk;b9<MGY$MB6M&T-'
    'q7*)YKFsl(hGiCZ%!88`7I+3<Q*Fpx4NC7pSYFRXCrnRfTjcX5xi<m3p2h>uU)2%7xy$Q91T;LYI5=(_^OiVCS!dtYIQS*;X(17)'
    'bP?nni|~A3<n<yk3B_slk&Z)lun^B#E94l-'
    '{&{NyrkdkYna*F_4EeDnlNVQ6B>#RsOIH*1}j9{B_DC+c0;Y(CMqXZARjwMM&aTXQy^}?oqoesWcuCyXk|J?q4(1v*Kc5QQRIg-'
    'z9uozHsQ6bntn9!3p_vZWm~#ZDJS23<O_?DNu$7pr*$V12fPMoLH2WmOgd!^%pZ59u5(6Xu@NjGmO!;c=1~?{F_mV3Op1>Ma>HTI'
    '*pF$`C56~yAwFi+UMqw4(ts>snHH@##b*U07L-tU01sQS=W%ooQ_hq{>FT{(l}%%^%v?+2jP)F^FKfYjE{*KfP-vi<AZf^NM<tzz'
    'gHfT-?jpuokS~|<g*sMI-D+JkfJ@0?<6QNc+qJ|TSy1Ab<f>qjB+mpdQzj$O=p#g(HxC4jMG-'
    'G<kWjOU>?p#+FZi9yimIV6CrS%r)DAMt5v9dTQ=vz+rQ<lMod(~b%_MiBJKU&2yPfL3{RXLS7>}dE6qvw8DP|sdm~xEEj{XLYCHA'
    'bQ`M|SFOmWP|5<upcHDTj)qDsdDhb&3+?0^Ic6CdO0*`@sFKfx#Hbzkrf8>a}AI`E@RT8)m<>v-'
    '8eeVM)*3hFTo#H#B`S{%<ylE5}GZzdrVP08VPECQldKqp8dnr3T|j=aO?Q0$G!KuheS$#ZU7zC=W+)$dB(^(-'
    '=#Qr2hJPNU8%g1p4t<>S!-;8cqhQA#J;-@c4p%Ib2({mDds=yGdx)w56Zo-NG7Xt39_R~nZ=+|_6n(6m&hGEHz+p5-'
    'l=>}HzDRx}VgV8KM3)zdxmdb(=mEaQwfIyiI4g*n5{7Aiz*#9s%x5y5EH{%IgqE9V9CBE@QV;<TcngJP{VeO42{E<wmndts_vJIn'
    'N&;6VXJC>-'
    'MoAy_V793p@y#<q~^7c_ZD<2KYJS92!*J^4$x6l>w0ie`#+iT_<C?aSIuxUUV)pu$sS9s$H?qUwyMpl`&n(d$UCn&vS084W>p&St'
    '%;&J_>|;v~&R=fkzAH9xSXCHn8B)1tTqag>2Q0Z)Wy0L8AMx8~E=ng*9=&)DukBPCI*-'
    '&er_h!hebsfbv_WL)(0OzzEHBZb4Lf)uBzV{von7TyMwBV#kl#2};xD%uB0FqPm{nK)C6rBru%2NU5vPwX<X_6s&YSmU9cD8q+^t'
    '*8Xp;r8n?1ePM#ddYU20c;6uUZ+z+VoGFPcoSttXD<p!H03tDus9~F*?yS9F!y6PO8Q{xfkYUTY}%(0UpqYW#7tBWUyG;VUd2*|7'
    '0C(<<gw_=j0qxZey29Tri3~gO)K2TaaUG_s(wa81+!qQT2el;25Dz$S~m+l|2kbnExe>&h%!sFpKq@`K>SKuc7R7&l(k`WJRRorr'
    'vNTwrf4|n*lCEvGyaxL6Amh084wKXAW}##kX{ZfiC@#?j(Nir{*QAZ$K(`0!&_3nZD{uvx0V|LO3DYp9bqV~8E5MVeb!XPIt_NHe'
    '0!t!thm{&f{(!u!$8Q_V944<q<+4V>tQ8PPCnf+cSqH*)mOAotyG5TXzb|q0g&(raHyCIn;1>AQ6!DEhWY8EsOn&|Y!a`_VB*V-'
    'xUp82fh0cg2E-'
    '!vxC_n{;AGuvFy$NUJS};ty|1me0@E8r;Xk`~Gtj+~hB+9gB(r;~RE!$Dvn>zgPQ+AHyX!2t0<s=YT#+_4>|KGKT!(jg|1qC%;+V'
    'HH6Us}5v^z$dg<Hjf9>94#>gj@p#dN4yqbRm%7_n?Lyw>uXeh8@m6ar}`&<&h(3=H=XGtjZ!-'
    'slFu&zh4b)I@ePt$iST=VKW0h2fP48Oy3)K*4p2z44!9BNE=#<2$Z<VLba-'
    '2{S75>8MwvJoe$UuLHk*GpS9jMYa(Vk(#O9qu#NG6MQF8w8$Tu$7YSU1P+Y}e8Rgin*_m%)Pd(0@mt7?D{3S`3jFwR4x!mEN+~P1'
    'JGLj!5@Ec|<sbemoPO%W)N6Z48<~qNfx#E`BI;6F<hqcM_p8HzVa3xz)Wm70#wrMl)8J4FY(_f<D+cVAOJiy%>=!d|TpO6N7fbr^'
    ')aIN3wJagSs=?4n!Wu(?lXq%g^awfI!XiS2XSka9U{af+ROw)1=d`fF!o;i6BTjTm2#2P{f;_UI8T!l<a?~Gk+$v))MJ0zSA<0w_'
    'F36)Y4WWb6`7&>oQIi%H?di>uQlLoDER)lx9_v_)K$jg&t74WCueay-<>hx5sE&Z5!G(Vr(=OqqwB%wTl=TYl&vKj|cc-'
    'NQgaNEqAjNsp-=<Mgl-LT`qZVUis@7*!J*3EEd7*|G-'
    'wm45sR%+STZ*@s$`Tj;s3P?gTA)UaCUCz1`vzqPWcoFvCF8FwRM`QOINqmuEF}QL;LtR9{Dak>;y8+L!54&Dt;$KnLJ2ZW#R-'
    'ud0`7)me^o+oRDBa5jad1wX^j(Tp;@P8#-(GdYX6)-'
    '!jfKtzyzsIqy@CX;l(BP_1+7fTx!$KmASdfMCtSn4zDi5^&qaMbNwtYHOcyE;B1$3(A0msSED6?c?p{4om6?I(N33w%XL!_@|mor'
    'Nj0>YE~(lUrCjQASCT0%6$^1@TgDkA*IaL7a2^jO?iO~#ge!nc0n_#rV9XrmuV{d53(ejq-xREM6zv$!5nM-'
    '%<))Bu^{EY_v@*LNQk<}4{1h?EZZuB<nU=;(>c2ukVDG95k=dA71Q*zcs*aDq0l}*o8VKdXwu)sd;wI)?M*+jDewvN}wQRVkfo~m'
    '#sda>@mod%M`t=_bEDG#l7cpWy9ZRToONmxP8*UarZCYUiFJNMS5Hf@@BU4wNxo%A&qD1VMSb=bd;%sqm=zyB(l|sn8wsPW$oJ2L'
    'zDqGUj?E*EYS(oUQEtY;xkYTcMcE@E4nghNh4?&p=VyVg%Q_a|F;&$VmA|~p{9o){HR%IpU6#05`MREXj|6kRt1-'
    'EHo@Pjn)N}x;W+cqJH;VT|x-RCJJT)K<spSXrh!+jD<-'
    'R<9%vvjU2wNSu~t?=3KVIYG2y;j^P**;ZD;8i1r#qk!D#RHS&&ap{>i#Y{XOD8$L_M)Y8BtwZnbZS{+Eek;ZKy{+BU<kP-nGVGW)'
    'Kax8i$5|njyMrmmCeL+7gYb2<gqPjRo2F)E~D-'
    'djP<A@(<AOJghhmdsZ1k=)_dzvaBlDn&}kelbC|Go3G^n)auXf!+sA?y3z+iC*`ids$80?0&vNzHke7j-'
    'pD}YS{wh3b2@vBk)4p$fCgQ+C0C!gbX!0k_Q7qNs@oXy1V5vw2Qwza_0^OBpTXPd=2VHQ4C-'
    'Y&n7}{{CGQhBSN=)5uUJ1r}oO??eEbfRLd9b?`QwKoMyBR0vh*-'
    'W#N(a}D`ftpxaPBm+Z=9Ec(1@w(Gl2!>N{mYl{}>q)1hFSvGeAol0x1Rc7si=jo^sx(Xsh92DX@r6fRqKp!msfO#&gsy?I{Hx@YW'
    'WzlQDmLHDrezRy^_VvzKC6(P1IEG@WFNIQ>A(cCvgU1lPs9N8-7PBP~)_srHZ2ch=ewVDRFM&5%k&h{<^nNR&L-'
    'R&h&k*)n?RQmw#vXrV%ZdU+V_8-<#W;d?@PB02chl6x;5JRtqxS+x);)wh?WQ_tA3dCmhC?xcd*R*@0esG~0`^fM7@kG*-'
    'g8vV@cdlkG4?%Z^!*@QXLX)3mEHWoMgs@iyI?Gmf>{(#24QI}S!lGb9rSU1>ckUnH&pEtc9iaWsviBRtPL_&Tk^hjDfr>=0BmYl^'
    '>2Z`FKSFsF;DTbw<MUUcG#peYvwlF4_i-<b9@LCmL&{y=kHg)+bLOCTBifWT)uYGqq58-'
    'xkaLK7r${93fYnOCiaan0jRA+u;ua=6XmU&O~QV~NcqS8~msmEy;W8JF?D;#66x{@Z5e!c3GgH4GC$}BiIjZO<GlU&h>=|F*VGi~'
    'C|nXA(9G4DOYIXOS0bbva-FRK}=M`*Q<W%x;I7_Z867cy}$x%u2UU!fll_cz@kUK^=7G-h}RO0r{I!qR6-'
    'f>M1^YD0=?>r9jqCGuA9;Rua7V**%V{<;}>LDI6Q{-'
    'a(ZoCIXF<c)JW&lY&vrxUf~V@tw|NOV`YmVmATo$A*q=wNtPOKeu<%IV&GUgd^J&b79G{;tVzY;ECQKfUY637JZtr|K2@@^n<Ii?'
    '6N*gw(h)(4r6Yf3%t>-'
    'jUTTa%xj%E{=t$iE{+5Cvj+)OFY2(5J=?F$`83CtxcJoAfzP8EV#meOG(mRof9;KsR6HbQjPDr+?3^QK;Q%KB)5u#71wJQo7PDb`'
    'jX(Kr}+#I7vf#X+V?xBme7sSknvz?PC*Hq*n!-'
    '!;mwpg+!sXkq?5Y>9kue)sfO*9el~(MytHNil)8o;^#NePB*pE<EtB=6qvo4gbT^Su=L<Bmv@$E1)MxptQc;T7YgD*MxB4RS@lEZ'
    '_2D%f&7!jjWjI$Zt6SsxUO@%f}8+`ALM4Ox5r{P$-'
    '18$~l0FR)g`yjzsD1H%}VMT=IH0%%yiwvDhT9Y~zL@$#xd&Ybkc94+LAy$Jj&Ajs)Ps1kT2ODn6uFuy4R0Xa|$KHu4+rkOPMiCi;'
    '*w!T(78e+4*Zo8ZgqnQJ1ftAKXvJJ01glL_V6fc25c8xbIm`sqJxtyi;iTFkrd$=vrl6j3_4myNo|{5n7;B-'
    '0+Zf&VPJxl%)Yr;5F=5&Q0p+>}kR2`{{)I~4`!2Yzf?{;CHn~c)kj5_LQcA*kGK8wT*t`iIz4^kk&u>&p#FX38$SXLnFF=P;vHZ#'
    'JfxUigRSSkBj!^k1z!|N+zf4XS33t@{Epg?hnnn<j5LLu6+WX^1GHWa-mPeR9eNd|{CnEqEYDuj`zC^>3{eTN8DKU^0fTgZvarkk'
    '&G7$5$TQ#c10t}c&vJcGTAox~wN5aE~{3PX_j4!^9YrR`F865FXSu|Wm$0uchkf(6m#c@)kb-'
    'D`7O{J7WEUmV4>hV?VCO2z^KBzNa{lAnIc1#+73GmqAiW7K;w>2^qczqLQWaI@`*=N;+43Rye$U8@5H<rFg)&@s}knXmp`NHg_rR'
    'icz?N$|C6cqLCxh0vR3WQZDEMO_+uF?V><6$1aQlgoh^S@}qS;J?c)I$DDH?xk%1#sB__AvMXD~dRwe^VP*-'
    'pNeGv95XI11GoU8y6A~C4I*OO?ePli!t$+hC~-'
    'CMK+irxg^32+?e6^yR8X)08?SYyux`cw8=<pq*bEI^r!*5gRHn=?bjuXV39!0;xoyHP6=;GDfGbfZ)jvD#6lt)`?wEp@pH(|t)D<'
    '7vkkldW!@|K9WrWO|4a=^-U3=cjMYo1LKw5cP4v-'
    '4^?P_;u|h}YF*9Y5T1A_EK8ccF51ruTc*Ad?CX>VBU;}5y0_<w4^106(VYQ?TD6v|v+4?EUlkF8tA8att-=-'
    'Il=PeMFTb2$Tvjwv#Y<u3zV^$#N1JzCzXwXj|1riP0n+&*f*x^{BBg@TT#V)H85}5Jm26GS<!)=u2X?r*(WKIo>8qIA*Kqys&l5{'
    'X%UO*F8Bc|f@cxs8VxHdep0XKHKNa8Lr+2m&Q@#ld(+<$yZX1@gYWU#dn>|u2FNwAhW7sWtPR;4lrrqfBd9wq9E(P5@CWLB_4I%i'
    'Og%?|EU5DPgNN>I8JD=kKHj_R$IqI6+}ChS6G$#lu_E;%hwC%WyUpRS<SqHZqinVH{msc;L$SS&`_p2A@zDMdRHh>$G$-'
    'AqhLQobqyr`K8m;tXFc=jpQP_T6}10joVrr!!Zvbp+S{+55>(us#{$Elo=jC%9ryvn!XM0|0VpuK$|v0JJd+#Oo<3(1O$m-'
    '3Fj$t15p^ee+k3J}w{tM9Se}b!`*bdyJH7cKa4Jv{O&+=V!){yT!DhgOryynO-'
    'f+q$?4D4h$PpL4*Vr0(96Ehj{KaIL;j<Uau)LK*|qZ)iOYCXg1*d1tGW|cUrx6`tw|?%ggd77%Q;%wkoPIc_}LXPYeiVSY`{S>3D'
    'F8%OmcJibv7JYrw3Ww2VIm%GPb@XBB9owo*1ld#KYer%vsT6bk|TW<4`?hIj{3*TZZp{j%jnt3tgelX;`r__#T8p_)}Ea?Qs~`Ee'
    'x83LMDsN4>h#g6Hk4uF=ujeT$;=YpL8Q2%{!m%cZ$hWLnlC;L2{Mh^-J0o7{iJ6nwGS{EQD#-+jc`Yn`p6y-'
    'V@jEQRdUR_rQ5r*sc8B`BxGj3rX9x~K2@JAtX`uzVg}o@yHh0v5Op5IDP@zy=O0X3^aoE)ipD$8^DHvEcA?;m*RQAt*cZ^2XE}y^'
    'kEJ=w&HjVLab*Q?-&>Xfz`pL^HCjAmDe3qL{Kpsi4dzO?leHJ#kQ5N|uP-'
    '9^5iWL;YM54A)MHHOo1peFvQU(N#NudX6H!hVNgJ8fO~ImgF0GL9EcQBme04=TTlxzosj5Z6=sFF;$g>#YX_I!)y}9;tUal89SFV'
    'bd|plv`_r=lF7JGge8`C36y4h{<rxw^Hv~bcnSon#t^|qaY@F1uuDHAJQU~`br2QV*+{nBDHS6XsvIuQ@Qtefl#M8ai~{RZq2)HB'
    '$nYi}1iOOZOw5=^j9;W!!Q527(Ub@UMRT<_Lp&gmDKl52gwdN|=mcKcveZ9a=(L5*&PD<`qJN4#v5u+-'
    '!&F%(KmK~^&5J~HEnkH;J0#q|XEudV>1RD};?lmzSmFcYJ9;Twt|XLBi<v%o{eeAhHhxHzJxjqTMgK`%2d;@2#udvn*wg9Z<?_+D'
    'd&cUJzI(bqQC`wfTdvR%{O(o<mR6-'
    'rgBgJ2=%zXa9UO{>4u>f7%<EiPznP8YlmfgbXox`|hSHmw8B{_!4e_T<x>30Uw7P!JTdS}T_`)<@t^!RCRckwrg9e+A9)`SSp;Kd'
    'R)oY+LA>Qze+)nFUh`|=i0C^J8KZ13XV(>mp&jTd=bGb#9TBbo?sqci-zMJAoZmR(Lr_IVUtt-'
    'S6tRSU>WqztswmVr}^tAlz7Y9aI>!d<ApIxDcG6z69S}SZ4&-*3cH)fe<PA%D$DN;_E5^w~9FlXMQu*jh$^~Dfu{^8TRySKl-xxa'
    'ren>cg+1w0zPS|3Nlz}8VIpyw*%94Ww+T%gBpiUI+mu?Wk?o=I#~dLQ>IfCV!-*U|qO_~LV;3cukVCAG>dVov(%HFvl!c>rQ-'
    'x*;U3d8pd9F#~<~rVulRuS|kP0sr8ZLjCSx`1RE$FBzdBxU6kJPl~(P@|(!a$N#bo;sR6O<uJo-g${-'
    '7g{S%`@?gd5=}@_GgCJ1kx_K${DF0lG%9Ne(l4RC}D*6L+c;yG0|0k#-=sUy_F|)LiziY&rABkcn+!rFdKu!qIvN-'
    'L^eO$O}r@j&x4nyQlgIC(b&%c*qo?V_QHW{h~$_CSB5k|8Xy&!>g3<8QUM7x`wiRDI}4bJmoZ<>wPyzmO+Olvuhr^Fz0AI$)0gIx'
    'SwGB54YZEFg)bI8MTV#Y)kENy!9>YFwpc6tjJ8|Pe}sV`93GV|zN@u&+ItXASj5ksyqiVie3+)BcRLW?YHP)?685p`3nI2U&nJ>i'
    '8nX}GL6Md2`26Ddm32|Gn3KAuCKU8M$+6QA)d6o<&Jt*(lWdjE{j!v=QfYl9S&5wI1w<G)BxK3pJz5*ASosu^(s3!%|iZOL0sGxx'
    '7lLJ@|zje)837h@(R!!QtrqZQD7pMzp6M?grn|HKE<-l`~KDZy4-'
    'vej&OHWvUF#S7%M&<13z(+DdS9UTU69;e^2PL2U4Frsc3hRhTAluu5=e{C#gUz(?dfI~km5==|65R)dfNWha;r(H0LynPVo8p9?!'
    'LvyaDXLMBFXg+qOC!kVKV1nm<$H``ZvQbs2{^IRDAHy3xA%!Bx(Uahn-'
    'ZA<G<hb(Mcr}Xa;kT_dB6w<qom<42VQ&VcsSfQw^Z0+>I}!i'
)
)).decode("utf-8"))
_V58_PIZZA_RECOVERY_ROUTE = json.loads(zlib.decompress(base64.b85decode(
(
    'c-rM%O>bODa{Mnm^Pv7<lk`n1_3j9(848qSVm%-R19%Ms#`-Y!&Dj5LX~^z={W3BlGV5_hi#>@TTd(U?WmV-zMC6bEckv%T|MIuL'
    '{&MjzKVE!z{qf_)<K@MF{`}wn{y$%S@#V+A{rt;+{q=vp{`~jL=|_LKyZ`iE_SqjV{_y!PKYh5rd;9s#r;E#rhwt{Uzx;dkc=_~~'
    'kNf@G)32{*zy5yz{_cm1%hmep@4tI@zrS#Q`1+97KfL??_4_Z6d2{!0ak&n^{`lQ~|KaN&W-s)x|M+S8K3`_z-'
    'J3su{&0BG>g$u9KXiKi$*<-'
    'gKcA3~`}glpue{RVe)@*vgP(`KIv>F4r$2mt_x|lqUl#Gx=dTlDtVkHghxf04_;g%@vjNSXJ{{QcX_s=`U%ueY{&|wb6kWQ5et7+'
    '9e?MEh>DS<egQI`*I?h~wTwzh49)AfZb2jsnF+csV(4fc)pG^6A_MR5**C9MlakTuGTf@^g{qgI;a5g1z{uUk0{&hGE!txx~l1$s'
    '|f4$h~^5r?3y{AttG>Yf<NA?2-'
    'F`KQWjCpopp>>+<_~*YpJ#D^p*+R)peVTl*hta~sWzY+JJPW`B!%yVVqcaviJ^RcHOkMbCbn2czG+qB+r=>M-'
    'r@1*kHlMc1Z`3!A&(_m;YA^Nl8#r0VzjY?-'
    '{Qr^}S?c+d$y#>Y$q($Y(bGuWX6fW=8`;lIJ36SR)3o5<Ck_)h^YtP0d?QVseY~U4srK|o^1OHz5l8Fv-'
    '01AhpL_TI{r=6TpZ>VN|Mc$tyMLQ|DDdypOF{pmbebJ}jL8FL3vsl|k9VKv>u|hk!+(eO?PhLo&yN(B{^3*EXa`2L1@0`G4`Y#z='
    'fi2Z#5eJVx7H5I(K5@Ch<x<vT030^0~g%e`@0Y4H^6b1j+~^E_g>;)Uih4k+vpn_+_yb-'
    '%Q_1GOoQwA6w5wsb^>iv4}~3v=V`qwD{Ch`1LDxc<Ju2VJ-=lhnuhaTc?cj9t~g4-'
    '3!_ie@ll*$5=UBNjFTM3Q;gx%q=MLlWu>IgjPA|CaEZ-'
    '=#TqhNG(Pz}HJfa(^5ua?IPs^VAM)Mn`+rp<juU!ZA+S__{vpmR8tQR`i`eSv8_vAqS?H^G8O!<g%ocghTXobN=O3;kydJi=G81!'
    'o^KuIxNyh-daf<eqzxwEbEETIWGG}!QK28?sNy{hRf?+x@>U?ZyRk7n_ERsI)PjJVHv2F(Kev}-'
    'X!X0G0HRz}LSC4O?o@e4+%;50sI6ZvW(@Vv8x_zmj(StHaCvA=|#CQxjH#$3b)8Vp8L~Yf<B#|jBEj#i+;mjF_v{-fE`!JuP<-'
    '0LQD}3$fqd{Jy=eBH;!zq3f^P8dfvN63EnJPY{{Z31kn@;idSJLA|)*gM4B)a#L?a<jh&%hK*4l@_$5~6bauTZOWe9|%ZX{FU0-'
    'd5+iW?AhF_%eH=f*W>Kb;BmV{xSpicb}ej&$pigdI`rU^}p&n4r~liMd05vS)7lb?q5IrVSj)B7w}zi@=sgO^uiimD|nrfH|E});'
    'A+rMXV^SA{X<DObl*BI7MWDwhSc&VZU!kjA-wojb0C24Ik%e*<dIqY(MrMvI-'
    'F)Y{VqwRm?$jQ@0fy9a0Qtdgm+Gna60wGmRT|6CoFPbd(T^HvBq8lfCb3&2Iil9(a~=zq<?@tUiFhpJO>G0?lQd`H;=z*-'
    'mBtpZG~esxLs*Zs_MOg;^NXS9e@vc?=tsPE`3kQK6wXIWB^5uFV(^CsX8TvM;8}tLC+64mf=q7R9_^jXeszA&LM()Vx_#0XAe#gp'
    'J#7ivIoeo={s7e0lL>%1Vj?J&S8Qcjn@_hLWMf4S$qQTps#-'
    'LY~aL#%BEv9fSNI<6y%0ctELjh4Dz8fW8Bx@Nbcv>n#b+T60CE0SGVk*dwUk{JZDn{mkNDTjyUA588`>l1qUp8o`rXQA>jAioRwF'
    '%PSR-HNgb(x8ZhrG;jWqMyef?9bZEev>3o0;wb}D8!RCr&uhLg)4+Fk(awq}kX_-M-aC4M*;Un;}g>C2HFvf?wyZ2ADVdy?dui1J'
    '7%Aq?BKn0s$?ya{MIW;-_|LNSUbvS-B5OB$O6+W{#v`#@h2M#3KLy1v=WYPR-'
    'X!v#=%V!nN4;Z~AL54ZS_p1{3)SKyILrET8kYa=<@6F)+3wY!=^${U4Iwd0)&bIkus$`)^f~a8;`^imta7l+4IMJ1I1u3EVUjKB$'
    'q_d6obT>Dd*S@De0IF8VoOdeNDAA#oi@_EaurRVYr$_Xxl7p8NY}XE`qmf?$-&2Kq)C3dG774;~qDNTDp-'
    '7HwEog%QGnkl+$})BXK)y5r?$8J;W9<~!jY}l)UuMmE11YYT?b>u{J}iFUmKA*3cwN`;YSDgnL1hTL=Bt9J(1iDH{VJnz`@iY}zA'
    'P9m|LJ%O&YY*wnn8T-@rUD8HoM1{C?=3EIsJeyFd9EBQ3YxaAo+C?swKa6!~3-'
    'fssy*1@*(GBZj87*0}*!1aLFW4_B+%I%3?`Ypz`iIs;UHofsi!{xDkKKXoSj52uFFR#h?4BS<K9DGGTsn{50YRA6tr5l$oxqB3U='
    'WaybSSA|5B^?Ylpz!2K)~5u6Jm!h_}~)H_?gcG%KK-'
    '8s4>AotiIUjaOvLzv85*^Y=5Ejc0KCE&#lIL<jKE{nVuVZFtOuMykNvdyFKJs#qXgem0pUP#-'
    '3z1(l3{M7qKLqK&&sw1o~0p?{bmHlN<zOx5wIsO|kL@<OnF#X5^_UCY<fB)|NpMMPnc}NmI9u=n=Q2M8*k<!w}E)h3MPDXaefY_@'
    ')rb1<#M$lRtA@B#-'
    '0HYw8E1+eGHbtND<nPWjb=TPi*N~4ozB=ASr@`1IF#2DXnLZi`sCa_@5d|nq*kJ`Z7$jU{F%0MBeLlqIv7n&o2)wElIXPxh*N+uq'
    'v*4PABFb{n8W2V3ridN^g&9gOILC4HJBk8>Ai#@*!Th0^=Rg%&7FD<tM)Y8$zdg6M%Y+wo9H%r&rppS}?=%1enh~KGGQPG_V_aA;'
    'jfK;xYjbQ@bNqA${(w870nS9ZF;U9q6QeF+Pt}J><z_`S<W{-'
    's<>eL`Ux3ygJ0{j4N1FjK=nPOQHu}<^>>K>q$vNM%<yxRJs#T!RF8tp~1ZdZdFqf@GLY@;ipo;iflQq5;olsUakSzl~5ezKI6o5`'
    '2T|Wujps^%CMmIgnZLZ7{s&iX|WJ#z~K1i$Ta~zaAnRfZAChbHsu1l1fDNTZdtLDe!WX_B(G}Q?v^=jm1MfMW$X~u=h<JT2{(M3r'
    '+cgB3?6*U60*5zyPc|^!~EYeRglHLL)mZyN!a7t3Ibu*iUKX`3v{z60VyQiN#mx1S#yWxNj=V*4&APr0*qTP`aOc^S=sc2&uavWY'
    '=ss{q<z>3LaEouBL2>^2rt-0|rv!oy*yRc}bl1>92dPvb4pI;=FI&o<+$jB5jzLiOU-V8uyT}4A`VFdxaa;VFcM-ssgZ+2bS@73c'
    '1YW|nS3j31f-tA(6>mus6G#F^<hR}-RO$++VW9-7f8}auh4Hd2iVa&8Qk{P6RDDiYqP9-}F%*f(cU1Xg^1_xfX)H^U?ZN56Ct1*-'
    'GP+#gwf%GKOt_l?^?AaVA1z>Mk9lk9WXN@q<394qXf;?D_&U`Yz9}QPQozYKcj^+WA^3+**Cy@9j)XCxV86@WTJoF~$TdA}j`VZ)'
    'L5ym|Q!ORzzz1e!}pV~+&0SpdQX+!lMex8+gxdpH{T&*8lJ!Q~PNs1Mfe!#tD40xBwmtB#SO53q*AA5jiS&d;=BdGZ17T``r`bJL'
    '-%r|#;AM&e3m6?IXF|xSK>C7rZog<Pe8Ud%AMYLJFmBh@Yn?Mv#$cdSO*rB|BEUpy`!!h|>SPQ$oA*G#?(fQjdt*Y~Ogfe91z8Ls'
    'ci&x;EAY_Z!qAbs#&{guyEGfyCN8LMY102TWYlgBVChdYL=AT%-KQNf9qf;Uh29c$xEq7<^xka$*7{m8F0q5&P#p*f>rzz1;-'
    'Pi!^12KNp(DYijbn}^>Y~m}Ua;`x5_YzP+^vDF76Yeo0_<*?6N%0Iz2vtgT5~!>Iv{d!be81nIe#{&e?~OQIL+!(;QE~gYfc7UXh'
    'SO5VJh8w|{Ww++Zr9xk9CY$hHV?``%D5%W7w~V`d>=kGz9IZFWLe6zxGtCdyq;ec2iZGX8@B3W*+9uP5FJCDcwy&Gj1^P!YAr~sK'
    '?JRl77o{v(w8uMLZmB*CYO~5+mLsnXGH)W=>#$n@lMy5g6J>^=FHMhr~d`YMMiVvm!iSHf0>>$$|RdtOi!7ckqk_Rybw4a>r_oTG'
    '(*TQ%$5qOd&dHq9f3AO`98OrkuThq93JBSUZ*VCI<Z_lI>Jp0QiV)odw#3m8kr2Ei|M8NDOSiE$!jF(H2!C*!MC`O_|1!hM|?d2d'
    'O7JrHg~vCl)f%7T5<9n0Tj;TicJKT?_}>^0yLkNdJf-'
    'E;3KeLFVjtbM#4v=G^uG(sJ!3H0Zd%v5i=%!CbzJu&T*R1dDYJqfONDf0-'
    'TE>iSvGbu3BSt_!^g5ah}%F+(rPi(LTL1OdG_b5)_qriOgs}mR06r6(S-'
    '?POM@PImf%gh;i1}kL}haVDfA;)Fnn*Y`fNH0lYe+Poi+R?27G5c*Xre5qQ7_+4sE+Dx?*yj(fMhooyd|c@VH0gk6E#Tx|yhdtgc'
    '+jRUSyT`#Stzd7T5r_q6p0WoR@#H+~Q>!E(EtsaM@&6K@S^$f$>oZ;<1YQBVK)>XRcoGOY#lb0xXq>H-'
    '5E<h}RP!#7$(9WrLJ7{L4VaZIooX~n&42#<#3si>=K~;=M<`ty)EW|{GIVWfN2G{3rS$TfJc$wnaxFi6t+!rYq%cz)Bm1QO`V~};'
    'HZ_m?7?LN1ZQ3+_<1nxS^kT!LLKuVoC<<PNdv_f~H3loFvsB5tzBEKr>eRy3YgmCIOGFpS5+-'
    'Q|Wbd3p*0$41s!_5CfF)U(LNJe?3jC8-'
    'hkC9fgwKlZxzb{i$90T2!V6)6SM3d?XR8?CKg7eTdxERG3I8x58h)1K<@GdvymIBCXwZQ3FRcr8Uy%s)Dxp^Q);&&fM<{E6LnWia'
    'q5GTR({D|%9@>7T$l>{K=OkeWirgX-1@b_2+QWrR-MczCXRPoHV3ovgn$AzUL`4yxXClY|e(+O^|L)sznGUL+4wj`}_{)89c?6&y'
    '1bP|1LsRW~uD=J!4OqP<k9muE|jcJ(E)^7dQ5;-_Va<c~C-%#CJ%l2I*H||-Ahv-YCar>4>=^c@P$hAGyHA(nt2?U^8sUx)EHNiC'
    '03SbdC7VK+V1B(Ab6hLy{?Q;%!L7-'
    '~gR;Z#}%?5`!wH(tH3U37UVHty%XFSS^JL?E5e*R+)Tj!XMb*LE4aShmtKwPg87B?Cr!VI2>C&LUQgH{b0|9XIjF(2t#wQ<1ys|('
    'SmRiazdoLFQG@^@BMX599HsYH4rOyc;y8QICTgb9&?Wty-!`lEGy-'
    ';8&CD=sK*l1eNm2*|K&XPPfF+ISn*_S@b@2wUa~GI{bAW&DvrIlk9vCvg++y)5ly*gjcflE~HLc|r<kGc6NTm6@YPm;$6(T({{qj'
    'kj79F}AsF%>Y>v=0b09cU$QblSsQBqr2N40EL&!vvad9=o>hMdrRkFFe@-'
    'Xx@Wce${|_Bv9DIYLqZ_B#X*P2;>~AI*d#^rLCM5*D}zA!d6XJrHJvgvw0QcZI6fKGkM~E)WvzrVASYfg*l}uC2@9uptLR&F{!vP'
    '~CM!de>z7*o#Fp{~uc9j;jFJb^0Tw$Y3DyB$mBJ8cXGz-Ku)GV%y3iws_Y^s|ALv1V#0XR$RRPrUUE7fN4795W8x?OODy}Nz<nwn'
    'D4mDgSzxjeMb-'
    '=51b8mgPSr@q(Q1q(&aW*~=d&cgM?Bs<FN7Y9``pAj2UKJQn*l4oUgZh<Cjx<Viajdqoh2`QD$R5h06C0EDW7I~#d!7&a?)+@$z%'
    'TwW!n`S@J6;u%hA6x~%U1#BN_!p`wAOPIAVH(NAi3(Kql}d)D|$^$(uM?z-'
    'c9({+J?c{qQpVk(jh&y3@O4^U4$u`&`c9Muy8@UWy#)%8#;ak-'
    '3F(FiQnXXs={}JvnMfUQ^ZlEe}hwfJ|cZ4tCY(1i)U0qn8cf~yD1dW%E3cqPeQjLN`%!nInVw8AyDvHzX6Ba73IeA>8M;ttZD$zK'
    '_cZac2cWG2en#;+oXxlF+RxGl`UbmjiVqB+Py%78aHWtADL-IC1oDv^9GJF-Qq8d(9(!7f~12%s&>E%&>rHdQBuV2$GKNHUUQ}rt'
    'Nu1{G%R_<;vDmC08~@kjDl3EJxlZ>vv^HZ`Sycatywbq%tivy8@b{0UJz4PWUI2DC0nN8hPr44?Wv*7;Wih*ziM@?wbc@9fHxDTb'
    'X7BMaQEbJHAx1l&^>I;zx3!MX03YU3{}@3xJ-jGVHH)nm`BqaA>(H^o~x?}f_3Ydm*LOWaYqnIhs`ZU7SqEzuhJAtpWs}5lAgzT8'
    'q$BqA3RA)&c<Q9fNaodNJ?47lcCh$dRqaN;Hga6FMcA(NvLcKZ7b{jRSM-AHuLg;to7OiAQ+3Q@{+)l+i!)4!s-'
    ')%g_1FFT);`zcxz$(2%@pTwJ>-m_<hntuU@w!;)Sq0m&@dGsY#}L-G*-'
    '>7_6rpRu(!ibtOca3E(grl42@fK;5xMb_5jK<D0VrFa?_wA_Uf&>f8Y8Gyz`prEULMvPNy?3f!UH)PPCtn=0LTey$~MVQM!U(0T#'
    '4pg~4U(}I_Wd9aU5#yEQ-'
    'q#t`N>RB>D1PGR9Cb@GLXh{QnQ#J%s2uGiirYr`u46%%I%Vt<ank^xRU^@C}EFc?#?{+VwM`PD2fE9|A$g~lgrl6^U45eQdrr;qz'
    'vr6C%EeA%FqaOB3@<s)Ry1!vf1B;?C;$=*4bQ+HNVz(CfqJ0Fg(z~z6D`5Zte}TD$v|DZb!PLW@4a{~dd|_HJ13PS>G|B2KK+5+7'
    'sBq^61-zvR;~3G$9N^tFerWf?{5`TEE-'
    '{3tY=n%5BY+V#I#^fRvwHYR9&CuE;{}KW&&+Dfh^gxaztvI4yr@SX+B@YY8_&N$(nQe5saznt9y*+I=sR=IgBeXlx67eJigd`XM0'
    'sJ%6@dm+o1$(w4YV^Cj^U~%esaop`_as1VG|r@p57d$*Q`evDI5^0bm|bz#v`d^V+V(fD5xVZTa~5V;!PF8&*d6(&X$GJhGG7&iJ'
    'Pp0RNv24*wFcc^>vaQ-V`t-'
    'JjcqIebCJCoL4Dj>1YeFya#1~A*WkLp1rjUCf2p=6r9Uh`eAQ%Y_v)~p7X^5>6*p?VN6qru8L2yUUh2<%#*PilQbtk9e9I#j5%Zx'
    '_VKEe$)Z&vjqP|<5JAwF0%_l5WgFuuTS*-'
    '8uG%rSXBmFd9?}L^(JsVfIDkG#pc0kjU=Bw=Gm34gZ&8ubr4k)h>U%caM!sb!rp`ZRk|onK;R+!fnL&FQrKy?tC?&yO$+2upm_U+'
    '$0JsD|4zw6ZV<U>rAZQ+wYs^?n*lj6{hO0LD6fJ<o5K^6Yr+l+1D>Ih)1xYPRwS#m@>zl`(!ZU3auM6vGz_A1bg9n-'
    'Mt9f8!LP}{TbZ8K&aX|9L-'
    '02387Z{n@ShXy&bQ)}D?!E>5&Ws4jnb!5zMKbaBu_Xxt+&r+0qhFKfCF}b^RgW3Um=pCGS);uRde{u=f18I+r<DLb9ZB6pC?GU+g'
    'G*fmI3bEk8WY(RC-SoLKHIiBEJMn}nrzO3i|<iWJY)$#g+C$a`sDCyaC2fL4vq?%n-'
    '{2JstqyobE#AEs;<eJvIgVs%rQ`+fs^L`PTK^Y52d2!8W%Z;#0SWNJO&3(mh&$xG(AMuB%?E1G@peEp1}Uo3D!NeY(+CmNtT>NE^'
    'sBhui`w$)DNx`VQ~aUde-1&2EOQ6(xi@nsl=wgf1U+s0XxbjTT^qE_E%-'
    'O7nx)k6G_?jI>GRCQ9}QLpIs++<imb>^fmCtEclI639Ahd#*$f`zg6v7u*6&hb%O8)t?xiv)=dHL%{tk_utNB26)lhoJ|fGmQN0)'
    '<?wckCdSnaHA8%G%0+;{VVLTgRXik0Ssz_yH>|k((6T#A&65Ca!NNlMKva+v4HpN)BY}=HQ163a~yLUSP$bs7RU)GP-MisJxwo$#'
    'lVxmqaY@CB5m_6fU2Hmi}=A_dVx@PPO^XdH1=@-I|3t1X5vipO3P~=D`uF4gu@C1v)`QOi{pjaN?eT>T0?i-'
    '|2D@CGA21jzWL4>x~ESpk*J9tdETm^->9@W-jT-ziYLnjU(6=K&<akD<Fb)h@CuN#)4OhoNO<RYEUZ!4`;)zp*qdjea%cnZotfP0'
    'lIo;W>%IO<hqO#TtIP<C1xgycs&T7WrN>vU#!h;WTO(8i!s{on=uq@x>yYAokS+jWkp{UKB#t@68Bfh6%DOCAt{03UK4TQUs*Zev'
    '>dsz!f-'
    '#c5_Xt_DTnRAv1ZRayi)`6kB*rY{!tuXSGk?Ylo|<t`rVvi!f@oR9LkXhPHysF=P%eC0mGYO{V^u(<^{WCvg~no*NY&2i#J#k#Cy'
    '{OfWoWbbTh4uAXdiuZSUoW(YTQD${2dnUWbfGLsQUV-0Fo57mR9gdUZG>r};P%R($*0H-XQ?om~0YSBB)&Fbb-'
    't)SAp;O>6M5WhMBjvonjnWtvZP9YVHe^SGeVtTAqQ!2WoEh|@WNeH~QHj{u6;=soT|r*QXjj+^!ms+6wvClW+1UpJh%(@LhR!x5s'
    'bexpc8`9*jxSQ$@ETd81u{FJPFyb1O<VNkFo`~1#!P8tNepIHH$`ced<x@k_F88QV^V7Rw~n-'
    '}n%{p0?UxGCg+$wD#^cGqoE0Bly(lh5)?mq-ohL!ol%8c|30kfZN5L>>HWkrbMiZC7bc9f8y~(B-83-'
    'srT9q>T0$i3rH%7?p#5I(ZYnQzZ{f4Sn3^T51Lg^ok%VW5KEzW%iOcCv~>9-'
    '%;F4fJsR2o$qjG+NC=Q_R$EmJZf6Co?plxlgIa=dBBj$BLO41Q?qQz@k$pegND)&qdl>`&!}U{r*grwM$4Fx8^!!AZJktCd7FWy^'
    'kGymDB53?#$S$5wibir%w!oCDjFS^<rtKoa>pv~f=LO$8By&BcZRF)wu<pi^gKQz^Py%6CxgT~WY%gJAay$He9Em-rIVY$EnzA@s'
    '|24QOoV=KK@`IQ=tZhJ5GiJYWAxryJ;6t&^P{mtS`0$$%anAa1sWjQ6tCdK1aFkl69?H>ISBE%5w8GPxWmlU3GVGKEsb%_v-lkaV'
    'f^RK6Y>H^J;MEJfr4iLODar~=M$UdB$^HZ%3UnCO_h>s8MKIDS5CL?nM1$lLD)d;8eYEro#ua{_$`2!98!7xL|hi0NV44F!kHbwG'
    '6xZ9&x{TgIxWHN;9o>#D8O#@*7li&a|DgtJ0scCrqp4h1uEo!FC4DJeg|WjM`wKo^)gL|kd90{~<0=y`7ZO37<QOLlw3hGMW~)Ly'
    'M!7&Q}AvKoM%d`CZLLIo=*7%XU&K#Y%pXsFRGZkJpUYT*Ra>i|3i*O&QqwVw0|x~5e6$L(#?Y-$OeMdy~Cln!xnG(A`x5-'
    'HzVjmB!GZ3unx)Vyiww0)4N%)GL$&q95K4oaHZ%u}ev3<97~?{;tIp5v2CO3kl4H5LOXhI7s2dd>5n;-'
    ';$D4AnNU^oAmmqz%>cnjF){$s*;_g|CD;R2Y$)Z$Y}&*I0S5TJ`M<twiSM>*5NwR<S1+P^qLYC?m*`+o$pxth~e8D4S3Rq8qvd9j'
    'PFFnBRozk9KY6wk&g-cQG)z*#>#W?rPAg1+uCSx&7q3oX3aTs-'
    '83H7cN=?g0^~RS(ZkF0X^KrP!z|x(D))PF<as{Md4dV%MVGkSTS3znL$rnvo2p@v-'
    '>H0f%vHn>j_DRAmw9iPmXXbXA#kj<LO7+*dX^ONBz4(>F23jS!yLt56n*HcW{l<Z)tKk%xEL_$FEQ~?&zDOO^7{ce0)DAk|;{ZsF'
    'vlHlHe>m*HQHZ)gE!Iv0SdpI?j*2B1mah6+@OrQaw%BE7#0ra+#AZqYPrq0%hYk&OIgIGIi47D*lb`NQ<mC8Z>}_9`du|4~!mFqd'
    'f!ru#gimVP98vZFIa|KaTWR9%}S#Ay{Gtf@4P_U+~P|U12!M&Ft6DtMDv~_*<#hI=z&|VWmZrS@xujH6hZif*j)bB=Sst{`wAO#U'
    'f8?4VseFGin6q36WU5<2>6m5D&(KPKjSJU19>Wz)L~t0iD(-'
    'n{|(j1!eW)+0F7ev^Ve)R*qfNYKK?WFR^6qETpIeSE*<{+fR(=lpmJ3mUG?S0wW1EzFaUVB--n?8GjV(uX4wNF;>Zy%=ZDOL&_{='
    'R!?S4drCV%l%daM9x4kB?xrRR<)&)enTi9h7lR{`H|(a|#uC@v50ndh1{zr=msKSx5pA4FI*<&H$~rlmqrwT##hfClN{E4lsMQH8'
    'tCk!`C6BF45NuNKSgi$7n<Y#@C1*31^0S0D$yvz6&}u*qk4U75j6jIOr-'
    'B|<YNmQ1x)xd;!MLLsp1`kcPakWQipFFXF9;}RBVwLxaY5j~H(&LjaDaOgt%Rk12vdh0hvImlGiLFHY#rX^JNsmbk<D+YT*9*<c}'
    'Haa|CR)!?8KYqs1zp(MYpTeG=c9-C3<{eds+%M6)Wh+XiuUpdceo{WB-j6g)EYP7FL$<cCxul0gqW$#O)mB>k^QF`;XX%Elaf-Kp'
    'M@ii_sfP7os}&UR1Ukl_+ShqGb~MT(4o3bz6H4a}qV`+qQkzD%Z3Tu9BEhvPg#JP~B3w-Ud1*2nHu>(`al(#|J-qB;Q-'
    'K`LrcFW0Z$!>g1-tcOTf9if;MfwH@i;yaDxjbl3WL8AG(D-'
    'Xz@YV=aPCV1yo*uv57=_?}RMm89eNo$3>gS5}|!5#mwd|5!q1q;GNhPJ)pnQ$zms6JNnTG>;}gX|R@}k7v{baofE<UETL2S)=|NJ'
    '$eSREtX<GMcXHRg;CBX`!LC!FH;OPSB};|HLA#BGx}o6C6U{z3TzEq^czT^>=wqXG?Yb18y%gDaPlrs>6M$#u-'
    'UF8swZaB$O5ypbr@v%b&>^`Ll0?C?+@^)C;~~X>PYfcPsA*a5iLo80l$q`+)G^mawtoyKZFxs9Ew;%un_#2m%lvf=<_!1P+hIyO|'
    'c6c{mt?Ix$;62GQ5-}!}-'
    'mAI&l@2A#7#y{svhC70+>Emc!M!c^t|Uz(gtC5h}abq!9SoW)Q;#K*)nGh1Q}>>V^A9xmN&n%Yp}QG)Ez>ynI*e_|UwwWXF#zP?G'
    '2T2E?LkxpQR?6$rPWtp>^Q-^<>aT~IoD9mhwH@im|W&vo7o(|wpN==x{b>Km4nxG6-'
    'M4@B|6i);KyET^XE++vLtK@W;TrKf`gL8S^%n`gl-Ens3h8FNFXoDr27$<kHmzi#s-'
    'aE1<J*XshBHb3ovIAw^>*@>2;SB8<Y7HCEyIcRwW9#>7bq|P83rTg?nQGyZ^=Jf2o1t`i!;m|GS$n0v^1fa<j7kJ3`><UsZfJK$R'
    'RPsu3qs3;3_5sJR-'
    '0n}TF|<DthH9l^u!zeNkDyk2n=<Fd?c}N&2T`Jqb96emCf$?QZB^}Hm?WOofn4)j|H0|d;WP$%EZ8Q^_t{Do9ia7k*EdfJ{{mPKP'
    '7!dmLeer|d=+7@y#$a`v$q6?qphZ*M@D@$MX#ws@si7L+iX6sj?ESYKg6ieHgsir=n1eYoKF1IE}*3HK3D^bZXJ(yC4Hzn7#j-'
    'h0j9_ZzWuFsdSMU8-%0F6#`mlQF?-x~jWsB06D#z)^1TpqwSqzgZ;dP@gzt6mo^N!H<v6;+R-'
    '!PYG@hyvX^`x54A6A0+oV0%Js45r9!2dX3=)&iK~L4RtKF?ZotcYb%JhpBFBi=LhQ8Cy_skrtZaqh(Lnb47#2E_+aq!l!UtAB>>7'
    'ZiCTcl0A=s~ng2gb1i7M7BV##?$KR7#aywM;I(JU~TCkmGWRyFB|$>jo_^fP0}v<5E)?jphev`fXQYDzVVH_GYEBJsp!-'
    'n$)r*qrHVxA(}Vtq}_Ah-rs$om*6JJqOJ>ND6j9Xc02@aqLee)tlK>(M5{*p+oy>(VlA>34wAH>purOk&ZX2LZz~o|LZ%ZAp`J<X'
    'jNTL*f<Np_J6&jf8mx<(3bl--I;q~Zoe5wFz$Xh&Y!TW&7~Ju5GKw-%w?Izv;67~)iAg&QrBx5nWNGgt-CA+g1L+tg)BOd|3*8+q'
    'zGc03qOE9Sl!OS(iaTn2g4jmA&J+YIJwT76JpKT*AmWESb+F)}ZPTlLsBP(SSeAyu@zchDcLkp#j@cQPHROtd(v3r&=t*djACBFm'
    '&ez0f)c*MQ$NvXU){k-'
)
)).decode("utf-8"))
_V58_POLICY_ROUTES = (
    ("base_backbone", _V56_BACKBONE_ROUTE),
    ("base_yarn", _V56_YARN_ROUTE),
    ("base_pet", _V57_PET_ROUTE),
    ("recovery", _V58_RECOVERY_ROUTE),
    ("smoothie", _V58_SMOOTHIE_ROUTE),
    ("clone", _V58_CLONE_ROUTE),
    ("known_yarn", _V58_KNOWN_YARN_ROUTE),
    ("ice_minimax", _V58_ICE_MINIMAX_ROUTE),
    ("bakery_yarn", _V58_BAKERY_YARN_ROUTE),
    ("pizza_recovery", _V58_PIZZA_RECOVERY_ROUTE),
)
_V58_POLICIES = {}
_V58_WARM_HISTORY = []
_V58_STATES = {0: {}, 1: {}}


def _v58_advance_extra_policies(obs, visible):
    """Build one heavy controller per early turn and replay its missed prefix."""
    _V58_WARM_HISTORY.append((obs, visible))
    built = len(_V58_POLICIES)
    if built < len(_V58_POLICY_ROUTES):
        name, route = _V58_POLICY_ROUTES[built]
        policy = _v51_build_policy(route, _V54_CONFIG)
        for previous_obs, previous_visible in _V58_WARM_HISTORY[:-1]:
            policy(previous_obs, previous_visible)
        _V58_POLICIES[name] = policy
    actions = {
        name: policy(obs, visible)
        for name, policy in _V58_POLICIES.items()
    }
    if len(_V58_POLICIES) == len(_V58_POLICY_ROUTES):
        _V58_WARM_HISTORY.clear()
    return actions


def _v58_seat(obs):
    return 1 if int((obs or {}).get("player", 0) or 0) == 1 else 0


def _v58_farms(obs):
    farms = list((obs or {}).get("farms", []) or [])
    return farms if len(farms) >= 2 else [{}, {}]


def _v58_shops(obs):
    town = (obs or {}).get("town", {}) or {}
    return [str(value) for value in (town.get("unlocked_shops", []) or [])]


def _v58_base_action(obs, step, shops, actions):
    backbone = actions.get("base_backbone")
    if backbone is None:
        return _v51_safe_action(obs)
    if step < 72:
        return backbone
    first = shops[0] if shops else ""
    if first == "YARN_STORE":
        return actions.get("base_yarn", backbone)
    if first != "PET_CAFE" or step < 144:
        return backbone
    second = shops[1] if len(shops) > 1 else ""
    if second in _V57_PET_SECOND_SHOPS:
        return actions.get("base_pet", backbone)
    return backbone


def _v58_walk_tiles(value):
    if isinstance(value, dict):
        if any(key in value for key in ("kind", "crop", "animal")):
            yield value
        else:
            for child in value.values():
                yield from _v58_walk_tiles(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from _v58_walk_tiles(child)


def _v58_counts(farm):
    result = {"COW": 0, "SHEEP": 0, "GOOSE": 0,
              "WHEAT": 0, "MELON": 0, "STRAWBERRY": 0}
    for tile in _v58_walk_tiles((farm or {}).get("tiles", []) or []):
        for field in ("animal", "crop"):
            value = str(tile.get(field, "") or "")
            if value in result:
                result[value] += 1
    return result


def _v58_number(value):
    try:
        return int(round(float(value or 0.0)))
    except (TypeError, ValueError):
        return 0


def _v58_recovery_mode(obs):
    """Match only legal step-72 public capital/asset signatures."""
    shops = _v58_shops(obs)
    if not shops:
        return "base"
    seat = _v58_seat(obs)
    farms = _v58_farms(obs)
    mine, opponent = farms[seat], farms[1 - seat]
    counts = _v58_counts(opponent)
    market = (obs or {}).get("market", {}) or {}
    inventory = market.get("inventory", {}) or {}
    signature = (
        shops[0],
        _v58_number(mine.get("money")),
        _v58_number(opponent.get("money")),
        _v58_number(inventory.get("WHEAT")),
        counts["COW"], counts["SHEEP"], counts["WHEAT"], counts["MELON"],
    )
    if signature == ("FARMERS_MARKET", 141, 193, 9974, 3, 2, 7, 12):
        return "farmers-recovery"
    if signature == ("BAKERY", 145, 195, 9975, 3, 2, 7, 12):
        return "recovery"
    if signature == ("SMOOTHIE_SHOP", 145, 193, 9975, 3, 2, 7, 12):
        return "recovery"
    if signature == ("BAKERY", 142, 142, 9973, 3, 2, 7, 12):
        return "recovery"
    if signature == ("ICE_CREAM_SHOP", 142, 191, 9974, 3, 2, 7, 12):
        return "recovery"
    if signature == ("ICE_CREAM_SHOP", 145, 195, 9975, 3, 2, 7, 12):
        return "ice-minimax"
    if signature == ("BAKERY", 141, 193, 9974, 3, 2, 7, 12):
        return "bakery-second-shop"
    if signature == ("PIZZA_SHOP", 141, 193, 9974, 3, 2, 7, 12):
        return "pizza-second-shop"
    return "base"


def _v58_known_yarn(obs):
    """Recognize two observed YARN continuation regimes from public state."""
    shops = _v58_shops(obs)
    if not shops or shops[0] != "YARN_STORE":
        return False
    seat = _v58_seat(obs)
    farms = _v58_farms(obs)
    mine, opponent = farms[seat], farms[1 - seat]
    counts = _v58_counts(opponent)
    market = (obs or {}).get("market", {}) or {}
    inventory = market.get("inventory", {}) or {}
    signature = (
        _v58_number(mine.get("money")),
        _v58_number(opponent.get("money")),
        _v58_number(inventory.get("WHEAT")),
        counts["COW"], counts["SHEEP"], counts["WHEAT"], counts["MELON"],
    )
    return signature in {
        (214, 214, 9982, 4, 2, 7, 12),
        (215, 125, 9979, 4, 2, 7, 12),
    }


def _v58_public_farm(farm):
    farm = farm or {}
    return {
        "money": farm.get("money", 0),
        "farmer": farm.get("farmer", []),
        "hands": farm.get("hands", []),
        "unlocked_quadrants": farm.get("unlocked_quadrants", []),
        "tiles": farm.get("tiles", []),
    }


def _v58_exact_public_mirror(obs):
    seat = _v58_seat(obs)
    farms = _v58_farms(obs)
    return _v58_public_farm(farms[seat]) == _v58_public_farm(farms[1 - seat])


def _v58_reset(step, seat):
    state = {
        "last_step": step,
        "mode": None,
        "mirror_streak": 0,
        "clone_selected": False,
        "known_yarn": False,
    }
    _V58_STATES[seat] = state
    return state


def agent(obs, configuration=None):
    """Route only on public shops, capital/assets, and persistent farm equality."""
    try:
        visible = _v56_visible_configuration(configuration)
        step = int((obs or {}).get("step", 0) or 0)
        seat = _v58_seat(obs)
        state = _V58_STATES.get(seat) or {}
        if step == 0 or step <= int(state.get("last_step", -1)):
            state = _v58_reset(step, seat)
        state["last_step"] = step

        # Warm one controller per early turn, replaying its missed prefix.
        extra = _v58_advance_extra_policies(obs, visible)
        shops = _v58_shops(obs)
        base_action = _v58_base_action(obs, step, shops, extra)
        recovery_action = extra.get("recovery", base_action)
        smoothie_action = extra.get("smoothie", base_action)
        clone_action = extra.get("clone", base_action)
        known_yarn_action = extra.get("known_yarn", base_action)
        ice_minimax_action = extra.get("ice_minimax", base_action)
        bakery_yarn_action = extra.get("bakery_yarn", base_action)
        pizza_recovery_action = extra.get("pizza_recovery", base_action)

        if step == 72 and state.get("mode") is None:
            state["mode"] = _v58_recovery_mode(obs)
        mode = str(state.get("mode") or "base")
        if mode == "farmers-recovery":
            if step >= 144 and len(shops) >= 2 and shops[1] == "SMOOTHIE_SHOP":
                return smoothie_action
            return recovery_action
        if mode == "recovery":
            return recovery_action
        if mode == "ice-minimax":
            return ice_minimax_action
        if mode == "bakery-second-shop":
            if step >= 144 and len(shops) >= 2 and shops[1] == "YARN_STORE":
                return bakery_yarn_action
            return base_action
        if mode == "pizza-second-shop":
            if step >= 144 and len(shops) >= 2 and shops[1] == "PET_CAFE":
                return pizza_recovery_action
            return base_action

        if step == 96 and shops and shops[0] == "YARN_STORE":
            state["known_yarn"] = _v58_known_yarn(obs)
        if step >= 96 and bool(state.get("known_yarn")):
            return known_yarn_action

        if step >= 72 and shops and shops[0] == "YARN_STORE":
            if _v58_exact_public_mirror(obs):
                state["mirror_streak"] = int(state.get("mirror_streak", 0)) + 1
            else:
                state["mirror_streak"] = 0
            if step == 360:
                state["clone_selected"] = int(state["mirror_streak"]) >= 240
            if step >= 360 and bool(state.get("clone_selected")):
                return clone_action
        return base_action
    except Exception:
        return _v51_safe_action(obs)


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)


def kaggle_agent_v58(obs, configuration=None):
    return agent(obs, configuration)


# v59 derivative of Kaito Fukami's public v58 notebook:
# https://www.kaggle.com/code/kaitofukami/41-49-future-unseen-v19-replication-to-control
# Exact-mirror premium-sale lead.  It leaves the v58 policy untouched
# unless both public farms have remained identical through the opening.  In
# that case, a premium sale already planned for the next turn is moved forward
# when the goods are in the shed, then removed from its original turn.
_V59_STATES = {0: {}, 1: {}}
_V59_PREMIUM = {"MELON", "STRAWBERRY", "MILK", "WOOL", "EGG"}


def _v59_step(obs):
    raw = (obs or {}).get("step")
    if raw is not None:
        return int(raw)
    return 24 * int((obs or {}).get("day", 0) or 0) + int(
        (obs or {}).get("hour", 0) or 0
    )


def _v59_route(obs, future_step):
    seat = _v58_seat(obs)
    state = _V58_STATES.get(seat) or {}
    shops = _v58_shops(obs)
    mode = str(state.get("mode") or "base")

    if mode == "farmers-recovery":
        if future_step >= 144 and len(shops) >= 2 and shops[1] == "SMOOTHIE_SHOP":
            return _V58_SMOOTHIE_ROUTE
        return _V58_RECOVERY_ROUTE
    if mode == "recovery":
        return _V58_RECOVERY_ROUTE
    if mode == "ice-minimax":
        return _V58_ICE_MINIMAX_ROUTE
    if mode == "bakery-second-shop":
        if future_step >= 144 and len(shops) >= 2 and shops[1] == "YARN_STORE":
            return _V58_BAKERY_YARN_ROUTE
        return _V56_BACKBONE_ROUTE
    if mode == "pizza-second-shop":
        if future_step >= 144 and len(shops) >= 2 and shops[1] == "PET_CAFE":
            return _V58_PIZZA_RECOVERY_ROUTE
        return _V56_BACKBONE_ROUTE
    if bool(state.get("known_yarn")):
        return _V58_KNOWN_YARN_ROUTE
    if future_step >= 360 and bool(state.get("clone_selected")):
        return _V58_CLONE_ROUTE

    first = shops[0] if shops else ""
    if first == "YARN_STORE":
        return _V56_YARN_ROUTE
    if (
        first == "PET_CAFE"
        and future_step >= 144
        and len(shops) >= 2
        and shops[1] in _V57_PET_SECOND_SHOPS
    ):
        return _V57_PET_ROUTE
    return _V56_BACKBONE_ROUTE


def _v59_remove_due(market, due):
    adjusted = []
    for raw in market:
        order = list(raw)
        if len(order) >= 3 and order[0] == "SELL" and due.get(order[1], 0) > 0:
            item = order[1]
            reduction = min(int(order[2]), due[item])
            order[2] = int(order[2]) - reduction
            due[item] -= reduction
            if order[2] <= 0:
                continue
        adjusted.append(order)
    return adjusted


def _v59_lead_sale(obs, action, step, state):
    market = [list(order) for order in (action.get("market") or [])]
    market = _v59_remove_due(market, dict(state.pop("due", {})))
    future_step = step + 1
    if future_step >= 719 or future_step % 72 == 0:
        result = dict(action)
        result["market"] = market
        return result

    route = _v59_route(obs, future_step)
    future_market = route[future_step].get("market") or []
    shed = dict(((obs or {}).get("private", {}) or {}).get("shed", {}) or {})
    for future in future_market:
        if len(future) < 3 or future[0] != "SELL" or future[1] not in _V59_PREMIUM:
            continue
        item = future[1]
        committed = sum(
            int(order[2])
            for order in market
            if len(order) >= 3 and order[0] == "SELL" and order[1] == item
        )
        available = max(0, int(shed.get(item, 0) or 0) - committed)
        quantity = min(8, int(future[2]), available)
        if quantity <= 0:
            continue
        same = next(
            (
                order
                for order in market
                if len(order) >= 3 and order[0] == "SELL" and order[1] == item
            ),
            None,
        )
        if same is not None:
            same[2] = int(same[2]) + quantity
        elif len(market) < 10:
            market.insert(0, ["SELL", item, quantity])
        else:
            break
        state["due"] = {item: quantity}
        break

    result = dict(action)
    result["market"] = market[:10]
    return result


def _v59_profitable_mirror_branch(obs):
    shops = _v58_shops(obs)
    first = shops[0] if shops else ""
    if first == "PIZZA_SHOP":
        return False
    if first == "PET_CAFE":
        return len(shops) >= 2 and shops[1] not in {
            "FARMERS_MARKET",
            "PIZZA_SHOP",
        }
    if first == "SMOOTHIE_SHOP":
        return len(shops) >= 2 and shops[1] not in {
            "ICE_CREAM_SHOP",
            "PIZZA_SHOP",
            "SMOOTHIE_SHOP",
        }
    if first == "ICE_CREAM_SHOP":
        return len(shops) >= 2 and shops[1] not in {
            "BRUNCH_SPOT",
            "PET_CAFE",
            "SMOOTHIE_SHOP",
        }
    if first == "YARN_STORE":
        return len(shops) >= 2 and shops[1] != "ICE_CREAM_SHOP"
    return True


def kaggle_agent_v59(obs, configuration=None):
    action = kaggle_agent_v58(obs, configuration)
    step = _v59_step(obs)
    seat = _v58_seat(obs)
    state = _V59_STATES.get(seat) or {}
    if step == 0 or step <= int(state.get("last_step", -1)):
        state = {"last_step": step, "mirror_streak": 0, "clone": False}
        _V59_STATES[seat] = state
    state["last_step"] = step
    if not state.get("clone"):
        if _v58_exact_public_mirror(obs):
            state["mirror_streak"] = int(state.get("mirror_streak", 0)) + 1
        else:
            state["mirror_streak"] = 0
        if step >= 96 and int(state["mirror_streak"]) >= 90:
            state["clone"] = True
    if (
        not state.get("clone")
        or step < 120
        or not _v59_profitable_mirror_branch(obs)
    ):
        return action
    return _v59_lead_sale(obs, action, step, state)


__version__ = "Kaito-v59-exact-mirror-premium-lead"


# ==========================================================================
# Local-only v60 composite experiment
#
# 1. Move only the five-unit WHEAT purchase from step 1 to step 0 on every
#    route.  No farmer/hand action or other market order moves.
# 2. Trim STRAWBERRY seed buys against the selected route's remaining plants.
# 3. At hour 23, sell exactly the projected shed overflow while reserving the
#    next day's animal feed and avoiding fertilizer liquidation.
# ==========================================================================
_V60_ROUTE_NAMES = (
    "_V56_BACKBONE_ROUTE",
    "_V56_YARN_ROUTE",
    "_V57_PET_ROUTE",
    "_V58_RECOVERY_ROUTE",
    "_V58_SMOOTHIE_ROUTE",
    "_V58_CLONE_ROUTE",
    "_V58_KNOWN_YARN_ROUTE",
    "_V58_ICE_MINIMAX_ROUTE",
    "_V58_BAKERY_YARN_ROUTE",
    "_V58_PIZZA_RECOVERY_ROUTE",
)


def _v60_copy_action(action):
    action = action or {}
    return {
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands": [list(order or ["PASS"]) for order in (action.get("hands") or [])],
        "market": [list(order) for order in (action.get("market") or [])],
    }


def _v60_move_wheat_early(route):
    first = _v60_copy_action(route[0])
    second = _v60_copy_action(route[1])
    moved = []
    kept = []
    for order in second["market"]:
        if (
            len(order) >= 3
            and order[0] == "BUY_PRODUCT"
            and order[1] == "WHEAT"
            and int(order[2]) == 5
        ):
            moved.append(order)
        else:
            kept.append(order)
    if len(moved) == 1:
        first["market"].extend(moved)
        second["market"] = kept
        route[0] = first
        route[1] = second


for _v60_route_name in _V60_ROUTE_NAMES:
    _v60_move_wheat_early(globals()[_v60_route_name])


_V60_BASE_AGENT = kaggle_agent_v59
_V60_ANIMAL_PRODUCTS = {"GOOSE": "EGG", "COW": "MILK", "SHEEP": "WOOL"}
_V60_FINISHED = ("WOOL", "MILK", "EGG", "MELON", "STRAWBERRY", "TOMATO", "CARROT")


def _v60_int(value):
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def _v60_plant_count(action, crop):
    orders = [(action or {}).get("farmer", ["PASS"]), *((action or {}).get("hands", []) or [])]
    return sum(
        1
        for order in orders
        if isinstance(order, (list, tuple))
        and len(order) >= 2
        and order[0] == "PLANT"
        and order[1] == crop
    )


def _v60_seed_trim(obs, action, step):
    market = [list(order) for order in ((action or {}).get("market") or [])]
    if not any(
        len(order) >= 3
        and order[0] == "BUY_SEED"
        and order[1] == "STRAWBERRY"
        for order in market
    ):
        return action
    route = _v59_route(obs, step)
    seeds = dict(((obs or {}).get("private", {}) or {}).get("seeds", {}) or {})
    have = _v60_int(seeds.get("STRAWBERRY"))
    remaining = _v60_plant_count(action, "STRAWBERRY") + sum(
        _v60_plant_count(future, "STRAWBERRY") for future in route[step + 1 :]
    )
    adjusted = []
    for order in market:
        if (
            len(order) >= 3
            and order[0] == "BUY_SEED"
            and order[1] == "STRAWBERRY"
        ):
            order[2] = min(_v60_int(order[2]), max(0, remaining - have))
            have += int(order[2])
            if order[2] <= 0:
                continue
        adjusted.append(order)
    result = dict(action)
    result["market"] = adjusted
    return result


def _v60_is_shed_access(position, size):
    half = size // 2
    return tuple(position) in {
        (half - 1, half - 1),
        (half, half - 1),
        (half - 1, half),
        (half, half),
    }


def _v60_tile_at(tiles, position):
    x, y = int(position[0]), int(position[1])
    if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]):
        return tiles[y][x]
    return None


def _v60_animal_count(tiles):
    return sum(
        1
        for row in tiles
        for tile in row
        if isinstance(tile, dict) and tile.get("animal") in _V60_ANIMAL_PRODUCTS
    )


def _v60_project_units(action, farm, private, capacity):
    tiles = farm.get("tiles") or []
    size = len(tiles) or 10
    positions = [farm.get("farmer", [0, 0]), *(farm.get("hands") or [])]
    inventories = [dict(bag or {}) for bag in (private.get("inventories") or [])]
    inventories.extend({} for _ in range(max(0, len(positions) - len(inventories))))
    shed = {item: _v60_int(quantity) for item, quantity in (private.get("shed") or {}).items()}
    orders = [action.get("farmer", ["PASS"]), *(action.get("hands") or [])]
    orders.extend([["PASS"]] * max(0, len(positions) - len(orders)))

    for actor, (position, raw_order) in enumerate(zip(positions, orders)):
        order = raw_order if isinstance(raw_order, list) and raw_order else ["PASS"]
        op = order[0]
        bag = inventories[actor]
        tile = _v60_tile_at(tiles, position)

        if op == "DROP" and _v60_is_shed_access(position, size):
            load = sum(_v60_int(value) for value in bag.values())
            room = max(0, capacity - sum(shed.values()))
            if load > room:
                orders[actor] = ["PASS"]
                continue
            for item, quantity in list(bag.items()):
                shed[item] = shed.get(item, 0) + _v60_int(quantity)
            inventories[actor] = {}
            continue

        if op == "PICKUP" and _v60_is_shed_access(position, size) and len(order) >= 2:
            item = order[1]
            requested = _v60_int(order[2] if len(order) >= 3 else 1)
            quantity = min(requested, shed.get(item, 0))
            shed[item] = shed.get(item, 0) - quantity
            bag[item] = bag.get(item, 0) + quantity
        elif op == "PLACE" and len(order) >= 2:
            item = order[1]
            if (
                item in _V60_ANIMAL_PRODUCTS
                and isinstance(tile, dict)
                and tile.get("kind") in ("COOP", "PASTURE")
                and "animal" not in tile
            ):
                if bag.get(item, 0) > 0:
                    bag[item] -= 1
            elif _v60_is_shed_access(position, size):
                requested = _v60_int(order[2] if len(order) >= 3 else 1)
                quantity = min(requested, bag.get(item, 0), max(0, capacity - sum(shed.values())))
                bag[item] = bag.get(item, 0) - quantity
                shed[item] = shed.get(item, 0) + quantity
        elif op == "HARVEST" and isinstance(tile, dict):
            quantity = _v60_int(tile.get("yield_units"))
            if quantity > 0:
                item = tile.get("crop")
                if tile.get("animal") in _V60_ANIMAL_PRODUCTS:
                    item = _V60_ANIMAL_PRODUCTS[tile["animal"]]
                if item:
                    bag[item] = bag.get(item, 0) + quantity
        elif op == "COLLECT_FERTILIZER" and isinstance(tile, dict) and tile.get("fertilizer_available"):
            bag["FERTILIZER"] = bag.get("FERTILIZER", 0) + 1
        elif op == "FEED" and isinstance(tile, dict) and "animal" in tile and not tile.get("fed_today"):
            if bag.get("WHEAT", 0) > 0:
                bag["WHEAT"] -= 1
        elif op == "FERTILIZE" and isinstance(tile, dict) and tile.get("kind") == "PLANT":
            if bag.get("FERTILIZER", 0) > 0:
                bag["FERTILIZER"] -= 1

    action["farmer"] = orders[0]
    action["hands"] = orders[1 : len(positions)]
    return shed, inventories


def _v60_project_market(shed, market, capacity):
    projected = dict(shed)
    for order in market:
        if not isinstance(order, list) or not order:
            continue
        op = order[0]
        if op == "SELL" and len(order) >= 3:
            item = order[1]
            projected[item] = max(0, projected.get(item, 0) - _v60_int(order[2]))
        elif op in ("BUY_PRODUCT", "BUY_ANIMAL") and len(order) >= 3:
            item = order[1]
            quantity = min(_v60_int(order[2]), max(0, capacity - sum(projected.values())))
            projected[item] = projected.get(item, 0) + quantity
    return projected


def _v60_append_sale(market, item, quantity):
    if quantity <= 0:
        return 0
    for order in market:
        if len(order) >= 3 and order[0] == "SELL" and order[1] == item:
            order[2] = _v60_int(order[2]) + quantity
            return quantity
    if len(market) < 10:
        market.append(["SELL", item, quantity])
        return quantity
    return 0


def _v60_shed_guard(obs, base_action, capacity):
    if _v60_int((obs or {}).get("hour")) != 23:
        return base_action
    action = _v60_copy_action(base_action)
    seat = 1 if _v60_int((obs or {}).get("player")) == 1 else 0
    farms = list((obs or {}).get("farms") or [])
    if seat >= len(farms):
        return action
    farm = farms[seat] or {}
    private = (obs or {}).get("private") or {}
    shed, inventories = _v60_project_units(action, farm, private, capacity)
    projected = _v60_project_market(shed, action["market"], capacity)
    carried = sum(_v60_int(value) for bag in inventories for value in bag.values())
    excess = max(0, sum(projected.values()) + carried - capacity)
    if excess <= 0:
        return action

    prices = (((obs or {}).get("market") or {}).get("prices") or {})
    candidates = sorted(
        _V60_FINISHED,
        key=lambda item: (_v60_int(prices.get(item)), item),
        reverse=True,
    )
    day = _v60_int((obs or {}).get("day"))
    if day >= 29:
        candidates.extend(("FERTILIZER", "WHEAT"))
    else:
        candidates.append("WHEAT")
    total_wheat = projected.get("WHEAT", 0) + sum(
        _v60_int(bag.get("WHEAT")) for bag in inventories
    )
    wheat_surplus = max(0, total_wheat - _v60_animal_count(farm.get("tiles") or []))
    for item in candidates:
        available = projected.get(item, 0)
        if item == "WHEAT" and day < 29:
            available = min(available, wheat_surplus)
        sold = _v60_append_sale(action["market"], item, min(excess, available))
        projected[item] = max(0, projected.get(item, 0) - sold)
        excess -= sold
        if excess <= 0:
            break
    return action


__version__ = "local-v60-wheat-early-strawberry-trim-shed-guard"


def kaggle_agent_v60_composite(obs, configuration=None):
    action = _V60_BASE_AGENT(obs, configuration)
    step = _v59_step(obs)
    action = _v60_seed_trim(obs, action, step)
    capacity = _v60_int((configuration or {}).get("shedCapacity", 100)) or 100
    return _v60_shed_guard(obs, action, capacity)


# Conservative 1m0ke branch: the exact public step-72 Bakery signature only
# arms the router.  It stays on the backbone and does not change behavior until
# the second shop is publicly visible as YARN_STORE at step 144.
_V62_SWITCH = {
    0: {"last": -1, "armed": False, "active": False},
    1: {"last": -1, "armed": False, "active": False},
}
_V62_ORIGINAL_ADVANCE = _v58_advance_extra_policies
_V62_ORIGINAL_RECOVERY_MODE = _v58_recovery_mode
_V62_ORIGINAL_ROUTE = _v59_route


def _v62_asset_counts(farm):
    counts = {}
    for tile in _v58_walk_tiles((farm or {}).get("tiles", []) or []):
        value = str(tile.get("animal") or tile.get("crop") or "")
        if value:
            counts[value] = counts.get(value, 0) + 1
    return counts


def _v62_matches_1m0ke(obs):
    if _v59_step(obs) != 72 or _v58_shops(obs)[:1] != ["BAKERY"]:
        return False
    seat = _v58_seat(obs)
    farms = _v58_farms(obs)
    mine, opponent = farms[seat], farms[1 - seat]
    inventory = (((obs or {}).get("market") or {}).get("inventory") or {})
    return (
        _v58_number(mine.get("money")),
        _v58_number(opponent.get("money")),
        _v58_number(inventory.get("WHEAT")),
        _v62_asset_counts(opponent),
    ) == (151, 39, 9971, {"COW": 2, "SHEEP": 2, "WHEAT": 7, "MELON": 12})


def _v62_advance(obs, visible):
    actions = _V62_ORIGINAL_ADVANCE(obs, visible)
    seat = _v58_seat(obs)
    step = _v59_step(obs)
    shops = _v58_shops(obs)
    state = _V62_SWITCH[seat]
    if step == 0 or step <= int(state.get("last", -1)):
        state = {"last": step, "armed": False, "active": False}
        _V62_SWITCH[seat] = state
    state["last"] = step
    if _v62_matches_1m0ke(obs):
        state["armed"] = True
    if (
        state["armed"]
        and not state["active"]
        and step >= 144
        and len(shops) >= 2
        and shops[1] == "YARN_STORE"
    ):
        state["active"] = True
    if state["armed"]:
        actions["recovery"] = actions["known_yarn" if state["active"] else "base_backbone"]
    return actions


def _v62_recovery_mode(obs):
    if _V62_SWITCH[_v58_seat(obs)]["armed"]:
        return "recovery"
    return _V62_ORIGINAL_RECOVERY_MODE(obs)


def _v62_route(obs, future_step):
    state = _V62_SWITCH[_v58_seat(obs)]
    if state["armed"]:
        return _V58_KNOWN_YARN_ROUTE if state["active"] else _V56_BACKBONE_ROUTE
    return _V62_ORIGINAL_ROUTE(obs, future_step)


_v58_advance_extra_policies = _v62_advance
_v58_recovery_mode = _v62_recovery_mode
_v59_route = _v62_route
_V62_COMPOSITE_AGENT = kaggle_agent_v60_composite
__version__ = "local-v62-v60-composite-bakery-yarn-confirmed"


def kaggle_agent_v62_composite_bakery_yarn(obs, configuration=None):
    return _V62_COMPOSITE_AGENT(obs, configuration)
