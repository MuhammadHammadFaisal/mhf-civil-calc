def build_step_by_step_markdown(results, fc, fy_long, Ag, Ast, reinf_style, core_diameter_input):
    md = f"""
### 0. Design Strengths
$$
f_{{cd}} = {results.fcd:.2f} \\, \\text{{MPa}}
$$
$$
f_{{yd}} = {results.fyd:.2f} \\, \\text{{MPa}}
$$

### 1. Concrete Contribution
$$
F_c = 0.85 f_{{cd}} (A_g - A_{{st}})
$$
$$
F_c = \\mathbf{{{results.Fc/1000:.0f}}} \\, \\text{{kN}}
$$

### 2. Steel Contribution
$$
F_s = A_{{st}} f_{{yd}}
$$
$$
F_s = \\mathbf{{{results.Fs/1000:.0f}}} \\, \\text{{kN}}
$$

### 3. Total Capacity
$$
N_{{or}} = F_c + F_s
$$
$$
N_{{or}} = \\mathbf{{{results.Nor1/1000:.0f}}} \\, \\text{{kN}}
$$
"""

    if "Spiral" in reinf_style and results.Nor2 is not None:
        md += f"""
---

### 4. Confined Core Capacity

$$
N_{{or2}} = \\mathbf{{{results.Nor2/1000:.0f}}} \\, \\text{{kN}}
$$
"""

    return md
