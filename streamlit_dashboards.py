import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# Set page title and configuration
st.set_page_config(
    page_title="Superstore Sales Dashboard",
    layout="wide"
)

# Apply custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0277BD;
    }
    .card {
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.markdown("<h1 class='main-header'>Superstore Sales Analysis</h1>", unsafe_allow_html=True)
st.markdown("---")

# Load the dataset
@st.cache_data
def load_data():
    # Check for file in current directory or parent directory
    if os.path.exists('Sample - Superstore.csv'):
        file_path = 'Sample - Superstore.csv'
    elif os.path.exists('../Sample - Superstore.csv'):
        file_path = '../Sample - Superstore.csv'
    else:
        st.error("Dataset file 'Sample - Superstore.csv' not found in current or parent directory.")
        return pd.DataFrame()
        
    df = pd.read_csv(file_path, encoding='latin-1')
    # Convert date columns to datetime
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    # Calculate processing time in days
    df['Processing Time'] = (df['Ship Date'] - df['Order Date']).dt.days
    return df

# Load the data
df = load_data()

# Check if dataframe is empty
if df.empty:
    st.error("Failed to load the dataset. Please check that the CSV file exists.")
    st.stop()

# Sidebar filters
st.sidebar.markdown("<h2 class='sub-header'>Filters</h2>", unsafe_allow_html=True)

# Date range filter
min_date = df['Order Date'].min().date()
max_date = df['Order Date'].max().date()

start_date = st.sidebar.date_input(
    "Start Date",
    value=min_date,
    min_value=min_date,
    max_value=max_date
)
end_date = st.sidebar.date_input(
    "End Date",
    max_date,
    min_value=min_date,
    max_value=max_date
)

# Convert to datetime for filtering
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Category filter
categories = df['Category'].unique()
selected_categories = []
with st.sidebar.expander("Select Category"):
    container = st.container()
    for category in categories:
        if st.checkbox(category, value=True, key=category):
            selected_categories.append(category)

# Sub-Category filter
subcategories = df['Sub-Category'].unique()
selected_subcategories = []
with st.sidebar.expander("Select Subcategory"):
    container = st.container()
    for subcategory in subcategories:
        if st.checkbox(subcategory, value=True, key=subcategory):
            selected_subcategories.append(subcategory)

# Region filter
regions = df['Region'].unique()
selected_regions = []
with st.sidebar.expander("Select Region"):
    container = st.container()
    for region in regions:
        if st.checkbox(region, value=True, key=region):
            selected_regions.append(region)


# State filter
states = df['State'].unique()
selected_states = []
with st.sidebar.expander("Select State"):
    container = st.container()
    for state in states:
        if st.checkbox(state, value=True, key=state):
            selected_states.append(state)

# Ship Mode filter
ship_modes = df['Ship Mode'].unique()
selected_ship_modes = []
with st.sidebar.expander("Select Ship Mode"):
    container = st.container()
    for smode in ship_modes:
        if st.checkbox(smode, value=True, key=smode):
            selected_ship_modes.append(smode)

# Segment filter
segments = df['Segment'].unique()
selected_segments = []
with st.sidebar.expander("Select Customer Segment"):
    container = st.container()
    for segment in segments:
        if st.checkbox(segment, value=True, key=segment):
            selected_segments.append(segment)

# Apply filters
filtered_df = df[
    (df['Order Date'] >= start_date) & 
    (df['Order Date'] <= end_date) &
    (df['Category'].isin(selected_categories)) &
    (df['Region'].isin(selected_regions)) &
    (df['Ship Mode'].isin(selected_ship_modes)) &
    (df['State'].isin(selected_states)) &
    (df['Segment'].isin(selected_segments)) &
    (df['Sub-Category'].isin(selected_subcategories))
]

# Main dashboard area with tabs
tab1, tab2, tab3 = st.tabs(["Overview", "Sales Analysis", "Profit/Loss Analysis"])

with tab1:
    st.markdown("<h2 class='sub-header'>Key Metrics</h2>", unsafe_allow_html=True)
    
    # metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_sales = filtered_df['Sales'].sum()
        st.metric(
            label="Total Sales",
            value=f"${total_sales:,.0f}",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="Total Profit",
            value=f"${filtered_df['Profit'].sum():,.0f}"
        )
    
    with col3:
        st.metric(
            label="Average Profit Margin",
            value=f"{filtered_df['Profit'].sum() / filtered_df['Sales'].sum()*100:.1f}%"
        )
    
    with col4:
        total_losses = abs(filtered_df[filtered_df['Profit'] < 0]['Profit'].sum())
        st.metric(
            label="Total Losses",
            value=f"${total_losses:,.0f}"
        )
    
    with col5:
        st.metric(
            label="Total Orders",
            value=f"{filtered_df['Order ID'].nunique():,}"
        )
    
    # Monthly sales trend
    st.markdown("<h3>Monthly Sales Trend</h3>", unsafe_allow_html=True)
    monthly_sales = filtered_df.groupby(pd.Grouper(key='Order Date', freq='M')).agg({
        'Sales': 'sum',
        'Profit': 'sum'
    }).reset_index()
    
    fig_monthly = px.line(
        monthly_sales,
        x='Order Date',
        y=['Sales', 'Profit'],
        labels={'value': 'Amount', 'Order Date': 'Month', 'variable': ''},
        template='plotly_white'
    )

    # Make legend 
    fig_monthly.update_layout(
        legend=dict(
            font=dict(color="black"),
            bgcolor="white"
        )
    )

    # Make hover text black with white background
    fig_monthly.update_traces(
        hoverlabel=dict(
            font_color="black",
            bgcolor="white"
        )
    )

    st.plotly_chart(fig_monthly, use_container_width=True)
    


    # Sales by category and region
    col1, col2 = st.columns(2)
    
    with col1:
        category_sales = filtered_df.groupby('Category').agg({
            'Sales': 'sum',
            'Profit': 'sum'
            }).reset_index()

        # Calculate profit margin per category
        category_sales['Profit Margin'] = (category_sales['Profit'] / category_sales['Sales']) * 100

        # Sort the data first to ensure proper alignment
        category_sales_sorted = category_sales.sort_values(by='Sales', ascending=False)

        # Create the bar chart
        fig_category = px.bar(
            category_sales_sorted,
            x='Category',
            y='Sales',
            color='Profit',
            title='Sales and Profit by Category',
            labels={'Sales': 'Total Sales', 'Profit': 'Profit'},
            color_continuous_scale='Blues',
            template='plotly_white'
        )

        # Update the hover template to include profit and margin using sorted data
        fig_category.update_traces(
            customdata=category_sales_sorted[['Profit', 'Profit Margin']].values,
            hovertemplate='<b>%{x}</b><br>' +
                        'Total Sales: $%{y:,.2f}<br>' +
                        'Total Profit: $%{customdata[0]:,.2f}<br>' +
                        'Profit Margin: %{customdata[1]:.2f}%<extra></extra>',
            hoverlabel=dict(
                font_color="black",
                bgcolor="white"
            )
        )

        st.plotly_chart(fig_category, use_container_width=True)
    
    with col2:
        region_sales = filtered_df.groupby('Region').agg({
            'Sales': 'sum',
            'Profit': 'sum'
        }).reset_index()
        
        # Calculate profit margin per region
        region_sales['Profit Margin'] = (region_sales['Profit'] / region_sales['Sales']) * 100
        
        # Sort the data first to ensure proper alignment
        region_sales_sorted = region_sales.sort_values(by='Sales', ascending=False)
        
        fig_region = px.bar(
            region_sales_sorted,
            x='Region',
            y='Sales',
            color='Profit',
            title='Sales and Profit by Region',
            labels={'Sales': 'Total Sales', 'Profit': 'Profit'},
            color_continuous_scale='Blues',
            template='plotly_white'
        )

        # Update the hover template to include profit and margin using sorted data
        fig_region.update_traces(
            customdata=region_sales_sorted[['Profit', 'Profit Margin']].values,
            hovertemplate='<b>%{x}</b><br>' +
                        'Total Sales: $%{y:,.2f}<br>' +
                        'Total Profit: $%{customdata[0]:,.2f}<br>' +
                        'Profit Margin: %{customdata[1]:.2f}%<extra></extra>',
            hoverlabel=dict(
                font_color="black",
                bgcolor="white"
            )
        )
        st.plotly_chart(fig_region, use_container_width=True)
    # Processing Time Analysis
    st.markdown("<h3>Processing Time Analysis</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Total orders by ship mode with average processing time
        shipmode_orders = filtered_df.groupby('Ship Mode').agg({
            'Order ID': 'nunique',
            'Processing Time': 'mean'
        }).reset_index()
        shipmode_orders.rename(columns={'Order ID': 'Total Orders'}, inplace=True)
        
        # Sort the data first to ensure proper alignment
        shipmode_orders_sorted = shipmode_orders.sort_values(by='Total Orders', ascending=False)
        
        fig_processing_shipmode = px.bar(
            shipmode_orders_sorted,
            x='Ship Mode',
            y='Total Orders',
            title='Total Orders by Ship Mode',
            labels={'Total Orders': 'Number of Orders', 'Ship Mode': 'Shipping Method'},
            color='Processing Time',
            color_continuous_scale='Viridis',
            template='plotly_white'
        )
        
        # Add hover template for orders with processing time using sorted data
        fig_processing_shipmode.update_traces(
            customdata=shipmode_orders_sorted['Processing Time'].values,
            hovertemplate='<b>%{x}</b><br>' +
                         'Total Orders: %{y:,}<br>' +
                         'Avg Processing Time: %{customdata:.1f} days<extra></extra>',
            hoverlabel=dict(
                font_color="black",
                bgcolor="white"
            )
        )
        
        st.plotly_chart(fig_processing_shipmode, use_container_width=True)
    
    with col2:
        # Processing time distribution
        fig_processing_dist = px.histogram(
            filtered_df,
            x='Processing Time',
            nbins=20,
            title='Processing Time Distribution',
            labels={'Processing Time': 'Days', 'count': 'Number of Orders'},
            template='plotly_white'
        )
        
        # Add hover template for processing time distribution
        fig_processing_dist.update_traces(
            hovertemplate='Processing Time: %{x:.0f} days<br>' +
                         'Number of Orders: %{y}<extra></extra>',
            hoverlabel=dict(
                font_color="black",
                bgcolor="white"
            )
        )
        
        st.plotly_chart(fig_processing_dist, use_container_width=True)

with tab2:
    st.markdown("<h2 class='sub-header'>Sales Analysis</h2>", unsafe_allow_html=True)
    
    # Sales by Sub-Category
    subcategory_sales = filtered_df.groupby('Sub-Category').agg({
        'Sales': 'sum'
    }).sort_values('Sales', ascending=False).reset_index()
    
    fig_subcategory = px.bar(
        subcategory_sales,
        x='Sub-Category',
        y='Sales',
        title='Sales by Sub-Category',
        color='Sales',
        color_continuous_scale='Blues',
        template='plotly_white'
    )
    
    # Add hover template for subcategory sales
    fig_subcategory.update_traces(
        hovertemplate='<b>%{x}</b><br>' +
                     'Sales: $%{y:,.2f}<extra></extra>',
        hoverlabel=dict(
            font_color="black",
            bgcolor="white"
        )
    )
    
    st.plotly_chart(fig_subcategory, use_container_width=True)
    
    # Sales by Ship Mode and Segment
    col1, col2 = st.columns(2)
    
    with col1:
        shipmode_sales = filtered_df.groupby('Ship Mode').agg({
            'Sales': 'sum'
        }).reset_index()
        
        fig_shipmode = px.pie(
            shipmode_sales,
            values='Sales',
            names='Ship Mode',
            title='Sales by Ship Mode',
            template='plotly_white',
            hole=0.4
        )
        
        # Add hover template for shipmode pie chart
        fig_shipmode.update_traces(
            hovertemplate='<b>%{label}</b><br>' +
                         'Sales: $%{value:,.2f}<br>' +
                         'Percentage: %{percent}<extra></extra>',
            hoverlabel=dict(
                font_color="black",
                bgcolor="white"
            )
        )
        
        st.plotly_chart(fig_shipmode, use_container_width=True)
    
    with col2:
        segment_sales = filtered_df.groupby('Segment').agg({
            'Sales': 'sum'
        }).reset_index()
        
        fig_segment = px.pie(
            segment_sales,
            values='Sales',
            names='Segment',
            title='Sales by Customer Segment',
            template='plotly_white',
            hole=0.4
        )
        
        # Add hover template for segment pie chart
        fig_segment.update_traces(
            hovertemplate='<b>%{label}</b><br>' +
                         'Sales: $%{value:,.2f}<br>' +
                         'Percentage: %{percent}<extra></extra>',
            hoverlabel=dict(
                font_color="black",
                bgcolor="white"
            )
        )
        
        st.plotly_chart(fig_segment, use_container_width=True)
    
    # Top 10 customers by sales
    top_customers = filtered_df.groupby('Customer Name').agg({
        'Sales': 'sum',
        'Profit': 'sum'
    }).sort_values('Sales', ascending=False).head(10).reset_index()
    
    fig_customers = px.bar(
        top_customers,
        x='Customer Name',
        y='Sales',
        color='Profit',
        title='Top 10 Customers by Sales',
        color_continuous_scale='Blues',
        template='plotly_white'
    )
    
    # Add hover template for top customers
    fig_customers.update_traces(
        customdata=top_customers['Profit'].values,
        hovertemplate='<b>%{x}</b><br>' +
                     'Sales: $%{y:,.2f}<br>' +
                     'Profit: $%{customdata:,.2f}<extra></extra>',
        hoverlabel=dict(
            font_color="black",
            bgcolor="white"
        )
    )
    
    st.plotly_chart(fig_customers, use_container_width=True)
    
    # Top 5 States by Sales
    st.markdown("<h3>Top 5 States by Profit</h3>", unsafe_allow_html=True)
    
    state_metrics = filtered_df.groupby('State').agg({
        'Profit': 'sum',
        'Sales': 'sum'
    }).reset_index()
    
    state_metrics['Profit Margin'] = (state_metrics['Profit'] / state_metrics['Sales']) * 100
    # Get top 5 states by Sales
    top_5_states = state_metrics.nlargest(5, 'Sales')
    
    fig_top_states = px.bar(
        top_5_states,
        x='State',
        y='Sales',
        title='Top 5 States by Total Sales',
        labels={'Profit': 'Total Profit ($)', 'State': 'State'},
        color='Profit',
        color_continuous_scale='Blues',
        template='plotly_white'
    )
    
    # Update hover template to include profit margin
    fig_top_states.update_traces(
        customdata=top_5_states[['Profit', 'Profit Margin']].values,
        hovertemplate='<b>%{x}</b><br>' +
                        'Total Sales: $%{y:,.2f}<br>' +
                        'Total Profit: $%{customdata[0]:,.2f}<br>' +
                        'Profit Margin: %{customdata[1]:.2f}%<extra></extra>',
                        hoverlabel=dict(
                            font_color="black",
                            bgcolor="white"
                                    )
        )   
    
    st.plotly_chart(fig_top_states, use_container_width=True)

with tab3:
    st.markdown("<h2 class='sub-header'>Profit Analysis</h2>", unsafe_allow_html=True)
    
    # Profit by Category and Sub-Category
    cat_subcat_profit = filtered_df.groupby(['Category', 'Sub-Category']).agg({
        'Profit': 'sum'
    }).reset_index()
    
    # Sort by profit for better visualization
    cat_subcat_sorted = cat_subcat_profit.sort_values('Profit', ascending=True)
    
    # Create combined label for better readability
    cat_subcat_sorted['Category_SubCategory'] = cat_subcat_sorted['Category'] + ' - ' + cat_subcat_sorted['Sub-Category']
    
    fig_cat_subcat_bar = px.bar(
        cat_subcat_sorted,
        x='Profit',
        y='Category_SubCategory',
        orientation='h',
        title='Profit by Category and Sub-Category',
        labels={'Profit': 'Profit ($)', 'Category_SubCategory': 'Category - Sub-Category'},
        color='Profit',
        color_continuous_scale='RdBu',
        template='plotly_white'
    )
    
    fig_cat_subcat_bar.update_traces(
        hovertemplate='<b>%{y}</b><br>' +
                     'Profit: $%{x:,.2f}<extra></extra>',
        hoverlabel=dict(
            font_color="black",
            bgcolor="white"
        )
    )
    
    fig_cat_subcat_bar.update_layout(height=600)  # Make it taller for better readability
    st.plotly_chart(fig_cat_subcat_bar, use_container_width=True)
    
    # Profit vs Sales scatter plot by Sub-Category
    subcat_metrics = filtered_df.groupby('Sub-Category').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Quantity': 'sum'
    }).reset_index()
    
    fig_scatter = px.scatter(
        subcat_metrics,
        x='Sales',
        y='Profit',
        size='Quantity',
        color='Sub-Category',
        text='Sub-Category',
        title='Profit vs Sales by Sub-Category',
        labels={'Sales': 'Total Sales', 'Profit': 'Total Profit'},
        template='plotly_white'
    )
    fig_scatter.update_traces(textposition='top center')
    
    # Add hover template for scatter plot
    fig_scatter.update_traces(
        customdata=subcat_metrics['Quantity'].values,
        hovertemplate='<b>%{text}</b><br>' +
                     'Sales: $%{x:,.2f}<br>' +
                     'Profit: $%{y:,.2f}<br>' +
                     'Quantity: %{customdata:,}<extra></extra>',
        hoverlabel=dict(
            font_color="black",
            bgcolor="white"
        )
    )
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Discount vs Profit Analysis
    st.markdown("<h3>Discount Impact on Profit</h3>", unsafe_allow_html=True)
    
    discount_profit = filtered_df.groupby('Discount').agg({
        'Profit': 'mean',
        'Sales': 'mean'
    }).reset_index()
    
    fig_discount = px.bar(
        discount_profit,
        x='Discount',
        y='Profit',
        color='Sales',
        title='Average Profit by Discount Level',
        labels={'Discount': 'Discount Rate', 'Profit': 'Average Profit', 'Sales': 'Average Sales'},
        color_continuous_scale='Reds',
        template='plotly_white'
    )
    
    # Add hover template for discount analysis
    fig_discount.update_traces(
        customdata=discount_profit['Sales'].values,
        hovertemplate='<b>Discount: %{x:.1%}</b><br>' +
                     'Avg Profit: $%{y:,.2f}<br>' +
                     'Avg Sales: $%{customdata:,.2f}<extra></extra>',
        hoverlabel=dict(
            font_color="black",
            bgcolor="white"
        )
    )
    
    st.plotly_chart(fig_discount, use_container_width=True)
    
    # Loss Analysis
    st.markdown("<h3>Loss Analysis</h3>", unsafe_allow_html=True)
    
    # Filter for loss-making transactions (negative profit)
    loss_df = filtered_df[filtered_df['Profit'] < 0].copy()
    
    if not loss_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Losses by Category
            category_losses = loss_df.groupby('Category').agg({
                'Profit': 'sum'
            }).reset_index()
            category_losses['Losses'] = abs(category_losses['Profit'])  # Convert to positive for display
            category_losses = category_losses.sort_values('Losses', ascending=False)
            
            fig_category_losses = px.bar(
                category_losses,
                x='Category',
                y='Losses',
                title='Total Losses by Category',
                labels={'Losses': 'Total Losses ($)', 'Category': 'Product Category'},
                color='Losses',
                color_continuous_scale='Reds',
                template='plotly_white'
            )
            
            fig_category_losses.update_traces(
                hovertemplate='<b>%{x}</b><br>' +
                             'Total Losses: $%{y:,.2f}<extra></extra>',
                hoverlabel=dict(
                    font_color="black",
                    bgcolor="white"
                )
            )
            
            st.plotly_chart(fig_category_losses, use_container_width=True)
        
        with col2:
            # Top 5 States with highest losses
            state_losses = loss_df.groupby('State').agg({
                'Profit': 'sum'
            }).reset_index()
            state_losses['Losses'] = abs(state_losses['Profit'])  # Convert to positive for display
            top_5_loss_states = state_losses.nlargest(5, 'Losses')
            
            fig_state_losses = px.bar(
                top_5_loss_states,
                x='State',
                y='Losses',
                title='Top 5 States by Total Losses',
                labels={'Losses': 'Total Losses ($)', 'State': 'State'},
                color='Losses',
                color_continuous_scale='Reds',
                template='plotly_white'
            )
            
            fig_state_losses.update_traces(
                hovertemplate='<b>%{x}</b><br>' +
                             'Total Losses: $%{y:,.2f}<extra></extra>',
                hoverlabel=dict(
                    font_color="black",
                    bgcolor="white"
                )
            )
            
            st.plotly_chart(fig_state_losses, use_container_width=True)
    else:
        st.info("No loss-making transactions found in the filtered data.")



# Footer
st.markdown("---")
st.markdown("Dashboard created with Streamlit and Plotly") 