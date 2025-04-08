#%%
%pip install "numpy<2"
#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# CSV 로드 (이미 df에 로드되어 있다면 이 셀은 건너뛰셔도 됩니다)
csv_file = "data/output.csv"
df = pd.read_csv(csv_file, encoding='utf-8')

#%%
# 1) rcl_publisher_init에서 topic_name ↔ publisher_handle 매핑 테이블 생성
pattern_topic  = r'topic_name\s*=\s*(?:"([^"]+)"|(\S+))'
pattern_handle = r'publisher_handle\s*=\s*(\S+)'

df_init = df[df['Event type'].str.strip() == 'rcl_publisher_init'].copy()
ex_t = df_init['Contents'].str.extract(pattern_topic)
df_init['topic_name']       = ex_t[0].fillna(ex_t[1])
df_init['publisher_handle'] = df_init['Contents'].str.extract(pattern_handle)[0].str.rstrip(',')

mapping = (
    df_init
    .drop_duplicates('publisher_handle')
    .set_index('publisher_handle')['topic_name']
)

#%%
# 2) rcl_publish 이벤트 집계 및 topic_name 매핑
df_pub = df[df['Event type'].str.strip() == 'rcl_publish'].copy()
df_pub['publisher_handle'] = df_pub['Contents'].str.extract(pattern_handle)[0].str.rstrip(',')

handle_counts = (
    df_pub['publisher_handle']
    .value_counts()
    .rename_axis('publisher_handle')
    .reset_index(name='count')
)
handle_counts['topic_name'] = handle_counts['publisher_handle'].map(mapping)

print(handle_counts)



#%%
# 4) 히트맵: 1초 단위 퍼블리시 이벤트 분포
df_pub_time = df_pub.copy()
df_pub_time['Time'] = pd.to_datetime(df_pub_time['Timestamp'], format="%H:%M:%S.%f")
df_pub_time.set_index('Time', inplace=True)

counts = (
    df_pub_time
    .groupby('publisher_handle')
    .resample('1s')
    .size()
    .unstack(level=0)
    .fillna(0)
)
import pandas as pd
import plotly.express as px

# Assumes df_pub_time (with Time index and 'publisher_handle') and mapping dict already exist

# 1) Reset index → Time, publisher_handle 컬럼 확보
df_freq = (
    df_pub_time
    .reset_index()[['Time', 'publisher_handle']]
    .sort_values(['publisher_handle', 'Time'])
)

# 2) 그룹별 시간 차(diff) 계산 (초 단위) 후 주파수(Hz) 계산
df_freq['interval_sec'] = (
    df_freq
    .groupby('publisher_handle')['Time']
    .diff()
    .dt.total_seconds()
)
df_freq = df_freq.dropna(subset=['interval_sec']).copy()
df_freq['frequency_hz'] = 1.0 / df_freq['interval_sec']

# topic_name 컬럼 추가
df_freq['topic_name'] = df_freq['publisher_handle'].map(mapping)

# 3) Interactive line chart with Plotly
fig = px.line(
    df_freq,
    x='Time',
    y='frequency_hz',
    color='topic_name',
    hover_name='publisher_handle',
    title='Publisher Call Frequency Over Time'
)

# y축 0~2000Hz로 제한
fig.update_yaxes(range=[0, 2000], title_text='Frequency (Hz)')

# 레이아웃 영어 라벨
fig.update_layout(
    xaxis_title='Time',
    legend_title_text='Topic Name',
    margin=dict(l=40, r=40, t=60, b=40)
)

fig.show()

# %%
