# Dunyo kimyosi yangiliklari: qanday yoziladi

Bu fayl `news-world.js` ni to‘ldiradigan har bir kishi (yoki haftalik avtomatik vazifa) uchun qoidalar.

## Qoidalar
1. Haftasiga 3–5 ta yangilik. Mavzu: yangi reaksiya yoki modda, Nobel va boshqa mukofotlar, xalqaro olimpiadalar (IChO, Mendeleyev, ARBIChO), o‘zbek kimyogarlari yutuqlari.
2. Har bir fakt shu seansda ochilgan sahifadan olinadi. Avval birlamchi manba (maqola DOI sahifasi, tashkilotning rasmiy sayti), keyin ikkinchi mustaqil manba bilan solishtiriladi. Ikkinchi manba topilmasa, yangilik qo‘shilmaydi.
3. Ismlar, sanalar va raqamlar manbadagidek yoziladi. Taxmin qilinmaydi.
4. Matn o‘zbek tilida, o‘z so‘zimiz bilan. Manba matni ko‘chirilmaydi, manba suratlari ishlatilmaydi.
5. Uzunligi: sarlavha 1 gap, `lead` 1–2 gap, `body` 2–4 qisqa xatboshi. Oxirgi xatboshida, iloji bo‘lsa, olimpiadachi uchun bog‘lanish (qaysi mavzuga tegishli).
6. `cover` — muqovadagi qisqa yozuv (formula, raqam yoki qisqartma), 8 belgigacha. `img` ixtiyoriy: faqat o‘zimiz chizgan rasm (`tools/covers.py` dagi kabi, haqiqiy geometriyadan chizilgan molekula), `assets/c/` ichida. Rasm bo‘lmasa, muqovada `cover` yozuvi ko‘rinadi.
7. `id` faqat lotin harflari, raqam va chiziqcha. `date` — voqea yoki maqola sanasi (YYYY-MM-DD).
8. Yangi yozuvlar ro‘yxat boshiga qo‘shiladi, 12 tadan ortig‘i oxiridan olib tashlanadi.

## Yozuv shakli
```js
{
  "id": "oksoboran",
  "date": "2026-10-27",
  "cat": "Noorganik kimyo",
  "cover": "B≡O",
  "title": "...",
  "lead": "...",
  "body": ["...", "..."],
  "src": [{"name": "Nature Chemistry, 2026", "url": "https://doi.org/..."}, {"name": "ScienceDaily", "url": "https://..."}]
}
```

## Tasdiqlash tartibi
Qoralama `news-draft` branchiga yoziladi va hech qachon to‘g‘ridan-to‘g‘ri `main` ga chiqarilmaydi. Daler ko‘rib, “ha” degandan keyingina `main` ga qo‘shiladi.
