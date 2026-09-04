"""Regenerates the editorial SVG diagrams embedded in README.md and
decisions/probability_decision_record.md (the former Mermaid sources).

Design system: diagram-design style guide — paper/ink/muted tokens, one
atomic-tangerine accent per diagram, hairline strokes, 4px grid, diamond
decisions, labeled branches. Run from the repo root:

    venv/bin/python docs/diagrams/build_diagrams.py
"""

import os

PAPER = "#f5f5f5"
INK = "#2d3142"
MUTED = "#4f5d75"
SOFT = "#7a8399"
ACCENT = "#eb6c36"
WHITE = "#ffffff"

SANS = "'Geist','Segoe UI',system-ui,-apple-system,sans-serif"
MONO = "'Geist Mono',ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace"

LINE_H = {"title": 18, "sub": 14, "mono": 13, "eyebrow": 13, "formula": 13}
FONT_SIZE = {"title": 12, "sub": 10, "mono": 9, "eyebrow": 8, "formula": 8}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def snap4(v):
    return int((v + 3) // 4 * 4)


def text_w(s, size, mono=False):
    return len(s) * size * (0.62 if mono else 0.60)


def wrap(text, max_px, size, mono=False):
    words, lines, cur = text.split(), [], ""
    for w in words:
        cand = f"{cur} {w}" if cur else w
        if text_w(cand, size, mono) <= max_px or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = snap4(w), snap4(h)
        self.edges = []
        self.nodes = []
        self.labels = []

    def path(self, d, dashed=False, arrow=True):
        dash = ' stroke-dasharray="4,3"' if dashed else ""
        marker = ' marker-end="url(#arr)"' if arrow else ""
        self.edges.append(
            f'<path d="{d}" fill="none" stroke="{MUTED}" stroke-width="1.2"{dash}{marker}/>'
        )

    def edge(self, pts, dashed=False, arrow=True):
        d = "M " + " L ".join(f"{x},{y}" for x, y in pts)
        self.path(d, dashed=dashed, arrow=arrow)

    def jump_edge(self, pts, jump_x, dashed=False):
        """Elbow path with a small arc jump where it crosses another line."""
        x0, y0 = pts[0]
        d = f"M {x0},{y0}"
        for x, y in pts[1:]:
            if y == y0 and x > jump_x > x0:
                d += f" L {jump_x - 8},{y0} A 8,8 0 0 1 {jump_x + 8},{y0}"
                x0 = jump_x + 8
            d += f" L {x},{y}"
            x0, y0 = x, y
        self.path(d, dashed=dashed)

    def dot(self, x, y):
        self.edges.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{INK}"/>')

    def edge_label(self, x, y, s, anchor="middle"):
        self.labels.append(
            f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="8" fill="{SOFT}"'
            f' letter-spacing="0.5" text-anchor="{anchor}">{esc(s)}</text>'
        )

    def eyebrow(self, x, y, s, anchor="start"):
        self.labels.append(
            f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="8" fill="{SOFT}"'
            f' letter-spacing="1.4" text-anchor="{anchor}">{esc(s.upper())}</text>'
        )

    def box(self, cx, cy, lines, w=None, h=None, kind="step"):
        """lines: list of (style, text). kind: step | input | optional | focal | capsule."""
        widths = [
            text_w(t, FONT_SIZE[s], s == "mono") + (len(t) - 1) * 1.4 if s == "eyebrow"
            else text_w(t, FONT_SIZE[s], s == "mono")
            for s, t in lines
        ]
        heights = [LINE_H.get(s, 13) for s, _ in lines]
        if w is None:
            w = snap4(max(widths) + 24)
        if h is None:
            h = snap4(sum(heights) + 24)
        x, y = cx - w / 2, cy - h / 2

        fill, stroke, dash, sw = WHITE, INK, "", 1
        rx = 6
        if kind == "input":
            fill, stroke = "rgba(79,93,117,0.10)", SOFT
        elif kind == "optional":
            fill, stroke, dash = "rgba(45,49,66,0.02)", "rgba(45,49,66,0.30)", ' stroke-dasharray="4,3"'
        elif kind == "focal":
            fill, stroke, sw = "rgba(235,108,54,0.08)", ACCENT, 1.2
        elif kind == "capsule":
            rx = h / 2

        self.nodes.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"'
            f' stroke="{stroke}" stroke-width="{sw}"{dash}/>'
        )

        ty = cy - sum(heights) / 2
        for (s, t), lh in zip(lines, heights):
            if s == "title":
                el = (f'font-family="{SANS}" font-size="12" font-weight="600" fill="{INK}"')
            elif s == "sub":
                el = f'font-family="{SANS}" font-size="10" fill="{MUTED}"'
            elif s == "mono":
                el = f'font-family="{MONO}" font-size="9" fill="{SOFT}"'
            elif s == "formula":
                el = f'font-family="{MONO}" font-size="8" fill="{INK}"'
            elif s == "eyebrow":
                el = (
                    f'font-family="{MONO}" font-size="8" fill="{SOFT}"'
                    f' letter-spacing="1.4"'
                )
                t = t.upper()
            else:
                raise ValueError(s)
            self.nodes.append(
                f'<text x="{cx}" y="{ty + lh - 5}" {el} text-anchor="middle">{esc(t)}</text>'
            )
            ty += lh
        return cx, cy, w, h

    def diamond(self, cx, cy, half_w, half_h, lines, focal=True):
        pts = f"{cx},{cy - half_h} {cx + half_w},{cy} {cx},{cy + half_h} {cx - half_w},{cy}"
        stroke, fill, sw = (ACCENT, "rgba(235,108,54,0.08)", 1.2) if focal else (INK, WHITE, 1)
        self.nodes.append(
            f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
        )
        ty = cy - len(lines) * 14 / 2
        for t in lines:
            self.nodes.append(
                f'<text x="{cx}" y="{ty + 11}" font-family="{SANS}" font-size="11"'
                f' font-weight="600" fill="{INK}" text-anchor="middle">{esc(t)}</text>'
            )
            ty += 14

    def svg(self):
        body = "\n".join(self.edges + self.nodes + self.labels)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}"'
            f' viewBox="0 0 {self.w} {self.h}" role="img" font-family="{SANS}">\n'
            f'<defs><marker id="arr" viewBox="0 0 8 8" refX="7" refY="4"'
            f' markerWidth="7" markerHeight="7" orient="auto">'
            f'<polygon points="0 0, 8 3, 0 6" fill="{MUTED}"/>'
            f"</marker></defs>\n"
            f'<rect width="{self.w}" height="{self.h}" fill="{PAPER}"/>\n{body}\n</svg>\n'
        )


def chain(c, nodes, y, labels=None):
    """Horizontal chain: nodes = [(cx, w)], arrows between consecutive."""
    for i in range(len(nodes) - 1):
        cx, w = nodes[i]
        nx, nw = nodes[i + 1]
        c.edge([(cx + w / 2, y), (nx - nw / 2 - 2, y)])
        if labels and labels[i]:
            mid = (cx + w / 2 + nx - nw / 2) / 2
            c.edge_label(mid, y - 6, labels[i])




def build_p1(c):
    c.eyebrow(48, 40, "no cost sensitivity")
    c.box(108, 96, [("title", "Free evidence"), ("mono", "E1 · E2")], w=120)
    c.box(276, 96, [("title", "Bayes update"), ("sub", "→ posterior")], w=128)
    c.box(448, 96, [("title", "argmax state")], w=116)
    c.box(624, 96, [("title", "state → action map")], w=156)
    chain(c, [(108, 120), (276, 128), (448, 116), (624, 156)], 96)
    return c
















def build_e1_pipeline(c):
    steps = [
        ("Checkout", None),
        ("Env setup", "setup-python"),
        ("Install", "pip · poetry"),
        ("Build", "compile"),
        ("Test", "pytest"),
        ("Lint / audit", "ruff · bandit"),
    ]
    centers = [100 + i * 132 for i in range(6)]
    for cx, (title, sub) in zip(centers, steps):
        lines = [("title", title)] + ([("mono", sub)] if sub else [])
        c.box(cx, 88, lines, w=104, h=52)
    for i in range(5):
        c.edge([(centers[i] + 52, 88), (centers[i + 1] - 54, 88)])
    c.box(430, 296, [("title", "Observed outcome")], w=176, kind="capsule")
    fails = [(364, 196, 390, "fails here → A"), (628, 220, 430, "fails here → C"), (760, 244, 470, "fails here → D")]
    for cx, rail_y, entry_x, label in fails:
        c.edge([(cx, 114), (cx, rail_y), (entry_x, rail_y), (entry_x, 266)], dashed=True)
    c.edge_label(372, 192, "fails here → A", anchor="start")
    c.edge_label(512, 214, "fails here → C")
    c.edge_label(588, 238, "fails here → D")
    return c


def build_e2_changed_files(c):
    c.box(160, 216, [("mono", "changed_files"), ("sub", "fix commit diff")], w=176)
    rows = [
        ("ci", ".github/ · Dockerfile · .python-version · *.yml"),
        ("config", "pyproject.toml · requirements.txt · poetry.lock"),
        ("test", "tests/ · test_*.py · *_test.py"),
        ("doc", ".rst · .md · .txt"),
        ("src", "*.py · *.pyi (not test/config/ci/doc)"),
        ("mixed", "2+ categories present"),
        ("none", "empty list"),
    ]
    c.edge([(248, 216), (288, 216)], arrow=False)
    c.edge([(288, 72), (288, 360)], arrow=False)
    for i, (tag, examples) in enumerate(rows):
        y = 52 + i * 48
        cy = y + 20
        c.box(496, cy, [], w=352, h=40)
        c.edge([(288, cy), (316, cy)])
        c.labels.append(
            f'<text x="336" y="{cy + 3}" font-family="{MONO}" font-size="9" font-weight="600"'
            f' fill="{INK}">{esc(tag)}</text>'
        )
        c.labels.append(
            f'<text x="416" y="{cy + 3}" font-family="{MONO}" font-size="8"'
            f' fill="{SOFT}">{esc(examples)}</text>'
        )
    return c


def build_expected_cost(c):
    c.box(616, 56, [("title", "CI failure")], w=136, kind="capsule")
    c.box(616, 136, [("title", "Bayesian update")], w=152)
    c.box(616, 216, [("title", "Posterior probabilities")], w=192)
    groups = [("p_code", "P(S1)+P(S2)+P(S4)"), ("p_dep", "P(S3)"), ("p_other", "P(S5)+P(S6)+P(S7)")]
    for cx, (name, expr) in zip([368, 616, 864], groups):
        c.box(cx, 312, [("mono", name), ("mono", expr)], w=208)
    c.box(616, 400, [("title", "Expected cost of each action")], w=228)
    formulas = [
        "EC(Fix code) = p_code×8.33 + (1−p_code)×75.07",
        "EC(Fix dep) = p_dep×8.33 + (1−p_dep)×75.07",
        "EC(Escalate) = $50.00",
    ]
    for cx, f in zip([316, 616, 916], formulas):
        c.box(cx, 488, [("formula", f)], w=276, h=36)
    c.diamond(616, 608, 104, 48, ["Lowest", "expected cost?"])
    c.box(316, 728, [("title", "Fix code")], w=104, kind="capsule")
    c.box(616, 728, [("title", "Escalate")], w=112, kind="capsule")
    c.box(916, 728, [("title", "Fix dependency")], w=152, kind="capsule")

    c.edge([(616, 80), (616, 110)])
    c.edge([(616, 158), (616, 194)])
    for cx in [368, 616, 864]:
        c.edge([(616, 238), (616, 260), (cx, 260), (cx, 288)])
        c.edge([(cx, 336), (cx, 356), (616, 356), (616, 378)])
        c.edge([(616, 422), (616, 444), (cx, 444), (cx, 470)])
    c.edge([(512, 608), (316, 608), (316, 702)])
    c.edge([(720, 608), (916, 608), (916, 702)])
    c.edge([(616, 656), (616, 702)])

    # break-even threshold annotation feeding the two repair-cost formulas
    c.box(104, 488, [("mono", "p* ≈ 37.5%"), ("sub", "break-even")], w=88, kind="optional")
    c.edge([(148, 488), (174, 488)], dashed=True)
    c.jump_edge([(124, 512), (124, 536), (616, 536), (616, 508)], jump_x=316, dashed=True)
    return c


BUILDERS = {
    "p1-belief-only": build_p1,
    "e1-pipeline": build_e1_pipeline,
    "e2-changed-files": build_e2_changed_files,
    "expected-cost-flow": build_expected_cost,
}

SIZES = {
    "p1-belief-only": (796, 176),
    "e1-pipeline": (860, 372),
    "e2-changed-files": (720, 428),
    "expected-cost-flow": (1120, 800),
}


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    for name, build in BUILDERS.items():
        w, h = SIZES[name]
        svg = build(Canvas(w, h)).svg()
        with open(os.path.join(out_dir, f"{name}.svg"), "w") as f:
            f.write(svg)
        print(f"wrote {name}.svg")


if __name__ == "__main__":
    main()
