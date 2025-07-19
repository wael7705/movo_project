import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import time
from datetime import datetime


########################################################
# Data structures - to be populated from database
orders = []  # Will be populated from database
status_tabs = ["pending", "Captain", "Processing", "Delayed", "Out for Delivery", "Delivered", "Cancelled", "Issue Center"] 
processing_substages = ["waiting Approval", "Preparing", "Captain Received"]

# Location data - to be populated from database
DEFAULT_COORDS = (33.5138, 36.2765)  # Default Damascus center coordinates
restaurant_locations = {}  # Will be populated from database
customer_locations = {}    # Will be populated from database
captains = []              # Will be populated from database
########################################################
st.set_page_config(layout="wide")
st.title("Order Management Dashboard")

# Initialize session state for timers
if 'order_timers' not in st.session_state:
    st.session_state['order_timers'] = {}
if 'order_stage_start_times' not in st.session_state:
    st.session_state['order_stage_start_times'] = {}
if 'order_stage_durations' not in st.session_state:
    st.session_state['order_stage_durations'] = {}

tabs = st.tabs(status_tabs)

# Helper to manage which order's map is shown in the Captain tab
if 'delivery_map_order_id' not in st.session_state:
    st.session_state['delivery_map_order_id'] = None
if 'delivery_map_zoom' not in st.session_state:
    st.session_state['delivery_map_zoom'] = 13

def show_order_card(order, show_delivery_btn=False):
    # Get timer for current status
    order_id = order['id']
    current_status = order['status']
    
    timer_display = ""
    if order_id in st.session_state['order_timers'] and current_status in st.session_state['order_timers'][order_id]:
        elapsed_time = st.session_state['order_timers'][order_id][current_status]
        timer_display = f"⏱️ {format_time(elapsed_time)}"
    
    color = "#f0f0f0"
    if order["vip"]:
        color = "#fff0f5"
    label = "🟢 First Order" if order["first_order"] else ""
    button_html = "<button style='margin: 4px;'>Delivery</button>" if show_delivery_btn else "<button style='margin: 4px;'>Invoice</button>"
    st.markdown(f"""
        <div style='background-color: {color}; color: #222; padding: 16px; border-radius: 10px; margin-bottom: 16px; border: 2px solid #d3d3d3;'>
            <div style='margin-bottom: 6px;'><strong>Order ID:</strong> {order['id']} &nbsp; | &nbsp; <strong>Track ID:</strong> {order['track_id']}</div>
            <div style='margin-bottom: 6px;'><strong>Customer:</strong> {order['customer']} | {order['customer_phone']} </div>
            <div style='margin-bottom: 6px;'><strong>Restaurant:</strong> {order['restaurant']}</div>
            <div style='margin-bottom: 6px;'><strong>Delivery:</strong> {order['delivery']}</div>
            <div style='margin-bottom: 6px;'><strong>Payment:</strong> {order['payment']}</div>
            <div style='margin-bottom: 6px;'><strong>AI Status:</strong> {order['ai_status']}</div>
            <div style='margin-bottom: 6px;'>{'🌟 <strong>VIP</strong>' if order['vip'] else ''} {label}</div>
            <div style='margin-bottom: 6px;'><strong>Timer:</strong> {timer_display}</div>
            <div style='margin-top: 10px;'>
                {button_html}
                <button style='margin: 4px;'>📝 Notes</button>
                <button style='margin: 4px;'>📍 Edit Address</button>
            </div>
        </div>
    """, unsafe_allow_html=True)

def show_captain_map(selected_order=None):
    zoom = st.session_state.get('delivery_map_zoom', 13)
    m = folium.Map(location=DEFAULT_COORDS, zoom_start=zoom)
    # Always show captain markers
    for cap in captains:
        folium.Marker(location=cap["coords"], popup=cap["name"], icon=folium.Icon(color="red")).add_to(m)
    # If an order is selected, add customer and restaurant markers
    if selected_order is not None:
        rest_coords = restaurant_locations.get(selected_order["restaurant"], DEFAULT_COORDS)
        cust_coords = customer_locations.get(selected_order["customer"], DEFAULT_COORDS)
        folium.Marker(location=cust_coords, popup="Customer", icon=folium.Icon(color="blue")).add_to(m)
        folium.Marker(location=rest_coords, popup="Restaurant", icon=folium.Icon(color="green")).add_to(m)
    st_folium(m, width=1600, height=400)
    col1, col2 = st.columns(2)

    # If an order is selected, show recommended captains
    if selected_order is not None:
        rest_coords = restaurant_locations.get(selected_order["restaurant"], DEFAULT_COORDS)
        captain_distances = []
        for cap in captains:
            dist = geodesic(rest_coords, cap["coords"]).km
            captain_distances.append({"name": cap["name"], "distance": dist})
        captain_distances.sort(key=lambda x: x["distance"])
        st.markdown("**Recommended Captains:**")
        for idx, cap in enumerate(captain_distances, 1):
            st.write(f"{idx}. {cap['name']} - {cap['distance']:.2f} km from restaurant")

def update_order_timers():
    """Update timers for all orders based on their current status"""
    current_time = time.time()
    
    for order in orders:
        order_id = order['id']
        current_status = order['status']
        
        # Initialize timer if not exists
        if order_id not in st.session_state['order_timers']:
            st.session_state['order_timers'][order_id] = {}
        
        # Initialize stage start times if not exists
        if order_id not in st.session_state['order_stage_start_times']:
            st.session_state['order_stage_start_times'][order_id] = {}
        
        # Initialize stage durations if not exists
        if order_id not in st.session_state['order_stage_durations']:
            st.session_state['order_stage_durations'][order_id] = {}
        
        # Check if status changed or if this is the first time seeing this status
        if current_status not in st.session_state['order_stage_start_times'][order_id]:
            # New stage - start timer
            st.session_state['order_stage_start_times'][order_id][current_status] = current_time
            st.session_state['order_timers'][order_id][current_status] = 0
        else:
            # Update current timer
            start_time = st.session_state['order_stage_start_times'][order_id][current_status]
            elapsed_time = current_time - start_time
            st.session_state['order_timers'][order_id][current_status] = elapsed_time

def format_time(seconds):
    """Format seconds into HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

# Update timers before displaying
update_order_timers()

for i, tab in enumerate(tabs):
    with tab:
        if status_tabs[i] == "Captain":
            # Show map at the top of the Captain tab
            show_captain_map(selected_order=None if st.session_state.get('delivery_map_order_id') is None else next((o for o in orders if o['id'] == st.session_state['delivery_map_order_id']), None))
            
            # Show counter for Captain tab
            captain_orders = [order for order in orders if order["status"] == status_tabs[i]]
            st.subheader(f"Orders - {status_tabs[i]} ({len(captain_orders)} orders)")
        else:
            if status_tabs[i] == "Processing":
                st.subheader(f"Orders - {status_tabs[i]}")
            else:
                # Show counter for other tabs
                filtered_orders = [order for order in orders if order["status"] == status_tabs[i]]
                st.subheader(f"Orders - {status_tabs[i]} ({len(filtered_orders)} orders)")
        
        if status_tabs[i] == "Processing":
            cols = st.columns(3)
            for j, substage in enumerate(processing_substages):
                with cols[j]:
                    sub_orders = [o for o in orders if o["status"] == substage]
                    st.markdown(f"### {substage} ({len(sub_orders)} orders)")
                    if not sub_orders:
                        st.info("No orders in this substage.")
                    else:
                        for order in sub_orders:
                            with st.container():
                                show_order_card(order, show_delivery_btn=False)
        elif status_tabs[i] == "Captain":
            filtered_orders = [order for order in orders if order["status"] == status_tabs[i]]
            if not filtered_orders:
                st.warning("No orders in this tab.")
            else:
                cols = st.columns(3)
                for idx, order in enumerate(filtered_orders):
                    with cols[idx % 3]:
                        with st.container():
                            show_order_card(order, show_delivery_btn=True)
                            # Delivery button logic
                            if st.button("Delivery", key=f"delivery_{order['id']}"):
                                st.session_state['delivery_map_order_id'] = order['id']
                                st.session_state['delivery_map_zoom'] = 13
                                st.rerun()
        else:
            filtered_orders = [order for order in orders if order["status"] == status_tabs[i]]
            if not filtered_orders:
                st.warning("No orders in this tab.")
            else:
                cols = st.columns(3)
                for idx, order in enumerate(filtered_orders):
                    with cols[idx % 3]:
                        with st.container():
                            show_order_card(order, show_delivery_btn=False)

# Simple auto-refresh for timers
if 'last_refresh' not in st.session_state:
    st.session_state['last_refresh'] = time.time()

current_time = time.time()
if current_time - st.session_state['last_refresh'] > 1:  # Refresh every second
    st.session_state['last_refresh'] = current_time
    st.rerun()