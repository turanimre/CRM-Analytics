import pandas as pd
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter


pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.float_format', lambda x: '%.3f' % x)


#### İş problemi

'''

FLO satış ve pazarlama faaliyetleri için roadmap belirlemek istemektedir. Şirketin orta uzun vadeli plan
yapabilmesi için var olan müşterilerin gelecekte şirkete sağlayacakları potansiyel değerin tahmin edilmesi
gerekmektedir.

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

##############################################
## Görev 1: Veriyi Hazırlama
##############################################

dff = pd.read_csv("Miuul_Course_1/CRM Analytics/Datasets/flo_data_20k.csv")
df = dff.copy()


### Adım 2: Aykırı değerleri baskılamak için gerekli olan outlier_thresholds ve replace_with_thresholds fonksiyonlarını tanımlayınız.
# Not: cltv hesaplanırken frequency değerleri integer olması gerekmektedir.Bu nedenle alt ve üst limitlerini round() ile yuvarlayınız.

def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquantille_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantille_range
    low_limit = quartile1 - 1.5 * interquantille_range
    return low_limit, up_limit

def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = int(low_limit)
    dataframe.loc[(dataframe[variable] > up_limit), variable] = int(up_limit)

### Adım 3: "order_num_total_ever_online", "order_num_total_ever_offline", "customer_value_total_ever_offline",
# "customer_value_total_ever_online" değişkenlerinin aykırı değerleri varsa baskılayanız.

col_outlier = [col for col in df.columns if "total" in col]

for i in col_outlier:
    replace_with_thresholds(df, i)

df.describe().T


### Adım 4: Omnichannel müşterilerin hem online'dan hem de offline platformlardan alışveriş yaptığını ifade etmektedir. Her bir müşterinin toplam
# alışveriş sayısı ve harcaması için yeni değişkenler oluşturunuz.

df.head()

df["total_order"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df["total_purchese"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]


### Adım 5: Değişken tiplerini inceleyiniz. Tarih ifade eden değişkenlerin tipini date'e çeviriniz.


date_col = [col for col in df.columns if "date" in col]

for i in date_col:
    df[i] = pd.to_datetime(df[i])

df.info()

##############################################
## Görev 2: CLTV Veri Yapısının Oluşturulması
##############################################

### Adım 1: Veri setindeki en son alışverişin yapıldığı tarihten 2 gün sonrasını analiz tarihi olarak alınız.

df["last_order_date"].max()
analysis_day = pd.to_datetime("2021-06-01")

### Adım 2: customer_id, recency_cltv_weekly, T_weekly, frequency ve monetary_cltv_avg değerlerinin yer aldığı yeni bir cltv dataframe'i oluşturunuz.
# Monetary değeri satın alma başına ortalama değer olarak, recency ve tenure değerleri ise haftalık cinsten ifade edilecek.

cltv = pd.DataFrame()

cltv.index = df["master_id"]
cltv["recency_cltv_weekly"] = ((df["last_order_date"] - df["first_order_date"]).astype("timedelta64[D]"))/7
cltv["T_weekly"] = ((analysis_day - df["first_order_date"]).astype("timedelta64[D]"))/7
cltv["frequency"] = df["total_order"]
cltv["monetary_cltv_avg"] = df["total_order"] / df["total_purchese"]

cltv.head()

##############################################
## Görev 3: BG/NBD, Gamma-Gamma Modellerinin Kurulması ve CLTV’nin Hesaplanması
##############################################

### Adım 1: BG/NBD modelini fit ediniz.

bgf = BetaGeoFitter(penalizer_coef=0.001)
bgf.fit(cltv["frequency"], cltv["recency_cltv_weekly"], cltv["T_weekly"])

#### a) 3 ay içerisinde müşterilerden beklenen satın almaları tahmin ediniz ve exp_sales_3_month olarak cltv dataframe'ine ekleyiniz.

cltv["exp_sales_3_month"] = bgf.predict(12,
                                        cltv["frequency"],
                                        cltv["recency_cltv_weekly"],
                                        cltv["T_weekly"]).sort_values(ascending=False)

#### b) 6 ay içerisinde müşterilerden beklenen satın almaları tahmin ediniz ve exp_sales_3_month olarak cltv dataframe'ine ekleyiniz.

cltv["exp_sales_6_month"] = bgf.predict(24,
                                        cltv["frequency"],
                                        cltv["recency_cltv_weekly"],
                                        cltv["T_weekly"]).sort_values(ascending=False)

### Adım 2: Gamma-Gamma modelini fit ediniz. Müşterilerin ortalama bırakacakları değeri tahminleyip exp_average_value olarak cltv
# dataframe'ine ekleyiniz.

ggf = GammaGammaFitter(penalizer_coef=0.01)
ggf.fit(cltv["frequency"], cltv["monetary_cltv_avg"])


cltv["exp_average_value"] = ggf.conditional_expected_average_profit(cltv["frequency"],
                                                                    cltv["monetary_cltv_avg"]).sort_values(ascending=False)


### Adım 3: 6 aylık CLTV hesaplayınız ve cltv ismiyle dataframe'e ekleyiniz.

cltv["cltv"] = ggf.customer_lifetime_value(bgf,
                            cltv["frequency"],
                            cltv["recency_cltv_weekly"],
                            cltv["T_weekly"],
                            cltv["monetary_cltv_avg"],
                            time=6,
                            freq="W",
                            discount_rate=0.01)

cltv["cltv"].sort_values(ascending=False).head(20)

##############################################
## Görev 4: CLTV Değerine Göre Segmentlerin Oluşturulması.
##############################################

### Adım 1: 6 aylık CLTV'ye göre tüm müşterilerinizi 4 gruba (segmente) ayırınız ve grup isimlerini veri setine ekleyiniz.
cltv["segment"] = pd.qcut(cltv["cltv"], 4, labels=["D", "C", "B", "A"])

