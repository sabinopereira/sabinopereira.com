import AppKit
import AVFoundation
import CoreVideo

let root = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
let imageDir = root.appendingPathComponent("assets/social/posts/built-by-grace-jezebel-light/tiktok")
let outputDir = root.appendingPathComponent("assets/social/posts/built-by-grace-jezebel-light/video")
try FileManager.default.createDirectory(at: outputDir, withIntermediateDirectories: true)

let audioURL = URL(fileURLWithPath: "/Users/binopereira/Desktop/Project Sabino Pereira/music/reira-bin-music/Built by Grace Music Album 2026/17 - God in the Center - Before We Say I Do.wav")
let silentURL = outputDir.appendingPathComponent("built-by-grace-reflection-silent.mp4")
let finalURL = outputDir.appendingPathComponent("built-by-grace-reflection-tiktok.mp4")
try? FileManager.default.removeItem(at: silentURL)
try? FileManager.default.removeItem(at: finalURL)

let width = 1080
let height = 1920
let fps: Int32 = 25
let secondsPerSlide = 4
let framesPerSlide = Int(fps) * secondsPerSlide
let slideNames = ["01-hook.png", "02-no.png", "03-character.png", "04-marriage.png", "05-built-by-grace.png"]

let writer = try AVAssetWriter(outputURL: silentURL, fileType: .mp4)
let settings: [String: Any] = [
  AVVideoCodecKey: AVVideoCodecType.h264,
  AVVideoWidthKey: width,
  AVVideoHeightKey: height,
  AVVideoCompressionPropertiesKey: [
    AVVideoAverageBitRateKey: 7_000_000,
    AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel
  ]
]
let input = AVAssetWriterInput(mediaType: .video, outputSettings: settings)
input.expectsMediaDataInRealTime = false
let attrs: [String: Any] = [
  kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32ARGB,
  kCVPixelBufferWidthKey as String: width,
  kCVPixelBufferHeightKey as String: height
]
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: attrs)
guard writer.canAdd(input) else { fatalError("Cannot add video input") }
writer.add(input)
guard writer.startWriting() else { fatalError("Cannot start writer: \(String(describing: writer.error))") }
writer.startSession(atSourceTime: .zero)

func pixelBuffer(for image: NSImage) -> CVPixelBuffer {
  var buffer: CVPixelBuffer?
  CVPixelBufferCreate(kCFAllocatorDefault, width, height, kCVPixelFormatType_32ARGB, attrs as CFDictionary, &buffer)
  guard let pixelBuffer = buffer else { fatalError("Cannot create pixel buffer") }
  CVPixelBufferLockBaseAddress(pixelBuffer, [])
  defer { CVPixelBufferUnlockBaseAddress(pixelBuffer, []) }
  guard let context = CGContext(
    data: CVPixelBufferGetBaseAddress(pixelBuffer),
    width: width,
    height: height,
    bitsPerComponent: 8,
    bytesPerRow: CVPixelBufferGetBytesPerRow(pixelBuffer),
    space: CGColorSpaceCreateDeviceRGB(),
    bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue
  ) else { fatalError("Cannot create drawing context") }
  context.setFillColor(NSColor(calibratedRed: 0.976, green: 0.945, blue: 0.894, alpha: 1).cgColor)
  context.fill(CGRect(x: 0, y: 0, width: width, height: height))
  guard let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else { fatalError("Cannot decode image") }
  context.draw(cg, in: CGRect(x: 0, y: 0, width: width, height: height))
  return pixelBuffer
}

var frame = 0
for name in slideNames {
  let path = imageDir.appendingPathComponent(name).path
  guard let image = NSImage(contentsOfFile: path) else { fatalError("Missing slide: \(name)") }
  let buffer = pixelBuffer(for: image)
  for _ in 0..<framesPerSlide {
    while !input.isReadyForMoreMediaData { Thread.sleep(forTimeInterval: 0.002) }
    let time = CMTime(value: CMTimeValue(frame), timescale: fps)
    guard adaptor.append(buffer, withPresentationTime: time) else { fatalError("Failed at frame \(frame)") }
    frame += 1
  }
}
input.markAsFinished()
await writer.finishWriting()
guard writer.status == .completed else { fatalError("Video render failed: \(String(describing: writer.error))") }

let composition = AVMutableComposition()
let videoAsset = AVURLAsset(url: silentURL)
let audioAsset = AVURLAsset(url: audioURL)
guard let sourceVideo = try await videoAsset.loadTracks(withMediaType: .video).first,
      let sourceAudio = try await audioAsset.loadTracks(withMediaType: .audio).first,
      let videoTrack = composition.addMutableTrack(withMediaType: .video, preferredTrackID: kCMPersistentTrackID_Invalid),
      let audioTrack = composition.addMutableTrack(withMediaType: .audio, preferredTrackID: kCMPersistentTrackID_Invalid) else {
  fatalError("Missing media track")
}
let duration = CMTime(seconds: Double(slideNames.count * secondsPerSlide), preferredTimescale: 600)
try videoTrack.insertTimeRange(CMTimeRange(start: .zero, duration: duration), of: sourceVideo, at: .zero)
try audioTrack.insertTimeRange(CMTimeRange(start: .zero, duration: duration), of: sourceAudio, at: .zero)

guard let exporter = AVAssetExportSession(asset: composition, presetName: AVAssetExportPresetHighestQuality) else { fatalError("Cannot create exporter") }
exporter.outputURL = finalURL
exporter.outputFileType = .mp4
exporter.shouldOptimizeForNetworkUse = true
await exporter.export()
guard exporter.status == .completed else { fatalError("Export failed: \(String(describing: exporter.error))") }
print(finalURL.path)
