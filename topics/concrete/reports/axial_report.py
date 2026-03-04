import numpy as np


def _fmt(val, nd=2):
    try:
        return f"{val:.{nd}f}"
    except Exception:
        return str(val)


def build_step_by_step_markdown(
    results,
    fc,
    fy_long,
    Ag,
    Ast,
    reinf_style,
    core_diameter_input,
    fywk=0.0,
    spiral_dia=0.0,
    spiral_spacing=0.0,
    strength_basis="Design Values (fcd, fyd)",
):
    """
    Generates a student-friendly step-by-step markdown report.

    Units convention in this module:
    - MPa = N/mm²
    - Areas = mm²
    - Forces = N (shown also in kN for readability)
    """

    ALPHA_CC = 0.85  # same as calculator assumption (Eurocode-like)
    gamma_c = getattr(results, "gamma_c", 1.5)
    gamma_s = getattr(results, "gamma_s", 1.15)

    # Strengths used (already computed in calculator)
    fcd = results.fcd
    fyd = results.fyd

    # ---- Basic areas
    Ac = max(Ag - Ast, 0.0)  # concrete net area
    # Forces
    # IMPORTANT: This matches the intended standard formula: 0.85*fcd*(Ag-Ast) + Ast*fyd
    Fc = ALPHA_CC * fcd * Ac
    Fs = Ast * fyd
    Nor1 = Fc + Fs

    # Use computed values if calculator provides them; otherwise fallback to our recompute
    # (We keep consistent with report so students see correct mechanics.)
    Nor1_show = getattr(results, "Nor1", Nor1)

    md = f"""
### Given / Inputs
- Concrete strength: $f_{{ck}} = {_fmt(fc,2)}\\,\\text{{MPa}}$
- Steel strength: $f_{{yk}} = {_fmt(fy_long,2)}\\,\\text{{MPa}}$
- Gross area: $A_g = {_fmt(Ag,0)}\\,\\text{{mm}}^2$
- Steel area: $A_{{st}} = {_fmt(Ast,0)}\\,\\text{{mm}}^2$
- Concrete net area: $A_c = A_g - A_{{st}} = {_fmt(Ac,0)}\\,\\text{{mm}}^2$
- Confinement type: **{reinf_style}**
- Strength basis: **{strength_basis}**

> Note: $1\\,\\text{{MPa}} = 1\\,\\text{{N/mm}}^2$.  
> So multiplying (MPa) × (mm²) gives **N**.

---

## Step 1 — Convert strengths (Design vs Characteristic)
We use partial safety factors:
- $\\gamma_c = {_fmt(gamma_c,2)}$
- $\\gamma_s = {_fmt(gamma_s,2)}$

If using design values:
$$
f_{{cd}} = \\frac{{f_{{ck}}}}{{\\gamma_c}}
\\quad\\Rightarrow\\quad
f_{{cd}} = {_fmt(fcd,2)}\\,\\text{{MPa}}
$$
$$
f_{{yd}} = \\frac{{f_{{yk}}}}{{\\gamma_s}}
\\quad\\Rightarrow\\quad
f_{{yd}} = {_fmt(fyd,2)}\\,\\text{{MPa}}
$$

---

## Step 2 — Concrete contribution ($F_c$)
We assume:
$$
F_c = \\alpha_{{cc}}\\, f_{{cd}}\\,(A_g - A_{{st}})
$$
Substitute:
$$
F_c = (0.85)\\times({_fmt(fcd,2)})\\times({_fmt(Ac,0)})
$$
$$
F_c = \\mathbf{{{Fc/1000:,.1f}}}\\,\\text{{kN}}
\\;\\;\\; (={Fc:,.0f}\\,\\text{{N}})
$$

---

## Step 3 — Steel contribution ($F_s$)
$$
F_s = A_{{st}}\\, f_{{yd}}
$$
Substitute:
$$
F_s = ({_fmt(Ast,0)})\\times({_fmt(fyd,2)})
$$
$$
F_s = \\mathbf{{{Fs/1000:,.1f}}}\\,\\text{{kN}}
\\;\\;\\; (={Fs:,.0f}\\,\\text{{N}})
$$

---

## Step 4 — Total axial capacity (Unconfined)
$$
N_{{or}} = F_c + F_s
$$
$$
N_{{or}} = \\mathbf{{{Nor1/1000:,.1f}}}\\,\\text{{kN}}
$$

"""

    # ------------------------------------------------------------
    # Spiral confinement section (only if spiral inputs exist)
    # ------------------------------------------------------------
    if ("Spiral" in reinf_style) and (spiral_spacing and spiral_spacing > 0) and (spiral_dia and spiral_dia > 0) and (fywk and fywk > 0) and (core_diameter_input and core_diameter_input > 0):

        d_outer = core_diameter_input  # Dk measured to centerline of spiral (as your UI says)
        d_center = d_outer - spiral_dia  # centerline diameter approx used in your calculator

        Ack = np.pi * d_outer**2 / 4.0   # core area
        Asp = np.pi * spiral_dia**2 / 4.0

        rho_s = (4.0 * Asp) / (d_center * spiral_spacing)

        # Same equations used in your calculator
        rho_min_calc = 0.45 * (fc / fywk) * ((Ag / Ack) - 1.0)
        rho_min_abs = 0.12 * (fc / fywk)
        rho_min_req = max(rho_min_calc, rho_min_abs)

        confinement_boost = (2.0 * rho_s * fywk) / 1.5  # as in your calculator
        fccd = fcd + confinement_boost

        Nor2 = fccd * Ack + Ast * fyd
        spiral_ok = rho_s >= rho_min_req

        ok_text = "✅ OK (meets minimum)" if spiral_ok else "❌ NOT OK (too weak)"

        md += f"""
---

# Spiral Confinement (Confined Core Capacity)

## Step 5 — Confined core geometry
Core diameter given:
$$
D_k = {_fmt(d_outer,1)}\\,\\text{{mm}}
$$
Spiral bar diameter:
$$
\\phi_{{sp}} = {_fmt(spiral_dia,1)}\\,\\text{{mm}}
$$
Spiral spacing:
$$
s = {_fmt(spiral_spacing,1)}\\,\\text{{mm}}
$$
Spiral steel strength:
$$
f_{{ywk}} = {_fmt(fywk,1)}\\,\\text{{MPa}}
$$

Core area:
$$
A_{{ck}} = \\frac{{\\pi D_k^2}}{{4}}
= \\frac{{\\pi({_fmt(d_outer,1)})^2}}{{4}}
= {_fmt(Ack,0)}\\,\\text{{mm}}^2
$$

Spiral steel area:
$$
A_{{sp}} = \\frac{{\\pi \\phi_{{sp}}^2}}{{4}}
= \\frac{{\\pi({_fmt(spiral_dia,1)})^2}}{{4}}
= {_fmt(Asp,0)}\\,\\text{{mm}}^2
$$

---

## Step 6 — Spiral volumetric ratio $\\rho_s$
(Using your calculator’s formula)
$$
\\rho_s = \\frac{{4A_{{sp}}}}{{D_{{center}}\\,s}}
\\quad\\text{{where}}\\quad
D_{{center}}=D_k-\\phi_{{sp}} = {_fmt(d_center,1)}\\,\\text{{mm}}
$$

Substitute:
$$
\\rho_s = \\frac{{4\\times({_fmt(Asp,0)})}}{{({_fmt(d_center,1)})\\times({_fmt(spiral_spacing,1)})}}
= \\mathbf{{{_fmt(rho_s,5)}}}
$$

---

## Step 7 — Minimum required spiral ratio $\\rho_{{min}}$
Two checks (your calculator uses the maximum):

1) Main requirement:
$$
\\rho_{{min,calc}} = 0.45\\left(\\frac{{f_{{ck}}}}{{f_{{ywk}}}}\\right)\\left(\\frac{{A_g}}{{A_{{ck}}}} - 1\\right)
= \\mathbf{{{_fmt(rho_min_calc,5)}}}
$$

2) Absolute minimum:
$$
\\rho_{{min,abs}} = 0.12\\left(\\frac{{f_{{ck}}}}{{f_{{ywk}}}}\\right)
= \\mathbf{{{_fmt(rho_min_abs,5)}}}
$$

So:
$$
\\rho_{{min}} = \\max(\\rho_{{min,calc}},\\rho_{{min,abs}})
= \\mathbf{{{_fmt(rho_min_req,5)}}}
$$

**Confinement Check:** $\\rho_s \\ge \\rho_{{min}}$ → **{ok_text}**

---

## Step 8 — Confined concrete strength boost
(Your calculator uses)
$$
\\Delta f = \\frac{{2\\rho_s f_{{ywk}}}}{{1.5}}
$$
Substitute:
$$
\\Delta f = \\frac{{2\\times({_fmt(rho_s,5)})\\times({_fmt(fywk,1)})}}{{1.5}}
= {_fmt(confinement_boost,2)}\\,\\text{{MPa}}
$$

Confined design strength:
$$
f_{{ccd}} = f_{{cd}} + \\Delta f
= {_fmt(fcd,2)} + {_fmt(confinement_boost,2)}
= \\mathbf{{{_fmt(fccd,2)}}}\\,\\text{{MPa}}
$$

---

## Step 9 — Confined axial capacity
$$
N_{{or2}} = f_{{ccd}} A_{{ck}} + A_{{st}} f_{{yd}}
$$

Substitute:
$$
N_{{or2}} = ({_fmt(fccd,2)})\\times({_fmt(Ack,0)}) + ({_fmt(Ast,0)})\\times({_fmt(fyd,2)})
$$

$$
N_{{or2}} = \\mathbf{{{Nor2/1000:,.1f}}}\\,\\text{{kN}}
$$

Capacity change:
$$
\\Delta N = N_{{or2}} - N_{{or}}
= {Nor2/1000:,.1f} - {Nor1/1000:,.1f}
= \\mathbf{{{(Nor2-Nor1)/1000:,.1f}}}\\,\\text{{kN}}
$$
"""

    return md
