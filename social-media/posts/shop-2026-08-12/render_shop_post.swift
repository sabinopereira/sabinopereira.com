import AppKit

let W: CGFloat = 1080, H: CGFloat = 1350
let canvas = NSImage(size: NSSize(width: W, height: H))
canvas.lockFocus()
let ctx = NSGraphicsContext.current!.cgContext

NSColor(calibratedRed: 0.93, green: 0.89, blue: 0.82, alpha: 1).setFill()
ctx.fill(CGRect(x: 0, y: 0, width: W, height: H))

func text(_ value: String, _ rect: CGRect, _ size: CGFloat, _ color: NSColor, _ font: String = "Helvetica Neue", _ align: NSTextAlignment = .left) {
    let p = NSMutableParagraphStyle(); p.alignment = align
    let f = NSFont(name: font, size: size) ?? NSFont.systemFont(ofSize: size)
    (value as NSString).draw(in: rect, withAttributes: [.font:f, .foregroundColor:color, .paragraphStyle:p])
}

func image(_ path: String, _ rect: CGRect) {
    guard let im = NSImage(contentsOfFile: path) else { return }
    let s = im.size, scale = min(rect.width/s.width, rect.height/s.height)
    let w = s.width*scale, h = s.height*scale
    im.draw(in: CGRect(x: rect.midX-w/2, y: rect.midY-h/2, width: w, height: h), from: .zero, operation: .sourceOver, fraction: 1)
}

let black = NSColor(calibratedWhite: 0.08, alpha: 1)
let red = NSColor(calibratedRed: 0.43, green: 0.07, blue: 0.05, alpha: 1)

text("RB  ·  REIRA BIN", CGRect(x: 64, y: 1250, width: 952, height: 42), 25, black, "Helvetica Neue Medium")
text("WEAR THE", CGRect(x: 64, y: 1075, width: 952, height: 110), 86, black, "Helvetica Neue Condensed Black")
text("STORY.", CGRect(x: 64, y: 975, width: 952, height: 110), 86, red, "Helvetica Neue Condensed Black")
text("Ideas that move from page and sound — into what you wear.", CGRect(x: 66, y: 920, width: 890, height: 48), 25, black)

let root = "/Users/binopereira/Desktop/Site SabinoPereira.com/sabinopereira.com/images/merch/"
let cards = [
    ("built-by-grace-oversized-t-shirt.png", "BUILT BY GRACE"),
    ("everybody-is-insane-premium-tee-black.png", "EVERYBODY IS INSANE"),
    ("love-loudly-womens-premium-crop-top-lifestyle.png", "LOVE LOUDLY")
]
let cardW: CGFloat = 296, gap: CGFloat = 32, startX: CGFloat = 64
for i in 0..<3 {
    let x = startX + CGFloat(i)*(cardW+gap)
    NSColor(calibratedWhite: 0.97, alpha: 1).setFill()
    NSBezierPath(roundedRect: CGRect(x:x, y:300, width:cardW, height:560), xRadius:14, yRadius:14).fill()
    image(root + cards[i].0, CGRect(x:x+12, y:375, width:cardW-24, height:460))
    text(cards[i].1, CGRect(x:x+14, y:325, width:cardW-28, height:32), 17, black, "Helvetica Neue Bold", .center)
}

NSColor(calibratedWhite: 0.12, alpha: 1).setFill()
NSBezierPath(roundedRect: CGRect(x:64, y:120, width:952, height:115), xRadius:10, yRadius:10).fill()
text("EXPLORE THE SHOP  ·  LINK IN BIO", CGRect(x:90, y:151, width:900, height:48), 28, .white, "Helvetica Neue Bold", .center)
text("Original worlds to read, hear and wear.", CGRect(x:64, y:58, width:952, height:38), 22, red, "Helvetica Neue Medium", .center)

canvas.unlockFocus()
guard let tiff = canvas.tiffRepresentation, let rep = NSBitmapImageRep(data:tiff), let png = rep.representation(using:.png, properties:[:]) else { exit(1) }
try png.write(to: URL(fileURLWithPath:"social-media/posts/shop-2026-08-12/reira-bin-shop-post.png"))
