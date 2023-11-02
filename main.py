import fitz  # PyMuPDF

pdf_file = "pdfs/2023-10-17T06-28 Transaction #6687598381352852-13529895.pdf"

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
listing_boosts_indexes = [index for index, value in enumerate(data) if "Listing Boost" in value]
listing_boosts = []

for index in listing_boosts_indexes:
    value = data[index]
    i = index
    while "#" not in data[i]:
        i += 1
    else:
        if i != index:
            value += data[i]

    listing_boosts.append(value)


print(len(listing_boosts))
print(len(prices))

headers = ["listing boost", "price"]

text = ""

for i in range(len(listing_boosts)):
    text += f"{listing_boosts[i]};{prices[i][1:]}" + "\n"

# print(f"Total: {total}")

splited = pdf_file.split(".")
splited.pop()
name = "".join(splited) + ".csv"
with open(name, "w") as file:
    headers_text = ";".join(headers)
    text = "\n".join([headers_text,text])
    file.write(text)