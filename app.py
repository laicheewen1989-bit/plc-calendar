from datetime import date, datetime, timedelta, time
import streamlit as st
from streamlit_calendar import calendar

# 1. 页面极简配置
st.set_page_config(
    page_title="PLC Schedule", page_icon="📅", layout="wide"
)

st.title("📅 PLC Team Calendar")
st.caption("Simplified version: Easily track schedules with auto-saved Engineers, Sites, and Tasks.")

# 2. 初始化 Session State 记忆库数据
if "calendar_events" not in st.session_state:
    st.session_state.calendar_events = []

if "saved_engineers" not in st.session_state:
    st.session_state.saved_engineers = ["Kelvin", "Alex", "Dave"]

if "saved_sites" not in st.session_state:
    st.session_state.saved_sites = ["Line 1 - Assembly", "Line 2 - Packaging", "Cell A"]

if "saved_tasks" not in st.session_state:
    st.session_state.saved_tasks = ["PLC Wiring", "I/O Signal Testing", "HMI Flashing", "Troubleshooting"]

# 3. 页签定义
tab_calendar, tab_add, tab_manage = st.tabs(
    ["📅 Calendar View", "➕ Request Schedule", "⚙️ Manage & Edit"]
)

# ----------------- TAB 1: 极简日历视图 -----------------
with tab_calendar:
    calendar_options = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek",
        },
        "initialView": "timeGridWeek",
        "slotMinTime": "08:00:00",
        "slotMaxTime": "18:00:00",
    }

    calendar(
        events=st.session_state.calendar_events,
        options=calendar_options,
        key="plc_calendar",
    )

# ----------------- TAB 2: 动态响应申请表单 -----------------
with tab_add:
    st.subheader("📝 Request Manpower")

    col1, col2 = st.columns(2)

    with col1:
        # --- 1. 工程师名字 (下拉选择 或 手动新增) ---
        eng_opts = ["-- Select Saved Engineer --"] + st.session_state.saved_engineers + ["➕ Add New Engineer"]
        sel_eng = st.selectbox("Engineer Name *", eng_opts, key="sel_eng")
        
        if sel_eng == "➕ Add New Engineer":
            eng_name = st.text_input("Enter New Engineer Name *", placeholder="e.g. John", key="txt_eng")
        elif sel_eng != "-- Select Saved Engineer --":
            eng_name = sel_eng
        else:
            eng_name = ""

        # --- 2. 地点 / Line ID (下拉选择 或 手动新增) ---
        site_opts = ["-- Select Saved Site --"] + st.session_state.saved_sites + ["➕ Add New Site"]
        sel_site = st.selectbox("Site / Line ID *", site_opts, key="sel_site")
        
        if sel_site == "➕ Add New Site":
            site_line = st.text_input("Enter New Site / Line ID *", placeholder="e.g. Line 3 Welding", key="txt_site")
        elif sel_site != "-- Select Saved Site --":
            site_line = sel_site
        else:
            site_line = ""

        # --- 3. 工作内容 (下拉选择 或 手动新增) ---
        task_opts = ["-- Select Saved Task --"] + st.session_state.saved_tasks + ["➕ Add New Task"]
        sel_task = st.selectbox("Task Name", task_opts, key="sel_task")
        
        if sel_task == "➕ Add New Task":
            task_name = st.text_input("Enter New Task Name", placeholder="e.g. Cabinet Inspection", key="txt_task")
        elif sel_task != "-- Select Saved Task --":
            task_name = sel_task
        else:
            task_name = ""

        st.markdown("**Manpower Requirement**")
        col_sup, col_work, col_safe = st.columns(3)
        sup_count = col_sup.number_input("Supervisor", min_value=0, value=1)
        worker_count = col_work.number_input("Worker", min_value=0, value=2)
        safe_count = col_safe.number_input("Safety", min_value=0, value=1)

    with col2:
        st.markdown("**Date & Time Settings**")
        start_date = st.date_input("Start Date", value=date.today())
        end_date = st.date_input("End Date", value=date.today())
        
        start_time = st.time_input("Start Time", value=time(9, 0))
        end_time = st.time_input("End Time", value=time(17, 0))
        
        color = st.selectbox(
            "Color Tag",
            [
                "#29B5E8 (Light Blue)",
                "#0052CC (Dark Blue)",
                "#FF4B4B (Red)",
                "#00D26A (Green)",
                "#FFC107 (Yellow)",
                "#9C27B0 (Purple)",
                "#795548 (Brown)"
            ],
        )

    st.markdown("---")
    submitted = st.button("🚀 Add to Calendar", use_container_width=True, type="primary")

    if submitted:
        if not eng_name or not site_line:
            st.error("Please provide both Engineer Name and Site / Line ID!")
        elif end_date < start_date:
            st.error("End Date cannot be earlier than Start Date!")
        else:
            # 自动保存新输入的名字、地点、工作内容到预设记忆库
            if eng_name and eng_name not in st.session_state.saved_engineers:
                st.session_state.saved_engineers.append(eng_name)
            if site_line and site_line not in st.session_state.saved_sites:
                st.session_state.saved_sites.append(site_line)
            if task_name and task_name not in st.session_state.saved_tasks:
                st.session_state.saved_tasks.append(task_name)

            delta_days = (end_date - start_date).days
            hex_color = color.split(" ")[0]
            
            total_people = sup_count + worker_count + safe_count
            display_title = f"[{site_line}] {eng_name} ({total_people} Pax)"

            for i in range(delta_days + 1):
                current_date = start_date + timedelta(days=i)
                
                start_iso = f"{current_date.strftime('%Y-%m-%d')}T{start_time.strftime('%H:%M:%S')}"
                end_iso = f"{current_date.strftime('%Y-%m-%d')}T{end_time.strftime('%H:%M:%S')}"
                
                event_id = f"evt_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}"
                
                new_event = {
                    "id": event_id,
                    "title": display_title,
                    "start": start_iso,
                    "end": end_iso,
                    "color": hex_color,
                    "extendedProps": {
                        "eng_name": eng_name,
                        "site_line": site_line,
                        "task_name": task_name,
                        "sup_count": sup_count,
                        "worker_count": worker_count,
                        "safe_count": safe_count,
                        "raw_start_date": current_date.strftime('%Y-%m-%d'),
                        "raw_start_time": start_time.strftime('%H:%M'),
                        "raw_end_time": end_time.strftime('%H:%M'),
                    }
                }
                st.session_state.calendar_events.append(new_event)
            
            st.success(f"Success! Scheduled for {delta_days + 1} day(s). New Engineer/Site/Task automatically saved for future use!")
            st.rerun()

# ----------------- TAB 3: 管理与记忆库查看 -----------------
with tab_manage:
    st.subheader("⚙️ Manage Saved Preset Lists & Schedules")
    
    st.markdown("### 📋 Auto-Saved Memory Lists")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.write("**Saved Engineers:**")
        st.json(st.session_state.saved_engineers)
    with col_m2:
        st.write("**Saved Sites / Locations:**")
        st.json(st.session_state.saved_sites)
    with col_m3:
        st.write("**Saved Tasks:**")
        st.json(st.session_state.saved_tasks)
        
    st.markdown("---")
    st.markdown("### 🗑️ Delete Active Schedules")
    if not st.session_state.calendar_events:
        st.info("No active schedule available to delete.")
    else:
        for idx, evt in enumerate(st.session_state.calendar_events):
            with st.expander(f"{evt['start'][:10]} | {evt['title']}"):
                props = evt.get('extendedProps', {})
                st.markdown(f"**Site:** {props.get('site_line', 'N/A')}  |  **Engineer:** {props.get('eng_name', 'N/A')}")
                st.markdown(f"**Task:** {props.get('task_name', 'N/A')}")
                st.markdown(f"**Manpower:** Supervisor: {props.get('sup_count', 0)} | Worker: {props.get('worker_count', 0)} | Safety: {props.get('safe_count', 0)}")
                st.markdown(f"**Time:** {props.get('raw_start_time', 'N/A')} - {props.get('raw_end_time', 'N/A')}")
                
                if st.button("🗑️ Delete this event", key=f"del_{evt['id']}"):
                    st.session_state.calendar_events = [e for e in st.session_state.calendar_events if e['id'] != evt['id']]
                    st.success("Event deleted!")
                    st.rerun()