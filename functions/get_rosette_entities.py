
from rosette.api import API, DocumentParameters, RosetteException

text = """Voici le bourgmestre de Morlanwelz, Charles-Ferdinand Dupont"""


def rosette(text):
    """ Run the example """
    # Create an API instance
    api = API(user_key="c3a4cbadf2c7be90a768b0269282209b",
              service_url="https://api.rosette.com/rest/v1/")
    params = DocumentParameters()
    params["content"] = text
    params["genre"] = "social-media"
    liste = []
    try:
        result = api.entities(params)
        for i in result['entities']:
            liste.append(i['type'] + "||" +
                         i['normalized'] + "||" + i['mention'])
        return liste
    except RosetteException as exception:
        print(exception)


test = rosette(text)
print(test)
