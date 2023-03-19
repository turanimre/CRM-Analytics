import pandas as pd
import numpy as np

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


### Soru 1: Veri setinde
#### a) İlk 10 gözlem





