import streamlit as st
import snowflake.connector
import email_validator
import secrets
import string

# Page configuration
st.set_page_config(
    page_title="Financial Advisor Sign Up",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Styling
st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    .reportview-container { background: #f0f0f5; }
    .stButton>button { background-color: #4CAF50; color: white; }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title('💼 Financial Advisor Sign Up')
st.subheader("Access the Financial Advisor App")

st.markdown("""
    Please enter your **Snowflake email** address below to request access.  
    After submitting, download your credentials to log in. \n\n**Note:** You will be prompted to change your password upon your first login.
    \n\n**MFA:** [🔐 You are also required to enroll in MFA after logging in](https://docs.snowflake.com/en/user-guide/ui-snowsight-profile#label-snowsight-set-up-mfa)\n\n
    """)

st.markdown("[🔗 Access & Architecture Slides](https://docs.google.com/presentation/d/1pHYRUULcfW-DPZJ5OzfaXL9Bh-MN4V_RfMHxdmkfQac/edit?usp=sharing)")

# Connect to Snowflake  
conn = snowflake.connector.connect(
    user=st.secrets["user"],
    password=st.secrets["password"],
    account=st.secrets["account"],
    role=st.secrets["role"],
    warehouse=st.secrets["warehouse"],
    session_parameters={'QUERY_TAG': 'Streamlit-signup-fin-chat-demo'}
)

# Function to run queries on Snowflake
def run_query(query): 
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

# Check if email is valid snowflake.com email
def check_email(e):
    try:
        validation = email_validator.validate_email(email=e)
        if validation.domain == 'snowflake.com':
            return True, validation.local_part
        else:
            st.error("Only valid Snowflake accounts are allowed.")
            return False, ''
    except email_validator.EmailNotValidError:
        return False, ''
    
# Function to generate a secure random password
def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(secrets.choice(characters) for i in range(length))
        # Ensure the password has at least one uppercase letter, one digit, and one symbol
        if (any(c.isupper() for c in password) and 
            any(c.isdigit() for c in password) and 
            any(c in string.punctuation for c in password)):
            return password


# Input form
with st.form("signup_form"):
    email_input = st.text_input(
        "Enter your Snowflake E-Mail 👇",
        placeholder="Only valid @snowflake.com emails allowed"
    )
    submit_button = st.form_submit_button("Request Access")

if submit_button:
    valid_email, local_val = check_email(email_input)
    if valid_email:
        generated_password = generate_password(8)
        output = f"""Username:\n{email_input}\n\nPassword:\n{generated_password}\n\nAcct URL:\nhttps://app.snowflake.com/east-us-2.azure/opa12479"""

        # Check if the user already exists
        if len(run_query(f"""SHOW USERS LIKE '{email_input}';""")) > 0:
            st.warning(f"User **{email_input}** already exists. \n\n If you need a password reset, please contact [Marius Ndini](mailto:Marius.Ndini@snowflake.com).")
        else:
            # Create new user
            run_query(f""" 
                CREATE USER IF NOT EXISTS "{email_input}" 
                DEFAULT_WAREHOUSE = FINWH 
                DEFAULT_NAMESPACE = EARNINGS.PUBLIC
                DEFAULT_ROLE = EARNINGS_CHAT_ROLE
                MUST_CHANGE_PASSWORD = true 
                PASSWORD = '{generated_password}';
            """)
            run_query(f'GRANT ROLE earnings_chat_role TO USER "{email_input}";')

            st.success("Account created successfully! Download your credentials below.")
            st.download_button(
                label="📥 Download Credentials",
                data=output,
                type="primary",
                file_name="FinServCreds.txt",
                mime="text/plain"
            )
            st.info("Go to the Demo Account: [Snowflake Demo Account](https://app.snowflake.com/east-us-2.azure/opa12479)")
    else:
        st.error("**Invalid Email**. Only `snowflake.com` emails are allowed.")

# Footer link
st.markdown("For any issues, please contact [Marius Ndini](mailto:Marius.Ndini@snowflake.com).")
