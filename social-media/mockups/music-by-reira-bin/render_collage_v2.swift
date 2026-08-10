import AppKit

let folder="social-media/mockups/music-by-reira-bin"
let bg=NSImage(contentsOfFile:folder+"/music-collage-background-v2.png")!
let canvas=NSSize(width:1080,height:1350)
let ink=NSColor(calibratedRed:0.075,green:0.07,blue:0.065,alpha:1)
let red=NSColor(calibratedRed:0.50,green:0.10,blue:0.065,alpha:1)
let muted=NSColor(calibratedRed:0.28,green:0.24,blue:0.20,alpha:1)

func draw(_ s:String,_ rect:NSRect,_ size:CGFloat,_ color:NSColor,_ font:String="Georgia",_ align:NSTextAlignment = .center,_ spacing:CGFloat=0) {
  let p=NSMutableParagraphStyle();p.alignment=align;p.lineSpacing=spacing
  let f=NSFont(name:font,size:size) ?? .systemFont(ofSize:size)
  (s as NSString).draw(in:rect,withAttributes:[.font:f,.foregroundColor:color,.paragraphStyle:p])
}

let image=NSImage(size:canvas);image.lockFocusFlipped(true)
NSGraphicsContext.current?.imageInterpolation = .high
// Fill 4:5 while retaining the collage edges and the musical desk.
bg.draw(in:NSRect(origin:.zero,size:canvas),from:.zero,operation:.sourceOver,fraction:1,respectFlipped:true,hints:nil)

// Soft paper veil keeps typography calm without erasing the collage.
NSColor(calibratedWhite:0.96,alpha:0.26).setFill()
NSBezierPath(roundedRect:NSRect(x:250,y:110,width:580,height:760),xRadius:12,yRadius:12).fill()

draw("R",NSRect(x:396,y:130,width:145,height:150),132,ink,"Georgia")
draw("B",NSRect(x:532,y:130,width:145,height:150),132,red,"Georgia")
draw("✦",NSRect(x:518,y:193,width:42,height:45),27,ink,"Helvetica Neue")
draw("REIRA BIN",NSRect(x:285,y:278,width:510,height:65),45,ink,"Helvetica Neue",.center)

ink.withAlphaComponent(0.35).setFill();NSBezierPath(rect:NSRect(x:340,y:355,width:400,height:2)).fill()
draw("MUSIC IS",NSRect(x:270,y:415,width:540,height:72),58,ink,"Georgia")
draw("ANOTHER DOOR.",NSRect(x:230,y:488,width:620,height:82),65,ink,"Georgia")

draw("Some stories are read.",NSRect(x:270,y:640,width:540,height:48),31,red,"Menlo-Bold")
draw("Others arrive as rhythm,\nmemory and voice.",NSRect(x:275,y:710,width:530,height:90),25,muted,"Menlo",.center,8)

red.setFill();NSBezierPath(rect:NSRect(x:348,y:838,width:384,height:4)).fill()
draw("R&B  ·  GOSPEL  ·  LATIN",NSRect(x:280,y:865,width:520,height:38),20,ink,"Menlo-Bold")

// Small torn-label treatment.
red.withAlphaComponent(0.94).setFill();NSBezierPath(roundedRect:NSRect(x:365,y:950,width:350,height:62),xRadius:2,yRadius:2).fill()
draw("ENTER THROUGH SOUND",NSRect(x:380,y:970,width:320,height:28),18,NSColor(calibratedRed:0.94,green:0.89,blue:0.80,alpha:1),"Menlo-Bold")

draw("EVERY SONG OPENS A WORLD  →",NSRect(x:270,y:1060,width:540,height:36),19,red,"Menlo-Bold")
image.unlockFocus()

let rep=NSBitmapImageRep(data:image.tiffRepresentation!)!
let data=rep.representation(using:.png,properties:[:])!
let out=folder+"/music-by-reira-bin-grid-mockup-v2.png"
try data.write(to:URL(fileURLWithPath:out),options:.atomic)
print(out)
