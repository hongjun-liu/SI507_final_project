#################################
##### Name: Hongjun Liu
##### Uniqname: hongjunl
#################################

from bs4 import BeautifulSoup
import requests
import json
import secret_data as secrets
import sqlite3
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd

CACHE_FILENAME = "final_project.json"
CACHE_DICT = {}
api_key = secrets.api_key


class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.

    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')

    parkcode: string
        the park code of a national site
    '''

    def __init__(self, cate="no category", name="no name", address="no address",
                 zip="no zipcode", phone="no phone", parkcode="no park"):
        self.category = cate
        self.name = name
        self.address = address
        self.zipcode = zip
        self.phone = phone
        self.parkcode = parkcode

    def info(self):
        return self.name + " (" + self.category + ")" + ": " + self.address + " " + self.zipcode


def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary

    Parameters
    ----------
    None

    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk

    Parameters
    ----------
    cache_dict: dict
        The dictionary to save

    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME, "w")
    fw.write(dumped_json_cache)
    fw.close()


def request_with_cache(url):
    ''' If URL in cache, retrieve the corresponding values from cache. Otherwise, connect to API again and retrieve from API.

    Parameters
    ----------
    url: string
        a URL

    Returns
    -------
    a string containing values of the URL from cache or from API
    '''
    cache_dict = open_cache()
    if url in cache_dict.keys():
        print("Using Cache")
        response = cache_dict[url]
    else:
        print("Fetching")
        response = requests.get(url).text  # need to append .text, otherwise, can't save a Response object to dict
        cache_dict[url] = response  # save all the text on the webpage as strings to cache_dict
        save_cache(cache_dict)
    return response


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    nps_base_url = "https://www.nps.gov"
    response = request_with_cache(nps_base_url)
    soup = BeautifulSoup(response, 'html.parser')

    state_link_dict = {}
    allstates = soup.find(class_="dropdown-menu SearchBar-keywordSearch").find_all('a')
    for i in allstates:
        state_name = i.text.strip()
        state_link = "https://www.nps.gov" + i.get('href')
        state_link_dict[state_name.lower()] = state_link

    return state_link_dict


def get_site_instance(site_url):
    '''Make an instances from a national site URL.

    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov

    Returns
    -------
    instance
        a national site instance
    '''
    global addressa
    global addressb
    global zipcode
    response = request_with_cache(site_url)
    soup = BeautifulSoup(response, 'html.parser')
    instance = NationalSite()
    instance.name = soup.find(class_="Hero-titleContainer clearfix").find("a").text.strip()
    instance.category = soup.find(class_="Hero-designationContainer").find("span").text.strip()
    search_foot = soup.find(id="ParkFooter")
    addresslist = search_foot.find_all("span")
    for i in addresslist:
        if i.find(itemprop="addressLocality") is not None:
            addressa = i.find(itemprop="addressLocality").text.strip()
        if i.find(itemprop="addressRegion") is not None:
            addressb = i.find(itemprop="addressRegion").text.strip()
        if i.find(itemprop="postalCode") is not None:
            zipcode = i.find(itemprop="postalCode").text.strip()

    instance.address = addressa + ", " + addressb
    instance.zipcode = zipcode
    link = site_url.split("/")
    instance.parkcode = link[3]
    search_foot = soup.find(id='ParkFooter')
    phonelist = search_foot.find_all('span', itemprop="telephone")
    instance.phone = phonelist[0].text.strip()

    return instance


def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.

    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov

    Returns
    -------
    list
        a list of national site instances
    '''
    response = request_with_cache(state_url)
    soup = BeautifulSoup(response, 'html.parser')
    park_list = list()
    search_div = soup.find_all('div', class_="col-md-9 col-sm-9 col-xs-12 table-cell list_left")
    for i in search_div:
        parklist = i.find_all("a")
        parkurl = "https://www.nps.gov" + parklist[0]["href"] + "index.htm"
        instance = get_site_instance(parkurl)
        park_list.append(instance)

    return park_list


def get_park_activities(site_object):
    '''Obtain API data from MapQuest API.

    Parameters
    ----------
    site_object: object
        an instance of a national site

    Returns
    -------
    list
        a converted API return from National park API
    '''

    endpoint_url = 'https://developer.nps.gov/api/v1/parks?'
    params = "parkCode=" + site_object.parkcode + "&api_key=" + api_key

    cache_dict = open_cache()
    if site_object.parkcode in cache_dict.keys():
        print("Using Cache")
        result = cache_dict[site_object.parkcode]
    else:
        print("Fetching")
        response = requests.get(endpoint_url + params)
        results = response.json()  # need to append .text, otherwise, can't save a Response object to dict
        cache_dict[site_object.parkcode] = results["data"][0][
            "activities"]  # save all the text on the webpage as strings to cache_dict
        result = results["data"][0]["activities"]
        save_cache(cache_dict)

    print("----------------------------------")
    print("Activities in the " + site_object.name + " National park")
    print("----------------------------------")

    num = 1
    for i in result:
        print("[" + str(num) + "] " + i["name"])
        num = num + 1

    return result

def joinbigtable():
    ''' Make a list of the big table which is joined by trails and parks

        Parameters
        ----------
        None

        Returns
        -------
        list
            list of tuples for the big table which is joined by trails and parks
            e.g. (10023165.0, 'Denali', 730.9104, 3.0, 3.304, 14644.994, 5.0, 'dena')
        '''
    connection = sqlite3.connect("parksandtrails.sqlite")
    cursor = connection.cursor()
    query = "SELECT trail_id, parks.ParkName, elevation_gain, difficulty_rating, popularity, leng, num_reviews, ParkCode" \
            " FROM parks JOIN trails ON trails.ParkName=parks.ParkName"
    result = cursor.execute(query).fetchall()
    connection.close()
    return result

def findalltrails(parkname):
    ''' find all information in all trails of this park

    Parameters
    ----------
    parkname: string
    the name where we want to find all information in all trails

    Returns
    -------
    list
    the list of tuples which meet the requirements of the park
    '''

    results=list()
    bigtable=joinbigtable()
    for i in bigtable:
        if(i[1]==parkname):
            results.append(i)
    return results

def drawbargraph(trails,n):
    ''' visualize all data requiring by trails

        Parameters
        ----------
        trails: list
        the list of tuples which meet the requirements of the park

        Returns
        -------
        None
    '''

    trailid=list()
    trailelevation_gain=list()
    traildifficulty_rating=list()
    trailpopularity=list()
    trailleng=list()
    for i in trails:
        trailid.append(str(i[0]))
        traildifficulty_rating.append(float(i[3]))
        trailelevation_gain.append(float(i[2]))
        trailpopularity.append(float(i[4]))
        trailleng.append(float(i[5]))

    if n==1:
        bar_data1 = go.Bar(x=trailid, y=trailelevation_gain)
        basic_layout1 = go.Layout(title="trails' elevation_gain comparison")
        fig1 = go.Figure(data=bar_data1, layout=basic_layout1)
        fig1.show()

    if n==2:
        bar_data2 = go.Bar(x=trailid, y=traildifficulty_rating)
        basic_layout2 = go.Layout(title="trails' difficulty_rating comparison")
        fig2 = go.Figure(data=bar_data2, layout=basic_layout2)
        fig2.show()

    if n==3:
        bar_data3 = go.Bar(x=trailid, y=trailpopularity)
        basic_layout3 = go.Layout(title="trails' popularity comparison")
        fig3 = go.Figure(data=bar_data3, layout=basic_layout3)
        fig3.show()

    if n==4:
        bar_data4 = go.Bar(x=trailid, y=trailleng)
        basic_layout4 = go.Layout(title="trails' length comparison")
        fig4 = go.Figure(data=bar_data4, layout=basic_layout4)
        fig4.show()

    # for i in range(len(trailid)):
    #     df = pd.DataFrame(dict(
    #         r=[trailelevation_gain[i],trailpopularity[i],traildifficulty_rating[i],trailleng[i]],
    #         theta=['trailelevation_gain','trailpopularity','traildifficulty_rating',
    #                'traillength']))
    #     fig = px.line_polar(df, r='r', theta='theta', line_close=True)
    #     fig.update_traces(fill='toself')
    #     fig.show()


if __name__ == "__main__":

    statesurl = build_state_url_dict()
    print('''Enter a state name (e.g. Alaska, alaska) or "exit"''')
    statename = input(":")
    temp = 0

    while True:
        while True:
            if statename == "exit":
                print("Bye!")
                temp = 1
                break

            try:
                intemp = 0
                stateurl = statesurl[statename.lower()]
                parklist = get_sites_for_state(stateurl)
                order = 0
                orderlist = list()
                print("----------------------------------")
                print("List of national sites in " + statename.lower())
                print("----------------------------------")
                for i in parklist:
                    order = order + 1
                    orderlist.append(order)
                    print("[" + str(order) + "] " + i.info())
                print("")

                while True:
                    print('''Choose the number for detail search or "exit" or "back"''')
                    number = input(":")
                    if number == "exit":
                        print("Bye!")
                        temp = 1
                        intemp = 1
                        break
                    if number == "back":
                        print('''Enter a state name (e.g. Alaska, alaska) or "exit"''')
                        statename = input(":")
                        break
                    try:
                        if int(number) in orderlist:
                            get_park_activities(parklist[int(number) - 1])
                            print("----------------------------------")
                            trails=findalltrails(parklist[int(number) - 1].name)
                            if(len(trails)==0):
                                print("Sorry. There is no data in this park!")
                            else:
                                while True:
                                    tem=0
                                    num=input("please enter a number(1,2,3,4) to see related trails information: ")
                                    if num=="exit":
                                        print("Bye!")
                                        tem=1
                                        intemp=1
                                        temp=1
                                        break
                                    if num=="back":
                                        break
                                    else:
                                        drawbargraph(trails,int(num))
                                if tem==1:
                                    break


                        else:
                            print("[Error] Invalid input")
                            print("")
                            print("----------------------------------")
                    except:
                        print("[Error] Invalid input")
                        print("")
                        print("----------------------------------")

                if intemp == 1:
                    break

            except:
                print('[ERROR] Enter proper state name')
                print('''\nEnter a state name (e.g. Alaska, alaska) or "exit"''')
                statename = input(":")

        if temp == 1:
            break