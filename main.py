import fitz  # PyMuPDF
import re

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
        # print(text)
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
for each in data:
    print(each)
# prices = [price for price in data if "$" in price and len(price) > 1]
# index = search_total_index(prices)
# total = None
# if index is not None:
#     total = prices[index]
#     prices.pop(index)
listing_boosts_indexes = [index for index, value in enumerate(data) if "Listing Boost" in value]
date_indexes = [(index, re.search(pattern, value).group(1)) for index, value in enumerate(data) if re.search(pattern, value)]


for each in date_indexes:
    print(each)


# listing_boosts = []
#
# for index in listing_boosts_indexes:
#     value = data[index]
#     i = index
#     while "#" not in data[i]:
#         i += 1
#     else:
#         if i != index:
#             value += data[i]
#
#     listing_boosts.append(value)
#
#
# print(len(listing_boosts))
# print(len(prices))
#
# headers = ["listing boost", "price"]
#
# text = ""
#
# for i in range(len(listing_boosts)):
#     text += f"{listing_boosts[i]};{prices[i][1:]}" + "\n"
#
#
# splited = pdf_file.split(".")
# splited.pop()
# name = "".join(splited) + ".csv"
# with open(name, "w") as file:
#     headers_text = ";".join(headers)
#     text = "\n".join([headers_text,text])
#     file.write(text)