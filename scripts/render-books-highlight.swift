import AppKit
import Foundation

let root = "/Users/binopereira/Desktop/Site SabinoPereira.com/sabinopereira.com"
let output = root + "/social-media/highlights/books"
try FileManager.default.createDirectory(atPath: output, withIntermediateDirectories: true)

let W: CGFloat = 1080
let H: CGFloat = 1920
let paper = NSColor(calibratedRed: 0.91, green: 0.87, blue: 0.79, alpha: 1)
let ink = NSColor(calibratedRed: 0.08, green: 0.075, blue: 0.07, alpha: 1)
let red = NSColor(calibratedRed: 0.42, green: 0.075, blue: 0.055, alpha: 1)
let muted = NSColor(calibratedRed: 0.25, green: 0.23, blue: 0.20, alpha: 1)

func font(_ size: CGFloat, _ weight: NSFont.Weight = .regular, serif: Bool = false) -> NSFont {
    if serif { return NSFont(name: "Baskerville", size: size) ?? NSFont.systemFont(ofSize: size, weight: weight) }
    return NSFont.monospacedSystemFont(ofSize: size, weight: weight)
}

func text(_ value: String, rect: NSRect, size: CGFloat, color: NSColor = ink, weight: NSFont.Weight = .regular, align: NSTextAlignment = .left, serif: Bool = false, spacing: CGFloat = 6) {
    let p = NSMutableParagraphStyle(); p.alignment = align; p.lineSpacing = spacing
    value.draw(with: rect, options: [.usesLineFragmentOrigin, .usesFontLeading], attributes: [
        .font: font(size, weight, serif: serif), .foregroundColor: color, .paragraphStyle: p
    ])
}

func base() {
    paper.setFill(); NSRect(x: 0, y: 0, width: W, height: H).fill()
    for i in 0..<2500 {
        let x = CGFloat((i * 73) % 1080), y = CGFloat((i * 137) % 1920)
        let a = CGFloat((i % 9) + 2) / 100.0
        NSColor(calibratedWhite: i % 3 == 0 ? 0.15 : 0.85, alpha: a).setFill()
        NSRect(x: x, y: y, width: 1.2, height: 1.2).fill()
    }
    red.withAlphaComponent(0.92).setFill(); NSRect(x: 0, y: H - 22, width: W, height: 22).fill()
    red.withAlphaComponent(0.92).setFill(); NSRect(x: 0, y: 0, width: W, height: 18).fill()
}

func brand() {
    text("RB", rect: NSRect(x: 70, y: 1730, width: 150, height: 100), size: 72, color: red, weight: .bold, serif: true)
    text("REIRA BIN", rect: NSRect(x: 190, y: 1748, width: 450, height: 70), size: 28, color: ink, weight: .semibold)
    text("BOOKS BY SABINO PEREIRA", rect: NSRect(x: 610, y: 1752, width: 400, height: 55), size: 18, color: muted, align: .right)
    ink.withAlphaComponent(0.35).setFill(); NSRect(x: 70, y: 1710, width: 940, height: 2).fill()
}

func tag(_ value: String, y: CGFloat) {
    let rect = NSRect(x: 70, y: y, width: 420, height: 56)
    red.setFill(); NSBezierPath(roundedRect: rect, xRadius: 4, yRadius: 4).fill()
    text(value.uppercased(), rect: NSRect(x: 90, y: y + 10, width: 380, height: 36), size: 20, color: paper, weight: .bold)
}

func cover(_ path: String, rect: NSRect) {
    guard let image = NSImage(contentsOfFile: path) else { return }
    NSGraphicsContext.current?.cgContext.setShadow(offset: CGSize(width: 12, height: -14), blur: 28, color: NSColor.black.withAlphaComponent(0.38).cgColor)
    image.draw(in: rect, from: .zero, operation: .sourceOver, fraction: 1)
    NSGraphicsContext.current?.cgContext.setShadow(offset: .zero, blur: 0, color: nil)
}

func save(_ name: String, drawing: () -> Void) {
    let image = NSImage(size: NSSize(width: W, height: H))
    image.lockFocus(); drawing(); image.unlockFocus()
    let rep = NSBitmapImageRep(data: image.tiffRepresentation!)!
    let data = rep.representation(using: .png, properties: [:])!
    try! data.write(to: URL(fileURLWithPath: output + "/" + name))
}

save("00-books-highlight-cover.png") {
    base()
    text("RB", rect: NSRect(x: 0, y: 1175, width: W, height: 220), size: 180, color: red, weight: .bold, align: .center, serif: true)
    text("BOOKS", rect: NSRect(x: 0, y: 905, width: W, height: 190), size: 118, color: ink, weight: .bold, align: .center, serif: true)
    red.setFill(); NSRect(x: 330, y: 865, width: 420, height: 12).fill()
    text("STORIES WITH A PULSE", rect: NSRect(x: 0, y: 740, width: W, height: 80), size: 30, color: muted, weight: .semibold, align: .center)
}

save("01-books-with-a-pulse.png") {
    base(); brand(); tag("Enter the library", y: 1550)
    text("Books with\na pulse.", rect: NSRect(x: 70, y: 1120, width: 940, height: 360), size: 116, color: ink, weight: .bold, serif: true, spacing: 2)
    text("Thirteen front doors.", rect: NSRect(x: 75, y: 970, width: 900, height: 90), size: 46, color: red, weight: .bold)
    text("Choose what you need today.", rect: NSRect(x: 75, y: 850, width: 900, height: 80), size: 34, color: muted)
    text("CONFESSION  ·  STRATEGY  ·  HEALING  ·  REFLECTION  ·  SATIRE", rect: NSRect(x: 75, y: 520, width: 900, height: 180), size: 25, color: ink, weight: .semibold, align: .center, spacing: 18)
    text("SWIPE TO CHOOSE YOUR DOOR  →", rect: NSRect(x: 0, y: 185, width: W, height: 70), size: 24, color: red, weight: .bold, align: .center)
}

save("02-bad-girl-gospel.png") {
    base(); brand(); tag("I want confession", y: 1550)
    cover(root + "/images/bad-girl-gospel-book-cover.jpg", rect: NSRect(x: 105, y: 620, width: 430, height: 645))
    text("START WITH\nSELAH.", rect: NSRect(x: 585, y: 1040, width: 400, height: 220), size: 60, color: ink, weight: .bold, serif: true)
    text("BAD GIRL\nGOSPEL", rect: NSRect(x: 585, y: 865, width: 400, height: 150), size: 38, color: red, weight: .bold)
    text("Four confessions.\nOne spiritual noir world.", rect: NSRect(x: 585, y: 690, width: 400, height: 140), size: 27, color: muted, spacing: 10)
    text("THE CLEAREST FIRST DOOR INTO THE FICTION UNIVERSE.", rect: NSRect(x: 95, y: 410, width: 890, height: 120), size: 24, color: ink, weight: .semibold, align: .center)
    text("READ THE BOOK  →", rect: NSRect(x: 0, y: 180, width: W, height: 55), size: 20, color: red, weight: .semibold, align: .center)
}

save("03-chess-on-the-block.png") {
    base(); brand(); tag("I want strategy", y: 1550)
    cover(root + "/books/chess-in-the-block/cover/chess-on-the-block-directors-cut-web.jpg", rect: NSRect(x: 105, y: 610, width: 430, height: 688))
    text("MOVE IN\nSILENCE.", rect: NSRect(x: 585, y: 1050, width: 410, height: 210), size: 60, color: ink, weight: .bold, serif: true)
    text("CHESS ON\nTHE BLOCK", rect: NSRect(x: 585, y: 860, width: 410, height: 160), size: 37, color: red, weight: .bold)
    text("Pressure, survival,\nand emotional discipline.", rect: NSRect(x: 585, y: 670, width: 405, height: 150), size: 27, color: muted, spacing: 10)
    text("A DIRECTOR'S CUT ABOUT MOVING WITHOUT LOSING YOURSELF.", rect: NSRect(x: 95, y: 400, width: 890, height: 120), size: 24, color: ink, weight: .semibold, align: .center)
    text("READ THE BOOK  →", rect: NSRect(x: 0, y: 180, width: W, height: 55), size: 20, color: red, weight: .semibold, align: .center)
}

save("04-built-by-grace.png") {
    base(); brand(); tag("I want healing", y: 1550)
    cover(root + "/images/built-by-grace-cover.jpg", rect: NSRect(x: 80, y: 665, width: 500, height: 500))
    text("RETURN TO\nGRACE.", rect: NSRect(x: 620, y: 1015, width: 380, height: 210), size: 58, color: ink, weight: .bold, serif: true)
    text("BUILT BY\nGRACE", rect: NSRect(x: 620, y: 835, width: 380, height: 150), size: 38, color: red, weight: .bold)
    text("Prayer, home, repair,\nand spiritual grounding.", rect: NSRect(x: 620, y: 650, width: 370, height: 150), size: 26, color: muted, spacing: 10)
    text("A BOOK AND ALBUM JOURNEY ABOUT HEALING, LOVE AND GOD IN THE CENTER.", rect: NSRect(x: 95, y: 400, width: 890, height: 125), size: 24, color: ink, weight: .semibold, align: .center)
    text("READ THE BOOK  →", rect: NSRect(x: 0, y: 180, width: W, height: 55), size: 20, color: red, weight: .semibold, align: .center)
}

save("05-more-worlds.png") {
    base(); brand(); tag("More ways in", y: 1550)
    text("NOT EVERY BOOK\nASKS THE SAME\nQUESTION.", rect: NSRect(x: 70, y: 1110, width: 940, height: 380), size: 75, color: ink, weight: .bold, serif: true, spacing: 4)
    text("QUIET STRENGTH", rect: NSRect(x: 90, y: 895, width: 420, height: 60), size: 29, color: red, weight: .bold)
    text("MEMORY & HOME", rect: NSRect(x: 570, y: 895, width: 420, height: 60), size: 29, color: red, weight: .bold)
    text("HEALING & REFLECTION", rect: NSRect(x: 90, y: 750, width: 420, height: 80), size: 29, color: red, weight: .bold)
    text("SOCIAL SATIRE", rect: NSRect(x: 570, y: 750, width: 420, height: 80), size: 29, color: red, weight: .bold)
    text("PSYCHOLOGICAL FICTION", rect: NSRect(x: 90, y: 605, width: 420, height: 80), size: 29, color: red, weight: .bold)
    text("DIGITAL WELLBEING", rect: NSRect(x: 570, y: 605, width: 420, height: 80), size: 29, color: red, weight: .bold)
    text("Every world has its own door.", rect: NSRect(x: 0, y: 330, width: W, height: 90), size: 38, color: muted, align: .center, serif: true)
}

save("06-open-the-shelf.png") {
    base(); brand(); tag("I want everything", y: 1550)
    text("OPEN THE\nSHELF.", rect: NSRect(x: 70, y: 1110, width: 940, height: 350), size: 120, color: ink, weight: .bold, align: .center, serif: true, spacing: 0)
    text("The full catalogue stays one click away.", rect: NSRect(x: 110, y: 930, width: 860, height: 100), size: 34, color: muted, align: .center)
    red.setFill(); NSBezierPath(roundedRect: NSRect(x: 180, y: 650, width: 720, height: 130), xRadius: 8, yRadius: 8).fill()
    text("EXPLORE ALL BOOKS", rect: NSRect(x: 190, y: 685, width: 700, height: 65), size: 36, color: paper, weight: .bold, align: .center)
    text("OPEN THE FULL SHELF  →", rect: NSRect(x: 120, y: 455, width: 840, height: 70), size: 24, color: red, weight: .semibold, align: .center)
    text("BOOKS BY SABINO PEREIRA", rect: NSRect(x: 0, y: 200, width: W, height: 65), size: 24, color: ink, weight: .bold, align: .center)
}

print(output)
