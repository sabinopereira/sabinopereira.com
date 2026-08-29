import Foundation
import AVFoundation
import AppKit
import CoreVideo

let args = CommandLine.arguments
guard args.count == 3 else { fatalError("usage: render_video input.png output.mp4") }
let inputURL = URL(fileURLWithPath: args[1])
let outputURL = URL(fileURLWithPath: args[2])
try? FileManager.default.removeItem(at: outputURL)
guard let image = NSImage(contentsOf: inputURL),
      let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
  fatalError("unable to load input image")
}

let width = 1080
let height = 1920
let fps: Int32 = 30
let durationSeconds = 8
let writer = try AVAssetWriter(outputURL: outputURL, fileType: .mp4)
let settings: [String: Any] = [
  AVVideoCodecKey: AVVideoCodecType.h264,
  AVVideoWidthKey: width,
  AVVideoHeightKey: height,
  AVVideoCompressionPropertiesKey: [
    AVVideoAverageBitRateKey: 8_000_000,
    AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel
  ]
]
let input = AVAssetWriterInput(mediaType: .video, outputSettings: settings)
input.expectsMediaDataInRealTime = false
let attributes: [String: Any] = [
  kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
  kCVPixelBufferWidthKey as String: width,
  kCVPixelBufferHeightKey as String: height,
  kCVPixelBufferCGImageCompatibilityKey as String: true,
  kCVPixelBufferCGBitmapContextCompatibilityKey as String: true
]
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: attributes)
guard writer.canAdd(input) else { fatalError("cannot add writer input") }
writer.add(input)
guard writer.startWriting() else { fatalError(writer.error?.localizedDescription ?? "writer failed") }
writer.startSession(atSourceTime: .zero)

let totalFrames = Int(fps) * durationSeconds
let queue = DispatchQueue(label: "reira.bin.reflection.render")
let done = DispatchSemaphore(value: 0)
var frame = 0

input.requestMediaDataWhenReady(on: queue) {
  while input.isReadyForMoreMediaData && frame < totalFrames {
    autoreleasepool {
      var pixelBuffer: CVPixelBuffer?
      CVPixelBufferPoolCreatePixelBuffer(nil, adaptor.pixelBufferPool!, &pixelBuffer)
      guard let buffer = pixelBuffer else { fatalError("pixel buffer failed") }
      CVPixelBufferLockBaseAddress(buffer, [])
      let base = CVPixelBufferGetBaseAddress(buffer)!
      let bytes = CVPixelBufferGetBytesPerRow(buffer)
      let colorSpace = CGColorSpaceCreateDeviceRGB()
      let info = CGBitmapInfo(rawValue: CGImageAlphaInfo.premultipliedFirst.rawValue)
      let context = CGContext(data: base, width: width, height: height, bitsPerComponent: 8, bytesPerRow: bytes, space: colorSpace, bitmapInfo: info.rawValue)!
      context.setFillColor(NSColor(calibratedWhite: 0.98, alpha: 1).cgColor)
      context.fill(CGRect(x: 0, y: 0, width: width, height: height))
      let progress = CGFloat(frame) / CGFloat(max(totalFrames - 1, 1))
      let scale = 1.0 + 0.012 * progress
      let drawWidth = CGFloat(width) * scale
      let drawHeight = CGFloat(height) * scale
      let rect = CGRect(x: (CGFloat(width) - drawWidth) / 2,
                        y: (CGFloat(height) - drawHeight) / 2,
                        width: drawWidth, height: drawHeight)
      context.interpolationQuality = .high
      context.draw(cgImage, in: rect)
      CVPixelBufferUnlockBaseAddress(buffer, [])
      let time = CMTime(value: CMTimeValue(frame), timescale: fps)
      if !adaptor.append(buffer, withPresentationTime: time) {
        fatalError(writer.error?.localizedDescription ?? "append failed")
      }
      frame += 1
    }
  }
  if frame >= totalFrames {
    input.markAsFinished()
    writer.finishWriting { done.signal() }
  }
}

done.wait()
if writer.status != .completed { fatalError(writer.error?.localizedDescription ?? "render failed") }
print(outputURL.path)
