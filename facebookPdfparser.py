import fitz

class FacebookPdfParser:
    def __init__(self, url:[str]):
        self._url_type_checker(url)
        self.url = url

    keyword = "Campaigns"

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

    def build_csv(self):
        data = self._get_data_from_pdf()
        start_index = self._search_campaings_index(data)
        data_length = len(data)
        i = start_index + 1
        _time = ""
        new_array = []
        listing_boost = ""
        text = ""

        while i < data_length - 1:
            if not data[i]:
                i += 1
                continue
            splited = data[i].split()

            if "From" in data[i + 1] and "To" in data[i + 1]:
                _time = data[i]
                listing_boost = data[i - 1]
                text = f"{listing_boost} {_time}"
                i += 2
                continue
            elif "Impressions" in splited and len(splited) != 2:
                impressions = self._impressions_extractor(splited)
                listing_boost = data[i]
                listing_boost = listing_boost.replace(impressions, "")
                # new_array.append(listing_boost)
                # new_array.append(impressions)
                print(1,text,f" {listing_boost} {impressions} {data[i + 1]}")
                i += 1
            else:
                if len(new_array)%3 == 0:
                    print(2,text," ".join(new_array))
                    new_array = []

                new_array.append(data[i])


            i += 1


        # for each in new_array:
        #     print(each)

            # j = i - 3
            # # each_line = []
            # while j < i:
            #     if not data[j]:
            #         data.pop(j)
            #         continue
            #
            #     j += 1
            # listing_boost = data[i - 3]
            # impressions = data[i - 2]
            # price = data[i - 1]
            #
            # if not self._is_price(price):
            #     if self._is_price(impressions):
            #         price = impressions
            #         impressions = self._impressions_extractor(listing_boost)
            #         listing_boost.replace(impressions, "")
            #     elif self._is_time(impressions):
            #         _time = impressions
            #         i += 3
            #         continue
            #
            # if _time and listing_boost and impressions and price:
            #     print(_time,listing_boost,impressions,price)
            #
            # i += 3






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



pdf_file = "2023-09-14T16-46 Transaction #6491719864274042-13296500.pdf"
obj = FacebookPdfParser(pdf_file)
obj.build_csv()