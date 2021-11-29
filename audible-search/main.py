# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings
import audible

USERNAME = "furbyhaxx@gmail.com"
PASSWORD = "4FK.studio$"

def audible_register():

    # Authorize and register in one step
    auth = audible.Authenticator.from_login(
        USERNAME,
        PASSWORD,
        locale="de",
        with_username=False
    )

    # Save credendtials to file
    auth.to_file("./audible.auth")

def audible_use_auth():
    pass

def audible_categories():
    auth = audible.Authenticator.from_file("./audible.auth")

    with audible.Client(auth=auth) as client:
        resp = client.get(
            "1.0/catalog/categories",
            num_results=1000,
            params={
                "categories_num_levels": 3,
                # "response_groups": (
                #     # "contributors, media, price, reviews, product_attrs, "
                #     # "product_extended_attrs, product_desc, product_plan_details, "
                #     # "product_plans, rating, sample, sku, series, ws4v, origin, "
                #     # "relationships, review_attrs, categories, badge_types, "
                #     # "category_ladders, claim_code_url, is_downloaded, pdf_url, "
                #     # "is_returnable, origin_asin, percent_complete, provided_review"
                # )
            }
        )

        print(resp)

def audible_read_library():
    auth = audible.Authenticator.from_file("./audible.auth")

    with audible.Client(auth=auth) as client:
        library = client.get(
            "1.0/catalog/products1",
            num_results=1000,
            params={
                # "categories_num_levels": 3,
                # "response_groups": (
                #     # "contributors, media, price, reviews, product_attrs, "
                #     # "product_extended_attrs, product_desc, product_plan_details, "
                #     # "product_plans, rating, sample, sku, series, ws4v, origin, "
                #     # "relationships, review_attrs, categories, badge_types, "
                #     # "category_ladders, claim_code_url, is_downloaded, pdf_url, "
                #     # "is_returnable, origin_asin, percent_complete, provided_review"
                # )
            }
        )
        for book in library["items"]:
            print(book)

def search(q="", author=None, title=None):
    url = "https://www.audible.de/search?keywords="

    if title is not None:
        url += "&title=" + title
    if author is not None:
        url += "&author_author=" + author

        print(url)

    #&author_author=Neal+Stephenson&narrator=&publisher=

    from bs4 import BeautifulSoup
    import requests

    page = requests.get(url)

    if page.status_code == 200:
        content = page.content

        soup = BeautifulSoup(content, 'html.parser')

        num_results = soup.find("span", {"class": "resultsSummarySubheading"})

        for f in num_results.text.split(" "):
            if f.isnumeric():
                print(f'{ f } Ergebnisse')

        items = soup.findAll("li", {"class": "productListItem"})
        #bc-list-item

        print(items)






        # url https://www.audible.de/search
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # search(title="corvus", author="Neal+Stephenson")
    audible_read_library()
    # from audiblesearch.audiblesearch import AudibleMetadata
    # search = AudibleMetadata()
    #
    # results = search.search(q="Ich bin viele")
    #
    # print(results)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
