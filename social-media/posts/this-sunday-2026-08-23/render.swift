import AppKit

let width = 1080
let height = 1350
let output = "/Users/binopereira/Desktop/Site SabinoPereira.com/sabinopereira.com/social-media/posts/this-sunday-2026-08-23/this-sunday-02-prayer-instagram-1080x1350.png"
let photoPath = "/Users/binopereira/Desktop/Site SabinoPereira.com/sabinopereira.com/social-media/posts/this-sunday-2026-08-23/pexels-cottonbro-prayer.jpg"

let canvas = NSImage(size: NSSize(width: width, height: height))
canvas.lockFocus()

NSColor(calibratedRed: 0.953, green: 0.914, blue: 0.843, alpha: 1).setFill()
NSBezierPath(rect: NSRect(x: 0, y: 0, width: width, height: height)).fill()

let photoRect = NSRect(x: 529, y: 0, width: 551, height: 1350)
if let photo = NSImage(contentsOfFile: photoPath) {
    let source = NSRect(x: 1550, y: 0, width: 2500, height: 3821)
    photo.draw(in: photoRect, from: source, operation: .sourceOver, fraction: 0.92, respectFlipped: false, hints: [.interpolation: NSImageInterpolation.high])
}

let fade = NSGradient(colors: [
    NSColor(calibratedRed: 0.953, green: 0.914, blue: 0.843, alpha: 0.36),
    NSColor(calibratedRed: 0.953, green: 0.914, blue: 0.843, alpha: 0)
])!
fade.draw(in: NSRect(x: 529, y: 0, width: 95, height: 1350), angle: 0)

func draw(_ text: String, x: CGFloat, yTop: CGFloat, width: CGFloat, font: NSFont, color: NSColor, spacing: CGFloat = 0, lineHeight: CGFloat? = nil) {
    let style = NSMutableParagraphStyle()
    if let lineHeight { style.minimumLineHeight = lineHeight; style.maximumLineHeight = lineHeight }
    let attrs: [NSAttributedString.Key: Any] = [
        .font: font,
        .foregroundColor: color,
        .kern: spacing,
        .paragraphStyle: style
    ]
    let string = NSAttributedString(string: text, attributes: attrs)
    let h = string.boundingRect(with: NSSize(width: width, height: 1000), options: [.usesLineFragmentOrigin, .usesFontLeading]).height
    string.draw(with: NSRect(x: x, y: CGFloat(height) - yTop - h, width: width, height: h + 8), options: [.usesLineFragmentOrigin, .usesFontLeading])
}

let rust = NSColor(calibratedRed: 0.55, green: 0.16, blue: 0.12, alpha: 1)
let ink = NSColor(calibratedRed: 0.11, green: 0.09, blue: 0.075, alpha: 1)

draw("✝", x: 76, yTop: 80, width: 120, font: NSFont(name: "Georgia", size: 43)!, color: rust)
draw("THIS SUNDAY", x: 76, yTop: 150, width: 400, font: NSFont.systemFont(ofSize: 25, weight: .semibold), color: rust, spacing: 7)

rust.setFill()
NSBezierPath(rect: NSRect(x: 76, y: height - 356, width: 58, height: 3)).fill()

draw("May God give", x: 76, yTop: 372, width: 410, font: NSFont(name: "Georgia", size: 54)!, color: ink, lineHeight: 64)
draw("rest", x: 76, yTop: 438, width: 410, font: NSFont(name: "Georgia-Italic", size: 54)!, color: rust, lineHeight: 64)
draw("to the part of you\nthat has been strong\nall week", x: 76, yTop: 506, width: 410, font: NSFont(name: "Georgia", size: 54)!, color: ink, lineHeight: 64)

draw("REIRA BIN", x: 76, yTop: 1175, width: 400, font: NSFont.systemFont(ofSize: 18, weight: .semibold), color: ink, spacing: 7)
draw("Faith & Grace", x: 76, yTop: 1210, width: 300, font: NSFont(name: "Georgia-Italic", size: 17)!, color: rust)

canvas.unlockFocus()
guard let tiff = canvas.tiffRepresentation,
      let bitmap = NSBitmapImageRep(data: tiff),
      let png = bitmap.representation(using: .png, properties: [:]) else { exit(1) }
try png.write(to: URL(fileURLWithPath: output))
