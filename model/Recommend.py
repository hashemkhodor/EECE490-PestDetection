import pandas as pd
import numpy as np
from pprint import pprint
import json
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import linear_kernel
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import scale
from math import log2


def extract_relevant_pesticides(pests):
    # Extracting relavent pests:
    df_pests = pd.read_csv("model/pests_to_pesticides.csv")
    df_pests = df_pests.fillna(0)

    # Contains the pesticide names
    headers = list(df_pests.columns)

    dataset_pests = df_pests.iloc[:, :1].values

    RESHAPE_pests = lambda x: list(x)[0]
    dataset_pests = list(map(RESHAPE_pests, dataset_pests))

    # Reshape list
    pests_indices = dict()

    for i in range(len(dataset_pests)):
        pests_indices[dataset_pests[i]] = i

    def relevant_pesticides(pests: list[str], df_pests) -> list:
        for pest in pests:
            assert (
                pest in pests_indices
            ), "[ Server ] : pest {} not found in database".format(pest)
        results = {}
        for pest in pests:
            pest_index = pests_indices[pest]
            results[pest] = df_pests.columns[df_pests.iloc[pest_index] == 1].tolist()
        return results

    return relevant_pesticides(pests, df_pests)


def Recommend_Top_K_Pesticides(pesticides: list[str], user_history: dict, k: int):
    df_pesticides_main = pd.read_csv("model/pesticides.csv")

    # dropping columns
    columns_to_drop = [
        "number_targeted_pests",
        "price_oz",
        "perc_act",
        "oz_5acres",
        "price_5acres",
    ]
    df_pesticides = df_pesticides_main.drop(columns=columns_to_drop)

    headers = list(df_pesticides.columns)

    dataset_vectors = df_pesticides.iloc[
        :, 1:
    ].values  # here we are removing the name of pest

    dataset_pesticides = df_pesticides.iloc[:, :1].values
    # scale the vectors
    RESHAPE_pests = lambda x: list(x)[0]
    dataset_pesticides = list(map(RESHAPE_pests, dataset_pesticides))

    pesticides_indices = dict()

    for i in range(len(dataset_pesticides)):
        pesticides_indices[dataset_pesticides[i]] = i
    # print(df_pesticides)
    cosine_similarities = cosine_similarity(dataset_vectors, dataset_vectors)
    user_history = {
        dataset_pesticides[0]: 1,
        dataset_pesticides[2]: 23,
        dataset_pesticides[3]: 1,
    }
    user_pesticide_history = dict()

    def similarity_function(cos_sim: float, occurences: int):
        """The function for similarity"""

        return cos_sim * log2(occurences)

    def combine(LIST):
        """returns average of list"""
        return sum(LIST) / len(LIST)

    def get_sim_to_user_history(pesticide: str, user_history: dict):
        """returns the similarity between pesticide and user_history. Values between -1 and 1"""
        assert (
            pesticide in dataset_pesticides
        ), "[ SERVER ] : Pesticide {} is not valid".format(pesticide)
        pesticide_index = pesticides_indices[pesticide]
        SIMILARITIES = []
        for choice in user_history:
            choice_index = pesticides_indices[choice]
            sim = similarity_function(
                cosine_similarities[choice_index][pesticide_index], user_history[choice]
            )
            SIMILARITIES.append(sim)
        return combine(SIMILARITIES)

    def recommend_top_k_pesticides(pesticides: list[str], user_history: dict, k: int):
        # assert k<= len(pesticides) , "[SERVER] : k = {} is greater than size of pesticides = {}".format(k,len(pesticides))
        SIMILARITIES = [
            (i, get_sim_to_user_history(pesticides[i], user_history))
            for i in range(len(pesticides))
        ]
        SIMILARITIES.sort(key=lambda x: x[1], reverse=True)
        return [pesticides[entry[0]] for entry in SIMILARITIES[0:k]]

    return recommend_top_k_pesticides(pesticides, user_history, k)


import re


def shorten_sources(source):
    pattern = "([a-zA-Z0-9]*),[a-zA-Z0-9 \._,&]*([\(\)0-9]*)[a-zA-Z0-9 \._,&\(\)]*"
    link = source.split("https")
    PATTERNS = re.findall(pattern, source)
    return "{} {} ".format(PATTERNS[0][0], PATTERNS[0][1])


def display_pesticide_information(
    pesticide: str,
    headers=[
        "Pesticide",
        "price_5acres",
        "evmt_score_animals",
        "evmt_score_pollution",
        "effectiveness_score",
        "human_health",
        "number_targeted_pests",
        "source_evmt_eff",
        "source_eff_add",
    ],
):
    # Scaled features ######################################################################################################
    scale = {
        "0": "low",
        "0.5": "low-to-moderate",
        "1": "moderate",
        "1.5": "moderate-to-high",
        "2": "high",
    }
    scaled_headers = [
        "evmt_score_animals",
        "evmt_score_pollution",
        "human_health",
    ]
    scaled_headers_2 = ["effectiveness_score"]
    ########################################################################################################################
    # Sources features #####################################################################################################
    sources = ["source_evmt_eff", "source_eff_add"]

    ########################################################################################################################

    df = pd.read_csv("model/Pesticides_Full_Data.csv", encoding="latin1")
    df = df.fillna("NA")
    """ returns information about pesticide in dictionary format """

    main_headers = list(df.columns)

    if headers == []:
        headers = main_headers
    print(headers)
    diction = dict(
        zip(list(df.columns), range(len(main_headers)))
    )  # header to key value
    _headers_ = [(header, diction[header]) for header in headers]
    _headers_.sort(key=lambda x: x[1])
    _headers_ = dict(_headers_)

    header_descriptions = df.iloc[0].to_list()
    row = list(df[df["Pesticide"] == pesticide].values[0])

    ################### header to header description #####################
    _description_ = dict()
    for header in _headers_:
        _description_[header] = header_descriptions[_headers_[header]].split("\n")
    ######################################################################

    ################### header to values #################################
    sources_free = False
    for header in _headers_:
        if header in scaled_headers:
            _headers_[header] = scale[row[_headers_[header]]]
        elif header in sources:
            sources_free = False
        else:
            _headers_[header] = row[_headers_[header]]

    if True:
        # if data_eff_research ==1 : take source_eff_add
        if row[diction["data_eff_research"]] == "1":
            _headers_["source1"] = row[diction["source_eff_add"]]
        else:
            source_evmt_eff = row[diction["source_evmt_eff"]].split(" / ")
            source_eff_add = (
                []
                if row[diction["source_eff_add"]] == "NA"
                else row[diction["source_eff_add"]].split("\n\n")
            )
            for i in range(len(source_eff_add)):
                source_eff_add[i] = shorten_sources(source_eff_add[i])
            _headers_["source1"] = "\n".join(source_evmt_eff + source_eff_add)
            print(_headers_["source1"])
    if True:
        _headers_["source2"] = row[diction["source_evmt_eff"]]

    ######################################################################
    # return
    #     header -> header description
    #     header -> value
    return _headers_


def get_recommended_pesticide(pest, user_history):
    pesticides = extract_relevant_pesticides([pest])
    recommended_pesticides = Recommend_Top_K_Pesticides(
        pesticides[pest], user_history, len(pesticides[pest])
    )
    recommended_pesticides_information = dict(
        [
            (pesticide, display_pesticide_information(pesticide))
            for pesticide in recommended_pesticides
        ]
    )
    # _    display_pesticide_information()
    return recommended_pesticides, recommended_pesticides_information

    # return Recommend_Top_K_Pesticides(]
    #     pesticides[pest], user_history, len(pesticides[pest])
    # )

    # def load_datasets(name):
    #     df_pests = pd.read_csv(name)
    #     df_pests = df_pests.fillna(0)
    #     return df_pests

    # df_pests=load_datasets("/model/pests_to_pesticides.csv")
    # headers= list(df_pests.columns)
    # dataset_pests = df_pests.iloc[:,:1].values
    # RESHAPE_pests= lambda x : list(x)[0]
    # dataset_pests = list(map(RESHAPE_pests,dataset_pests))
    # pests_indices=dict()

    # for i in range(len(dataset_pests)):
    #     pests_indices[dataset_pests[i]]=i

    # def relevant_pesticides(pests:list[str],df_pests)-> list:
    #     for pest in pests:
    #         assert pest in pests_indices, "[ Server ] : pest {} not found in database".format(pest)
    #     results={}
    #     for pest in pests:
    #         pest_index=pests_indices[pest]
    #         results[pest]=df_pests.columns[df_pests.iloc[pest_index] == 1].tolist()
    #     return results

    # # get relevant pests
    # # get cosine similarities
    # #
    # pass
