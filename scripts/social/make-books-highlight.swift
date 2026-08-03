import AppKit

let root = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
let out = root.appendingPathComponent("assets/social/highlights")
let size = NSSize(width: 1080, height: 1920)
let bg = NSColor(calibratedRed: 0.035, green: 0.047, blue: 0.047, alpha: 1)
let ivory = NSColor(calibratedRed: 0.95, green: 0.93, blue: 0.89, alpha: 1)
let muted = NSColor(calibratedRed: 0.80, green: 0.77, blue: 0.71, alpha: 1)
let gold = NSColor(calibratedRed: 0.73, green: 0.55, blue: 0.31, alpha: 1)

func italicFont(ofSize size: CGFloat) -> NSFont {
  let base = NSFont.systemFont(ofSize: size)
  return NSFontManager.shared.convert(base, toHaveTrait: .italicFontMask)
}

func attrs(_ font: NSFont, _ color: NSColor, _ align: NSTextAlignment = .center, _ spacing: CGFloat = 0) -> [NSAttributedString.Key: Any] {
  let p = NSMutableParagraphStyle(); p.alignment = align
  return [.font: font, .foregroundColor: color, .paragraphStyle: p, .kern: spacing]
}

func text(_ value: String, rect: NSRect, font: NSFont, color: NSColor, align: NSTextAlignment = .center, spacing: CGFloat = 0) {
  (value as NSString).draw(in: rect, withAttributes: attrs(font, color, align, spacing))
}

func line(_ y: CGFloat) {
  gold.withAlphaComponent(0.45).setStroke(); let p = NSBezierPath(); p.move(to: NSPoint(x: 80, y: y)); p.line(to: NSPoint(x: 1000, y: y)); p.lineWidth = 2; p.stroke()
}

func cover(_ path: String, x: CGFloat, y: CGFloat, w: CGFloat = 290, h: CGFloat = 465) {
  guard let img = NSImage(contentsOfFile: root.appendingPathComponent(path).path) else { return }
  NSGraphicsContext.current?.imageInterpolation = .high
  img.draw(in: NSRect(x: x, y: y, width: w, height: h), from: .zero, operation: .sourceOver, fraction: 1, respectFlipped: true, hints: nil)
}

func render(_ name: String, draw: () -> Void) {
  let image = NSImage(size: size)
  image.lockFocusFlipped(true)
  bg.setFill(); NSBezierPath(rect: NSRect(origin: .zero, size: size)).fill()
  draw()
  image.unlockFocus()
  guard let tiff = image.tiffRepresentation,
        let rep = NSBitmapImageRep(data: tiff),
        let png = rep.representation(using: .png, properties: [:]) else {
    fatalError("Could not encode \(name)")
  }
  do {
    try png.write(to: out.appendingPathComponent(name), options: .atomic)
    print("Wrote \(name)")
  } catch {
    fatalError("Could not write \(name): \(error)")
  }
}

render("books-01.png") {
  gold.withAlphaComponent(0.35).setStroke()
  for y in [540.0, 1380.0] { let p=NSBezierPath(); p.move(to:NSPoint(x:190,y:y)); p.line(to:NSPoint(x:890,y:y)); p.lineWidth=2; p.stroke() }
  text("ENTER THE LIBRARY", rect:NSRect(x:90,y:720,width:900,height:55), font:.systemFont(ofSize:30,weight:.medium), color:gold, spacing:7)
  text("BOOKS", rect:NSRect(x:80,y:860,width:920,height:180), font:.systemFont(ofSize:142,weight:.regular), color:ivory, spacing:8)
  text("Original worlds by Sabino Pereira.", rect:NSRect(x:90,y:1050,width:900,height:60), font:italicFont(ofSize:38), color:muted)
  text("STORIES TO READ, HEAR AND FEEL.", rect:NSRect(x:80,y:1215,width:920,height:50), font:.systemFont(ofSize:30,weight:.regular), color:ivory, spacing:3)
}

render("books-02.png") {
  text("FICTION · STRATEGY · MODERN LIFE", rect:NSRect(x:80,y:125,width:920,height:50), font:.systemFont(ofSize:28,weight:.medium), color:gold, align:.left, spacing:5)
  text("Three doors.\nThree different worlds.", rect:NSRect(x:80,y:215,width:920,height:160), font:.systemFont(ofSize:64,weight:.regular), color:ivory, align:.left)
  cover("books/a-seat-at-the-table/assets/a-seat-at-the-table-cover-web.jpg", x:70,y:460)
  cover("books/borrow-delay-repeat/directors-cut/premium-edition/ebook/borrow-delay-repeat-directors-cut-cover.jpg", x:395,y:460)
  cover("books/chess-in-the-block/cover/chess-on-the-block-directors-cut-cover.png", x:720,y:460)
  text("A Seat at\nthe Table",rect:NSRect(x:60,y:950,width:310,height:90),font:.systemFont(ofSize:30,weight:.semibold),color:ivory)
  text("Borrow. Delay.\nRepeat.",rect:NSRect(x:385,y:950,width:310,height:90),font:.systemFont(ofSize:30,weight:.semibold),color:ivory)
  text("Chess on\nthe Block",rect:NSRect(x:710,y:950,width:310,height:90),font:.systemFont(ofSize:30,weight:.semibold),color:ivory)
  line(1160)
  text("POWER CHANGES SHAPE.\nTHE CONSEQUENCES REMAIN.",rect:NSRect(x:80,y:1240,width:920,height:110),font:.systemFont(ofSize:30,weight:.regular),color:muted,spacing:2)
}

render("books-03.png") {
  text("LOVE · FAITH · HEALING", rect:NSRect(x:80,y:125,width:920,height:50), font:.systemFont(ofSize:28,weight:.medium), color:gold, align:.left, spacing:5)
  text("For what breaks—\nand what rebuilds.", rect:NSRect(x:80,y:215,width:920,height:160), font:.systemFont(ofSize:64,weight:.regular), color:ivory, align:.left)
  cover("books/yes-i-do-again/direct-sale/english/yes-i-do-again-digital-cover.jpg", x:70,y:460)
  cover("books/built-by-grace-premium/assets/built-by-grace-premium-cover-v2.png", x:395,y:460)
  cover("books/o-que-ainda-doi-ecos-da-harmonia/images/optimized/what-still-hurts-cover.png", x:720,y:460)
  text("Yes, I Do...\nAgain.",rect:NSRect(x:60,y:950,width:310,height:90),font:.systemFont(ofSize:30,weight:.semibold),color:ivory)
  text("Built by\nGrace",rect:NSRect(x:385,y:950,width:310,height:90),font:.systemFont(ofSize:30,weight:.semibold),color:ivory)
  text("What Still\nHurts",rect:NSRect(x:710,y:950,width:310,height:90),font:.systemFont(ofSize:30,weight:.semibold),color:ivory)
  line(1160)
  text("SOME WOUNDS NEED WORDS.\nSOME STORIES BECOME HOME.",rect:NSRect(x:80,y:1240,width:920,height:110),font:.systemFont(ofSize:30,weight:.regular),color:muted,spacing:2)
}

render("books-04.png") {
  gold.withAlphaComponent(0.3).setStroke(); let c=NSBezierPath(ovalIn:NSRect(x:140,y:520,width:800,height:800)); c.lineWidth=2; c.stroke()
  text("YOUR NEXT WORLD IS WAITING",rect:NSRect(x:80,y:690,width:920,height:50),font:.systemFont(ofSize:28,weight:.medium),color:gold,spacing:5)
  text("Find the story\nthat belongs to you.",rect:NSRect(x:90,y:820,width:900,height:190),font:.systemFont(ofSize:72,weight:.regular),color:ivory)
  line(1100)
  text("EXPLORE ALL BOOKS",rect:NSRect(x:80,y:1160,width:920,height:50),font:.systemFont(ofSize:32,weight:.medium),color:muted,spacing:3)
  text("sabinopereira.com/books.html",rect:NSRect(x:80,y:1230,width:920,height:55),font:.systemFont(ofSize:34,weight:.regular),color:ivory)
  text("Written by Sabino Pereira.",rect:NSRect(x:80,y:1410,width:920,height:50),font:italicFont(ofSize:28),color:gold)
}
