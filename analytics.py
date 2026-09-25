import asyncio

import streamlit as st
import pandas as pd
from sqlalchemy import text

from app.db.database import new_session

st.set_page_config( page_title="Sales Dashboard", page_icon="🛒", layout="wide", )


async def load_sales_mart():
    query = text("""
        SELECT *
        FROM product_sales_mart
        ORDER BY revenue DESC;
    """)

    async with new_session() as session:
        result = await session.execute(query)
        rows = result.mappings().all()

    return pd.DataFrame(rows)


async def main():
    df = await load_sales_mart()

    st.title("🛒 Sales Dashboard") 
    st.caption("Аналитика продаж магазина")

    total_revenue = df["revenue"].sum() 
    total_units = df["units_sold"].sum() 
    total_products = len(df) 
    col1, col2, col3 = st.columns(3)

    with col1: st.metric( label="Выручка", value=f"{total_revenue:,.0f} ₽".replace(",", " "), )
    with col2: st.metric( label="Продано", value=f"{total_units}", )
    with col3: st.metric( label="Товаров", value=f"{total_products}", )
    st.divider()

    st.subheader("Выручка по товарам") 
    chart_data = ( df[["product_name", "revenue"]] .set_index("product_name") ) 
    st.bar_chart( chart_data, horizontal=True, ) 
    st.divider()

    st.subheader("Продажи по товарам")

    display_df = df[ [ "product_name", "price", "units_sold", "buyers_count", "revenue", ] ].copy()

    display_df.columns = [ "Товар", "Цена", "Продано", "Покупателей", "Выручка", ]

    display_df["Цена"] = display_df["Цена"].map( lambda value: f"{value:,.0f} ₽".replace(",", " ") )

    display_df["Выручка"] = display_df["Выручка"].map( lambda value: f"{value:,.0f} ₽".replace(",", " ") )

    st.dataframe( display_df, use_container_width=True, hide_index=True, )
    

if __name__ == "__main__":
    asyncio.run(main())