import fitz, os, re

pdf_file = "pdfs/invoice_600000008826766.pdf"
_headers = ["Campaign", "Code", "Date", "price"]
pattern = r"(\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2},\s\d{4}\b)"
pdf_document = fitz.open(pdf_file)
def extract_text_with_coords(pdf_path):
    data = []

    pdf_document = fitz.open(pdf_path)

    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        text = page.get_text()
        print(text)
        data = data + text.split("\n")


    return data


def search_total_index(array):
    array = [float(price[1:]) for price in array]
    max_index = 0
    i = 1
    while i < len(array):
        if array[i] > array[max_index]:
            max_index = i
        i += 1

    return max_index


data = extract_text_with_coords(pdf_file)

prices = [price for price in data if "$" in price and len(price) > 1]
index = search_total_index(prices)
total = None
if index is not None:
    total = prices[index]
    prices.pop(index)
listing_boosts_indexes = [max(0, index - 1) for index, value in enumerate(data) if "#" in value]
date_indexes = [(index, re.search(pattern, value).group(1)) for index, value in enumerate(data) if re.search(pattern, value)]
date_indexes.pop(0)
end_time = date_indexes[0][1]
date_indexes.pop(0)
listing_boosts = []
dates = []

j = 1
for index, each in enumerate(data):
    value = data[index]
    i = index
    while "#" not in data[i]:
        i += 1
    else:
        if i != index:
            value += data[i]

    if date_indexes[j - 1][0] < index and date_indexes[j][0] > index:
        dates.append(date_indexes[j - 1][1])
    else:
        if j < len(date_indexes) - 1:
            j += 1
        dates.append(date_indexes[j][1])

    listing_boosts.append(value)

_headers = ["Campaign", "Code", "From", "To", "Total Amount", "Ads set", "Code", "price"]

def _base16_exctractor(_str):
    return re.findall(r'\b[0-9a-fA-F]{20,}\b', _str)

text = ""
#



splited = pdf_file.split(".")
splited.pop()
name = "".join(splited) + ".csv"
with open(name, "w") as file:
    headers_text = ";".join(_headers)
    text = "\n".join([headers_text,text])
    file.write(text)


def callback(data):
    response, lines, octets = data
    raw_email = b'\n'.join(lines)
    # Parse the raw email into a convenient object
    msg = BytesParser(policy=policy.default).parsebytes(raw_email)

    # Getting various email headers
    subject = msg['Subject']
    sender = msg['From']
    recipient = msg['To']

    print("we got a email")
    print(msg)

    if pop_username in recipient and pop_username in sender:
        raise Exception("you can't send message to yourself")

    attached_files = []

    # logger.info(f"Subject: {subject}")
    # logger.info(f"From: {sender}")
    # logger.info(f"To: {recipient}")

    if msg.is_multipart():
        for part in msg.iter_parts():
            if part.get_content_disposition() == 'attachment':
                filename = part.get_filename()
                if not filename:
                    continue
                # Save the file or process it as you need
                with open(filename, 'wb') as f:
                    f.write(part.get_payload(decode=True))

                try:
                    read_pdf_and_save_as_pdf(filename, filename)
                    attached_files.append(filename)
                except Exception as e:
                    print(str(e))
                    print(type(e))

    if attached_files:
        EmailSenderInstance.send_email(receiver_email=sender, sender_email=recipient, subject=subject, files=attached_files,
                            body="pdf file conveertor to pdf file")
