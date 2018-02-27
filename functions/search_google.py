from google import google


def search_google(query, num_page):
    """
    Search Google using the scraper https://github.com/abenassi/Google-Search-API
    Return the titles of the links and their descriptions.
    Other elements can be :
    name # The title of the link
    link # The external link
    google_link # The google link
    description # The description of the link
    cached # A link to the cached version of the page
    page # What page this result was on (When searching more than one page)
    index # What index on this page it was on
    """
    search_results = google.search(query, num_page)
    results = []
    for i in search_results:
        results.append(i.name + "\n" + i.description)
    return results


if __name__ == "__main__":

    print(search_google("Einstein", 4))
