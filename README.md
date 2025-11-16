# 🏗️ Mimari Tasarım Ofisi AI Simülatörü

Farklı mimari uzmanlık alanlarındaki AI ajanlarını kullanarak mimari tasarım süreçlerini simüle eden konfigüre edilebilir bir sistem.

## 🎯 Amaç

Mimari tasarım ofislerinde sözel ve düşünsel yükü azaltmak, farklı konularda gelen isteklerde gerekli rollerin otomatik olarak konfigüre edilip çağırılmasını ve birbirleriyle tartışarak sonuç üretmelerini sağlamak.

## ✨ Özellikler

- **🖥️ Modern Web UI** (Gradio tabanlı interaktif arayüz)
- **15+ farklı uzman ajan tipi** (Proje Yöneticisi, Baş Tasarımcı, Sürdürülebilirlik Danışmanı, vb.)
- **Tam özelleştirilebilir konfigürasyon** (model, temperature, özel talimatlar)
- **Real-time konuşma takibi** (Agent'ların tartışmalarını canlı izleyin)
- **YAML/JSON konfig dosyası desteği**
- **İnteraktif ve programatik kullanım**
- **Hazır şablonlar** (Minimal, Sürdürülebilir, Tam Ekip)
- **Markdown/JSON/TXT çıktı formatları**
- **Otomatik toplantı notları**

## 📋 Gereksinimler

- Python 3.8+
- OpenAI API Key

## 🚀 Kurulum

```bash
# Depoyu klonlayın
git clone <repo-url>
cd agent-architecutre-office

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

## 💡 Kullanım

### 1. 🖥️ Web UI (Önerilen)

Modern, kullanıcı dostu web arayüzü ile:

```bash
python ui_app.py
```

Tarayıcınızda otomatik olarak açılacak arayüzde:

**📋 Proje Ayarları Sekmesi:**
- Proje adı ve API key girin
- Detaylı proje briefi oluşturun
- Hazır şablonları yükleyin

**👥 Agent Seçimi Sekmesi:**
- İstediğiniz agent'ları seçin (checkbox ile)
- Her agent için özel ayarlar yapın:
  - Temperature (yaratıcılık seviyesi)
  - Model seçimi (GPT-4, GPT-3.5, Claude vb.)
  - Özel talimatlar

**➕ Özel Agent Sekmesi:**
- Kendi özel agent'larınızı oluşturun
- Özel rol tanımları yapın

**🚀 Simülasyon Sekmesi:**
- Toplantıyı başlatın
- Agent'ların konuşmalarını canlı takip edin
- Toplantı notlarını indirin

**Erişim:**
- Yerel: http://localhost:7860
- Ağ: http://0.0.0.0:7860

### 2. İnteraktif Terminal Modu

```bash
python mimari_ofis.py
```

Menüden seçim yaparak:
1. Hazır şablon kullanabilirsiniz
2. Özel ofis oluşturabilirsiniz
3. Konfigurasyon dosyasından yükleyebilirsiniz

### 3. Örnek Konfigurasyon Oluşturma

```bash
python mimari_ofis.py --ornek
```

Bu komut `ornek_konfigurasyon.yaml` dosyası oluşturur.

### 4. Programatik Kullanım

```python
from mimari_ofis import (
    MimariOfisSimulatoru,
    OfisKonfigurasyonu,
    AjanKonfigurasyonu,
    AjanTipi
)

# Özel bir ofis konfigürasyonu oluştur
konfig = OfisKonfigurasyonu(
    proje_adi="Modern_Muzesi",
    ajanlar=[
        AjanKonfigurasyonu(
            tip=AjanTipi.PROJE_YONETICISI,
            ozel_talimatlar="Sürdürülebilirlik odaklı"
        ),
        AjanKonfigurasyonu(
            tip=AjanTipi.BAS_TASARIMCI,
            temperature=0.8
        ),
        AjanKonfigurasyonu(
            tip=AjanTipi.SURDURULEBILIRLIK
        ),
    ],
    max_tur=15,
    api_key="your-api-key",
    cikti_formati="markdown"
)

# Simülatörü başlat
simulator = MimariOfisSimulatoru(konfig)
simulator.ofis_kur()

# Toplantıyı başlat
proje_briefi = """
PROJE: Modern Sanat Müzesi
ALAN: 8000 m²
BÜTÇE: 100 Milyon TL
HEDEF: İkonik, sürdürülebilir, toplumla iç içe
"""

simulator.toplanti_baslat(proje_briefi)
```

### 5. Konfigurasyon Dosyası ile Kullanım

```bash
python mimari_ofis.py
# Menüden "3. Konfigurasyon Dosyasından Yükle" seçin
# ornek_konfigurasyon.yaml dosya yolunu girin
```

## 🖼️ Web UI Ekran Görüntüleri

Web arayüzü şu özellikleri sunar:

- ✅ Checkbox ile kolay agent seçimi
- 🎚️ Her agent için slider ile temperature ayarı
- 📝 Özel talimat alanları
- 💬 Canlı chat görünümü
- 📥 Tek tık ile toplantı notlarını indirme
- 🎨 Hazır şablon yükleme
- ➕ Özel agent oluşturma

## 🧑‍💼 Mevcut Ajan Tipleri

1. **Proje Yöneticisi** - Koordinasyon ve dokümantasyon
2. **Baş Tasarımcı** - Konsept ve tasarım vizyonu
3. **Araştırma Uzmanı** - Precedent studies, yönetmelik analizi
4. **Sürdürülebilirlik Danışmanı** - LEED, enerji verimliliği
5. **Teknik Mimar** - Strüktür, yapı fiziği, detaylar
6. **UX Tasarımcı** - Kullanıcı deneyimi, erişilebilirlik
7. **Bütçe Uzmanı** - Maliyet analizi, optimizasyon
8. **Peyzaj Mimarı** - Dış mekan, yeşil altyapı
9. **Akustik Danışman** - Ses yalıtımı, reverberasyon
10. **Aydınlatma Uzmanı** - Doğal ve yapay aydınlatma
11. **Yangın Güvenlik** - Güvenlik stratejileri, tahliye
12. **Sanat Yönetmeni** - Sanat entegrasyonu
13. **BIM Uzmanı** - 3D modelleme, parametrik tasarım
14. **Malzeme Uzmanı** - İnovatif malzemeler, performans
15. **Kentsel Plancı** - Urban context, kamusal alan

## 📂 Çıktı Formatları

Toplantı notları otomatik olarak `cikti/` klasörüne kaydedilir:

- **Markdown** (.md) - Okunabilir format, başlıklarla organize
- **JSON** (.json) - Programatik işleme için yapısal veri
- **Text** (.txt) - Düz metin format

## 🎨 Hazır Şablonlar

### Minimal Ofis (3 ajan)
Küçük projeler için temel ekip:
- Proje Yöneticisi
- Baş Tasarımcı
- Teknik Mimar

### Sürdürülebilir Ofis (5 ajan)
Yeşil binalar için:
- Proje Yöneticisi
- Baş Tasarımcı
- Sürdürülebilirlik Danışmanı
- Peyzaj Mimarı
- Malzeme Uzmanı

### Tam Ekip Ofis (9 ajan)
Büyük ve kompleks projeler için:
- Proje Yöneticisi
- Baş Tasarımcı
- Araştırma Uzmanı
- Sürdürülebilirlik Danışmanı
- Teknik Mimar
- UX Tasarımcı
- Bütçe Uzmanı
- Peyzaj Mimarı
- BIM Uzmanı

## ⚙️ Konfigürasyon Parametreleri

```yaml
proje_adi: "Proje_Adi"
max_tur: 20              # Maksimum konuşma turu
otomatik_mod: true       # Otomatik/Manuel mod
loglama: true            # Çıktı kaydetme
cikti_formati: "markdown" # markdown, json, txt

ajanlar:
  - tip: "proje_yoneticisi"
    aktif: true
    model: "gpt-4-turbo-preview"
    temperature: 0.7     # 0.0-1.0 arası yaratıcılık
    max_tokens: 2000
    ozel_talimatlar: "Özel talimatlar buraya"
```

## 🔐 API Key Yönetimi

API Key'inizi güvenli tutmak için `.env` dosyası kullanabilirsiniz:

```bash
# .env dosyası oluştur
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

```python
# Python kodunuzda
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
```

## 📝 Örnek Kullanım Senaryoları

### Senaryo 1: Müze Projesi
```python
konfig = OfisTemplates.tam_ekip_ofis()
konfig.proje_adi = "Cagdas_Sanat_Muzesi"
konfig.api_key = "your-key"

simulator = MimariOfisSimulatoru(konfig)
simulator.ofis_kur()
simulator.toplanti_baslat("Modern bir sanat müzesi...")
```

### Senaryo 2: Yeşil Ofis Binası
```python
konfig = OfisTemplates.surdurulebilir_ofis()
konfig.proje_adi = "Net_Zero_Ofis"
# ... devamı
```

## 🤝 Katkıda Bulunma

Bu proje açık kaynak olarak geliştirilmektedir. Katkılarınızı bekliyoruz!

## 📄 Lisans

MIT License

## 🙏 Teşekkürler

Bu proje [AutoGen](https://github.com/microsoft/autogen) framework kullanılarak geliştirilmiştir.

## 📞 İletişim

Sorularınız için issue açabilirsiniz.

---

**Not:** Bu sistem gerçek mimari kararlar için yalnızca bir başlangıç noktası ve fikir üretici olarak kullanılmalıdır. Tüm tasarım kararları lisanslı mimarlar tarafından onaylanmalıdır.
