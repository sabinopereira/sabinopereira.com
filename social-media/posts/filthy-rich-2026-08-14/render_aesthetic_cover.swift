import AppKit

let width = 1080
let height = 1920
let folder = "social-media/posts/filthy-rich-2026-08-14"
let background = NSImage(contentsOfFile: folder + "/financially-delusional-vertical-background.png")!
let outputURL = URL(fileURLWithPath: folder + "/the-aesthetic-cover.png")

func drawText(
    _ text: String,
    _ rect: CGRect,
    _ size: CGFloat,
    _ color: NSColor,
    _ fontName: String = "Helvetica Neue",
    _ alignment: NSTextAlignment = .left
) {
    let paragraph = NSMutableParagraphStyle()
    paragraph.alignment = alignment
    let font = NSFont(name: fontName, size: size) ?? .systemFont(ofSize: size)
    (text as NSString).draw(in: rect, withAttributes: [
        .font: font,
        .foregroundColor: color,
        .paragraphStyle: paragraph
    ])
}

let image = NSImage(size: NSSize(width: width, height: height))
image.lockFocus()

background.draw(
    in: CGRect(x: 0, y: 0, width: width, height: height),
    from: .zero,
    operation: .sourceOver,
    fraction: 1
)

let context = NSGraphicsContext.current!.cgContext
let gradient = CGGradient(
    colorsSpace: CGColorSpaceCreateDeviceRGB(),
    colors: [NSColor.black.withAlphaComponent(0.90).cgColor, NSColor.black.withAlphaComponent(0.04).cgColor] as CFArray,
    locations: [0, 1]
)!
context.drawLinearGradient(
    gradient,
    start: CGPoint(x: 0, y: height),
    end: CGPoint(x: 760, y: height),
    options: []
)

let gold = NSColor(calibratedRed: 0.84, green: 0.64, blue: 0.29, alpha: 1)
drawText("FILTHY RICH  ·  THE PERFORMANCE", CGRect(x: 70, y: 1740, width: 900, height: 45), 28, gold, "Helvetica Neue Bold")
drawText("Some people don’t have", CGRect(x: 70, y: 1475, width: 880, height: 70), 47, .white, "Helvetica Neue Bold")
drawText("a financial plan.", CGRect(x: 70, y: 1375, width: 880, height: 100), 75, gold, "Helvetica Neue Condensed Black")
drawText("They have", CGRect(x: 70, y: 1205, width: 780, height: 65), 43, .white, "Helvetica Neue Bold")
drawText("AN AESTHETIC.", CGRect(x: 70, y: 1080, width: 930, height: 115), 82, gold, "Helvetica Neue Condensed Black")

context.setFillColor(NSColor.black.withAlphaComponent(0.62).cgColor)
context.fill(CGRect(x: 0, y: 78, width: width, height: 160))
drawText("FILTHY RICH", CGRect(x: 60, y: 130, width: 960, height: 54), 40, .white, "Helvetica Neue Condensed Black", .center)

image.unlockFocus()

let representation = NSBitmapImageRep(data: image.tiffRepresentation!)!
let png = representation.representation(using: .png, properties: [:])!
try png.write(to: outputURL)
print(outputURL.path)
