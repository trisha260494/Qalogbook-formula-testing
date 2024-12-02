from flask import Flask, request, render_template, jsonify
import sqlite3
import sympy as sp
import re

app = Flask(__name__)


# Function to get formulas from the database
def get_formulas():
    conn = sqlite3.connect('formulas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, formula_string FROM formulas")
    formulas = cursor.fetchall()
    conn.close()
    return formulas

@app.route('/get_formula_details', methods=['POST'])
def get_formula_details():
    data = request.json
    formula_string = data.get('formula_string')

    try:
        conn = sqlite3.connect('formulas.db')
        cursor = conn.cursor()
        cursor.execute("SELECT variables FROM formulas WHERE formula_string = ?", (formula_string,))
        result = cursor.fetchone()
        conn.close()

        if result:
            variables = result[0].split(", ")  # Split saved variables into a list
            return jsonify({"success": True, "variables": variables})
        else:
            return jsonify({"success": False, "error": "Formula not found."})
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
    equation = re.sub(r'[^a-zA-Z0-9_]', lambda match: match.group(0).encode('unicode_escape').decode('utf-8'), equation)
    return equation

# Function to calculate the result for the formula
# Route to calculate based on user input
@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    equation = data.get('equation')
    values = data.get('values', {})
    variable_to_calculate_name = data.get('variable_to_calculate')

    try:
        # Parse the equation
        lhs, rhs = equation.split('=')
        equation = sp.Eq(sp.sympify(lhs.strip()), sp.sympify(rhs.strip()))

        # Handle variable to calculate
        variable_to_calculate = None
        if variable_to_calculate_name:
            variable_to_calculate = sp.Symbol(variable_to_calculate_name)
        else:
            # Infer the missing variable
            all_variables = equation.free_symbols
            provided_variables = {sp.Symbol(k) for k in values.keys()}
            missing_variable = list(all_variables - provided_variables)
            if len(missing_variable) == 1:
                variable_to_calculate = missing_variable[0]
            else:
                return jsonify({"error": "Could not infer the variable to calculate."}), 400

        # Substitute provided values
        substituted_equation = equation.subs(values)

        # Solve the equation
        solution = sp.solve(substituted_equation, variable_to_calculate)

        # Convert solution to a serializable format (e.g., float or str)
        if solution:
            # If the solution is a list of solutions, convert them to floats or strings
            serialized_solution = [float(sol) if sol.is_real else str(sol) for sol in solution]
        else:
            serialized_solution = "No solution found."

        return jsonify({"result": serialized_solution})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/')
def auto_index():
    return render_template('auto_index.html', title="Auto Calculate")

if __name__ == '__main__':
    
    app.run(debug=True, port=5002)
