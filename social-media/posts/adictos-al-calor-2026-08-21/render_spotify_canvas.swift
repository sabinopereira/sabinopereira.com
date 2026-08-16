import AppKit
import AVFoundation
import CoreVideo

let sourcePath = "output/covers/Adictos al calor - REIRA BIN - 3000px.jpg"
let outputPath = "social-media/posts/adictos-al-calor-2026-08-21/adictos-al-calor-spotify-canvas.mp4"
let cover = NSImage(contentsOfFile: sourcePath)!
let width = 1080, height = 1920, fps: Int32 = 30
let duration = 8.0

func smooth(_ x: Double) -> CGFloat {
  let v = max(0, min(1, x))
  return CGFloat(v * v * (3 - 2 * v))
}

func drawAspectFill(_ image: NSImage, in rect: CGRect, alpha: CGFloat = 1) {
  let scale = max(rect.width / image.size.width, rect.height / image.size.height)
  let sw = rect.width / scale, sh = rect.height / scale
  let source = CGRect(x: (image.size.width - sw) / 2, y: (image.size.height - sh) / 2, width: sw, height: sh)
  image.draw(in: rect, from: source, operation: .sourceOver, fraction: alpha)
}

func render() async throws {
  let url = URL(fileURLWithPath: outputPath)
  try? FileManager.default.removeItem(at: url)
  let writer = try AVAssetWriter(outputURL: url, fileType: .mp4)
  let input = AVAssetWriterInput(mediaType: .video, outputSettings: [
    AVVideoCodecKey: AVVideoCodecType.h264,
    AVVideoWidthKey: width,
    AVVideoHeightKey: height,
    AVVideoCompressionPropertiesKey: [
      AVVideoAverageBitRateKey: 5_000_000,
      AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel
    ]
  ])
  let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: [
    kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32ARGB,
    kCVPixelBufferWidthKey as String: width,
    kCVPixelBufferHeightKey as String: height
  ])
  writer.add(input)
  writer.startWriting()
  writer.startSession(atSourceTime: .zero)

  for frame in 0..<Int(duration * Double(fps)) {
    while !input.isReadyForMoreMediaData { usleep(1000) }
    var pixel: CVPixelBuffer?
    CVPixelBufferPoolCreatePixelBuffer(nil, adaptor.pixelBufferPool!, &pixel)
    let buffer = pixel!
    CVPixelBufferLockBaseAddress(buffer, [])
    let context = CGContext(data: CVPixelBufferGetBaseAddress(buffer), width: width, height: height,
      bitsPerComponent: 8, bytesPerRow: CVPixelBufferGetBytesPerRow(buffer),
      space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue)!
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = NSGraphicsContext(cgContext: context, flipped: false)

    let t = Double(frame) / Double(fps)
    let phase = t / duration
    let loopWave = 0.5 - 0.5 * cos(phase * .pi * 2)
    let zoom = CGFloat(1.08 + 0.025 * loopWave)
    let imageRect = CGRect(x: (CGFloat(width) - CGFloat(width) * zoom) / 2,
                           y: (CGFloat(height) - CGFloat(height) * zoom) / 2,
                           width: CGFloat(width) * zoom, height: CGFloat(height) * zoom)
    drawAspectFill(cover, in: imageRect)

    let warm = NSColor(calibratedRed: 0.95, green: 0.20, blue: 0.02,
                       alpha: CGFloat(0.06 + 0.08 * loopWave))
    context.setFillColor(warm.cgColor)
    context.fill(CGRect(x: 0, y: 0, width: width, height: height))

    for i in 0..<28 {
      let seed = Double((i * 67) % 101) / 101.0
      let x = CGFloat(30 + ((i * 181) % 1020))
      let yCycle = (phase + seed).truncatingRemainder(dividingBy: 1.0)
      let y = CGFloat(80 + yCycle * 1740)
      let r = CGFloat(2.0 + 4.0 * seed)
      let fade = CGFloat(sin(yCycle * .pi))
      context.setFillColor(NSColor(calibratedRed: 1, green: 0.48 + 0.25 * seed, blue: 0.04,
                                   alpha: 0.18 + 0.48 * fade).cgColor)
      context.fillEllipse(in: CGRect(x: x, y: y, width: r, height: r))
    }

    let vignette = CGGradient(colorsSpace: CGColorSpaceCreateDeviceRGB(), colors: [
      NSColor.clear.cgColor,
      NSColor.black.withAlphaComponent(0.40).cgColor
    ] as CFArray, locations: [0.55, 1.0])!
    context.drawRadialGradient(vignette, startCenter: CGPoint(x: 540, y: 980), startRadius: 300,
                               endCenter: CGPoint(x: 540, y: 980), endRadius: 1050, options: [])

    NSGraphicsContext.restoreGraphicsState()
    CVPixelBufferUnlockBaseAddress(buffer, [])
    adaptor.append(buffer, withPresentationTime: CMTime(value: Int64(frame), timescale: fps))
  }

  input.markAsFinished()
  await writer.finishWriting()
  if writer.status != .completed { throw writer.error ?? NSError(domain: "canvas", code: 1) }
  print(outputPath)
}

try await render()
