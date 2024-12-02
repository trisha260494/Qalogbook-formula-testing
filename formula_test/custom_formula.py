from flask import Flask, request, render_template, jsonify
import sympy as sp
import re
import sqlite3

app = Flask(__name__)

# Function to initialize the database
def init_db():
    conn = sqlite3.connect('formulas.db')
    cursor = conn.cursor()

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS formulas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                formula_string TEXT,
                variables TEXT
            )
        """)
    conn.commit()
    conn.close()

# Function to save formula into the database
def save_formula(formula_string, variables):
    conn = sqlite3.connect('formulas.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO formulas (formula_string, variables)
        VALUES (?, ?)
    """, (formula_string, variables))
    conn.commit()
    conn.close()

# Initialize the database when the server starts
init_db()

@app.route('/save_formula', methods=['POST'])
def save_formula_route():
    data = request.json
    formula_string = data.get('formula_string')
    variables = data.get('variables')
    
    try:
        # Save the formula to the database
        save_formula(formula_string, variables)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/view_formulas', methods=['GET'])
def view_formulas():
    conn = sqlite3.connect('formulas.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT formula_string, variables FROM formulas")
    formulas = cursor.fetchall()
    
    conn.close()
    
    # Format the response as a list of dictionaries for readability
    formula_data = [{"formula_string": formula[0], "variables": formula[1]} for formula in formulas]
    return jsonify(formula_data)



# Function to normalize non-alphanumeric symbols to valid variable names
def normalize_symbols(equation):
    # Replace non-alphanumeric characters (e.g., Δ) with valid variable names (e.g., 'Delta')
    equation = re.sub(r'[^a-zA-Z0-9_]', lambda match: match.group(0).encode('unicode_escape').decode('utf-8'), equation)
    
    return equation


# Function to extract variables from the equation
def get_variables(equation):
    try:
        lhs, rhs = equation.split('=')
        lhs_expr = sp.sympify(lhs, evaluate=False)
        rhs_expr = sp.sympify(rhs, evaluate=False)
        return list(lhs_expr.free_symbols.union(rhs_expr.free_symbols))
    except Exception as e:
        return str(e)

# Function to substitute values into the equation and solve
def substitute_values(equation, variable_to_calculate, values):
    try:
        lhs, rhs = equation.split('=')
        lhs_expr = sp.sympify(lhs, evaluate=False)
        rhs_expr = sp.sympify(rhs, evaluate=False)
        solved_expr = sp.solve(sp.Eq(lhs_expr, rhs_expr), variable_to_calculate)
        
        # If there's a solution, substitute the values
        if solved_expr:
            substituted_expr = solved_expr[0].subs(values)
            return substituted_expr
        else:
            raise ValueError("Unable to solve the equation.")
    except Exception as e:
        return str(e)

# Route to display variables and prompt for variable to calculate
@app.route('/get_variables', methods=['POST'])
def display_variables():
    data = request.json
    equation = data.get('equation')
    variables = get_variables(equation)
    if isinstance(variables, list):
        variables_str = [str(var) for var in variables]
        return jsonify({"variables": variables_str})
    else:
        return jsonify({"error": variables})

# Route to calculate based on user input
@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    equation = data.get('equation')
    variable_to_calculate = sp.Symbol(data.get('variable_to_calculate'))
    values = {sp.Symbol(key): value for key, value in data.get('values').items()}
    
     # Convert symbols to strings for JSON serialization
    values_str = {str(k): v for k, v in values.items()}

    try:
        # Get the result of the calculation
        result = substitute_values(equation, variable_to_calculate, values)
        
        # Convert result to float for JSON serialization
        numeric_result = float(result.evalf())  # Ensure it's a regular float
        
        return jsonify({
            "result": numeric_result,
            "save_prompt": True,  # Prompt to save formula
            "equation": equation,
            "variable_to_calculate": str(variable_to_calculate),
            "variables": list(values_str.keys())
            })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/')
def custom_index():
    return render_template('custom_index.html', title="Custom Formula App") 

if __name__ == '__main__':
    app.run(debug=True, port=5001)