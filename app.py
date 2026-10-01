import pandas as pd
import streamlit as st
from database import create_connection, create_table

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.main {
    padding-top: 2rem;
}

/* Main headings */
h1 {
    font-size: 2.5rem;
}

h2, h3 {
    font-weight: 700;
}

/* Dashboard metric cards */
[data-testid="stMetric"] {
    background-color: #1f2937;
    border: 1px solid #374151;
    padding: 20px;
    border-radius: 12px;
}

/* Metric labels */
[data-testid="stMetricLabel"] {
    color: #d1d5db !important;
}

/* Metric values */
[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 700;
}

/* Buttons */
.stButton > button {
    border-radius: 8px;
}

/* Text inputs */
.stTextInput input,
.stTextArea textarea {
    border-radius: 8px;
}

/* Select boxes */
.stSelectbox div[data-baseweb="select"] {
    border-radius: 8px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# DATABASE SETUP
# =====================================================

create_table()


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Job Application Tracker",
    page_icon="💼",
    layout="wide"
)


# =====================================================
# TITLE
# =====================================================

st.title("💼 Job Application Tracker")
st.write("Track and manage your job applications easily.")


# =====================================================
# ADD APPLICATION
# =====================================================

st.divider()
st.subheader("➕ Add Job Application")

with st.form("application_form"):

    company = st.text_input("Company Name")
    job_role = st.text_input("Job Role")
    location = st.text_input("Location")

    application_date = st.date_input("Application Date")

    status = st.selectbox(
        "Application Status",
        [
            "Applied",
            "Shortlisted",
            "Interview",
            "Selected",
            "Rejected",
            "On Hold"
        ]
    )

    interview_date = st.date_input("Interview Date")
    follow_up_date = st.date_input("Follow-up Date")

    notes = st.text_area("Notes")

    submit = st.form_submit_button("💾 Save Application")

    if submit:

        if company and job_role:

            connection = create_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO applications
                (
                    company,
                    job_role,
                    location,
                    application_date,
                    status,
                    interview_date,
                    follow_up_date,
                    notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    company,
                    job_role,
                    location,
                    application_date,
                    status,
                    interview_date,
                    follow_up_date,
                    notes
                )
            )

            connection.commit()
            connection.close()

            st.success("✅ Application saved successfully!")

        else:
            st.error("⚠️ Company Name and Job Role are required.")


# =====================================================
# DASHBOARD
# =====================================================

st.divider()
st.subheader("📊 Application Dashboard")

connection = create_connection()

total_applications = connection.execute(
    "SELECT COUNT(*) FROM applications"
).fetchone()[0]

applied = connection.execute(
    "SELECT COUNT(*) FROM applications WHERE status = 'Applied'"
).fetchone()[0]

interviews = connection.execute(
    "SELECT COUNT(*) FROM applications WHERE status = 'Interview'"
).fetchone()[0]

selected = connection.execute(
    "SELECT COUNT(*) FROM applications WHERE status = 'Selected'"
).fetchone()[0]

rejected = connection.execute(
    "SELECT COUNT(*) FROM applications WHERE status = 'Rejected'"
).fetchone()[0]

shortlisted = connection.execute(
    "SELECT COUNT(*) FROM applications WHERE status = 'Shortlisted'"
).fetchone()[0]

on_hold = connection.execute(
    "SELECT COUNT(*) FROM applications WHERE status = 'On Hold'"
).fetchone()[0]

connection.close()


col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Applications",
    total_applications
)

col2.metric(
    "Applied",
    applied
)

col3.metric(
    "Interviews",
    interviews
)

col4.metric(
    "Selected",
    selected
)

col5.metric(
    "Rejected",
    rejected
)


# =====================================================
# STATUS CHART
# =====================================================

st.divider()
st.subheader("📈 Application Status Analysis")

connection = create_connection()

status_data = pd.read_sql_query(
    """
    SELECT
        status,
        COUNT(*) AS total
    FROM applications
    GROUP BY status
    """,
    connection
)

connection.close()

if not status_data.empty:

    st.bar_chart(
        status_data.set_index("status")
    )

else:

    st.info("No data available for chart.")


# =====================================================
# SEARCH & FILTER
# =====================================================

st.divider()
st.subheader("🔍 Search & Filter Applications")

col1, col2 = st.columns(2)

with col1:

    search_company = st.text_input(
        "Search by Company",
        placeholder="Enter company name..."
    )

with col2:

    filter_status = st.selectbox(
        "Filter by Status",
        [
            "All",
            "Applied",
            "Shortlisted",
            "Interview",
            "Selected",
            "Rejected",
            "On Hold"
        ]
    )

# =====================================================
# CSV EXPORT
# =====================================================

st.divider()
st.subheader("📤 Export Applications")

connection = create_connection()

export_data = pd.read_sql_query(
    """
    SELECT
        company,
        job_role,
        location,
        application_date,
        status,
        interview_date,
        follow_up_date,
        notes
    FROM applications
    ORDER BY id DESC
    """,
    connection
)

connection.close()

if not export_data.empty:

    csv_data = export_data.to_csv(index=False)

    st.download_button(
        label="📥 Download Applications CSV",
        data=csv_data,
        file_name="job_applications.csv",
        mime="text/csv"
    )

else:
    st.info("No applications available for export.")
    # =====================================================
# REMINDERS
# =====================================================

st.divider()
st.subheader("⏰ Follow-up & Interview Reminders")

today = pd.Timestamp.today().date()

connection = create_connection()

reminders = connection.execute(
    """
    SELECT
        company,
        job_role,
        status,
        interview_date,
        follow_up_date
    FROM applications
    WHERE
        (interview_date IS NOT NULL AND interview_date != '')
        OR
        (follow_up_date IS NOT NULL AND follow_up_date != '')
    ORDER BY follow_up_date
    """
).fetchall()

connection.close()


if reminders:

    overdue_followups = []
    today_followups = []
    upcoming_followups = []
    upcoming_interviews = []

    for reminder in reminders:

        company = reminder[0]
        job_role = reminder[1]
        status = reminder[2]
        interview_date = reminder[3]
        follow_up_date = reminder[4]

        # Follow-up reminder
        if follow_up_date:

            try:
                followup = pd.to_datetime(
                    follow_up_date
                ).date()

                if followup < today:
                    overdue_followups.append(
                        (company, job_role, followup)
                    )

                elif followup == today:
                    today_followups.append(
                        (company, job_role, followup)
                    )

                else:
                    upcoming_followups.append(
                        (company, job_role, followup)
                    )

            except:
                pass


        # Interview reminder
        if interview_date:

            try:
                interview = pd.to_datetime(
                    interview_date
                ).date()

                if interview >= today:
                    upcoming_interviews.append(
                        (company, job_role, interview)
                    )

            except:
                pass


    # -------------------------------------------------
    # OVERDUE
    # -------------------------------------------------

    if overdue_followups:

        st.error("🔴 Overdue Follow-ups")

        for company, role, date in overdue_followups:

            st.write(
                f"**{company}** — {role} — "
                f"Follow-up was due on **{date}**"
            )


    # -------------------------------------------------
    # TODAY
    # -------------------------------------------------

    if today_followups:

        st.warning("🟠 Follow-ups Due Today")

        for company, role, date in today_followups:

            st.write(
                f"**{company}** — {role} — "
                f"Follow-up: **{date}**"
            )


    # -------------------------------------------------
    # UPCOMING FOLLOW-UPS
    # -------------------------------------------------

    if upcoming_followups:

        st.info("🔵 Upcoming Follow-ups")

        for company, role, date in upcoming_followups:

            st.write(
                f"**{company}** — {role} — "
                f"Follow-up: **{date}**"
            )


    # -------------------------------------------------
    # UPCOMING INTERVIEWS
    # -------------------------------------------------

    if upcoming_interviews:

        st.success("🟢 Upcoming Interviews")

        for company, role, date in upcoming_interviews:

            st.write(
                f"**{company}** — {role} — "
                f"Interview: **{date}**"
            )

else:

    st.info("No reminders available.")
# =====================================================
# GET APPLICATIONS
# =====================================================

st.divider()
st.subheader("📋 All Job Applications")

connection = create_connection()

query = """
    SELECT
        id,
        company,
        job_role,
        location,
        application_date,
        status,
        interview_date,
        follow_up_date,
        notes
    FROM applications
    WHERE 1=1
"""

parameters = []


# Company search

if search_company:

    query += " AND company LIKE ?"

    parameters.append(
        f"%{search_company}%"
    )


# Status filter

if filter_status != "All":

    query += " AND status = ?"

    parameters.append(
        filter_status
    )


query += " ORDER BY id DESC"


applications = connection.execute(
    query,
    parameters
).fetchall()

connection.close()


# =====================================================
# DISPLAY APPLICATIONS
# =====================================================

if applications:

    for application in applications:

        application_id = application[0]

        st.write(
            f"### 🏢 {application[1]}"
        )

        st.write(
            f"**Job Role:** {application[2]}"
        )

        st.write(
            f"**Location:** {application[3]}"
        )

        st.write(
            f"**Application Date:** {application[4]}"
        )

        st.write(
            f"**Status:** {application[5]}"
        )

        st.write(
            f"**Interview Date:** {application[6]}"
        )

        st.write(
            f"**Follow-up Date:** {application[7]}"
        )

        st.write(
            f"**Notes:** {application[8]}"
        )


        # =================================================
        # EDIT & DELETE BUTTONS
        # =================================================

        col1, col2 = st.columns(2)


        # EDIT BUTTON

        with col1:

            edit_clicked = st.button(
                "✏️ Edit",
                key=f"edit_{application_id}"
            )

            if edit_clicked:

                st.session_state[
                    f"editing_{application_id}"
                ] = True


        # DELETE BUTTON

        with col2:

            delete_clicked = st.button(
                "🗑️ Delete",
                key=f"delete_{application_id}"
            )

            if delete_clicked:

                connection = create_connection()

                connection.execute(
                    """
                    DELETE FROM applications
                    WHERE id = ?
                    """,
                    (application_id,)
                )

                connection.commit()
                connection.close()

                st.success(
                    "🗑️ Application deleted successfully!"
                )

                st.rerun()


        # =================================================
        # EDIT FORM
        # =================================================

        if st.session_state.get(
            f"editing_{application_id}",
            False
        ):

            st.write("#### ✏️ Edit Application")

            status_options = [
                "Applied",
                "Shortlisted",
                "Interview",
                "Selected",
                "Rejected",
                "On Hold"
            ]

            current_status = application[5]

            if current_status in status_options:

                current_status_index = (
                    status_options.index(current_status)
                )

            else:

                current_status_index = 0


            with st.form(
                f"edit_form_{application_id}"
            ):

                new_company = st.text_input(
                    "Company Name",
                    value=application[1]
                )

                new_job_role = st.text_input(
                    "Job Role",
                    value=application[2]
                )

                new_location = st.text_input(
                    "Location",
                    value=application[3]
                )

                new_status = st.selectbox(
                    "Status",
                    status_options,
                    index=current_status_index
                )

                new_notes = st.text_area(
                    "Notes",
                    value=application[8] or ""
                )

                update = st.form_submit_button(
                    "💾 Update Application"
                )


                if update:

                    if new_company and new_job_role:

                        connection = create_connection()

                        connection.execute(
                            """
                            UPDATE applications
                            SET
                                company = ?,
                                job_role = ?,
                                location = ?,
                                status = ?,
                                notes = ?
                            WHERE id = ?
                            """,
                            (
                                new_company,
                                new_job_role,
                                new_location,
                                new_status,
                                new_notes,
                                application_id
                            )
                        )

                        connection.commit()
                        connection.close()

                        st.session_state[
                            f"editing_{application_id}"
                        ] = False

                        st.success(
                            "✅ Application updated successfully!"
                        )

                        st.rerun()

                    else:

                        st.error(
                            "⚠️ Company Name and Job Role are required."
                        )


        st.divider()


else:

    st.info(
        "No job applications found."
    )