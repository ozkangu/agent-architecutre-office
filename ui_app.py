"""
Mimari Tasarım Ofisi AI Simülatörü - Web UI

Gradio tabanlı interaktif web arayüzü
"""

import gradio as gr
from mimari_ofis import (
    MimariOfisSimulatoru,
    OfisKonfigurasyonu,
    AjanKonfigurasyonu,
    AjanTipi,
    AjanFabrikasi,
    OfisTemplates
)
from typing import List, Dict, Any, Tuple
import json
import threading
import queue
import time
from dataclasses import asdict

# Global message queue for real-time updates
message_queue = queue.Queue()

class CustomMessageListener:
    """AutoGen mesajlarını yakalamak için özel listener"""
    def __init__(self, msg_queue):
        self.msg_queue = msg_queue

    def __call__(self, sender, recipient, message):
        """Mesaj gönderildiğinde çağrılır"""
        self.msg_queue.put({
            'sender': sender.name if hasattr(sender, 'name') else str(sender),
            'recipient': recipient.name if hasattr(recipient, 'name') else str(recipient),
            'content': message.get('content', '') if isinstance(message, dict) else str(message)
        })

# OpenRouter Modelleri (Popüler seçenekler)
OPENROUTER_MODELS = [
    # Anthropic Claude
    "anthropic/claude-3.5-sonnet",
    "anthropic/claude-3-opus",
    "anthropic/claude-3-sonnet",
    "anthropic/claude-3-haiku",

    # OpenAI GPT
    "openai/gpt-4-turbo-preview",
    "openai/gpt-4",
    "openai/gpt-3.5-turbo",

    # Google
    "google/gemini-pro-1.5",
    "google/gemini-pro",

    # Meta Llama
    "meta-llama/llama-3-70b-instruct",
    "meta-llama/llama-3-8b-instruct",

    # Mistral
    "mistralai/mistral-large",
    "mistralai/mistral-medium",
    "mistralai/mixtral-8x7b-instruct",

    # Others
    "perplexity/llama-3-sonar-large-32k-chat",
    "qwen/qwen-2-72b-instruct",
]

# Agent bilgileri ve açıklamaları
AJAN_ACIKLAMALARI = {
    AjanTipi.PROJE_YONETICISI: "Koordinasyon, dokümantasyon ve takım yönetimi",
    AjanTipi.BAS_TASARIMCI: "Tasarım konsepti, form ve estetik vizyon",
    AjanTipi.ARASTIRMA_UZMANI: "Precedent studies, yönetmelik ve bağlam analizi",
    AjanTipi.SURDURULEBILIRLIK: "LEED, enerji verimliliği, yeşil sertifikalar",
    AjanTipi.TEKNIK_MIMAR: "Strüktür, yapı fiziği, teknik detaylar",
    AjanTipi.UX_TASARIMCI: "Kullanıcı deneyimi, erişilebilirlik, ergonomi",
    AjanTipi.BUTCE_UZMANI: "Maliyet analizi, değer mühendisliği",
    AjanTipi.PEYZAJ_MIMARI: "Dış mekan, yeşil altyapı, bitkilendirme",
    AjanTipi.AKUSTIK_DANISMAN: "Ses yalıtımı, akustik performans",
    AjanTipi.AYDINLATMA_UZMANI: "Doğal ve yapay aydınlatma tasarımı",
    AjanTipi.YANGIN_GUVENLIK: "Yangın güvenliği, tahliye stratejileri",
    AjanTipi.SANAT_YONETMENI: "Sanat entegrasyonu, kültürel kimlik",
    AjanTipi.BIM_UZMANI: "3D modelleme, parametrik tasarım",
    AjanTipi.MALZEME_UZMANI: "İnovatif malzemeler, performans analizi",
    AjanTipi.KENTSEL_PLANCI: "Kentsel bağlam, ulaşım, kamusal alan"
}

def create_agent_config_ui():
    """Agent konfigürasyon UI'ı oluştur"""
    agent_configs = {}

    with gr.Accordion("🔧 Agent Seçimi ve Konfigürasyonu", open=True):
        gr.Markdown("### Projeye dahil etmek istediğiniz agent'ları seçin ve yapılandırın")

        for ajan_tipi in AjanTipi:
            with gr.Group():
                with gr.Row():
                    # Agent seçim checkbox
                    aktif = gr.Checkbox(
                        label=f"✅ {ajan_tipi.value.replace('_', ' ').title()}",
                        value=False,
                        scale=2
                    )

                with gr.Row(visible=False) as config_row:
                    with gr.Column(scale=1):
                        gr.Markdown(f"**Açıklama:** {AJAN_ACIKLAMALARI[ajan_tipi]}")

                        temperature = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=0.7,
                            step=0.1,
                            label="Temperature (Yaratıcılık)",
                            info="Düşük=tutarlı, Yüksek=yaratıcı"
                        )

                        model = gr.Dropdown(
                            choices=OPENROUTER_MODELS,
                            value="anthropic/claude-3.5-sonnet",
                            label="Model (OpenRouter)",
                            info="OpenRouter üzerinden erişilebilen tüm modeller"
                        )

                        ozel_talimatlar = gr.Textbox(
                            label="Özel Talimatlar",
                            placeholder="Bu agent için özel talimatlar...",
                            lines=3
                        )

                # Toggle visibility of config when checkbox is clicked
                def toggle_config(checked):
                    return gr.update(visible=checked)

                aktif.change(
                    fn=toggle_config,
                    inputs=[aktif],
                    outputs=[config_row]
                )

                agent_configs[ajan_tipi] = {
                    'aktif': aktif,
                    'temperature': temperature,
                    'model': model,
                    'ozel_talimatlar': ozel_talimatlar
                }

    return agent_configs

def create_custom_agent_ui():
    """Özel agent oluşturma UI'ı"""
    with gr.Accordion("➕ Yeni Özel Agent Oluştur", open=False):
        gr.Markdown("### Kendi özel agent'ınızı tanımlayın")

        with gr.Row():
            custom_name = gr.Textbox(
                label="Agent Adı",
                placeholder="Örn: Enerji_Analiz_Uzmani"
            )
            custom_model = gr.Dropdown(
                choices=["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"],
                value="gpt-4-turbo-preview",
                label="Model"
            )

        custom_role = gr.Textbox(
            label="Rol Tanımı (System Message)",
            placeholder="Sen ... uzmanısın. Görevlerin: ...",
            lines=5
        )

        custom_temperature = gr.Slider(
            minimum=0.0,
            maximum=1.0,
            value=0.7,
            step=0.1,
            label="Temperature"
        )

        add_custom_btn = gr.Button("🆕 Özel Agent'ı Ekle", variant="secondary")
        custom_status = gr.Textbox(label="Durum", interactive=False)

    return {
        'name': custom_name,
        'model': custom_model,
        'role': custom_role,
        'temperature': custom_temperature,
        'button': add_custom_btn,
        'status': custom_status
    }

def run_simulation(
    proje_adi: str,
    proje_briefi: str,
    max_tur: int,
    api_key: str,
    agent_configs: Dict,
    progress=gr.Progress()
) -> Tuple[str, List[Tuple[str, str]]]:
    """Simülasyonu çalıştır"""

    if not api_key:
        return "❌ Lütfen OpenAI API Key girin!", []

    if not proje_briefi:
        return "❌ Lütfen proje briefi girin!", []

    # Seçili agent'ları topla
    ajanlar = []
    for ajan_tipi, config in agent_configs.items():
        if isinstance(config, dict) and 'aktif' in config:
            # UI'dan gelen değerleri al (bu noktada değerler çekilmiş olmalı)
            # Ama bu fonksiyon çağrıldığında değerler parametre olarak gelmeli
            # Bu yüzden bu kısmı düzeltelim
            pass

    return "⚠️ Bu fonksiyon agent config parametrelerini doğru almıyor. Düzeltme gerekiyor.", []

def load_template(template_name: str) -> Dict:
    """Hazır şablon yükle"""
    templates = {
        "Minimal Ofis (3 agent)": OfisTemplates.minimal_ofis(),
        "Sürdürülebilir Ofis (5 agent)": OfisTemplates.surdurulebilir_ofis(),
        "Tam Ekip Ofis (9 agent)": OfisTemplates.tam_ekip_ofis()
    }

    template = templates.get(template_name)
    if not template:
        return {}

    # Template'teki aktif agent'ları döndür
    active_agents = {}
    for ajan_konfig in template.ajanlar:
        active_agents[ajan_konfig.tip.value] = {
            'aktif': ajan_konfig.aktif,
            'temperature': ajan_konfig.temperature,
            'model': ajan_konfig.model,
            'ozel_talimatlar': ajan_konfig.ozel_talimatlar
        }

    return active_agents

def create_main_ui():
    """Ana UI'ı oluştur"""

    with gr.Blocks(
        theme=gr.themes.Soft(),
        title="🏗️ Mimari Tasarım Ofisi AI Simülatörü",
        css="""
        .chat-message {
            padding: 10px;
            margin: 5px 0;
            border-radius: 8px;
        }
        .agent-message {
            background-color: #f0f0f0;
        }
        """
    ) as app:

        gr.Markdown("""
        # 🏗️ Mimari Tasarım Ofisi AI Simülatörü

        ### Farklı uzmanlık alanlarındaki AI agent'larını seçin ve tasarım toplantısı simüle edin
        """)

        with gr.Tabs():
            # Tab 1: Proje Ayarları
            with gr.Tab("📋 Proje Ayarları"):
                with gr.Row():
                    with gr.Column(scale=1):
                        proje_adi_input = gr.Textbox(
                            label="Proje Adı",
                            placeholder="Örn: Modern_Sanat_Muzesi",
                            value="Yeni_Proje"
                        )

                        api_provider_input = gr.Radio(
                            choices=["openrouter", "openai"],
                            value="openrouter",
                            label="API Provider",
                            info="OpenRouter: Çoklu model erişimi (önerilen)"
                        )

                        api_key_input = gr.Textbox(
                            label="API Key",
                            placeholder="OpenRouter: sk-or-... | OpenAI: sk-...",
                            type="password",
                            info="OpenRouter key: https://openrouter.ai/keys"
                        )

                        max_tur_input = gr.Slider(
                            minimum=5,
                            maximum=50,
                            value=20,
                            step=5,
                            label="Maksimum Konuşma Turu"
                        )

                        cikti_format_input = gr.Radio(
                            choices=["markdown", "json", "txt"],
                            value="markdown",
                            label="Çıktı Formatı"
                        )

                    with gr.Column(scale=2):
                        proje_briefi_input = gr.Textbox(
                            label="Proje Briefi",
                            placeholder="""Örnek:
PROJE: Modern Sanat Müzesi
ALAN: 8000 m²
BÜTÇE: 100 Milyon TL
HEDEF: İkonik, sürdürülebilir, toplumla iç içe
KONUM: İstanbul, Beşiktaş
ÖZELLİKLER:
- Esnek sergileme alanları
- Kafe ve müze mağazası
- Açık hava heykel bahçesi
- Eğitim atölyeleri""",
                            lines=15
                        )

                with gr.Row():
                    template_dropdown = gr.Dropdown(
                        choices=[
                            "Minimal Ofis (3 agent)",
                            "Sürdürülebilir Ofis (5 agent)",
                            "Tam Ekip Ofis (9 agent)"
                        ],
                        label="🎨 Hazır Şablon Yükle",
                        value=None
                    )
                    load_template_btn = gr.Button("📥 Şablonu Yükle", variant="secondary")

            # Tab 2: Agent Seçimi
            with gr.Tab("👥 Agent Seçimi ve Konfigürasyonu"):
                agent_configs = create_agent_config_ui()

            # Tab 3: Özel Agent
            with gr.Tab("➕ Özel Agent"):
                custom_agent_ui = create_custom_agent_ui()

            # Tab 4: Simülasyon
            with gr.Tab("🚀 Simülasyon"):
                gr.Markdown("### Toplantıyı Başlat ve Takip Et")

                with gr.Row():
                    start_btn = gr.Button(
                        "🎬 Toplantıyı Başlat",
                        variant="primary",
                        size="lg"
                    )
                    stop_btn = gr.Button(
                        "⏹️ Durdur",
                        variant="stop",
                        size="lg"
                    )

                status_output = gr.Textbox(
                    label="Durum",
                    interactive=False,
                    lines=2
                )

                with gr.Row():
                    with gr.Column(scale=3):
                        chat_output = gr.Chatbot(
                            label="💬 Toplantı Konuşmaları",
                            height=600,
                            bubble_full_width=False
                        )

                    with gr.Column(scale=1):
                        participants_output = gr.Textbox(
                            label="👥 Katılımcılar",
                            interactive=False,
                            lines=20
                        )

                download_btn = gr.Button("💾 Toplantı Notlarını İndir")
                download_output = gr.File(label="İndirilecek Dosya")

        # Event handlers
        def gather_agent_configs():
            """Tüm agent konfigürasyonlarını topla"""
            configs = {}
            for ajan_tipi, ui_components in agent_configs.items():
                configs[ajan_tipi.value] = ui_components
            return configs

        def start_simulation_wrapper(
            proje_adi, api_provider, api_key, proje_briefi, max_tur, cikti_format, *agent_values
        ):
            """Simülasyonu başlat (wrapper)"""

            if not api_key:
                return "❌ API Key gerekli!", [], "", None

            if not proje_briefi:
                return "❌ Proje briefi gerekli!", [], "", None

            # Agent config değerlerini parse et
            # Her agent için 4 değer var: aktif, temperature, model, ozel_talimatlar
            ajanlar = []
            agent_types = list(AjanTipi)

            aktif_agent_isimleri = []

            for i, ajan_tipi in enumerate(agent_types):
                idx = i * 4
                if idx + 3 < len(agent_values):
                    aktif = agent_values[idx]
                    temperature = agent_values[idx + 1]
                    model = agent_values[idx + 2]
                    ozel_talimatlar = agent_values[idx + 3]

                    if aktif:
                        ajanlar.append(AjanKonfigurasyonu(
                            tip=ajan_tipi,
                            aktif=True,
                            temperature=temperature,
                            model=model,
                            ozel_talimatlar=ozel_talimatlar or "",
                            api_provider=api_provider
                        ))
                        aktif_agent_isimleri.append(
                            ajan_tipi.value.replace('_', ' ').title()
                        )

            if not ajanlar:
                return "❌ En az bir agent seçmelisiniz!", [], "", None

            # Konfigürasyonu oluştur
            konfig = OfisKonfigurasyonu(
                proje_adi=proje_adi,
                ajanlar=ajanlar,
                max_tur=int(max_tur),
                otomatik_mod=True,
                api_key=api_key,
                api_provider=api_provider,
                loglama=True,
                cikti_formati=cikti_format
            )

            participants_text = "📋 Seçilen Agent'lar:\n\n" + "\n".join(
                f"✓ {name}" for name in aktif_agent_isimleri
            )

            # Simülasyonu çalıştır
            try:
                simulator = MimariOfisSimulatoru(konfig)
                simulator.ofis_kur()

                messages = simulator.toplanti_baslat(proje_briefi)

                # Chat formatına dönüştür
                chat_messages = []
                for msg in messages:
                    sender = msg.get('name', 'Sistem')
                    content = msg.get('content', '')
                    chat_messages.append((sender, content))

                status = f"✅ Toplantı tamamlandı! {len(messages)} mesaj oluşturuldu."

                # Son kaydedilen dosyayı bul
                import os
                import glob
                output_files = glob.glob(f"cikti/{proje_adi}_*.{cikti_format}")
                latest_file = max(output_files, key=os.path.getctime) if output_files else None

                return status, chat_messages, participants_text, latest_file

            except Exception as e:
                return f"❌ Hata: {str(e)}", [], participants_text, None

        # Tüm agent input'larını topla
        agent_inputs = []
        for ajan_tipi in AjanTipi:
            config = agent_configs[ajan_tipi]
            agent_inputs.extend([
                config['aktif'],
                config['temperature'],
                config['model'],
                config['ozel_talimatlar']
            ])

        # Start butonu
        start_btn.click(
            fn=start_simulation_wrapper,
            inputs=[
                proje_adi_input,
                api_provider_input,
                api_key_input,
                proje_briefi_input,
                max_tur_input,
                cikti_format_input
            ] + agent_inputs,
            outputs=[
                status_output,
                chat_output,
                participants_output,
                download_output
            ]
        )

        # Template yükleme
        def load_template_handler(template_name):
            """Şablon yükle ve agent'ları güncelle"""
            if not template_name:
                return [gr.update() for _ in range(len(AjanTipi) * 4)]

            templates = {
                "Minimal Ofis (3 agent)": OfisTemplates.minimal_ofis(),
                "Sürdürülebilir Ofis (5 agent)": OfisTemplates.surdurulebilir_ofis(),
                "Tam Ekip Ofis (9 agent)": OfisTemplates.tam_ekip_ofis()
            }

            template = templates.get(template_name)
            if not template:
                return [gr.update() for _ in range(len(AjanTipi) * 4)]

            # Template'teki aktif agent'ları bul
            active_types = {a.tip: a for a in template.ajanlar if a.aktif}

            updates = []
            for ajan_tipi in AjanTipi:
                if ajan_tipi in active_types:
                    ajan_konfig = active_types[ajan_tipi]
                    updates.extend([
                        gr.update(value=True),  # aktif
                        gr.update(value=ajan_konfig.temperature),
                        gr.update(value=ajan_konfig.model),
                        gr.update(value=ajan_konfig.ozel_talimatlar)
                    ])
                else:
                    updates.extend([
                        gr.update(value=False),  # aktif değil
                        gr.update(value=0.7),
                        gr.update(value="gpt-4-turbo-preview"),
                        gr.update(value="")
                    ])

            return updates

        load_template_btn.click(
            fn=load_template_handler,
            inputs=[template_dropdown],
            outputs=agent_inputs
        )

        gr.Markdown("""
        ---
        ### 💡 Kullanım İpuçları
        - **Proje Ayarları**: Proje adınızı ve detaylı briefi girin
        - **Agent Seçimi**: İhtiyacınıza göre agent'ları seçin ve konfigüre edin
        - **Hazır Şablonlar**: Hızlı başlamak için hazır şablonları kullanın
        - **Simülasyon**: Toplantıyı başlatın ve agent'ların tartışmasını izleyin
        - **İndirme**: Toplantı notlarını markdown/json/txt formatında indirin
        """)

    return app

if __name__ == "__main__":
    app = create_main_ui()
    app.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )
