"""Generates 8 High-Resolution (1920x1080, 16:9) Slide Visuals & PDF Deck for Colossyan Studio.

Each slide is designed specifically for the Colossyan Creator canvas:
- Left 66% (x: 0..1290): High-contrast Cisco Dark Glassmorphism UI mockups, vector diagrams, and callouts.
- Right 34% (x: 1320..1920): Dedicated Avatar Safe Zone so the Colossyan AI presenter never overlaps text.
- Uses pure vector shapes & standard glyphs (zero missing emoji boxes).
- Outputs individual PNGs (scene_01.png .. scene_08.png) + a combined multi-page PDF (cisco_colossyan_8_scenes_deck.pdf)
  ready for 1-click "Import PDF" in Colossyan Creator.
"""

import pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = ROOT_DIR / "app" / "static" / "colossyan_slides"

W, H = 1920, 1080

# Colors (Cisco Dark Glassmorphism Palette)
BG_DARK = (6, 13, 25)
BG_CARD = (13, 25, 48)
BG_CARD_ALT = (19, 36, 66)
BG_TERMINAL = (4, 9, 18)
CYAN = (0, 188, 235)
BLUE = (4, 159, 217)
EMERALD = (16, 185, 129)
ROSE = (244, 63, 94)
AMBER = (245, 158, 11)
TEXT_WHITE = (248, 250, 252)
TEXT_MUTED = (148, 163, 184)
BORDER_SUBTLE = (45, 65, 95)


def get_font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    """Loads Windows system fonts (Segoe UI / Consolas / Arial) with fallback."""
    if mono:
        candidates = ["consolab.ttf" if bold else "consola.ttf", "courbd.ttf" if bold else "cour.ttf"]
    else:
        candidates = [
            "segoeuib.ttf" if bold else "segoeui.ttf",
            "arialbd.ttf" if bold else "arial.ttf",
            "calibrib.ttf" if bold else "calibri.ttf",
        ]
    for name in candidates:
        for base in [pathlib.Path("C:/Windows/Fonts"), pathlib.Path("/usr/share/fonts")]:
            p = base / name
            if p.exists():
                try:
                    return ImageFont.truetype(str(p), size)
                except Exception:
                    pass
    return ImageFont.load_default()


def draw_arrow(d: ImageDraw.ImageDraw, x1: int, y: int, x2: int, color: tuple[int, int, int]) -> None:
    """Draws a crisp horizontal vector arrow from (x1, y) to (x2, y)."""
    head_len = 18
    shaft_end = x2 - head_len
    d.rectangle([x1, y - 4, shaft_end, y + 4], fill=color)
    d.polygon([(shaft_end, y - 14), (x2, y), (shaft_end, y + 14)], fill=color)


def create_base_canvas(scene_num: int, timecode: str, title: str, subtitle: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    """Creates a 1920x1080 base canvas with header, footer, and right-side Avatar Safe Zone."""
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    # Subtle top accent bar
    draw.rectangle([0, 0, W, 8], fill=CYAN)

    # Top Header Badges
    draw.rounded_rectangle([70, 45, 330, 92], radius=8, fill=(0, 80, 120), outline=CYAN, width=2)
    draw.text((92, 56), "CISCO SECURE ACCESS", font=get_font(20, bold=True), fill=TEXT_WHITE)

    draw.rounded_rectangle([345, 45, 640, 92], radius=8, fill=BG_CARD, outline=BORDER_SUBTLE, width=1)
    draw.text((368, 56), f"SCENE 0{scene_num}  |  {timecode}", font=get_font(20, bold=True, mono=True), fill=CYAN)

    # Main Title & Subtitle (Left 66% zone)
    draw.text((70, 118), title, font=get_font(44, bold=True), fill=TEXT_WHITE)
    draw.text((70, 178), subtitle, font=get_font(24, bold=False), fill=TEXT_MUTED)

    # Right-side Avatar Safe Zone subtle frame (x: 1340..1860)
    draw.rounded_rectangle(
        [1340, 60, 1860, 1000],
        radius=24,
        fill=(9, 19, 36),
        outline=(25, 45, 75),
        width=2,
    )
    draw.text(
        (1465, 955),
        "COLOSSYAN AVATAR ZONE",
        font=get_font(18, bold=True),
        fill=(45, 75, 110),
    )

    # Footer bar
    draw.line([(70, 1015), (1290, 1015)], fill=BORDER_SUBTLE, width=1)
    draw.text(
        (70, 1030),
        "Cisco Security Solutions Engineering  |  GenAI Governance & DLP AI Guardrails",
        font=get_font(18),
        fill=TEXT_MUTED,
    )
    return img, draw


def build_scene_1() -> Image.Image:
    img, d = create_base_canvas(
        1, "0:00 - 0:14",
        "The 9:00 AM Data Leak",
        "Well-intentioned developer pastes 200 lines of proprietary code into a public AI assistant"
    )
    # Left Box: IDE Code Editor
    d.rounded_rectangle([70, 240, 640, 740], radius=16, fill=BG_TERMINAL, outline=BORDER_SUBTLE, width=2)
    d.rounded_rectangle([70, 240, 640, 295], radius=16, fill=BG_CARD)
    d.ellipse([95, 258, 113, 276], fill=ROSE)
    d.ellipse([125, 258, 143, 276], fill=AMBER)
    d.ellipse([155, 258, 173, 276], fill=EMERALD)
    d.text((195, 253), "auth_token_service.py (PROPRIETARY)", font=get_font(18, bold=True, mono=True), fill=TEXT_WHITE)

    code_lines = [
        "104  class InternalTokenSigner:",
        "105      SECRET_SALT = 'c1sc0-pr0d-9981'",
        "106      def sign_payload(self, tenant):",
        "107          # Confidential routing logic",
        "108          digest = self.compute(tenant)",
        "109          return f'{tenant}.{digest}'",
        "110",
        "111  # [200 lines copied to clipboard...]",
    ]
    y = 325
    for line in code_lines:
        color = ROSE if "SECRET_SALT" in line else (CYAN if "class " in line or "def " in line else TEXT_MUTED)
        d.text((95, y), line, font=get_font(19, mono=True), fill=color)
        y += 42

    # Vector Arrow from IDE to Public AI Chat
    draw_arrow(d, 655, 485, 735, ROSE)

    # Right Box: Unapproved Public AI Assistant
    d.rounded_rectangle([750, 240, 1290, 740], radius=16, fill=BG_CARD, outline=ROSE, width=3)
    d.rounded_rectangle([750, 240, 1290, 295], radius=16, fill=(70, 18, 35))
    d.text((780, 253), "Public AI Assistant (Unsanctioned Cloud)", font=get_font(20, bold=True), fill=TEXT_WHITE)

    d.rounded_rectangle([780, 325, 1260, 520], radius=12, fill=BG_TERMINAL, outline=BORDER_SUBTLE, width=1)
    d.text((800, 345), "Prompt sent over HTTPS (TLS):", font=get_font(18, bold=True), fill=AMBER)
    d.text((800, 385), "\"Can you fix the bug in this auth", font=get_font(20), fill=TEXT_WHITE)
    d.text((800, 418), "service? Here is our internal code...\"", font=get_font(20), fill=TEXT_WHITE)
    d.text((800, 465), "[+ 200 lines of proprietary source code]", font=get_font(18, bold=True, mono=True), fill=ROSE)

    d.rounded_rectangle([780, 550, 1260, 705], radius=12, fill=(55, 15, 28), outline=ROSE, width=2)
    d.text((805, 575), "EXPOSURE IMPACT:", font=get_font(20, bold=True), fill=ROSE)
    d.text((805, 615), "- Stored on external vendor servers", font=get_font(20), fill=TEXT_WHITE)
    d.text((805, 650), "- Outside corporate visibility & control", font=get_font(20), fill=TEXT_WHITE)

    # Bottom Callout Banner
    d.rounded_rectangle([70, 780, 1290, 955], radius=16, fill=(55, 15, 28), outline=ROSE, width=3)
    d.rounded_rectangle([105, 808, 225, 855], radius=8, fill=ROSE)
    d.text((122, 816), "ALERT", font=get_font(24, bold=True), fill=TEXT_WHITE)
    d.text((245, 808), "\"DATA JUST LEFT THE BUILDING.\"", font=get_font(34, bold=True), fill=TEXT_WHITE)
    d.text((105, 878), "No bad intent - but proprietary intellectual property just exited your organization.", font=get_font(24), fill=(254, 205, 211))
    return img


def build_scene_2() -> Image.Image:
    img, d = create_base_canvas(
        2, "0:14 - 0:32",
        "Why Traditional Controls Fail on Shadow AI",
        "Employees using unapproved GenAI apps create blind spots that legacy security cannot stop"
    )
    cards = [
        (
            "1. Blanket Category Blocking",
            "PUSHES USERS TO PERSONAL DEVICES",
            "Blocking all 'AI / ML' domains disrupts legitimate engineering workflows and drives developers to personal laptops or mobile hotspots.",
            AMBER,
        ),
        (
            "2. Legacy Pattern-Only DLP",
            "MISSES SOURCE CODE & CONTEXT",
            "Traditional regex-based DLP looks for credit cards or SSNs - it fails to recognize proprietary source code, logic, or conversational prompts.",
            ROSE,
        ),
        (
            "3. Uninspected TLS / HTTPS Traffic",
            "COMPLETE BLINDNESS TO PROMPTS",
            "Every GenAI prompt travels inside an encrypted HTTPS session. Without TLS decryption, your DLP engine cannot see a single word.",
            CYAN,
        ),
    ]
    y = 250
    for idx, (title, badge_txt, desc, color) in enumerate(cards):
        d.rounded_rectangle([70, y, 1290, y + 215], radius=16, fill=BG_CARD, outline=color, width=3)
        d.rounded_rectangle([95, y + 25, 620, y + 70], radius=8, fill=BG_TERMINAL)
        d.text((115, y + 33), title, font=get_font(26, bold=True), fill=TEXT_WHITE)

        d.rounded_rectangle([810, y + 25, 1260, y + 70], radius=8, fill=(25, 35, 55), outline=color, width=2)
        d.text((830, y + 36), badge_txt, font=get_font(18, bold=True, mono=True), fill=color)

        words = desc.split(" ")
        mid = len(words) // 2 + 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])
        d.text((100, y + 100), line1, font=get_font(22), fill=TEXT_MUTED)
        d.text((100, y + 138), line2, font=get_font(22), fill=TEXT_MUTED)
        y += 245
    return img


def build_scene_3() -> Image.Image:
    img, d = create_base_canvas(
        3, "0:32 - 0:38",
        "Cisco Secure Access: 5-Step GenAI Governance",
        "Turning Shadow AI exposure into a structured, repeatable security architecture"
    )
    steps = [
        ("STEP 1", "DISCOVER", "AI Access Visibility &\nApp Risk Scoring", CYAN),
        ("STEP 2", "DECRYPT", "HTTPS Inspection\non Access Policy", BLUE),
        ("STEP 3", "CLASSIFY", "DLP AI Guardrails\nSource Code & PII", EMERALD),
        ("STEP 4", "ENFORCE", "Monitor or Block\nPrompts & Uploads", AMBER),
        ("STEP 5", "REFINE", "Baseline in Monitor\nThen Move to Block", ROSE),
    ]
    x = 70
    w_box = 220
    gap = 25
    for idx, (step_lbl, name, sub, col) in enumerate(steps):
        d.rounded_rectangle([x, 310, x + w_box, 720], radius=18, fill=BG_CARD, outline=col, width=3)
        d.rounded_rectangle([x + 25, 340, x + w_box - 25, 385], radius=8, fill=BG_TERMINAL)
        d.text((x + 58, 350), step_lbl, font=get_font(20, bold=True, mono=True), fill=col)

        d.text((x + 25, 430), name, font=get_font(30, bold=True), fill=TEXT_WHITE)
        d.line([(x + 25, 490), (x + w_box - 25, 490)], fill=col, width=2)

        for i, l in enumerate(sub.split("\n")):
            d.text((x + 22, 525 + i * 38), l, font=get_font(19), fill=TEXT_MUTED)

        if idx < 4:
            ax = x + w_box + 4
            d.polygon([(ax, 505), (ax + 17, 515), (ax, 525)], fill=TEXT_WHITE)
        x += w_box + gap

    d.rounded_rectangle([70, 780, 1290, 940], radius=16, fill=BG_CARD_ALT, outline=CYAN, width=2)
    d.text((110, 815), "SINGLE CONVERGED SSE WORKFLOW", font=get_font(24, bold=True), fill=CYAN)
    d.text((110, 860), "Discover  -->  Decrypt  -->  Classify  -->  Enforce  -->  Refine", font=get_font(30, bold=True, mono=True), fill=TEXT_WHITE)
    return img


def build_scene_4() -> Image.Image:
    img, d = create_base_canvas(
        4, "0:38 - 0:50",
        "Step 1 - Discover with AI Access",
        "Identify every GenAI application in use across your organization and evaluate its risk profile"
    )
    d.rounded_rectangle([70, 240, 1290, 800], radius=16, fill=BG_TERMINAL, outline=CYAN, width=2)
    d.rounded_rectangle([70, 240, 1290, 305], radius=16, fill=BG_CARD_ALT)
    d.text((105, 258), "Cisco Secure Access  >  Experience Insights  >  AI Access Dashboard", font=get_font(22, bold=True), fill=CYAN)

    d.rectangle([95, 330, 1265, 385], fill=BG_CARD)
    d.text((115, 345), "APPLICATION NAME", font=get_font(19, bold=True), fill=TEXT_MUTED)
    d.text((460, 345), "RISK SCORE", font=get_font(19, bold=True), fill=TEXT_MUTED)
    d.text((710, 345), "DATA RETENTION POLICY", font=get_font(19, bold=True), fill=TEXT_MUTED)
    d.text((1040, 345), "GOVERNANCE", font=get_font(19, bold=True), fill=TEXT_MUTED)

    rows = [
        ("CodeHelper-FreeAI", "CRITICAL (92/100)", "Trains on user prompts", "UNSANCTIONED", ROSE),
        ("PublicChat-LLM", "HIGH (78/100)", "Retains logs 30 days", "UNSANCTIONED", AMBER),
        ("DocSummarize-Cloud", "HIGH (74/100)", "No enterprise DPA", "UNSANCTIONED", AMBER),
        ("EnterpriseCopilot-Pro", "LOW (12/100)", "Zero data retention", "SANCTIONED", EMERALD),
    ]
    ry = 405
    for app_name, risk, retention, status, col in rows:
        d.rounded_rectangle([95, ry, 1265, ry + 78], radius=8, fill=(10, 20, 38), outline=BORDER_SUBTLE, width=1)
        d.text((115, ry + 24), app_name, font=get_font(22, bold=True), fill=TEXT_WHITE)
        d.text((460, ry + 24), risk, font=get_font(21, bold=True, mono=True), fill=col)
        d.text((710, ry + 24), retention, font=get_font(20), fill=TEXT_MUTED)
        d.rounded_rectangle([1035, ry + 16, 1245, ry + 62], radius=6, fill=(20, 32, 52), outline=col, width=2)
        d.text((1055, ry + 26), status, font=get_font(18, bold=True, mono=True), fill=col)
        ry += 92

    d.rounded_rectangle([70, 830, 1290, 955], radius=14, fill=BG_CARD, outline=CYAN, width=2)
    d.text((110, 855), "KEY PRINCIPLE: \"You can't govern what you can't see.\"", font=get_font(28, bold=True), fill=TEXT_WHITE)
    d.text((110, 900), "AI Access baselines Shadow AI adoption and ranks applications by data-exposure risk.", font=get_font(22), fill=TEXT_MUTED)
    return img


def build_scene_5() -> Image.Image:
    img, d = create_base_canvas(
        5, "0:50 - 1:05",
        "Step 2 - Decrypt: The Mandatory Prerequisite",
        "Prompt inspection requires HTTPS Inspection enabled on the matching Access Policy rule"
    )
    # Top Flow: Broken / Misconfigured
    d.rounded_rectangle([70, 245, 1290, 515], radius=16, fill=(40, 14, 24), outline=ROSE, width=3)
    d.text((105, 270), "[MISCONFIGURATION] HTTPS Inspection OFF -> DLP Sees Only Encrypted TLS", font=get_font(24, bold=True), fill=ROSE)

    d.rounded_rectangle([105, 335, 430, 470], radius=12, fill=BG_TERMINAL, outline=BORDER_SUBTLE, width=2)
    d.text((130, 365), "Developer Prompt", font=get_font(22, bold=True), fill=TEXT_WHITE)
    d.text((130, 405), "TLS 1.3 Encrypted", font=get_font(20, mono=True), fill=AMBER)

    draw_arrow(d, 445, 402, 520, ROSE)

    d.rounded_rectangle([535, 335, 875, 470], radius=12, fill=BG_TERMINAL, outline=ROSE, width=2)
    d.text((560, 365), "Access Policy Rule", font=get_font(22, bold=True), fill=TEXT_WHITE)
    d.text((560, 405), "Decrypt: [ DISABLED ]", font=get_font(20, bold=True, mono=True), fill=ROSE)

    draw_arrow(d, 890, 402, 965, ROSE)

    d.rounded_rectangle([980, 335, 1255, 470], radius=12, fill=BG_TERMINAL, outline=ROSE, width=2)
    d.text((1005, 365), "DLP AI Guardrails", font=get_font(22, bold=True), fill=TEXT_WHITE)
    d.text((1005, 405), "Result: 0 HITS (Blind)", font=get_font(20, bold=True, mono=True), fill=ROSE)

    # Bottom Flow: Correct Configuration
    d.rounded_rectangle([70, 555, 1290, 825], radius=16, fill=(10, 38, 35), outline=EMERALD, width=3)
    d.text((105, 580), "[CORRECT ARCHITECTURE] HTTPS Inspection ON -> Full Prompt Visibility", font=get_font(24, bold=True), fill=EMERALD)

    d.rounded_rectangle([105, 645, 430, 780], radius=12, fill=BG_TERMINAL, outline=BORDER_SUBTLE, width=2)
    d.text((130, 675), "Developer Prompt", font=get_font(22, bold=True), fill=TEXT_WHITE)
    d.text((130, 715), "Source Code Payload", font=get_font(20, mono=True), fill=CYAN)

    draw_arrow(d, 445, 712, 520, EMERALD)

    d.rounded_rectangle([535, 645, 875, 780], radius=12, fill=BG_TERMINAL, outline=EMERALD, width=2)
    d.text((560, 675), "Access Policy Rule", font=get_font(22, bold=True), fill=TEXT_WHITE)
    d.text((560, 715), "HTTPS Decrypt: [ ON ]", font=get_font(20, bold=True, mono=True), fill=EMERALD)

    draw_arrow(d, 890, 712, 965, EMERALD)

    d.rounded_rectangle([980, 645, 1255, 780], radius=12, fill=BG_TERMINAL, outline=EMERALD, width=2)
    d.text((1005, 675), "DLP AI Guardrails", font=get_font(22, bold=True), fill=TEXT_WHITE)
    d.text((1005, 715), "Prompt Inspected!", font=get_font(20, bold=True, mono=True), fill=EMERALD)

    d.rounded_rectangle([70, 855, 1290, 960], radius=12, fill=BG_CARD, outline=AMBER, width=2)
    d.text((105, 890), "FIELD TIP: If an AI Guardrails rule shows 0 hits, verify HTTPS Inspection on the Access Policy first.", font=get_font(22, bold=True), fill=AMBER)
    return img


def build_scene_6() -> Image.Image:
    img, d = create_base_canvas(
        6, "1:05 - 1:20",
        "Steps 3 & 4 - Classify and Enforce with AI Guardrails",
        "Configure a DLP AI Guardrails rule to inspect prompts, responses, and file uploads in real time"
    )
    d.rounded_rectangle([70, 240, 1290, 950], radius=16, fill=BG_TERMINAL, outline=CYAN, width=2)
    d.rounded_rectangle([70, 240, 1290, 305], radius=16, fill=BG_CARD_ALT)
    d.text((105, 258), "Cisco Secure Access  >  Data Loss Prevention Policy  >  Add AI Guardrails Rule", font=get_font(22, bold=True), fill=CYAN)

    d.text((110, 335), "1. INSPECTION SCOPE (INLINE CONTENT):", font=get_font(21, bold=True), fill=TEXT_MUTED)
    scopes = ["[ON] User Prompts", "[ON] AI Model Responses", "[ON] File Uploads"]
    sx = 110
    for sc in scopes:
        d.rounded_rectangle([sx, 375, sx + 360, 445], radius=10, fill=BG_CARD, outline=CYAN, width=2)
        d.text((sx + 25, 395), sc, font=get_font(22, bold=True, mono=True), fill=TEXT_WHITE)
        sx += 385

    d.text((110, 485), "2. SENSITIVE DATA & AI CLASSIFIERS:", font=get_font(21, bold=True), fill=TEXT_MUTED)
    classifiers = [
        ("Source Code & Proprietary Algorithms", EMERALD),
        ("API Keys, Tokens & Cloud Credentials", EMERALD),
        ("PII, Customer Records & Financial Data", CYAN),
        ("Intellectual Property & Internal Docs", CYAN),
    ]
    cy = 530
    cx = 110
    for idx, (cl_text, col) in enumerate(classifiers):
        bx = cx if idx % 2 == 0 else cx + 575
        by = cy + (idx // 2) * 85
        d.rounded_rectangle([bx, by, bx + 550, by + 68], radius=10, fill=BG_CARD, outline=col, width=2)
        d.ellipse([bx + 22, by + 25, bx + 38, by + 41], fill=col)
        d.text((bx + 52, by + 19), cl_text, font=get_font(21, bold=True), fill=TEXT_WHITE)

    d.text((110, 735), "3. ENFORCEMENT ACTION:", font=get_font(21, bold=True), fill=TEXT_MUTED)
    d.rounded_rectangle([110, 780, 660, 910], radius=12, fill=(15, 42, 38), outline=EMERALD, width=3)
    d.text((140, 800), "ACTION: MONITOR (Baseline Phase)", font=get_font(24, bold=True), fill=EMERALD)
    d.text((140, 845), "Logs full event & matched snippet without blocking user", font=get_font(19), fill=TEXT_MUTED)

    d.rounded_rectangle([700, 780, 1250, 910], radius=12, fill=(55, 16, 28), outline=ROSE, width=3)
    d.text((730, 800), "ACTION: BLOCK (Enforcement Phase)", font=get_font(24, bold=True), fill=ROSE)
    d.text((730, 845), "Intercepts prompt/upload & displays policy notification", font=get_font(19), fill=TEXT_MUTED)
    return img


def build_scene_7() -> Image.Image:
    img, d = create_base_canvas(
        7, "1:20 - 1:30",
        "Step 5 - Refine: Safe Enterprise Rollout Strategy",
        "Avoid operational friction by baselining in Monitor mode before enforcing Block"
    )
    phases = [
        (
            "PHASE 1: WEEKS 1-2",
            "Start in MONITOR Mode",
            [
                "- Deploy AI Guardrails rule in Monitor",
                "- Capture real prompt & upload telemetry",
                "- Zero disruption to engineering sprints",
            ],
            CYAN,
        ),
        (
            "PHASE 2: TUNING",
            "Tune Out False Positives",
            [
                "- Review matched snippets in DLP logs",
                "- Whitelist sanctioned coding assistants",
                "- Refine source-code classifier thresholds",
            ],
            AMBER,
        ),
        (
            "PHASE 3: PRODUCTION",
            "Enforce BLOCK Mode",
            [
                "- Switch high-risk Shadow AI apps to Block",
                "- Prevent real-time source code exfiltration",
                "- Maintain high developer trust & velocity",
            ],
            EMERALD,
        ),
    ]
    px = 70
    pw = 385
    for tag, title, bullets, col in phases:
        d.rounded_rectangle([px, 260, px + pw, 780], radius=16, fill=BG_CARD, outline=col, width=3)
        d.rounded_rectangle([px + 25, 290, px + pw - 25, 340], radius=8, fill=BG_TERMINAL)
        d.text((px + 45, 302), tag, font=get_font(20, bold=True, mono=True), fill=col)
        d.text((px + 25, 375), title, font=get_font(27, bold=True), fill=TEXT_WHITE)
        d.line([(px + 25, 435), (px + pw - 25, 435)], fill=col, width=2)

        by = 475
        for b in bullets:
            d.text((px + 25, by), b, font=get_font(20), fill=TEXT_MUTED)
            by += 75
        px += pw + 32

    d.rounded_rectangle([70, 825, 1290, 950], radius=14, fill=BG_CARD_ALT, outline=EMERALD, width=2)
    d.text((110, 868), "RESULT: High-precision data protection with near-zero false positives.", font=get_font(28, bold=True), fill=TEXT_WHITE)
    return img


def build_scene_8() -> Image.Image:
    img, d = create_base_canvas(
        8, "1:30 - 1:35",
        "Govern AI - Don't Just Block It",
        "Summary & Transition to the Interactive Branching Scenario Assessment"
    )
    d.rounded_rectangle([70, 250, 1290, 680], radius=18, fill=BG_CARD, outline=CYAN, width=3)
    d.text((115, 295), "SHADOW AI IS A DATA-EXPOSURE PROBLEM", font=get_font(34, bold=True), fill=CYAN)

    takeaways = [
        "[1] DISCOVER: Use AI Access to uncover unsanctioned GenAI apps and risk scores.",
        "[2] DECRYPT: Enable HTTPS Inspection on the Access Policy so DLP can read prompts.",
        "[3] CLASSIFY & ENFORCE: Apply DLP AI Guardrails to prompts, responses, and uploads.",
        "[4] REFINE: Baseline in Monitor mode first, tune false positives, then enforce Block.",
    ]
    ty = 380
    for t in takeaways:
        d.text((115, ty), t, font=get_font(23, bold=True), fill=TEXT_WHITE)
        ty += 68

    d.rounded_rectangle([70, 725, 1290, 950], radius=18, fill=(12, 45, 42), outline=EMERALD, width=3)
    d.text((115, 765), "NEXT UP: HANDS-ON SCENARIO CHALLENGE (ANDES FREIGHT)", font=get_font(28, bold=True), fill=EMERALD)
    d.text((115, 825), "Put this architecture into practice: Diagnose a 0-hit DLP policy and design", font=get_font(24), fill=TEXT_WHITE)
    d.text((115, 865), "a safe Monitor-to-Block rollout to earn the 'Leak Stopper' badge.", font=get_font(24), fill=TEXT_WHITE)
    return img


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    builders = [
        ("scene_01_hook.png", build_scene_1),
        ("scene_02_problem.png", build_scene_2),
        ("scene_03_framework.png", build_scene_3),
        ("scene_04_discover.png", build_scene_4),
        ("scene_05_decrypt.png", build_scene_5),
        ("scene_06_classify_enforce.png", build_scene_6),
        ("scene_07_refine.png", build_scene_7),
        ("scene_08_close.png", build_scene_8),
    ]
    images = []
    for filename, fn in builders:
        img = fn()
        out_path = OUT_DIR / filename
        img.save(out_path, format="PNG", optimize=True)
        images.append(img)
        print(f"Generated: {out_path.name} (1920x1080)")

    pdf_path = OUT_DIR / "cisco_colossyan_8_scenes_deck.pdf"
    images[0].save(
        pdf_path,
        "PDF",
        resolution=150.0,
        save_all=True,
        append_images=images[1:],
    )
    print(f"Generated combined PDF deck for 1-click Colossyan import: {pdf_path.name}")


if __name__ == "__main__":
    main()
