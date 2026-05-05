import math
from decimal import Decimal

#MODELS
TAU = 0.5

class TempPlayer:
    def __init__(self, name, elo=1500.00, glicko=1500.00, glicko_rd=350.00, volatility=0.06):
        self.name = name
        self.elo = Decimal(str(elo))
        self.glicko = Decimal(str(glicko))
        self.glicko_rd = Decimal(str(glicko_rd))
        self.volatility = Decimal(str(volatility))
        self.gamecount = 0
        self.wins = 0
        self.losses = 0
        self._tau = TAU
        
    def rating(self, r):
        return float((r - 1500)) / 173.7178

    def phi(self, RD):
        return float(RD / 173.7178)
    
    #ELO
    def update_elo(self, exp, result):
        exp = Decimal(str(exp))
        result = Decimal(str(result))

        if self.gamecount < 8:
            k = Decimal('40')
        elif self.elo < 2400:
            k = Decimal('20')
        elif self.elo >= 2400:
            k = Decimal('10')

        #New ranking
        rprime=self.elo + k*(result-exp)        
        self.elo = rprime
        self.gamecount+=1
        return self.elo
    #Glicko
    def _v(self, opp_rating, opp_RD):
        # expected variance of the player’s rating based on game outcomes
        tempSum=0
        tempE=self._E(opp_rating, opp_RD)
        tempSum= math.pow(self._g(opp_RD), 2) * tempE * (1 - tempE)
        return 1 / tempSum
    
    def _E(self, opp_rating, opp_rd):
        # expected score against an opponent
        #Convert to glicko scale:
        mu=self.rating(self.glicko)
        opp_rating=self.rating(opp_rating)
        #Compute expected score:
        return 1 / (1 + math.exp(-1 * self._g(opp_rd) * \
                                 (mu - opp_rating)))
    def _g(self, opp_rd):
        #The Glicko2 g(RD) function.
        opp_rd=self.phi(opp_rd)
        return 1/math.sqrt(1 + 3 * math.pow(opp_rd, 2) / math.pow(math.pi, 2))
    
    def preRD(self):
        phi= self.phi(float(self.glicko_rd))
        sigma=float(self.volatility)
        phiprime = math.sqrt(math.pow(phi, 2) + math.pow(sigma, 2)) #Compute new RD
        self.glicko_rd = Decimal(str(phiprime * 173.7178)) #convert back to original scale
    
    def update_glicko(self, opp_rating, opp_RD, outcome):
        #Calculates the new rating and rating deviation of the player.
        
        #Convert variables
        opp_rating=float(opp_rating)
        opp_RD=float(opp_RD)
        outcome=float(outcome)
        
        v=self._v(opp_rating, opp_RD)
        newvol=self.newvol(opp_rating, opp_RD, outcome, v)
        self.volatility=Decimal(str(newvol))
        self.preRD()
        
        phi = 1/math.sqrt((1 / math.pow(self.phi(float(self.glicko_rd)), 2))+ 1/v)
        
        mu=self.rating(float(self.glicko))
        tempsum=self._g(opp_RD) * (outcome - self._E(opp_rating, opp_RD))
        mu+= math.pow(phi, 2) * tempsum
        
        self.glicko_rd = Decimal(str(phi * 173.7178))
        self.glicko = Decimal(str(mu * 173.7178 + 1500))
        
        return self.glicko
        
    def newvol(self, opp_rating, opp_RD, outcome, v):
        #Calculates the new volatility of the player.
        i = 0
        delta = self._delta(opp_rating, opp_RD, outcome, v)
        a = math.log(math.pow(self.volatility, 2))
        tau = self._tau
        x0 = a
        x1 = 0
        
        while x0 != x1:
            # New iteration, so x(i) becomes x(i-1)
            x0 = x1
            d = math.pow(self.rating(self.glicko), 2) + v + math.exp(x0)
            h1 = -(x0 - a) / math.pow(tau, 2) - 0.5 * math.exp(x0) \
            / d + 0.5 * math.exp(x0) * math.pow(delta / d, 2)
            h2 = -1 / math.pow(tau, 2) - 0.5 * math.exp(x0) * \
            (math.pow(self.rating(self.glicko), 2) + v) \
            / math.pow(d, 2) + 0.5 * math.pow(delta, 2) * math.exp(x0) \
            * (math.pow(self.rating(self.glicko), 2) + v - math.exp(x0)) / math.pow(d, 3)
            x1 = x0 - (h1 / h2)
            
        return math.exp(x1 / 2)
    
    def _delta(self, opp_rating, opp_RD, outcome, v):
        #the estimated improvement in rating by comparing the pre-period rating to the performance rating based only on game outcomes
        sum=self._g(opp_RD) * (outcome - self._E(opp_rating, opp_RD))
        return v*sum
    
    #helpers for glicko scale:
    def rating(self, r):
        return float((r- 1500)) / 173.7178
    def phi(self, RD):
        return float(RD / 173.7178)
    
##############################################################################
#Test case

def elo_expected(rating_a, rating_b):
    return 1 / (1 + 10 ** ((float(rating_b) - float(rating_a)) / 400))


def play_match(p1, p2, winner):
    if winner == 1:
        p1_result, p2_result = 1, 0
        p1.wins += 1
        p2.losses += 1
    elif winner == 2:
        p1_result, p2_result = 0, 1
        p2.wins += 1
        p1.losses += 1
    else:
        p1_result, p2_result = 0.5, 0.5

    # Elo
    exp1 = elo_expected(p1.elo, p2.elo)
    exp2 = elo_expected(p2.elo, p1.elo)
    p1.update_elo(exp1, p1_result)
    p2.update_elo(exp2, p2_result)

    # Glicko - save opponent values before updating
    opp_rating = float(p2.glicko)
    opp_rd = float(p2.glicko_rd)
    opp_rating2 = float(p1.glicko)
    opp_rd2 = float(p1.glicko_rd)

    p1.update_glicko(opp_rating, opp_rd, p1_result)
    p2.update_glicko(opp_rating2, opp_rd2, p2_result)
    
def print_player(p):
    print(f"  {p.name:>8}  |  Elo: {float(p.elo):7.2f}  |  "
          f"Glicko: {float(p.glicko):7.2f}  |  "
          f"RD: {float(p.glicko_rd):6.2f}  |  "
          f"Vol: {float(p.volatility):.6f}  |  "
          f"W/L: {p.wins}/{p.losses}")
    
#1st test: equal players
def test_1_equal_players():
    print("\n" + "=" * 60)
    print("TEST 1: Two equal players, alternating wins")
    print("=" * 60)

    a = TempPlayer("Alice")
    b = TempPlayer("Bob")

    for i in range(20):
        winner = 1 if i % 2 == 0 else 2
        play_match(a, b, winner)

    print_player(a)
    print_player(b)

    # Both should stay close to 1500
    assert abs(float(a.elo) - 1500) < 50, f"FAIL: Alice Elo drifted to {a.elo}"
    assert abs(float(b.elo) - 1500) < 50, f"FAIL: Bob Elo drifted to {b.elo}"
    assert abs(float(a.glicko) - 1500) < 100, f"FAIL: Alice Glicko drifted to {a.glicko}"
    assert abs(float(b.glicko) - 1500) < 100, f"FAIL: Bob Glicko drifted to {b.glicko}"
    print("PASSED: Equal players stay near 1500")
    
#2nd test: one player dominates
def test_2_dominant_player():
    print("\n" + "=" * 60)
    print("TEST 2: Player A always beats Player B")
    print("=" * 60)

    a = TempPlayer("Strong")
    b = TempPlayer("Weak")

    for _ in range(20):
        play_match(a, b, winner=1)

    print_player(a)
    print_player(b)

    assert float(a.elo) > float(b.elo), "FAIL: Winner should have higher Elo"
    assert float(a.glicko) > float(b.glicko), "FAIL: Winner should have higher Glicko"
    assert float(a.elo) > 1500, "FAIL: Winner Elo should be above 1500"
    assert float(b.elo) < 1500, "FAIL: Loser Elo should be below 1500"
    print("PASSED: Dominant player rated higher")
    
#3rd test: new player vs established player: upset from the new player
def test_3_upset():
    print("\n" + "=" * 60)
    print("TEST 3: Low-rated player beats high-rated player")
    print("=" * 60)

    high = TempPlayer("Favorite", elo=1800, glicko=1800, glicko_rd=100)
    low = TempPlayer("Underdog", elo=1200, glicko=1200, glicko_rd=100)

    elo_before = float(high.elo)
    glicko_before = float(high.glicko)

    play_match(high, low, winner=2)  # Upset!

    elo_drop = elo_before - float(high.elo)
    glicko_drop = glicko_before - float(high.glicko)

    print_player(high)
    print_player(low)
    print(f"  Favorite Elo drop: {elo_drop:.2f}")
    print(f"  Favorite Glicko drop: {glicko_drop:.2f}")

    assert elo_drop > 10, f"FAIL: Upset should cause significant Elo drop, got {elo_drop:.2f}"
    assert glicko_drop > 5, f"FAIL: Upset should cause significant Glicko drop, got {glicko_drop:.2f}"
    print("PASSED: Upset causes meaningful rating change")

#Testing RD decrease over time with games
def test_4_rd_decreases():
    print("\n" + "=" * 60)
    print("TEST 4: Rating Deviation decreases over games")
    print("=" * 60)

    a = TempPlayer("Active")
    b = TempPlayer("Opponent")

    rd_values = [float(a.glicko_rd)]

    for i in range(10):
        winner = 1 if i % 2 == 0 else 2
        play_match(a, b, winner)
        rd_values.append(float(a.glicko_rd))

    print(f"  RD progression: {' → '.join(f'{rd:.1f}' for rd in rd_values)}")

    assert rd_values[-1] < rd_values[0], \
        f"FAIL: RD should decrease from {rd_values[0]:.2f}, got {rd_values[-1]:.2f}"
    print("PASSED: RD decreases with more games")

#K-factor adjustment test
def test_6_k_factor():
    print("\n" + "=" * 60)
    print("TEST 6: K-factor is higher during placement (first 8 games)")
    print("=" * 60)

    a = TempPlayer("NewPlayer")
    b = TempPlayer("Opponent", glicko_rd=100)
    b.gamecount = 20  # Established player

    # Track Elo changes during placement
    placement_changes = []
    for i in range(8):
        elo_before = float(a.elo)
        play_match(a, b, winner=1)
        placement_changes.append(float(a.elo) - elo_before)

    # Track Elo changes after placement
    post_changes = []
    for i in range(4):
        elo_before = float(a.elo)
        play_match(a, b, winner=1)
        post_changes.append(float(a.elo) - elo_before)

    avg_placement = sum(placement_changes) / len(placement_changes)
    avg_post = sum(post_changes) / len(post_changes)

    print(f"  Avg Elo change during placement (k=40): {avg_placement:.2f}")
    print(f"  Avg Elo change after placement  (k=20): {avg_post:.2f}")

    assert avg_placement > avg_post, \
        "FAIL: Placement games should have larger rating changes"
    print("PASSED: K-factor correctly higher during placement")
    
#Final test: competition
def test_7_tournament():
    print("\n" + "=" * 60)
    print("TEST 7: Tournament with known skill ordering")
    print("=" * 60)

    import random
    random.seed(123)

    # True skill: Best > Good > Average > Weak
    # Higher skill = higher win probability
    players = [
        TempPlayer("Best"),
        TempPlayer("Good"),
        TempPlayer("Average"),
        TempPlayer("Weak"),
    ]
    true_skill = [0.85, 0.65, 0.45, 0.25]

    for _ in range(100):
        i, j = random.sample(range(4), 2)
        # Probability i beats j based on skill difference
        prob_i_wins = true_skill[i] / (true_skill[i] + true_skill[j])
        winner = 1 if random.random() < prob_i_wins else 2
        play_match(players[i], players[j], winner)

    print("  Final standings (should be Best > Good > Average > Weak):")
    for p in players:
        print_player(p)

    elos = [float(p.elo) for p in players]
    glickos = [float(p.glicko) for p in players]

    # Check ordering
    elo_ordered = all(elos[i] >= elos[i + 1] for i in range(len(elos) - 1))
    glicko_ordered = all(glickos[i] >= glickos[i + 1] for i in range(len(glickos) - 1))

    if elo_ordered:
        print("✅ PASSED: Elo ranking matches true skill order")
    else:
        print(f"⚠️  WARNING: Elo order is {[p.name for p in sorted(players, key=lambda x: -float(x.elo))]}")

    if glicko_ordered:
        print("✅ PASSED: Glicko ranking matches true skill order")
    else:
        print(f"⚠️  WARNING: Glicko order is {[p.name for p in sorted(players, key=lambda x: -float(x.glicko))]}")
        
#Test scalibility
def test_9_scalability():
    print("\n" + "=" * 60)
    print("TEST 9: Scalability - 20 players, ~50 games each")
    print("=" * 60)

    import random
    import time
    random.seed(999)
    
    tier_definitions = [
    ("Elite",     0.90, 4),   # 4 elite players
    ("Strong",    0.70, 4),   # 4 strong players
    ("Average",   0.50, 4),   # 4 average players
    ("BelowAvg",  0.35, 4),   # 4 below average
    ("Beginner",  0.20, 4),   # 4 beginners
    ]

    players = []
    true_skills = {}

    for tier_name, skill, count in tier_definitions:
        for i in range(count):
            name = f"{tier_name}_{i+1}"
            p = TempPlayer(name)
            players.append(p)
            true_skills[name] = skill

    total_players = len(players)
    print(f"  Created {total_players} players across 5 tiers\n")

    # Each player should play ~50 games
    # Total matches needed: (20 players * 50 games) / 2 = 500 matches
    total_matches = 500
    match_count = {p.name: 0 for p in players}

    start_time = time.time()

    for _ in range(total_matches):
        # Pick two random players, weighted toward those with fewer games
        # to keep game counts balanced
        weights = [max(1, 55 - match_count[p.name]) for p in players]
        p1, p2 = random.choices(players, weights=weights, k=2)

        # Ensure different players
        while p1.name == p2.name:
            p2 = random.choice(players)

        # Determine winner based on true skill
        skill1 = true_skills[p1.name]
        skill2 = true_skills[p2.name]
        prob_p1_wins = skill1 / (skill1 + skill2)

        winner = 1 if random.random() < prob_p1_wins else 2
        play_match(p1, p2, winner)

        match_count[p1.name] += 1
        match_count[p2.name] += 1

    elapsed = time.time() - start_time

    # ---- Display Results by Tier ----
    print(f"  {'Name':>12}  |  {'Skill':>5}  |  {'Games':>5}  |  "
          f"{'Elo':>7}  |  {'Glicko':>7}  |  {'RD':>6}  |  {'W/L':>7}")
    print("  " + "-" * 80)

    for tier_name, skill, count in tier_definitions:
        for i in range(count):
            name = f"{tier_name}_{i+1}"
            p = next(pl for pl in players if pl.name == name)
            print(f"  {p.name:>12}  |  {true_skills[p.name]:>5.2f}  |  "
                  f"{match_count[p.name]:>5}  |  {float(p.elo):>7.2f}  |  "
                  f"{float(p.glicko):>7.2f}  |  {float(p.glicko_rd):>6.2f}  |  "
                  f"{p.wins:>3}/{p.losses:<3}")
        print("  " + "-" * 80)

    # ---- Metric 1: Tier Average Ratings ----
    print("\n  TIER AVERAGES:")
    print(f"  {'Tier':>12}  |  {'Avg Elo':>8}  |  {'Avg Glicko':>10}  |  {'Expected Order':>15}")
    print("  " + "-" * 60)

    tier_avg_elo = []
    tier_avg_glicko = []

    for tier_name, skill, count in tier_definitions:
        tier_players = [p for p in players if p.name.startswith(tier_name)]
        avg_elo = sum(float(p.elo) for p in tier_players) / len(tier_players)
        avg_glicko = sum(float(p.glicko) for p in tier_players) / len(tier_players)
        tier_avg_elo.append((tier_name, avg_elo))
        tier_avg_glicko.append((tier_name, avg_glicko))
        print(f"  {tier_name:>12}  |  {avg_elo:>8.2f}  |  {avg_glicko:>10.2f}  |  "
              f"{'skill=' + str(skill):>15}")

    # ---- Metric 2: Tier ordering matches true skill ----
    elo_order = [t[0] for t in sorted(tier_avg_elo, key=lambda x: -x[1])]
    glicko_order = [t[0] for t in sorted(tier_avg_glicko, key=lambda x: -x[1])]
    expected_order = [t[0] for t in tier_definitions]  # Already ordered best to worst

    print(f"\n  Expected tier order:  {expected_order}")
    print(f"  Elo tier order:      {elo_order}")
    print(f"  Glicko tier order:   {glicko_order}")

    elo_order_correct = elo_order == expected_order
    glicko_order_correct = glicko_order == expected_order

    # ---- Metric 3: Separation - elite should be clearly above beginner ----
    elite_avg_elo = next(avg for name, avg in tier_avg_elo if name == "Elite")
    beginner_avg_elo = next(avg for name, avg in tier_avg_elo if name == "Beginner")
    elo_separation = elite_avg_elo - beginner_avg_elo

    elite_avg_glicko = next(avg for name, avg in tier_avg_glicko if name == "Elite")
    beginner_avg_glicko = next(avg for name, avg in tier_avg_glicko if name == "Beginner")
    glicko_separation = elite_avg_glicko - beginner_avg_glicko

    print(f"\n  Elite vs Beginner Elo separation:    {elo_separation:.2f}")
    print(f"  Elite vs Beginner Glicko separation:  {glicko_separation:.2f}")

    # ---- Metric 4: Elo zero-sum check ----
    total_elo = sum(float(p.elo) for p in players)
    expected_total = total_players * 1500
    elo_drift = abs(total_elo - expected_total)
    print(f"\n  Total Elo: {total_elo:.2f} (expected {expected_total}), drift: {elo_drift:.4f}")

    # ---- Metric 5: Within-tier consistency (low variance = good) ----
    print("\n  WITHIN-TIER ELO VARIANCE:")
    for tier_name, skill, count in tier_definitions:
        tier_players = [p for p in players if p.name.startswith(tier_name)]
        tier_elos = [float(p.elo) for p in tier_players]
        avg = sum(tier_elos) / len(tier_elos)
        variance = sum((e - avg) ** 2 for e in tier_elos) / len(tier_elos)
        std_dev = math.sqrt(variance)
        print(f"  {tier_name:>12}: std_dev = {std_dev:.2f}")

    # ---- Metric 6: Rank correlation (Spearman) ----
    # Sort players by true skill, then check if Elo/Glicko rank similarly
    sorted_by_skill = sorted(players, key=lambda p: -true_skills[p.name])
    sorted_by_elo = sorted(players, key=lambda p: -float(p.elo))
    sorted_by_glicko = sorted(players, key=lambda p: -float(p.glicko))

    def rank_correlation(list_a, list_b):
        """Spearman rank correlation between two orderings."""
        n = len(list_a)
        rank_a = {p.name: i for i, p in enumerate(list_a)}
        rank_b = {p.name: i for i, p in enumerate(list_b)}
        d_sq = sum((rank_a[p.name] - rank_b[p.name]) ** 2 for p in list_a)
        return 1 - (6 * d_sq) / (n * (n ** 2 - 1))

    elo_corr = rank_correlation(sorted_by_skill, sorted_by_elo)
    glicko_corr = rank_correlation(sorted_by_skill, sorted_by_glicko)

    print(f"\n  RANK CORRELATION WITH TRUE SKILL (Spearman):")
    print(f"  Elo:    {elo_corr:.4f}  (1.0 = perfect)")
    print(f"  Glicko: {glicko_corr:.4f}  (1.0 = perfect)")

    # ---- Metric 7: Performance timing ----
    print(f"\n  PERFORMANCE:")
    print(f"  {total_matches} matches computed in {elapsed:.4f} seconds")
    print(f"  {total_matches / elapsed:.0f} matches/second")

    # ---- Assertions ----
    print("\n  ASSERTIONS:")

    # Tier order
    if elo_order_correct:
        print("  ✅ Elo tier ordering matches true skill")
    else:
        print(f"  ⚠️  Elo tier ordering doesn't perfectly match (got {elo_order})")

    if glicko_order_correct:
        print("  ✅ Glicko tier ordering matches true skill")
    else:
        print(f"  ⚠️  Glicko tier ordering doesn't perfectly match (got {glicko_order})")

    # Separation
    assert elo_separation > 100, \
        f"FAIL: Elite-Beginner Elo gap too small: {elo_separation:.2f}"
    print(f"  ✅ Elo separation between Elite and Beginner > 100 ({elo_separation:.2f})")

    assert glicko_separation > 100, \
        f"FAIL: Elite-Beginner Glicko gap too small: {glicko_separation:.2f}"
    print(f"  ✅ Glicko separation between Elite and Beginner > 100 ({glicko_separation:.2f})")

    # Zero-sum
    max_drift = total_players * 8 * 20  # theoretical max from placement asymmetry
    reasonable_drift = max_drift * 0.15  # expect much less in practice

    assert elo_drift < reasonable_drift, \
        f"FAIL: Elo drift too large: {elo_drift:.4f} (max allowed: {reasonable_drift:.0f})"
    print(f"  ✅ Elo drift within expected range for K-factor asymmetry ({elo_drift:.2f} < {reasonable_drift:.0f})")

    # Rank correlation should be reasonably high
    assert elo_corr > 0.7, f"FAIL: Elo rank correlation too low: {elo_corr:.4f}"
    print(f"  ✅ Elo rank correlation > 0.7 ({elo_corr:.4f})")

    assert glicko_corr > 0.7, f"FAIL: Glicko rank correlation too low: {glicko_corr:.4f}"
    print(f"  ✅ Glicko rank correlation > 0.7 ({glicko_corr:.4f})")

    # Performance (should handle 500 matches easily)
    assert elapsed < 10, f"FAIL: Too slow: {elapsed:.2f}s for {total_matches} matches"
    print(f"  ✅ Performance OK: {total_matches} matches in {elapsed:.4f}s")

    print("\n✅ TEST 9 PASSED: Scalability test complete")


if __name__ == "__main__":
    print("🎮 RATING ALGORITHM TEST SUITE")
    print("No database. No Django. Pure math.\n")

    test_1_equal_players()
    test_2_dominant_player()
    test_3_upset()
    test_4_rd_decreases()
    test_6_k_factor()
    test_7_tournament()
    test_9_scalability()

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)