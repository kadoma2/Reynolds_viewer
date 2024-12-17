import streamlit as st
import numpy as np
import plotly.graph_objects as go
import math

# 関数定義: レイノルズ数の計算
def reynolds(x, y, density, viscosity):
    return (4 * density * x) / (60 * viscosity * math.pi * y)

# Z範囲でマスクする関数
def mask_z_values(Z, z_min, z_max):
    Z_masked = np.where((Z < z_min) | (Z > z_max), np.nan, Z)  # 範囲外はNaNに置き換え
    return Z_masked

# Streamlitアプリ
def main():
    st.title("Reynolds Number Visualization")
    st.write("### Enter Parameters to Generate the 3D and XZ Plane Graphs")

    # 入力パラメータ（サイドバー）
    st.sidebar.header("Input Parameters")
    viscosity = st.sidebar.number_input("Viscosity (Pa·s):", min_value=0.0, value=0.001016, format="%.6f")
    density = st.sidebar.number_input("Density (kg/m³):", min_value=0.0, value=999.974, format="%.3f")
    
    x_min, x_max = st.sidebar.slider("X-axis Range (Flow rate, mL/min):", 1, 100, (1, 20))
    y_min, y_max = st.sidebar.slider("Y-axis Range (Nozzle diameter, µm):", 1, 500, (1, 250))
    z_min, z_max = st.sidebar.slider("Z-axis Range:", 1, 10000, (1, 5000))
    
    y_value = st.sidebar.number_input("Y-coordinate for XZ Plane (µm):", min_value=1, max_value=500, value=250)

    # 3Dグラフ生成
    x = np.linspace(x_min, x_max, 100)
    y = np.linspace(y_min, y_max, 100)
    X, Y = np.meshgrid(x, y)
    Z = reynolds(X, Y, density, viscosity)

    # Z軸の範囲でマスク
    Z_masked = mask_z_values(Z, z_min, z_max)

    # 乱流・層流境界面の追加 (z = 2000)
    Z_boundary = np.full_like(X, 2000)  # z=2000の平面データ

    # Plotlyで3Dサーフェスグラフ描画
    st.write("### 3D Surface Plot")
    fig_3d = go.Figure()

    # レイノルズ数の3Dサーフェス
    fig_3d.add_trace(go.Surface(
        z=Z_masked, x=X, y=Y, 
        colorscale='viridis', 
        showscale=True, 
        name="Reynolds Number"
    ))

    # z=2000の平面を半透明で追加
    fig_3d.add_trace(go.Surface(
        z=Z_boundary, x=X, y=Y, 
        colorscale=[[0, 'rgba(255, 0, 0, 0.3)'], [1, 'rgba(255, 0, 0, 0.3)']],  # 赤色, 半透明
        showscale=False,  # カラーバーを非表示
        name="Transition Boundary (z=2000)"
    ))

    # レイアウトの設定
    fig_3d.update_layout(
        width=900,  # グラフの横幅
        height=700,  # グラフの高さ
        scene=dict(
            xaxis_title="Flow rate (mL/min)",
            yaxis_title="Nozzle diameter (µm)",
            zaxis_title="Reynolds number (-)",
            xaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
            yaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
            zaxis=dict(title_font=dict(size=18), tickfont=dict(size=14), range=[z_min, z_max])
        ),
        title=dict(text="Red surface is the boundary between laminar and turbulent flow (Re = 2000)", font=dict(size=20)),
        margin=dict(l=50, r=50, t=50, b=50)  # マージン調整
    )
    st.plotly_chart(fig_3d)

    # xz平面グラフ生成
    st.write(f"### XZ Plane Plot at Y = {y_value} µm")
    Z_y_fixed = reynolds(x, y_value, density, viscosity)
    Z_y_fixed_masked = np.where((Z_y_fixed < z_min) | (Z_y_fixed > z_max), np.nan, Z_y_fixed)

    fig_xz = go.Figure()
    fig_xz.add_trace(go.Scatter(x=x, y=Z_y_fixed_masked, mode='lines', line=dict(color='blue')))
    fig_xz.update_layout(
        width=900,  # グラフの横幅
        height=500,  # グラフの高さ
        xaxis_title="Flow rate (mL/min)",
        yaxis_title="Reynolds number (-, log scale)",
        xaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        yaxis=dict(
            type="log", 
            title_font=dict(size=18), 
            tickfont=dict(size=14), 
            range=[np.log10(z_min), np.log10(z_max)]
        ),
        title=dict(text=f"XZ Plane at Nozzle Diameter = {y_value} µm", font=dict(size=20)),
        margin=dict(l=50, r=50, t=50, b=50)  # マージン調整
    )
    st.plotly_chart(fig_xz)

if __name__ == "__main__":
    main()
