import streamlit as st
import pandas as pd
from itertools import combinations

# 初始化數據
if 'criteria' not in st.session_state:
    st.session_state.criteria = ["投入預算", "使用場景", "時間", "性能", "舒適度", "油耗", "零件妥善率", "二手折舊", "空間實用性", "社交形象"]
if 'weights' not in st.session_state:
    st.session_state.weights = [1] * len(st.session_state.criteria)
if 'cars' not in st.session_state:
    st.session_state.cars = {}

# 標題
st.title("加權平均決策矩陣 (WADM)")

# 新增需求
with st.sidebar:
    st.header("新增/刪除需求")
    new_criterion = st.text_input("輸入新需求名稱:")
    if st.button("新增需求"):
        if new_criterion:
            st.session_state.criteria.append(new_criterion)
            st.session_state.weights.append(1)
            st.success(f"已新增需求: {new_criterion}")
    
    # 刪除需求
    delete_criterion = st.selectbox("選擇要刪除的需求:", st.session_state.criteria)
    if st.button("刪除需求"):
        if delete_criterion:
            index = st.session_state.criteria.index(delete_criterion)
            st.session_state.criteria.pop(index)
            st.session_state.weights.pop(index)
            for car in st.session_state.cars:
                st.session_state.cars[car].pop(index)
            st.success(f"已刪除需求: {delete_criterion}")

# 新增車型
with st.sidebar:
    st.header("新增車型")
    new_car = st.text_input("輸入新車型名稱:")
    if st.button("新增車型"):
        if new_car:
            st.session_state.cars[new_car] = [0] * len(st.session_state.criteria)
            st.success(f"已新增車型: {new_car}")

# 顯示表格
st.header("評分表格")
data = {"需求": st.session_state.criteria, "權重": st.session_state.weights}
for car, scores in st.session_state.cars.items():
    data[car] = scores

df = pd.DataFrame(data)
edited_df = st.data_editor(df, num_rows="dynamic")

# 更新數據
if st.button("更新數據"):
    st.session_state.criteria = edited_df["需求"].tolist()
    st.session_state.weights = edited_df["權重"].tolist()
    for car in st.session_state.cars:
        st.session_state.cars[car] = edited_df[car].tolist()
    st.success("數據已更新！")

# 計算加權總分
if st.button("計算加權總分"):
    weighted_scores = {}
    for car, scores in st.session_state.cars.items():
        total_score = sum([score * weight for score, weight in zip(scores, st.session_state.weights)])
        weighted_scores[car] = total_score
    
    st.header("加權總分")
    st.write(pd.DataFrame({"車型": weighted_scores.keys(), "加權總分": weighted_scores.values()}))

# 多車組合方案
if st.button("推薦多車組合方案"):
    budget = st.number_input("請輸入總預算:", min_value=0, value=1000)
    car_prices = {}
    for car in st.session_state.cars:
        price = st.number_input(f"輸入 {car} 的價格:", min_value=0, value=500)
        car_prices[car] = price
    
    # 找出所有可能的組合
    valid_combinations = []
    for r in range(1, len(st.session_state.cars) + 1):
        for combo in combinations(st.session_state.cars.keys(), r):
            total_price = sum([car_prices[car] for car in combo])
            if total_price <= budget:
                valid_combinations.append(combo)
    
    # 顯示推薦組合
    if valid_combinations:
        st.header("推薦的多車組合方案")
        for combo in valid_combinations:
            st.write(f"組合: {combo}, 總價格: {sum([car_prices[car] for car in combo])}")
    else:
        st.warning("沒有符合預算的組合方案。")

# 保存為CSV
if st.button("保存為CSV"):
    edited_df.to_csv("wadm_data.csv", index=False)
    st.success("數據已保存為 wadm_data.csv")

# 加載CSV
uploaded_file = st.file_uploader("上傳CSV文件", type=["csv"])
if uploaded_file:
    loaded_df = pd.read_csv(uploaded_file)
    st.session_state.criteria = loaded_df["需求"].tolist()
    st.session_state.weights = loaded_df["權重"].tolist()
    st.session_state.cars = {}
    for car in loaded_df.columns[2:]:
        st.session_state.cars[car] = loaded_df[car].tolist()
    st.success("數據已加載！")