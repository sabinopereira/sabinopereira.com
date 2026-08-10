import AppKit
import AVFoundation
import CoreVideo

let folder = "social-media/posts/aqui-me-quedo-2026-08-14"
let bg = NSImage(contentsOfFile: folder + "/aqui-me-quedo-vertical-background.png")!
let audioURL = URL(fileURLWithPath: "audio/siempre-nosotros/01-aqui-me-quedo.mp3")
let width = 1080, height = 1920, fps: Int32 = 30
let cream = NSColor(calibratedRed: 0.96, green: 0.91, blue: 0.82, alpha: 1)
let terra = NSColor(calibratedRed: 0.67, green: 0.30, blue: 0.20, alpha: 1)
let olive = NSColor(calibratedRed: 0.30, green: 0.34, blue: 0.22, alpha: 1)

func ease(_ x: Double) -> CGFloat { let v = max(0, min(1, x)); return CGFloat(v*v*(3-2*v)) }
func alpha(_ t: Double, _ start: Double, _ end: Double) -> CGFloat { ease((t-start)/(end-start)) }
func drawText(_ s: String, _ rect: CGRect, _ size: CGFloat, _ color: NSColor, _ font: String = "Helvetica Neue", _ a: CGFloat = 1, _ align: NSTextAlignment = .center) {
  let p = NSMutableParagraphStyle(); p.alignment = align
  let f = NSFont(name: font, size: size) ?? .systemFont(ofSize: size)
  (s as NSString).draw(in: rect, withAttributes: [.font:f, .foregroundColor:color.withAlphaComponent(a), .paragraphStyle:p])
}
func drawBase(_ ctx: CGContext, _ time: Double, _ duration: Double) {
  let zoom = CGFloat(1.0 + 0.022*time/duration), dw = CGFloat(width)*zoom, dh = CGFloat(height)*zoom
  bg.draw(in: CGRect(x:(CGFloat(width)-dw)/2, y:(CGFloat(height)-dh)/2, width:dw, height:dh), from:.zero, operation:.sourceOver, fraction:1)
  let grad = CGGradient(colorsSpace: CGColorSpaceCreateDeviceRGB(), colors:[NSColor.black.withAlphaComponent(0.12).cgColor, NSColor.black.withAlphaComponent(0.68).cgColor] as CFArray, locations:[0,1])!
  ctx.drawLinearGradient(grad, start:CGPoint(x:540,y:1500), end:CGPoint(x:540,y:150), options:[])
}
func render(name: String, duration: Double, audioStart: Double, teaser: Bool) async throws {
  let silentURL = URL(fileURLWithPath: folder + "/\(name)-silent.mp4")
  let finalURL = URL(fileURLWithPath: folder + "/\(name).mp4")
  try? FileManager.default.removeItem(at:silentURL); try? FileManager.default.removeItem(at:finalURL)
  let writer = try AVAssetWriter(outputURL:silentURL, fileType:.mp4)
  let input = AVAssetWriterInput(mediaType:.video, outputSettings:[AVVideoCodecKey:AVVideoCodecType.h264, AVVideoWidthKey:width, AVVideoHeightKey:height, AVVideoCompressionPropertiesKey:[AVVideoAverageBitRateKey:9_000_000, AVVideoProfileLevelKey:AVVideoProfileLevelH264HighAutoLevel]])
  let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput:input, sourcePixelBufferAttributes:[kCVPixelBufferPixelFormatTypeKey as String:kCVPixelFormatType_32ARGB, kCVPixelBufferWidthKey as String:width, kCVPixelBufferHeightKey as String:height])
  writer.add(input); writer.startWriting(); writer.startSession(atSourceTime:.zero)
  for frame in 0..<Int(duration*Double(fps)) {
    while !input.isReadyForMoreMediaData { usleep(1000) }
    var px: CVPixelBuffer?; CVPixelBufferPoolCreatePixelBuffer(nil, adaptor.pixelBufferPool!, &px)
    let pb=px!; CVPixelBufferLockBaseAddress(pb, [])
    let ctx=CGContext(data:CVPixelBufferGetBaseAddress(pb), width:width, height:height, bitsPerComponent:8, bytesPerRow:CVPixelBufferGetBytesPerRow(pb), space:CGColorSpaceCreateDeviceRGB(), bitmapInfo:CGImageAlphaInfo.noneSkipFirst.rawValue)!
    let gc=NSGraphicsContext(cgContext:ctx, flipped:false); NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current=gc
    let t=Double(frame)/Double(fps); drawBase(ctx,t,duration)
    drawText("REIRA BIN", CGRect(x:70,y:1742,width:940,height:45), 29, cream, "Helvetica Neue Bold", alpha(t,0.1,0.6))
    if teaser {
      drawText("Hay canciones para", CGRect(x:80,y:1120,width:920,height:65), 45, cream, "Helvetica Neue", alpha(t,0.5,1.2))
      drawText("enamorarse.", CGRect(x:80,y:1038,width:920,height:100), 76, cream, "Georgia Italic", alpha(t,0.8,1.5))
      drawText("Esta es una canción", CGRect(x:80,y:900,width:920,height:65), 45, cream, "Helvetica Neue", alpha(t,2.6,3.2))
      drawText("para quedarse.", CGRect(x:80,y:810,width:920,height:100), 78, terra, "Georgia Bold Italic", alpha(t,2.9,3.6))
      drawText("AQUÍ ME QUEDO", CGRect(x:60,y:430,width:960,height:105), 78, cream, "Helvetica Neue Condensed Black", alpha(t,5.0,5.7))
      drawText("14 · 08", CGRect(x:60,y:358,width:960,height:55), 35, cream, "Helvetica Neue Bold", alpha(t,5.4,6.0))
    } else {
      drawText("AQUÍ ME QUEDO", CGRect(x:55,y:1330,width:970,height:110), 84, cream, "Helvetica Neue Condensed Black", alpha(t,0.3,1.0))
      drawText("OUT NOW", CGRect(x:55,y:1250,width:970,height:60), 38, terra, "Helvetica Neue Bold", alpha(t,0.6,1.2))
      drawText("Aquí me quedo", CGRect(x:80,y:820,width:920,height:85), 68, cream, "Georgia Italic", alpha(t,2.2,2.9))
      drawText("En este silencio", CGRect(x:80,y:720,width:920,height:85), 68, cream, "Georgia Italic", alpha(t,4.2,4.9))
      drawText("Contigo", CGRect(x:80,y:610,width:920,height:100), 82, terra, "Georgia Bold Italic", alpha(t,6.2,6.9))
      ctx.setFillColor(olive.withAlphaComponent(0.86*alpha(t,7.7,8.3)).cgColor); ctx.fill(CGRect(x:155,y:260,width:770,height:100))
      drawText("ESCUCHA AHORA · LINK EN BIO", CGRect(x:165,y:289,width:750,height:42), 27, cream, "Helvetica Neue Bold", alpha(t,7.7,8.3))
    }
    NSGraphicsContext.restoreGraphicsState(); CVPixelBufferUnlockBaseAddress(pb, [])
    adaptor.append(pb, withPresentationTime:CMTime(value:Int64(frame), timescale:fps))
  }
  input.markAsFinished(); await writer.finishWriting()
  let composition=AVMutableComposition(), videoAsset=AVURLAsset(url:silentURL), audioAsset=AVURLAsset(url:audioURL)
  let vr=CMTimeRange(start:.zero,duration:CMTime(seconds:duration,preferredTimescale:600))
  if let src=try await videoAsset.loadTracks(withMediaType:.video).first, let dst=composition.addMutableTrack(withMediaType:.video,preferredTrackID:kCMPersistentTrackID_Invalid) { try dst.insertTimeRange(vr,of:src,at:.zero) }
  if let src=try await audioAsset.loadTracks(withMediaType:.audio).first, let dst=composition.addMutableTrack(withMediaType:.audio,preferredTrackID:kCMPersistentTrackID_Invalid) { try dst.insertTimeRange(CMTimeRange(start:CMTime(seconds:audioStart,preferredTimescale:600),duration:vr.duration),of:src,at:.zero) }
  let exporter=AVAssetExportSession(asset:composition,presetName:AVAssetExportPresetHighestQuality)!; exporter.outputURL = finalURL; exporter.outputFileType = .mp4
  await exporter.export(); if exporter.status != .completed { throw exporter.error ?? NSError(domain:"export",code:1) }
  try? FileManager.default.removeItem(at:silentURL); print(finalURL.path)
}

func renderStory() throws {
  let canvas=NSImage(size:NSSize(width:width,height:height)); canvas.lockFocus()
  let ctx=NSGraphicsContext.current!.cgContext; drawBase(ctx,0,1)
  drawText("AQUÍ ME QUEDO",CGRect(x:55,y:1370,width:970,height:105),82,cream,"Helvetica Neue Condensed Black")
  drawText("ya disponible",CGRect(x:55,y:1295,width:970,height:65),42,terra,"Georgia Italic")
  drawText("¿Qué pequeña rutina",CGRect(x:80,y:760,width:920,height:70),54,cream,"Helvetica Neue Bold")
  drawText("significa amor para ti?",CGRect(x:80,y:680,width:920,height:70),54,cream,"Helvetica Neue Bold")
  ctx.setFillColor(olive.withAlphaComponent(0.88).cgColor);ctx.fill(CGRect(x:190,y:330,width:700,height:100))
  drawText("ESCUCHA AHORA · LINK EN BIO",CGRect(x:200,y:359,width:680,height:42),26,cream,"Helvetica Neue Bold")
  canvas.unlockFocus()
  let rep=NSBitmapImageRep(data:canvas.tiffRepresentation!)!; let data=rep.representation(using:.png,properties:[:])!
  try data.write(to:URL(fileURLWithPath:folder+"/aqui-me-quedo-story.png"))
}

try renderStory()
try await render(name:"aqui-me-quedo-teaser-reel",duration:8,audioStart:0,teaser:true)
try await render(name:"aqui-me-quedo-launch-reel",duration:10,audioStart:136,teaser:false)
