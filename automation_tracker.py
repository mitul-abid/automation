import pandas as pd
import streamlit as st
from io import BytesIO

st.set_page_config(page_title="Automation Project Tracker", layout="wide")
st.title("🛠️ Automation Project Tracker")

# Session state to persist task data
if "task_data" not in st.session_state:
    st.session_state.task_data = []

st.subheader("➕ Add Task")

with st.form("task_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        project = st.text_input("Project Name")
        phase = st.text_input("Phase Name")
        task = st.text_input("Task Name")
    with col2:
        phase_weight = st.number_input("Phase Weight", min_value=0.0, step=1.0)
        task_weight = st.number_input("Task Weight", min_value=0.0, step=1.0)
        dependency = st.text_input("Dependency (optional)")
    with col3:
        task_progress = st.slider("Task Progress (%)", min_value=0, max_value=100)
        comment = st.text_input("Comment")
        submitted = st.form_submit_button("Add Task")

    if submitted and project and phase and task:
        st.session_state.task_data.append({
            "Project": project,
            "Phase": phase,
            "Phase Weight": phase_weight,
            "Task": task,
            "Task Weight": task_weight,
            "Dependency": dependency,
            "Comment": comment,
            "Task Progress": task_progress
        })
        st.success(f"Task '{task}' added to project '{project}'!")

# Show current task table
df = pd.DataFrame(st.session_state.task_data)

if not df.empty:
    # Compute progress metrics
    df["Phase Weight"] = df["Phase Weight"].fillna(method="ffill")

    phase_progress = df.groupby(["Project", "Phase"]).apply(
        lambda x: (x["Task Progress"] * x["Task Weight"]).sum() / x["Task Weight"].sum()
    ).reset_index(name="Phase Progress")

    df = df.merge(phase_progress, on=["Project", "Phase"], how="left")

    project_progress = df.groupby("Project").apply(
        lambda x: (x["Phase Progress"] * x["Phase Weight"]).sum() / x["Phase Weight"].sum()
    ).reset_index(name="Project Progress")

    df = df.merge(project_progress, on="Project", how="left")

    # Format progress columns
    df["Phase Progress"] = df["Phase Progress"].round(2).astype(str) + "%"
    df["Project Progress"] = df["Project Progress"].round(2).astype(str) + "%"

    st.subheader("📊 Task Table")
    st.dataframe(df, use_container_width=True)

    # Download button
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Project Tracker')
    output.seek(0)

    st.download_button(
        label="📥 Download Excel Report",
        data=output,
        file_name="project_tracker.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Add some tasks to begin tracking your project.")
