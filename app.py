from datetime import date, datetime, timedelta, time
import streamlit as st
from streamlit_calendar import calendar

# 1. 页面极简配置 & 手机端 CSS 优化
st.set_page_config(
    page_title="PLC Schedule", page_icon="📅", layout="wide"
)

# 注入 Mobile 专用 CSS，让手机界面极致干净
st.markdown("""
<style>
    /* 压缩手机端的左右边距，最大化使用屏幕 */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    /* 优化日历顶栏按钮在手机上的自动换行 */
    .fc-toolbar {
        flex-wrap: wrap !important;
        gap: 6px !important;
        justify-content: center !important;
    }
    .fc-toolbar-title {
        font-size: 1.1rem !important;
    }
    .fc-button {
        padding: 0.3rem 0.5rem !important;
        font-size: 0.85rem !important;
    }
    /* 解决手机端文字折行问题 */
    .fc-event-title {
        font-size: 0.8rem !important;
        white-space: normal !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📅 PLC Team Calendar")

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
    ["📅 Calendar", "➕ Request", "⚙️ Manage"]
)

# ----------------- TAB 1: 📱 手机友好型日历 -----------------
with tab_calendar:
    # 新增 listWeek 列表视图，高度设为 auto，完美适配手机
    calendar_options = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,listWeek,timeGridWeek",
        },
        "initialView": "dayGridMonth",  # 手机上默认月视图，也可切到 listWeek 清单模式
        "height": "auto",
        "slotMinTime": "08:00:00",
        "slotMaxTime": "18:00:00",
    }

    calendar(
        events=st.session_state.calendar_events,
        options=calendar_options,
        key="plc_calendar",
    )

# ----------------- TAB 2: 动态响应表单 -----------------
with tab_add:
    st.subheader("📝 Request Manpower")

    col1, col2 = st.columns(2)

    with col1:
        # 1. 工程师名字
        eng_opts = ["-- Select Saved Engineer --"] + st.session_state.saved_engineers + ["➕ Add New Engineer"]
        sel_eng = st.selectbox("Engineer Name *", eng_opts, key="sel_eng")
        
        if sel_eng == "➕ Add New Engineer":
            eng_name = st.text_input("New Engineer Name *", placeholder="e.g. John", key="txt_eng")
        elif sel_eng != "-- Select Saved Engineer --":
            eng_name = sel_eng
        else:
            eng_name = ""

        # 2. 地点 / Line ID
        site_opts = ["-- Select Saved Site --"] + st.session_state.saved_sites + ["➕ Add New Site"]
        sel_site = st.selectbox("Site / Line ID *", site_opts, key="sel_site")
        
        if sel_site == "➕ Add New Site":
            site_line = st.text_input("New Site / Line ID *", placeholder="e.g. Line 3 Welding", key="txt_site")
        elif sel_site != "-- Select Saved Site --":
            site_line = sel_site
        else:
            site_line = ""

        # 3. 工作内容
        task_opts = ["-- Select Saved Task --"] + st.session_state.saved_tasks + ["➕ Add New Task"]
        sel_task = st.selectbox("Task Name", task_opts, key="sel_task")
        
        if sel_task == "➕ Add New Task":
            task_name = st.text_input("New Task Name", placeholder="e.g. Inspection", key="txt_task")
        elif sel_task != "-- Select Saved Task --":
            task_name = sel_task
        else:
            task_name = ""

        st.markdown("**Manpower Needed**")
        col_sup, col_work, col_safe = st.columns(3)
        sup_count = col_sup.number_input("Supervisor", min_value=0, value=1)
        worker_count = col_work.number_input("Worker", min_value=0, value=2)
        safe_count = col_safe.number_input("Safety", min_value=0, value=1)

    with col2:
        st.markdown("**Date & Time**")
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
            
            st.success("Scheduled successfully!")
            st.rerun()

# ----------------- TAB 3: 管理 -----------------
with tab_manage:
    st.subheader("⚙️ Manage Schedules & Presets")
    
    with st.expander("📋 View Auto-Saved Presets"):
        st.write("**Engineers:**", st.session_state.saved_engineers)
        st.write("**Sites:**", st.session_state.saved_sites)
        st.write("**Tasks:**", st.session_state.saved_tasks)
        
    st.markdown("### 🗑️ Delete Active Schedules")
    if not st.session_state.calendar_events:
        st.info("No active schedule to delete.")
    else:
        for idx, evt in enumerate(st.session_state.calendar_events):
            with st.expander(f"{evt['start'][:10]} | {evt['title']}"):
                props = evt.get('extendedProps', {})
                st.write(f"**Site:** {props.get('site_line')} | **Eng:** {props.get('eng_name')}")
                st.write(f"**Task:** {props.get('task_name')}")
                st.write(f"**Manpower:** Sup:{props.get('sup_count')} | Work:{props.get('worker_count')} | Safe:{props.get('safe_count')}")
                
                if st.button("🗑️ Delete Event", key=f"del_{evt['id']}"):
                    st.session_state.calendar_events = [e for e in st.session_state.calendar_events if e['id'] != evt['id']]
                    st.success("Deleted!")
                    st.rerun()
