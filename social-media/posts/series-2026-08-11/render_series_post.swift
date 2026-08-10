import AppKit

let W: CGFloat = 1080, H: CGFloat = 1350
let image = NSImage(size: NSSize(width: W, height: H))
image.lockFocus()
let c = NSGraphicsContext.current!.cgContext
NSColor(calibratedRed: 0.93, green: 0.89, blue: 0.82, alpha: 1).setFill()
c.fill(CGRect(x:0,y:0,width:W,height:H))

func label(_ s:String,_ r:CGRect,_ size:CGFloat,_ color:NSColor,_ font:String="Helvetica Neue",_ align:NSTextAlignment = .left) {
  let p=NSMutableParagraphStyle(); p.alignment=align
  let f=NSFont(name:font,size:size) ?? .systemFont(ofSize:size)
  (s as NSString).draw(in:r,withAttributes:[.font:f,.foregroundColor:color,.paragraphStyle:p])
}
let ink=NSColor(calibratedWhite:0.08,alpha:1)
let red=NSColor(calibratedRed:0.43,green:0.07,blue:0.05,alpha:1)
label("RB  ·  REIRA BIN",CGRect(x:64,y:1250,width:952,height:42),25,ink,"Helvetica Neue Medium")
label("ORIGINAL",CGRect(x:64,y:1085,width:952,height:100),82,ink,"Helvetica Neue Condensed Black")
label("SERIES.",CGRect(x:64,y:990,width:952,height:100),82,red,"Helvetica Neue Condensed Black")
label("Different worlds. One creative universe.",CGRect(x:66,y:930,width:900,height:45),26,ink)

let items=[
  ("TRUTH FILES","What if someone said the truth everyone avoids?"),
  ("AFRAID OF AI","What if AI were stranger than it is scary?"),
  ("FILTHY RICH","What if luxury were a comedy?"),
  ("ECHOES","What if the past never stopped speaking?")
]
for i in 0..<4 {
  let y:CGFloat=760-CGFloat(i)*165
  NSColor(calibratedWhite:0.975,alpha:1).setFill()
  NSBezierPath(roundedRect:CGRect(x:64,y:y,width:952,height:132),xRadius:12,yRadius:12).fill()
  NSColor(calibratedRed:0.43,green:0.07,blue:0.05,alpha:1).setFill()
  c.fill(CGRect(x:64,y:y,width:10,height:132))
  label(items[i].0,CGRect(x:100,y:y+67,width:850,height:38),27,ink,"Helvetica Neue Bold")
  label(items[i].1,CGRect(x:100,y:y+22,width:850,height:38),21,red,"Helvetica Neue")
}

NSColor(calibratedWhite:0.12,alpha:1).setFill()
NSBezierPath(roundedRect:CGRect(x:64,y:105,width:952,height:112),xRadius:10,yRadius:10).fill()
label("WHICH WORLD SHOULD OPEN FIRST?",CGRect(x:85,y:137,width:910,height:45),27,.white,"Helvetica Neue Bold",.center)
label("Stories · ideas · music · strange little worlds",CGRect(x:64,y:48,width:952,height:35),21,red,"Helvetica Neue Medium",.center)
image.unlockFocus()
guard let t=image.tiffRepresentation,let b=NSBitmapImageRep(data:t),let p=b.representation(using:.png,properties:[:]) else {exit(1)}
try p.write(to:URL(fileURLWithPath:"social-media/posts/series-2026-08-11/reira-bin-series-post.png"))
