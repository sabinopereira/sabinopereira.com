import AppKit

let W:CGFloat=1080,H:CGFloat=1350
let out=NSImage(size:NSSize(width:W,height:H)); out.lockFocus()
let bg=NSImage(contentsOfFile:"social-media/posts/filthy-rich-2026-08-14/financially-delusional-background.png")!
bg.draw(in:CGRect(x:0,y:0,width:W,height:H),from:.zero,operation:.sourceOver,fraction:1)
let ctx=NSGraphicsContext.current!.cgContext
let colors=[NSColor.black.withAlphaComponent(0.9).cgColor,NSColor.black.withAlphaComponent(0.02).cgColor] as CFArray
let gradient=CGGradient(colorsSpace:CGColorSpaceCreateDeviceRGB(),colors:colors,locations:[0,1])!
ctx.drawLinearGradient(gradient,start:CGPoint(x:0,y:H),end:CGPoint(x:720,y:H),options:[])
ctx.setFillColor(NSColor.black.withAlphaComponent(0.45).cgColor);ctx.fill(CGRect(x:0,y:0,width:W,height:185))
func t(_ s:String,_ r:CGRect,_ z:CGFloat,_ color:NSColor,_ font:String="Helvetica Neue",_ align:NSTextAlignment = .left){let p=NSMutableParagraphStyle();p.alignment=align;let f=NSFont(name:font,size:z) ?? .systemFont(ofSize:z);(s as NSString).draw(in:r,withAttributes:[.font:f,.foregroundColor:color,.paragraphStyle:p])}
let gold=NSColor(calibratedRed:0.82,green:0.63,blue:0.29,alpha:1)
t("FILTHY RICH  ·  EPISODE 01",CGRect(x:64,y:1240,width:700,height:42),23,gold,"Helvetica Neue Bold")
t("FINANCIALLY",CGRect(x:64,y:1032,width:800,height:100),75,.white,"Helvetica Neue Condensed Black")
t("DELUSIONAL",CGRect(x:64,y:948,width:800,height:100),75,gold,"Helvetica Neue Condensed Black")
t("The bank account said no.",CGRect(x:66,y:868,width:610,height:42),27,.white,"Helvetica Neue Medium")
t("The lifestyle said manifest harder.",CGRect(x:66,y:824,width:720,height:42),27,.white,"Helvetica Neue Medium")
t("WHAT IF LUXURY WERE A COMEDY?",CGRect(x:64,y:72,width:952,height:44),25,gold,"Helvetica Neue Bold",.center)
out.unlockFocus()
let rep=NSBitmapImageRep(data:out.tiffRepresentation!)!;let png=rep.representation(using:.png,properties:[:])!
try png.write(to:URL(fileURLWithPath:"social-media/posts/filthy-rich-2026-08-14/financially-delusional-preview.png"))
