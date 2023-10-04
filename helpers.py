import os
import requests
import sqlite3
import numpy as np

from flask import redirect, session, request
from functools import wraps
from typing import Any, List




def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# Functions ###############################################################

def database(db="database.db"):
    con = sqlite3.connect(db)
    cur = con.cursor()
    return con, cur


def split_dict(dct, sections):
    lst = sorted(list(dct.items()))
    split_lst = np.array_split(lst, sections)
    splitted = []
    for i in range(sections):
        sec_i = split_lst[i]
        splitted.append(dict(sec_i))
    return splitted


def stringify(list_name, string):
    list = request.args.getlist(list_name)
    arr = []
    for l in list:
        arr.append(string + l)
    stringified = "".join(arr)
    return list, stringified
        
    
def lookup(param):
    try:
        api_key = os.environ.get("API_KEY")
        api_id = os.environ.get("API_ID")
        response = requests.get(
            f"https://api.edamam.com/api/recipes/v2?type=public&app_id={api_id}&app_key={api_key}&q={param}")
        response.raise_for_status()
    except requests.RequestException:
        return None
    try:
        result = response.json()
        # count = result["count"]
        # next = result["_links"]["next"]["href"]
        hits_dict = result["hits"]
        recipes_list = []
        for index in hits_dict:
            link = index["_links"]["self"]["href"]  # Recipe's JSON link
            label = index["recipe"]["label"]
            image = index["recipe"]["image"]
            source = index["recipe"]["source"]
            url = index["recipe"]["url"]  # Source link
            dietLabels = list(index["recipe"]["dietLabels"])
            healthLabels = list(index["recipe"]["healthLabels"])
            ingredientLines = list(index["recipe"]["ingredientLines"])
            calories = index["recipe"]["calories"]
            totalTime = index["recipe"]["totalTime"]
            cuisineType = list(index["recipe"]["cuisineType"])
            dishType = list(index["recipe"]["dishType"])
            recipes_list.append(
                {
                    "link": link,
                    "label": label,
                    "image": image,
                    "source": source,
                    "url": url,
                    "dietLabels": dietLabels,
                    "healthLabels": healthLabels,
                    "ingredientLines": ingredientLines,
                    "calories": calories,
                    "totalTime": totalTime,
                    "cuisineType": cuisineType,
                    "dishType": dishType
                })
        return recipes_list  # , next, count
    except (KeyError, TypeError, ValueError):
        return None


def readable_list(seq: List[Any]) -> str:
    seq = [str(s) for s in seq]
    if len(seq) < 3:
        return ' and '.join(seq)
    return ', '.join(seq[:-1]) + ', and ' + seq[-1]


