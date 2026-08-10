import AppKit
import AVFoundation
import CoreVideo

let folder = "social-media/posts/built-by-grace-sunday-2026-08-16"
try FileManager.default.createDirectory(atPath: folder, withIntermediateDirectories: true)
let cover = NSImage(contentsOfFile: "books/built-by-grace-premium/assets/built-by-grace-premium-cover-v2.png")!
let audioURL = URL(fileURLWithPath: "/Users/binopereira/Desktop/Project Sabino Pereira/music/reira-bin-music/Built by Grace Music Album 2026/17 - God in the Center - Before We Say I Do.wav")
let silentURL = URL(fileURLWithPath: folder + "/built-by-grace-sunday-silent.mp4")
let finalURL = URL(fileURLWithPath: folder + "/built-by-grace-sunday-reel.mp4")
try? FileManager.default.removeItem(at: silentURL); try? FileManager.default.removeItem(at: finalURL)

let width=1080, height=1920, fps:Int32=30, duration=11.0
let ivory=NSColor(calibratedRed:0.975,green:0.945,blue:0.89,alpha:1)
let ink=NSColor(calibratedRed:0.20,green:0.145,blue:0.095,alpha:1)
let gold=NSColor(calibratedRed:0.70,green:0.42,blue:0.16,alpha:1)
let sage=NSColor(calibratedRed:0.42,green:0.48,blue:0.35,alpha:1)

func ease(_ x:Double)->CGFloat { let v=max(0,min(1,x)); return CGFloat(v*v*(3-2*v)) }
func alpha(_ t:Double,_ a:Double,_ b:Double)->CGFloat { ease((t-a)/(b-a)) }
func drawText(_ s:String,_ rect:CGRect,_ size:CGFloat,_ color:NSColor,_ font:String="Helvetica Neue",_ a:CGFloat=1,_ align:NSTextAlignment = .center) {
  let p=NSMutableParagraphStyle(); p.alignment=align; p.lineSpacing=8
  let f=NSFont(name:font,size:size) ?? .systemFont(ofSize:size)
  (s as NSString).draw(in:rect,withAttributes:[.font:f,.foregroundColor:color.withAlphaComponent(a),.paragraphStyle:p])
}

let writer=try AVAssetWriter(outputURL:silentURL,fileType:.mp4)
let input=AVAssetWriterInput(mediaType:.video,outputSettings:[AVVideoCodecKey:AVVideoCodecType.h264,AVVideoWidthKey:width,AVVideoHeightKey:height,AVVideoCompressionPropertiesKey:[AVVideoAverageBitRateKey:9_000_000,AVVideoProfileLevelKey:AVVideoProfileLevelH264HighAutoLevel]])
let adaptor=AVAssetWriterInputPixelBufferAdaptor(assetWriterInput:input,sourcePixelBufferAttributes:[kCVPixelBufferPixelFormatTypeKey as String:kCVPixelFormatType_32ARGB,kCVPixelBufferWidthKey as String:width,kCVPixelBufferHeightKey as String:height])
writer.add(input);writer.startWriting();writer.startSession(atSourceTime:.zero)

for frame in 0..<Int(duration*Double(fps)) {
  while !input.isReadyForMoreMediaData { usleep(1000) }
  var px:CVPixelBuffer?;CVPixelBufferPoolCreatePixelBuffer(nil,adaptor.pixelBufferPool!,&px)
  let pb=px!;CVPixelBufferLockBaseAddress(pb,[])
  let ctx=CGContext(data:CVPixelBufferGetBaseAddress(pb),width:width,height:height,bitsPerComponent:8,bytesPerRow:CVPixelBufferGetBytesPerRow(pb),space:CGColorSpaceCreateDeviceRGB(),bitmapInfo:CGImageAlphaInfo.noneSkipFirst.rawValue)!
  let gc=NSGraphicsContext(cgContext:ctx,flipped:false);NSGraphicsContext.saveGraphicsState();NSGraphicsContext.current=gc
  let t=Double(frame)/Double(fps)
  ctx.setFillColor(ivory.cgColor);ctx.fill(CGRect(x:0,y:0,width:width,height:height))
  let glow=CGGradient(colorsSpace:CGColorSpaceCreateDeviceRGB(),colors:[NSColor.white.withAlphaComponent(0.92).cgColor,gold.withAlphaComponent(0.05).cgColor] as CFArray,locations:[0,1])!
  ctx.drawRadialGradient(glow,startCenter:CGPoint(x:820,y:1500),startRadius:0,endCenter:CGPoint(x:820,y:1500),endRadius:900,options:[])
  ctx.setFillColor(gold.withAlphaComponent(0.12).cgColor);ctx.fill(CGRect(x:70,y:1740,width:940,height:2))
  drawText("A SUNDAY REFLECTION",CGRect(x:70,y:1765,width:940,height:40),25,gold,"Helvetica Neue Bold",alpha(t,0.1,0.7))

  let first=alpha(t,0.4,1.1)
  drawText("You don’t have to be",CGRect(x:75,y:1370,width:930,height:80),54,ink,"Helvetica Neue",first)
  drawText("fully healed",CGRect(x:75,y:1260,width:930,height:110),88,gold,"Georgia Bold Italic",first)
  drawText("for God to start",CGRect(x:75,y:1165,width:930,height:80),54,ink,"Helvetica Neue",first)
  drawText("rebuilding you.",CGRect(x:75,y:1055,width:930,height:110),88,sage,"Georgia Bold Italic",first)

  let reveal=alpha(t,4.1,4.9)
  let scale=CGFloat(1+0.025*max(0,t-4.0)/(duration-4.0))
  let cw=CGFloat(485)*scale,ch=CGFloat(776)*scale
  cover.draw(in:CGRect(x:(CGFloat(width)-cw)/2,y:410-(ch-776)/2,width:cw,height:ch),from:.zero,operation:.sourceOver,fraction:reveal)
  ctx.setStrokeColor(gold.withAlphaComponent(0.55*reveal).cgColor);ctx.setLineWidth(3);ctx.stroke(CGRect(x:(CGFloat(width)-cw)/2-12,y:398-(ch-776)/2,width:cw+24,height:ch+24))
  drawText("BUILT BY GRACE",CGRect(x:70,y:1270,width:940,height:72),54,ink,"Helvetica Neue Bold",reveal)
  drawText("A journey of healing, faith and restoration.",CGRect(x:95,y:1190,width:890,height:58),31,sage,"Georgia Italic",reveal)

  let cta=alpha(t,8.1,8.8)
  ctx.setFillColor(sage.withAlphaComponent(0.92*cta).cgColor);ctx.fill(CGRect(x:175,y:185,width:730,height:94))
  drawText("READ THE BOOK · LINK IN BIO",CGRect(x:190,y:214,width:700,height:40),26,ivory,"Helvetica Neue Bold",cta)
  drawText("SABINO PEREIRA",CGRect(x:70,y:90,width:940,height:34),20,gold,"Helvetica Neue Bold",cta)
  NSGraphicsContext.restoreGraphicsState();CVPixelBufferUnlockBaseAddress(pb,[])
  adaptor.append(pb,withPresentationTime:CMTime(value:Int64(frame),timescale:fps))
}
input.markAsFinished();await writer.finishWriting()

let composition=AVMutableComposition(), videoAsset=AVURLAsset(url:silentURL), audioAsset=AVURLAsset(url:audioURL)
let range=CMTimeRange(start:.zero,duration:CMTime(seconds:duration,preferredTimescale:600))
if let src=try await videoAsset.loadTracks(withMediaType:.video).first,let dst=composition.addMutableTrack(withMediaType:.video,preferredTrackID:kCMPersistentTrackID_Invalid){try dst.insertTimeRange(range,of:src,at:.zero)}
if let src=try await audioAsset.loadTracks(withMediaType:.audio).first,let dst=composition.addMutableTrack(withMediaType:.audio,preferredTrackID:kCMPersistentTrackID_Invalid){try dst.insertTimeRange(range,of:src,at:.zero)}
let exporter=AVAssetExportSession(asset:composition,presetName:AVAssetExportPresetHighestQuality)!;exporter.outputURL = finalURL;exporter.outputFileType = .mp4;exporter.shouldOptimizeForNetworkUse=true
await exporter.export();if exporter.status != .completed { print(exporter.error?.localizedDescription ?? "Export failed");exit(1) }
try? FileManager.default.removeItem(at:silentURL);print(finalURL.path)
