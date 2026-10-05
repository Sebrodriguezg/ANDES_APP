"""Lista de temas y hoja de referencia para el examen de la UNAL (16-oct-2026).

Las dos salen de los mismos datos, así que la numeración siempre coincide:
el ítem 12 de la lista es el 12 de la referencia.

    python3 04_ESTUDIO/formularios/unal/generar.py

Método: con la LISTA, escribir de memoria en una hoja en blanco; después abrir
la REFERENCIA y corregir en rojo. Lo que se estudia es lo rojo.
"""

import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent

# (área, preguntas en el examen, [(bloque, [(tema, contenido de referencia)])])
CUANTICA_MODERNA = [
    ("Mecánica cuántica", "3 preguntas", [
        ("Formalismo", [
            ("Ecuación de Schrödinger (con y sin tiempo)",
             r"$i\hbar\,\partial_t\Psi = \hat H\Psi$, \ $\hat H = -\frac{\hbar^2}{2m}\nabla^2 + V$. "
             r"Separando $\Psi=\psi(x)e^{-iEt/\hbar}$: $\hat H\psi = E\psi$."),
            ("Normalización, probabilidad y valor esperado",
             r"$\int|\Psi|^2dx=1$; \ $P(a<x<b)=\int_a^b|\Psi|^2$; \ "
             r"$\langle Q\rangle=\int\Psi^*\hat Q\Psi\,dx$; \ $\sigma_Q^2=\langle Q^2\rangle-\langle Q\rangle^2$."),
            ("Operadores básicos y $[x,p]$",
             r"$\hat p=-i\hbar\,\partial_x$; \ $[x,p]=i\hbar$; \ $[AB,C]=A[B,C]+[A,C]B$. "
             r"Hermítico $\Rightarrow$ autovalores reales, autovectores ortogonales, base completa."),
            ("Principio de incertidumbre",
             r"$\sigma_A\sigma_B\ge\tfrac12|\langle[A,B]\rangle|$ $\Rightarrow$ $\sigma_x\sigma_p\ge\hbar/2$. "
             r"Tiempo--energía: $\Delta E\,\Delta t\gtrsim\hbar/2$ (ancho de línea $\Gamma\sim\hbar/\tau$). "
             r"Gaussiana: la igualdad se cumple."),
            ("Evolución temporal y superposiciones",
             r"$\Psi=\sum c_n\psi_n e^{-iE_nt/\hbar}$. Estado estacionario: $|\Psi|^2$ y todo "
             r"$\langle Q\rangle$ constantes. En una mezcla de $n,m$, $\langle x\rangle$ oscila con "
             r"$\omega=(E_n-E_m)/\hbar$."),
            ("Teorema de Ehrenfest",
             r"$\frac{d}{dt}\langle Q\rangle=\frac{i}{\hbar}\langle[\hat H,\hat Q]\rangle+\langle\partial_t Q\rangle$. "
             r"$\frac{d\langle x\rangle}{dt}=\frac{\langle p\rangle}{m}$, \ "
             r"$\frac{d\langle p\rangle}{dt}=\langle-V'\rangle$. Si $[H,Q]=0$, $Q$ se conserva."),
            ("Medición",
             r"Resultado posible: solo autovalores $q_n$. Probabilidad $|c_n|^2=|\langle q_n|\Psi\rangle|^2$. "
             r"Tras medir, colapso a $|q_n\rangle$: repetir enseguida da lo mismo."),
            ("Notación de Dirac",
             r"$\langle\phi|\psi\rangle=\int\phi^*\psi$; \ completitud $\sum_n|n\rangle\langle n|=1$; \ "
             r"$\langle\psi|\phi\rangle=\langle\phi|\psi\rangle^*$; \ $(AB)^\dagger=B^\dagger A^\dagger$."),
        ]),
        ("Sistemas en una dimensión", [
            ("Pozo infinito de ancho $a$",
             r"$E_n=\frac{n^2\pi^2\hbar^2}{2ma^2}$, \ $\psi_n=\sqrt{2/a}\,\sin\frac{n\pi x}{a}$, \ $n=1,2,\dots$ "
             r"$E\propto n^2/(ma^2)$; el estado $n$ tiene $n-1$ nodos. $\langle x\rangle=a/2$."),
            ("Oscilador armónico",
             r"$E_n=\hbar\omega(n+\tfrac12)$, $n=0,1,\dots$ (equiespaciados). "
             r"$\psi_0=(\frac{m\omega}{\pi\hbar})^{1/4}e^{-m\omega x^2/2\hbar}$. "
             r"$a_+|n\rangle=\sqrt{n+1}|n{+}1\rangle$, $a_-|n\rangle=\sqrt n|n{-}1\rangle$, "
             r"$x=\sqrt{\frac{\hbar}{2m\omega}}(a_++a_-)$. $\langle x^2\rangle_n=\frac{\hbar}{m\omega}(n+\tfrac12)$. "
             r"Virial: $\langle T\rangle=\langle V\rangle=E/2$. Medio oscilador ($x>0$): solo $n$ impares."),
            ("Partícula libre y paquetes",
             r"$E=\hbar^2k^2/2m$, no normalizable $\Rightarrow$ paquetes. "
             r"$v_g=d\omega/dk=\hbar k/m=v_{\rm clás}$; \ $v_f=\omega/k=v_{\rm clás}/2$. El paquete se ensancha."),
            ("Escalón, barrera y túnel",
             r"Escalón con $E>V_0$: $R=\left(\frac{k_1-k_2}{k_1+k_2}\right)^2$, $T=1-R$ (refleja aunque $E>V_0$). "
             r"Barrera ancha: $T\approx e^{-2\kappa L}$, \ $\kappa=\sqrt{2m(V_0-E)}/\hbar$. "
             r"Exponencial en $L$ y $\sqrt m$."),
            (r"Pozo delta $V=-\alpha\delta(x)$",
             r"Un solo estado ligado: $E=-\frac{m\alpha^2}{2\hbar^2}$, \ $\psi=\sqrt\kappa\,e^{-\kappa|x|}$, "
             r"$\kappa=m\alpha/\hbar^2$. $\psi'$ salta en $0$."),
            ("Paridad y nodos",
             r"$V$ par $\Rightarrow$ $\psi_n$ alternan par/impar. El fundamental no tiene nodos y es par. "
             r"Integrandos impares en intervalo simétrico dan cero (atajo para $\langle x\rangle$, elementos de matriz)."),
        ]),
        ("Tres dimensiones y momento angular", [
            ("Átomo de hidrógeno",
             r"$E_n=-\frac{13{,}6\ {\rm eV}}{n^2}$, \ $a_0=0{,}529$ \AA. "
             r"$l=0..n-1$, \ $m=-l..l$; degeneración $n^2$ ($2n^2$ con espín). "
             r"$\psi_{100}=\frac{1}{\sqrt{\pi a_0^3}}e^{-r/a_0}$: $r$ más probable $=a_0$, $\langle r\rangle=\frac32a_0$. "
             r"Virial coulombiano: $\langle T\rangle=-E$, $\langle V\rangle=2E$."),
            ("Momento angular orbital",
             r"$L^2|lm\rangle=\hbar^2l(l+1)|lm\rangle$, \ $L_z|lm\rangle=m\hbar|lm\rangle$. "
             r"$[L_x,L_y]=i\hbar L_z$ (cíclico); $[L^2,L_i]=0$. "
             r"$L_\pm|lm\rangle=\hbar\sqrt{l(l+1)-m(m\pm1)}\,|l,m{\pm}1\rangle$."),
            ("Espín $\\tfrac12$",
             r"$\vec S=\frac\hbar2\vec\sigma$; \ "
             r"$\sigma_x=\begin{psmallmatrix}0&1\\1&0\end{psmallmatrix}$, "
             r"$\sigma_y=\begin{psmallmatrix}0&-i\\i&0\end{psmallmatrix}$, "
             r"$\sigma_z=\begin{psmallmatrix}1&0\\0&-1\end{psmallmatrix}$. "
             r"$S^2=\frac34\hbar^2$. $|{\uparrow_z}\rangle$ medido en $x$: $\pm\hbar/2$ con prob.\ $\frac12$ cada uno. "
             r"$|{\pm_x}\rangle=\frac{1}{\sqrt2}(|{\uparrow}\rangle\pm|{\downarrow}\rangle)$."),
            ("Suma de momentos angulares",
             r"$j=|j_1-j_2|,\dots,j_1+j_2$; total de estados $(2j_1+1)(2j_2+1)$. "
             r"Dos espines $\frac12$: triplete $s=1$ (simétrico, 3 estados) y singlete "
             r"$s=0$: $\frac{1}{\sqrt2}(|{\uparrow\downarrow}\rangle-|{\downarrow\uparrow}\rangle)$ (antisimétrico)."),
            ("Partículas idénticas",
             r"$\psi(1,2)=\pm\psi(2,1)$: bosones $+$, fermiones $-$ (Pauli). "
             r"$\psi_\pm=\frac{1}{\sqrt2}[\psi_a(1)\psi_b(2)\pm\psi_a(2)\psi_b(1)]$. "
             r"Para fermiones, la función total (espacial $\times$ espín) es antisimétrica: "
             r"singlete $\leftrightarrow$ espacial simétrica."),
        ]),
        ("Aproximaciones y transiciones", [
            ("Perturbaciones, primer y segundo orden",
             r"$E_n^{(1)}=\langle n|H'|n\rangle$. "
             r"$E_n^{(2)}=\sum_{m\ne n}\frac{|\langle m|H'|n\rangle|^2}{E_n-E_m}$: el fundamental siempre baja. "
             r"Truco: si $H'$ es impar y $\psi_n$ tiene paridad definida, $E^{(1)}=0$."),
            ("Perturbación degenerada",
             r"Diagonalizar $H'$ dentro del subespacio degenerado; los autovalores son las correcciones "
             r"y los autovectores, los estados ``buenos''."),
            ("Método variacional",
             r"$E_0\le\frac{\langle\psi|H|\psi\rangle}{\langle\psi|\psi\rangle}$ para cualquier $\psi$ de prueba: "
             r"da una cota superior; se minimiza sobre el parámetro."),
            ("Transiciones y reglas de selección",
             r"Regla de oro: $\Gamma=\frac{2\pi}{\hbar}|\langle f|H'|i\rangle|^2\rho(E_f)$. "
             r"Dipolo eléctrico: $\Delta l=\pm1$, \ $\Delta m=0,\pm1$, \ $\Delta s=0$. "
             r"$2s\to1s$ prohibida (metaestable)."),
            ("Escalamientos rápidos (atajos)",
             r"Pozo: $E\propto\frac{n^2}{mL^2}$. Oscilador: $E\propto\omega$, espaciado $\hbar\omega$. "
             r"Hidrógeno: $E\propto\mu Z^2/n^2$, $r\propto n^2/(\mu Z)$. Duplicar $m$ en el pozo $\Rightarrow$ $E/2$."),
        ]),
    ]),
    ("Física moderna", "4 preguntas", [
        ("Orígenes cuánticos", [
            ("Cuerpo negro",
             r"Wien: $\lambda_{\max}T=2{,}898\times10^{-3}$ m$\cdot$K. "
             r"Stefan--Boltzmann: $P=\sigma AT^4$, $\sigma=5{,}67\times10^{-8}$ W/m$^2$K$^4$. "
             r"Planck: $u(\nu)=\frac{8\pi h\nu^3/c^3}{e^{h\nu/kT}-1}$; Rayleigh--Jeans falla en el UV."),
            ("Efecto fotoeléctrico",
             r"$K_{\max}=hf-\phi=eV_0$. Umbral $f_0=\phi/h$. La intensidad cambia el \emph{número} de "
             r"electrones (corriente), no $K_{\max}$. Gráfica $V_0$ vs $f$: pendiente $h/e$."),
            ("Efecto Compton",
             r"$\lambda'-\lambda=\frac{h}{m_ec}(1-\cos\theta)$, \ $\frac{h}{m_ec}=2{,}43$ pm. "
             r"Máximo en $\theta=180^\circ$: $2\lambda_C$. Notable solo con rayos X o $\gamma$."),
            ("Longitud de onda de de Broglie",
             r"$\lambda=h/p$. Electrón acelerado por $V$: $\lambda=\frac{h}{\sqrt{2m_eeV}}\approx\frac{1{,}23}{\sqrt V}$ nm. "
             r"Térmica: $p\sim\sqrt{3mkT}$. Relativista si $eV\gtrsim0{,}5$ MeV: usar $pc=\sqrt{K^2+2Kmc^2}$."),
            ("Modelo de Bohr",
             r"$L=n\hbar$; \ $r_n=\frac{n^2a_0}{Z}$, \ $v_n=\frac{Z\alpha c}{n}$, \ $E_n=-\frac{13{,}6\,Z^2}{n^2}$ eV. "
             r"$\frac1\lambda=RZ^2\left(\frac1{n_f^2}-\frac1{n_i^2}\right)$, $R=1{,}097\times10^7$ m$^{-1}$. "
             r"Lyman ($n_f=1$, UV, L$\alpha$ = 122 nm), Balmer ($n_f=2$, visible, H$\alpha$ = 656 nm), Paschen ($n_f=3$, IR)."),
            ("Masa reducida",
             r"$\mu=\frac{mM}{m+M}$: $E\propto\mu$, $r\propto1/\mu$. "
             r"Positronio: $\mu=m_e/2$ $\Rightarrow$ $E_1=-6{,}8$ eV, radio doble. "
             r"Hidrógeno muónico: $\mu\approx186\,m_e$, energías $\times186$."),
            ("Rayos X",
             r"Bragg: $2d\sin\theta=n\lambda$. Moseley: $E_{K\alpha}\approx10{,}2\,(Z-1)^2$ eV. "
             r"Corte del bremsstrahlung: $\lambda_{\min}=hc/eV$."),
            ("Experimentos clave",
             r"Davisson--Germer: ondas de electrones. Stern--Gerlach: momento angular cuantizado (Ag, 2 haces = espín). "
             r"Franck--Hertz: niveles atómicos (Hg, 4,9 eV). Rutherford: núcleo, $\frac{d\sigma}{d\Omega}\propto\sin^{-4}\frac\theta2$. "
             r"Millikan: carga cuantizada. Michelson--Morley: no hay éter."),
        ]),
        ("Estructura atómica", [
            ("Configuración y notación espectroscópica",
             r"Orden: 1s 2s 2p 3s 3p 4s 3d 4p. Término $^{2S+1}L_J$ ($L$ = S, P, D, F). "
             r"Hund: máximo $S$; luego máximo $L$; $J=|L-S|$ si la capa está a menos de la mitad, $L+S$ si a más. "
             r"Capa cerrada: $^1S_0$."),
            ("Zeeman, estructura fina e hiperfina",
             r"Zeeman normal: $\Delta E=\mu_BBm_l$, $\mu_B=5{,}79\times10^{-5}$ eV/T; la línea se parte en 3. "
             r"Fina $\sim\alpha^2E_n$ (espín--órbita). Hiperfina del H: línea de 21 cm (1420 MHz)."),
            ("Láser",
             r"Emisión estimulada: misma fase, dirección y polarización. Requiere inversión de población "
             r"($\ge3$ niveles). Einstein: $A/B\propto\nu^3$."),
        ]),
        ("Relatividad especial", [
            ("Dilatación, contracción y simultaneidad",
             r"$\gamma=\frac1{\sqrt{1-\beta^2}}$; \ $\Delta t=\gamma\Delta\tau$ (tiempo propio, el más corto); "
             r"$L=L_0/\gamma$ (solo en la dirección del movimiento). Sucesos simultáneos en un marco no lo son en otro."),
            ("Transformación de Lorentz y suma de velocidades",
             r"$x'=\gamma(x-vt)$, \ $t'=\gamma(t-vx/c^2)$. \ $u'=\frac{u-v}{1-uv/c^2}$. "
             r"Intervalo invariante $s^2=c^2\Delta t^2-\Delta x^2$ ($>0$: temporal, causal)."),
            ("Energía y momento",
             r"$E=\gamma mc^2$, \ $p=\gamma mv$, \ $E^2=(pc)^2+(mc^2)^2$, \ $K=(\gamma-1)mc^2$, \ $\beta=pc/E$. "
             r"Fotón: $E=pc$. Masa invariante: $(\sum E)^2-(\sum\vec pc)^2$ igual en todo marco. "
             r"Umbral con blanco fijo: $E_{\rm proy}=\frac{(\sum m_f)^2-m_a^2-m_b^2}{2m_b}c^2$."),
            ("Doppler relativista",
             r"Acercándose: $f=f_0\sqrt{\frac{1+\beta}{1-\beta}}$. Transversal: $f=f_0/\gamma$."),
        ]),
        ("Núcleo y partículas", [
            ("Decaimiento radiactivo",
             r"$N=N_0e^{-\lambda t}$, \ $t_{1/2}=\frac{\ln2}{\lambda}=0{,}693\,\tau$, \ $A=\lambda N$. "
             r"Tras $n$ vidas medias queda $2^{-n}$."),
            ("Tipos de decaimiento",
             r"$\alpha$: $A-4$, $Z-2$. \ $\beta^-$: $n\to p\,e^-\bar\nu_e$ ($Z+1$). \ "
             r"$\beta^+$: $p\to n\,e^+\nu_e$ ($Z-1$); captura electrónica. \ $\gamma$: no cambia $A$ ni $Z$. "
             r"Espectro $\beta$ continuo $\Rightarrow$ neutrino."),
            ("Energía de enlace y valor $Q$",
             r"$B=(Zm_p+Nm_n-M)c^2$; $B/A$ máximo $\approx8{,}8$ MeV en Fe/Ni. Fisión (pesados) y fusión "
             r"(ligeros) liberan energía. $Q=(m_i-m_f)c^2$; 1 u $=931{,}5$ MeV/$c^2$."),
            ("Radio nuclear",
             r"$R=R_0A^{1/3}$, $R_0\approx1{,}2$ fm $\Rightarrow$ densidad nuclear casi constante "
             r"($\sim2\times10^{17}$ kg/m$^3$)."),
            ("Partículas y leyes de conservación",
             r"Leptones: $e,\mu,\tau$ y sus $\nu$. Quarks $u,c,t$ ($+\frac23$), $d,s,b$ ($-\frac13$). "
             r"Bariones $qqq$ ($B=1$), mesones $q\bar q$. Se conservan: carga, número bariónico, número leptónico "
             r"de cada familia. Extrañeza: se conserva en la interacción fuerte y la EM, \emph{no} en la débil. "
             r"Bosones: fotón (EM), gluones (fuerte), $W^\pm,Z$ (débil), Higgs."),
            ("Alcance de una interacción",
             r"Yukawa: $R\approx\frac{\hbar}{mc}=\frac{\hbar c}{mc^2}$. Pion (140 MeV) $\Rightarrow$ $\approx1{,}4$ fm. "
             r"Fotón sin masa $\Rightarrow$ alcance infinito."),
        ]),
        ("Estado sólido", [
            ("Bandas y semiconductores",
             r"Conductor: banda parcialmente llena. Semiconductor: gap $\sim1$ eV (Si 1,1; Ge 0,67). "
             r"Aislante: $\gtrsim4$ eV (diamante 5,5). Dopaje $n$ = donador (grupo V: P, As); "
             r"$p$ = aceptor (grupo III: B, Ga). Con $T$, $\sigma$ sube en semiconductores y baja en metales."),
            ("Calor específico y otros",
             r"Debye: $C\propto T^3$ a $T$ baja; Dulong--Petit $3R$ a $T$ alta. Electrones: $C\propto T$, "
             r"$E_F\sim$ unos eV. Superconductor: $R=0$, efecto Meissner, pares de Cooper."),
        ]),
        ("Números que hay que saber", [
            ("Constantes y atajos",
             r"$hc=1240$ eV$\cdot$nm; \ $\hbar c=197$ MeV$\cdot$fm; \ $m_ec^2=0{,}511$ MeV; \ "
             r"$m_pc^2=938$ MeV; \ $kT(300\,{\rm K})\approx\frac1{40}$ eV; \ $\alpha\approx\frac1{137}$; \ "
             r"$a_0=0{,}0529$ nm; \ $h=4{,}14\times10^{-15}$ eV$\cdot$s; \ 1 eV $=1{,}60\times10^{-19}$ J. "
             r"Luz visible: 400--700 nm $\leftrightarrow$ 3,1--1,8 eV."),
        ]),
    ]),
]

EXPERIMENTAL_MATEMATICA = [
    ("Física experimental", "3 preguntas", [
        ("Incertidumbres", [
            ("Error sistemático y aleatorio; exactitud y precisión",
             r"Aleatorio: dispersión, baja como $1/\sqrt N$ al repetir. Sistemático: sesgo, no baja al repetir "
             r"(calibración, cero mal puesto). Exactitud = cerca del valor real; precisión = poca dispersión."),
            ("Media, desviación estándar y error de la media",
             r"$\bar x=\frac1N\sum x_i$; \ $s=\sqrt{\frac{1}{N-1}\sum(x_i-\bar x)^2}$ (dispersión de \emph{un} dato); "
             r"$\sigma_{\bar x}=s/\sqrt N$. Para reducir el error a la mitad: $4\times$ más datos."),
            ("Propagación de incertidumbres",
             r"Suma o resta: absolutos en cuadratura, $\delta q=\sqrt{\delta x^2+\delta y^2}$. "
             r"Producto o cociente: \emph{relativos} en cuadratura, $\frac{\delta q}{|q|}=\sqrt{(\frac{\delta x}{x})^2+(\frac{\delta y}{y})^2}$. "
             r"Potencia: $\frac{\delta(x^n)}{|x^n|}=|n|\frac{\delta x}{|x|}$. General: "
             r"$\delta q^2=\sum(\partial_iq\,\delta x_i)^2$ (si son independientes)."),
            ("Cifras significativas",
             r"La incertidumbre con 1 (o 2) cifras; el valor redondeado a la misma posición decimal: "
             r"$9{,}81\pm0{,}03$, no $9{,}8132\pm0{,}03$. Instrumento analógico: $\pm$ media división; digital: $\pm1$ en el último dígito."),
            ("Promedio ponderado",
             r"$\bar x=\frac{\sum w_ix_i}{\sum w_i}$, \ $w_i=1/\sigma_i^2$; \ $\sigma_{\bar x}=1/\sqrt{\sum w_i}$. "
             r"Dos medidas iguales de error $\sigma$: $\sigma/\sqrt2$."),
        ]),
        ("Estadística", [
            ("Poisson y conteo",
             r"$P(n)=\frac{\mu^ne^{-\mu}}{n!}$, \ $\sigma=\sqrt\mu$. $N$ cuentas $\Rightarrow$ error relativo $1/\sqrt N$: "
             r"1\% pide $10^4$ cuentas. Tasa: $R=N/t\pm\sqrt N/t$. Restar fondo: $\sigma=\sqrt{N_s+N_b}$ (cuadratura)."),
            ("Gaussiana",
             r"$68\%$ en $\pm1\sigma$, $95\%$ en $\pm2\sigma$, $99{,}7\%$ en $\pm3\sigma$. "
             r"FWHM $=2\sqrt{2\ln2}\,\sigma\approx2{,}355\,\sigma$. Poisson con $\mu\gtrsim20$ ya es casi gaussiana."),
            ("Binomial",
             r"$P(k)=\binom Nk p^k(1-p)^{N-k}$; media $Np$, varianza $Np(1-p)$. $p\ll1$, $N$ grande $\to$ Poisson."),
            (r"Ajuste y $\chi^2$",
             r"$\chi^2=\sum\frac{(y_i-f(x_i))^2}{\sigma_i^2}$; grados de libertad $\nu=N-$(parámetros). "
             r"$\chi^2/\nu\approx1$: buen ajuste. $\gg1$: modelo malo o $\sigma$ subestimadas. $\ll1$: $\sigma$ sobreestimadas."),
        ]),
        ("Gráficas y análisis", [
            ("Linealizar",
             r"$y=Ax^n$: $\log y$ vs $\log x$, pendiente $=n$. \ $y=Ae^{kx}$: $\ln y$ vs $x$, pendiente $=k$. "
             r"$T=2\pi\sqrt{L/g}$: $T^2$ vs $L$, pendiente $4\pi^2/g$. Leer la pendiente con puntos de la recta, no con datos."),
            ("Mínimos cuadrados (recta)",
             r"$y=mx+b$: \ $m=\frac{N\sum xy-\sum x\sum y}{N\sum x^2-(\sum x)^2}$, \ $b=\frac{\sum y-m\sum x}{N}$. "
             r"La recta pasa por $(\bar x,\bar y)$."),
            ("Análisis dimensional y órdenes de magnitud",
             r"Revisar unidades de cada opción antes de calcular: descarta muchas. "
             r"Ej.: frecuencia de un péndulo $\sim\sqrt{g/L}$; la única combinación con unidades de tiempo."),
        ]),
        ("Instrumentación", [
            ("Voltímetro y amperímetro",
             r"Voltímetro: en paralelo, resistencia interna \emph{muy alta}. Amperímetro: en serie, resistencia \emph{muy baja}. "
             r"Si no lo son, cargan el circuito y la lectura sale sesgada (error sistemático)."),
            ("Osciloscopio y señales AC",
             r"Leer período y $V_{pp}$ con las divisiones (V/div, s/div). Senoidal: $V_{\rm rms}=V_p/\sqrt2$, "
             r"$V_{pp}=2V_p$. Lissajous $x$--$y$: razón de frecuencias = cruces; desfase: elipse."),
            ("Filtros RC y constante de tiempo",
             r"$\tau=RC$; carga $V(1-e^{-t/\tau})$: $63\%$ en $\tau$. Corte $f_c=\frac{1}{2\pi RC}$, ahí $|H|=1/\sqrt2$ ($-3$ dB). "
             r"Paso bajo: salida en $C$; paso alto: salida en $R$. Por encima del corte, el paso bajo cae $\propto1/f$ ($-20$ dB/década)."),
            ("Amplificador operacional ideal",
             r"Reglas de oro (con realimentación negativa): sin corriente en las entradas; $V_+=V_-$. "
             r"Inversor: $-R_f/R_{\rm in}$. No inversor: $1+R_f/R_1$. Seguidor: ganancia 1, aísla impedancias."),
            ("Ruido y señal",
             r"Johnson: $\overline{V^2}=4kTR\Delta f$. Disparo (shot): $\propto\sqrt{I\Delta f}$. Promediar $N$ barridos: "
             r"señal/ruido mejora $\sqrt N$. Lock-in: detecta a una frecuencia de referencia y reduce el ancho de banda."),
        ]),
        ("Técnicas y detectores", [
            ("Detectores",
             r"Geiger: cuenta, no da energía; tiene tiempo muerto. Centelleador + fotomultiplicador: rápido, energía con resolución moderada. "
             r"Germanio (enfriado): la mejor resolución en $\gamma$. CCD y fotodiodos: luz. Tiempo muerto $\tau$: $R_{\rm real}=\frac{R_{\rm medida}}{1-R_{\rm medida}\tau}$."),
            ("Interferometría y redes",
             r"Michelson: mover el espejo $d$ pasa $N=2d/\lambda$ franjas. Red: $d\sin\theta=m\lambda$; "
             r"poder resolutivo $\lambda/\Delta\lambda=mN$ (N = rendijas iluminadas)."),
            ("Resolución óptica",
             r"Rayleigh: $\theta_{\min}=1{,}22\,\lambda/D$ (abertura circular). Mejora con $D$ grande o $\lambda$ corta "
             r"(por eso los microscopios electrónicos)."),
        ]),
    ]),
    ("Física matemática", "2 preguntas", [
        ("Álgebra lineal", [
            ("Autovalores y autovectores",
             r"$\det(A-\lambda I)=0$. Atajos: $\operatorname{tr}A=\sum\lambda_i$, \ $\det A=\prod\lambda_i$. "
             r"$2\times2$: $\lambda^2-(\operatorname{tr}A)\lambda+\det A=0$. Matriz triangular: autovalores en la diagonal."),
            ("Matrices especiales",
             r"Hermítica $A=A^\dagger$: $\lambda$ reales, autovectores ortogonales. Unitaria $U^\dagger U=I$: $|\lambda|=1$, "
             r"conserva la norma. Ortogonal real: rotaciones, $\det=\pm1$. Simétrica real: siempre diagonalizable."),
            (r"Vectores, $\delta_{ij}$ y $\varepsilon_{ijk}$",
             r"$\vec A\times(\vec B\times\vec C)=\vec B(\vec A\cdot\vec C)-\vec C(\vec A\cdot\vec B)$. "
             r"$\varepsilon_{ijk}\varepsilon_{imn}=\delta_{jm}\delta_{kn}-\delta_{jn}\delta_{km}$. "
             r"$\vec A\cdot(\vec B\times\vec C)$ = volumen = determinante."),
        ]),
        ("Cálculo vectorial", [
            ("Operadores en esféricas y cilíndricas",
             r"Esféricas: $\nabla\cdot\vec A\ni\frac1{r^2}\partial_r(r^2A_r)$; \ "
             r"$\nabla^2f=\frac{1}{r^2}\partial_r(r^2\partial_rf)+\frac{1}{r^2\sin\theta}\partial_\theta(\sin\theta\,\partial_\theta f)"
             r"+\frac{1}{r^2\sin^2\theta}\partial_\phi^2f$. Cilíndricas: $\nabla\cdot\vec A\ni\frac1s\partial_s(sA_s)$. "
             r"$\nabla\cdot(\hat r/r^2)=4\pi\delta^3(\vec r)$."),
            ("Identidades y teoremas",
             r"$\nabla\times\nabla f=0$, \ $\nabla\cdot(\nabla\times\vec A)=0$, \ "
             r"$\nabla\times(\nabla\times\vec A)=\nabla(\nabla\cdot\vec A)-\nabla^2\vec A$. "
             r"Gauss: $\int_V\nabla\cdot\vec A\,dV=\oint_S\vec A\cdot d\vec a$. Stokes: $\int_S(\nabla\times\vec A)\cdot d\vec a=\oint\vec A\cdot d\vec l$."),
            ("Elementos de volumen",
             r"Esféricas: $dV=r^2\sin\theta\,dr\,d\theta\,d\phi$ (ángulo sólido total $4\pi$). "
             r"Cilíndricas: $dV=s\,ds\,d\phi\,dz$. Polares: $dA=r\,dr\,d\theta$."),
        ]),
        ("Series e integrales", [
            ("Taylor de las que más salen",
             r"$(1+x)^n\approx1+nx+\frac{n(n-1)}2x^2$; \ $e^x=\sum\frac{x^k}{k!}$; \ $\sin x\approx x-\frac{x^3}6$; \ "
             r"$\cos x\approx1-\frac{x^2}2$; \ $\ln(1+x)\approx x-\frac{x^2}2$; \ $\frac1{1-x}=\sum x^k$ ($|x|<1$). "
             r"$\gamma\approx1+\frac12\beta^2$."),
            ("Integrales gaussianas y función gamma",
             r"$\int_{-\infty}^\infty e^{-ax^2}dx=\sqrt{\pi/a}$; \ $\int_{-\infty}^\infty x^2e^{-ax^2}dx=\frac{\sqrt\pi}{2a^{3/2}}$; "
             r"impares $\to0$. $\int_0^\infty x^ne^{-x}dx=n!=\Gamma(n+1)$, \ $\Gamma(\frac12)=\sqrt\pi$."),
        ]),
        ("Variable compleja", [
            ("Euler y raíces",
             r"$e^{i\theta}=\cos\theta+i\sin\theta$; $z=re^{i\theta}$, $|z|^2=zz^*$. "
             r"Raíces $n$-ésimas de 1: $e^{2\pi ik/n}$, suman 0. $\cos\theta=\frac{e^{i\theta}+e^{-i\theta}}2$; $i^i=e^{-\pi/2}$."),
            ("Analiticidad y residuos",
             r"Cauchy--Riemann: $u_x=v_y$, $u_y=-v_x$. $\oint f\,dz=2\pi i\sum{\rm Res}$ (polos dentro). "
             r"Polo simple: ${\rm Res}_{z_0}=\lim(z-z_0)f(z)$. Analítica sin polos dentro $\Rightarrow$ integral $=0$."),
        ]),
        ("Ecuaciones diferenciales", [
            ("EDO lineales de coeficientes constantes",
             r"Probar $e^{rt}$ $\Rightarrow$ ecuación característica. $\ddot x+2\beta\dot x+\omega_0^2x=0$: "
             r"subamortiguado $\beta<\omega_0$ (oscila con $\omega=\sqrt{\omega_0^2-\beta^2}$), crítico $\beta=\omega_0$ "
             r"(vuelve más rápido sin oscilar), sobreamortiguado $\beta>\omega_0$."),
            ("Oscilador forzado y resonancia",
             r"Solución = homogénea (se apaga) + particular. Amplitud máxima cerca de $\omega_0$; "
             r"$Q=\omega_0/(2\beta)\approx\omega_0/\Delta\omega$ (ancho a media potencia). En resonancia, desfase $90^\circ$."),
            ("Separación de variables y Laplace",
             r"$\nabla^2V=0$ en esféricas con simetría azimutal: $V=\sum(A_lr^l+B_lr^{-l-1})P_l(\cos\theta)$. "
             r"$P_0=1$, $P_1=x$, $P_2=\frac12(3x^2-1)$. Cartesianas: senos en una dirección, exponenciales en la otra."),
            ("Onda y difusión",
             r"Onda: $\partial_t^2u=v^2\nabla^2u$, solución $f(x-vt)+g(x+vt)$. "
             r"Difusión/calor: $\partial_tu=D\nabla^2u$; los modos decaen como $e^{-Dk^2t}$ y el ancho crece $\propto\sqrt{t}$."),
            ("Funciones especiales y dónde aparecen",
             r"Legendre y armónicos esféricos: problemas con simetría esférica. Bessel: cilindros, membranas circulares. "
             r"Hermite: oscilador cuántico. Laguerre: parte radial del hidrógeno. Son ortogonales $\Rightarrow$ desarrollos en serie."),
        ]),
        ("Fourier y delta de Dirac", [
            ("Serie de Fourier",
             r"$f=\frac{a_0}2+\sum(a_n\cos nx+b_n\sin nx)$, $a_n=\frac1\pi\int_{-\pi}^{\pi}f\cos nx$. "
             r"Función impar: solo senos; par: solo cosenos. Cuadrada: $\frac4\pi\sum_{n\ {\rm impar}}\frac{\sin nx}{n}$ "
             r"(armónicos impares, caen $1/n$; triangular cae $1/n^2$). Gibbs: sobreimpulso del 9\% en saltos."),
            ("Transformada de Fourier",
             r"Gaussiana $\to$ gaussiana; $\sigma_x\sigma_k=\frac12$: angosta en $x$ $\Leftrightarrow$ ancha en $k$. "
             r"$\delta(x)\leftrightarrow$ constante. Rendija (rectángulo) $\to$ ${\rm sinc}$. Derivar $\to$ multiplicar por $ik$."),
            ("Delta de Dirac",
             r"$\int f(x)\delta(x-a)dx=f(a)$; \ $\delta(ax)=\frac{\delta(x)}{|a|}$; \ "
             r"$\delta(g(x))=\sum\frac{\delta(x-x_i)}{|g'(x_i)|}$ ($g(x_i)=0$). Unidades: $1/[x]$. $\frac{d}{dx}\Theta(x)=\delta(x)$."),
        ]),
    ]),
]

ANALITICA_EM_TERMO = [
    ("Mecánica analítica", "3 preguntas", [
        ("Lagrange", [
            (r"Lagrangiano y Euler--Lagrange",
             r"$L=T-V$; \ $\frac{d}{dt}\frac{\partial L}{\partial\dot q}-\frac{\partial L}{\partial q}=0$. "
             r"Escribir $T$ en las coordenadas naturales (polares: $T=\frac m2(\dot r^2+r^2\dot\theta^2)$; "
             r"esféricas: $+r^2\sin^2\theta\,\dot\phi^2$)."),
            (r"Coordenadas generalizadas y ligaduras",
             r"Grados de libertad $=3N-k$ (ligaduras holónomas). Elegir $q$ que hagan obvias las ligaduras. "
             r"Fuerzas de ligadura: multiplicadores, $\frac{d}{dt}\partial_{\dot q}L-\partial_qL=\lambda\,\partial_q f$."),
            (r"Momento conjugado y coordenadas cíclicas",
             r"$p_q=\partial L/\partial\dot q$. Si $L$ no depende de $q$ (cíclica), $p_q$ se conserva. "
             r"Ej.: fuerza central $\Rightarrow$ $p_\theta=mr^2\dot\theta=\ell$ constante."),
            (r"Función energía $h$",
             r"$h=\sum\dot q\,p-L$; se conserva si $\partial L/\partial t=0$. Es $T+V$ solo si las ligaduras "
             r"no dependen del tiempo (aro que gira: $h$ se conserva pero no es la energía)."),
            (r"Teorema de Noether",
             r"Simetría continua $\Rightarrow$ cantidad conservada. Traslación $\to$ momento lineal; "
             r"rotación $\to$ momento angular; traslación en el tiempo $\to$ energía."),
            (r"Partícula cargada",
             r"$L=\frac12mv^2-q\phi+q\vec v\cdot\vec A$. Momento canónico $\vec p=m\vec v+q\vec A$ (no el cinético). "
             r"$H=\frac{(\vec p-q\vec A)^2}{2m}+q\phi$."),
            (r"Principio de acción y cálculo variacional",
             r"$\delta S=0$, $S=\int L\,dt$. Funcional $\int f(y,y',x)dx$: Euler--Lagrange en $y$. "
             r"Si $f$ no depende de $x$: $f-y'\partial_{y'}f=$ cte (Beltrami). Braquistócrona: cicloide; geodésica plana: recta."),
        ]),
        ("Hamilton", [
            (r"Hamiltoniano y ecuaciones canónicas",
             r"$H=\sum p\dot q-L$ (expresado en $q,p$). $\dot q=\partial H/\partial p$, \ $\dot p=-\partial H/\partial q$. "
             r"Oscilador: $H=\frac{p^2}{2m}+\frac12m\omega^2x^2$."),
            (r"Corchetes de Poisson",
             r"$\{f,g\}=\sum\left(\frac{\partial f}{\partial q}\frac{\partial g}{\partial p}-\frac{\partial f}{\partial p}\frac{\partial g}{\partial q}\right)$; "
             r"$\{q,p\}=1$. $\frac{df}{dt}=\{f,H\}+\partial_tf$: si $\{f,H\}=0$ se conserva. $\{L_x,L_y\}=L_z$."),
            (r"Espacio de fases y Liouville",
             r"Oscilador: elipse de área $2\pi E/\omega$. Liouville: el volumen en el espacio de fases se conserva. "
             r"Invariante adiabático: $E/\omega$ (cambios lentos de $\omega$). Trayectorias no se cruzan."),
            (r"Transformaciones canónicas",
             r"Conservan $\{Q,P\}=1$ y la forma de las ecuaciones de Hamilton. Prueba rápida: calcular $\{Q,P\}$. "
             r"Hamilton--Jacobi: $H(q,\partial_qS)+\partial_tS=0$."),
        ]),
        ("Aplicaciones", [
            (r"Fuerzas centrales y potencial efectivo",
             r"$U_{\rm ef}=V(r)+\frac{\ell^2}{2mr^2}$. Circular: $U_{\rm ef}'=0$; estable si $U_{\rm ef}''>0$; "
             r"frecuencia radial $\omega_r^2=U_{\rm ef}''/m$. Problema de dos cuerpos: masa reducida."),
            (r"Kepler",
             r"$T^2=\frac{4\pi^2a^3}{GM}$; $E=-\frac{GMm}{2a}$ (solo depende de $a$). Velocidad areolar $\ell/2m$ constante. "
             r"Circular: $v=\sqrt{GM/r}$; escape $\sqrt2\,v_{\rm circ}$. Virial: $\langle T\rangle=-\frac12\langle V\rangle$."),
            (r"Pequeñas oscilaciones",
             r"Equilibrio: $V'(q_0)=0$; estable si $V''>0$. Si $T=\frac12M\dot q^2$: $\omega^2=V''(q_0)/M$. "
             r"Péndulo: $\omega^2=g/l$; físico: $\omega^2=mgd/I$."),
            (r"Modos normales",
             r"$\det(K-\omega^2M)=0$. Pared--$k$--$m$--$k$--$m$--$k$--pared: $\omega^2=\frac km$ (en fase) y $\frac{3k}m$ (contrafase). "
             r"$N$ grados de libertad $\to$ $N$ modos; un modo de $\omega=0$ es traslación libre."),
            (r"Ejemplos clásicos",
             r"Atwood: $a=\frac{m_1-m_2}{m_1+m_2}g$. Cuenta en aro que gira con $\omega$: equilibrio "
             r"$\cos\theta=g/(\omega^2R)$ si $\omega^2>g/R$ (si no, solo el fondo). Péndulo con soporte acelerado: $g_{\rm ef}=\vec g-\vec a$."),
            (r"Marcos no inerciales",
             r"$m\vec a'=\vec F-2m\vec\omega\times\vec v'-m\vec\omega\times(\vec\omega\times\vec r)$. "
             r"Coriolis desvía a la derecha en el hemisferio norte. Foucault: $\Omega=\omega\sin\lambda$."),
            (r"Cuerpo rígido",
             r"$T=\frac12\vec\omega\cdot I\vec\omega$; ejes principales diagonalizan $I$. Steiner: $I=I_{\rm cm}+Md^2$. "
             r"Giroscopio: $\Omega_{\rm prec}=\frac{mgr}{I\omega}$. Rotación estable en el eje de $I$ máximo y mínimo, no en el intermedio."),
        ]),
    ]),
    ("Electromagnetismo y electrodinámica", "5 preguntas", [
        ("Electrostática", [
            (r"Gauss y campos típicos",
             r"$\oint\vec E\cdot d\vec a=Q_{\rm enc}/\varepsilon_0$. Puntual $\frac{kq}{r^2}$; línea $\frac{\lambda}{2\pi\varepsilon_0r}$; "
             r"plano $\frac{\sigma}{2\varepsilon_0}$; junto a conductor $\frac{\sigma}{\varepsilon_0}$; esfera uniforme dentro $\frac{kQr}{R^3}$; cascarón dentro: 0."),
            (r"Potencial y energía",
             r"$\vec E=-\nabla V$, \ $V=\frac{kq}r$. Energía de cargas $W=\sum_{i<j}\frac{kq_iq_j}{r_{ij}}$; "
             r"$W=\frac{\varepsilon_0}2\int E^2dV$. Esfera conductora: $W=\frac{kQ^2}{2R}$."),
            (r"Conductores e imágenes",
             r"Dentro $E=0$, superficie equipotencial, carga en la superficie. Plano a tierra: imagen $-q$ a $d$ detrás; "
             r"fuerza $\frac{kq^2}{(2d)^2}$. Esfera a tierra: $q'=-\frac Raq$ en $\frac{R^2}a$."),
            (r"Dipolo eléctrico",
             r"$\vec p=q\vec d$; $V=\frac{kp\cos\theta}{r^2}$, $E\propto1/r^3$. $\vec\tau=\vec p\times\vec E$, $U=-\vec p\cdot\vec E$; "
             r"fuerza neta solo si $E$ no es uniforme. Multipolos: monopolo $1/r$, dipolo $1/r^2$, cuadrupolo $1/r^3$ (en $V$)."),
            (r"Capacitores y dieléctricos",
             r"$C=\varepsilon_0A/d$; serie $\frac1C=\sum\frac1{C_i}$, paralelo $C=\sum C_i$. $U=\frac{Q^2}{2C}=\frac12CV^2$. "
             r"Dieléctrico: $C\to\kappa C$. Con batería: $V$ fijo, $U$ sube. Aislado: $Q$ fijo, $U$ baja ($\div\kappa$)."),
            (r"Laplace, Poisson y unicidad",
             r"$\nabla^2V=-\rho/\varepsilon_0$; sin carga, $V$ no tiene máximos ni mínimos locales (Earnshaw: no hay equilibrio estable electrostático). "
             r"Condiciones de frontera fijan la solución: si una adivinanza las cumple, es la solución."),
        ]),
        ("Magnetostática", [
            (r"Ampère, Biot--Savart y campos típicos",
             r"$\oint\vec B\cdot d\vec l=\mu_0I_{\rm enc}$. Hilo $\frac{\mu_0I}{2\pi r}$; centro de espira $\frac{\mu_0I}{2R}$; "
             r"eje de espira $\frac{\mu_0IR^2}{2(R^2+z^2)^{3/2}}$; solenoide $\mu_0nI$ (fuera $\approx0$); toroide $\frac{\mu_0NI}{2\pi r}$."),
            (r"Fuerza de Lorentz y movimiento",
             r"$\vec F=q(\vec E+\vec v\times\vec B)$; $B$ no hace trabajo. Ciclotrón: $r=\frac{mv}{qB}$, $\omega=\frac{qB}m$ (independiente de $v$). "
             r"Selector: $v=E/B$. Hilos paralelos: $\frac{F}{l}=\frac{\mu_0I_1I_2}{2\pi d}$, misma dirección se atraen."),
            (r"Dipolo magnético",
             r"$\vec m=I\vec A$; $\vec\tau=\vec m\times\vec B$, $U=-\vec m\cdot\vec B$; campo dipolar $\propto1/r^3$. "
             r"Momento magnético y angular: $\vec m=\frac{q}{2m}\vec L$ (clásico)."),
            (r"Materiales magnéticos",
             r"$\vec H=\vec B/\mu_0-\vec M$, $\vec M=\chi_m\vec H$. Diamagnético $\chi<0$ (pequeño, repelido); paramagnético $\chi>0$ (Curie $\chi\propto1/T$); "
             r"ferromagnético: histéresis, pierde el orden sobre $T_C$. Superconductor: $\chi=-1$."),
        ]),
        ("Inducción y circuitos", [
            (r"Faraday y Lenz",
             r"$\mathcal E=-\frac{d\Phi_B}{dt}$; la corriente inducida se opone al cambio. Barra móvil: $\mathcal E=BLv$. "
             r"Generador: $\mathcal E=NBA\omega\sin\omega t$. Imán que cae por un tubo conductor: frenado."),
            (r"Inductancia y energía magnética",
             r"$\mathcal E=-L\dot I$; solenoide $L=\mu_0n^2Al$. $U=\frac12LI^2$; densidad $\frac{B^2}{2\mu_0}$ "
             r"(eléctrica: $\frac{\varepsilon_0E^2}2$). Mutua: $M_{12}=M_{21}$."),
            (r"Circuitos RC, RL, LC y RLC",
             r"$\tau_{RC}=RC$, $\tau_{RL}=L/R$, $\omega_0=1/\sqrt{LC}$. Impedancias $Z_R=R$, $Z_L=i\omega L$, $Z_C=\frac{1}{i\omega C}$. "
             r"Justo después de cerrar: $C$ = cable, $L$ = abierto; al final al revés. Potencia media $I_{\rm rms}^2R$; "
             r"$Q=\frac{\omega_0L}{R}$."),
        ]),
        ("Maxwell, ondas y radiación", [
            (r"Ecuaciones de Maxwell",
             r"$\nabla\cdot\vec E=\rho/\varepsilon_0$, \ $\nabla\cdot\vec B=0$, \ $\nabla\times\vec E=-\partial_t\vec B$, \ "
             r"$\nabla\times\vec B=\mu_0\vec J+\mu_0\varepsilon_0\partial_t\vec E$ (corriente de desplazamiento: entre placas de un capacitor que carga). "
             r"Continuidad: $\nabla\cdot\vec J=-\partial_t\rho$."),
            (r"Ondas en el vacío y Poynting",
             r"$c=1/\sqrt{\mu_0\varepsilon_0}$; $E=cB$; $\vec E\perp\vec B\perp\vec k$. $\vec S=\frac1{\mu_0}\vec E\times\vec B$; "
             r"$I=\langle S\rangle=\frac12c\varepsilon_0E_0^2$. Presión: $I/c$ si absorbe, $2I/c$ si refleja. Momento $=U/c$."),
            (r"Ondas en medios y en fronteras",
             r"$n=c/v\approx\sqrt{\varepsilon_r}$. Normal: $R=\left(\frac{n_1-n_2}{n_1+n_2}\right)^2$ (vidrio $\approx4\%$). "
             r"Brewster: $\tan\theta_B=n_2/n_1$ (reflejada polarizada $\perp$ al plano de incidencia). Crítico: $\sin\theta_c=n_2/n_1$. "
             r"Conductor: profundidad $\delta=\sqrt{2/(\mu\sigma\omega)}$. Malus: $I=I_0\cos^2\theta$; polarizador ideal sobre luz natural: $I_0/2$."),
            (r"Radiación",
             r"Larmor: $P=\frac{q^2a^2}{6\pi\varepsilon_0c^3}$. Dipolo oscilante: $P\propto\omega^4p_0^2$ (cielo azul), "
             r"patrón $\propto\sin^2\theta$, nada a lo largo del eje. Carga a velocidad constante no radia."),
            (r"Potenciales y gauge",
             r"$\vec B=\nabla\times\vec A$, $\vec E=-\nabla V-\partial_t\vec A$. Gauge: $\vec A\to\vec A+\nabla\lambda$, "
             r"$V\to V-\partial_t\lambda$. Coulomb $\nabla\cdot\vec A=0$; Lorenz $\nabla\cdot\vec A+\frac1{c^2}\partial_tV=0$ (ecuaciones de onda)."),
            (r"Electrodinámica relativista",
             r"$\vec E$ y $\vec B$ se mezclan entre marcos: $E'_\perp=\gamma(\vec E+\vec v\times\vec B)_\perp$, componentes paralelas iguales. "
             r"Invariantes: $\vec E\cdot\vec B$ y $E^2-c^2B^2$. Carga y fase son invariantes."),
            (r"Constantes",
             r"$\varepsilon_0=8{,}85\times10^{-12}$ F/m; $\mu_0=4\pi\times10^{-7}$ T$\cdot$m/A; $k=9\times10^9$ N$\cdot$m$^2$/C$^2$; "
             r"$e=1{,}6\times10^{-19}$ C; 1 T $=10^4$ G; Tierra $\approx0{,}5$ G."),
        ]),
    ]),
    ("Termodinámica y mecánica estadística", "2 preguntas", [
        ("Termodinámica", [
            (r"Primera ley y trabajo",
             r"$\Delta U=Q-W$ ($W$ hecho \emph{por} el gas), $W=\int P\,dV$ = área bajo la curva $P$--$V$. "
             r"Ciclo: $\Delta U=0$, $W_{\rm neto}$ = área encerrada (horario = máquina)."),
            (r"Gas ideal y equipartición",
             r"$PV=nRT=NkT$. $U=\frac f2nRT$; $C_V=\frac f2R$, $C_P=C_V+R$, $\gamma=C_P/C_V$: monoatómico $\frac53$, diatómico $\frac75$. "
             r"Cada término cuadrático: $\frac12kT$. Sólido: $3R$ (Dulong--Petit)."),
            (r"Procesos",
             r"Isotérmico: $\Delta U=0$, $W=nRT\ln\frac{V_f}{V_i}$. Adiabático: $PV^\gamma$ y $TV^{\gamma-1}$ ctes, "
             r"$W=\frac{P_iV_i-P_fV_f}{\gamma-1}$, más empinada que la isoterma. Isobárico: $W=P\Delta V$, $Q=nC_P\Delta T$. Isocórico: $W=0$."),
            (r"Entropía",
             r"$dS=\frac{dQ_{\rm rev}}T$; aislado: $\Delta S\ge0$. Isotérmico: $nR\ln\frac{V_f}{V_i}$. Calentar: $mc\ln\frac{T_f}{T_i}$. "
             r"Expansión libre (gas ideal): $W=Q=0$, $\Delta T=0$, $\Delta S=nR\ln\frac{V_f}{V_i}>0$. Cambio de fase: $\Delta S=\frac{mL}{T}$."),
            (r"Máquinas y refrigeradores",
             r"Carnot: $\eta=1-\frac{T_c}{T_h}$ (máximo posible, en kelvin). Refrigerador $COP=\frac{T_c}{T_h-T_c}$; "
             r"bomba de calor $\frac{T_h}{T_h-T_c}$. $\eta=W/Q_h$."),
            (r"Potenciales y relaciones de Maxwell",
             r"$dU=TdS-PdV$; $H=U+PV$; $F=U-TS$ ($dF=-SdT-PdV$); $G=H-TS$ ($dG=-SdT+VdP$). "
             r"Maxwell: $\left(\frac{\partial S}{\partial V}\right)_T=\left(\frac{\partial P}{\partial T}\right)_V$. Equilibrio a $T,P$ fijas: $G$ mínima."),
            (r"Calorimetría y transferencia",
             r"$Q=mc\Delta T$, $Q=mL$. Conducción $P=kA\frac{\Delta T}{L}$ (resistencias térmicas en serie se suman). "
             r"Radiación $P=e\sigma AT^4$; neta $e\sigma A(T^4-T_0^4)$."),
            (r"Teoría cinética",
             r"$\langle K\rangle=\frac32kT$; $v_{\rm rms}=\sqrt{3kT/m}$, $\bar v=\sqrt{8kT/\pi m}$, $v_p=\sqrt{2kT/m}$ "
             r"($v_p<\bar v<v_{\rm rms}$). $P=\frac13nm\langle v^2\rangle$. Camino libre medio $\lambda=\frac1{\sqrt2n\sigma}$. Efusión $\propto1/\sqrt m$."),
            (r"Gases reales y fases",
             r"van der Waals: $\left(P+\frac{an^2}{V^2}\right)(V-nb)=nRT$ ($a$ atracción, $b$ volumen propio). "
             r"Clausius--Clapeyron: $\frac{dP}{dT}=\frac{L}{T\Delta v}$. Punto triple, punto crítico."),
        ]),
        ("Mecánica estadística", [
            (r"Boltzmann y función de partición",
             r"$P_i=\frac{g_ie^{-E_i/kT}}Z$, $Z=\sum g_ie^{-\beta E_i}$. $\langle E\rangle=-\partial_\beta\ln Z$; "
             r"$F=-kT\ln Z$; $S=k\ln\Omega$. Sistemas independientes: $Z_{\rm tot}=Z_1^N$ ($/N!$ si son indistinguibles)."),
            (r"Sistema de dos niveles",
             r"Niveles $0$ y $\varepsilon$: $\langle E\rangle=\frac{\varepsilon}{e^{\varepsilon/kT}+1}$. $T\to\infty$: poblaciones iguales "
             r"($\langle E\rangle\to\varepsilon/2$). $C$ tiene un pico (Schottky) en $kT\sim\varepsilon$. Inversión $\leftrightarrow$ $T<0$."),
            (r"Oscilador cuántico y sólidos",
             r"$\langle E\rangle=\frac{\hbar\omega}2+\frac{\hbar\omega}{e^{\hbar\omega/kT}-1}$; alta $T$: $kT$; baja: se congela. "
             r"Einstein: $C\to0$ exponencial; Debye: $C\propto T^3$. Grados de libertad congelados explican $C_V$ del H$_2$."),
            (r"Bose--Einstein y Fermi--Dirac",
             r"$\bar n=\frac{1}{e^{(E-\mu)/kT}\mp1}$ ($-$ bosones, $+$ fermiones). Fotones: $\mu=0$. "
             r"Fermiones a $T=0$: llenos hasta $E_F$ ($\bar n=1$ abajo, 0 arriba). Límite clásico: $e^{(E-\mu)/kT}\gg1$ $\to$ Boltzmann."),
            (r"Paramagnetismo",
             r"Espines $\pm\mu$ en $B$: $M=N\mu\tanh\frac{\mu B}{kT}$; $kT\gg\mu B$: $M\approx\frac{N\mu^2B}{kT}$ (Curie, $\chi\propto1/T$)."),
            (r"Gas de fotones",
             r"$u\propto T^4$ (Stefan--Boltzmann), $P=u/3$, número de fotones $\propto T^3$. "
             r"Expansión adiabática: $T\propto1/a$ (fondo cósmico)."),
        ]),
    ]),
]

PREAMBULO = r"""\documentclass[10pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish,es-noquoting]{babel}
\usepackage[a4paper,top=1.4cm,bottom=1.4cm,left=1.5cm,right=1.5cm]{geometry}
\usepackage{amsmath,amssymb,mathtools,xcolor,multicol,enumitem,fancyhdr,lastpage,needspace}
\definecolor{cab}{HTML}{1F3864}
\definecolor{alerta}{HTML}{B00020}
\setlength{\parindent}{0pt}
\pagestyle{fancy}\fancyhf{}
\lhead{\small\textbf{%s}}
\rhead{\small UNAL Física \textperiodcentered\ 16-oct \textperiodcentered\ \thepage/\pageref{LastPage}}
\renewcommand{\headrulewidth}{0.4pt}
\newcommand{\area}[2]{\vspace{2mm}{\color{cab}\Large\textbf{#1}}\hfill{\color{cab}#2}\par\vspace{1mm}\hrule\vspace{2mm}}
\newcommand{\bloque}[1]{\needspace{5\baselineskip}\vspace{1.5mm}{\color{cab}\textbf{#1}}\par\vspace{0.5mm}}
\begin{document}
"""


def lista(areas):
    partes = [PREAMBULO % "Lista de temas — escribir de memoria"]
    partes.append(
        r"\fbox{\parbox{\dimexpr\linewidth-2\fboxsep}{\small "
        r"\textbf{Cómo se usa.} Hoja en blanco, 10--15 minutos por área, sin libro. Para cada número "
        r"escribe lo que recuerdes: fórmula, valor, condición, gráfica. Si no sale nada, deja el número "
        r"y sigue. Después abre la \emph{referencia} y corrige \textcolor{alerta}{\textbf{en rojo}}. "
        r"Lo rojo son los problemas de hoy y lo que reescribes mañana.}}\par\vspace{3mm}")
    n = 0
    for nombre, peso, bloques in areas:
        partes.append(rf"\area{{{nombre}}}{{{peso}}}")
        partes.append(r"\begin{multicols}{2}")
        for bloque, temas in bloques:
            partes.append(rf"\bloque{{{bloque}}}")
            partes.append(r"\begin{itemize}[leftmargin=2.2em,itemsep=1.2pt,topsep=0pt]")
            for tema, _ in temas:
                n += 1
                partes.append(rf"\item[$\square$ \textbf{{{n}.}}] {tema}")
            partes.append(r"\end{itemize}")
        partes.append(r"\end{multicols}")
    partes.append(r"\end{document}")
    return "\n".join(partes)


def referencia(areas):
    partes = [PREAMBULO % "Hoja de referencia — abrir solo para corregir"]
    n = 0
    for nombre, peso, bloques in areas:
        partes.append(rf"\area{{{nombre}}}{{{peso}}}")
        partes.append(r"\begin{multicols}{2}\small")
        for bloque, temas in bloques:
            partes.append(rf"\bloque{{{bloque}}}")
            for tema, texto in temas:
                n += 1
                partes.append(rf"\textbf{{{n}. {tema}.}} {texto}\par\vspace{{1.6mm}}")
        partes.append(r"\end{multicols}")
    partes.append(r"\end{document}")
    return "\n".join(partes)


def compilar(nombre, fuente):
    tex = AQUI / f"{nombre}.tex"
    tex.write_text(fuente, encoding="utf-8")
    for _ in range(2):  # dos pasadas para LastPage
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex.name],
                           cwd=AQUI, capture_output=True, text=True, errors="replace")
        if r.returncode:
            print(r.stdout[-2500:])
            sys.exit(f"falló {nombre}")
    for ext in ("aux", "log", "out"):
        (AQUI / f"{nombre}.{ext}").unlink(missing_ok=True)
    print(f"ok  {nombre}.pdf")


if __name__ == "__main__":
    compilar("lista_cuantica_moderna", lista(CUANTICA_MODERNA))
    compilar("referencia_cuantica_moderna", referencia(CUANTICA_MODERNA))
    compilar("lista_experimental_matematica", lista(EXPERIMENTAL_MATEMATICA))
    compilar("referencia_experimental_matematica", referencia(EXPERIMENTAL_MATEMATICA))
    compilar("lista_analitica_em_termo", lista(ANALITICA_EM_TERMO))
    compilar("referencia_analitica_em_termo", referencia(ANALITICA_EM_TERMO))
