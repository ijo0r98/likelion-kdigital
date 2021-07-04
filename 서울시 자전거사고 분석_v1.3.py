#!/usr/bin/env python
# coding: utf-8

# # 서울시에서 자전거타기에 가장 위험한 곳은?

# 라이브러리

# In[3]:


import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import folium
import json
import requests
from bs4 import BeautifulSoup # HTTP Response -> HTML
from matplotlib import font_manager, rc # rc == run configure(configuration file)

get_ipython().run_line_magic('matplotlib', 'inline')
font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name() # 여백 X 한글 X
rc('font', family=font_name) # run configure


# ---
# 
# ## ○ 서울시 구별 자전거 교통사고 현황

# 서울시 자전거 교통사고 통계 데이터

# In[4]:


# 서울 열린데이터광장 - 서울시 자전거 교통사고 통계
df_bic_acc = pd.read_excel('data/자전거교통사고현황.xlsx', encoding='utf-8', index_col='지역')

# 전처리
df_bic_acc.replace('-', 0, inplace=True) # '-' 0으로 치환
df_bic_acc.drop('합계', inplace=True) # 시각화를 위헤 합계 행 제거

# 합계 열 추가
df_bic_acc['합계']=df_bic_acc['피해자사고 발생건수'] + df_bic_acc['가해자사고 발생건수']

df_bic_acc.head()


# 피해자사고 발생건수와 가해자사고 발생건수 시각화

# In[5]:


df_bic_acc_plt = df_bic_acc[['피해자사고 발생건수', '가해자사고 발생건수']]
df_bic_acc_plt.plot(kind='bar', figsize=(20, 15), fontsize=15, colormap='bwr').legend(fontsize = 20)


# <span style="color:blue;">
# 피해자사고 발생건수가 가장 많은 곳 : <b>송파구</b><br> 가해자사고 발생건수가 가장 많은 곳 : <b> 영등포구</b>
# </span>

# ++ 추가) 사고 발생건수 시각화 (stacked=True)

# In[6]:


df_bic_acc_plt.plot(kind="bar", stacked=True, figsize=(20, 15), fontsize=15, colormap='bwr')


# <span style="color:blue;">
# 피해자사고 발생건수가 가장 많은 곳 : <b>송파구</b><br> 가해자사고 발생건수가 가장 많은 곳 : <b> 영등포구</b>
# </span>

# <br>
# 
# #### [인구수 대비] 사고 발생건수

# In[7]:


# 구별 인구수 데이터
popul_df = pd.read_csv('data/pop_kor.csv', encoding='UTF-8', index_col='구별')
popul_df.head()


# In[8]:


df_bic_acc_plt.head()


# In[9]:


# 인구수 열 추가
df_bic_acc_plt_ratio = df_bic_acc_plt.join(popul_df)
df_bic_acc_plt_ratio.head()


# In[10]:


# 최대값으로 나눔
weight_col = df_bic_acc_plt_ratio.max()
df_bic_acc_norm = df_bic_acc_plt_ratio / weight_col

# 인구 수 대비 비율 계산
df_bic_acc_norm = df_bic_acc_norm.div(df_bic_acc_norm['인구수'] , axis=0 ) * 100000 

# 피해자사고 + 가해자사고 합계 열 추가
df_bic_acc_norm['합계'] = df_bic_acc_norm['피해자사고 발생건수'] + df_bic_acc_norm['가해자사고 발생건수']
df_bic_acc_norm.sort_values(by='합계', ascending=False).head()


# 인구 수 대비 자전거 사고 발생건수(합계) 시각화

# In[11]:


df_bic_acc_norm['합계'].plot(kind='bar', figsize=(15, 10), fontsize=13, color='limegreen').legend(fontsize = 15)


# <span style="color:blue;">
#     인구 수 대비 자전서 사고 발생건수가 가장 많은 곳은 <b>영등포구</b>와 <b>송파구</b>
# </span>

# 인구 수 대비 자전거 사고 발생 건수 지도 시각화

# In[19]:


geo_path = 'data/skorea_municipalities_geo_simple.json'
geo_str = json.load(open(geo_path, 'r', encoding = 'utf-8'))

map_acc = folium.Map(location=[37.5502, 126.982], zoom_start=11, tiles='Stamen Toner')

map_acc.choropleth(geo_data = geo_str,               
               data = df_bic_acc_norm['합계'],
               columns = [df_bic_acc_norm.index, df_bic_acc_norm['합계']],
               fill_color = 'BuGn', 
               key_on = 'feature.id')
map_acc


# 구 이름과 인구 수 정보 팝업 추가

# In[20]:


gu_geo = pd.read_excel('data/구별위도경도.xlsx', encoding='UTF-8')
gu_geo.head()


# In[21]:


import folium
from folium.features import DivIcon

lat = ""
lng = ""

for i in range(25):
    #tmpMap = gmaps.geocode(name)
    #tmpLoc = tmpMap[0].get('geometry')
    name = gu_geo['구별'][i]
    lat = gu_geo['lat'][i]
    lng = gu_geo['lng'][i]
    text = name
    # 구별 텍스트 마커추가
    folium.map.Marker(
        [lat, lng],
        icon=DivIcon(
            icon_size=(100,50),
            icon_anchor=(15,0),
            html='<div style="font-size: 10pt">%s</div>' %text,
            )
        ).add_to(map_acc)
    
    folium.Marker([lat, lng],
              popup='인구수: '+str(popul_df['인구수'][i])+'명',
              icon=folium.Icon(color='red', icon='glyphicon-user')    
              ).add_to(map_acc)

map_acc


# ---

# <br>
# 
# ## ○ 사고 다발 지역의 원인 예측

# ### 0. 구별 공공자전거 이용정보

# In[11]:


bicycle_using_df = pd.read_excel('data/공공자전거 대여소별 이용정보_202006.csv', encoding='utf-8')

bicycle_using_df = bicycle_using_df.drop(['대여소 명', '대여 일자 / 월'], axis =1)
bicycle_using_df.rename(columns = {'대여소 그룹':'지역'}, inplace = True)
bicycle_using_df = bicycle_using_df.groupby(bicycle_using_df['지역']).sum()

bicycle_using_df.sort_values(by='대여 건수', ascending=False).head()


# <span style='color:blue;'>
#     강서구, 영등포구, 송파구의 공공자전거 이용률이 가장 높음
#     (인구 수 고려 x)
# </span>

# ### 1. 사고다발지역의 특징

# 서울시 자전거도로 현황 데이터

# In[12]:


geo_path = 'data/서울시자전거도로.geojson'
df_bic_road_geo = json.load(open(geo_path, encoding = 'utf-8'))


# 지도 시각화

# In[11]:


map_bic_road = folium.Map(location=[37.5502, 126.982], zoom_start=11)

map_bic_road.choropleth(geo_data = df_bic_road_geo,
               line_color = 'black',
               line_weight=1.5,
               line_opacity=0.5,
               key_on = 'feature.id') 
map_bic_road


# 공공 데이터포털 - 자전거사고 다발지역 open API

# In[13]:


# 서울시 전체 구,군 코드
guGun_list2 = {
    '강남구': '680',
    '강동구': '740',
    '강북구': '305',
    '강서구': '500',
    '관악구': '620',
    '광진구': '215',
    '구로구': '530',
    '금천구': '545',
    '노원구': '350',
    '도봉구': '320',
    '동대문구': '230',
    '동작구': '590',
    '마포구': '440',
    '서대문구': '410',
    '서초구': '650',
    '성동구': '200',
    '성북구': '290',
    '송파구': '710',
    '양천구': '470',
    '영등포구': '560',
    '용산구': '170',
    '은평구': '380',
    '종로구': '110',
    '중구': '140',
    '중랑구': '260'
}

# query param
service_key = '%2BAWnyLrxdxmjreCkVW86y7jmJw2Jzk%2BYQEqCJk8Cv3hTgcYeCfjXSz48r%2BRd6%2F0%2BHTaVN88iJgKhQthIUyxgeA%3D%3D'
base_url = 'http://apis.data.go.kr/B552061/frequentzoneBicycle/getRestFrequentzoneBicycle'
searchYearCd = '2015'
siDo = '11'
type = 'xml'
numOfRows = '100'
pageNo = '1'

# list
gu_nm = []
spot_nm = []
lat = []
lnd = []
    
for key, guGun in guGun_list2.items():
    request_url = base_url + '?' + "serviceKey=" + service_key + '&searchYearCd=' + searchYearCd + '&siDo=' + siDo + '&guGun=' + guGun+ '&type=' + type + '&numOfRows=' + numOfRows + '&pageNo=' + pageNo
    
    try:
        response = requests.get(request_url)
        soup = BeautifulSoup(response.text, 'lxml-xml')

        for value in soup.find('body').find_all('lo_crd'):
            gu_nm.append(key)
            lnd.append(value.get_text())
        for value in soup.find('body').find_all('la_crd'):
            lat.append(value.get_text())
        for item in soup.find('body').find_all('item'):
        #     print(item.find('spot_nm'))
            spot_nm.append(item.find('spot_nm').get_text())
    except:
        pass

# dataframe
df_acc_prone = pd.DataFrame({'구별': gu_nm, '장소명': spot_nm, 'lat': lat, 'lnd': lnd})
df_acc_prone.head()


# 사고다발지역 지도 위 시각화

# In[189]:


for n in df_acc_prone.index:
    folium.Circle(location=[float(df_acc_prone.lat[n]), float(df_acc_prone.lnd[n])], popup=df_acc_prone['장소명'][n], color='red').add_to(map_bic_road)
    
map_bic_road


# ++ 추가) 지도 위 사고다발지역 클러스터링

# In[193]:


from folium.plugins import MarkerCluster
import folium.plugins

legend_html = """
<div style="position:fixed;
     color : black;
     bottom: 50px; 
     left: 50px; 
     width: 140px; 
     height: 90px; 
     border:2px solid grey; 
     z-index: 9999;
     font-size:14px;">
     &nbsp;<b>Positive Cases:</b><br>
     &nbsp;<i class="fa fa-circle fa-1x" style="color:#298A08"></i>&nbsp;자전거도로구간<br><br>
     &nbsp;<i class="fa fa-circle fa-1x" style="color:red"></i>&nbsp;사고다발구간
</div>
"""

map.get_root().html.add_child(folium.Element(legend_html))

marker_cluster = MarkerCluster().add_to(map_bic_road)
for n in df_acc_prone.index:
    folium.Circle(location=[float(df_acc_prone.lat[n]), float(df_acc_prone.lnd[n])], 
                  popup=df_acc_prone['장소명'][n], 
                  color='red').add_to(marker_cluster)
        
folium.LayerControl(collapsed=False)        
map_bic_road


# <span style="color:blue">
#     대부분의 경우 자전거 도로 위에서 사고 발생
# </span>

# <br>
# 
# ### 2. 자전거도로 수와 비율

# #### 1) 자전거도로 수

# In[25]:


# 데이터 읽기
df_bic_road_csv = pd.read_excel('data/서울시_자전거도로현황.xlsx', encoding='utf-8')
df_bic_road_csv.head()


# In[26]:


# 데이터 전처리

# 필요없는 열 삭제
del df_bic_road_csv['기간']
del df_bic_road_csv['자치구']

# 필요없는 행 삭제
df_bic_road_csv.dropna(axis=0, inplace=True)
df_bic_road_csv.drop([2, 28, 29, 30, 31], inplace=True)

# 빈 데이터 0 치환
df_bic_road_csv.replace('-', 0, inplace=True)

# 기존 컬럼명 리스트
column_list = list(df_bic_road_csv.columns)

# 새 컬럼명 리스트
new_column_list = []
for index, value in enumerate(column_list):
    if value.startswith('Unnamed'):
        new_column_list.insert(index, column_list[index - 1] + ' 길이')
        new_column_list.insert(index - 1, column_list[index - 1] + ' 구간')
    elif value == '자치구(2)':
        new_column_list.insert(index, '구별')
        
# 컬럼명 변경에 쓰일 dict
column_dict = dict(zip(column_list,new_column_list))

# 컬럼명 변경
df_bic_road_csv.rename(columns=column_dict, inplace=True)

# 인덱스 변경
df_bic_road_csv.set_index('구별', inplace=True)

df_bic_road_csv.head()


# In[27]:


geo_path = 'data/skorea_municipalities_geo_simple.json'
geo_str = json.load(open(geo_path, 'r', encoding = 'utf-8'))

map_road_cnt = folium.Map(location=[37.5502, 126.982], zoom_start=11, tiles='Stamen Toner')

map_road_cnt.choropleth(geo_data = geo_str,               
               data = df_bic_road_csv['합계 구간'],
               columns = [df_bic_road_csv.index, df_bic_road_csv['합계 구간']],
               fill_color = 'BuGn', 
               key_on = 'feature.id')
map_road_cnt


# In[28]:


df_bic_road_csv.sort_values(by='합계 구간', ascending=False).head(3)


# <span style="color:blue;">
# 송파구와 영등포구, 강서구에 자전거도로가 가장 많음을 알 수 있음
# </span>

# <br>
# 
# ++ 추가)
# 자전거 도로 종류별 수 (stacked)

# In[29]:


road_list = ['자전거전용도로 구간', '자전거보행자겸용도로 구간', '자전거전용차로 구간', '자전거우선도로 구간']

df_bic_road_csv[road_list].plot(kind="bar", stacked=True, figsize=(20, 15), fontsize=15, colormap='Set3').legend(fontsize = 20)


# In[78]:


df_bic_road_csv.sum(axis=0).values


# In[80]:


df_bic_road_csv.loc['합계'] = (df_bic_road_csv.sum(axis=0).values)


# In[81]:


df_bic_road_csv.tail()


# In[84]:


df_bic_road_csv.loc['합계', road_list].plot(kind='pie', figsize=(15, 10), fontsize=13, colormap='Set3',  autopct='%.1f%%')


# 
# <br>
# 
# ### 3. 자전거도로의 종류

# #### 송파구와 영등포구의 자전거도로 현황

# In[29]:


road_list


# In[30]:


df_bic_road_csv.loc[['종로구', '영등포구'], road_list]


# 종로구

# In[31]:


df_bic_road_csv.loc['종로구', road_list].plot(kind='pie', autopct='%.1f%%',figsize=(15, 10), fontsize=13, colormap='Set3')


# 영등포구

# In[32]:


df_bic_road_csv.loc['영등포구', road_list].plot(kind='pie', autopct='%.1f%%',figsize=(15, 10), fontsize=13, colormap='Set3')


# 자전거 우선도로, 자전거 전용차로, 자전거 보행자 겸용도로란?

# In[33]:


pd.set_option('display.max.colwidth', 100) #셀 최대 넓이 지정


# In[34]:


# 도로교통공단 이륜차 안전운전 스크랩핑
url = 'https://www.koroad.or.kr/kp_web/knTwoWheel3-03.do'

response = requests.get(url).content
source = BeautifulSoup(response, 'html.parser')

road_nm = []
for item in source.find_all('h4')[-5:]:
#     print(item.get_text())
    road_nm.append(item.get_text())
    
road_info = []
for index, item in enumerate(source.find_all('ul', {'class': 'list2'})):
#     print((item.find('li').get_text()).strip())
    road_info.append((item.find('li').get_text()).strip())
    
df_road_info = pd.DataFrame({'도로 종류': road_nm, '설명': road_info})
df_road_info


# <span style="color:blue">
# 
# 두 지역 모두 자동차와 함께 통행하는 자전거 우선도로, 전용차로의 비율이 가장 높음
# 
# 
# </span>

# ++ 추가, 수정)

# <span style='color:green;'>
# <b> [자전거 교통사고 발생이 높은 곳의 특징] </b>
# 
# - 자전거 도로가 많다.
# 
# - 자전거 이용률(공공자전거 기준)이 높다.
# 
# - 자전거 우선도로와 전용차로의 비율이 높고 자전거 전용도로의 비율이 적다.
# 
# <br>
# 
# <b>[자전거 교통사고에 영향을 주는 요인 예측]</b>
# 
# - 자전거 이용률(공공자전거)과 자전거 사고 발생률 사이 연관관계가 있을 것이다.
# 
# - 자전거 우선도로와 자전거 전용차로가 사고 발생에 가장 큰 영향을 줄 것이다.
#     <br> -> 자전거 도로 수와 이용률에 비해 자전거 전용도로의 비율이 적어 안전한 자전거 도로상황이라 할 수 없을 것
# 
# <br>
# 
# ---
# 

# <br>
# 
# ## ○ 자전거 교통사고 연관관계 분석

# 자전거 교통사고 발생건수와 여러 요인사이 상관관계 분석

# In[35]:


from scipy import stats


# In[36]:


# 인구수 열 추가
df_bic_acc_corr = df_bic_road_csv[['합계 구간', '인구수']].join(bicycle_using_df)
# 사고 합계 열 추가
df_bic_acc_corr = df_bic_acc_corr.join(df_bic_acc['합계'])
# 이름 변경
df_bic_acc_corr.rename(columns={'합계': '사고 합계'}, inplace=True)
df_bic_acc_corr.rename(columns={'인구수': '인구 수'}, inplace=True)
df_bic_acc_corr.rename(columns={'합계 구간': '도로 수'}, inplace=True)
df_bic_acc_corr.rename(columns={'사고 합계': '사고 수'}, inplace=True)

df_bic_acc_corr.head()


# 상관관계

# In[37]:


df_bic_acc_corr.corr()


# <br>
# 
# #### 자전거 교통사고 발생건수와 여러 요인사이 관계가 있는지 분석 (p-value 기준 0.05)

# ### 1. 인구 수

# In[38]:


result = stats.pearsonr(df_bic_acc_corr['사고 수'], df_bic_acc_corr['인구 수'])

print('피어슨 상관계수: ', result[0])
print('p-value: ', result[1])


# p-value가 0.0019로 구별 자전거 교통사고 수와 인구수가 통계적으로 유의미한 상관관계가 없다는 전제 하에 이러한 측정 결과가 나올 확률이 0.19%라고 할 수 있음 (귀무가설 기각)
# 
# <span style='color:blue;'> 구별 인구 수와 자전거 교통사고 수 사이에는 통계적으로 유의미한 상관관계(0.58)가 있다.</span>

# <br>
# 
# ### 2. 자전거 이용(공공자전거 기준 대여 건수)

# In[39]:


result = stats.pearsonr(df_bic_acc_corr['사고 수'], df_bic_acc_corr['대여 건수'])

print('피어슨 상관계수: ', result[0])
print('p-value: ', result[1])


# p-value가 0.05 미만으로 구별 자전거 교통사고 수와 자전거 대여 건수가 통계적으로 유의미한 상관관계가 없다는 전제 하에 이러한 측정 결과가 5% 미만이라고 할 수 있음 (귀무가설 기각)

# <span style='color:blue;'>구별 공공자전거 대여 건수와 자전거 교통사고 수 사이에는 통계적으로 유의미한 상관관계(0.7)가 있다. </span>

# <br>
# 
# ### 3. 자전거 도로 수

# In[40]:


result = stats.pearsonr(df_bic_acc_corr['사고 수'], df_bic_acc_corr['도로 수'])

print('피어슨 상관계수: ', result[0])
print('p-value: ', result[1])


# p-value가 0.05 미만으로 구별 자전거 교통사고 수와 자전거 도로 수가 통계적으로 유의미한 상관관계가 없다는 전제 하에 이러한 측정 결과가 5% 미만이라고 할 수 있음 (귀무가설 기각)

# <span style='color:blue;'>구별 자전거 도로 수와 자전거 교통사고 수 사이에는 통계적으로 유의미한 상관관계(0.75)가 있다.</span>

# #### 자전거 도로 종류별 상관계수 

# In[41]:


df_bic_acc_corr.sort_values(by='사고 수', ascending=False).head()


# In[42]:


df_bic_road_csv[road_list].head()


# In[43]:


df_road_corr = df_bic_acc_corr.join(df_bic_road_csv[road_list])
df_road_corr.head()


# In[44]:


# 각 도로 종류별 상관계수, p-value 계산

nm_list = ['자전거보행자겸용도로', '자전거우선도로', '자전거전용도로', '자전거전용차로']
corr_list = []
p_value_list = []
for item in nm_list:
    result_all = stats.pearsonr(df_road_corr[item + ' 구간'], df_road_corr['사고 수'])
    print('{}: {} / {}'.format(item, result_all[0], result_all[1]))
    corr_list.append(result_all[0]) # 상관계수
    p_value_list.append(result_all[1]) # p-value


# In[45]:


df_corr = pd.DataFrame({'도로 종류': nm_list, '상관계수': corr_list, 'p-value': p_value_list})
df_corr.sort_values(by='상관계수', ascending=False, inplace=True)
df_corr


# <span style='color:blue;'><b> 각 종류별 도로 수와 자전거 교통사고 수 사이 연관관계</span></b>
#     
# #### 자전거보행자겸용도로, 자전거전용도로
# 
# p-value가 0.05 미만임으로 자전거보행자겸용도로, 자전거전용도로 수와 자전거 사고 수 사이 서로 연관관계 존재
# 
# 
# #### 자전거전용차로, 자전거우선도로
# 
# p-value가 0.05 넘음으로 자전거전용차로, 자전거우선도로 수와 자전거 사고 수 사이 연관관계 없다고 할 수 있음
# 
# </br>

# In[46]:


df_corr_pie = df_corr.set_index('도로 종류')
ax1 = df_corr_pie['상관계수'].plot(kind='bar', figsize=(15, 10), fontsize=10, color='palevioletred')
ax1


# ++ 추가) p-value 꺾은선 추가

# In[47]:


# 데이터 준비
x = df_corr['도로 종류']
y1 = df_corr['상관계수']
y2 = df_corr['p-value']

# 기본 설정
plt.rcParams['figure.figsize'] = (15,10)
plt.rcParams['font.size'] = 12

# 그래프
fig, ax1 = plt.subplots()

# 막대그래프 - 상관계수
ax1.bar(x, y1, color='deeppink', label='상관계수', alpha=0.7, width=0.7)
# ax1.plot(x, y1, '-s', color='green', markersize=7, linewidth=5, alpha=0.7, label='상관계수')
ax1.set_xlabel('자전거 도로 종류')
ax1.set_ylabel('상관계수')
ax1.tick_params(axis='both', direction='in')

# 꺾은선그래프 - p-value
ax2 = ax1.twinx()
ax2.plot(x, y2, '-s', color='green', markersize=7, linewidth=5, alpha=0.7, label='p-value')
# ax1.bar(x, y1, color='deeppink', label='', alpha=0.7, width=0.7)
ax2.set_ylabel('p-value')
ax2.tick_params(axis='y', direction='in')

ax1.legend(loc='upper left', fontsize=15)
ax2.legend(loc='upper right', fontsize=15)

# p-value 기준값
plt.axhline(0.05, color='gray', linestyle='--', linewidth='1', label='ddd')

plt.show()


# <br>
# 
# <br>
# 
# <span style="color:green">
# 
# <b>[분석 결과]</b>
# 
# - 인구수: 연관관계 있으나 그 영향이 높지 않음
# 
# - 공공자전거 대여 수(자전거 이용률): 연관관계 높음(70%)
# 
# - 자전거도로 수: 연관관계 높음(75%) <br> -> 자전거 보행자 겸용도로, 자전거 전용도로
# </span>

# <br>
# ++ 추가) 인구 수 / 대여 건수 / 자전거도로 수 / 사고 발생 수 scaling 후 비교

# In[48]:


def reRange(x, oldMin, oldMax, newMin, newMax):
    return (x - oldMin) * (newMax - newMin) / (oldMax - oldMin) + newMin

# 필요한 열 선택
df_heatmap = df_road_corr[['도로 수', '인구 수', '대여 건수', '사고 수']]

# 점수 열 추가
for col in df_heatmap.columns:
    new_col = col + ' 점수'
    df_heatmap[new_col] = reRange(df_heatmap[col], min(df_heatmap[col]), max(df_heatmap[col]), 1, 100)
    
df_heatmap.sort_values(by='사고 수 점수', ascending=False, inplace=True)
sns.heatmap(df_heatmap[['도로 수 점수', '인구 수 점수', '대여 건수 점수', '사고 수 점수']], cmap='PuRd', fmt='f', annot=True)
plt.title('각 요인별 점수 및 사고 발생 수 시각화')

