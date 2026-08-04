import AppKit

let root = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
let output = root.appendingPathComponent("assets/social/posts/built-by-grace-jezebel")
try FileManager.default.createDirectory(at: output, withIntermediateDirectories: true)

let canvas = NSSize(width: 1080, height: 1350)
let ink = NSColor(calibratedRed: 0.035, green: 0.042, blue: 0.04, alpha: 1)
let ivory = NSColor(calibratedRed: 0.96, green: 0.94, blue: 0.90, alpha: 1)
let muted = NSColor(calibratedRed: 0.76, green: 0.73, blue: 0.67, alpha: 1)
let gold = NSColor(calibratedRed: 0.76, green: 0.55, blue: 0.28, alpha: 1)

func font(_ size: CGFloat, _ weight: NSFont.Weight = .regular) -> NSFont {
  NSFont.systemFont(ofSize: size, weight: weight)
}

func attributes(_ font: NSFont, _ color: NSColor, _ alignment: NSTextAlignment = .left, _ lineSpacing: CGFloat = 10, _ kern: CGFloat = 0) -> [NSAttributedString.Key: Any] {
  let paragraph = NSMutableParagraphStyle()
  paragraph.alignment = alignment
  paragraph.lineSpacing = lineSpacing
  return [.font: font, .foregroundColor: color, .paragraphStyle: paragraph, .kern: kern]
}

func drawText(_ value: String, _ rect: NSRect, _ font: NSFont, _ color: NSColor, _ alignment: NSTextAlignment = .left, _ lineSpacing: CGFloat = 10, _ kern: CGFloat = 0) {
  (value as NSString).draw(in: rect, withAttributes: attributes(font, color, alignment, lineSpacing, kern))
}

func rule(_ y: CGFloat, from x1: CGFloat = 80, to x2: CGFloat = 1000) {
  gold.withAlphaComponent(0.55).setStroke()
  let path = NSBezierPath()
  path.move(to: NSPoint(x: x1, y: y))
  path.line(to: NSPoint(x: x2, y: y))
  path.lineWidth = 2
  path.stroke()
}

func signature(_ page: Int) {
  drawText("SABINO PEREIRA", NSRect(x: 80, y: 1260, width: 500, height: 30), font(19, .medium), gold, .left, 0, 4)
  drawText(String(format: "%02d / 05", page), NSRect(x: 800, y: 1260, width: 200, height: 30), font(19, .medium), muted, .right, 0, 3)
}

func render(_ filename: String, page: Int, content: () -> Void) {
  let image = NSImage(size: canvas)
  image.lockFocusFlipped(true)
  ink.setFill()
  NSBezierPath(rect: NSRect(origin: .zero, size: canvas)).fill()

  let glow = NSGradient(colors: [gold.withAlphaComponent(0.14), gold.withAlphaComponent(0)])!
  glow.draw(fromCenter: NSPoint(x: 870, y: 160), radius: 0, toCenter: NSPoint(x: 870, y: 160), radius: 520, options: [])
  content()
  signature(page)
  image.unlockFocus()

  guard let tiff = image.tiffRepresentation,
        let bitmap = NSBitmapImageRep(data: tiff),
        let png = bitmap.representation(using: .png, properties: [:]) else {
    fatalError("Unable to encode \(filename)")
  }
  try! png.write(to: output.appendingPathComponent(filename), options: .atomic)
}

render("01-hook.png", page: 1) {
  drawText("THE ADVICE I READ TODAY", NSRect(x: 80, y: 105, width: 920, height: 45), font(24, .medium), gold, .left, 0, 5)
  rule(190)
  drawText("“If you don’t take care\nof your husband,\nthe devil will send him\na Jezebel.”", NSRect(x: 80, y: 275, width: 900, height: 560), font(70, .medium), ivory, .left, 16)
  drawText("It sounds spiritual. But is it wisdom?", NSRect(x: 80, y: 1030, width: 900, height: 100), font(32, .regular), muted)
}

render("02-no.png", page: 2) {
  drawText("NO.", NSRect(x: 80, y: 115, width: 920, height: 150), font(118, .bold), gold)
  drawText("A faithful man does not become unfaithful because his wife failed to manage him.", NSRect(x: 80, y: 340, width: 900, height: 500), font(54, .medium), ivory, .left, 14)
  rule(985)
  drawText("Adults remain responsible\nfor their own choices.", NSRect(x: 80, y: 1040, width: 900, height: 120), font(30, .regular), muted, .left, 6)
}

render("03-character.png", page: 3) {
  drawText("TEMPTATION MAY KNOCK.", NSRect(x: 80, y: 145, width: 920, height: 55), font(26, .medium), gold, .left, 0, 4)
  drawText("Character\ndecides who\nopens the door.", NSRect(x: 80, y: 330, width: 900, height: 440), font(82, .semibold), ivory, .left, 15)
  rule(930)
  drawText("Faith does not remove accountability.\nIt should deepen it.", NSRect(x: 80, y: 985, width: 900, height: 150), font(36, .regular), muted, .left, 8)
}

render("04-marriage.png", page: 4) {
  drawText("MARRIAGE REQUIRES", NSRect(x: 80, y: 125, width: 920, height: 50), font(25, .medium), gold, .left, 0, 5)
  drawText("Attention.\nAffection.\nHonesty.", NSRect(x: 80, y: 245, width: 900, height: 330), font(77, .semibold), ivory, .left, 11)
  drawText("From both people.", NSRect(x: 80, y: 620, width: 900, height: 70), font(44, .medium), gold)
  rule(790)
  drawText("But betrayal remains the responsibility of the person who chooses it.", NSRect(x: 80, y: 860, width: 900, height: 230), font(40, .regular), ivory, .left, 11)
}

render("05-built-by-grace.png", page: 5) {
  let coverPath = root.appendingPathComponent("books/built-by-grace-premium/assets/built-by-grace-premium-cover-v2.png").path
  guard let cover = NSImage(contentsOfFile: coverPath) else { fatalError("Missing Built by Grace cover") }
  NSGraphicsContext.current?.imageInterpolation = .high
  cover.draw(in: NSRect(x: 80, y: 120, width: 350, height: 560), from: .zero, operation: .sourceOver, fraction: 1, respectFlipped: true, hints: nil)
  drawText("Grace can rebuild\nwhat was broken.", NSRect(x: 490, y: 155, width: 500, height: 220), font(52, .semibold), ivory, .left, 11)
  drawText("But grace should never be used to excuse what refuses to change.", NSRect(x: 490, y: 420, width: 490, height: 240), font(37, .regular), muted, .left, 10)
  rule(790)
  drawText("BUILT BY GRACE", NSRect(x: 80, y: 865, width: 920, height: 70), font(48, .bold), gold, .left, 0, 3)
  drawText("A journey of repair, healing, love—\nand God at the centre.", NSRect(x: 80, y: 965, width: 900, height: 150), font(38, .regular), ivory, .left, 10)
  drawText("READ THE BOOK · SABINOPEREIRA.COM", NSRect(x: 80, y: 1160, width: 900, height: 40), font(23, .medium), muted, .left, 0, 3)
}

let manifest = """
{
  "campaign": "Built by Grace — Jezebel advice response",
  "format": "Instagram carousel",
  "dimensions": "1080x1350",
  "slides": 5,
  "sourceCover": "books/built-by-grace-premium/assets/built-by-grace-premium-cover-v2.png",
  "sourcePreserved": true,
  "generatedImages": false
}
"""
try! manifest.write(to: output.appendingPathComponent("manifest.json"), atomically: true, encoding: .utf8)
print(output.path)
