import os

import fitz  # PyMuPDF
import re

class TwitterPdfParser:
    def __init__(self, url):
        self._url_type_checker(url)
        self.url = url
        self.data = self._get_data_from_pdf()
        self.text = ";".join(self._headers) + "\n"

    text = ""
    _headers = ["Campaign", "Code", "From", "To", "Total Amount", "Ads set", "Code", "Impressions", "price"]
    _pattern = r"(\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2},\s\d{4}\b)"

    def save(self, url):
        self._url_type_checker(url)
        with open(url, 'w') as file:
            file.write(self.text)

    def _url_type_checker(self, url):
        if not isinstance(url,str):
            raise TypeError("Url should be string")

    def _get_data_from_pdf(self):
        data = []
        pdf_document = fitz.open(self.url)
        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)
            text = page.get_text()
            data = data + text.split("\n")

        return data

    def get_total_price_index(self, array):
        array = [float(price[1:]) for price in array]
        max_index = 0
        i = 1
        while i < len(array):
            if array[i] > array[max_index]:
                max_index = i
            i += 1

        return max_index

    def build_csv(self):
        prices = self.get_prices()
        index = self.get_total_price_index(prices)
        total = None
        if index is not None:
            total = prices[index]
            prices.pop(index)

        listing_boosts_indexes = self.get_listing_boosts_indexes()

        date_indexes, end_time = self.get_dates_indexes_and_end_time()

        listing_boosts = []
        dates = []

        j = 0
        for index in listing_boosts_indexes:
            value = self.data[index]
            i = index
            while "#" not in self.data[i]:
                i += 1
            else:
                if i != index:
                    value += self.data[i]

            if date_indexes[j - 1][0] < index and date_indexes[j][0] > index:
                dates.append(date_indexes[j - 1][1])
            else:
                if j < len(date_indexes) - 1:
                    j += 1
                dates.append(date_indexes[j][1])

            listing_boosts.append(value)

        for i in range(len(listing_boosts)):
            id = self._base16_exctractor(listing_boosts[i])
            if id:
                id = id[0]
            else:
                id = None
            each_line = f"{listing_boosts[i]};{id};{dates[i]};{end_time};{total};{listing_boosts[i]};{id};{prices[i][1:]}" + "\n"
            self.text += each_line

    def get_dates_indexes_and_end_time(self):
        date_indexes = [(index, re.search(self._pattern, value).group(1)) for index, value in enumerate(self.data) if re.search(self._pattern, value)]
        date_indexes.pop(0)
        end_time = date_indexes[0][1]
        date_indexes.pop(0)

        return date_indexes, end_time

    def get_listing_boosts_indexes(self):
        listing_boosts_indexes = [index for index, value in enumerate(self.data) if "Listing Boost" in value]
        return listing_boosts_indexes
    def get_prices(self):
        prices = [price for price in self.data if "$" in price and len(price) > 1]
        return prices

    def _base16_exctractor(self, _str):
        return re.findall(r'\b[0-9a-fA-F]{20,}\b', _str)


folder = "./pdfs"
pdf_files = [os.path.join(folder,url) for url in os.listdir(folder)]
for each in pdf_files:
    obj = TwitterPdfParser(url=each)
    obj.build_csv()
    obj.save(each.replace(".pdf", ".csv"))

