import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("OnlineRetail.csv",encoding="ISO-8859-1")

df= df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]#Burada iptal olan siparişleri sildik

df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate']) #Burada tarihi tarih olarak okumasını sağladık

df['TotalPrice'] = df['Quantity'] * df['UnitPrice']

df.dropna(subset=['CustomerID'], inplace=True) #customerıd'yi sildik veri daha doğru olcak boyle


print("Temizlik sonrası boş ID sayısı:", df['CustomerID'].isnull().sum()) #Burada temizlik yaptık.
df['CustomerID'] = df['CustomerID'].astype(int) #Burada customerıd'nin tipini değiştirdik çünkü tipi floatdı yani ondalıklı ama ıd yarım olamaz.
print(df.head(5))
print(df.describe())

#EN ÇOK SATAN 10 ÜRÜN
# En çok satan ilk 10 ürünün tamamının dekorasyon ve parti malzemesi olması, müşteri kitlesinin "etkinlik ve özel gün" odaklı olduğunu gösteriyor.
#Burda görüldüğü üzere Gelirin büyük bir kısmı tek bir ürüne (Paper Craft) bağımlı. Stok tükenmesi riskine karşı ürün çeşitliliği artırılmalı.
# Kargo gelirlerinin (Postage) 6. sırada olması, nakliye ücretlerinin ciroda beklenenden çok daha kritik bir rol oynadığını kanıtlıyor.
encokonurun = df.groupby('Description')['TotalPrice'].sum().sort_values(ascending=False).head(10)
print(encokonurun)
#EN ÖOK HANGİ ÜLKEDEN SİPARİŞ GELİYOR 
# İngiltere pazarının ardından Almanya ve Fransa, en yüksek sipariş frekansına sahip stratejik pazarlar olarak öne çıkmaktadır.
filtered = df[df['Country'] != 'United Kingdom'] # İngilteriyi çıkardık çünkü zaten verinin %90 'nını oluşturuyordu.
encoksipariş = filtered.groupby('Country')['InvoiceNo'].nunique().sort_values(ascending=False)
print(encoksipariş)
#grafikteki gösterimi
plt.figure(figsize=(12,6))
sns.barplot(x=encoksipariş.index,y=encoksipariş.values,palette="magma")
plt.title("EN ÇOK HANGİ ÜLKEDEN SİPARİŞ GELİYOR")
plt.xticks(rotation = 45,ha='right')
plt.show()
#GUNUN HANGİ SAATLERİ DAHA YOGUN
# InvoiceDate içindeki saat bilgisini çekip yeni bir sütun oluşturuyoruz 
# Saat 06:00'dan 12:00'ye kadar dik bir çıkış var, saat 15:00'ten sonra ise sert bir düşüş başlıyor.
df['Hour'] = df['InvoiceDate'].dt.hour
saatyogunlu=df.groupby('Hour')['TotalPrice'].sum()
print(saatyogunlu)
sns.lineplot(x=saatyogunlu.index,y=saatyogunlu.values,marker='o')
plt.xticks(range(0,25))
plt.show()
#HANGİ GUNLER DAHA YOĞUN
# Burda da gördüğümüze göre en yoğun gün perşembe günü gözüküyor.
#En yoğun gün Perşembe olduğu için, Çarşamba akşamından stokların ve personelin bu yoğunluğa göre hazır edilmesi operasyonel maliyeti düşürecektir.
# En düşük satışlar ise pazar günüdür. Pazar günkü düşük satışı canlandırmak için "Pazartesiye hazırlık" temalı indirimler yapılabilir.
gun_sirasi = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Sunday']
df['day'] = df['InvoiceDate'].dt.day_name()
gunluk_kazanc = df.groupby('day')['TotalPrice'].sum()
gunluk_kazanc = gunluk_kazanc.reindex(gun_sirasi)
print(gunluk_kazanc)
#GETİRİN %80 NİNİ SAGLAYAN MUSTERİ GRUBU
#Müşterilerinin sadece %26'sı toplam kazancının %80'ini getiriyor. Bu, işletmenin başarısının çok küçük ve sadık bir kitleye bağlı olduğunu kanıtlar.
# Reklam bütçesini 4339 kişiye eşit dağıtmak yerine, 
# bu 1132 kişiye özel "sadakat programları", "kişiye özel indirimler" veya "erken erişim hakları" verilmelidir. Çünkü senin asıl paranı bu ekip kazandırıyor.

musteri_harcama = df.groupby('CustomerID')['TotalPrice'].sum().sort_values(ascending=False).reset_index()
toplam_ciro = musteri_harcama['TotalPrice'].sum()
musteri_harcama['kumalitiftoplam'] = musteri_harcama['TotalPrice'].cumsum()
musteri_harcama['yuzdesekseni'] = (musteri_harcama['kumalitiftoplam'] / toplam_ciro) * 100
vipmusteri = musteri_harcama[musteri_harcama['yuzdesekseni'] <= 80]
print(f"Gelirin %80 'ini sağlayan VIP müşteri sayısı:{len(vipmusteri)}")
print(vipmusteri.head(10))
#AYLIK BUYUME
df['aylik'] = df['InvoiceDate'].dt.to_period('M')
aylikkazanc = df.groupby("aylik")["TotalPrice"].sum()
aylikbuyume = aylikkazanc.pct_change() * 100
print(aylikbuyume)
#AYLIK BUYUME GRAFİĞİ
#İşletme mevsimsel geçişlerde (Bahar ve Sonbahar başı) çok güçlü bir talep görüyor. Muhtemelen yeni sezon ürün stokları veya okul/iş başı dönemleri bu büyümeyi tetikliyor."
#Satışlar stabil bir büyüme trendinde değil, kampanya odaklı veya stok yenileme döngülerine bağlı olarak aşırı dalgalı seyrediyor.
plt.figure(figsize=(12,6))
sns.lineplot(x=aylikbuyume.index.astype(str),y=aylikbuyume.values,marker='o',color="green",linewidth= 2.5)
plt.title("AYLIK BÜYÜME",fontsize=15)
plt.xlabel("Ay", fontsize=12)
plt.ylabel("Büyüme Yüzdesi (%)", fontsize=12)
plt.xticks(rotation=45)
plt.show()
#EN AZ 10 KERE ALIŞVERİŞ YAPMIŞ MÜŞTERİLER
# Müşteri sadakat oranı %9 seviyesinde.
# Listeye baktığımızda en üstteki müşteri (CustomerID: 12748) tam 209 kez alışveriş yapmış! Onu 14911 (201 kez) ve 17841 (124 kez) takip ediyor.
# Bu 391 kişilik gruba özel bir "VIP Kartı" veya "Ömür Boyu Ücretsiz Kargo" gibi tanımlamalar yapılmalı. 
musteriler=df.groupby('CustomerID')['InvoiceNo'].nunique().reset_index()
yildiz= musteriler[musteriler['InvoiceNo'] >= 10].sort_values(by='InvoiceNo',ascending=False)
print(f"Toplam müsteri sayısı{len(musteriler)}")
print(f"10 dan fazla alışveriş yapmış müşteriler {len(yildiz)}")
print(yildiz.head(10))
#EN EN ÇOK SATILACAK 5 ÜRÜNÜ TAHMİN EDİYORUZ
#PAPER CRAFT için tahmin edilen miktar yaklaşık 26,998
# Stoklarda bu miktarı karşılayacak ürün yoksa acilen tedarik edilmeli. Aksi takdirde satabileceğimiz malı yokluktan satamayız.
df['aylik'] = df['InvoiceDate'].dt.to_period('M')
aylik_satis=df.groupby(['aylik','Description'])['Quantity'].sum().reset_index()
pivoty=aylik_satis.pivot(index='aylik',columns='Description',values='Quantity').fillna(0)
tahmin=pivoty.rolling(window=3).mean().iloc[-1]
en_iyi_5_tahmin = tahmin.sort_values(ascending=False).head(5)
print(en_iyi_5_tahmin)
#STOK RİSKİ OLAN ÜRÜNLER
#PAPER CRAFT , LITTLE BIRDIE bu ürün günde ortalama 217 adet satılıyor. Bu inanılmaz bir hız.Eğer depomuzda bu üründen binlerce yoksa, birkaç gün içinde 'yok satmaya' başlarız.
#Bu 10 ürün dükkanın en çok satan  ürünleri. Bunların stoklarını takip etmek için manuel sayım yerine,
# stok miktarı belirli bir seviyenin (örneğin 500 adet) altına düştüğünde otomatik uyarı veren bir sistem kurmalıyız."
toplam_ürün = df.groupby("Description")["Quantity"].sum()
gun_sayisi = (df['InvoiceDate'].max() - df['InvoiceDate'].min()).days
gunluk_satiş = toplam_ürün / gun_sayisi
stok_riski = gunluk_satiş.sort_values(ascending= False).head(10)
print(f"Stok riski en yüksek 10 ürün {stok_riski}")
#FİYAT %10 ARTARSA CİRO NASIL ETKİLENİR
df['yeni_fiyat'] = df['UnitPrice'] * 1.10
df['yeni_toplam'] = df['Quantity'] * df['yeni_fiyat']
eski_ciro = df['TotalPrice'].sum()
yeni_ciro = df['yeni_toplam'].sum()
print(f"Eski ciro: {eski_ciro}")
print(f"yeni ciro: {yeni_ciro}")
fark = (eski_ciro / yeni_ciro) * 100
print(f"Aralarında ki fark{fark}")  
#HANGİ ÜRÜNÜ ARTIK SATMAMALIYIZ
#Bu ürünler  hem satış adedi hem de getirdiği ciro bakımından listemizin en zayıf halkası. Depoda kapladığı alan, bize maliyetinden daha fazla yük getiriyor
urunler=df.groupby("Description").agg({'Quantity':'sum','TotalPrice': 'sum',
    'InvoiceDate': 'max'})
silinecekler = urunler[
    (urunler['Quantity'] < 5) & 
    (urunler['TotalPrice'] < 100)
]
sonuc=silinecekler.sort_values(ascending=True,by="TotalPrice").head(10)
print(f"Silinece ürünler: {sonuc}")






