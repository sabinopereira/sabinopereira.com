import AppKit
import AVFoundation
import CoreVideo

let folder = "social-media/posts/adictos-al-calor-2026-08-21"
let coverPath = "output/covers/Adictos al calor - REIRA BIN - 3000px.jpg"
let audioPath = "output/audio/Adictos al calor - REIRA BIN.wav"
let cover = NSImage(contentsOfFile: coverPath)!
let width = 1080, height = 1920, fps: Int32 = 30
let cream = NSColor(calibratedRed: 0.98, green: 0.91, blue: 0.78, alpha: 1)
let ember = NSColor(calibratedRed: 0.92, green: 0.25, blue: 0.07, alpha: 1)
let gold = NSColor(calibratedRed: 1.0, green: 0.64, blue: 0.05, alpha: 1)

func ease(_ x: Double) -> CGFloat {
  let v = max(0, min(1, x)); return CGFloat(v * v * (3 - 2 * v))
}
func reveal(_ t: Double, _ start: Double, _ duration: Double = 0.55) -> CGFloat {
  ease((t - start) / duration)
}
func pulse(_ t: Double, speed: Double = 1.0) -> CGFloat {
  CGFloat(0.5 + 0.5 * sin(t * .pi * 2 * speed))
}
func font(_ name: String, _ size: CGFloat) -> NSFont {
  NSFont(name: name, size: size) ?? .systemFont(ofSize: size, weight: .bold)
}
func text(_ value: String, rect: CGRect, size: CGFloat, color: NSColor, name: String = "Helvetica Neue Bold", alpha: CGFloat = 1, align: NSTextAlignment = .center) {
  let style = NSMutableParagraphStyle(); style.alignment = align; style.lineSpacing = 5
  (value as NSString).draw(in: rect, withAttributes: [
    .font: font(name, size),
    .foregroundColor: color.withAlphaComponent(alpha),
    .paragraphStyle: style,
    .kern: 0.8
  ])
}
func drawAspectFill(_ image: NSImage, in rect: CGRect, alpha: CGFloat = 1) {
  let iw = image.size.width, ih = image.size.height
  let scale = max(rect.width / iw, rect.height / ih)
  let sourceW = rect.width / scale, sourceH = rect.height / scale
  let source = CGRect(x: (iw-sourceW)/2, y: (ih-sourceH)/2, width: sourceW, height: sourceH)
  image.draw(in: rect, from: source, operation: .sourceOver, fraction: alpha)
}
func drawBackground(_ ctx: CGContext, time: Double, duration: Double) {
  let zoom = CGFloat(1.05 + 0.04 * time / max(duration, 0.1))
  let rect = CGRect(x: (CGFloat(width)-CGFloat(width)*zoom)/2, y: (CGFloat(height)-CGFloat(height)*zoom)/2, width: CGFloat(width)*zoom, height: CGFloat(height)*zoom)
  drawAspectFill(cover, in: rect, alpha: 0.48)
  ctx.setFillColor(NSColor.black.withAlphaComponent(0.55).cgColor)
  ctx.fill(CGRect(x: 0, y: 0, width: width, height: height))
  let gradient = CGGradient(colorsSpace: CGColorSpaceCreateDeviceRGB(), colors: [
    NSColor.black.withAlphaComponent(0.10).cgColor,
    NSColor(calibratedRed: 0.22, green: 0.015, blue: 0.0, alpha: 0.72).cgColor,
    NSColor.black.withAlphaComponent(0.84).cgColor
  ] as CFArray, locations: [0, 0.52, 1])!
  ctx.drawLinearGradient(gradient, start: CGPoint(x: 540, y: 1900), end: CGPoint(x: 540, y: 0), options: [])
  for i in 0..<22 {
    let seed = Double((i * 71) % 101) / 101.0
    let x = CGFloat(55 + ((i * 193) % 970))
    let travel = (time * (90 + seed * 120) + seed * 1700).truncatingRemainder(dividingBy: 1840)
    let y = CGFloat(40 + travel)
    let r = CGFloat(2.0 + seed * 4.5)
    ctx.setFillColor(gold.withAlphaComponent(CGFloat(0.18 + seed * 0.42)).cgColor)
    ctx.fillEllipse(in: CGRect(x: x, y: y, width: r, height: r))
  }
}
func drawCover(_ t: Double, start: Double = 0.15) {
  let a = reveal(t, start, 0.75)
  let scale = 0.94 + 0.06 * a
  let side = CGFloat(870) * scale
  let rect = CGRect(x: (1080-side)/2, y: 520 + (1-a)*35, width: side, height: side)
  NSShadow().apply {
    $0.shadowColor = NSColor.black.withAlphaComponent(0.75)
    $0.shadowBlurRadius = 30
    $0.shadowOffset = NSSize(width: 0, height: -12)
  }
  cover.draw(in: rect, from: .zero, operation: .sourceOver, fraction: a)
  NSGraphicsContext.current?.cgContext.setStrokeColor(gold.withAlphaComponent(0.72*a).cgColor)
  NSGraphicsContext.current?.cgContext.setLineWidth(2)
  NSGraphicsContext.current?.cgContext.stroke(rect.insetBy(dx: -3, dy: -3))
}
extension NSShadow {
  func apply(_ block: (NSShadow) -> Void) { block(self); set() }
}

enum Kind { case teaser, launch }

func render(name: String, duration: Double, audioStart: Double, kind: Kind) async throws {
  let silentURL = URL(fileURLWithPath: folder + "/\(name)-silent.mp4")
  let finalURL = URL(fileURLWithPath: folder + "/\(name).mp4")
  try? FileManager.default.removeItem(at: silentURL)
  try? FileManager.default.removeItem(at: finalURL)
  let writer = try AVAssetWriter(outputURL: silentURL, fileType: .mp4)
  let input = AVAssetWriterInput(mediaType: .video, outputSettings: [
    AVVideoCodecKey: AVVideoCodecType.h264,
    AVVideoWidthKey: width,
    AVVideoHeightKey: height,
    AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: 9_000_000, AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel]
  ])
  let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: [
    kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32ARGB,
    kCVPixelBufferWidthKey as String: width,
    kCVPixelBufferHeightKey as String: height
  ])
  writer.add(input); writer.startWriting(); writer.startSession(atSourceTime: .zero)
  for frame in 0..<Int(duration * Double(fps)) {
    while !input.isReadyForMoreMediaData { usleep(1000) }
    var px: CVPixelBuffer?; CVPixelBufferPoolCreatePixelBuffer(nil, adaptor.pixelBufferPool!, &px)
    let pb = px!; CVPixelBufferLockBaseAddress(pb, [])
    let ctx = CGContext(data: CVPixelBufferGetBaseAddress(pb), width: width, height: height, bitsPerComponent: 8, bytesPerRow: CVPixelBufferGetBytesPerRow(pb), space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue)!
    NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current = NSGraphicsContext(cgContext: ctx, flipped: false)
    let t = Double(frame) / Double(fps)
    drawBackground(ctx, time: t, duration: duration)
    text("REIRA BIN", rect: CGRect(x: 70, y: 1780, width: 940, height: 48), size: 30, color: cream, alpha: reveal(t, 0.1))
    switch kind {
    case .teaser:
      drawCover(t)
      text("DIME, BEBÉ", rect: CGRect(x: 60, y: 1432, width: 960, height: 80), size: 48, color: cream, alpha: reveal(t, 0.5))
      text("¿ES AMOR O ES QUE SOMOS", rect: CGRect(x: 45, y: 365, width: 990, height: 62), size: 39, color: cream, alpha: reveal(t, 3.0))
      text("ADICTOS AL CALOR?", rect: CGRect(x: 45, y: 275, width: 990, height: 86), size: 62, color: gold, name: "Helvetica Neue Condensed Black", alpha: reveal(t, 3.4))
      text("21 · 08", rect: CGRect(x: 60, y: 175, width: 960, height: 55), size: 34, color: ember, alpha: reveal(t, 6.2))
    case .launch:
      let lyrics: [(Double,String,CGFloat)] = [
        (0.4,"SEGUIMOS BAILANDO CON FUEGO",44),
        (5.0,"COMO SI NO SUPIÉRAMOS\nCÓMO TERMINA",42),
        (10.4,"CADA VEZ QUE DECIMOS\nQUE ES EL FINAL",42),
        (15.0,"LO ENCENDEMOS DE NUEVO",46),
        (18.1,"DIME, BEBÉ",55),
        (20.0,"¿ES AMOR O ES QUE SOMOS\nADICTOS AL CALOR?",56)
      ]
      drawCover(t, start: 0.0)
      for (index,item) in lyrics.enumerated() {
        let next = index+1 < lyrics.count ? lyrics[index+1].0 : duration
        let a = reveal(t,item.0,0.35) * (1 - reveal(t,next-0.35,0.32))
        text(item.1, rect: CGRect(x: 45, y: 260, width: 990, height: 150), size: item.2, color: index == lyrics.count-1 ? gold : cream, name: "Helvetica Neue Condensed Black", alpha: a)
      }
      text("OUT 21 AUGUST", rect: CGRect(x: 60, y: 150, width: 960, height: 45), size: 29, color: ember, alpha: reveal(t, 0.5))
    }
    NSGraphicsContext.restoreGraphicsState(); CVPixelBufferUnlockBaseAddress(pb, [])
    adaptor.append(pb, withPresentationTime: CMTime(value: Int64(frame), timescale: fps))
  }
  input.markAsFinished(); await writer.finishWriting()
  let comp = AVMutableComposition(), videoAsset = AVURLAsset(url: silentURL), audioAsset = AVURLAsset(url: URL(fileURLWithPath: audioPath))
  let durationTime = CMTime(seconds: duration, preferredTimescale: 600)
  if let src = try await videoAsset.loadTracks(withMediaType: .video).first, let dst = comp.addMutableTrack(withMediaType: .video, preferredTrackID: kCMPersistentTrackID_Invalid) {
    try dst.insertTimeRange(CMTimeRange(start: .zero, duration: durationTime), of: src, at: .zero)
  }
  if let src = try await audioAsset.loadTracks(withMediaType: .audio).first, let dst = comp.addMutableTrack(withMediaType: .audio, preferredTrackID: kCMPersistentTrackID_Invalid) {
    try dst.insertTimeRange(CMTimeRange(start: CMTime(seconds: audioStart, preferredTimescale: 600), duration: durationTime), of: src, at: .zero)
  }
  let exporter = AVAssetExportSession(asset: comp, presetName: AVAssetExportPresetHighestQuality)!
  exporter.outputURL = finalURL; exporter.outputFileType = .mp4
  await exporter.export()
  if exporter.status != .completed { throw exporter.error ?? NSError(domain: "export", code: 1) }
  try? FileManager.default.removeItem(at: silentURL)
  print(finalURL.path)
}

func renderStory() throws {
  let image = NSImage(size: NSSize(width: width, height: height)); image.lockFocus()
  let ctx = NSGraphicsContext.current!.cgContext; drawBackground(ctx, time: 0, duration: 1)
  text("REIRA BIN", rect: CGRect(x: 70, y: 1780, width: 940, height: 48), size: 30, color: cream)
  drawCover(1)
  text("THE HEAT RETURNS", rect: CGRect(x: 60, y: 1438, width: 960, height: 70), size: 48, color: cream)
  text("21 AUGUST", rect: CGRect(x: 60, y: 320, width: 960, height: 90), size: 64, color: gold, name: "Helvetica Neue Condensed Black")
  text("ADICTOS AL CALOR", rect: CGRect(x: 60, y: 235, width: 960, height: 62), size: 38, color: cream)
  image.unlockFocus()
  let rep = NSBitmapImageRep(data: image.tiffRepresentation!)!
  let data = rep.representation(using: .jpeg, properties: [.compressionFactor: 0.92])!
  try data.write(to: URL(fileURLWithPath: folder + "/adictos-countdown-story.jpg"))
}

try FileManager.default.createDirectory(atPath: folder, withIntermediateDirectories: true)
try renderStory()
try await render(name: "adictos-teaser-reel", duration: 10, audioStart: 63.8, kind: .teaser)
try await render(name: "adictos-launch-reel", duration: 27, audioStart: 45.1, kind: .launch)
