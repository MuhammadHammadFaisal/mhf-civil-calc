import numpy as np


def _fmt(x, nd=2):
    try:
        return f"{float(x):.{nd}f}"
    except Exception:
        return str(x)


def build_step_by_step_markdown(
    results,
    fc,
    fy_long,
    Ag,
    Ast,
    reinf_style,
    core_diameter_input,
    strength_basis,
    fywk=0.0,
    spiral_dia=0.0,
    spiral_spacing=0.0,
):
    """
    Student-friendly step-by-step report.

    Units:
    - MPa = N/mm²
    - Area = mm²
    - Force = N (we also display kN)
    """

    ALPHA_CC = 0.85
    gamma_c = getattr(results, "gamma_c", 1.5)
    gamma_s = getattr(results, "gamma_s", 1.15)

    # Based on the radio selection, your calculator sets:
    fcd = results.fcd
    fyd = results.fyd

    # Course assumption: use Ag (not Ag-Ast)
    Fc = ALPHA_CC * fcd * Ag
    Fs = Ast * fyd
    Nor1 = Fc + Fs

    md = f"""
### Given / Inputs
- Concrete strength input: $f_{{ck}} = {_fmt(fc,2)}\\,\\text{{MPa}}$
- Steel strength input: $f_{{yk}} = {_fmt(fy_long,2)}\\,\\text{{MPa}}$
- Gross area: $A_g = {_fmt(Ag,0)}\\,\\text{{mm}}^2$
- Steel area: $A_{{st}} = {_fmt(Ast,0)}\\,\\text{{mm}}^2$
- Confinement type: **{reinf_style}**
- Strength selection (radio): **{strength_basis}**

> Unit note: $1\\,\\text{{MPa}} = 1\\,\\text{{N/mm}}^2$  
> So (MPa) × (mm²) = **N**.

---

## Step 1 — Choose design or characteristic strengths
Your radio button decides what we use:

### If **Design Values (fcd, fyd)**
Use partial safety factors:
- $\\gamma_c = {_fmt(gamma_c,2)}$
- $\\gamma_s = {_fmt(gamma_s,2)}$

$$
f_{{cd}} = \\frac{{f_{{ck}}}}{{\\gamma_c}}
= \\frac{{{_fmt(fc,2)}}}{{{_fmt(gamma_c,2)}}}
= \\mathbf{{{_fmt(fc/gamma_c,2)}}}\\,\\text{{MPa}}
$$

$$
f_{{yd}} = \\frac{{f_{{yk}}}}{{\\gamma_s}}
= \\frac{{{_fmt(fy_long,2)}}}{{{_fmt(gamma_s,2)}}}
= \\mathbf{{{_fmt(fy_long/gamma_s,2)}}}\\,\\text{{MPa}}
$$

### If **Characteristic Values (fck, fyk)**
No reduction:
$$
f_{{cd}} = f_{{ck}} = \\mathbf{{{_fmt(fc,2)}}}\\,\\text{{MPa}}
\\qquad
f_{{yd}} = f_{{yk}} = \\mathbf{{{_fmt(fy_long,2)}}}\\,\\text{{MPa}}
$$

✅ Your selected values used in calculations:
$$
f_{{cd}} = \\mathbf{{{_fmt(fcd,2)}}}\\,\\text{{MPa}}
\\qquad
f_{{yd}} = \\mathbf{{{_fmt(fyd,2)}}}\\,\\text{{MPa}}
$$

---

## Step 2 — Concrete contribution $F_c$
**Course assumption:** concrete compression uses *gross* area $A_g$.

Formula:
$$
F_c = \\alpha_{{cc}}\\, f_{{cd}}\\, A_g
$$

Substitute:
$$
F_c = 0.85\\times({_fmt(fcd,2)})\\times({_fmt(Ag,0)})
$$

Result:
$$
F_c = \\mathbf{{{Fc/1000:,.1f}}}\\,\\text{{kN}}
\\;\\;\\; (={Fc:,.0f}\\,\\text{{N}})
$$

---

## Step 3 — Steel contribution $F_s$
Formula:
$$
F_s = A_{{st}}\\, f_{{yd}}
$$

Substitute:
$$
F_s = ({_fmt(Ast,0)})\\times({_fmt(fyd,2)})
$$

Result:
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

    # -----------------------------
    # Spiral confinement part (if present)
    # -----------------------------
    if ("Spiral" in reinf_style) and (results.Nor2 is not None) and (spiral_spacing > 0) and (spiral_dia > 0) and (fywk > 0) and (core_diameter_input > 0):

        d_outer = core_diameter_input
        d_center = d_outer - spiral_dia

        Ack = np.pi * d_outer**2 / 4.0
        Asp = np.pi * spiral_dia**2 / 4.0

        rho_s = (4.0 * Asp) / (d_center * spiral_spacing)

        rho_min_calc = 0.45 * (fc / fywk) * ((Ag / Ack) - 1.0)
        rho_min_abs = 0.12 * (fc / fywk)
        rho_min_req = max(rho_min_calc, rho_min_abs)

        confinement_boost = (2.0 * rho_s * fywk) / 1.5
        fccd = fcd + confinement_boost

        Nor2 = fccd * Ack + Ast * fyd

        ok_text = "✅ OK" if rho_s >= rho_min_req else "❌ NOT OK"

        md += f"""
---

# Spiral confinement (Confined core)

## Step 5 — Core & spiral geometry
- $D_k = {_fmt(d_outer,1)}\\,\\text{{mm}}$ (to centerline)
- Spiral bar $\\phi_{{sp}} = {_fmt(spiral_dia,1)}\\,\\text{{mm}}$
- Spacing $s = {_fmt(spiral_spacing,1)}\\,\\text{{mm}}$
- Spiral steel $f_{{ywk}} = {_fmt(fywk,1)}\\,\\text{{MPa}}$

Core area:
$$
A_{{ck}} = \\frac{{\\pi D_k^2}}{{4}}
= \\frac{{\\pi({_fmt(d_outer,1)})^2}}{{4}}
= {_fmt(Ack,0)}\\,\\text{{mm}}^2
$$

Spiral steel area:
$$
A_{{sp}} = \\frac{{\\pi \\phi_{{sp}}^2}}{{4}}
= {_fmt(Asp,0)}\\,\\text{{mm}}^2
$$

---

## Step 6 — Volumetric ratio $\\rho_s$
Using your calculator’s formula:
$$
\\rho_s = \\frac{{4A_{{sp}}}}{{D_{{center}}\\,s}}
\\quad \\text{{with}}\\quad D_{{center}} = D_k - \\phi_{{sp}} = {_fmt(d_center,1)}\\,\\text{{mm}}
$$

$$
\\rho_s = \\frac{{4\\times({_fmt(Asp,0)})}}{{({_fmt(d_center,1)})\\times({_fmt(spiral_spacing,1)})}}
= \\mathbf{{{_fmt(rho_s,5)}}}
$$

---

## Step 7 — Minimum required $\\rho_{{min}}$
$$
\\rho_{{min,calc}} = 0.45\\left(\\frac{{f_{{ck}}}}{{f_{{ywk}}}}\\right)\\left(\\frac{{A_g}}{{A_{{ck}}}} - 1\\right)
= \\mathbf{{{_fmt(rho_min_calc,5)}}}
$$

$$
\\rho_{{min,abs}} = 0.12\\left(\\frac{{f_{{ck}}}}{{f_{{ywk}}}}\\right)
= \\mathbf{{{_fmt(rho_min_abs,5)}}}
$$

$$
\\rho_{{min}} = \\max(\\rho_{{min,calc}},\\rho_{{min,abs}})
= \\mathbf{{{_fmt(rho_min_req,5)}}}
$$

Check: $\\rho_s \\ge \\rho_{{min}}$ → **{ok_text}**

---

## Step 8 — Confined concrete strength
Boost (your calculator):
$$
\\Delta f = \\frac{{2\\rho_s f_{{ywk}}}}{{1.5}}
= \\frac{{2\\times({_fmt(rho_s,5)})\\times({_fmt(fywk,1)})}}{{1.5}}
= {_fmt(confinement_boost,2)}\\,\\text{{MPa}}
$$

$$
f_{{ccd}} = f_{{cd}} + \\Delta f
= {_fmt(fcd,2)} + {_fmt(confinement_boost,2)}
= \\mathbf{{{_fmt(fccd,2)}}}\\,\\text{{MPa}}
$$

---

## Step 9 — Confined axial capacity
$$
N_{{or2}} = f_{{ccd}}A_{{ck}} + A_{{st}}f_{{yd}}
$$

$$
N_{{or2}} = ({_fmt(fccd,2)})\\times({_fmt(Ack,0)}) + ({_fmt(Ast,0)})\\times({_fmt(fyd,2)})
= \\mathbf{{{Nor2/1000:,.1f}}}\\,\\text{{kN}}
$$
"""

    return md
def build_required_as_markdown(Nu_kN, f_used, fy_used, Ag, Fc_N, Ast_req):
    md = f"""
### Required Steel (As) — Step-by-step

Given:
- $N_u = {Nu_kN:,.1f}\\,\\text{{kN}}$
- $A_g = {Ag:,.0f}\\,\\text{{mm}}^2$
- Concrete strength used: $f = {f_used:.2f}\\,\\text{{MPa}}$
- Steel strength used: $f_y = {fy_used:.2f}\\,\\text{{MPa}}$

Concrete force:
$$
F_c = 0.85\\, f\\, A_g
$$
$$
F_c = {Fc_N/1000:,.1f}\\,\\text{{kN}}
$$

Solve for steel:
$$
N_u = F_c + A_s f_y
\\Rightarrow
A_s = \\frac{{N_u - F_c}}{{f_y}}
$$

Result:
$$
A_s = \\mathbf{{{Ast_req:,.0f}}}\\,\\text{{mm}}^2
$$
"""
    return md
