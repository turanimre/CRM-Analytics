import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.float_format', lambda x: '%.3f' % x)


#### İş problemi

'''

Online ayakkabı mağazası olan FLO müşterilerini segmentlere ayırıp bu segmentlere göre pazarlama
stratejileri belirlemek istiyor. Buna yönelik olarak müşterilerin davranışları tanımlanacak ve bu
davranışlardaki öbeklenmelere göre gruplar oluşturulacak.

'''


#### Veri seti & Değişkenler

'''
master_id:  Eşsiz müşteri numarası
order_channel:  Alışveriş yapılan platforma ait hangi kanalın kullanıldığı (Android, ios, Desktop, Mobile)
last_order_channel:  En son alışverişin yapıldığı kanal
first_order_date:  Müşterinin yaptığı ilk alışveriş tarihi
last_order_date:  Müşterinin yaptığı son alışveriş tarihi
last_order_date_online:  Müşterinin online platformda yaptığı son alışveriş tarihi
last_order_date_offline:  Müşterinin offline platformda yaptığı son alışveriş tarihi
order_num_total_ever_online:  Müşterinin online platformda yaptığı toplam alışveriş sayısı
order_num_total_ever_offline:  Müşterinin offline'da yaptığı toplam alışveriş sayısı
customer_value_total_ever_offline:  Müşterinin offline alışverişlerinde ödediği toplam ücret
customer_value_total_ever_online:  Müşterinin online alışverişlerinde ödediği toplam ücret
interested_in_categories_12:  Müşterinin son 12 ayda alışveriş yaptığı kategorilerin listesi

'''

#######################
## Görev 1: Veriyi Anlama ve Hazırlama
#######################

dff = pd.read_csv("Miuul_Course_1/CRM Analytics/Datasets/flo_data_20k.csv")
df = dff.copy()


### Adım 1: Veri setinde
#### a) İlk 10 gözlem
df.head(10)

#### b) Değişken isimleri
df.columns

#### c) Betimsel istatistik
df.describe().T

#### d) Boş değer
df.isnull().sum()

#### e) Değişken tipleri, incelemesi yapınız
df.info()


### Adım 2:  Omnichannel müşterilerin hem online'dan hemde offline platformlardan alışveriş yaptığını ifade etmektedir.
# Her bir müşterinin toplam alışveriş sayısı ve harcaması için yeni değişkenler oluşturunuz.

df["order_channel"].value_counts()

df["frequency"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df["monetary"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]


### Adım 3:  Değişken tiplerini inceleyiniz. Tarih ifade eden değişkenlerin tipini date'e çeviriniz.

df.info()
date_col = [col for col in df.columns if "date" in col]

for i in date_col:
    df[i] = pd.to_datetime(df[i])

### Adım 4:  Alışveriş kanallarındaki müşteri sayısının, toplam alınan ürün sayısının ve toplam harcamaların dağılımına bakınız.

df.groupby("order_channel").agg({"master_id": "count",
                                 "order_num_total_ever_online": "sum",
                                 "customer_value_total_ever_online": "sum"})


### Adım 5:  En fazla kazancı getiren ilk 10 müşteriyi sıralayınız.

df.sort_values(by="monetary", ascending=False).head(10)


### Adım 6:  En fazla siparişi veren ilk 10 müşteriyi sıralayınız.

df.sort_values(by="frequency", ascending=False).head(10)


### Adım 7: Veri ön hazırlık sürecini fonksiyonlaştırınız.


def data_prep(dataframe):

    dataframe["frequency"] = dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
    dataframe["monetary"] = dataframe["customer_value_total_ever_offline"] + dataframe["customer_value_total_ever_online"]
    date_colm = [col for col in dataframe.columns if "date" in col]
    for j in date_colm:
        dataframe[j] = pd.to_datetime(dataframe[j])
    print(dataframe.head(10))
    print(dataframe.info())

data_prep(dff)


#######################
## Görev 2: RFM Metriklerinin Hesaplanması
#######################

### Adım 1: Recency, Frequency ve Monetary tanımlarını yapınız.

'''

Recency : Müşterinin en son alışverişinden analiz gününe kadar geçen gün sayısıdır.

Frequency : Müşterinin toplam kaç defa alışveriş(online-ofline) yaptığının sayısıdır.

Monetary : Müşterinin yaptığı alışverişlerde toplamda ne kadarlık harcama yaptığıdır.

'''

### Adım 2: Müşteri özelinde Recency, Frequency ve Monetary metriklerini hesaplayınız.

# df["last_order_date"].max()

analysis_day = pd.to_datetime("2021-06-01")
df["recency"] = df["last_order_date"].apply(lambda x: (analysis_day - x).days)

df["frequency"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]

df["monetary"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]

### Adım 3: Hesapladığınız metrikleri rfm isimli bir değişkene atayınız.


rfm = df[["recency", "frequency", "monetary"]]

rfm.head()


#######################
## Görev 3: RFM Skorunun Hesaplanması
#######################


### Adım 1: Recency, Frequency ve Monetary metriklerini qcut yardımı ile 1-5 arasında skorlara çeviriniz.

### Adım 2: Bu skorları recency_score, frequency_score ve monetary_score olarak kaydediniz.

rfm["recency_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5])


### Adım 3: recency_score ve frequency_score’u tek bir değişken olarak ifade ediniz ve RF_SCORE olarak kaydediniz.

rfm["rf_score"] = rfm["recency_score"].astype("string") + rfm["frequency_score"].astype("string")



#######################
## Görev 4: RF Scorunun Segment Olarak Tanımlanması
#######################


### Adım 1: Oluşturulan RF skorları için segment tanımlamaları yapınız.


seg_map = {
    r"[1-2][1-2]" : "hibernating",
    r"[1-2][3-4]" : "at_risk",
    r"[1-2]5" : "cant_lose",
    r"3[1-2]" : "about_to_sleep",
    r"33" : "need_attention",
    r"[3-4][4-5]" : "loyal_customers",
    r"41" : "promising",
    r"51" : "new_customer",
    r"[4-5][2-3]" : "potential_loyalist",
    r"5[4-5]" : "champions"

}

### Adım 2: Aşağıdaki seg_map yardımı ile skorları segmentlere çeviriniz.

rfm.info()

rfm["rf_score"] = rfm["rf_score"].astype("str")
rfm["segment"] = rfm["rf_score"].replace(seg_map, regex=True)


#######################
## Görev 5: Aksiyon Zamanı
#######################

### Adım 1: Segmentlerin recency, frequnecy ve monetary ortalamalarını inceleyiniz.

rfm.groupby("segment").agg({"recency": "mean",
                            "frequency": "mean",
                            "monetary": "mean"})


### Adım 2: RFM analizi yardımıyla aşağıda verilen 2 case için ilgili profildeki müşterileri bulun ve müşteri id'lerini csv olarak kaydediniz.

'''

a. FLO bünyesine yeni bir kadın ayakkabı markası dahil ediyor. Dahil ettiği markanın ürün fiyatları genel müşteri
tercihlerinin üstünde. Bu nedenle markanın tanıtımı ve ürün satışları için ilgilenecek profildeki müşterilerle özel olarak
iletişime geçmek isteniliyor. Sadık müşterilerinden(champions, loyal_customers) ve kadın kategorisinden alışveriş
yapan kişiler özel olarak iletişim kurulacak müşteriler. Bu müşterilerin id numaralarını csv dosyasına kaydediniz.

'''

df["segment"] = rfm["segment"]

df.loc[(df["interested_in_categories_12"].str.contains("KADIN") & ((df["segment"] == "loyal_customers") | (df["segment"] == "champions"))), "master_id"].to_csv("Miuul_Course_1/CRM Analytics/Output_Case_study_1/flo_output_1.csv")


'''

b. Erkek ve Çocuk ürünlerinde %40'a yakın indirim planlanmaktadır. Bu indirimle ilgili kategorilerle ilgilenen geçmişte
iyi müşteri olan ama uzun süredir alışveriş yapmayan kaybedilmemesi gereken müşteriler, uykuda olanlar ve yeni
gelen müşteriler özel olarak hedef alınmak isteniyor. Uygun profildeki müşterilerin id'lerini csv dosyasına kaydediniz.

'''
df["segment"].value_counts()

df.loc[(df["interested_in_categories_12"].str.contains("ERKEK", "COCUK") & ((df["segment"] == "cant_lose") | (df["segment"] == "new_customer") | (df["segment"] == "about_to_sleep"))), "master_id"].to_csv("Miuul_Course_1/CRM Analytics/Output_Case_study_1/flo_output_2.csv")



