import pandas as pd
import numpy as np
import streamlit as st
import joblib
import os

st.title("D1 College Baseball Stuff Plus Search Tool")

st.markdown("Welcome to my Stuff+ search tool! In this app, you can search the results of the model, evaluate the Stuff+ of custom metrics, or attach a TrackMan CSV to calculate Stuff+ of a new set of pitches")

st.subheader("Search Results")

st.markdown("Enter the information of a pitcher you would like to search. Enter the name in the form: Last, First. Results shown will be calculated from all pitches thrown by your pitcher on a TrackMan during the 2024 college baseball season. If your pitcher did not pitch in 2024, or did not pitch at a stadium with TrackMan, he will not appear in the dataset. If two pitchers have the same name, a dropdown will appear that allows you to filter by the team your pitcher plays for.")

st.markdown("AdjustedVAA and Adjusted HAA are metrics used in the Stuff+ calculation to control for release point. For AdjustedVAA, 0 is the average VAA for the release height, negative is steeper than average, and positive is flatter than average. Similarly for AdjustedHAA, 0 is the average HAA for the horizontal release point, negative is sharper towards right handed hitters, and positive is sharper towards left handed hitters.")

# Import Stuff+ CSVs
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
1. The calculation will be the same if you choose Fastball or Sinker as your pitch type - they are both treated the same.
2. Input Release Height, Release Side, and Extension as decimal numbers, in feet. 1 inch = 0.833 feet.
3. IVB - Induced Vertical Break, HB - Horizontal Break, VAA - Vertical Approach Angle, HAA - Horizontal Approach Angle
4. Using readings from other systems, such as Yakkertech, Rapsodo, or portable Trackman, will not produce the intended results. All of the pitches in the dataset I used were captured with stadium TrackMan, so inputting pitches captured on stadium TrackMan will produce the most accurate calculations. Portable TrackMan is the next best option if no stadium TrackMan data is available.
5. **Very Important**: Enter your VAA and HAA as if your pitch is thrown down the middle: Height = 2.5 and Side = 0. Be as accurate as possible. VAA is always a negative number

If your pitch was a Fastball or Sinker, you don't have to fill out any of the primary fastball information, so click 'Calculate'. The primary fastball information allows the model to take into account difference in break and velo when evaluating breaking balls and offspeed pitches. One more note - if the pitcher's primary fastball is a Cutter, it will be treated as a fastball. If not, it will be treated as a breaking ball. This allows for cutters to be fairly quantified based on how the pitcher uses it in his arsenal.
""")

# Import trained random forest models
fb_model = joblib.load("FB_model.pkl")
bb_model = joblib.load("BB_model.pkl")
os_model = joblib.load("OS_model.pkl")

# Average whiff rates for each pitch category - taken from original notebook
fb_avg_whiff = 0.27167388032984463
bb_avg_whiff = 0.427275318103788
os_avg_whiff = 0.42386659187930714

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
primary_fb = ''

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
    st.markdown("Add your metrics and click Calculate")
        
if st.button("Calculate"):
    if pitcher_hand == 'Left':
        hb = -(float(hb))
    else:
        hb = float(hb)

    # helper functions to find average VAA and HAA values for pitch down the middle
    def bin_contains_0(bin_str):
        # Remove brackets and split on comma
        bin_str = bin_str.replace('(', '').replace(']', '')
        lower, upper = map(float, bin_str.split(','))
        return lower < 0 <= upper

    def bin_contains_2point5(bin_str):
        # Remove brackets and split on comma
        bin_str = bin_str.replace('(', '').replace(']', '')
        lower, upper = map(float, bin_str.split(','))
        return lower < 2.5 <= upper

    # Load in average VAA by height and HAA by side for different locations from training
    vaa_bins = pd.read_csv(os.path.join("adjusted_haa_vaa_bins", f"vaa_by_height_{pitch_type}.csv"))[['height_bin', 'VertApprAngle']]
    haa_bins = pd.read_csv(os.path.join("adjusted_haa_vaa_bins", f"haa_by_side_{pitch_type}_{pitcher_hand}.csv"))[['side_bin', 'HorzApprAngle']]

    # Find expected VAA/HAA for pitch down the middle
    bin_with_zero = haa_bins[haa_bins['side_bin'].apply(bin_contains_0)]
    bin_with_2point5 = vaa_bins[vaa_bins['height_bin'].apply(bin_contains_2point5)]
    haa_middle_avg = bin_with_zero['HorzApprAngle'].iloc[0] if not bin_with_zero.empty else None
    vaa_middle_avg = bin_with_2point5['VertApprAngle'].iloc[0] if not bin_with_2point5.empty else None

    # Calculate adjusted VAA and adjusted HAA - if no value in bin, the average will be assumed (adj = 0)
    try:
        adj_vaa = float(vaa) - vaa_middle_avg
        adj_haa = float(haa) - haa_middle_avg
    except:
        adj_vaa = 0
        adj_haa = 0

    # put together inputs, calculate stuff+ and display
    if pitch_type == 'Fastball' or pitch_type == 'Sinker' or (pitch_type == 'Cutter' and primary_fb == 'Cutter'):
        pitch = pd.DataFrame([{'RelSpeed': float(velo), 'RelHeight': float(height), 'RelSide': float(side), 'Extension': float(extension), 'InducedVertBreak': float(ivb), 'StandardizedHB': hb, 'AdjustedVAA': adj_vaa, 'AdjustedHAA': adj_haa}])
        result = fb_model.predict_proba(pitch)
        x_whiff = result[0][1]
        stuff_plus = int((x_whiff / fb_avg_whiff) * 100)
        st.markdown(stuff_plus)

    if pitch_type == 'Slider' or pitch_type == 'Curveball' or (pitch_type == 'Cutter' and primary_fb != 'Cutter'):
        velodiff = float(velo) - float(primaryfb_velo)
        ivbdiff = float(ivb) - float(primaryfb_ivb)
        hbdiff = float(hb) - float(primaryfb_hb)
        pitch = pd.DataFrame([{'RelSpeed': float(velo), 'RelHeight': float(height), 'RelSide': float(side), 'Extension': float(extension), 'InducedVertBreak': float(ivb), 'StandardizedHB': hb, 'AdjustedVAA': adj_vaa, 'AdjustedHAA': adj_haa, 'VeloDiff': velodiff, 'IVBDiff': ivbdiff, 'HBDiff': hbdiff}])
        result = bb_model.predict_proba(pitch)
        x_whiff = result[0][1]
        stuff_plus = int((x_whiff / bb_avg_whiff) * 100)
        st.markdown(stuff_plus)

    if pitch_type == 'ChangeUp' or pitch_type == 'Splitter':
        velodiff = float(velo) - float(primaryfb_velo)
        ivbdiff = float(ivb) - float(primaryfb_ivb)
        hbdiff = float(hb) - float(primaryfb_hb)
        pitch = pd.DataFrame([{'RelSpeed': float(velo), 'RelHeight': float(height), 'RelSide': float(side), 'Extension': float(extension), 'InducedVertBreak': float(ivb), 'StandardizedHB': hb, 'AdjustedVAA': adj_vaa, 'AdjustedHAA': adj_haa, 'VeloDiff': velodiff, 'IVBDiff': ivbdiff, 'HBDiff': hbdiff}])
        result = os_model.predict_proba(pitch)
        x_whiff = result[0][1]
        stuff_plus = int((x_whiff / os_avg_whiff) * 100)
        st.markdown(stuff_plus)
        

st.subheader("CSV")

st.markdown("Enter a TrackMan CSV and search the Stuff+ results")

# Get user's CSV and make necessary transformations
all_pitches = st.file_uploader("Upload your CSV file", type=['csv'])
if all_pitches:
    all_pitches = pd.read_csv(all_pitches)
    all_pitches = all_pitches[['Date', 'Pitcher', 'PitcherTeam', 'PitcherThrows', 'TaggedPitchType', 'PitchCall', 'PlayResult', 'RelSpeed', 'PlateLocHeight', 'PlateLocSide', 'RelHeight', 'RelSide', 'Extension', 'InducedVertBreak', 'HorzBreak', 'VertApprAngle', 'HorzApprAngle', 'Level', 'PitchReleaseConfidence', 'PitchLocationConfidence', 'PitchMovementConfidence']]
    
    all_pitches = all_pitches[(all_pitches['Level'] == 'D1') & (all_pitches['PitchReleaseConfidence'] == 'High') & (all_pitches['PitchLocationConfidence'] == 'High') & (all_pitches['PitchMovementConfidence'] == 'High')].drop(columns = ['Level', 'PitchReleaseConfidence', 'PitchLocationConfidence', 'PitchMovementConfidence'])
    all_pitches = all_pitches[(all_pitches['TaggedPitchType'] != 'Other') & (all_pitches['TaggedPitchType'] != 'Undefined')].reset_index()
    all_pitches['TaggedPitchType'] = all_pitches['TaggedPitchType'].replace({
        'FourSeamFastBall': 'Fastball',
        'TwoSeamFastBall': 'Sinker',
        'OneSeamFastBall': 'Fastball'
    })

    # Convert range strings into actual intervals
    def parse_bin(bin_str):
        # Remove brackets and split on comma
        bin_str = bin_str.replace('(', '').replace(']', '')
        lower, upper = map(float, bin_str.split(','))
        return lower, upper
        
    # Calculate Adjusted VAA and HAA for all pitches in new data using bins from training
    def calc_adj_vaa_haa(pitches):
        pitches_adj = []
        for p_type in pitches['TaggedPitchType'].unique():
            pitches_pitch = pitches[pitches['TaggedPitchType'] == p_type]
            both_hands = []
            # Adjusted HAA - normalize for pitch location and pitcher handedness
            for hand in ['Left', 'Right']:
                pitches_pitch_hand = pitches_pitch[pitches_pitch['PitcherThrows'] == hand]
                #load bins from training
                haa_by_side = pd.read_csv(os.path.join("adjusted_haa_vaa_bins", f"haa_by_side_{p_type}_{hand}.csv"))[['side_bin', 'HorzApprAngle']]

                # Apply parsing to create bin edges
                bin_edges = sorted(set(edge for b in haa_by_side['side_bin'].apply(parse_bin) for edge in b))
                bin_labels = haa_by_side['side_bin']
                
                # Assign bins to new data df
                pitches_pitch_hand['side_bin'] = pd.cut(pitches_pitch_hand['PlateLocSide'], bins=bin_edges, labels=bin_labels, right=False)

                # Merge this back with the original dataframe
                pitches_pitch_hand = pitches_pitch_hand.merge(haa_by_side, on='side_bin', suffixes=('', '_mean'))
    
                # Calculate HAA Above/Below Average
                pitches_pitch_hand['AdjustedHAA'] = pitches_pitch_hand['HorzApprAngle'] - pitches_pitch_hand['HorzApprAngle_mean']
    
                both_hands.append(pitches_pitch_hand)
    
            pitches_pitch = pd.concat(both_hands)
    
            #load bins from training
            vaa_by_height = pd.read_csv(os.path.join("adjusted_haa_vaa_bins", f"vaa_by_height_{p_type}.csv"))[['height_bin', 'VertApprAngle']]

            # Apply parsing to create bin edges
            bin_edges = sorted(set(edge for b in vaa_by_height['height_bin'].apply(parse_bin) for edge in b))
            bin_labels = vaa_by_height['height_bin']
                
            # Assign bins to new data df
            pitches_pitch['height_bin'] = pd.cut(pitches_pitch_hand['PlateLocHeight'], bins=bin_edges, labels=bin_labels, right=False)
    
            # Merge this back with the original dataframe
            pitches_pitch = pitches_pitch.merge(vaa_by_height, on='height_bin', suffixes=('', '_mean'))
    
            # Calculate VAA Above/Below Average
            pitches_pitch['AdjustedVAA'] = pitches_pitch['VertApprAngle'] - pitches_pitch['VertApprAngle_mean']
    
            # Will drop PlateLocSide and PlateLocHeight when applied to all_pitches dataframe
            pitches_new = pitches_pitch.drop(columns = ['VertApprAngle', 'HorzApprAngle', 'PlateLocHeight', 'PlateLocSide', 'height_bin', 'side_bin', 'VertApprAngle_mean', 'HorzApprAngle_mean'])
            pitches_adj.append(pitches_new)
        return pd.concat(pitches_adj)
        
    all_pitches = calc_adj_vaa_haa(all_pitches)
    
    all_pitches['StandardizedHB'] = all_pitches.apply(lambda row: -row['HorzBreak'] if row['PitcherThrows'] == 'Left' else row['HorzBreak'], axis=1)
    
    # Calculate VeloDiff, IVBDiff, HBDiff
    def get_pitcher_primary_FB_info(pitches):
        gb_pitcher = pitches[(pitches['TaggedPitchType'] == 'Fastball') | (pitches['TaggedPitchType'] == 'Sinker') | (pitches['TaggedPitchType'] == 'Cutter')].groupby(['Pitcher', 'TaggedPitchType']).count()
        pitcher_primary_FB = gb_pitcher.groupby(level = 'Pitcher')['Date'].idxmax().apply(lambda x: x[1])
        pitches['primaryFB'] = pitches['Pitcher'].map(pitcher_primary_FB)
        pitcher_FB_shape = pitches[pitches['TaggedPitchType'] == pitches['primaryFB']].groupby('Pitcher')[['RelSpeed','InducedVertBreak', 'StandardizedHB']].mean()
        pitches_shapes = pitches.merge(pitcher_FB_shape, on='Pitcher', suffixes=('', 'FBavg'))
        return pitches_shapes
    
    all_pitches = get_pitcher_primary_FB_info(all_pitches)
    
    # Sort pitches and prep data for model
    all_pitches_FB = all_pitches[(all_pitches['TaggedPitchType'] == 'Fastball') | (all_pitches['TaggedPitchType'] == 'Sinker') | (all_pitches['TaggedPitchType'] == 'Cutter')]
    all_pitches_BB = all_pitches[(all_pitches['TaggedPitchType'] == 'Curveball') | (all_pitches['TaggedPitchType'] == 'Slider')]
    all_pitches_OS = all_pitches[(all_pitches['TaggedPitchType'] == 'ChangeUp') | (all_pitches['TaggedPitchType'] == 'Splitter') | (all_pitches['TaggedPitchType'] == 'Knuckleball')]
    fb_data = all_pitches_FB[['RelSpeed', 'RelHeight', 'RelSide', 'Extension', 'InducedVertBreak', 'StandardizedHB', 'AdjustedVAA', 'AdjustedHAA']].dropna()
    
    all_pitches_BB['VeloDiff'] = all_pitches_BB['RelSpeed'] - all_pitches_BB['RelSpeedFBavg']
    all_pitches_BB['IVBDiff'] = all_pitches_BB['InducedVertBreak'] - all_pitches_BB['InducedVertBreakFBavg']
    all_pitches_BB['HBDiff'] = all_pitches_BB['StandardizedHB'] - all_pitches_BB['StandardizedHBFBavg']
    bb_data = all_pitches_BB[['RelSpeed', 'RelHeight', 'RelSide', 'Extension', 'InducedVertBreak', 'StandardizedHB', 'AdjustedVAA', 'AdjustedHAA', 'VeloDiff', 'IVBDiff', 'HBDiff']].dropna()
    
    all_pitches_OS['VeloDiff'] = all_pitches_OS['RelSpeed'] - all_pitches_OS['RelSpeedFBavg']
    all_pitches_OS['IVBDiff'] = all_pitches_OS['InducedVertBreak'] - all_pitches_OS['InducedVertBreakFBavg']
    all_pitches_OS['HBDiff'] = all_pitches_OS['StandardizedHB'] - all_pitches_OS['StandardizedHBFBavg']
    os_data = all_pitches_OS[['RelSpeed', 'RelHeight', 'RelSide', 'Extension', 'InducedVertBreak', 'StandardizedHB', 'AdjustedVAA', 'AdjustedHAA', 'VeloDiff', 'IVBDiff', 'HBDiff']].dropna()
    
    # Calculate Stuff+
    results_FB = fb_model.predict_proba(fb_data)
    x_whiff_FB = [x[1] for x in results_FB]
    all_pitches_FB['xWhiff'] = x_whiff_FB
    all_pitches_FB['Stuff+'] = (all_pitches_FB['xWhiff'] / fb_avg_whiff) * 100
    
    results_BB = bb_model.predict_proba(bb_data)
    x_whiff_BB = [x[1] for x in results_BB]
    all_pitches_BB['xWhiff'] = x_whiff_BB
    all_pitches_BB['Stuff+'] = (all_pitches_BB['xWhiff'] / bb_avg_whiff) * 100
    
    results_OS = os_model.predict_proba(os_data)
    x_whiff_OS = [x[1] for x in results_OS]
    all_pitches_OS['xWhiff'] = x_whiff_OS
    all_pitches_OS['Stuff+'] = (all_pitches_OS['xWhiff'] / os_avg_whiff) * 100

    # Calculate Stuff+ by Pitcher
    stuff_plusFB = all_pitches_FB.groupby(['Pitcher', 'PitcherTeam', 'TaggedPitchType'])[['Stuff+', 'RelSpeed', 'RelHeight', 'RelSide', 'Extension', 'InducedVertBreak', 'HorzBreak', 'AdjustedVAA', 'AdjustedHAA']].mean()
    stuff_plusFB['Stuff+'] = stuff_plusFB['Stuff+'].astype(int)

    stuff_plusBB = all_pitches_BB.groupby(['Pitcher', 'PitcherTeam', 'TaggedPitchType'])[['Stuff+', 'RelSpeed', 'RelHeight', 'RelSide', 'Extension', 'InducedVertBreak', 'HorzBreak', 'AdjustedVAA', 'AdjustedHAA']].mean()
    stuff_plusBB['Stuff+'] = stuff_plusBB['Stuff+'].astype(int)

    stuff_plusOS = all_pitches_OS.groupby(['Pitcher', 'PitcherTeam', 'TaggedPitchType'])[['Stuff+', 'RelSpeed', 'RelHeight', 'RelSide', 'Extension', 'InducedVertBreak', 'HorzBreak', 'AdjustedVAA', 'AdjustedHAA']].mean()
    stuff_plusOS['Stuff+'] = stuff_plusOS['Stuff+'].astype(int)

    pitcher_name = st.text_input("Pitcher:") 
    if pitcher_name:
        try:
            result = pd.concat([stuff_plusFB.loc[pitcher_name], stuff_plusBB.loc[pitcher_name], stuff_plusOS.loc[pitcher_name]])
            teams = pd.Series([team for team, pitch in result.index]).unique()
            if teams.size > 1:
                team = st.selectbox("Teams", teams)
                st.dataframe(result.loc[team])
            else:
                st.dataframe(result)
        except KeyError:
            st.markdown("Name not found in dataset. Make sure name is written in 'Last, First' format, and your pitcher appears in your CSV")