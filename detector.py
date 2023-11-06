import fitz
import os

class PdfTypeError(Exception):
    def __init__(self, message="Pdf File is not identified"):
            self.message = message
            super().__init__(self.message)

def _get_data_from_pdf(url):
    data = ""
    pdf_document = fitz.open(url)
    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        text = page.get_text()
        data += text
        if page_number == 2:
            return data

    return data

pdf_file = "pdfs/invoice_600000008842433.pdf"

text = _get_data_from_pdf(pdf_file)

def _is_twitter_pdf(text):
    x_signal_words = ["Twitter", "Inc", "Michael", "Burstein", "Total", "INVOICE"]
    counter = 0
    for word in x_signal_words:
        if word in text:
            counter += 1

    return counter / len(x_signal_words)


def _is_facebook_pdf(text):
    facebook_signal_words = ["Type","Product","Receipt for","MediaBoost", "Campaigns", "Meta ads"]
    counter = 0
    for word in facebook_signal_words:
        if word in text:
            counter += 1

    return counter / len(facebook_signal_words)


def detector(pdf_file):
    text = _get_data_from_pdf(pdf_file)
    facebook_point = _is_facebook_pdf(text)
    twitter_point = _is_twitter_pdf(text)
    if facebook_point > twitter_point:
        return "facebook"
    else:
        return "twitter"

    raise PdfTypeError



if __name__ == "__main__":
    facebook_pdfs = [os.path.join("./facebookPdf", url) for url in os.listdir("./facebookPdf")]
    twitter_pdf = [os.path.join("./pdfs", url) for url in os.listdir("./pdfs")]
    files = facebook_pdfs + twitter_pdf

    for each in files:
        try:
            print(each, detector(each))
        except Exception as e:
            print(e, type(e))