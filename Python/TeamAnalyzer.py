import sqlite3  # This is the package for all sqlite3 access in Python
import sys      # This helps with command-line parameters

class PokemonIDError(Exception):
    pass

# All the "against" column suffixes:
types = ["bug","dark","dragon","electric","fairy","fight",
    "fire","flying","ghost","grass","ground","ice","normal",
    "poison","psychic","rock","steel","water"]

# Flexible input: Accept either Pokedex numbers or Pokemon names at the command line
def flexible_input(pokemon, cursor):
    if pokemon.isdigit():
        return int(pokemon)
    else:
        cursor.execute("SELECT pokedex_number FROM pokemon WHERE name=?", (pokemon,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            raise ValueError("Invalid Pokemon name: {}".format(pokemon))

# You will need to write the SQL, extract the results, and compare
    # Remember to look at those "against_NNN" column values; greater than 1
    # means the Pokemon is strong against that type, and less than 1 means
    # the Pokemon is weak against that type
def pokemon_analyze(pokemon_id, cursor):
    cursor.execute("SELECT name, type1, type2 FROM pokemon WHERE id=?", (pokemon_id,))
    pokemon = cursor.fetchone()
    name, type1, type2 = pokemon
    types = [type1] + ([type2] if type2 else [])
    strengths = []
    weaknesses = []

    for against_type in types_list:
        for t in types:
            against_value = cursor.execute(f"SELECT {t} FROM pokemon WHERE id=?", (pokemon_id,)).fetchone()[0]
            if against_value > 1 and against_type == t:
                strengths.append(against_type)
            else: 
                weaknesses.append(against_type)

    return name, types, list(set(strengths)), list(set(weaknesses))

# Take six parameters on the command-line
if len(sys.argv) < 6:
    print("You must give me six Pokemon to analyze!")
    sys.exit()

# Connect with the database
conn = sqlite3.connect('pokemon.db')
cursor = conn.cursor()

team = []
for i, arg in enumerate(sys.argv):
    if i == 0:
        continue

    try:
        pokemon_id = flexible_input(arg, cursor)
    except ValueError as e:
        raise PokemonIDError(str(e))
    # Analyze the pokemon whose pokedex_number is in "arg"
    pokemon_data = pokemon_analyze(pokemon_id, cursor)
    name, types, strengths, weaknesses = pokemon_data
    team.append((name, types, strengths, weaknesses))


answer = input("Would you like to save this team? (Y)es or (N)o: ")
if answer.upper() == "Y" or answer.upper() == "YES":
    teamName = input("Enter the team name: ")

    # Write the pokemon team to the "teams" table
    cursor.execute("INSERT INTO teams (name) VALUES (?)", (teamName,))
    # Get team ID from the last inserted row
    team_id = cursor.lastrowid

    # Add team members to the database
    for arg in sys.argv[1:]:
        try:
            pokemon_id = flexible_input(arg, cursor)
            cursor.execute("INSERT INTO team_members (team_id, pokemon_id) VALUES (?, ?)", (team_id, pokemon_id))
        except ValueError as e:
            print(f"Error adding team member {arg}: {e}")
            continue

    # Commit changes to the database
    conn.commit()

    print("Saving " + teamName + " ...")
else:
    print("Bye for now!")

