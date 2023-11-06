import fitz
import re
import os


class FacebookPdfParser:
    def __init__(self, url:[str]):
        self._url_type_checker(url)
        self.url = url

    keyword = "Campaigns"
    text = ""
    #Campaign Name;Date From; Date  To;Total Amount;Ads set name ;  Impressions;Amount;
    _headers = ["Campaign", "Code", "From", "To", "Total Amount", "Ads set", "Code", "Impressions", "price"]

    def _get_data_from_pdf(self):
        data = []
        pdf_document = fitz.open(self.url)
        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)
            text = page.get_text()
            data = data + text.split("\n")

        return data

    def _is_price(self,possible_price):
        if "$" in possible_price:
            return True

        return False

    def _impressions_extractor(self, _str):
        data = None
        if isinstance(_str, list):
            data = _str
        else:
            data = _str.split()
        try:
            impressions_index = data.index("Impressions")
            return f"{data[impressions_index - 1]} {data[impressions_index]}"
        except Exception:
            return ""

    def _is_time(self, array):
        if "From" in array and "To" in array:
            return True

        return False

    def _corrector(self, data):
        start_index = self._search_campaings_index(data)
        data_length = len(data)
        i = start_index + 1
        _time = ""
        new_array = []
        listing_boost = ""

        while i < data_length - 1:
            if not data[i]:
                i += 1
                continue
            splited = data[i].split()
            if "Impressions" in splited and len(splited) != 2:
                impressions = self._impressions_extractor(splited)
                listing_boost = data[i]
                listing_boost = listing_boost.replace(impressions, "")
                new_array.append(listing_boost)
                new_array.append(impressions)
            else:
                new_array.append(data[i])

            i += 1

        return new_array

    def build_csv(self):
        self.text = ";".join(self._headers) +"\n"
        data = self._get_data_from_pdf()
        corrected_data = self._corrector(data)
        indexes = self._find_all_start_index(corrected_data)
        i = 1
        while i < len(indexes):
            start = indexes[i - 1]
            end = indexes[i]
            self.text += self._processor(corrected_data[start:end]) + "\n"
            i += 1


    def _processor(self, array):
        campaign = array[0]
        possible_codes = self._base16_exctractor(campaign) + [""]
        code = possible_codes[0]
        _from, _to = self._time_formatter(array[1])
        _total = array[2].replace("$", "")
        _starting = f"{campaign};{code};{_from};{_to};{_total}"
        text = ""
        i = 5
        while i < len(array):
            possible_ads_codes = self._base16_exctractor(array[i - 2]) + [""]
            _code = possible_ads_codes[0]
            text += f"{_starting};{array[i - 2]};{_code};{re.sub(r'Impressions?','', array[i-1])};{array[i].replace('$', '')}"
            i += 3

        return text


    def _base16_exctractor(self, _str):
        return re.findall(r'\b[0-9a-fA-F]{20,}\b', _str)



    def _time_formatter(self, _time):
        arr = _time.split("to")
        _to = arr[1]
        _from = arr[0].replace("From", "")

        return _from, _to

    def _find_all_start_index(self, array):
        i = 0
        indexes = []
        last_price_index = len(array)
        while i < len(array):
            if "From" in array[i] and "to" in array[i]:
                indexes.append(i - 1)

            if self._is_price(array[i]):

                last_price_index = i

            i += 1

        indexes.append(last_price_index + 1)

        return indexes

    def save(self, url):
        self._url_type_checker(url)

        with open(url, 'w') as file:
            file.write(self.text)

    def _url_type_checker(self, url):
        if not isinstance(url,str):
            raise TypeError("Url should be string")

    def _search_campaings_index(self, array):
        index = 0
        while index < len(array):
            if self.keyword in array[index]:
                return index
            index += 1

        return 0

if __name__ == "__main__":
    folder = "./facebookPdf"
    pdf_files = [os.path.join(folder, url) for url in os.listdir(folder)]
    print(pdf_files)
    for each in pdf_files:
        obj = FacebookPdfParser(url=each)
        obj.build_csv()
        obj.save(each.replace(".pdf", ".csv"))

