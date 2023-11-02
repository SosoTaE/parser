import string

csv_file = "pdfs/2023-08-31--2023-09-30_Invoice_Summary.csv"


class FacebookCsvParser:
    def __init__(self, url):
        if not url:
            return

        text = self._open_file(url)
        self._build()


    _result = ""
    headers = ["Date", "Transaction ID"]

    def _open_file(self, url):
        with open(url, "r") as file:
            self.text = file.read()

    def _into_array(self):
        return self.text.split("\n")

    def _search_headers_index(self, array):
        i = 0
        while i < len(array):
             if self.headers[0] in array[i] and self.headers[1] in array[i]:
                 return i
             i += 1

    def _build(self):
        array = self._into_array()
        header_index = self._search_headers_index(array)
        text = ""
        # for each in array[:header_index]:
        #     text += each + '\n'

        for each in array:
            each_line = None
            if "Total" in each:
                each = [*each]
                i = 0
                while i < len(each):
                   try:
                       if each[i] == "," and each[i - 1] in string.digits and each[i + 1] in string.digits:
                           each[i] = ","
                       elif each[i] == ",":
                           each[i] = ";"

                   except Exception as e:
                       print(str(e))

                   i += 1

                each_line = ''.join(each).rsplit(";")
                print(each_line)
            else:
                each_line = each.replace(",", ";").rsplit(";")

            i = 0
            while i < len(each_line):
                if each_line[i] == "":
                    each_line.pop(i)
                    # i -= 1
                else:
                    i += 1

            text += ";".join(each_line) + "\n"

        self._result = text

    def save(self,url):
        with open(url,"w") as file:
            file.write(self._result)

    def get_result(self):
        return self._result



obj = FacebookCsvParser(csv_file)
obj.save(csv_file.replace(".","(1)."))