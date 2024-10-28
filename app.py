import streamlit as st
import snowflake.connector
import email_validator


# CONNECT TO SNOWFLAKE  
conn = snowflake.connector.connect( user= st.secrets["user"],
                                    password= st.secrets["password"],
                                    account= st.secrets["account"],
                                    role = st.secrets["role"],
                                    warehouse = st.secrets["warehouse"],
                                    session_parameters={
                                        'QUERY_TAG': 'Streamlit-signup-fin-chat-demo',
                                    })

# function to run queries on Snowflake
def run_query(query): 
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

def check_email(e):
    try:
        validation = email_validator.validate_email(email = e)
        if(validation.domain == 'snowflake.com'):
            return True, validation.local_part
        else:
            st.markdown("**Only Valid Snowflake Accounts are Allowed.**")
            return False, ''
        
    except email_validator.EmailNotValidError as e:
        #   st.write(str(e))
          return False, ''


    

st.title('Financial Advisor Sign Up')

st.markdown('To access the Financial Advisor SiS Application, kindly provide your Snowflake email address below.')
st.markdown('Once you\'ve submitted your email, make sure to download your credentials to login.')
st.markdown('You will be asked to change your password once logging into the Demo Account.')

st.markdown('[Access & Architecture Slides](https://docs.google.com/presentation/d/1pHYRUULcfW-DPZJ5OzfaXL9Bh-MN4V_RfMHxdmkfQac/edit?usp=sharing)')
st.text("")

st.markdown('**After** credentials are downloaded log into https://app.snowflake.com/east-us-2.azure/opa12479 \n\n All Demo Assets will be available. ')

email_input = st.text_input(
        "Enter your Snowflake E-Mail👇",
        placeholder = "Only Valid @Snowflake.com E-Mails Allowed"
    )


if st.button('GO!'):
    valid_email, local_val = check_email(email_input)

    if valid_email==True:
        output = f'''username: 
    {email_input}

password: 
    Red123!!!

log-in URL: 
    https://app.snowflake.com/east-us-2.azure/opa12479'''


        if len(run_query(f'''SHOW USERS LIKE '{email_input}';''')) > 0:
            st.markdown( '**User** {email_input} **Already Exists**' )
            st.markdown( 'If you are looking to reset your PW please Email Marius.Ndini@snowflake.com' )         

        else:

            run_query( f''' 
                create user IF NOT EXISTS "{email_input}" 
                    DEFAULT_WAREHOUSE = FINWH 
                    DEFAULT_NAMESPACE = EARNINGS.PUBLIC
                    DEFAULT_ROLE = EARNINGS_CHAT_ROLE
                    MUST_CHANGE_PASSWORD=true 
                    PASSWORD="Red123!!!";
                ''' )
            run_query( f'grant role earnings_chat_role to user "{email_input}";' )

            st.markdown('**Download your log-in credentials below!** \n\n Do not exit this app without doing so. \n\n You will be asked to changed your Password after logging in.')
            st.download_button('Download Credentials', output, 'MyDayCreds.txt', type="primary", icon="✅")
            st.markdown('log into: https://app.snowflake.com/east-us-2.azure/opa12479 \n\n after downloading your credentials')


    else:
        st.markdown(f'''**INVALID EMAIL** \n\n Only Snowflake.com emails: {email_input} is not a Snowflake email address''')



