import AppKit

let outDir = "social-media/mockups/music-by-reira-bin"
try FileManager.default.createDirectory(atPath: outDir, withIntermediateDirectories: true)
let size = NSSize(width: 1080, height: 1350)
let paper = NSColor(calibratedRed: 0.95, green: 0.91, blue: 0.84, alpha: 1)
let ink = NSColor(calibratedRed: 0.08, green: 0.075, blue: 0.07, alpha: 1)
let red = NSColor(calibratedRed: 0.53, green: 0.095, blue: 0.045, alpha: 1)
let muted = NSColor(calibratedRed: 0.34, green: 0.31, blue: 0.27, alpha: 1)

func font(_ name: String, _ size: CGFloat) -> NSFont { NSFont(name: name, size: size) ?? .systemFont(ofSize: size) }
func text(_ value: String, _ rect: NSRect, _ f: NSFont, _ color: NSColor, _ align: NSTextAlignment = .left, _ spacing: CGFloat = 0) {
  let p=NSMutableParagraphStyle(); p.alignment=align; p.lineSpacing=spacing
  (value as NSString).draw(in:rect,withAttributes:[.font:f,.foregroundColor:color,.paragraphStyle:p])
}

let image=NSImage(size:size); image.lockFocusFlipped(true)
paper.setFill(); NSBezierPath(rect:NSRect(origin:.zero,size:size)).fill()

// restrained paper texture
for i in 0..<420 {
  let x=CGFloat((i*83)%1080), y=CGFloat((i*137)%1350)
  ink.withAlphaComponent(i % 3 == 0 ? 0.018 : 0.009).setFill()
  NSBezierPath(ovalIn:NSRect(x:x,y:y,width:1.3,height:1.3)).fill()
}

red.setFill(); NSBezierPath(rect:NSRect(x:0,y:0,width:1080,height:18)).fill()
text("RB",NSRect(x:64,y:55,width:130,height:80),font("Georgia",64),red)
text("REIRA BIN",NSRect(x:190,y:76,width:300,height:40),font("Menlo-Bold",28),ink)
text("MUSIC BY REIRA BIN",NSRect(x:690,y:80,width:325,height:35),font("Menlo",18),muted,.right)
muted.withAlphaComponent(0.35).setFill();NSBezierPath(rect:NSRect(x:64,y:148,width:952,height:2)).fill()

red.setFill();NSBezierPath(roundedRect:NSRect(x:64,y:225,width:365,height:58),xRadius:4,yRadius:4).fill()
text("ENTER THROUGH SOUND",NSRect(x:85,y:241,width:325,height:30),font("Menlo-Bold",18),paper)

text("MUSIC IS",NSRect(x:64,y:345,width:930,height:105),font("Georgia",82),ink)
text("ANOTHER DOOR.",NSRect(x:64,y:445,width:950,height:112),font("Georgia",92),ink)

text("Some stories are read.",NSRect(x:68,y:650,width:900,height:60),font("Menlo-Bold",34),red)
text("Others arrive as rhythm, memory and voice.",NSRect(x:68,y:735,width:900,height:55),font("Menlo",25),muted)

// abstract waveform / doorway motif
let baseY:CGFloat=950
red.withAlphaComponent(0.9).setStroke()
let wave=NSBezierPath(); wave.lineWidth=4
for i in 0...46 {
  let x=CGFloat(70+i*20)
  let amp=CGFloat([12,18,28,44,66,38,24,80,45,26,16][i%11])
  wave.move(to:NSPoint(x:x,y:baseY-amp/2)); wave.line(to:NSPoint(x:x,y:baseY+amp/2))
}
wave.stroke()
ink.setStroke(); let door=NSBezierPath(rect:NSRect(x:833,y:844,width:150,height:215));door.lineWidth=5;door.stroke()
red.setFill();NSBezierPath(ovalIn:NSRect(x:950,y:950,width:9,height:9)).fill()

text("R&B   ·   GOSPEL   ·   LATIN   ·   STORY-DRIVEN SOUND",NSRect(x:64,y:1125,width:952,height:36),font("Menlo-Bold",20),ink,.center)
text("EVERY SONG OPENS A WORLD  →",NSRect(x:64,y:1240,width:952,height:34),font("Menlo-Bold",20),red,.center)
red.setFill(); NSBezierPath(rect:NSRect(x:0,y:1332,width:1080,height:18)).fill()
image.unlockFocus()

let rep=NSBitmapImageRep(data:image.tiffRepresentation!)!
let data=rep.representation(using:.png,properties:[:])!
let output=outDir+"/music-by-reira-bin-grid-mockup.png"
try data.write(to:URL(fileURLWithPath:output),options:.atomic)
print(output)
