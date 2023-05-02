'''
Author: David Hammond
Date: 4/28/2023
Data: Meteorite_Landings.csv meteorite landings recorded by NASA

project will import data about meteorites gathered by NASA and create an interactive website
users can use to sort data by year, class, and name. Website will include a map of where the
meteorites were found, infographics, and information about the meteors
'''

# import packages for data managment, graph creation, map creation, and website creation
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk

# Show all columns and text in pandas data frames
pd.set_option('display.max_columns', 1000)
pd.set_option('display.max_rows', 1000)
pd.set_option('display.width', 1000)


def getData():
    '''Function will read a CSV file and return the data as a data frame'''
    meteordf = pd.read_csv("Meteorite_Landings.csv", encoding="latin-1")
    return meteordf


def getMeteorsPerYear(meteordf, years = [1970, 860]):
    '''Function will take in data frame and values for years and return the number of meteors
    that fell in selected years
    @meteordf: data frame of meteors, where they fell, when they fell, and class
    @years: List of Years desired by the user
    '''
    yearsdf = meteordf.sort_values(by = ["year"])
    yearsCountdf = yearsdf.groupby("year")['id'].count()
    yearsOfInterest = yearsCountdf.loc[years]
    return yearsOfInterest


def sortClassAndFindValues(meteordf, recclass="Acapulcoite"):
    '''Function will take in data frame of meteors, group the values by their classification
    and find the mean weights by group as well as the overall mean weight and mean landing spot
    @meteordf: data frames of meteors, class, weight, landing lattitude, and landing longitude
    '''
    # Group by class, find mean values, and counts of each group
    grouped = meteordf.dropna().groupby('recclass')
    means = grouped.mean(numeric_only=True)
    count = grouped["name"].count().loc[recclass]
    maxgroups = grouped["mass (g)"].max()
    mingroups = grouped["mass (g)"].min()

    # Convert from scientific notation to numeric floats
    pd.options.display.float_format = '{:.0f}'.format
    meanweightclass = means["mass (g)"].apply(pd.to_numeric).loc[recclass]
    maxweight = maxgroups.apply(pd.to_numeric).loc[recclass]
    minweight = mingroups.apply(pd.to_numeric).loc[recclass]

    # Find weights and average landing site of all meteors
    aveweight = pd.Series.mean(meteordf["mass (g)"])
    avelat = pd.Series.mean(meteordf["reclat"])
    avelong = pd.Series.mean(meteordf["reclong"])
    return aveweight, avelat, avelong, meanweightclass, count, maxweight, minweight


def sortName(meteordf, ):
    '''Function will take data frame and return a dictionary. The dictionary will have a
    letter of the alphabet as a key and its values willl be every meteorite name that starts
    with that letter
    @meteordf: data frame of meteors that includes meteor name, year, location fallen, and class
    '''
    # create new column of first leters
    meteordf["firstLetter"] = meteordf["name"].str[0].str.upper()

    # group by first letter
    grouped = meteordf.groupby('firstLetter')

    # use grouped data frame to create dictionary with letter as key and list of names as value
    namesdict = {key: value['name'].tolist() for key, value in grouped}
    return namesdict


def homePage():
    st.title("Meteorites That Hit Earth")
    st.header("Welcome to my CS 230 Project")
    image = open('meteorite.png', 'rb').read()
    st.image(image)
    st.write("Project by David Hammond")
    st.write("Data collected by NASA")
    return


def mapPage(meteordf):
    meteorslayer = pdk.Layer(
        'ScatterplotLayer',
        data=meteordf.dropna(),
        get_position=['reclong', 'reclat'],
        get_color=[255, 0, 0],
        get_radius=10000,
        pickable=True,
    )
    map = pdk.Deck(layers=meteorslayer, tooltip = {"html": "<b>Meteor Name:</b> {name}<br/><b>Classification:</b> {recclass}<br/><b>Mass:</b> {mass (g)}</br/><b>Latitude:</b> {reclat}<br/><b>Longitude:</b> {reclong}"})
    st.title("Meteor Map")
    st.subheader("Each dot on the map below is a location a meteorite was found. Hover your mouse over a dot to see more about that meteorite!")
    st.pydeck_chart(map)
    return


def meteorYearsPage(meteorsdf):
    '''Page will allow user to sort meteorites by year discovered and output the amount that
    were found that year and a pie chart showing the proportion of each year selected
    @meteordf: data frame of meteorites, names, landing sites, years found, and masses
    '''
    # Title
    st.title("Meteorites Sorted by Year")
    st.subheader("On this page enter a set of years to learn how many meteorites were discovered during that year")

    # Get years user wants to analyze
    yearsInput = st.multiselect('Please select which years you would like to learn about', meteorsdf["year"].dropna().drop_duplicates().sort_values())

    # Find and output years of interest using previously defined function
    yearsOfInterest = getMeteorsPerYear(meteorsdf, yearsInput)

    # Create Pie Chart
    pie, ax = plt.subplots()
    ax.pie(yearsOfInterest, labels=yearsOfInterest.index)
    ax.set_title('Distribution by Year Selected')
    st.pyplot(pie)

    #Create table showing years and number of meteorites that hit earth
    st.write("Year, Number of meteorites discovered on Earth")
    st.write(yearsOfInterest)
    return


def classificationPage(meteorsdf):
    '''Page will allow users to pick a classification of meteorite and output the meteorite
    class's class name, the average mass of the class, the number of that class that have
    been discovered, the largest and smallest of that class that has been found, and whether
    that class is above average weight or below
    @meteordf: data frame of meteorites, names, landing sites, years found, and masses
    '''
    # Title
    st.title("Meteorites Sorted By Class")
    st.subheader("On this page select a classification of meteorites to learn how they relate to the average meteorite")

    # Gather desired class
    classInput = st.selectbox('Classifications of meteorites', meteorsdf["recclass"].dropna().drop_duplicates())

    # Compute and output average mass and the number of meteorites from that class
    aveweight, avelat, avelong, classOfInterest, count, maxweight, minweight = sortClassAndFindValues(meteorsdf, classInput)
    st.write("Meteorite Class:", classInput)
    st.write("Average Mass:", classOfInterest, "grams")
    st.write("Count:", count)
    st.write("Heaviest Recorded Meteor From Class", maxweight)
    st.write("Lightest Recorded Meteor From Class", minweight)

    # Tell user if their selected class is typically heavier or lighter than average
    if classOfInterest > aveweight:
        st.write(classInput, 'on average have been heavier than the average meteorite which weighs', aveweight, 'grams')
    elif classOfInterest < aveweight:
        st.write(classInput, 'on average have been less heavy than the average meteorite which weighs', aveweight,
                 'grams')
    return


def namepage(meteordf):
    '''Page will allow user to sort meteor data by their names. Page will show the letter,
    How many meteorites have been named starting with that letter, and a bar graph depicting
    how many meteorites have been named for each letters
    @meteordf: data frame of meteorites, names, landing sites, years found, and masses
    '''
    # title and opening text
    st.title("Meteorites Sorted by Their Names")
    st.subheader(
        "On this page you can find the number of meteorites whose names start with a certain letter and a lits of those meteorites")

    # create dictionary of letters and their names and take inputs
    namesDict = sortName(meteordf)
    menu = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
            'V', 'W', 'X', 'Y', 'Z']
    letterLst = st.multiselect("Select a Letter", menu)

    # find counts for each letter
    lettercountsdict = {}
    for letter in letterLst:
        st.write(letter, ":", len(namesDict[letter]))
        lettercountsdict[letter] = len(namesDict[letter])

    alphabetical = st.checkbox("Display bar chart alphabetically?")

    # sort letterscountdict alphabetically to ensure bar chart appears in alphabetical order
    if alphabetical:
        sortedKeys = sorted(lettercountsdict.keys())
        sortedlettercountsdict = {}
        for key in sortedKeys:
            sortedlettercountsdict[key] = lettercountsdict[key]
    else:
        sortedlettercountsdict = lettercountsdict

    # create bar chart showing how many meteorites started with each letter selected
    bar, ax = plt.subplots()
    ax.bar(list(sortedlettercountsdict.keys()), list(sortedlettercountsdict.values()))
    ax.set_title('Number of Meteorites per Letter')
    ax.set_xlabel('Letter')
    ax.set_ylabel('Number of Meteorites')
    st.pyplot(bar)

    # print out all names selected beneath their letter
    for letter in letterLst:
        st.write(letter)
        for name in namesDict[letter]:
            st.write(name)
    return


def nav():
    '''Function will create sidebar that allows user to navigate between pages. Function will
    Output different session_state depending on what the user clicks'''
    session_state = st.session_state

    # Open session state
    if 'page' not in session_state:
        session_state['page'] = 'home'

    # Create a menu that allows the user to navigate between the pages
    menu = ['Home', 'Map', 'Year', 'Classification', 'Names']
    navigation = st.sidebar.selectbox('Select a page', menu)

    # Update the session state based on the user's selection
    if navigation == 'Home':
        session_state['page'] = 'Home'
    elif navigation == 'Year':
        session_state['page'] = 'Year'
    elif navigation == 'Map':
        session_state['page'] = 'Map'
    elif navigation == 'Classification':
        session_state['page'] = 'Classification'
    elif navigation == 'Names':
        session_state['page'] = 'Names'
    return session_state, menu


def main():
    session_state, menu = nav()
    meteordf = getData()
    if session_state['page'] == 'Home' or session_state['page'] not in menu:
        homePage()
    elif session_state['page'] == 'Year':
        meteorYearsPage(meteordf)
    elif session_state['page'] == 'Map':
        mapPage(meteordf)
    elif session_state['page'] == 'Classification':
        classificationPage(meteordf)
    elif session_state['page'] == 'Names':
        namepage(meteordf)
    return

main()