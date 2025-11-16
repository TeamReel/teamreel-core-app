
def processUserAndSendEmailAndLog(user_data):
    # SRP violation - doing multiple things
    processed = user_data.upper()
    send_email(processed)  # Not defined - will cause issues
    log_activity(user_data)  # Not defined
    return processed
