import AppKit

let root = "/Users/binopereira/Desktop/Site SabinoPereira.com/sabinopereira.com/social-media/templates/built-by-grace-reflections-sunday"
let sourcePath = root + "/source-built-by-grace-reflections.png"
let source = NSImage(contentsOfFile: sourcePath)!

let white = NSColor.white
let ink = NSColor(calibratedRed: 0.13, green: 0.105, blue: 0.08, alpha: 1)
let warm = NSColor(calibratedRed: 0.48, green: 0.28, blue: 0.15, alpha: 1)

func drawText(_ text: String, in rect: NSRect, font: NSFont, color: NSColor, alignment: NSTextAlignment = .left, spacing: CGFloat = 0, lineHeight: CGFloat? = nil) {
    let paragraph = NSMutableParagraphStyle()
    paragraph.alignment = alignment
    if let lineHeight { paragraph.minimumLineHeight = lineHeight; paragraph.maximumLineHeight = lineHeight }
    NSAttributedString(string: text, attributes: [
        .font: font,
        .foregroundColor: color,
        .kern: spacing,
        .paragraphStyle: paragraph
    ]).draw(with: rect, options: [.usesLineFragmentOrigin, .usesFontLeading])
}

func save(_ image: NSImage, path: String) {
    guard let tiff = image.tiffRepresentation,
          let bitmap = NSBitmapImageRep(data: tiff),
          let png = bitmap.representation(using: .png, properties: [:]) else { exit(1) }
    try! png.write(to: URL(fileURLWithPath: path))
}

func renderVertical() {
    let w: CGFloat = 1080, h: CGFloat = 1920, imageH: CGFloat = 1080
    let canvas = NSImage(size: NSSize(width: w, height: h))
    canvas.lockFocus()
    white.setFill(); NSBezierPath(rect: NSRect(x: 0, y: 0, width: w, height: h)).fill()
    source.draw(in: NSRect(x: 0, y: 0, width: w, height: imageH), from: NSRect(origin: .zero, size: source.size), operation: .sourceOver, fraction: 1, respectFlipped: false, hints: [.interpolation: NSImageInterpolation.high])
    warm.setFill(); NSBezierPath(rect: NSRect(x: 88, y: 1078, width: 80, height: 3)).fill()
    drawText("✝", in: NSRect(x: 88, y: 1730, width: 100, height: 70), font: NSFont(name: "Georgia", size: 44)!, color: warm)
    drawText("THIS SUNDAY", in: NSRect(x: 88, y: 1640, width: 800, height: 50), font: NSFont.systemFont(ofSize: 24, weight: .semibold), color: warm, spacing: 7)
    drawText("May God give rest\nto the part of you\nthat has been strong\nall week", in: NSRect(x: 88, y: 1218, width: 890, height: 350), font: NSFont(name: "Georgia", size: 61)!, color: ink, lineHeight: 76)
    drawText("REIRA BIN   ·   FAITH & GRACE", in: NSRect(x: 88, y: 1125, width: 850, height: 35), font: NSFont.systemFont(ofSize: 16, weight: .semibold), color: warm, spacing: 3)
    canvas.unlockFocus()
    save(canvas, path: root + "/built-by-grace-sunday-template-1080x1920.png")
}

func renderFeed() {
    let w: CGFloat = 1080, h: CGFloat = 1350, imageH: CGFloat = 760
    let canvas = NSImage(size: NSSize(width: w, height: h))
    canvas.lockFocus()
    white.setFill(); NSBezierPath(rect: NSRect(x: 0, y: 0, width: w, height: h)).fill()
    let src = NSRect(x: 0, y: 155, width: source.size.width, height: source.size.height - 300)
    source.draw(in: NSRect(x: 0, y: 0, width: w, height: imageH), from: src, operation: .sourceOver, fraction: 1, respectFlipped: false, hints: [.interpolation: NSImageInterpolation.high])
    drawText("✝", in: NSRect(x: 76, y: 1217, width: 90, height: 60), font: NSFont(name: "Georgia", size: 36)!, color: warm)
    drawText("THIS SUNDAY", in: NSRect(x: 76, y: 1145, width: 760, height: 44), font: NSFont.systemFont(ofSize: 22, weight: .semibold), color: warm, spacing: 7)
    drawText("May God give rest\nto the part of you that has been strong\nall week", in: NSRect(x: 76, y: 895, width: 930, height: 220), font: NSFont(name: "Georgia", size: 48)!, color: ink, lineHeight: 59)
    drawText("REIRA BIN   ·   FAITH & GRACE", in: NSRect(x: 76, y: 806, width: 850, height: 30), font: NSFont.systemFont(ofSize: 15, weight: .semibold), color: warm, spacing: 3)
    warm.setFill(); NSBezierPath(rect: NSRect(x: 76, y: 782, width: 70, height: 3)).fill()
    canvas.unlockFocus()
    save(canvas, path: root + "/built-by-grace-sunday-feed-1080x1350.png")
}

renderVertical()
renderFeed()
