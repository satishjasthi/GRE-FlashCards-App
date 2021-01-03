import sqlite3

import streamlit as st
import pandas as pd

usage_mode = st.text

def get_current_date_and_time():
    # it will get the time zone  
    # of the specified location 
    IST = pytz.timezone('Asia/Kolkata') 

    datetime_ist = datetime.now(IST) 
    return  datetime_ist.strftime('%Y:%m:%d %H:%M:%S')


sqliteConnection = sqlite3.connect('expenses2021.db')
cursor = sqliteConnection.cursor()
print("Successfully Connected to SQLite")

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'
    return href

# create table if not exists
table_name = "ExpensesTable2021"
try:
    sql_table_query = 'create table ' + table_name + '(DateTime text PRIMARY KEY, Amount REAL, Reason text)'
    cursor.execute(sql_table_query)
except:
    pass

st.text("Expense Manager 2021")
written_state=0

# encode passcode to bytes
passcode = str.encode(st.text_input(" passcode", ''))
try:
    cipher_suite = Fernet(passcode)
    with open(".pickachu.pckl","rb") as handle:
        message = cipher_suite.decrypt(pickle.load(handle))
    encoded_text = cipher_suite.encrypt(message)
    decoded_text = cipher_suite.decrypt(encoded_text)
    try:
        expense_name, amount_spent  = st.text_input(" reason, amount", '').split(',')
        expense_name = expense_name.strip()
        amount_spent = float(amount_spent.strip())
        curr_date_time = get_current_date_and_time()

        sqlite_insert_query = f"""INSERT OR REPLACE INTO {table_name}
                                (DateTime, Amount, Reason) 
                                VALUES 
                                ('{curr_date_time}', {amount_spent}, '{expense_name}')"""

        count = cursor.execute(sqlite_insert_query)
        sqliteConnection.commit()
        print(f"Record inserted successfully into {table_name} table ", cursor.rowcount)
        cursor.close()
    except:
        pass


    '''
    **Previous expenses**
    '''
    last_3_rows_query = f"""SELECT * FROM (
    SELECT * FROM {table_name} ORDER BY DateTime DESC LIMIT 3);"""
    df = pd.read_sql(sql=last_3_rows_query, con=sqliteConnection)
    df  

    expense_query = f"SELECT SUM(Amount) FROM {table_name}"
    st.text(f"Total expenses: {cursor.execute(expense_query).fetchone()[0]}")
    all_data = pd.read_sql(sql=f"SELECT * FROM {table_name}", con=sqliteConnection)
    st.markdown(get_table_download_link(all_data), unsafe_allow_html=True)

except Exception as e:
    print(f"Error: {e}")
    if passcode!=b'':
        st.text("Mind your own business👻👻👻")