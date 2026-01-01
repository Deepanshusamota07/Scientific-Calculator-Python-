from flask import Flask, render_template, request
import math

app = Flask(__name__)

def safe_eval(expr):
    try:
        # normalize symbols
        expr = expr.replace("^", "**")
        expr = expr.replace("√(", "sqrt(")
        expr = expr.replace("∛(", "cuberoot(")
        expr = expr.replace("%", "/100")

        # Allowed math functions (start from math module)
        allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        allowed.update({
            'abs': abs,
            'round': round,
            'sqrt': math.sqrt,
            'log10': math.log10,
            'ln': math.log,
            'factorial': math.factorial,
            'pi': math.pi,
            'e': math.e,
            'cuberoot': lambda x: x**(1/3),

            # Trig (degree-based)
            'sin':  lambda x: math.sin(math.radians(x)),
            'cos':  lambda x: math.cos(math.radians(x)),
            'tan':  lambda x: math.tan(math.radians(x)),

            # Inverse trig — return degrees
            'asin': lambda x: math.degrees(math.asin(x)),
            'acos': lambda x: math.degrees(math.acos(x)),
            'atan': lambda x: math.degrees(math.atan(x)),

            # Hyperbolic (note: hyperbolic functions normally take radians;
            # here kept consistent with your "degree-based" intent)
            'sinh': lambda x: math.sinh(math.radians(x)),
            'cosh': lambda x: math.cosh(math.radians(x)),
            'tanh': lambda x: math.tanh(math.radians(x)),
        })

        # Restrict builtins correctly
        result = eval(expr, {"__builtins__": None}, allowed)

        # Format floats
        if isinstance(result, float):
            if abs(result) < 1e-12:
                result = 0
            elif abs(result) > 1e12:
                return "Infinity"
            else:
                result = round(result, 12)

        # Add degree symbol to inverse trig results when expression used them
        if any(fn in expr for fn in ["asin(", "acos(", "atan("]):
            return f"{result}°"

        return result

    except Exception:
        return "Error"

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""
    expression_raw = ""        # <-- raw expression to keep for hidden input
    expression_display = ""    # <-- pretty expression for visible field

    if request.method == 'POST':
        # We expect the form to post the raw expression under name="expression"
        expression_raw = request.form.get('expression', '')
        result = safe_eval(expression_raw)

    # create a pretty display only for the visible (readonly) input
    expression_display = expression_raw \
        .replace("asin", "sin⁻¹") \
        .replace("acos", "cos⁻¹") \
        .replace("atan", "tan⁻¹")

    # In your template, use:
    #   value="{{ expression_display|e }}"  for the visible input (id="display_expression")
    #   value="{{ expression_raw|e }}"     for the hidden input (id="expression")
    return render_template('index.html',
                           result=result,
                           expression_raw=expression_raw,
                           expression_display=expression_display)

if __name__ == '__main__':
    app.run(debug=True)
