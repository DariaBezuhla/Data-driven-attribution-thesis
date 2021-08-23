# This code is adapted from a post linked down below, from Morten Hegewald
# Title: Marketing Channel Attribution with Markov Chains in Python — Part 2: The Complete Walkthrough
# Author: Morten Hegewald
# Date: November 20, 2019
# Availability:https://towardsdatascience.com/marketing-channel-attribution-with-markov-chains-in-python-part-2-the-complete-walkthrough-733c65b23323


# Chapter 5.2.1 Data preprocessing

import csv
import pandas as pd
import numpy as np
from collections import defaultdict

df = pd.read_csv('file_name.csv')
df = df.sort_values(['cookie', 'timestamp'],
                    ascending=[False, True])
df['visit_order'] = df.groupby('cookie').cumcount() + 1

df_paths = df.groupby('cookie')['channel'].aggregate(
    lambda x: x.unique().tolist()).reset_index()

df_last_interaction = df.drop_duplicates('cookie', keep='last')[['cookie', 'leadouts']]
df_paths = pd.merge(df_paths, df_last_interaction, how='left', on='cookie')

df_paths['path'] = np.where(
    df_paths['leadouts'] == 0,
    list(map(lambda x: ['Start', *x, 'Null'], df_paths['channel'])),
    list(map(lambda x: ['Start', *x, 'Conversion'], df_paths['channel']))
)

df_paths = df_paths[['cookie', 'path']]

# Chapter 5.2.2 Markov chains

list_of_paths = df_paths['path']
total_conversions = sum(path.count('Conversion') for path in df_paths['path'].tolist())
base_conversion_rate = total_conversions / len(list_of_paths)

# Step 1. Calculating the probability of transition between all states.

def transition_states(list_of_paths):
    list_of_unique_channels = set(x for element in list_of_paths for x in element)
    transition_states = {x + '>' + y: 0 for x in list_of_unique_channels for y in list_of_unique_channels}

    for possible_state in list_of_unique_channels:
        if possible_state not in ['Conversion', 'Null']:
            for user_path in list_of_paths:
                if possible_state in user_path:
                    indices = [i for i, s in enumerate(user_path) if possible_state in s]
                    for col in indices:
                        transition_states[user_path[col] + '>' + user_path[col + 1]] += 1

    return transition_states

trans_states = transition_states(list_of_paths)

def transition_prob(trans_dict):
    list_of_unique_channels = set(x for element in list_of_paths for x in element)
    trans_prob = defaultdict(dict)
    for state in list_of_unique_channels:
        if state not in ['Conversion', 'Null']:
            counter = 0
            index = [i for i, s in enumerate(trans_dict) if state + '>' in s]
            for col in index:
                if trans_dict[list(trans_dict)[col]] > 0:
                    counter += trans_dict[list(trans_dict)[col]]
            for col in index:
                if trans_dict[list(trans_dict)[col]] > 0:
                    state_prob = float((trans_dict[list(trans_dict)[col]])) / float(counter)
                    trans_prob[list(trans_dict)[col]] = state_prob

    return trans_prob

trans_prob = transition_prob(trans_states)


def transition_matrix(list_of_paths, transition_probabilities):
    trans_matrix = pd.DataFrame()
    list_of_unique_channels = set(x for element in list_of_paths for x in element)

    for channel in list_of_unique_channels:
        trans_matrix[channel] = 0.00
        trans_matrix.loc[channel] = 0.00
        trans_matrix.loc[channel][channel] = 1.0 if channel in ['Conversion', 'Null'] else 0.0

    for key, value in transition_probabilities.items():
        origin, destination = key.split('>')
        trans_matrix.at[origin, destination] = value

    return trans_matrix

trans_matrix = transition_matrix(list_of_paths, trans_prob)
trans_matrix.to_csv(open('transitionMatrix.csv', 'w'))
print("transition matrix: ", trans_matrix)


# Step 2. Calculating the removal effect of every state.

def removal_effects(df, conversion_rate):
    removal_effects_dict = {}
    channels = [channel for channel in df.columns if channel not in ['Start',
                                                                     'Null',
                                                                     'Conversion']]
    for channel in channels:
        removal_df = df.drop(channel, axis=1).drop(channel, axis=0)
        for column in removal_df.columns:
            row_sum = np.sum(list(removal_df.loc[column]))
            null_pct = float(1) - row_sum
            if null_pct != 0:
                removal_df.loc[column]['Null'] = null_pct
            removal_df.loc['Null']['Null'] = 1.0

        removal_to_conv = removal_df[
            ['Null', 'Conversion']].drop(['Null', 'Conversion'], axis=0)
        removal_to_non_conv = removal_df.drop(
            ['Null', 'Conversion'], axis=1).drop(['Null', 'Conversion'], axis=0)

        removal_inv_diff = np.linalg.inv(
            np.identity(
                len(removal_to_non_conv.columns)) - np.asarray(removal_to_non_conv))
        removal_dot_prod = np.dot(removal_inv_diff, np.asarray(removal_to_conv))
        removal_cvr = pd.DataFrame(removal_dot_prod,
                                   index=removal_to_conv.index)[[1]].loc['Start'].values[0]
        removal_effect = 1 - removal_cvr / conversion_rate
        removal_effects_dict[channel] = removal_effect

    return removal_effects_dict


removal_effects_dict = removal_effects(trans_matrix, base_conversion_rate)
print("removal effect: ", removal_effects_dict)

# Step 3. Calculate the Markov chain attribution for each of the marketing channels

def markov_chain_allocations(removal_effects, total_conversions):
    re_sum = np.sum(list(removal_effects.values()))
    return {k: (v / re_sum) * total_conversions for k, v in removal_effects.items()}

attributions = markov_chain_allocations(removal_effects_dict, total_conversions)


with open('attributionResults.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    for key, value in attributions.items():
        writer.writerow([key, value])
print("attributions: ", attributions)

