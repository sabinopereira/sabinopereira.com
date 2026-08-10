import AppKit
import AVFoundation
import CoreVideo

let width=1080, height=1920, fps:Int32=30, duration=9.0
let folder="social-media/posts/filthy-rich-2026-08-14"
let silentURL=URL(fileURLWithPath:folder+"/financially-delusional-silent.mp4")
let finalURL=URL(fileURLWithPath:folder+"/financially-delusional-reel.mp4")
try? FileManager.default.removeItem(at:silentURL); try? FileManager.default.removeItem(at:finalURL)
let bg=NSImage(contentsOfFile:folder+"/financially-delusional-vertical-background.png")!

let writer=try AVAssetWriter(outputURL:silentURL,fileType:.mp4)
let input=AVAssetWriterInput(mediaType:.video,outputSettings:[AVVideoCodecKey:AVVideoCodecType.h264,AVVideoWidthKey:width,AVVideoHeightKey:height,AVVideoCompressionPropertiesKey:[AVVideoAverageBitRateKey:9_000_000,AVVideoProfileLevelKey:AVVideoProfileLevelH264HighAutoLevel]])
let adaptor=AVAssetWriterInputPixelBufferAdaptor(assetWriterInput:input,sourcePixelBufferAttributes:[kCVPixelBufferPixelFormatTypeKey as String:kCVPixelFormatType_32ARGB,kCVPixelBufferWidthKey as String:width,kCVPixelBufferHeightKey as String:height])
writer.add(input); writer.startWriting(); writer.startSession(atSourceTime:.zero)

func ease(_ x:Double)->CGFloat { let v=max(0,min(1,x)); return CGFloat(v*v*(3-2*v)) }
func alpha(_ t:Double,_ start:Double,_ end:Double)->CGFloat { ease((t-start)/(end-start)) }
func drawText(_ s:String,_ rect:CGRect,_ size:CGFloat,_ color:NSColor,_ font:String="Helvetica Neue",_ a:CGFloat=1,_ align:NSTextAlignment = .left){
  let p=NSMutableParagraphStyle();p.alignment=align
  let f=NSFont(name:font,size:size) ?? .systemFont(ofSize:size)
  (s as NSString).draw(in:rect,withAttributes:[.font:f,.foregroundColor:color.withAlphaComponent(a),.paragraphStyle:p])
}
let gold=NSColor(calibratedRed:0.84,green:0.64,blue:0.29,alpha:1)
for frame in 0..<Int(duration*Double(fps)) {
  while !input.isReadyForMoreMediaData { usleep(1000) }
  var px:CVPixelBuffer?; CVPixelBufferPoolCreatePixelBuffer(nil,adaptor.pixelBufferPool!,&px)
  let pb=px!; CVPixelBufferLockBaseAddress(pb,[])
  let ctx=CGContext(data:CVPixelBufferGetBaseAddress(pb),width:width,height:height,bitsPerComponent:8,bytesPerRow:CVPixelBufferGetBytesPerRow(pb),space:CGColorSpaceCreateDeviceRGB(),bitmapInfo:CGImageAlphaInfo.noneSkipFirst.rawValue)!
  let gc=NSGraphicsContext(cgContext:ctx,flipped:false); NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current=gc
  let time=Double(frame)/Double(fps), zoom=CGFloat(1.0+0.025*time/duration)
  let dw=CGFloat(width)*zoom,dh=CGFloat(height)*zoom
  bg.draw(in:CGRect(x:(CGFloat(width)-dw)/2,y:(CGFloat(height)-dh)/2,width:dw,height:dh),from:.zero,operation:.sourceOver,fraction:1)
  let grad=CGGradient(colorsSpace:CGColorSpaceCreateDeviceRGB(),colors:[NSColor.black.withAlphaComponent(0.88).cgColor,NSColor.black.withAlphaComponent(0.05).cgColor] as CFArray,locations:[0,1])!
  ctx.drawLinearGradient(grad,start:CGPoint(x:0,y:height),end:CGPoint(x:760,y:height),options:[])
  drawText("FILTHY RICH  ·  EPISODE 01",CGRect(x:70,y:1740,width:850,height:45),28,gold,"Helvetica Neue Bold",alpha(time,0.15,0.7))
  let a1=alpha(time,0.7,1.35)
  drawText("FINANCIALLY",CGRect(x:70,y:1485,width:850,height:110),83,.white,"Helvetica Neue Condensed Black",a1)
  drawText("DELUSIONAL",CGRect(x:70,y:1385,width:850,height:110),83,gold,"Helvetica Neue Condensed Black",a1)
  let a2=alpha(time,2.65,3.3)
  drawText("The bank account said no.",CGRect(x:72,y:1270,width:780,height:52),35,.white,"Helvetica Neue Bold",a2)
  let a3=alpha(time,4.45,5.1)
  drawText("The lifestyle said",CGRect(x:72,y:1170,width:780,height:52),35,.white,"Helvetica Neue Bold",a3)
  drawText("manifest harder.",CGRect(x:72,y:1118,width:780,height:52),35,gold,"Helvetica Neue Bold",a3)
  let a4=alpha(time,6.65,7.25)
  ctx.setFillColor(NSColor.black.withAlphaComponent(0.55*a4).cgColor);ctx.fill(CGRect(x:0,y:78,width:width,height:150))
  drawText("WHAT IF LUXURY WERE A COMEDY?",CGRect(x:60,y:126,width:960,height:48),28,gold,"Helvetica Neue Bold",a4,.center)
  NSGraphicsContext.restoreGraphicsState(); CVPixelBufferUnlockBaseAddress(pb,[])
  adaptor.append(pb,withPresentationTime:CMTime(value:Int64(frame),timescale:fps))
}
input.markAsFinished(); await writer.finishWriting()

let composition=AVMutableComposition()
let videoAsset=AVURLAsset(url:silentURL), audioAsset=AVURLAsset(url:URL(fileURLWithPath:"audio/siempre-nosotros/02-cafe-para-dos.mp3"))
let range=CMTimeRange(start:.zero,duration:CMTime(seconds:duration,preferredTimescale:600))
if let src=try await videoAsset.loadTracks(withMediaType:.video).first,let dst=composition.addMutableTrack(withMediaType:.video,preferredTrackID:kCMPersistentTrackID_Invalid){try dst.insertTimeRange(range,of:src,at:.zero)}
if let src=try await audioAsset.loadTracks(withMediaType:.audio).first,let dst=composition.addMutableTrack(withMediaType:.audio,preferredTrackID:kCMPersistentTrackID_Invalid){try dst.insertTimeRange(range,of:src,at:.zero)}
let exporter = AVAssetExportSession(asset:composition,presetName:AVAssetExportPresetHighestQuality)!
exporter.outputURL = finalURL
exporter.outputFileType = .mp4
await exporter.export()
if exporter.status != .completed { print(exporter.error?.localizedDescription ?? "Export failed"); exit(1) }
try? FileManager.default.removeItem(at:silentURL)
print(finalURL.path)
