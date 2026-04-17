Çoklu Kaynak ve Metadata Destekli RAG Sistemi
Bu proje, farklı formatlardaki (TXT, CSV, JSON) kurumsal verileri entegre ederek, kullanıcı sorularına en güncel ve doğrulanmış yanıtları sağlayan bir Retrieval-Augmented Generation (RAG) pipeline tasarımıdır. Sistem, özellikle statik belgeler ile dinamik güncelleme logları arasındaki çelişkileri çözme ve tablo verilerini bağlamını bozmadan işleme yeteneğine odaklanmaktadır.

Mimari Kararlar ve Teknik Detaylar
1. Veri Yükleme ve İşleme Stratejisi
Proje, verinin doğasına göre üç farklı işleme stratejisi kullanmaktadır:

Metin Verisi (TXT): Şirketin temel sözleşme maddeleri TextLoader ile yüklenerek hukuki dildeki madde bütünlüğü korunmuştur.

Tablo Verisi (CSV): Standart chunking yöntemlerinin tablo yapısını bozması nedeniyle, her satır kendi sütun başlıklarıyla birleştirilerek anlamlı birer cümle şeklinde vektörize edilmiştir. Bu sayede fiyat ve limit bilgileri birbirine karışmadan doğru bağlamda sorgulanabilmektedir.

Log Kayıtları (JSON): Güncelleme kayıtları, sistemin "en güncel bilgiyi seçme" yeteneğini test etmek amacıyla yarı-yapılandırılmış formatta işlenmiştir. Her log, kategori ve etkilenen paket bilgilerini içeren zengin bir metadata yapısıyla sisteme dahil edilmiştir.

2. Vektörizasyon ve Semantik Arama
Embedding Modeli: Türkçe dil desteği ve semantik benzerlik başarısı nedeniyle sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 modeli tercih edilmiştir.

Vektör Veritabanı: Metadata filtreleme desteği ve hızlı prototipleme imkanı sunan in-memory Chroma kullanılmıştır.

Retrieval: Kullanıcı sorgularına en uygun 6 farklı veri bloğu (k=6) çekilerek LLM'e sunulmaktadır.

Veri Seti Detayları
Sözleşme (sozlesme.txt): Şirketin hizmet kapsamı, KVKK taahhütleri ve standart iade süreleri gibi yapılandırılmamış hukuki metinleri içerir.

Fiyat Listesi (paket_fiyatlari.csv): Basic, Pro ve Enterprise paketlerinin aylık fiyatlarını ve teknik limitlerini içeren tablo verisidir.

Güncelleme Logları (guncellemeler.json): Zaman içinde değişen fiyatları, yeni güvenlik kurallarını ve kampanya iptallerini içeren kronolojik kayıtlardır. Bu dosya, sistemin çelişkili veriler arasında karar verici mekanizması olarak çalışır.

Karşılaşılan Zorluklar ve Çözümler
Zaman Algısı ve Mantık Hataları: Testler sırasında modelin, güncel tarihi bilmediği için geçmişteki kampanya sürelerini hala geçerli sandığı (Mayıs 2025 kuralını gelecek bir tarih sanması gibi) gözlemlenmiştir. Bu durum, prompt içerisine dinamik tarih bağlamı (Örn: "Bugünün tarihi: 16 Nisan 2026") eklenerek çözülmüş ve modelin kronolojik mantık yürütmesi sağlanmıştır.

API ve Model Uyumluluğu: Google Gemini API versiyon geçişleri ve ücretsiz sunuculardaki anlık yoğunluklar (503/404 hataları) try-except bloklarıyla yönetilmiş ve sistem en kararlı çalışan gemini-2.5-flash modeline optimize edilmiştir.

Kurulum Adımları
1. Gereksinimler
Sistemde Python 3.10+ sürümü kurulu olmalıdır. Proje, kütüphane erişimini kolaylaştırmak ve sistem terminaliyle tam uyum sağlamak için global interpreter üzerinden çalışacak şekilde yapılandırılmıştır.

2. Bağımlılıkların Yüklenmesi
Bash
pip install pandas langchain-community langchain-huggingface langchain-google-genai chromadb python-dotenv
3. Ortam Değişkenleri
Kök dizinde bir .env dosyası oluşturun ve API anahtarınızı ekleyin:

Plaintext
GOOGLE_API_KEY=your_api_key_here
4. Projeyi Çalıştırma
Sistemi başlatmak ve interaktif sohbet moduna geçmek için:

Bash
python app.py
Proje Çıktısı
Sistem, bir kullanıcı sorusu geldiğinde üç kaynağı aynı anda tarar. Örneğin, bir fiyat sorulduğunda önce CSV'deki taban fiyatı bulur, ardından JSON loglarında bu fiyata bir güncelleme gelip gelmediğini kontrol eder. Eğer bir güncelleme varsa, kullanıcıya eski veriyi değil, en güncel logdaki veriyi "GÜNCELLEME NOTU" referansıyla sunar.

Multi-Source & Metadata-Driven RAG System
This project implements a Retrieval-Augmented Generation (RAG) pipeline designed to integrate corporate data from various formats (TXT, CSV, JSON). The core objective of the system is to provide accurate, verified responses to user queries by resolving conflicts between static legal documents and dynamic update logs through a chronological priority logic.

Architectural Decisions & Technical Details
1. Data Ingestion & Processing Strategy
The system employs distinct ingestion strategies tailored to the nature of the data:

Textual Data (TXT): General terms and conditions were processed using TextLoader to maintain the integrity of legal clauses and hierarchical numbering.

Tabular Data (CSV): To prevent standard chunking methods from breaking row/column relationships, each row was transformed into a discrete Document object by merging cell values with their respective headers. This ensures that pricing and limits remain contextually linked during vector retrieval.

Update Logs (JSON): Dynamic records were ingested as semi-structured data to test the system's "latest-truth" selection capabilities. Each log entry is enriched with metadata (category, affected package, date) to allow for precise filtering.

2. Vectorization & Semantic Search
Embedding Model: I utilized sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 due to its high performance in semantic similarity for Turkish and multi-language support.

Vector Store: In-memory Chroma was chosen for its robust metadata filtering support and rapid prototyping capabilities.

Retrieval Logic: The system retrieves the top 6 most relevant data segments (k=6) to provide the LLM with sufficient context for resolving potential informational conflicts.

Dataset Specifications
Contract (sozlesme.txt): Contains unstructured legal text regarding service scope, GDPR (KVKK) commitments, and standard refund policies.

Price List (paket_fiyatlari.csv): Structured tabular data defining monthly prices and technical quotas for Basic, Pro, and Enterprise tiers.

Update Logs (guncellemeler.json): A chronological stream of records capturing price hikes, security policy changes, and campaign expirations. This file serves as the "decision-making" layer for the system.

Challenges & Engineering Solutions
Temporal Context & Logic Errors: Initial testing revealed that the model lacked an inherent sense of "today," leading it to misinterpret past campaign dates as still valid (e.g., treating a May 2025 rule as a future event). This was resolved by injecting a dynamic temporal context (e.g., "Today is April 17, 2026") into the system prompt, enabling accurate chronological reasoning.

API Stability & Model Fallbacks: Regional demand spikes on Google Gemini servers (503/404 errors) were managed through try-except blocks and a robust retry logic. The system is currently optimized for the gemini-2.5-flash model for the best balance of speed and reasoning.

Setup & Installation
1. Prerequisites
Python 3.10+ is required. This project is configured to run via the global interpreter to streamline library management and ensure terminal compatibility across environments.

2. Dependencies
Install the required packages using the following command:

Bash
pip install pandas langchain-community langchain-huggingface langchain-google-genai chromadb python-dotenv
3. Environment Variables
Create a .env file in the root directory and add your Google AI Studio API key:

Plaintext
GOOGLE_API_KEY=your_api_key_here
4. Running the Project
Launch the system and enter interactive chat mode:

Bash
python app.py
System Workflow
Upon receiving a query, the system scans all three sources simultaneously. For instance, when asked about pricing, it identifies the base price in the CSV, cross-references it with the JSON logs for any recent updates or hikes, and presents the most current "Update Note" to the user with full source attribution.