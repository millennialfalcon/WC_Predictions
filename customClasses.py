import csv 
import numpy as np

class Team: 
    def __init__(self, name, elo): 
        self.name = name 
        self.elo = elo 
        self.points = 0 
        self.init_elo = elo

        self.champion = 0 
        self.finalist = 0 
        self.semi_finalist = 0 
        self.quarter_finalist = 0 
        self.groupWinner = 0 
        self.groupRunnerUp = 0 

    def reset_results(self): 
        self.champion = 0 
        self.finalist = 0 
        self.semi_finalist = 0 
        self.quarter_finalist = 0 
        self.groupWinner = 0 
        self.groupRunnerUp = 0 
    
    def update_champions(self): 
        self.champion += 1 

    def update_finalist(self): 
        self.finalist += 1 

    def update_semi_finalist(self): 
        self.semi_finalist += 1

    def update_quarter_finalist(self): 
        self.quarter_finalist += 1 
    
    def update_groupWinner(self): 
        self.groupWinner += 1 

    def update_groupRunnerUp(self): 
        self.groupRunnerUp += 1
    
    def reset_elo(self): 
        self.elo = self.init_elo
        
    def updatePoints(self, value):
        self.points += value
        # print(f'{self.name} new point total is {self.points}')

    def updateElo(self, value): 
        # print(f'{value} change to elo is')
        self.elo += value
        # print(f'{self.name}\'s new elo is {self.elo}')

class Group:
    def __init__(self, name, teams:list, match_order): 
        self.name = name 
        self.teams = teams
        self.match_order = match_order
    
    def getStandings(self): 
        standings = [team for team in self.teams]
        standings = sorted(standings, key = lambda x: (x.points, x.elo), reverse=True)
        return standings

    def simGroup(self): 
        for team in self.teams: 
            team.updatePoints(team.points * -1)
            team.reset_elo()
        # print('\n')

        for match in self.match_order: 
            team1 = match[0]
            team2 = match[1]
            
            if team1.elo >= team2.elo: 
                favorite = team1 
                underdog = team2 
            else: 
                favorite = team2 
                underdog = team1    
            elo_dif = favorite.elo - underdog.elo
            
            #probs
            favorite_prob = (1 / (10 ** (-1 * elo_dif / 400) + 1))
            draw_prob = (1 - (1 / (10 ** (-1 * elo_dif / 400) + 1))) / 5 * 3 
            underdog_prob = 1 - (favorite_prob + draw_prob)
            
            # print(f'{favorite.name} is favored to beat {underdog.name}.')
            # print(f'{favorite.name}\'s odds of winning are {favorite_prob:.2%}.')
            # print(f'Odds of a draw are {draw_prob:.2%}.')
            # print(f'{underdog.name}\'s odds of winning are {underdog_prob:.2%}.')
            
            #run sim 
            favorite_num = favorite_prob * 100_000 
            draw_num = favorite_num + (draw_prob * 100_000) 
            underdog_num = draw_num + (underdog_prob * 100_000)
            winning_num = np.random.randint(0,100_000) 
            goal_dif = np.random.choice(self.group_non_draws)

            if winning_num < favorite_num: 
                # print(f'{favorite.name} won by {goal_dif}.')
                winner = favorite
            elif winning_num < draw_num: 
                # print(f'Match ended in a draw.' )
                winner = 'draw'
                goal_dif = 0
            else: 
                # print(f'{underdog.name} won by {goal_dif}.')
                winner = underdog
                
            #update standings 
            if winner != 'draw': 
                winner.updatePoints(3)
            else: 
                team1.updatePoints(1)
                team2.updatePoints(1)
            
            #win_expect only needed for elo update at end    
            if goal_dif == 2: 
                goal_weight = 1.5 
            elif goal_dif == 3: 
                goal_weight = 1.75
            elif goal_dif >= 4: 
                goal_weight = 1.75 + ((goal_dif-3)/8)
            else: 
                goal_weight = 1
            
            win_expectancy = 1 / (10 ** (-1 * elo_dif / 400) + 1)

            #update elo for favorite 
            if winner == favorite: 
                favorite_elo_change = (60 * goal_weight) * (1 - win_expectancy)
                underdog_elo_change = (60 * goal_weight) * (0 - (1 - win_expectancy))
            elif winner == underdog: 
                favorite_elo_change = (60 * goal_weight) * (0 - win_expectancy)
                underdog_elo_change = (60 * goal_weight) * (1 - (1 - win_expectancy))
            else: 
                favorite_elo_change = (60 * goal_weight) * (0.5 - win_expectancy)
                underdog_elo_change = (60 * goal_weight) * (0.5 - (1 - win_expectancy))
            
            favorite.updateElo(favorite_elo_change)
            underdog.updateElo(underdog_elo_change)
            # print('\n')
    
    group_non_draws = []
    with open('group_nondraw_scores.csv', 'r') as f: 
        next(f)
        reader = csv.reader(f)
        for line in reader: 
            group_non_draws.append(int(line[-1]))

def simulate_group_stage(groups): 
    positions = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2', 'E1', 'E2', 'F1', 'F2', 'G1', 'G2', 'H1', 'H2']
    results = []
    for group in groups:
        group.simGroup() 
        result = group.getStandings()
        winner = result[0]
        runnerUp = result[1]
        results.append(winner)
        results.append(runnerUp)
        winner.update_groupWinner() 
        runnerUp.update_groupRunnerUp()


    results = {p:r for p, r in zip(positions, results)}
    return results

def simulate_knockout_game(team1, team2): 
    knockout_non_draws = []
    with open('knockout_non_draw_scores.csv', 'r') as f: 
        next(f)
        reader = csv.reader(f)
        for line in reader: 
            knockout_non_draws.append(int(line[-1]))

    if team1.elo >= team2.elo: 
        favorite = team1 
        underdog = team2 
    else: 
        favorite = team2 
        underdog = team1    
    elo_dif = favorite.elo - underdog.elo
                
    #probs
    favorite_prob = (1 / (10 ** (-1 * elo_dif / 400) + 1))
    shootout_prob = (1 - (1 / (10 ** (-1 * elo_dif / 400) + 1))) / 5 * 3 
    underdog_prob = 1 - (favorite_prob + shootout_prob)

    # print(f'{favorite.name} is favored to beat {underdog.name}.')
    # print(f'{favorite.name}\'s odds of winning are {favorite_prob:.2%}.')
    # print(f'Odds of a shootout are {shootout_prob:.2%}.')
    # print(f'{underdog.name}\'s odds of winning are {underdog_prob:.2%}.')

    #run sim 
    favorite_num = favorite_prob * 100_000 
    draw_num = favorite_num + (shootout_prob * 100_000) 
    underdog_num = draw_num + (underdog_prob * 100_000)
    winning_num = np.random.randint(0,100_000) 
    goal_dif = np.random.choice(knockout_non_draws)

    if winning_num < favorite_num: 
        # print(f'{favorite.name} won by {goal_dif}.')
        winner = favorite
    elif winning_num < draw_num: 
        # print(f'Match goes to a shootout.' )
        winner = 'draw'
        goal_dif = 0
        if winning_num % 2 == 0: 
            winner = favorite 
            # print(f'{winner.name} won.')
        else: 
            winner = underdog
            # print(f'{winner.name} won.')
                
    else: 
        # print(f'{underdog.name} won by {goal_dif}.')
        winner = underdog

    if goal_dif == 2: 
        goal_weight = 1.5 
    elif goal_dif == 3: 
        goal_weight = 1.75
    elif goal_dif >= 4: 
        goal_weight = 1.75 + ((goal_dif-3)/8)
    else: 
        goal_weight = 1
    
    win_expectancy = 1 / (10 ** (-1 * elo_dif / 400) + 1)

    #update elo for favorite 
    if winner == favorite: 
        favorite_elo_change = (60 * goal_weight) * (1 - win_expectancy)
        underdog_elo_change = (60 * goal_weight) * (0 - (1 - win_expectancy))
    elif winner == underdog: 
        favorite_elo_change = (60 * goal_weight) * (0 - win_expectancy)
        underdog_elo_change = (60 * goal_weight) * (1 - (1 - win_expectancy))
    else: 
        favorite_elo_change = (60 * goal_weight) * (0.5 - win_expectancy)
        underdog_elo_change = (60 * goal_weight) * (0.5 - (1 - win_expectancy))
                
    favorite.updateElo(favorite_elo_change)
    underdog.updateElo(underdog_elo_change)
    # print('\n')

    return winner

def simulate_knockout(results): 
    
    #round of 16 
    winner1 = simulate_knockout_game(results['A1'], results['B2'])
    winner2 = simulate_knockout_game(results['C1'], results['D2'])
    winner3 = simulate_knockout_game(results['E1'], results['F2'])
    winner4 = simulate_knockout_game(results['G1'], results['H2'])
    winner5 = simulate_knockout_game(results['B1'], results['A2'])
    winner6 = simulate_knockout_game(results['D1'], results['C2'])
    winner7 = simulate_knockout_game(results['F1'], results['E2'])
    winner8 = simulate_knockout_game(results['H1'], results['G2'])

    #quater finals 
    winner9 = simulate_knockout_game(winner1, winner2)
    winner10 = simulate_knockout_game(winner3, winner4)
    winner11 = simulate_knockout_game(winner5, winner6)
    winner12 = simulate_knockout_game(winner7, winner8)

    #semi finals
    winner13 = simulate_knockout_game(winner9, winner10)
    winner14 = simulate_knockout_game(winner11, winner12)

    #finals 
    winner15 = simulate_knockout_game(winner13, winner14)

    quarter_finalists = [winner1, winner2, winner3, winner4, winner5, winner6, winner7, winner8]
    for qf in quarter_finalists: 
        qf.update_quarter_finalist() 
    
    semi_finalists = [winner9, winner10, winner11, winner12]
    for sf in semi_finalists:
        sf.update_semi_finalist()

    finalists = [winner13, winner14]
    for f in finalists: 
        f.update_finalist() 

    winner15.update_champions() 


