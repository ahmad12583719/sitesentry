"""Create a clearly labelled simulated authorized-target SiteSentry walkthrough GIF."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUTPUT = Path(__file__).resolve().parents[1] / "docs" / "assets" / "sitesentry-authorized-demo.gif"
SIZE = (960, 540)
INK = "#0B1C1E"
PAPER = "#EDF6F3"
PANEL = "#132D2F"
TEAL = "#0B8F83"
PALE_TEAL = "#9BE0D4"
MUTED = "#789A94"
AMBER = "#C88B26"
RED = "#C7503D"


def font(size: int, bold: bool = False):
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(path, size)


def canvas(step: str):
    image = Image.new("RGB", SIZE, PAPER)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, SIZE[0], 48), fill=INK)
    draw.ellipse((24, 18, 34, 28), fill=TEAL)
    draw.text((48, 14), "SITESENTRY  /  SIMULATED AUTHORIZED-TARGET DEMO", font=font(14, True), fill=PALE_TEAL)
    draw.text((760, 16), step, font=font(11, True), fill="#A5C5BE")
    draw.text((36, 76), "DEMO ONLY — uses fictional authorized target and illustrative results", font=font(11, True), fill=TEAL)
    return image, draw


def terminal_frame():
    image, draw = canvas("01 / INSTALL")
    draw.rounded_rectangle((36, 115, 924, 470), radius=6, fill=INK)
    draw.rectangle((36, 115, 924, 153), fill="#173638")
    draw.ellipse((56, 128, 66, 138), fill=RED)
    draw.ellipse((74, 128, 84, 138), fill=AMBER)
    draw.ellipse((92, 128, 102, 138), fill=TEAL)
    lines = [
        "$ git clone https://github.com/<your-username>/sitesentry.git",
        "Cloning into 'sitesentry'...",
        "$ cd sitesentry",
        "$ ./install.sh",
        "SiteSentry is installed.",
        "Start it with: .venv/bin/python backend/app.py",
        "Then open http://127.0.0.1:5123",
    ]
    for index, line in enumerate(lines):
        color = PALE_TEAL if line.startswith("$") else "#DCECE8"
        draw.text((68, 183 + index * 35), line, font=font(19, line.startswith("$")), fill=color)
    return image


def login_frame():
    image, draw = canvas("02 / LOCAL LOGIN")
    draw.rectangle((0, 48, 190, 540), fill=INK)
    draw.text((35, 96), "SiteSentry", font=font(22, True), fill="#EFFAF7")
    draw.text((35, 128), "PRIVATE LOCAL\nINSPECTION", font=font(11, True), fill=TEAL, spacing=5)
    draw.rounded_rectangle((308, 116, 760, 458), radius=4, fill="#FFFFFF", outline="#B8D0C8", width=2)
    draw.text((346, 152), "Create your local credential", font=font(26, True), fill=INK)
    draw.text((346, 207), "Username", font=font(13, True), fill=MUTED)
    draw.rectangle((346, 230, 722, 276), outline="#A9C4BC", width=2)
    draw.text((360, 244), "site-operator", font=font(16), fill="#47635D")
    draw.text((346, 303), "Password", font=font(13, True), fill=MUTED)
    draw.rectangle((346, 326, 722, 372), outline="#A9C4BC", width=2)
    draw.text((360, 340), "••••••••••••••", font=font(16), fill="#47635D")
    draw.rectangle((346, 397, 722, 438), fill=TEAL)
    draw.text((430, 409), "CREATE LOCAL CREDENTIAL", font=font(14, True), fill="white")
    return image


def target_frame():
    image, draw = canvas("03 / AUTHORIZE")
    draw.rectangle((0, 48, 188, 540), fill=INK)
    draw.text((35, 94), "01  LAUNCH", font=font(12, True), fill=PALE_TEAL)
    draw.text((35, 123), "02  POSTURE", font=font(12, True), fill=MUTED)
    draw.text((35, 152), "03  EVIDENCE", font=font(12, True), fill=MUTED)
    draw.text((242, 116), "Open the aperture.", font=font(42, True), fill=INK)
    draw.text((242, 164), "Read the perimeter.", font=font(42, True), fill=TEAL)
    draw.rounded_rectangle((242, 240, 768, 410), radius=4, fill="white", outline="#AFCBC4", width=2)
    draw.text((270, 267), "WEBSITE DOMAIN OR URL", font=font(11, True), fill=TEAL)
    draw.rectangle((270, 294, 570, 340), outline="#A8C2BA", width=2)
    draw.text((286, 308), "demo-authorized.example", font=font(16), fill="#46645E")
    draw.rectangle((588, 294, 738, 340), fill=TEAL)
    draw.text((611, 308), "RUN SCAN  ↗", font=font(13, True), fill="white")
    draw.rectangle((270, 362, 287, 379), fill=TEAL)
    draw.text((298, 361), "I am authorized to inspect this target.", font=font(13), fill="#4C6862")
    return image


def scan_frame():
    image, draw = canvas("04 / SCAN")
    draw.rectangle((0, 48, 190, 540), fill=INK)
    draw.text((35, 96), "SCANNING", font=font(13, True), fill=PALE_TEAL)
    draw.text((258, 140), "Reading a simulated authorized target…", font=font(31, True), fill=INK)
    for radius, color, start, end in [(146, "#BDEBE2", 20, 320), (110, TEAL, 80, 360), (72, PALE_TEAL, 150, 300)]:
        draw.arc((480 - radius, 320 - radius, 480 + radius, 320 + radius), start, end, fill=color, width=12)
    draw.rectangle((464, 304, 496, 336), fill=INK)
    draw.rectangle((474, 314, 486, 326), fill=TEAL)
    draw.line((270, 445, 690, 445), fill="#B1C8C1", width=8)
    draw.line((270, 445, 548, 445), fill=TEAL, width=8)
    draw.text((270, 468), "TLS · HEADERS · COMMON PORTS · WEB EXPOSURE", font=font(12, True), fill=MUTED)
    return image


def report_frame():
    image, draw = canvas("05 / REPORT")
    draw.rectangle((0, 48, 190, 540), fill=INK)
    draw.text((35, 96), "03  EVIDENCE", font=font(12, True), fill=PALE_TEAL)
    draw.text((242, 100), "Security posture / demo-authorized.example", font=font(13, True), fill=TEAL)
    draw.ellipse((260, 140, 410, 290), outline=TEAL, width=16)
    draw.text((302, 160), "B", font=font(95, True), fill=INK)
    draw.text((440, 170), "82", font=font(44, True), fill=INK)
    draw.text((514, 190), "/100", font=font(15), fill=MUTED)
    draw.text((440, 220), "3 observations\nneed attention", font=font(14), fill=MUTED, spacing=5)
    findings = [(RED, "HIGH / TLS", "Certificate renewal window is approaching"), (AMBER, "MEDIUM / HEADERS", "Content-Security-Policy is missing"), (AMBER, "MEDIUM / PORT", "Port 3306 is reachable — MySQL")]
    for index, (color, meta, title) in enumerate(findings):
        y = 335 + index * 55
        draw.rectangle((242, y, 250, y + 8), fill=color)
        draw.text((267, y - 3), meta, font=font(10, True), fill=MUTED)
        draw.text((267, y + 13), title, font=font(15, True), fill=INK)
    draw.text((242, 508), "SIMULATED REPORT — illustrative findings only", font=font(10, True), fill=TEAL)
    return image


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frames = [terminal_frame(), login_frame(), target_frame(), scan_frame(), report_frame()]
    frames[0].save(OUTPUT, save_all=True, append_images=frames[1:], duration=[1400, 1200, 1300, 1200, 1700], loop=0, optimize=True)
    step_files = [
        "01-clone-and-install.png",
        "02-create-local-credential.png",
        "03-authorize-target.png",
        "04-scanning-target.png",
        "05-graded-report.png",
    ]
    for frame, filename in zip(frames, step_files):
        frame.save(OUTPUT.parent / filename, optimize=True)
    frames[2].save(
        OUTPUT.parent / "sitesentry-scan-to-report.gif",
        save_all=True,
        append_images=[frames[3], frames[4]],
        duration=[1100, 1100, 1800],
        loop=0,
        optimize=True,
    )
    print(f"Created {OUTPUT} ({OUTPUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
