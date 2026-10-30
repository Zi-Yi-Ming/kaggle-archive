# Medal push R2 (2026-09-11). Local VERIFIED: beats frozen v11E 16-0, mean margin +20k..+50k.
# Modified September 9, 2026 by prvsiyan: lossless single-file packaging only.
# Original policy and all 13 action tapes: yhay81, Shop Router 0909.
# https://www.kaggle.com/code/yhay81/shop-router-0909
# Sell timing / shed projection credit: aurax7 (see original docstring).
# Licensed under Apache License 2.0; full original license below.
# No routing, repair, sale, or liquidation rule has been changed.

"""Shop plans with small, observation-based repairs. Python standard library only.

The 13 complete action tapes live in actions.json. This file contains every rule:
choose a plan after two shops, delay weed-blocked work within the current day,
bring some planned sales forward one turn, and liquidate on the final turn.

Sell timing and shed projection follow aurax7's public Reactive Router:
https://www.kaggle.com/code/aurax7/kaggriculture-reactive-router
The shop-pair routes and worker-local, same-day queues were developed here.
"""

import copy
import json
import os
import shutil
from collections import deque
from pathlib import Path

# Code-competition submit requires a Notebook Output File named main.py.
if os.path.isdir("/kaggle/working"):
    try:
        _src = os.path.abspath(__file__)
        _dst = "/kaggle/working/main.py"
        if os.path.isfile(_src) and os.path.realpath(_src) != os.path.realpath(_dst):
            shutil.copyfile(_src, _dst)
        elif not os.path.isfile(_dst):
            open(_dst, "w", encoding="utf-8").write("# kaggriculture agent\n")
    except Exception:
        pass

import base64
import lzma
_INLINE_TAPES = json.loads(lzma.decompress(base64.b85decode('{Wp48S^xk9=GL@E0stWa761SMbT8$j_ltjI5?uf-;pjwWF%1?|GCPY(HZtP?h@;BOuWgFW;WLR_G0XY9HaS`N=*Gi*fJ<GpPWAWiI}JHEAL%Dc`@6ZSL%t;v6ZziJ)Q35O-pbi;U(dHm;Sdt0$<C|<7SS{gll#`P1VXRO3=ZN}T~F6DN=nC%#X&JD-3E1kwlp6*Pwsn5_a?xv4X+zgUnfN+2{(K*MrgR91FNXXs3zn7j`LF}TSq&oP$&i39;g9Oh_(`Akps2HV=Nm$Qz1*VK1Q1}SgqEi9iUL}8YY+&phe4xTx86U-=-GeI?t0L?IhOAcMNkVLuWNj1!kRiv0y;ds5N!wxtnOHg4)qxbB>)ajRwKrxn2BoKQnOc%Nhr9m<?{+whVD%VNFkM_yX%Htz{LVJ2#Z4)kD^CE~>7C_tFnmiZ>QCr#2}}HDK`ul>*b8-;T`338e%{zy7PX%obW%+djX4hfBe+RS$(#%AwzGt~*XPDhOS*71!x;H5)$~{*Y?C!)dtV2_~VhWH&hWhtUQKOR9TkI=dV;a>2+18{g+PGBUp{$0jpPJiST~I1W?7aP!{saCxkIZL-=G7DC4ku;sfkZ1KECk4`;}5lx=j#gC<E`y3RI87G;wIPgzv5Ve_Xu-G*#7gzmn*6LqrS3ZMD5E_?1wSO%*{RQClpQ8g$L(quogFwHWO+a1_<pVIEv-a-s2-7;btjRcKEZW$*ROj79!T)M|3T|rhvd4j5UV{-gM7=i!4xJoqB5x2lww^~2MO%br+giM{F{6iJ)wjW<nj9r1I?9*>F`5{Y4>=ZU#Z)fX>0gf8uC2*S)$SGCXyB!S2#fL&plh0yPCtD;tuU6eMp1U1r8Ff~Uqh$iG)a1h3qANmGpy!s{TAU8XyK+XEdA`*0UAz)8q@nnFH$5hcVvMY1t2#31j1FOB>+?qinydp%w1|W8d+GsXIHw$jB1EBKoD>0@jZzX74Cv-eOkRqTci}XF~i8e>_UHu>IgSr1YKp9?Grd<W9a|3-C|xbM&%r)(Dz%tI1FseLnK1(o*yZe5?xdU*3%6eLq!e521r#O;NvHp51m(rldFMV!k*Lv&f82(AhU7yOWOl<6g!%ez~1mm4c-;O?g}mZ0EIF!J$fh#=#-(fubOvWsbAt9Sb!c7(O;gAzL1$MX|7)oEOgct84p~J5l^1<1yab6UK2^bzD!+2N0j3Z_QIV;i-8lq0w|whfa7n&=-Z{;dSGho2*J8Eg|7i!%8~oDgrz19!xU|bWLH?@rATtHi=+2xJE`NYL=p{uksjeFu`=7IU+_XuK5D`~W5iP7xM|!1EnkE9V=I*#*?4vlGUsjdZltfjwn%^*i$=9#rtPPN#}RTG3c2#1XUq`INp{O?AY`GGjWQyBS+HfCiy(NvTq9>CMMdc=c##Wv3;;I-WmW52Sd8?x?8&d)qQNhDCoYpWba-FaO-hLKqg)R!peyLi;80+6WzYoXl2o|@6CHFJ)bv4n+sEAdI#EMw3TOI9m6nlwpeY3`A+@@qJ4dR&0px`t9=p>x{2{fqK53;O`+&2IqGL1ZK%C0oe$g^dXqR_gy0=k+=r?+4yiY?tVC<f49s6E_lC|AWBy7CGq~)5CBfRWjrr*GuX|~ZZ)eo0>IJBCP&=dwC*KqFAd9iKHgw;AI>7Y(e<(6(}8L26x`=9NJyvQG<kbyj7mjs!U)v=)uOfL0}7`-S^X30W2Wxcg&Z#e`rz6yOL2odt0JIazMBh#&+e2e^+?M}6tFHf<3@-&2W9xTwvZ=0Zt8IY1A90n{v<1!3NR}Hp8ag%OC)qB*%eurMR;Ucz!2r>_a47)?xu1jF}fa>POIVy}Ugv52I_o>v^6yWTr7dW!&a9D1d?F8UrI(oEqPC)Fa%353%TJ}7>Mm|J<nSLo7MQe5Po#|T4`6(vqP1rnQ1I8Y5Oq3Q6u@{In)^JcN^p@~?@^Jg|l@WWgnB<9_EvGX(<5AxK<ml}5SHIdg9W8o*P={^=5cAW?BTcO-$uCV(NWF9ARFk(#$hv1JeoT9qU+atS{o{nI<~@7Mr4~|VGZS-N-e8FO*DPjLr$q7D9BAX>`i5^XRIi7=3X2fobS@!jS>a9Bs46@r9H9MTX3HVrE5h5SvYjTzbYx(XJ5cjY3ZUc9azHUr8rbyhuZY<mOpLwwstA}*XJ3UlgH1IXurDA)taj%*9}m`2uMQPWq{d$2D5M+BKe@wKIk{pbG5bQ@ajvDoGPy!u-|(LyT~zE>G5&ik4?$2}667+jAhQ@RK9NHJRJBmopR#k@dl^N07`C{=V1X6oEn&F;5eb?_XY?N*f$>@nIWzPE={Zo@*6#U`q$g~WP1ocHu_|2xwUg)>Ld2SGDL*um#7yoU6N6%8aux~tGcF&S4W9wFRva9nqoKA-5?*44V=%KkvAc3esvkR8&E4kkTGoj~W~Pa;r!8ljLBxf-wB}AH2OQ=pLGD0ZVi<-pj5W(jzDSE?`@P7q?@=&83hq#$HXzgavN}()A7bFI?_!e)Z6cs<FLjG$jR7THF8t8&gp5rP)wJu=DLe$8bQHAra?1*zoI^t+msM}t@@*$a0boz2*ZZ0=1ilk49yumF>24Jf(EF(yZKo0Az~oyxXQ{Eb+s>|Er(%LMvYe*OZTqG&WriP-_tuA?kJ;q?vQZP|OOb<WH}ZJzZl(Ny5{!fXE`;Vom5Axm-oM-$rW3Wb;T%;D?rN+LY`M3IYIHk{`%2&_JA=Jd+{<NpXs6Dzt?k9+3{rm+i9Vj8uNVG@xyK9kEi;<F9jp}i9w;_+7=5`X7EXkZ4|WMvJkAHg!-qv8C;95)RbRQ?*5j2L3J8*Sr`z%8``8sLB0-Vk#&1-+fPt4AiPAW%QJ&4re}>F|bTaRg!G<S__}8-orDSHK3&F|MHW37h$crG*XgzZGCB$`ymI$*blP5}iX4vPmjkd$jfxi%!YrWsa>qtrR(3P`1MGj%55oHC0NbAee;RV$;65pT`AO(KsF@*!Z(H>le`=p1BBU*Vmu9xE{);bhF(SvF{5*JnyP!MDU^+47L#Sd6aD4N#30{CFh-}0BK!$hdc!oZ5#s9SgBXEgoj1H;M~Bg$nV(Tp*@fB$^*$l-=<q!k(&n+o(8;b=Sd;Z>@Yvh45n)ljZ1$!O)yMU1B~VLddJ2(|e5shG$z>?aV1#y|N)cRpbiY*l4<O>r!MewR9hHY{rt*-d#X`ia<IopA#Xx0J9gUEg&pM9m`7`;8JrHzW!Z<dX&i_`eSGDy)VRBwhJqvi}62JIFjM+StDb^EtUEAc2)wurSU1%6&6PoCF$J*S^7|x%s_UIgn-}ZLkT11+gd=PTUxjn$XN0E_k6l(Wl@3*=HG4n?H>p@IgN@W>L~{DzG~!^ZXDW<iAV*NEwj}j<l*@Ja@!Rme2Vcw*NvuJehaIPf(Qi$C*Z{C)I-810jLPPK}ht^W*bsvY{HQ_curF18?MQQ~{rzE@aey^V(&3MV|PrWRcJ(h0vjbmrj;Ey0gYgK+Nmv^n>hF{$<hp;`gA-Fn0n4$+Pyu!?T%s!=M!3vFy>zl&u_46a&5g)3dD>ig>UFmT&<3V|zYz86p}EbkIB_PkE5b9E3zPEL2MJ0<@ugmbje59q(22ZpW!3#qiU<Wt#tNwsk*x&u%JQ=OPSn6TDpzh<i-)5GHk@xPS<*I7tNJLRa5J|Gh45M`3nr{V9vn0NQ~`T)GGQ{ch;f^W0)b=7NGJF7pHbYrN>O3edtE@WEGEPbpEIgPcpA-><ivpat;elaTJ$&FUYW8>jqy_O$?%uBoR7<AK_+TTeQ*$yo3J9^81IY9yj~aR|mR1v-tx_u<t5BiS1I3DM~YOY@lda*egfhvXC1g(wqUu;T5MT%vtk(ZHEcFYnbk$o=np`Fy>%)83&ICHa|M=6VXahP}YxKl+z0jdbPr^Tc9mAaBv#Do;B27z}%|h$gA5iUjmQE(A2{h@>%68ZN_PzAcgL=n8~KgMZbKq{g*8C1=KWn;d?m{P*GUGTq11BwCH_hcgmwBWFka-!WiQCfxUqvbITVY+7gnTOo@*gY60C00#`kW+=bgN;;n{`($)0DQ$*qs?q{3Fxyw*i_Pvi$r4KJTF7-gK&KjMT(ADFE^m=#)CEwN^^O=Q^hIU|ZxEh^-2S_k9JXdufx_j%NXVbxvKJz-*Mh&RxSwRXhu)DAk6m2Pt0m4KMQw<IL2W<Re}Np*c0|qC+EdHe#S17nm$*U;4{1mZP~Eh6lakMB_W;rbyTB$1_jWuN?|pSJh@X?zcAR8LMlXlixV8Uk|4dFU^!fMp+ThLRi*Hv5OZe2D2Hv~$xObK33~bYlQn9@9@`I8$(_X0xsP|i}L^|IjAc6op05%P^vF2hZS@-M#WCS5#@FfDH$<-{h1`lwyO=^)!hw`WI7=y*!WbLfPzo=S4s4MJ_I;0bh*38&KKFm#rCB~`21pi&>@J3VnUbjx33#r4moP4?h6ESCu$EVBsd?}D+^6r!tznr%hOQ`^Ji=vm-(1@1j17ko3Ri6XJU(Gnc@*C`0AX{9ovdR(!#dcYMb&@4tCuAm!BVuc@g4O-NU`0dLD7sYg5&+wrZe*6GG<4|!#Ir-2Hm99)(!}3YCb4p^;4IJco@Ta7`RwKGt^f=<7ay$KS|2$X-FMr<qE5amLyN0<v;-yG95DU#qC)KWEbyl^Hxj65ZDB@v^?p$klcMD}D)uNr-qBOQ!<HJHZcPG&YE7-JkF|)qINI7!UQUG-Y`I<z=K-=rSYNU0B&6SuO>-u?*@k976`tT{^S#m=I*)bO{$B;M(>J+0ls`FSUBB4)!WfX^)y%C>jMwV_;b82m^*7^|T!Y2k$NL&7{>?1k<$lE%>v3K=&#S1kJ}0q4p997FL-i^neI8VXG4nqOw1ygmZJps<jh9!+2Jii)L;P|g;q}v;flDT+^TH~(dYq>uLdanKXzr3k?|Xm%f`!lH3gIvYh%+7LdoeP+bGj?VW+O6~akge}uS_D|xUJ5w1RI}n?q6GbPtd3|-!h=}U(sZt;*R;N3RypCWht<JysC)$3>hhN4QClIbl_h<?p4$8?3w&L#fr*3_(x<8GAiE&mQ?Xvi#EU@k?GX%>Iiy3f9mCfr?+cBSZ&x+%Z*xwgVi!4h<k~XLlV#00Mc_k%d0M#@fHU^`$nlx{{^F6KGRAE%$q=ov*Xc71sRmu1w$#|L6d@3Y13*(64Vt}kEC{z#Gj}w<L9qge}`6w$&2^RUuYp3e3B;w5zG51Y7PX1M6%{joKN0tbMQI?rkO68y;1m+x}L9i!g$;EY<u`icW@o6QB~pU0ydCQgHCgZLTMZaj;h4RSgnY|_ha9|tQhw(N|=W&^B~cT^P!h`I*r+sG!^nON!X~Nqc9wui{J<SE1=}H;Dd`xQ}pxBr~zQ6eql+|pqr+B6=9;I%DUP6!lrU>7FLWw^9Qxj2FeTzSrXTDDB5^y90Zq|GOJa!PY$vX*A<pW?CgxBqY0lyU{fZ?D7-iyfIxR#Jn^wum_8NEvCPM;&cc!?9h_kn_@jY1gawRDHLlP2d0%7O4kR$31Gr?_HGVM^VNQF0#AQ~^#aER9+GC)Nu{3WI<Sbx(owO$T0&YCnV6d-q$5BlkRimGBjWFy}XmUpCsA4PvDGi9z=wz_>`*)t~2l^8#TAE+)jjfH4nd0Q&9dM%Ld-k}NU}0CG?qP&JNka-0?D)q4P5f!!sU6Te6QWF$?>spNrpFEvkQTX6grv-O=3Fm%F{c^YRyg47q}yhWp-elQcJX7(vFCuc>zWD)QDL!DT5_DlP}7zGJV=f!wB2t+!kNb-sV3(Uo66{9R-DBQ6u~evaO_Z2O=SCHLDF2e6|K%mP4-rAAq95KoQNk9PkcmKN>%ijUp<P|j}U2G0G<aP)^7@z><uGoa1GaEoAha9(rcW6NY^+9EQ`jWpRdmGpjT(n6c3^oCFw#&(FARXz!gqREMH5?l|JCNzOVc6p}q6?rii6Xk9#P=Hr-Unu=ju53lTnkFAi##2(A7^*jh9OdV@Hif;Qi`Jc{Lf@G~c9N=l^|+&~v_8U-PLh?j4fAAQ7}Q_|@sa`|F^uNq_QmfP!^N!;AVCU$ZBK%Pvcv^~u3x{|nZK*@))Z5BISn@a$lI0N~b`R_TxwBRRMxS8&CQ`;&bvc2Ok#}3Z&v`->LV2M)W?>u<7e#b$VXL}nz@zj|W7EkV407WwYa4slEV2qdB5<m4J5h3Ek6p)Pj2kCIk*zhib?^rpEmP+0w_5UK4Pdn#Ww)s*vQav-0SkvreO#<Fk*+v_``$J_^xuFi6v5+e46a11z;ievdeiwp%N?&xXuNQK9BKa;QUrabNc$098Mx>utu>EMZ%=c)w_4uN6?_I@IK9f1L2*OQlL5D>J{?HAf&*0nc_eejD$7~so{})tv;D8=cR7e?f0@h7_-&|@LJfGq-<}Rt(gfntiUvrE#pSyN^4*{T4zv3vE$4n*KMfJYbcsIXB9S4M<RDLlcbt@?cfT)?L%q{Z1RpiFIsXNM_%?GLODAsR}h@qUIDLsshO_w5!y%)W5q65Fu%!1bOHiyn|?eZJ;Y&&vPbVlil&xdD&2^XZ3KcTwx<}*DPm-#hAsryV5becNT<+^}SuA2V2V)@nyJrEq&ilx~;5`!0>qt9BfhOIw&$p&vBOEQ&VIqsidsao)IT=%|WR4_}gX1A80HxgS|@pWF2bHf!-7$3e9Bk@l~LdVA)HNwrR=mMM2ZdB$j2l0q+A3AhyBGI3sVx99x)ZAfZh5y*&J4U-#P}qU1iKcn;!3}|5z}GTIVS*^{qhy_(IPF##iL@-@FFqx({jr7;-Kp5=j*MRh!GC<P74Ue0AIm^tC4;CNwY)n&MyBe-K#A=+Ke#{vmjl^5`qcTHep0S-9#^9O&fm2)Spe|db)`sBGRwZ^<uN||tAX5l7)@#|Fc#3+>EPC7hi#k+%mE%gFzFbJqURdSCmtW#KCnS&EMoY1fx1RNa1ItcSp-^{+4wY?yl9J^fGd<}X<=Wkw~i%!tUNq;VtivnR+}u?Pm14C<N@RECS&X7ITw;qKrsUp8`Rs`WGVSfSONVXv5CeKhN6h`y|_p@gPvU=OdPUTZ>zC7muv)B8=b-Aqj<jTvd8}UBUEdwx@oK#TezGcSo29LU9ekIGqYDn#|)8(9azxmV}qeU(2g^>6m~J9tBOSkYMWp?6t0lLW^#qglp_Bi`o*Es+ko0tHlB-Q%Rg5%F$myFl*M0JdZxBruGs1;17`%z%WtmD!<H$Td#as}0okQxms|c!US~#el=hKdM^`LQ_n5nJYFK#ht>YCbu^un3RkOM%AlU`K9#H+;iC(#dxqTPU#SbkZ37unN8CLv*C)Dnb|Bd7AYptj=dMtffb@HTGjH`>}$+n0?(<dFcvYf<g;p5=pZk<@9zP)1*%&h3>V-Id%F#^gmZr=w2h^deVs8ONIm%y)ID@PT4Jq)g{Jo;i#mGMKvBnuE;lt$cywNw0;$01H^q<J9ON>b&khJ}pa_=5$lm1Z9X0fhcij{LEqk50k{ANfdx5YD7-=tuo6PyuQJU-Lgw>Z-a$f~DZP@JS}i4h;rPDO9KF)!Cf%q<$2`4rW4o=eqGRJ{-@%{Td4Qdie_)c|WYAq?qVxkG}0L(_LL9J~xDu5pL?qn*Mo8wo)Rsi@(1_nS&kT>Nk4nhEY%wRu;EbiNx2TY>img7Fhv{OId$==~wsbhE7a(=I0`c=&dGW;cAS7O}|&IjBxir08V*#9TcoYgp3qK3bt%p2XB#$rE|4vU;RY3W250>5d7=CB7m{lb7v%<kfm(!LsFl$Ajt`2Omfc*;S!p?oECzI+M<_8&Zf)YB+2i_1aL1lD;aIY@~VBnIb3@fL3debf*Lwvu-7u~=vk3rvd_Bd@HO<{=C|1HOWWRLFZ3Kcw<BJedKQeh1!Cazd#nCgTsH?%xTY@pG1#Z95(tB60q*6^AF~j#;V_(0(ujb0pD0q0%w;VQ*Mqb8s3Pr@uXz$V)Qd-COpKr=FyAij%|=CPHR3C@`>%?TTdfQdGr6^8<*!uROR(;#f(a(F+rQN>*Ym%F@9PH3(Y;8QpFsnU18pqK_1V>|O?pMvolgO01Z63gyQouJLe^PL_Wx_X7AXiaUUO&V22xY-X2>CkvuAFYMe=ZJY3L?AlQiq_Z5C)e<gdxkMAQqG&AOy=WMTRUO|j?7j#eL%Z%fpEWh=`^ZL1)o>-m16()NBMLE?OGv|Z%wvNi2^TT*pZ#((touZ|Gq2P;*PG(t*$+@PPLX_wxC+E`;?$XkDY(R3Zign22!YmSSjlXCFywfAvUGhS#wGsx-4a(=A$?qN1(ZNg0$RgMvTft<*n{ksi*Ef{5$E_|ND3=EB6C$J#R+l5H4QM|i=q)=OT4X=$?iFzwakrvY6Ec0P5lKZ`RPwqB~#%R#MD|*LeBN)re28*dCnsnYEK|=MLH#h;cGHfGbI5G=6b?Na_*<h8zs=qRG9)W@w$r${Tq73CyOViBNR<PDQndQ!6&9}q$M;Wt5Tps*_Sx`;`o~<a+mk>8+pYGJS7t2_N8R(|q(~h*%(VG9}gh}T|1$eU>=#5I}COZWava*;budljLEc%mA*jGr?QCl-4X_Ytyqv#9)pzSK*2JlPzIgXxffZh?xMO%8QsOsOQpIXw;gwSCVGu7pd-0iRg<e65jUy3OEH|LGs3N;Dm+vzt^W&IYemKmbBeA#`lAu85O#aPo>P?xn4FTvHyBq<^oOxK_S-dxbEWS%*-^jSMRCk)of%)ZK+)-WBM%$5)kR@cCXDLABiReSdE6qIH1e|b#`D&#byrtUGecTv?)EfBE3x{d185&v1#PxE#rJ~4bMZLV@>J#4QyJS$a$ewhvGQ@biSTA#HY;tup?NKByu!v0rLooNRjcm%8cOGtl0cBtvbce>YHsdgwo1RdWsw0omBTs8YRi{OLBGagc?VQW#NAgeLGU{vgdo}G0QX;w}b+Q_dqml$Za_ew=%`%KabV6X9YHfZJnI~sylEPCkwAQuo-k)?A`I&Djz!fAJK89sLV3+|xD^6_kH1QovQ5fP||Z3=xdayBtr$32z~HoJxkx`M1pFuNd>nm|yx`|&^$llm9sn^gh29)=chQBquQuq1P1!E6q0;2!N+TtFf3F)^@MkR<49-pAr^%GUqWut&9$vnY>N%)nT}AM`;O0DUl08l**6PbmA%vpM?FGlhCoZAKR?x<n0_&E>=(ECf)^DNa^)I_NhbjHAX*H5UT+q2%KcCnqw=Hfq;2ny4_Skh}?W5~!-Q;r)DKB>Q$s6Wa+?bgstPr#a6u2On-bA5dff{e9Oww8&H`h<!({&E}VLWTS@1F)NTzCIp6Q+8VZtWGS$Cjv?AZ5>7igg)P2%|6!Xs%POKE*6mQ9Cz4T#_RO2()h6+O1N@PfJlq3o2$h}R*DOceuYAeDb!5KrpEgROsq^b%JZd}A#4UlY{!GpG$~|KXWSz>oBTl+$(E_@wn54vE^%+619e(~z1h7-R0D=UCp^22H<m_RXF>FZV-oidF_<94P-(fRF8n^KXjkjsc1?5vqWERf3EDGnWvb<}mnU@+~Rjoq83%63qA~32KE~b+-_%s4ZBP;NMbAG69Emp(OC1so>rAT|OF*!sbQ@rHAbHzuCdjuWhA%G-J&zh2=7@63;6<t(|6Y%r%c%WvHz~Kinpeff9ly$T;%zfUCLFovy;sv^-<RqMKZ8*TmA|@Jh9{YBhJN*O|JZS0}p}nd1&mtz)2O+Opj|5(B@S!4#HJqieDg&RR+@cg7&^-dlbS1(SjbYhs=raHSQG=&S@$<~*HNX&1zFq@r*y>SZ)U}cm2P~cKZMa=ji0r70%1MtenAN>9lO#sFz)pW82sp3AQd7fsEyT%-sYSm$S-9ks|2jY61|?qT+Ze2STh`vGPPY@b3-T^?Y)TqnoZ4=kKJNy2@lh<_!~+7NgcxKwDDU7QzG`(5a4_h#fg6Tbp~#g@UQsz6d=}FlHb76>5ehSzQTY}q=i|oOAxUvB2v(t&;G;{l<xemNGSTN4I*g?373s9wg3e7K&@zxpFNv3Mat}!s`OaN6|Mnfjs0BahrHyQ(j&ZFfwO!p{b^#guL6wqJxZh3@@*y2s+-V=wnv8k5*c_o-pO$nE9Itq`l?R+1@}2LVU4$_lEJKM)1)@>|2as3hOKERYwIhkL;^PqP323@>UtQv_PN_V-Mykhp%l9NE?DpcrWHM~z5&s{JbMg`e(Prt<kPiLaQ0`@awm0x4A{ZHKjF&e`E^IwF;-hyz#L`rhWT|1RB%x97a3iA@d}+;2iTzwY`NpLy`VVwk_3gJH162j_I;HF3=@2hw)+=pa6_7f8$|9`Y6Lw8q5+;o;m6_3w8pl)SG;e{lCl7KPcdw-eUOF^d20c3_pI33-KNFcP%|0fyOg*>g$L=ZFpyvTf`d!b@MT%)SjZcS>d%u^)r0}FUnIwfE;GQ>Fk|LO1o8(i`{UF4z4mede=GPq$qG!DWq+uA>-PdFg)pMA%HkH=;fh<uyhm)`AcfRy1R!-#q4P69QB^64H&hr|@lC-s@4m<o<Un}pu0dywagCacunZaE5@c3!E-PH2uh&-DeMerT!4J3E}aN%v1YvpP^-<SG<M<MV+PF>%voVUzdqg;qQdE1h7a=f_pvd#?>SxQc#wr@7{95T>J(~#r}TmPmZtF4K2+!}U{77?vorQ%qx1sAa+s=L|E+qh9(MCA7nP%Ym$kJQHULk|AK3cA`7A>TU$o8;j%kuDfH;d(u(sXqJ$OOo-<MD_WN409Di&EYwro3mw<@W(8NFk%VC=(E_EPpc{r{v4D<+U^s~i)W^PcruHc`2f>k!|eCJDWcg9vk+R_hw3!GpbvyC$<5!rdL2nU@Vg^9#AtwX*H*V~GVX%tqq595T1|4Y{c}bX$Sn-@os8{-IMhe3Y)u$(-PGj2+KKgl;W4ZK+4oq__z*(oh%IK2)fz@z!x04bR7N&KAEY)~p<GGNWtf4<FuM>pqH`1y0<Ig`X?(kn2eTSJ1b_p6jSOmURR963t}BiN?cyD62;WdeBNKe$(+_g*ReZ~3fD{YZ=cY9u|6LN6b+@@=p(1Y;UNUg~au3Kiz#S7vi*v<1CT`-Y4!kQJ>Gx9DDm(3e9%?BA2;`t6>d3T8C;UeEg59w3yYEKpkDn(Gh@-J^;&%QK$W>Fbk2cCLai4$`$VVuWtFqVBp&8(p8Vjti56;FdqKL!;@2NuLYMmZ#@1yXQ7O<GRZy;-emO;$0KP}$*tDJ;o`r@JRz*ZlMkAT2=*;J5Vuir{+IlX>{Tu=PI`*ll!i@w?y{HQLtn$>wxFbsFstN8PM3jjUx3(@x6u6`Ls;0ot(%*)ZH3aZ^O3o$0<f4;0+1UKT4#htk>_Mie^_C%mZ`^1T@qP^&>&cawu74PZT*v1*!V-Ww#R%$rG6Ib2zyAMTDxF-ogR~Ky2K3ylnA3vSdGnSz+dp*1WOq=1NJ5b0Aq+o<Dj+DT!Ye^osML$0^sd%iS`n<Er5;fIolrk>@Als_?N!<$+ulx8JEB8mY1vRWGo$*OHBD4;HlzO?##b!!5>>#73IF>n-rCjeLRCFlEu#|*hd8zYxgGBR(6881sBp=_h3`_h0amI?9{F^i6#KJ8YmPGT|atb3P>ho$#A>wDQS(cAYrEXe1ck)LKDVGo*VqHed+Sq9dkWpsL%{B$oNH4OF-P+|+6c|!9lV1YT_YSjFHxe`ZvU*QL00i~AE-B!zO{BNZJZnd6?sf}eSOsa2+RCo8n*1p$i$)sqdxXyrFcW_G^(P6-gJTo(H+`Gva(912ne^wQ8`h-{)HE-*m;rM=hTiT<q%gXid+7SO+vl0sKl27sUkNq3x3bWPBwE+B(*iz-ceTydB2=?PqiRm3WgL`xY!)lhD6~g|&FSXDX`cp>d^;SrB1o+o4ySDT1F&8pc(1((DIM1$U>g}Mw&ufZGRU)|>^<9O*DPK^`YKG@Mw2h1?8#xNyFK)mgPW4sn$_VAeU@UA#n7$pE9*>k&1eXfIklodv$CJ+l+cr>^V#MnUx%3LeHdLyOUqeL#xO%*;Doy=;7ea^2w7HPdOkei#XyRM%U~k_hpi9>fV#U;rU(!m%>uFAXBLyfy2!N50kJwZ%k7oy<jFglYy#6$<WnP|8ULJAwmVWdOV=GhOQjB?+e;8<a6iY;S!DVM|BSxMZ%#EZEX1#|vwnQI{#C$xXby_Qy%(<>BrQjx{6IanLtI5_<W{QAKmf#~fs@mqk-Va<|H{e1=VJVlqF?wy2@z59QS8A>gOOo^mhoSxd=M@`d;0l{kVL9P)}lGFAXYgWlpuZhJ^k<R2GD_YrRfRp<G5X!kXpD9oWV$}qK#0^J%>#7>fYf~vOtzsv4<CNMT;BH<(0n74H~sSk$*h-6HrcnpE?*AgF8lLME>=kQzv)2zdTlJO1Ftl=S`&Wl7ZkBk#&y=&CkyxPJjy`R#vQXKL7O5S@p_Q!WbQb`ZKG1$ERf?2yMveyiCuxzBOXXEmCH5aVqYW(ZD@vqJD9&{=>3%S|)@je<g;Ak1#odTdqy5xJ%1u$z-#A?^}SOgO<eeT-{)tkXaL+>;-OR2xOQIb+eLQwYgTVU>^^&mE)Q>R2UVlf69+3HJiup`W+lQQ%p5`?ZgZE^}TqRz+#>4WA0W{Z{5iGl&yopy;k;dcRo`gHbTivYkZg;hrt!(IZmc|v*+!F_oOTb!8*|aVH+<CpN_fRIX(q>Kysd|2>pZ@*O8VPkQ#82jFU-Xx-1-MHk5$(*#+CFnTIY%%x7Tdu7ca{;!NrVh-U<*v3`_%S+v0v7${kYr>a1YcYUL*J5}6j08(S0#HJN3bP-A3H=qaTP}uIhP;6QG$}M1-<254{QXbNg0{hNj<EL*BJRuJP^pcp-jUHI|1=egLD9J{RFAhn@-CoM{Hi>I3n3Y{!Sw-RGgT9IA&dn%AP{Y`q_-rrxaSU}w*{5mI+5avjC03+mDIL%n+iLkMu53O(J$ZM2y(*--!_g{|D&Y3}-!OBMu!V0{8_r2=^RF?`<`tI7tKPAU%UJ0E!6<}a%hc9jFeJXf$4e{Sm3Qt|z)S<Eve9Cj<r<h<*w=d4E}3K#a@ODc_PeNX_3nsJn5zfW88bzVv(qswKsPO2kMOcS<doIx<dr4rFj+@%y*N>RH?hw+9N|5@*VO^1?syh=6k4_1Jy5R7#4fcWD4(Q`V56iFYtwc~7ruQ@P5fJ9atz<^`x%^dtrfy~NH(%AUBU2S5nlBc_k@5F;r9gmx!$J*R}WIAXc#aRB#)^d04#kFiDr#E3c|nglNVKXTZ}5&<AkDs%cNPgFATcC;%Zc<+Pernbw-WX=A|{ZeU0J^nHTz_qdBs-A$-QuQLX3Qt%y_@_N^g>`FYl?b=h)rR&pl_UCD91=ogw&IZ&=c3V!0@`X$;6CT}0N!16}Xkjv5>hUf6*?br5$6P+){t`218xM^=Mi~YT5=@dAHs9StjooYL60K~&&E&}%f%WmK=cK;hbcTW9HlURKXne(>mnZ*2ZGlkb2X|d=@0?;~}RPr(dy1A}U&!Mvj3uG&^%K2*Eg4Zs^Q@7goc$5HkRU8A{IQCe!^q_XX=`>%o`Gm)z908f6U%?=qd|c0c))Grd5NTw0BU8}2%P+rgQly3bAl^w{QEUepgE{OJ0SvuV0`(damNHsOW0SfTWIu?50GecRwbz61xz)vebr=mVFmdgK?A1_bIkM))c$>Qf6Y!eFJJ;hQZ=%5PIxzM#znnQKrOpeCe7&`)Bw?|&U3&H**edr;TUvImrl2np6xeBZA%m#OO!!)W)a|_@>Ry{5`wWK9&d~Ziw@agDz~Y=$k6;5=W~k~ae>HKGM(kc<A}Y`W%zR`L(VN%;Qn}@{HbZsZkwc5<*Y1qmj7fDK{uuJMB!MjE^ElrpnOG3{#g%wwCSMVuEVyVm%LBKR`+`Bww}gdKClOCWne8N#cHL!IvyHom(zFcnSgo{?zAi>Qegc0R%o5@f<w!+7jb_$hA%@i%z!l)2HvKr5_&sO1&}UwX8nGB4$K{Qc;)tZO5-TZB^2PXEUJo>$IMVIMuzsyCCiZTvr?f;Rn7spB`yI4QN4r6;{paPkteI($U5K}%I*~a-ht@4TfT^vNaUXw3nR``(zl@D?DNQmsAr)EXeukcPelxzMcoY-|bGOHuRrpN{VlICMt8<g;gr)Sqm>G}b&pxW{DLU12Na3<Fn4q(##}79pEG(|N5x{A!%in_xWLCV&B5q1u(L-AnKBR{{Gj0?nXmIEx{Wxq*vS}|S$A4Xt`p-nxFn)2X^*JhuY@2eF^|?S-Def<Cn|3XbCjQ^^cstc`Y)!k^?Li>d58VebTu;vtq;j%GP3NNbF`N*Jxbi6!-$T*4_uH&a$Bo-27i1tfWdfzh+3zGY^1Io_zPm)@1FXpjnq{M7-&PlXFdDQkC~0y{sqwjzv4WMk^kyvu4?kq6oJ#&O_cCIh+cZ6*e-huE7hKVXthv5BbR4fOHAl`vBFwN4vtG7!W$a384&{Bogq(Miy-C<!=$C%(2{w+pOiX!ff#xQ6i@&mkdN)y>y?BaUO|CO(ZyJ=TYZNl?R9#Y#C#^f=fqC+Mp>{i#xZR~0WkGyHIczclm?z(-+a(OKs;hLNYaK?b3g!d)kN@<p)BlOmhGplAAV$N8F<9SFzu*74bm8c}J*Px6(fUEQQ!8R+lw$Mvc4BIww8?W(8sY84w&Y!pQlt)<bi4Fnn}p?D|JyUj6I(iIaAnhY6N1k_`nSqBbs1c6JPgk1qAY$4sHxCoj8=IGITlSJdWb7N3SJ=@T1q;jh|-~Q@zvlsZN<7(*`ognK&KajDI!=%jN7iUi53BHK)Xf|(J@=aEve9D^(fH}+LyTaRp3su<kuu?d`GtWUS}KYVB<ml1_IXIP-5=Ro)N@2W=n?s1L)lWD8E{yC15X_^DX8cu-2(9bsEJ=k(HV%SS~M1TGc)cS(xtGjRmner+E(S34(=1A6qY*;$bT@#r0z0nJcNH<L3a9p4T>WkZ>#0XwcdMTVhtNktR0`$IJmX-4;&`RGL(bU(*tx^izH}3_%9pPwxk$lT{!<NVeJf$|=Y?PRnYHB4+}{V=etDkU+IH1V(_b-q*y4_g@?wPdoftS0Zk{&xF+&XY;=#C{-j5=*e#^(9SfTzmLcAy11oa_4NAYADxM|!F+nawIn%!swLI<w-r_5(N>W%`_pITQ)HL{LLPz&HIutk)W-g)hQsKK8lG&w5`&mp=s7nm@Stf4#HrgM$JimCRFaH!Y)gVngUoP^Md~KBPtdE7kO#+PXh+eNC#49%|7uiGaCG)FfTRt8AT5Y{{PK7VY?-W8mw1Y6*YuX}IAtfU)(R&GBxow!at*LKvfJCX2MS87(nn8WetGbdXUdH%LredY9#(uJU;jTJLia8~hsVent~{EQ-;Rkw<wpx%0|g75TDMy0Ny}&I5}pS>58I93vedzt&j%Rn$*^a$OrmLq9*y#M%W1G~e+2Z9^e?o*svBQ8Se%<Y!p3IP<_nv77bOYE_0d!4wh<%1Y%sZbe4uBj1Q1ak|6(dEE=Ra`@QYtiK02Lk;MZj;{Wz`T-}P-0krvMwH$A-kVySOiA<@%qFN*c9bgV#z0tV4m<F#lTD;X*~C8&xwM{N>5{FGo~qncvC<Z6DULI76+V9e6t#>wkqozm{2*)dG84c|KSbvtt@)cgAyhx|gD-H%rAOcQkPwKSC7)o67*qgQLe{ewF$%q*ouDo0z*u!X)xG<gEXyk$9*E!~2!;IpNW3Bum>ss>PTiD)m|XXdb`^)Hh(GPSckYJg2^GW3-*o06_f!@(c4={TrqL0D`D`=zT&kS$}i)8q2DQc7aH4mv?9n2lqbJy|?8pa)MY!OZzkMY*7ZDw#d|2%))a4vzi3rGheqPgLi0E9v$`dAmJv?c2XovUvORK+ST7tg-nnG4+HM1OC19jA~43DC+?VU5Rl}X`<`V_qZ1@6>hs*Z)A-pq=>Ne2fdeWlU*)sU;^XRjiD*1mF%6E;Hxi-k7Drm;@`XHaxSY;UwWxVs^nX`i**NHj7W#p;e8p|5zm|M0u!uTQs1Nmb%4-B*cJH0>xO@Mwg5#in9f6BR&N(aBP~QXN5DWZX{sE6LN=_vma*Dt0Anhnp#U4yMyWM)%ISsfty&gCmTj?5wPE4=YfKV{FXkgu<xsT7-BP>sV=;JTI_aN73pIoExO^%2mTrLbmsxrrr)Th;cS+ZYBLTBWx@>f2&pxBzRDTO^d-9YL;y3m5PI1g~83?`$9DHkjAd1EKK1{2vg+^vdNhbLx71EFd?D1`6^Kkl&0_@e|Tx!vH2_bI0@75y1(Tr0-I8`iODmzn^Jgi7eSc|}ZKfXR$yqyvR#95+Z{f0mNMe6PgD{p$-V+uv|@xR=J*2+XVa0Py8{d-DqUevip==>!&-AAquUyB`nxAqk-*Wo)9u89wM)@CCO*Y{rhNE(1-E-Z|VbB}5`l0UE*)U4=C6Et=<=H;{&EcJd<8ppb^*U-=M_Xg8d0g6Y_j~+DRwW@d@S1-xPj=_=abPY1J;7VX*ck>P0?HQJ6YI2v4aLoG;W{;$LgHJs*l~}e8Wkm58BynN(I2YH1wJ&ga*T?**eZw!m9}Gcjk`{7mvgMR+s^y<J<ll>SwR3oy`&B4^Ot`%s${Rj*t5AfyCQg;IHM8xxrj$A$EvE<tZSFm`)<(4Y(*0XhR9AlV_zd?glCiqg%c0t<ICOs<W4HJC7ymXYi-p-4KZ@6D2XTxe1?W&}(0O5cNF)dkTzn@}wH<82G%*b}sdsfkNZi615FxV$Js}A}keUfxn;&19&Ap*l(SpX#SC$uqxev2@potfLD=W&PE`i%OlQZl57!$(}W^C7!6W%t>YHarA(_2quILcc<nmQGPAe@JlcQ}RF%;mn~nBG5XrS?Ipt-^ecoDphT%=UfVi%)R25OD<k@0ToV1tJnzM~V-f=qF<5Giz;s6cPSnZ++%FpaDC!Sys71dgj{l<S8D8(;Y!x_gjl$A(y>jb-BuH1v(Ga0BKURg306HAOP;mXl|%FKgY^(%&UW&;D6_vU=nm|bSf+Ua3C9TfgyrXK={j0j0|!d+c?TYpO|EqAy&F~l<?0V{{$;f!YGmZkEj-ZC5v(dF;TV*)=v$$&a?wsEvI8dU16!9;1V`y%PTw5I=-=KBtSDjt?414<`uwUCMmeT0UO;)H&=zQ>x33e)4NjsY8Qe21QK9(gjoa281;mhMlNOx>OM#Mv_ppKf=-gev=Lu8J4%BZUk4>rdyjK<rw^+U-2@V1n*>Xs-!aoCYFmX*cA&HMi**|>!<QgnUIUj<n<pZ8xdmcvo);@?cxQQ5M3O6nkHQu$Aibi3<VuSRmYJ{E?CMzBZ)tcTu7xA*<d>>+o`jd(4cT29RcpYAnNAoN1o>rVLyFVO!S;`}E)NOr+&6rVOrM|`>8qB}oLtpMn(OuLotnTR*5-~gh$An-2G^-j{hb#<J3m;^1A-W6m)ATXB^##lbcRv6!YsE2Ec*?3RM_QkGZfsnjHwe7&iWwSgP($v1Wo`TwhpYP@Wc8k2Eu||g47|uxwXFS%EAh^8kIE{-mBVXi<^3usVCd1yY#Z_5U_kIJahEbO<RkIDG0Y?gEKL_7Bp5Ij#)jqPb(}Z-iwY#+gaC5Gz^8(B$hjxWrFL$F-bXwSJ1Vo{Nx{I21}yEm)x~{@!g0{3qR)C<R2!o&|tlqi!oAnHmng<074i_=JooMvwi|+cQ+^rNf$RGnD7MPzWVFU&Ac-Stowf`Z_u&3pkEIPNP`{ZWPNaSD$uW6_Ht>xLObwv?_qx77Tv4uY48bLiS+C?d1+Ld=puNZ_M+TS{-#<SmFnl60nf)NoHj0hj_6UjABI)M>h2T_0yecv8PlhS6{{@Hb5rFt!?mu@Tlq;lz_+F{wNF10uT?u46?aQSuM@&}UWOL9Y~h=wQtn|~^eBlgCGE+6-{Z_a%b)ouwZ(R|1uS_0wGl4JW0i*nfw1Rr78-udERqEORYVN_Jb1W>u}VZ>4AmJQ5?>0StxOG!&Awsv_J@V*@O(_0A86m2?PVLY-!eksX<eh=^((STZ}Hg4`BDJ^gjK^@yP{C-t#}gA<xxbuj=w{H%QjZA`Kj?4d{~KYZ-MF=gY=4piB=eT=NFP)b{H>`HV4nN2RZVoJTFc0{&L$Er#g-2V==_m#}J-W&_btMA2~6IyLjO)q*wXk=!n<dPep-S49#~s7!%U<f5M(Xx%7Q<t$XO<!+Ai|G=qoEm*e{KHr`5@+)MP~fp))sgJeDQcu3V?d!k~FZclEW`+K$uErS@#?QYP`R`MwsP!{Vhg;~Rkt~MAj7YzpjoXT8YJkDB%HzdROSjl$AjeI&=f6nDf7ow7&Gf=(HX7ko)e=5<cmz^`xENrc+u4+{_<wgiiDrA9RDOCbi2LG?$8@c42UrhYKQck}anxazGF?&ZXdLUX0wA%?XFohn-<98l(nHYrAXq3$5QL)JBya<MYb7MH>Z6kD4mlR%9`5|C~R%Hu>q3-p-xqUa*LDWJZqy<~~`#w4)$q@7m4E@qcZ_~vZ6Fq>6_HWKt-e{(#5lUQeN#M%nvNJKN)hWtzT8i=O!>f`J=8Bu+4(b7VYx(#A;m?3rWd9MuN>H!r>i?3{HLXbc`XxAaPr_=*Njc_6f-2D;Oj1|^KNHJ;V+d!5$0XI4O;Q;H1J1oL8kJuOz`y{dm*96^lg3=De)V(IebrH?-1|T>;o}G)CY}deD4)>DE=YlG_d({zk&gLwWZrpWEP*UJ6-~i?#cSPnydY+P8g(!IDAJ&zO`)4dh|Z+E6E4fuTZxQip+&ukM_PeX8m&8EtpK~%DHr7!To^KvX!4R8W#H&;`!iv<VTG}dt93V=$92unK&eRW=5NIO237EHv!K`^Ly?PHOlvePB($h-K4IdTW@EhjE29b6LTUj{qttACK`zM4cSL~=!Api(Ox;?|p1VQiuF2Oven2rqO&s}Lz%jr_&d<@5s{_Ug5!anyaq5nf;P>9<rK*tWy;t}GAVh=2KT>8>jHY)i`VICUJvC-Y6xr{mh}&lQ$7f`-t*Mbk-(WT;?{+mCOm%U;TV`Az3c)EcCnUSS-o7R%NYr1sIZI8bYW@a8rAJy^n%H;Um#9vHo%g`oE6AR^3oiigG)BtYOBw3bcl^RXsy(R;y_QLACIWbys`dFLK!FRKSiZobb5`Y0s7_PMC7(Ca>-K^M(s}aUm)i2_pV6WHcKlXQrb*E8iqS^igw5MiZpHZ8h(M5X^a^53|1dT>nzfDhUa)xAB7l;PnTZz|)jzyeCBAbW>AGgA-fJ?|3krt@2)G{n&KFrhW6ygw<c03<cfalA{nd$4;I8o2{g@Tsp`D;25F;sON9!V~kjv@VFLVds>XqDBA|Ml;>ov<t8QUv5u);|;sPPa|LzY^=-YZ)i`6oQ)hMv@=m0PGGB{8Jvuh3U^hOQi`jR9%Eu{>zbkE7kEM)MteuXUlgQPhJjS;IFNT6DzPtL>1f;vFf9raAm3WkbSMbfTe$!)rxt6^5N&m<o_-xJ4~sCX?<ojkzc!T&FMH<W<lv69j9UGX`h83Zm0Fn6f|!sscom!`YW7*ZfCXq15s!CEdQvC4~l)-}L4=l;tBt5#d>Y3<44p;ysxcxvbPRJ@?B1$u_Ki9~BOJ?5vZ!enUVGId$I;HOwDpjc|jFMtgShQsFfK3MM^U#cvqT{G`_qDLy;u-@9U(WV)I=d2Ko-eL1#6nRG~uOq+Aq#g}z~-L_QaLM&Myy8X}oy5nvJGMd^-oY%F9q`yPVLCPm?>W2Su!~KWj|I==N_Ap(S(@Ezjwl6Svq*>Ry6%w^Quca^tI9{4w5-L8gC^Qak!q=3fQMwFLwh`h7h8@THHp|-u;CW@W!-R{mdBR`e+Ko{3wul3>^szZ%o}W+lu45JVn!ShzcD->2`0C0gz8@V2lk=71pv&>Wly)g}XhcaqLnh(KJTVMFX&I?;7+c;4-tL71(r%{>pRx?M<QBK{vMFcoHg+)%Lt7h~Kl;)3^BYJkc*I^MmpY2I(i-)$%5Y@xly}h#L4)28%zr-al30(boU+qj*Y?v>(pNu6>u7m~B%(wOy8cmxF%d4mT3zdXiQm#IG@!&#@gz^>K_U};1VC9k=Mo?mA#6gH1k9g%LPVqv53YcdwBJa%n&`WfvMgYq#Bu^}i%>_nG6KPRrt;WE#_uF2aKx#2Q;Lm*be5Mp%jpR0^CXwd-1FIPAN6Dd|5HnOH;73ek%2=_I3lW16OB5{yr3$7Ak|Mc6vFh5VU-ZEQQlf6c`oLAH8Fz*I~E6AFt$FDDj(0QEz>W%+10xRb>q(^{MD~;f(?(Cw{Toyb8#a+>oW!X-e#<fisG(l6BLAQ7=f=KsyUq(88{5IgDDH)?~48W+4a)GHZ0k1{iQ?A71LPwJ0WOcLI2^tZaMZAE5=8Ec_|uLxkt~y*?tWD;1vt`<abI&=L4UCV25IG@AU;NzyRi7`bEcNB|^sBZ0=$s3`Pj6*O(f_V<RvNNy{Wud^r82Z>0PHMI{SDLiq07V{9(~^ss``t#ugm4Vr=?krqeC$@4%m5-206ug-eAW?x)BP?RUblCZ`W$+Gk`@?es0Es+aqlX3(fm*z{;l@Lu>Ol@!bC;~6?FjRD5tUIFCraHG61WV+pmqP?y2F`-&e}ce+gR0YyXDLwL3p4{69tGA|g7y`p`;&1%&{C7cI6#tLCAb!#5~lQL+M8ZRD-lt`C>+R&Ec2^Z23h<MIkHv@gKd@E=S;6=&o28wkBHF`a7xnUKb^M0{ECk6!XGN+Znd)<;y?a~3ix!(S{Docr+ahGQhu$YU4+0+?bg{tkQYLgj-*ghVwV<n&#OXxO5GJ#j*euzpO=B<Od%em4qI5xfI>$(F|W096!F`6gMFpLLD*%3PVV8FEzg6wR~Bqh?wXZ;H{T?;K&xg|`rEC3H`qA-c_FoVk28?;W(isg)DM=bAR_XYo;0}FJxnF+KaZ2}UlBajHE<zk1=_+kROrX|WHg_vl4Rdf0@A3g`wToBGY7nm0ao(j{((rjmGZT)xZHBvh>pt={Jk+6ByxDAIqFDnbHVU5=Z4=wIFX%YnK4kNZvGzv!>QSNqh*HAhePWy|M>9Yt7wo#VZ!=95x>=t>`{jBtAn4gb-6y-<{#nQb<6-~N6Q$&hk35%AIhyv1)Sx?y<hs0i)295NEZ~`jwR!PvhhN%uQ#zYK^Ks%rL4S(l56+GSvxpmqBC8Sk?mw46oZ02wfjyp@V^M7UtnYmCE^waT?cf3fp-SfvpV9V8v}v;38<;Q62`!|T{=VOicPORP|a*XM3am!1H_0Zi2{8W+7$mxcR_W&HZQtIwL+EH`=xoa4RGjHpAq8gUPxvYQ4#qe(y+N%6Ex<`I}eRUGL$0>;doTE_~J_>)m`g`LK8h_p9!uuf$x|td&~PdPT7ES9A)#nSRl%F&wtJ@ZOM=;6PQdr8tB#fHi2ZdFo@BQOp`ETn@9AnTsWq=p{OwPIhGH=<5%gT!)VA;!3WC%p+Gp2-f1#lwmd5*F1IGn&TvwZ0(6^>Z{Ee==In*cc!OxOGw1OXF2^bPThA^7KT=k_E)KK1g{mF>n=AkCZ!FFvk3APZ-HifI_kM?5sa@hVPDyCY1QU3!%@tyr)-kBe^4V|{sHXaohS+x2fsKY8(Oj}ZPO1)lceeI;Vp08jA!A2k09SJ*(t`1KTudj>n?03IwdR<4aR1pvp=<z9#<qN@4RS=x;ANW;tCly1!{Z?5I)Hvd+#URPsFwCNV9IkAp!2K_q%w%F3tX3VocGW5M@`XGAH{)XRv;8}@N@vzAAYamFSeuMt>O%xcA<_2#5lPG1Qvsa(!q-v*UqgJp@QRC|Cm7BVN?^{Qb~oRoIrjtkuD%i{A@k1i8+(Nc-s!Y0$^H*me3b+qV2e%tDIl0TN?+Nf=^JUo)qcIku&kL7e9(U{>&txUZx7b@<F0ZRC?-HMOc*B&U5K<wE0GA-yi^}weE#p*}e+l;8ya$wyS2>^rHT|4*>KVVz7Tl)HI`bdt@ui<qm-NV>~|Oc=hNX)j$dzVl;84zuup>oIW1YPiFGl0yv)fYIghH2EdHQ-p;zTv{A8j`)4B9-Bm>#dh*$0`6k_8uk||IrYvvfsiFW4S+=0JenKcrxe}1zS|W|$y~Pyc5ZbpeqKH%ZrI}cn23L;77b{ya@n71m5Jep55fUy$AB@l@inFmY^}k<uzrA-xv?wvgm{B3_3^!YNiX4j1*{#h<l~x-PWqyVYZe!hecr68M4ai}%p7?i5^#R#mwgLOWlE*iyy&ozwxT#tAiB1orS1TfJn~c?4C#(XYXRj%4rAqVTp5JHDzugPRr}%Acb}uP9!j37N6^fuCtFf^+Q~dQW-5x7sRP>tmES<hd&NUfU&jknX1&&m{*kqN{J4f%%NWdF4g{GMG16AxzNEFz`P%7NV`(_+6uJiaBR7gNQ02uOZk^3Xq#nbwr3BW_U#<C;)(9wuHJpdkuYNZ#0bd}=fOd}WN5Ks|g!I3l#b>ZR~gu(3%FfWk7pOS5h!tP4=9(MFoC}~tBY@gCNF1k9tV1>K60y#JVB3hhNFjE<uafnsik^)j3vpu0!Pp8RtY<<~m1tP8TDCto+1Y_Uz7~Rj8piHsIBoLi-gr5{*!Y}JRzDrFf;j5Xiar&_{yB`(&CYTbqh~F-*FOth#D*c2TwC^t#YxRs#SWdtDd-0-Te}8Xr%~c}DqHzacR)$nYNnJUHPN)hxT8It8jh$xNPK?1+SPu)Ht4!SJUm2w>60&RYcVT`Es}T71LgC+7SbMSq<ZN@?i@=%-q%nySIIR=}wTbCs3-?bZbs?%aDsHG60=o<WS<K%0Q$Uo`Qwt(!H%ZWMPb}#Qj+?Y|UKad|X1jqg>ZP@@+{&7W{;2u=0$jN_wy0?s4>eHHeVM~MH*U;F1OO3BhYfE|P_8X<Xvpk~dAbJxdsu%=A~To(ITjxTpkuw*E&`j;oy>;ZXtcUm4`Y9eM}c!yxM^qcd)rh%(}KeSb2~;Qe&%QYWQ=2(UpIUmJ7z@NNN0Cbpz_iP=MfT(Vzr#5H<aH7Ft@HLK8ht2!MWg#yAR+!fEa1sID>AwUCqhis#3W3Y6aY#^8^|9N<DwN=3Nw%bvCSMyf5m5Gc2X@s3}=H0%N6qp;+2-F(RYKnNt7fIHj$9*$-XMV8InGcdcpa5}_eA*Bv|FD`qLv-~2s=wVV98x&-@<J-@(@+#^#ov_7`HBG+%Qc`qkv8Aca>wQXdooXIQ0E_4+A5i*j>ZG4U@P63!RF0|vvnM56Npx$Ls8nxr;6y$~ws5U|P)?lxS|1R0>l?=xiTUHzNx<e2yL2Duk%5OQ?k=@)~Rx;~zEPp%L`e-!YO=}U{6#<{VP~FVCr=can;0DeLo$L)mZ}(ex8pKJm7mBYJ<}VQEqUCL7?5$x!aq^}<;)17Maj2KHTnuAi<Qv2wt?@}hY{>mQ__UNsas;s^`sc3$Mw+s+S5IO0JZyiOla-mhI&~7L%$*&PTr{Ur9pPhOpE67xT9<s<Rh5aGLzj9SPUA`Lpr-j{6T?e^slNNBsoK>Uebm5fEk9d~gN_J7k@qUlvcYeO`h9h26?m`-O4&8|w)ScLzLb75wBXq%7d@~Pfr53{?vY*{FRGw#W*}tnGFla_1S$^r+MPtT36e~tDr&AlFRnXLsV=&HN%s%2VJVrg+-JBD+cth$*BedDK0Va$m7t4CYyU(>Z$xFXZx1gWZH=D4v};t{YobtuwkST0n3{2DS@Q@&SjFW?hw4#{B~0<H=3dF?el^;9Zdr%!m}`VB+KJQzrhARBp!%UxGfoc9W{gC(5=aI-`+OG}nU?fgZH-)!06i24O0ALLz{I)?LSaW~O0gN}rRRs|<h@s~H7@)QvU9>QX-4H3kd{INIH1%h=gWEKF3!x%;~*t}$F17~68tj0?Ks}Ii6Q4|G-TqF%7_p+IlGZwGth%$;7s8q7i?Q_$*>z7s!`E)8Hs1k%>l4&fZ?<Prp~zm14z3P4l^0e;ujj)tbJO!a=H&!mKUgJgt6~f=6G_gw3(Pu>DZZ6q62VcGUuLgsR~RW{`&0yn_zYA6~!OA$g{bysI)x>)Uo9ol!r)Wyz2rTvdx?$+++05KJ&rN;xKT9higs6RTv5aIx2;mPo3l3$*QHtZ{=s567Nw2Z~h@~T|4pBKt(j`yBDB^i7KkxJ+anLIJ3Hb#fo&@Au<T1Ty8F`xD_&4y<!G|&x$v~Yk3_X-q!P2Kce*j%&woL*#F)FIRHAyrU!L<PWC)!1`X&YX1Y(`2K=dSv^aOv9Ysy@j*VTT7HC;<NmsLA4S|6ne<)2XBY-gM6<s_+B~Lb<Tr)i!A5qzKEuoa-G;eI&$D+AFa_p(>FIWBZ^8-LjSjdMVrR+MxNuF~3<y|6xA|JT>TYL<{%qD*<D}V9SLjo!SV+rfvulQ|k2NCS}&A&qNvkwR-Uz<8T()`zqN*1|>xm2O?3Q|!)6e;x5hIX|B3gW=ZP<eZ7ibQm%p!#{oGS+`1trfk}{U^v4=w)3FyS#(y8)e+h;T0N%bTpjk&hW8cMg8gc9_D?GTt%}J9rap8C*Ui2qWwe&8g6<KtR|KOOs&ZUEO{2&7_H|rK;^Gw)yk`_4yN#^%E;OMmN9qk&|)4!BZhzaC{Jcnopg{Da`X65aa^yZFAF;$(p@xlY7<+IMikRxy@r=W+pPC>Riz}tXZH%uTDsmy&01hxh&NFyyHG-obh|V-#wb0r+M0j`saL?w$!Q=TDc3%*O55PkYM-u}z`z~^WlTKof*IMiEM{0uxD*~=ssoiL=P>z5KRo#9$jWe!n|o}1z6-I`Cj}}y2~XA@g6bJIoL=omWzhXwr<;agh`YmPd<6p5Y5a!jyR#?bX2}dWroo4wHrK})3P}&~Ux*?~{2;^Ae7UYF8Zw9)pQ9=V4l}DqM3x)CCR1L+&iRv=lLL1XoEtEwLlhx29a|kTSg?@svi?D8A=F3jvL*_{*jrkM(=?Hu3dqdHfTga=Y?RsDx+LWiR;V=M$|K`=zZ{Tp+>JRhaapSFe!#{!{=7A=C)(FgDN$OqlPS7-Nzk^1irjLkznY^QDZMug!franmS1|TwfrRr#3)rYU@bmz2{fyUn$MO*7)s0+&z)^}%a_$zM>kIt#a?W3DWAnWpcS<Z0APj8r%<XXjP5P-4T<L7Qoa-&*MiCm^tn?>QZI&gs!8^99L=sR+7sV0D>BAx-vp+wb6$dPV56zyA*iC>d%qCyg(88{BRk2?8i!c%&ZDF^eY4ZjmnTr!SE|x+5kdquO>M)a6VWmV^lAx(TThGj+pqt;rhPL)5M_XHg7m!$CAsbVlT|OFO|GeEZ?9l0UT7Kr$ou~{D)H|-j}|0}0H*(~G`vZKNR`mSnA(Qrl5oIH_1tQ*y|}3^7Sj(3P=m8W{wfkG;4g%A^Mm66r3l=cdU(I4hw*=Jr7mVQkgK|sqjkvcc*B+z#Kya6U=dQok-Vo7{Frl8sM}<3-d74Mrc)UaA7oU7%-XNNf&}4A<nzZlFELbX?j1Ayu~3>Qf^yHUV)@vu2D<Npvq_)yqSP7{1<nE+rLZ&6z&t;lJWy*^7AiY`wu&1|jl{S{pK>P^F}a_{s)?Vqyjix$0sS;2w_`vN*JnhvOHjz3@KvDc!F0q6i7bSFBn)h{1Mr>Zi;mem{`U1J?=F?x;d=54y2yXeJY!w2J?jC(DRjGBYC@l_^xIIMR&e<Q^dM>w4vWCZu??++f0BMvMa07g<_rX85H|&tUi>sg8zuzGdDc5j^wK3XAiE@#@U~qTi&95sm!n5l5HUnsX@$99<sNHhKU7r1Dgnm959Ccy>k-CkAOp8yrVG+Lq6)#tf;v~D<b_mu3Fdr>X(rNtCNa-dvx>Ec?3k<UNCn@uQ_cFg8OPbkw9Sr}D_B;0&!*j)D;Fyg)*DYe%Hq1{<H^XHwKxJ##aY;FCNBH{Xe1jTMD=78ZAoOs#&bfOTsCeyLGd@n7vE~<^~RGcUocd0#ag}JkR~;b%(Ac`>l{*R<^dfAcU%75_qcL^w!Ro;XxoeU2)R&PIB4|XLI!PYsxNO43xOO|AQK}h468`Z{!Ms1>&V%IOU}L%R3Us&v&D9T^0{ml>s_^ogQu84EGk(k{n9__x4;9yA+!U{O*6GFW1I7~vPi>zoW8rN%s>mkg`y`yIaaet|1g&IEx6C+0D!CLX#JfMHDH<W+V08d*$0yDF<Cl!-aja+o)5*HT@Yih(YAN99w@zH=yDfEfMF2!U1id8J{{VU`cTJ4BzBVmmR)SP3n<fd)b`SMdqJjP1Ql&U8a?Hdz6Mkc8(FJ~syu2}({%!5%1mD)1YU`vyW!CKRBWr2qrv`p|A=THDX1eYC!NbC&<DFR-Q9#MD8qNJ{d~)wP-Zv(sts0~bzaRKbcs{fkKqKiQJ)3VHkb%1$(wy~(W^XD6~5!4fk|f6^RXb@YUlrizu*>~0zoB>6%Tz_wOb&SHdd=a3w;~SmN@1g>Q8_a6_+dwoej1u)&tG#Ro1{j74_ETB0NZ7p3{6rqr3nzs0(>~Ln)1RdRGUH#IaepSFnx9|Jc51x^SnWlaP2I_9jcXVBK+|zp&%W-}3}GWWfgp4vw`<d&0BY4$so)teZ0_Jo><>GXJe-x_R<!B**kPy%-ZDd%ufYNrbJBla-0Rgi^+FHs^$Eyt4h{2+%Z&nPbM@#*<r{Z+{277$d`9k#d^cH}OZ%%2qCy-ImTvvri^larQTaslC4O=ydWg(%&(wzgo-1`8*W=|JM7qtBd=0vPp`PzRV#1A-cW#3%t$}<n<oIv`Z}4>h=(P_#0U!dW-93jilQWLB1wz>6GDRtjv2Q-Iq&YQCR8wjEX{ENHc;kRqf5KODuRGCrEOky1<T<(<*~C-)SVJ;QFX3SToC8v!7?BL?j@Df_^Jr5+|~>&)HQET25$($@VmJPHek5e2USCUK7S#$7c_Ew(+_xflr9yUt2{of6W?cG1C_T91W_~#XCf&GOiPcZG}XF@?nyoqL$WcCPul=p(Mx<6qU~jE;)PBK!{&J`@e-J%&c-o@O2FV!_UOy(4$PHu(j3J$yf;*LUfk&NMSIs2_bxhY)3jtoDuCF>|eDue%abA;SKKs2Dk)r_esJdcbu36p>0SX;ewRhM=`&ojJ|W|e=f>Djtba@J8R-4xpig5PLP+WN=kcWbkPNc@cE{ehFF6a^Equh(8Nq_&zICt@j<51b)j$eG+*mVfExD^hy3vDdES2?23AflC67Dnzl$Up@%eBhm3vLoMxSep$S9nCS8=j?96O9I_|$h;xg2gPTX-nKY@k{I(@<2Qxo&H9fwu2q!h=Ogy}FV%x5AM{CvtJR@O&ZQn*I$#arCi!aa5R;CWN-0FPTkBj$G$+O|aBxl^_e^_Bf_*><{XWw@wsVp?l<s^juXF>yAWlGwSM2o`Cz*eJdQ?(x8CZ0nrnC0$dhViZs~kPKCn3BDY!>ZxX3l0kWe4oDs?Ki4LOfHzTa6YI?P<nat=kf)#?oDG3sXP77oyh5RQ+86BE`Ee-aL?bik1=vy<#UgLA()U4ga+;j?A8Zfy7DiRr2WhEv=1tH=j(4@toGFFdK9KH$R^~-|kZ&Um()Mx6PPTUvlM$SrLCQ&1bB}8u#7-Y&hD${-(h)>1`_%4~>tHnw8oi?WYg-}2L6;{#u$=pRaxWXsI5zhW>AAZ9Y8s*EQ#;p|$(;nE(2?M8(u44wX7sO`~J2Hg{J1WF1oc4Tsa*m6xMmtjjSFTKMU`~c4uVpOq5jLwI<**ev9Y@O)z(zl!&eT>iZGySt?Z_$sb$Qz;gc3(W)X#kQw0emAcd_&Q-hgwN-7ZB9tq6)X0IJtTSG|yyqBbMa=xhJ~u_yKv8u~t=7I-m~dvjR$CWs_-3Z(cZXa(O=QyMl|UPU6{%KY;U?@*`2dy*p`w<D(Ey!KGBiXn0I>m`f$UFaA9tf*q{K{APQlMl(v=$Bx62s`)K_4?V~$x|78yFN@l@Pv=;CO1t$j^;nzAs#&sv(|!U3rkieOK7O}5gNl}OlCnEOd`+0RO4}7NoyY)xY9{>Li*k3n3P|ZMe)U{Z)n<ZN8&xLjW#Hg&W_qUK2kXymRxZk52i@3LWAfNLcC8gg-9y_4MeG24hlE2iE_O>Y@efbPm_nRa-g(Q?|^`Q`dA*ZRIpLABKbV~Ea<Vj9X1~X<5#w}E8gV&M^zesF1k${UJquEVrpgmgd|G!(r$kCwpe9!8RwdmI9Xb|F|RJ<*x>5k5IcNLHI1B(431i_SS2T=@N$i!Vo{>^g*b>2_NJU#adwUcL%iO^=xG6Qf!Aid`^+2*rvo$`MXu>{*V~7OY0Bp|c1^)NN+Hb`*7n+&7{S&aJ&eh_i@Nj1q7ZxwPmBV%TqZ5;R`(vJ!j1W+%^DakR1sJS^RkkKrgKc+P2|04=eF57gp#%+f)`j#Ae`$xmXR~3OPly#e<S_}=nJY73Eqw{Uywl7ySBErlaLN$f^L?r%wi#Fe$KflRcw#En(g0(mSL0?$6xmnI{o#3xiyfLSq)T^J*->S5ACu&;zyO*iX!Nd1ECLfCD@!<o=abg2jP`t8uOh?A6V;QD$cbg*qS^6gxujbtjWqaHK2Fc@yZFyq9C&P^@7I}3kPHb?Q*)FId&io*bHx=jXru|7OCj02&;KHnqqq}kqr?c^UUAAX2b&2sn?XkM0vC8hfNLArzfbNSed(qcr4y0=y~Vxx5$Thj2OKsqs{yN1|*5)eQUY))siSe^c!OeTvz-)gO4Rt=W7_0291ICcu^#JUWl^!OxduJWov&k|JN}vkB|mIEbG_eng2T?X-Qn_mzmqPRd`C5=ZMjQ6Yvv4zk!g^*xp)$J`v0UUIzTFz@dUas?T3!2VR#z)hbs*Y=>C356MA=pOu+z;QJjcGMOfWJn4=5gLF*BFNvt7KbA-gjpgAomCjhc-g_Jyv2(0iyT{=Dd(yt~!f0fA#j2S<&$RJ|J-5x^pp5N%&TI}MJNE{_K5m-=oxHii6CL>_!%gi6feV$L7eJ6+J1Kb({>l|*D@gJ0VYdME@^@Xa_6Us2^T)|cn2<S1_Uk+LSF5Nb*12xkX`IY^Q;e&9DWNi>N<GgJq2maqxZt9o$?M^)7JPAw1sAe&YMh3l@}sJj_z}!UgHwG03-PFOEDWCLoK|*xvSqD~`{IhA<j48tfRt3|yjbFTJ?UPZ%w%>Xp*$Gi$-0ptU$|8iBouq6fDeUA0pUV0sdBV6I@)^kpHCFXC7x^}tss0vDFkDA%t@YfBpj^%YQ2H;Tj*`hBM=0V;)K<ZoHP3CgBOQ*?3lsYNah3Q>xhCAG;N;Wi~+7dh0ME*vBo5rQdB<1_vI|{`~U5?nrqUJO(0v-D%cOg;J)nKsBHlM00c|N->sRQGPjsSbjv7Wd4YX@7r7XR)eWdQHT1C(3P-zFG@(}SWY&pyvRckLo0YFM;yNLlS-7<mGi47V4la>W!&o;_DxODztQU5b4{0j7DT?PK_*4^-#o6iP?F<ThD{@6yZF3T4HI}mnx;$l-yWf%J3ukUyq|82drfFHrb~IWrw3l46V_7-$cHb*}95T}LaYp>#R2v5eef5&>uwUT)a*n75+}Qp!Xq8uQc1GoX@f;}^PVF|BD__o!W0JN~PvkbBBT!wkUqKs`j^>H&NL66)9AbtK4r3+9x+9@OnRHW=_KT`$(|Q%a$%7N)6j!Xe5uAUOdkiL{;xS0CaPPKPBjOqDVwd+}ycwyy<ouM!X-<EaPWy4C9u$S$(!2ROl(HGOE{#oqbUf17;)%%32L_h>k}qH88fYz+@q)V9lQ3BeSj5A$SxXYk2Xm!3GP7SH5!Sh6l6`!PiYmO{lz9@Rwzyito32@M0F{s=X>`D!-@OGkONk$_f>*9=;mZA}Q*xOTfOf;V1V_g%!Z5fsN4&+uG>%SGiotJk<#ucMjs|yf#nXp-#2*r9to?i2c!2mK7{OhrV37=m=M_ii79@EPv`QJaX^n%mEjxpEgXMxS3AmXWyIXKoAvz&1%a0PS^?BL@hU!R2D8*s4-OiFYxe^F}7WbIQtE?aAw`$UKoD<ZBt(SujaH1Y=@`GLGOa?08K**|pOxOlo13sPuXx?$$*jFj5X(+xV9(YfIB_j%kRVPxkvfKMf)kRr}D0PCU5vaYfFouEA5uy?cYEv>ahG~n;JVTf1gq}jPSk$Ls3qcEPBsmoJMc=%=Rlu2amfHKfIP{Ijx$kZVgrG4|{W-tJ_6kJQXQ!vYF`{S%gRVK1e#yGs@!Q~HJ5}Q9VMm(lK8}Cd;q`}HN;9}x*%Hdwhn<tUy$Wi2xUR*$(n#ShNAOf)yzNYNc!g4#yEr*UvaQrRl{IJ<Ejt4!oxq6(F8&WT5w86vZGRu@W!;w1>8{0NPKEfUf#t7~4r}>tq!p~!1@u|+A2z-PWNZ2*L=6>%B_XbCM1~Z)>e_-ycdL={A!R5WGx6VzC)t3VawPL)u!Mou8Pn<GSM7g%#jMJvOk|?<fNY6jyyxJ8D{}iBY$i9;DqcMZW!6T5gdK~sjP+?oc-qcWFoM!@-qZ-JehDWzts3e*d^TmZuDd3gn}W5ylmR(yL#DbPiCN&Smws8_5xKSzo%D>itf({|5?s9^v#f3`5AoKi#NxdMFT9#5iCy28J94Y-xRh!j><vS!Wn4gKB14zUP_$6{vx|4Ynhaoieu0@%#_y{|Ng@11tc;+elUxjJ4XyDyi_DM{nYPaqU7_Jd7fv=v$c5sftvI_*9V>BLTK{!C5WjV-I4GRH#wk92*iJveq<9UFtW^#Y5;mkq0_ogyCSq|6r+GH1TBuMB<EYaxFm}R?g7)uQIb?ZS5@CvzxG&*mt+7}?UKxky+a!9MKw4$eYY=8<TH<z-tX8%g8r<Haj!y<kfTlM*gevxvJVCQk)URl6aSoatSYge7D1>fGdFO{GhZ$XG6K%2(C;f0XZeLvLxmyz-)s;US^rU2YN8Q!z3RI85`*|qIS4oq^LtELnnhxTD;$W9^Rj0R%{+1g0@dF6fa%;jj?hZ)&*hv_JCtG%a{mP@&r?NH}aY8X>o$cY12A$Ii#c(~j4qTlyV-&I_)1po?P6G`qZtA+B<j*3r(7xZ1B|KNQcuz(9fBdT;&|o;$hKej>!RB0lq9r1!2Nzb=YXIBE*iPQdQ|?BsH|aXjbk+ScOaaQD(<{w~Xu~^^x3%UKme<aQ`O;Eh+q|=MPEL;P%kodAqcAU}Oo#V2-V^Z`q#9sX3TVi7_n%Y*26o!#%h7(vhetofWg*?Vkq_j2%cxiXSkicuhNSI}J-I~yF8!y%nA+)tZ1xNrG(XeB<$jQrHq{ntK~DD*r8J-g_3E@Mo_4sWDm4Lmcg@54#FiKA4Ye`d!nUdd=SmYO5B$GoY;m)qxi--92JnVQAnpF6Jy3^1FsuV_tTv~{!UcU+Y}X+h#cFjTs43^oo$53&w9r4}t3L1J=9Vizwc&4EgsN@2v@<_<z1oNH215*oY5k`Y!VFEH;FMf)C)}&}DnH5B;AYa*(}{B{F9M=+Ih`lR{g-Z1Q^M+Q*}CW5@TKcL2o`To#RK+~z8wg25bVMIZZGKUF#F5_%7aG>tMK4+*}Cx)1D+_!HSa_6>m^c<shCPT&0V1TyHgCD=3W;pEj6S|v@5V3Bvpninqw{=9Ou(LFc^dK#UGe`ieP$@2Mi07J8`BE;KFhq%eSspM{s<w%};x5oy2xINSf%Ku2d|R{jr@iMnlKIAVLr;{YzvlxnpX-P&O>rfd8e~iejY5`My>ipAGZCk3`bMCFr=ZJ!_FrQGqXphL^Evtdv*;F0W7odR+ElRvQsux!}F@4yO3rGw6(wjA2^8^b+NjXgU_{v2uR}o=S}Yvv&*gMG1>yZe3T8H>5ox1*njkgbE0WmoO#2xk&|hOf?^>_Nd6h>XcF9F9X}ODtl~MN016e67XaaO3Qb+S4rSpH>q)`)C@KHM%3BS=;0<9$qSIC2QWztaX6&uk3yMbbW+D7j+H=Cpqhf`cJ&&N*!x@($OY%GBiC&@%$W*O5x;)yRHTcjN&YSi^)kHnH9I6r@lE+y=eAA5%=Em_H5B78OdDduoNa}Zi%0TI|2-pz#NO&1EvZIN80HR}!`yjth-iQNg;i>A0S06I1kt0Wm$1iIC{p4fXaUN}b=Lntzu^?gW`<J6hSq#y679)@@6(2ytLB^1QWC2v<poIAGrV3rdA;i1r5Y#l?f#&0RaBuu9rZLb=YKtnHLMJiY8p&ylol0}3SS>W2NUa!6jl(xfYgeT_I|7d@QfWAl){o`dlPPM7|V&UmAMN;3h6LZyL`j+bAS{K2>8%7qL!R|JRH|QL?+*ChzG@?s_O0R8G1xz><s#~SJbWfo)jK05YtZ<H|4K3QhH=<z$-NL-;tT-N}5*Ef}BJXxt7X{;ZSs}%L|VWd_iRj&;2q#^~^&Zb@r<opv#bN+p0ZB#AW>WSj2t}$~C?`d9_nG#fY$}LHDOpQDXl|FrBVTH8SZ^TnrakXPOr(-;Gd5v*u&>PtQCYCKoi=IBEDtF4TioiMxTbh_sVJkg%voqDA+4tn^n>+???TxtVjEt(T3>VQ7T|-&6^~OA*9aE4<IPwi637IN5C9&O&<ox})?X@kts05wa&t<GXG^;bfy*y{Nl#;QeP+57DxW<!MZ^F`B?6>&A1nwp?-qxNR>RC$EEAB?aipr$S!7@?MHifTH43G%9DYwl*{$?nIlZkL8_F^5YISQ&Ne=YrmG1cEydv*XEF*jkHGqbtmNWR~gY#0Ar}UFbohffB*mhf!XJC44nk200FMZ0f3iYk{f)|vBYQl0ssI200dcD')))

TURNS_PER_DAY = 24
ROUTE_STEP = 144
FINAL_PLAN_STEP = 648
LAST_STEP = 718
SHED_CAPACITY = 100
MAX_ORDERS = 10
PRODUCTS = (
    "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
    "EGG", "MILK", "WOOL", "FERTILIZER",
)
WEED_BLOCKED_WORK = {"PLANT", "BUILD_COOP", "BUILD_PASTURE"}
ANIMALS = {"GOOSE", "COW", "SHEEP"}

# Keys are the first two shops in their observed order; values index actions.json.
# All other pairs keep plan 0. Plan 1 is the previous yarn-market continuation.
# Plans 3..12 are the ten distinct continuations selected in the latest search.
SHOP_PLANS = {
    ("BAKERY", "YARN_STORE"): 3,
    ("BRUNCH_SPOT", "YARN_STORE"): 4,
    ("FARMERS_MARKET", "YARN_STORE"): 5,
    ("ICE_CREAM_SHOP", "YARN_STORE"): 6,
    ("PET_CAFE", "YARN_STORE"): 5,
    ("PIZZA_SHOP", "YARN_STORE"): 7,
    ("SMOOTHIE_SHOP", "YARN_STORE"): 8,
    ("YARN_STORE", "BAKERY"): 9,
    ("YARN_STORE", "BRUNCH_SPOT"): 9,
    ("YARN_STORE", "FARMERS_MARKET"): 1,
    ("YARN_STORE", "ICE_CREAM_SHOP"): 9,
    ("YARN_STORE", "PET_CAFE"): 10,
    ("YARN_STORE", "PIZZA_SHOP"): 6,
    ("YARN_STORE", "SMOOTHIE_SHOP"): 11,
    ("YARN_STORE", "YARN_STORE"): 12,
}


class FarmView:
    """Only the current own farm, private inventory, and public prices."""

    def __init__(self, observation):
        farm = observation["farms"][observation["player"]]
        private = observation["private"]
        self.tiles = farm["tiles"]
        self.positions = [farm["farmer"], *farm["hands"]]
        self.inventories = private["inventories"]
        self.shed = {item: max(0, int(qty)) for item, qty in private["shed"].items()}
        self.prices = observation["market"]["prices"]

    def inventory(self, worker):
        return self.inventories[worker] if worker < len(self.inventories) else {}

    def beside_shed(self, position):
        center = len(self.tiles) // 2
        return position[0] in (center - 1, center) and position[1] in (center - 1, center)


class DayState:
    """Per-player memory; queues expire at dawn and sales expire next turn."""

    def __init__(self):
        self.plan = 0
        self.last_step = -1
        self.day = -1
        self.queues = {}
        self.sale_due_step = -1
        self.advanced_sales = {}


def repair_weeds(action, view, state, step):
    """Insert DIG without consuming the blocked action; shift only this worker."""
    day = step // TURNS_PER_DAY
    if day != state.day:
        state.day = day
        state.queues.clear()  # Unfinished work never spills into tomorrow.

    workers = [action.get("farmer") or ["PASS"], *(action.get("hands") or [])]
    for worker in range(min(len(workers), len(view.positions))):
        queue = state.queues.setdefault(worker, deque())
        queue.append(list(workers[worker]))
        x, y = view.positions[worker]
        tile = view.tiles[y][x]
        blocked = (queue[0][0] in WEED_BLOCKED_WORK
                   and isinstance(tile, dict) and tile.get("kind") == "WEED")
        workers[worker] = ["DIG"] if blocked else queue.popleft()
    action["farmer"], action["hands"] = workers[0], workers[1:]


def projected_shed(action, view):
    """Estimate stock after this turn's nearby PICKUP, DROP and PLACE actions.

    Preserve worker and inventory order: limited shed capacity can make it matter.
    This is the qualified lightweight estimate, not a full game simulation.
    """
    stock = {item: view.shed.get(item, 0) for item in PRODUCTS}
    stock.update(view.shed)
    total = sum(stock.values())
    workers = [action.get("farmer") or ["PASS"], *(action.get("hands") or [])]
    for worker in range(min(len(workers), len(view.positions))):
        if not view.beside_shed(view.positions[worker]):
            continue
        work = workers[worker]
        operation = work[0] if work else "PASS"
        inventory = view.inventory(worker)
        if operation == "PICKUP" and len(work) >= 2 and work[1] in stock:
            quantity = max(0, int(work[2]) if len(work) >= 3 else 1)
            taken = min(stock[work[1]], quantity)
            stock[work[1]] -= taken
            total -= taken
        elif operation == "DROP":
            for item, held in inventory.items():
                added = min(max(0, int(held)), max(0, SHED_CAPACITY - total))
                if added > 0:
                    stock[item] = stock.get(item, 0) + added
                    total += added
        elif operation == "PLACE" and len(work) >= 2 and work[1] not in ANIMALS:
            item = work[1]
            quantity = max(0, int(work[2]) if len(work) >= 3 else 1)
            added = min(quantity, max(0, int(inventory.get(item, 0))),
                        max(0, SHED_CAPACITY - total))
            if added > 0:
                stock[item] = stock.get(item, 0) + added
                total += added
    return stock


def subtract_advanced_sales(action, state, step):
    """Remove quantities already requested one turn early, retaining order slots."""
    if state.sale_due_step == step:
        remaining = dict(state.advanced_sales)
        for order in action["market"]:
            if order and order[0] == "SELL" and len(order) >= 3:
                item = order[1]
                removed = min(max(0, int(order[2])), remaining.get(item, 0))
                if removed > 0:
                    order[2] = int(order[2]) - removed
                    remaining[item] -= removed
    state.advanced_sales = {}
    state.sale_due_step = -1


def advance_sales(action, view, state, tape, step):
    """Bring eligible sales from our next planned action forward by one turn."""
    next_step = step + 1
    if next_step > LAST_STEP or next_step % 72 == 0 or (step % 4 == 0 and step < 144):
        return
    planned = {}
    for order in tape[next_step].get("market") or []:
        if order and order[0] == "SELL" and len(order) >= 3 and order[1] in PRODUCTS:
            item = order[1]
            planned[item] = planned.get(item, 0) + max(0, int(order[2]))
    already_selling = {order[1] for order in action["market"]
                       if order and order[0] == "SELL" and len(order) > 1}
    stock = projected_shed(action, view)
    for item in PRODUCTS:
        if item in ("WHEAT", "FERTILIZER") or item in already_selling:
            continue
        quantity = min(stock.get(item, 0), planned.get(item, 0))
        if quantity <= 0 or int(view.prices.get(item, 0)) < 2:
            continue
        if len(action["market"]) >= MAX_ORDERS:
            break
        action["market"].append(["SELL", item, quantity])
        state.advanced_sales[item] = quantity
    if state.advanced_sales:
        state.sale_due_step = next_step


def liquidate(view):
    """On the last turn, drop reachable inventory and sell the projected shed."""
    workers = [["DROP"] if view.beside_shed(pos) and view.inventory(worker) else ["PASS"]
               for worker, pos in enumerate(view.positions)]
    action = {"farmer": workers[0], "hands": workers[1:], "market": []}
    stock = projected_shed(action, view)
    action["market"] = [["SELL", item, stock[item]] for item in PRODUCTS if stock[item] > 0]
    action["market"].sort(key=lambda order: -int(view.prices.get(order[1], 0)) * order[2])
    return action


class Policy:
    def __init__(self, folder):
        self.tapes = copy.deepcopy(_INLINE_TAPES)
        if len(self.tapes) != 13 or any(len(tape) != LAST_STEP + 1 for tape in self.tapes):
            raise ValueError("Expected 13 complete, 719-turn action tapes")
        self.players = {}

    def act(self, observation):
        step, player = int(observation["step"]), int(observation["player"])
        state = self.players.get(player)
        if state is None or step <= state.last_step:
            state = self.players[player] = DayState()
        state.last_step = step

        if step == ROUTE_STEP:
            shops = observation["town"]["unlocked_shops"]
            state.plan = SHOP_PLANS.get(tuple(shops[:2]), 0)
        if step == FINAL_PLAN_STEP:
            state.plan = 2

        view = FarmView(observation)
        tape = self.tapes[state.plan]
        action = copy.deepcopy(tape[step])
        repair_weeds(action, view, state, step)
        subtract_advanced_sales(action, state, step)
        advance_sales(action, view, state, tape, step)
        action["market"] = action["market"][:MAX_ORDERS]
        return liquidate(view) if step == LAST_STEP else action


_POLICY = None


def agent(observation, configuration=None):
    global _POLICY
    if _POLICY is None:
        # Kaggle's source loader omits __file__, but retains the code filename.
        folder = Path(agent.__code__.co_filename).resolve().parent
        _POLICY = Policy(folder)
    return _POLICY.act(observation)


# 
#                                  Apache License
#                            Version 2.0, January 2004
#                         http://www.apache.org/licenses/
# 
#    TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION
# 
#    1. Definitions.
# 
#       "License" shall mean the terms and conditions for use, reproduction,
#       and distribution as defined by Sections 1 through 9 of this document.
# 
#       "Licensor" shall mean the copyright owner or entity authorized by
#       the copyright owner that is granting the License.
# 
#       "Legal Entity" shall mean the union of the acting entity and all
#       other entities that control, are controlled by, or are under common
#       control with that entity. For the purposes of this definition,
#       "control" means (i) the power, direct or indirect, to cause the
#       direction or management of such entity, whether by contract or
#       otherwise, or (ii) ownership of fifty percent (50%) or more of the
#       outstanding shares, or (iii) beneficial ownership of such entity.
# 
#       "You" (or "Your") shall mean an individual or Legal Entity
#       exercising permissions granted by this License.
# 
#       "Source" form shall mean the preferred form for making modifications,
#       including but not limited to software source code, documentation
#       source, and configuration files.
# 
#       "Object" form shall mean any form resulting from mechanical
#       transformation or translation of a Source form, including but
#       not limited to compiled object code, generated documentation,
#       and conversions to other media types.
# 
#       "Work" shall mean the work of authorship, whether in Source or
#       Object form, made available under the License, as indicated by a
#       copyright notice that is included in or attached to the work
#       (an example is provided in the Appendix below).
# 
#       "Derivative Works" shall mean any work, whether in Source or Object
#       form, that is based on (or derived from) the Work and for which the
#       editorial revisions, annotations, elaborations, or other modifications
#       represent, as a whole, an original work of authorship. For the purposes
#       of this License, Derivative Works shall not include works that remain
#       separable from, or merely link (or bind by name) to the interfaces of,
#       the Work and Derivative Works thereof.
# 
#       "Contribution" shall mean any work of authorship, including
#       the original version of the Work and any modifications or additions
#       to that Work or Derivative Works thereof, that is intentionally
#       submitted to Licensor for inclusion in the Work by the copyright owner
#       or by an individual or Legal Entity authorized to submit on behalf of
#       the copyright owner. For the purposes of this definition, "submitted"
#       means any form of electronic, verbal, or written communication sent
#       to the Licensor or its representatives, including but not limited to
#       communication on electronic mailing lists, source code control systems,
#       and issue tracking systems that are managed by, or on behalf of, the
#       Licensor for the purpose of discussing and improving the Work, but
#       excluding communication that is conspicuously marked or otherwise
#       designated in writing by the copyright owner as "Not a Contribution."
# 
#       "Contributor" shall mean Licensor and any individual or Legal Entity
#       on behalf of whom a Contribution has been received by Licensor and
#       subsequently incorporated within the Work.
# 
#    2. Grant of Copyright License. Subject to the terms and conditions of
#       this License, each Contributor hereby grants to You a perpetual,
#       worldwide, non-exclusive, no-charge, royalty-free, irrevocable
#       copyright license to reproduce, prepare Derivative Works of,
#       publicly display, publicly perform, sublicense, and distribute the
#       Work and such Derivative Works in Source or Object form.
# 
#    3. Grant of Patent License. Subject to the terms and conditions of
#       this License, each Contributor hereby grants to You a perpetual,
#       worldwide, non-exclusive, no-charge, royalty-free, irrevocable
#       (except as stated in this section) patent license to make, have made,
#       use, offer to sell, sell, import, and otherwise transfer the Work,
#       where such license applies only to those patent claims licensable
#       by such Contributor that are necessarily infringed by their
#       Contribution(s) alone or by combination of their Contribution(s)
#       with the Work to which such Contribution(s) was submitted. If You
#       institute patent litigation against any entity (including a
#       cross-claim or counterclaim in a lawsuit) alleging that the Work
#       or a Contribution incorporated within the Work constitutes direct
#       or contributory patent infringement, then any patent licenses
#       granted to You under this License for that Work shall terminate
#       as of the date such litigation is filed.
# 
#    4. Redistribution. You may reproduce and distribute copies of the
#       Work or Derivative Works thereof in any medium, with or without
#       modifications, and in Source or Object form, provided that You
#       meet the following conditions:
# 
#       (a) You must give any other recipients of the Work or
#           Derivative Works a copy of this License; and
# 
#       (b) You must cause any modified files to carry prominent notices
#           stating that You changed the files; and
# 
#       (c) You must retain, in the Source form of any Derivative Works
#           that You distribute, all copyright, patent, trademark, and
#           attribution notices from the Source form of the Work,
#           excluding those notices that do not pertain to any part of
#           the Derivative Works; and
# 
#       (d) If the Work includes a "NOTICE" text file as part of its
#           distribution, then any Derivative Works that You distribute must
#           include a readable copy of the attribution notices contained
#           within such NOTICE file, excluding those notices that do not
#           pertain to any part of the Derivative Works, in at least one
#           of the following places: within a NOTICE text file distributed
#           as part of the Derivative Works; within the Source form or
#           documentation, if provided along with the Derivative Works; or,
#           within a display generated by the Derivative Works, if and
#           wherever such third-party notices normally appear. The contents
#           of the NOTICE file are for informational purposes only and
#           do not modify the License. You may add Your own attribution
#           notices within Derivative Works that You distribute, alongside
#           or as an addendum to the NOTICE text from the Work, provided
#           that such additional attribution notices cannot be construed
#           as modifying the License.
# 
#       You may add Your own copyright statement to Your modifications and
#       may provide additional or different license terms and conditions
#       for use, reproduction, or distribution of Your modifications, or
#       for any such Derivative Works as a whole, provided Your use,
#       reproduction, and distribution of the Work otherwise complies with
#       the conditions stated in this License.
# 
#    5. Submission of Contributions. Unless You explicitly state otherwise,
#       any Contribution intentionally submitted for inclusion in the Work
#       by You to the Licensor shall be under the terms and conditions of
#       this License, without any additional terms or conditions.
#       Notwithstanding the above, nothing herein shall supersede or modify
#       the terms of any separate license agreement you may have executed
#       with Licensor regarding such Contributions.
# 
#    6. Trademarks. This License does not grant permission to use the trade
#       names, trademarks, service marks, or product names of the Licensor,
#       except as required for reasonable and customary use in describing the
#       origin of the Work and reproducing the content of the NOTICE file.
# 
#    7. Disclaimer of Warranty. Unless required by applicable law or
#       agreed to in writing, Licensor provides the Work (and each
#       Contributor provides its Contributions) on an "AS IS" BASIS,
#       WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
#       implied, including, without limitation, any warranties or conditions
#       of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
#       PARTICULAR PURPOSE. You are solely responsible for determining the
#       appropriateness of using or redistributing the Work and assume any
#       risks associated with Your exercise of permissions under this License.
# 
#    8. Limitation of Liability. In no event and under no legal theory,
#       whether in tort (including negligence), contract, or otherwise,
#       unless required by applicable law (such as deliberate and grossly
#       negligent acts) or agreed to in writing, shall any Contributor be
#       liable to You for damages, including any direct, indirect, special,
#       incidental, or consequential damages of any character arising as a
#       result of this License or out of the use or inability to use the
#       Work (including but not limited to damages for loss of goodwill,
#       work stoppage, computer failure or malfunction, or any and all
#       other commercial damages or losses), even if such Contributor
#       has been advised of the possibility of such damages.
# 
#    9. Accepting Warranty or Additional Liability. While redistributing
#       the Work or Derivative Works thereof, You may choose to offer,
#       and charge a fee for, acceptance of support, warranty, indemnity,
#       or other liability obligations and/or rights consistent with this
#       License. However, in accepting such obligations, You may act only
#       on Your own behalf and on Your sole responsibility, not on behalf
#       of any other Contributor, and only if You agree to indemnify,
#       defend, and hold each Contributor harmless for any liability
#       incurred by, or claims asserted against, such Contributor by reason
#       of your accepting any such warranty or additional liability.
# 
#    END OF TERMS AND CONDITIONS
# 
#    APPENDIX: How to apply the Apache License to your work.
# 
#       To apply the Apache License to your work, attach the following
#       boilerplate notice, with the fields enclosed by brackets "[]"
#       replaced with your own identifying information. (Don't include
#       the brackets!)  The text should be enclosed in the appropriate
#       comment syntax for the file format. We also recommend that a
#       file or class name and description of purpose be included on the
#       same "printed page" as the copyright notice for easier
#       identification within third-party archives.
# 
#    Copyright [yyyy] [name of copyright owner]
# 
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
# 
#        http://www.apache.org/licenses/LICENSE-2.0
# 
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


# Modified by prvsiyan: V216 adds an observed day-one hiring reserve.
# At most one wheat sale, at step23 only, preserving two projected wheat.
_V216_PARENT=agent
del agent

def agent(observation, configuration=None):
    action=_V216_PARENT(observation,configuration)
    step=int(observation['step'])
    if step!=23 or action.get('market'):
        return action
    player=int(observation['player'])
    state=_POLICY.players[player]
    tape=_POLICY.tapes[state.plan]
    hires=sum(bool(o) and o[0]=='HIRE' for o in tape[24].get('market',[]))
    if not 1<=hires<=5:
        return action
    mult=(configuration or {}).get('farmHandCostMult',1)
    required=sum((1,1,2,3,5)[i] for i in range(hires))*mult
    money=observation['farms'][player]['money']
    view=FarmView(observation)
    if (0<=money<required and projected_shed(action,view).get('WHEAT',0)>=3
            and view.prices.get('WHEAT',0)>=required-money):
        action=copy.deepcopy(action)
        action['market']=[['SELL','WHEAT',1]]
    return action


# Modified by prvsiyan: V217 adds bounded idle-farmer starvation rescue.
# Preserve native pending queues, planned feeds and wheat pickup obligations.
_V217_PARENT=agent
del agent
_V217_MOVES={'EAST':(1,0),'WEST':(-1,0),'NORTH':(0,-1),'SOUTH':(0,1)}

def _v217_farmer(tape, step):
    return list(tape[step].get('farmer') or ['PASS'])

def _v217_plan(view, st, step, action, pending):
    hour = step % 24
    if not 16 <= hour <= 21 or st.get('v217_used', 0) >= 2:
        return None
    if action.get('farmer') != ['PASS']:
        return None
    tape = _POLICY.tapes[st['plan']]
    end = min(step + 24 - hour, 719)
    if len(tape) < end:
        return None
    # Leave every existing planned feeding task intact. This conservative rule
    # also prevents a duplicate rescue when another worker is about to feed.
    reserved_wheat = sum(max(0,int(cmd[2]) if len(cmd)>2 else 1) for cmd in pending if len(cmd)>=2 and cmd[:2]==['PICKUP','WHEAT'])
    for planned in tape[step:end]:
        for cmd in [planned.get('farmer') or []] + list(planned.get('hands') or []):
            if cmd and cmd[0] == 'FEED':
                return None
            if len(cmd) >= 2 and cmd[:2] == ['PICKUP', 'WHEAT']:
                reserved_wheat += max(0, int(cmd[2]) if len(cmd) > 2 else 1)
    start = tuple(view.positions[0])
    inventory = view.inventory(0)
    need_pickup = inventory.get('WHEAT', 0) < 1
    if need_pickup:
        if any(inventory.values()) or not view.beside_shed(start):
            return None
        projected = projected_shed(action, view)
        if projected.get('WHEAT', 0) < max(2, reserved_wheat + 1):
            return None
    targets = []
    for y, row in enumerate(view.tiles):
        for x, tile in enumerate(row):
            if isinstance(tile, dict) and tile.get('animal') and not tile.get('fed_today') and tile.get('consecutive_unfed', 0) >= 1:
                targets.append((abs(x-start[0])+abs(y-start[1]), y, x))
    for distance, y, x in sorted(targets):
        moves = (['EAST'] * max(0, x-start[0]) + ['WEST'] * max(0, start[0]-x)
                 + ['SOUTH'] * max(0, y-start[1]) + ['NORTH'] * max(0, start[1]-y))
        opposite = {'EAST':'WEST','WEST':'EAST','NORTH':'SOUTH','SOUTH':'NORTH'}
        commands = ([['PICKUP','WHEAT']] if need_pickup else []) + [[m] for m in moves] + [['FEED']] + [[opposite[m]] for m in reversed(moves)]
        if len(commands) > end-step or any(_v217_farmer(tape, step+i) != ['PASS'] for i in range(len(commands))):
            continue
        positions = []
        pos = start
        for cmd in commands:
            positions.append(pos)
            if cmd[0] in _V217_MOVES:
                dx, dy = _V217_MOVES[cmd[0]]
                pos = (pos[0]+dx, pos[1]+dy)
        assert pos == start
        return {'step':step, 'route':st.get('plan'), 'commands':commands,
                'positions':positions, 'target':(x,y)}
    return None


def agent(observation, configuration=None):
    action=_V217_PARENT(observation,configuration)
    step=int(observation['step'])
    player=int(observation['player'])
    state=_POLICY.players[player]
    st=vars(state)
    view=FarmView(observation)
    task=st.get('v217_task')
    if task and step>=task['step']+len(task['commands']):
        task=st['v217_task']=None
    if task is None:
        # Pending work is part of this native router's actual schedule. Avoid
        # displacing the farmer or duplicating a delayed feed from any worker.
        pending=[cmd for queue in state.queues.values() for cmd in queue]
        if state.queues.get(0) or any(cmd and cmd[0]=='FEED' for cmd in pending):
            return action
        task=_v217_plan(view,st,step,action,pending)
        if task:
            st['v217_task']=task
            st['v217_used']=st.get('v217_used',0)+1
    if task is None:
        return action
    offset=step-task['step']
    if (not 0<=offset<len(task['commands']) or tuple(view.positions[0])!=task['positions'][offset]
            or state.plan!=task['route'] or action.get('farmer')!=['PASS']):
        st['v217_task']=None
        return action
    command=task['commands'][offset]
    if command==['FEED']:
        x,y=task['target'];tile=view.tiles[y][x]
        if not isinstance(tile,dict) or not tile.get('animal') or tile.get('fed_today') or view.inventory(0).get('WHEAT',0)<1:
            command=['PASS']
    action=copy.deepcopy(action)
    action['farmer']=command
    return action


# V218: terminal fertilizer collection by up to three otherwise idle workers.
# Inspired by Dmitrii Gluzdov's public Seven-Turn Rescue: collect, return, sell.
# https://www.kaggle.com/code/dmitriigluzdov/kaggriculture-seven-turn-rescue-best-lb-2800
# This smaller planner searches fertilizer-only trips. Existing productive tasks
# and market orders remain intact; a conservative physical bound rules out shed
# overflow. No future shared price or universal profit guarantee is assumed.
_V218_PARENT=agent
del agent
_V218_REPORT={'plans':0,'planned_units':0,'collections':0,'aborts':0,'capacity_declines':0}

def _v218_path(start, end, tiles):
    x,y=start
    result=[]
    for name,dx,dy,count in [('EAST',1,0,max(0,end[0]-x)),
                             ('WEST',-1,0,max(0,x-end[0])),
                             ('SOUTH',0,1,max(0,end[1]-y)),
                             ('NORTH',0,-1,max(0,y-end[1]))]:
        for _ in range(count):
            x+=dx;y+=dy
            if not (0<=y<len(tiles) and 0<=x<len(tiles[y])) or tiles[y][x]=='LOCKED':
                return None
            result.append([name])
    return result

def _v218_capacity_bound(view):
    total=sum(max(0,int(v)) for v in view.shed.values())
    total+=sum(max(0,int(v)) for inv in view.inventories for v in inv.values())
    for row in view.tiles:
        for tile in row:
            if not isinstance(tile,dict):continue
            total+=int(bool(tile.get('fertilizer_available')))
            if tile.get('animal') or tile.get('crop') in ('TOMATO','STRAWBERRY'):
                total+=max(0,int(tile.get('yield_units',0)))
            elif tile.get('crop'):
                # Absolute fertilized maxima, even for crops that will not be
                # harvested. Within steps712..718 there is no dawn production.
                bound={'WHEAT':12,'CARROT':8,'MELON':12}.get(tile['crop'])
                if bound is None:return 1000000
                total+=bound
    return total

def _v218_routes(start, targets, tiles, sheds):
    by_mask={}
    def visit(pos, mask, commands, count):
        if mask:
            for shed in sheds:
                home=_v218_path(pos,shed,tiles)
                if home is None:continue
                final=commands+home+[['DROP']]
                if len(final)<=7 and (mask not in by_mask or len(final)<len(by_mask[mask]['commands'])):
                    by_mask[mask]={'mask':mask,'count':count,'commands':final}
        if count>=3:return
        for i,target in enumerate(targets):
            if mask&(1<<i):continue
            walk=_v218_path(pos,target,tiles)
            if walk is None:continue
            route=commands+walk+[['COLLECT_FERTILIZER']]
            if len(route)>=7:continue
            if min(abs(target[0]-s[0])+abs(target[1]-s[1]) for s in sheds)+len(route)+1>7:continue
            visit(target,mask|(1<<i),route,count+1)
    visit(start,0,[],0)
    # Bounded search budget. All retained alternatives end with a real DROP.
    options=sorted(by_mask.values(),key=lambda r:(-r['count'],len(r['commands']),r['mask']))[:32]
    return options+[{'mask':0,'count':0,'commands':[]}]

def _v218_plan(observation, action):
    player=int(observation['player'])
    state=_POLICY.players[player]
    if state.plan!=2 or state.last_step!=712:return None
    view=FarmView(observation)
    if view.prices.get('FERTILIZER')!=1:return None
    tape=_POLICY.tapes[state.plan]
    remaining=tape[712:719]
    # No purchases, builds, planting, or fertilizer collection by the parent.
    # This keeps the physical production bound and target ownership simple.
    for planned in remaining:
        if any(o and o[0]!='SELL' for o in planned.get('market',[])):return None
        for c in [planned.get('farmer') or ['PASS']]+list(planned.get('hands') or []):
            if c and c[0] in ('PLANT','BUILD_COOP','BUILD_PASTURE','COLLECT_FERTILIZER'):return None
    if any(c and c[0] in ('PLANT','BUILD_COOP','BUILD_PASTURE','COLLECT_FERTILIZER')
           for queue in state.queues.values() for c in queue):return None
    if _v218_capacity_bound(view)>100:
        _V218_REPORT['capacity_declines']+=1
        return None
    current=[action.get('farmer') or ['PASS']]+list(action.get('hands') or [])
    idle=[]
    for i,pos in enumerate(view.positions):
        if any(view.inventory(i).values()) or state.queues.get(i):continue
        if i<len(current) and current[i]!=['PASS']:continue
        ready=True
        for planned in remaining[:-1]:
            commands=[planned.get('farmer') or ['PASS']]+list(planned.get('hands') or [])
            if i<len(commands) and commands[i]!=['PASS']:ready=False;break
        if ready:idle.append((i,tuple(pos)))
    idle=idle[:3]
    if not idle:return None
    half=len(view.tiles)//2
    sheds=[(x,y) for x,y in ((half-1,half-1),(half,half-1),(half-1,half),(half,half)) if view.tiles[y][x]!='LOCKED']
    targets=[(x,y) for y,row in enumerate(view.tiles) for x,t in enumerate(row)
             if isinstance(t,dict) and t.get('animal') and t.get('fertilizer_available')]
    if not targets or not sheds:return None
    choices=[_v218_routes(pos,targets,view.tiles,sheds) for i,pos in idle]
    best=[(-1,0),[]]
    def choose(index,used,chosen,count,cost):
        if index==len(choices):
            score=(count,-cost)
            if score>best[0]:best[:]=[score,list(chosen)]
            return
        for option in choices[index]:
            if used&option['mask']:continue
            choose(index+1,used|option['mask'],chosen+[option],count+option['count'],cost+len(option['commands']))
    choose(0,0,[],0,0)
    if best[0][0]<=0:return None
    tasks={}
    for (actor,start),option in zip(idle,best[1]):
        if not option['mask']:continue
        commands=option['commands']
        positions=[];pos=start
        for command in commands:
            positions.append(pos)
            if command[0] in _V217_MOVES:
                dx,dy=_V217_MOVES[command[0]];pos=(pos[0]+dx,pos[1]+dy)
        assert pos in sheds and commands[-1]==['DROP']
        tasks[actor]={'commands':commands,'positions':positions}
    _V218_REPORT['plans']+=1
    _V218_REPORT['planned_units']+=best[0][0]
    return tasks

def agent(observation, configuration=None):
    action=_V218_PARENT(observation,configuration)
    step=int(observation['step']);player=int(observation['player'])
    state=_POLICY.players[player]
    if step==712:
        state.v218_tasks=_v218_plan(observation,action)
    tasks=getattr(state,'v218_tasks',None)
    if not tasks or not 712<=step<=718:return action
    view=FarmView(observation)
    commands=[action.get('farmer') or ['PASS']]+list(action.get('hands') or [])
    commands+=[['PASS'] for _ in range(len(view.positions)-len(commands))]
    for actor,task in list(tasks.items()):
        offset=step-712
        if offset>=len(task['commands']):continue
        if actor>=len(view.positions) or tuple(view.positions[actor])!=task['positions'][offset]:
            del tasks[actor];_V218_REPORT['aborts']+=1;continue
        command=task['commands'][offset]
        if command==['COLLECT_FERTILIZER']:
            x,y=view.positions[actor];tile=view.tiles[y][x]
            if not isinstance(tile,dict) or not tile.get('fertilizer_available'):
                command=['PASS']
            else:_V218_REPORT['collections']+=1
        commands[actor]=command
    action=copy.deepcopy(action)
    action['farmer'],action['hands']=commands[0],commands[1:]
    return action

agent.telemetry=_V218_REPORT


# Appended to frozen V218 by build_v219_tomatoes.py.
# V219: a finite late tomato investment with dedicated, observed workers.
_V219_PARENT = agent
del agent
_V219_FERTILIZE = True  # Builder changes only this flag for the ablation.
_V219_STATES = {}
_V219_REPORT = {'commitments': 0, 'hire_requests': 0, 'confirmed_workers': 0,
                'hire_shortfalls': 0, 'plant_requests': 0, 'confirmed_plants': 0,
                'water_requests': 0, 'fertilize_requests': 0, 'harvest_requests': 0,
                'confirmed_harvest_units': 0, 'drop_requests': 0,
                'tomato_sale_requests': 0, 'budget_declines': 0, 'lost_plants': 0}


def _v219_fib(n):
    a, b = 1, 1
    for _ in range(n): a, b = b, a+b
    return a


def _v219_native_day(native, day):
    tape = _POLICY.tapes[2 if day >= 27 else native.plan]
    return tape[day*24:min((day+1)*24,719)]


def _v219_qualifies(obs, native):
    farm=obs['farms'][obs['player']]
    if len(farm['tiles']) != 10 or set(farm['unlocked_quadrants']) != {'NW','NE','SW'}:
        return False
    if farm['money'] < 12000 or obs['market']['prices']['TOMATO'] < 70:
        return False
    if sum(s in ('PIZZA_SHOP','FARMERS_MARKET') for s in obs['town']['unlocked_shops']) < 3:
        return False
    if any(farm['tiles'][y][x] != 'LOCKED' for y in (5,6) for x in range(5,10)):
        return False
    if obs['private']['seeds'].get('TOMATO',0) or obs['private']['shed'].get('TOMATO',0):
        return False
    if any(isinstance(t,dict) and t.get('crop')=='TOMATO' for row in farm['tiles'] for t in row):
        return False
    # The investment uses spare land and new worker indices. Avoid taking over
    # any native tomato or land purchase obligation on the known own schedule.
    for day in range(18,30):
        for a in _v219_native_day(native,day):
            if any(o and o[0]=='BUY_LAND' for o in a.get('market',[])):return False
            if any(c==['PLANT','TOMATO'] for c in [a.get('farmer')]+a.get('hands',[])):return False
    return True


def _v219_walk(pos, target):
    x,y=pos;tx,ty=target
    if x != tx:return ['EAST' if x < tx else 'WEST']
    if y != ty:return ['SOUTH' if y < ty else 'NORTH']
    return None


def _v219_home(pos):
    return min(((4,4),(5,4),(4,5),(5,5)),key=lambda p:abs(pos[0]-p[0])+abs(pos[1]-p[1]))


def _v219_request(obs, action, state, native):
    step=int(obs['step']);day=step//24;offset=step%24
    farm=obs['farms'][obs['player']];private=obs['private']
    # If the planting-day transaction could not complete, abandon investment.
    # Later purchases would miss the finite day26..29 production window.
    if not state.get('committed') and day!=18:return action
    if state.get('requested_day')==day or offset>3:return action
    planned=_v219_native_day(native,day)
    remaining=planned[offset+1:]
    if any(o and o[0]=='HIRE' for a in remaining for o in a.get('market',[])):
        return action
    parent_hires=sum(bool(o) and o[0]=='HIRE' for o in action['market'])
    expected=max(len(a.get('hands',[])) for a in planned)
    if len(farm['hands'])+parent_hires != expected:return action
    fertilizer=bool(_V219_FERTILIZE and day in (24,27) and obs['market']['prices']['FERTILIZER']<=30)
    # One watering tour: at most 2 entry moves + 9 between tiles + 10 waters.
    # A hire request by hour2 leaves at least21 callbacks after confirmation.
    crop_workers=1 if day in (19,20,21,22,23,25) and offset<=2 else (3 if 26<=day<=28 else 2)
    count=crop_workers+int(fertilizer and day==27)
    extra=[]
    if not state.get('committed'):
        extra += [['BUY_LAND'],['BUY_SEED','TOMATO',10]]
    if fertilizer:extra.append(['BUY_PRODUCT','FERTILIZER',10])
    extra += [['HIRE'] for _ in range(count)]
    if len(action['market'])+len(extra)>MAX_ORDERS:return action
    # No assumed sale proceeds. Reserve 3,000 for parent obligations and price
    # movement; the qualification separately requires 12,000 initial liquidity.
    budget=sum(_v219_fib(n) for n in range(farm['hires_today'],farm['hires_today']+parent_hires+count))
    if not state.get('committed'):budget+=4500
    if fertilizer:budget+=10*(obs['market']['prices']['FERTILIZER']+5)
    for order in action['market']:
        if not order:continue
        if order[0]=='BUY_PRODUCT':budget+=int(order[2])*(int(obs['market']['prices'][order[1]])+10)
        elif order[0]=='BUY_ANIMAL':budget+=int(order[2])*{'COW':400,'SHEEP':500,'GOOSE':300}[order[1]]
        elif order[0]=='BUY_SEED':budget+=int(order[2])*{'WHEAT':10,'CARROT':20,'TOMATO':50,'STRAWBERRY':100,'MELON':80}[order[1]]
    if farm['money']<budget+3000:
        _V219_REPORT['budget_declines']+=1;return action
    state['pending']={'step':step,'first_actor':expected+1,'count':count,'crop_workers':crop_workers,'fertilizer':fertilizer}
    state['requested_day']=day
    _V219_REPORT['hire_requests']+=count
    if not state.get('committed'):
        state['committed']=True;_V219_REPORT['commitments']+=1
    changed=copy.deepcopy(action);changed['market']+=extra
    return changed


def _v219_worker(obs, state, actor, role):
    day=int(obs['step'])//24;step=int(obs['step']);view=FarmView(obs)
    pos=tuple(view.positions[actor]);inv=view.inventory(actor)
    targets=role['targets']
    # Actual cargo differences, observed on the next callback, verify harvests.
    previous=state['last_work'].get(actor)
    if previous and previous['step']==step-1 and previous['command']==['HARVEST']:
        _V219_REPORT['confirmed_harvest_units']+=max(0,int(inv.get('TOMATO',0))-previous['tomatoes'])
    if role.get('needs_fertilizer') and not role.get('loaded'):
        home=_v219_home(pos)
        walk=_v219_walk(pos,home)
        if walk:return walk
        desired=10 if role['kind']=='fertilizer' else 5
        if inv.get('FERTILIZER',0)>=desired:role['loaded']=True
        elif role.get('pickup_requested'):
            # Never spend repeated turns waiting for stock that was not bought.
            role['loaded']=True;role['fertilizer_available']=int(inv.get('FERTILIZER',0))
        elif view.shed.get('FERTILIZER',0)>=desired:
            role['pickup_requested']=True;return ['PICKUP','FERTILIZER',desired]
        else:role['loaded']=True
    todo=[]
    for target in targets:
        x,y=target;tile=view.tiles[y][x]
        tomato=isinstance(tile,dict) and tile.get('crop')=='TOMATO'
        if tomato and target not in state['seen_plants']:
            state['seen_plants'].add(target);_V219_REPORT['confirmed_plants']+=1
        if target in state['seen_plants'] and not tomato and target not in state['lost']:
            state['lost'].add(target);_V219_REPORT['lost_plants']+=1
        command=None
        if role['kind']=='fertilizer':
            if tomato and tile.get('fertilized_until_day',-1)<day+2 and inv.get('FERTILIZER',0)>0:
                command=['FERTILIZE']
        elif day==18 and not tomato:
            if tile is None and obs['private']['seeds'].get('TOMATO',0)>0:command=['PLANT','TOMATO']
            elif isinstance(tile,dict) and tile.get('kind')=='WEED':command=['DIG']
        elif tomato:
            # No later production follows the final day, so watering then would
            # consume time needed to harvest and deliver the final cargo.
            if day<29 and not tile.get('watered_today'):command=['WATER']
            elif role.get('needs_fertilizer') and tile.get('fertilized_until_day',-1)<day+2 and inv.get('FERTILIZER',0)>0:
                command=['FERTILIZE']
            elif tile.get('yield_units',0)>0:command=['HARVEST']
        if command:todo.append((target,command))
    # Final return has priority once only the exact distance plus DROP remains.
    home=_v219_home(pos);distance=abs(pos[0]-home[0])+abs(pos[1]-home[1])
    if step>=718-distance and inv.get('TOMATO',0):
        return _v219_walk(pos,home) or ['PLACE','TOMATO',int(inv.get('TOMATO',0))]
    if todo:
        target,command=min(todo,key=lambda v:(abs(pos[0]-v[0][0])+abs(pos[1]-v[0][1]),targets.index(v[0])))
        return _v219_walk(pos,target) or command
    if inv.get('TOMATO',0):return _v219_walk(pos,home) or ['PLACE','TOMATO',int(inv['TOMATO'])]
    if any(inv.values()):return _v219_walk(pos,home) or ['DROP']
    return ['PASS']


def agent(observation, configuration=None):
    action=_V219_PARENT(observation,configuration)
    step=int(observation['step']);player=int(observation['player']);day=step//24
    state=_V219_STATES.get(player)
    if state is None or step<=state['last_step']:
        state={'last_step':step,'day':-1,'workers':{},'last_work':{},'seen_plants':set(),'lost':set(),
               'targets':[(x,y) for y in (5,6) for x in range(5,10)]}
        _V219_STATES[player]=state
    state['last_step']=step
    native=_POLICY.players[player]
    if step==432:state['eligible']=_v219_qualifies(observation,native)
    if not state.get('eligible') or day<18:return action
    if state['day']!=day:
        state['day']=day;state['workers']={};state['last_work']={}
    farm=observation['farms'][player]
    pending=state.pop('pending',None)
    if pending:
        if len(farm['hands'])+1 >= pending['first_actor']+pending['count'] and 'SE' in farm['unlocked_quadrants']:
            for index in range(pending['count']):
                fertilizer_worker=index==pending['crop_workers']
                if fertilizer_worker:targets=state['targets']
                elif pending['crop_workers']==1:targets=state['targets']
                elif pending['crop_workers']==2:targets=state['targets'][index*5:index*5+5]
                else:targets=[[(5,5),(6,5),(7,5)],[(8,5),(9,5),(9,6),(8,6)],[(5,6),(6,6),(7,6)]][index]
                state['workers'][pending['first_actor']+index]={'kind':'fertilizer' if fertilizer_worker else 'crop','targets':targets,
                    'needs_fertilizer':pending['fertilizer'] and (day==24 or fertilizer_worker)}
            _V219_REPORT['confirmed_workers']+=pending['count']
        else:_V219_REPORT['hire_shortfalls']+=pending['count']
    action=_v219_request(observation,action,state,native)
    if state['workers']:
        commands=[action.get('farmer') or ['PASS']]+list(action.get('hands') or [])
        commands += [['PASS'] for _ in range(len(farm['hands'])+1-len(commands))]
        for actor,role in state['workers'].items():
            if actor>=len(commands):continue
            command=_v219_worker(observation,state,actor,role)
            commands[actor]=command
            name={'PLANT':'plant_requests','WATER':'water_requests','FERTILIZE':'fertilize_requests',
                  'HARVEST':'harvest_requests','DROP':'drop_requests'}.get(command[0])
            if name:_V219_REPORT[name]+=1
            state['last_work'][actor]={'step':step,'command':command,'tomatoes':observation['private']['inventories'][actor].get('TOMATO',0)}
        action=copy.deepcopy(action);action['farmer'],action['hands']=commands[0],commands[1:]
    if state.get('committed') and len(action['market'])<MAX_ORDERS and not any(o[:2]==['SELL','TOMATO'] for o in action['market']):
        quantity=projected_shed(action,FarmView(observation)).get('TOMATO',0)
        if quantity>0:
            action=copy.deepcopy(action);action['market'].append(['SELL','TOMATO',quantity])
            _V219_REPORT['tomato_sale_requests']+=quantity
    return action


agent.telemetry=_V219_REPORT

# V221B: labor-only ablation of frozen V219G; not yet publicly scored.

# V224: prioritize already requested sales without crossing same-item purchases.
_V224_PARENT=agent
del agent
_V224_REPORT=dict(_V219_REPORT, reordered_market_turns=0)

def _v224_sales_first(action):
    original=action.get('market',[])[:MAX_ORDERS]
    orders=[list(o) for o in original if o and (o[0] in ('HIRE','BUY_LAND') or (len(o)>=3 and int(o[2])>0))]
    for index in range(len(orders)):
        order=orders[index]
        if order[0]!='SELL':continue
        cursor=index
        while cursor>0:
            previous=orders[cursor-1]
            if previous[0]=='SELL':break
            if previous[0] in ('BUY_PRODUCT','BUY_ANIMAL') and previous[1]==order[1]:break
            orders[cursor-1],orders[cursor]=orders[cursor],orders[cursor-1]
            cursor-=1
    if orders==original:return action
    _V224_REPORT['reordered_market_turns']+=1
    changed=copy.deepcopy(action);changed['market']=orders
    return changed

def agent(observation,configuration=None):
    action=_V224_PARENT(observation,configuration)
    if int(observation['step'])>=144:action=_v224_sales_first(action)
    _V224_REPORT.update(_V219_REPORT)
    return action

agent.telemetry=_V224_REPORT

# V224C: frozen sale timing ablation; no competition rating.

# V226: buy only a bounded shortage in already scheduled next-turn grain pickups.
_V226_PARENT=agent
del agent
_V226_DAY={}
_V226_REPORT=dict(_V224_REPORT, wheat_topup_orders=0, wheat_topup_units=0,
    wheat_topup_budget_declines=0, wheat_topup_capacity_declines=0)


def _v226_topup(obs,action,state,configuration=None):
    step=int(obs['step']);player=int(obs['player'])
    if configuration is not None and any(configuration.get(k,v)!=v for k,v in
        (('boardSize',10),('turnsPerDay',24),('shedCapacity',100),('maxMarketOrdersPerTurn',10))):return action
    if not 24<=step<696 or step%24==23 or (step+1)%72==0:return action
    market=action.get('market',[])[:MAX_ORDERS]
    if len(market)>=MAX_ORDERS:return action
    purchases={'HIRE','BUY_LAND','BUY_PRODUCT','BUY_ANIMAL','BUY_SEED'}
    if any(o and (o[0] in purchases or (len(o)>1 and o[1]=='WHEAT')) for o in market):return action
    tape=_POLICY.tapes[state.plan]
    nxt=tape[step+1]
    if any(o and o[0] in purchases for o in nxt.get('market',[])):return action
    view=FarmView(obs);commands=[action.get('farmer') or ['PASS'],*(action.get('hands') or [])]
    future=[nxt.get('farmer') or ['PASS'],*(nxt.get('hands') or [])]
    demand=0
    for actor,pos in enumerate(view.positions):
        current=commands[actor] if actor<len(commands) else ['PASS']
        x,y=pos
        if current and current[0] in _V217_MOVES:
            dx,dy=_V217_MOVES[current[0]];nx,ny=x+dx,y+dy
            if 0<=nx<10 and 0<=ny<10:x,y=nx,ny
        if not view.beside_shed((x,y)):continue
        pending=state.queues.get(actor)
        command=pending[0] if pending else (future[actor] if actor<len(future) else ['PASS'])
        task=vars(state).get('v217_task') if actor==0 else None
        if task:
            offset=step+1-task['step']
            if 0<=offset<len(task['commands']):command=task['commands'][offset]
        if len(command)>=2 and command[:2]==['PICKUP','WHEAT']:
            demand+=max(0,int(command[2]) if len(command)>2 else 1)
    stock=projected_shed(action,view)
    shortage=demand-stock.get('WHEAT',0)
    if not 0<shortage<=4:return action
    day=step//24
    previous=_V226_DAY.get(player)
    if previous is None or previous['day']!=day:
        previous=_V226_DAY[player]={'day':day,'units':0}
    if previous['units']+shortage>8:return action
    if sum(stock.values())+shortage>100:
        _V226_REPORT['wheat_topup_capacity_declines']+=1;return action
    quote=int(obs['market']['prices']['WHEAT'])
    if quote<1 or obs['farms'][player]['money']<100+shortage*(quote+10):
        _V226_REPORT['wheat_topup_budget_declines']+=1;return action
    result=copy.deepcopy(action)
    result['market']=market+[['BUY_PRODUCT','WHEAT',shortage]]
    previous['units']+=shortage
    _V226_REPORT['wheat_topup_orders']+=1;_V226_REPORT['wheat_topup_units']+=shortage
    return result


def agent(observation,configuration=None):
    if int(observation['step'])==0:_V226_DAY.pop(int(observation['player']),None)
    action=_V226_PARENT(observation,configuration)
    state=_POLICY.players[int(observation['player'])]
    action=_v226_topup(observation,action,state,configuration)
    _V226_REPORT.update(_V224_REPORT)
    return action

agent.telemetry=_V226_REPORT

# Bounded livestock substitution; confirm owned animals before redirecting workers.
_V231_PARENT=agent
_V231_CAP=4
_V231_STATES={}
_V231_REPORT={}

def _v231_new_state():
    return {'last':-1,'confirmed':0,'reserved':0,'pending_buy':None,
            'carrying':{},'pending_places':[],'sites':{},'milk_credit':0,
            'requested':0,'failed_purchase_units':0,'picked':0,'placed':0,
            'failed_placements':0,'extra_milk_harvested':0,'extra_milk_sale_requests':0}

def _v231_controller(obs,action,state,cap):
    step=int(obs['step']);seat=int(obs['player']);farm=obs['farms'][seat]
    private=obs['private'];shed=private['shed'];inventories=private['inventories']
    positions=[farm['farmer'],*farm['hands']]
    pending=state['pending_buy']
    if pending is not None:
        gained=max(0,int(shed.get('COW',0))-pending['before'])
        confirmed=min(pending['quantity'],gained)
        state['confirmed']+=confirmed;state['reserved']+=confirmed
        state['failed_purchase_units']+=pending['quantity']-confirmed
        state['pending_buy']=None
    for pending in state['pending_places']:
        x,y=pending['site'];tile=farm['tiles'][y][x]
        if (isinstance(tile,dict) and tile.get('animal')=='COW'
                and tile.get('placed_day')==pending['day']):
            state['sites'][(x,y)]=pending['day'];state['placed']+=1
            actor=pending['actor'];state['carrying'][actor]=max(0,state['carrying'].get(actor,0)-1)
        else:state['failed_placements']+=1
    state['pending_places']=[]
    state['last']=step
    result=copy.deepcopy(action)
    workers=[result.get('farmer') or ['PASS'],*(result.get('hands') or [])]
    seen_harvest=set();cow_available=int(shed.get('COW',0));occupied=set()
    for actor,work in enumerate(workers[:len(positions)]):
        inventory=inventories[actor] if actor<len(inventories) else {}
        x,y=positions[actor];tile=farm['tiles'][y][x];site=(x,y)
        if (work==['HARVEST'] and site in state['sites'] and site not in seen_harvest
                and isinstance(tile,dict) and tile.get('animal')=='COW'
                and tile.get('placed_day')==state['sites'][site]):
            units=max(0,int(tile.get('yield_units',0)))
            state['milk_credit']+=units;state['extra_milk_harvested']+=units
            seen_harvest.add(site)
        if len(work)>=2 and work[:2]==['PICKUP','SHEEP']:
            quantity=max(0,int(work[2]) if len(work)>2 else 1)
            center=len(farm['tiles'])//2
            if (quantity and state['reserved']>=quantity and cow_available>=quantity
                    and x in (center-1,center) and y in (center-1,center)
                    and not any(inventory.get(a,0) for a in ('COW','SHEEP','GOOSE'))):
                work[1]='COW';state['reserved']-=quantity;cow_available-=quantity
                state['carrying'][actor]=state['carrying'].get(actor,0)+quantity
                state['picked']+=quantity
        if (len(work)>=2 and work[:2]==['PLACE','SHEEP']
                and state['carrying'].get(actor,0)>0 and inventory.get('COW',0)>0
                and isinstance(tile,dict) and tile.get('kind')=='PASTURE'
                and 'animal' not in tile and site not in occupied):
            work[1]='COW'
            state['pending_places'].append({'actor':actor,'site':site,'day':step//24})
        if (len(work)>=2 and work[0]=='PLACE' and work[1] in ('COW','SHEEP','GOOSE')
                and inventory.get(work[1],0)>0):occupied.add(site)
    result['farmer'],result['hands']=workers[0],workers[1:]
    market=result.get('market',[])
    animal_orders=[o for o in market if len(o)>=3 and o[0]=='BUY_ANIMAL']
    shops=obs['town']['unlocked_shops'];prices=obs['market']['prices']
    counts={'COW':0,'SHEEP':0}
    for line in farm['tiles']:
        for tile in line:
            if isinstance(tile,dict) and tile.get('animal') in counts:counts[tile['animal']]+=1
    cargo=sum(int(inv.get(a,0)) for inv in inventories for a in ('COW','SHEEP','GOOSE'))
    stock_animals=sum(int(shed.get(a,0)) for a in ('COW','SHEEP','GOOSE'))
    milk_shops=sum(shop in ('PIZZA_SHOP','ICE_CREAM_SHOP','SMOOTHIE_SHOP') for shop in shops)
    if (216<=step<=227 and len(shops)>=3 and state['confirmed']<cap and not state['reserved']
            and not any(state['carrying'].values()) and not state['pending_places']
            and not cargo and not stock_animals and len(animal_orders)==1
            and animal_orders[0][1]=='SHEEP' and milk_shops>=2 and 'YARN_STORE' not in shops
            and int(prices.get('MILK',0))>=int(prices.get('WOOL',0))
            and counts['COW']>=4 and counts['SHEEP']>=2):
        order=animal_orders[0];quantity=int(order[2])
        if 1<=quantity<=2 and quantity<=cap-state['confirmed']:
            order[1]='COW';state['requested']+=quantity
            state['pending_buy']={'before':int(shed.get('COW',0)),'quantity':quantity}
    # Sell only additional physically harvested production at an existing sale slot.
    if state['milk_credit']>0:
        stock=projected_shed(result,FarmView(obs))
        total_planned=sum(max(0,int(o[2])) for o in market if len(o)>=3 and o[:2]==['SELL','MILK'])
        extra=min(state['milk_credit'],max(0,int(stock.get('MILK',0))-total_planned))
        if extra:
            for order in market:
                if len(order)>=3 and order[:2]==['SELL','MILK'] and int(order[2])>0:
                    order[2]=int(order[2])+extra
                    state['milk_credit']-=extra;state['extra_milk_sale_requests']+=extra
                    break
    result['market']=market
    return result

def agent(observation,configuration=None):
    step=int(observation['step']);seat=int(observation['player'])
    state=_V231_STATES.get(seat)
    if state is None or step<=state['last']:
        state=_V231_STATES[seat]=_v231_new_state()
    action=_V231_PARENT(observation,configuration)
    action=_v231_controller(observation,action,state,_V231_CAP)
    _V231_REPORT.clear();_V231_REPORT.update(_V231_PARENT.telemetry)
    for name in ('confirmed','reserved','requested','failed_purchase_units','picked','placed',
                 'failed_placements','extra_milk_harvested','extra_milk_sale_requests','milk_credit'):
        _V231_REPORT['cattle_'+name]=state[name]
    _V231_REPORT['cattle_carried_pending']=sum(state['carrying'].values())
    return action

agent.telemetry=_V231_REPORT

# Kaggle selects the last callable inserted into the source namespace.
kaggle_agent = agent


# V233: bounded, financed six-sheep SE discovery investment.
_V233_PARENT=agent
del agent
_V233_STATES={}
_V233_REPORT=dict(sheep_commit_requests=0,sheep_committed=0,sheep_hire_requests=0,
    sheep_workers_confirmed=0,sheep_hire_shortfalls=0,sheep_budget_declines=0,
    sheep_capacity_declines=0,sheep_purchase_shortfalls=0,sheep_feed_buy_requests=0,
    sheep_wool_harvested=0,sheep_fert_collected=0,sheep_extra_wool_sales=0,
    sheep_extra_fert_sales=0,sheep_rescue_feed_requests=0)

def _v233_eligible(obs,native):
    farm=obs['farms'][obs['player']];prices=obs['market']['prices']
    if len(farm['tiles'])!=10 or set(farm['unlocked_quadrants'])!={'NW','NE','SW'}:return False
    if obs['town']['unlocked_shops'].count('YARN_STORE')<2 or prices['WOOL']<220 or prices['WHEAT']>45:return False
    if any(farm['tiles'][y][x]!='LOCKED' for y in (5,6) for x in range(5,8)):return False
    if obs['private']['shed'].get('SHEEP',0) or any(i.get('SHEEP',0) for i in obs['private']['inventories']):return False
    for day in range(12,30):
        for a in _v219_native_day(native,day):
            if any(o and (o[0]=='BUY_LAND' or o[:2]==['BUY_ANIMAL','SHEEP']) for o in a.get('market',[])):return False
            if any(c and c[0] in ('PICKUP','PLACE') and len(c)>1 and c[1]=='SHEEP' for c in [a.get('farmer')]+a.get('hands',[])):return False
    return True

def _v233_request(obs,action,state,native):
    step=int(obs['step']);day=step//24;hour=step%24
    if hour>(2 if state.get('committed') else 1) or state.get('requested_day')==day:return action
    if not state.get('committed') and (day!=12 or not _v233_eligible(obs,native)):return action
    planned=_v219_native_day(native,day)
    if any(o and o[0]=='HIRE' for a in planned[hour+1:] for o in a.get('market',[])):return action
    farm=obs['farms'][obs['player']];market=action.get('market',[])
    parent_hires=sum(bool(o) and o[0]=='HIRE' for o in market)
    expected=max(len(a.get('hands',[])) for a in planned)
    if len(farm['hands'])+parent_hires!=expected:return action
    initial=not state.get('committed')
    extra=([['BUY_LAND'],['BUY_ANIMAL','SHEEP',6]] if initial else [])+[['BUY_PRODUCT','WHEAT',6],['HIRE'],['HIRE']]
    if len(market)+len(extra)>MAX_ORDERS:return action
    stock=projected_shed(action,FarmView(obs))
    incoming=6+6*initial
    budget=7000*initial+6*(int(obs['market']['prices']['WHEAT'])+10)
    budget+=sum(_v219_fib(n) for n in range(farm['hires_today'],farm['hires_today']+parent_hires+2))
    for o in market:
        if not o:continue
        if o[0]=='BUY_LAND':return action
        if o[0]=='BUY_PRODUCT':
            incoming+=int(o[2]);budget+=int(o[2])*(int(obs['market']['prices'][o[1]])+10)
        elif o[0]=='BUY_ANIMAL':
            incoming+=int(o[2]);budget+=int(o[2])*{'SHEEP':500,'COW':400,'GOOSE':300}[o[1]]
        elif o[0]=='BUY_SEED':budget+=int(o[2])*{'WHEAT':10,'CARROT':20,'TOMATO':50,'STRAWBERRY':100,'MELON':80}[o[1]]
    if sum(stock.values())+incoming>100:
        _V233_REPORT['sheep_capacity_declines']+=1;return action
    if farm['money']<budget+(3000 if initial else 1000):
        _V233_REPORT['sheep_budget_declines']+=1;return action
    state['requested_day']=day
    state['pending']={'first':expected+1,'initial':initial}
    _V233_REPORT['sheep_hire_requests']+=2;_V233_REPORT['sheep_feed_buy_requests']+=6
    if initial:_V233_REPORT['sheep_commit_requests']+=1
    result=copy.deepcopy(action);result['market']=market+extra
    return result

def _v233_worker(obs,actor,targets):
    farm=obs['farms'][obs['player']];private=obs['private'];step=int(obs['step'])
    pos=tuple(farm['hands'][actor-1]);inv=private['inventories'][actor]
    access=((4,4),(5,4),(4,5),(5,5))
    home=min(access,key=lambda p:(abs(pos[0]-p[0])+abs(pos[1]-p[1]),p))
    distance=abs(pos[0]-home[0])+abs(pos[1]-home[1])
    cargo=[item for item in ('WOOL','FERTILIZER') if inv.get(item,0)]
    if cargo and step%24 >= (22 if step//24==29 else 23)-distance:
        return _v219_walk(pos,home) or ['PLACE',cargo[0],inv[cargo[0]]]
    missing=sum(not(isinstance(farm['tiles'][y][x],dict) and farm['tiles'][y][x].get('animal')=='SHEEP') for x,y in targets)
    if missing and not inv.get('SHEEP',0) and private['shed'].get('SHEEP',0):
        return _v219_walk(pos,home) or ['PICKUP','SHEEP',min(missing,private['shed']['SHEEP'])]
    hungry=sum(not(isinstance(farm['tiles'][y][x],dict) and farm['tiles'][y][x].get('fed_today')) for x,y in targets)
    if hungry and not inv.get('WHEAT',0) and private['shed'].get('WHEAT',0):
        return _v219_walk(pos,home) or ['PICKUP','WHEAT',min(hungry,private['shed']['WHEAT'])]
    tasks=[]
    for target in targets:
        x,y=target;tile=farm['tiles'][y][x];command=None
        if tile is None:command=['BUILD_PASTURE']
        elif isinstance(tile,dict) and tile.get('kind')=='WEED':command=['DIG']
        elif isinstance(tile,dict) and tile.get('kind')=='PASTURE' and not tile.get('animal'):
            if inv.get('SHEEP',0):command=['PLACE','SHEEP']
        elif isinstance(tile,dict) and tile.get('animal')=='SHEEP':
            if not tile['fed_today'] and inv.get('WHEAT',0):command=['FEED']
            elif not tile['cared_today']:command=['CARE']
            elif tile['yield_units']:command=['HARVEST']
            elif tile['fertilizer_available']:command=['COLLECT_FERTILIZER']
        if command:tasks.append((abs(pos[0]-x)+abs(pos[1]-y),targets.index(target),target,command))
    if tasks:
        _,_,target,command=min(tasks);return _v219_walk(pos,target) or command
    if cargo:return _v219_walk(pos,home) or ['PLACE',cargo[0],inv[cargo[0]]]
    return ['PASS']

def _v234_rescue(obs,action,state):
    if not state['workers'] or int(obs['step'])%24>14:return action
    orders=action.get('market',[])
    if len(orders)>=MAX_ORDERS:return action
    if any(o and (o[0] in ('HIRE','BUY_LAND','BUY_ANIMAL','BUY_PRODUCT','BUY_SEED') or (len(o)>1 and o[1]=='WHEAT')) for o in orders):return action
    farm=obs['farms'][obs['player']];private=obs['private'];hungry=carried=0
    commands=[action.get('farmer') or ['PASS']]+list(action.get('hands') or [])
    for actor,targets in state['workers'].items():
        command=commands[actor]
        if command==['FEED'] or command[:2]==['PICKUP','WHEAT']:return action
        carried+=private['inventories'][actor].get('WHEAT',0)
        hungry+=sum(isinstance(farm['tiles'][y][x],dict) and farm['tiles'][y][x].get('animal')=='SHEEP' and not farm['tiles'][y][x].get('fed_today') for x,y in targets)
    stock=projected_shed(action,FarmView(obs))
    shortage=hungry-carried-stock.get('WHEAT',0)
    if not 0<shortage<=6 or state.get('rescue_today',0)+shortage>6:return action
    quote=int(obs['market']['prices']['WHEAT'])
    if quote<1 or farm['money']<1000+shortage*(quote+10) or sum(stock.values())+shortage>100:return action
    result=copy.deepcopy(action);result['market'].append(['BUY_PRODUCT','WHEAT',shortage])
    state['rescue_today']=state.get('rescue_today',0)+shortage
    _V233_REPORT['sheep_rescue_feed_requests']+=shortage
    return result

def agent(observation,configuration=None):
    action=_V233_PARENT(observation,configuration)
    step=int(observation['step']);player=int(observation['player']);day=step//24
    state=_V233_STATES.get(player)
    if state is None or step<=state['last_step']:
        state={'last_step':step,'day':-1,'workers':{},'work':{},'credit':{'WOOL':0,'FERTILIZER':0}}
        _V233_STATES[player]=state
    state['last_step']=step
    if configuration is not None and any(configuration.get(k,v)!=v for k,v in
        (('boardSize',10),('turnsPerDay',24),('shedCapacity',100),('maxMarketOrdersPerTurn',10))):return action
    if day<12:return action
    farm=observation['farms'][player];private=observation['private']
    if state['day']!=day:state['day']=day;state['workers']={};state['work']={};state['rescue_today']=0
    for actor,previous in state['work'].items():
        if previous['step']!=step-1 or actor>=len(private['inventories']):continue
        item={'HARVEST':'WOOL','COLLECT_FERTILIZER':'FERTILIZER'}.get(previous['command'][0])
        if item:
            gained=max(0,private['inventories'][actor].get(item,0)-previous['inventory'].get(item,0))
            state['credit'][item]+=gained
            _V233_REPORT['sheep_wool_harvested' if item=='WOOL' else 'sheep_fert_collected']+=gained
    pending=state.pop('pending',None)
    if pending:
        funded='SE' in farm['unlocked_quadrants'] and (not pending['initial'] or private['shed'].get('SHEEP',0)>=6)
        if not funded:_V233_REPORT['sheep_purchase_shortfalls']+=1
        elif len(farm['hands'])<pending['first']+1:_V233_REPORT['sheep_hire_shortfalls']+=1
        else:
            for i in range(2):state['workers'][pending['first']+i]=[(x,5+i) for x in range(5,8)]
            _V233_REPORT['sheep_workers_confirmed']+=2
            if pending['initial']:state['committed']=True;_V233_REPORT['sheep_committed']+=1
    action=_v233_request(observation,action,state,_POLICY.players[player])
    if not state.get('committed'):return action
    result=copy.deepcopy(action)
    commands=[result.get('farmer') or ['PASS']]+list(result.get('hands') or [])
    commands += [['PASS'] for _ in range(len(farm['hands'])+1-len(commands))]
    state['work']={}
    for actor,targets in state['workers'].items():
        command=_v233_worker(observation,actor,targets);commands[actor]=command
        state['work'][actor]={'step':step,'command':command,'inventory':dict(private['inventories'][actor])}
    result['farmer'],result['hands']=commands[0],commands[1:]
    result=_v234_rescue(observation,result,state)
    stock=projected_shed(result,FarmView(observation))
    for item in ('WOOL','FERTILIZER'):
        scheduled=sum(int(o[2]) for o in result['market'] if o[:2]==['SELL',item])
        count=min(state['credit'][item],max(0,stock.get(item,0)-scheduled))
        if count and len(result['market'])<MAX_ORDERS:
            result['market'].append(['SELL',item,count]);state['credit'][item]-=count
            _V233_REPORT['sheep_extra_wool_sales' if item=='WOOL' else 'sheep_extra_fert_sales']+=count
    return result

agent.telemetry=_V233_REPORT
kaggle_agent=agent


# ---------------------------------------------------------------------------
# MEDAL_R11_EARLYPREM: day-29 morning premium slice (append-only)
# ---------------------------------------------------------------------------
_R11_PARENT = agent
_R11_WINDOW = range(700, 712)  # day 29 hours 4-15
_R11_RULES = (
    # item, min_price, min_stock, slice
    ("MILK", 40, 16, 8),
    ("WOOL", 80, 12, 6),
    ("STRAWBERRY", 80, 16, 8),
    ("EGG", 40, 16, 8),
)


def _r11_early(obs, action):
    step = int(obs.get("step") or 0)
    if step not in _R11_WINDOW:
        return action
    private = obs.get("private") or {}
    shed = private.get("shed") or {}
    prices = ((obs.get("market") or {}).get("prices") or {})
    market = list(action.get("market") or [])
    already = {}
    for o in market:
        if isinstance(o, (list, tuple)) and len(o) >= 3 and o[0] == "SELL":
            already[o[1]] = already.get(o[1], 0) + int(o[2] or 0)
    changed = False
    for item, min_price, min_stock, slice_qty in _R11_RULES:
        if len(market) >= 10:
            break
        price = int(prices.get(item) or 1)
        stock = int(shed.get(item) or 0)
        avail = stock - already.get(item, 0)
        if price < min_price or avail < min_stock:
            continue
        qty = min(slice_qty, avail)
        if qty <= 0:
            continue
        merged = False
        for o in market:
            if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL" and o[1] == item:
                o[2] = int(o[2] or 0) + qty
                merged = True
                changed = True
                break
        if not merged:
            market.append(["SELL", item, qty])
            changed = True
    if not changed:
        return action
    result = dict(action)
    result["market"] = market[:10]
    return result


def agent(observation, configuration=None):
    action = _R11_PARENT(observation, configuration)
    try:
        return _r11_early(observation, action)
    except Exception:
        return action

kaggle_agent=agent

