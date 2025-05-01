import streamlit as st
import pandas as pd
import altair as alt
import os


st.set_page_config(
    page_title="📈 Daily Stock Dashboard",
    layout="wide"
)


file_path = "daily_stocks_data.csv"
st.title("📊 Daily Stock Market Overview")

if os.path.exists(file_path):
    df = pd.read_csv(file_path)

       
    st.subheader("🔎 Search for a Specific Stock")

    col1, col2 = st.columns([1, 4])  # col1 narrower
    with col1:
        search_term = st.text_input("Enter SYMBOL or Company", label_visibility="visible").strip().lower()

    if search_term:
        results = df[df['SYMBOL'].str.lower().str.contains(search_term) | 
                 df['COMPANY_NAME'].str.lower().str.contains(search_term)]

        if not results.empty:
            st.success(f"Found {len(results)} match(es):")
            st.dataframe(results, use_container_width=True)
        else:
            st.warning("No matching stocks found.")

    st.subheader("Explore yesterday's stocks")

    
    col1, col2, col3 = st.columns([2, 2, 1.5])

    with col1:
        sort_column = st.selectbox("Sort by", ["OPEN_PRICE", "CLOSE_PRICE", "VOLUME", "PERCENT_CHANGE"])

    with col2:
        sort_order = st.radio("Order", ["Descending", "Ascending"], horizontal=True)

    with col3:
        min_pct, max_pct = float(df['PERCENT_CHANGE'].min()), float(df['PERCENT_CHANGE'].max())
        pct_range = st.slider("± % Change", min_value=min_pct, max_value=max_pct,
                            value=(min_pct, max_pct), step=0.1, label_visibility="collapsed")

 
    filtered_df = df[(df["PERCENT_CHANGE"] >= pct_range[0]) & (df["PERCENT_CHANGE"] <= pct_range[1])]
    filtered_df = filtered_df.sort_values(by=sort_column, ascending=(sort_order == "Ascending"))

    st.dataframe(filtered_df, use_container_width=True, height=400)



    st.markdown("---")

    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔝 Top 10 Stocks by Volume")
        top_volume = df.sort_values(by='VOLUME', ascending=False).head(10)

        # melt into long form, but carry along the other two metrics + company name for tooltip
        df_long = top_volume.reset_index().melt(
            id_vars=['SYMBOL', 'COMPANY_NAME', 'OPEN_PRICE', 'CLOSE_PRICE'],
            var_name='Metric',
            value_name='Value'
        )

        chart = (
            alt.Chart(df_long)
            .mark_bar()
            .encode(
                x=alt.X('SYMBOL:N', title='Symbol'),
                y=alt.Y('Value:Q', title='Value'),
                color=alt.Color('Metric:N', title='Metric'),
                tooltip=[
                    alt.Tooltip('SYMBOL:N', title='Symbol'),
                    alt.Tooltip('COMPANY_NAME:N', title='Company Name'),
                    alt.Tooltip('Metric:N', title='Metric'),
                    alt.Tooltip('Value:Q', title='Metric Value'),
                    alt.Tooltip('OPEN_PRICE:Q', title='Open Price'),
                    alt.Tooltip('CLOSE_PRICE:Q', title='Close Price'),
                ]
            )
            .properties(width=700, height=400)
        )

        st.altair_chart(chart, use_container_width=True)
    with col2:
        st.subheader("💹 Open vs Close Price – Top 10 Traded")
        top_price_change = df.sort_values(by='VOLUME', ascending=False).head(10)
        st.line_chart(top_price_change.set_index('SYMBOL')[['OPEN_PRICE', 'CLOSE_PRICE']])

    st.markdown("---")

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("📈 Top 5 Gainers")
        top_gainers = df.sort_values(by='PERCENT_CHANGE', ascending=False).head(5)
        gainers_chart = alt.Chart(top_gainers).mark_bar().encode(
            x=alt.X("PERCENT_CHANGE", title="Percent Change"),
            y=alt.Y("SYMBOL", sort='-x'),
            color=alt.Color("PERCENT_CHANGE", scale=alt.Scale(scheme='greens')),
            tooltip=['COMPANY_NAME', 'PERCENT_CHANGE']
        )
        st.altair_chart(gainers_chart, use_container_width=True)

    with col4:
        st.subheader("📉 Top 5 Losers")
        top_losers = df.sort_values(by='PERCENT_CHANGE').head(5)
        losers_chart = alt.Chart(top_losers).mark_bar().encode(
            x=alt.X("PERCENT_CHANGE", title="Percent Change"),
            y=alt.Y("SYMBOL", sort='x'),
            color=alt.Color("PERCENT_CHANGE", scale=alt.Scale(scheme='reds')),
            tooltip=['COMPANY_NAME', 'PERCENT_CHANGE']
        )
        st.altair_chart(losers_chart, use_container_width=True)

    st.markdown("---")

    col5, col6 = st.columns(2)

    with col5:
        st.subheader("📏 Price Range per Stock")
        price_range = df[(df['CLOSE_PRICE'] <= 1000) & (df['HIGH_PRICE'] <= 1000)].head(50).copy()
        price_range['PRICE_RANGE'] = price_range['HIGH_PRICE'] - price_range['LOW_PRICE']
        top_range = price_range.sort_values(by='PRICE_RANGE', ascending=False).head(10)

        range_chart = alt.Chart(top_range).mark_bar().encode(
            x=alt.X('SYMBOL', sort='-y'),
            y='PRICE_RANGE',
            tooltip=['COMPANY_NAME', 'HIGH_PRICE', 'LOW_PRICE', 'PRICE_RANGE']
        )
        st.altair_chart(range_chart, use_container_width=True)

    with col6:
        st.subheader("Close Price vs VWAP")
        
        # Filter out high-priced outliers
        vwap_df = df[(df['CLOSE_PRICE'] <= 1000) & (df['HIGH_PRICE'] <= 1000)].head(50).copy()
        
        vwap_df['DIFF'] = vwap_df['CLOSE_PRICE'] - vwap_df['VWAP']

        vwap_chart = alt.Chart(vwap_df).mark_bar().encode(
            x=alt.X("SYMBOL", sort='-y'),
            y='DIFF',
            color=alt.condition(
                alt.datum.DIFF > 0,
                alt.value("green"),
                alt.value("red")
            ),
            tooltip=['COMPANY_NAME', 'CLOSE_PRICE', 'VWAP', 'DIFF']
        )
        st.altair_chart(vwap_chart, use_container_width=True)


else:
    st.warning(f"`{file_path}` not found. Please make sure the pipeline has generated the file.")
