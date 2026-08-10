import AppKit
import Foundation

let root = "/Users/binopereira/Desktop/Site SabinoPereira.com/sabinopereira.com"
let output = root + "/social-media/highlights/music"
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
    text("MUSIC BY REIRA BIN", rect: NSRect(x: 610, y: 1752, width: 400, height: 55), size: 18, color: muted, align: .right)
    ink.withAlphaComponent(0.35).setFill(); NSRect(x: 70, y: 1710, width: 940, height: 2).fill()
}

func tag(_ value: String, y: CGFloat) {
    let rect = NSRect(x: 70, y: y, width: 440, height: 56)
    red.setFill(); NSBezierPath(roundedRect: rect, xRadius: 4, yRadius: 4).fill()
    text(value.uppercased(), rect: NSRect(x: 90, y: y + 10, width: 400, height: 36), size: 20, color: paper, weight: .bold)
}

func artwork(_ path: String, rect: NSRect) {
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

save("00-music-highlight-cover.png") {
    base()
    text("RB", rect: NSRect(x: 0, y: 1175, width: W, height: 220), size: 180, color: red, weight: .bold, align: .center, serif: true)
    text("MUSIC", rect: NSRect(x: 0, y: 905, width: W, height: 190), size: 118, color: ink, weight: .bold, align: .center, serif: true)
    red.setFill(); NSRect(x: 330, y: 865, width: 420, height: 12).fill()
    text("STORIES YOU CAN HEAR", rect: NSRect(x: 0, y: 740, width: W, height: 80), size: 30, color: muted, weight: .semibold, align: .center)
}

save("01-another-door.png") {
    base(); brand(); tag("Enter through sound", y: 1550)
    text("MUSIC IS\nANOTHER DOOR.", rect: NSRect(x: 70, y: 1110, width: 940, height: 360), size: 100, color: ink, weight: .bold, serif: true, spacing: 2)
    text("Some stories are read.", rect: NSRect(x: 75, y: 920, width: 900, height: 80), size: 42, color: red, weight: .bold)
    text("Others arrive as rhythm, memory and voice.", rect: NSRect(x: 75, y: 750, width: 900, height: 130), size: 33, color: muted, spacing: 12)
    text("R&B  ·  GOSPEL  ·  LATIN  ·  STORY-DRIVEN SOUND", rect: NSRect(x: 80, y: 505, width: 920, height: 120), size: 25, color: ink, weight: .semibold, align: .center, spacing: 18)
    text("PRESS PLAY  →", rect: NSRect(x: 0, y: 190, width: W, height: 60), size: 24, color: red, weight: .bold, align: .center)
}

save("02-impossible-to-leave.png") {
    base(); brand(); tag("Start here", y: 1550)
    artwork("/Users/binopereira/Desktop/Impossible to Leave/Impossible to Leave - Cover Art.jpg", rect: NSRect(x: 80, y: 650, width: 540, height: 540))
    text("HARD TO\nIGNORE.", rect: NSRect(x: 660, y: 1040, width: 350, height: 200), size: 58, color: ink, weight: .bold, serif: true)
    text("IMPOSSIBLE\nTO LEAVE", rect: NSRect(x: 660, y: 845, width: 350, height: 170), size: 34, color: red, weight: .bold)
    text("Desire, tension,\nand no easy exit.", rect: NSRect(x: 660, y: 675, width: 350, height: 140), size: 27, color: muted, spacing: 10)
    text("THE CLEAREST FIRST DOOR INTO THE R&B SIDE OF REIRA BIN.", rect: NSRect(x: 95, y: 420, width: 890, height: 120), size: 24, color: ink, weight: .semibold, align: .center)
    text("LISTEN NOW  →", rect: NSRect(x: 0, y: 180, width: W, height: 55), size: 20, color: red, weight: .semibold, align: .center)
}

save("03-zapatillas.png") {
    base(); brand(); tag("A summer detour", y: 1550)
    artwork("/Users/binopereira/Desktop/musicas soltas verao/Zapatillas bajo la mesa - capa v2.jpg", rect: NSRect(x: 80, y: 650, width: 540, height: 540))
    text("LEAVE THE\nTABLE.", rect: NSRect(x: 660, y: 1040, width: 350, height: 200), size: 58, color: ink, weight: .bold, serif: true)
    text("ZAPATILLAS\nBAJO LA MESA", rect: NSRect(x: 660, y: 830, width: 350, height: 180), size: 31, color: red, weight: .bold)
    text("Spanish nights,\nlights and dancing.", rect: NSRect(x: 660, y: 675, width: 350, height: 140), size: 27, color: muted, spacing: 10)
    text("A VERBENA, ONE INVITATION, AND A SUMMER THAT WILL NOT WAIT.", rect: NSRect(x: 95, y: 420, width: 890, height: 120), size: 24, color: ink, weight: .semibold, align: .center)
    text("MOVE WITH IT  →", rect: NSRect(x: 0, y: 180, width: W, height: 55), size: 20, color: red, weight: .semibold, align: .center)
}

save("04-built-by-grace.png") {
    base(); brand(); tag("When books become sound", y: 1550)
    artwork(root + "/books/built-by-grace-premium/assets/built-by-grace-album-cover.jpg", rect: NSRect(x: 80, y: 650, width: 540, height: 540))
    text("ONE WORLD.\nTWO FORMS.", rect: NSRect(x: 660, y: 1040, width: 350, height: 200), size: 54, color: ink, weight: .bold, serif: true)
    text("BUILT BY\nGRACE", rect: NSRect(x: 660, y: 845, width: 350, height: 170), size: 36, color: red, weight: .bold)
    text("A book journey\nexpanded through music.", rect: NSRect(x: 660, y: 660, width: 350, height: 160), size: 26, color: muted, spacing: 10)
    text("PRAYER, HEALING, LOVE, HOME — WITH GOD IN THE CENTER.", rect: NSRect(x: 95, y: 420, width: 890, height: 120), size: 24, color: ink, weight: .semibold, align: .center)
    text("ENTER THE WORLD  →", rect: NSRect(x: 0, y: 180, width: W, height: 55), size: 20, color: red, weight: .semibold, align: .center)
}

save("05-find-the-music.png") {
    base(); brand(); tag("Choose your platform", y: 1550)
    text("FIND REIRA BIN\nWHERE YOU LISTEN.", rect: NSRect(x: 70, y: 1120, width: 940, height: 330), size: 82, color: ink, weight: .bold, align: .center, serif: true, spacing: 3)
    text("SPOTIFY", rect: NSRect(x: 120, y: 820, width: 840, height: 80), size: 44, color: red, weight: .bold, align: .center)
    text("APPLE MUSIC", rect: NSRect(x: 120, y: 680, width: 840, height: 80), size: 44, color: red, weight: .bold, align: .center)
    text("YOUTUBE", rect: NSRect(x: 120, y: 540, width: 840, height: 80), size: 44, color: red, weight: .bold, align: .center)
    text("ONE ARTIST. MANY DOORS.", rect: NSRect(x: 0, y: 300, width: W, height: 70), size: 28, color: muted, weight: .semibold, align: .center)
}

save("06-listen-to-reira-bin.png") {
    base(); brand(); tag("Keep listening", y: 1550)
    text("LISTEN TO\nREIRA BIN.", rect: NSRect(x: 70, y: 1110, width: 940, height: 350), size: 112, color: ink, weight: .bold, align: .center, serif: true, spacing: 0)
    text("Songs with stories inside them.", rect: NSRect(x: 110, y: 925, width: 860, height: 100), size: 34, color: muted, align: .center)
    red.setFill(); NSBezierPath(roundedRect: NSRect(x: 180, y: 650, width: 720, height: 130), xRadius: 8, yRadius: 8).fill()
    text("OPEN THE MUSIC", rect: NSRect(x: 190, y: 685, width: 700, height: 65), size: 36, color: paper, weight: .bold, align: .center)
    text("PLAY. SAVE. SHARE.  →", rect: NSRect(x: 120, y: 455, width: 840, height: 70), size: 24, color: red, weight: .semibold, align: .center)
    text("MUSIC BY REIRA BIN", rect: NSRect(x: 0, y: 200, width: W, height: 65), size: 24, color: ink, weight: .bold, align: .center)
}

print(output)
