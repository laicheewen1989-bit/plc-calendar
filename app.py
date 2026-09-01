from datetime import date, datetime, timedelta, time
import gspread
import pandas as pd
import streamlit as st
from streamlit_calendar import calendar

# 1. 页面配置与 CSS
st.set_page_config(page_title="PLC Schedule", page_icon="📅", layout="wide")

st.markdown(
    """
<style>
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
    .fc-toolbar { flex-wrap: wrap !important; gap: 6px !important; justify-content: center !important; }
    .fc-toolbar-title { font-size: 1.1rem !important; }
    .fc-button { padding: 0.3rem 0.5rem !important; font-size: 0.85rem !important; }
    .fc-event-title { font-size: 0.8rem !important; white-space: normal !important; }
</style>
""",
    unsafe_allow_html=True,
)

st.title("📅 PLC Team Calendar")


# 2. 精准用 Sheet ID 连接（彻底解决 404）
@st.cache_resource
def get_gspread_client():
    try:
        secrets_dict = dict(st.secrets["connections"]["gsheets"])
        spreadsheet_url = secrets_dict.pop("spreadsheet", "")

        gc = gspread.service_account_from_dict(secrets_dict)

        # 从 URL 中精确提取 Sheet ID (例如: 17KsOcPgdS8NRtmGC_C-sQ9Eorl6N9znC0WzA95_X_EY)
        if "spreadsheets/d/" in spreadsheet_url:
            sheet_id = spreadsheet_url.split("spreadsheets/d/")[1].split("/")[
                0
            ]
            sh = gc.open_by_key(sheet_id)
        elif spreadsheet_url:
            sh = gc.open_by_url(spreadsheet_url)
        else:
            sh = gc.open("PLC_Schedule_DB")
        return sh
    except Exception as e:
        st.error(f"Cloud DB Connection Error: {e}")
        return None


sh = get_gspread_client()


def load_data():
    if not sh:
        return (
            [],
            ["Kelvin", "Alex", "Dave"],
            ["Line 1 - Assembly", "Line 2 - Packaging", "Cell A"],
            ["PLC Wiring"],
        )

    try:
        ws_events = sh.worksheet("Events")
        records_events = ws_events.get_all_records()
        df_events = pd.DataFrame(records_events)
    except Exception:
        df_events = pd.DataFrame()

    try:
        ws_presets = sh.worksheet("Presets")
        records_presets = ws_presets.get_all_records()
        df_presets = pd.DataFrame(records_presets)
    except Exception:
        df_presets = pd.DataFrame()

    events_list = []
    if not df_events.empty:
        for _, row in df_events.iterrows():
            events_list.append(
                {
                    "id": str(row.get("id", "")),
                    "title": str(row.get("title", "")),
                    "start": str(row.get("start", "")),
                    "end": str(row.get("end", "")),
                    "color": str(row.get("color", "#29B5E8")),
                    "extendedProps": {
                        "eng_name": str(row.get("eng_name", "")),
                        "site_line": str(row.get("site_line", "")),
                        "task_name": str(row.get("task_name", "")),
                        "sup_count": int(row.get("sup_count", 0)),
                        "worker_count": int(row.get("worker_count", 0)),
                        "safe_count": int(row.get("safe_count", 0)),
                        "raw_start_date": str(row.get("raw_start_date", "")),
                        "raw_start_time": str(row.get("raw_start_time", "")),
                        "raw_end_time": str(row.get("raw_end_time", "")),
                    },
                }
            )

    saved_engs = ["Kelvin", "Alex", "Dave"]
    saved_sites = ["Line 1 - Assembly", "Line 2 - Packaging", "Cell A"]
    saved_tasks = [
        "PLC Wiring",
        "I/O Signal Testing",
        "HMI Flashing",
        "Troubleshooting",
    ]

    if not df_presets.empty and "type" in df_presets.columns:
        e_list = df_presets[df_presets["type"] == "engineer"][
            "value"
        ].dropna().tolist()
        s_list = df_presets[df_presets["type"] == "site"][
            "value"
        ].dropna().tolist()
        t_list = df_presets[df_presets["type"] == "task"][
            "value"
        ].dropna().tolist()
        if e_list:
            saved_engs = list(set(saved_engs + [str(x) for x in e_list]))
        if s_list:
            saved_sites = list(set(saved_sites + [str(x) for x in s_list]))
        if t_list:
            saved_tasks = list(set(saved_tasks + [str(x) for x in t_list]))

    return events_list, saved_engs, saved_sites, saved_tasks


def save_data(events_list, saved_engs, saved_sites, saved_tasks):
    if not sh:
        return

    rows = []
    for evt in events_list:
        props = evt.get("extendedProps", {})
        rows.append(
            {
                "id": evt.get("id"),
                "title": evt.get("title"),
                "start": evt.get("start"),
                "end": evt.get("end"),
                "color": evt.get("color"),
                "eng_name": props.get("eng_name"),
                "site_line": props.get("site_line"),
                "task_name": props.get("task_name"),
                "sup_count": props.get("sup_count"),
                "worker_count": props.get("worker_count"),
                "safe_count": props.get("safe_count"),
                "raw_start_date": props.get("raw_start_date"),
                "raw_start_time": props.get("raw_start_time"),
                "raw_end_time": props.get("raw_end_time"),
            }
        )
    df_events = pd.DataFrame(rows)

    preset_rows = []
    for eng in saved_engs:
        preset_rows.append({"type": "engineer", "value": eng})
    for site in saved_sites:
        preset_rows.append({"type": "site", "value": site})
    for task in saved_tasks:
        preset_rows.append({"type": "task", "value": task})
    df_presets = pd.DataFrame(preset_rows)

    try:
        ws_events = sh.worksheet("Events")
        ws_events.clear()
    except Exception:
        ws_events = sh.add_worksheet(title="Events", rows="1000", cols="20")

    if not df_events.empty:
        ws_events.update(
            [df_events.columns.values.tolist()] + df_events.values.tolist()
        )

    try:
        ws_presets = sh.worksheet("Presets")
        ws_presets.clear()
    except Exception:
        ws_presets = sh.add_worksheet(title="Presets", rows="1000", cols="10")

    if not df_presets.empty:
        ws_presets.update(
            [df_presets.columns.values.tolist()] + df_presets.values.tolist()
        )


if "loaded" not in st.session_state:
    (
        st.session_state.calendar_events,
        st.session_state.saved_engineers,
        st.session_state.saved_sites,
        st.session_state.saved_tasks,
    ) = load_data()
    st.session_state.loaded = True

tab_calendar, tab_add, tab_manage = st.tabs(
    ["📅 Calendar", "➕ Request", "⚙️ Manage"]
)

with tab_calendar:
    calendar_options = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,listWeek,timeGridWeek",
        },
        "initialView": "dayGridMonth",
        "height": "auto",
        "slotMinTime": "08:00:00",
        "slotMaxTime": "18:00:00",
    }

    calendar(
        events=st.session_state.calendar_events,
        options=calendar_options,
        key="plc_calendar",
    )

with tab_add:
    st.subheader("📝 Request Manpower")

    col1, col2 = st.columns(2)

    with col1:
        eng_opts = [
            "-- Select Saved Engineer --"
        ] + st.session_state.saved_engineers + ["➕ Add New Engineer"]
        sel_eng = st.selectbox("Engineer Name *", eng_opts, key="sel_eng")

        if sel_eng == "➕ Add New Engineer":
            eng_name = st.text_input(
                "New Engineer Name *", placeholder="e.g. John", key="txt_eng"
            )
        elif sel_eng != "-- Select Saved Engineer --":
            eng_name = sel_eng
        else:
            eng_name = ""

        site_opts = [
            "-- Select Saved Site --"
        ] + st.session_state.saved_sites + ["➕ Add New Site"]
        sel_site = st.selectbox("Site / Line ID *", site_opts, key="sel_site")

        if sel_site == "➕ Add New Site":
            site_line = st.text_input(
                "New Site / Line ID *",
                placeholder="e.g. Line 3 Welding",
                key="txt_site",
            )
        elif sel_site != "-- Select Saved Site --":
            site_line = sel_site
        else:
            site_line = ""

        task_opts = [
            "-- Select Saved Task --"
        ] + st.session_state.saved_tasks + ["➕ Add New Task"]
        sel_task = st.selectbox("Task Name", task_opts, key="sel_task")

        if sel_task == "➕ Add New Task":
            task_name = st.text_input(
                "New Task Name", placeholder="e.g. Inspection", key="txt_task"
            )
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
                "#795548 (Brown)",
            ],
        )

    st.markdown("---")
    submitted = st.button(
        "🚀 Add to Calendar", use_container_width=True, type="primary"
    )

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
                        "raw_start_date": current_date.strftime("%Y-%m-%d"),
                        "raw_start_time": start_time.strftime("%H:%M"),
                        "raw_end_time": end_time.strftime("%H:%M"),
                    },
                }
                st.session_state.calendar_events.append(new_event)

            save_data(
                st.session_state.calendar_events,
                st.session_state.saved_engineers,
                st.session_state.saved_sites,
                st.session_state.saved_tasks,
            )

            st.success("Scheduled and saved to Cloud DB!")
            st.rerun()

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
                props = evt.get("extendedProps", {})
                st.write(
                    f"**Site:** {props.get('site_line')} | **Eng:** {props.get('eng_name')}"
                )
                st.write(f"**Task:** {props.get('task_name')}")
                st.write(
                    f"**Manpower:** Sup:{props.get('sup_count')} | Work:{props.get('worker_count')} | Safe:{props.get('safe_count')}"
                )

                if st.button("🗑️ Delete Event", key=f"del_{evt['id']}"):
                    st.session_state.calendar_events = [
                        e
                        for e in st.session_state.calendar_events
                        if e["id"] != evt["id"]
                    ]
                    save_data(
                        st.session_state.calendar_events,
                        st.session_state.saved_engineers,
                        st.session_state.saved_sites,
                        st.session_state.saved_tasks,
                    )
                    st.success("Deleted from Cloud DB!")
                    st.rerun()
