import streamlit as st
import pandas as pd
import numpy as np

st.title('English Premier League - Betting Simulator')
st.subheader('Try out various betting strategies for the English Primier League for the last ten years')

df_earnings = pd.read_csv('Earnings_Odds.csv')

st.markdown('Welcome to a comparison of odds between different betting websites for the last 10 years.')

season = st.sidebar.selectbox('Select season:', df_earnings.Season.unique().tolist())
st.sidebar.text('')
st.sidebar.text('')

df_season = df_earnings.loc[df_earnings.Season==season,:].reset_index(drop=True)

sources = {'B365':'Bet365',
           'BS':'Blue Square',
           'BW':'Bet&Win',
           'GB':'Gamebookers',
           'IW':'Interwetten',
           'LB':'Ladbrokes',
           'PS':'Pinnacle',
           'SB':'Sportingbet',
           'SJ':'Stan James',
           'VC':'VC',
           'WH':'William Hill'}

betting_strat = st.sidebar.selectbox('Betting Strategy', ['Constant Bet','Percentage of total'])
st.sidebar.text('')
st.sidebar.text('')

matches = st.radio("How do you want to bet?",('Bet on all matches', 'Bet on selected teams'))
selected_teams = False
teams = ''
if matches == 'Bet on selected teams':
    selected_teams=True
    teams = st.multiselect('Select the teams you want to bet on:', df_season.HomeTeam.unique())

st.markdown('The bet is always made on the safest bet according to each betting agency.')

st.sidebar.markdown('Betting Parameters:')

if betting_strat == 'Constant Bet':

    bet_per_match = st.sidebar.number_input('Bet per match:',value=10, min_value=5, max_value=1000, step=1)
    df_season.loc[:,sources] = df_season.loc[:,sources]*bet_per_match

    # st.write('Number of teams selected:', len(teams))

    if selected_teams:
        df_season = pd.concat([df_season[df_season.HomeTeam.apply(lambda x: x in teams)],df_season[df_season.AwayTeam.apply(lambda x: x in teams)]])

    try:
        assert len(teams)>0
    except NameError:
        pass
    except AssertionError:
        st.text('Select at least one team to get started')

    df_cumearnings = df_season.iloc[:,[0,1,2,3,4]].merge(df_season[sources].cumsum(axis=0), how='left', left_index=True, right_index=True)

    st.header('Cumulative earnings for the season:')
    st.line_chart(df_cumearnings.loc[:,sources.keys()])

    st.write('Total amount bet for the season:', len(df_season)*bet_per_match)
    st.header('Top performers of the season:')

    try:
        df_top = df_cumearnings.tail(1).T.iloc[5:,:].sort_values(by=df_cumearnings.index.tolist()[-1], ascending=False)
        df_top = df_top.head(5).round(0)
        df_top.rename(index=sources, inplace=True)
        df_top.columns = ['Winnings']
        df_top.Winnings = df_top.Winnings.apply(lambda x: str(x)[:7])
        df_top['Earnings'] = df_top.Winnings.apply(float) - len(df_season)*bet_per_match
        df_top['Earnings'] = df_top['Earnings'].apply(lambda x: str(x)[:8])
        st.table(df_top)
    except IndexError:
        st.text('Select at least one team to get started')


if betting_strat == 'Percentage of total':

    # st.header('This section is a work in progress.... check back again soon!')

    st.markdown('This betting strategy bets a portion of your current balance for a match')

    start_amount = st.sidebar.number_input('Starting amount:',value=1000, min_value=0, max_value=10000, step=1)
    pct = st.sidebar.number_input('Percentage of account total:',value=0.2, min_value=0.0, max_value=1.0, step=0.01)

    if selected_teams:
        df_season = pd.concat([df_season[df_season.HomeTeam.apply(lambda x: x in teams)],df_season[df_season.AwayTeam.apply(lambda x: x in teams)]])
        st.markdown('Number of matches: {0}'.format(len(df_season)))

    try:
        assert len(teams)>0
    except NameError:
        pass
    except AssertionError:
        st.text('Select at least one team to get started')

    for src in sources.keys():
    # src='B365'
        df_src = df_season.loc[:,['Season','Date','HomeTeam','AwayTeam','FTR',src]].reset_index(drop=True)
        # df_src['opening_balance'] = 0
        df_src['closing_balance'] = 0

        bet = start_amount*pct
        bal = start_amount*(1-pct)
        if df_src.loc[df_src.index[0],src] < 0:
            df_src.loc[df_src.index[0],'closing_balance'] = start_amount*(1-pct)
        else:
            earning = bet*df_src.loc[df_src.index[0],src]
            df_src.loc[df_src.index[0],'closing_balance'] = start_amount*(1-pct) + (start_amount*pct*df_src.loc[df_src.index[0],src])

        for i in df_src.index[1:]:
            if df_src.loc[i,src] < 0:
                df_src.loc[i,'closing_balance'] = df_src.loc[i-1,'closing_balance']*(1-pct)
            else:
                df_src.loc[i,'closing_balance'] = df_src.loc[i-1,'closing_balance']*(1-pct) + (df_src.loc[i-1,'closing_balance']*pct*df_src.loc[i,src])
                # if i == df_src.index[1]:
                #     st.text('Here',df_src.loc[i-1,'closing_balance']*pct*df_src.loc[i,src])

            # earning = df_src.loc[i-1,'closing_balance'] + (df_src.loc[i-1,'closing_balance']*pct*df_src.loc[i,src]) - (df_src.loc[i-1,'closing_balance']*pct)
            # df_src.loc[i,'closing_balance'] = df_src.loc[i-1,'closing_balance'] + earning

        df_season[src] = df_src.closing_balance
    # df_season
    st.line_chart(df_season.loc[:,sources.keys()])
    # try:
    df_top = df_season.tail(1).T#.iloc[5:,:].sort_values(by=df_season.index.tolist()[-1], ascending=False)
    df_top
    # df_top = df_top.head(5).round(0)
    # df_top.rename(index=sources, inplace=True)
    # df_top.columns = ['Winnings']
    # df_top.Winnings = df_top.Winnings.apply(lambda x: str(x)[:7])
    # df_top['Earnings'] = df_top.Winnings.apply(float) - len(df_season)*bet_per_match
    # df_top['Earnings'] = df_top['Earnings'].apply(lambda x: str(x)[:8])
    # st.table(df_top)
    # except IndexError:
    #     st.text('Select at least one team to get started')

if st.sidebar.checkbox('Show data'):
    st.subheader('Match-wise earnings data')
    st.write(df_season.round(0))
