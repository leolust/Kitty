def remboursement(contributions, depenses):
    # Calcul du montant total des contributions
    total_contributions = sum(contributions.values())
    # Calcul du montant total des dépenses
    total_depenses = sum(depenses.values())

    reste = total_contributions - total_depenses

    if reste > 1:
        reste -= 1
        while reste >= 1:
            contribMax = max(contributions, key=contributions.get)
            contributions[contribMax[1]] -= 1
            reste -= 1
        reste += 1

    while reste >= 0.01:
        contribMax = max(contributions, key=contributions.get)
        contributions[contribMax[1]] -= 0.01
        reste -= 0.01
    
    # 5 10 10 10 10 10 10 

    contribMax = max(contributions, key=contributions.get)
    contributions[contribMax[1]] -= reste
    
    return transactions


contributions = {'A': 10, 'B': 5, 'C': 15, 'D': 10.55, 'E': 9.45, 'F': 10, 'G': 30, 'H': 10} # 100
depenses = {'D': 53, 'F': 7, 'A': 10, 'H': 20}                                               #  90

transactions = remboursement(contributions, depenses)

for transaction in transactions:
    print(f"{transaction[0]} rembourse {transaction[1]} un montant de {transaction[2]} euros.")
