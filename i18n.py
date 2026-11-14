"""Güvenli Okul arayüzü için Türkçe/İngilizce yerelleştirme katmanı.

Veritabanındaki sabit kodlar ve kayıtlar Türkçe/orijinal biçimde tutulur;
çeviri yalnızca kullanıcıya gösterilen arayüz katmanında uygulanır.
Resmî kurum/okul adları ve proje adı çevrilmez.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any
import re

TR = "Türkçe"
EN = "English"

# Tam cümleler önce, kısa terimler sonra uygulanır. Serbest kullanıcı metinleri
# translate() ile otomatik çevrilmez; yalnızca bilinen arayüz ifadeleri eşlenir.
CATALOG: dict[str, str] = {
    # Navigasyon ve genel
    "Genel bakış": "Overview", "Yeni bildirim": "New report", "Bildirim sorgula": "Track a report",
    "Destek rehberi": "Support guide", "Yönetici girişi": "Administrator sign-in",
    "Bildirim inceleme": "Report review", "İstatistikler": "Statistics", "Trend ve ortam": "Trends and settings",
    "Gizlilik ve KVKK": "Privacy and data protection", "Araştırma ve test": "Research and testing",
    "Güvenli kullanım": "Safe use", "KULLANICI": "USER", "YÖNETİM": "ADMINISTRATION",
    "KURUMSAL": "INFORMATION", "OTURUM": "SESSION", "Oturumu kapat": "Sign out",
    "Ziyaretçi (giriş yapılmadı)": "Visitor (not signed in)", "Yönetici:": "Administrator:",
    "Dil / Language": "Language / Dil", "Türkçe": "Türkçe", "English": "English",
    "Güvenli Okul · Bildirim ve takip": "Güvenli Okul · Reporting and follow-up",
    "Güvenli Okul · Bildirim ve takip sistemi · Kural tabanlı sinyaller karar değildir.":
        "Güvenli Okul · Reporting and follow-up platform · Rule-based signals are not decisions.",
    "Bağımsız çalışma alanı": "Independent demonstration environment",
    "Gerçek okul sistemine bağlı değildir. Gerçek kişisel verileri girmeyin.":
        "This platform is not connected to a live school system. Do not enter real personal data.",
    "Bağımsız çalışma alanı · Gerçek okul sistemine bağlı değildir. Gerçek kişisel verileri girmeyin.":
        "Independent demonstration environment · Not connected to a live school system. Do not enter real personal data.",
    "DEMO": "DEMO", "PİLOT": "PILOT", "Yönetici": "Administrator", "Ziyaretçi": "Visitor",
    "Sürüm": "Version", "Algılayıcı": "Detector",

    # Genel bakış
    "Güvenli bir okul, herkesin hakkı.": "A safe school is everyone's right.",
    "Zorbalığı kimliğini vermeden bildir, gizli kodunla durumu takip et.":
        "Report bullying without identifying yourself and track its status using your private code.",
    "Anonim": "Anonymous", "Gizli takip kodu": "Private tracking code", "İnsan incelemesi": "Human review",
    "Yönetici özeti": "Administrator dashboard", "Açık kayıt": "Open reports", "Toplam kayıt": "Total reports",
    "Nasıl kullanılır?": "How it works", "Rehberlik bilgi bankası": "Guidance resource centre",
    "Güvenlik ilkeleri": "Security principles", "İnceleme kuyruğunu aç": "Open review queue",
    "Destek rehberini aç": "Open support guide", "Yeni bildirim": "New report",
    "Bildirim sorgula": "Track a report", "Güvenli kullanım": "Safe use",
    "Gizlilik": "Privacy", "Sinyal, karar değil": "A signal is not a decision",
    "Hesap verebilirlik": "Accountability", "1 · Bildir": "1 · Report",
    "2 · Takip et": "2 · Track", "3 · İnsan inceler": "3 · Human review",
    "Formu doldur. Ad ve sınıf istenmez; sana gizli bir kod verilir.":
        "Complete the form. Your name and class are not requested; you will receive a private tracking code.",
    "Kodunla durumu gör, aynı gün ek bilgi ekle.": "Check the status using your code and add further information on the same day.",
    "Yetkili kişiler kaydı inceler. Kararı makine vermez.":
        "Authorised staff review the report. The system does not make decisions.",
    "Telefon, T.C. no, e-posta ve IBAN otomatik gizlenir.":
        "Phone numbers, national ID numbers, email addresses and IBANs are automatically masked.",

    # Yetkilendirme
    "Yönetici erişimi gerekli": "Administrator access required",
    "Bu bölümü görüntülemek için yönetici oturumu açın.": "Sign in as an administrator to view this section.",
    "Yönetici girişine git": "Go to administrator sign-in", "Yönetici girişi": "Administrator sign-in",
    "Bildirim inceleme alanına yalnızca yetkili kullanıcılar erişebilir.":
        "Only authorised users can access the report review area.",
    "Yönetici oturumu açık.": "Administrator session is active.",
    "Bildirim incelemeye git": "Go to report review", "Kullanıcı adı": "Username", "Parola": "Password",
    "Giriş yap": "Sign in", "Kullanıcı adı veya parola yanlış.": "The username or password is incorrect.",
    "Yönetici bilgileri ayarlanmamış.": "Administrator credentials have not been configured.",
    "Çok fazla hatalı deneme. Lütfen": "Too many failed attempts. Please wait",
    "Sistem genelinde çok fazla hatalı giriş denemesi var. Lütfen bir süre sonra tekrar deneyin.":
        "There have been too many failed sign-in attempts across the system. Please try again later.",
    "Hareketsizlik nedeniyle yönetici oturumu kapatıldı.": "The administrator session was signed out due to inactivity.",
    "Oturum kapatıldı": "Session signed out", "Oturum zaman aşımı": "Session timed out",

    # Bildirim formu / takip
    "BİLDİRİM": "REPORT", "Kimliğini vermeden bildir. Ad, sınıf veya telefon istenmez.":
        "Submit a report without identifying yourself. Your name, class and phone number are not requested.",
    "Hazırlanıyor…": "Preparing…", "Günde bir bildirim hakkın var.": "You can submit one report per day.",
    "Ne oldu?": "What happened?", "Nerede oldu?": "Where did it happen?", "Ne zaman oldu?": "When did it happen?",
    "Bu olay kaç kez yaşandı?": "How often has this happened?", "Olayı kendi cümlelerinle anlat": "Describe what happened in your own words",
    "Ne oldu, nerede ve ne zaman oldu? Ad, telefon gibi bilgileri yazma.":
        "Describe what happened, where and when. Do not include names, phone numbers or other identifying details.",
    "Gerçek kişisel bilgi içermeyen örnek bir açıklama girdiğimi onaylıyorum.":
        "I confirm that I have entered a sample description that contains no real personal information.",
    "Bilgilendirme metnini okudum; verdiğim bilgilerin bildirim sürecinde işlenmesini kabul ediyorum.":
        "I have read the privacy notice and agree to the processing of the information I provide for the reporting process.",
    "Bildirimi gönder": "Submit report", "Lütfen olayı anlat.": "Please describe what happened.",
    "Açıklama yalnızca boşluk veya noktalama işaretlerinden oluşamaz. Kısaca ne olduğunu yaz.":
        "The description cannot consist only of spaces or punctuation. Please briefly describe what happened.",
    "Lütfen onay kutusunu işaretle.": "Please tick the confirmation box.",
    "Kısa sürede çok fazla bildirim gönderildi. Lütfen yaklaşık": "Too many reports have been submitted in a short period. Please try again in approximately",
    "saniye sonra tekrar dene.": "seconds.", "Bildirimin kaydedildi. Teşekkür ederiz.": "Your report has been submitted. Thank you.",
    "Gizli takip kodun.": "Your private tracking code.",
    "Durumu ve ek bilgi eklemeyi bu kodla yaparsın.": "Use this code to check the status and add further information.",
    "Not al ya da ekran görüntüsü al; kod kaybolursa yeniden oluşturulamaz:":
        "Save this code or take a screenshot. It cannot be recovered if lost:",
    "Açıklamandaki şu bilgiler gizlilik için otomatik gizlendi:":
        "The following information in your description was automatically masked for privacy:",
    "Durumu sorgula": "Check status", "Kodumu not aldım": "I have saved my code",
    "Bu takip kodu yalnızca uygulamadaki kaydı tanımlar. Rehberlikle mesajlaşma yoktur; yalnızca bildirimin durumunu görürsün.":
        "This tracking code identifies only the report in this platform. It does not provide messaging with the guidance service; it only lets you view the report status.",
    "Herhangi bir kuruma otomatik bildirim gönderilmez.": "No automatic notification is sent to any institution.",
    "TAKİP": "TRACKING", "Takip koduyla durumu gör, aynı gün ek bilgi ekle. Mesajlaşma yoktur.":
        "Check the status using your tracking code and add further information on the same day. Messaging is not available.",
    "Gizli takip kodu": "Private tracking code", "GO-XXXXXXXXXX": "GO-XXXXXXXXXX",
    "Durumu göster": "Show status", "Bu kodla eşleşen bir kayıt bulunamadı. Kodu kontrol edip tekrar dene.":
        "No report was found for this code. Check the code and try again.",
    "Ek bilgi ekle": "Add further information", "Ek bilgi yalnızca anonim bildirimlerde, bildirimin yapıldığı gün ve bildirim sonuçlanmadan önce eklenebilir.":
        "Further information can only be added to anonymous reports on the day they were submitted and before the report is closed.",
    "Eklenen ek bilgi:": "Additional entries:", "Ek bilgiler aynı bildirimin altına eklenir.":
        "Additional information is attached to the same report.", "Bugün için ek bilgi sınırına ulaştın.":
        "You have reached today's limit for additional information.",
    "Yeni ek bilgi için yaklaşık": "Please wait approximately", "beklemen gerekiyor.": "before adding more information.",
    "Eklemek istediğin bilgi": "Additional information", "Ek bilgiyi gönder": "Submit additional information",
    "Ek bilgi kaydedilemedi. Lütfen daha sonra tekrar dene.": "Additional information could not be saved. Please try again later.",
    "Günlük bildirim hakkınız dolmuştur. Yarın yeniden bildirim yapabilirsin. Bugünkü bildirimine takip koduyla ek bilgi ekleyebilirsin.":
        "You have reached the daily report limit. You can submit another report tomorrow. You may add information to today's report using your tracking code.",
    "Bildirimime ek bilgi ekle": "Add information to my report", "Lütfen yaklaşık": "Please wait approximately",

    # Kayıt ve inceleme
    "Oluşturulma": "Created", "Son güncelleme": "Last updated", "Bildirim ayrıntıları": "Report details",
    "Olay türü": "Incident type", "Ortam": "Setting", "Yaklaşık zaman": "Approximate time",
    "Tekrarlanma": "Frequency", "Açıklama": "Description", "Bildirimde belirtilen kişi bilgileri": "Personal details mentioned in the report",
    "Otomatik sinyal ve değerlendirme notu": "Automated signals and assessment notes",
    "Öncelik sinyali:": "Priority signal:", "Kategoriler:": "Categories:", "Eşleşen ifadeler:": "Matched phrases:",
    "Belirgin eşleşme yok": "No notable matches", "Açıklamada otomatik maskelenen bilgi türleri:":
        "Types of information automatically masked in the description:",
    "Açıklama kalitesi kontrolü:": "Description quality check:",
    "Metin çok kısa, yeterince açıklayıcı olmayabilir veya tekrar eden karakterler içeriyor. ":
        "The text may be too short, insufficiently descriptive, or contain repeated characters. ",
    "Bu bir spam/asılsız bildirim kanıtı değildir; otomatik silinmez, yetkili kişi bağlamı kontrol etmelidir.":
        "This is not evidence of spam or a false report. The report is not deleted automatically; an authorised reviewer should assess the context.",
    "Metin temel uzunluk kontrolünü geçti. Bu, bildirimin doğru olduğu anlamına gelmez.":
        "The text passed the basic length check. This does not mean that the report is accurate.",
    "Algılayıcı sürümü:": "Detector version:", "Bu sürüm gerçek bir yapay zekâ modeli değil, kural tabanlı sinyal ve basit metin kalite kontrolü kullanır.":
        "This version is not an AI model; it uses rule-based signals and a basic text-quality check.",
    "İnceleme ve yönlendirme": "Review and assignment", "Durum": "Status", "Sorumlu birim": "Assigned team",
    "Değişiklikleri kaydet": "Save changes", "İnceleme notları": "Review notes", "Yeni not": "New note",
    "Notu kaydet": "Save note", "İşlem geçmişi": "Activity history", "Henüz not eklenmemiş.": "No notes have been added yet.",
    "Henüz işlem geçmişi yok.": "There is no activity history yet.", "Henüz kayıt yok. Yeni bir bildirim oluşturulduğunda burada görünür.":
        "There are no reports yet. New reports will appear here when submitted.",
    "Kayıt kuyruğu": "Report queue", "Kayıt ara": "Search reports", "Takip kodu, olay türü, ortam veya birim":
        "Tracking code, incident type, setting or team", "İnceleme durumu": "Review status", "Öncelik sinyali": "Priority signal",
    "Bildirim türü": "Report type", "Sıralama": "Sort by", "Tüm durumlar": "All statuses", "Tüm birimler": "All teams",
    "Tümü": "All", "Öncelik (yüksekten)": "Priority (highest first)", "En yeni önce": "Newest first",
    "En eski önce": "Oldest first", "Kayıt seç": "Select a report", "Seçili kayıt": "Selected report",
    "Tarih aralığı": "Date range", "Başlangıç tarihi": "Start date", "Bitiş tarihi": "End date",
    "Bu filtrelerle eşleşen kayıt bulunamadı.": "No reports match these filters.", "Kayıt": "Report",
    "kayıt": "reports", "GECİKMİŞ": "OVERDUE", "Gecikmiş": "Overdue", "Açık": "Open",
    "İnceleme kuyruğunu aç": "Open review queue", "Anonim": "Anonymous", "Kimlik bilgisi belirtilmiş": "Identifying details provided",
    "Kayıtlar": "Reports", "Denetim kaydı": "Audit log", "Dışa aktarım ve saklama": "Export and retention",
    "Girişler, başarısız denemeler, dışa aktarımlar ve silme işlemleri burada izlenir.":
        "Sign-ins, failed attempts, exports and deletion actions are tracked here.", "Henüz denetim kaydı yok.": "There are no audit records yet.",
    "Dışa aktarım": "Export", "Kimlik bilgilerini (ad, soyad, sınıf) dahil et": "Include identifying details (first name, last name, class)",
    "CSV indir": "Download CSV", "Saklama süresi": "Retention period", "Saklama süresi (gün)": "Retention period (days)",
    "Süresi dolan, sonuçlandırılmış kayıtlar notları ve geçmişiyle birlikte kalıcı olarak silinir.":
        "Expired, closed reports are permanently deleted together with their notes and history.",
    "Silmenin geri alınamayacağını anlıyorum": "I understand that deletion cannot be undone",
    "Süresi dolan kayıtları sil": "Delete expired reports", "Kayıtlar silindi.": "Reports have been deleted.",
    "İnceleme bilgileri kaydedildi.": "Review details have been saved.", "Değişiklik yapılmadı; bilgiler zaten güncel.": "No changes were made; the information is already up to date.",
    "Değişiklik kaydedilemedi. Lütfen yeniden deneyin.": "Changes could not be saved. Please try again.",
    "Boş not eklenemez.": "A note cannot be empty.", "Not kaydedilemedi.": "The note could not be saved.",
    "Not kaydedildi.": "The note has been saved.", "Açıklama": "Description", "Anonim gönderenin ek bilgileri": "Additional information from the anonymous reporter",

    # Günlük yönetici paneli ve tavsiyeler
    "Günlük Durum Özeti": "Daily Status Summary", "Bugünkü yeni bildirim": "New reports today",
    "Aktif yüksek/acil": "Active high/urgent", "İnceleme bekleyen": "Awaiting review",
    "Acil öncelikli bildirim": "Urgent-priority report", "Yüksek öncelikli bildirim": "High-priority report",
    "Rehberlik için önerilen adımlar": "Suggested guidance steps",
    "Genel kontrol listesidir; okul psikolojik danışmanı ve kurum protokolü tarafından uyarlanmalıdır.":
        "This is a general checklist and should be adapted by the school counsellor and the institution's procedures.",
    "Ekran görüntülerini ve ilgili dijital kayıtları, öğrencinin güvenliğini gözeterek koruyun; içeriği yaymayın.":
        "Preserve screenshots and relevant digital records while safeguarding the student's privacy; do not redistribute the content.",
    "Öğrenciyle güvenli ve gizli bir ortamda bireysel görüşme yapın.":
        "Meet with the student individually in a safe and confidential setting.",
    "Olayın tekrar edip etmediğini ve öğrencinin kendini güvende hissedip hissetmediğini değerlendirin.":
        "Assess whether the incident is recurring and whether the student feels safe.",
    "Gerekli görülürse okulun ilgili koruma ve yönlendirme prosedürlerini izleyin.":
        "If needed, follow the school's relevant safeguarding and referral procedures.",

    # Dashboard / statistics
    "Yüksek veya acil sinyal (açık)": "High or urgent signals (open)", "saati aşan bekleyen": "Awaiting review for over hours",
    "Toplam kayıt": "Total reports", "İstatistikler": "Statistics", "Grafikler yalnızca bu uygulamada kayıtlı bilgileri özetler; okul geneline ilişkin sonuç göstermez.":
        "Charts summarise information recorded in this platform only; they do not represent findings about the whole school.",
    "Henüz kayıt yok. Yeni kayıtlar eklendikçe istatistikler burada görüntülenir.":
        "There are no reports yet. Statistics will appear here as reports are added.",
    "Kayıt sayısı çok az; yüzdeler ve karşılaştırmalar yanıltıcı olabilir, yorum yapmayın.":
        "The number of reports is very small; percentages and comparisons may be misleading and should not be interpreted.",
    "Durum dağılımı": "Status distribution", "Öncelik sinyali dağılımı": "Priority-signal distribution",
    "Olay türü dağılımı": "Incident-type distribution", "Son 30 gün: günlük bildirim": "Daily reports: last 30 days",
    "Süreler kayıt oluşturma ile ilk durum değişikliği / 'Sonuçlandırıldı' arasındaki farktır.":
        "Durations are measured from report creation to the first status change or closure.",
    "Yeni anonim kayıtlar dakika ve saniye hassasiyetinde kaydedilir; eski yuvarlanmış kayıtların geçmiş zamanı geriye dönük kesinleştirilemez.":
        "New anonymous reports are recorded to the minute and second; the original time of older rounded records cannot be reconstructed retrospectively.",
    "Bu dönemde kayıt yok.": "There are no reports for this period.", "Kayıt sayısı": "Number of reports",

    # Destek rehberi
    "DESTEK": "SUPPORT", "Destek rehberi": "Support guide",
    "Zorbalıkla baş etme yolları ve kime nasıl ulaşabileceğin. Bu içerik bilgilendirme amaçlıdır.":
        "Ways to respond to bullying and how to seek help. This content is provided for information only.",
    "Öğrenciler": "Students", "Tanık olanlar": "Witnesses", "Siber zorbalık": "Cyberbullying",
    "Veliler": "Parents and carers", "Öğretmenler": "Teachers", "Bildirimden sonra ne olur?": "What happens after a report?",
    "Zorbalık nedir, ne değildir?": "What is bullying and what is not?", "Yaşıyorsan ne yapabilirsin?": "What can you do if this is happening to you?",
    "Kendine zarar verme düşüncen varsa": "If you are having thoughts of harming yourself",
    "Gördüysen sessiz kalma": "If you witness bullying, do not stay silent",
    "İnternette aşağılanıyor ya da tehdit ediliyorsan": "If you are being humiliated or threatened online",
    "Çocuğunuz zorbalığa uğruyor olabilir": "Your child may be experiencing bullying",
    "Çocuğunuzun zorbalık yaptığı söyleniyorsa": "If you are told that your child has bullied someone",
    "Bildirim geldiğinde": "When a report is received", "Rehberlik içerikleri taslaktır; okul psikolojik danışmanı tarafından onaylanmalıdır.":
        "The guidance content is a draft and must be reviewed by the school's counsellor before use.",
    "Acil bir tehlike varsa beklemeyin:": "If there is immediate danger, do not wait:",

    # Trend and analytics
    "ANALİTİK": "ANALYTICS", "Trend ve ortam analizi": "Trends and setting analysis",
    "Bildirimlerin saat, gün, mekân ve türlere göre dağılımı. Yalnızca bu uygulamadaki kayıtları özetler.":
        "Distribution of reports by time, day, setting and type. This summarises records in this platform only.",
    "Dönem": "Period", "Son": "Last", "gün": "days", "Küçük hücre eşiği (k)": "Small-cell threshold (k)",
    "Çapraz tabloda sayısı bu değerden küçük hücreler kimliksizleştirme için gizlenir.":
        "Cells with counts below this value are suppressed in the cross-tabulation to reduce identification risk.",
    "Ne zaman bildiriliyor?": "When are reports submitted?", "Haftalık eğilim": "Weekly trend",
    "Saate göre (bildirimin yapıldığı saat)": "By hour (time the report was submitted)",
    "Haftanın gününe göre": "By day of the week", "Hangi ortamda, hangi tür?": "Which types are reported in which settings?",
    "Ortama göre": "By setting", "Olay türüne göre": "By incident type", "Ortam haritası (ısı tablosu)": "Setting map (heatmap)",
    "Bildirim sayısındaki artış, olayların arttığını değil bildirme isteğinin arttığını da gösterebilir; ayrım için ayrı bir ölçüm (ör. anket) gerekir. Saat, olayın değil bildirimin saatidir; anonim kayıtlarda zaman saate yuvarlanır.":
        "An increase in reports may reflect a greater willingness to report rather than an increase in incidents; a separate measure (such as a survey) is needed to distinguish these. The time shown is the submission time, not the time of the incident.",
    "yalnızca": "only", "kayıt var; yüzdeler ve eğilimler yanıltıcı olabilir, yorum yapmayın.":
        "reports are available; percentages and trends may be misleading and should not be interpreted.",

    # Privacy, consent, research and app limits
    "GİZLİLİK": "PRIVACY", "Gizlilik ve KVKK paneli": "Privacy and data protection panel",
    "Hangi veri neden toplanıyor, ne kadar saklanıyor ve nasıl siliniyor. Metinler taslaktır.":
        "What data is collected and why, how long it is retained, and how it is deleted. The texts are drafts.",
    "Aydınlatma metni": "Privacy notice", "Veri envanteri": "Data inventory", "Saklama ve imha": "Retention and deletion",
    "Onam akışı (simülasyon)": "Consent flow (simulation)",
    "Köşeli parantezli alanlar doldurulmadan ve hukuk danışmanı onaylamadan yayımlanmamalıdır.":
        "Do not publish this notice until all bracketed fields have been completed and it has been reviewed by legal counsel.",
    "Veri": "Data", "Amaç": "Purpose", "Ne zaman": "When", "Saklama": "Retention", "Not": "Note",
    "Veri minimizasyonu (sistemde uygulananlar)": "Data minimisation (implemented in the platform)",
    "Açık riskler (raporda belirtilmeli)": "Open risks (to be disclosed in the report)",
    "Otomatik/elle imha kuralları": "Automatic and manual deletion rules", "Önizleme: saklama süresi (gün)": "Preview: retention period (days)",
    "günden eski sonuçlanmış kayıt (silinecek)": "closed reports older than days (to be deleted)",
    "Canlı silinecek kayıt sayısı yalnızca yönetici oturumunda görünür.":
        "The live count of reports eligible for deletion is visible only to administrators.",
    "SİMÜLASYON: Bu akış gerçek onam toplamaz, hiçbir veri kaydetmez ve kimseyle iletişime geçmez. Araştırmada onam, okulun resmî kanallarıyla yazılı olarak alınmalıdır.":
        "SIMULATION: This flow does not collect real consent, save any data or contact anyone. For research, consent must be obtained in writing through the school's official channels.",
    "Katılımcının yaş grubu": "Participant age group", "18 yaşından küçük": "Under 18", "18 yaş ve üzeri": "18 or over",
    "18 yaşından küçüklerde gönüllü katılımın yanında veli/yasal temsilcinin bilgilendirilmesi ve izni gerekir.":
        "For participants under 18, a parent or legal guardian must be informed and provide permission in addition to the participant's voluntary agreement.",
    "İleri": "Continue", "Katılımcı bilgilendirmesi": "Participant information", "Bilgilendirmeyi okudum, gönüllü katılıyorum (simülasyon).":
        "I have read the information and agree to participate voluntarily (simulation).",
    "Veli/yasal temsilci bilgilendirmesi ve izni.": "Parent/legal guardian information and permission.",
    "Veli/yasal temsilci izin verdi (simülasyon).": "The parent/legal guardian has given permission (simulation).",
    "18 yaş ve üzeri katılımcı için veli izni gerekmez; kendi gönüllü onamı yeterlidir.":
        "Participants aged 18 or over do not need parental permission; their own voluntary consent is sufficient.",
    "Simülasyon tamamlandı: katılım koşulları sağlandı.": "Simulation complete: participation conditions have been met.",
    "Baştan başla": "Start again", "Gönüllü katılım ve veli onam formu taslağı (.txt)": "Draft voluntary participation and parental consent form (.txt)",
    "Araştırma ve kalite kontrol": "Research and quality assurance", "Otomatik değerlendirme": "Automated evaluation",
    "Elle kontrol listesi": "Manual checklist", "Yöntem ve sınırlılıklar": "Methodology and limitations",
    "Değerlendirmeyi çalıştır": "Run evaluation", "Sonucu JSON olarak indir": "Download result as JSON",
    "Karışıklık matrisi": "Confusion matrix", "Örnek türüne göre doğruluk": "Accuracy by sample type",
    "Kategoriye göre yakalama (duyarlılık)": "Detection by category (recall)", "Yanlış alarm": "False positive",
    "Kaçırılan": "Missed", "İşaretler yalnızca bu oturumda tutulur; resmi test raporu veya bilimsel doğrulama yerine geçmez.":
        "Selections are stored only for this session; they do not replace an official test report or scientific validation.",
    "Bu senaryoyu test ettim": "I have tested this scenario", "Yanlış alarmlar": "False positives", "ve kaçırılanlar": "and missed cases",
    "Algılayıcının sentetik (elle yazılmış, gerçek veri içermeyen) örnek kümesindeki performansını ölçer.":
        "Measures the detector's performance on a synthetic (manually written and containing no real data) sample set.",
    "Platformun işlevleri": "Platform features", "Sınırlar": "Limitations", "Gerçek kullanıma geçmeden önce (kontrol listesi)": "Before real-world use (checklist)",
    "Güvenli kullanım": "Safe use", "Bu dönemde kayıt yok.": "There are no reports in this period.",

    # Static content / privacy notice and research notes
    "Veri sorumlusu": "Data controller", "İletişim": "Contact", "İşlenen veriler": "Data processed",
    "Bildirim formunda yazdığınız olay bilgisi (tür, ortam, zaman, açıklama). Ad, soyad, sınıf, telefon istenmez.":
        "Incident information entered in the report form (type, setting, time and description). First name, last name, class and phone number are not requested.",
    "Amaç": "Purpose", "Hukuki sebep": "Legal basis", "Aktarım": "Data transfers", "Saklama ve imha": "Retention and deletion", "Haklarınız": "Your rights",
    "GÖNÜLLÜ KATILIM VE VELİ ONAM FORMU (TASLAK)": "VOLUNTARY PARTICIPATION AND PARENTAL CONSENT FORM (DRAFT)",
    "Proje:": "Project:", "Okul:": "School:", "Danışman öğretmen:": "Supervising teacher:",
    "Öğrenci:": "Student:", "Veli/Yasal temsilci:": "Parent/Legal guardian:", "Tarih:": "Date:", "İmza:": "Signature:",

    # Enum values shown to end users (database values remain Turkish)
    "İnceleme bekliyor": "Awaiting review", "İnceleniyor": "Under review", "Takip gerekiyor": "Follow-up required",
    "Sonuçlandırıldı": "Closed", "Henüz atanmadı": "Not yet assigned", "Rehberlik birimi": "Guidance service",
    "Okul yönetimi": "School administration", "Öğrenci destek ekibi": "Student support team",
    "Hakaret veya alay": "Insults or mockery", "Tehdit": "Threat", "Dışlama": "Exclusion",
    "Dijital zorbalık": "Cyberbullying", "Fiziksel zorbalık şüphesi": "Suspected physical bullying", "Diğer": "Other",
    "Sınıfta": "In the classroom", "Okul bahçesinde": "In the school yard", "Koridorda": "In the corridor",
    "Sosyal medyada": "On social media", "Mesajlaşmada": "In messaging apps", "Bugün": "Today", "Dün": "Yesterday",
    "Bu hafta": "This week", "Daha önce": "Earlier", "Emin değilim": "Not sure", "Bir kez oldu": "Once",
    "Birkaç kez oldu": "A few times", "Sık sık / sürekli oluyor": "Frequently / ongoing",
    "Sinyal yok": "No signal", "Düşük": "Low", "Orta": "Medium", "Yüksek": "High", "Acil": "Urgent",
    "Sonuçlandırıldı": "Closed", "İnceleme bekliyor": "Awaiting review",

    # Emergency/help and validation messages
    "Yazdıkların için endişeleniyoruz. Şu an güvende değilsen ya da kendini veya başkasını tehlikede hissediyorsan lütfen hemen güvendiğin bir yetişkine, okul rehber öğretmenine ya da yukarıdaki acil hatlara ulaş.":
        "We are concerned about what you have written. If you are not safe right now, or feel that you or someone else may be in danger, contact a trusted adult, your school counsellor or one of the emergency services listed above immediately.",
    "Ek bilgi boş olamaz.": "Additional information cannot be empty.",
    "Bu bildirim sonuçlandırıldığı için ek bilgi eklenemez.": "Additional information cannot be added because this report has been closed.",
    "Ek bilgi yalnızca bildirimin yapıldığı gün eklenebilir.": "Additional information can only be added on the day the report was submitted.",
}



CATALOG.update({
    # Home-page cards and additional interface copy
    "Yaşıyorsan": "If you are experiencing bullying", "Kime anlatabileceğini ve neler yapabileceğini öğren.": "Learn whom you can talk to and what you can do.",
    "Tanık olduysan": "If you witnessed bullying", "Sessiz kalmadan, güvenli şekilde nasıl destek olursun?": "How can you offer support safely instead of staying silent?",
    "Veli ve öğretmenler": "Parents and teachers", "İşaretleri tanı, çocuğu dinle, doğru adımı at.": "Recognise the signs, listen to the child and take appropriate action.",
    "Otomatik eşleşme yalnızca inceleme sırasına yardım eder.": "Automated matching only helps prioritise reports for review.",
    "Yönetici işlemleri kim yaptığıyla kayda geçer.": "Administrator actions are logged with the identity of the person who performed them.",
    "Kime anlatabileceğini ve neler yapabileceğini öğren.": "Learn whom you can talk to and what you can do.",
    "Kayıtları tek bir çalışma alanında görüntüleyin, yönlendirin ve işlem geçmişini takip edin.": "View reports, assign them and follow their activity history in one workspace.",
    "KAYIT YÖNETİMİ": "REPORT MANAGEMENT", "BİLDİRİM": "REPORT", "TAKİP": "TRACKING",
    "Bildirim alındı": "Report received", "Durum": "Status", "Oluşturulma zamanı": "Date submitted",
    "Son güncelleme": "Last updated", "Bu bildirim için ek bilgi": "Additional information for this report",
    "Aynı gün içinde ek bilgi gönderebilirsin.": "You can submit additional information on the same day.",
    "Bildirim alındı. Yetkili kişi henüz incelemeye başlamadı.": "Your report has been received. An authorised reviewer has not started reviewing it yet.",
    "Bildirimin yetkili kişiler tarafından inceleniyor.": "Your report is being reviewed by authorised staff.",
    "İnceleme sürüyor; konu takip edilmeye devam ediyor.": "The review is ongoing and the matter will continue to be monitored.",
    "Bildirimin değerlendirildi ve süreç tamamlandı.": "Your report has been assessed and the process is complete.",
    "Kayıt seçimi": "Report selection", "Seçili kaydı görüntüle": "View selected report",
    "Kayıt ayrıntısı": "Report details", "Açıklama metni": "Report description", "Ek bilgiler": "Additional information",
    "Kayıt tarihi": "Report date", "İşlem": "Action", "Kullanıcı": "User", "Ayrıntı": "Details",
    "İşlemi yapan": "Performed by", "Yazar": "Author", "Birim": "Team", "Atama": "Assignment",
    "Sinyal değerlendirmesi": "Signal assessment", "İlk incelemeye kadar geçen süre": "Time to initial review",
    "Bekleme süresi": "Waiting time", "Saat": "Hour", "Dakika": "Minute", "saat": "hours",
    "Gecikmiş kayıt": "Overdue report", "SLA süresi": "SLA threshold", "SLA": "SLA",
    "Acil bir tehlike varsa beklemeyin:": "If there is immediate danger, do not wait:",
    "Acil Çağrı Merkezi (Polis, Sağlık, Jandarma - 7/24)": "Emergency Call Centre (Police, Medical and Gendarmerie services – 24/7)",
    "ALO Sosyal Destek Hattı (7/24)": "ALO Social Support Line (24/7)", "MEB İletişim Merkezi (MEBİM)": "Ministry of National Education Contact Centre (MEBİM)",
    "İnceleme bekliyor": "Awaiting review", "İnceleniyor": "Under review", "Takip gerekiyor": "Follow-up required",
    "Sonuçlandırıldı": "Closed", "Henüz atanmadı": "Not yet assigned", "Rehberlik birimi": "Guidance service",
    "Okul yönetimi": "School administration", "Öğrenci destek ekibi": "Student support team",
    "Hakaret veya alay": "Insults or mockery", "Fiziksel zorbalık şüphesi": "Suspected physical bullying",
    "Sınıfta": "In the classroom", "Okul bahçesinde": "In the school yard", "Koridorda": "In the corridor",
    "Sosyal medyada": "On social media", "Mesajlaşmada": "In messaging apps", "Bir kez oldu": "Once",
    "Birkaç kez oldu": "A few times", "Sık sık / sürekli oluyor": "Frequently / ongoing",
    "Sinyal yok": "No signal", "Düşük": "Low", "Orta": "Medium", "Yüksek": "High", "Acil": "Urgent",
    "Tüm durumlar": "All statuses", "Tüm birimler": "All teams", "Tüm öncelikler": "All priorities",
    "Kimlik bilgisi belirtilmiş": "Identifying details provided", "Anonim bildirim": "Anonymous report",
    "Kimlik bilgili bildirim": "Report with identifying details", "Kayıt bulunamadı.": "No report was found.",
    "Kayıt güncellenemedi.": "The report could not be updated.", "İşlem tamamlandı.": "Action completed.",
    "İnceleme için önerilen adımlar": "Recommended review steps", "Rehberlik servisi için not": "Guidance service note",
    "Bu öneriler karar veya tanı değildir; yetkili uzman değerlendirmesinin yerine geçmez.":
        "These suggestions are not decisions or diagnoses and do not replace assessment by an authorised professional.",
    "Siber zorbalıkta": "For cyberbullying", "Akran dışlamasında": "For peer exclusion",
    "Ekran görüntülerini, bağlantıları ve tarih bilgilerini güvenli biçimde muhafaza edin; içerikleri yaymayın.":
        "Preserve screenshots, links and date information securely; do not redistribute the content.",
    "Öğrenciyle bireysel ve güvenli bir görüşme yapın; öğrenciyi suçlayıcı sorulardan kaçının.":
        "Arrange an individual meeting in a safe setting and avoid questions that blame the student.",
    "Olayın tekrar sıklığını, güç dengesizliğini ve öğrencinin güvenlik ihtiyacını değerlendirin.":
        "Assess recurrence, power imbalance and the student's safeguarding needs.",
    "Gerekli durumlarda okulun koruma, bilgilendirme ve yönlendirme prosedürlerini izleyin.":
        "Where necessary, follow the school's safeguarding, notification and referral procedures.",
    "Destek içerikleri bilgilendirme amaçlıdır; okulun rehberlik ve koruma prosedürlerinin yerini almaz.":
        "Support content is for information only and does not replace the school's counselling and safeguarding procedures.",
    "Zorbalık; bilerek yapılan, tekrar eden ve güç dengesizliği olan davranıştır (alay, tehdit, dışlama, fiziksel saldırı, internette aşağılama).":
        "Bullying is intentional, repeated behaviour involving a power imbalance (such as mockery, threats, exclusion, physical aggression or online humiliation).",
    "Arkadaşlar arasındaki tek seferlik tartışma genellikle zorbalık sayılmaz; ama seni korkutuyor ya da üzüyorsa yine de anlatmaya değer.":
        "A one-off disagreement between friends is not usually considered bullying. However, if it frightens or upsets you, it is still worth talking about.",
    "Olanlar senin suçun değildir.": "What is happening is not your fault.",
    "Güvendiğin bir yetişkine (rehber öğretmen, sınıf öğretmeni, aile) olanı anlat.":
        "Tell a trusted adult, such as a school counsellor, classroom teacher or family member, what happened.",
    "Cevap vermek zorunda değilsin; güvenli bir yere git, yanında birileriyle ol.":
        "You do not have to respond. Move to a safe place and stay with someone you trust.",
    "Mesaj ve ekran görüntülerini sakla, silme; yetişkine gösterirsin.":
        "Keep messages and screenshots; do not delete them. You can show them to a trusted adult.",
    "Bu sitedeki anonim formu kullanabilirsin; ama form acil durum hattı değildir.":
        "You can use the anonymous form on this platform, but it is not an emergency service.",
    "Bu düşünceleri tek başına taşımak zorunda değilsin. Hemen güvendiğin bir yetişkine söyle.":
        "You do not have to deal with these thoughts alone. Tell a trusted adult immediately.",
    "Acil tehlikede 112'yi, destek için 183'ü arayabilirsin.": "In an emergency, call 112. For support, you can call 183.",
    "Zorbalığa gülmek ya da paylaşmak onu büyütür. Katılmamak bile bir destektir.":
        "Laughing at or sharing bullying makes it worse. Choosing not to take part is already a form of support.",
    "Güvenliysen mağdurun yanına git, yalnız olmadığını hissettir.":
        "If it is safe, approach the person affected and let them know they are not alone.",
    "Müdahale etmek tehlikeliyse bir yetişkine haber ver. Bu ‘çaksıl’ değil, arkadaşını korumaktır.":
        "If intervening could be dangerous, tell an adult. This is not 'snitching'; it is helping to keep someone safe.",
    "Anonim form ile adını vermeden bildirebilirsin.": "You can submit an anonymous report without giving your name.",
    "Cevap verme, kişiyi engelle, platformda şikâyet et.": "Do not respond. Block the person and report the content on the platform.",
    "Kanıtları (ekran görüntüsü, tarih, hesap adı) sakla.": "Keep relevant evidence (screenshots, dates and account names).",
    "Şifrelerini kimseyle paylaşma, gizlilik ayarlarını gözden geçir.": "Do not share your passwords and review your privacy settings.",
    "Sık görülen işaretler: okula gitmek istememe, uyku/iştah değişikliği, eşya kaybı, çekingenlik, telefona karşı aşırı tedirginlik. Bunlar tek başına kanıt değildir.":
        "Possible signs include reluctance to attend school, changes in sleep or appetite, missing belongings, withdrawal or unusual anxiety about a phone. These signs alone are not proof of bullying.",
    "Önce sakin kalın, dinleyin; suçlamayın, ‘sen de karşılık ver’ demeyin.":
        "First, stay calm and listen. Do not blame the child or tell them to retaliate.",
    "Olayı tarih ve ayrıntılarıyla yazın; okul rehberlik servisiyle görüşün.":
        "Record the incident with dates and relevant details, and contact the school's guidance service.",
    "Savunmaya geçmeden dinleyin; davranışın başkasına verdiği zararı konuşun.":
        "Listen without becoming defensive and discuss the impact the behaviour has had on others.",
    "Okul rehberlik servisiyle birlikte çalışın; cezadan çok davranış değişikliğini hedefleyin.":
        "Work with the school's guidance service and focus on changing behaviour rather than punishment alone.",
    "Kaydı yalnızca insan olarak değerlendirin; otomatik sinyal kanıt veya karar değildir.":
        "Assess the report through human review only; an automated signal is not evidence or a decision.",
    "Kaynağı belirlemeye çalışmayın; bildirimin anonimliğini koruyun.":
        "Do not try to identify the reporter; protect the anonymity of the report.",
    "Şüpheli öğrencinin yanlış suçlanma riskini gözetin; süreci rehberlik servisi ve okul yönetimiyle yürütün.":
        "Be mindful of the risk of wrongly accusing a student; follow the process with the guidance service and school administration.",
    "Acil sinyal veya doğrudan zarar riski varsa okulun acil durum protokolünü uygulayın.":
        "If an urgent signal or immediate risk of harm is identified, follow the school's emergency protocol.",
    "Formu gönderirsin ve gizli takip kodunu alırsın.": "You submit the form and receive a private tracking code.",
    "Kayıt, yetkili kişiler (rehberlik / okul yönetimi) tarafından incelenir; bunu bir insan yapar.":
        "The report is reviewed by authorised staff (the guidance service or school administration); a person makes the assessment.",
    "Takip koduyla durumu görürsün. Sistemde mesajlaşma yoktur; bu yüzden acil durumlarda bir yetişkine ulaş.":
        "You can check the status using your tracking code. Messaging is not available, so contact an adult in an emergency.",
    "Bildirim sayısındaki artış, olayların arttığını değil bildirme isteğinin arttığını da gösterebilir; ayrım için ayrı bir ölçüm (ör. anket) gerekir.":
        "An increase in reports may reflect greater willingness to report rather than an increase in incidents; a separate measure (such as a survey) is needed to distinguish the two.",
    "Saat, olayın değil bildirimin saatidir; anonim kayıtlarda zaman saate yuvarlanır.":
        "The time shown is when the report was submitted, not when the incident occurred.",
    "SİMÜLASYON:": "SIMULATION:", "Bu akış gerçek onam toplamaz, hiçbir veri kaydetmez ve kimseyle iletişime geçmez.":
        "This flow does not collect real consent, save data or contact anyone.",
    "Araştırmada onam, okulun resmî kanallarıyla yazılı olarak alınmalıdır.":
        "For research, consent must be obtained in writing through the school's official channels.",
    "Bu aşamadan sonra katılımcı bildirim formunu kullanabilir.": "After this step, the participant may use the report form.",
    "Katılımcıdan": "The participant is not asked for", "ad, sınıf, telefon istenmez": "a name, class or phone number",
    "onay kaydı bu uygulamada tutulmaz, okulda yazılı saklanır.": "; the consent record is not stored in this platform and must be retained in writing by the school.",
    "Gerçek sistemde bu adım, okulun resmî iletişim kanalıyla ve yazılı olarak yürütülür; bu uygulama veli iletişim bilgisi toplamaz.":
        "In a live system, this step must be handled in writing through the school's official communication channel. This platform does not collect parent contact details.",
    "Açıklamadaki telefon, T.C. kimlik numarası, e-posta ve IBAN'ı otomatik maskeler.":
        "Automatically masks phone numbers, Turkish national ID numbers, email addresses and IBANs in report descriptions.",
    "Takip koduyla durum sorgulamaya ve (anonim kayıtlarda, aynı gün) ek bilgi eklemeye izin verir.":
        "Allows users to check report status and, for anonymous reports, add further information on the same day using a tracking code.",
    "Yönetici girişinden sonra kayıtları listeler; durum/birim günceller; not ve işlem geçmişi tutar.":
        "After administrator sign-in, lists reports, updates statuses and assigned teams, and maintains notes and an activity history.",
    "Girişleri ve yönetici işlemlerini denetim kaydında saklar; CSV dışa aktarım ve saklama süresi temizliği sunar.":
        "Maintains an audit log of sign-ins and administrator actions, provides CSV export and supports retention-based deletion.",
    "İfade eşleşmelerini yalnızca insan incelemesi için öncelik sinyali olarak gösterir.":
        "Displays phrase matches only as priority signals to support human review.",
    "Gerçek bir okul veya rehberlik servisine bağlı değildir; acil yardım ya da resmi bildirim hizmeti değildir.":
        "It is not connected to a real school or guidance service and is not an emergency or official reporting service.",
    "Zorbalık hakkında otomatik kesin karar vermez; sinyaller yanlış alarm üretebilir ve olayları kaçırabilir.":
        "It does not make definitive automated decisions about bullying; signals may produce false positives or miss incidents.",
    "Tek yönetici hesabı kurumsal kimlik doğrulamanın (SSO/2FA) yerini tutmaz.":
        "A single administrator account is not a substitute for institutional authentication (SSO/2FA).",
    "Yerel SQLite dosyasının bulut ortamında kalıcı olacağı garanti edilmez; yedekleme planı gerekir.":
        "Persistence of a local SQLite file in a cloud environment is not guaranteed; a backup plan is required.",
    "Hatalı giriş ve zaman aşımı korumaları vardır, ancak bu bir güvenlik denetiminden geçmemiştir.":
        "Failed-login and session-timeout protections are implemented, but the platform has not undergone a security audit.",
    "Veri sorumlusunun belirlenmesi, aydınlatma metni, hukuki sebep/veli onayı, saklama-imha politikası":
        "Determine the data controller, prepare a privacy notice, establish the legal basis and parental consent requirements, and define retention and deletion policies",
    "Çocuk verisi ve olası yurt dışı sunucu kullanımı ayrıca hukuki değerlendirme gerektirir.":
        "The processing of children's data and any use of servers outside the country require separate legal assessment.",
    "Kişi bazlı hesaplar, rol ayrımı, iki aşamalı doğrulama, parola özeti":
        "Individual accounts, role-based access, two-factor authentication and password hashing",
    "HTTPS, şifreli yedek, günlüklerin korunması, bağımsız güvenlik testi.":
        "HTTPS, encrypted backups, log protection and independent security testing.",
    "Kayıtları kimin, ne kadar sürede inceleyeceği, acil durum protokolü ve rehberlik servisiyle iş akışı.":
        "Define who reviews reports and within what timeframe, the emergency protocol and the workflow with the guidance service.",
    "Sonuçlar iyimserdir ve genellenemez.": "The results are optimistic and cannot be generalised.",
    "Bilimsel geçerlik için bağımsız, etik onaylı ve en az iki değerlendiricinin etiketlediği bir veri kümesi gerekir.":
        "Scientific validity requires an independent, ethically approved dataset labelled by at least two evaluators.",
    "İşaretler yalnızca bu oturumda tutulur; resmi test raporu veya bilimsel doğrulama yerine geçmez.":
        "Selections are stored only for this session and do not replace an official test report or scientific validation.",
    "Açıklama yalnızca boşluk veya noktalama işaretlerinden oluşamaz.": "The description cannot consist only of spaces or punctuation.",
    "Kayıt ara": "Search reports", "Kayıt sayısı": "Number of reports", "Örnek sayısı": "Sample size",
    "Kesinlik (precision)": "Precision", "Duyarlılık (recall)": "Recall", "Doğruluk": "Accuracy",
    "Yakalanan": "Detected", "Oran": "Rate", "Örnek": "Samples", "Doğru": "Correct",
    "Saklama süresi (gün)": "Retention period (days)", "Süresi dolan kayıtları sil": "Delete expired reports",
    "Bu kodla eşleşen bir kayıt bulunamadı. Kodu kontrol edip tekrar dene.": "No report was found for this code. Check the code and try again.",
})


CATALOG.update({
    "Sınırlar": "Limitations", "Sıralama": "Sort order", "**Açıklama**": "**Description**",
    "Kayıt oluşturulamadı. Lütfen daha sonra tekrar dene.": "The report could not be created. Please try again later.",
    "Sınırlılıklar": "Limitations", "Süreç": "Process", "İşaretlenen test:": "Tests checked:",
    "OTURUM": "SESSION", "Sinyal:": "Signal:", "saat bekliyor": "hours waiting",
    "Günlük durum özeti": "Daily status summary", "Yeni bildirim": "New report",
    "24 saati aşan bekleyen": "Awaiting review for over 24 hours",
    "Yüksek veya acil sinyal (açık)": "High or urgent signals (open)",
    "İlk inceleme": "Initial review", "Aktif takip": "Active follow-up",
    "24 saati aşan bekleyen": "Awaiting review for over 24 hours",
    "Öncelik (yüksekten)": "Priority (highest first)",
    "{n} kayıt": "{n} reports",
    "Bu hak, tarayıcında saklanan rastgele bir kodla uygulanır; kimliğinle ilişkili değildir.":
        "This limit is enforced using a random code stored in your browser; it is not linked to your identity.",
    "Telefon, adres gibi bilgileri yazmana gerek yok; yalnızca olayı anlat.":
        "You do not need to provide a phone number or address; describe only what happened.",
    "Ad, telefon gibi bilgileri yazma.": "Do not include names, phone numbers or similar identifying details.",
    "Ek bilgin eklendi. Bugün": "Your additional information has been added. You have",
    "ek bilgi hakkın kaldı.": "additional entries remaining today.",
    "Yönetici girişi başarılı.": "Administrator sign-in successful.",
    "Yönetici bilgileri ayarlanmamış. .streamlit/secrets.toml (veya Streamlit Cloud > Settings > Secrets) içindeki [admin] bölümünü yapılandırın.":
        "Administrator credentials have not been configured. Set up the [admin] section in .streamlit/secrets.toml (or Streamlit Cloud > Settings > Secrets).",
    "Lütfen": "Please", "tekrar deneyin.": "try again.",
    "Sınıf:": "Class:", "Ad soyad:": "Full name:", "Belirtilmedi": "Not provided",
    "Tekrarlanma": "Frequency", "Yaklaşık zaman": "Approximate time", "Bildirim türü": "Report type",
    "SEÇİLİ KAYIT": "SELECTED REPORT", "TAKİP KODU": "TRACKING CODE", "KAYIT YÖNETİMİ": "REPORT MANAGEMENT",
    "İşlem geçmişi": "Activity history", "Anonim gönderenin ek bilgileri": "Additional information from the anonymous reporter",
    "İnceleme bilgileri kaydedildi.": "Review details have been saved.", "Not eklendi.": "Note added.",
    "CSV dışa aktarım": "CSV export", "kimlik dahil": "identifiers included", "kimlik hariç": "identifiers excluded",
    "Kayıt sayısı": "Number of reports", "En çok bildirilen ortam": "Most frequently reported setting",
    "En çok bildirilen tür": "Most frequently reported type", "Ne zaman bildiriliyor?": "When are reports submitted?",
    "Yalnızca": "Only", "kayıt var; yüzdeler ve eğilimler yanıltıcı olabilir, yorum yapmayın.":
        "reports are available; percentages and trends may be misleading and should not be interpreted.",
    "Bu dönemde kayıt yok.": "There are no reports for this period.",
    "‘·’ ile gösterilen": "Cells marked with '·'", "hücre (toplam": "are suppressed (a total of",
    "kayıt)": "reports)", "'den az olduğu için gizlendi.": "were hidden because their count is below the threshold.",
    "Çapraz tabloda sayısı bu değerden küçük hücreler kimliksizleştirme için gizlenir.":
        "Cells with counts below this threshold are suppressed in the cross-tabulation to reduce identification risk.",
    "Zorbalıkla baş etme yolları ve kime nasıl ulaşabileceğin. Bu içerik bilgilendirme amaçlıdır.":
        "Ways to respond to bullying and how to seek help. This content is provided for information only.",
    "Özel fotoğrafın izinsiz paylaşılıyorsa ya da paylaşılmakla tehdit ediliyorsan hemen bir yetişkine söyle; bu ciddi bir durumdur ve suç oluşturabilir.":
        "If a private image is shared without your permission or someone threatens to share it, tell a trusted adult immediately. This is serious and may be a criminal offence.",
    "Çocuğunuzun kendine zarar verme düşüncesi olabileceğinden endişeleniyorsanız 112'yi arayın.":
        "If you are concerned that your child may be at risk of harming themselves, contact emergency services on 112.",
    "Müdahale etmek tehlikeliyse bir yetişkine haber ver. Bu ‘çaksıl’ değil, arkadaşını korumaktır.":
        "If intervening could be unsafe, tell an adult. This is not 'snitching'; it is helping to protect someone.",
    "**Veri sorumlusu:**": "**Data controller:**", "**İletişim:**": "**Contact:**",
    "**İşlenen veriler:**": "**Data processed:**", "**Amaç:**": "**Purpose:**", "**Hukuki sebep:**": "**Legal basis:**",
    "**Aktarım:**": "**Data transfers:**", "**Saklama ve imha:**": "**Retention and deletion:**", "**Haklarınız:**": "**Your rights:**",
    "[OKUL ADI / KURUM]": "[SCHOOL / INSTITUTION NAME]", "[KVKK İLETİŞİM ADRESİ]": "[DATA PROTECTION CONTACT ADDRESS]",
    "Bildirim formunda yazdığınız olay bilgisi (tür, ortam, zaman, açıklama). Ad, soyad, sınıf, telefon istenmez.":
        "Incident information entered in the report form (type, setting, time and description). First name, last name, class and phone number are not requested.",
    "Açıklamadaki telefon, T.C. kimlik no, e-posta ve IBAN otomatik maskelenir.":
        "Phone numbers, Turkish national ID numbers, email addresses and IBANs in descriptions are automatically masked.",
    "Akran zorbalığı bildirimlerinin yetkili kişilerce incelenmesi ve öğrencinin korunması. Veriler başka amaçla kullanılmaz.":
        "To enable authorised staff to review peer-bullying reports and safeguard students. Data is not used for other purposes.",
    "Otomatik sinyal yalnızca inceleme sırasına yardımcıdır; hiçbir karar otomatik verilmez.":
        "Automated signals only help prioritise reviews; no decisions are made automatically.",
    "[HUKUK DANIŞMANI BELİRLEYECEK: ör. KVKK m.5/2 ilgili bendi / açık rıza / veli onamı]":
        "[TO BE DETERMINED BY LEGAL COUNSEL: e.g. applicable provision of KVKK Article 5(2) / explicit consent / parental consent]",
    "Veriler yetkili okul personeli dışında paylaşılmaz.": "Data is not shared outside authorised school personnel.",
    "[BARINDIRMA YERİ VE YURT DIŞI AKTARIM DURUMU YAZILACAK]": "[SPECIFY HOSTING LOCATION AND WHETHER DATA IS TRANSFERRED ABROAD]",
    "Sonuçlanan kayıtlar [180] gün sonra silinir; günlük cihaz kodu özeti 1 gün sonra silinir.":
        "Closed reports are deleted after [180] days; the daily device-token hash is deleted after one day.",
    "KVKK m.11 kapsamındaki haklar için yukarıdaki adrese başvurabilirsiniz.":
        "You may contact the address above to exercise your rights under Article 11 of the Turkish Personal Data Protection Law (KVKK).",
    "Anonim bildirimlerde bildirimi size bağlamak mümkün olmadığından bazı haklar (erişim, düzeltme) teknik olarak kullanılamayabilir.":
        "For anonymous reports, it may not be technically possible to link a report to you, so certain rights (such as access and rectification) may not be exercisable.",
    "Olay açıklaması (maskelenmiş)": "Incident description (masked)", "Bildirimi incelemek": "Reviewing the report",
    "Bildirim gönderildiğinde": "When the report is submitted", "Sonuç + [180] gün": "Closure + [180] days",
    "Serbest metin; üçüncü kişilerin adı geçebilir, maskeleme adları yakalamaz.":
        "Free text; third-party names may appear and are not detected by the masking layer.",
    "Olay türü, ortam, zaman, tekrar": "Incident type, setting, time and frequency", "İstatistik ve önceliklendirme": "Statistics and prioritisation",
    "Seçmeli alanlar.": "Structured selection fields.", "Takip kodu": "Tracking code", "Durum sorgulama, ek bilgi": "Status checks and additional information",
    "Rastgele; kimlikle ilişkisiz.": "Randomly generated; not linked to an identity.", "Kayıtla birlikte": "Retained with the report",
    "Cihaz jetonu özeti (SHA-256)": "Device-token hash (SHA-256)", "Günlük bildirim hakkı": "Daily reporting limit",
    "1 gün": "1 day", "Rapora bağlanmaz.": "Not linked to the report.", "Ek bilgiler": "Additional information",
    "Aynı bildirimi tamamlamak": "Supplementing the same report", "Takip koduyla, aynı gün": "Using the tracking code, on the same day",
    "En çok 3 ek.": "Maximum of 3 entries.", "Öncelik sinyali / kategoriler": "Priority signal / categories",
    "Kayıt anında (otomatik)": "At the time of submission (automatically)", "Kural tabanlı; karar değildir.": "Rule-based; not a decision.",
    "İnceleme notları, işlem geçmişi": "Review notes and activity history", "Hesap verebilirlik": "Accountability",
    "Yönetici işlemlerinde": "During administrator actions", "Kim yaptı bilgisi içerir.": "Includes information about who performed the action.",
    "Denetim kaydı, giriş denemeleri": "Audit log and sign-in attempts", "Yönetici girişlerinde": "During administrator sign-ins",
    "Giriş denemeleri 7 gün; denetim kaydı: TANIMSIZ": "Sign-in attempts: 7 days; audit-log retention: UNDEFINED",
    "Denetim kaydı için saklama süresi karar verilmeli.": "A retention period must be defined for the audit log.",
    "Ad, soyad, sınıf (yalnızca eski kayıtlar)": "First name, last name and class (legacy records only)",
    "Formda artık istenmiyor": "No longer requested in the form", "Eski kayıtlarla birlikte": "Retained with legacy records",
    "Eski kimlikli kayıtlar varsa silinmeli veya gözden geçirilmeli.": "Legacy reports containing identifying information should be reviewed or deleted.",
    "- Formda ad, sınıf, telefon istenmez.": "- The form does not request a name, class or phone number.",
    "- Açıklamadaki T.C. no, telefon, e-posta, IBAN maskelenir; ham metin saklanmaz.":
        "- Turkish ID numbers, phone numbers, email addresses and IBANs in descriptions are masked; the unmasked text is not stored.",
    "- Anonim kayıt ve ek bilgi zamanı saate yuvarlanır.": "- Anonymous report and additional-information timestamps are recorded to the second.",
    "- Cihaz jetonu yalnızca özet olarak ve 1 gün saklanır; rapora bağlanmaz.": "- Only a hash of the device token is retained for one day; it is not linked to a report.",
    "- Öğrenci sorgusunda açıklama, not ve değerlendirme gösterilmez.": "- Student status checks do not display descriptions, notes or assessments.",
    "- Serbest metin kişileri dolaylı tanıtabilir; ‘tam anonim’ yerine ‘kimliksizleştirilmiş’ demek daha doğrudur.":
        "- Free text may indirectly identify people; 'de-identified' is more accurate than 'fully anonymous'.",
    "- Üçüncü kişilerin (şüpheli öğrenci) adı metinde geçebilir; maskeleme adları yakalamaz.":
        "- Third-party names (including a student who is the subject of a report) may appear in text; the masking layer does not detect names.",
    "- Barındırma yeri ve olası yurt dışı aktarım hukuken değerlendirilmelidir.":
        "- Hosting location and any potential international data transfer must be assessed legally.",
    "- Sonuçlanan kayıtlar: ‘Bildirim inceleme → Dışa aktarım ve saklama’ ekranından, seçilen gün sonunda notları ve ek bilgileriyle silinir (varsayılan 180).":
        "- Closed reports: deleted with their notes and additional information from 'Report review → Export and retention' after the selected retention period (default: 180 days).",
    "- Cihaz jetonu özeti: ertesi gün silinir.": "- Device-token hash: deleted the following day.",
    "- Giriş denemeleri: 7 gün.": "- Sign-in attempts: 7 days.",
    "- Denetim kaydı: saklama süresi tanımlı değil; karar verilmeli.": "- Audit log: no retention period is currently defined; one must be set.",
    "GÖNÜLLÜ KATILIM VE VELİ ONAM FORMU (TASLAK)": "VOLUNTARY PARTICIPATION AND PARENTAL CONSENT FORM (DRAFT)",
    "1. Amaç: Bildirim sisteminin kullanılabilirliğini ve kural tabanlı sinyalin başarımını değerlendirmek.":
        "1. Purpose: To evaluate the usability of the reporting system and the performance of rule-based signals.",
    "2. Katılım gönüllüdür; istediğiniz zaman, gerekçe göstermeden ayrılabilirsiniz.":
        "2. Participation is voluntary; you may withdraw at any time without giving a reason.",
    "3. Toplanan veri: Formdaki olay bilgisi (ad, soyad, telefon toplanmaz). Gerçek kişileri tanıtan bilgi yazmayınız.":
        "3. Data collected: Incident information entered in the form (names and phone numbers are not collected). Do not enter information that identifies real people.",
    "4. Saklama: [SÜRE]. Veriler yalnızca araştırma ekibi ve yetkili okul personelince görülür.":
        "4. Retention: [PERIOD]. Data is accessible only to the research team and authorised school staff.",
    "5. Riskler: Zorbalık konusu bazı öğrencileri üzebilir; bu durumda rehberlik servisine başvurabilirsiniz.":
        "5. Risks: Discussing bullying may be upsetting for some students; you may contact the school guidance service if needed.",
    "Öğrenci: Bilgilendirildim, gönüllü katılıyorum.": "Student: I have been informed and agree to participate voluntarily.",
    "Veli/Yasal temsilci: Bilgilendirildim, çocuğumun katılımına izin veriyorum.":
        "Parent/Legal guardian: I have been informed and give permission for my child's participation.",
    "18 yaşından küçük": "Under 18", "18 yaş ve üzeri": "18 or over", "Pzt": "Mon", "Sal": "Tue", "Çar": "Wed",
    "Per": "Thu", "Cum": "Fri", "Cmt": "Sat", "Paz": "Sun",
    "Tüm durumlar": "All statuses", "Öncelik (yüksekten)": "Priority (highest first)",
    "Dışa aktarım ve saklama": "Export and retention", "Denetim kaydı": "Audit log", "Kayıtlar": "Reports",
    "Yönetici:": "Administrator:", "Acil:": "Emergency:", "Sürüm 2.0": "Version 2.0",
    "Örnek": "Samples", "Tür": "Type", "Kategori": "Category", "Gerçekte sinyal var": "Signal present in ground truth",
    "Gerçekte sinyal yok": "No signal in ground truth", "Sinyal verildi": "Signal raised", "Sinyal verilmedi": "No signal raised",
    "Sinyal": "Signal", "Yanlış alarmlar": "False positives", "Kaçırılanlar": "Missed cases",
})


CATALOG.update({
    "Varsa ilgili mesaj, bağlantı ve ekran görüntülerini güvenli biçimde muhafaza edin; gereksiz kişilerle paylaşmayın.":
        "If available, preserve relevant messages, links and screenshots securely; do not share them with unnecessary parties.",
    "Öğrenciyle ayrı ve gizliliği koruyan bireysel görüşme yapın.":
        "Hold an individual meeting with the student in a way that protects their privacy.",
    "Okul prosedürüne uygun platform bildirim adımlarını ve güvenlik riskini değerlendirin.":
        "Assess the platform-reporting steps and safety risks in line with school procedures.",
    "Gerekirse veli ve okul yönetimiyle yetkili süreç üzerinden koordinasyon sağlayın.":
        "Where appropriate, coordinate with the parent or carer and school administration through authorised procedures.",
    "Öğrenciyi suçlamadan, yönlendirici olmayan sorularla bireysel olarak dinleyin.":
        "Listen to the student individually, without blame and using non-leading questions.",
    "Olayın tekrarı, güç dengesi ve farklı ortamlardaki etkisini değerlendirin.":
        "Assess recurrence, power dynamics and the impact across different settings.",
    "Sınıf ortamını ve akran ilişkilerini gözlemleyin; öğrencileri topluluk önünde etiketlemeyin.":
        "Observe the classroom environment and peer relationships; do not label students in front of others.",
    "Destek planını rehberlik servisi ve okulun ilgili ekibiyle birlikte belirleyin.":
        "Develop a support plan with the guidance service and the relevant school team.",
    "Önce öğrencilerin o anki güvenliğini değerlendirin; yakın tehlikede okulun acil durum protokolünü uygulayın.":
        "First assess the students' immediate safety; if there is imminent danger, follow the school's emergency protocol.",
    "Tarafları tek başına yüzleştirmeyin; ilgili yetişkinleri ve okul yönetimini bilgilendirin.":
        "Do not arrange a confrontation between the parties on your own; inform the relevant adults and school administration.",
    "Görüşmeleri ayrı ve gizli yürütün; beyanları yorum eklemeden kaydedin.":
        "Conduct interviews separately and confidentially; record statements without adding interpretation.",
    "Öğrenciyi bireysel ve yargılamadan dinleyin; olayın sıklığını, bağlamını ve etkisini netleştirin.":
        "Listen to the student individually and without judgement; clarify the frequency, context and impact of the incident.",
    "Tanık beyanlarını ayrı alın; otomatik sinyali tek başına kanıt kabul etmeyin.":
        "Take witness statements separately; do not treat an automated signal as evidence on its own.",
    "Güvenli sınıf iklimi ve davranış değişikliği için takip planı oluşturun.":
        "Create a follow-up plan to support a safe classroom climate and positive behaviour change.",
    "Metinde aktarma/alıntı ifadeleri var; eşleşen söz bildirimi yapanın kendi sözü olmayabilir.":
        "The text contains reported-speech or quotation markers; the matched phrase may not be the reporter's own words.",
    "Olumsuzlama ifadeleri var; eşleşme olumsuz bağlamda kullanılmış olabilir.":
        "Negation markers are present; the matched phrase may have been used in a negative context.",
    "Şaka/mizah ifadeleri var; bağlam insan tarafından değerlendirilmelidir.":
        "Humour or joking markers are present; the context should be assessed by a human reviewer.",
    "Ad soyad:": "Full name:", "Sınıf:": "Class:", "Açıklama bulunmuyor.": "No description is available.",
    "İşaretlenen test:": "Tests checked:", "Gizli takip kodun.": "Your private tracking code.",
    "Durumu ve ek bilgi eklemeyi bu kodla yaparsın.": "Use this code to check its status and add further information.",
    "Not al ya da ekran görüntüsü al; kod kaybolursa yeniden oluşturulamaz:": "Save this code or take a screenshot; it cannot be recovered if lost:",
    "ek bilgi": "additional information", "GECİKMİŞ": "OVERDUE", "24 saati aşan bekleyen": "Awaiting review for over 24 hours",
    "İlk inceleme": "Initial review", "Aktif takip": "Active follow-up", "Sonuçlandırıldı": "Closed",
    "Sinyal: ": "Signal: ", "SEÇİLİ KAYIT": "SELECTED REPORT", "TAKİP KODU": "TRACKING CODE",
    "Bu takip kodu yalnızca uygulamadaki kaydı tanımlar.": "This tracking code identifies only the report in this platform.",
    "Rehberlikle mesajlaşma yoktur; yalnızca bildirimin durumunu görürsün.": "Messaging with the guidance service is not available; you can only view the report status.",
    "Girişler, başarısız denemeler, dışa aktarımlar ve silme işlemleri burada izlenir.":
        "Sign-ins, failed attempts, exports and deletion actions are monitored here.",
    "Varsayılan olarak kapalıdır (veri minimizasyonu).": "Disabled by default (data minimisation).",
    "Küçük hücre eşiği (k)": "Small-cell threshold (k)", "Küçük hücre": "Small cell",
    "Süreler kayıt oluşturma ile ilk durum değişikliği / 'Sonuçlandırıldı' arasındaki farktır.":
        "Durations are measured from report creation to the first status change or closure.",
    "Sinyal kanıt veya karar değildir; bağlamı anlayamaz. Eşleşme olmaması da sorun olmadığı anlamına gelmez.":
        "A signal is not evidence or a decision and cannot understand context. The absence of a match does not mean there is no issue.",
    "Bu sürüm gerçek bir yapay zekâ modeli değil, kural tabanlı sinyal ve basit metin kalite kontrolü kullanır.":
        "This version is not an AI model; it uses rule-based signals and a basic text-quality check.",
    "Günlük cihaz kodu özeti 1 gün sonra silinir.": "The daily device-token hash is deleted after one day.",
    "Anonim kayıt ve ek bilgi zamanı dakika ve saniye hassasiyetinde kaydedilir.":
        "Anonymous report and additional-information timestamps are recorded to the second.",
    "- Anonim kayıt ve ek bilgi zamanı saate yuvarlanır.": "- Anonymous report and additional-information timestamps are recorded to the second.",
    "zaman saate yuvarlanır": "timestamps are recorded to the second",
    "zaman dakika ve saniye hassasiyetinde kaydedilir": "timestamps are recorded to the second",
})


CATALOG.update({
    "Bildirimin alındı. Yetkili kişi henüz incelemeye başlamadı.": "Your report has been received. An authorised reviewer has not started reviewing it yet.",
    "Bildirimin yetkili kişiler tarafından inceleniyor.": "Your report is being reviewed by authorised staff.",
    "İnceleme sürüyor; konu takip edilmeye devam ediyor.": "The review is ongoing and the matter will continue to be monitored.",
    "Bildirimin değerlendirildi ve süreç tamamlandı.": "Your report has been assessed and the process is complete.",
    "aktif yüksek/acil öncelikli kayıt var. Yetkili personel tarafından insan incelemesi gerekir.":
        "active high/urgent-priority reports require human review by authorised staff.",
    "Formda ad/soyad/sınıf istenmemeli ve kaydedilmemeli.": "The form must not request or store first name, last name or class.",
    "Her kayıt benzersiz ve tahmin edilmesi zor bir kod üretmeli.": "Each report must generate a unique, hard-to-guess code.",
    "Girişsiz, inceleme/istatistik/denetim kayıtları görünmemeli.": "Review, statistics and audit records must not be visible without signing in.",
    "Değişiklik kaydedilmeli, geçmişe işlemi yapanla birlikte eklenmeli.": "Changes must be saved and added to the activity history with the actor identified.",
    "Not kaydedilmeli; yazar bilgisiyle ilgili kayıtta görünmeli.": "Notes must be saved and displayed in the relevant report with the author's details.",
    "Açıklama veya onay yoksa kayıt oluşturulmamalı; yazılan metin silinmemeli.": "A report must not be created without a description or confirmation; entered text must not be erased.",
    "Yeni kurulumda örnek kayıt olmamalı; yeniden başlatmada kayıt silinmemeli.": "A fresh installation must not contain sample reports; restarting the app must not delete existing records.",
    "Grafik toplamları kayıt sayılarıyla uyumlu olmalı.": "Chart totals must match the report counts.",
    "Arayüz gerçek kişisel veri girilmemesi gerektiğini açıkça belirtmeli.": "The interface must clearly state that real personal data must not be entered.",
    "5 hatalı denemeden sonra giriş geçici olarak kilitlenmeli.": "Sign-in must be temporarily locked after five failed attempts.",
    "30 dakika hareketsizlikte yönetici oturumu kapanmalı.": "The administrator session must expire after 30 minutes of inactivity.",
    "Açıklamaya yazılan telefon/T.C. no/e-posta/IBAN kayıtta maskeli olmalı.": "Phone numbers, Turkish ID numbers, email addresses and IBANs entered in a description must be masked in storage.",
    "Sorgu yalnızca durum ve tarih göstermeli; açıklama/not göstermemeli.": "A status lookup must show only the status and date; it must not display the description or notes.",
    "Kimlik alanları varsayılan olarak dışarıda olmalı; işlem denetim kaydına yazılmalı.": "Identifying fields must be excluded by default; the export action must be recorded in the audit log.",
    "İncelemeyle ilgili kısa not ekleyin.": "Add a brief note about the review.",
    "Açıklama veya onay yoksa kayıt oluşturulmamalı; yazılan metin silinmemeli.": "A report must not be created without a description or confirmation; entered text must not be erased.",
    "KVKK (6698): veri sorumlusunun belirlenmesi, aydınlatma metni, hukuki sebep/veli onayı, saklama-imha politikası,":
        "KVKK (Law No. 6698): identify the data controller, prepare a privacy notice, establish the legal basis and parental-consent requirements, and define retention and deletion policies,",
    "gerekiyorsa VERBİS ve veri işleyen sözleşmeleri. Çocuk verisi ve olası yurt dışı sunucu kullanımı (ör. bulut barındırma)":
        "and, where required, VERBIS registration and data-processing agreements. Children's data and any use of servers abroad (for example, cloud hosting)",
    "ayrıca hukuki değerlendirme gerektirir.": "also require legal assessment.",
    "Yasal bildirim yükümlülükleri: çocuğa yönelik istismar/şiddet şüphesinde mevzuattaki bildirim yükümlülükleri bu":
        "Legal reporting obligations: where there is suspicion of abuse or violence against a child, statutory reporting duties apply independently of this platform's",
    "uygulamanın kayıt akışından bağımsızdır; okul yönetimi ve hukuk danışmanıyla netleştirilmelidir.":
        "reporting workflow and must be clarified with the school administration and legal counsel.",
    "Erişim: kişi bazlı hesaplar, rol ayrımı, iki aşamalı doğrulama, parola özeti (`tools/parola_hash.py`).":
        "Access: individual accounts, role-based permissions, two-factor authentication and password hashing (`tools/parola_hash.py`).",
    "Okul süreci: kayıtları kimin, ne kadar sürede inceleyeceği, acil durum protokolü ve rehberlik servisiyle iş akışı.":
        "School procedures: define who reviews reports and within what timeframe, the emergency protocol and the workflow with the guidance service.",
    "1. **Amaç:** Bildirim sürecinin anlaşılırlığını, temel işlevlerin doğruluğunu ve kural tabanlı sinyalin ölçülebilir":
        "1. **Purpose:** Evaluate the clarity of the reporting process, the correctness of core functions and the measurable performance of rule-based signals.",
    "başarımını raporlamak.": "report their performance.",
    "2. **Algılayıcı:** Makine öğrenmesi içermez; Türkçe'ye duyarlı normalleştirme (İ/ı, ASCII katlama), kelime başı sınırı,":
        "2. **Detector:** Does not use machine learning; it uses Turkish-aware normalisation (İ/ı handling and ASCII folding), word-boundary checks,",
    "harf tekrarı/ayraç/rakamla yazım çözümü ve kategori+ağırlık tabanlı öncelik kuralı kullanır.":
        "repeated-letter, separator and digit-substitution handling, and a category-and-weight-based priority rule.",
    "3. **Ölçüt:** Kesinlik, duyarlılık, F1 ve kategori bazlı yakalama; ayrıca \"zor örnek\" kümesiyle bilinen sınırlılıklar.":
        "3. **Metrics:** Precision, recall, F1 and category-level detection, alongside known limitations assessed using a 'challenging examples' set.",
    "4. **Sınırlılıklar:** Bağlam, ironi, imâ ve ima yoluyla dışlama yakalanmaz; deyimsel abartı (\"babam beni öldürecek\")":
        "4. **Limitations:** Context, irony and indirect exclusion may not be detected; figurative exaggeration may produce false positives,",
    "yanlış alarm üretir; yazım hataları (\"apdal\") kaçar; sözlük küçüktür.":
        "spelling variations may be missed, and the phrase dictionary is limited.",
    "5. **Yol haritası:** (a) etik kurul/okul izniyle, kimliksizleştirilmiş ve en az iki uzmanca etiketlenmiş veri kümesi,":
        "5. **Roadmap:** (a) an ethically approved, de-identified dataset labelled by at least two experts with school approval,",
    "(b) değerlendiriciler arası uyum (Cohen kappa), (c) eğitim/doğrulama/test ayrımı, (d) kural tabanlı yöntemin bir":
        "(b) inter-rater agreement (Cohen's kappa), (c) separate training, validation and test sets, (d) comparison of the rule-based method with a",
    "dil modeli veya sınıflandırıcı ile karşılaştırılması, (e) kullanılabilirlik testi (SUS ölçeği).":
        "language model or classifier, and (e) usability testing (System Usability Scale, SUS).",
    "6. **Etik:** Gerçek öğrenci verisi için önceden okul/veli onayı, gönüllülük, veri minimizasyonu ve güvenli saklama planı":
        "6. **Ethics:** Use of real student data requires prior school and parental approval, voluntary participation, data minimisation and a secure retention plan.",
    "gerekir. Bu uygulamada gerçek öğrenci verisi kullanmayın.": "Do not use real student data in this application.",
    "- Açıklamadaki telefon, T.C. kimlik numarası, e-posta ve IBAN'ı otomatik maskeler.":
        "- Automatically masks phone numbers, Turkish national ID numbers, email addresses and IBANs in descriptions.",
    "- Cihaz jetonu yalnızca özet olarak ve 1 gün saklanır; rapora bağlanmaz.": "- Only a hash of the device token is retained for one day; it is not linked to a report.",
    "- Öğrenci sorgusunda açıklama, not ve değerlendirme gösterilmez.": "- Student status checks do not display descriptions, notes or assessments.",
    "- Serbest metin kişileri dolaylı tanıtabilir; ‘tam anonim’ yerine ‘kimliksizleştirilmiş’ demek daha doğrudur.":
        "- Free text may indirectly identify people; 'de-identified' is more accurate than 'fully anonymous'.",
    "- Üçüncü kişilerin (şüpheli öğrenci) adı metinde geçebilir; maskeleme adları yakalamaz.":
        "- Third-party names (including a student who is the subject of a report) may appear in text; the masking layer does not detect names.",
    "- Barındırma yeri ve olası yurt dışı aktarım hukuken değerlendirilmelidir.": "- Hosting location and any potential international data transfer must be assessed legally.",
    "- Cihaz jetonu özeti: ertesi gün silinir.": "- Device-token hash: deleted the following day.",
    "- Giriş denemeleri: 7 gün.": "- Sign-in attempts: 7 days.",
    "Hakaret": "Insults", "Tehdit": "Threats", "Dışlama": "Exclusion", "Siber zorbalık": "Cyberbullying",
    "Akran dışlaması": "Peer exclusion", "Fiziksel zorbalık": "Physical bullying",
})


CATALOG.update({
    "Sınıf seçenekleri": "Class options", "Takip kodu": "Tracking code", "Yetkisiz erişim": "Unauthorised access",
    "İnceleme sırası": "Review prioritisation",
    "Durum güncelleme": "Status update", "Not geçmişi": "Note history", "Boş form": "Empty form",
    "Temiz başlangıç": "Clean installation", "Güvenli metin": "Safe text handling", "Hatalı giriş sınırı": "Failed sign-in limit",
    "Oturum zaman aşımı": "Session timeout", "Kişisel veri maskeleme": "Personal data masking",
    "Takip kodu sorgusu": "Tracking-code lookup", "CSV dışa aktarım": "CSV export", "Günlük kota": "Daily limit",
    "Ek bilgi": "Additional information", "9/A … 12/B seçenekleri görünmeli.": "Class options from 9/A to 12/B must be displayed.",
    "Proje:": "Project:", "Okul:": "School:", "Danışman öğretmen:": "Supervising teacher:",
    "[OKUL ADI]": "[SCHOOL NAME]", "[AD SOYAD]": "[FULL NAME]", "Tarih:": "Date:", "İmza:": "Signature:",
    "**Açıklama**": "**Description**", "**Olay türü**": "**Incident type**", "**Ortam**": "**Setting**",
    "**Yaklaşık zaman**": "**Approximate time**", "**Tekrarlanma**": "**Frequency**", "**Oluşturulma**": "**Created**",
    "**Bildirim türü**": "**Report type**", "**Kategoriler:**": "**Categories:**", "**Eşleşen ifadeler:**": "**Matched phrases:**",
})


CATALOG.update({
    "**KVKK (6698):**": "**KVKK (Law No. 6698):**",
    "veri sorumlusunun belirlenmesi, aydınlatma metni, hukuki sebep/veli onayı, saklama-imha politikası,":
        "identify the data controller, prepare a privacy notice, establish the legal basis and parental-consent requirements, and define retention and deletion policies,",
    "**Yasal bildirim yükümlülükleri:**": "**Statutory reporting obligations:**",
    "çocuğa yönelik istismar/şiddet şüphesinde mevzuattaki bildirim yükümlülükleri bu":
        "where there is suspicion of abuse or violence against a child, statutory reporting duties apply independently of this platform's",
    "**Erişim:**": "**Access:**", "kişi bazlı hesaplar, rol ayrımı, iki aşamalı doğrulama, parola özeti":
        "individual accounts, role-based permissions, two-factor authentication and password hashing",
    "**Okul süreci:**": "**School procedures:**",
    "kayıtları kimin, ne kadar sürede inceleyeceği, acil durum protokolü ve rehberlik servisiyle iş akışı.":
        "define who reviews reports and within what timeframe, the emergency protocol and the workflow with the guidance service.",
})


CATALOG.update({
    "saniye beklenir.": "seconds between entries.",
    "Cihaz jetonu geçersiz.": "The device token is invalid.",
    "Günlük bildirim hakkınız dolmuştur.": "You have reached the daily report limit.",
    "Bu kodla ek bilgi eklenebilecek bir bildirim bulunamadı.": "No report was found that can accept additional information with this code.",
    "Ek bilgi yalnızca bildirimin yapıldığı gün eklenebilir.": "Additional information can only be added on the day the report was submitted.",
    "Bu bildirim sonuçlandırıldığı için ek bilgi eklenemez.": "Additional information cannot be added because this report has been closed.",
    "Bugün en fazla 3 ek bilgi eklenebilir.": "You can add a maximum of three additional entries today.",
    "Yeni ek bilgi için yaklaşık": "Please wait approximately",
    "Yeni ek bilgi için yaklaşık {kalan} saniye beklemelisin.": "Please wait approximately {kalan} seconds before adding more information.",
    "Ek bilgi boş olamaz.": "Additional information cannot be empty.",
    "Ek bilgi en fazla 1000 karakter olabilir.": "Additional information must not exceed 1,000 characters.",
    "Bu kodla ek bilgi eklenebilecek bir bildirim bulunamadı.": "No report was found that can accept additional information with this code.",
    "Okul: [OKUL ADI]": "School: [SCHOOL NAME]", "Danışman öğretmen: [AD SOYAD]": "Supervising teacher: [FULL NAME]",
    "Öğrenci: Bilgilendirildim, gönüllü katılıyorum.": "Student: I have been informed and agree to participate voluntarily.",
    "Veli/Yasal temsilci: Bilgilendirildim, çocuğumun katılımına izin veriyorum.":
        "Parent/Legal guardian: I have been informed and give permission for my child's participation.",
})


CATALOG.update({
    "Proje:": "Project:", "Tarih:": "Date:", "İmza:": "Signature:",
    "telefon istenmez. Açıklamadaki": "phone numbers are not requested. The following information in descriptions",
    "Akran zorbalığı bildirimlerinin yetkili kişilerce incelenmesi ve öğrencinin korunması. Veriler başka amaçla kullanılmaz.":
        "To enable authorised staff to review peer-bullying reports and safeguard students. Data is not used for other purposes.",
    "size bağlamak mümkün olmadığından bazı haklar (erişim, düzeltme) teknik olarak kullanılamayabilir.":
        "it may not be technically possible to link a report to you, so certain rights (such as access and rectification) may not be exercisable.",
})


CATALOG.update({
    "Zaman": "Time", "Kullanıcı": "User", "İşlem": "Action", "Ayrıntı": "Details", "Yazar": "Author",
    "Yönetici girişi": "Administrator sign-in", "Başarısız giriş denemesi": "Failed sign-in attempt",
    "CSV dışa aktarım": "CSV export", "Oturum zaman aşımı": "Session timeout", "Oturum kapatıldı": "Session signed out",
    "Saklama süresi temizliği": "Retention cleanup", "Yeni bildirim oluşturuldu": "New report created",
    "Durum değiştirildi": "Status changed", "Birim ataması değiştirildi": "Team assignment changed",
    "İnceleme notu eklendi": "Review note added", "Anonim ek bilgi eklendi": "Additional information added anonymously",
})

CATALOG.update({
    "Veri yok": "No data", "Toplam bildirim": "Total reports", "Anonim oranı": "Anonymous share",
    "İlk işlem süresi (medyan)": "Time to first action (median)",
    "Sonuçlanma süresi (medyan)": "Time to closure (median)",
})

def _translate_tr_en(value: Any, language: str = EN) -> Any:
    """Translate known UI copy while leaving unknown/user-authored text intact."""
    if not isinstance(value, str) or language != EN:
        return value
    # Exact enum/label values are translated directly. For composed UI strings,
    # only longer phrases are replaced so short words such as "Acil" cannot
    # accidentally alter a student's free-text report.
    if value in CATALOG:
        return CATALOG[value]
    dynamic_patterns = (
        (r"^(\d+) saati aşan bekleyen$", lambda m: f"Awaiting review for over {m.group(1)} hours"),
        (r"^(\d+) günden eski sonuçlanmış kayıt \(silinecek\)$", lambda m: f"Closed reports older than {m.group(1)} days (to be deleted)"),
        (r"^(\d+) kayıt$", lambda m: f"{m.group(1)} reports"),
        (r"^Son (\d+) gün$", lambda m: f"Last {m.group(1)} days"),
        (r"^(\d+) kayıt silindi\.$", lambda m: f"{m.group(1)} reports deleted."),
        (r"^(\d+(?:[.,]\d+)?) saat bekliyor$", lambda m: f"waiting for {m.group(1)} hours"),
    )
    for pattern, render in dynamic_patterns:
        match = re.match(pattern, value)
        if match:
            return render(match)
    for source, target in sorted(CATALOG.items(), key=lambda item: len(item[0]), reverse=True):
        if len(source) < 9 and not (source.endswith(":") and len(source) >= 6):
            continue
        # Flexible whitespace also handles wrapped Markdown paragraphs and HTML.
        pattern = re.compile(r"\s+".join(re.escape(part) for part in source.split()))
        value = pattern.sub(lambda _m, replacement=target: replacement, value)
    return value


def _format_timestamp_tr_en(value: str | None, language: str = TR) -> str:
    """Format ISO-like database timestamps for display without changing stored values."""
    if not value:
        return "—"
    try:
        dt = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return value
    if language == EN:
        # Explicit month/AM-PM labels avoid dependence on the host OS locale.
        months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
        hour = dt.hour % 12 or 12
        meridiem = "AM" if dt.hour < 12 else "PM"
        return f"{months[dt.month - 1]} {dt.day:02d}, {dt.year} · {hour:02d}:{dt.minute:02d}:{dt.second:02d} {meridiem}"
    return f"{dt.day:02d}.{dt.month:02d}.{dt.year} · {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"


def _translate_structure_tr_en(value: Any, language: str = EN) -> Any:
    """Translate labels and known enum values in table-like structures, not free text."""
    if language != EN:
        return value
    if isinstance(value, dict):
        return {translate(k, language): translate_structure(v, language) for k, v in value.items()}
    if isinstance(value, list):
        return [translate_structure(v, language) for v in value]
    if isinstance(value, tuple):
        return tuple(translate_structure(v, language) for v in value)
    if isinstance(value, str):
        # Table cells may contain controlled audit labels/status transitions. Unknown
        # free-text values (including descriptions) remain unchanged.
        return translate(value, language)
    return value


# ---------------------------------------------------------------------------
# Multi-language catalogue (TR / EN / DE / FR / ES / AR / AZ)
# ---------------------------------------------------------------------------
LANGUAGES = {
    "Türkçe": {"code": "tr", "locale": "tr_TR", "direction": "ltr"},
    "English": {"code": "en", "locale": "en_GB", "direction": "ltr"},
    "Deutsch": {"code": "de", "locale": "de_DE", "direction": "ltr"},
    "Français": {"code": "fr", "locale": "fr_FR", "direction": "ltr"},
    "Español": {"code": "es", "locale": "es_ES", "direction": "ltr"},
    "العربية": {"code": "ar", "locale": "ar", "direction": "rtl"},
    "Azərbaycan dili": {"code": "az", "locale": "az_AZ", "direction": "ltr"},
}
CURRENT_LANGUAGE = TR

def set_language(language: str) -> None:
    """Set the language for helper calls made without an explicit language."""
    global CURRENT_LANGUAGE
    CURRENT_LANGUAGE = language if language in LANGUAGES else TR

# Reviewed core interface terminology. Keys are the canonical Turkish UI strings.
# User-authored report descriptions, notes and names are intentionally never translated.
MULTI_CATALOG: dict[str, dict[str, str]] = {
"Deutsch": {
"Genel bakış":"Übersicht","Yeni bildirim":"Neue Meldung","Bildirim sorgula":"Meldung verfolgen","Destek rehberi":"Unterstützungsleitfaden","Yönetici girişi":"Administrator-Anmeldung","Bildirim inceleme":"Meldungsprüfung","İstatistikler":"Statistiken","Trend ve ortam":"Trends und Kontext","Gizlilik ve KVKK":"Datenschutz","Araştırma ve test":"Forschung und Tests","Güvenli kullanım":"Sichere Nutzung","Oturumu kapat":"Abmelden","Kullanıcı adı":"Benutzername","Parola":"Passwort","Giriş yap":"Anmelden","Dil / Language":"Sprache / Language","Türkçe":"Türkisch","English":"Englisch","Güvenli bir okul, herkesin hakkı.":"Eine sichere Schule ist das Recht aller.","Ne oldu?":"Was ist passiert?","Nerede oldu?":"Wo ist es passiert?","Ne zaman oldu?":"Wann ist es passiert?","Bu olay kaç kez yaşandı?":"Wie oft ist das passiert?","Olayı kendi cümlelerinle anlat":"Beschreibe den Vorfall mit eigenen Worten","Bildirimi gönder":"Meldung absenden","Durumu sorgula":"Status abfragen","Durumu göster":"Status anzeigen","Ek bilgi ekle":"Weitere Informationen hinzufügen","Bildirim inceleme alanına yalnızca yetkili kullanıcılar erişebilir.":"Nur autorisierte Personen können auf den Bereich zur Meldungsprüfung zugreifen.","İnceleme bekliyor":"Wird geprüft","İnceleniyor":"In Bearbeitung","Sonuçlandırıldı":"Abgeschlossen","Acil":"Dringend","Yüksek":"Hoch","Orta":"Mittel","Düşük":"Niedrig","GECİKMİŞ":"ÜBERFÄLLIG","Günlük Durum Özeti":"Tagesübersicht","Yeni bildirim":"Neue Meldung","Toplam kayıt":"Gesamtzahl der Einträge","Açık kayıt":"Offene Meldungen","Kayıt ara":"Meldung suchen","Öncelik sinyali":"Prioritätssignal","Başlangıç tarihi":"Startdatum","Bitiş tarihi":"Enddatum","Tümü":"Alle","Son 7 gün":"Letzte 7 Tage","Son 30 gün":"Letzte 30 Tage","En yeni önce":"Neueste zuerst","En eski önce":"Älteste zuerst","Rehberlik önerisi":"Empfehlung der Beratungsstelle","Güvenlik ilkeleri":"Sicherheitsgrundsätze","Açıklama":"Beschreibung","Olay türü":"Vorfallart","Ortam":"Umgebung","Oluşturulma":"Erstellt am","Son güncelleme":"Letzte Aktualisierung","Zaman":"Zeit","Kullanıcı":"Benutzer","İşlem":"Aktion","Ayrıntı":"Details","Yazar":"Verfasser","Kaydet":"Speichern","Durumu kaydet":"Status speichern","Not ekle":"Not hinzufügen","İnceleme bilgileri kaydedildi.":"Prüfinformationen wurden gespeichert.","Kullanıcı adı veya parola yanlış.":"Benutzername oder Passwort ist falsch.","Yönetici erişimi gerekli":"Administratorzugriff erforderlich","Bu bölümü görüntülemek için yönetici oturumu açın.":"Melden Sie sich als Administrator an, um diesen Bereich anzuzeigen.","Telefon, T.C. no, e-posta ve IBAN otomatik gizlenir.":"Telefonnummern, türkische ID-Nummern, E-Mail-Adressen und IBANs werden automatisch maskiert.","Acil bir tehlike varsa beklemeyin:":"Warten Sie bei unmittelbarer Gefahr nicht:","Sinyal, karar değil":"Ein Signal ist keine Entscheidung","Yetkili kişiler kaydı inceler. Kararı makine vermez.":"Autorisierte Personen prüfen die Meldung. Das System trifft keine Entscheidung.","Güvenli kullanım":"Sichere Nutzung","Gizlilik":"Datenschutz","Hakaret":"Beleidigung","Tehdit":"Drohung","Dışlama":"Ausgrenzung","Siber zorbalık":"Cybermobbing","Akran dışlaması":"Ausgrenzung unter Gleichaltrigen","Fiziksel zorbalık":"Körperliches Mobbing","Sınıfta":"Im Klassenraum","Okul bahçesinde":"Auf dem Schulhof","Koridorda":"Im Flur","Sosyal medyada":"In sozialen Medien","Mesajlaşmada":"Beim Messaging","Bugün":"Heute","Dün":"Gestern","Bu hafta":"Diese Woche","Daha önce":"Früher","Emin değilim":"Ich bin mir nicht sicher","Bir kez":"Einmal","Birkaç kez":"Mehrmals","Birden fazla kez":"Mehr als einmal","Gizli takip kodu":"Vertraulicher Tracking-Code","Açıklama yalnızca boşluk veya noktalama işaretlerinden oluşamaz. Kısaca ne olduğunu yaz.":"Die Beschreibung darf nicht nur aus Leerzeichen oder Satzzeichen bestehen. Beschreiben Sie kurz, was passiert ist.","Lütfen onay kutusunu işaretle.":"Bitte aktivieren Sie das Bestätigungsfeld.","Bildirimin kaydedildi. Teşekkür ederiz.":"Ihre Meldung wurde gespeichert. Vielen Dank.","Bu kodla eşleşen bir kayıt bulunamadı. Kodu kontrol edip tekrar dene.":"Zu diesem Code wurde kein Eintrag gefunden. Bitte überprüfen Sie den Code.","Ek bilgi boş olamaz.":"Weitere Informationen dürfen nicht leer sein.","Acil bir durum değil, yalnızca bilgi vermek istiyorum.":"",},
"Français": {
"Genel bakış":"Vue d’ensemble","Yeni bildirim":"Nouveau signalement","Bildirim sorgula":"Suivre un signalement","Destek rehberi":"Guide d’accompagnement","Yönetici girişi":"Connexion administrateur","Bildirim inceleme":"Examen des signalements","İstatistikler":"Statistiques","Trend ve ortam":"Tendances et contexte","Gizlilik ve KVKK":"Confidentialité et protection des données","Araştırma ve test":"Recherche et tests","Güvenli kullanım":"Utilisation sûre","Oturumu kapat":"Se déconnecter","Kullanıcı adı":"Nom d’utilisateur","Parola":"Mot de passe","Giriş yap":"Se connecter","Dil / Language":"Langue / Language","Türkçe":"Turc","English":"Anglais","Güvenli bir okul, herkesin hakkı.":"Une école sûre est un droit pour toutes et tous.","Ne oldu?":"Que s’est-il passé ?","Nerede oldu?":"Où cela s’est-il passé ?","Ne zaman oldu?":"Quand cela s’est-il passé ?","Bu olay kaç kez yaşandı?":"Combien de fois cela s’est-il produit ?","Olayı kendi cümlelerinle anlat":"Décrivez les faits avec vos propres mots","Bildirimi gönder":"Envoyer le signalement","Durumu sorgula":"Consulter le statut","Durumu göster":"Afficher le statut","Ek bilgi ekle":"Ajouter des informations","Bildirim inceleme alanına yalnızca yetkili kullanıcılar erişebilir.":"Seules les personnes autorisées peuvent accéder à l’espace d’examen des signalements.","İnceleme bekliyor":"En attente d’examen","İnceleniyor":"En cours d’examen","Sonuçlandırıldı":"Clôturé","Acil":"Urgent","Yüksek":"Élevé","Orta":"Moyen","Düşük":"Faible","GECİKMİŞ":"EN RETARD","Günlük Durum Özeti":"Résumé quotidien","Toplam kayıt":"Nombre total de dossiers","Açık kayıt":"Dossiers ouverts","Kayıt ara":"Rechercher un dossier","Öncelik sinyali":"Indicateur de priorité","Başlangıç tarihi":"Date de début","Bitiş tarihi":"Date de fin","Tümü":"Tout","Son 7 gün":"7 derniers jours","Son 30 gün":"30 derniers jours","En yeni önce":"Du plus récent au plus ancien","En eski önce":"Du plus ancien au plus récent","Rehberlik önerisi":"Conseil du service d’accompagnement","Güvenlik ilkeleri":"Principes de sécurité","Açıklama":"Description","Olay türü":"Type d’incident","Ortam":"Lieu","Oluşturulma":"Créé le","Son güncelleme":"Dernière mise à jour","Zaman":"Date et heure","Kullanıcı":"Utilisateur","İşlem":"Action","Ayrıntı":"Détails","Yazar":"Auteur","Kaydet":"Enregistrer","Durumu kaydet":"Enregistrer le statut","Not ekle":"Ajouter une note","İnceleme bilgileri kaydedildi.":"Les informations d’examen ont été enregistrées.","Kullanıcı adı veya parola yanlış.":"Le nom d’utilisateur ou le mot de passe est incorrect.","Yönetici erişimi gerekli":"Accès administrateur requis","Bu bölümü görüntülemek için yönetici oturumu açın.":"Connectez-vous en tant qu’administrateur pour consulter cette section.","Telefon, T.C. no, e-posta ve IBAN otomatik gizlenir.":"Les numéros de téléphone, numéros d’identité turcs, adresses e-mail et IBAN sont automatiquement masqués.","Acil bir tehlike varsa beklemeyin:":"En cas de danger immédiat, n’attendez pas :","Sinyal, karar değil":"Un signal n’est pas une décision","Yetkili kişiler kaydı inceler. Kararı makine vermez.":"Les personnes autorisées examinent le signalement. Le système ne prend aucune décision.","Gizlilik":"Confidentialité","Hakaret":"Insultes","Tehdit":"Menaces","Dışlama":"Exclusion","Siber zorbalık":"Cyberharcèlement","Akran dışlaması":"Exclusion entre pairs","Fiziksel zorbalık":"Harcèlement physique","Sınıfta":"En classe","Okul bahçesinde":"Dans la cour de l’école","Koridorda":"Dans le couloir","Sosyal medyada":"Sur les réseaux sociaux","Mesajlaşmada":"Dans les messageries","Bugün":"Aujourd’hui","Dün":"Hier","Bu hafta":"Cette semaine","Daha önce":"Auparavant","Emin değilim":"Je ne sais pas","Bir kez":"Une fois","Birkaç kez":"Plusieurs fois","Birden fazla kez":"Plus d’une fois","Gizli takip kodu":"Code de suivi confidentiel","Lütfen onay kutusunu işaretle.":"Veuillez cocher la case de confirmation.","Bildirimin kaydedildi. Teşekkür ederiz.":"Votre signalement a été enregistré. Merci.","Bu kodla eşleşen bir kayıt bulunamadı. Kodu kontrol edip tekrar dene.":"Aucun dossier ne correspond à ce code. Vérifiez le code.","Ek bilgi boş olamaz.":"Les informations complémentaires ne peuvent pas être vides."},
"Español": {
"Genel bakış":"Resumen","Yeni bildirim":"Nuevo reporte","Bildirim sorgula":"Consultar un reporte","Destek rehberi":"Guía de apoyo","Yönetici girişi":"Acceso de administración","Bildirim inceleme":"Revisión de reportes","İstatistikler":"Estadísticas","Trend ve ortam":"Tendencias y contexto","Gizlilik ve KVKK":"Privacidad y protección de datos","Araştırma ve test":"Investigación y pruebas","Güvenli kullanım":"Uso seguro","Oturumu kapat":"Cerrar sesión","Kullanıcı adı":"Nombre de usuario","Parola":"Contraseña","Giriş yap":"Iniciar sesión","Dil / Language":"Idioma / Language","Türkçe":"Turco","English":"Inglés","Güvenli bir okul, herkesin hakkı.":"Una escuela segura es un derecho de todas las personas.","Ne oldu?":"¿Qué ocurrió?","Nerede oldu?":"¿Dónde ocurrió?","Ne zaman oldu?":"¿Cuándo ocurrió?","Bu olay kaç kez yaşandı?":"¿Cuántas veces ha ocurrido?","Olayı kendi cümlelerinle anlat":"Describe lo ocurrido con tus propias palabras","Bildirimi gönder":"Enviar reporte","Durumu sorgula":"Consultar estado","Durumu göster":"Mostrar estado","Ek bilgi ekle":"Añadir información","Bildirim inceleme alanına yalnızca yetkili kullanıcılar erişebilir.":"Solo el personal autorizado puede acceder al área de revisión de reportes.","İnceleme bekliyor":"Pendiente de revisión","İnceleniyor":"En revisión","Sonuçlandırıldı":"Cerrado","Acil":"Urgente","Yüksek":"Alta","Orta":"Media","Düşük":"Baja","GECİKMİŞ":"ATRASADO","Günlük Durum Özeti":"Resumen diario","Toplam kayıt":"Total de registros","Açık kayıt":"Reportes abiertos","Kayıt ara":"Buscar un registro","Öncelik sinyali":"Indicador de prioridad","Başlangıç tarihi":"Fecha de inicio","Bitiş tarihi":"Fecha de finalización","Tümü":"Todos","Son 7 gün":"Últimos 7 días","Son 30 gün":"Últimos 30 días","En yeni önce":"Más recientes primero","En eski önce":"Más antiguos primero","Rehberlik önerisi":"Recomendación de orientación","Güvenlik ilkeleri":"Principios de seguridad","Açıklama":"Descripción","Olay türü":"Tipo de incidente","Ortam":"Lugar","Oluşturulma":"Creado","Son güncelleme":"Última actualización","Zaman":"Fecha y hora","Kullanıcı":"Usuario","İşlem":"Acción","Ayrıntı":"Detalles","Yazar":"Autor","Kaydet":"Guardar","Durumu kaydet":"Guardar estado","Not ekle":"Añadir nota","İnceleme bilgileri kaydedildi.":"La información de revisión se ha guardado.","Kullanıcı adı veya parola yanlış.":"El nombre de usuario o la contraseña son incorrectos.","Yönetici erişimi gerekli":"Se requiere acceso de administración","Bu bölümü görüntülemek için yönetici oturumu açın.":"Inicia sesión como administrador para ver esta sección.","Telefon, T.C. no, e-posta ve IBAN otomatik gizlenir.":"Los teléfonos, números de identidad turcos, correos electrónicos e IBAN se ocultan automáticamente.","Acil bir tehlike varsa beklemeyin:":"Si existe un peligro inmediato, no esperes:","Sinyal, karar değil":"Una señal no es una decisión","Yetkili kişiler kaydı inceler. Kararı makine vermez.":"El personal autorizado revisa el reporte. El sistema no toma decisiones.","Gizlilik":"Privacidad","Hakaret":"Insultos","Tehdit":"Amenazas","Dışlama":"Exclusión","Siber zorbalık":"Ciberacoso","Akran dışlaması":"Exclusión entre compañeros","Fiziksel zorbalık":"Acoso físico","Sınıfta":"En el aula","Okul bahçesinde":"En el patio de la escuela","Koridorda":"En el pasillo","Sosyal medyada":"En redes sociales","Mesajlaşmada":"En aplicaciones de mensajería","Bugün":"Hoy","Dün":"Ayer","Bu hafta":"Esta semana","Daha önce":"Antes","Emin değilim":"No estoy seguro/a","Bir kez":"Una vez","Birkaç kez":"Varias veces","Birden fazla kez":"Más de una vez","Gizli takip kodu":"Código privado de seguimiento","Lütfen onay kutusunu işaretle.":"Marca la casilla de confirmación.","Bildirimin kaydedildi. Teşekkür ederiz.":"Tu reporte se ha guardado. Gracias.","Bu kodla eşleşen bir kayıt bulunamadı. Kodu kontrol edip tekrar dene.":"No se encontró ningún registro con este código. Comprueba el código.","Ek bilgi boş olamaz.":"La información adicional no puede estar vacía."},
"العربية": {
"Genel bakış":"نظرة عامة","Yeni bildirim":"بلاغ جديد","Bildirim sorgula":"متابعة بلاغ","Destek rehberi":"دليل الدعم","Yönetici girişi":"دخول المسؤول","Bildirim inceleme":"مراجعة البلاغات","İstatistikler":"الإحصاءات","Trend ve ortam":"الاتجاهات والسياق","Gizlilik ve KVKK":"الخصوصية وحماية البيانات","Araştırma ve test":"البحث والاختبار","Güvenli kullanım":"الاستخدام الآمن","Oturumu kapat":"تسجيل الخروج","Kullanıcı adı":"اسم المستخدم","Parola":"كلمة المرور","Giriş yap":"تسجيل الدخول","Dil / Language":"اللغة / Language","Türkçe":"التركية","English":"الإنجليزية","Güvenli bir okul, herkesin hakkı.":"المدرسة الآمنة حق للجميع.","Ne oldu?":"ماذا حدث؟","Nerede oldu?":"أين حدث ذلك؟","Ne zaman oldu?":"متى حدث ذلك؟","Bu olay kaç kez yaşandı?":"كم مرة حدث ذلك؟","Olayı kendi cümlelerinle anlat":"صف ما حدث بكلماتك الخاصة","Bildirimi gönder":"إرسال البلاغ","Durumu sorgula":"الاستعلام عن الحالة","Durumu göster":"عرض الحالة","Ek bilgi ekle":"إضافة معلومات","Bildirim inceleme alanına yalnızca yetkili kullanıcılar erişebilir.":"يقتصر الوصول إلى قسم مراجعة البلاغات على الأشخاص المخوّلين.","İnceleme bekliyor":"بانتظار المراجعة","İnceleniyor":"قيد المراجعة","Sonuçlandırıldı":"مغلق","Acil":"عاجل","Yüksek":"مرتفع","Orta":"متوسط","Düşük":"منخفض","GECİKMİŞ":"متأخر","Günlük Durum Özeti":"الملخص اليومي للحالة","Toplam kayıt":"إجمالي السجلات","Açık kayıt":"البلاغات المفتوحة","Kayıt ara":"البحث عن سجل","Öncelik sinyali":"مؤشر الأولوية","Başlangıç tarihi":"تاريخ البداية","Bitiş tarihi":"تاريخ النهاية","Tümü":"الكل","Son 7 gün":"آخر 7 أيام","Son 30 gün":"آخر 30 يومًا","En yeni önce":"الأحدث أولاً","En eski önce":"الأقدم أولاً","Rehberlik önerisi":"توصية الإرشاد","Güvenlik ilkeleri":"مبادئ السلامة","Açıklama":"الوصف","Olay türü":"نوع الحادثة","Ortam":"المكان","Oluşturulma":"تاريخ الإنشاء","Son güncelleme":"آخر تحديث","Zaman":"الوقت","Kullanıcı":"المستخدم","İşlem":"الإجراء","Ayrıntı":"التفاصيل","Yazar":"الكاتب","Kaydet":"حفظ","Durumu kaydet":"حفظ الحالة","Not ekle":"إضافة ملاحظة","İnceleme bilgileri kaydedildi.":"تم حفظ معلومات المراجعة.","Kullanıcı adı veya parola yanlış.":"اسم المستخدم أو كلمة المرور غير صحيحة.","Yönetici erişimi gerekli":"يلزم وصول المسؤول","Bu bölümü görüntülemek için yönetici oturumu açın.":"يرجى تسجيل الدخول بصفتك مسؤولاً لعرض هذا القسم.","Telefon, T.C. no, e-posta ve IBAN otomatik gizlenir.":"تُخفى أرقام الهاتف وأرقام الهوية التركية وعناوين البريد الإلكتروني وأرقام IBAN تلقائيًا.","Acil bir tehlike varsa beklemeyin:":"في حال وجود خطر فوري، لا تنتظر:","Sinyal, karar değil":"المؤشر ليس قرارًا","Yetkili kişiler kaydı inceler. Kararı makine vermez.":"يراجع الأشخاص المخوّلون البلاغ. ولا يتخذ النظام القرار.","Gizlilik":"الخصوصية","Hakaret":"إهانات","Tehdit":"تهديدات","Dışlama":"إقصاء","Siber zorbalık":"تنمّر إلكتروني","Akran dışlaması":"إقصاء الأقران","Fiziksel zorbalık":"تنمّر جسدي","Sınıfta":"في الصف","Okul bahçesinde":"في ساحة المدرسة","Koridorda":"في الممر","Sosyal medyada":"على وسائل التواصل الاجتماعي","Mesajlaşmada":"في تطبيقات المراسلة","Bugün":"اليوم","Dün":"أمس","Bu hafta":"هذا الأسبوع","Daha önce":"سابقًا","Emin değilim":"لست متأكدًا","Bir kez":"مرة واحدة","Birkaç kez":"عدة مرات","Birden fazla kez":"أكثر من مرة","Gizli takip kodu":"رمز متابعة خاص","Lütfen onay kutusunu işaretle.":"يرجى تحديد مربع التأكيد.","Bildirimin kaydedildi. Teşekkür ederiz.":"تم حفظ البلاغ. شكرًا لك.","Bu kodla eşleşen bir kayıt bulunamadı. Kodu kontrol edip tekrar dene.":"لم يتم العثور على سجل بهذا الرمز. يرجى التحقق من الرمز.","Ek bilgi boş olamaz.":"لا يمكن ترك المعلومات الإضافية فارغة."},
"Azərbaycan dili": {
"Genel bakış":"Ümumi baxış","Yeni bildirim":"Yeni bildiriş","Bildirim sorgula":"Bildirişi izlə","Destek rehberi":"Dəstək bələdçisi","Yönetici girişi":"Administrator girişi","Bildirim inceleme":"Bildirişlərin yoxlanılması","İstatistikler":"Statistika","Trend ve ortam":"Trendlər və mühit","Gizlilik ve KVKK":"Məxfilik və şəxsi məlumatların qorunması","Araştırma ve test":"Tədqiqat və sınaq","Güvenli kullanım":"Təhlükəsiz istifadə","Oturumu kapat":"Sessiyanı bağla","Kullanıcı adı":"İstifadəçi adı","Parola":"Şifrə","Giriş yap":"Daxil ol","Dil / Language":"Dil / Language","Türkçe":"Türk dili","English":"İngilis dili","Güvenli bir okul, herkesin hakkı.":"Təhlükəsiz məktəb hər kəsin haqqıdır.","Ne oldu?":"Nə baş verdi?","Nerede oldu?":"Harada baş verdi?","Ne zaman oldu?":"Nə vaxt baş verdi?","Bu olay kaç kez yaşandı?":"Bu hadisə neçə dəfə baş verib?","Olayı kendi cümlelerinle anlat":"Baş verənləri öz sözlərinlə təsvir et","Bildirimi gönder":"Bildirişi göndər","Durumu sorgula":"Statusu yoxla","Durumu göster":"Statusu göstər","Ek bilgi ekle":"Əlavə məlumat əlavə et","Bildirim inceleme alanına yalnızca yetkili kullanıcılar erişebilir.":"Bildirişlərin yoxlanılması bölməsinə yalnız səlahiyyətli şəxslər daxil ola bilər.","İnceleme bekliyor":"Yoxlanılmağı gözləyir","İnceleniyor":"Yoxlanılır","Sonuçlandırıldı":"Tamamlandı","Acil":"Təcili","Yüksek":"Yüksək","Orta":"Orta","Düşük":"Aşağı","GECİKMİŞ":"GECİKİB","Günlük Durum Özeti":"Gündəlik vəziyyət xülasəsi","Toplam kayıt":"Ümumi qeyd sayı","Açık kayıt":"Açıq bildirişlər","Kayıt ara":"Qeydi axtar","Öncelik sinyali":"Prioritet göstəricisi","Başlangıç tarihi":"Başlanğıc tarixi","Bitiş tarihi":"Bitmə tarixi","Tümü":"Hamısı","Son 7 gün":"Son 7 gün","Son 30 gün":"Son 30 gün","En yeni önce":"Əvvəlcə ən yenilər","En eski önce":"Əvvəlcə ən köhnələr","Rehberlik önerisi":"Psixoloji dəstək tövsiyəsi","Güvenlik ilkeleri":"Təhlükəsizlik prinsipləri","Açıklama":"Təsvir","Olay türü":"Hadisə növü","Ortam":"Mühit","Oluşturulma":"Yaradılma tarixi","Son güncelleme":"Son yenilənmə","Zaman":"Vaxt","Kullanıcı":"İstifadəçi","İşlem":"Əməliyyat","Ayrıntı":"Təfərrüatlar","Yazar":"Müəllif","Kaydet":"Yadda saxla","Durumu kaydet":"Statusu yadda saxla","Not ekle":"Qeyd əlavə et","İnceleme bilgileri kaydedildi.":"Yoxlama məlumatları yadda saxlanıldı.","Kullanıcı adı veya parola yanlış.":"İstifadəçi adı və ya şifrə yanlışdır.","Yönetici erişimi gerekli":"Administrator girişi tələb olunur","Bu bölümü görüntülemek için yönetici oturumu açın.":"Bu bölməyə baxmaq üçün administrator kimi daxil olun.","Telefon, T.C. no, e-posta ve IBAN otomatik gizlenir.":"Telefon nömrələri, Türkiyə şəxsiyyət nömrələri, e-poçt ünvanları və IBAN avtomatik maskalanır.","Acil bir tehlike varsa beklemeyin:":"Təcili təhlükə varsa gözləməyin:","Sinyal, karar değil":"Siqnal qərar deyil","Yetkili kişiler kaydı inceler. Kararı makine vermez.":"Qeydi səlahiyyətli şəxslər yoxlayır. Qərarı sistem vermir.","Gizlilik":"Məxfilik","Hakaret":"Təhqir","Tehdit":"Təhdid","Dışlama":"Kənarlaşdırma","Siber zorbalık":"Kiberzorakılıq","Akran dışlaması":"Həmyaşıdların kənarlaşdırılması","Fiziksel zorbalık":"Fiziki zorakılıq","Sınıfta":"Sinifdə","Okul bahçesinde":"Məktəb həyətində","Koridorda":"Dəhlizdə","Sosyal medyada":"Sosial mediada","Mesajlaşmada":"Mesajlaşmada","Bugün":"Bu gün","Dün":"Dünən","Bu hafta":"Bu həftə","Daha önce":"Əvvəllər","Emin değilim":"Əmin deyiləm","Bir kez":"Bir dəfə","Birkaç kez":"Bir neçə dəfə","Birden fazla kez":"Bir dəfədən çox","Gizli takip kodu":"Məxfi izləmə kodu","Lütfen onay kutusunu işaretle.":"Zəhmət olmasa təsdiq xanasını işarələyin.","Bildirimin kaydedildi. Teşekkür ederiz.":"Bildirişiniz yadda saxlanıldı. Təşəkkür edirik.","Bu kodla eşleşen bir kayıt bulunamadı. Kodu kontrol edip tekrar dene.":"Bu kodla uyğun qeyd tapılmadı. Kodu yoxlayın.","Ek bilgi boş olamaz.":"Əlavə məlumat boş ola bilməz."}
}

# Expanded, reviewed UI coverage: form choices, safety notices, tracking and administration.
# These entries intentionally translate interface copy only, never submitted report text.
_EXPANDED_UI = {
"Deutsch": {
"Kimliğini vermeden bildir. Ad, sınıf veya telefon istenmez.":"Melde den Vorfall, ohne deine Identität anzugeben. Name, Klasse und Telefonnummer werden nicht abgefragt.",
"Ne oldu?":"Was ist passiert?", "Nerede oldu?":"Wo ist es passiert?", "Ne zaman oldu?":"Wann ist es passiert?",
"Bu olay kaç kez yaşandı?":"Wie oft ist das passiert?", "Olayı kendi cümlelerinle anlat":"Beschreibe den Vorfall mit eigenen Worten",
"Hakaret veya alay":"Beleidigung oder Verspottung", "Tehdit":"Bedrohung", "Dışlama":"Ausgrenzung",
"Dijital zorbalık":"Cybermobbing", "Fiziksel zorbalık şüphesi":"Verdacht auf körperliches Mobbing", "Diğer":"Sonstiges",
"Sınıfta":"Im Klassenzimmer", "Okul bahçesinde":"Auf dem Schulhof", "Koridorda":"Im Flur", "Sosyal medyada":"In sozialen Medien", "Mesajlaşmada":"In Messaging-Apps",
"Bugün":"Heute", "Dün":"Gestern", "Bu hafta":"Diese Woche", "Daha önce":"Früher", "Emin değilim":"Ich bin mir nicht sicher",
"Bir kez":"Einmal", "Birkaç kez":"Mehrmals", "Birden fazla kez":"Mehr als einmal",
"Acil bir durum değil, yalnızca bilgi vermek istiyorum.":"Es handelt sich nicht um einen Notfall; ich möchte lediglich etwas mitteilen.",
"Acil bir tehlike varsa beklemeyin:":"Warten Sie bei unmittelbarer Gefahr nicht:",
"112 Acil Çağrı Merkezi":"112 Notrufzentrale", "Günde bir bildirim hakkın var.":"Du kannst eine Meldung pro Tag einreichen.",
"Bu platform gerçek bir okul sistemine bağlı değildir. Gerçek kişisel veri girmeyin.":"Diese Plattform ist nicht mit einem echten Schulsystem verbunden. Gib keine echten personenbezogenen Daten ein.",
"Bildirimi gönder":"Meldung absenden", "Gizli takip kodun.":"Dein vertraulicher Nachverfolgungscode.",
"Durumu sorgula":"Status abfragen", "Durumu göster":"Status anzeigen", "Ek bilgi ekle":"Weitere Informationen hinzufügen",
"Ek bilgi boş olamaz.":"Zusätzliche Angaben dürfen nicht leer sein.", "Lütfen olayı anlat.":"Bitte beschreibe den Vorfall.",
"Lütfen onay kutusunu işaretle.":"Bitte aktiviere das Bestätigungsfeld.", "Bildirimin kaydedildi. Teşekkür ederiz.":"Deine Meldung wurde gespeichert. Vielen Dank.",
"Bu kodla eşleşen bir kayıt bulunamadı. Kodu kontrol edip tekrar dene.":"Zu diesem Code wurde kein Eintrag gefunden. Bitte überprüfe den Code.",
"Açıklama":"Beschreibung", "Olay türü":"Vorfallart", "Ortam":"Ort", "Tekrar durumu":"Häufigkeit", "İnceleme durumu":"Prüfstatus",
"İnceleme bekliyor":"Wartet auf Prüfung", "İnceleniyor":"Wird geprüft", "Sonuçlandırıldı":"Abgeschlossen",
"Öncelik sinyali":"Prioritätssignal", "Sorumlu birim":"Zuständige Stelle", "Durumu kaydet":"Status speichern", "Not ekle":"Not hinzufügen",
"Kayıt ara":"Eintrag suchen", "Tüm durumlar":"Alle Status", "Tüm birimler":"Alle Stellen", "Sıralama":"Sortierung",
"En yeni önce":"Neueste zuerst", "En eski önce":"Älteste zuerst", "Öncelik (yüksekten)":"Priorität (absteigend)",
"İnceleme bilgileri kaydedildi.":"Prüfinformationen wurden gespeichert.", "Değişiklik yapılmadı; bilgiler zaten güncel.":"Keine Änderung vorgenommen; die Angaben sind bereits aktuell.",
"Not kaydedildi.":"Die Notiz wurde gespeichert.", "Not kaydedilemedi.":"Die Notiz konnte nicht gespeichert werden.",
"Yönetici erişimi gerekli":"Administratorzugriff erforderlich", "Bu bölümü görüntülemek için yönetici oturumu açın.":"Melde dich als Administrator an, um diesen Bereich aufzurufen.",
"Kullanıcı adı veya parola yanlış.":"Benutzername oder Passwort ist falsch.", "Yönetici bilgileri ayarlanmamış.":"Die Administrator-Zugangsdaten wurden nicht eingerichtet.",
"Günlük Durum Özeti":"Tagesübersicht", "Bugünkü yeni bildirim":"Neue Meldungen heute", "Aktif yüksek/acil":"Aktive Meldungen mit hoher/dringender Priorität",
"İnceleme bekleyen":"Ausstehende Prüfungen", "Toplam kayıt":"Gesamtzahl der Einträge", "Açık kayıt":"Offene Meldungen",
"İstatistikler":"Statistiken", "Grafikler yalnızca bu uygulamada kayıtlı bilgileri özetler; okul geneline ilişkin sonuç göstermez.":"Die Diagramme fassen nur die in dieser Anwendung gespeicherten Angaben zusammen; sie erlauben keine Rückschlüsse auf die gesamte Schule.",
"Sinyal, karar değil":"Ein Signal ist keine Entscheidung", "Yetkili kişiler kaydı inceler. Kararı makine vermez.":"Autorisierte Personen prüfen die Meldung. Das System trifft keine Entscheidung.",
"Telefon, T.C. no, e-posta ve IBAN otomatik gizlenir.":"Telefonnummern, türkische ID-Nummern, E-Mail-Adressen und IBAN werden automatisch maskiert.",
"Destek rehberi":"Unterstützungsleitfaden", "Gizlilik ve KVKK paneli":"Datenschutzbereich", "Araştırma ve kalite kontrol":"Forschung und Qualitätssicherung",
},
"Français": {
"Kimliğini vermeden bildir. Ad, sınıf veya telefon istenmez.":"Faites un signalement sans révéler votre identité. Aucun nom, classe ou numéro de téléphone n’est demandé.",
"Ne oldu?":"Que s’est-il passé ?", "Nerede oldu?":"Où cela s’est-il passé ?", "Ne zaman oldu?":"Quand cela s’est-il passé ?",
"Bu olay kaç kez yaşandı?":"Combien de fois cela s’est-il produit ?", "Olayı kendi cümlelerinle anlat":"Décrivez les faits avec vos propres mots",
"Hakaret veya alay":"Insultes ou moqueries", "Tehdit":"Menaces", "Dışlama":"Exclusion", "Dijital zorbalık":"Cyberharcèlement", "Fiziksel zorbalık şüphesi":"Suspicion de harcèlement physique", "Diğer":"Autre",
"Sınıfta":"En classe", "Okul bahçesinde":"Dans la cour de l’école", "Koridorda":"Dans le couloir", "Sosyal medyada":"Sur les réseaux sociaux", "Mesajlaşmada":"Dans les applications de messagerie",
"Bugün":"Aujourd’hui", "Dün":"Hier", "Bu hafta":"Cette semaine", "Daha önce":"Auparavant", "Emin değilim":"Je ne sais pas",
"Bir kez":"Une fois", "Birkaç kez":"Plusieurs fois", "Birden fazla kez":"Plus d’une fois",
"Acil bir durum değil, yalnızca bilgi vermek istiyorum.":"Il ne s’agit pas d’une urgence ; je souhaite simplement transmettre une information.",
"Acil bir tehlike varsa beklemeyin:":"En cas de danger immédiat, n’attendez pas :",
"Günde bir bildirim hakkın var.":"Vous pouvez envoyer un signalement par jour.",
"Bu platform gerçek bir okul sistemine bağlı değildir. Gerçek kişisel veri girmeyin.":"Cette plateforme n’est pas reliée à un véritable système scolaire. N’y saisissez aucune donnée personnelle réelle.",
"Bildirimi gönder":"Envoyer le signalement", "Gizli takip kodun.":"Votre code de suivi confidentiel.",
"Durumu sorgula":"Consulter le statut", "Durumu göster":"Afficher le statut", "Ek bilgi ekle":"Ajouter des informations",
"Ek bilgi boş olamaz.":"Les informations complémentaires ne peuvent pas être vides.", "Lütfen olayı anlat.":"Veuillez décrire les faits.",
"Lütfen onay kutusunu işaretle.":"Veuillez cocher la case de confirmation.", "Bildirimin kaydedildi. Teşekkür ederiz.":"Votre signalement a été enregistré. Merci.",
"Bu kodla eşleşen bir kayıt bulunamadı. Kodu kontrol edip tekrar dene.":"Aucun dossier ne correspond à ce code. Veuillez vérifier le code.",
"Açıklama":"Description", "Olay türü":"Type d’incident", "Ortam":"Lieu", "Tekrar durumu":"Fréquence", "İnceleme durumu":"Statut de l’examen",
"İnceleme bekliyor":"En attente d’examen", "İnceleniyor":"En cours d’examen", "Sonuçlandırıldı":"Clôturé",
"Öncelik sinyali":"Indicateur de priorité", "Sorumlu birim":"Service responsable", "Durumu kaydet":"Enregistrer le statut", "Not ekle":"Ajouter une note",
"Kayıt ara":"Rechercher un dossier", "Tüm durumlar":"Tous les statuts", "Tüm birimler":"Tous les services", "Sıralama":"Tri",
"En yeni önce":"Du plus récent au plus ancien", "En eski önce":"Du plus ancien au plus récent", "Öncelik (yüksekten)":"Priorité (de la plus élevée à la plus faible)",
"İnceleme bilgileri kaydedildi.":"Les informations d’examen ont été enregistrées.", "Değişiklik yapılmadı; bilgiler zaten güncel.":"Aucune modification : les informations sont déjà à jour.",
"Not kaydedildi.":"La note a été enregistrée.", "Not kaydedilemedi.":"La note n’a pas pu être enregistrée.",
"Yönetici erişimi gerekli":"Accès administrateur requis", "Bu bölümü görüntülemek için yönetici oturumu açın.":"Connectez-vous en tant qu’administrateur pour consulter cette rubrique.",
"Kullanıcı adı veya parola yanlış.":"Le nom d’utilisateur ou le mot de passe est incorrect.", "Yönetici bilgileri ayarlanmamış.":"Les identifiants administrateur n’ont pas été configurés.",
"Günlük Durum Özeti":"Synthèse quotidienne", "Bugünkü yeni bildirim":"Nouveaux signalements aujourd’hui", "Aktif yüksek/acil":"Signalements actifs à priorité élevée/urgente",
"İnceleme bekleyen":"En attente d’examen", "Toplam kayıt":"Nombre total de dossiers", "Açık kayıt":"Dossiers ouverts",
"İstatistikler":"Statistiques", "Grafikler yalnızca bu uygulamada kayıtlı bilgileri özetler; okul geneline ilişkin sonuç göstermez.":"Les graphiques résument uniquement les informations enregistrées dans cette application ; ils ne décrivent pas l’ensemble de l’établissement.",
"Sinyal, karar değil":"Un signal n’est pas une décision", "Yetkili kişiler kaydı inceler. Kararı makine vermez.":"Les personnes habilitées examinent le signalement. Le système ne prend aucune décision.",
"Telefon, T.C. no, e-posta ve IBAN otomatik gizlenir.":"Les numéros de téléphone, numéros d’identité turcs, adresses e-mail et IBAN sont automatiquement masqués.",
"Destek rehberi":"Guide d’accompagnement", "Gizlilik ve KVKK paneli":"Espace confidentialité et protection des données", "Araştırma ve kalite kontrol":"Recherche et assurance qualité",
},
"Español": {
"Kimliğini vermeden bildir. Ad, sınıf veya telefon istenmez.":"Envía un aviso sin revelar tu identidad. No se solicita tu nombre, curso ni número de teléfono.",
"Ne oldu?":"¿Qué ha ocurrido?", "Nerede oldu?":"¿Dónde ocurrió?", "Ne zaman oldu?":"¿Cuándo ocurrió?",
"Bu olay kaç kez yaşandı?":"¿Cuántas veces ha ocurrido?", "Olayı kendi cümlelerinle anlat":"Describe lo ocurrido con tus propias palabras",
"Hakaret veya alay":"Insultos o burlas", "Tehdit":"Amenazas", "Dışlama":"Exclusión", "Dijital zorbalık":"Ciberacoso", "Fiziksel zorbalık şüphesi":"Sospecha de acoso físico", "Diğer":"Otro",
"Sınıfta":"En el aula", "Okul bahçesinde":"En el patio del colegio", "Koridorda":"En el pasillo", "Sosyal medyada":"En las redes sociales", "Mesajlaşmada":"En aplicaciones de mensajería",
"Bugün":"Hoy", "Dün":"Ayer", "Bu hafta":"Esta semana", "Daha önce":"Anteriormente", "Emin değilim":"No estoy seguro/a",
"Bir kez":"Una vez", "Birkaç kez":"Varias veces", "Birden fazla kez":"Más de una vez",
"Acil bir durum değil, yalnızca bilgi vermek istiyorum.":"No es una emergencia; solo quiero comunicar una situación.",
"Acil bir tehlike varsa beklemeyin:":"Si existe un peligro inmediato, no esperes:",
"Günde bir bildirim hakkın var.":"Puedes enviar un aviso al día.",
"Bu platform gerçek bir okul sistemine bağlı değildir. Gerçek kişisel veri girmeyin.":"Esta plataforma no está conectada a un sistema escolar real. No introduzcas datos personales reales.",
"Bildirimi gönder":"Enviar aviso", "Gizli takip kodun.":"Tu código confidencial de seguimiento.",
"Durumu sorgula":"Consultar el estado", "Durumu göster":"Mostrar estado", "Ek bilgi ekle":"Añadir información adicional",
"Ek bilgi boş olamaz.":"La información adicional no puede estar vacía.", "Lütfen olayı anlat.":"Describe lo ocurrido, por favor.",
"Lütfen onay kutusunu işaretle.":"Marca la casilla de confirmación, por favor.", "Bildirimin kaydedildi. Teşekkür ederiz.":"Tu aviso se ha registrado. Gracias.",
"Bu kodla eşleşen bir kayıt bulunamadı. Kodu kontrol edip tekrar dene.":"No se ha encontrado ningún registro con ese código. Comprueba el código.",
"Açıklama":"Descripción", "Olay türü":"Tipo de incidente", "Ortam":"Lugar", "Tekrar durumu":"Frecuencia", "İnceleme durumu":"Estado de revisión",
"İnceleme bekliyor":"Pendiente de revisión", "İnceleniyor":"En revisión", "Sonuçlandırıldı":"Cerrado",
"Öncelik sinyali":"Indicador de prioridad", "Sorumlu birim":"Equipo responsable", "Durumu kaydet":"Guardar estado", "Not ekle":"Añadir nota",
"Kayıt ara":"Buscar registro", "Tüm durumlar":"Todos los estados", "Tüm birimler":"Todos los equipos", "Sıralama":"Ordenar",
"En yeni önce":"Más recientes primero", "En eski önce":"Más antiguos primero", "Öncelik (yüksekten)":"Prioridad (de mayor a menor)",
"İnceleme bilgileri kaydedildi.":"La información de revisión se ha guardado.", "Değişiklik yapılmadı; bilgiler zaten güncel.":"No se realizaron cambios; la información ya está actualizada.",
"Not kaydedildi.":"La nota se ha guardado.", "Not kaydedilemedi.":"No se pudo guardar la nota.",
"Yönetici erişimi gerekli":"Se requiere acceso de administración", "Bu bölümü görüntülemek için yönetici oturumu açın.":"Inicia sesión como administrador para ver esta sección.",
"Kullanıcı adı veya parola yanlış.":"El nombre de usuario o la contraseña son incorrectos.", "Yönetici bilgileri ayarlanmamış.":"No se han configurado las credenciales de administración.",
"Günlük Durum Özeti":"Resumen diario", "Bugünkü yeni bildirim":"Avisos nuevos de hoy", "Aktif yüksek/acil":"Avisos activos de prioridad alta/urgente",
"İnceleme bekleyen":"Pendientes de revisión", "Toplam kayıt":"Total de registros", "Açık kayıt":"Avisos abiertos",
"İstatistikler":"Estadísticas", "Grafikler yalnızca bu uygulamada kayıtlı bilgileri özetler; okul geneline ilişkin sonuç göstermez.":"Los gráficos resumen únicamente los datos registrados en esta aplicación; no representan a todo el centro educativo.",
"Sinyal, karar değil":"Una señal no es una decisión", "Yetkili kişiler kaydı inceler. Kararı makine vermez.":"El personal autorizado revisa el aviso. El sistema no toma decisiones.",
"Telefon, T.C. no, e-posta ve IBAN otomatik gizlenir.":"Los teléfonos, números de identidad turcos, correos electrónicos e IBAN se ocultan automáticamente.",
"Destek rehberi":"Guía de apoyo", "Gizlilik ve KVKK paneli":"Panel de privacidad y protección de datos", "Araştırma ve kalite kontrol":"Investigación y control de calidad",
},
"العربية": {
"Kimliğini vermeden bildir. Ad, sınıf veya telefon istenmez.":"قدّم بلاغًا دون الكشف عن هويتك. لا يُطلب اسمك أو صفك أو رقم هاتفك.",
"Ne oldu?":"ماذا حدث؟", "Nerede oldu?":"أين حدث ذلك؟", "Ne zaman oldu?":"متى حدث ذلك؟",
"Bu olay kaç kez yaşandı?":"كم مرة حدث ذلك؟", "Olayı kendi cümlelerinle anlat":"صِف ما حدث بكلماتك الخاصة",
"Hakaret veya alay":"إهانة أو سخرية", "Tehdit":"تهديد", "Dışlama":"إقصاء", "Dijital zorbalık":"تنمّر إلكتروني", "Fiziksel zorbalık şüphesi":"اشتباه في تنمّر جسدي", "Diğer":"أخرى",
"Sınıfta":"في الفصل الدراسي", "Okul bahçesinde":"في ساحة المدرسة", "Koridorda":"في الممر", "Sosyal medyada":"على وسائل التواصل الاجتماعي", "Mesajlaşmada":"في تطبيقات المراسلة",
"Bugün":"اليوم", "Dün":"أمس", "Bu hafta":"هذا الأسبوع", "Daha önce":"سابقًا", "Emin değilim":"لست متأكدًا",
"Bir kez":"مرة واحدة", "Birkaç kez":"عدة مرات", "Birden fazla kez":"أكثر من مرة",
"Acil bir durum değil, yalnızca bilgi vermek istiyorum.":"هذه ليست حالة طارئة؛ أريد فقط تقديم معلومة.",
"Acil bir tehlike varsa beklemeyin:":"إذا كان هناك خطر فوري، فلا تنتظر:",
"Günde bir bildirim hakkın var.":"يمكنك تقديم بلاغ واحد يوميًا.",
"Bu platform gerçek bir okul sistemine bağlı değildir. Gerçek kişisel veri girmeyin.":"هذه المنصة غير متصلة بنظام مدرسي فعلي. لا تُدخل بيانات شخصية حقيقية.",
"Bildirimi gönder":"إرسال البلاغ", "Gizli takip kodun.":"رمز المتابعة السري الخاص بك.",
"Durumu sorgula":"الاستعلام عن الحالة", "Durumu göster":"عرض الحالة", "Ek bilgi ekle":"إضافة معلومات إضافية",
"Ek bilgi boş olamaz.":"لا يمكن أن تكون المعلومات الإضافية فارغة.", "Lütfen olayı anlat.":"يرجى وصف ما حدث.",
"Lütfen onay kutusunu işaretle.":"يرجى تحديد مربع التأكيد.", "Bildirimin kaydedildi. Teşekkür ederiz.":"تم حفظ بلاغك. شكرًا لك.",
"Bu kodla eşleşen bir kayıt bulunamadı. Kodu kontrol edip tekrar dene.":"لم يتم العثور على بلاغ مطابق لهذا الرمز. يرجى التحقق من الرمز.",
"Açıklama":"الوصف", "Olay türü":"نوع الحادثة", "Ortam":"المكان", "Tekrar durumu":"معدل التكرار", "İnceleme durumu":"حالة المراجعة",
"İnceleme bekliyor":"بانتظار المراجعة", "İnceleniyor":"قيد المراجعة", "Sonuçlandırıldı":"مكتمل",
"Öncelik sinyali":"مؤشر الأولوية", "Sorumlu birim":"الجهة المسؤولة", "Durumu kaydet":"حفظ الحالة", "Not ekle":"إضافة ملاحظة",
"Kayıt ara":"البحث عن بلاغ", "Tüm durumlar":"جميع الحالات", "Tüm birimler":"جميع الجهات", "Sıralama":"الترتيب",
"En yeni önce":"الأحدث أولًا", "En eski önce":"الأقدم أولًا", "Öncelik (yüksekten)":"الأولوية (من الأعلى إلى الأقل)",
"İnceleme bilgileri kaydedildi.":"تم حفظ معلومات المراجعة.", "Değişiklik yapılmadı; bilgiler zaten güncel.":"لم يتم إجراء أي تغيير؛ المعلومات محدثة بالفعل.",
"Not kaydedildi.":"تم حفظ الملاحظة.", "Not kaydedilemedi.":"تعذّر حفظ الملاحظة.",
"Yönetici erişimi gerekli":"يلزم الوصول بصلاحية المسؤول", "Bu bölümü görüntülemek için yönetici oturumu açın.":"سجّل الدخول بصفتك مسؤولًا لعرض هذا القسم.",
"Kullanıcı adı veya parola yanlış.":"اسم المستخدم أو كلمة المرور غير صحيحة.", "Yönetici bilgileri ayarlanmamış.":"لم يتم إعداد بيانات اعتماد المسؤول.",
"Günlük Durum Özeti":"الملخص اليومي للحالة", "Bugünkü yeni bildirim":"البلاغات الجديدة اليوم", "Aktif yüksek/acil":"البلاغات النشطة ذات الأولوية العالية أو العاجلة",
"İnceleme bekleyen":"بانتظار المراجعة", "Toplam kayıt":"إجمالي البلاغات", "Açık kayıt":"البلاغات المفتوحة",
"İstatistikler":"الإحصاءات", "Grafikler yalnızca bu uygulamada kayıtlı bilgileri özetler; okul geneline ilişkin sonuç göstermez.":"تلخّص الرسوم البيانية البيانات المسجلة في هذا التطبيق فقط، ولا تمثل نتائج المدرسة بأكملها.",
"Sinyal, karar değil":"المؤشر ليس قرارًا", "Yetkili kişiler kaydı inceler. Kararı makine vermez.":"يراجع الأشخاص المخوّلون البلاغ. ولا يتخذ النظام القرار.",
"Telefon, T.C. no, e-posta ve IBAN otomatik gizlenir.":"تُخفى أرقام الهواتف وأرقام الهوية التركية وعناوين البريد الإلكتروني وأرقام IBAN تلقائيًا.",
"Destek rehberi":"دليل الدعم", "Gizlilik ve KVKK paneli":"لوحة الخصوصية وحماية البيانات", "Araştırma ve kalite kontrol":"البحث وضمان الجودة",
},
"Azərbaycan dili": {
"Kimliğini vermeden bildir. Ad, sınıf veya telefon istenmez.":"Şəxsiyyətini açıqlamadan bildiriş göndər. Ad, sinif və telefon nömrəsi tələb olunmur.",
"Ne oldu?":"Nə baş verdi?", "Nerede oldu?":"Harada baş verdi?", "Ne zaman oldu?":"Nə vaxt baş verdi?",
"Bu olay kaç kez yaşandı?":"Bu hadisə neçə dəfə baş verib?", "Olayı kendi cümlelerinle anlat":"Baş verənləri öz sözlərinlə təsvir et",
"Hakaret veya alay":"Təhqir və ya lağ", "Tehdit":"Təhdid", "Dışlama":"Kənarlaşdırma", "Dijital zorbalık":"Kiberzorakılıq", "Fiziksel zorbalık şüphesi":"Fiziki zorakılıq şübhəsi", "Diğer":"Digər",
"Sınıfta":"Sinifdə", "Okul bahçesinde":"Məktəb həyətində", "Koridorda":"Dəhlizdə", "Sosyal medyada":"Sosial mediada", "Mesajlaşmada":"Mesajlaşma tətbiqlərində",
"Bugün":"Bu gün", "Dün":"Dünən", "Bu hafta":"Bu həftə", "Daha önce":"Əvvəllər", "Emin değilim":"Əmin deyiləm",
"Bir kez":"Bir dəfə", "Birkaç kez":"Bir neçə dəfə", "Birden fazla kez":"Bir dəfədən çox",
"Acil bir durum değil, yalnızca bilgi vermek istiyorum.":"Bu təcili vəziyyət deyil; sadəcə məlumat vermək istəyirəm.",
"Acil bir tehlike varsa beklemeyin:":"Təcili təhlükə varsa gözləməyin:",
"Günde bir bildirim hakkın var.":"Gündə bir bildiriş göndərə bilərsiniz.",
"Bu platform gerçek bir okul sistemine bağlı değildir. Gerçek kişisel veri girmeyin.":"Bu platform real məktəb sisteminə qoşulmayıb. Həqiqi şəxsi məlumatları daxil etməyin.",
"Bildirimi gönder":"Bildirişi göndər", "Gizli takip kodun.":"Məxfi izləmə kodunuz.",
"Durumu sorgula":"Statusu yoxla", "Durumu göster":"Statusu göstər", "Ek bilgi ekle":"Əlavə məlumat əlavə et",
"Ek bilgi boş olamaz.":"Əlavə məlumat boş ola bilməz.", "Lütfen olayı anlat.":"Zəhmət olmasa, baş verənləri təsvir edin.",
"Lütfen onay kutusunu işaretle.":"Zəhmət olmasa, təsdiq xanasını işarələyin.", "Bildirimin kaydedildi. Teşekkür ederiz.":"Bildirişiniz yadda saxlanıldı. Təşəkkür edirik.",
"Bu kodla eşleşen bir kayıt bulunamadı. Kodu kontrol edip tekrar dene.":"Bu kodla uyğun qeyd tapılmadı. Zəhmət olmasa kodu yoxlayın.",
"Açıklama":"Təsvir", "Olay türü":"Hadisə növü", "Ortam":"Mühit", "Tekrar durumu":"Təkrarlanma tezliyi", "İnceleme durumu":"Yoxlama statusu",
"İnceleme bekliyor":"Yoxlanılmağı gözləyir", "İnceleniyor":"Yoxlanılır", "Sonuçlandırıldı":"Tamamlandı",
"Öncelik sinyali":"Prioritet göstəricisi", "Sorumlu birim":"Məsul bölmə", "Durumu kaydet":"Statusu yadda saxla", "Not ekle":"Qeyd əlavə et",
"Kayıt ara":"Qeydi axtar", "Tüm durumlar":"Bütün statuslar", "Tüm birimler":"Bütün bölmələr", "Sıralama":"Sıralama",
"En yeni önce":"Əvvəlcə ən yenilər", "En eski önce":"Əvvəlcə ən köhnələr", "Öncelik (yüksekten)":"Prioritet (yüksəkdən aşağıya)",
"İnceleme bilgileri kaydedildi.":"Yoxlama məlumatları yadda saxlanıldı.", "Değişiklik yapılmadı; bilgiler zaten güncel.":"Dəyişiklik edilmədi; məlumatlar artıq yenidir.",
"Not kaydedildi.":"Qeyd yadda saxlanıldı.", "Not kaydedilemedi.":"Qeydi yadda saxlamaq mümkün olmadı.",
"Yönetici erişimi gerekli":"Administrator girişi tələb olunur", "Bu bölümü görüntülemek için yönetici oturumu açın.":"Bu bölməyə baxmaq üçün administrator kimi daxil olun.",
"Kullanıcı adı veya parola yanlış.":"İstifadəçi adı və ya şifrə yanlışdır.", "Yönetici bilgileri ayarlanmamış.":"Administrator giriş məlumatları təyin edilməyib.",
"Günlük Durum Özeti":"Gündəlik vəziyyət xülasəsi", "Bugünkü yeni bildirim":"Bu günün yeni bildirişləri", "Aktif yüksek/acil":"Aktiv yüksək/təcili prioritetli bildirişlər",
"İnceleme bekleyen":"Yoxlanılmağı gözləyən", "Toplam kayıt":"Ümumi qeyd sayı", "Açık kayıt":"Açıq bildirişlər",
"İstatistikler":"Statistika", "Grafikler yalnızca bu uygulamada kayıtlı bilgileri özetler; okul geneline ilişkin sonuç göstermez.":"Qrafiklər yalnız bu tətbiqdə qeydə alınmış məlumatları ümumiləşdirir; bütün məktəb üzrə nəticələri göstərmir.",
"Sinyal, karar değil":"Siqnal qərar deyil", "Yetkili kişiler kaydı inceler. Kararı makine vermez.":"Bildirişi səlahiyyətli şəxslər yoxlayır. Qərarı sistem vermir.",
"Telefon, T.C. no, e-posta ve IBAN otomatik gizlenir.":"Telefon nömrələri, Türkiyə şəxsiyyət nömrələri, e-poçt ünvanları və IBAN avtomatik maskalanır.",
"Destek rehberi":"Dəstək bələdçisi", "Gizlilik ve KVKK paneli":"Məxfilik və fərdi məlumatların qorunması paneli", "Araştırma ve kalite kontrol":"Tədqiqat və keyfiyyətə nəzarət",
},
}
_ENUM_TRANSLATIONS = {
"Deutsch": {"Bir kez oldu":"Einmal passiert", "Birkaç kez oldu":"Ein paar Mal passiert", "Sık sık / sürekli oluyor":"Häufig / ständig", "Takip gerekiyor":"Weitere Beobachtung erforderlich", "Henüz atanmadı":"Noch nicht zugewiesen", "Rehberlik birimi":"Beratungsstelle", "Okul yönetimi":"Schulleitung", "Öğrenci destek ekibi":"Schüler:innen-Unterstützungsteam", "Sinyal yok":"Kein Signal", "Diğer":"Sonstiges"},
"Français": {"Bir kez oldu":"Une seule fois", "Birkaç kez oldu":"Quelques fois", "Sık sık / sürekli oluyor":"Fréquemment / continuellement", "Takip gerekiyor":"Un suivi est nécessaire", "Henüz atanmadı":"Pas encore attribué", "Rehberlik birimi":"Service d’accompagnement", "Okul yönetimi":"Direction de l’établissement", "Öğrenci destek ekibi":"Équipe de soutien aux élèves", "Sinyal yok":"Aucun indicateur", "Diğer":"Autre"},
"Español": {"Bir kez oldu":"Ha ocurrido una vez", "Birkaç kez oldu":"Ha ocurrido varias veces", "Sık sık / sürekli oluyor":"Ocurre con frecuencia o continuamente", "Takip gerekiyor":"Requiere seguimiento", "Henüz atanmadı":"Aún sin asignar", "Rehberlik birimi":"Servicio de orientación", "Okul yönetimi":"Dirección del centro", "Öğrenci destek ekibi":"Equipo de apoyo al alumnado", "Sinyal yok":"Sin indicador", "Diğer":"Otro"},
"العربية": {"Bir kez oldu":"حدث مرة واحدة", "Birkaç kez oldu":"حدث عدة مرات", "Sık sık / sürekli oluyor":"يحدث بشكل متكرر أو مستمر", "Takip gerekiyor":"يتطلب المتابعة", "Henüz atanmadı":"لم يتم التعيين بعد", "Rehberlik birimi":"وحدة الإرشاد المدرسي", "Okul yönetimi":"إدارة المدرسة", "Öğrenci destek ekibi":"فريق دعم الطلاب", "Sinyal yok":"لا يوجد مؤشر", "Diğer":"أخرى"},
"Azərbaycan dili": {"Bir kez oldu":"Bir dəfə baş verib", "Birkaç kez oldu":"Bir neçə dəfə baş verib", "Sık sık / sürekli oluyor":"Tez-tez / davamlı baş verir", "Takip gerekiyor":"İzləmə tələb olunur", "Henüz atanmadı":"Hələ təyin edilməyib", "Rehberlik birimi":"Psixoloji dəstək bölməsi", "Okul yönetimi":"Məktəb rəhbərliyi", "Öğrenci destek ekibi":"Şagirdlərə dəstək qrupu", "Sinyal yok":"Göstərici yoxdur", "Diğer":"Digər"},
}
for _language, _entries in _ENUM_TRANSLATIONS.items():
    MULTI_CATALOG[_language].update(_entries)

for _language, _entries in _EXPANDED_UI.items():
    MULTI_CATALOG[_language].update(_entries)

# Additional page-level copy for tracking, review, guidance and privacy screens.
_PAGE_COPY = {
"Deutsch": {
"İnceleme kuyruğunu aç":"Prüfwarteschlange öffnen", "Kodumu not aldım":"Ich habe meinen Code notiert", "Hazırlanıyor…":"Wird vorbereitet…",
"Günlük bildirim hakkınız dolmuştur. Yarın yeniden bildirim yapabilirsin. Bugünkü bildirimine takip koduyla ek bilgi ekleyebilirsin.":"Du hast dein tägliches Meldelimit erreicht. Morgen kannst du erneut eine Meldung einreichen. Mit deinem Tracking-Code kannst du deiner heutigen Meldung weitere Informationen hinzufügen.",
"Bildirimime ek bilgi ekle":"Meiner Meldung Informationen hinzufügen", "Ne oldu, nerede ve ne zaman oldu? Ad, telefon gibi bilgileri yazma.":"Beschreibe, was, wo und wann passiert ist. Gib keine Namen, Telefonnummern oder andere persönliche Angaben ein.",
"Ek bilgi yalnızca anonim bildirimlerde, bildirimin yapıldığı gün ve bildirim sonuçlanmadan önce eklenebilir.":"Zusätzliche Informationen können nur zu anonymen Meldungen, am Tag der Einreichung und vor Abschluss der Prüfung hinzugefügt werden.",
"Bugün için ek bilgi sınırına ulaştın.":"Du hast das heutige Limit für zusätzliche Informationen erreicht.", "Eklemek istediğin bilgi":"Welche zusätzlichen Informationen möchtest du hinzufügen?", "Ad, telefon gibi bilgileri yazma.":"Gib keine Namen, Telefonnummern oder ähnliche Angaben ein.", "Ek bilgiyi gönder":"Zusätzliche Informationen senden",
"Yönetici oturumu açık.":"Administrator-Sitzung ist aktiv.", "Sistem genelinde çok fazla hatalı giriş denemesi var. Lütfen bir süre sonra tekrar deneyin.":"Es gab systemweit zu viele fehlgeschlagene Anmeldeversuche. Bitte versuche es später erneut.",
"Otomatik sinyal ve değerlendirme notu":"Automatisches Signal und Bewertungshinweis", "Değişiklikleri kaydet":"Änderungen speichern", "İnceleme notları":"Prüfnotizen", "İşlem geçmişi":"Aktivitätsverlauf",
"Platformun işlevleri":"Funktionen der Plattform", "Sınırlar":"Grenzen", "Gerçek kullanıma geçmeden önce (kontrol listesi)":"Checkliste vor einem echten Einsatz",
"Değerlendirmeyi çalıştır":"Auswertung durchführen", "Sonucu JSON olarak indir":"Ergebnis als JSON herunterladen", "Karışıklık matrisi":"Konfusionsmatrix", "Örnek türüne göre doğruluk":"Genauigkeit nach Beispieldatentyp", "Kategoriye göre yakalama (duyarlılık)":"Erkennung nach Kategorie (Sensitivität)",
"Bildirim ayrıntıları":"Meldungsdetails", "İnceleme ve yönlendirme":"Prüfung und Weiterleitung", "İnceleme notları":"Prüfnotizen", "İşlem geçmişi":"Aktivitätsverlauf",
"Gizlilik ve KVKK paneli":"Datenschutzbereich", "Aydınlatma metni":"Datenschutzhinweis", "Veri envanteri":"Datenverzeichnis", "Saklama ve imha":"Aufbewahrung und Löschung", "Onam akışı (simülasyon)":"Einwilligungsablauf (Simulation)",
"Katılımcının yaş grubu":"Altersgruppe der teilnehmenden Person", "18 yaşından küçük":"Unter 18 Jahre", "18 yaş ve üzeri":"18 Jahre oder älter", "İleri":"Weiter", "Baştan başla":"Von vorn beginnen",
},
"Français": {
"İnceleme kuyruğunu aç":"Ouvrir la file d’examen", "Kodumu not aldım":"J’ai noté mon code", "Hazırlanıyor…":"Préparation…",
"Günlük bildirim hakkınız dolmuştur. Yarın yeniden bildirim yapabilirsin. Bugünkü bildirimine takip koduyla ek bilgi ekleyebilirsin.":"Vous avez atteint votre limite quotidienne de signalements. Vous pourrez en envoyer un nouveau demain. Vous pouvez ajouter des informations à celui d’aujourd’hui à l’aide de votre code de suivi.",
"Bildirimime ek bilgi ekle":"Ajouter des informations à mon signalement", "Ne oldu, nerede ve ne zaman oldu? Ad, telefon gibi bilgileri yazma.":"Décrivez ce qui s’est passé, où et quand. N’indiquez ni nom, ni numéro de téléphone, ni autre donnée permettant d’identifier quelqu’un.",
"Ek bilgi yalnızca anonim bildirimlerde, bildirimin yapıldığı gün ve bildirim sonuçlanmadan önce eklenebilir.":"Des informations complémentaires peuvent être ajoutées uniquement aux signalements anonymes, le jour de leur envoi et avant leur clôture.",
"Bugün için ek bilgi sınırına ulaştın.":"Vous avez atteint la limite quotidienne d’informations complémentaires.", "Eklemek istediğin bilgi":"Informations complémentaires à ajouter", "Ad, telefon gibi bilgileri yazma.":"N’indiquez pas de nom, de numéro de téléphone ni d’autres données personnelles.", "Ek bilgiyi gönder":"Envoyer les informations complémentaires",
"Yönetici oturumu açık.":"La session administrateur est ouverte.", "Sistem genelinde çok fazla hatalı giriş denemesi var. Lütfen bir süre sonra tekrar deneyin.":"Le système a enregistré trop de tentatives de connexion échouées. Veuillez réessayer plus tard.",
"Otomatik sinyal ve değerlendirme notu":"Indicateur automatique et note d’évaluation", "Değişiklikleri kaydet":"Enregistrer les modifications", "İnceleme notları":"Notes d’examen", "İşlem geçmişi":"Historique des actions",
"Platformun işlevleri":"Fonctionnalités de la plateforme", "Sınırlar":"Limites", "Gerçek kullanıma geçmeden önce (kontrol listesi)":"Liste de vérification avant toute utilisation réelle",
"Değerlendirmeyi çalıştır":"Lancer l’évaluation", "Sonucu JSON olarak indir":"Télécharger le résultat au format JSON", "Karışıklık matrisi":"Matrice de confusion", "Örnek türüne göre doğruluk":"Précision par type d’exemple", "Kategoriye göre yakalama (duyarlılık)":"Détection par catégorie (sensibilité)",
"Bildirim ayrıntıları":"Détails du signalement", "İnceleme ve yönlendirme":"Examen et orientation",
"Aydınlatma metni":"Notice d’information", "Veri envanteri":"Inventaire des données", "Saklama ve imha":"Conservation et suppression", "Onam akışı (simülasyon)":"Parcours de consentement (simulation)",
"Katılımcının yaş grubu":"Tranche d’âge de la personne participante", "18 yaşından küçük":"Moins de 18 ans", "18 yaş ve üzeri":"18 ans ou plus", "İleri":"Suivant", "Baştan başla":"Recommencer",
},
"Español": {
"İnceleme kuyruğunu aç":"Abrir la cola de revisión", "Kodumu not aldım":"He guardado mi código", "Hazırlanıyor…":"Preparando…",
"Günlük bildirim hakkınız dolmuştur. Yarın yeniden bildirim yapabilirsin. Bugünkü bildirimine takip koduyla ek bilgi ekleyebilirsin.":"Has alcanzado el límite diario de avisos. Podrás enviar otro mañana. Puedes añadir información al aviso de hoy con tu código de seguimiento.",
"Bildirimime ek bilgi ekle":"Añadir información a mi aviso", "Ne oldu, nerede ve ne zaman oldu? Ad, telefon gibi bilgileri yazma.":"Describe qué ocurrió, dónde y cuándo. No incluyas nombres, teléfonos ni otros datos que permitan identificar a alguien.",
"Ek bilgi yalnızca anonim bildirimlerde, bildirimin yapıldığı gün ve bildirim sonuçlanmadan önce eklenebilir.":"Solo se puede añadir información a avisos anónimos el mismo día en que se envían y antes de que se cierren.",
"Bugün için ek bilgi sınırına ulaştın.":"Has alcanzado el límite de información adicional de hoy.", "Eklemek istediğin bilgi":"Información adicional que deseas añadir", "Ad, telefon gibi bilgileri yazma.":"No incluyas nombres, teléfonos ni otros datos personales.", "Ek bilgiyi gönder":"Enviar información adicional",
"Yönetici oturumu açık.":"La sesión de administración está activa.", "Sistem genelinde çok fazla hatalı giriş denemesi var. Lütfen bir süre sonra tekrar deneyin.":"Se han producido demasiados intentos fallidos de acceso en el sistema. Inténtalo de nuevo más tarde.",
"Otomatik sinyal ve değerlendirme notu":"Indicador automático y nota de evaluación", "Değişiklikleri kaydet":"Guardar cambios", "İnceleme notları":"Notas de revisión", "İşlem geçmişi":"Historial de actividad",
"Platformun işlevleri":"Funciones de la plataforma", "Sınırlar":"Limitaciones", "Gerçek kullanıma geçmeden önce (kontrol listesi)":"Lista de comprobación antes de un uso real",
"Değerlendirmeyi çalıştır":"Ejecutar evaluación", "Sonucu JSON olarak indir":"Descargar resultado en JSON", "Karışıklık matrisi":"Matriz de confusión", "Örnek türüne göre doğruluk":"Precisión por tipo de ejemplo", "Kategoriye göre yakalama (duyarlılık)":"Detección por categoría (sensibilidad)",
"Bildirim ayrıntıları":"Detalles del aviso", "İnceleme ve yönlendirme":"Revisión y derivación",
"Aydınlatma metni":"Aviso de privacidad", "Veri envanteri":"Inventario de datos", "Saklama ve imha":"Conservación y eliminación", "Onam akışı (simülasyon)":"Proceso de consentimiento (simulación)",
"Katılımcının yaş grubu":"Grupo de edad de la persona participante", "18 yaşından küçük":"Menor de 18 años", "18 yaş ve üzeri":"18 años o más", "İleri":"Continuar", "Baştan başla":"Volver a empezar",
},
"العربية": {
"İnceleme kuyruğunu aç":"فتح قائمة البلاغات للمراجعة", "Kodumu not aldım":"لقد احتفظت بالرمز", "Hazırlanıyor…":"جارٍ التحضير…",
"Günlük bildirim hakkınız dolmuştur. Yarın yeniden bildirim yapabilirsin. Bugünkü bildirimine takip koduyla ek bilgi ekleyebilirsin.":"لقد وصلت إلى الحد اليومي للبلاغات. يمكنك تقديم بلاغ جديد غدًا، كما يمكنك إضافة معلومات إلى بلاغ اليوم باستخدام رمز المتابعة.",
"Bildirimime ek bilgi ekle":"إضافة معلومات إلى بلاغي", "Ne oldu, nerede ve ne zaman oldu? Ad, telefon gibi bilgileri yazma.":"وضّح ما الذي حدث وأين ومتى. لا تكتب أسماء أو أرقام هواتف أو أي معلومات تكشف الهوية.",
"Ek bilgi yalnızca anonim bildirimlerde, bildirimin yapıldığı gün ve bildirim sonuçlanmadan önce eklenebilir.":"يمكن إضافة معلومات إلى البلاغات المجهولة فقط، في يوم تقديم البلاغ وقبل إغلاقه.",
"Bugün için ek bilgi sınırına ulaştın.":"لقد وصلت إلى الحد اليومي لإضافة المعلومات.", "Eklemek istediğin bilgi":"المعلومات الإضافية التي تريد إدخالها", "Ad, telefon gibi bilgileri yazma.":"لا تكتب أسماء أو أرقام هواتف أو معلومات شخصية أخرى.", "Ek bilgiyi gönder":"إرسال المعلومات الإضافية",
"Yönetici oturumu açık.":"جلسة المسؤول مفتوحة.", "Sistem genelinde çok fazla hatalı giriş denemesi var. Lütfen bir süre sonra tekrar deneyin.":"تم تسجيل عدد كبير جدًا من محاولات الدخول الفاشلة على مستوى النظام. يرجى المحاولة لاحقًا.",
"Otomatik sinyal ve değerlendirme notu":"المؤشر الآلي وملاحظة التقييم", "Değişiklikleri kaydet":"حفظ التغييرات", "İnceleme notları":"ملاحظات المراجعة", "İşlem geçmişi":"سجل الإجراءات",
"Platformun işlevleri":"وظائف المنصة", "Sınırlar":"الحدود", "Gerçek kullanıma geçmeden önce (kontrol listesi)":"قائمة التحقق قبل الاستخدام الفعلي",
"Değerlendirmeyi çalıştır":"تشغيل التقييم", "Sonucu JSON olarak indir":"تنزيل النتيجة بصيغة JSON", "Karışıklık matrisi":"مصفوفة الالتباس", "Örnek türüne göre doğruluk":"الدقة حسب نوع العينة", "Kategoriye göre yakalama (duyarlılık)":"الكشف حسب الفئة (الحساسية)",
"Bildirim ayrıntıları":"تفاصيل البلاغ", "İnceleme ve yönlendirme":"المراجعة والإحالة",
"Aydınlatma metni":"إشعار الخصوصية", "Veri envanteri":"سجل البيانات", "Saklama ve imha":"الاحتفاظ بالبيانات وحذفها", "Onam akışı (simülasyon)":"مسار الموافقة (محاكاة)",
"Katılımcının yaş grubu":"الفئة العمرية للمشارك", "18 yaşından küçük":"أقل من 18 عامًا", "18 yaş ve üzeri":"18 عامًا فأكثر", "İleri":"متابعة", "Baştan başla":"البدء من جديد",
},
"Azərbaycan dili": {
"İnceleme kuyruğunu aç":"Yoxlama növbəsini aç", "Kodumu not aldım":"Kodumu qeyd etdim", "Hazırlanıyor…":"Hazırlanır…",
"Günlük bildirim hakkınız dolmuştur. Yarın yeniden bildirim yapabilirsin. Bugünkü bildirimine takip koduyla ek bilgi ekleyebilirsin.":"Gündəlik bildiriş limitiniz bitib. Sabah yenidən bildiriş göndərə bilərsiniz. Bugünkü bildirişə izləmə kodu ilə əlavə məlumat daxil edə bilərsiniz.",
"Bildirimime ek bilgi ekle":"Bildirişimə əlavə məlumat daxil et", "Ne oldu, nerede ve ne zaman oldu? Ad, telefon gibi bilgileri yazma.":"Nə baş verdiyini, harada və nə vaxt baş verdiyini təsvir edin. Ad, telefon nömrəsi və digər şəxsi məlumatları yazmayın.",
"Ek bilgi yalnızca anonim bildirimlerde, bildirimin yapıldığı gün ve bildirim sonuçlanmadan önce eklenebilir.":"Əlavə məlumat yalnız anonim bildirişlərə, bildiriş göndərilən gün və yoxlama tamamlanmazdan əvvəl əlavə edilə bilər.",
"Bugün için ek bilgi sınırına ulaştın.":"Bu gün üçün əlavə məlumat limitinə çatmısınız.", "Eklemek istediğin bilgi":"Əlavə etmək istədiyiniz məlumat", "Ad, telefon gibi bilgileri yazma.":"Ad, telefon nömrəsi və digər şəxsi məlumatları yazmayın.", "Ek bilgiyi gönder":"Əlavə məlumatı göndər",
"Yönetici oturumu açık.":"Administrator sessiyası aktivdir.", "Sistem genelinde çok fazla hatalı giriş denemesi var. Lütfen bir süre sonra tekrar deneyin.":"Sistem üzrə çoxsaylı uğursuz giriş cəhdi qeydə alınıb. Bir qədər sonra yenidən cəhd edin.",
"Otomatik sinyal ve değerlendirme notu":"Avtomatik göstərici və qiymətləndirmə qeydi", "Değişiklikleri kaydet":"Dəyişiklikləri yadda saxla", "İnceleme notları":"Yoxlama qeydləri", "İşlem geçmişi":"Əməliyyat tarixçəsi",
"Platformun işlevleri":"Platformun funksiyaları", "Sınırlar":"Məhdudiyyətlər", "Gerçek kullanıma geçmeden önce (kontrol listesi)":"Real istifadədən əvvəl yoxlama siyahısı",
"Değerlendirmeyi çalıştır":"Qiymətləndirməni işə sal", "Sonucu JSON olarak indir":"Nəticəni JSON formatında yüklə", "Karışıklık matrisi":"Qarışıqlıq matrisi", "Örnek türüne göre doğruluk":"Nümunə növünə görə dəqiqlik", "Kategoriye göre yakalama (duyarlılık)":"Kateqoriya üzrə aşkarlama (həssaslıq)",
"Bildirim ayrıntıları":"Bildiriş təfərrüatları", "İnceleme ve yönlendirme":"Yoxlama və yönləndirmə",
"Aydınlatma metni":"Məlumatlandırma mətni", "Veri envanteri":"Məlumatların reyestri", "Saklama ve imha":"Saxlanma və məhv edilmə", "Onam akışı (simülasyon)":"Razılıq prosesi (simulyasiya)",
"Katılımcının yaş grubu":"İştirakçının yaş qrupu", "18 yaşından küçük":"18 yaşdan kiçik", "18 yaş ve üzeri":"18 yaş və yuxarı", "İleri":"İrəli", "Baştan başla":"Yenidən başla",
},
}
for _language, _entries in _PAGE_COPY.items():
    MULTI_CATALOG[_language].update(_entries)

# Homepage copy: complete, reviewed translations for the first screen.
# These entries intentionally cover every visible sentence in the landing-page cards
# and emergency banner so languages do not fall back to Turkish or mix languages.
_HOME_COPY = {
"Deutsch": {
"Zorbalığı kimliğini vermeden bildir, gizli kodunla durumu takip et.":"Melde Mobbing, ohne deine Identität preiszugeben, und verfolge den Status mit deinem vertraulichen Code.",
"Nasıl kullanılır?":"So funktioniert es", "1 · Bildir":"1 · Melden",
"Formu doldur. Ad ve sınıf istenmez; sana gizli bir kod verilir.":"Fülle das Formular aus. Name und Klasse werden nicht abgefragt; du erhältst einen vertraulichen Code.",
"2 · Takip et":"2 · Nachverfolgen", "Kodunla durumu gör, aynı gün ek bilgi ekle.":"Prüfe den Status mit deinem Code und ergänze noch am selben Tag weitere Informationen.",
"3 · İnsan inceler":"3 · Menschliche Prüfung", "Yetkili kişiler kaydı inceler. Kararı makine vermez.":"Befugte Mitarbeitende prüfen die Meldung. Das System trifft keine Entscheidungen.",
"Acil bir tehlike varsa beklemeyin:":"Bei unmittelbarer Gefahr nicht warten:",
"Acil Çağrı Merkezi (Polis, Sağlık, Jandarma - 7/24)":"Notrufzentrale (Polizei, Rettungsdienst und Gendarmerie – rund um die Uhr)",
"ALO Sosyal Destek Hattı (7/24)":"ALO-Sozialhilfetelefon (rund um die Uhr)", "MEB İletişim Merkezi (MEBİM)":"Kontaktzentrum des türkischen Bildungsministeriums (MEBİM)",
"Rehberlik bilgi bankası":"Beratungsangebote", "Güvenlik ilkeleri":"Sicherheitsgrundsätze", "Gizlilik":"Datenschutz", "Sinyal, karar değil":"Ein Hinweis ist keine Entscheidung", "Hesap verebilirlik":"Rechenschaftspflicht",
"Yaşıyorsan":"Wenn du betroffen bist", "Kime anlatabileceğini ve neler yapabileceğini öğren.":"Erfahre, mit wem du sprechen kannst und was du tun kannst.", "Tanık olduysan":"Wenn du etwas beobachtet hast", "Sessiz kalmadan, güvenli şekilde nasıl destek olursun?":"Wie kannst du helfen, ohne zu schweigen und ohne dich zu gefährden?", "Veli ve öğretmenler":"Eltern und Lehrkräfte", "İşaretleri tanı, çocuğu dinle, doğru adımı at.":"Erkenzeichen erkennen, dem Kind zuhören und angemessen handeln.",
"Telefon, T.C. no, e-posta ve IBAN otomatik gizlenir.":"Telefonnummern, türkische Identifikationsnummern, E-Mail-Adressen und IBANs werden automatisch unkenntlich gemacht.", "Otomatik eşleşme yalnızca inceleme sırasına yardım eder.":"Automatische Treffer helfen lediglich bei der Priorisierung der Prüfung.", "Yönetici işlemleri kim yaptığıyla kayda geçer.":"Administratoraktionen werden mit Angabe der ausführenden Person protokolliert.",
},
"Français": {
"Zorbalığı kimliğini vermeden bildir, gizli kodunla durumu takip et.":"Signalez une situation de harcèlement sans révéler votre identité et suivez son état grâce à votre code confidentiel.",
"Nasıl kullanılır?":"Comment ça marche", "1 · Bildir":"1 · Signaler",
"Formu doldur. Ad ve sınıf istenmez; sana gizli bir kod verilir.":"Remplissez le formulaire. Votre nom et votre classe ne sont pas demandés ; un code confidentiel vous sera attribué.",
"2 · Takip et":"2 · Suivre", "Kodunla durumu gör, aynı gün ek bilgi ekle.":"Consultez l’état du signalement avec votre code et ajoutez des précisions le jour même.",
"3 · İnsan inceler":"3 · Examen humain", "Yetkili kişiler kaydı inceler. Kararı makine vermez.":"Le signalement est examiné par des personnes habilitées. Le système ne prend aucune décision.",
"Acil bir tehlike varsa beklemeyin:":"En cas de danger immédiat, n’attendez pas :",
"Acil Çağrı Merkezi (Polis, Sağlık, Jandarma - 7/24)":"Centre d’urgence 112 (police, secours médicaux et gendarmerie – 24 h/24)",
"ALO Sosyal Destek Hattı (7/24)":"Ligne d’aide sociale ALO 183 (24 h/24)", "MEB İletişim Merkezi (MEBİM)":"Centre de contact du ministère turc de l’Éducation (MEBİM)",
"Rehberlik bilgi bankası":"Ressources d’accompagnement", "Güvenlik ilkeleri":"Principes de sécurité", "Gizlilik":"Confidentialité", "Sinyal, karar değil":"Un signalement n’est pas une décision", "Hesap verebilirlik":"Responsabilité",
"Yaşıyorsan":"Si vous êtes concerné", "Kime anlatabileceğini ve neler yapabileceğini öğren.":"Découvrez à qui en parler et quelles démarches entreprendre.", "Tanık olduysan":"Si vous êtes témoin", "Sessiz kalmadan, güvenli şekilde nasıl destek olursun?":"Comment apporter votre soutien en toute sécurité, sans rester silencieux ?", "Veli ve öğretmenler":"Parents et personnel éducatif", "İşaretleri tanı, çocuğu dinle, doğru adımı at.":"Repérez les signes, écoutez l’enfant et adoptez la bonne démarche.",
"Telefon, T.C. no, e-posta ve IBAN otomatik gizlenir.":"Les numéros de téléphone, numéros d’identité turcs, adresses e-mail et IBAN sont automatiquement masqués.", "Otomatik eşleşme yalnızca inceleme sırasına yardım eder.":"Les correspondances automatiques aident uniquement à organiser l’ordre des examens.", "Yönetici işlemleri kim yaptığıyla kayda geçer.":"Les actions des administrateurs sont consignées avec l’identité de leur auteur.",
},
"Español": {
"Zorbalığı kimliğini vermeden bildir, gizli kodunla durumu takip et.":"Comunica una situación de acoso sin revelar tu identidad y consulta su estado con tu código privado.",
"Nasıl kullanılır?":"Cómo funciona", "1 · Bildir":"1 · Comunicar",
"Formu doldur. Ad ve sınıf istenmez; sana gizli bir kod verilir.":"Completa el formulario. No se solicitan tu nombre ni tu curso; recibirás un código privado.",
"2 · Takip et":"2 · Consultar", "Kodunla durumu gör, aynı gün ek bilgi ekle.":"Consulta el estado con tu código y añade información adicional ese mismo día.",
"3 · İnsan inceler":"3 · Revisión humana", "Yetkili kişiler kaydı inceler. Kararı makine vermez.":"El aviso es revisado por personal autorizado. El sistema no toma decisiones.",
"Acil bir tehlike varsa beklemeyin:":"Si existe un peligro inmediato, no esperes:",
"Acil Çağrı Merkezi (Polis, Sağlık, Jandarma - 7/24)":"Centro de Emergencias 112 (policía, servicios médicos y gendarmería, 24 horas)",
"ALO Sosyal Destek Hattı (7/24)":"Línea de apoyo social ALO 183 (24 horas)", "MEB İletişim Merkezi (MEBİM)":"Centro de Atención del Ministerio de Educación de Turquía (MEBİM)",
"Rehberlik bilgi bankası":"Recursos de orientación", "Güvenlik ilkeleri":"Principios de seguridad", "Gizlilik":"Privacidad", "Sinyal, karar değil":"Una señal no es una decisión", "Hesap verebilirlik":"Rendición de cuentas",
"Yaşıyorsan":"Si te está ocurriendo", "Kime anlatabileceğini ve neler yapabileceğini öğren.":"Descubre con quién puedes hablar y qué puedes hacer.", "Tanık olduysan":"Si has sido testigo", "Sessiz kalmadan, güvenli şekilde nasıl destek olursun?":"¿Cómo puedes ayudar de forma segura sin quedarte en silencio?", "Veli ve öğretmenler":"Familias y docentes", "İşaretleri tanı, çocuğu dinle, doğru adımı at.":"Reconoce las señales, escucha al menor y actúa de forma adecuada.",
"Telefon, T.C. no, e-posta ve IBAN otomatik gizlenir.":"Los teléfonos, números de identidad turcos, correos electrónicos e IBAN se ocultan automáticamente.", "Otomatik eşleşme yalnızca inceleme sırasına yardım eder.":"Las coincidencias automáticas solo ayudan a organizar la revisión.", "Yönetici işlemleri kim yaptığıyla kayda geçer.":"Las acciones administrativas quedan registradas junto con la persona que las realizó.",
},
"العربية": {
"Zorbalığı kimliğini vermeden bildir, gizli kodunla durumu takip et.":"أبلغ عن التنمّر دون الكشف عن هويتك، وتابع حالة البلاغ باستخدام رمزك الخاص.",
"Nasıl kullanılır?":"كيف تعمل الخدمة؟", "1 · Bildir":"١ · أرسل بلاغًا",
"Formu doldur. Ad ve sınıf istenmez; sana gizli bir kod verilir.":"املأ النموذج. لن يُطلب اسمك أو صفك، وستحصل على رمز متابعة خاص.",
"2 · Takip et":"٢ · تابع البلاغ", "Kodunla durumu gör, aynı gün ek bilgi ekle.":"تحقق من حالة البلاغ باستخدام الرمز، وأضف معلومات أخرى في اليوم نفسه.",
"3 · İnsan inceler":"٣ · مراجعة بشرية", "Yetkili kişiler kaydı inceler. Kararı makine vermez.":"يراجع الموظفون المخوّلون البلاغ. ولا يتخذ النظام القرارات.",
"Acil bir tehlike varsa beklemeyin:":"في حال وجود خطر فوري، لا تنتظر:",
"Acil Çağrı Merkezi (Polis, Sağlık, Jandarma - 7/24)":"مركز الطوارئ 112 (الشرطة والخدمات الطبية والدرك – على مدار الساعة)",
"ALO Sosyal Destek Hattı (7/24)":"خط الدعم الاجتماعي ALO 183 (على مدار الساعة)", "MEB İletişim Merkezi (MEBİM)":"مركز الاتصال بوزارة التعليم التركية (MEBİM)",
"Rehberlik bilgi bankası":"مصادر الإرشاد والدعم", "Güvenlik ilkeleri":"مبادئ الأمان", "Gizlilik":"الخصوصية", "Sinyal, karar değil":"المؤشر ليس قرارًا", "Hesap verebilirlik":"المساءلة",
"Yaşıyorsan":"إذا كنت تتعرض للتنمّر", "Kime anlatabileceğini ve neler yapabileceğini öğren.":"تعرّف إلى الشخص الذي يمكنك التحدث إليه والخطوات التي يمكنك اتخاذها.", "Tanık olduysan":"إذا شاهدت التنمّر", "Sessiz kalmadan, güvenli şekilde nasıl destek olursun?":"كيف تقدم الدعم بأمان دون التزام الصمت؟", "Veli ve öğretmenler":"أولياء الأمور والمعلمون", "İşaretleri tanı, çocuğu dinle, doğru adımı at.":"تعرّف إلى العلامات، واستمع إلى الطالب، واتخذ الخطوة المناسبة.",
"Telefon, T.C. no, e-posta ve IBAN otomatik gizlenir.":"تُحجب أرقام الهواتف وأرقام الهوية التركية وعناوين البريد الإلكتروني وأرقام IBAN تلقائيًا.", "Otomatik eşleşme yalnızca inceleme sırasına yardım eder.":"تساعد المطابقة الآلية في ترتيب المراجعة فقط.", "Yönetici işlemleri kim yaptığıyla kayda geçer.":"تُسجّل إجراءات المسؤول مع تحديد الشخص الذي نفّذها.",
},
"Azərbaycan dili": {
"Zorbalığı kimliğini vermeden bildir, gizli kodunla durumu takip et.":"Kimliyinizi açıqlamadan zorakılıq barədə məlumat verin və məxfi kodunuzla müraciətin vəziyyətini izləyin.",
"Nasıl kullanılır?":"Necə işləyir", "1 · Bildir":"1 · Məlumat ver",
"Formu doldur. Ad ve sınıf istenmez; sana gizli bir kod verilir.":"Formanı doldurun. Adınız və sinfiniz soruşulmur; sizə məxfi izləmə kodu verilir.",
"2 · Takip et":"2 · İzləyin", "Kodunla durumu gör, aynı gün ek bilgi ekle.":"Kodunuzla vəziyyəti yoxlayın və həmin gün əlavə məlumat daxil edin.",
"3 · İnsan inceler":"3 · İnsan yoxlaması", "Yetkili kişiler kaydı inceler. Kararı makine vermez.":"Müraciəti səlahiyyətli əməkdaşlar yoxlayır. Qərarı sistem vermir.",
"Acil bir tehlike varsa beklemeyin:":"Təcili təhlükə varsa, gözləməyin:",
"Acil Çağrı Merkezi (Polis, Sağlık, Jandarma - 7/24)":"112 Təcili Yardım Mərkəzi (polis, tibbi xidmət və jandarma – 24/7)",
"ALO Sosyal Destek Hattı (7/24)":"ALO 183 Sosial Dəstək Xətti (24/7)", "MEB İletişim Merkezi (MEBİM)":"Türkiyə Təhsil Nazirliyinin Əlaqə Mərkəzi (MEBİM)",
"Rehberlik bilgi bankası":"Dəstək və məsləhət resursları", "Güvenlik ilkeleri":"Təhlükəsizlik prinsipləri", "Gizlilik":"Məxfilik", "Sinyal, karar değil":"Siqnal qərar deyil", "Hesap verebilirlik":"Hesabatlılıq",
"Yaşıyorsan":"Əgər bunu yaşayırsınızsa", "Kime anlatabileceğini ve neler yapabileceğini öğren.":"Kimə müraciət edə biləcəyinizi və hansı addımları ata biləcəyinizi öyrənin.", "Tanık olduysan":"Əgər şahid olmusunuzsa", "Sessiz kalmadan, güvenli şekilde nasıl destek olursun?":"Susmadan və özünüzü riskə atmadan necə dəstək ola biləcəyinizi öyrənin.", "Veli ve öğretmenler":"Valideynlər və müəllimlər", "İşaretleri tanı, çocuğu dinle, doğru adımı at.":"Əlamətləri tanıyın, uşağı dinləyin və düzgün addım atın.",
"Telefon, T.C. no, e-posta ve IBAN otomatik gizlenir.":"Telefon nömrələri, Türkiyə şəxsiyyət nömrələri, e-poçt ünvanları və IBAN məlumatları avtomatik gizlədilir.", "Otomatik eşleşme yalnızca inceleme sırasına yardım eder.":"Avtomatik uyğunluqlar yalnız yoxlama ardıcıllığını müəyyənləşdirməyə kömək edir.", "Yönetici işlemleri kim yaptığıyla kayda geçer.":"Administrator əməliyyatları onları həyata keçirən şəxslə birlikdə qeydə alınır.",
}
}
for _language, _entries in _HOME_COPY.items():
    MULTI_CATALOG[_language].update(_entries)

# Shared sidebar and footer labels used across all language catalogues.
MULTI_CATALOG["Deutsch"].update({"Dil / Language":"Sprache / Language","KULLANICI":"BENUTZER","YÖNETİM":"VERWALTUNG","KURUMSAL":"INFORMATIONEN","OTURUM":"SITZUNG","Yönetici:":"Administrator:","Ziyaretçi (giriş yapılmadı)":"Gast (nicht angemeldet)","Sürüm":"Version","Algılayıcı":"Detektor","Acil:":"Notfall:","Güvenli Okul · Bildirim ve takip":"Güvenli Okul · Meldung und Nachverfolgung"})
MULTI_CATALOG["Français"].update({"Dil / Language":"Langue / Language","KULLANICI":"UTILISATEUR","YÖNETİM":"ADMINISTRATION","KURUMSAL":"INFORMATIONS","OTURUM":"SESSION","Yönetici:":"Administrateur :","Ziyaretçi (giriş yapılmadı)":"Visiteur (non connecté)","Sürüm":"Version","Algılayıcı":"Détecteur","Acil:":"Urgence :","Güvenli Okul · Bildirim ve takip":"Güvenli Okul · Signalement et suivi"})
MULTI_CATALOG["Español"].update({"Dil / Language":"Idioma / Language","KULLANICI":"USUARIO","YÖNETİM":"ADMINISTRACIÓN","KURUMSAL":"INFORMACIÓN","OTURUM":"SESIÓN","Yönetici:":"Administrador:","Ziyaretçi (giriş yapılmadı)":"Visitante (sin iniciar sesión)","Sürüm":"Versión","Algılayıcı":"Detector","Acil:":"Emergencia:","Güvenli Okul · Bildirim ve takip":"Güvenli Okul · Reportes y seguimiento"})
MULTI_CATALOG["العربية"].update({"Dil / Language":"اللغة / Language","KULLANICI":"المستخدم","YÖNETİM":"الإدارة","KURUMSAL":"معلومات","OTURUM":"الجلسة","Yönetici:":"المسؤول:","Ziyaretçi (giriş yapılmadı)":"زائر (لم يتم تسجيل الدخول)","Sürüm":"الإصدار","Algılayıcı":"الكاشف","Acil:":"طوارئ:","Güvenli Okul · Bildirim ve takip":"Güvenli Okul · البلاغات والمتابعة"})
MULTI_CATALOG["Azərbaycan dili"].update({"Dil / Language":"Dil / Language","KULLANICI":"İSTİFADƏÇİ","YÖNETİM":"İDARƏETMƏ","KURUMSAL":"MƏLUMAT","OTURUM":"SESSİYA","Yönetici:":"Administrator:","Ziyaretçi (giriş yapılmadı)":"Qonaq (daxil olmayıb)","Sürüm":"Versiya","Algılayıcı":"Aşkarlayıcı","Acil:":"Təcili:","Güvenli Okul · Bildirim ve takip":"Güvenli Okul · Bildiriş və izləmə"})

# Keep explicit source-language semantics. Unknown/user-authored content is never
# machine-translated or guessed; untranslated UI strings remain Turkish.
def translate(value: Any, language: str | None = None) -> Any:
    lang = language or CURRENT_LANGUAGE
    if not isinstance(value, str) or lang == TR:
        return value
    if lang == EN:
        return _translate_tr_en(value, EN)
    table = MULTI_CATALOG.get(lang, {})
    if value in table:
        return table[value]
    dynamic = re.match(r"^(\d+) kayıt$", value)
    if dynamic:
        n = dynamic.group(1)
        return {"Deutsch": f"{n} Meldungen", "Français": f"{n} signalements", "Español": f"{n} reportes", "العربية": f"{n} بلاغات", "Azərbaycan dili": f"{n} bildiriş"}.get(lang, value)
    dynamic = re.match(r"^Son (\d+) gün$", value)
    if dynamic:
        n = dynamic.group(1)
        return {"Deutsch": f"Letzte {n} Tage", "Français": f"{n} derniers jours", "Español": f"Últimos {n} días", "العربية": f"آخر {n} أيام", "Azərbaycan dili": f"Son {n} gün"}.get(lang, value)
    dynamic = re.match(r"^(\d+(?:[.,]\d+)?) saat bekliyor$", value)
    if dynamic:
        n = dynamic.group(1)
        return {"Deutsch": f"wartet seit {n} Stunden", "Français": f"en attente depuis {n} heures", "Español": f"en espera durante {n} horas", "العربية": f"بانتظار المراجعة منذ {n} ساعة", "Azərbaycan dili": f"{n} saatdır gözləyir"}.get(lang, value)
    # Exact, reviewed UI phrases may also occur inside longer Markdown copy.
    # Longer phrases are replaced first; short tokens are restricted to exact
    # values to avoid altering unrelated words or user-authored text.
    result = value
    for source, target in sorted(table.items(), key=lambda item: len(item[0]), reverse=True):
        if len(source) < 7:
            continue
        pattern = re.compile(r"\s+".join(re.escape(part) for part in source.split()))
        result = pattern.sub(lambda _m, replacement=target: replacement, result)
    return result


def format_timestamp(value: str | None, language: str | None = None) -> str:
    lang = language or CURRENT_LANGUAGE
    if lang in (TR, EN):
        return _format_timestamp_tr_en(value, lang)
    if not value:
        return "—"
    try:
        dt = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return value
    months = {
      "Deutsch":("Jan","Feb","Mär","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"),
      "Français":("janv.","févr.","mars","avr.","mai","juin","juil.","août","sept.","oct.","nov.","déc."),
      "Español":("ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"),
      "العربية":("يناير","فبراير","مارس","أبريل","مايو","يونيو","يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"),
      "Azərbaycan dili":("yan","fev","mar","apr","may","iyn","iyl","avq","sen","okt","noy","dek")}
    if lang == "Deutsch":
        return f"{dt.day:02d}.{dt.month:02d}.{dt.year} · {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"
    if lang == "Français":
        return f"{dt.day:02d} {months[lang][dt.month-1]} {dt.year} · {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"
    if lang == "Español":
        return f"{dt.day:02d} {months[lang][dt.month-1]} {dt.year} · {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"
    if lang == "العربية":
        return f"{dt.day:02d} {months[lang][dt.month-1]} {dt.year} · {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"
    return f"{dt.day:02d} {months[lang][dt.month-1]} {dt.year} · {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"


def translate_structure(value: Any, language: str | None = None) -> Any:
    lang = language or CURRENT_LANGUAGE
    if isinstance(value, dict):
        return {translate(k, lang): translate_structure(v, lang) for k, v in value.items()}
    if isinstance(value, list):
        return [translate_structure(v, lang) for v in value]
    if isinstance(value, tuple):
        return tuple(translate_structure(v, lang) for v in value)
    if isinstance(value, str):
        return translate(value, lang)
    return value


def text_direction(language: str | None = None) -> str:
    lang = language or CURRENT_LANGUAGE
    return LANGUAGES.get(lang, LANGUAGES[TR])["direction"]


def locale_code(language: str | None = None) -> str:
    lang = language or CURRENT_LANGUAGE
    return LANGUAGES.get(lang, LANGUAGES[TR])["locale"]
