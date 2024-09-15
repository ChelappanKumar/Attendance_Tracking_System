import smtplib
from email.mime.text import MIMEText
import sqlite3
import time
import pandas as pd

# Function to send an email to one student
def send_email(to_email, student_name, percentage):
    sender_email = "t67284125@gmail.com"
    sender_password = "vwgpqzoefedbfgts"  # Use your app-specific password (16 characters without spaces)
    
    # Dynamically set the subject based on student name and attendance percentage
    subject = f"Attendance Alert for {student_name}: Your Current Attendance is {percentage}%"
    
    body = f"Dear {student_name},\n\nYour current attendance is {percentage}%. Please ensure you meet the required attendance threshold.\n\nRegards,\nKCT"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        print(f"Attempting to send email to {to_email} with subject: '{subject}'")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        print(f"Email successfully sent to {to_email}")
    except smtplib.SMTPAuthenticationError:
        print("Failed to authenticate with the email server. Check your email and password.")
    except smtplib.SMTPRecipientsRefused:
        print(f"Email address rejected: {to_email}. Check if the email is correct.")
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {str(e)}")

# Function to send emails to all students in the DataFrame
def send_bulk_emails(df):
    for index, row in df.iterrows():
        email = row.get('email')  # Adjusted to match the database column
        student_name = row.get('student_name')
        percentage = row.get('cumulative_percentage')  # Adjusted to match the database column

        # Validate email format
        if pd.isna(email) or not isinstance(email, str) or '@' not in email:
            print(f"Skipping invalid or missing email for {student_name}")
            continue
        
        if pd.isna(student_name) or pd.isna(percentage):
            print(f"Skipping row with missing data for {student_name}")
            continue

        send_email(email, student_name, percentage)

        # Add a delay to avoid Gmail rate limits
        time.sleep(2)  # Delay of 2 seconds between each email

# Function to fetch data from the SQLite database
def fetch_data_from_db():
    # Connect to SQLite database
    conn = sqlite3.connect('attendance.db')
    query = "SELECT admission_no, registration_no, student_name, attended_periods, conducted_periods, percentage, cumulative_attended, cumulative_conducted, cumulative_percentage, phone_number, email FROM attendance"
    
    # Read data from the database into a DataFrame
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Main function to fetch data and initiate email sending
def main():
    try:
        # Fetch data from the SQLite database
        df = fetch_data_from_db()
        print("Data fetched from database successfully.")
        
        # Start sending emails in bulk
        send_bulk_emails(df)
    
    except sqlite3.Error as e:
        print(f"An error occurred while fetching data from the database: {str(e)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Run the main function
if __name__ == "__main__":
    main()
