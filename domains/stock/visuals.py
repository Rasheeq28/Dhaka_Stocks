
import streamlit as st
import plotly.graph_objects as go


def render_stock_daily_charts(df, ticker, bench_name):
    """Refreshed daily charts including the overlay candlestick."""
    render_candlestick_chart(df, ticker, bench_name)
    st.divider()

    # 1. Daily Return Comparison
    col1, col2 = st.columns(2)
    with col1:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df['date'], y=df['Daily Return'], name=ticker, line=dict(color='#636EFA')))
        fig1.add_trace(
            go.Scatter(x=df['date'], y=df['Bench Return'], name=bench_name, line=dict(color='#FECB52', dash='dot')))
        fig1.update_layout(title="Daily Return Comparison (%)", template="plotly_white", height=300,
                           hovermode="x unified")
        st.plotly_chart(fig1, use_container_width=True, key=f"ret_{ticker}_{bench_name}")

    with col2:
        # Participation Index Comparison
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df['date'], y=df['Participation Index'], name=ticker, fill='tozeroy',
                                  line=dict(color='#FFA15A')))
        fig2.add_trace(
            go.Scatter(x=df['date'], y=df['Bench Participation Index'], name=bench_name, line=dict(color='#B6E880')))
        fig2.add_hline(y=1.0, line_dash="dot", line_color="gray")
        fig2.update_layout(title="Participation Index (1.0 = Avg)", template="plotly_white", height=300,
                           hovermode="x unified")
        st.plotly_chart(fig2, use_container_width=True, key=f"part_{ticker}_{bench_name}")

    # 2. Volume & Liquidity
    col3, col4 = st.columns(2)
    with col3:
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=df['date'], y=df['Daily Traded Value'], name=ticker, marker_color='#00CC96'))
        # Note: We don't overlay Benchmark volume here as the scale difference (Stock vs Index) would break the chart.
        fig3.update_layout(title=f"{ticker} Value (Mn)", template="plotly_white", height=300)
        st.plotly_chart(fig3, use_container_width=True, key=f"val_{ticker}")

    with col4:
        fig4 = go.Figure(go.Scatter(x=df['date'], y=df['Liquidity Share'], line=dict(color='#EF553B')))
        fig4.update_layout(title="Liquidity Share (%)", template="plotly_white", height=300)
        st.plotly_chart(fig4, use_container_width=True, key=f"liq_{ticker}")

        # 3. Excess Return (BREAK OUT OF COLUMNS)
        st.write("---")  # Visual separator

        colors = ['#00CC96' if x >= 0 else '#EF553B' for x in df['Excess Return vs Market']]

        fig5 = go.Figure(go.Bar(
            x=df['date'],
            y=df['Excess Return vs Market'],
            marker_color=colors,
        ))

        fig5.update_layout(
            title={'text': f"Excess Return: {ticker} vs {bench_name} (%)", 'x': 0.5, 'xanchor': 'center'},
            template="plotly_dark",
            height=400,
            margin=dict(l=10, r=10, t=50, b=10),  # Tighten margins
            hovermode="x unified"
        )

        # This ensures the chart fills the entire screen width regardless of parent columns
        st.components.v1.html(fig5.to_html(include_plotlyjs='cdn'), height=450)

def render_comparison_cards(target, bench):
    """Side-by-side metric cards for Period Average."""
    c1, c2 = st.columns(2)

    for data, col in [(target, c1), (bench, c2)]:
        with col:
            st.subheader(f"Results: {data['Entity']}")
            with st.container(border=True):
                m1, m2, m3 = st.columns(3)
                m1.metric("Avg Return", f"{data['Avg Return']:.2f}%")
                m2.metric("Volatility", f"{data['Volatility']:.2f}%")
                m3.metric("Pos. Days", f"{data['Pos. Days']:.0f}%")

                m4, m5 = st.columns(2)
                m4.metric("ADTV", f"{data['ADTV']:.2f}M")
                # Total volume is a secondary metric here
                st.caption(f"Total Period Volume: {data.get('Total Volume', 0):,.0f}")


def render_candlestick_chart(df, ticker, bench_name):
    """Renders a candlestick chart with a benchmark trend line overlay."""
    fig = go.Figure()

    # 1. Primary Candlestick for Target Stock
    fig.add_trace(go.Candlestick(
        x=df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        increasing_line_color='#00CC96',  # Green
        decreasing_line_color='#EF553B',  # Red
        name=f"{ticker} (OHLC)"
    ))

    # 2. Overlay Trend Line for Benchmark/Peer
    # We only show this if the price is within a comparable range (e.g., not DSEX index points vs Stock price)
    # If comparing Peer vs Peer, this works perfectly.
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['Bench Price'],
        name=f"{bench_name} (Trend)",
        line=dict(color='#FECB52', width=2),  # Yellow/Gold trend line
        mode='lines'
    ))

    fig.update_layout(
        title=f"Price Action: {ticker} vs {bench_name}",
        template="plotly_white",
        height=500,
        xaxis_rangeslider_visible=False,
        yaxis_title="Price (BDT)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True, key=f"candle_{ticker}_{bench_name}")