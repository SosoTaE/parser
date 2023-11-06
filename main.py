import os
import fitz  # PyMuPDF
import re

class TwitterPdfParser:
    def __init__(self, url):
        self._url_type_checker(url)
        self.url = url
        self.data = self._get_data_from_pdf()
        self._pdf_structure_corrector()
        self.text = ";".join(self._headers) + "\n"

    text = ""
    _headers = ["Campaign", "Code", "From", "To", "Total Amount", "Ads set", "Code", "price"]
    _pattern = r"(\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2},\s\d{4}\b)"

    def save(self, url):
        self._url_type_checker(url)
        with open(url, 'w') as file:
            file.write(self.text)

    def _url_type_checker(self, url):
        if not isinstance(url,str):
            raise TypeError("Url should be string")

    def _pdf_structure_corrector(self):
        i = self._get_start_point_index()
        if i is None:
            i = 0
        while i < len(self.data):
            if self._is_price(self.data[i - 1]) and self._is_price(self.data[i]):
                i += 1
                continue
            elif self._is_price(self.data[i - 1]) and not re.search(self._pattern, self.data[i]):
                j = i + 1;
                while j < len(self.data):
                    date = re.search(self._pattern, self.data[j])
                    if date:
                        dt = date.group(1)
                        self.data.insert(i,dt)
                        break
                    j += 1
            i += 1



    def _get_data_from_pdf(self):
        data = []
        pdf_document = fitz.open(self.url)
        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)
            text = page.get_text()
            data = data + text.split("\n")

        return data

    def get_total_price_index(self, array):
        array = [float(price[1:].replace(",", "")) for price in array]
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

        j = 1
        for index in listing_boosts_indexes:
            value = self.data[index]
            i = index
            while "#" not in self.data[i]:
                i += 1
            else:
                if i != index:
                    value += self.data[i]

            if date_indexes[j][0] >= index:
                dates.append(date_indexes[j - 1][1])
            elif date_indexes[j][0] < index and j == len(date_indexes) - 1:
                dates.append(date_indexes[j][1])
            else:
                j += 1
                dates.append(date_indexes[j - 1][1])

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

    def _get_start_point_index(self):
        i = 0
        while i < len(self.data):
            if "(USD" in self.data[i]:
                return i

            i += 1

    def get_listing_boosts_indexes(self):
        listing_boosts_indexes = []
        start = self._get_start_point_index() + 1
        if start is None:
            start = 0

        for index, value in enumerate(self.data):
            if index <= start:
                continue

            if not value:
                continue

            if self._is_price(value):
                continue

            if re.search(self._pattern, value):
                continue

            if "#" in value:
                continue

            if "Total" in value:
                continue

            listing_boosts_indexes.append(index)

        return listing_boosts_indexes
    def get_prices(self):
        prices = [price for price in self.data if "$" in price and len(price) > 1]
        return prices

    def _is_price(self,possible_price):
        if "$" in possible_price:
            return True

        return False

    def _base16_exctractor(self, _str):
        return re.findall(r'\b[0-9a-fA-F]{20,}\b', _str)


folder = "./pdfs"
pdf_files = [os.path.join(folder,url) for url in os.listdir(folder)]
# pdf_files = ["./pdfs/invoice_600000008847584.pdf"]
print(pdf_files)
for each in pdf_files:
    try:
        print(each)
        obj = TwitterPdfParser(url=each)
        obj.build_csv()
        obj.save(each.replace(".pdf", ".csv"))
    except Exception as e:
        print(e, type(e))

