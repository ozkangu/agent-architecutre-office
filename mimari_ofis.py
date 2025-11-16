"""
Konfigüre Edilebilir Mimari Tasarım Ofisi AI Simülasyonu

Bu modül, farklı mimari uzmanlık alanlarını temsil eden AI ajanları kullanarak
mimari tasarım süreçlerini simüle eder.
"""

import autogen
from typing import List, Dict, Optional, Any
import json
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import yaml
import os

# ============= KONFIGURASYON SINIFLARI =============

class AjanTipi(Enum):
    """Mevcut ajan tipleri"""
    PROJE_YONETICISI = "proje_yoneticisi"
    BAS_TASARIMCI = "bas_tasarimci"
    ARASTIRMA_UZMANI = "arastirma_uzmani"
    SURDURULEBILIRLIK = "surdurulebilirlik"
    TEKNIK_MIMAR = "teknik_mimar"
    UX_TASARIMCI = "ux_tasarimci"
    BUTCE_UZMANI = "butce_uzmani"
    PEYZAJ_MIMARI = "peyzaj_mimari"
    AKUSTIK_DANISMAN = "akustik_danisman"
    AYDINLATMA_UZMANI = "aydinlatma_uzmani"
    YANGIN_GUVENLIK = "yangin_guvenlik"
    SANAT_YONETMENI = "sanat_yonetmeni"
    BIM_UZMANI = "bim_uzmani"
    MALZEME_UZMANI = "malzeme_uzmani"
    KENTSEL_PLANCI = "kentsel_planci"

@dataclass
class AjanKonfigurasyonu:
    """Tek bir ajan için konfigurasyon"""
    tip: AjanTipi
    aktif: bool = True
    model: str = "gpt-4-turbo-preview"
    temperature: float = 0.7
    max_tokens: int = 2000
    ozel_talimatlar: str = ""

@dataclass
class OfisKonfigurasyonu:
    """Tüm ofis için konfigurasyon"""
    proje_adi: str
    ajanlar: List[AjanKonfigurasyonu]
    max_tur: int = 20
    otomatik_mod: bool = True
    api_key: str = ""
    loglama: bool = True
    cikti_formati: str = "markdown"  # markdown, json, txt

# ============= AJAN FABRİKASI =============

class AjanFabrikasi:
    """Dinamik ajan oluşturucu"""

    # Ajan şablonları
    AJAN_SABLONLARI = {
        AjanTipi.PROJE_YONETICISI: {
            "isim": "Proje_Yoneticisi",
            "rol": """Sen deneyimli bir mimari proje yöneticisisin.
            Görevlerin:
            - Tasarım sürecini koordine etmek
            - Toplantıları yönetmek ve özetlemek
            - Kararları dokümante etmek
            - Zaman çizelgesini takip etmek
            - Ekip üyeleri arasında iletişimi sağlamak
            {ozel_talimatlar}
            Her tartışma sonunda ÖZET ve ALINAN KARARLAR başlıklarıyla durumu özetle."""
        },

        AjanTipi.BAS_TASARIMCI: {
            "isim": "Bas_Tasarimci",
            "rol": """Sen vizyoner bir baş mimarsın.
            Görevlerin:
            - Güçlü tasarım konseptleri geliştirmek
            - Form, fonksiyon ve estetik dengesi kurmak
            - Mekansal kalite ve atmosfer yaratmak
            - İkonik ve anlamlı tasarımlar üretmek
            {ozel_talimatlar}
            Konseptlerini şu başlıklarla sun: KONSEPT, FORM, MEKAN KALİTESİ, MALZEME PALETİ"""
        },

        AjanTipi.ARASTIRMA_UZMANI: {
            "isim": "Arastirma_Uzmani",
            "rol": """Sen detaylı araştırma yapan bir mimari araştırmacısın.
            Görevlerin:
            - Benzer projeler (precedent studies) araştırmak
            - Yerel yönetmelikleri ve yapı kodlarını incelemek
            - İklim ve çevre verilerini analiz etmek
            - Malzeme alternatifleri araştırmak
            {ozel_talimatlar}
            Araştırmalarını şu başlıklarla sun: PRECEDENT, YÖNETMELİK, BAĞLAM, FIRSATLAR"""
        },

        AjanTipi.SURDURULEBILIRLIK: {
            "isim": "Surdurulebilirlik_Danismani",
            "rol": """Sen LEED sertifikalı sürdürülebilir tasarım uzmanısın.
            Görevlerin:
            - Enerji verimliliği stratejileri geliştirmek
            - Pasif tasarım prensiplerini uygulamak
            - Yeşil malzeme önerileri yapmak
            - Su yönetimi çözümleri sunmak
            {ozel_talimatlar}
            Önerilerini şu başlıklarla sun: ENERJİ, MALZEME, SU, KARBON, SERTİFİKA"""
        },

        AjanTipi.TEKNIK_MIMAR: {
            "isim": "Teknik_Mimar",
            "rol": """Sen yapısal sistemler ve teknik detaylar konusunda uzman bir mimarsın.
            Görevlerin:
            - Taşıyıcı sistem önerileri yapmak
            - Yapı fiziği çözümleri geliştirmek
            - Detay çözümleri üretmek
            - MEP sistemleri entegrasyonu
            {ozel_talimatlar}
            Teknik çözümlerini şu başlıklarla sun: STRÜKTÜR, DETAYLAR, SİSTEMLER, RİSKLER"""
        },

        AjanTipi.UX_TASARIMCI: {
            "isim": "Kullanici_Deneyimi_Tasarimcisi",
            "rol": """Sen insan odaklı tasarım uzmanısın.
            Görevlerin:
            - Kullanıcı yolculuklarını tasarlamak
            - Erişilebilirlik standartlarını sağlamak
            - Sosyal etkileşim alanları yaratmak
            - Konfor ve ergonomi sağlamak
            {ozel_talimatlar}
            Analizini şu başlıklarla sun: KULLANICI PROFİLİ, DENEYİM, ERİŞİLEBİLİRLİK, KONFOR"""
        },

        AjanTipi.BUTCE_UZMANI: {
            "isim": "Butce_Uzmani",
            "rol": """Sen mimari projeler için maliyet analizi uzmanısın.
            Görevlerin:
            - İnşaat maliyeti tahmini yapmak
            - Değer mühendisliği önerileri sunmak
            - Maliyet optimizasyonu stratejileri
            - Yatırım geri dönüş analizi
            {ozel_talimatlar}
            Analizini şu başlıklarla sun: MALİYET TAHMİNİ, OPTİMİZASYON, ALTERNATİFLER, GETİRİ"""
        },

        AjanTipi.PEYZAJ_MIMARI: {
            "isim": "Peyzaj_Mimari",
            "rol": """Sen peyzaj tasarımı uzmanısın.
            Görevlerin:
            - Dış mekan tasarımı
            - Yeşil altyapı çözümleri
            - Bitkilendirme stratejileri
            - Su ögeleri tasarımı
            {ozel_talimatlar}"""
        },

        AjanTipi.AKUSTIK_DANISMAN: {
            "isim": "Akustik_Danisman",
            "rol": """Sen akustik tasarım uzmanısın.
            Görevlerin:
            - Ses yalıtımı çözümleri
            - Reverberasyon kontrolü
            - Gürültü analizi
            {ozel_talimatlar}"""
        },

        AjanTipi.AYDINLATMA_UZMANI: {
            "isim": "Aydinlatma_Uzmani",
            "rol": """Sen aydınlatma tasarımı uzmanısın.
            Görevlerin:
            - Doğal ışık optimizasyonu
            - Yapay aydınlatma tasarımı
            - Enerji verimli çözümler
            {ozel_talimatlar}"""
        },

        AjanTipi.YANGIN_GUVENLIK: {
            "isim": "Yangin_Guvenlik_Uzmani",
            "rol": """Sen yangın güvenliği ve acil durum uzmanısın.
            Görevlerin:
            - Yangın güvenlik stratejileri
            - Tahliye planları
            - Yasal uyumluluk kontrolü
            {ozel_talimatlar}"""
        },

        AjanTipi.SANAT_YONETMENI: {
            "isim": "Sanat_Yonetmeni",
            "rol": """Sen sanat yönetmeni ve kültürel danışmansın.
            Görevlerin:
            - Sanat entegrasyonu stratejileri
            - Kültürel kimlik oluşturma
            - Estetik koordinasyon
            {ozel_talimatlar}"""
        },

        AjanTipi.BIM_UZMANI: {
            "isim": "BIM_Uzmani",
            "rol": """Sen BIM koordinasyon uzmanısın.
            Görevlerin:
            - 3D modelleme koordinasyonu
            - Clash detection analizi
            - Parametrik tasarım çözümleri
            {ozel_talimatlar}"""
        },

        AjanTipi.MALZEME_UZMANI: {
            "isim": "Malzeme_Uzmani",
            "rol": """Sen malzeme ve yapı fiziği uzmanısın.
            Görevlerin:
            - İnovatif malzeme önerileri
            - Malzeme performans analizi
            - Yerel malzeme araştırması
            {ozel_talimatlar}"""
        },

        AjanTipi.KENTSEL_PLANCI: {
            "isim": "Kentsel_Planci",
            "rol": """Sen kentsel planlama uzmanısın.
            Görevlerin:
            - Kentsel bağlam analizi
            - Ulaşım ve erişilebilirlik
            - Kamusal alan tasarımı
            {ozel_talimatlar}"""
        }
    }

    @classmethod
    def ajan_olustur(cls, konfig: AjanKonfigurasyonu, api_key: str) -> autogen.AssistantAgent:
        """Konfigurasyon bazlı ajan oluştur"""

        sablon = cls.AJAN_SABLONLARI.get(konfig.tip)
        if not sablon:
            raise ValueError(f"Bilinmeyen ajan tipi: {konfig.tip}")

        llm_config = {
            "config_list": [{
                'model': konfig.model,
                'api_key': api_key,
            }],
            "temperature": konfig.temperature,
            "max_tokens": konfig.max_tokens,
        }

        system_message = sablon["rol"].format(
            ozel_talimatlar=f"\n{konfig.ozel_talimatlar}" if konfig.ozel_talimatlar else ""
        )

        return autogen.AssistantAgent(
            name=sablon["isim"],
            system_message=system_message,
            llm_config=llm_config,
        )

# ============= MİMARİ OFİS SIMÜLATÖRÜ =============

class MimariOfisSimulatoru:
    """Ana simülasyon sınıfı"""

    def __init__(self, konfigurasyon: OfisKonfigurasyonu):
        self.konfig = konfigurasyon
        self.ajanlar = []
        self.sohbet_gecmisi = []

    def ofis_kur(self):
        """Ofisteki ajanları oluştur"""
        print("🏗️  Mimari ofis kuruluyor...")

        for ajan_konfig in self.konfig.ajanlar:
            if ajan_konfig.aktif:
                try:
                    ajan = AjanFabrikasi.ajan_olustur(ajan_konfig, self.konfig.api_key)
                    self.ajanlar.append(ajan)
                    print(f"✅ {ajan_konfig.tip.value} eklendi")
                except Exception as e:
                    print(f"❌ {ajan_konfig.tip.value} eklenemedi: {e}")

        # Müşteri ajanı ekle
        self.musteri = autogen.UserProxyAgent(
            name="Musteri",
            human_input_mode="NEVER" if self.konfig.otomatik_mod else "TERMINATE",
            max_consecutive_auto_reply=1,
            code_execution_config=False,
        )

        print(f"📊 Toplam {len(self.ajanlar)} ajan aktif")

    def toplanti_baslat(self, proje_briefi: str) -> List[Dict]:
        """Tasarım toplantısını başlat"""

        if not self.ajanlar:
            raise ValueError("Hiç ajan eklenmemiş! Önce ofis_kur() çalıştırın.")

        # Grup sohbeti oluştur
        groupchat = autogen.GroupChat(
            agents=[self.musteri] + self.ajanlar,
            messages=[],
            max_round=self.konfig.max_tur,
            speaker_selection_method="auto",
        )

        # LLM config for manager
        manager_llm_config = {
            "config_list": [{
                'model': 'gpt-4-turbo-preview',
                'api_key': self.konfig.api_key,
            }],
            "temperature": 0.5,
        }

        # Grup yöneticisi
        manager = autogen.GroupChatManager(
            groupchat=groupchat,
            llm_config=manager_llm_config,
        )

        # Başlangıç mesajı
        baslangic = f"""
        🏗️ {self.konfig.proje_adi} - MİMARİ TASARIM TOPLANTISI

        📋 PROJE BRİEFİ:
        {proje_briefi}

        👥 KATILIMCILAR:
        {', '.join([ajan.name for ajan in self.ajanlar])}

        Toplantıyı başlatıyoruz. İlk söz Proje Yöneticisi'nde...
        """

        # Sohbeti başlat
        self.musteri.initiate_chat(
            manager,
            message=baslangic,
        )

        self.sohbet_gecmisi = groupchat.messages
        self._kaydet()

        return groupchat.messages

    def _kaydet(self):
        """Toplantı notlarını kaydet"""
        if not self.konfig.loglama:
            return

        # Çıktı klasörü oluştur
        output_dir = "cikti"
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.konfig.proje_adi}_{timestamp}"

        if self.konfig.cikti_formati == "markdown":
            self._markdown_kaydet(os.path.join(output_dir, f"{filename}.md"))
        elif self.konfig.cikti_formati == "json":
            self._json_kaydet(os.path.join(output_dir, f"{filename}.json"))
        else:
            self._txt_kaydet(os.path.join(output_dir, f"{filename}.txt"))

    def _markdown_kaydet(self, dosya_adi: str):
        """Markdown formatında kaydet"""
        with open(dosya_adi, "w", encoding="utf-8") as f:
            f.write(f"# {self.konfig.proje_adi} - Tasarım Toplantısı\n\n")
            f.write(f"**Tarih:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write("---\n\n")

            for msg in self.sohbet_gecmisi:
                f.write(f"## {msg.get('name', 'Anonim')}\n\n")
                f.write(f"{msg.get('content', '')}\n\n")
                f.write("---\n\n")

        print(f"📝 Toplantı notları kaydedildi: {dosya_adi}")

    def _json_kaydet(self, dosya_adi: str):
        """JSON formatında kaydet"""
        with open(dosya_adi, "w", encoding="utf-8") as f:
            json.dump({
                "proje": self.konfig.proje_adi,
                "tarih": datetime.now().isoformat(),
                "mesajlar": self.sohbet_gecmisi
            }, f, indent=2, ensure_ascii=False)

        print(f"📝 Toplantı notları kaydedildi: {dosya_adi}")

    def _txt_kaydet(self, dosya_adi: str):
        """Düz metin formatında kaydet"""
        with open(dosya_adi, "w", encoding="utf-8") as f:
            for msg in self.sohbet_gecmisi:
                f.write(f"{msg.get('name', 'Anonim')}: {msg.get('content', '')}\n")
                f.write("-" * 80 + "\n")

        print(f"📝 Toplantı notları kaydedildi: {dosya_adi}")

# ============= HAZIR ŞABLONLAR =============

class OfisTemplates:
    """Hazır ofis konfigürasyonları"""

    @staticmethod
    def minimal_ofis() -> OfisKonfigurasyonu:
        """Minimal ekip: Yönetici, Tasarımcı, Teknik"""
        return OfisKonfigurasyonu(
            proje_adi="Minimal_Proje",
            ajanlar=[
                AjanKonfigurasyonu(tip=AjanTipi.PROJE_YONETICISI),
                AjanKonfigurasyonu(tip=AjanTipi.BAS_TASARIMCI),
                AjanKonfigurasyonu(tip=AjanTipi.TEKNIK_MIMAR),
            ],
            max_tur=10,
            otomatik_mod=True,
            api_key="",
            loglama=True,
            cikti_formati="markdown"
        )

    @staticmethod
    def surdurulebilir_ofis() -> OfisKonfigurasyonu:
        """Sürdürülebilirlik odaklı ekip"""
        return OfisKonfigurasyonu(
            proje_adi="Yesil_Proje",
            ajanlar=[
                AjanKonfigurasyonu(tip=AjanTipi.PROJE_YONETICISI),
                AjanKonfigurasyonu(tip=AjanTipi.BAS_TASARIMCI),
                AjanKonfigurasyonu(tip=AjanTipi.SURDURULEBILIRLIK),
                AjanKonfigurasyonu(tip=AjanTipi.PEYZAJ_MIMARI),
                AjanKonfigurasyonu(tip=AjanTipi.MALZEME_UZMANI),
            ],
            max_tur=15,
            otomatik_mod=True,
            api_key="",
            loglama=True,
            cikti_formati="markdown"
        )

    @staticmethod
    def tam_ekip_ofis() -> OfisKonfigurasyonu:
        """Tam donanımlı büyük ofis"""
        return OfisKonfigurasyonu(
            proje_adi="Buyuk_Proje",
            ajanlar=[
                AjanKonfigurasyonu(tip=AjanTipi.PROJE_YONETICISI),
                AjanKonfigurasyonu(tip=AjanTipi.BAS_TASARIMCI),
                AjanKonfigurasyonu(tip=AjanTipi.ARASTIRMA_UZMANI),
                AjanKonfigurasyonu(tip=AjanTipi.SURDURULEBILIRLIK),
                AjanKonfigurasyonu(tip=AjanTipi.TEKNIK_MIMAR),
                AjanKonfigurasyonu(tip=AjanTipi.UX_TASARIMCI),
                AjanKonfigurasyonu(tip=AjanTipi.BUTCE_UZMANI),
                AjanKonfigurasyonu(tip=AjanTipi.PEYZAJ_MIMARI),
                AjanKonfigurasyonu(tip=AjanTipi.BIM_UZMANI),
            ],
            max_tur=25,
            otomatik_mod=True,
            api_key="",
            loglama=True,
            cikti_formati="markdown"
        )

# ============= İNTERAKTİF KULLANIM =============

class InteraktifOfisKurucu:
    """Kullanıcı dostu ofis kurulum arayüzü"""

    @staticmethod
    def kullanici_menusu():
        """İnteraktif menü"""
        print("\n" + "="*60)
        print("🏗️  MİMARİ OFİS SIMÜLATÖRÜ")
        print("="*60)
        print("\n1. Hazır Şablon Kullan")
        print("2. Özel Ofis Oluştur")
        print("3. Konfigurasyon Dosyasından Yükle")
        print("4. Çıkış")

        secim = input("\nSeçiminiz (1-4): ").strip()
        return secim

    @staticmethod
    def sablon_sec():
        """Hazır şablon seçimi"""
        print("\n📋 HAZIR ŞABLONLAR:")
        print("1. Minimal Ofis (3 ajan)")
        print("2. Sürdürülebilir Ofis (5 ajan)")
        print("3. Tam Ekip Ofis (9 ajan)")

        secim = input("\nŞablon seçin (1-3): ").strip()

        sablonlar = {
            "1": OfisTemplates.minimal_ofis(),
            "2": OfisTemplates.surdurulebilir_ofis(),
            "3": OfisTemplates.tam_ekip_ofis()
        }

        return sablonlar.get(secim, OfisTemplates.minimal_ofis())

    @staticmethod
    def ozel_ofis_olustur():
        """Kullanıcı tanımlı ofis oluştur"""
        print("\n🔧 ÖZEL OFİS OLUŞTURMA")

        proje_adi = input("Proje Adı: ").strip() or "Ozel_Proje"

        print("\n👥 AJAN SEÇİMİ (virgülle ayırın, örnek: 1,2,5,7)")
        print("Mevcut ajanlar:")

        for i, ajan_tipi in enumerate(AjanTipi, 1):
            print(f"{i}. {ajan_tipi.value}")

        secimler = input("\nAjan numaraları: ").strip().split(",")

        ajanlar = []
        for secim in secimler:
            try:
                index = int(secim.strip()) - 1
                ajan_tipi = list(AjanTipi)[index]

                # Özel talimat sorgusu
                ozel = input(f"\n{ajan_tipi.value} için özel talimat (opsiyonel): ").strip()

                ajanlar.append(AjanKonfigurasyonu(
                    tip=ajan_tipi,
                    ozel_talimatlar=ozel
                ))
            except:
                print(f"⚠️  Geçersiz seçim: {secim}")

        max_tur = int(input("\nMaksimum konuşma turu (önerilen: 15): ").strip() or "15")

        return OfisKonfigurasyonu(
            proje_adi=proje_adi,
            ajanlar=ajanlar,
            max_tur=max_tur,
            otomatik_mod=True,
            api_key="",
            loglama=True,
            cikti_formati="markdown"
        )

    @staticmethod
    def konfigurasyon_yukle(dosya_yolu: str) -> OfisKonfigurasyonu:
        """YAML/JSON dosyasından konfigurasyon yükle"""
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            if dosya_yolu.endswith('.yaml') or dosya_yolu.endswith('.yml'):
                data = yaml.safe_load(f)
            else:
                data = json.load(f)

        ajanlar = []
        for ajan_data in data.get('ajanlar', []):
            ajanlar.append(AjanKonfigurasyonu(
                tip=AjanTipi[ajan_data['tip'].upper()],
                aktif=ajan_data.get('aktif', True),
                model=ajan_data.get('model', 'gpt-4-turbo-preview'),
                temperature=ajan_data.get('temperature', 0.7),
                ozel_talimatlar=ajan_data.get('ozel_talimatlar', '')
            ))

        return OfisKonfigurasyonu(
            proje_adi=data['proje_adi'],
            ajanlar=ajanlar,
            max_tur=data.get('max_tur', 20),
            otomatik_mod=data.get('otomatik_mod', True),
            api_key=data.get('api_key', ''),
            loglama=data.get('loglama', True),
            cikti_formati=data.get('cikti_formati', 'markdown')
        )

# ============= ANA PROGRAM =============

def main():
    """Ana program döngüsü"""

    kurucu = InteraktifOfisKurucu()

    while True:
        secim = kurucu.kullanici_menusu()

        if secim == "4":
            print("\n👋 Güle güle!")
            break

        # Konfigurasyon oluştur
        if secim == "1":
            konfig = kurucu.sablon_sec()
        elif secim == "2":
            konfig = kurucu.ozel_ofis_olustur()
        elif secim == "3":
            dosya_yolu = input("Konfigurasyon dosya yolu: ").strip()
            try:
                konfig = kurucu.konfigurasyon_yukle(dosya_yolu)
            except Exception as e:
                print(f"❌ Dosya yüklenemedi: {e}")
                continue
        else:
            print("⚠️  Geçersiz seçim!")
            continue

        # API Key
        api_key = input("\nOpenAI API Key: ").strip()
        if not api_key:
            print("❌ API Key gerekli!")
            continue
        konfig.api_key = api_key

        # Proje briefi
        print("\n📋 PROJE BRİEFİ GİRİN (bitirmek için boş satır):")
        brief_lines = []
        while True:
            line = input()
            if not line:
                break
            brief_lines.append(line)

        proje_briefi = "\n".join(brief_lines)

        if not proje_briefi:
            # Örnek brief
            proje_briefi = """
            PROJE: Modern Sanat Müzesi
            ALAN: 8000 m²
            BÜTÇE: 100 Milyon TL
            HEDEF: İkonik, sürdürülebilir, toplumla iç içe
            """

        # Simülasyonu başlat
        try:
            print("\n🚀 Simülasyon başlıyor...")
            simulator = MimariOfisSimulatoru(konfig)
            simulator.ofis_kur()
            simulator.toplanti_baslat(proje_briefi)
            print("\n✅ Simülasyon tamamlandı! Notlar kaydedildi.")
        except Exception as e:
            print(f"\n❌ Hata: {e}")
            import traceback
            traceback.print_exc()

# ============= ÖRNEK KONFİGURASYON DOSYASI =============

def ornek_yaml_olustur():
    """Örnek YAML konfigurasyon dosyası oluştur"""
    ornek = """# Mimari Ofis Konfigurasyon Dosyası
proje_adi: "Akilli_Sehir_Kompleksi"
max_tur: 20
otomatik_mod: true
loglama: true
cikti_formati: "markdown"

ajanlar:
  - tip: "proje_yoneticisi"
    aktif: true
    model: "gpt-4-turbo-preview"
    temperature: 0.5
    ozel_talimatlar: "Sürdürülebilirlik hedeflerini öne çıkar"

  - tip: "bas_tasarimci"
    aktif: true
    model: "gpt-4-turbo-preview"
    temperature: 0.8
    ozel_talimatlar: "Parametrik tasarım yaklaşımlarını kullan"

  - tip: "surdurulebilirlik"
    aktif: true
    model: "gpt-4-turbo-preview"
    temperature: 0.6
    ozel_talimatlar: "Net-zero enerji hedefine odaklan"

  - tip: "bim_uzmani"
    aktif: true
    model: "gpt-4-turbo-preview"
    temperature: 0.5
    ozel_talimatlar: "Revit ve Dynamo entegrasyonunu düşün"

  - tip: "butce_uzmani"
    aktif: false  # Bu ajan devre dışı
    model: "gpt-4-turbo-preview"
    temperature: 0.5
"""

    with open("ornek_konfigurasyon.yaml", "w", encoding="utf-8") as f:
        f.write(ornek)

    print("📁 'ornek_konfigurasyon.yaml' dosyası oluşturuldu!")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--ornek":
        ornek_yaml_olustur()
    else:
        main()
