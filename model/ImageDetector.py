import time
import os, shutil

"""
def get_pest_prediction(*args):
    return 'hs'
def get_recommended_pesticide(*args):
    return ["fdsafdhgoas"]
"""
from .Recommend import get_recommended_pesticide
from .DetectPest import get_pest_prediction


def get_pesticide(user):
    user.is_processing = True
    pests = []

    # for image in something
    for image_path in os.listdir(os.path.join("temp", user.token)):
        pests.append(
            get_pest_prediction(
                os.path.join(os.path.join("temp", user.token), image_path)
            )
        )

    pesticide_pests = {}
    ####### Added by HK ############
    description = []
    ################################
    for pest in pests:
        pesticides, descriptions = get_recommended_pesticide(
            pest, user.history_of_purchases
        )
        pesticide_pests[pest] = pesticides
        description.append(descriptions)

    user.pesticide_pests = pesticide_pests
    user.pesticide_pests_descriptions = description
    user.is_processing = False
