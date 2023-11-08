from emailer import EmailReceiver, EmailSender
from config import *
from email import policy
from email.parser import BytesParser
from config import SERVER, ADDRESS, PORT, PASSWORD
from detector import parsers_map, detector, PdfTypeError

pop_server = str(SERVER)
pop_port = int(PORT)  # or 995 for SSL
pop_username = str(ADDRESS)
pop_password = str(PASSWORD)

# SMTP settings
smtp_server = str(SERVER)
smtp_port = 587  # or 465 for SSL 587
smtp_username = str(ADDRESS)
smtp_password = str(PASSWORD)


def callback(data):
    response, lines, octets = data
    raw_email = b'\n'.join(lines)
    # Parse the raw email into a convenient object
    msg = BytesParser(policy=policy.default).parsebytes(raw_email)

    # Getting various email headers
    subject = msg['Subject']
    sender = msg['From']
    recipient = msg['To']
    cc_recipients = msg['Cc']
    if isinstance(cc_recipients, str):
        cc_recipients = [cc_recipients]
    elif cc_recipients is None:
        cc_recipients = []


    try:
        _index = cc_recipients.index(pop_username)
        cc_recipients.pop(_index)
    except Exception as e:
        print(e, type(e))

    print("we got a email")

    if pop_username in recipient and pop_username in sender:
        raise Exception("you can't send message to yourself")

    attached_files = []
    messages = []

    if msg.is_multipart():
        for part in msg.iter_parts():
            if part.get_content_disposition() == 'attachment':
                filename = part.get_filename()
                if not filename:
                    continue

                if not filename.endswith(".pdf"):
                    messages.append(f"filename:{filename}, message:{'file should be pdf.'}")
                    continue

                received_filepath = os.path.join("received_files", filename)
                with open(received_filepath, 'wb') as f:
                    f.write(part.get_payload(decode=True))
                try:
                    filetype = detector(received_filepath)
                    obj = parsers_map.get(filetype)(received_filepath)
                    obj.build_csv()
                    splited_filename = filename.split(".")
                    splited_filename[-1] = "csv"
                    output_filename = ".".join(splited_filename)
                    output_filepath = os.path.join("results", output_filename)
                    obj.save(output_filepath)
                    attached_files.append(output_filepath)
                    messages.append(
                        f"filename:{filename}, message:{'converted successfully'}")
                except PdfTypeError as e:
                    messages.append(f"filename:{filename}, message:{'sorry, I can process only twitter and facebook pdf file. I did not detect that it is one of them, but if it is report about that error.'}")
                except Exception as e:
                    messages.append(f"filename:{filename}, message:{'sorry, there was an error'}")




        EmailSenderInstance.send_email(receiver_email=sender, sender_email=recipient, subject=subject,
                                       cc_email=cc_recipients, files=attached_files,
                                       body="\n".join(messages) if messages else "there was nothing to process")


if __name__ == "__main__":
    EmailSenderInstance = EmailSender(smtp_server=SERVER, smtp_port=smtp_port, smtp_username=smtp_username,
                                      smtp_password=smtp_password)
    EmailReceiverInstance = EmailReceiver(pop_server=pop_server, pop_port=pop_port, pop_username=pop_username,
                                          pop_password=pop_password)
    EmailReceiverInstance.set_sender(EmailSenderInstance)
    EmailReceiverInstance.listen_to_server(callback=callback, thread=True)
