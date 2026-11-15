#!/usr/bin/env python3
"""Build kunlik-data.js: the daily-problem pool. Every numeric answer is recomputed here from the givens
in the statement, so the key cannot drift from the text. Run: python3 tools/kunlik_build.py"""
import json, math

NA = 6.02214076e23; R = 8.314462618; F = 96485.33212

def uranium_series():
    # 238U -> 206Pb: mass drops by 32 => 8 alpha; Z must go 92 -> 82: 92 - 2*8 + n_beta = 82
    n_a = (238 - 206) // 4; n_b = 82 - (92 - 2 * n_a); return n_a, n_b
n_alpha, n_beta = uranium_series(); assert (n_alpha, n_beta) == (8, 6)

ph_buf = 4.76 + math.log10(0.050 / 0.10)                       # Henderson-Hasselbalch
rho_nacl = 4 * 58.44 / (NA * (564.0e-10) ** 3)                   # g/cm3, 4 NaCl per cell
p32_left = 1.00 * 0.5 ** (57.2 / 14.3)                          # mg
e_cu = 0.34 + (R * 298.15 / (2 * F)) * math.log(0.010)          # V
Ka, C = 6.8e-4, 0.10
x = (-Ka + math.sqrt(Ka * Ka + 4 * Ka * C)) / 2; ph_hf = -math.log10(x)
co_x = (18 - (9 + 1)) // 2                                       # [Co(CO)x]-: Co(-I) d10 -> 10 + 2x = 18
assert co_x == 4

P = [
 dict(t="Radioaktivlik", lvl="O‘rta",
  q="<sup>238</sup>U bir qator α- va β<sup>−</sup>-yemirilishlardan keyin barqaror <sup>206</sup>Pb ga aylanadi. Shu yo‘lda nechta β<sup>−</sup>-yemirilish bo‘ladi?",
  kind="num", ans=n_beta, tol=0, unit="ta",
  hint="Massa soni faqat α-yemirilishda o‘zgaradi, har safar 4 ga. Avval α lar sonini toping.",
  sol=["Massa soni 238 dan 206 ga, ya’ni 32 ga kamaydi: 32 / 4 = 8 ta α.",
       "8 ta α zaryadni 16 ga kamaytiradi: 92 − 16 = 76.",
       "Pb uchun Z = 82 kerak. Har bir β<sup>−</sup> zaryadni 1 ga oshiradi: 82 − 76 = <b>6 ta β<sup>−</sup></b>."]),
 dict(t="Bufer eritma", lvl="Oson",
  q="Eritmada 0,10 M CH<sub>3</sub>COOH va 0,050 M CH<sub>3</sub>COONa bor. pK<sub>a</sub>(CH<sub>3</sub>COOH) = 4,76. Eritmaning pH ini toping (ikki xona aniqlikda).",
  kind="num", ans=round(ph_buf, 2), tol=0.011, unit="",
  hint="Kuchsiz kislota va uning tuzi aralashmasi: Genderson–Hasselbalx tenglamasi.",
  sol=["pH = pK<sub>a</sub> + lg([A<sup>−</sup>]/[HA]).",
       "pH = 4,76 + lg(0,050 / 0,10) = 4,76 − 0,30.",
       "pH = <b>%s</b>." % f"{ph_buf:.2f}".replace(".", ",")]),
 dict(t="Aromatiklik", lvl="O‘rta",
  q="Qaysi zarracha aromatik?",
  kind="choice", opts=["Siklopentadienil kationi C<sub>5</sub>H<sub>5</sub><sup>+</sup>","Siklopropenil kationi C<sub>3</sub>H<sub>3</sub><sup>+</sup>","Siklooktatetraen C<sub>8</sub>H<sub>8</sub>","Siklobutadien C<sub>4</sub>H<sub>4</sub>"], ans=1,
  hint="Tekis siklik tutash sistemada π-elektronlar soni 4n + 2 bo‘lishi kerak.",
  sol=["C<sub>5</sub>H<sub>5</sub><sup>+</sup>: 4 ta π-elektron, antiaromatik.",
       "C<sub>3</sub>H<sub>3</sub><sup>+</sup>: 2 ta π-elektron, n = 0 da 4n + 2 = 2. <b>Aromatik.</b>",
       "C<sub>8</sub>H<sub>8</sub> tekis emas (vanna shaklida), C<sub>4</sub>H<sub>4</sub> esa 4 ta π-elektron bilan antiaromatik."]),
 dict(t="SN2 va stereokimyo", lvl="Qiyin",
  q="Optik faol (S)-2-yodbutan Na<sup>131</sup>I eritmasida qoldirildi. Har bir almashinish SN2 bo‘yicha, inversiya bilan ketadi. Optik faollik yo‘qolish tezligi radioaktiv yod kirish tezligidan necha marta katta?",
  kind="num", ans=2, tol=0, unit="marta",
  hint="Bitta molekula S dan R ga aylansa, optik aylanish necha birlikka o‘zgaradi?",
  sol=["Har bir almashinish bitta S molekulani R ga aylantiradi.",
       "Bitta S yo‘qoladi va bitta R paydo bo‘ladi, ikkalasi ham aylanishni bir xil tomonga o‘zgartiradi.",
       "Demak, faollik almashinishdan <b>2 marta</b> tez yo‘qoladi (Hughes tajribasi)."]),
 dict(t="Kristall panjara", lvl="O‘rta",
  q="NaCl kubik yacheykasining qirrasi a = 564,0 pm, M(NaCl) = 58,44 g/mol, N<sub>A</sub> = 6,022·10<sup>23</sup> mol<sup>−1</sup>. NaCl zichligini g/sm<sup>3</sup> da toping.",
  kind="num", ans=round(rho_nacl, 3), tol=0.02, unit="g/sm³",
  hint="NaCl yacheykasi yoqlari markazlashgan kub (fcc). Yacheykada nechta NaCl birligi bor?",
  sol=["fcc yacheykada 4 ta Na<sup>+</sup> va 4 ta Cl<sup>−</sup>, ya’ni 4 ta NaCl.",
       "V = (564,0·10<sup>−10</sup> sm)<sup>3</sup> = 1,794·10<sup>−22</sup> sm<sup>3</sup>.",
       "ρ = 4·58,44 / (6,022·10<sup>23</sup> · 1,794·10<sup>−22</sup>) = <b>%s g/sm<sup>3</sup></b>." % f"{rho_nacl:.2f}".replace(".", ",")]),
 dict(t="Kinetika", lvl="Oson",
  q="<sup>32</sup>P ning yarim yemirilish davri 14,3 kun. 1,00 mg <sup>32</sup>P dan 57,2 kundan keyin necha mg qoladi?",
  kind="num", ans=round(p32_left, 4), tol=0.0006, unit="mg",
  hint="57,2 kun nechta yarim yemirilish davriga teng?",
  sol=["57,2 / 14,3 = 4 ta yarim yemirilish davri.",
       "Har davrda miqdor ikki marta kamayadi: 1,00 · (1/2)<sup>4</sup>.",
       "m = <b>0,0625 mg</b>."]),
 dict(t="18 elektron qoidasi", lvl="O‘rta",
  q="[Co(CO)<sub>x</sub>]<sup>−</sup> anioni 18 elektron qoidasiga bo‘ysunadi. x ni toping.",
  kind="num", ans=co_x, tol=0, unit="",
  hint="Kobalt 9-guruhda. Anion zaryadi metallga yana bitta elektron qo‘shadi, har bir CO 2 elektron beradi.",
  sol=["Co: 9 ta valent elektron, −1 zaryad bilan 10 ta.",
       "Har bir CO 2 elektron beradi: 10 + 2x = 18.",
       "x = <b>4</b>, ya’ni [Co(CO)<sub>4</sub>]<sup>−</sup>, tetraedrik anion."]),
 dict(t="Elektrokimyo", lvl="O‘rta",
  q="E°(Cu<sup>2+</sup>/Cu) = 0,34 V. [Cu<sup>2+</sup>] = 0,010 M bo‘lgan eritmaga botirilgan mis elektrod potensialini 25 °C da toping (V, ikki xona).",
  kind="num", ans=round(e_cu, 2), tol=0.006, unit="V",
  hint="Nernst tenglamasi: 25 °C da E = E° + (0,0592/n)·lg[Ox].",
  sol=["Cu<sup>2+</sup> + 2e<sup>−</sup> → Cu, n = 2.",
       "E = 0,34 + (0,0592/2)·lg(0,010) = 0,34 − 0,059.",
       "E = <b>%s V</b>." % f"{e_cu:.2f}".replace(".", ",")]),
 dict(t="Stereoizomeriya", lvl="O‘rta",
  q="2,3-dibrombutan nechta stereoizomer shaklida mavjud?",
  kind="num", ans=3, tol=0, unit="ta",
  hint="Ikkita stereomarkaz 2<sup>2</sup> = 4 ni beradi, lekin molekula simmetrik. Mezo-shakl bormi?",
  sol=["C2 va C3 stereomarkaz, maksimal 4 ta kombinatsiya: RR, SS, RS, SR.",
       "Molekula simmetrik bo‘lgani uchun RS va SR bitta mezo-birikma, u optik nofaol.",
       "Jami: (2R,3R), (2S,3S) va mezo, ya’ni <b>3 ta</b>."]),
 dict(t="Kristall maydon nazariyasi", lvl="Qiyin",
  q="[Fe(CN)<sub>6</sub>]<sup>3−</sup> ionida nechta juftlashmagan elektron bor?",
  kind="num", ans=1, tol=0, unit="ta",
  hint="Temirning oksidlanish darajasi va d-elektronlar soni qancha? CN<sup>−</sup> kuchli maydonli ligand.",
  sol=["Fe<sup>3+</sup>: d<sup>5</sup>.",
       "CN<sup>−</sup> kuchli maydon beradi, kompleks past spinli: t<sub>2g</sub><sup>5</sup> e<sub>g</sub><sup>0</sup>.",
       "t<sub>2g</sub> da 5 elektron: ikki juft va <b>1 ta</b> juftlashmagan elektron."]),
 dict(t="Kislota-asos muvozanati", lvl="O‘rta",
  q="0,10 M HF eritmasining pH ini toping. K<sub>a</sub>(HF) = 6,8·10<sup>−4</sup> (ikki xona aniqlikda).",
  kind="num", ans=round(ph_hf, 2), tol=0.011, unit="",
  hint="Dissotsilanish darajasi 5% dan katta chiqadi, shuning uchun soddalashtirish ishlamaydi: kvadrat tenglamani yeching.",
  sol=["x<sup>2</sup> / (0,10 − x) = 6,8·10<sup>−4</sup>.",
       "x<sup>2</sup> + 6,8·10<sup>−4</sup>x − 6,8·10<sup>−5</sup> = 0, bundan x = %s M." % f"{x:.2e}".replace(".", ",").replace("e-03", "·10<sup>−3</sup>"),
       "pH = −lg x = <b>%s</b>." % f"{ph_hf:.2f}".replace(".", ",")]),
 dict(t="Molekula shakli", lvl="Oson",
  q="XeF<sub>4</sub> molekulasining shakli qanday?",
  kind="choice", opts=["Tetraedr","Tekis kvadrat","Qaychisimon (see-saw)","Kvadrat piramida"], ans=1,
  hint="Xe atrofidagi elektron juftlarni sanang: bog‘lovchi va bo‘linmagan juftlar.",
  sol=["Xe: 8 valent elektron, 4 tasi F bilan bog‘da, 2 ta bo‘linmagan juft qoladi.",
       "6 ta elektron jufti oktaedr hosil qiladi, bo‘linmagan juftlar bir-biriga qarama-qarshi turadi.",
       "Atomlar bitta tekislikda qoladi: <b>tekis kvadrat</b>."]),
]

out = "/* Generated by tools/kunlik_build.py. Do not edit by hand. */\nwindow.KUNLIK={start:\"2026-11-15\",list:" + json.dumps(P, ensure_ascii=False) + "};\n"
open("/home/claude/uac-/kunlik-data.js", "w").write(out)
for i, p in enumerate(P): print(i, p["t"], p["ans"] if p["kind"] == "num" else p["opts"][p["ans"]])
