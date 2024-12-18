import pandas as pd
import numpy as np
import streamlit as st
import joblib

st.title("D1 College Baseball Stuff Plus Search Tool")

st.markdown("Welcome to my Stuff+ search tool! In this app, you can search the results of the model, evaluate the Stuff+ of custom metrics, or attach a TrackMan CSV to calculate Stuff+ of a new set of pitches")

st.subheader("Search Results")

st.markdown("Enter the information of a pitcher you would like to search. Enter the name in the form: Last, First. Results shown will be calculated from all pitches thrown by your pitcher on a TrackMan during the 2024 college baseball season. If your pitcher did not pitch in 2024, or did not pitch at a stadium with TrackMan, he will not appear in the dataset. If two pitchers have the same name, a dropdown will appear that allows you to filter by the team your pitcher plays for.")

st.markdown("AdjustedVAA and Adjusted HAA are metrics used in the Stuff+ calculation to control for release point. For AdjustedVAA, 0 is the average VAA for the release height, negative is steeper than average, and positive is flatter than average. Similarly for AdjustedHAA, 0 is the average HAA for the horizontal release point, negative is sharper towards right handed hitters, and positive is sharper towards left handed hitters.")

fb_stuffplus = pd.read_csv("stuff_plus_fb.csv").set_index(['Pitcher', 'PitcherTeam', 'TaggedPitchType'])
bb_stuffplus = pd.read_csv("stuff_plus_bb.csv").set_index(['Pitcher', 'PitcherTeam', 'TaggedPitchType'])
os_stuffplus = pd.read_csv("stuff_plus_os.csv").set_index(['Pitcher', 'PitcherTeam', 'TaggedPitchType'])

pitcher_name = st.text_input("Pitcher Name:") 
if pitcher_name:
    try:
        result = pd.concat([fb_stuffplus.loc[pitcher_name], bb_stuffplus.loc[pitcher_name], os_stuffplus.loc[pitcher_name]])
        teams = pd.Series([team for team, pitch in result.index]).unique()
        if teams.size > 1:
            team = st.selectbox("Team", teams)
            st.dataframe(result.loc[team])
        else:
            st.dataframe(result)
    except KeyError:
        st.markdown("Name not found in dataset. Make sure name is written in 'Last, First' format, and that your pitcher threw pitches on TrackMan during games in the 2024 season")

st.subheader("Custom Metrics")

st.markdown("""This section allows you to input custom metrics to the Stuff+ model. This is best used to evaluate a new pitch or to calculate Stuff+ of a pitcher not in the 2024 dataset. Here are a few notes to follow to ensure the calculation runs correctly:
1. For a 4-Seam Fastball, choose Fastball. For a 2-Seam Fastball, choose Sinker. I lumped these terms to simplify the classification. If the pitch is in between or you are unsure of which one to choose, it does not matter. The calculation will be the same.
2. Input Release Height, Release Side, and Extension as decimal numbers, in feet. 1 inch = 0.833 feet.
3. IVB - Induced Vertical Break, HB - Horizontal Break, VAA - Vertical Approach Angle, HAA - Horizontal Approach Angle
4. VAA should be a negative number
5. Using readings from other systems, such as Yakkertech, Rapsodo, or portable Trackman, will not produce the intended results. All of the pitches in the dataset I used were captured with stadium TrackMan, so inputting pitches captured on stadium TrackMan will produce the most accurate calculations. Portable TrackMan is the next best option if no stadium TrackMan data is available.

If your pitch was a Fastball or Sinker, you don't have to fill out any of the primary fastball information, so click 'Calculate'. The primary fastball information allows the model to take into account difference in break and velo when evaluating breaking balls and offspeed pitches. One more note - if the pitcher's primary fastball is a Cutter, it will be treated as a fastball. If not, it will be treated as a breaking ball. This allows for cutters to be fairly quantified based on how the pitcher uses it in his arsenal.
""")


fb_model = joblib.load("FB_model.pkl")
bb_model = joblib.load("BB_model.pkl")
os_model = joblib.load("OS_model.pkl")

col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])

with col1:
    pitch_type = st.selectbox("Pitch Type", ['Fastball', 'Sinker', 'Cutter', 'Slider', 'Curveball', 'ChangeUp', 'Splitter'])
    height = st.text_input("Release Height:")

with col2:
    pitcher_hand = st.selectbox("Throws", ['Left', 'Right'])
    side = st.text_input("Release Side:")

with col3:
    velo = st.text_input("Velo:")
    extension = st.text_input("Extension:")

with col4:
    ivb = st.text_input("IVB:")
    vaa = st.text_input("VAA:")

with col5:
    hb = st.text_input("HB:")
    haa = st.text_input("HAA:")

primaryfb_velo = ''
primaryfb_ivb = ''
primaryfb_hb = ''

if (pitch_type != 'Fastball') and (pitch_type != 'Sinker'):
    primary_fb = st.selectbox("Primary Fastball", ['Fastball', 'Sinker', 'Cutter'])
    if primary_fb:
        if pitch_type != 'Cutter' or (primary_fb != 'Cutter' and pitch_type == 'Cutter'):
            col6, col7, col8 = st.columns([1,1,1])
            with col6:
                primaryfb_velo = st.text_input("Primary FB Velo:")
            with col7:
                primaryfb_ivb = st.text_input("Primary FB IVB:")
            with col8:
                primaryfb_hb = st.text_input("Primary FB HB:")
        else:
            st.markdown("You're ready to go! Click Calculate")
else:
    st.markdown("You're ready to go! Click Calculate")
        
if st.button("Calculate"):
    st.markdown("hi")
        

st.subheader("CSV")

st.markdown("")