import streamlit as st

st.set_page_config(
    page_title="Nodal Analysis Solver",   
    page_icon="logo.png",                        
    layout="centered",                     
    initial_sidebar_state="expanded"     
)
# Gaussian Elimination with step tracking
def gaussian_elimination_rref(A, b):
    n = len(b)
    steps = []

    # Initial augmented matrix
    steps.append(("Initial Augmented Matrix", [row + [b[i]] for i, row in enumerate(A)]))

    # Forward elimination
    for i in range(n):
        if A[i][i] == 0:
            raise ValueError("Zero pivot detected!")

        for j in range(i + 1, n):
            ratio = A[j][i] / A[i][i]
            for k in range(n):
                A[j][k] -= ratio * A[i][k]
            b[j] -= ratio * b[i]

            steps.append((f"R{j+1} = R{j+1} - ({ratio:.4f})R{i+1}", [row + [b[idx]] for idx, row in enumerate(A)]))

    # Backward elimination to RREF
    for i in range(n-1, -1, -1):
        # Make the pivot 1
        pivot = A[i][i]
        if pivot != 0:
            for k in range(n):
                A[i][k] /= pivot
            b[i] /= pivot
            steps.append((f"Divide R{i+1} by {pivot:.4f} to make pivot 1", [row + [b[idx]] for idx, row in enumerate(A)]))

        # Eliminate above
        for j in range(i):
            factor = A[j][i]
            for k in range(n):
                A[j][k] -= factor * A[i][k]
            b[j] -= factor * b[i]
            steps.append((f"R{j+1} = R{j+1} - ({factor:.4f})R{i+1}", [row + [b[idx]] for idx, row in enumerate(A)]))

    # Final solution
    solution = [b[i] for i in range(n)]
    return solution, steps

# --- Streamlit App ---
st.title("Nodal Analysis Solver")
st.subheader("Solve Systems of Linear Equations")

# Number of nodes
n = st.number_input("Number of Nodes", min_value=1, max_value=6, step=1)

st.markdown("### Input Nodal Equations")

A = []
b = []

for i in range(n):
    cols = st.columns(n + 3)
    row = []
    cols[0].markdown(f"**Eq {i+1}**")
  
    for j in range(n):
        val_str = cols[j + 1].text_input(
            label=f"a{i+1}{j+1}",
            key=f"A{i}{j}",
            value="",
            label_visibility="collapsed"
        )
        try:
            val = float(val_str) if val_str.strip() != "" else 0.0
        except ValueError:
            val = 0.0
        row.append(val)

    cols[n+1].markdown("<div style='text-align:center; font-weight:bold;'>=</div>", unsafe_allow_html=True)

    b_str = cols[n+2].text_input(
        label=f"b{i+1}",
        key=f"b{i}",
        value="",
        label_visibility="collapsed"
    )
    try:
        b_val = float(b_str) if b_str.strip() != "" else 0.0
    except ValueError:
        b_val = 0.0

    A.append(row)
    b.append(b_val)

# Solve button
if st.button("Solve Node Voltages"):
    try:
        solution, steps = gaussian_elimination_rref([row[:] for row in A], b[:])

        st.subheader("Step-by-Step Gaussian Elimination to RREF")

        for title, matrix in steps:
            st.markdown(f"**{title}**")
            rows = []
            for r in matrix:
                rows.append(" & ".join([f"{val:.4f}" for val in r[:-1]]) + " & | & " + f"{r[-1]:.4f}")
            st.latex(
                r"\left[ \begin{array}{" + "c "*(len(matrix[0])-1) + " c}" +
                " \\\\ ".join(rows) +
                r"\end{array} \right]"
            )

        st.subheader("Final Node Voltages")
        st.latex(
            r"V = \begin{bmatrix}" +
            " \\\\ ".join([f"{val:.4f}" for val in solution]) +
            r"\end{bmatrix}"
        )

    except Exception as e:
        st.error(f"Error: {e}")