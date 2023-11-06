import poplib
import threading
import time
import email
from email import policy
from email.parser import BytesParser
from config import SERVER, ADDRESS, PORT, PASSWORD
from logger import logger
import smtplib
from email.message import EmailMessage

# Server Configuration
pop_server = str(SERVER)
pop_port = int(PORT)  # or 995 for SSL
pop_username = str(ADDRESS)
pop_password = str(PASSWORD)

# SMTP settings
smtp_server =  str(SERVER)
smtp_port = 587  # or 465 for SSL 587
smtp_username = str(ADDRESS)
smtp_password = str(PASSWORD)


def pdf_downloader(data):
    try:
        response, lines, octets = data
        raw_email = b'\n'.join(lines)
        # Parse the raw email into a convenient object
        msg = BytesParser(policy=policy.default).parsebytes(raw_email)

        # Getting various email headers
        subject = msg['Subject']
        sender = msg['From']
        recipient = msg['To']

        if pop_username in recipient and pop_username in sender:
            raise Exception("you can't send message to yourself")

        if msg.is_multipart():
            for part in msg.iter_parts():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    if not filename:
                        continue
                    # Save the file or process it as you need
                    with open(filename, 'wb') as f:
                        f.write(part.get_payload(decode=True))

    except Exception as e:
        logger.error(f"error type:{str(type(e))}, error message:{str(e)}")

class POPService:
    def __init__(self, pop_server, pop_port, pop_username, pop_password):
        self.pop_server = pop_server
        self.pop_port = pop_port
        self.pop_username = pop_username
        self.pop_password = pop_password

    def _try_to_connect(self):
        logger.info(
            f"start connecting to server server:{self.pop_server}, port:{self.pop_port} username:{self.pop_username}")
        try:
            server = poplib.POP3_SSL(self.pop_server, self.pop_port)
            server.user(self.pop_username)
            server.pass_(self.pop_password)
            return server
        except Exception as e:
            raise ConnectionError(
                f"Could not connect to server: {e} server:{self.pop_server}, port:{self.pop_port} username:{self.pop_username}")

    def _try_reconnect_to_server(self):
        logger.info(
            f"start reconnecting to server server:{self.pop_server}, port:{self.pop_port} username:{self.pop_username}")
        for i in range(5):
            try:
                server = self._try_to_connect()
                return server
            except ConnectionError as e:
                logger.error(str(e))

        raise ConnectionError(
            f"Could not connect to server: {e} server:{self.pop_server}, port:{self.pop_port} username:{self.pop_username}")

    def _connect_to_server(self):
        # Connect and Authenticate
        try:
            server = self._try_to_connect()
            return server
        except Exception as e:
            logger.error(str(e))
            server = self._try_reconnect_to_server()

class EmailReceiver(POPService):
    def __init__(self, pop_server: str, pop_port: int, pop_username: str, pop_password: str):
        super().__init__(pop_server, int(pop_port), pop_username, pop_password)
        self.server = self._connect_to_server()
        self.server.set_debuglevel(1)

    _sender = None
    def _email_listener(self, callback, thread=False):
        messages_quantity = len(self.server.list()[1])
        index = 0
        while True:
           print("done")
           try:
               print("looping", index)
               index += 1
               self.quit()
               self.server = self._connect_to_server()

               if not self.server:
                   continue

               new_messages_quantity = len(self.server.list()[1])

               # Check if the count has increased
               if messages_quantity < new_messages_quantity:
                   for i in range(messages_quantity + 1, new_messages_quantity + 1):
                       # Fetch the last email (use your own logic to get the email you want)
                       if not thread:
                           callback(self.server.retr(i))
                       else:
                           t = threading.Thread(target=callback, args=(self.server.retr(i),))
                           t.start()

                   messages_quantity = new_messages_quantity

               time.sleep(2)  # sleep for 30 seconds
           except Exception as e:
               logger.error(f"error type:{str(type(e))}, error message:{str(e)}")

           time.sleep(2)  # sleep for 30 seconds

    def set_sender(self, class_instace):
        if not isinstance(class_instace, EmailSender):
            raise TypeError("class_instance should be a EmailSender class")

        self._sender = class_instace
    def listen_to_server(self, callback,thread=False):
        self._email_listener(thread=thread, callback=callback)

    def quit(self):
        try:
            self.server.quit()
        except poplib.error_proto as e:
            print("POP3 protocol error: ", e)

class SMTPService:
    def __init__(self, smtp_server, smtp_port, smtp_username, smtp_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port  # or 465 for SSL
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password

    def _try_to_reconnect_to_server(self):
        logger.info(
            f"start reconnecting to server server:{self.smtp_server}, port:{self.smtp_port} username:{self.smtp_username}")
        for i in range(5):
            try:
                server = self._try_to_connect()
                return server
            except ConnectionError as e:
                logger.error(str(e))

        raise ConnectionError(
            f"Could not connect to server: {e} server:{self.pop_server}, port:{self.pop_port} username:{self.pop_username}")

    def _try_to_connect_to_server(self):
        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.ehlo()  # Can be omitted
        server.starttls()  # For security
        server.ehlo()  # Can be omitted
        server.login(self.smtp_username, self.smtp_password)

        return server

    def connect_to_server(self):
        try:
            server = self._try_to_connect_to_server()
            return server
        except Exception as e:
            logger.error(f"Could not connect to server: {e} server:{self.smtp_server}, port:{self.smtp_port} username:{self.smtp_username}")
            return self._try_to_reconnect_to_server()

class EmailSender(SMTPService):
    def __init__(self, smtp_server, smtp_port, smtp_username, smtp_password):
        super().__init__(smtp_server, smtp_port, smtp_username, smtp_password)
        self.server = self.connect_to_server()

    def _send_message(self, msg):
        self.server.sendmail(msg['From'], [msg['To']] + msg["Cc"].split(", "), msg.as_string())
    def send_email(self, sender_email, receiver_email, cc_email, subject, body, files):
        msg = EmailMessage()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg['Cc'] = ', '.join(cc_email)
        msg.set_content(body)
        for file_path in files:
            file_name = file_path.split("/")[-1]
            with open(file_path, "rb") as f:
                file_data = f.read()
                file_type = "application/octet-stream"  # General binary file type; you can be more specific
                msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

        self._send_message(msg)

    def quit(self):
        self.server.quit()


# if __name__ == "__main__":
#     EmailSenderInstance = EmailSender(smtp_server=smtp_server, smtp_port=smtp_port, smtp_username=smtp_username,smtp_password=smtp_password)
#     EmailReceiverInstance = EmailReceiver(pop_server=pop_server, pop_port=pop_port, pop_username=pop_username, pop_password=pop_password)
#     EmailReceiverInstance.set_sender(EmailSenderInstance)
#     EmailReceiverInstance.listen_to_server(callback=callback,thread=True)