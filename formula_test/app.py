from flask import Flask, request, render_template, jsonify
import math
import sympy as sp
from flask_caching import Cache
import sqlite3

app = Flask(__name__)

# Configure Flask-Caching
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
cache.init_app(app)

# Fetch custom formulas from the database
def get_custom_formulas():
    conn = sqlite3.connect('formulas.db')
    c = conn.cursor()
    c.execute("SELECT formula_string,  variables FROM formulas")
    formulas = [{'formula': row[0], 'variables': row[1].split(',')} for row in c.fetchall()]
    conn.close()
    return formulas


@app.route('/')
def index():
    formulas = get_custom_formulas()
    return render_template('index.html', formulas=formulas)


@app.route('/get_formulas', methods=['GET'])
def get_formulas():
    predefined_formulas = [
        "P(A) = n(A) / n(S)", "F = m * a", "V = A * h", "E = mc^2",
        "A = πr^2", "V = (1/3) * A * h", "Q = m * ΔT", "I = V / R",
        "F_friction = μ * N", "s = u * t + (1/2) * a * t^2", "a = (v_f - v_i) / t",
        "A = 2 * π * r^2 + 2 * π * r * h", "C = 2 * π * r", "F = G * (m1 * m2) / r^2",
        "P = W / t", "C = (n * R * T) / P", "a + b", "a - b", "a * b", "a / b",
        "sin(a)", "cos(a)", "log(a)", "exp(a)", "a ** b", "a + b * c", "a * b + c",
        "a / (b + c)", "a - sin(b)", "sqrt(a + b)", "A / (6.023 * 10^23)", "polynomial", "custom"
    ]


    # Combine predefined and custom formulas
    all_formulas = predefined_formulas 

    return jsonify(all_formulas)

@app.route('/get_formula_inputs', methods=['POST'])
def get_formula_inputs():
    formula = request.json.get('formula')
    formula_inputs = {
        "P(A) = n(A) / n(S)": ["n(A)", "n(S)"],
        "F = m * a": ["m", "a"],
        "V = A * h": ["A", "h"],
        "E = mc^2": ["m"],
        "A = πr^2": ["r"],
        "V = (1/3) * A * h": ["A", "h"],
        "Q = m * ΔT": ["m", "ΔT"],
        "I = V / R": ["V", "R"],
        "F_friction = μ * N": ["μ", "N"],
        "s = u * t + (1/2) * a * t^2": ["u", "t", "a"],
        "a = (v_f - v_i) / t": ["v_f", "v_i", "t"],
        "A = 2 * π * r^2 + 2 * π * r * h": ["r", "h"],
        "C = 2 * π * r": ["r"],
        "F = G * (m1 * m2) / r^2": ["m1", "m2", "r"],
        "P = W / t": ["W", "t"],
        "C = (n * R * T) / P": ["n", "R", "T", "P"],
        "a + b": ["a", "b"],
        "a - b": ["a", "b"],
        "a * b": ["a", "b"],
        "a / b": ["a", "b"],
        "sin(a)": ["a"],
        "cos(a)": ["a"],
        "log(a)": ["a"],
        "exp(a)": ["a"],
        "a ** b": ["a", "b"],
        "a + b * c": ["a", "b", "c"],
        "a * b + c": ["a", "b", "c"],
        "a / (b + c)": ["a", "b", "c"],
        "a - sin(b)": ["a", "b"],
        "sqrt(a + b)": ["a", "b"],
        "A / (6.023 * 10^23)": ["A"],
        "polynomial": ["degree"]
    }
    
    # Return predefined inputs
    inputs = formula_inputs.get(formula, [])
    return jsonify(inputs=inputs)

@app.route('/get_coefficients', methods=['POST'])
def get_coefficients():
    degree = request.json.get('degree')
    try:
        degree = int(degree)
        # Generate HTML for coefficient fields based on the degree
        coefficient_fields = ''.join([f'<input type="text" name="coef_{i}" placeholder="Coefficient {i}" required><br>' for i in range(degree + 1)])
        return jsonify(html=coefficient_fields)
    except ValueError:
        return jsonify(error="Invalid degree"), 400
    
    

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    formula = data.get('formula')
    values = data.get('values', {})
    result = None



    try:
        # Calculating result based on predefined formulas
        if formula == "P(A) = n(A) / n(S)":
            result = values['n(A)'] / values['n(S)']
        elif formula == "F = m * a":
            result = values['m'] * values['a']
        elif formula == "V = A * h":
            result = values['A'] * values['h']
        elif formula == "E = mc^2":
            result = values['m'] * (299792458**2)
        elif formula == "A = πr^2":
            result = math.pi * (values['r'] ** 2)
        elif formula == "V = (1/3) * A * h":
            result = (1 / 3) * values['A'] * values['h']
        elif formula == "Q = m * ΔT":
            result = values['m'] * values['ΔT']
        elif formula == "I = V / R":
            result = values['V'] / values['R']
        elif formula == "F_friction = μ * N":
            result = values['μ'] * values['N']
        elif formula == "s = u * t + (1/2) * a * t^2":
            result = values['u'] * values['t'] + (0.5) * values['a'] * (values['t'] ** 2)
        elif formula == "a = (v_f - v_i) / t":
            result = (values['v_f'] - values['v_i']) / values['t']
        elif formula == "C = 2 * π * r":
            result = 2 * math.pi * values['r']
        elif formula == "F = G * (m1 * m2) / r^2":
            result = (6.67430e-11) * (values['m1'] * values['m2']) / (values['r'] ** 2)
        elif formula == "P = W / t":
            result = values['W'] / values['t']
        elif formula == "C = (n * R * T) / P":
            result = (values['n'] * values['R'] * values['T']) / values['P']
        elif formula == "a + b":
            result = values['a'] + values['b']
        elif formula == "a - b":
            result = values['a'] - values['b']
        elif formula == "a * b":
             result = values['a'] * values['b'] 
        elif formula == "a / b":
             result = values['a'] / values['b']    
        elif formula == "sin(a)":
            result = math.sin(values['a'])
        elif formula == "cos(a)":
            result = math.cos(values['a'])
        elif formula == "log(a)":
            result = math.log(values['a'])
        elif formula == "exp(a)":
                result = math.exp(values['a'])
        elif formula == "a ** b":
                result = math.pow(values['a'], values['b'])
        elif formula == "a + b * c":
                result = values['a'] + values['b'] * values['c']
        elif formula == "a * b + c":
                result = values['a'] * values['b'] + values['c']
        elif formula == "a / (b + c)":
                if values['b'] + values['c'] != 0:
                    result = values['a'] / (values['b'] + values['c'])
                else:
                    return jsonify(error="Error: Division by zero.")
        elif formula == "a - sin(b)":
                result = values['a'] - sp.sin(values['b'])
        elif formula == "sqrt(a + b)":
                result = sp.sqrt(values['a'] + values['b'])
        elif formula == "A / (6.023 * 10^23)":
                result = values['A'] / (6.023 * 10**23)
           # Polynomial formula
        elif formula == "polynomial":
              degree = int(values.get('degree', 0))  # Get degree
              coefficients = [float(values.get(f'coef_{i}', 0)) for i in range(degree + 1)]
              x = sp.Symbol('x')
              poly = sum(c * x**i for i, c in enumerate(coefficients))
              roots = sp.solve(poly, x)  # Calculate the roots of the polynomial
              result = roots  # Set the result to the roots of the polynomial
              
        
        else:
             result = "Formula not implemented."
        
        
        return jsonify(result=f"Result of {formula} is {result}")
    except Exception as e:
        return jsonify(error=str(e)), 400

if __name__ == '__main__':
    app.run(debug=True)
    
