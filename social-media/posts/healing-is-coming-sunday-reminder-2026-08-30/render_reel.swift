import Foundation
import AVFoundation
import AppKit
import CoreVideo

let a = CommandLine.arguments
guard a.count == 9 else { fatalError("usage: render frame1 frame2 frame3 frame4 frame5 audio output silent") }
let framePaths = Array(a[1...5])
let audioURL = URL(fileURLWithPath: a[6])
let finalURL = URL(fileURLWithPath: a[7])
let silentURL = URL(fileURLWithPath: a[8])
try? FileManager.default.removeItem(at: silentURL)
try? FileManager.default.removeItem(at: finalURL)
let images: [CGImage] = framePaths.map {
  guard let im = NSImage(contentsOfFile: $0), let cg = im.cgImage(forProposedRect: nil, context: nil, hints: nil) else { fatalError("bad frame \($0)") }
  return cg
}
let width = 1080, height = 1920, fps: Int32 = 30, seconds = 12
let writer = try AVAssetWriter(outputURL: silentURL, fileType: .mp4)
let settings: [String:Any] = [AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: width, AVVideoHeightKey: height, AVVideoCompressionPropertiesKey:[AVVideoAverageBitRateKey:7_000_000,AVVideoProfileLevelKey:AVVideoProfileLevelH264HighAutoLevel]]
let input = AVAssetWriterInput(mediaType:.video,outputSettings:settings)
let attrs:[String:Any] = [kCVPixelBufferPixelFormatTypeKey as String:kCVPixelFormatType_32BGRA,kCVPixelBufferWidthKey as String:width,kCVPixelBufferHeightKey as String:height,kCVPixelBufferCGImageCompatibilityKey as String:true,kCVPixelBufferCGBitmapContextCompatibilityKey as String:true]
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput:input,sourcePixelBufferAttributes:attrs)
writer.add(input); writer.startWriting(); writer.startSession(atSourceTime:.zero)
let total = Int(fps) * seconds, q = DispatchQueue(label:"reira.reel"), sem = DispatchSemaphore(value:0)
var f = 0
func stage(_ t:Double)->(Int,Int,CGFloat){
  let cuts=[0.0,1.8,4.2,7.0,9.0,12.0], fade=0.35
  var i=0; while i<4 && t>=cuts[i+1] { i += 1 }
  if i<4 && t>cuts[i+1]-fade { return (i,i+1,CGFloat((t-(cuts[i+1]-fade))/fade)) }
  return (i,i,0)
}
input.requestMediaDataWhenReady(on:q){
  while input.isReadyForMoreMediaData && f<total {
    autoreleasepool {
      var pb:CVPixelBuffer?; CVPixelBufferPoolCreatePixelBuffer(nil,adaptor.pixelBufferPool!,&pb); let b=pb!
      CVPixelBufferLockBaseAddress(b,[])
      let bitmapInfo = CGBitmapInfo.byteOrder32Little.rawValue | CGImageAlphaInfo.premultipliedFirst.rawValue
      let ctx=CGContext(data:CVPixelBufferGetBaseAddress(b),width:width,height:height,bitsPerComponent:8,bytesPerRow:CVPixelBufferGetBytesPerRow(b),space:CGColorSpaceCreateDeviceRGB(),bitmapInfo:bitmapInfo)!
      let t=Double(f)/Double(fps), s=stage(t), rect=CGRect(x:0,y:0,width:width,height:height)
      ctx.setAlpha(1); ctx.draw(images[s.0],in:rect)
      if s.0 != s.1 { ctx.setAlpha(s.2); ctx.draw(images[s.1],in:rect) }
      CVPixelBufferUnlockBaseAddress(b,[])
      adaptor.append(b,withPresentationTime:CMTime(value:CMTimeValue(f),timescale:fps)); f += 1
    }
  }
  if f>=total { input.markAsFinished(); writer.finishWriting{sem.signal()} }
}
sem.wait(); guard writer.status == .completed else { fatalError(writer.error?.localizedDescription ?? "video failed") }

let composition=AVMutableComposition(), videoAsset=AVURLAsset(url:silentURL), audioAsset=AVURLAsset(url:audioURL)
let range=CMTimeRange(start:.zero,duration:CMTime(seconds:Double(seconds),preferredTimescale:600))
let cv=composition.addMutableTrack(withMediaType:.video,preferredTrackID:kCMPersistentTrackID_Invalid)!
try cv.insertTimeRange(range,of:videoAsset.tracks(withMediaType:.video)[0],at:.zero)
if let sourceAudio=audioAsset.tracks(withMediaType:.audio).first {
  let ca=composition.addMutableTrack(withMediaType:.audio,preferredTrackID:kCMPersistentTrackID_Invalid)!
  try ca.insertTimeRange(range,of:sourceAudio,at:.zero)
}
let export=AVAssetExportSession(asset:composition,presetName:AVAssetExportPresetHighestQuality)!
export.outputURL = finalURL; export.outputFileType = .mp4; export.shouldOptimizeForNetworkUse = true
let out=DispatchSemaphore(value:0); export.exportAsynchronously{out.signal()}; out.wait()
guard export.status == .completed else { fatalError(export.error?.localizedDescription ?? "export failed") }
print(finalURL.path)
