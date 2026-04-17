import os
import pandas as pd
import json
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def verileri_yukle():
    dokumanlar = []
    
    try:
        txt_yukleyici = TextLoader("data/sozlesme.txt", encoding="utf-8")
        dokumanlar.extend(txt_yukleyici.load())
    except Exception as e:
        print(f"Sözleşme yüklenemedi: {e}")
        

    try:
        df = pd.read_csv("data/paket_fiyatlari.csv")
        for index, satir in df.iterrows():
            icerik = (f"Paket Adı: {satir['paket_adi']}, Aylık Fiyat: {satir['aylik_fiyat_tl']} TL, "
                      f"İndirim: {satir['yillik_indirim_orani']}, Kullanıcı Limiti: {satir['kullanici_limiti']}, "
                      f"Depolama: {satir['depolama_gb']} GB, API İstek Limiti: {satir['api_istek_limiti_aylik']}, "
                      f"Destek: {satir['destek_seviyesi']}, SLA Garantisi: {satir['sla_garantisi']}")
            
            metadata = {
                "kaynak": "paket_fiyatlari.csv", 
                "tip": "tablo_satiri",
                "paket": satir['paket_adi']
            }
            dokumanlar.append(Document(page_content=icerik, metadata=metadata))
    except Exception as e:
        print(f"Tablo yüklenemedi: {e}")
        

    try:
        with open("data/guncellemeler.json", "r", encoding="utf-8") as f:
            guncellemeler = json.load(f)
            for g in guncellemeler:
                icerik = f"GÜNCELLEME NOTU [{g.get('kategori', 'Genel')}]: {g.get('degisiklik')}"
                metadata = {
                    "kaynak": "guncellemeler.json", 
                    "tarih": g.get("tarih", "Bilinmiyor"),
                    "log_id": g.get("log_id", "Bilinmiyor"),
                    "etkilenen_paket": g.get("etkilenen_paket", "Tümü/Belirtilmemiş")
                }
                dokumanlar.append(Document(page_content=icerik, metadata=metadata))
    except Exception as e:
        print(f"Loglar yüklenemedi: {e}")
            
    return dokumanlar

def vektor_veritabani_olustur(dokumanlar):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    db = Chroma.from_documents(dokumanlar, embeddings)
    return db



if __name__ == "__main__":
    print("Sistem verileri okuyor ve vektörleri hazırlıyor (Lütfen bekleyin)...")
    veriler = verileri_yukle()
    db = vektor_veritabani_olustur(veriler)
    print("\nSİSTEM HAZIR! ✅")
    print("="*50)
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    
    print("Sohbet Asistanı başlatıldı! Çıkmak için 'q', 'exit' veya 'çıkış' yazabilirsiniz.\n")
    
  
    while True:
    
        soru = input("You: ")
        
        if soru.lower() in ['q', 'exit', 'çıkış', 'quit', 'cikis']:
            print("Sistem kapatılıyor. İyi günler!")
            break  
            
        if not soru.strip():
            continue
            
        bulunan_dokumanlar = db.similarity_search(soru, k=6)
        baglam_metni = "\n\n".join([doc.page_content for doc in bulunan_dokumanlar])
        
        prompt = f"""
        Sen şirketin resmi yapay zeka müşteri temsilcisisin. 
        Sana verilen aşağıdaki sistem kayıtlarına ve sözleşme maddelerine bakarak kullanıcının sorusuna cevap ver.
        
        KURALLAR:
        1. Eğer eski bir sözleşme maddesi veya tablo bilgisi ile yeni bir "GÜNCELLEME NOTU" çelişiyorsa, HER ZAMAN GÜNCELLEME NOTUNU baz al.
        2. Cevabını verirken hangi dosyalardan/tarihlerden yararlandığını referans olarak mutlaka belirt.
        3. Kullanıcının sorusu verilen metinlerde yoksa, uydurma. "Bu bilgiye erişimim yok" de.
        
        SİSTEM KAYITLARI:
        {baglam_metni}
        
        MÜŞTERİ SORUSU: {soru}
        
        CEVAP:
        """
        
        try:
            print("Sohbet Asistanı düşünüyor...\n")
            cevap = llm.invoke(prompt)
            print("Sohbet Asistanı:")
            print(cevap.content)
        except Exception as e:
            print(f"Sistemsel bir hata oluştu (Sunucu meşgul olabilir): {e}")
            
        print("\n" + "-"*60 + "\n")
