from itertools import combinations
import json
import numpy as np
import os
import random

from ortools.sat.python import cp_model
import pandas as pd
from tabulate import tabulate
import yaml

from .utils import loading_spinner

yaml_path = os.path.join(os.path.dirname(__file__), 'config.yml')
players_path = os.path.join(os.path.dirname(__file__), 'players2024.csv')
stats_path = os.path.join(os.path.dirname(__file__), 'player_stats.csv')
state_path = os.path.join(os.path.dirname(__file__), 'state.json')
active_path = os.path.join(os.path.dirname(__file__), 'active.txt')
config_path = os.path.join(os.path.dirname(__file__), 'config.json')

with open(yaml_path, "r") as file:
    config = yaml.safe_load(file)
    # config = yaml.load(file, Loader=yaml.SafeLoader)
    print("Loaded config:", config)


SCORE_DIFF_LIMIT = config.get("SCORE_DIFF_LIMIT")  # Default to 40 if not specified in config
NUM_COURTS = config.get("NUM_COURTS", 5)  # Default to 5 if not specified in config
SKILL_SCORES = config.get("SKILL_SCORES")
GENDER_SCORE_MODIFIER = config.get("GENDER_SCORE_MODIFIER", -10)
TEMPERATURE = config.get("TEMPERATURE", 0)
MAX_TIME = config.get("MAX_TIME", None)  # Default to finding optimal solution if not specified
DEBUG = config.get("DEBUG", False)

def getConfig():
    with open(config_path, "r") as f:
        data = json.load(f)
    return data

def updateConfig(value):
    with open(config_path, "r") as f:
        data = json.load(f)
    data["courtCount"] = value
    with open(config_path, "w") as f:
        json.dump(data, f, indent=4)

def getActivePlayers():
    df = pd.read_csv(stats_path)
    return df.to_json(orient='records', indent=4)

def playerScore(colour, gender, temperature=TEMPERATURE):

    score = SKILL_SCORES[colour]
    if gender == "f":
        score += GENDER_SCORE_MODIFIER

    score += random.randint(0, temperature)

    return score

def addActivePlayer(peg_name, peg_colour, gender):
    df = pd.read_csv(stats_path)
    colour = "blue" # default
    match int(peg_colour):
        case 40:
            colour = 'green'
        case 50:
            colour = 'blue-green'
        case 60:
            colour = 'blue'
        case 70:
            colour = 'black-blue'
        case 80:
            colour = 'black'
        case 90:
            colour = 'red-black'
        case 100:
            colour = 'red'
    score = playerScore(colour, gender.lower())
    new_row = {"peg_name": peg_name, "peg_colour": colour, "gender": gender.lower(), "games_played":0, "play_priority":0.99, "skill_score":score}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    output_file = stats_path
    df.sort_values(by="play_priority", ascending=False).to_csv(
        f"{output_file}", index=False
    )

def removeActivePlayer(peg_name):
    df = pd.read_csv(stats_path)
    df = df[df["peg_name"] != peg_name]
    output_file = stats_path
    df.sort_values(by="play_priority", ascending=False).to_csv(
        f"{output_file}", index=False
    )

def reset():
    with open(state_path, 'r') as f:
        data = json.load(f)
        data['gameCount'] = 0
        data['matchLog'] = []
        data['playedMatches'] = []
    with open(state_path, 'w') as f:
        json.dump(data, f, indent=4)
    df = pd.read_csv(stats_path)
    df["games_played"] = 0
    df["play_priority"] = 1  # Initialize play priority
    df["skill_score"] = df.apply(
        lambda row: playerScore(row["peg_colour"], row["gender"]), axis=1
    )
    output_file = stats_path
    df.sort_values(by="play_priority", ascending=False).to_csv(
        f"{output_file}", index=False
    )

def main():

    def generate_valid_matches(players):
        # players: list of (player_name, score)
        valid_matches = []
        players = [(p["peg_name"], p["skill_score"]) for p in players]
        for team1 in combinations(players, 2):
            for team2 in combinations(players, 2):
                if set(team1) & set(team2):  # if intersection is not empty, skip
                    continue
                score1 = team1[0][1] + team1[1][1]
                score2 = team2[0][1] + team2[1][1]
                if abs(score1 - score2) <= SCORE_DIFF_LIMIT:
                    match = tuple([p[0] for p in team1 + team2])
                    # print(f"Match: {match} with scores {score1} vs {score2}")
                    valid_matches.append(match)
        # Remove duplicates (same 4 players, different order)
        valid_matches = list(set(valid_matches))
        return valid_matches

    def schedule_round(players, courts, played_matches, play_priority):
        """
        players: list of dicts with player info
        courts: int (max matches this round)
        played_matches: set of frozenset(player_ids) that already happened
        play_priority: dict {player_id: priority score}
        """
        matches = generate_valid_matches(players)
        model = cp_model.CpModel()

        # Create variables: 1 if match is chosen
        match_vars = {}
        for m in matches:
            match_vars[m] = model.NewBoolVar(f"match_{'_'.join(map(str,m))}")

        names = [p["peg_name"] for p in players]  # list of player names
        # Constraint: each player plays at most once per round
        for name in names:
            model.Add(sum(match_vars[m] for m in matches if name in m) <= 1)

        # Constraint: limit by court count
        model.Add(sum(match_vars[m] for m in matches) <= courts)

        # Avoid repeats: forbid matches already played
        for m in matches:
            # print(m)
            if frozenset(m) in played_matches:
                model.Add(match_vars[m] == 0)

        # Objective: prioritize players who haven't played recently
        model.Maximize(
            sum(sum(play_priority[p] for p in m) * match_vars[m] for m in matches)
        )

        # Solve
        solver = cp_model.CpSolver()

        # Faster with these settings for small models
        solver.parameters.num_search_workers = 1
        solver.parameters.cp_model_presolve = False

        solver.parameters.log_search_progress = DEBUG

        if MAX_TIME:
            solver.parameters.max_time_in_seconds = (
                MAX_TIME  # Optimal solution relatively fast for N <= 40
            )

        done_spinner = loading_spinner("Solving with CP-SAT")
        status = solver.Solve(model)
        done_spinner()

        # Optimal is provable best solution. Feasible is a solution found within time limit.
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            chosen_matches = [m for m in matches if solver.Value(match_vars[m])]
            return chosen_matches
        else:
            return []


    # def teamScore(team):
    #     score = team[0][1] + team[1][1]
    #     if (PENALISE_PARTNER_SKILL_GAP):
    #         score -= abs(team[0][1] - team[1][1]) / 2
    #     return score

    def print_matches(df, matches):
        """
        matches: list of tuples (name1, name2, name3, name4)
        """

        output = {
            "court0": [],
            "court1": [],
            "court2": [],
            "court3": [],
            "court4": [],
            "sittingOut": []
        }

        # Prepare table rows
        def get_score(p):
            return df.loc[df["peg_name"] == p, ["peg_colour", "skill_score"]].values[0]

        rows = []
        index = 0
        for p1, p2, p3, p4 in matches:
            team1 = f"{p1} {get_score(p1)} & {p2} {get_score(p2)}"
            team2 = f"{p3} {get_score(p3)} & {p4} {get_score(p4)}"
            rows.append([team1, "vs", team2])
            output['court' + str(index)].append([team1, "vs", team2])
            index += 1

        # Print table
        print(tabulate(rows, headers=["Team 1", "", "Team 2"], tablefmt="grid"))

        # Playerrs sitting out
        sitting_out = set(df["peg_name"]) - set(sum(matches, ()))
        if sitting_out:
            print("\nPlayers sitting out this round:")
            print(", ".join(sitting_out))
            output['sittingOut'] = ", ".join(sitting_out)

        return output
        


    def save_matches(df, match_log, output_file="matches.json"):
        """
        Save matches to a JSON file.
        """
        log = []
        for matches in match_log:
            round = {"matches": [], "waiting": []}
            for match in matches:
                game = {}
                game["T1"] = [match[0], match[1]]
                game["T2"] = [match[2], match[3]]
                round["matches"].append(game)

            sitting_out = set(df["peg_name"]) - set(sum(matches, ()))
            round["waiting"] = list(sitting_out)
            log.append(round)

        with open(output_file, "w") as f:
            json.dump(log, f, indent=4)
        print(f"Matches saved to {output_file}")


    def generate_game(df, players, game_count):
        play_priority = df.set_index("peg_name")[
            "play_priority"
        ].to_dict()  # get play priority from df
        matches = schedule_round(players, courts, played_matches, play_priority)

        # add 1 to games played for each player in matches
        for match in matches:
            for player in match:
                df.loc[
                    df["peg_name"].str.contains(player.split("_")[0]), "games_played"
                ] += 1

        # add matches to played_matches
        for match in matches:
            # played_matches.add(frozenset(match))
            with open(state_path, 'r') as file:
                data = json.load(file)
            data['playedMatches'].append(match)
            with open(state_path, 'w') as f:
                json.dump(data, f, indent=4)


        # print(played_matches)
        # print(data['playedMatches'])

        print(f"Removed {len(played_matches)} matches from pool.")

        return matches

    ### Program Start ###



    #game_count = 0
    # df = pd.read_csv(players_path)
    df_stat = pd.read_csv(stats_path)
    #df["games_played"] = 0
    #df["play_priority"] = 1  # Initialize play priority
    #df["skill_score"] = df.apply(
    #    lambda row: playerScore(row["peg_colour"], row["gender"]), axis=1
    #)
    # df = df[:40]

    # convert df into a list of dicts
    #players = df.to_dict("records")
    stats = df_stat.to_dict("records")

    courts = NUM_COURTS
    played_matches = set()  # no history yet


    match_log = []  # to store all matches played

    matches = []

    with open(state_path, 'r') as f:
        data = json.load(f)
        data['gameCount'] = data.get('gameCount', 0) + 1
    with open(state_path, 'w') as f:
        json.dump(data, f, indent=4)

    f = open(state_path, 'r')
    data = json.load(f)
    f.close()

    # df["games_played"] = 0
    # df["play_priority"] = 1  # Initialize play priority
    # df["skill_score"] = df.apply(
    #    lambda row: playerScore(row["peg_colour"], row["gender"]), axis=1
    # )

    matches = generate_game(df_stat, stats, data['gameCount'])
    # print(matches)

    with open(state_path, 'r') as f:
        data = json.load(f)
    data['matchLog'].append(matches)
    with open(state_path, 'w') as f:
        json.dump(data, f, indent=4)


    match_log = data["matchLog"]
    played_matches = data["playedMatches"]

    # print(data['matchLog'])
    # print(match_log)

    output = print_matches(df_stat, matches)

    # update play priority based on games played
    df_stat["play_priority"] = (
        1 - df_stat["games_played"] / data['gameCount']
    )
    # if didn't play in previous match, priority is 1
    sitting_out = set(df_stat["peg_name"]) - set(sum(matches, ()))
    for player in sitting_out:
        df_stat.loc[df_stat["peg_name"] == player, "play_priority"] = 1

    output_file = stats_path
    df_stat.sort_values(by="play_priority", ascending=False).to_csv(
        f"{output_file}", index=False
    )
    print(f"Player statistics saved to {output_file}")

    return output


if __name__ == "__main__":
    main()
