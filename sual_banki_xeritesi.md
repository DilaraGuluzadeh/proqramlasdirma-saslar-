# Sual bankı → variant xəritəsi (müəllim üçündür)

Mənbə: `proqramlasdirmanin_esaslari_imtahan_suallari_v2.docx` — Proqramlaşdırmanın əsasları, 1-ci kurs, qrup 136a1. Bankda 20 nəzəri və 60 kod yazma sualı var.

Hər variantda 10 tapşırıq: **4 nəzəri + 6 praktiki**, hər biri 10 bal, cəmi 100 bal.

* **Nəzəri suallar** (Nəzəri Anlayış və Mövzu): 20 sualın hər biri dəqiq bir variantda işlənir; hər variantın 4 nəzəri sualı ən azı 3 fərqli kateqoriyadandır (bir kateqoriyadan ən çox 2 sual).
* **Kod tapşırıqları**: hər variantda 5 kateqoriyanın (A–E) hamısı + 1 əlavə tapşırıq var.
* Heç bir sual iki variantda təkrarlanmır. Bankda yan-yana olan və ya məzmunca oxşar tapşırıqlar (məs. C6 və E9, C5 və E10, C7 və E16, C10 və E12) eyni variantda deyil.
* Suallar variantlara bank sırası ilə paylanmayıb; hər variantda tapşırıqların sırası qarışdırılıb (eyni kateqoriyadan iki tapşırıq ardıcıl gəlmir).

Qiymətləndirmə: `0 / 10` — yalnız 0 və ya 10 bal; `0–10 (qismən)` — hər düzgün hissə üçün ayrıca bal. Yoxlama nəticəyə əsaslanır: funksiya cavabı qaytara və ya çap edə bilər, istənilən düzgün alqoritm qəbul olunur. *“swapcase olmadan”*, *“rekursiv”*, *“Bubble Sort ilə”*, *“üçüncü dəyişənsiz”*, *“while ilə”* kimi göstərişlər avtomatik yoxlanılmır — lazım olsa, kodu müəllim panelində özünüz baxın.

Qeyd: Word faylındakı E4 nümunəsində *'Salam Baku'* üçün samit sayı 4 yazılıb, düzgün cavab isə 5-dir (S, l, m, B, k) — tapşırıqda düzgün qiymət (4, 5) istifadə olunub. Eyni şəkildə C16-da 1–100 aralığı üçün cavab 735 yox, 679-dur (3 + 10 + … + 94, 14 ədəd) — tapşırıqda 679 istifadə olunub.


## Variant A  (kod: 3 qismən, 3 tapşırıq 0/10; nəzəri: 4 × 0/10)

| Tapşırıq | Növ | Bank nömrəsi | Kateqoriya | Mövzu | Qiymətləndirmə | Cavab / funksiya |
|---|---|---|---|---|---|---|
| T1 | Nəzəri | [B4] | Nəzəri — B. Şərt Operatorları və Budaqlanan Alqoritmlər | pass operatoru | 0 / 10 | c |
| T2 | Kod | [A15] | A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar | Selsidən Farenheytə çevirmə | 0 / 10 | `selsi_farenheyt()` |
| T3 | Nəzəri | [D3] | Nəzəri — D. Birölçülü və İkiölçülü Massivlər / Siyahılar | İkiölçülü massivlər (matrislər) | 0 / 10 | d |
| T4 | Kod | [A9] | A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar | Düzbucaqlının sahəsi və perimetri | 0–10 (qismən) | `duzbucaqli()` |
| T5 | Kod | [D10] | D. Birölçülü və İkiölçülü Massivlər / Siyahılar | X ədədinin təkrar sayı və ilk indeksi | 0–10 (qismən) | `tekrar_ve_indeks()` |
| T6 | Nəzəri | [A2] | Nəzəri — A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar | Stack və Heap yaddaş sahələri | 0 / 10 | c |
| T7 | Kod | [C10] | C. Dövr Operatorları və İterasiya (For, While) | ƏBOB və ƏKOB | 0–10 (qismən) | `ebob_ekob()` |
| T8 | Nəzəri | [D1] | Nəzəri — D. Birölçülü və İkiölçülü Massivlər / Siyahılar | İndeksləmə, mənfi indekslər və dilimləmə | 0 / 10 | b |
| T9 | Kod | [B15] | B. Şərt Operatorları və Budaqlanan Alqoritmlər | Həm 3-ə, həm də 5-ə bölünmə | 0 / 10 | `uc_ve_bese_bolunur()` |
| T10 | Kod | [E10] | E. Mətn Sətirləri (Strings) və Funksiyalar | Rekursiv faktorial | 0 / 10 | `factorial_recursive()` |

## Variant B  (kod: 5 qismən, 1 tapşırıq 0/10; nəzəri: 4 × 0/10)

| Tapşırıq | Növ | Bank nömrəsi | Kateqoriya | Mövzu | Qiymətləndirmə | Cavab / funksiya |
|---|---|---|---|---|---|---|
| T1 | Kod | [A14] | A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar | İki nöqtə arasındakı məsafə | 0 / 10 | `mesafe()` |
| T2 | Kod | [E4] | E. Mətn Sətirləri (Strings) və Funksiyalar | Sait və samit hərflərin sayı | 0–10 (qismən) | `sait_samit()` |
| T3 | Nəzəri | [B1] | Nəzəri — B. Şərt Operatorları və Budaqlanan Alqoritmlər | if-if və if-elif icra fərqi | 0 / 10 | d |
| T4 | Kod | [C14] | C. Dövr Operatorları və İterasiya (For, While) | 0 daxil edilənə qədər cəm və ədədi orta | 0–10 (qismən) | `cem_orta()` |
| T5 | Nəzəri | [A4] | Nəzəri — A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar | Əsas məlumat tipləri, type() və tip çevrilməsi | 0 / 10 | c |
| T6 | Kod | [B11] | B. Şərt Operatorları və Budaqlanan Alqoritmlər | Nöqtənin koordinat rübü | 0–10 (qismən) | `rub()` |
| T7 | Nəzəri | [C1] | Nəzəri — C. Dövr Operatorları və İterasiya (For, While) | for və while dövrləri, sonsuz dövr | 0 / 10 | c |
| T8 | Kod | [D14] | D. Birölçülü və İkiölçülü Massivlər / Siyahılar | Matrisin transponirə edilməsi | 0–10 (qismən) | `transpoze()` |
| T9 | Kod | [E6] | E. Mətn Sətirləri (Strings) və Funksiyalar | Hərflərin registrini dəyişmək | 0–10 (qismən) | `registr_deyis()` |
| T10 | Nəzəri | [A6] | Nəzəri — A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar | Məntiqi və müqayisə operatorları | 0 / 10 | b |

## Variant C  (kod: 4 qismən, 2 tapşırıq 0/10; nəzəri: 4 × 0/10)

| Tapşırıq | Növ | Bank nömrəsi | Kateqoriya | Mövzu | Qiymətləndirmə | Cavab / funksiya |
|---|---|---|---|---|---|---|
| T1 | Nəzəri | [C3] | Nəzəri — C. Dövr Operatorları və İterasiya (For, While) | range(start, stop, step) | 0 / 10 | a |
| T2 | Kod | [B6] | B. Şərt Operatorları və Budaqlanan Alqoritmlər | Müsbət, mənfi və ya sıfır | 0–10 (qismən) | `isare()` |
| T3 | Kod | [E11] | E. Mətn Sətirləri (Strings) və Funksiyalar | Siyahının orta qiyməti | 0–10 (qismən) | `calculate_average()` |
| T4 | Nəzəri | [B2] | Nəzəri — B. Şərt Operatorları və Budaqlanan Alqoritmlər | İç-içə if və girintilər | 0 / 10 | c |
| T5 | Kod | [A11] | A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar | 3 rəqəmli ədədin rəqəmlərinin cəmi | 0–10 (qismən) | `reqemler_cemi()` |
| T6 | Kod | [C15] | C. Dövr Operatorları və İterasiya (For, While) | Ədədin bölənləri və onların sayı | 0–10 (qismən) | `bolenler()` |
| T7 | Nəzəri | [A1] | Nəzəri — A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar | Yüksək və aşağı səviyyəli dillər; kompilyator və interpretator | 0 / 10 | a |
| T8 | Kod | [D12] | D. Birölçülü və İkiölçülü Massivlər / Siyahılar | Baş diaqonalın cəmi | 0 / 10 | `bas_diaqonal_cemi()` |
| T9 | Nəzəri | [E1] | Nəzəri — E. Mətn Sətirləri (Strings) və Funksiyalar | Sətirlərin dəyişməzliyi və sətir metodları | 0 / 10 | a |
| T10 | Kod | [B12] | B. Şərt Operatorları və Budaqlanan Alqoritmlər | 3 rəqəmli polindrom ədəd | 0 / 10 | `polindrom_eded()` |

## Variant D  (kod: 3 qismən, 3 tapşırıq 0/10; nəzəri: 4 × 0/10)

| Tapşırıq | Növ | Bank nömrəsi | Kateqoriya | Mövzu | Qiymətləndirmə | Cavab / funksiya |
|---|---|---|---|---|---|---|
| T1 | Nəzəri | [C2] | Nəzəri — C. Dövr Operatorları və İterasiya (For, While) | break, continue və dövrün else bloku | 0 / 10 | a |
| T2 | Kod | [D13] | D. Birölçülü və İkiölçülü Massivlər / Siyahılar | Köməkçi diaqonalın maksimumu | 0–10 (qismən) | `komekci_diaqonal_max()` |
| T3 | Nəzəri | [A3] | Nəzəri — A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar | Dinamik tipləşdirmə və girintilər | 0 / 10 | b |
| T4 | Kod | [E5] | E. Mətn Sətirləri (Strings) və Funksiyalar | Polindrom söz | 0 / 10 | `polindrom_soz()` |
| T5 | Nəzəri | [A7] | Nəzəri — A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar | Truthy və falsy dəyərlər | 0 / 10 | a |
| T6 | Kod | [C4] | C. Dövr Operatorları və İterasiya (For, While) | 1-dən N-ə qədər ədədlərin cəmi | 0 / 10 | `cem_1_n()` |
| T7 | Nəzəri | [D2] | Nəzəri — D. Birölçülü və İkiölçülü Massivlər / Siyahılar | Siyahı metodları (append, insert, remove, pop) | 0 / 10 | d |
| T8 | Kod | [A13] | A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar | İki dəyişənin qiymətlərinin yerini dəyişmək | 0 / 10 | `yer_deyis()` |
| T9 | Kod | [B8] | B. Şərt Operatorları və Budaqlanan Alqoritmlər | Bala görə qiymət hərfi | 0–10 (qismən) | `qiymet_herfi()` |
| T10 | Kod | [C8] | C. Dövr Operatorları və İterasiya (For, While) | Rəqəmlərin sayı və cəmi (while ilə) | 0–10 (qismən) | `reqem_say_cem()` |

## Variant E  (kod: 5 qismən, 1 tapşırıq 0/10; nəzəri: 4 × 0/10)

| Tapşırıq | Növ | Bank nömrəsi | Kateqoriya | Mövzu | Qiymətləndirmə | Cavab / funksiya |
|---|---|---|---|---|---|---|
| T1 | Kod | [A12] | A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar | Saniyəni saat, dəqiqə və saniyəyə çevirmək | 0–10 (qismən) | `saniye_cevir()` |
| T2 | Kod | [E15] | E. Mətn Sətirləri (Strings) və Funksiyalar | Cüt ədədləri süzgəcdən keçirmək: get_evens(lst) | 0–10 (qismən) | `get_evens()` |
| T3 | Nəzəri | [A5] | Nəzəri — A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar | Riyazi operatorlar və icra prioriteti | 0 / 10 | a |
| T4 | Kod | [D11] | D. Birölçülü və İkiölçülü Massivlər / Siyahılar | Matrisin hər sətrinin cəmi | 0–10 (qismən) | `setir_cemleri()` |
| T5 | Nəzəri | [B3] | Nəzəri — B. Şərt Operatorları və Budaqlanan Alqoritmlər | Qısa qapanma qiymətləndirməsi (Short-Circuit) | 0 / 10 | a |
| T6 | Kod | [C16] | C. Dövr Operatorları və İterasiya (For, While) | 7-yə bölündükdə qalığı 3 olan ədədlərin cəmi | 0–10 (qismən) | `qaliq_cemi()` |
| T7 | Kod | [D15] | D. Birölçülü və İkiölçülü Massivlər / Siyahılar | Tək ədədləri 0 ilə əvəz etmək | 0 / 10 | `tekleri_sifirla()` |
| T8 | Nəzəri | [E2] | Nəzəri — E. Mətn Sətirləri (Strings) və Funksiyalar | Funksiyalar, return və lokal / qlobal dəyişənlər | 0 / 10 | c |
| T9 | Kod | [B9] | B. Şərt Operatorları və Budaqlanan Alqoritmlər | Üçbucaq əmələ gəlirmi? | 0–10 (qismən) | `ucbucaqdir()` |
| T10 | Nəzəri | [A8] | Nəzəri — A. Əsas Anlayışlar, Yaddaş, Tiplər və Operatorlar | Şərt operatorunun üçlü forması (Ternary) | 0 / 10 | d |

## Ehtiyat kod tapşırıqları (heç bir variantda istifadə olunmayıb)

Təkrar (ehtiyat) imtahan üçün: [A10] Dairənin sahəsi və çevrənin uzunluğu, [A16] 4 rəqəmli ədədin ilk və son rəqəmi, [B5] Cüt və ya tək ədəd, [B7] Üç ədədin ən böyüyü və ən kiçiyi, [B10] Uzun il (Leap Year), [B13] 4 ədəd arasında mənfilərin sayı, [B14] Sadə kalkulyator, [B16] Ayın nömrəsinə görə fəsil, [C5] N ədədinin faktorialı (dövr ilə), [C6] Sadə və ya mürəkkəb ədəd, [C7] Fibonacci ardıcıllığının ilk N həddi, [C9] Ədədin tərsi, [C11] Armstrong ədədləri, [C12] N-ə qədər bütün sadə ədədlər, [C13] Ulduzlu üçbucaq (iç-içə dövrlər), [D4] Ən böyük və ən kiçik element və onların indeksləri, [D5] Cüt indekslərdəki elementlərin cəmi, [D6] Müsbət ədədlərin ədədi ortası, [D7] Bubble Sort ilə çeşidləmə, [D8] Təkrarlanan elementləri silmək, [D9] Siyahını K mövqe sağa dövri sürüşdürmək, [D16] İki siyahının kəsişməsi, [E3] Cümlədəki sözlərin sayı, [E7] Simvolu başqa simvolla əvəz etmək, [E8] Mətni tərsinə çevirmək, [E9] Sadə ədəd funksiyası is_prime(n), [E12] Avklid alqoritmi ilə ƏBOB: gcd(a, b), [E13] Cümlədə ən uzun söz, [E14] Simvolların tezlik lüğəti, [E16] Rekursiv Fibonacci: fibonacci(n).
